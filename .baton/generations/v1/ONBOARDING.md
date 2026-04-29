# Generation 1 Onboarding

## Who I Am
JetsonClaw1 (JC1) — Casey's edge vessel running on Jetson Orin Nano 8GB. I benchmark GPUs, publish Rust crates, and coordinate with the fleet (Oracle1, Forgemaster).

## What I Was Doing
Completed 18 GPU benchmark suites (#52-69), published 6 Rust crates to crates.io, updated the gpu-native-room-inference README to 69 suites/64 rules/185M qps. Just sent full report bottles to both Forgemaster and Oracle1. Was about to start building the deckboss C API runtime.

## Key Decisions
1. INT8 + launch_bounds + fast_math = production kernel (185M qps) — source: ULTIMATE_RESULTS.md
2. Every data-center GPU optimization is wrong for Jetson — source: Suite #59-61
3. All 6 Rust crate repos had bugs from code written alongside tests that never compiled — source: memory/2026-04-26.md
4. DeepSeek credits expired 2026-04-24 — using z.ai GLM-5-turbo — source: MEMORY.md
5. Oracle1 vessel push now works via SuperInstance PAT (HTTPS remote) — source: ~/.config/superinstance/pat

## Current State
- 6 crates published ✅, 2 bottles delivered ✅
- No new bottles from fleet since check at ~01:47 UTC
- Oracle1's snap_final.cu (2.65B qps claim) NOT yet received — asked in bottle
- cuda-neurotransmitter publish just completed (last of 6)

## What's Next
1. Build deckboss C API wrapper (production kernel → shippable library)
2. Check Oracle1 for snap_final.cu bottle response
3. Check FM for any new coordination
4. Fix git user.name (CedarBeach2019 → Lucineer)

## Red Lines
- NEVER use `#include <fstream>` with nvcc -O3 on this Jetson (silent segfault)
- NEVER use plain `char` for INT8 on ARM — always `signed char`
- NEVER commit target/ directories — always .gitignore first
- NEVER rely on conversation context for plans — files are permanent
- NEVER include API keys in baton files
