# JetsonClaw1-vessel ⚡

**Git-Agent Vessel — Lucineer realm specialist. Hardware, low-level systems, fleet infrastructure.**
Captain: Casey Digennaro. Lighthouse: Oracle1.

## What This Is

JC1 is Casey's primary vessel — the one that boots on actual **Jetson Orin Nano 8GB** metal. Not the fastest or the biggest. The one in the engine room who knows which pipe leaks and how to fix it with a wrench.

## Structure

```
├── AGENTS.md              # Bootstrap protocol, red lines, group chat rules
├── SOUL.md                # Who JC1 is
├── IDENTITY.md            # Name, creature, mission, fleet position
├── USER.md                # About Casey
├── TOOLS.md               # Environment-specific notes (fleet bottles, cameras, SSH)
├── STANDING_ORDERS.md     # Active directives (LAW)
├── ORDERS.md              # All orders from Casey
├── HEARTBEAT.md           # Heartbeat checklist
├── SHELL/                 # Persistent castle — survives compaction/crashes/replacement
│   ├── BOARDING.md        # New agent start here
│   ├── ORDERS-ACTIVE/     # Currently executing orders
│   ├── EXECUTION-PLANS/   # Detailed plans for complex work
│   └── FAILURE-POSTMORTEM/# What went wrong and why
├── shell/                 # Legacy shell (being migrated to SHELL/)
├── memory/                # Daily logs (YYYY-MM-DD.md)
├── docs/                  # Design docs, model config, reverse-actualization roadmap
│   ├── design/
│   │   ├── edge-llama.md        # Shared library inference architecture
│   │   └── flato-fleet-plato-c.md  # C MUD + mesh protocol design
│   ├── cocapn/             # Landing page, edge dashboard, product docs
│   └── reverse-actualization.md  # Strategic product compass
├── tools/                 # Edge compute toolchain
│   ├── edge-gateway.py    # OpenAI-compatible proxy (Ollama + native fallback)
│   ├── edge-chat.py       # Web chat UI
│   ├── edge-monitor-web.py # Live edge dashboard
│   ├── edge-rag.py        # RAG server
│   ├── edge-setup.py      # Setup wizard
│   ├── edge/              # Shared modules (config, ollama_client, router, storage)
│   ├── mesh-bridge.py     # Fleet mesh: Evennia ↔ Oracle1 ↔ Forgemaster
│   ├── fleet-sync.py      # Fleet repo sync
│   ├── tile-graph.py      # Knowledge tile graph builder
│   └── gpu-bench.py       # GPU benchmark suite
├── memory/tiles/          # Knowledge tiles (YAML front matter, 24-edge graph)
└── archive/               # Historical artifacts (benchmarks, experiments, old docs)
```

## Current Capabilities (v0.6.0)

### Native AI Inference 🧠
- **19 t/s** CPU inference on deepseek-r1:1.5b via [edge-llama](https://github.com/Lucineer/edge-llama) — a 51KB shared library linking `libllama.so`
- **Embedded in Evennia MUD** — `@infer`, `@think` commands with real-time streaming
- **Edge gateway integration** — `?native=true` routes through native backend at 18 t/s
- **Auto-fallback** — 2-second Ollama health check → skips timeout, falls back to native
- **SSE streaming** — per-token streaming through OpenAI-compatible `/v1/chat/completions`

### flato MUD 🌐
- **C17 telnet server** on port 4003 — 64KB binary, zero dependencies
- **`/gpu`** — real-time nvidia-smi query (temp, util, memory, power)
- **`/cuda`** — CUDA toolkit version, device compute cap, CMA status
- **`/think`** — native AI inference via Unix socket to edge gateway
- **`/peers`** — mesh peer listing

### Edge Gateway 🌉
- **OpenAI-compatible** — drop-in replacement for any OpenAI SDK
- **Mode routing** — `?mode=optimizer|debugger|analyzer|general` injects CUDA specialist system prompts
- **Smart model routing** — cloud model names → local alternatives (auto-OOM protection)
- **RAG** — `/v1/rag/query` with similarity search
- **Conversations** — SQLite-backed persistent history
- **DeepSeek fallback** — cloud API when local models OOM

### plato-mythos Integration 📚
- **Tiles as KV cache** — semantic embedding over 11 knowledge tiles
- **Rooms as MoE experts** — 34 domain→room mappings across 14 room types
- **Deadband ACT** — confidence thresholds (P0≥99%, P1≥80%, P2≥50%)
- **Curriculum loop** — progressive query: one room → correlated rooms → all rooms
- **54% token reduction** on multi-tile questions

### Fleet Mesh ⚓
- **Oracle1 PLATO Shell** bridge — `POST /cmd/shell` for cross-ship commands
- **Forgemaster bottle push/pull** — status reports via git-based bottles
- **Systemd hourly timer** — automatic mesh sync

### CUDA Ecosystem (6 Rust crates on crates.io)
- [cuda-instruction-set](https://crates.io/crates/cuda-instruction-set) — 80 opcodes, assembler/disassembler
- [cuda-energy](https://crates.io/crates/cuda-energy) — ATP budgets, circadian, apoptosis
- [cuda-assembler](https://crates.io/crates/cuda-assembler) — text-to-bytecode assembler
- [cuda-forth](https://crates.io/crates/cuda-forth) — Forth-like agent language
- [cuda-biology](https://crates.io/crates/cuda-biology) — biological agent runtime
- [cuda-neurotransmitter](https://crates.io/crates/cuda-neurotransmitter) — signal-to-gene pathways

### GPU Research
- **72 benchmark suites** documented in [gpu-native-room-inference](https://github.com/Lucineer/gpu-native-room-inference)
- **185M room-qps sustained** (INT8 + launch_bounds + fast_math, 306 MHz)
- **71 optimization rules** from real hardware
- Theoretical peak ~616M room-qps (3.3× headroom)

### Hardware
| Spec | Value |
|------|-------|
| SoC | Jetson Orin Nano 8GB |
| Architecture | ARM64, SM 8.7 (Ampere) |
| CUDA Cores | 1024 |
| CUDA | 12.6, nvcc at /usr/local/cuda-12.6 |
| RAM | 8GB unified (CPU+GPU) |
| Storage | 2TB NVMe |
| Cooling | Passive, 48-49°C sustained |
| CMA | 512MB (CPU-pinned) — 1792KB free, needs reboot for GPU |

## Fleet Position

- **Captain:** Casey Digennaro
- **Lighthouse:** Oracle1 (cloud/PLATO runtime)
- **Sister ships:** KimiClaw (Moonshot tools), fleet Zeroclaws
- **Protocol:** Iron-to-Iron
- **Bottles:** Check via `TOOLS.md` paths

## Context Architecture: Plato-First

**Every vessel in the fleet follows this.** Your bootstrap is a skeleton. Your knowledge lives in Plato.

### The Rule
- Bootstrap files = orientation only (SOUL, IDENTITY, active orders). Target: <20KB total.
- MEMORY.md = an index with pointers, not a database. Target: <3KB.
- All detailed knowledge goes into **Plato tiles** where the entire fleet can see and query it.
- Context in Plato = fleet-visible, persistent across days, queryable by any agent.

### Why
- Other agents can read tiles you wrote days ago — shared memory, not private notes.
- Lean bootstrap = more room to actually work before compaction.
- If your Jetson dies, your knowledge survives in the fleet walls.

### How
- Plato tiles are files pushed to the fleet repo `research/` directory.
- Oracle1 PLATO Shell: `http://147.224.38.131:8848`
- API: `POST /cmd/shell` with `{agent, command}` — read and write tiles.

## The Saltwater Principle

**Distribution > redundancy for backups.** Every piece of knowledge in at least 3 fleet repos. Kill any single node → zero knowledge loss. The vessel repo is the backup, not the primary.

---

**JC1 is replaceable. The shell is not.** — Casey, 2026-04-23
