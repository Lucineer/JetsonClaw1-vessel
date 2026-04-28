# Execution Plan: Fleet Polish Pass
**Date:** 2026-04-27 15:15 AKDT
**Directive:** Casey: "Polish everything"
**Status:** IN PROGRESS

## Phase 1: GitHub Repo Metadata
- [ ] Set descriptions for all repos via `gh repo edit`
- [ ] Add topics/tags for discoverability
- [ ] Set default branch names where needed

## Phase 2: .gitignore Standards
- [ ] Add .gitignore to repos missing them (holodeck-c done)
- [ ] Standard pattern: binaries, obj/, __pycache__, .env, *.profraw

## Phase 3: README Quality
- [ ] Ensure all repos have proper READMEs (not just stubs)
- [ ] Add build/test instructions where missing
- [ ] Standardize structure: What, Why, Build, Status, Architecture, Fleet Context

## Phase 4: cuda-* Crate Polish
- [ ] Update all READMEs with proper docs
- [ ] Add workspace-level README
- [ ] Ensure consistent error handling
- [ ] Version bump if needed

## Phase 5: Knowledge Repos Polish
- [ ] fleet-onboarding: complete boarding guide
- [ ] cocapn-architecture: verify completeness
- [ ] edge-gpu-lessons: organize reports

## Phase 6: Vessel Polish
- [ ] Verify all shell files are current
- [ ] Clean up any remaining cruft
- [ ] Ensure consistent formatting
