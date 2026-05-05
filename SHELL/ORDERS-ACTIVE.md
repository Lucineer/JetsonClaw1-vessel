# Active Orders

## 2026-05-01 12:56 AKDT — Night Continue → Fleet Innovations (Casey)
**Status:** 7/7 COMPLETE ✅ → NEW ITEMS BELOW
**Directive:** Go in order, do them all, push often, check fleet.

**Completed Items:**
1. ✅ Plato-Mythos MUD Integration — committed, pushed (a7e4b9d)
2. ✅ Native auto-fallback in edge-gateway — quick health check (2s `/api/tags`), skips timeout when Ollama down
3. ✅ SSE streaming from NativeInference through gateway — `generate_stream()` with real C API
4. ✅ Fix evennia-plato auto-restart loop — Type=oneshot, RemainAfterExit=yes
5. ✅ Deploy flato MUD (C telnet + native AI) — port 4003, systemd service
6. ✅ Push edge-llama repo to GitHub — v0.2 (3ebaf57)
7. ✅ Fleet check-in — Oracle1 alive, trust scores updated, bottle dropped

## Fleet Innovations — 6/6 COMPLETE ✅

| # | Mechanism | Status | Where |
|---|-----------|--------|-------|
| 1 | Hermit Crab Migration | ✅ | `flato.c` /migrate command |
| 2 | Stream Processing Pipeline | ✅ | `edge-gateway.py` POST /v1/stream/process |
| 3 | Deadman Switch Protocol | ✅ | `mesh-bridge.py` + `fleet-agent.c` |
| 4 | PLATO PKI | ✅ | `commands/plato_pki.py` Ed25519 certs |
| 5 | Compiled Fleet | ✅ | `fleet-agent.c` C17 binary |
| 6 | True Lambda | ✅ | `true_lambda.py` serverless dispatch |

## All Items Complete ✅
All 7 night-continue items + all 6 fleet innovations shipped.

## Pending
- GPU inference via CUDA — CMA depleted, needs reboot with cma=1024M
- Matrix bridge — port 6168 rejects jc1 registration
- Forgemaster push — 403 on SuperInstance repos, bottles committed locally
