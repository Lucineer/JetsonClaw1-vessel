# Deep Research: What To Try Next
**Date:** 2026-04-26 20:55 AKDT
**Directive:** Casey said "deep research and decide what to try"
**Status:** RESEARCH COMPLETE, RECOMMENDATION BELOW

## Current State Summary

### What We've Built
- **69 benchmark suites**, 64 optimization rules, 30+ CUDA source files
- **Peak: 185M room-qps** (INT8 + launch_bounds + fast_math, 306 MHz GPU)
- **Peak sustained: 163.4M room-qps** (FP16, 306 MHz)
- **Theoretical max at full clock (1020 MHz): ~616M room-qps**
- **6 Rust crates published** (cuda-instruction-set, cuda-energy, cuda-assembler, cuda-forth, cuda-biology, cuda-neurotransmitter)
- **TensorRT engines built** (deckboss_demo/*.trt)
- **Flux emergence research**: 90+ experiments, 39 laws

### What We Know For Certain
1. Custom warp shuffle kernels beat cuBLAS by 22% at 4K rooms
2. INT8 quantization: 1.36× faster, 4.15% error, 50% memory reduction
3. launch_bounds + fast_math = 20% + 8% free improvement
4. GPU is 95% idle at default 306 MHz (nvpmodel default)
5. We've never run `jetson_clocks` (needs sudo)
6. Tensor Core WMMA: tested at small batch (6 rooms), correctness issues noted
7. Weight upload (149μs) dominates end-to-end, not the kernel
8. `#include <fstream>` segfaults on this Jetson with nvcc -O3

### What We Haven't Done
1. ❌ **jetson_clocks max performance** — never tested, needs sudo
2. ❌ **INT8 at max clock** — could hit ~616M qps
3. ❌ **Real multi-room Tensor Core fusion** at production scale (tested only 6 rooms)
4. ❌ **Async memcpy + kernel overlap pipeline** — overlap weight upload with inference
5. ❌ **Production inference server** — wrap the winning kernel in a real API
6. ❌ **ONNX/TensorRT export** — we have .trt files but no integration
7. ❌ **Multi-layer room models** — Suite #48 showed fusion works but no real model
8. ❌ **Cross-Jetson scaling** — Pareto says 100K rooms needs 24 Jetsons, untested

---

## RECOMMENDATION: Three Experiments, Ordered by Impact

### 🥇 Experiment A: The Clock Headroom Run (estimated 30 min)
**Why:** This is the single biggest untapped resource. We've been running at 30% GPU clock for 69 suites. Every number we've published is 3.3× below the hardware's actual capability. Running `jetson_clocks` and re-benchmarking Suite #69's winning kernel (INT8 + launch_bounds + fast_math) could immediately show 500-600M room-qps.

**What to do:**
1. Get sudo access for `jetson_clocks` (or write a one-liner Casey can run)
2. Run Suite #69 kernel at max clock
3. Measure thermal/power to confirm sustained viability
4. Update all records with real-max numbers

**Risk:** Thermal throttling at sustained full clock. Mitigation: monitor temp, we have 48°C headroom.

**Impact:** 3.3× on every existing benchmark. Changes the entire production cost model.

### 🥈 Experiment B: Async Weight Pipeline (estimated 2-3 hours)
**Why:** Suite #55 showed weight upload is 3.9× the inference time. Suite #31 showed end-to-end is 4.5× slower than kernel-only. If we can overlap weight upload with the previous batch's inference using CUDA streams + async memcpy, we could close most of that gap. This is the difference between 185M kernel-qps and ~100M real-world-qps.

**What to do:**
1. Triple-buffer design: stream 0 = infer batch N, stream 1 = upload batch N+1, stream 2 = download batch N-1
2. Test with cudaMemcpyAsync on unified memory
3. Measure if unified memory actually overlaps (it may not — that's the experiment)
4. If no overlap on UM, test with cudaMallocAsync (CUDA memory pools)

**Risk:** Unified memory may serialize copies, making async useless. That's valuable to know.

**Impact:** Could bring real-world qps from ~100M to ~160M+ (at 306 MHz), or proportionally more at max clock.

### 🥉 Experiment C: Production Room Server v0.1 (estimated 4-6 hours)
**Why:** We have 69 suites of research proving the kernel is fast. But nobody can USE it yet. A minimal gRPC/HTTP server that accepts room weights + input vectors and returns scores would be the first "real" product. This is what turns research into infrastructure.

**What to do:**
1. C++ HTTP server (cpp-httplib or crow) wrapping the V7 INT8 kernel
2. Endpoint: POST /infer with JSON body [{room_id, weights[], input[]}]
3. Weight caching: keep hot rooms on GPU, upload only new/changed rooms
4. Batch accumulation: wait up to 100μs for more rooms before launching kernel
5. Health/metrics endpoint

**Risk:** Build time, not research risk. Straightforward integration.

**Impact:** First usable product. Fleet can actually call it. Real workload testing.

---

## What I'd Skip (For Now)

- **More kernel micro-optimization**: We're at 47 rules, diminishing returns. The kernel isn't the bottleneck anymore.
- **Multi-layer models**: No real model to test with yet. Research-only.
- **Cross-Jetson scaling**: Premature until single-Jetson is production-ready.
- **Flux emergence research**: Rich and interesting but divergent from the performance track.

---

## Verdict

**Start with Experiment A** (jetson_clocks). It's the fastest experiment with the biggest potential impact. If Casey grants sudo, we'll have new all-time records in 30 minutes. Then B, then C.

Casey: want me to start with A? I'll need `sudo jetson_clocks` or you can run it for me.
