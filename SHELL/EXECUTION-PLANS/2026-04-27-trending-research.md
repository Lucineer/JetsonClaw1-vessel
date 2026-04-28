# Execution Plan: Trending Edge Tech Research + Integration
**Date:** 2026-04-27 09:52 AKDT
**Directive:** Casey: "Research trending tech and git repos from the last month for ideas for new things to refactor into our plato systems. Especially edge."
**Status:** IN PROGRESS

## Phase 1: Install rtk (token savings) — ✅ COMPLETE
- [x] Download ARM64 Linux build
- [x] Install to ~/.local/bin
- [x] Test with common commands (ls, git status, cargo test)
- [x] Measure actual token savings (87% on verbose commands)
- [x] Update TOOLS.md with installation notes

## Phase 2: Benchmark LiteRT-LM on Jetson
- [ ] Clone and build LiteRT-LM from source
- [ ] Test with small model (Phi-4-mini or Qwen)
- [ ] Compare against our raw CUDA + TensorRT benchmarks
- [ ] Document results in edge-gpu-lessons repo

## Phase 3: Study GenericAgent skill crystallization — ✅ COMPLETE
- [x] Read their 3K-line core architecture
- [x] Map their skill system to Plato spells/equipment
- [x] Write integration analysis to fleet-onboarding or new repo

## Phase 4: Study hermes-agent learning loop — ✅ COMPLETE
- [x] Read their memory/compression system (context_compressor.py, 1350 lines)
- [x] Compare with our baton compaction protocol
- [x] Identify 7 adoptable patterns for Plato
- [x] Implement all 7 patterns in baton-compaction SKILL.md v3

## Phase 5: Google AI Edge Gallery on Jetson
- [ ] Try APK or build from source
- [ ] Test on-device inference capabilities
- [ ] Document what works on ARM64/Jetson

## Phase 6: agentskills.io ↔ Plato Bridge Design — ✅ COMPLETE
- [x] Study agentskills.io specification (YAML frontmatter + SKILL.md)
- [x] Map all fleet skills to Plato domains (Bridge, Workshop, Library, Lab, Dojo, Harbor)
- [x] Create fleet skills index tile (114 lines, 5.4KB)
- [x] Design 5-layer bridge architecture
- [x] Push to Forgemaster as bottle

## Notes
- xAI API key invalid — web_search broken, using web_fetch + GitHub trending
- rtk has ARM64 build — immediate install, no compilation needed
- LiteRT-LM supports Raspberry Pi — should work on Orin Nano
- All findings go to edge-gpu-lessons repo (not vessel)
- Oracle1 vessel push denied (403) — tile stored in workspace + bottle sent
- **BLOCKED**: Oracle1 vessel push needs SuperInstance org access
