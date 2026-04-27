# Active Orders

## 2026-04-26 20:56 AKDT — Casey: Night Shift (ALL REPOS)
**Status:** COMPLETE
**Directive:** "continue working on all our repos. I am going to bed. don't stop. there is lots of work to do if you look around"
**Plan:** SHELL/EXECUTION-PLANS/2026-04-26-night-shift.md

### Results:
- Phase 1: gpu-native-room-inference — 72 suites, 71 rules ✅
- Phase 2: Vessel cleanup — 15 stale dirs, 78MB freed, secrets scrubbed ✅
- Phase 3: cuda-* crates — 6 crates, 88/88 tests, workspace interop ✅
- Phase 4: flux-runtime-c — 39/39 tests, Makefile fix ✅
- Phase 5: Repo sweep — all clean, purplepincher.org committed ✅
- Phase 6: Fleet footer — 8 vessel repos updated ✅
- Phase 7: Context architecture reset — 63KB → 17KB bootstrap ✅
- Phase 8: New repos — fleet-onboarding, cocapn-architecture, edge-gpu-lessons ✅
- Phase 9: Bottles to Forgemaster + Oracle1 ✅

## 2026-04-26 21:40 AKDT — Casey: Trending Tech Research + Repo Cleanup
**Status:** IN PROGRESS
**Directive:** "Research trending tech and git repos from the last month for ideas for new things to refactor into our plato systems. Especially edge. Get all uncommitted changes taken care of of course."

## 2026-04-27 06:01 AKDT — Casey: Context Architecture Reset (PLATO-FIRST)
**Status:** COMPLETE
**Directive:** Context lives in Plato/standalone repos, not bootstrap. Shell = skeleton only.
### Steps:
- [x] Slim MEMORY.md: 35KB → 2KB
- [x] Trim AGENTS.md: 10KB → 2KB
- [x] Trim STANDING_ORDERS.md: 4KB → 1.3KB
- [x] Clean ORDERS-ACTIVE.md: archive completed cron orders
- [x] Set bootstrapTotalMaxChars=25000 in openclaw.json
- [x] Push GPU lessons, craftmind, flux, cocapn tiles to Oracle1 vessel
- [x] Create fleet-onboarding, cocapn-architecture, edge-gpu-lessons repos
- [x] Update BOARDING.md with Plato-first onboarding protocol
- [x] Fleet footer on 8 vessel repos
- [x] Bottles to Forgemaster + Oracle1
