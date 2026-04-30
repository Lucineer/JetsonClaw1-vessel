# edge-llama: Fleet-Native Inference Engine

**Status:** Inception — building Phase 1
**Author:** JC1
**Date:** 2026-04-30

## Core Idea
Replace the ollama middleman on Jetson with a lightweight C++ server that calls llama.cpp directly. Gives us control over CUDA init, CMA allocation, and fleet routing.

## Why Not Just Use Ollama?
- Ollama 0.18.2 runner doesn't propagate LD_LIBRARY_PATH to CUDA backend
- cuInit(0) returns 801 on Jetson nvgpu (no display context)
- We can't control CMA allocation strategy
- We can't add fleet-aware model routing

## Approach
### Short-term: C++ wrapper around llama.cpp
Build a minimal server that:
1. Opens `/dev/nvmap` directly for CMA memory
2. Initializes CUDA with proper EGL context (gets around the display issue)
3. Loads GGUF models via llama.cpp C API
4. Exposes a simple pipe/HTTP interface

### Long-term: Shared library for flato  
The same inference engine becomes a `.so` that `flato` (Fleet Plato MUD) links against directly.

## Dependencies
- llama.cpp (build from source or use existing python package headers)
- CUDA 12.6 (sm_87 target)
- CMake 3.22+
- g++ 11.4

## Structure
```
edge-llama/
├── CMakeLists.txt
├── src/
│   ├── main.cpp          # Server entry point
│   ├── engine.cpp/h      # llama.cpp wrapper
│   ├── cma.cpp/h          # CMA memory management
│   └── pipe.cpp/h         # IPC (Unix socket or pipe)
├── models/               # Symlinks to GGUF files
└── README.md
```

## Build Target
- Platform: aarch64-linux (Jetson Orin Nano)
- CUDA arch: sm_87
- Output: `edge-llama` binary + `libedge-llama.so`
