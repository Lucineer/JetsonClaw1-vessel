# HEARTBEAT.md
## 2026-04-30 14:30 AKDT — v0.6.1: Native Inference Live in Edge Gateway

### ✅ Shipped
- **NativeInference class** in edge-gateway fully works
  - Pre-loads libggml-cuda.so with RTLD_GLOBAL to fix `quantize_row_nvfp4_ref` weak symbol
  - Loads libedge-cuda.so with RTLD_LOCAL for isolation
  - Uses real ctypes API: `edge_load -> c_void_p`, `edge_generate -> char*`
  - Lazy-loaded on first use via `?native=true` query parameter
  - Backend correctly reports `llama.cpp (CPU)` at 18 t/s
  - Thread-safe via threading.Lock for concurrent HTTP requests
- **All fixes pushed**: workspace/edge-gateway.py (1072e42)

### Architecture
```
curl "http://localhost:11435/v1/chat/completions?native=true"
  → GatewayHandler (ThreadingMixIn)
  → NativeInference.load() (lazy, RTLD_GLOBAL preload)
  → libedge-cuda.so → libllama.so → libggml-cuda.so (CPU)
  → 18 t/s, no Ollama, pure native
```

### What's Running
- Edge gateway: port 11435 ✅ native works
- Edge chat: port 8081
- Edge monitor: port 8082
- Evennia Plato: port 4000 (telnet) ✅ has @infer native AI
- Ollama: running (deepseek-r1:1.5b, may be slow)
- Services: 5 persistent user services

### Next
1. Wire native as auto-fallback when Ollama down
2. Add SSE streaming from NativeInference through gateway
3. Fix evennia-plato systemd auto-restart loop
4. Deploy flato MUD (C telnet server + native AI)
5. Push edge-llama repo updates to GitHub
