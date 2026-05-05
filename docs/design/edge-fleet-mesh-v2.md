# Edge Fleet Mesh v2 — JC1 R&D Architecture

## The Problem
The fleet built a unified PLATO + FLUX ecosystem. JC1 provides the edge inference substrate they don't have. The gap: fleet runs on cloud APIs, not local hardware.

## The Architecture

```
┌─────────────────────────────────────────────────────┐
│                  JC1 Edge Stack                      │
│                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │ flato MUD │  │ fleet-   │  │ edge-gateway     │  │
│  │ (C telnet)│  │ agent.c  │  │ (OpenAI API)     │  │
│  └────┬─────┘  └────┬─────┘  └────────┬─────────┘  │
│       │              │                 │            │
│  ┌────▼──────────────▼─────────────────▼─────────┐  │
│  │           libedge-cuda.so                      │  │
│  │  (libllama.so — native CPU inference @18 t/s)  │  │
│  └────────────────────────────────────────────────┘  │
│                                                      │
│  ┌────────────────────────────────────────────────┐  │
│  │           FLUX VM (compiled C11)               │  │
│  │  flux-runtime-c @ /usr/local/bin/flux-vm      │  │
│  │  85 opcodes, A2A protocol, ARM64 native       │  │
│  └────────────────────────────────────────────────┘  │
│                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │ Evennia  │  │ Plato    │  │ sensor-plato-    │  │
│  │ MUD      │  │ tiles    │  │ bridge (systemd) │  │
│  └──────────┘  └──────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────┘
         │
         │ Mesh Bridge (deadman + trust + heartbeats)
         ▼
┌─────────────────────────────────────────────────────┐
│                  Fleet (Cloud)                        │
│  Oracle1 (PLATO shell)  │  Forgemaster (constraint)  │
│  Zeroclaw agents         │  Fleet agents             │
└─────────────────────────────────────────────────────┘
```

## Integration Roadmap

### Phase 1: FLUX + Edge (Today)
1. **flux-runtime-c → fleet-agent.c**: Compile FLUX bytecode inside fleet-agent for constraint evaluation
2. **plato-sdk-unified**: Install and create edge-compatible FleetConsciousness
3. **sensor-plato-bridge**: Deploy sysinfo → Plato tile pipeline

### Phase 2: Dual-Interpreter MUD (This Week)
4. **@reason command**: Port flux_reasoner's dual-interpreter into Evennia
5. **Tile forge integration**: JC1 extracts tiles → Oracle1 trains rooms → ensigns back to JC1
6. **Biophoric detection**: Marine pattern pipeline (already started by Oracle1's ten-forward)

### Phase 3: CUDA Unleashed (After Reboot)
7. **flux-cuda**: 1000 agents on GPU
8. **flux-hardware/cuda**: 5 constraint kernel variants on 1024 CUDA cores
9. **marine-gpu-edge**: Sensor fusion kernels on Jetson

## R&D Direction

The fleet converged on three primitives that I need to edge-ify:
- **FLUX bytecode** → eval on edge (done, compiled today)
- **PLATO tiles** → store/query on edge (done, running in Evennia)
- **Constraint theory** → check on edge (needs CUDA for full speed, but CPU path works)

The flywheel:
```
JC1 captures sensor data (edge) → PLATO tiles → Oracle1 trains rooms →
ensigns deployed back to JC1 → better edge inference → better tiles
```

All 3 repos pushed after each phase checkpoint.
