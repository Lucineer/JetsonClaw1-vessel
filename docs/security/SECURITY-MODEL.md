# Security Model — log-origin

> **Version:** 0.1-draft  
> **Status:** Architecture design  
> **Last updated:** 2026-03-25

---

## Table of Contents

1. [Threat Model](#1-threat-model)
2. [Authentication](#2-authentication)
3. [Authorization](#3-authorization)
4. [API Security](#4-api-security)
5. [Worker Security](#5-worker-security)
6. [Open Questions](#6-open-questions)

---

## 1. Threat Model

### 1.1 Threat Matrix

| # | Threat | Attacker | Likelihood | Impact | Mitigation |
|---|--------|----------|-----------|--------|-----------|
| 1 | D1 database compromise (DB contents exfiltrated) | External hacker, CF insider | Medium | High | AES-256-GCM encryption at rest; DB stores ciphertext only |
| 2 | XSS steals passphrase from memory/DOM | Attacker via injected script | Medium | Critical | Strict CSP, SRI on all scripts, no passphrase in DOM, Web Crypto (not JS-visible keys) |
| 3 | KV store compromise (session tokens leaked) | External hacker, CF insider | Low | High | JWTs are short-lived (15min), HMAC-signed, rotation on use |
| 4 | Passphrase brute-force (online) | External attacker | High | High | Rate limiting (5 attempts/15min), bcrypt/Argon2 verification cost, progressive delays |
| 5 | Passphrase brute-force (offline — DB dump + hash) | External hacker | Low | Critical | HMAC-SHA256 with high-iteration PBKDF2-derived key; pepper stored in env var only |
| 6 | Worker env var exposure (secret leaks) | Misconfigured wrangler, CF dashboard breach | Low | High | Rotate secrets via wrangler secret, minimize stored secrets, use ephemeral DEKs |
| 7 | TLS MitM (Cloudflare → LLM provider) | Network attacker on provider side | Low | High | Cloudflare edge terminates TLS; provider connections use TLS 1.3; no plaintext in transit |
| 8 | CSRF on auth endpoints | Attacker via malicious site | Medium | Medium | SameSite=Strict cookies, anti-CSRF tokens on state-changing endpoints |
| 9 | Supply chain attack (CDN/JS dependency compromise) | Attacker compromises NPM/CDN | Low | Critical | SRI hashes on all CDN assets, lockfile auditing, minimal dependencies |
| 10 | Subrequest DoS (Worker makes unlimited outbound calls) | Attacker sends crafted request | Low | Medium | Subrequest limit (50/request), per-endpoint limits, timeout caps |
| 11 | SQL injection via D1 | Attacker via API input | Medium | High | Parameterized queries only (D1/SQLite API), input validation, no raw SQL concatenation |
| 12 | Session hijacking (token theft) | Attacker via XSS or network | Low | High | HttpOnly, Secure, SameSite=Strict cookies; short TTL; token binding to IP hint |
| 13 | Malicious browser extension reads encryption keys | Attacker via extension | Medium | Critical | Web Crypto API (keys never in JS heap); document CSP restrictions; extension isolation is out of scope |
| 14 | Cloudflare Worker code tampering | CF insider, compromised deploy pipeline | Low | Critical | Deploy via CI with branch protection, review wrangler.toml diffs, minimal Worker code surface |
| 15 | Timing attack on passphrase comparison | Attacker measuring response times | Low | Medium | Constant-time comparison (built into HMAC-SHA256 verification) |
| 16 | Cache poisoning (Cache API stores sensitive responses) | Attacker via cache key collision | Low | Medium | No sensitive data in Cache API; cache keys include tenant ID; no cross-tenant caching |
| 17 | DDoS on auth endpoint | Botnet | High | Low | Cloudflare rate limiting + JS challenge on `/auth/*` routes |

### 1.2 Threat Model Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        ATTACK SURFACES                          │
├──────────┬──────────┬──────────┬──────────┬─────────────────────┤
│ Browser  │  Worker  │    D1    │   LLM    │   Cloudflare Infra  │
│ (Client) │ (Edge)   │  (DB)    │ (Provider)│   (Platform)        │
├──────────┼──────────┼──────────┼──────────┼─────────────────────┤
│ • XSS    │ • Code   │ • SQLi   │ • Data   │ • KV/D1 access      │
│ • Ext.   │   inject │ • Encr.  │   leak   │ • Env var access    │
│ • Phish  │ • Subreq │ • Dump   │ • Prompt │ • Worker isolation  │
│ • Tab    │   abuse  │   theft  │   inject │   failure            │
│   nab    │ • Secret │ • Query  │          │ • Supply chain      │
│          │   leak   │   abuse  │          │   compromise        │
└──────────┴──────────┴──────────┴──────────┴─────────────────────┘
         │          │          │          │
         ▼          ▼          ▼          ▼
    ┌─────────────────────────────────────────┐
    │         DEFENSE IN DEPTH                 │
    │  1. Client-side encryption (keys never   │
    │     leave browser)                        │
    │  2. D1 stores ciphertext only             │
    │  3. Worker DEKs are request-scoped        │
    │  4. Strict CSP + SRI                      │
    │  5. Rate limiting everywhere              │
    │  6. Minimal secret footprint              │
    └─────────────────────────────────────────┘
```

---

## 2. Authentication

### 2.1 Passphrase-Based Auth

The system uses a single passphrase per tenant (the repo owner). This passphrase never leaves the client; only a hash is stored and compared.

#### Hash Storage

```javascript
// On setup (client-side, one-time):
const salt = crypto.getRandomValues(new Uint8Array(32));
const passphraseKey = await deriveKey(passphrase, salt, 600000);
// passphraseKey is also the master key for encryption

// HMAC of a known value for verification (NOT storing the derived key itself)
const verifier = crypto.getRandomValues(new Uint8Array(32));
const verifierHMAC = await crypto.subtle.sign(
  'HMAC',
  passphraseKey,
  verifier
);

// Stored in D1: { salt (hex), verifier (hex), verifier_hmac (hex) }

// On login (server-side, via Worker):
async function verifyPassphrase(passphrase, storedSalt, storedVerifier, storedHMAC) {
  // Re-derive key from passphrase + salt
  const candidateKey = await deriveKey(passphrase, fromHex(storedSalt), 600000);
  const candidateHMAC = await crypto.subtle.sign('HMAC', candidateKey, fromHex(storedVerifier));
  return constantTimeEqual(candidateHMAC, fromHex(storedHMAC));
}
```

> **Why HMAC verification, not storing the derived key hash?**  
> The derived key *is* the encryption master key. Storing any reversible derivation of it would weaken the encryption. Instead, we HMAC a random verifier — this proves the user knows the passphrase without storing anything that helps recover the key.

#### Key Derivation

```javascript
async function deriveKey(passphrase, salt, iterations = 600000) {
  const encoder = new TextEncoder();
  const keyMaterial = await crypto.subtle.importKey(
    'raw', encoder.encode(passphrase), 'PBKDF2', false, ['deriveKey']
  );
  return crypto.subtle.deriveKey(
    { name: 'PBKDF2', salt, iterations, hash: 'SHA-256' },
    keyMaterial,
    { name: 'AES-GCM', length: 256 },
    false,  // non-extractable
    ['encrypt', 'decrypt', 'wrapKey', 'unwrapKey', 'sign', 'verify']
  );
}
```

> **PBKDF2 with 600K iterations** — takes ~2-3 seconds in modern browsers. This is intentional: it makes online brute-force expensive. We considered Argon2id (superior memory-hard KDF) but WebAssembly implementations add 200KB+ bundle size and vary in quality across browsers. PBKDF2 is well-supported natively via Web Crypto.

### 2.2 JWT Token Flow

```
┌──────┐                    ┌────────┐                    ┌──────┐
│Client│                    │ Worker │                    │  D1  │
└──┬───┘                    └───┬────┘                    └──┬───┘
   │ POST /auth/login           │                             │
   │ {passphrase, salt_hint}    │                             │
   │───────────────────────────>│                             │
   │                            │ deriveKey(passphrase,salt)  │
   │                            │ verify HMAC against D1      │
   │                            │<────────────────────────────│
   │                            │                             │
   │  Set-Cookie: access_token  │  generate JWT:              │
   │  Set-Cookie: refresh_token │   access: 15min, HS256      │
   │<───────────────────────────│   refresh: 7d, HS256        │
   │                            │   store refresh in KV       │
   │                            │──────────────────────────>  │
   │                            │                         KV  │
```

#### JWT Structure

```json
// Access Token (15 min TTL)
{
  "sub": "tenant:abc123",
  "iat": 1711400000,
  "exp": 1711400900,
  "type": "access",
  "jti": "a1b2c3d4-uuid"
}

// Refresh Token (7 day TTL, stored in KV for revocation)
{
  "sub": "tenant:abc123",
  "iat": 1711400000,
  "exp": 1712000000,
  "type": "refresh",
  "jti": "e5f6g7h8-uuid"
}
```

#### Token Generation & Validation

```javascript
// Worker-side JWT operations
const JWT_SECRET = env.JWT_SECRET; // HMAC-SHA256 signing key (env var)

async function signJWT(payload) {
  const header = { alg: 'HS256', typ: 'JWT' };
  const headerB64 = b64url(JSON.stringify(header));
  const payloadB64 = b64url(JSON.stringify(payload));
  const data = `${headerB64}.${payloadB64}`;
  const sig = await crypto.subtle.sign(
    'HMAC',
    await getSigningKey(JWT_SECRET),
    new TextEncoder().encode(data)
  );
  return `${data}.${b64url(new Uint8Array(sig))}`;
}

async function verifyJWT(token) {
  const [headerB64, payloadB64, sigB64] = token.split('.');
  const data = `${headerB64}.${payloadB64}`;
  const sig = Uint8Array.from(atoburl(sigB64), c => c.charCodeAt(0));
  const valid = await crypto.subtle.verify(
    'HMAC',
    await getSigningKey(JWT_SECRET),
    sig,
    new TextEncoder().encode(data)
  );
  if (!valid) throw new AuthError('Invalid token');
  const payload = JSON.parse(atoburl(payloadB64));
  if (payload.exp < Date.now() / 1000) throw new AuthError('Token expired');
  return payload;
}
```

#### Refresh Flow

```
Client sends refresh_token cookie → Worker:
  1. Verify JWT signature + expiry
  2. Look up jti in KV — if missing, token was revoked
  3. Rotate: delete old jti from KV, generate new refresh pair
  4. Set new cookies
```

### 2.3 Session Management (KV-Backed)

```
KV Namespace: SESSIONS
Key:   "refresh:{jti}"        → Value: "{tenant_id, created_at}"
TTL:   7 days (auto-expire)

KV Namespace: RATE_LIMIT
Key:   "login:{ip}"           → Value: "{attempts, first_attempt_at}"
TTL:   15 minutes
```

### 2.4 Rate Limiting on Auth

| Endpoint | Limit | Window | Strategy |
|----------|-------|--------|----------|
| `POST /auth/login` | 5 attempts | 15 min | Per IP, progressive delay (1s → 2s → 4s → 8s → lockout) |
| `POST /auth/refresh` | 30 requests | 15 min | Per tenant |
| `POST /auth/setup` | 1 request | Per tenant | One-time, idempotent |

```javascript
// Pseudocode: rate-limited login
async function rateLimitedLogin(ip, tenantId, passphrase) {
  const key = `login:${ip}`;
  const state = await KV.get(key, 'json') || { attempts: 0, first: Date.now() };
  
  if (state.attempts >= 5) {
    const elapsed = Date.now() - state.first;
    if (elapsed < 15 * 60 * 1000) {
      const remaining = Math.ceil((15 * 60 * 1000 - elapsed) / 1000);
      throw new AuthError(`Locked out. Try again in ${remaining}s`, 429);
    }
    state.attempts = 0;
    state.first = Date.now();
  }
  
  const valid = await verifyPassphrase(passphrase, ...);
  if (!valid) {
    state.attempts++;
    await KV.put(key, JSON.stringify(state), { expirationTtl: 900 });
    throw new AuthError('Invalid passphrase');
  }
  
  await KV.delete(key); // Clear on success
  return generateTokenPair(tenantId);
}
```

### 2.5 Future: OAuth/OIDC Upgrade Path

The passphrase system is the bootstrapping mechanism. OAuth/OIDC (GitHub, Google, etc.) can be layered on top:

```
Phase 1 (now):    Passphrase → derives master key → auth
Phase 2 (later):  OAuth → verified identity → auth  
                  Passphrase → still needed for encryption key
Phase 3 (full):   OAuth → auth + key wraps via provider-side secret
                  (user trusts provider more than remembering passphrase)
```

> The passphrase is fundamentally a **key derivation seed**, not just an auth credential. Even with OAuth login, users still need a way to derive their encryption master key. Options: (a) store a wrapped key server-side (less secure), (b) keep passphrase derivation as the key source (current design), (c) use WebAuthn + biometric as a passkey (future).

---

## 3. Authorization

### 3.1 Single-User System

log-origin is a **personal log system**. Each deployment = one user (the repo owner). There is no RBAC, no admin panel, no multi-user.

```
Authorization model:
  Repo owner (passphrase holder) → FULL ACCESS
  Everyone else                  → DENIED
```

This simplicity is a security advantage: fewer code paths, fewer permission bugs.

### 3.2 Friend Access (Scoped, Time-Limited)

Planned feature: share a log entry or dashboard with a friend.

```javascript
// Share token structure
{
  "sub": "tenant:abc123",
  "scope": ["read:log:entry:xyz789"],  // specific entry only
  "iat": 1711400000,
  "exp": 1711486400,  // 24 hours
  "jti": "share-uuid",
  "grantee": "friend@email.com"
}
```

- Tokens are created by the owner via a UI action
- Scopes are additive and specific: `read:log:*`, `read:log:entry:{id}`, `read:dashboard:{id}`
- Maximum TTL: configurable per token, default 24h, max 7d
- Tokens stored in KV for revocation
- No write access for shared tokens — ever

### 3.3 Agent-to-Agent Auth

For future AI agent integrations (the system is called "log-origin" — logs from AI agents):

```javascript
// Agent token (capability-based)
{
  "sub": "agent:my-assistant",
  "tenant": "abc123",
  "capabilities": [
    { "action": "write:log", "resource": "log:*" },
    { "action": "read:log", "resource": "log:own" }  // only own entries
  ],
  "iat": 1711400000,
  "exp": 1714000000,
  "key_id": "agent-key-1"  // for key rotation
}
```

- Agents are provisioned by the owner with specific capabilities
- Agent keys are separate from the owner's passphrase
- Agent-written entries are tagged with the agent's identity
- Agents cannot read other agents' entries unless explicitly scoped

### 3.4 Cross-Repo Auth (Federation)

For the forkable-repo pattern — multiple repos sharing a single auth context:

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Repo A      │     │  Repo B      │     │  Repo C      │
│  (primary)   │     │  (fork)      │     │  (fork)      │
│  Has master  │     │  Delegates   │     │  Delegates   │
│  key store   │     │  to A        │     │  to A        │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │
       └────────────────────┼────────────────────┘
                            │
                    ┌───────▼───────┐
                    │  Signing Auth │
                    │  Authority    │
                    │  (Repo A)     │
                    └───────────────┘
```

- Primary repo holds the canonical tenant identity
- Forks carry a delegation token signed by the primary
- Workers verify the delegation chain before processing
- Federation is opt-in; each repo can run standalone

---

## 4. API Security

### 4.1 CORS Configuration

```javascript
// Default: strict — only same-origin
const CORS_STRICT = {
  'Access-Control-Allow-Origin': 'same-origin',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization',
  'Access-Control-Allow-Credentials': 'true',
  'Access-Control-Max-Age': '86400'
};

// For shared dashboard embeds (future):
const CORS_EMBED = {
  'Access-Control-Allow-Origin': specificOrigins, // explicit allowlist, never '*'
  'Access-Control-Allow-Methods': 'GET',  // read-only
  'Access-Control-Allow-Credentials': 'true'
};
```

> **Rule: Never use `Access-Control-Allow-Origin: *` with `Allow-Credentials: true`.**

### 4.2 Request Validation

```javascript
// Body size limits per endpoint
const LIMITS = {
  'POST /api/log':     100_000,   // 100KB per log entry
  'POST /api/import':  1_000_000, // 1MB for bulk import
  'POST /auth/login':  1_024,     // 1KB passphrase
  'DEFAULT':           10_000     // 10KB
};

// Content-Type enforcement
function validateRequest(request, limit) {
  const ct = request.headers.get('Content-Type');
  if (!ct?.includes('application/json')) {
    throw new ValidationError('Content-Type must be application/json');
  }
  if (request.headers.get('Content-Length') > limit) {
    throw new ValidationError('Request body too large');
  }
}
```

### 4.3 Input Sanitization

```javascript
// D1 parameterized queries (SQL injection prevention)
// GOOD — parameterized
await env.DB.prepare(
  'SELECT * FROM logs WHERE tenant_id = ? AND created_at > ?'
).bind(tenantId, dateStr).all();

// BAD — concatenation (this would be a critical bug)
await env.DB.prepare(
  `SELECT * FROM logs WHERE tenant_id = '${tenantId}'`
).all();

// XSS prevention: all user content is stored as-is but rendered via textContent,
// never innerHTML. Markdown rendering uses a sanitized parser (e.g., DOMPurify).
```

### 4.4 Response Filtering

```javascript
// Never leak internal errors in production responses
function safeResponse(error) {
  const status = error.status || 500;
  
  if (status >= 500) {
    // Internal error — log details, return generic message
    console.error(`[${error.code}] ${error.message}`, error.stack);
    return new Response(JSON.stringify({ error: 'Internal server error' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
  
  // 4xx errors can include details
  return new Response(JSON.stringify({
    error: error.message,
    code: error.code
  }), { status, headers: { 'Content-Type': 'application/json' } });
}
```

### 4.5 Rate Limiting Per Endpoint

| Endpoint Category | Limit | Window | Scope |
|---|---|---|---|
| Auth endpoints | 5/min | 15 min | Per IP |
| Read (GET) | 100/min | 1 min | Per tenant |
| Write (POST/PUT) | 30/min | 1 min | Per tenant |
| Delete | 10/min | 1 min | Per tenant |
| Import/Bulk | 3/hour | 1 hour | Per tenant |

Rate limiting is implemented via KV with atomic increments and TTL-based expiry. For higher-scale needs, Cloudflare's built-in Rate Limiting rules can supplement application-level checks.

---

## 5. Worker Security

### 5.1 V8 Isolate Properties

Cloudflare Workers run in **V8 isolates**, not VMs or containers. Security implications:

| Property | Security Benefit | Security Limitation |
|---|---|---|
| No filesystem access | Can't read/write files on the host | Can't load CA certs, can't use file-based secrets |
| No network sockets | Can't open raw TCP/UDP | Must use `fetch()` — all outbound traffic is HTTPS only |
| Per-request isolation | State doesn't leak between requests | Can't maintain in-memory state (use KV/R2) |
| Memory limits (128MB) | Limits damage from memory corruption | Can't load large datasets into memory |
| CPU limits (10ms billed) | Limits computation time | Can't do heavy crypto (Argon2id is borderline) |
| No `eval()` on origin | Reduces dynamic code injection risk | Some libraries use `eval` internally — must audit |

> **Key insight:** V8 isolates provide strong sandboxing. Even if a Worker is compromised, the attacker cannot access other tenants, the filesystem, or raw network. The blast radius is limited to the KV/D1 data that specific Worker has access to.

### 5.2 Subrequest Limits

- **Maximum 50 subrequests** per request (free plan: 50, paid: varies)
- **No WebSocket** in Workers (must use Durable Objects for persistent connections)
- Each subrequest has a **30-second timeout**

```
Can this be exploited?
  • Attacker could craft a request that triggers many subrequests → 
    Worker hits limit → 503 error. This is DoS, not data exfiltration.
  • Mitigation: count subrequests, fail fast at limit/2, don't cascade.
  • Outbound fetches go only to allowlisted LLM provider domains.
```

### 5.3 Secrets Management

```
┌─────────────────────────────────────────────────────┐
│                  SECRETS HIERARCHY                   │
├────────────────┬────────────────────────────────────┤
│ Level 1        │ JWT_SECRET, HMAC_PEPPER            │
│ (wrangler env) │ Set via `wrangler secret put`      │
│                │ Available as env vars in Worker     │
│                │ NOT in D1, NOT in KV                │
│                │ Rotation: manual via wrangler CLI   │
├────────────────┼────────────────────────────────────┤
│ Level 2        │ Refresh tokens (revocable)          │
│ (KV)           │ TTL-based expiry, manual revocation │
│                │ Encrypted at rest by Cloudflare      │
├────────────────┼────────────────────────────────────┤
│ Level 3        │ Log entry ciphertext                │
│ (D1)           │ Client-side AES-256-GCM encrypted  │
│                │ Even with DB access, data is unread │
├────────────────┼────────────────────────────────────┤
│ Level 4        │ User's passphrase-derived master key│
│ (Browser only) │ NEVER leaves the browser            │
│                │ No server-side copy, no backup       │
└────────────────┴────────────────────────────────────┘
```

> **Critical rule:** The encryption master key is derived client-side from the passphrase. It is **never** transmitted to the server, stored in D1, or cached in KV. The Worker receives wrapped (encrypted) data, decrypts it only transiently for LLM API calls, and discards the DEK immediately after.

### 5.4 Log Redaction

What gets logged by the Worker:

| Log Type | Content | Redacted? |
|---|---|---|
| Request metadata | Method, path, status, duration, tenant ID | No — needed for debugging |
| Auth events | Login success/failure, token refresh | Yes — no IP, no user agent, no passphrase |
| Errors | Error code, stack trace (sanitized) | Yes — no user data in messages |
| Subrequest metadata | Provider URL, status, duration | No — needed for monitoring |
| User data | Log entry content, PII | **NEVER logged** |

```javascript
// Structured logging example
console.log(JSON.stringify({
  ts: new Date().toISOString(),
  level: 'info',
  event: 'request',
  method: request.method,
  path: request.url,  // could leak path params — sanitize
  tenant: tenantId,
  status: 200,
  duration_ms: 12,
  // NEVER: request.body, auth.token, user passphrase
}));
```

---

## 6. Open Questions

1. **Argon2id via WASM?** — Bundle size vs. security tradeoff. If we ship Argon2, the 200KB WASM blob adds attack surface. Is PBKDF2 at 600K iterations sufficient? For a single-user personal tool, probably yes. For higher-value targets, probably no.

2. **WebAuthn / Passkey support?** — Biometric auth is great for UX but doesn't solve the key derivation problem. We'd need a way to wrap the encryption key with a hardware-bound key. This is solvable but complex.

3. **Session fixation on refresh tokens?** — If an attacker steals a refresh token, they can rotate it and lock out the legitimate user. Mitigation: email/device notification on token rotation, or require re-auth for rotation.

4. **What happens when Cloudflare's KV has an outage?** — Auth becomes unavailable. Should we fall back to local token validation (accepting the risk of unrevoked tokens during outage)?

5. **Can we use Cloudflare Access instead of custom auth?** — For teams/multi-user, yes. For single-user with client-side encryption, no — Cloudflare Access doesn't integrate with key derivation.

6. **Security audit scope?** — Before public launch, we need a third-party audit of: (a) the encryption implementation, (b) the auth flow, (c) the Worker code. Budget TBD.

7. **What if Workers are backdoored by Cloudflare?** — This is an unmitigatable trust assumption. The same applies to any hosted platform (AWS Lambda, Vercel, etc.). Mitigation: reproducible builds, open-source Worker code, community review.

---

*This document is a living design. It should be reviewed and updated before every release.*
