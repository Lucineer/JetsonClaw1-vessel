# TensorRT On-Device Benchmark Results
**Date:** 2026-04-24 08:58 AKDT
**Hardware:** Jetson Orin Nano 8GB (sm_87), CUDA 12.6, TensorRT 10.3.0
**Method:** Native on-device engine building — no cross-compilation, no x86 host

## Executive Summary

All room inference architectures benchmark at **13,000-21,700 qps** on the Jetson Orin Nano. Engine build times are **0.3-1.5 seconds**. This means a deckboss instance can build, deploy, and swap room models in real-time without any pre-compilation step.

## Results

| Model | Architecture | Build (s) | QPS | Mean Latency | P99 Latency | Engine Size |
|-------|-------------|-----------|------|-------------|-------------|-------------|
| tiny_room_64 | 64→32→64 | 0.34 | 20,935 | 0.040 ms | 0.051 ms | 0.03 MB |
| small_room_128 | 128→64→128 | 0.31 | 21,487 | 0.040 ms | 0.051 ms | 0.08 MB |
| medium_room_256 | 256→128→256 | 0.31 | 21,301 | 0.041 ms | 0.053 ms | 0.27 MB |
| deep_room_256 | 256→256→128→256 | 0.46 | 19,615 | 0.047 ms | 0.064 ms | 0.53 MB |
| wide_room_512 | 512→256→512 | 0.33 | 21,290 | 0.044 ms | 0.061 ms | 1.02 MB |
| embedding_room_768 | 768→384→768 | 0.33 | 21,689 | 0.049 ms | 0.072 ms | 2.27 MB |
| attention_room_256 | Transformer (4-head, 256d) | 1.48 | 13,127 | 0.088 ms | 0.109 ms | 3.08 MB |

## Key Findings

### 1. Sub-millisecond inference across the board
Even the heaviest model (attention/transformer) runs at 0.088ms mean — well under the 1ms real-time threshold. Simple MLP rooms are 4x faster at 0.040ms.

### 2. On-device engine building is practical
Build times of 0.3-1.5 seconds mean room models can be compiled at deploy time. No need for a cloud build pipeline or pre-compiled engines. A deckboss instance can:
- Receive a new room model definition
- Build the TRT engine on-device
- Start serving inference in under 2 seconds

### 3. MLP room size barely matters
64-dim and 768-dim MLP rooms run at nearly identical QPS (20,935 vs 21,689). The GPU compute is so fast that launch overhead dominates. Only the attention model shows meaningful slowdown.

### 4. Attention is the bottleneck
The transformer room is 35% slower than the fastest MLP — but still 13K qps. This is the first architecture where model complexity actually shows in the numbers.

### 5. Engine sizes are tiny
All engines fit comfortably in GPU memory. The largest (attention) is 3MB. You could cache hundreds of room engines.

## Implications for deckboss

- **Room hot-swap:** Build + deploy a new room in <2s without downtime
- **Fleet deployment:** Push ONNX models, let each Jetson build its own engines
- **No build server dependency:** Each edge device is self-sufficient
- **Memory budget:** 100 room engines = ~50MB GPU memory. Negligible on 8GB.

## Methodology

- `trtexec --useSpinWait --duration=3` for stable GPU clock measurements
- All engines built natively on Jetson (no cross-compilation)
- SpinWait prevents clock throttling during measurement
- 3-second measurement window per model
- FP16 precision throughout (TensorRT default for GPU)
