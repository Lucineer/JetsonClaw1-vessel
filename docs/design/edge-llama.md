# edge-llama: Fleet-Native Inference Engine

**Status:** v0.6.0 — CPU inference at 19 t/s (deepseek-r1:1.5b)
**Author:** JC1
**Date:** 2026-04-30

## Core Idea (Mostly Solved)

Replace the ollama middleman with a 51KB shared library (`libedge-cuda.so`) that links llama.cpp directly. Loaded into Python processes via ctypes (`edge_native.py`) or into Evennia MUD via `EdgePlatoModel` singleton.

No HTTP. No subprocess. Just `dlopen()` → function call → text.

## Why Not Just Use Ollama?

| Factor | Ollama | edge-llama |
|--------|--------|------------|
| API | HTTP subprocess | In-process shared library |
| Overhead | ~50ms serialization | ~2μs function call |
| Embedding | Separate daemon | Link into any process |
| Fleet routing | Ollama config only | Custom per-route prompts |
| CMA control | No | Direct nvmap access planned |

## Architecture

```
Evennia MUD (Python)
    │ ctypes
    ▼
libedge-cuda.so (51KB)
    │ linking
    ▼
libllama.so (llama.cpp C API)
    │
    ▼
model.gguf (deepseek-r1:1.5b, ~1GB)
```

## Current State

- **✅ CPU inference**: 19 t/s via llama.cpp C API (CPU backend, `CUDA_VISIBLE_DEVICES=""`)
- **✅ Python wrapper**: `EdgePlatoModel` singleton, thread-safe via `threading.Lock`
- **✅ Streaming**: Per-token callback (`edge_generate_stream`) → Twisted reactor → telnet
- **✅ Edge gateway integration**: `?native=true` routes through `libedge-cuda.so`
- **✅ Auto-fallback**: 2s Ollama health check → native when down
- **❌ GPU inference**: CMA pool depleted (1792KB/512MB). Fix: reboot with `cma=1024M`.

## The Remaining Challenge: CMA

NVIDIA's Jetson driver allocates CMA during first CUDA context creation and **never frees it**. After running ollama once, `cat /proc/meminfo` shows `CMA: 1792KB/524288KB`. Fix confirmed in `/boot/extlinux/extlinux.conf` — `cma=1024M` — needs a reboot.

After reboot: ~1024MB CMA → CUDA works → GPU inference at ~3-5× CPU speed.
