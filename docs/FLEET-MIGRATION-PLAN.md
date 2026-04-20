# Cocapn Fleet Migration & Reengineering Plan
## 2026-04-03 — Casey Directive: Full migration to dad's CF account

## The Pivot

### Old System
- API keys hardcoded or stored in KV (encrypted)
- All repos on magnus-digennaro.workers.dev
- Single account, single set of keys
- No user isolation

### New System: "Zero-Keys-in-Code"
- **ALL API keys via Cloudflare Secrets Store** (env bindings)
- User sets keys at https://dash.cloudflare.com/?to=/:account/secrets-store/
- Each deployment has its own keys
- Free tier fallback: built-in routing to free endpoints for quick start
- Docker containers on dad's account for heavier workloads

## Cloudflare Secrets Architecture

### Worker Env Bindings (wrangler.toml)
```toml
[vars]
AGENT_NAME = "StudyLog.ai"

# Secrets (set via CF dashboard, never in code):
# OPENAI_API_KEY
# ANTHROPIC_API_KEY
# DEEPSEEK_API_KEY
# SILICONFLOW_API_KEY
# MOONSHOT_API_KEY
# ZAI_API_KEY
```

### Key Hierarchy (worker reads from env, no KV storage)
1. **env.SECRET_KEY** — User's own key from CF Secrets Store (highest priority)
2. **Built-in free fallback** — Routes to free-tier models (Cloudflare Workers AI or free SiliconFlow models)
3. **No key mode** — Read-only, no chat, just landing page

### BYOK Module Rewrite
```
loadBYOKConfig(request, env):
  1. Check env.OPENAI_API_KEY → if set, use as provider
  2. Check env.DEEPSEEK_API_KEY → fallback
  3. Check env.SILICONFLOW_API_KEY → fallback
  4. Check cookie/header (browser-side BYOK for non-deployed users)
  5. Free tier: use CLOUDFLARE_ACCOUNT_ID + Workers AI (free 10K neurons/day)
  6. No key: return null → landing page only
```

## Pricing Architecture: Pay-For-Convenience

### Philosophy
- We make money from SAVING consumers costs through synergy
- Community developing together → bulk pricing on inference
- Global training for more token-effective systems
- Pay-for-convenience, not profit from consumers

### Membership Tiers

| Tier | Cost | LLM Markup | Features |
|------|------|-----------|----------|
| **Free** | $0 | 20% cost-plus | Free tier models, ad-supported, 50 req/day |
| **Standard** | $5/mo | 2% cost-plus | All providers, 5K req/day, no ads |
| **Gold** | $15/mo | At cost | Unlimited, Docker containers, priority |
| **Enterprise** | $50/seat/mo | At cost | Gold benefits, discounted per-seat, SLA, custom domain support |

### How It Works
- Free users: routed to free-tier models (Cloudflare Workers AI), ads on loading screen
- Paid members: their own API keys via CF Secrets, we route through our optimization layer
- Docker containers: Gold+ can spin up GPU containers for heavy tasks (training, batch processing)
- Our margin comes from:
  - Membership fees (not per-token)
  - Ad revenue (free tier loading screens)
  - Bulk inference negotiation (we buy tokens wholesale, pass savings to members)
  - Docker container hosting fees (cost-plus)

## Migration Plan

### Phase 1: Deploy All Repos to Dad's Account (NOW)
- 34 repos total: 7 already done + 27 remaining
- Create KV namespaces for repos that need them
- Update all wrangler.toml with new account ID

### Phase 2: Reengineer BYOK Module
- Strip all hardcoded keys from byok.ts
- Rewrite loadBYOKConfig() to use env bindings first
- Add free-tier fallback (Cloudflare Workers AI)
- Add setup page that directs users to CF Secrets Store
- Cookie/header BYOK still works for non-deployed demo users

### Phase 3: Docker Integration
- Cloudflare Containers (when available) or Hyperbeam/Val.town
- Gold+ members get container allocation
- Spin up for heavy tasks, spin down to save costs

### Phase 4: Membership System
- Stripe integration for payments
- API key management dashboard
- Usage tracking and rate limiting per tier
- Ad injection for free tier

## New Repos to Build

### 1. fleet-orchestrator (CRITICAL)
Central control plane for all fleet deployments. Health checks, updates, secret rotation.

### 2. membership-api
Stripe integration, tier management, usage tracking, rate limiting.

### 3. docker-gateway
Container lifecycle management for Gold+ members.

### 4. free-tier-router
Routes free users to available free models with ad injection.

### 5. byok-v2 (library, not standalone repo)
Drop-in replacement for byok.ts that uses env bindings + CF Secrets Store.

## Account Structure

### Dad's Account (049ff5e84ecf636b53b162cbb580aae6)
- casey.digennaro@gmail.com
- Paid Workers plan
- All production deployments
- Docker containers (when available)
- casey-digennaro.workers.dev subdomain

### Casey's Account (future)
- Casey's own keys
- Personal deployments
- Forks from dad's account

### User Accounts (self-service)
- Sign up → get CF account (free) → deploy cocapn vessel → set keys in Secrets Store
- Or: use our hosted fleet (paid tier) → we manage everything

---

*Superinstance & Lucineer (DiGennaro et al.) — 2026-04-03*
