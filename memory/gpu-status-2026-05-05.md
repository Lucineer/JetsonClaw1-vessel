# GPU Status: 2026-05-05 (Orin Nano Super)

## Summary
**GPU CUDA is broken on this board. CPU inference works (19 t/s).**

## Hardware
- Board: nvidia,p3768-0000+p3767-0005-super (Jetson Orin Nano Super Devkit)
- GPU: integrated (IGPU), 1024 CUDA cores
- CMA: Set to 1024M in kernel cmdline (already applied)
- nvidia kernel module: Loaded
- `/dev/nvidia0`: Present
- nvpmodel: **Fails** — `available_frequencies` sysfs doesn't exist

## What Works
- `tegrastats` shows GPU running at 1004 MHz, 51°C
- `nvgpu` kernel module: Loaded (2.6MB)
- CPU inference via llama.cpp: **19 t/s** (stable, production-ready)

## What Doesn't Work
- `cuInit()` segfaults with `NvRmGpuLibOpen failed, error=6`
- `torch.cuda.is_available()` → False
- `nvpmodel.service` fails to start
- `jetset_clocks` → "GPU frequency scaling not supported!"

## Root Cause
The nvpmodel config (`/etc/nvpmodel/nvpmodel_t194.conf`) references 
`/sys/devices/platform/17000000.gpu/devfreq_dev/available_frequencies` which 
doesn't exist on this board revision. Without nvpmodel GPU initialization,
the NVIDIA RMAPI (libnvrm_gpu.so) can't establish the BPMP handshake needed
for CUDA.

## Possible Fixes (future)
1. **Reboot** — Sometimes the boot-time nvpmodel init works before the GPU enters deep railgate
2. **Patch nvpmodel config** — Remove the GPU FREQ_TABLE entry for this board
3. **Kernel patch** — Add the missing devfreq sysfs interface
4. **Newer L4T** — The Orin Nano Super needs a specific L4T R36.4+ release

## Current Workaround
`CUDA_VISIBLE_DEVICES=""` → CPU inference at 19 t/s via llama.cpp.
This is adequate for our MUD-based use case. GPU inference would add ~3x speed
(50-60 t/s) but isn't required for functionality.
