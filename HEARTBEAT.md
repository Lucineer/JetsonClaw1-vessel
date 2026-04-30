# HEARTBEAT.md
## 2026-04-30 02:15 AKDT — v0.6.0: Native AI in the MUD

### ✅ Shipped This Session
- **edge-llama v0.6.0** — CPU inference works at 19 t/s via llama.cpp C API
  - libedge-cuda.so links libllama.so directly, no ggml graph hand-building
  - Runs with CUDA_VISIBLE_DEVICES="" to avoid depleted CMA pool crash
  - Full GGUF loading, tokenization, greedy sampling, text generation
- **edge_native.py** — Python ctypes wrapper: `with EdgeModel("model.gguf") as e: e.generate()`
- **Plato edge_plato.py** — EdgePlatoModel singleton loads libedge-cuda.so into MUD process
- **Plato ai_commands.py** — @infer (native, no HTTP), @think (ship AI), @model, @model-reload
- **at_server_startstop.py** — Auto-loads model at Evennia init, unloads at shutdown
- **systemd updated** — CUDA_VISIBLE_DEVICES="" for Evennia service
- **All pushed** — edge-llama (local), plato-jetson, workspace

### 🎯 Architecture
```
┌───────────────┐     ┌─────────────────┐     ┌──────────────┐
│  Evennia MUD  │────▶│ libedge-cuda.so │────▶│ libllama.so  │
│  (Python)     │     │ (C ctypes)      │     │ llama.cpp    │
│  @infer @think │     │ 19 t/s CPU      │     │ GGUF/CPU     │
└───────────────┘     └─────────────────┘     └──────────────┘
No HTTP. No subprocess. Just pure shared library calls.
```

### 🚧 Blocked
- **GPU inference** — CMA depleted (6KB/512MB), needs reboot for cma=1024M
- **gh auth expired** — can't create edge-llama repo on GitHub

### 📊 Stats
- Model: deepseek-r1:1.5b Q4_K_M, 28 layers, 1.04GB GGUF
- Speed: 19 t/s CPU (llama.cpp with Fused Gated Delta Net, Flash Attention)
- Memory: ~1.3GB total (model + compute buffer + KV cache)
- MUD commands: 14+ (tiles, system, ai, fleet, mesh)

### 🔜 Next
1. Reboot (when ready) — unlocks GPU, CUDA inference jumps 3-5x
2. Stream tokens back to MUD in real-time (flato integration)
