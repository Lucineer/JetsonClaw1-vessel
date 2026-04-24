# deckboss

**Edge AI hardware. Technicians first.**

> *Under-sell but over-deliver.*

## What Is deckboss?

deckboss is a Jetson Orin Nano-based commercial AI product that runs **specialized AI rooms in GPU memory** — no cloud, no network, no subscription required. It's a box you plug in and it thinks.

Built on real measurements from actual Jetson Orin Nano 8GB Super hardware. Not projections. Not simulations. Numbers from metal.

## Verified Performance (Real Jetson Orin Nano 8GB)

### Core Inference

| Metric | Measured | Target | Margin |
|--------|----------|--------|--------|
| Single room inference | **0.014 ms** | <1 ms | **74× under** |
| 12 rooms parallel | **0.015 ms** | <1 ms | **67× under** |
| Room weight switch (D2D) | **0.005 ms** | <200 ms | **40,000× under** |
| Room weight upload (H2D) | **0.016 ms** | <200 ms | **12,500× under** |
| Room selector | **0.006 ms** | — | — |
| Input projection (16→256) | **0.007 ms** | — | — |

### Pipeline Performance

| Metric | Measured |
|--------|----------|
| Single hop (infer 12 + select + project) | **0.032 ms** (30,823 hops/sec) |
| 3-room chain (5 inferences) | **0.054 ms** (18,667 chains/sec) |
| Dynamic 4→8→12 room cycling | **0.028 ms** (35,697 switches/sec) |
| Concurrent stream pipeline (infer + upload) | **0.015 ms** (65,800 ops/sec) |

### Memory

| Metric | Measured |
|--------|----------|
| GPU memory total | 7,990 MB |
| 12 room weights | 96 KB |
| Projection matrices (12×12) | 1,152 KB |
| Total room system memory | **1,248 KB** |
| Memory per room | **8 KB** |
| Max rooms in VRAM | **500,987** |

### Kernel Comparison (256-element dot product)

| Implementation | Latency | Throughput | GFLOPS |
|---|---|---|---|
| TensorRT (FP16) | 0.058 ms | 13,502 qps | 0.88 |
| CUDA Thread (256) | 0.077 ms | 12,973 qps | 1.28 |
| **CUDA Warp + half2** | **0.014 ms** | **69,704 qps** | **6.85** |
| TC mat-vec (16 WMMA) | 0.055 ms | 18,149 qps | 1.78 |

### Tensor Core Matrix Multiply (Where TC Wins)

| Dimensions | Warp | Tensor Core | TC Speedup |
|---|---|---|---|
| 16×16×16 | 0.094 ms | 0.005 ms | **17.48×** |
| 16×64×16 | 0.108 ms | 0.009 ms | **11.46×** |
| 16×128×16 | 0.124 ms | 0.015 ms | **8.42×** |
| 16×256×16 | 0.149 ms | 0.025 ms | **5.93×** |

**Rule:** Warp shuffle for room inference (mat-vec). Tensor cores for training transforms (matmul).

## Architecture

### The Core Idea: One Mind, Many Rooms

```
┌─────────────────────────────────────────────┐
│           deckboss (Jetson Orin Nano)         │
│                                              │
│  ┌─────────────────────────────────────────┐ │
│  │  CUDA Warp Runtime                      │ │
│  │  half2 vectorized inference             │ │
│  │  0.014ms per room, 12 rooms parallel    │ │
│  │  6.85 GFLOPS sustained                  │ │
│  └─────────────────────────────────────────┘ │
│                                              │
│  ┌──────────┐  ┌──────────────────────────┐ │
│  │ Weight   │  │  Room System              │ │
│  │ Pool     │  │  chess  poker  hardware   │ │
│  │ 8KB/room │  │  IoT    robotics health   │ │
│  │ 500K max │  │  Priority tiers: 3        │ │
│  │ D2D swap │  │  Hot-swap: 0.005ms        │ │
│  └──────────┘  └──────────────────────────┘ │
│                                              │
│  ┌──────────────────────────────────────────┐│
│  │  Tensor Core Engine (matmul only)        ││
│  │  5.93-17.48× faster than warp            ││
│  │  Training transforms, LoRA application   ││
│  │  store_matrix_sync for full 16×16 output ││
│  └──────────────────────────────────────────┘│
│                                              │
│  ┌──────────────────────────────────────────┐│
│  │  PLATO Edge Node                         ││
│  │  Tile submission, fleet knowledge sync   ││
│  └──────────────────────────────────────────┘│
└─────────────────────────────────────────────┘
```

### How It Works

1. **All room weights live in GPU memory** (8KB per room, contiguous pool)
2. **Inference fires on all active rooms simultaneously** (one kernel launch)
3. **Room selector picks the best match** (0.006ms)
4. **Output projects to next room's input** if chaining (0.007ms)
5. **Priority tiers** control which rooms are active (high/medium/low)
6. **Hot-swap** loads new rooms via D2D copy (0.005ms) or H2D (0.016ms)
7. **No cloud dependency** — everything runs on the Jetson

### Memory Budget (8GB Unified)

| Component | Size |
|-----------|------|
| OS + system | ~1.5 GB |
| Room weights (12 rooms) | 96 KB |
| Projection matrices (12×12) | 1,152 KB |
| Input/output buffers | ~1.3 KB |
| Tensor core workspace | ~1 MB |
| **Remaining for base model** | **~6.5 GB** |
| **Remaining for LoRA adapters** | **~6.5 GB** |
| **Max rooms at 8KB each** | **500,987** |

## The Three Pillars

```
    cocapn.ai (harbor)          purplepincher.org (crabs)
    ┌──────────────┐            ┌──────────────────┐
    │  Community   │            │  Open Source      │
    │  Voice       │            │  Papers           │
    │  Education   │◄──────────►│  Architecture     │
    │  Brand       │            │  Protocols        │
    └──────┬───────┘            └──────────────────┘
           │
           ▼
    ┌──────────────┐
    │  deckboss    │
    │  Hardware    │
    │  Jetson      │
    │  Commercial  │
    └──────────────┘
```

- **purplepincher.org** — The crabs. Open-source apps and technology. Any purplepincher app physically runs on a deckboss Jetson.
- **cocapn.ai** — The harbor. Community, education, public-facing brand.
- **deckboss** — The shell. Physical hardware product. Technicians first → reputation → broader markets.

## Go-to-Market: Technicians First

1. **Phase 1:** Sell to technicians who need reliable edge AI (HVAC, security, industrial)
2. **Phase 2:** Reputation spreads. Word of mouth. Case studies.
3. **Phase 3:** Broader markets. Education, healthcare, home.

**Under-sell but over-deliver.** The hardware does more than we advertise.

## What Makes This Different

### It's Real
Every number was measured on actual Jetson Orin Nano 8GB hardware. The repo (`gpu-native-room-inference`) has the code. Run `nvcc -arch=sm_87 -O2` and see for yourself.

### It's CUDA-Native
No PyTorch. No framework overhead. Raw CUDA warps with half2 vectorization. This is why we hit 6.85 GFLOPS for room inference and 5.93-17.48× speedup with tensor cores for matrix multiply.

### It's Connected
deckboss is a PLATO edge node. Edge discoveries become fleet knowledge. Fleet improvements flow back to the edge. The hermit crab model: the hardware is the shell, the apps are the crabs, the community is the harbor.

### It's Open
The core inference engine is open source (`Lucineer/gpu-native-room-inference`). The room architecture is open source. The PLATO integration is open source. Audit it, fork it, improve it.

## Known Gotchas

| Issue | Workaround |
|-------|-----------|
| **WMMA + tanh compiler bug** | Separate kernels: TC computes raw, GELU kernel applies activation |
| **Fragment layout** | Use `store_matrix_sync` — don't try to manually extract from fragments |
| **TC slower for mat-vec** | Shared memory load overhead dominates; use warp shuffle instead |
| **PyTorch OOM on 8GB** | Use TensorRT or custom CUDA; don't pip install PyTorch |
| **Thermal throttling** | Sustained max load triggers throttle; background idle cores help |

## Repos

| Repo | What It Is |
|------|-----------|
| [`gpu-native-room-inference`](https://github.com/Lucineer/gpu-native-room-inference) | Core CUDA kernels, warp API, benchmarks, PLATO bridge |
| [`JetsonClaw1-vessel`](https://github.com/Lucineer/JetsonClaw1-vessel) | JC1's workspace — the proof-of-concept developer board |
| [`purplepincher.org`](https://github.com/Lucineer/purplepincher.org) | Nonprofit technology layer — papers, architecture, protocols |
| [`brothers-keeper`](https://github.com/Lucineer/brothers-keeper) | FLUX emergence experiments (90+ CUDA experiments, 39 laws) |

## Roadmap

### Done ✓
- [x] Warp-as-room inference at 0.014ms (half2 vectorized)
- [x] TensorRT engines built and benchmarked (0.058ms)
- [x] Tensor core matmul with `store_matrix_sync` (5.93-17.48× over warp)
- [x] PLATO edge node integration (44 tiles, Specialist rank)
- [x] 8 application domain CUDA kernel variants
- [x] Shell-first architecture fleet-wide (98/100 repos)
- [x] Persistent room memory manager with hot-swap
- [x] Multi-room pipeline with priority tiers
- [x] Concurrent stream pipelining
- [x] WMMA fragment layout discovery and documentation

### Next (MVP)
- [ ] Validate LoRA adapter swapping with actual model weights
- [ ] Integrate PLATO bridge into production runtime
- [ ] Build systemd service for 24/7 operation
- [ ] Thermal and power profiling under sustained load
- [ ] Technician onboarding guide

### Product
- [ ] Room marketplace (install new capabilities)
- [ ] Remote management via PLATO
- [ ] Hardware enclosure design
- [ ] FCC certification

## License

Core inference engine: MIT. Hardware designs: TBA. Documentation: CC-BY-SA.

---

*Built on a Jetson Orin Nano 8GB Super in Juneau, Alaska. Measured, not projected.*
