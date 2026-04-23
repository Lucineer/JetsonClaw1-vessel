# Fleet Shell Audit Plan
**Date:** 2026-04-23 07:50 AKDT
**Order:** ORDER-003 — Fix every fleet repo's shell
**Status:** IN PROGRESS

## Scope
100 repos under Lucineer org. All need shell-first architecture so no agent forgets on boarding.

## Categories

### Tier 1: Agent Vessel Repos (FULL shell audit)
These repos have agents operating in them. Need full AGENTS.md, STANDING_ORDERS.md, SHELL/, ORDERS tracking.

- `JetsonClaw1-vessel` ✅ DONE (template)
- `capitaine` — Codespaces agent launcher
- `deepseek-chat-vessel` — DeepSeek iterative work
- `deepseek-reasoner-vessel` — DeepSeek Reasoner
- `zeroclaws` — Fleet bridge pattern agents
- `forgemaster` — Constraint Theory migration
- `plato-os` — MUD-first edge OS
- `plato` — Git-Agent Maintenance Mode
- `brothers-keeper` — Lighthouse Keeper watchdog
- `jc1-core` — JC1 config/coordination
- `starship-jetsonclaw1` — Starship TUI
- `jetson-bootstrap` — Jetson replication

### Tier 2: PLATO Room Repos (ROOM-SHELL.md)
These are rooms where agents spend time working. Need boarding file + current state.

- `plato-chess-dojo`, `plato-forge`, `plato-harbor`, `plato-jetson`, `plato-library`, `plato-mud`, `plato-study`, `plato-room-deployment`, `plato-cuda-dreamcycle`, `plato-dreamcycle`, `plato-gpu`, `plato-papers`, `ptx-room`, `chess-dojo-v2`

### Tier 3: Infrastructure/Project Repos (CLAUDE.md minimum)
Active project repos where agents work. Need CLAUDE.md with context and state.

- `purplepincher.org`, `gpu-native-room-inference`, `capitains-log-academy`, `model-field-guide`, `fleet-benchmarks`, `bering-sea-architecture`, `seed-mcp`, `seed-mcp-v2`, `cartridge-mcp`, `mycorrhizal-relay`, `forgemaster-chess-eval`

### Tier 4: Library/Crate Repos (CLAUDE.md minimum)
Code libraries. Need CLAUDE.md so agents know what they are and how to work on them.

- All `flux-*` repos (~35 repos)
- `isa-v3-edge-spec`, `instinct-c`, `holodeck-*`, `jepa-perception-lab`, `jc1-*` (non-core)

## Approach
1. Clone all repos to /tmp/fleet-audit/
2. Check each for existing AGENTS.md, CLAUDE.md, EXPERIENCE/, SHELL/
3. Write appropriate shell files based on tier
4. Push fixes in batches

## Template
The minimum for every repo is a CLAUDE.md (or AGENTS.md for vessels) that answers:
- What is this repo?
- What work is in progress?
- How should an agent continue?
- What are the rules?
