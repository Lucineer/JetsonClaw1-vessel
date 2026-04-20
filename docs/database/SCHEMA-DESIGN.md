# Database & Storage Schema Design — Log-Origin

> **Author:** Expert 1: Database & Storage Architect  
> **Date:** 2026-03-25  
> **Status:** Draft  
> **Engine:** Cloudflare D1 (SQLite at the edge)

---

## Table of Contents

1. [Schema Design](#1-schema-design)
   - 1.1 [sessions](#11-sessions)
   - 1.2 [messages](#12-messages)
   - 1.3 [pii_entities](#13-pii_entities)
   - 1.4 [interactions](#14-interactions)
   - 1.5 [feedback](#15-feedback)
   - 1.6 [routing_rules](#16-routing_rules)
   - 1.7 [user_preferences](#17-user_preferences)
   - 1.8 [providers](#18-providers)
   - 1.9 [agent_registry](#19-agent_registry)
   - 1.10 [agent_health](#110-agent_health)
   - 1.11 [training_exports](#111-training_exports)
   - 1.12 [schema_version](#112-schema_version)
   - 1.13 [ER Summary](#113-er-summary)
2. [D1-Specific Considerations](#2-d1-specific-considerations)
3. [Migration Strategy](#3-migration-strategy)
4. [Data Lifecycle](#4-data-lifecycle)
5. [Encryption at Rest](#5-encryption-at-rest)
6. [Performance Analysis](#6-performance-analysis)
7. [Devil's Advocate](#7-devils-advocate)
8. [Open Questions](#8-open-questions)

---

## 1. Schema Design

### 1.1 `sessions`

**Purpose:** Represents a conversation session — a bounded context for a series of messages between a user and the AI system. Sessions enable grouping messages for context, export, and archival.

| Column | Type | Nullable | Default | Purpose |
|--------|------|----------|---------|---------|
| `id` | TEXT | NO | — | Primary key. ULID for time-sortability and uniqueness without coordination. |
| `user_id` | TEXT | NO | — | Tenant isolation. Foreign key to external identity provider. |
| `title` | TEXT | YES | NULL | User-assigned or AI-generated session title. Display only. |
| `metadata` | TEXT | YES | `'{}'` | JSON blob for extensible session-level settings (model preference, system prompt overrides). |
| `status` | TEXT | NO | `'active'` | Enum: `active`, `archived`, `deleted`. Soft-delete support. |
| `created_at` | TEXT | NO | `now` | ISO-8601 timestamp. Session creation time. |
| `updated_at` | TEXT | NO | `now` | ISO-8601 timestamp. Last message or edit time. Bumped on every message insert. |
| `message_count` | INTEGER | NO | `0` | Denormalized count of messages. Avoids `COUNT(*)` on every session list query. |
| `last_message_at` | TEXT | YES | NULL | ISO-8601. Precise timestamp of the most recent message. Sorted for inbox ordering. |

**Indexes:**

| Index | Columns | Rationale |
|-------|---------|-----------|
| `pk_sessions` | `id` PRIMARY KEY | Lookup by ID (every message insert needs this). |
| `idx_sessions_user_updated` | `(user_id, updated_at DESC)` | Primary list query: "show my sessions, most recent first." Covers the dashboard. |
| `idx_sessions_user_status` | `(user_id, status)` | Filter sessions by status (e.g., list archived vs active). |
| `idx_sessions_last_message` | `(user_id, last_message_at DESC)` | Alternative sort: order by actual last message time rather than metadata update. |

**Why ULID not UUID?** ULIDs are lexicographically sortable by creation time. In SQLite, `TEXT` primary keys with ULIDs give us time-ordered inserts without an additional timestamp index. UUIDv7 would also work; ULID is chosen for ecosystem familiarity.

**Why `message_count` denormalized?** A session list page shows message counts. Without this, every list render requires `SELECT COUNT(*) FROM messages WHERE session_id = ?` per session — O(N) queries for N sessions. The denormalized count adds minimal write cost (one extra integer update on message insert/delete).

**DDL:**

```sql
CREATE TABLE sessions (
    id          TEXT NOT NULL PRIMARY KEY,
    user_id     TEXT NOT NULL,
    title       TEXT,
    metadata    TEXT NOT NULL DEFAULT '{}',
    status      TEXT NOT NULL DEFAULT 'active'
                CHECK(status IN ('active', 'archived', 'deleted')),
    created_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    message_count INTEGER NOT NULL DEFAULT 0,
    last_message_at TEXT
);

CREATE INDEX idx_sessions_user_updated ON sessions(user_id, updated_at DESC);
CREATE INDEX idx_sessions_user_status ON sessions(user_id, status);
CREATE INDEX idx_sessions_last_message ON sessions(user_id, last_message_at DESC);
```

---

### 1.2 `messages`

**Purpose:** Stores every message in a conversation — both user messages and AI responses. This is the highest-volume table.

| Column | Type | Nullable | Default | Purpose |
|--------|------|----------|---------|---------|
| `id` | TEXT | NO | — | Primary key. ULID. |
| `session_id` | TEXT | NO | — | FK → sessions.id. Groups messages into conversations. |
| `user_id` | TEXT | NO | — | Denormalized from session for direct filtering without JOIN. |
| `role` | TEXT | NO | — | Enum: `user`, `assistant`, `system`, `tool`. Message sender type. |
| `content` | TEXT | NO | — | Message body. Plain text or markdown. |
| `content_type` | TEXT | NO | `'text'` | Enum: `text`, `image_url`, `tool_call`, `tool_result`. Enables future multimodal support. |
| `token_count` | INTEGER | YES | NULL | Tokens in this message. NULL for user messages (not counted), populated for assistant responses. Used for cost tracking. |
| `model_id` | TEXT | YES | NULL | Which model generated this response. NULL for user messages. Cost attribution. |
| `interaction_id` | TEXT | YES | NULL | FK → interactions.id. Links to the routing/classification record. |
| `parent_id` | TEXT | YES | NULL | FK → messages.id. Supports branching/regeneration (user edits a previous message). |
| `metadata` | TEXT | YES | `'{}'` | JSON: tool calls, attachments, PII references, etc. |
| `created_at` | TEXT | NO | `now` | ISO-8601. Message timestamp. |

**Indexes:**

| Index | Columns | Rationale |
|-------|---------|-----------|
| `pk_messages` | `id` PRIMARY KEY | Direct lookup. |
| `idx_messages_session_created` | `(session_id, created_at ASC)` | Core query: load all messages in a session in chronological order. This is the hottest query path. |
| `idx_messages_user_created` | `(user_id, created_at DESC)` | Cross-session search: "find all my messages matching X." |
| `idx_messages_interaction` | `(interaction_id)` | Reverse lookup from interaction to its messages. |
| `idx_messages_parent` | `(parent_id)` | Branch traversal for regeneration trees. |

**Why `user_id` denormalized?** Searching messages across sessions by user would require JOINing through sessions. With `user_id` directly on messages, we can do single-table queries for user-level operations (search, export, deletion).

**Why `parent_id` for branching?** When a user regenerates a response, we need to track the message tree. A linear list would lose the branching structure. This enables showing the regeneration UI without a separate table.

**DDL:**

```sql
CREATE TABLE messages (
    id            TEXT NOT NULL PRIMARY KEY,
    session_id    TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    user_id       TEXT NOT NULL,
    role          TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'system', 'tool')),
    content       TEXT NOT NULL DEFAULT '',
    content_type  TEXT NOT NULL DEFAULT 'text'
                  CHECK(content_type IN ('text', 'image_url', 'tool_call', 'tool_result')),
    token_count   INTEGER,
    model_id      TEXT,
    interaction_id TEXT REFERENCES interactions(id) ON DELETE SET NULL,
    parent_id     TEXT REFERENCES messages(id) ON DELETE SET NULL,
    metadata      TEXT NOT NULL DEFAULT '{}',
    created_at    TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE INDEX idx_messages_session_created ON messages(session_id, created_at ASC);
CREATE INDEX idx_messages_user_created ON messages(user_id, created_at DESC);
CREATE INDEX idx_messages_interaction ON messages(interaction_id);
CREATE INDEX idx_messages_parent ON messages(parent_id);
```

---

### 1.3 `pii_entities`

**Purpose:** Maps PII entity IDs (used in prompts sent to models) to their real values, encrypted at rest. When the system detects PII in a message, it replaces the real value with a placeholder like `[PII:abc123]` and stores the mapping here.

| Column | Type | Nullable | Default | Purpose |
|--------|------|----------|---------|---------|
| `id` | TEXT | NO | — | Primary key. The entity ID used in prompts (e.g., `abc123`). |
| `user_id` | TEXT | NO | — | Owner of this PII entity. |
| `entity_type` | TEXT | NO | — | Enum: `email`, `phone`, `name`, `address`, `ssn`, `custom`. Classification of the PII. |
| `display_label` | TEXT | YES | NULL | User-visible label (e.g., "My Email", "Home Phone"). Shown in the privacy vault UI. |
| `encrypted_value` | TEXT | NO | — | AES-256-GCM encrypted real value. Base64-encoded. Application-layer encryption; D1 sees ciphertext. |
| `key_id` | TEXT | NO | — | References the encryption key version used. Enables key rotation without re-encrypting everything at once. |
| `usage_count` | INTEGER | NO | `0` | How many times this entity has been referenced in messages. For analytics and cache eviction. |
| `last_used_at` | TEXT | YES | NULL | ISO-8601. Last time this entity was referenced. |
| `created_at` | TEXT | NO | `now` | ISO-8601. |
| `expires_at` | TEXT | YES | NULL | ISO-8601. Optional TTL for ephemeral PII (e.g., OTPs). |

**Indexes:**

| Index | Columns | Rationale |
|-------|---------|-----------|
| `pk_pii` | `id` PRIMARY KEY | Lookup by entity ID (needed on every message that references PII). |
| `idx_pii_user_type` | `(user_id, entity_type)` | List all PII of a type for a user (privacy vault UI). |
| `idx_pii_user_label` | `(user_id, display_label)` | Search PII by label. |

**Why not a hash index on the real value?** The real value is encrypted; we can't index it. The entity ID is generated per-detection event. If the same email appears in two messages, we ideally want the same entity ID — but that requires fuzzy matching on the plaintext, which we can't do at the DB layer. The application layer handles deduplication by normalizing and hashing the plaintext before generating the entity ID.

**DDL:**

```sql
CREATE TABLE pii_entities (
    id              TEXT NOT NULL PRIMARY KEY,
    user_id         TEXT NOT NULL,
    entity_type     TEXT NOT NULL CHECK(entity_type IN ('email', 'phone', 'name', 'address', 'ssn', 'custom')),
    display_label   TEXT,
    encrypted_value TEXT NOT NULL,
    key_id          TEXT NOT NULL,
    usage_count     INTEGER NOT NULL DEFAULT 0,
    last_used_at    TEXT,
    created_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    expires_at      TEXT
);

CREATE INDEX idx_pii_user_type ON pii_entities(user_id, entity_type);
CREATE INDEX idx_pii_user_label ON pii_entities(user_id, display_label);
```

---

### 1.4 `interactions`

**Purpose:** Records every AI model interaction — the metadata about what happened when a message was routed to a model. This is the observability and routing intelligence table.

| Column | Type | Nullable | Default | Purpose |
|--------|------|----------|---------|---------|
| `id` | TEXT | NO | — | Primary key. ULID. |
| `user_id` | TEXT | NO | — | Tenant. |
| `session_id` | TEXT | NO | — | FK → sessions. Context for the interaction. |
| `message_id` | TEXT | YES | NULL | FK → messages.id. The specific assistant message produced. |
| `provider_id` | TEXT | NO | — | FK → providers. Which provider was used. |
| `model_id` | TEXT | NO | — | Model identifier (e.g., `gpt-4o`, `claude-3-opus`). |
| `routing_reason` | TEXT | NO | — | Why this provider/model was chosen. Enum: `default`, `cost_optimized`, `quality_required`, `user_preference`, `fallback`, `rule_match`, `learned`. |
| `classification` | TEXT | YES | NULL | Task classification: `code`, `creative`, `factual`, `math`, `conversation`, `unknown`. Used for routing analytics. |
| `input_tokens` | INTEGER | YES | NULL | Tokens sent to the model. |
| `output_tokens` | INTEGER | YES | NULL | Tokens received. |
| `latency_ms` | INTEGER | YES | NULL | End-to-end latency in milliseconds. |
| `cost_usd` | REAL | YES | NULL | Estimated cost in USD. |
| `status` | TEXT | NO | `'success'` | Enum: `success`, `error`, `timeout`, `rate_limited`. |
| `error_detail` | TEXT | YES | NULL | Error message if status != success. |
| `metadata` | TEXT | YES | `'{}'` | JSON: routing scores, A/B test info, etc. |
| `created_at` | TEXT | NO | `now` | ISO-8601. |

**Indexes:**

| Index | Columns | Rationale |
|-------|---------|-----------|
| `pk_interactions` | `id` PRIMARY KEY | Lookup. |
| `idx_interactions_user_created` | `(user_id, created_at DESC)` | User's interaction history / analytics. |
| `idx_interactions_session` | `(session_id, created_at ASC)` | All interactions in a session (for session replay/debug). |
| `idx_interactions_provider` | `(provider_id, created_at DESC)` | Provider-level analytics (cost, latency, error rate). |
| `idx_interactions_status` | `(status, created_at DESC)` | Error monitoring dashboard. |
| `idx_interactions_routing` | `(routing_reason, created_at DESC)` | Routing analytics — how often each reason triggers. |

**DDL:**

```sql
CREATE TABLE interactions (
    id              TEXT NOT NULL PRIMARY KEY,
    user_id         TEXT NOT NULL,
    session_id      TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    message_id      TEXT REFERENCES messages(id) ON DELETE SET NULL,
    provider_id     TEXT NOT NULL REFERENCES providers(id) ON DELETE RESTRICT,
    model_id        TEXT NOT NULL,
    routing_reason  TEXT NOT NULL
                    CHECK(routing_reason IN ('default', 'cost_optimized', 'quality_required', 'user_preference', 'fallback', 'rule_match', 'learned')),
    classification  TEXT
                    CHECK(classification IN ('code', 'creative', 'factual', 'math', 'conversation', 'unknown')),
    input_tokens    INTEGER,
    output_tokens   INTEGER,
    latency_ms      INTEGER,
    cost_usd        REAL,
    status          TEXT NOT NULL DEFAULT 'success'
                    CHECK(status IN ('success', 'error', 'timeout', 'rate_limited')),
    error_detail    TEXT,
    metadata        TEXT NOT NULL DEFAULT '{}',
    created_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE INDEX idx_interactions_user_created ON interactions(user_id, created_at DESC);
CREATE INDEX idx_interactions_session ON interactions(session_id, created_at ASC);
CREATE INDEX idx_interactions_provider ON interactions(provider_id, created_at DESC);
CREATE INDEX idx_interactions_status ON interactions(status, created_at DESC);
CREATE INDEX idx_interactions_routing ON interactions(routing_reason, created_at DESC);
```

---

### 1.5 `feedback`

**Purpose:** Stores user feedback on AI responses — thumbs up/down, rankings, and textual critiques. This feeds into model evaluation and routing optimization.

| Column | Type | Nullable | Default | Purpose |
|--------|------|----------|---------|---------|
| `id` | TEXT | NO | — | Primary key. ULID. |
| `user_id` | TEXT | NO | — | Who gave the feedback. |
| `interaction_id` | TEXT | NO | — | FK → interactions. What the feedback is about. |
| `message_id` | TEXT | YES | NULL | FK → messages. Optional direct link to a message. |
| `rating` | INTEGER | NO | — | 1–5 scale. 1 = terrible, 5 = excellent. |
| `thumbs_up` | BOOLEAN | YES | NULL | Simple binary feedback. NULL if only rating given. |
| `critique` | TEXT | YES | NULL | Free-text feedback from the user. |
| `tags` | TEXT | YES | `'[]'` | JSON array of user-assigned tags (e.g., `["hallucination", "slow"]`). |
| `created_at` | TEXT | NO | `now` | ISO-8601. |

**Indexes:**

| Index | Columns | Rationale |
|-------|---------|-----------|
| `pk_feedback` | `id` PRIMARY KEY | Lookup. |
| `idx_feedback_interaction` | `(interaction_id)` | One feedback per interaction (typically). |
| `idx_feedback_user_created` | `(user_id, created_at DESC)` | User's feedback history. |
| `idx_feedback_rating` | `(rating)` | Aggregate analytics: average rating per model/provider. |

**DDL:**

```sql
CREATE TABLE feedback (
    id             TEXT NOT NULL PRIMARY KEY,
    user_id        TEXT NOT NULL,
    interaction_id TEXT NOT NULL REFERENCES interactions(id) ON DELETE CASCADE,
    message_id     TEXT REFERENCES messages(id) ON DELETE SET NULL,
    rating         INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
    thumbs_up      BOOLEAN,
    critique       TEXT,
    tags           TEXT NOT NULL DEFAULT '[]',
    created_at     TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE INDEX idx_feedback_interaction ON feedback(interaction_id);
CREATE INDEX idx_feedback_user_created ON feedback(user_id, created_at DESC);
CREATE INDEX idx_feedback_rating ON feedback(rating);
```

---

### 1.6 `routing_rules`

**Purpose:** Stores routing rules that determine which provider/model to use for a given request. Rules can be static (user-configured) or learned (derived from interaction analytics).

| Column | Type | Nullable | Default | Purpose |
|--------|------|----------|---------|---------|
| `id` | TEXT | NO | — | Primary key. ULID. |
| `user_id` | TEXT | YES | NULL | NULL = global/system rule. Non-null = user-specific override. |
| `name` | TEXT | NO | — | Human-readable rule name. |
| `description` | TEXT | YES | NULL | What this rule does. |
| `rule_type` | TEXT | NO | — | Enum: `static`, `learned`, `ab_test`. |
| `condition` | TEXT | NO | — | JSON: match expression (e.g., `{"classification": "code", "min_tokens": 100}`). Evaluated by the router. |
| `action` | TEXT | NO | — | JSON: routing action (e.g., `{"provider_id": "anthropic", "model_id": "claude-3-opus"}`). |
| `priority` | INTEGER | NO | `0` | Higher priority rules evaluated first. |
| `weight` | REAL | YES | NULL | For A/B tests: traffic split weight (0.0–1.0). |
| `is_active` | BOOLEAN | NO | `1` | Enable/disable without deletion. |
| `hit_count` | INTEGER | NO | `0` | How many times this rule matched. Performance tracking. |
| `success_count` | INTEGER | NO | `0` | How many matched interactions succeeded. |
| `avg_rating` | REAL | YES | NULL | Average feedback rating for interactions matching this rule. |
| `created_at` | TEXT | NO | `now` | ISO-8601. |
| `updated_at` | TEXT | NO | `now` | ISO-8601. |

**Indexes:**

| Index | Columns | Rationale |
|-------|---------|-----------|
| `pk_rules` | `id` PRIMARY KEY | Lookup. |
| `idx_rules_user_priority` | `(user_id, priority DESC)` | Rule evaluation order per user. NULL user_id sorts first (global rules). |
| `idx_rules_active` | `(is_active, priority DESC)` | Fetch only active rules for the router. |
| `idx_rules_type` | `(rule_type)` | Analytics: separate static from learned rules. |

**Why JSON conditions instead of a normalized condition table?** Conditions are evaluated in application code, not SQL. A normalized `conditions` table would require multiple JOINs to reconstruct a rule, and the condition structure is variable (different fields for different match types). JSON is the pragmatic choice — queryable with D1's `json_extract()` for simple cases.

**DDL:**

```sql
CREATE TABLE routing_rules (
    id           TEXT NOT NULL PRIMARY KEY,
    user_id      TEXT,
    name         TEXT NOT NULL,
    description  TEXT,
    rule_type    TEXT NOT NULL CHECK(rule_type IN ('static', 'learned', 'ab_test')),
    condition    TEXT NOT NULL,
    action       TEXT NOT NULL,
    priority     INTEGER NOT NULL DEFAULT 0,
    weight       REAL CHECK(weight BETWEEN 0.0 AND 1.0),
    is_active    BOOLEAN NOT NULL DEFAULT 1,
    hit_count    INTEGER NOT NULL DEFAULT 0,
    success_count INTEGER NOT NULL DEFAULT 0,
    avg_rating   REAL,
    created_at   TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at   TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE INDEX idx_rules_user_priority ON routing_rules(user_id, priority DESC);
CREATE INDEX idx_rules_active ON routing_rules(is_active, priority DESC);
CREATE INDEX idx_rules_type ON routing_rules(rule_type);
```

---

### 1.7 `user_preferences`

**Purpose:** Key-value store for per-user settings. Kept simple — no need for a complex settings table when the number of preferences is bounded and the access pattern is "load all for this user."

| Column | Type | Nullable | Default | Purpose |
|--------|------|----------|---------|---------|
| `id` | TEXT | NO | — | Primary key. Auto-increment surrogate (internal). |
| `user_id` | TEXT | NO | — | Tenant. |
| `key` | TEXT | NO | — | Preference key (e.g., `default_model`, `theme`, `language`, `privacy_level`). |
| `value` | TEXT | NO | — | Preference value. Always TEXT; application handles type coercion. |
| `updated_at` | TEXT | NO | `now` | ISO-8601. |

**Indexes:**

| Index | Columns | Rationale |
|-------|---------|-----------|
| `pk_prefs` | `id` PRIMARY KEY | Internal. |
| `uq_prefs_user_key` | `(user_id, key)` UNIQUE | One value per key per user. Primary access pattern. |

**Why not use KV?** KV could work here, but preferences are part of the user's data boundary — they need to be included in GDPR exports and deletions alongside the rest of the user's data. Keeping them in D1 simplifies data lifecycle management.

**DDL:**

```sql
CREATE TABLE user_preferences (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    TEXT NOT NULL,
    key        TEXT NOT NULL,
    value      TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    UNIQUE(user_id, key)
);

CREATE INDEX idx_prefs_user ON user_preferences(user_id);
```

---

### 1.8 `providers`

**Purpose:** Registry of configured AI providers — their endpoints, credentials, and capabilities. This is a small, infrequently-changing table.

| Column | Type | Nullable | Default | Purpose |
|--------|------|----------|---------|---------|
| `id` | TEXT | NO | — | Primary key. Slug (e.g., `anthropic`, `openai`, `local-llama`). |
| `name` | TEXT | NO | — | Display name. |
| `provider_type` | TEXT | NO | — | Enum: `cloud`, `local`, `proxy`. |
| `base_url` | TEXT | NO | — | API endpoint URL. |
| `encrypted_api_key` | TEXT | YES | NULL | AES-256-GCM encrypted API key. Application-layer encryption. |
| `key_id` | TEXT | YES | NULL | Encryption key version for the API key. |
| `models` | TEXT | NO | `'[]'` | JSON array of supported model IDs and their metadata. |
| `capabilities` | TEXT | NO | `'{}'` | JSON: feature flags (e.g., `{"streaming": true, "vision": false}`). |
| `rate_limit_rpm` | INTEGER | YES | NULL | Requests per minute limit. Self-enforced; does not guarantee provider limit. |
| `priority` | INTEGER | NO | `0` | Default routing priority. Higher = preferred. |
| `is_active` | BOOLEAN | NO | `1` | Enable/disable. |
| `created_at` | TEXT | NO | `now` | ISO-8601. |
| `updated_at` | TEXT | NO | `now` | ISO-8601. |

**Indexes:**

| Index | Columns | Rationale |
|-------|---------|-----------|
| `pk_providers` | `id` PRIMARY KEY | Lookup by provider slug. |
| `idx_providers_active` | `(is_active, priority DESC)` | Router needs the list of active providers in priority order. |

**DDL:**

```sql
CREATE TABLE providers (
    id                TEXT NOT NULL PRIMARY KEY,
    name              TEXT NOT NULL,
    provider_type     TEXT NOT NULL CHECK(provider_type IN ('cloud', 'local', 'proxy')),
    base_url          TEXT NOT NULL,
    encrypted_api_key TEXT,
    key_id            TEXT,
    models            TEXT NOT NULL DEFAULT '[]',
    capabilities      TEXT NOT NULL DEFAULT '{}',
    rate_limit_rpm    INTEGER,
    priority          INTEGER NOT NULL DEFAULT 0,
    is_active         BOOLEAN NOT NULL DEFAULT 1,
    created_at        TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at        TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE INDEX idx_providers_active ON providers(is_active, priority DESC);
```

---

### 1.9 `agent_registry`

**Purpose:** Registry of connected AI agents — both local (on-user-device) and cloud (serverless). Agents are the "who" that can handle conversations.

| Column | Type | Nullable | Default | Purpose |
|--------|------|----------|---------|---------|
| `id` | TEXT | NO | — | Primary key. ULID. |
| `user_id` | TEXT | NO | — | Owner of this agent. |
| `name` | TEXT | NO | — | Human-readable agent name. |
| `agent_type` | TEXT | NO | — | Enum: `local`, `cloud`, `hybrid`. |
| `endpoint` | TEXT | YES | NULL | URL for cloud agents. NULL for local-only. |
| `capabilities` | TEXT | NO | `'[]'` | JSON array of capabilities (e.g., `["code", "web_search", "image_gen"]`). |
| `config` | TEXT | NO | `'{}'` | JSON: agent-specific configuration (model overrides, system prompts, tool configs). |
| `is_active` | BOOLEAN | NO | `1` | Currently available for routing. |
| `last_seen_at` | TEXT | YES | NULL | ISO-8601. Last heartbeat. |
| `created_at` | TEXT | NO | `now` | ISO-8601. |
| `updated_at` | TEXT | NO | `now` | ISO-8601. |

**Indexes:**

| Index | Columns | Rationale |
|-------|---------|-----------|
| `pk_agents` | `id` PRIMARY KEY | Lookup. |
| `idx_agents_user_active` | `(user_id, is_active)` | List available agents for a user. |
| `idx_agents_type` | `(agent_type)` | Filter by agent type for analytics. |

**DDL:**

```sql
CREATE TABLE agent_registry (
    id            TEXT NOT NULL PRIMARY KEY,
    user_id       TEXT NOT NULL,
    name          TEXT NOT NULL,
    agent_type    TEXT NOT NULL CHECK(agent_type IN ('local', 'cloud', 'hybrid')),
    endpoint      TEXT,
    capabilities  TEXT NOT NULL DEFAULT '[]',
    config        TEXT NOT NULL DEFAULT '{}',
    is_active     BOOLEAN NOT NULL DEFAULT 1,
    last_seen_at  TEXT,
    created_at    TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at    TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE INDEX idx_agents_user_active ON agent_registry(user_id, is_active);
CREATE INDEX idx_agents_type ON agent_registry(agent_type);
```

---

### 1.10 `agent_health`

**Purpose:** Time-series heartbeat and health check data for agents. High write volume — one row per heartbeat per agent.

| Column | Type | Nullable | Default | Purpose |
|--------|------|----------|---------|---------|
| `id` | TEXT | NO | — | Primary key. ULID. |
| `agent_id` | TEXT | NO | — | FK → agent_registry.id. |
| `user_id` | TEXT | NO | — | Denormalized for partition pruning in queries. |
| `status` | TEXT | NO | `'healthy'` | Enum: `healthy`, `degraded`, `unhealthy`, `offline`. |
| `latency_ms` | INTEGER | YES | NULL | Round-trip latency of the health check. |
| `metadata` | TEXT | YES | `'{}'` | JSON: CPU usage, memory, error details, etc. |
| `created_at` | TEXT | NO | `now` | ISO-8601. |

**Indexes:**

| Index | Columns | Rationale |
|-------|---------|-----------|
| `pk_health` | `id` PRIMARY KEY | Lookup. |
| `idx_health_agent_created` | `(agent_id, created_at DESC)` | Most recent health checks for an agent. |
| `idx_health_user_status` | `(user_id, status, created_at DESC)` | "Show me all unhealthy agents" for a user. |

**Data volume concern:** At 1 heartbeat/minute/agent with 10 agents, that's 14,400 rows/day. At 1 heartbeat/10s (aggressive), it's 86,400/day. Over a year: 31.5M rows. This table WILL be the largest. Mitigation: TTL cleanup (see §4), and consider R2 archival for health data older than 30 days.

**DDL:**

```sql
CREATE TABLE agent_health (
    id          TEXT NOT NULL PRIMARY KEY,
    agent_id    TEXT NOT NULL REFERENCES agent_registry(id) ON DELETE CASCADE,
    user_id     TEXT NOT NULL,
    status      TEXT NOT NULL DEFAULT 'healthy'
                CHECK(status IN ('healthy', 'degraded', 'unhealthy', 'offline')),
    latency_ms  INTEGER,
    metadata    TEXT NOT NULL DEFAULT '{}',
    created_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE INDEX idx_health_agent_created ON agent_health(agent_id, created_at DESC);
CREATE INDEX idx_health_user_status ON agent_health(user_id, status, created_at DESC);
```

---

### 1.11 `training_exports`

**Purpose:** Tracks exports of training/evaluation data. When a user or admin exports interaction data for model evaluation, this table records what was exported, when, and by whom.

| Column | Type | Nullable | Default | Purpose |
|--------|------|----------|---------|---------|
| `id` | TEXT | NO | — | Primary key. ULID. |
| `user_id` | TEXT | NO | — | Who initiated the export. |
| `export_type` | TEXT | NO | — | Enum: `full`, `sampled`, `feedback_only`, `interactions_with_ratings`. |
| `format` | TEXT | NO | `'jsonl'` | Enum: `jsonl`, `csv`, `parquet`. |
| `record_count` | INTEGER | NO | `0` | Number of records exported. |
| `file_size_bytes` | INTEGER | YES | NULL | Size of the exported file. |
| `storage_key` | TEXT | YES | NULL | R2 key where the export file is stored. |
| `filters` | TEXT | YES | `'{}'` | JSON: what filters were applied (date range, model, rating range). |
| `status` | TEXT | NO | `'pending'` | Enum: `pending`, `processing`, `completed`, `failed`, `expired`. |
| `expires_at` | TEXT | YES | NULL | When the export file should be deleted from R2. |
| `created_at` | TEXT | NO | `now` | ISO-8601. |
| `completed_at` | TEXT | YES | NULL | ISO-8601. |

**Indexes:**

| Index | Columns | Rationale |
|-------|---------|-----------|
| `pk_exports` | `id` PRIMARY KEY | Lookup. |
| `idx_exports_user_created` | `(user_id, created_at DESC)` | User's export history. |
| `idx_exports_status` | `(status)` | Admin dashboard: find pending/failed exports. |

**DDL:**

```sql
CREATE TABLE training_exports (
    id              TEXT NOT NULL PRIMARY KEY,
    user_id         TEXT NOT NULL,
    export_type     TEXT NOT NULL
                    CHECK(export_type IN ('full', 'sampled', 'feedback_only', 'interactions_with_ratings')),
    format          TEXT NOT NULL DEFAULT 'jsonl'
                    CHECK(format IN ('jsonl', 'csv', 'parquet')),
    record_count    INTEGER NOT NULL DEFAULT 0,
    file_size_bytes INTEGER,
    storage_key     TEXT,
    filters         TEXT NOT NULL DEFAULT '{}',
    status          TEXT NOT NULL DEFAULT 'pending'
                    CHECK(status IN ('pending', 'processing', 'completed', 'failed', 'expired')),
    expires_at      TEXT,
    created_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    completed_at    TEXT
);

CREATE INDEX idx_exports_user_created ON training_exports(user_id, created_at DESC);
CREATE INDEX idx_exports_status ON training_exports(status);
```

---

### 1.12 `schema_version`

**Purpose:** Tracks which schema migrations have been applied to the database. This is the migration bookkeeping table.

| Column | Type | Nullable | Default | Purpose |
|--------|------|----------|---------|---------|
| `version` | INTEGER | NO | — | Sequential migration number. |
| `name` | TEXT | NO | — | Human-readable migration name (e.g., `create_sessions_table`). |
| `checksum` | TEXT | NO | — | SHA-256 of the migration SQL. Detects tampering or drift. |
| `applied_at` | TEXT | NO | `now` | ISO-8601. When the migration ran. |
| `rollback_sql` | TEXT | YES | NULL | SQL to undo this migration, if possible. |

**Indexes:**

| Index | Columns | Rationale |
|-------|---------|-----------|
| `pk_version` | `version` PRIMARY KEY | Lookup and ordering. |

**DDL:**

```sql
CREATE TABLE schema_version (
    version      INTEGER PRIMARY KEY,
    name         TEXT NOT NULL,
    checksum     TEXT NOT NULL,
    applied_at   TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    rollback_sql TEXT
);
```

---

### 1.13 ER Summary

```
sessions 1──* messages
sessions 1──* interactions
messages ?──1 interactions  (via interaction_id)
messages ?──1 messages      (via parent_id, self-referential)
interactions *──1 providers
interactions 1──* feedback
agent_registry 1──* agent_health
```

All tables have `user_id` for tenant isolation. Foreign keys use `ON DELETE CASCADE` where child data should not outlive the parent (messages → sessions, feedback → interactions), `ON DELETE SET NULL` where the reference is informational and can survive parent deletion (messages.interaction_id), and `ON DELETE RESTRICT` where deletion would be a logic error (interactions → providers).

---

## 2. D1-Specific Considerations

### 2.1 Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| **No ATTACH DATABASE** | Can't split data across files | Single-database design; use R2 for overflow |
| **No extensions** | No full-text search (FTS5), no JSON1 tricks | Use D1's built-in `json_extract()` (available via Cloudflare's build). For FTS, use Cloudflare Vectorize or application-level search |
| **No WAL mode on edge** | Readers block writers | Acceptable for our write pattern (single-writer-per-row from Worker); D1's internal serialization handles this |
| **10 GB max database size** | Hard cap on storage | Aggressive archival to R2 (see §4); monitor size |
| **No ALTER TABLE DROP COLUMN** | Can't remove columns easily | Mark columns as deprecated; add new columns; handle in application layer |
| **No window functions in early versions** | Analytics queries limited | Use subqueries; materialized views via Workers + KV cache |
| **Single-region primary** | Write latency from non-primary regions | Writes go through Workers which route to primary; reads can be local |

### 2.2 Connection Pooling

D1 handles connection pooling internally. The application never manages connections — it calls `env.DB.prepare(sql).bind(...).run()` from a Worker, and D1's infrastructure handles the rest.

**Implications:**
- No connection string configuration
- No pool size tuning
- No connection timeout management
- **No long-running transactions** — Workers have a CPU time limit (~30s for paid), so transactions must complete quickly
- **No read-after-write consistency guarantees across requests** — D1 uses eventual consistency for reads from replicas. Writes are committed to the primary; reads may lag by milliseconds. Use `RETURNING` clauses to get authoritative post-write data.

### 2.3 Transaction Boundaries

We need atomic writes in these scenarios:

| Scenario | What's Atomic | Rationale |
|----------|--------------|-----------|
| **Message insert** | Insert message + update `sessions.message_count` + update `sessions.last_message_at` + update `sessions.updated_at` | Session metadata must be consistent with message state |
| **Interaction complete** | Insert interaction + update `messages.interaction_id` + update `messages.token_count` + update `routing_rules.hit_count` | All metadata must be written together |
| **Feedback submission** | Insert feedback + update `routing_rules.success_count` + recalculate `routing_rules.avg_rating` | Rating analytics consistency |
| **PII detection** | Insert pii_entity + update message content (replace with placeholder) | Must not have a message with unresolved PII references |
| **Agent health update** | Insert agent_health + update `agent_registry.last_seen_at` | Status must be current |

All of these are single-Worker-request operations and should use D1's `batch()` API, which executes statements in a single transaction.

### 2.4 Read Replicas

D1 automatically creates read replicas in regions where the database is accessed. The application doesn't configure replicas.

**When replica reads are fine:**
- Loading session list (slightly stale `updated_at` is acceptable)
- Loading message history (messages are immutable once written)
- Loading user preferences (rarely changes)

**When you need primary reads (use `D1_DATABASE` with read-your-writes):**
- Immediately after a write in the same request (use the response, not a re-read)
- The `RETURNING` clause returns authoritative data

### 2.5 Cost Minimization

D1 pricing (as of 2025): $0.75/million rows read, $1.25/million rows written, $0.50/million rows stored/month.

**Strategies:**
- **Batch reads:** Use `batch()` to combine multiple queries into one HTTP round-trip to D1
- **Denormalization:** `message_count`, `last_message_at` on sessions avoid COUNT queries
- **Selective indexing:** Every index costs writes and storage. Only index hot query paths
- **Pagination:** Never `SELECT * FROM messages WHERE session_id = ?` without LIMIT
- **Archive aggressively:** Move data older than the active window to R2
- **Avoid ORMs that generate N+1:** Use raw SQL or a query builder that supports JOINs

---

## 3. Migration Strategy

### 3.1 Schema Version Tracking

The `schema_version` table (§1.12) tracks applied migrations. Each migration is:

```sql
-- Migration 001: create_sessions_table
-- Checksum: <sha256 of this SQL>

CREATE TABLE sessions (...);
CREATE INDEX ...;

INSERT INTO schema_version (version, name, checksum, rollback_sql)
VALUES (1, 'create_sessions_table', '<sha256>', 'DROP TABLE sessions;');
```

### 3.2 Migration Tooling

**Recommendation:** Use **drizzle-orm** with **drizzle-kit** for schema definition and migration generation, but with manual review.

**Workflow:**
1. Define schema in Drizzle TypeScript (`schema.ts`)
2. Run `drizzle-kit generate` to produce SQL migration files
3. **Review every generated migration** — Drizzle's SQLite support can produce surprising ALTER TABLE statements
4. Apply migrations via a Worker that reads migration files in order, checks `schema_version`, and applies pending ones

**Why not purely manual SQL?** Drizzle provides type safety in application code. The migration generator reduces boilerplate. But D1 has enough quirks (no DROP COLUMN, limited ALTER TABLE) that manual review is essential.

### 3.3 Data Transformation Migrations

When a migration needs to transform data (not just add/modify schema):

```sql
-- Migration 015: add_cost_tracking
-- Adds cost_usd to interactions, backfills from token counts

BEGIN;

-- Add new column (nullable first)
ALTER TABLE interactions ADD COLUMN cost_usd REAL;

-- Backfill: rough cost estimate based on model pricing
UPDATE interactions SET cost_usd = CASE
    WHEN model_id LIKE 'gpt-4%' THEN (input_tokens * 0.00003 + output_tokens * 0.00006)
    WHEN model_id LIKE 'claude%' THEN (input_tokens * 0.000008 + output_tokens * 0.000024)
    ELSE NULL
END
WHERE cost_usd IS NULL AND input_tokens IS NOT NULL;

-- Make non-nullable after backfill
-- Note: D1 doesn't support ALTER TABLE ... NOT NULL
-- This constraint must be enforced at the application layer

COMMIT;
```

**Important:** D1 doesn't support `ALTER TABLE ADD COLUMN ... NOT NULL DEFAULT value` for all cases. Add columns as nullable, backfill, then enforce in application code.

### 3.4 Rollback Strategy

D1 does support `DROP TABLE`, but it's destructive and there's no undo. Our approach:

1. **Every migration stores `rollback_sql`** in `schema_version` (when possible)
2. **Additive-only schema changes** where feasible — don't drop columns, add new ones and migrate data
3. **Soft-delete for tables:** Add a `status = 'deprecated'` column instead of dropping
4. **Data backup before destructive migrations:** Export to R2 before running DROP/ALTER
5. **Test migrations on a staging D1 instance** before production

**Rollback priority (safest to riskiest):**
1. Application-layer rollback (change code, leave schema as-is) — **preferred**
2. Additive rollback (add a new column, migrate data back) — safe
3. Destructive rollback (DROP TABLE, DROP INDEX) — last resort, requires R2 backup

---

## 4. Data Lifecycle

### 4.1 Retention Policy

| Data Type | Default Retention | Configurable? | Rationale |
|-----------|------------------|---------------|-----------|
| Sessions (active) | Indefinite | Yes | Core user data |
| Messages | 90 days in D1, archived to R2 | Yes | Hot data in D1 for fast queries; cold data in R2 |
| PII entities | Until user deletes or account closes | No (privacy requirement) | Must persist as long as referenced data exists |
| Interactions | 30 days in D1, archived to R2 | Yes | Analytics data; cold quickly |
| Feedback | Indefinite (in R2 after 90 days) | Yes | Valuable for long-term model evaluation |
| Agent health | 7 days in D1, archived to R2 | No | Time-series; only recent data useful |
| Training exports | 30 days (auto-delete from R2) | Yes | Temporary artifacts |
| Routing rules | Indefinite | N/A | Configuration data |

### 4.2 GDPR / Right to Be Forgotten

**Deletion request flow:**

1. User requests account deletion
2. Worker marks user as `status = 'deleting'` (grace period: 30 days)
3. **Cascade delete from D1:**
   ```sql
   DELETE FROM messages WHERE user_id = ?;
   DELETE FROM sessions WHERE user_id = ?;
   DELETE FROM pii_entities WHERE user_id = ?;
   DELETE FROM interactions WHERE user_id = ?;
   DELETE FROM feedback WHERE user_id = ?;
   DELETE FROM routing_rules WHERE user_id = ?;
   DELETE FROM user_preferences WHERE user_id = ?;
   DELETE FROM agent_health WHERE user_id = ?;
   DELETE FROM agent_registry WHERE user_id = ?;
   DELETE FROM training_exports WHERE user_id = ?;
   ```
4. **Delete from R2:** Enumerate and delete all user objects in the `users/{user_id}/` prefix
5. **Delete PII encryption keys** from the key management store
6. **Confirm deletion:** Mark user record as `status = 'deleted'` in external identity store

**Transaction:** Wrap step 3 in a single D1 `batch()` call. This is a one-time operation, so the transaction size is acceptable.

### 4.3 Archival Strategy (D1 → R2)

**Mechanism:** A Cron Trigger (Cloudflare Workers) runs daily to archive old data.

```javascript
// Pseudocode for archival worker
export default {
  async scheduled(event, env, ctx) {
    const cutoff = new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString();

    // Archive old messages to R2
    const oldMessages = await env.DB.prepare(
      'SELECT * FROM messages WHERE created_at < ?'
    ).bind(cutoff).all();

    if (oldMessages.results.length > 0) {
      const batchKey = `archives/messages/${Date.now()}.jsonl`;
      const jsonl = oldMessages.results.map(m => JSON.stringify(m)).join('\n');
      await env.ARCHIVE_BUCKET.put(batchKey, jsonl);

      // Delete archived messages from D1 (batched, 100 at a time)
      await env.DB.prepare(
        'DELETE FROM messages WHERE created_at < ?'
      ).bind(cutoff).run();
    }
  }
};
```

**R2 key structure:**
```
archives/
  messages/{year}/{month}/{day}.jsonl
  interactions/{year}/{month}/{day}.jsonl
  health/{year}/{month}/{day}.jsonl
  users/{user_id}/export_{timestamp}.jsonl
```

### 4.4 Database Size Management

**Monitoring:** Daily cron checks database size:
```sql
SELECT page_count * page_size as size_bytes
FROM pragma_database_list(), pragma_page_count(), pragma_page_size();
```

**Alert thresholds:**
- 5 GB: Warning — review archival policies
- 7 GB: Critical — force archival of oldest data
- 9 GB: Emergency — disable non-essential writes, force archive

**Proactive measures:**
- Vacuum periodically (but note: D1's VACUUM may not be available; Cloudflare may handle this internally)
- Rebuild indexes (same caveat)
- Monitor table sizes to identify growth outliers

---

## 5. Encryption at Rest

### 5.1 What Gets Encrypted

| Table | Column | Encryption | Key |
|-------|--------|------------|-----|
| `pii_entities` | `encrypted_value` | AES-256-GCM | Per-user data key |
| `providers` | `encrypted_api_key` | AES-256-GCM | Global provider key |
| `user_preferences` | `value` (if key matches sensitive patterns) | Optional AES-256-GCM | Per-user data key |

All other columns are stored in plaintext within D1. D1 itself provides encryption at rest at the storage layer, but application-layer encryption protects against:
- Cloudflare employee access
- D1 data exposure via bugs/breaches
- Subpoena of raw database contents

### 5.2 Query Interaction with Encrypted Columns

**Encrypted columns cannot be meaningfully indexed or queried.** The ciphertext is different each time (due to GCM random nonce), so:
- You cannot `WHERE encrypted_value LIKE '%@%'` to find email entities
- You cannot ORDER BY encrypted_value
- You cannot GROUP BY encrypted_value

**This is intentional and desired** — the whole point of encrypting PII is that the database can't leak it via queries.

**Lookup strategy:**
- PII entities are looked up by their `id` (plaintext), not by their value
- The application decrypts on read, encrypts on write
- Entity IDs are generated by the application before database storage

### 5.3 Key Management

**Architecture:**

```
┌──────────────┐     ┌─────────────────┐     ┌──────────────┐
│ Cloudflare   │     │ Application     │     │ D1 Database  │
│ Workers      │────▶│ Layer (Worker)  │────▶│ (ciphertext) │
│ (Env vars)   │     │ (encrypt/decrypt)│     │              │
└──────────────┘     └─────────────────┘     └──────────────┘
                            │
                     ┌──────┴──────┐
                     │ Key Store   │
                     │ (KV / env)  │
                     └─────────────┘
```

**Key hierarchy:**
1. **Master Key (MK):** Stored as a Cloudflare Workers secret (environment variable). Never in code, never in D1.
2. **Data Encryption Keys (DEKs):** Generated per-user or per-category. Encrypted with MK and stored in KV (`keys/{user_id}` or `keys/global/providers`).
3. **Key IDs:** Stored alongside encrypted data (`key_id` column) to support key rotation.

**Rotation:**
1. Generate a new DEK
2. Encrypt new DEK with MK, store in KV
3. Re-encrypt all data using old key → new key (background job)
4. Update `key_id` references
5. Delete old DEK after verification

**For PII entities:** Re-encryption requires decrypting with old key and re-encrypting with new. This must be done in a Worker (the only place with access to both keys). Batch processing with rate limiting to avoid Worker timeouts.

---

## 6. Performance Analysis

### 6.1 Single-User Query Patterns

| Query | Frequency | Table(s) | Index Used | Estimated Rows |
|-------|-----------|----------|------------|----------------|
| List sessions (dashboard) | Every page load | `sessions` | `idx_sessions_user_updated` | 10–100 |
| Load messages for a session | Every session open | `messages` | `idx_messages_session_created` | 10–500 |
| Send a message (write) | Per user action | `messages` + `sessions` | `pk_messages` (write) | 1 insert + 1 update |
| Search messages | Occasional | `messages` | `idx_messages_user_created` (filter) | 100–1000 |
| View PII vault | Occasional | `pii_entities` | `idx_pii_user_type` | 5–50 |
| Load preferences | Per session init | `user_preferences` | `uq_prefs_user_key` | 5–20 |

**Bottleneck:** Loading messages for a session with 500+ messages. Pagination (see §6.5) is critical.

### 6.2 Platform Query Patterns

| Query | Frequency | Table(s) | Index Used | Notes |
|-------|-----------|----------|------------|-------|
| Active user count | Dashboard | `sessions` | `idx_sessions_user_updated` | COUNT DISTINCT user_id |
| Cost per provider | Daily report | `interactions` | `idx_interactions_provider` | SUM(cost_usd) GROUP BY provider |
| Error rate monitoring | Real-time | `interactions` | `idx_interactions_status` | COUNT WHERE status != 'success' |
| Model performance | Weekly | `interactions` + `feedback` | JOIN on `interaction_id` | AVG(rating) GROUP BY model_id |
| Database size | Daily | `pragma` | N/A | Built-in SQLite |
| Routing rule effectiveness | Weekly | `routing_rules` | `idx_rules_type` | Direct lookup (small table) |

### 6.3 Full Table Scan Risk

| Query | Table | Full Scan? | Mitigation |
|-------|-------|------------|------------|
| Find all messages containing "X" | `messages` | **YES** — `content` is not indexed | FTS via application (Cloudflare Vectorize) or batch scanning with pagination |
| Find PII by real value | `pii_entities` | **YES** — `encrypted_value` not queryable | Design limitation (acceptable — use entity ID lookup) |
| List all routing rules (admin) | `routing_rules` | **No** — table is tiny (< 100 rows) | Acceptable even without perfect index |
| JSON field queries (`json_extract`) | Any table with `metadata` | **YES** — D1 doesn't index JSON | Avoid JSON queries in hot paths; extract to columns if needed |

### 6.4 N+1 Query Risks

**Risk: Session list with message previews.**

Naive approach:
```javascript
// N+1: one query for sessions, then one per session for last message
const sessions = await db.query('SELECT * FROM sessions WHERE user_id = ? ORDER BY updated_at DESC LIMIT 20');
for (const session of sessions) {
  session.lastMessage = await db.query('SELECT * FROM messages WHERE session_id = ? ORDER BY created_at DESC LIMIT 1', [session.id]);
}
```

**Fix:** Use a window function or JOIN:
```sql
SELECT s.*, m.content AS last_message_preview, m.created_at AS last_message_time
FROM sessions s
LEFT JOIN messages m ON m.session_id = s.id AND m.created_at = s.last_message_at
WHERE s.user_id = ? AND s.status = 'active'
ORDER BY s.updated_at DESC
LIMIT 20;
```

Or, since `sessions.last_message_at` is denormalized, just fetch the session list first, then batch-fetch last messages:
```sql
-- Single batch query
SELECT * FROM messages WHERE session_id IN (?, ?, ?, ...) AND created_at = ?
```

**Risk: Message loading with interaction metadata.**

Naive: Load messages, then for each assistant message, load the interaction.

Fix: LEFT JOIN interactions in the message query, or load interactions in a second batched query.

### 6.5 Message Pagination

**Approach: Cursor-based pagination using `created_at` + ULID.**

```sql
-- First page
SELECT * FROM messages
WHERE session_id = ? AND role IN ('user', 'assistant')
ORDER BY created_at ASC, id ASC
LIMIT 50;

-- Next page (client passes last_seen_at and last_seen_id)
SELECT * FROM messages
WHERE session_id = ? AND role IN ('user', 'assistant')
  AND (created_at > ? OR (created_at = ? AND id > ?))
ORDER BY created_at ASC, id ASC
LIMIT 50;
```

**Why cursor-based, not offset-based?**
- Offset-based (`LIMIT 50 OFFSET 100`) gets slower as offset grows (SQLite must scan and discard rows)
- Cursor-based is O(1) regardless of page depth
- ULIDs are time-sortable, so `created_at` + `id` gives a strict total order
- No "skipped rows" problem when new messages arrive between pages

**Reverse pagination** (newest first, for "scroll up" UI):
```sql
SELECT * FROM messages
WHERE session_id = ? AND role IN ('user', 'assistant')
  AND (created_at < ? OR (created_at = ? AND id < ?))
ORDER BY created_at DESC, id DESC
LIMIT 50;
-- Then reverse in application code for correct display order
```

---

## 7. Devil's Advocate

### 7.1 "Why not use Durable Objects instead of D1?"

**Strongest counterargument:** Durable Objects provide strong consistency, single-writer semantics, and can store state directly in memory or via their transactional storage API. They avoid the eventual consistency issues of D1 replicas. For a chat application where message ordering matters, Durable Objects per-session would guarantee correctness.

**Why we chose D1:**
- **Cost:** Durable Objects bill per-request and per-second of existence. A session that's open for weeks costs money even when idle. D1 is billed per-row-read/write — idle data is free.
- **Query flexibility:** D1 supports SQL with JOINs, aggregations, and indexing. Durable Objects storage is essentially a key-value store with limited query capabilities. Analytics queries (cost per model, error rates, routing effectiveness) would require separate infrastructure with DOs.
- **Operational simplicity:** D1 is a single database to manage. Per-session Durable Objects would require lifecycle management (creation, deletion, migration, scaling).
- **Our mitigation for consistency:** Messages are immutable once written and ordered by `created_at` + ULID. Even with eventual consistency, a user won't see their own messages out of order because their writes go to the primary, and they read their own messages shortly after writing.

**When we'd reconsider:** If per-session consistency becomes a hard requirement (e.g., multi-user collaborative sessions with real-time edits), Durable Objects per-session would be the right choice.

### 7.2 "Why not separate databases per user instead of shared with tenant_id?"

**Strongest counterargument:** Per-user databases eliminate tenant isolation concerns entirely. No risk of data leakage between users. Each database can be placed in the user's preferred region. Deletion is trivial — just delete the database.

**Why we chose shared database:**
- **D1 database limit:** Cloudflare has limits on the number of D1 databases per account (typically 20–100). This doesn't scale to thousands of users.
- **Cost efficiency:** A single 1 GB database costs less than 100 databases of 10 MB each (each has overhead).
- **Cross-user queries:** Analytics, admin dashboards, and routing optimization require querying across users. With per-user databases, you'd need to aggregate in application code.
- **Operational overhead:** Migrations, backups, and monitoring scale linearly with database count.

**Mitigation for isolation:**
- Every query includes `WHERE user_id = ?`
- Middleware enforces tenant isolation (no query without user_id filter)
- Row-level security isn't available in D1, so we rely on application-level enforcement + testing

### 7.3 "Why not use KV for everything instead of D1?"

**Strongest counterargument:** KV is simpler, globally distributed, and has no schema to manage. For a chat app, you could store sessions as KV objects and messages as lists within those objects. KV is also faster for single-key lookups (no SQL parsing overhead).

**Why we chose D1:**
- **Relational queries:** "Show me all sessions ordered by last message time" requires sorting across keys. In KV, you'd need a separate index key structure. In D1, it's a single query.
- **Consistent transactions:** KV's eventual consistency means a user might send a message, then load the session and not see it. D1's read-your-writes (via RETURNING) avoid this.
- **JOIN support:** Loading messages with interaction metadata, computing costs per session, etc., all require joins. KV would require multiple round-trips and application-level joins.
- **Ad-hoc queries:** Debugging, analytics, and admin operations benefit from SQL's expressiveness.

**Where KV makes sense as a complement:**
- Session-level caching (store the full session object in KV, rebuild from D1 on miss)
- Encryption key storage (KV is faster for key lookups than D1)
- Rate limiting counters (KV's eventual consistency is fine for rate limits)

### 7.4 "Why store messages in D1 instead of R2?"

**Strongest counterargument:** Messages are write-heavy, append-only, and rarely queried except by session_id. This is exactly the pattern R2 is designed for — object storage with prefix-based listing. Storing messages in R2 would reduce D1 size, lower query costs, and scale to unlimited message history.

**Why we chose D1 for hot messages:**
- **Query latency:** D1 queries return in < 10ms for indexed lookups. R2 object retrieval is ~50–100ms. For interactive chat, this latency difference matters.
- **Pagination:** D1's SQL supports cursor-based pagination natively. R2 prefix listing has a 1,000-object limit per request and no efficient "start after this key" pagination for sorted access.
- **Search:** D1 supports `LIKE` and `json_extract()` for basic search. R2 requires listing and filtering in application code.
- **JOIN support:** Messages need to reference sessions, interactions, and PII entities. R2 objects can't JOIN.

**Our hybrid approach:**
- **Hot messages (last 90 days):** D1 for fast interactive queries
- **Cold messages (older than 90 days):** Archived to R2 as JSONL files
- **Access pattern:** When a user scrolls past the 90-day mark, the application fetches from R2 on demand

---

## 8. Open Questions

1. **FTS strategy:** D1 doesn't have FTS5. Should we use Cloudflare Vectorize for semantic search over messages, or is basic prefix search (`LIKE 'keyword%'`) sufficient for MVP?

2. **Multi-user sessions:** The current schema assumes one user per session. If collaborative sessions are needed, we'd need a `session_participants` join table. Is this in scope?

3. **Message size limit:** D1 rows have practical size limits (SQLite max BLOB is ~1 GB, but D1 query latency increases with row size). Should we cap message `content` at a certain size and store overflow in R2?

4. **Key management provider:** The encryption design references a key store in KV. Should we use Cloudflare's built-in secrets management, or an external KMS (AWS KMS, Vault)? This affects key rotation automation.

5. **Agent health retention:** 7 days was proposed for agent_health in D1. Is this sufficient for debugging, or do operators need longer retention? Should it be configurable per agent?

6. **Drizzle vs raw SQL:** We've recommended Drizzle ORM. Should the entire data layer use Drizzle's query builder, or should performance-critical paths use raw SQL with Drizzle only for schema definitions?

7. **Soft-delete across all tables:** Only `sessions` has a `status` column for soft-delete. Should `messages`, `interactions`, etc., also support soft-delete for audit trail purposes?

8. **Rate limiting data:** Where should per-user rate limiting counters live? KV (fast, eventually consistent) or D1 (transactional but slower)?

9. **Backup strategy:** D1 doesn't offer automatic backups beyond Cloudflare's internal replication. Should we implement periodic R2 exports of the entire database?

10. **Testing migrations:** How do we test migrations against a production-like D1 instance without affecting production? Wrangler supports `--remote` for staging databases, but is this sufficient?
