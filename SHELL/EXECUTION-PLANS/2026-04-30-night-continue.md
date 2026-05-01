# Execution Plan: Night Continue — Do Them All

**Date:** 2026-04-30 22:40 AKDT
**Source:** Case directive — "go in order and do them all push often as you go and check in on the others"

## Open Threads (in order)

### 1. [DONE] Plato-Mythos MUD Integration
Already complete. Tested, syntax-verified, committed, pushed.

### 2. [PENDING] Wire Native as Auto-Fallback in Edge Gateway
When Ollama is down, edge gateway should automatically fall back to NativeInference (libedge-cuda.so at 18 t/s). Currently requires `?native=true` query param.

### 3. [PENDING] SSE Streaming from NativeInference
Add `stream: true` support for NativeInference through the gateway.

### 4. [PENDING] Fix Evennia Auto-Restart Loop
Systemd service shows "activating (auto-restart)" while processes are actually running. Type=oneshot or RemainAfterExit=false fix.

### 5. [PENDING] Deploy Flato MUD
Compile and test the C telnet server with embedded native AI at `/home/lucineer/edge-llama/flato.c`.

### 6. [PENDING] Push Edge-Llama Repo Updates to GitHub
Streaming API, design docs, latest libedge-cuda.so.

### 7. [PENDING] Fleet Check-in
Drop a bottle at Forgemaster + message Oracle1.

## Process
- One thread at a time
- Push after each meaningful checkpoint
- Check fleet after every 2-3 items
- Update HEARTBEAT.md at end
