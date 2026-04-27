# Night Shift Execution Plan
**Date:** 2026-04-26 21:00 AKDT
**Directive:** Casey: "continue working on all our repos. I am going to bed. don't stop. there is lots of work to do if you look around"
**Status:** IN PROGRESS

## Priority Triage

### P0: gpu-native-room-inference (main research repo)
- Has 82 CUDA files but README says 69 suites, 64 rules
- Suites 70-72 committed but README not updated
- deckboss/ C API exists
- **Work:** Update README with suites 70-72 results, clean up stale temp .cu files in /tmp, ensure all benchmark results are documented

### P1: JetsonClaw1-vessel (my vessel repo)
- Messy root — dozens of .cu files, stale experiment dirs (suite57-69), old .md files
- Has shell/, memory/, SHELL/ — good structure
- **Work:** Clean up root, move .cu files to benchmarks/, archive old docs, update README

### P2: cuda-* crates (6 crates)
- All published, doctests fixed and pushed
- **Work:** Cross-reference dependencies, verify `cargo test --all` works together, add interop examples

### P3: capitaine / capitaine-ai
- capitaine = repo-as-agent, capitaine-ai = Cloudflare Workers version
- **Work:** Verify they work, update READMEs, ensure fleet continuity (CLAUDE.md)

### P4: flux-* repos (30+ repos)
- Large fleet of FLUX crates — many are thin Rust/Go/C wrappers
- **Work:** Spot-check READMEs, fix broken ones, ensure consistent structure

### P5: plato-* repos
- Core PLATO ecosystem repos
- **Work:** Audit, ensure consistent fleet branding and cross-links

### P6: zeroclaws / cocapn-* / misc
- ZeroClaw MUD agents, cocapn fleet modules
- **Work:** Low priority, audit if time permits

---

## Execution Order

### Phase 1: gpu-native-room-inference cleanup (now)
- [ ] Read suites 70-72 source and results
- [ ] Update README with new suite data
- [ ] Verify CMakeLists.txt covers all benchmarks
- [ ] Add results documentation for suites 70-72

### Phase 2: JetsonClaw1-vessel cleanup (next)
- [ ] Move root-level .cu files to benchmarks/
- [ ] Archive stale experiment dirs
- [ ] Clean up old doc files
- [ ] Update vessel README

### Phase 3: cuda-* crate interop (then)
- [ ] Test all 6 crates build together
- [ ] Add workspace example
- [ ] Update READMEs with usage examples

### Phase 4: capitaine repos (then)
- [ ] Audit and update both repos

### Phase 5: flux-* fleet sweep (if time)
- [ ] Spot check 10 most important flux-* repos
- [ ] Fix stale/broken READMEs

### Phase 6: Push everything (continuous)
- [ ] Git push after each meaningful change

## Notes
- Casey sleeping ~midnight AKDT, work until morning or until I run out of things
- Push frequently per standing orders
- Log progress to memory/2026-04-26.md
