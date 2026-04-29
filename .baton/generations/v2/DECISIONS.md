# DECISIONS.md — Key Decisions with Rationale

## Architecture Decisions (Cumulative, Suites 1-45)

### Kernel Architecture
1. **V7 (contig8 general shuffle) is the production kernel** — 105M room-qps at 1024 rooms. General stride-32 loop beats hardcoded unroll because register spilling kills stride-8 at 256 threads/block. (suite #30)
2. **Batch <=32 → V1 baseline; 32-64 → V4 fused+vec+multi; >=64 → V7** — each kernel wins in its regime. (suite #30)
3. **8 rooms per block, 256 threads (32 per warp = 1 room)** — contiguous warp layout eliminates shared memory entirely. Warp shuffle for reduction. (suite #29)

### Memory Architecture
4. **Row-major weight layout is optimal** — don't try interleaved or transposed. Interleaved is 5x slower at scale. (suite #41)
5. **Zero-copy output (cudaHostAllocMapped) is mandatory** — eliminates D2H copy (3.7x at 1 room, 15.48us → 0.001us). (suite #14)
6. **L2 cache handles input reuse perfectly** — no need for shared memory or constant memory for input vector. (suite #42)
7. **Direct-mapped weights beat gather** — gather kernel adds 378% overhead. (suite #18)

### Pipeline Architecture
8. **Double-buffered async pipeline eliminates sync** — 104.1M room-qps by removing cudaStreamSynchronize from hot path. (suite #33)
9. **CUDA Graphs not worth complexity** — only 1.01x at large batch. Sync barrier is the bottleneck, not launch. (suite #32)
10. **Don't combine CUDA Graphs with Streams** — 0.88x, they conflict. (suite #11)
11. **Pipeline parallelism doesn't work on single GPU** — stream sync adds more overhead than overlap. Fusion is the answer. (suite #26)
12. **Don't prefetch on unified memory** — cudaStreamWaitEvent sync overhead (~2us) > overlap savings. (suite #25)

### System Architecture
13. **Weight-swap architecture** — 31,000x faster room switching vs engine rebuild. (suite #10)
14. **Batch rooms, never dispatch per-room** — 130x advantage. (suite #11)
15. **4 CUDA streams is the sweet spot** — 4 = 2.53x, 8 adds no benefit. (suite #5)
16. **Consolidate fleet inference requests** — one big batch > multiple small streams (2.6x faster). (suite #12)

### Warmup & Contention (NEW — Suites 44-45)
17. **Background compute REDUCES inference p99 by 3.5x** — warm SMs + warm memory bus = less scheduling jitter. Novel finding. (suite #44)
18. **10 memory warmups = 58% p99 reduction** — as effective as 1000 inference warmups. Pre-warm before production. (suite #45)
19. **Continuous memory background maintains improvement** — but continuous compute background causes tail spikes. (suite #45)
20. **Only H2D copies hurt under contention** — compute and memory bandwidth contention actually help. (suite #44)

### What Doesn't Work (Negative Results)
21. **Quantization doesn't help memory-bound dot products** — FP16 optimal; INT8/INT4 dequant overhead > savings. (suite #22)
22. **Half2 vectorization gives zero speedup at dim=256** — only 1.09x at dim=1024. (suite #24)
23. **Tensor Core WMMA is wrong workload shape** — 2.3-8.5x slower than V7 for dot products. (suite #37)
24. **Adaptive weights (scale+bias) fail** — 128% error with quantization artifacts. (suite #35)
25. **Stream priority is useless on Orin** — [-5, 0] range, no measurable effect. (suite #9)
26. **Persistent kernels don't work on unified memory** — host→device queue management deadlocks. (suite #10)
27. **Pinned memory NOT worth it on unified memory** — only 1.04x vs pageable. Use zero-copy instead. (suite #14)
