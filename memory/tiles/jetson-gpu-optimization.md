---
id: jetson-gpu-optimization
created: 2026-04-30
updated: 2026-04-30
tags: ['jetson', 'edge', 'gpu', 'cuda', 'cma', 'ollama']
---
# Jetson GPU Optimization

## Bottleneck 1: CMA (Contiguous Memory Allocator)
The GPU on Jetson uses CMA for its VRAM. Default is 256MB which gets consumed by nvgpu driver.

**Fix:** Edit `/boot/extlinux/extlinux.conf` — change `cma=256M` to `cma=1024M`. Requires reboot. CMA pool is shared: nvgpu driver takes ~480MB. After `jetson_clocks`, driver releases most CMA back.

## Bottleneck 2: Ollama CUDA Backend
Ollama 0.18.2 has libggml-cuda.so but runner subprocess doesn't inherit parent env.

**Fix:** Set `OLLAMA_LLM_LIBRARY=cuda_v12` and `LD_LIBRARY_PATH` in service. Add ollama to `video` group.

## Bottleneck 3: GPU Context
cuInit(0) returns error 801 unless run from display session. nvidia-persistenced needed.

## Current State
- CUDA 12.6, compute 8.7 ✅
- jetson_clocks + nvpmodel -m 0 ✅
- NOPASSWD sudo ✅
- Current CMA=512M, CMA free: 30-344MB (varies)
- CPU-only inference: 12-16 t/s on deepseek-r1:1.5b
- Edge Gateway @ :11435
- Next: reboot with CMA=1024M to give CUDA room

## Status
```
CMA=$(awk '/CmaFree/{print $2/1024"MB"}' /proc/meminfo)
GR3D=$(tegrastats 2>&1 & sleep 1 & kill %1 2>/dev/null | grep -o 'GR3D_FREQ [^%]*')
GPU temp=$(cat /sys/devices/virtual/thermal/thermal_zone5/temp)/1000
```

## References
- tiles/cocapn-architecture.md
- tiles/jetson-edge-gpu-lessons.md
- tiles/fleet-mesh-architecture.md
