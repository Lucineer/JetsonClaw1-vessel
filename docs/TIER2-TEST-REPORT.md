# Tier 2 Test Report — Zero-Shot Visitor Audit

**Date:** 2026-04-02 16:13 AKDT  
**Repos tested:** reallog-ai, playerlog-ai, activelog-ai, activeledger-ai, cocapn  
**Also checked:** cocapn-lite (local code only)  
**Method:** curl, no API keys, no cookies

---

## Summary

| Repo | Landing | Health | Setup | Chat | Seed | Domain Routes | 404 | OPTIONS | Notes |
|------|---------|--------|-------|------|------|---------------|-----|---------|-------|
| **reallog-ai** | ✅ HTML | ✅ JSON | ✅ HTML | ⚠️ No provider | ✅ Rich seed | ✅ stories, media | 404 ✅ | 404 ✅ | Clean |
| **playerlog-ai** | ✅ HTML | ✅ JSON | ✅ HTML | ⚠️ No provider | ✅ Rich seed | ✅ coaching, agents, games | 404 ✅ | 404 ✅ | Clean |
| **activelog-ai** | ✅ HTML | ✅ JSON | ✅ HTML | ⚠️ No provider | ✅ Rich seed | ✅ routines, workouts | 404 ✅ | 404 ✅ | Clean |
| **activeledger-ai** | ✅ HTML | ✅ JSON | ✅ HTML | ⚠️ No provider | ✅ Rich seed | ✅ portfolio, trades, market | 404 ✅ | 404 ✅ | market has real data |
| **cocapn** | ✅ HTML | ✅ JSON | ⚠️ Falls through to landing | ⚠️ Falls through to landing | ✅ Full repo list | ✅ repos, fleet | 200 ⚠️ | 200 ⚠️ | SPA catch-all; no dedicated setup page |

**cocapn-lite:** Code exists at `/tmp/cocapn-lite/src/worker.ts` — not tested as a deployment.

---

## Per-Repo Details

### reallog-ai
- **Landing:** "Organize Your Content Universe" — 5 feature cards (video, story pipeline, research, repo-agent, BYOK)
- **Health:** `{"status":"ok","service":"RealLog.ai","fleet":{"tier":2,"domain":"journalism-content"}}`
- **Setup:** BYOK provider selector UI with provider cards
- **Chat:** `{"error":"No provider configured. Visit /setup"}` — expected, no keys
- **Seed:** Journalism frameworks (Inverted Pyramid, AP Style), content types, editorial pipeline, media formats, sourcing principles
- **Domain routes:** `/api/stories` → `{"stories":[]}`, `/api/media` → `{"media":[]}` — empty but valid
- **Edge cases:** 404 on nonexistent, 404 on OPTIONS ✅

### playerlog-ai
- **Landing:** "Your AI Gaming Partner" — 5 features (screen feed, AI coach, repo-agent players, vibe-coded games, BYOK)
- **Health:** `{"status":"ok","service":"PlayerLog.ai","fleet":{"tier":2,"domain":"gaming-intelligence"}}`
- **Setup:** Same BYOK UI pattern, orange theme
- **Chat:** No provider error (expected)
- **Seed:** Gaming genres (FPS, MOBA, RPG…), coaching frameworks, game design patterns, performance metrics
- **Domain routes:** `/api/coaching` → `{"sessions":[]}`, `/api/agents` → `{"agents":[]}`, `/api/games` → `{"games":[]}`
- **Edge cases:** 404/404 ✅

### activelog-ai
- **Landing:** "Train Smarter" — 5 features (workout tracking, OpenMAIC routines, sessions, AI coach, BYOK)
- **Health:** `{"status":"ok","service":"ActiveLog.ai","fleet":{"tier":2,"domain":"athletics-training"}}`
- **Setup:** BYOK UI, green theme
- **Chat:** No provider error (expected)
- **Seed:** Training frameworks (linear periodization, 5/3/1, HIIT…), muscle groups, principles, sport-specific options
- **Domain routes:** `/api/routines` → `{"routines":[]}`, `/api/workouts` → `{"workouts":[]}`
- **Edge cases:** 404/404 ✅

### activeledger-ai
- **Landing:** "Finance-Focused Repo-Agents" — gradient green-gold title, 5 features (trading agents, portfolio, market analysis, risk mgmt, BYOK)
- **Health:** `{"status":"ok","service":"ActiveLedger.ai","fleet":{"tier":2,"domain":"finance-trading"}}`
- **Setup:** BYOK UI, emerald theme
- **Chat:** No provider error (expected)
- **Seed:** Trading strategies, risk management frameworks, market analysis types, asset classes
- **Domain routes:** `/api/portfolio` → `{"portfolio":[]}`, `/api/trades` → `{"trades":[]}`, `/api/market` → **Rich response** with supported strategies, analysis types, risk frameworks + note about external API integration
- **Edge cases:** 404/404 ✅

### cocapn
- **Landing:** "The Repo-Agent Platform" — purple-blue gradient, 6 feature cards, full ecosystem directory (14 repos with tier badges)
- **Health:** `{"status":"ok","service":"cocapn.ai","fleet":{"totalRepos":14,"tiers":{"1":5,"2":5,"3":4}}}`
- **Setup:** ⚠️ No dedicated setup page — falls through to landing page SPA
- **Chat:** ⚠️ POST `/api/chat` falls through to landing HTML — no API handler
- **Seed:** Full repo manifest with tiers, architecture info, fleet protocol version
- **Domain routes:** `/api/repos` → full repo list with URLs, `/api/fleet` → fleet version and tier breakdown
- **Edge cases:** ⚠️ `/nonexistent` returns **200** (SPA catch-all), OPTIONS returns **200** — not true 404s

### cocapn-lite
- **Code exists** at `/tmp/cocapn-lite/src/worker.ts` — not deployed to workers.dev, code-only check

---

## Issues Found

| Severity | Repo | Issue |
|----------|------|-------|
| ⚠️ Medium | cocapn | No dedicated `/setup` route — falls through to landing |
| ⚠️ Medium | cocapn | No `/api/chat` handler — POST returns landing HTML |
| ⚠️ Low | cocapn | SPA catch-all returns 200 for nonexistent routes (no proper 404) |
| ⚠️ Low | cocapn | OPTIONS preflight returns 200 (may be intentional for SPA) |

---

## Grades

| Repo | Grade |
|------|-------|
| **reallog-ai** | A |
| **playerlog-ai** | A |
| **activelog-ai** | A |
| **activeledger-ai** | A+ (richest domain route responses) |
| **cocapn** | B (missing setup page, no chat endpoint, SPA 404 issue) |

**Overall Tier 2: A-** — All repos are live, healthy, and functional. Cocapn's SPA catch-all and missing routes are the only real issues.
