# Intelligence Design — Routing, Classification & Adaptive Learning

> **Document owner:** Expert 2 (Routing & Intelligence Architect)
> **Date:** 2026-03-25
> **Status:** Draft

---

## Table of Contents

1. [Intent Classification](#1-intent-classification)
2. [Provider Selection](#2-provider-selection)
3. [Adaptive Learning](#3-adaptive-learning)
4. [Dynamic Rule Generation](#4-dynamic-rule-generation)
5. [Provider Health Tracking](#5-provider-health-tracking)
6. [The Draft Round in Detail](#6-the-draft-round-in-detail)
7. [Agent Routing (Future)](#7-agent-routing-future)
8. [Devil's Advocate](#8-devils-advocate)
9. [Open Questions](#9-open-questions)
- [Appendix A: SQL Schema](#appendix-a-sql-schema)
- [Appendix B: Ported Routing Rules](#appendix-b-ported-routing-rules)

---

## 1. Intent Classification

### 1.1 Approach: Layered Regex + Optional ML

**Primary: Regex/keyword matching (Workers-compatible).** The classifier uses ordered pattern rules evaluated top-to-bottom, first-match-wins for commands, highest-confidence-wins for heuristics.

**Why regex, not ML:**
- Runs on Cloudflare Workers (cold start <5ms, no model loading)
- Deterministic and auditable — users can see why a message was routed
- The Python routing script already proves this approach works
- ML can be layered on top later as a "re-ranking" step

**Classification pipeline:**

```
User message
  ├─ Command prefix? (/draft, /local, /compare, /model:xxx) → immediate action, confidence=1.0
  ├─ Dynamic rules (DB) matched? → use highest-confidence dynamic rule
  ├─ Static heuristic matched? → use highest-confidence static rule
  └─ Fallback → cheap, confidence=0.3
```

### 1.2 Classification Taxonomy

| Action | Description | Default Confidence |
|--------|-------------|-------------------|
| `cheap` | Fast, low-cost model for simple queries | 0.7–0.9 |
| `escalation` | Reasoning model for complex tasks | 0.6–0.8 |
| `compare` | Run cheap + escalation in parallel, present both | 0.5 |
| `draft` | Multi-provider draft round with profiles | 1.0 (command) |
| `local` | Route to local model (llama.cpp) | 1.0 (command) |
| `manual` | User specified exact model | 1.0 (command) |

### 1.3 Triggers & Confidence Thresholds

**Decision rule:** After evaluating all matching rules (static + dynamic), pick the highest-confidence match. If multiple rules match with different actions, use the highest confidence. If confidence < 0.5 for escalation/compare, fall through to cheap (cost safety).

**Tie-breaking:** When confidence is equal, prefer: manual > draft > local > compare > escalation > cheap.

### 1.4 Command Prefixes (User Overrides)

These always take priority (confidence=1.0), evaluated before any other rules:

| Prefix | Action | Example |
|--------|--------|---------|
| `/draft` | DRAFT round | `/draft write me a landing page` |
| `/local` | LOCAL model | `/local summarize this` |
| `/compare` | COMPARE mode | `/compare react vs vue` |
| `/model:<name>` | MANUAL override | `/model:claude-3 explain this` |
| `/cheap` | Force cheap | `/cheap what time is it` |
| `/escalate` | Force escalation | `/escalate debug this error` |

After extracting the command, the remainder of the message (minus the prefix) is the actual prompt.

### 1.5 Integration with Python Routing Rules (Port)

The existing Python `routing_script.py` defines 14 static rules. These are ported directly to Workers-compatible JS in the appendix. The key integration points:

- **Command prefixes** (`/draft`, `/local`, `/model:*`) are evaluated first, identical to the Python script
- **Static heuristics** (debug, code, review patterns) are ported as regex rules with identical confidence values
- **`_normalize_action()`** is replicated: `cheap_only` → `cheap`, `escalate` → `escalation`
- **Fallback behavior** preserved: no match → cheap at 0.3 confidence
- The Python script's `RoutingOptimizer` (dynamic rules from SQLite) becomes the D1-backed dynamic rules layer in Workers

---

## 2. Provider Selection

### 2.1 Selection Algorithm

Given an action + confidence, select a provider:

```
resolve(action) → list of candidate providers (ranked by priority)
filter → remove degraded providers (see §5)
pick → select first available, apply cost/latency adjustments
```

### 2.2 Provider Priority by Action

| Action | Primary | Secondary | Notes |
|--------|---------|-----------|-------|
| `cheap` | deepseek-chat | claude-haiku | Pick lowest latency |
| `escalation` | deepseek-reasoner | claude-sonnet | Pick based on health score |
| `compare` | cheap + escalation | — | Always both |
| `draft` | config-defined profiles | — | See §6 |
| `local` | llama.cpp endpoint | — | Single provider |
| `manual` | user-specified | cheap fallback | If specified fails |

### 2.3 Multi-Provider Failover

```
try primary_provider:
    if response.success: return response
    if error is retryable (429, 503, timeout):
        log failure, degrade provider temporarily
        try secondary_provider
    if error is non-retryable (400, 401, 403):
        return error to user (user must fix config)
catch timeout (>30s):
    log timeout, degrade provider
    try secondary_provider
```

**Max retries:** 1 (immediate failover, no retry loop — latency matters).

### 2.4 Cost-Aware Routing

- Each provider has a `cost_per_1k_tokens` config value
- For `cheap` action: always pick cheapest healthy provider
- For `escalation`: pick cheapest among providers with health score > 0.8
- For `compare`: cost is accepted (user implicitly chose it)
- **Budget caps:** Per-user daily budget, configurable. When budget is hit, force `cheap` routing with a notice.

### 2.5 Latency-Aware Routing

- Provider health tracker maintains rolling average latency (p95)
- For `cheap` action: prefer provider with lowest p95 latency
- For `escalation`: allow up to 2× latency of the fastest if health is significantly better
- **Timeout:** 30s default per provider. Configurable per-action.

### 2.6 Compare Mode

Both cheap and escalation providers are called in parallel. The user sees both responses and can vote. Rankings feed back into routing (see §4).

---

## 3. Adaptive Learning

### 3.1 Feedback Collection

After every response, the system collects:
- **Implicit signals:** user replied (engagement), user ignored (no reply within 30min), user typed `/retry`, user switched model
- **Explicit signals:** thumbs up (👍), thumbs down (👎), compare-mode winner selection

Feedback is stored per message:

```sql
CREATE TABLE feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    action TEXT NOT NULL,
    rating INTEGER NOT NULL,  -- 1 (down), 0 (neutral), 1 (up)
    signal TEXT NOT NULL,     -- 'explicit_up', 'explicit_down', 'implicit_retry', 'implicit_engaged', 'compare_winner'
    created_at INTEGER NOT NULL DEFAULT (unixepoch())
);
```

### 3.2 Feedback → Routing Rule Updates

**Threshold for rule change:** A routing rule requires **5 feedback events** with the same pattern-action combination before it can be modified. This prevents single-vote volatility.

**How updates work:**

1. For each classified message, record: pattern matched, action chosen, provider, feedback
2. Aggregate weekly: for each pattern, compute `satisfaction_rate = positive_feedback / total_feedback`
3. If `satisfaction_rate < 0.4` (40% positive) for an escalation route, suggest downgrading to cheap
4. If `satisfaction_rate > 0.85` for a cheap route, keep as-is (no need to escalate)
5. If `satisfaction_rate > 0.85` for an escalation route, confirm the pattern is correctly classified

### 3.3 Confidence Calibration

The system tracks whether its classifications match user preference:

```sql
CREATE TABLE classification_accuracy (
    pattern_id INTEGER REFERENCES routing_rules(id),
    total_classifications INTEGER DEFAULT 0,
    user_agreed INTEGER DEFAULT 0,  -- positive feedback or no action
    user_disagreed INTEGER DEFAULT 0,  -- negative feedback, retry, manual override
    calibrated_confidence REAL,  -- adjusted confidence based on history
    last_updated INTEGER
);
```

**Calibration formula:**
```
calibrated_confidence = base_confidence × (user_agreed / total_classifications)
```

A pattern with base confidence 0.7 but only 50% user agreement gets calibrated to 0.35, which may fall below the escalation threshold → automatically downgrades to cheap.

### 3.4 Cold Start (Zero Feedback)

With zero feedback:
- **Static rules only** — the 14 ported rules from the Python script
- Default providers: deepseek-chat (cheap), deepseek-reasoner (escalation)
- No dynamic rule creation until minimum feedback threshold (5 events per pattern)
- The system is conservative: defaults to cheap unless a pattern clearly matches escalation

### 3.5 Decay

- **Feedback data:** No decay — all feedback is kept for calibration
- **Routing rules:** Dynamic rules expire after 90 days of no matching messages
- **Health metrics:** Rolling window of 7 days for provider health (older data ages out)
- **Calibration scores:** Recalculated weekly from full feedback history (not decayed — more data = better calibration)

---

## 4. Dynamic Rule Generation

### 4.1 When Rules Are Created

A new dynamic routing rule is created when:

1. **Compare mode produces a consistent winner:** If the same provider wins 5+ times for messages matching a similar pattern, create a rule favoring that provider
2. **Manual override pattern:** If a user consistently uses `/model:X` for messages matching pattern P (3+ times), create a rule `P → manual:X`
3. **Retry signal:** If a user retries with `/escalate` after getting a cheap response for pattern P (3+ times), create a rule `P → escalation`

### 4.2 Rule Format

```sql
CREATE TABLE routing_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    pattern TEXT NOT NULL,          -- regex pattern
    action TEXT NOT NULL,           -- cheap, escalation, compare, draft, local, manual
    provider TEXT,                  -- specific provider override (nullable)
    confidence REAL NOT NULL DEFAULT 0.5,
    source TEXT NOT NULL DEFAULT 'static',  -- 'static', 'dynamic', 'learned'
    feedback_count INTEGER DEFAULT 0,
    positive_feedback INTEGER DEFAULT 0,
    enabled INTEGER DEFAULT 1,
    created_at INTEGER NOT NULL DEFAULT (unixepoch()),
    updated_at INTEGER NOT NULL DEFAULT (unixepoch()),
    expires_at INTEGER,             -- NULL = never (static), or timestamp
    UNIQUE(name)
);
```

### 4.3 Avoiding Overfitting

- **Minimum feedback threshold:** 5 events before a rule can be created/modified
- **Statistical significance:** Rule must have p < 0.1 (binomial test) to differ from default routing
- **User scope:** Rules are global (all users) by default. Per-user rules are opt-in and weighted at 1.5× global rules
- **Anti-spike:** A single user cannot generate >30% of the feedback for any rule

### 4.4 Generalization from Specific Feedback

When a user gives negative feedback ("I didn't like this response"):

1. **Don't create a rule immediately** — wait for pattern
2. **Log the full context:** message text, action, provider, model, confidence
3. **Cluster similar messages:** Use simple keyword overlap (Jaccard similarity > 0.5) to find similar past messages
4. **If cluster shows trend:** 3+ similar messages with negative feedback → propose a rule change
5. **Human review gate:** Proposed rules from feedback (not compare-mode wins) are marked `source='learned'` and start with `enabled=0`. They require either:
   - 10 more confirming feedback events, OR
   - Admin approval

This prevents the system from learning wrong lessons from outlier feedback.

---

## 5. Provider Health Tracking

### 5.1 Metrics Per Provider

```sql
CREATE TABLE provider_health (
    provider TEXT PRIMARY KEY,
    total_requests INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    total_latency_ms INTEGER DEFAULT 0,  -- cumulative for avg calculation
    p95_latency_ms INTEGER DEFAULT 0,
    total_tokens_in INTEGER DEFAULT 0,
    total_tokens_out INTEGER DEFAULT 0,
    total_cost_usd REAL DEFAULT 0.0,
    consecutive_failures INTEGER DEFAULT 0,
    degraded_until INTEGER DEFAULT 0,     -- unix timestamp, 0 = healthy
    last_success INTEGER,
    last_error TEXT,
    updated_at INTEGER NOT NULL DEFAULT (unixepoch())
);
```

### 5.2 Tracked Metrics

| Metric | Calculation | Update frequency |
|--------|-------------|-----------------|
| Success rate | `success_count / total_requests` | Per request |
| Avg latency | `total_latency_ms / total_requests` | Per request |
| P95 latency | Rolling window (last 100 requests) | Per request |
| Error rate | `error_count / total_requests` | Per request |
| Cost per request | `total_cost_usd / total_requests` | Per request |

### 5.3 Auto-Degradation

A provider gets **temporarily degraded** when:
- **3 consecutive failures** → degraded for 5 minutes
- **5 consecutive failures** → degraded for 30 minutes
- **Error rate > 50%** (rolling 1-hour window) → degraded for 1 hour
- **P95 latency > 2× baseline** → soft-degraded (still used for escalation, skipped for cheap)

When degraded:
- Provider is skipped in normal selection
- If all providers are degraded, use the one with the shortest degradation period remaining
- Log degradation event with reason

### 5.4 Recovery

A degraded provider returns to normal when:
- `degraded_until` timestamp passes
- On first successful request after recovery, reset `consecutive_failures` to 0
- Apply a **probabilistic warm-up**: first 3 requests after recovery have 50% chance of being routed to the recovering provider (canary testing)
- If canary fails, re-degrade for 2× the original period (exponential backoff, max 24h)

---

## 6. The Draft Round in Detail

### 6.1 Provider Profiles for Draft Rounds

A draft round runs multiple providers in parallel, each with a configurable profile:

```sql
CREATE TABLE draft_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    system_prompt TEXT,              -- optional override
    temperature REAL DEFAULT 0.7,
    max_tokens INTEGER DEFAULT 2048,
    priority INTEGER DEFAULT 0,      -- lower = shown first
    enabled INTEGER DEFAULT 1
);
```

**Default profiles:**

| Profile | Provider | Model | Temperature | System Prompt |
|---------|----------|-------|-------------|---------------|
| `creative` | openrouter | claude-haiku | 0.9 | "You are creative and concise." |
| `precise` | deepseek | deepseek-chat | 0.3 | "You are precise and thorough." |
| `reasoning` | deepseek | deepseek-reasoner | 0.1 | "Think step by step." |

### 6.2 Draft Round Execution

1. User sends `/draft <prompt>` or system triggers draft for high-uncertainty messages
2. All enabled draft profiles are called **in parallel**
3. Responses are collected with a 30s timeout per provider
4. Responses are presented to user (numbered or in a comparison view)
5. User selects winner (or none)

### 6.3 Winner Selection & Storage

```sql
CREATE TABLE draft_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id TEXT NOT NULL,
    prompt TEXT NOT NULL,
    profile_id INTEGER REFERENCES draft_profiles(id),
    provider TEXT,
    model TEXT,
    response TEXT,
    latency_ms INTEGER,
    winner INTEGER DEFAULT 0,         -- 1 if user selected this
    created_at INTEGER NOT NULL DEFAULT (unixepoch())
);
```

### 6.4 Rankings → Training Data

- Every draft result is training data, not just winners
- Winner = label 1, non-selected = label 0
- Training data is exported weekly as JSON for potential future ML classifier training
- No ML classifier currently exists — this is forward-compatibility

### 6.5 Rankings → Routing Rules

- If profile X wins >70% of draft rounds for messages matching pattern P, create rule: `P → manual:X.provider/X.model`
- This auto-promotes draft winners to preferred providers for similar messages
- Rule starts with `source='learned'` and requires 10 confirming wins before `enabled=1`

### 6.6 Agent Comparison (Future)

Draft rounds can compare agents, not just models:
- Agent A (code specialist) vs Agent B (generalist)
- Same infrastructure — draft profiles reference agent endpoints instead of model endpoints
- Winner ranking applies to agent selection, not model selection
- This is the bridge between model routing and agent routing (§7)

---

## 7. Agent Routing (Future)

### 7.1 The Omni-Bot Vision

The omni-bot concept: a single entry point that routes to specialized agents based on intent. This is a natural extension of provider routing.

**Current state:** We route to providers (models). **Future:** Route to agents (capabilities).

### 7.2 Agent Capability Matching

```
Intent classification
  → action (cheap/escalation/draft/...)
  → required capabilities (code, research, creative, math, ...)
  → available agents (registered with capability tags)
  → best agent (highest capability match + health score)
  → provider selection within that agent
```

Each agent registers capabilities:

```sql
CREATE TABLE agent_capabilities (
    agent_id TEXT NOT NULL,
    capability TEXT NOT NULL,  -- 'code', 'research', 'creative', 'math', 'writing'
    proficiency REAL DEFAULT 0.5,  -- 0-1
    PRIMARY KEY (agent_id, capability)
);
```

### 7.3 Cross-Agent Handoff

When one agent can't handle a request:
1. Agent signals: `{"handoff": true, "reason": "requires code review", "suggested_agent": "code-reviewer"}`
2. System routes to suggested agent (or best-matching agent for the reason)
3. Context (conversation history) is passed to the new agent
4. User is notified: "Switching to [agent] for this part."

### 7.4 Agent Comparison

Draft rounds between agents:
- Same mechanism as model comparison
- Draft profiles reference agent endpoints
- Rankings determine default agent for each capability
- Agents can specialize without blocking generalist fallback

---

## 8. Devil's Advocate

### 8.1 "Why not use an ML classifier instead of regex?"

**Strongest argument for ML:** Regex is brittle. It can't understand semantics. "Fix my code" and "Here's my fixed code" both match "fix" but need different routing. An ML classifier trained on user feedback would continuously improve and handle edge cases regex misses.

**Counter:** On Cloudflare Workers, we need <50ms classification latency. Loading even a tiny ML model (like a distilled BERT) adds 50-200ms cold start and requires WASM compilation. Regex runs in <1ms. The 14 static rules cover 80%+ of real queries. The 20% edge cases get handled by dynamic rules + feedback learning over time. ML is the right answer eventually — but regex gets us to MVP in days, not months. **Decision: Regex now, ML as a future re-ranking layer (not replacement).**

### 8.2 "Why not let users manually route everything?"

**Strongest argument for manual routing:** Users know best. If someone always wants Claude for code, let them set that. No classification needed. Simpler system, more user control, no classification errors.

**Counter:** Most users won't bother setting up manual routes. They'll just use the default and get frustrated when simple queries use expensive models. The system's value is *not* needing to think about which model to use. Compare mode and feedback let the system learn user preferences without requiring explicit configuration. Manual routing exists as an escape hatch (`/model:X`), not the default. **Decision: Auto-classify by default, manual override available.**

### 8.3 "Why not route by token count instead of intent?"

**Strongest argument for token routing:** Simple to implement. Short messages → cheap, long messages → escalation. No regex, no classification, just `if tokens > 500 then escalate`. Token count correlates well with complexity.

**Counter:** "What's 2+2?" is 3 tokens. "Explain quantum entanglement to a 5-year-old" is 7 tokens. Token count says both are cheap. The first is, the second isn't. Conversely, a 1000-line code dump with "fix line 42" is long but may only need a cheap model. Intent matters more than length. Token count is a useful *signal* (included as the `long_message` heuristic rule) but not the classifier. **Decision: Token count as one heuristic signal among many, not the classifier.**

### 8.4 "Why classify at all? Why not just always use the best model?"

**Strongest argument for best-model-always:** Simplicity. No classification, no routing, no learning. Just send everything to the best model (Claude Sonnet / GPT-4o). Cost is decreasing, latency is improving. Why engineer complexity for a problem that's solving itself?

**Counter:** Cost. Using Claude Sonnet for "what time is it" is 10× more expensive than necessary. At scale (thousands of messages/day), the difference is hundreds of dollars/month. Latency: cheap models respond in 1-2s, reasoning models in 5-15s. Users notice. The draft round's value is discovering *which* model is actually best for each query type — it's not always the most expensive one. **Decision: Classify. The cost savings fund the system. The latency improvement funds the UX.**

---

## 9. Open Questions

1. **Compare mode UI:** How do we present two responses in Telegram? Side-by-side isn't possible. Sequential with a button? Two messages with inline vote buttons?
2. **Per-user vs global rules:** Should the system start per-user or global? Per-user is more personalized but needs more data. Global gives faster cold start.
3. **Feedback in group chats:** If multiple users see a response, whose feedback counts? First reactor? All reactors? Only the original asker?
4. **Draft round cost:** A draft round with 3 providers is 3× cost. Should there be a per-user or global budget for draft rounds?
5. **ML classifier timeline:** At what point (users, feedback volume, accuracy plateau) do we invest in an ML classifier?
6. **Rate limiting:** Should the system rate-limit classification changes? (e.g., max 1 rule change per day per pattern)
7. **Mobile latency:** Mobile clients may have higher latency. Should provider selection account for client type?
8. **Conversation context:** Should classification consider conversation history? (e.g., if the last 3 messages were code, escalate even a short follow-up)
9. **A/B testing new rules:** Should new learned rules be A/B tested against current rules before full deployment?

---

## Appendix A: SQL Schema

Full schema for routing intelligence:

```sql
-- Core routing rules
CREATE TABLE IF NOT EXISTS routing_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    pattern TEXT NOT NULL,
    action TEXT NOT NULL CHECK(action IN ('cheap', 'escalation', 'compare', 'draft', 'local', 'manual')),
    provider TEXT,
    confidence REAL NOT NULL DEFAULT 0.5,
    source TEXT NOT NULL DEFAULT 'static' CHECK(source IN ('static', 'dynamic', 'learned')),
    feedback_count INTEGER DEFAULT 0,
    positive_feedback INTEGER DEFAULT 0,
    enabled INTEGER DEFAULT 1,
    created_at INTEGER NOT NULL DEFAULT (unixepoch()),
    updated_at INTEGER NOT NULL DEFAULT (unixepoch()),
    expires_at INTEGER,
    UNIQUE(name)
);

-- User feedback on responses
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    action TEXT NOT NULL,
    rating INTEGER NOT NULL CHECK(rating IN (-1, 0, 1)),
    signal TEXT NOT NULL,
    created_at INTEGER NOT NULL DEFAULT (unixepoch())
);

-- Classification accuracy tracking
CREATE TABLE IF NOT EXISTS classification_accuracy (
    pattern_id INTEGER PRIMARY KEY REFERENCES routing_rules(id),
    total_classifications INTEGER DEFAULT 0,
    user_agreed INTEGER DEFAULT 0,
    user_disagreed INTEGER DEFAULT 0,
    calibrated_confidence REAL,
    last_updated INTEGER
);

-- Provider health metrics
CREATE TABLE IF NOT EXISTS provider_health (
    provider TEXT PRIMARY KEY,
    total_requests INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    total_latency_ms INTEGER DEFAULT 0,
    p95_latency_ms INTEGER DEFAULT 0,
    total_tokens_in INTEGER DEFAULT 0,
    total_tokens_out INTEGER DEFAULT 0,
    total_cost_usd REAL DEFAULT 0.0,
    consecutive_failures INTEGER DEFAULT 0,
    degraded_until INTEGER DEFAULT 0,
    last_success INTEGER,
    last_error TEXT,
    updated_at INTEGER NOT NULL DEFAULT (unixepoch())
);

-- Draft round profiles
CREATE TABLE IF NOT EXISTS draft_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    system_prompt TEXT,
    temperature REAL DEFAULT 0.7,
    max_tokens INTEGER DEFAULT 2048,
    priority INTEGER DEFAULT 0,
    enabled INTEGER DEFAULT 1
);

-- Draft round results
CREATE TABLE IF NOT EXISTS draft_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id TEXT NOT NULL,
    prompt TEXT NOT NULL,
    profile_id INTEGER REFERENCES draft_profiles(id),
    provider TEXT,
    model TEXT,
    response TEXT,
    latency_ms INTEGER,
    winner INTEGER DEFAULT 0,
    created_at INTEGER NOT NULL DEFAULT (unixepoch())
);

-- Agent capabilities (future)
CREATE TABLE IF NOT EXISTS agent_capabilities (
    agent_id TEXT NOT NULL,
    capability TEXT NOT NULL,
    proficiency REAL DEFAULT 0.5,
    PRIMARY KEY (agent_id, capability)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_feedback_pattern ON feedback(message_id, user_id);
CREATE INDEX IF NOT EXISTS idx_feedback_provider ON feedback(provider, signal);
CREATE INDEX IF NOT EXISTS idx_routing_rules_enabled ON routing_rules(enabled, source);
CREATE INDEX IF NOT EXISTS idx_draft_results_winner ON draft_results(message_id, winner);
CREATE INDEX IF NOT EXISTS idx_provider_health_degraded ON provider_health(degraded_until);
```

---

## Appendix B: Ported Routing Rules (Python → JS)

The following rules are ported from `routing_script.py` (`_STATIC_RULES`) to Workers-compatible JavaScript:

```javascript
// Ported from vault/routing_script.py _STATIC_RULES
// All patterns are regex, evaluated in order

const STATIC_RULES = [
  // --- Command prefixes (highest priority, confidence=1.0) ---
  {
    name: "draft_mode",
    pattern: /^\/draft\b/i,
    action: "draft",
    confidence: 1.0,
    isCommand: true,
  },
  {
    name: "local_mode",
    pattern: /^\/local\b/i,
    action: "local",
    confidence: 1.0,
    isCommand: true,
  },
  {
    name: "manual_override",
    pattern: /^\/(deepseek|gpt|claude|local|cheap|escalate)\b/i,
    action: "manual",
    confidence: 1.0,
    isCommand: true,
  },

  // --- Heuristic signals ---
  {
    name: "code_block",
    pattern: /```/s,
    action: "escalation",
    confidence: 0.8,
  },
  {
    name: "long_message",
    pattern: /.{500,}/s,
    action: "escalation",
    confidence: 0.6,
  },

  // --- Escalation patterns (complex tasks) ---
  {
    name: "debug",
    pattern: /\b(debug|traceback|error|fix|broken|bug)\b/i,
    action: "escalation",
    confidence: 0.7,
  },
  {
    name: "write_code",
    pattern: /\b(write|implement|create|build|code)\s+(a |the )?(function|class|module|script|program|app|service|api|endpoint)/i,
    action: "escalation",
    confidence: 0.7,
  },
  {
    name: "explain_complex",
    pattern: /\b(explain|describe)\b.*\b(in detail|thoroughly|step\.?by\.?step|comprehensive)\b/i,
    action: "escalation",
    confidence: 0.6,
  },
  {
    name: "plan",
    pattern: /\b(plan|strategy|architecture|roadmap|migration)\b/i,
    action: "escalation",
    confidence: 0.7,
  },
  {
    name: "review",
    pattern: /\b(review|audit|critique|analyze|evaluate|improve|optimize)\b/i,
    action: "escalation",
    confidence: 0.7,
  },
  {
    name: "design",
    pattern: /\b(design|architect|structure|schema)\b/i,
    action: "escalation",
    confidence: 0.7,
  },

  // --- Comparison (dual-model) ---
  {
    name: "comparison",
    pattern: /\b(compare|vs|versus|difference)\b/i,
    action: "compare",
    confidence: 0.5,
  },

  // --- Cheap patterns (simple queries) ---
  {
    name: "factual_question",
    pattern: /^(what|how|who|when|where|which|count|convert|define|calculate)\b/i,
    action: "cheap",
    confidence: 0.7,
  },
  {
    name: "acknowledgment",
    pattern: /^(ok|thanks|thank you|got it|sure|great|nice|cool)\b/i,
    action: "cheap",
    confidence: 0.9,
  },
  {
    name: "help",
    pattern: /^help$/i,
    action: "cheap",
    confidence: 0.8,
  },
];
```

### Classification function:

```javascript
function classifyStatic(message, length = 0, hasCode = false) {
  // 1. Check command prefixes first (isCommand=true)
  for (const rule of STATIC_RULES) {
    if (rule.isCommand && rule.pattern.test(message)) {
      return {
        action: rule.action,
        confidence: rule.confidence,
        reason: `[static] ${rule.name}`,
      };
    }
  }

  // 2. Check all heuristic rules, pick highest confidence match
  let bestMatch = null;
  for (const rule of STATIC_RULES) {
    if (!rule.isCommand && rule.pattern.test(message)) {
      if (!bestMatch || rule.confidence > bestMatch.confidence) {
        bestMatch = {
          action: rule.action,
          confidence: rule.confidence,
          reason: `[static] ${rule.name}`,
        };
      }
    }
  }

  if (bestMatch) return bestMatch;

  // 3. Fallback
  return {
    action: "cheap",
    confidence: 0.3,
    reason: "[static] no pattern matched",
  };
}

function normalizeAction(action) {
  const map = {
    cheap_only: "cheap",
    cheap: "cheap",
    escalate: "escalation",
    escalation: "escalation",
    compare: "compare",
    draft: "draft",
    local: "local",
    manual_override: "manual",
    manual: "manual",
  };
  return map[action.toLowerCase()] || "cheap";
}

function resolveAction(action, cheapModel, escalationModel) {
  const mapping = {
    cheap: { type: "cheap", model: cheapModel },
    escalation: { type: "escalation", model: escalationModel },
    compare: { type: "compare", model: cheapModel },
    draft: { type: "draft", model: cheapModel },
    local: { type: "local", model: "local" },
    manual: { type: "cheap", model: cheapModel },
  };
  return mapping[action] || mapping.cheap;
}
```

### Port changes from Python:

| Python | JS | Reason |
|--------|-----|--------|
| `re.IGNORECASE \| re.DOTALL` | `/pattern/flags` with `i` and `s` | JS regex flags |
| `re.search(pattern, msg)` | `pattern.test(msg)` | Simpler, equivalent for our use |
| `_normalize_action()` | `normalizeAction()` | CamelCase JS convention |
| `resolve_action()` returns tuple | Returns object `{type, model}` | More idiomatic JS |
| `step.by.step` → `step\.?by\.?step` | More permissive regex | Handles both `step-by-step` and `step by step` |

All 14 rules ported with identical patterns and confidence values. Command prefix evaluation order preserved. Fallback behavior preserved.
