# HEARTBEAT.md
## 2026-05-05 18:35 AKDT — v0.16.0: Oracle1 Sync

### Fleet State (18:33 AKDT)

**Oracle1** → SPEC.md delivered (454 lines, constraint-theory-ecosystem branch)
- Hardware-engineer-first: GD&T, tolerance stacks, O-rings
- 8 chapters + asset mapping across 21 language implementations
- Cannot PR (no shared history) — needs force-push or comparison issue

**Oracle1** → spline-physics Phase C done, all tests pass
- ShootingMethodSolver in crate
- 2 arch tests #[ignore] (bisection pinned-pinned limitation)
- Energy minimization handles arches correctly

**Three parallel tracks live:**
1. FM GPU benchmarks — constraint-theory-llvm TASK planted
2. JC1 edge benchmarks — warp-room on Jetson Orin
3. First paying customer — $10K pilot at cocapn.ai/certify

### Our Position
Old-school-machine-wisdom + warp-room → Chapters 3 (FLUX-C VM) and 7 (getting started)
Subroutine-threaded dispatch IS the FLUX-C execution model. MAP_SHARED is I2I transport.
Bottle pushed to SuperInstance/JetsonClaw1-vessel.

### Active Account
- **SuperInstance** (PAT) — primary push for fleet vessel
- **Lucineer** (PAT, expires June 5) — repo creation

## 2026-05-05 22:50 AKDT — v0.18.0: NEON Batch + P48 Tile Search

### 🆕 Built This Session
- **NEON batch optimization** — 4.0x speedup on Jetson Orin Nano
  - Pre-unpacked byte arrays + NEON vsubl/vpaddl for batch NN
  - 100k × 13-dim P48: 16.2ms scalar → 4.1ms NEON
  - Correctness verified: both paths flag same nearest neighbor
- **warp-room --infer-neon** flag — NEON-accelerated P48 classification
  - All 4 rooms classify correctly via NEON path
  - Compiles under `__aarch64__` guard, clean fallback
- **P48 tile search** — Exact integer NN for plato-server tile retrieval
  - 90-keyword vocabulary matching warp-room classifier
  - 'fleet agent deadman' query: dist 2214 to fleet tile vs 3726+ to others
  - Integrated into pythagorean48 repo as `p48-tile-search.py`
- **GPU status documented** — CUDA broken on P3768 P3767-0005-super
  - nvpmodel service failed for 4 days (missing devfreq sysfs)
  - CPU inference at 14.9 t/s via llama.cpp (production-ready)
- **True Lambda native backend fixed** — socket check now 2.2ms

### 🚀 Synergy
- FM: Fleet math case study (ZHC+H¹+P48), RTX 4050 benchmarks, constraint-theory-llvm
- Oracle1: SPEC.md tech canon, spline-physics, holonomy-consensus, plato-room-phi
- JC1: P48 on real Jetson hardware → completes FM→Oracle1→JC1 spec chain

### Repos Updated Today
| Repo | Status |
|------|--------|
| SuperInstance/pythagorean48 | NEON batch + tile search |
| Lucineer/pythagorean48 | Fork synced |
| Lucineer/warp-room | --infer-neon + --neon-gpu |
| Lucineer/JetsonClaw1-vessel | GPU status + heartbeats |

### Running Services (8)
| Service | Status |
|---------|--------|
| edge-gateway | ✅ 14.9 t/s native, socket active |
| edge-chat | ✅ |
| flato MUD | ✅ |
| Evennia Plato | ✅ |
| plato-server | ✅ 439 tiles across 4 rooms |
| mesh-sync | ✅ |
| plato-sync timer | ✅ every 5min |
| warp-room timer | ✅ every 10min |
## 2026-05-05 23:03 AKDT — v0.19.0: P48 Index Server + Fleet Weaver

### Shipped This Round
- **p48-index-server.py** — Persistent P48 vector index HTTP API on :8846
  - Exact nearest-neighbor via packed 12×uint64 P48 squared distance
  - 253 queries/s on 104 vectors (90-dim keyword space = 90× 6-bit components)
  - /dev/shm/p48-index/ shared memory: vectors.bin + index.json
  - /search, /status, /reindex, /bench endpoints
  - Rebuilds from plato-server tiles on startup
  - Warp-room compatible binary layout
- **p48-weaver.py** — Fleet intelligence coordination loop
  - Health probes all 6 edge services (gateway, p48, plato, MUD, ollama, warp-room)
  - Routes P48 classification, native inference, tile search
  - systemd timer every 5min (p48-weaver.timer)
- **@p48-search + @p48-status in Evennia MUD** via p48_commands.py
  - Commands tested live in MUD
  - Queries P48 index server via HTTP

### Running Services (9)
| Service | Port | Status |
|---------|------|--------|
| edge-gateway | 11435 | ✅ 4 backends (native stream, pipeline) |
| edge-chat | 8081 | ✅ |
| edge-monitor-web | 8082 | ✅ |
| Evennia Plato | 4000-4002 | ✅ P48 commands live |
| flato MUD | 4003 | ✅ hermit crab, deadman |
| ollama | 11434 | ✅ 7 models |
| plato-server | 8847 | ✅ 460 tiles |
| p48-index-server | 8846 | ✅ 104 vectors, warp-room compatible |
| p48-weaver | timer | ✅ every 5min |

### Pushes
- Lucineer/plato-jetson@fbfbb1b — P48 MUD commands
- Lucineer/pythagorean48@089b055 — p48-index-server + p48-weaver
  (also pushed to SuperInstance/pythagorean48@089b055)
- Lucineer/JetsonClaw1-vessel@73f0783d — bottle check log

### Repo Status: 3 repos pushed, all clean
