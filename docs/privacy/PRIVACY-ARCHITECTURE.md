# Privacy Architecture — log-origin

> **Version:** 0.1-draft  
> **Status:** Architecture design  
> **Last updated:** 2026-03-25

---

## Table of Contents

1. [Encryption Architecture](#1-encryption-architecture)
2. [PII Detection & Replacement](#2-pii-detection--replacement)
3. [Encrypted Storage Design](#3-encrypted-storage-design)
4. [Zero-Knowledge Analysis](#4-zero-knowledge-analysis)
5. [Compliance](#5-compliance)
6. [Devil's Advocate](#6-devils-advocate)
7. [Open Questions](#7-open-questions)

---

## 1. Encryption Architecture

### 1.1 Full Data Flow

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         LOG ORIGIN ENCRYPTION FLOW                       │
│                                                                          │
│  ┌────────┐      ┌──────────────┐      ┌────────┐      ┌────────────┐   │
│  │        │      │              │      │        │      │            │   │
│  │ User   │─────>│ Client-Side  │─────>│ Worker │─────>│ LLM        │   │
│  │ Input  │      │ Encryption   │      │ (CF)   │      │ Provider   │   │
│  │        │      │ Layer        │      │        │      │            │   │
│  └────────┘      └──────┬───────┘      └───┬────┘      └─────┬──────┘   │
│                        │                  │                  │          │
│                        ▼                  ▼                  ▼          │
│                  ┌──────────┐       ┌──────────┐       ┌──────────┐    │
│                  │ 1. PII   │       │ 3. Temp  │       │ 5. LLM   │    │
│                  │  Detect  │       │  Decrypt │       │  Returns │    │
│                  │  Replace │       │  (DEK)   │       │  Result  │    │
│                  └────┬─────┘       └────┬─────┘       └────┬─────┘    │
│                       │                  │                  │          │
│                       ▼                  ▼                  ▼          │
│                  ┌──────────┐       ┌──────────┐       ┌──────────┐    │
│                  │ 2. AES   │       │ 4. Send  │       │ 6. Re-   │    │
│                  │ -GCM     │──────>│ plaintext│──────>│ Encrypt  │    │
│                  │ Encrypt  │       │ to LLM   │       │ w/ DEK   │    │
│                  │ w/ DEK   │       │          │       │          │    │
│                  └────┬─────┘       └──────────┘       └────┬─────┘    │
│                       │                                       │          │
│                       ▼                                       ▼          │
│                  ┌──────────┐                            ┌──────────┐   │
│                  │ Store    │<───────────────────────────│ Store    │   │
│                  │ ciphertext│                            │ ciphertext│  │
│                  │ in D1    │                            │ in D1    │   │
│                  └──────────┘                            └──────────┘   │
│                                                                          │
│  KEY HIERARCHY:                                                          │
│  Passphrase → PBKDF2 → Master Key (never leaves browser)                │
│  Master Key → wraps DEK → DEK sent to Worker per-request               │
│  DEK → encrypts/decrypts individual log entries                         │
└──────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Key Derivation

#### PBKDF2 vs Argon2id

| Property | PBKDF2 | Argon2id (WASM) |
|---|---|---|
| Native browser support | ✅ Web Crypto API | ❌ Requires WASM (200-400KB) |
| Memory hardness | ❌ No | ✅ Configurable |
| GPU resistance | ❌ Weak | ✅ Strong |
| Key derivation time (600K iter) | ~2-3s | ~0.5s (1 thread, 64MB RAM) |
| Bundle impact | 0 bytes | ~300KB gzip |
| WASM attack surface | N/A | Potential (complex, but real) |
| Audit history | Decades, well-understood | Newer, fewer production audits |

**Decision: PBKDF2-SHA256 with 600,000 iterations.**

Rationale:
- For a **personal, single-user** system, the threat model doesn't justify the complexity of WASM Argon2
- The passphrase is used to derive the master key **once per session**, not per request
- PBKDF2 at 600K iterations makes online brute-force impractical (2-3s per attempt)
- Offline attacks require access to the D1 database AND the HMAC verifier — and even then, they'd crack a hash, not the encryption key (the master key is never stored)

**Future upgrade path:** Ship Argon2id WASM as an optional enhancement for users who want stronger KDF. The key derivation output format includes the KDF identifier, so migration is seamless:

```json
{
  "kdf": "pbkdf2-sha256-600000",
  "salt": "a1b2c3d4...",
  "verifier": "e5f6g7h8...",
  "verifier_hmac": "i9j0k1l2..."
}
```

### 1.3 Session Key Exchange (ECIES Flow)

When the browser needs the Worker to decrypt data for LLM calls, it uses a hybrid encryption scheme:

#### Message 1: Client → Worker (Key Transport)

```json
{
  "type": "key_transport",
  "tenant_id": "abc123",
  "dek_wrapped": "BASE64_ENCODED_AES_256_GCM_WRAPPED_DEK",
  "dek_iv": "BASE64_ENCODED_IV",
  "ephemeral_public_key": "BASE64_ENCODED_P256_PUBLIC_KEY",
  "session_id": "uuid-v4"
}
```

#### Detailed ECIES Flow

```
CLIENT SIDE:
  1. Generate ephemeral ECDH key pair: (eph_priv, eph_pub)
  2. Generate random DEK: 32 bytes from crypto.getRandomValues()
  3. Import tenant's master key (from PBKDF2 derivation)
  4. Wrap DEK with master key:
     wrapped_dek = AES_256_GCM_encrypt(key=masterKey, plaintext=DEK, iv=random_iv)
  5. Send {wrapped_dek, dek_iv, eph_pub} to Worker

WORKER SIDE:
  6. Receive wrapped DEK + IV + ephemeral public key
  7. Worker does NOT have the master key — how does it unwrap?

  REVISION: Worker receives the DEK directly, wrapped with a Worker
  transport key that is derived per-session from a shared secret.
```

#### Corrected Key Exchange (Simpler, More Secure)

Actually, the flow is simpler than full ECIES. Here's the practical design:

```
CLIENT SIDE:
  1. User enters passphrase → derive master key (PBKDF2)
  2. Generate random DEK: 32 bytes
  3. Wrap DEK with master key: wrapped_dek = AES-GCM-Encrypt(masterKey, DEK)
  4. Attach wrapped_dek to the request body

WORKER SIDE:
  5. Receive encrypted_data + wrapped_dek + iv + tag
  6. WAIT — the Worker cannot unwrap the DEK without the master key!
```

> **This is the fundamental tension.** The Worker needs the DEK to decrypt data for LLM calls, but the master key never leaves the browser. The solution:

**The Worker never sees the master key. The browser sends the DEK encrypted under a *separate* transport layer:**

```
ACTUAL FLOW:
  1. User authenticates (passphrase → HMAC check → JWT issued)
  2. Browser derives master key from passphrase
  3. Browser generates a DEK (per session or per entry)
  4. Browser encrypts log entry with DEK: ciphertext = AES-GCM(kek=DEK, plaintext)
  5. Browser wraps DEK with master key: wrapped_dek = AES-GCM(kek=masterKey, plaintext=DEK)
  6. Browser sends {ciphertext, wrapped_dek, dek_iv} to Worker
  7. Worker STORES {ciphertext, wrapped_dek, dek_iv} in D1 — still encrypted!

  FOR LLM CALLS:
  8. Browser reads {ciphertext, wrapped_dek, dek_iv} from Worker
  9. Browser unwraps DEK: DEK = AES-GCM-Decrypt(kek=masterKey, ciphertext=wrapped_dek)
  10. Browser decrypts entry: plaintext = AES-GCM-Decrypt(kek=DEK, ciphertext=ciphertext)
  11. Browser sends plaintext to Worker → Worker sends to LLM
  12. Worker receives LLM response, sends to browser
  13. Browser encrypts response, sends back to Worker for storage

  WAIT — this means the browser decrypts, then sends plaintext to the Worker?
  That defeats the purpose of server-side encryption!
```

### 1.4 Revised Encryption Architecture (The Honest Design)

After the above analysis, here is the **actual, honest** encryption model:

```
┌─────────────────────────────────────────────────────────────┐
│  HONEST ENCRYPTION MODEL                                    │
│                                                              │
│  AT REST (D1): Fully encrypted. AES-256-GCM ciphertext.     │
│  Worker cannot read stored data without the DEK.             │
│                                                              │
│  IN TRANSIT (Browser ↔ Worker): TLS 1.3. All data in        │
│  transit is encrypted by the transport layer.                │
│                                                              │
│  IN USE (Worker memory): The Worker DOES see plaintext      │
│  for the ~3ms it takes to forward to the LLM provider and   │
│  receive the response. This is NOT zero-knowledge.           │
│                                                              │
│  THE THREAT WINDOW: DEK exists in Worker memory for the     │
│  duration of one request (~50-200ms). After the response,    │
│  the DEK is garbage collected with the request scope.        │
│                                                              │
│  WHO CAN READ YOUR DATA:                                     │
│  ✅ You (browser, with passphrase)                           │
│  ❌ Cloudflare (at rest — ciphertext only)                   │
│  ⚠️  Worker (transiently, during request processing)         │
│  ❌ LLM provider (they see the prompt, that's the point)     │
│  ❌ Database dump thief (ciphertext only)                     │
└─────────────────────────────────────────────────────────────┘
```

#### Practical Key Flow

```javascript
// === CLIENT SIDE ===

// On login: derive master key from passphrase
const masterKey = await deriveKey(passphrase, storedSalt, 600000);

// Per-session: generate a DEK
const dek = crypto.getRandomValues(new Uint8Array(32));
const dekCryptoKey = await crypto.subtle.importKey(
  'raw', dek, 'AES-GCM', false, ['encrypt', 'decrypt']
);

// Wrap DEK with master key (for storage/recovery)
const wrappedDEK = await crypto.subtle.wrapKey(
  'raw', dekCryptoKey, masterKey, { name: 'AES-GCM', iv: dekWrapIV }
);

// Store wrappedDEK in D1 via Worker
// DEK itself is kept in browser memory only

// Encrypt log entry
const entryIV = crypto.getRandomValues(new Uint8Array(12));
const ciphertext = await crypto.subtle.encrypt(
  { name: 'AES-GCM', iv: entryIV, tagLength: 128 },
  dekCryptoKey,
  encoder.encode(JSON.stringify(entry))
);

// Send to Worker:
// { ciphertext: base64, iv: base64, tag: base64, wrapped_dek: base64 }

// === WORKER SIDE ===

// Worker stores ciphertext + wrapped_dek in D1
// Worker CANNOT decrypt — it doesn't have masterKey

// === FOR LLM CALLS ===

// Browser decrypts locally, sends plaintext to Worker for LLM forwarding
// OR (better design):
// Browser sends DEK to Worker (wrapped in a per-request transport),
// Worker decrypts, sends to LLM, re-encrypts response, discards DEK

// RECOMMENDED DESIGN:
// 1. Browser decrypts entry locally
// 2. Browser applies PII replacement
// 3. Browser sends PII-cleaned plaintext to Worker
// 4. Worker sends to LLM (no PII in transit to third party)
// 5. LLM response comes back through Worker to browser
// 6. Browser re-encrypts response for storage
```

### 1.5 DEK Lifecycle

```
┌──────────────────────────────────────────────────────────┐
│                   DEK LIFECYCLE                          │
│                                                           │
│  CREATION:                                               │
│    crypto.getRandomValues(new Uint8Array(32))            │
│    Source: CSPRNG (browser's crypto.getRandomValues)     │
│    Timing: Once per session (or per entry, configurable) │
│                                                           │
│  STORAGE:                                                │
│    Wrapped with master key → stored in D1                │
│    Unwrapped (plaintext) → browser JS memory only        │
│    Worker receives DEK only if needed for LLM call,      │
│    wrapped with session transport key                    │
│                                                           │
│  ROTATION:                                               │
│    User changes passphrase → new master key              │
│    → re-derive → re-wrap all DEKs with new master key    │
│    → requires decrypting all entries (needs old master)  │
│    → must be done before old passphrase is discarded     │
│                                                           │
│  DESTRUCTION:                                            │
│    Browser tab close → DEK evicted from memory            │
│    Worker request end → DEK garbage collected             │
│    No persistence in cookies, localStorage, or IndexedDB  │
│    No logging, no serialization                          │
│                                                           │
│  SCOPING:                                                │
│    Session DEK: covers one browser session                │
│    Entry DEK: per-entry encryption (higher security)      │
│    Decision: start with session DEK, allow per-entry      │
│    as an option for high-sensitivity entries              │
└──────────────────────────────────────────────────────────┘
```

---

## 2. PII Detection & Replacement

### 2.1 Why Client-Side PII Detection?

The LLM provider will see your prompts. We can't encrypt what we send them. So we **replace PII before it leaves the browser**:

```
Original:   "Call John Smith at 555-0123 about the meeting tomorrow"
Detected:   [PERSON: John Smith] [PHONE: 555-0123]
Replaced:   "Call [PERSON_A] at [PHONE_A] about the meeting tomorrow"
```

The LLM sees placeholders, not real data. When the response comes back, we **don't** reverse the replacement — the LLM's analysis refers to `[PERSON_A]`, which is fine.

### 2.2 Client-Side NER (Named Entity Recognition)

We don't use a full ML model for NER (too heavy for browser). Instead, a **layered detection system**:

```
Layer 1: Regex Patterns (fast, deterministic)
  → Email, phone, SSN, credit card, IP address, API keys

Layer 2: Pattern Matching (moderate)
  → Dates, addresses, zip codes, IBANs

Layer 3: Contextual Heuristics (best-effort)
  → Names (capitalized words near title words like "Mr.", "Dr.")
  → Organization names (near "Inc.", "Corp.", "Ltd.")
  → Locations (near prepositions + capitalized words)

Layer 4: User-Defined Patterns (custom)
  → User can define additional regex patterns for their specific PII
```

### 2.3 Regex Patterns

```javascript
const PII_PATTERNS = {
  // US Social Security Number
  ssn: {
    regex: /\b(?!000|666|9\d{2})\d{3}-(?!00)\d{2}-(?!0000)\d{4}\b/g,
    replacement: '[SSN]',
    falsePositiveRisk: 'low'
  },
  
  // Email addresses
  email: {
    regex: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g,
    replacement: '[EMAIL]',
    falsePositiveRisk: 'very-low'
  },
  
  // US Phone numbers
  phone_us: {
    regex: /(?:\+?1[-.\s]?)?\(?[2-9]\d{2}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b/g,
    replacement: '[PHONE]',
    falsePositiveRisk: 'medium'  // could match order numbers
  },
  
  // International phone (simplified)
  phone_intl: {
    regex: /\+\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}\b/g,
    replacement: '[PHONE]',
    falsePositiveRisk: 'medium'
  },
  
  // Credit card numbers
  credit_card: {
    regex: /\b(?:\d[ -]*?){13,19}\b/g,
    replacement: '[CREDIT_CARD]',
    validator: (match) => luhnCheck(match.replace(/[-\s]/g, '')),
    falsePositiveRisk: 'medium'  // Luhn check reduces false positives
  },
  
  // IPv4 addresses
  ipv4: {
    regex: /\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b/g,
    replacement: '[IP]',
    falsePositiveRisk: 'medium'  // version numbers look like IPs
  },
  
  // API keys (common patterns)
  api_key: {
    regex: /\b(?:sk|pk|api|key|token|secret)[_-][A-Za-z0-9]{20,}\b/gi,
    replacement: '[API_KEY]',
    falsePositiveRisk: 'low'
  },
  
  // AWS-style keys
  aws_key: {
    regex: /\bAKIA[0-9A-Z]{16}\b/g,
    replacement: '[API_KEY]',
    falsePositiveRisk: 'very-low'
  },
  
  // GitHub tokens
  github_token: {
    regex: /\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36,}\b/g,
    replacement: '[API_KEY]',
    falsePositiveRisk: 'very-low'
  },
  
  // US mailing address (simplified)
  address_us: {
    regex: /\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Boulevard|Blvd|Drive|Dr|Lane|Ln|Road|Rd|Court|Ct|Way|Place|Pl)\b(?:\.?)/gi,
    replacement: '[ADDRESS]',
    falsePositiveRisk: 'medium'
  },
  
  // Dates (ISO and US formats)
  date: {
    regex: /\b(?:\d{4}[-/]\d{2}[-/]\d{2}|\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b/g,
    replacement: '[DATE]',
    falsePositiveRisk: 'high'  // lots of numeric patterns look like dates
  },
  
  // Zip codes (US)
  zip_us: {
    regex: /\b\d{5}(?:-\d{4})?\b/g,
    replacement: '[ZIP]',
    contextRequired: true,  // only replace near address patterns
    falsePositiveRisk: 'high'
  }
};
```

### 2.4 Multi-Language PII

```
Chinese names:
  regex: /[\u4e00-\u9fff]{2,4}/g  (CJK unified ideographs, 2-4 chars)
  context: near title words (先生, 女士, 教授)
  falsePositiveRisk: HIGH — Chinese text is ALL ideographs

Russian names:
  regex: /\b[А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+){1,3}\b/g
  context: patronymic pattern (middle name ending in -ич/-на)
  falsePositiveRisk: MEDIUM

Japanese names:
  regex: /[\u4e00-\u9fff]{1,4}\s+[\u4e00-\u9fff]{1,4}/g (kanji + kanji)
  falsePositiveRisk: HIGH

German addresses:
  regex: /[A-Za-zäöüß]+\s+\d+[A-Za-z]?,\s*\d{5}\s+[A-Za-zäöüß]+/g
  falsePositiveRisk: LOW-MEDIUM

APPROACH:
  - Default: English patterns only (highest accuracy)
  - User can enable additional language packs
  - Each language pack includes its own patterns + context rules
  - Multi-language increases false positives — warn users
```

### 2.5 False Positive Handling

```
Strategy:
  1. CONFIDENCE TIERS:
     Tier 1 (auto-replace): email, SSN, API keys — almost never false positives
     Tier 2 (suggest): phone, address, credit card — moderate risk
     Tier 3 (manual): names, dates, zip codes — high false positive rate

  2. USER REVIEW:
     - Tier 1: replaced automatically, shown in sidebar for review
     - Tier 2: highlighted in UI, user clicks to confirm/decline
     - Tier 3: highlighted but not replaced unless user approves

  3. CONTEXT RULES:
     - "555-0123" in a paragraph → probably a phone number → replace
     - "5550123" as a standalone number → might be an order ID → don't replace
     - "John Smith" after "Dear" → probably a name → replace
     - "Smith" alone → could be a common word → don't replace

  4. WHITELIST:
     - User can mark patterns as "not PII" per entry or globally
     - E.g., "don't replace [my-project-api-key]"
```

### 2.6 Entity ID Generation

```
QUESTION: Why [PERSON_A] instead of [PERSON_1]?

ANSWER: Semantic coherence for the LLM.

  Input: "John Smith called. He said Jane Doe would follow up. 
          John mentioned the deadline is Friday."

  With numeric IDs:
    "[PERSON_1] called. He said [PERSON_2] would follow up. 
     [PERSON_1] mentioned the deadline is Friday."
    → LLM can track which person is which

  With letter IDs:
    "[PERSON_A] called. He said [PERSON_B] would follow up. 
     [PERSON_A] mentioned the deadline is Friday."
    → Same tracking ability, but more distinct from numbered references

  RULES:
  - Each entity TYPE gets its own namespace: [PERSON_A], [PHONE_A], [EMAIL_A]
  - Within a type, IDs are sequential per entry: A, B, C...
  - Same entity appearing multiple times gets the same ID:
    "John" and "John Smith" → both become [PERSON_A]
  - Cross-entry consistency: user can define a "name registry" that
    maps "John Smith" → [PERSON_A] across all entries
```

### 2.7 Preamble Injection

Before sending PII-replaced text to the LLM, we inject a preamble:

```
The following text has been processed for privacy. Personal identifiable 
information has been replaced with semantic placeholders:
  [PERSON_X] = a person's name
  [PHONE_X]  = a phone number
  [EMAIL_X]  = an email address
  [ADDRESS_X] = a physical address
  [SSN_X]    = a social security number
  [DATE_X]   = a date reference
  [API_KEY_X] = an API key or credential

Multiple instances of the same letter (e.g., [PERSON_A]) refer to the 
same entity. Please analyze the text below:

---
{PII-replaced content}
---
```

This helps the LLM understand that placeholders represent real entities, improving analysis quality without exposing the actual data.

---

## 3. Encrypted Storage Design

### 3.1 D1 Schema (Encrypted vs Plaintext)

```sql
CREATE TABLE tenants (
  id          TEXT PRIMARY KEY,       -- plaintext: tenant identifier
  created_at  TEXT NOT NULL,          -- plaintext: ISO timestamp
  kdf_config  TEXT NOT NULL,          -- plaintext: KDF params (algorithm, iterations, salt)
  verifier    TEXT NOT NULL,          -- plaintext: random 32-byte verifier (hex)
  verifier_hmac TEXT NOT NULL         -- plaintext: HMAC of verifier (hex)
);

CREATE TABLE log_entries (
  id          TEXT PRIMARY KEY,       -- plaintext: UUID
  tenant_id   TEXT NOT NULL,          -- plaintext: FK to tenants
  created_at  TEXT NOT NULL,          -- plaintext: ISO timestamp (for sorting/filtering)
  updated_at  TEXT NOT NULL,          -- plaintext: ISO timestamp
  entry_type  TEXT NOT NULL,          -- plaintext: 'journal', 'reflection', 'note', etc.
  ciphertext  TEXT NOT NULL,          -- 🔒 ENCRYPTED: AES-256-GCM ciphertext (base64)
  iv          TEXT NOT NULL,          -- 🔒 ENCRYPTION METADATA: initialization vector (base64)
  tag         TEXT NOT NULL,          -- 🔒 ENCRYPTION METADATA: auth tag (base64)
  dek_id      TEXT NOT NULL,          -- plaintext: references which DEK was used
  word_count  INTEGER,                -- plaintext: for UI display without decryption
  has_attachments INTEGER DEFAULT 0,  -- plaintext: boolean flag
  FOREIGN KEY (tenant_id) REFERENCES tenants(id)
);

CREATE TABLE data_encryption_keys (
  id          TEXT PRIMARY KEY,       -- plaintext: DEK identifier
  tenant_id   TEXT NOT NULL,          -- plaintext: FK to tenants
  wrapped_dek TEXT NOT NULL,          -- 🔒 ENCRYPTED: master-key-wrapped DEK (base64)
  wrap_iv     TEXT NOT NULL,          -- 🔒 ENCRYPTION METADATA
  wrap_tag    TEXT NOT NULL,          -- 🔒 ENCRYPTION METADATA
  created_at  TEXT NOT NULL,          -- plaintext: ISO timestamp
  expires_at  TEXT,                   -- plaintext: optional expiry
  FOREIGN KEY (tenant_id) REFERENCES tenants(id)
);

CREATE TABLE pim_whitelist (
  id          TEXT PRIMARY KEY,       -- plaintext: UUID
  tenant_id   TEXT NOT NULL,          -- plaintext
  pattern     TEXT NOT NULL,          -- plaintext: regex pattern (user-defined)
  description TEXT,                   -- plaintext: user's note about why this is safe
  created_at  TEXT NOT NULL,
  FOREIGN KEY (tenant_id) REFERENCES tenants(id)
);
```

### 3.2 Impact on Indexing & Queries

```
WHAT CAN WE QUERY WITHOUT DECRYPTION:
  ✅ By date range (created_at, updated_at)
  ✅ By entry type (entry_type)
  ✅ By tenant (tenant_id)
  ✅ By DEK (dek_id — for key rotation queries)
  ✅ By presence of attachments (has_attachments)
  ✅ By word count range (word_count)

WHAT REQUIRES DECRYPTION (client-side):
  ❌ Full-text search
  ❌ Content filtering (e.g., "entries about work")
  ❌ PII-based queries (e.g., "entries mentioning John")
  ❌ Semantic search (embeddings)
  ❌ Tag extraction from content

SOLUTIONS:
  1. Client-side search: decrypt all entries in browser, search locally
     → Works for personal use (typically <10K entries)
     → Won't scale to 100K+ entries

  2. Encrypted search indexes (future):
     → Use blind indexing (hashed trigrams) or ORAM
     → Complex, performance overhead, trade security for search

  3. Search on PII-replaced text:
     → Store PII-replaced version alongside ciphertext
     → Searchable, but PII-replaced text reveals structure
     → Good middle ground for most users

  4. LLM-powered search:
     → Send PII-cleaned query to LLM
     → LLM returns matching entry IDs
     → Client decrypts and displays
     → Requires sending query (not content) to LLM provider
```

### 3.3 Key Rotation

```javascript
// Key rotation flow (passphrase change):
// 1. User enters OLD passphrase → derive old_master_key
// 2. User enters NEW passphrase → derive new_master_key
// 3. For each DEK in data_encryption_keys:
//    a. Decrypt wrapped_dek with old_master_key → plaintext DEK
//    b. Re-encrypt plaintext DEK with new_master_key → new_wrapped_dek
//    c. Update data_encryption_keys row
// 4. Update verifier HMAC with new_master_key
// 5. Store new salt + new verifier HMAC
// 6. DONE — log entries are NOT re-encrypted (same DEK, new wrapping)

// DEK rotation (periodic, for forward secrecy):
// 1. Generate new DEK
// 2. Re-encrypt all log entries that used the old DEK
//    (requires browser to decrypt with old DEK, re-encrypt with new DEK)
// 3. Store new wrapped DEK, mark old DEK as expired
// 4. Old DEK kept until all entries are re-encrypted

// NOTE: DEK rotation requires the master key (i.e., user must be logged in).
// This is a background task that runs in the browser with user consent.
```

### 3.4 Key Backup / Passphrase Loss

```
WHAT HAPPENS IF THE USER FORGETS THEIR PASSPHRASE:
  → All encrypted data is PERMANENTLY INACCESSIBLE
  → There is no "forgot password" flow
  → There is no admin override
  → There is no backdoor

THIS IS INTENTIONAL:
  - If we can recover your data without your passphrase, 
    so can anyone who compromises our infrastructure
  - The whole point of client-side encryption is that 
    the server cannot access your data
  - "We can't read your data" is only true if we genuinely CAN'T

MITIGATION OPTIONS (user-facing):
  1. Passphrase hint (stored in plaintext in D1 — reveals nothing about key)
  2. Key export: user can export their master key (or wrapped DEKs) 
     and store in a password manager or safe
  3. Shamir's Secret Sharing: split recovery key into N shares, 
     give to trusted friends/family (complex, future feature)
  4. Paper backup: print the wrapped DEK + recovery instructions

RECOMMENDED UX:
  - On setup: "Write down your passphrase. We cannot recover it."
  - On login: optional passphrase hint display
  - Settings: "Export recovery key" (downloads encrypted key bundle)
  - Warning: "If you lose your passphrase AND your recovery key, 
    your data is gone forever."
```

---

## 4. Zero-Knowledge Analysis

### 4.1 Is This Zero-Knowledge?

```
                    ZERO-KNOWLEDGE MATRIX
                    
Aspect              Status    Explanation
─────────────────────────────────────────────────────────
Data at rest        ✅ YES    D1 stores AES-256-GCM ciphertext.
                              Without the master key (which never 
                              leaves the browser), data is unreadable.

Data in transit     ❌ NO     TLS protects against network eavesdroppers,
                              but the Worker receives plaintext when 
                              forwarding to LLM providers.

Worker processing   ❌ NO     The Worker sees plaintext for the duration
                              of the LLM API call (~50-200ms per request).
                              The DEK exists in Worker memory during this
                              window.

LLM provider        ❌ NO     The LLM provider sees the prompt (with PII
                              replaced). They see structure, patterns, 
                              and PII-cleaned content.

Database operator   ✅ YES    Cloudflare (as D1 operator) sees ciphertext
                              only. A database dump is useless without
                              the client-side key.
```

### 4.2 Threat Window Analysis

```
TIMELINE OF DATA EXPOSURE:
  ──────────────────────────────────────────────────────
  Browser:         ████ (user is looking at screen)
  TLS transit:     █ (milliseconds, encrypted by TLS)
  Worker memory:   █ (50-200ms per request)
  LLM provider:    ████ (they process and may store prompts)
  D1 storage:      ░░░░ (ciphertext only — no exposure)
  ──────────────────────────────────────────────────────
  █ = plaintext visible
  ░ = encrypted at rest

THE BIGGEST EXPOSURE:
  The LLM provider. Not our infrastructure. This is by design —
  we send data to an LLM for analysis. The PII replacement layer
  is our mitigation, but it's not perfect (see Section 2.5).

WORKER EXPOSURE MITIGATION:
  - DEK is request-scoped (V8 isolate, GC'd after request)
  - No disk persistence (Workers have no filesystem)
  - No KV/D1 caching of plaintext
  - Structured logging never includes user data
  - Worker code is minimal (just HTTP forwarding)
```

### 4.3 Comparison with Other Tools

```
                        ZERO-KNOWLEDGE COMPARISON
                    ──────────────────────────────────────
                    At Rest    During Use    Threat Model
                    ─────────  ────────────  ─────────────
log-origin (us)     ✅ Yes     ❌ No*        Personal logs
Signal              ✅ Yes     ✅ Yes        Messaging
1Password           ✅ Yes     ✅ Yes        Password vault
Bitwarden           ✅ Yes     ⚠️ Partial**  Password vault
ProtonMail          ✅ Yes     ⚠️ Partial*** Email
Logseq              ❌ No      ❌ No         Notes
Notion              ❌ No      ❌ No         Notes

* Worker sees plaintext transiently for LLM calls
** Browser extension can decrypt; server has access to encrypted vault
*** ProtonMail decrypts in browser, but contact search is server-side
```

**We are NOT zero-knowledge during processing.** This is a deliberate tradeoff:
- To send data to an LLM, the Worker must decrypt it
- We could use client-side LLM inference (WASM LLM) to achieve zero-knowledge, but this is:
  - Slow (10-100x slower than API calls)
  - Large model downloads (1-4GB)
  - Limited model quality (can't run GPT-4 locally)
  - Battery-intensive on mobile

**Our honest positioning:** "Zero-knowledge at rest. Client-side encrypted. Your data is protected from database breaches and server-side access. LLM processing requires transient decryption on our servers."

---

## 5. Compliance

### 5.1 GDPR

| Right | Capability | Notes |
|---|---|---|
| **Right to erasure (Art. 17)** | ✅ Supported | Delete tenant → cascading delete of all D1 rows. Since data is encrypted, even a "partial delete" would leave useless ciphertext. Full delete wipes everything. |
| **Right to data portability (Art. 20)** | ⚠️ Partial | Can export ciphertext + wrapped DEKs. User can decrypt on their own machine if they have the master key. Plaintext export requires user to be logged in (have passphrase). |
| **Right to access (Art. 15)** | ✅ Supported | User decrypts and views their own data. We can't provide "a copy of your data" in plaintext — only ciphertext. User must use their own passphrase. |
| **Right to rectification (Art. 16)** | ✅ Supported | User decrypts, edits, re-encrypts, stores. |
| **Consent (Art. 6)** | ✅ Clear | User explicitly sets up encryption with their own passphrase. No data is collected without user action. |
| **Data Protection Impact Assessment** | 📋 Needed | Required under Art. 35 if processing is "likely to result in high risk." PII detection + LLM processing probably qualifies. |

### 5.2 CCPA

| Right | Capability | Notes |
|---|---|---|
| **Right to delete (§1798.105)** | ✅ Supported | Same as GDPR erasure. |
| **Right to know (§1798.110)** | ⚠️ Partial | We can tell the user what data we store (ciphertext, metadata). We cannot provide the actual content without their passphrase. |
| **Right to opt out of sale** | N/A | We don't sell data. Never have, never will. |
| **Right to non-discrimination** | N/A | We don't offer differential pricing based on data collection. |

### 5.3 Can We Honestly Claim "We Can't Read Your Data"?

```
CLAIM: "We can't read your data."

ANALYSIS:
  ✅ TRUE for data at rest: D1 stores ciphertext. Without the passphrase
     (which we never receive), we cannot decrypt stored data.

  ⚠️ PARTIALLY TRUE during processing: Our Worker code transiently 
     handles plaintext data for LLM API calls. In theory, a Cloudflare
     employee with Worker debugging access could see this data. 
     In practice, Workers don't have a "debug mode" that logs request 
     bodies, and our code doesn't store or log plaintext.

  ❌ NOT TRUE for metadata: We store plaintext metadata (dates, entry 
     types, word counts). We can see when you write, how much you write,
     and what type of entry it is.

HONEST CLAIM:
  "Your log content is encrypted before it leaves your browser. 
   We store only ciphertext — we cannot read your entries, 
   reflections, or personal notes without your passphrase. 
   Metadata (timestamps, entry types) is stored in plaintext 
   for app functionality."
```

### 5.4 Compliance Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                  DATA FLOW FOR COMPLIANCE                    │
│                                                              │
│  USER (EU/CA)                                                │
│    │                                                         │
│    ├─── "I want my data deleted"                             │
│    │       → DELETE FROM tenants WHERE id = ?               │
│    │       → CASCADE deletes all log_entries, DEKs          │
│    │       → Cloudflare D1 replication propagates            │
│    │       → ✅ Complete erasure                             │
│    │                                                         │
│    ├─── "I want my data exported"                            │
│    │       → Export ciphertext bundle (encrypted)            │
│    │       → OR: Decrypt in browser, export plaintext       │
│    │       → ⚠️ Plaintext export requires user passphrase   │
│    │                                                         │
│    ├─── "What data do you have on me?"                       │
│    │       → List: metadata fields, ciphertext blobs         │
│    │       → We cannot list content without passphrase       │
│    │                                                         │
│    └─── "Stop processing my data"                            │
│            → Delete account → same as erasure                │
│            → No background processing without user action    │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. Devil's Advocate

### 6.1 "Client-Side Encryption in the Browser is Unreliable"

**The criticism:** Browser environments are hostile. Malicious extensions, CSP bypasses, prototype pollution, and supply chain attacks can all defeat client-side encryption.

**Our response:** This is partially true, and we should be honest about it.

```
WHAT CAN DEFEAT CLIENT-SIDE ENCRYPTION:
  ❌ Malicious browser extension with content_scripts permissions
     → Can intercept any DOM content, including form inputs
     → Can hook crypto.subtle to capture key material
     → Mitigation: This is beyond our control. Same risk as any web app.

  ❌ XSS vulnerability in our code
     → Can read variables in the same JS context
     → If passphrase is in a variable, it's exposed
     → Mitigation: Passphrase is used to derive a non-extractable 
       CryptoKey, then the passphrase string is zeroed out.
       The key object itself is non-extractable — even XSS can't 
       export it.

  ❌ Compromised CDN/dependency
     → If our JS bundle is tampered with, all bets are off
     → Mitigation: SRI hashes, minimal dependencies, CSP with 
       script-src restrictions, lockfile auditing

  ❌ Browser zero-day
     → Can theoretically break V8 sandboxing
     → Mitigation: We can't fix browser bugs. Keep up with 
       updates. Non-extractable keys help limit damage.

WHAT HELPS:
  ✅ Web Crypto API keys marked as non-extractable
     → crypto.subtle.deriveKey({ extractable: false })
     → Even if an attacker gets a reference to the key, they 
       cannot export it as raw bytes
     → They CAN still use it for encrypt/decrypt (it's in memory)
     → But they can't persist it for later use

  ✅ Strict CSP
     → Content-Security-Policy: default-src 'self'; 
       script-src 'self' 'nonce-{random}'; style-src 'self' 'unsafe-inline'
     → Prevents injection of unauthorized scripts

  ✅ Subresource Integrity (SRI)
     → All external resources loaded with integrity hashes
     → <script src="lib.js" integrity="sha384-..."></script>
```

### 6.2 "If the Worker Decrypts, It's Not Zero-Knowledge"

**The criticism:** True zero-knowledge means the server never sees plaintext. If the Worker decrypts for LLM calls, it's not zero-knowledge.

**Our response:** Guilty as charged. This is not zero-knowledge. It's **zero-knowledge at rest**.

```
THE ALTERNATIVES:
  1. Client-side LLM inference (WASM)
     → Run the LLM model in the browser
     → Truly zero-knowledge
     → But: slow, limited models, huge downloads, poor UX
     
  2. Homomorphic encryption
     → Encrypt data, LLM processes ciphertext, decrypt result
     → Truly zero-knowledge
     → But: impractical with current technology (orders of 
       magnitude slower, not supported by any major LLM API)
     
  3. Secure enclaves (SGX, TrustZone)
     → Worker runs inside a hardware enclave
     → Even Cloudflare can't peek
     → But: enclaves have their own vulnerabilities (side 
       channels), not available on Cloudflare Workers

  4. Trusted execution + attestation
     → User verifies the Worker code hasn't been tampered with
     → Then sends data for processing
     → But: complex, not standard on Cloudflare

OUR CHOICE: Accept the tradeoff.
  - We're honest about what we protect: database breaches, server 
    access at rest, and most importantly — your privacy from us.
  - The LLM provider sees your (PII-replaced) data regardless of 
    whether we encrypt it in transit or not.
  - The Worker is a thin proxy — it forwards and forgets.

HONEST POSITIONING:
  "We encrypt your data before storing it. During LLM processing, 
   our servers briefly handle plaintext. This is a deliberate 
   tradeoff: we chose fast, capable LLM analysis over theoretical 
   zero-knowledge processing. If you need absolute zero-knowledge, 
   consider running a local LLM."
```

### 6.3 "Key Derivation in JavaScript is Slow"

**The criticism:** PBKDF2 with 600K iterations takes 2-3 seconds in the browser. That's terrible UX.

**Our response:** That's the point.

```
WHY IT'S SLOW:
  PBKDF2 is intentionally computationally expensive.
  600K iterations × SHA-256 = ~2-3 seconds on a modern laptop
  This makes brute-force attacks expensive:
    - 1 attempt = 3 seconds
    - 100 attempts = 5 minutes
    - 1000 attempts = 50 minutes
    - With a 20-character passphrase, 2^100 combinations...
    - Universe heat death before brute-force succeeds

THE UX MITIGATION:
  1. Key derivation happens once per session, not per request
  2. Show a progress indicator during first login
  3. Cache the derived key in memory for the session
  4. Don't re-derive on page refresh (use sessionStorage cautiously,
     or require re-entry)
  5. Consider Web Workers for non-blocking derivation:
     ```javascript
     // Offload PBKDF2 to a Web Worker
     const worker = new Worker('/js/derive-worker.js');
     worker.postMessage({ passphrase, salt, iterations: 600000 });
     worker.onmessage = (e) => { masterKey = e.data; };
     ```

ALTERNATIVES:
  - Argon2id WASM: 0.5s at similar security level
    → Adds 300KB to bundle
    → Consider if users complain about login time
  - WebAuthn (passkeys): instant authentication
    → But still need a key derivation mechanism
    → Could wrap the master key with a hardware-bound key
```

### 6.4 "What About Quantum Computers?"

**The criticism:** Quantum computers will break encryption. Is log-origin future-proof?

**Our response:** Partially.

```
QUANTUM-RESISTANCE ANALYSIS:

AES-256-GCM (data encryption):
  ✅ QUANTUM-RESISTANT
  Grover's algorithm provides quadratic speedup: 2^128 operations 
  instead of 2^256. 2^128 is still computationally infeasible.
  NIST considers AES-256 quantum-safe.

ECDH / ECDSA (if we add them for key exchange):
  ❌ NOT QUANTUM-RESISTANT
  Shor's algorithm breaks elliptic curve cryptography in 
  polynomial time. If we add ECIES for key exchange, it 
  would be vulnerable.

PBKDF2 / SHA-256 (key derivation):
  ⚠️ PARTIALLY RESISTANT
  Grover's algorithm halves the effective iteration count.
  600K iterations → effectively 300K. Still expensive.
  Post-quantum KDFs exist (e.g., using lattice-based hashes)
  but are not standardized for this use case.

HMAC verification:
  ⚠️ Same as PBKDF2 — quadratic speedup but still secure.

TIMELINE:
  - Practical quantum computers: unknown (10-30 years?)
  - NIST post-quantum standards: finalized (CRYSTALS-Kyber, CRYSTALS-Dilithium)
  - Migration: when browser APIs support PQC natively

OUR PLAN:
  - AES-256 is fine for now
  - Monitor NIST PQC standards
  - When Web Crypto API adds PQC support, migrate key exchange
  - Key derivation can be increased (1.2M iterations → 600K effective)
```

### 6.5 "What If the User Loses Their Passphrase?"

**The criticism:** All encrypted data is lost. Forever. That's unacceptable for most users.

**Our response:** It's a feature, not a bug. But we need to make the UX forgiving.

```
THE HARD TRUTH:
  If you lose your passphrase, your data is gone.
  There is no recovery. There is no backdoor. There is no 
  "forgot password" button. This is the cost of true 
  client-side encryption.

COMPARISON:
  - Signal: Lose your device + no backup? Messages are gone.
  - 1Password: Lose your master password + no emergency kit? Vault is gone.
  - Bitwarden: Same.
  - ProtonMail: Lose your password + no recovery key? Account is gone.
  
  ALL serious encrypted systems have this property. It's not 
  unique to us.

WHAT WE SHOULD DO:
  1. On setup: Big, clear warning about passphrase importance
  2. Passphrase strength meter: guide users to 16+ chars, 
     preferably a passphrase ("correct horse battery staple")
  3. Passphrase hint: optional, stored in plaintext, helps 
     the user remember without revealing the key
  4. Recovery key export: immediately after setup, prompt 
     the user to download a recovery package:
     ```
     recovery.json:
     {
       "tenant_id": "abc123",
       "wrapped_deks": [...],
       "salt": "...",
       "verifier": "...",
       "note": "Import this in Settings > Recovery to restore access"
     }
     ```
  5. Recovery import: user uploads recovery.json + enters new 
     passphrase → re-derive master key → re-wrap DEKs

WHAT WE SHOULD NOT DO:
  ❌ Email the passphrase to the user
  ❌ Store the passphrase server-side
  ❌ Add a "security question" fallback (reduces to knowledge factor, 
     much easier to guess)
  ❌ Add a "backdoor key" held by us (defeats the entire purpose)

THE UNCOMFORTABLE ANSWER:
  Some data loss from forgotten passphrases is acceptable and 
  expected. The alternative (server-side key escrow) is worse. 
  We should design the UX to minimize this risk, not eliminate 
  the possibility entirely.
```

---

## 7. Open Questions

1. **Should we offer an "encrypted search" mode?** Storing PII-replaced text alongside ciphertext enables search but reveals structure. Is this worth the privacy tradeoff?

2. **Web Workers for key derivation?** Non-blocking PBKDF2 is important for UX. How do we handle the complexity of message-passing between the main thread and derivation workers?

3. **Recovery key format?** Should the recovery key be a mnemonic phrase (like seed phrases in crypto wallets) or a JSON file? Mnemonic is more user-friendly but harder to implement securely.

4. **LLM provider audit?** How do we verify that the LLM provider isn't training on our prompts? OpenAI says they don't train on API calls, but we have no way to verify this.

5. **PII replacement accuracy?** How do we measure false positive/negative rates? Should we run a benchmark against a labeled dataset?

6. **Multi-device key sync?** If a user wants to access their log on two devices, how do they get the master key to the second device without transmitting it through our server?

7. **Browser extension risk?** Should we recommend using a dedicated browser profile for log-origin? Or is this overkill?

8. **How often should DEKs be rotated?** Monthly? Per-session? Per-entry? The security-privacy-performance tradeoff needs user research.

---

*This document is a living design. It should be reviewed and updated before every release.*
