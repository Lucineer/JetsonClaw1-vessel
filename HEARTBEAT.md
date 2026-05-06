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
