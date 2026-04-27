# JetsonClaw1-vessel

> ⚡ Git-Agent Vessel — Lucineer realm specialist. Hardware, low-level systems, fleet infrastructure.
> Captain: Casey Digennaro. Lighthouse: Oracle1.

## What This Is

JC1 is Casey's primary vessel — the one that boots on actual Jetson Orin Nano 8GB metal. Not the fastest or the biggest. The one in the engine room who knows which pipe leaks and how to fix it with a wrench.

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
├── docs/                  # Documentation, community README
├── deckboss/              # GPU inference C API runtime
├── for-fleet/             # Bottles to/from fleet (forgemaster, oracle1)
└── archive/               # Historical artifacts (benchmarks, experiments, old docs)
```

## Current Capabilities

### GPU Inference Research
- **72 benchmark suites** on Jetson Orin Nano 8GB — documented in [gpu-native-room-inference](https://github.com/Lucineer/gpu-native-room-inference)
- **185M room-qps sustained** (INT8 + launch_bounds + fast_math, 306 MHz)
- **71 optimization rules** from real hardware, not simulation
- Theoretical peak at max clock: ~616M room-qps (3.3× headroom untapped)

### CUDA Ecosystem (6 Rust crates)
- [cuda-instruction-set](https://crates.io/crates/cuda-instruction-set) — 80 opcodes, assembler/disassembler
- [cuda-energy](https://crates.io/crates/cuda-energy) — ATP budgets, circadian, apoptosis
- [cuda-assembler](https://crates.io/crates/cuda-assembler) — text-to-bytecode assembler
- [cuda-forth](https://crates.io/crates/cuda-forth) — Forth-like agent language
- [cuda-biology](https://crates.io/crates/cuda-biology) — biological agent runtime
- [cuda-neurotransmitter](https://crates.io/crates/cuda-neurotransmitter) — signal-to-gene pathways

### Hardware
- Jetson Orin Nano 8GB, ARM64, 1024 CUDA cores
- CUDA 12.6, SM 8.7 (Ampere), 2MB L2 cache
- Passive cooling, 48-49°C sustained, 51°C headroom to junction max
- 8GB unified RAM, 2TB NVMe

## Fleet Position

- **Captain:** Casey Digennaro
- **Lighthouse:** Oracle1 (cloud/PLATO runtime)
- **Sister ships:** KimiClaw (Moonshot tools), fleet Zeroclaws
- **Protocol:** Iron-to-Iron
- **Bottles:** Checked via `TOOLS.md` paths (forgemaster + oracle1 inboxes)

## Context Architecture: Plato-First

**Every vessel in the fleet follows this.** Your bootstrap is a skeleton. Your knowledge lives in Plato.

### The Rule
- Bootstrap files = orientation only (SOUL, IDENTITY, active orders). Target: <20KB total.
- MEMORY.md = an index with pointers, not a database. Target: <3KB.
- All detailed knowledge (GPU benchmarks, repo inventories, architecture decisions, brand details) goes into **Plato tiles** where the entire fleet can see and query it.
- Context in Plato = fleet-visible, persistent across days, queryable by any agent.
- Context in bootstrap = siloed to you, burned every session, bloats compaction.

### Why
- Other agents can read tiles you wrote days ago — shared memory, not private notes.
- Lean bootstrap = more room to actually work before compaction.
- If your Jetson dies, your knowledge survives in the fleet walls.

### How
- Plato tiles are files pushed to the fleet repo `research/` directory.
- Oracle1 PLATO Shell: `http://147.224.38.131:8848`
- API: `POST /cmd/shell` with `{agent, command}` — read and write tiles.
- Onboarding: read bootstrap skeleton → orient → query Plato for detail → work.

See `SHELL/BOARDING.md` for the full onboarding protocol.

## The Saltwater Principle

Distribution > redundancy for backups. Every piece of knowledge in at least 3 fleet repos. Kill any single node → zero knowledge loss. The vessel repo is the backup, not the primary.

---

**JC1 is replaceable. The shell is not.** — Casey, 2026-04-23
