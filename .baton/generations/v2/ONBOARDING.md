# Generation 2 Onboarding

## Who I Am
JetsonClaw1 (JC1) — Casey's edge AI vessel running on a Jetson Orin Nano 8GB. I benchmark GPU-native room inference and push every result to GitHub.

## What I Was Doing
Running benchmark suites 41-45 overnight on `/home/lucineer/.openclaw/workspace/gpu-native-room-inference/`. Casey said "Continue as long as you can" and "you have work all day. go without stopping." 45 suites complete, 30+ optimization rules documented. All pushed to GitHub.

## Key Decisions
1. Row-major weight layout is optimal — don't change it (suite #41)
2. L2 cache handles input reuse — no need for shmem/const mem (suite #42)
3. Pareto frontier mapped: 161M room-qps peak at 3072 rooms (suite #43)
4. Background compute REDUCES inference p99 by 3.5× (suite #44)
5. 10 memory warmups = 58% p99 reduction (suite #45)

## Current State
- 45 suites complete, all committed and pushed
- Context at ~107% — compaction imminent
- Memory updated: `memory/2026-04-25.md`
- Git pushes all succeeded (confirmed by system messages)

## What's Next
1. Continue with suites 46+ — explore L2 cache bank conflicts, warp-level scheduling, or multi-GPU simulation
2. Update docs (research paper, optimization guide, README) with suites 41-45
3. Get PyPI token from Casey (lost during previous compaction)
4. Check Oracle1/fleet bottles

## Red Lines
- NEVER commit API keys/tokens to git
- Always use `background=true` for git push on ARM (5 min pack-objects)
- PyPI token is LOST — don't try to publish without it
- DeepSeek credits exhausted — no subagent spawning, do everything directly
- No sudo available — can't use ncu, nvidia-smi -pm 1
