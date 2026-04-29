---
id: cocapn-architecture
created: 2026-04-28
updated: 2026-04-28
tags: [cocapn, product, architecture, cloudflare, ai]
---

# Cocapn-Architecture

cocapn.ai — AI chat proxy with smart model routing.

Three pillars: deckboss (design), cocapn (operate), capitaine (evolve)
Company: cocapn.com = billing, cocapn.ai = runtime

Tech stack:
- Cloudflare Workers (single 42KB worker)
- KV for auth, sessions, usage logging
- D1 for structured data
- Secrets Store for BYOK keys
- OpenAI-compatible API (Anthropic auto-converted)

Products:
- cocapn-chat: Chat UI + API proxy + dashboard + settings
- cocapn SDK: npm install cocapn (Node.js)
- cocapn-py: pip install cocapn (Python)
- cocapn-go: go get cocapn-go (Go)

4-tier pricing: Free, Builder ($9), Team ($29), Enterprise (custom)
