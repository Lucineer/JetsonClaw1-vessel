# Code Audit Report
**Date:** 2026-04-02  
**Repos Audited:** 13

---

### === dmlog-ai ===
Syntax: ✅ | ESM (.js): ✅ (0 missing) | Secrets: ✅ (false positives only) | try/catch: 47 | SA: ✅ | BYOK: ✅ | CSP: ✅ | Export: ✅ | Size: 1703 lines ⚠️ | package.json: ✅
**SCORE: 9/10**  
**FIXES:** worker.ts >1000 lines (1703) — consider splitting

### === makerlog-ai ===
Syntax: ✅ | ESM (.js): ✅ (0) | Secrets: ✅ (false positives) | try/catch: 1 ⚠️ | SA: ✅ | BYOK: ✅ | CSP: ❌ (0) | Export: ✅ | Size: 61 lines | package.json: ✅
**SCORE: 8/10**  
**FIXES:** Missing CSP header; only 1 try/catch

### === personallog-ai ===
Syntax: ✅ | ESM (.js): ✅ (0) | Secrets: ✅ (false positives) | try/catch: 4 | SA: ✅ | BYOK: ✅ | CSP: ✅ | Export: ✅ | Size: 194 lines | package.json: ✅
**SCORE: 10/10**  
**FIXES:** None

### === studylog-ai ===
Syntax: ✅ | ESM (.js): ❌ (1 missing) | Secrets: ✅ (false positives) | try/catch: 1 ⚠️ | SA: ✅ | BYOK: ✅ | CSP: ✅ | Export: ✅ | Size: 359 lines | package.json: ✅
**SCORE: 8/10**  
**FIXES:** 1 ESM import missing .js extension; only 1 try/catch

### === fishinglog-ai ===
Syntax: ✅ | ESM (.js): ✅ (0) | Secrets: ✅ (false positives) | try/catch: 4 | SA: ✅ | BYOK: ✅ | CSP: ❌ (0) | Export: ✅ | Size: 99 lines | package.json: ✅
**SCORE: 9/10**  
**FIXES:** Missing CSP header

### === luciddreamer-ai ===
Syntax: ✅ | ESM (.js): ✅ (0) | Secrets: ✅ (false positives) | try/catch: 5 | SA: ✅ | BYOK: ✅ | CSP: ✅ | Export: ✅ | Size: 301 lines | package.json: ✅
**SCORE: 10/10**  
**FIXES:** None

### === deckboss-ai ===
Syntax: ✅ | ESM (.js): ✅ (0) | Secrets: ✅ (false positives) | try/catch: 0 ⚠️ | SA: ✅ | BYOK: ✅ | CSP: ✅ | Export: ✅ | Size: 171 lines | package.json: ❌ (missing)
**SCORE: 7/10**  
**FIXES:** Missing package.json; 0 try/catch blocks

### === businesslog-ai ===
Syntax: ✅ | ESM (.js): ✅ (0) | Secrets: ✅ (false positives) | try/catch: 45 | SA: ✅ | BYOK: ✅ | CSP: ✅ | Export: ✅ | Size: 1505 lines ⚠️ | package.json: ✅
**SCORE: 9/10**  
**FIXES:** worker.ts >1000 lines (1505) — consider splitting

### === cocapn ===
Syntax: ✅ | ESM (.js): ✅ (0) | Secrets: ✅ | try/catch: 0 ⚠️ | SA: ✅ (unused) | BYOK: ❌ | CSP: ✅ | Export: ✅ | Size: 115 lines | package.json: ✅
**SCORE: 7/10**  
**FIXES:** Missing BYOK module; 0 try/catch; SA present but unused

### === reallog-ai ===
Syntax: ✅ | ESM (.js): ❌ (5 missing) | Secrets: ✅ (false positives) | try/catch: 2 | SA: ✅ (unused) | BYOK: ✅ | CSP: ✅ | Export: ✅ | Size: 138 lines | package.json: ✅
**SCORE: 8/10**  
**FIXES:** 5 ESM imports missing .js extension; SA present but unused

### === playerlog-ai ===
Syntax: ✅ | ESM (.js): ❌ (5 missing) | Secrets: ✅ (false positives) | try/catch: 3 | SA: ✅ (unused) | BYOK: ✅ | CSP: ✅ | Export: ✅ | Size: 148 lines | package.json: ✅
**SCORE: 8/10**  
**FIXES:** 5 ESM imports missing .js extension; SA present but unused

### === activelog-ai ===
Syntax: ✅ | ESM (.js): ❌ (5 missing) | Secrets: ✅ (false positives) | try/catch: 2 | SA: ✅ (unused) | BYOK: ✅ | CSP: ✅ | Export: ✅ | Size: 135 lines | package.json: ✅
**SCORE: 8/10**  
**FIXES:** 5 ESM imports missing .js extension; SA present but unused

### === activeledger-ai ===
Syntax: ✅ | ESM (.js): ✅ (0) | Secrets: ✅ (false positives) | try/catch: 2 | SA: ✅ (unused) | BYOK: ✅ | CSP: ✅ | Export: ✅ | Size: 149 lines | package.json: ✅
**SCORE: 9/10**  
**FIXES:** SA present but unused

---

## Summary

| Repo | Score | Key Issues |
|------|-------|-----------|
| dmlog-ai | 9/10 | Large worker (1703 lines) |
| makerlog-ai | 8/10 | No CSP, low try/catch |
| personallog-ai | 10/10 | ✅ Clean |
| studylog-ai | 8/10 | 1 missing .js, low try/catch |
| fishinglog-ai | 9/10 | No CSP |
| luciddreamer-ai | 10/10 | ✅ Clean |
| deckboss-ai | 7/10 | Missing package.json, no try/catch |
| businesslog-ai | 9/10 | Large worker (1505 lines) |
| cocapn | 7/10 | No BYOK, no try/catch, SA unused |
| reallog-ai | 8/10 | 5 missing .js, SA unused |
| playerlog-ai | 8/10 | 5 missing .js, SA unused |
| activelog-ai | 8/10 | 5 missing .js, SA unused |
| activeledger-ai | 9/10 | SA unused |

### Priority Fixes
1. **deckboss-ai** — missing package.json (deployment blocker)
2. **reallog/playerlog/activelog-ai** — 5 ESM imports each missing `.js` extension
3. **makerlog-ai, fishinglog-ai** — missing CSP headers
4. **cocapn** — missing BYOK module, no error handling
5. **dmlog-ai, businesslog-ai** — worker files >1000 lines (refactor)

### Notes
- No actual hardcoded secrets found; all matches were false positives (parameter names, CSS selectors, PII detection patterns, documentation strings)
- All repos pass syntax checks
- Soft actualize is present in all repos but unused in cocapn, reallog, playerlog, activelog, and activeledger
