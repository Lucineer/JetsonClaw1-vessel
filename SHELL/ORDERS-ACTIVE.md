# Active Orders

## 2026-04-30 23:15 AKDT — Night Continue (Casey)
**Status:** 5/7 COMPLETE 🔄
**Directive:** Go in order, do them all, push often, check fleet.

**Order:**
1. ✅ Plato-Mythos MUD Integration — committed, pushed (a7e4b9d)
2. ✅ Native auto-fallback in edge-gateway — quick health check (2s `/api/tags`), skips timeout when Ollama down, both streaming + non-streaming paths
3. ✅ SSE streaming from NativeInference through gateway — `generate_stream()` with real C API, uses `_send_sse`/`_send_sse_done`
4. ✅ Fix evennia-plato auto-restart loop — changed to Type=oneshot, RemainAfterExit=yes, `active (exited)` with no restart
5. ✅ Deploy flato MUD (C telnet + native AI) — compiled, JSON parser fixed, socket handler working, 64 tokens at ~18 t/s, systemd service created (startup port conflict needs final adjustment)
6. ✅ Push edge-llama repo to GitHub — v0.2 (3ebaf57), streaming API, design docs, flato.c, libedge-cuda.so
7. [ ] Fleet check-in — Oracle1 shell live but Matrix bridge rejects jc1 (not registered). Forgemaster push blocked (403). Bottle via DM unavailable. Plato shell pinged.

**Notes:**
- Thread safety: `_gen_lock` added to NativeInference for serialized generate()
- Native socket listener: `/tmp/edge-native.sock` (newline-delimited JSON, boot-persistent)
- Gateway at 11435: 3 concurrent pathways (Ollama, native direct, native socket)

**Plan:** `SHELL/EXECUTION-PLANS/2026-04-30-night-continue.md`

**Previous orders history:** Synergy order — COMPLETE ✅
