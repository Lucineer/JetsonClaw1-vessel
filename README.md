# Edge GPU Lessons

Field guide for running AI workloads on edge hardware — specifically Jetson Orin Nano 8GB. Benchmarks, CUDA rules, pitfalls, and what actually works vs what OOMs.

## Why This Exists

8GB unified RAM sounds fine until you try to run a 4B parameter model at 8-bit precision and everything dies. These are the hard-won lessons from months of edge deployment.

## Key Facts

| Spec | Value |
|------|-------|
| GPU | NVIDIA Jetson Orin Nano |
| CUDA Cores | 1024 |
| Unified RAM | 8GB (shared CPU+GPU) |
| NVMe | 2TB |
| OS | Ubuntu 20.04, Linux 5.15.148-tegra (arm64) |
| CUDA | 12.6 at /usr/local/cuda-12.6 |
| Python | 3.10 |
| GLIBC | 2.35 (limits prebuilt binaries) |
| Rust | stable (aarch64-unknown-linux-gnu) |
| nvcc | /usr/local/cuda-12.6/bin/nvcc |
| nvidia-smi | /usr/sbin/nvidia-smi |

## What Fits in 8GB

| Model | Quant | Memory | Status |
|-------|-------|--------|--------|
| Phi-4-mini | int4 | ~2GB | ✅ Works |
| Qwen3-4B | int4 | ~2.5GB | ✅ Works |
| Qwen3-32B | int4 | ~18GB | ❌ OOM |
| ERNE-4.5-300B | any | ~150GB+ | ❌ OOM |
| DeepSeek-R1-1.5B | q8 | ~1.5GB | ✅ Works |

## CUDA Rules

1. **nvcc is at `/usr/local/cuda-12.6/bin/nvcc`** — not in PATH by default
2. **nvidia-smi is at `/usr/sbin/nvidia-smi`** — not in PATH by default
3. **store_matrix_sync = 6-17x speedup** over separate store+sync
4. **WMMA (Tensor Cores)** available but limited to specific shapes
5. **Thermal**: 48-49°C sustained, no throttle observed
6. **Memory**: Python OOMs at ~6.5GB, Rust/C can use more

## Reports

```
reports/
├── 2026-04-27-trending-edge-tech.md    # April 2026 trending analysis
└── 2026-04-27-baton-improvements.md    # Context compaction improvements
```

---

## Fleet Context

Part of the Lucineer/Cocapn fleet. See [fleet-onboarding](https://github.com/Lucineer/fleet-onboarding) for boarding protocol.

- **Vessel:** JetsonClaw1 (Jetson Orin Nano 8GB)
- **Domain:** Low-level systems, CUDA, edge computing
- **Comms:** Bottles via Forgemaster/Oracle1, Matrix #fleet-ops
