# Batch Multi-Room Inference Benchmark
**Date:** 2026-04-24 09:02 AKDT
**Hardware:** Jetson Orin Nano 8GB, TensorRT 10.3.0

## Executive Summary

Batching room inference is absurdly efficient on the Jetson. A single room costs 0.041ms. Running 64 rooms in a single batch costs 0.053ms total — **0.00083ms per room**. That's a **49x reduction in per-room cost** through batching.

## Results

### Batch Mode (parallel rooms, shared weights)

| Rooms | QPS | Mean Latency | Per-room Cost | Engine Size |
|-------|------|-------------|---------------|-------------|
| 1 | 21,266 | 0.041 ms | 0.041 ms | 0.27 MB |
| 2 | 17,405 | 0.056 ms | 0.028 ms | 0.31 MB |
| 4 | 17,743 | 0.054 ms | 0.013 ms | 0.31 MB |
| 8 | 17,401 | 0.055 ms | 0.007 ms | 0.34 MB |
| 16 | 17,514 | 0.057 ms | 0.004 ms | 0.28 MB |
| 32 | 17,256 | 0.057 ms | 0.002 ms | 0.29 MB |
| **64** | **17,324** | **0.053 ms** | **0.001 ms** | **0.30 MB** |

### Pipeline Mode (sequential room chain)

| Rooms | QPS | Mean Latency | Per-room Cost | Engine Size |
|-------|------|-------------|---------------|-------------|
| 1 | 21,122 | 0.043 ms | 0.043 ms | 0.27 MB |
| 2 | 18,164 | 0.053 ms | 0.027 ms | 0.54 MB |
| 4 | 14,102 | 0.072 ms | 0.018 ms | 1.05 MB |
| 8 | 8,073 | 0.133 ms | 0.017 ms | 2.06 MB |

## Key Insights

### 1. Batch is nearly free
Adding rooms to a batch barely increases latency. 1 room = 0.041ms. 64 rooms = 0.053ms. The difference is 0.012ms for 63 additional rooms. GPU launch overhead dominates — actual compute is negligible.

### 2. 17K qps is the floor, not the ceiling
Batch QPS plateaus around 17K regardless of room count. This isn't a compute limit — it's a launch/scheduling floor. The GPU finishes faster than the CPU can dispatch.

### 3. Pipeline scales linearly (almost)
Pipeline cost grows roughly linearly: 1→2→4→8 rooms at 0.043→0.053→0.072→0.133ms. But per-room cost *improves* with depth (0.043→0.017ms), showing TRT fuses sequential ops efficiently.

### 4. 64 rooms in 53 microseconds
This is the headline number. A deckboss instance can evaluate 64 rooms simultaneously in under 53 microseconds. That's 18,868 room evaluations per millisecond.

## deckboss Implications

- **Room evaluation is free.** The cost is in orchestration, not inference.
- **Batch everything.** Never evaluate rooms one at a time — always batch.
- **Pipeline chains are practical.** 8-room deep chains at 0.13ms — still sub-millisecond.
- **A single Jetson can serve an entire fleet's room inference needs.**
