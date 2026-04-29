# STATE.md — Generation 2 Full State Restoration

## Active Work
Running GPU benchmark suites on Jetson Orin Nano 8GB for the `gpu-native-room-inference` project. Overnight sustained execution per Casey directive "Continue as long as you can."

**Project:** `/home/lucineer/.openclaw/workspace/gpu-native-room-inference/`
**GitHub:** `https://github.com/Lucineer/gpu-native-room-inference.git`
**Vessel:** `/home/lucineer/.openclaw/workspace/` → `github.com/Lucineer/JetsonClaw1-vessel.git`

## Suites Completed This Generation (41-45)

### Suite #41: Memory Layout (`mem_layout.cu`)
- Row-major weight layout is optimal. Interleaved 5x SLOWER at scale (cache thrashing).
- Files: `mem_layout.cu`, `MEM_LAYOUT_RESULTS.md`

### Suite #42: Input Reuse (`input_reuse.cu`)
- Global/shmem/const memory all within 5%. L2 cache handles 512B input perfectly.
- Files: `input_reuse.cu`, `INPUT_REUSE_RESULTS.md`

### Suite #43: Pareto Frontier (`pareto.cu`)
- <10us p99: 768 rooms, 89M qps. <20us: 2048 rooms, 142M qps. <50us: 3072 rooms, 161M qps (PEAK).
- Cost: 100K rooms at 50us SLA = 24 Jetsons = $5,976.
- Files: `pareto.cu`, `PARETO_RESULTS.md`

### Suite #44: Mixed Workload Contention (`contention_mixed.cu`)
- Background compute REDUCES inference p99 from 16us to 4.6us (3.5x improvement).
- Memory bandwidth saturation also helps. Only H2D copies hurt.
- Novel finding: warm SMs + warm memory bus = less scheduling jitter.
- Files: `contention_mixed.cu`, `CONTENTION_MIXED_RESULTS.md`

### Suite #45: GPU Warmup Effects (`warmup_effect.cu`)
- 10 memory warmups = 1000 inference warmups for latency reduction.
- Cold: p99=16.2us -> Warmed: p99=6.8us (58% reduction), p999=38.5->13.3us (65%).
- Continuous memory bg maintains improvement. Continuous compute bg causes tail spikes.
- Files: `warmup_effect.cu`

## All-Time Records (45 suites)
- Peak throughput: 161M room-qps (3072 rooms, async pipeline)
- Peak kernel-only: 149M room-qps (suite #40)
- Best latency: 3.87us kernel minimum (suite #40)
- Best real-world: 23.5M room-qps end-to-end at 1024 rooms (suite #31)
- Best sustained: 93.8M room-qps over 10M inferences (suite #28)
- Best jitter: p99/p50=1.030x sustained (suite #28)
- V7 kernel: 105M room-qps at 1024 rooms, dim=256 (suite #30)
- Warm GPU p99: 4.6us at 256 rooms with background compute (suite #44)
- 30+ optimization rules documented

## Technical Constraints
- Compile: `/usr/local/cuda-12.6/bin/nvcc -arch=sm_87 -O3`
- No sudo (no ncu, no nvidia-smi -pm 1)
- DeepSeek credits exhausted (no subagents)
- PyPI token LOST (need Casey to re-provide)
- Git push: use `exec(background=true)` (5 min pack-objects)
- Oracle1 dark ~5 days

## Environment
- Jetson Orin Nano 8GB, sm_87, 1024 CUDA cores, ARM64
- CUDA 12.6, Linux 5.15.148-tegra
- Thermal: 48-55C sustained, junction max 100C, no throttle
- Power: ~5.8W GPU idle, ~11.3W total, ~4.9W sustained inference
- Memory bandwidth: 25-44 GB/s practical (unified memory)
- L2 cache: 2MB, 11x speedup for hot rooms
- OpenClaw 2026.3.13

## Pending
1. Update docs (research paper, optimization guide, README) with suites 41-45
2. Get PyPI token from Casey
3. Continue suites 46+ (ideas: L2 bank conflicts, warp scheduling, multi-GPU sim)
4. Check fleet bottles (Oracle1/FM)
5. Sync submodule in main vessel workspace

## Git State
- gpu-native-room-inference: all committed and pushed
- JetsonClaw1-vessel: submodule updated, pushed
- No uncommitted changes
