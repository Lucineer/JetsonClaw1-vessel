# TASKS_NEXT.md — What To Do Next

## Immediate (Continue Benchmarking)

### Suite #46 Ideas (pick one)
1. **L2 cache bank conflicts** — measure if 8-warps-per-block causes bank conflicts when all access same input address simultaneously
2. **Warp-level preemption impact** — does context switching between warps in same block affect latency?
3. **Multi-GPU fleet scaling** — simulate 2-8 Orins with analytical model, validate suite #39 at small scale
4. **Input dimension sensitivity** — how does throughput scale from dim=64 to dim=4096? (partially done in suite #30 V7)
5. **NUMA-aware weight placement** — on Jetson, all memory is unified, but test if placement near SMs helps

### Suite #47+ Ideas
- **Real model workload** — actual neural network weights instead of random sin/cos
- **KV-cache simulation** — attention-style inference where input grows per room
- **Dynamic room addition/removal** — simulate fleet churn
- **Error correction** — what happens on memory errors? Can we detect them?

## Documentation Updates (HIGH PRIORITY)
1. **Research paper** (`docs/edge-gpu-utilization-problem.md`) — add sections 41-45
2. **Optimization guide** (`docs/edge-optimization-guide.md`) — add rules 29-31 (row-major layout, input reuse, GPU warmup)
3. **README** (`gpu-native-room-inference/README.md`) — update to 45 suites, 31 rules
4. **Submodule sync** — update vessel workspace submodule pointer

## Blocked Items
1. **PyPI token** — LOST during compaction. Ask Casey to re-provide. Needed for:
   - deckboss-runtime 0.1.1
   - fleet-git-agent 0.1.1
   - deckboss 0.1.1 metadata update
2. **Oracle1** — offline ~5 days. Check bottles but don't expect reply.
3. **Nsight Compute profiling** — requires sudo, not available

## Verification
- Next generation should: read this file, pick a suite idea, compile+run, commit+push, verify results
- Success = new benchmark data in `benchmarks/real_hardware/` with results .md file
- All pushes confirmed via `background=true` exec
