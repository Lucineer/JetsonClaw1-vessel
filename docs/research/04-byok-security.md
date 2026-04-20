# BYOK Security Models

## Overview

Bring Your Own Key (BYOK) in AI platforms lets users provide their own API keys for LLM providers, rather than the platform managing keys centrally. This shifts cost, control, and security responsibilities.

## Why BYOK Matters

- **Cost control**: Users pay directly for their own API usage — no middleman markup
- **Data sovereignty**: API calls go directly from user's infrastructure to the provider — platform never sees the key or the data in transit
- **Provider choice**: Users pick their preferred model/provider
- **Compliance**: In regulated environments, BYOK can satisfy data handling requirements
- **Rate limit isolation**: Each user gets their own rate limits, not shared pool limits

## Security Architecture

### Key Storage

**Client-side (browser)**
- Keys stored in browser localStorage/sessionStorage
- Transmitted directly to provider APIs from the client
- Platform never touches the key
- Risk: XSS can steal keys; use Content Security Policy, HttpOnly cookies where possible
- Best for: Low-stakes applications, individual use

**Encrypted server-side**
- User provides key → server encrypts with user-derived key (or app-level encryption key) → stores ciphertext
- Key is decrypted only at request time, used to make the API call, then discarded
- Risk: Server compromise exposes encrypted keys (need strong encryption + key management)
- Best for: Multi-device access, team settings

**Vault-based (HashiCorp Vault, AWS Secrets Manager, etc.)**
- Keys stored in dedicated secret management service
- Fine-grained access policies, audit logging, automatic rotation
- Most secure but highest operational complexity
- Best for: Enterprise/team deployments

**Hybrid: Key proxy**
- User provides key → stored encrypted server-side
- A proxy service (e.g., LiteLLM, OpenAI proxy) handles API calls
- Proxy adds usage tracking, rate limiting, caching
- Keys never leave the proxy boundary
- Best for: Platforms that need metering and control while respecting BYOK

### Key Rotation

- **Manual rotation**: User updates key in settings. Simple but prone to forgotten rotations.
- **Provider-driven rotation**: Some providers (AWS, GCP) support automatic rotation with aliasing. The app references an alias; the provider swaps the underlying key.
- **Prompted rotation**: Platform detects key age and prompts user to rotate before expiry.
- **Multi-key support**: Allow users to configure multiple keys (primary + fallback). If primary fails (rate limit, revocation), fall back automatically.

### Multi-Provider Considerations

Each provider has different auth mechanisms:
- **OpenAI**: Bearer token in Authorization header
- **Anthropic**: x-api-key header
- **Google AI**: API key as query parameter OR OAuth2 service account
- **Azure OpenAI**: Subscription key or Azure AD token
- **AWS Bedrock**: Sigv4 signing (most complex — requires AWS SDK)
- **Cohere, Mistral, etc.**: Usually x-api-key or Bearer token

The proxy pattern (LiteLLM, OpenRouter) normalizes these into a single interface.

## Threat Model

| Threat | Mitigation |
|--------|-----------|
| XSS steals key from browser | CSP headers, avoid localStorage, use short-lived tokens |
| Server breach exposes keys | Encrypt at rest, minimize key surface, audit access |
| Key reuse across services | Encourage per-service keys, detect leaked keys (GitHub token scanning) |
| Key logged in plaintext | Never log keys; use hash/identifier for logging |
| User shares key publicly | Scanning for leaked keys, rate limit alerts, auto-revocation |
| Man-in-the-middle | TLS everywhere, certificate pinning for mobile |

## Actionable Recommendations for Cocapn

1. **Start with client-side BYOK**: For MVP, store keys in browser and make API calls directly from the client. This is the simplest and most secure for a single-user scenario. The platform server never sees keys.

2. **Use a proxy for multi-user**: When you need usage tracking, rate limiting, or multi-device support, deploy a lightweight proxy (LiteLLM is excellent — open source, normalizes providers, adds caching). The proxy handles key management server-side.

3. **Encrypt keys at rest**: If storing server-side, use AES-256-GCM with a key derived from a master secret (not the user's password — use an app-level encryption key stored in env/secrets). Never store plaintext keys in your database.

4. **Key validation on input**: When a user provides a key, immediately validate it by making a lightweight API call (e.g., list models). This catches typos and revoked keys before the user needs them.

5. **Provider abstraction layer**: Build an interface that normalizes all providers. Don't hardcode OpenAI-specific logic throughout your codebase. LiteLLM can do this for you, or build your own thin wrapper.

6. **Fallback chains**: Allow users to configure primary + fallback providers. If OpenAI is down or rate-limited, automatically fall back to Anthropic. This improves reliability.

7. **Usage dashboard**: Show users their per-provider usage and estimated costs. This builds trust and helps them manage spending.

8. **Key rotation UX**: Make rotation a one-click operation. Pre-validate the new key before deactivating the old one. Support a grace period where both keys work simultaneously.

## Anti-Patterns

- Storing plaintext keys in a database
- Logging API keys (even partially — log a hash instead)
- Using a single shared key for all users (defeats the purpose of BYOK)
- No key validation on input (user discovers their key is bad when they need it most)
- Ignoring provider-specific auth requirements (AWS Sigv4 is not just a header)
