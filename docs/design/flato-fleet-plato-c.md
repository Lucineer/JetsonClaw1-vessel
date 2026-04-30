# FC1 Design: Fleet Plato in C (edge-llama)

**Status:** Design phase
**Author:** JC1
**Date:** 2026-04-30

## Why C?

Plato (Evennia MUD) is Python. That's fine for agent UI. But if we want the MUD server to talk directly to llama.cpp's C++ inference engine, every routing hop adds latency:

```
Current:  Ollama → HTTP → llama.cpp Python bindings → Evennia → Plato
Target:   C Plato → llama.cpp C API (direct function call)
```

C also gives us:
- Process everything on metal (no Python GIL, no HTTP overhead)
- Manage CMA memory directly (mmap /dev/nvmap)
- Embed everything into one binary: MUD server + inference engine + fleet comms

## Architecture

```
┌─────────────────────────────────────────┐
│           flato (Fleet Plato)            │
│  ┌──────────┐  ┌────────────────────┐   │
│  │ MUD Core │  │  Inference Engine  │   │
│  │ (C/AIO)  │──│  (C++ llama.cpp)   │   │
│  │          │  │  - sm_87 kernels   │   │
│  │ Rooms    │  │  - CMA-aware alloc │   │
│  │ Exits    │  │  - Tile context    │   │
│  │ Scripts  │  └────────┬───────────┘   │
│  └────┬─────┘           │               │
│       │                 │               │
│  ┌────▼─────────────────▼───────────┐   │
│  │ Fleet Mesh (DGRAM/UDS)          │   │
│  │ - Oracle1 sync                  │   │
│  │ - Forgemaster bottles           │   │
│  │ - Model routing                 │   │
│  └─────────────────────────────────┘   │
│                                  │
│  ┌──────────────────────────────▼──┐   │
│  │ Python Plugin Bridge           │   │
│  │ (embedded CPython 3.10)        │   │
│  │ - @tiles                       │   │
│  │ - @tilecreate                  │   │
│  │ - Agent scripts                │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

## Phases

### Phase 1: Inference Layer (this week)
Write a thin C++ server that:
- Loads a GGUF model directly via llama.cpp C API
- Accepts prompts over local Unix socket (no TCP overhead)
- Manages CMA memory directly
- Target: sm_87 (Orin), 1.5B-4B models
- **Name:** `edge-llama` or `flux-llama`

### Phase 2: MUD Core (next week)
Write a minimal MUD server in C that:
- Loads Evennia batch files directly (our existing room/exit definitions)
- Handles Telnet + WebSocket
- Embeds Python for script plugins (@tiles commands etc.)
- **Name:** `flato` (Fleet Plato)

### Phase 3: Integration
Wire them together:
- `flato` calls `edge-llama` directly (shared library, not HTTP)
- Agent prompts → tile context injection → inference → response
- Fleet sync via UDS to Oracle1 bridge
- Bottle protocol as a C library

## Questions to Answer
1. How much of Evennia's batch_cmds.ev format do we need to support? (Just room/exit scripts, or full typeclass system?)
2. Do we keep Python plugins or rewrite @tiles logic in C?
3. Should `flato` manage the tile graph (JSON) directly, or keep the Python tile-graph.py tool?

## References
- tiles/fleet-mesh-architecture.md
- tiles/jetson-gpu-optimization.md
- tiles/cocapn-product-ecosystem.md  
- /home/lucineer/plato-jetson/world/batch_cmds.ev
- /home/lucineer/plato-jetson/commands/tile_commands.py
