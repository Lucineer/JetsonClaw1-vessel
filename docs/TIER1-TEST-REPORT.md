# Tier 1 Test Report — Zero-Shot First-Time Visitor

**Date:** 2026-04-02  
**Tester:** Automated subagent (new user perspective)  
**Scope:** 8 repos × 6 test categories  

---

## Summary

| Repo | Score | Status |
|------|-------|--------|
| dmlog-ai | 7/8 | ✅ Good |
| makerlog-ai | 7/8 | ✅ Good |
| personallog-ai | 4/8 | ⚠️ Gaps |
| studylog-ai | 8/8 | ✅ Excellent |
| fishinglog-ai | 7/8 | ✅ Good |
| luciddreamer-ai | 3/8 | ❌ Needs Work |
| deckboss-ai | 2/8 | ❌ Needs Work |
| businesslog-ai | 4/8 | ⚠️ Gaps |

**Average: 5.3/8**

---

## Detailed Report Cards

### === dmlog-ai ===
**Landing:** ✅ Clean HTML, has `<title>`, mentions "DMLog.ai", has CTA ("Enter the Realm"), references `/css/style.css` (external file). No Cocapn mention. No CSP issues (has proper CSP header).  
**Health:** ✅ Valid JSON, `status: "ok"`, lists agent/files/lines. Missing fleet metadata (version, agentCount, timestamp) but has agent name and file stats.  
**Setup:** ✅ HTML with BYOK provider selection cards (OpenAI, DeepSeek, etc.), API key input, brand color #d4af37 (gold).  
**API Chat:** ✅ Returns themed error JSON: `"The spell fizzles..."` with code. Graceful handling.  
**API Seed:** ✅ Domain-specific content — D&D 5e rules, bounded accuracy, system prompt.  
**CORS:** ✅ OPTIONS returns 204.  
**404 Handling:** ✅ Returns 404.  
**Branding:** ✅ Title "DMLog.ai — Your AI Dungeon Master", gold (#d4af37) theme, D&D terminology.  

**OVERALL: 7/8**  
**Issues:** No Cocapn ecosystem mention on landing; health endpoint missing standard fleet metadata (version/agentCount/timestamp).

---

### === makerlog-ai ===
**Landing:** ✅ Full featured HTML page, `<title>`, mentions "MakerLog.ai", CTA "Get Started", Cocapn mention in footer, inline CSS. Has gallery images (may be broken — external placeholder URLs).  
**Health:** ✅ Full fleet metadata: version, agentCount, modules, seedVersion, timestamp.  
**Setup:** ✅ BYOK wizard with provider cards, brand color #00d4ff (cyan).  
**API Chat:** ✅ Returns `{"error":"No LLM configured","confidence":0}` — helpful.  
**API Seed:** ✅ Domain-specific: SOLID, DRY/KISS, TDD, Git strategies, 11 practices listed.  
**CORS:** ⚠️ OPTIONS returns 400 instead of 204 — CORS preflight may fail for browsers.  
**404 Handling:** ⚠️ Returns 200 for `/nonexistent` — should be 404.  
**Branding:** ✅ Title correct, cyan-to-purple gradient, features grid, footer links to Cocapn.  

**OVERALL: 7/8**  
**Issues:** CORS preflight returns 400; 404 routes return 200 (SPA fallback too broad). Gallery images likely broken (placeholder filenames).

---

### === personallog-ai ===
**Landing:** ✅ HTML with `<title>`, product name, Cocapn mention. Minimal — just hero + footer, no CTA button, no features.  
**Health:** ✅ Full fleet metadata, 8 modules listed.  
**Setup:** ❌ Returns `{"success":false,"error":"Not Found"}` — no setup wizard.  
**API Chat:** ❌ Returns `{"success":false,"error":"Not Found"}` — chat endpoint missing.  
**API Seed:** ✅ Domain-specific: CBT journaling, mindfulness, SMART goals, wellness prompts.  
**CORS:** ❌ OPTIONS returns 404.  
**404 Handling:** ✅ Returns 404.  
**Branding:** ⚠️ Title correct, indigo/cyan gradient, but landing page is extremely minimal — no features, no CTA, looks unfinished.  

**OVERALL: 4/8**  
**Issues:** No setup wizard, no chat endpoint, no CORS support, landing page is bare minimum.

---

### === studylog-ai ===
**Landing:** ✅ Rich HTML, `<title>`, product name, CTA "Get Started →", 8 feature cards, mentions "Cross-Cocapn" and "LogOS ecosystem".  
**Health:** ✅ Full fleet metadata, agentCount: 5, 9 modules, timestamp.  
**Setup:** ✅ BYOK wizard with dropdown (7 providers including Ollama), brand color #F59E0B (amber).  
**API Chat:** ✅ Returns helpful error: `"Missing profile ID — set X-Profile-Id header"`.  
**API Seed:** ✅ Domain-specific: spaced repetition, SM-2, Socratic steps, learning principles.  
**CORS:** ✅ OPTIONS returns 200.  
**404 Handling:** ✅ Returns 404.  
**Branding:** ✅ Title correct, amber theme, navy background, educational focus.  

**OVERALL: 8/8**  
**Issues:** None. This is the gold standard.

---

### === fishinglog-ai ===
**Landing:** ✅ HTML, `<title>`, product name "🎣 FishingLog.ai", CTA implicit (AI Chat card), Cocapn mention in footer, 6 feature cards, green/ocean theme.  
**Health:** ✅ Full fleet metadata, 6 modules.  
**Setup:** ✅ BYOK wizard with provider cards, brand color #4ade80 (green).  
**API Chat:** ✅ Returns `{"error":"No LLM configured","confidence":0}`.  
**API Seed:** ✅ Excellent — 25 Alaska species listed, techniques, seasons, Alaska-specific regulations.  
**CORS:** ⚠️ OPTIONS returns 400.  
**404 Handling:** ⚠️ Returns 200 for `/nonexistent`.  
**Branding:** ✅ Title correct, green/ocean gradient, Alaska fishing focus.  

**OVERALL: 7/8**  
**Issues:** CORS preflight returns 400; 404 routes return 200.

---

### === luciddreamer-ai ===
**Landing:** ✅ HTML with `<title>`, product name, Cocapn mention. But minimal — just hero + footer, no CTA, no features, no interactivity.  
**Health:** ✅ Full fleet metadata, 11 modules.  
**Setup:** ❌ `/setup` returns landing page HTML (no setup wizard — route not implemented).  
**API Chat:** ❌ Returns `{"error":"Not found"}`.  
**API Seed:** ✅ Domain-specific: content formats, repurposing practices.  
**CORS:** ❌ OPTIONS returns 404.  
**404 Handling:** ⚠️ Returns 200 for `/nonexistent`.  
**Branding:** ⚠️ Title correct, purple/pink gradient, but page is bare — looks like a placeholder.  

**OVERALL: 3/8**  
**Issues:** No setup wizard, no chat API, no CORS, 404 returns 200, landing page is just a stub with no CTA or features.

---

### === deckboss-ai ===
**Landing:** ✅ HTML with `<title>`, product name, Cocapn mention. Minimal — hero + footer only.  
**Health:** ✅ Full fleet metadata, 7 modules.  
**Setup:** ❌ `/setup` returns landing page HTML (same as root — no setup route).  
**API Chat:** ❌ `/api/chat` returns landing page HTML (not JSON!).  
**API Seed:** ✅ Domain-specific: spreadsheet formulas, cell types.  
**CORS:** ⚠️ OPTIONS returns 200 but content-type would be HTML.  
**404 Handling:** ❌ Everything returns 200 with landing page — no proper routing.  
**Branding:** ⚠️ Title correct, amber/red gradient, but the entire app seems to be a single HTML page with no backend routes.  

**OVERALL: 2/8**  
**Issues:** ALL API routes return HTML instead of JSON. No setup wizard. No chat endpoint. Catch-all routing returns landing page for everything. This appears to be a static page only.

---

### === businesslog-ai ===
**Landing:** ✅ Rich HTML, `<title>`, product name "🏢 BusinessLog.ai", 4 feature cards, inline chat UI, setup link. No Cocapn mention.  
**Health:** ✅ Full fleet metadata, agentCount: 2, 7 modules.  
**Setup:** ❌ `/setup` returns "404 Not Found" (plain text, not JSON).  
**API Chat:** ✅ Returns `{"error":"Missing or invalid authorization header"}` — good auth check.  
**API Seed:** ✅ Domain-specific: STAR, OKR, CRM patterns, meeting formats.  
**CORS:** ❌ OPTIONS returns 404.  
**404 Handling:** ✅ Returns 404.  
**Branding:** ⚠️ Title just "BusinessLog.ai" (no subtitle), blue theme, inline chat is nice touch. Missing Cocapn mention.  

**OVERALL: 4/8**  
**Issues:** No setup wizard (404), no CORS support, no Cocapn ecosystem mention.

---

## Cross-Repo Patterns

### ✅ What's Working Well
- **Health endpoints** — all 8 repos return valid JSON with `status: "ok"` and meaningful data
- **Seed endpoints** — all 8 return domain-specific content (this is excellent)
- **CSP headers** — dmlog-ai, studylog-ai, businesslog-ai have proper CSP; others don't set one
- **Branding** — each repo has a distinct color scheme and personality

### ❌ Common Issues
1. **CORS preflight** — only dmlog-ai (204), studylog-ai (200), and deckboss-ai (200) handle OPTIONS; others return 400 or 404
2. **404 handling** — makerlog-ai, fishinglog-ai, luciddreamer-ai, deckboss-ai return 200 for nonexistent routes (SPA fallback too broad)
3. **Setup wizard** — personallog-ai, luciddreamer-ai, deckboss-ai, businesslog-ai are missing setup pages
4. **Chat API** — personallog-ai, luciddreamer-ai, deckboss-ai don't have working chat endpoints
5. **Landing page completeness** — personallog-ai, luciddreamer-ai, deckboss-ai have stub/minimal pages with no CTA or features

### Priority Fixes
| Priority | Repo | Issue |
|----------|------|-------|
| 🔴 High | deckboss-ai | All API routes return HTML — no backend routing |
| 🔴 High | luciddreamer-ai | No setup, no chat, no CORS, stub page |
| 🟡 Medium | personallog-ai | No setup, no chat, no CORS |
| 🟡 Medium | businesslog-ai | No setup, no CORS |
| 🟢 Low | makerlog-ai, fishinglog-ai | CORS + 404 handling |
| 🟢 Low | dmlog-ai | Health metadata normalization, Cocapn mention |

### Gold Standard: studylog-ai
StudyLog.ai passes all 8 tests. It should be the template for the other repos.
