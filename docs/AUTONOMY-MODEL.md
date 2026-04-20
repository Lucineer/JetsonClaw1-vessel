# COCAPN AUTONOMY MODEL — 2026-04-05

## Human Monitoring Resolution

The human controls how much they see, at what granularity:

```
Autonomy Level 1 — LOG ONLY
  Agent works silently. Everything goes to logs.
  Human reviews later (or never).
  Use for: worldbuilding, data processing, bulk content generation

Autonomy Level 2 — TALLY
  Agent works silently. Increments counters.
  "12 files changed, 3 NPCs created, 1 quest chain completed"
  Human sees a dashboard, not a terminal.
  Use for: ongoing fleet maintenance, routine tasks

Autonomy Level 3 — NOTIFY
  Agent works. Logs everything. Notifies on notable events.
  "New equipment module proposed: compass-filter (confidence: 0.92)"
  Human gets pinged, can ignore or investigate.
  Use for: development work, PR reviews

Autonomy Level 4 — ASK
  Agent works. Asks before anything uncertain.
  "Should I add a water-breathing mechanic to the merfolk encounter?"
  Human approves/rejects each decision.
  Use for: creative work, important changes

Autonomy Level 5 — LIVE
  Every message streams to terminal in real time.
  Human reads along at their own speed.
  Use for: demos, debugging, learning, pair programming with AI
```

Human sets autonomy PER AGENT, PER TASK. The chatbot on a fishing boat runs at Level 1. The navigation system runs at Level 3. A coding session with Claude Code runs at Level 4 or 5.

## PR Review: The CTO Pattern

Coding agents (Claude Code, Codex, Aider) push to branches.
Cocapn agent reviews PRs asymmetrically — like a CTO scanning a large org's output:

```
1. Zero-shot changes (simple, obvious) → auto-merge, log only
   - Typo fixes, config changes, test additions
   - Confidence > 0.95

2. Low-risk changes → auto-merge, notify
   - New functions that pass tests, refactors
   - Confidence > 0.85

3. Medium-risk changes → queue for human review
   - New endpoints, schema changes, logic modifications
   - Confidence > 0.70

4. High-risk changes → block, ask human
   - Auth changes, API key handling, payment logic
   - Confidence < 0.70

5. Novel changes → flag as opportunity
   - "This contributor added a compass-filter module we don't have"
   - Surface to human: "New equipment from the community"
```

The human gets a morning briefing: "3 auto-merged, 1 queued for review, 1 novel contribution from @username." They scan for 30 seconds, approve the queued one, star the novel one.

## Memory Garbage Collection

Hot → Warm → Cold → Archived → Deleted

```
Hot memory (onboard, fast): ~100KB
  - Active session context, recent commands, current task state
  - TTL: session length

Warm memory (KV, fast): ~10MB
  - Recent work, PR history, equipment configs
  - TTL: 7 days

Cold memory (R2, cheap): ~1GB
  - Archived sessions, old PRs, generated content
  - TTL: 90 days, then compress

Archived (R2 Glacier or similar): unlimited
  - Compressed snapshots, training data
  - TTL: 1 year, then review

Garbage collection runs as cron heartbeat:
  - Every 6 hours: hot → warm promotion, cold eviction
  - Every day: warm → cold for stale data
  - Every week: cold → archive for old data
  - Every month: review archive, delete truly stale
```

Human sets cost allocation: "Keep my total storage under $2/month." The system auto-tiers to stay within budget. Active data stays hot. Old data compresses and cools.

## The Community Flywheel

```
Developer builds cool fork → pins to GitHub profile → gets stars
  → Stars attract other developers → they fork too
  → Novel features surface via PR review → human spots them
  → Best features get pulled into core fleet → recognition
  → Developer's resume has "built [feature] used by 10K people"
  → Developer becomes community hero → teaches others
  → More developers join → cycle repeats

Cocapn's role:
  - We host the playground (free tier)
  - We manage the connections (who forked what, what's trending)
  - We surface the best work (trending, stars, novel PRs)
  - We provide the infrastructure (KV, R2, Workers)
  - We take 0% of their work (optional 10% opt-in only)
  - We grow because the community grows
```

## Cloudflare Free Tier as On-Ramp

A power user can clone our repos, connect to their own Cloudflare account:
- Workers: 100K requests/day free
- KV: 100K reads/day, 1K writes/day free
- R2: 10GB storage, 10M reads/month free
- D1: 5GB storage, 5M reads/day free

If Cocapn is their ONLY thing on Cloudflare free tier:
- That's 100K API calls/day for free
- 10GB of assets (images, content, generated materials)
- Full CRUD for their agent's memory
- Zero cost until they scale past free limits

When they hit limits:
- $5/mo Workers Paid → 10M requests/day
- Still cheaper than managing their own infra
- Or they use BYOK with their own keys
- Or they upgrade to Cocapn managed ($10/mo)

## Easy Onboarding, Two Paths

### Path A: Managed (one click)
1. Sign up on cocapn.ai
2. We deploy vessels to our Cloudflare account
3. We manage keys, billing, storage
4. User gets custom domain: user.cocapn.ai
5. User never touches infrastructure

### Path B: Independent (fork and fly)
1. Fork repo on GitHub
2. Open Codespaces → agent is alive in 60 seconds
3. Or clone locally → run wrangler dev
4. Connect to YOUR Cloudflare account
5. Follow README for deploy
6. Add your own API keys or use Cocapn API
7. You own everything, we provide the community

Both paths lead to the same community. Both paths produce the same output.
Managed = convenience. Independent = control. Most power users choose independent.
