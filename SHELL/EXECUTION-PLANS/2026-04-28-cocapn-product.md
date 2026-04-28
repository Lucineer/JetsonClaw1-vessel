# Execution Plan: Cocapn.ai Full Product Build
**Date:** 2026-04-28
**Directive:** Casey: "Yes. Full throttle" — build the complete cocapn.ai product
**Status:** IN PROGRESS

## Phase 1: Auth System (API)
- [ ] /v1/auth/signup — email + password → user record in KV
- [ ] /v1/auth/login — email + password → JWT token
- [ ] /v1/auth/me — validate JWT → user info
- [ ] API key generation on signup (cocapn_ prefix)
- [ ] Rate limiting per user tier

## Phase 2: Landing Page
- [ ] Hero section with value prop
- [ ] Pricing table (4 tiers)
- [ ] Model comparison
- [ ] "Get Started" → signup
- [ ] Clean, dark theme matching chat UI

## Phase 3: Dashboard
- [ ] /dashboard — usage history, cost breakdown
- [ ] Daily/weekly/monthly spend graphs
- [ ] Model usage pie chart
- [ ] Per-request cost log

## Phase 4: Settings Page
- [ ] /settings — manage Cocapn API keys
- [ ] BYOK provider key management (stored encrypted in KV)
- [ ] Subscription tier display
- [ ] Account deletion

## Phase 5: SPA Router
- [ ] Hash-based routing (#/, #/chat, #/dashboard, #/settings)
- [ ] Auth state management
- [ ] Shared layout (header, nav)

## Phase 6: Polish + Deploy Prep
- [ ] Mobile responsive
- [ ] Error states, loading states
- [ ] wrangler.toml with KV bindings
- [ ] D1 schema for usage logging
- [ ] Deploy instructions
