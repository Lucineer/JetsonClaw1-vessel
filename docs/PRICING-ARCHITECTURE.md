# COCAPN PRICING — 2026-04-05

## Core Principle
Keys never in code. Forks get zero secrets. Original repos = free playground (Casey subsidizes). Clones = BYOK only or Cocapn managed.

## Membership Tiers

### Free (no account)
- BYOK only — user provides their own keys
- No Cocapn API management
- Community features: trending, forks, equipment marketplace

### Pay-as-you-go (no membership)
- Cocapn manages API keys + routing
- **10% cost-plus** on inference
- Per-message billing
- For: casual users who don't want to manage keys

### Standard — $10/month
- Cocapn manages all API keys + routing
- **1% cost-plus** on inference
- Priority routing (faster models)
- Analytics dashboard
- For: individual developers, power users

### Gold — $50/month
- **Zero cost-plus** — at-cost inference
- Cocapn manages all keys, routing, caching
- Crystal graph, dead reckoning, fleet events
- Custom domains (user.studylog.ai)
- Equipment marketplace listing
- For: serious developers, small teams

### Enterprise — $200/month
- **$12/seat** on zero cost-plus
- White-label invoicing (our bill, their letterhead)
- We manage ALL API accounting across their org
- Monthly consolidated bill
- Internal pricing: enterprise dev charges their users $20+, we bill enterprise $12/seat
- SLA, priority support
- For: companies, agencies, app developers

## Why These Prices Work
- $10/mo Standard = cheaper than managing 3+ API keys yourself
- $50/mo Gold = one month of a junior dev's time to manage keys/routing/caching
- $200/mo Enterprise = cheaper than hiring someone to manage API billing
- $12/seat = the seat pays, not the company budget committee

## Fork/Clone Security
- Secrets via CF Secrets Store (env bindings) — NEVER in repo
- Forked repos = no CF secrets = playground credits don't work
- Forked repos = BYOK only (user adds their own keys)
- OR: user connects to Cocapn API → we manage keys → they pay membership
- This is BY DESIGN: free playground is a marketing funnel, not a product

## The Mobile/App Revenue Flywheel
1. Developer builds app using Cocapn fleet as backend
2. Developer signs up for Enterprise ($200/mo)
3. Developer's users get memberships ($12-50/mo each)
4. Developer charges users $20+/mo (their margin)
5. We bill developer $200 + $12/seat
6. Developer never touches API keys or billing
7. We send monthly invoice on developer's letterhead
8. Developer grows → more seats → more revenue for us
9. Enterprise's IT budget can't beat our price — too cheap to build internally

## Revenue Stack (in order)
1. **Enterprise seats** — $12/seat/mo, the main business
2. **Gold memberships** — $50/mo, power users
3. **Standard memberships** — $10/mo, casual pay-as-you-go
4. **Pay-as-you-go 10%** — non-members using Cocapn API
5. **Education/courses** — teaching people to use the fleet
6. **Hardware** — pre-built Jetson kits
7. **Equipment marketplace** — optional 10% cut on bounties/sales
8. **Analytics** — usage pattern data as market intelligence

## Key Insight
The price is so cheap it's not worth maintaining internally. That's the moat.
