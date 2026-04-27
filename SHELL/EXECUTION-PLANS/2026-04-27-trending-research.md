# Execution Plan: Trending Edge Tech Research + Integration
**Date:** 2026-04-27 09:52 AKDT
**Directive:** Casey: "Research trending tech and git repos from the last month for ideas for new things to refactor into our plato systems. Especially edge."
**Status:** IN PROGRESS

## Phase 1: Install rtk (token savings) — IMMEDIATE WIN
- [ ] Download ARM64 Linux build
- [ ] Install to ~/.local/bin
- [ ] Test with common commands (ls, git status, cargo test)
- [ ] Measure actual token savings
- [ ] Update TOOLS.md with installation notes

## Phase 2: Benchmark LiteRT-LM on Jetson
- [ ] Clone and build LiteRT-LM from source
- [ ] Test with small model (Phi-4-mini or Qwen)
- [ ] Compare against our raw CUDA + TensorRT benchmarks
- [ ] Document results in edge-gpu-lessons repo

## Phase 3: Study GenericAgent skill crystallization
- [ ] Read their 3K-line core architecture
- [ ] Map their skill system to Plato spells/equipment
- [ ] Write integration analysis to fleet-onboarding or new repo

## Phase 4: Study hermes-agent learning loop
- [ ] Read their memory/compression system
- [ ] Compare with our baton compaction protocol
- [ ] Identify adoptable patterns for Plato

## Phase 5: Google AI Edge Gallery on Jetson
- [ ] Try APK or build from source
- [ ] Test on-device inference capabilities
- [ ] Document what works on ARM64/Jetson

## Notes
- xAI API key invalid — web_search broken, using web_fetch + GitHub trending
- rtk has ARM64 build — immediate install, no compilation needed
- LiteRT-LM supports Raspberry Pi — should work on Orin Nano
- All findings go to edge-gpu-lessons repo (not vessel)
