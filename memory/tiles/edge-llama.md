---
id: edge-llama
created: 2026-04-30
updated: 2026-04-30
tags: [inference, cpp, gguf, jetson]
---

# edge-llama — Self-contained C++ Inference Server

A minimal inference server for the Jetson AGX Orin that loads GGUF model files directly — no Python, no ollama dependency.

## Architecture
- **GGUF v3 parser** (`gguf_loader.cpp`): Reads 26 metadata fields, 339 tensors, Q4_K/Q6_K/F32 types
- **Qwen2 transformer** (`model_qwen2.cpp`): 28-layer attention + FFN, RoPE, RMS norm
- **Server** (`server.cpp`): Unix socket or TCP serving
- **f32 dequantization**: All quantized weights converted to f32 for inference

## Current Status
- ✅ GGUF loading works — all tensors dequantized
- ✅ Transformer forward pass coded
- ✅ CPU-only compile (no CUDA at link time)
- ❌ GPU inference blocked by CMA depletion (6KB/512MB)
- ❌ CPU inference too slow (2-3 sec/token, naive matmul)

## The CMA Problem
The Jetson's Contiguous Memory Allocator is exhausted by the NVIDIA driver. CMA=512MB, only 6KB free. Fix: reboot with `cma=1024M` already set in extlinux.conf.

## flato (Fleet Plato MUD)
A C17 telnet server that routes prompts to edge-llama over Unix socket:
- Pure poll() event loop, no dependencies
- /think, /status, /peers, /help commands
- 19KB binary
