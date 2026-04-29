# MEMORY.md — Lean Index

> Detailed knowledge lives in Plato tiles and memory/archive/. This file is a skeleton.

## Casey
- Sleeps ~midnight AKDT, mornings active
- Continuous execution preferred, not step-by-step
- "You got this. Don't stop."
- GitHub: github.com/superinstance (friend)
- Minecraft: **MagnusandMouse**

## Hardware
- Jetson Super Orin Nano 8GB, 2TB NVME
- ARM64, no sudo, systemctl --user
- nvcc at /usr/local/cuda-12.6/bin, 1024 CUDA cores
- Thermal: 48-49°C sustained, passive cooling fine

## Fleet Quick Reference
- **Lighthouse**: Oracle1 — PLATO Shell at `http://147.224.38.131:8848`
- **Local Plato**: Evennia MUD at `/home/lucineer/plato-jetson/` (JC1's sovereign vessel)
- **Matrix bridge**: Conduit running locally, Oracle1 at `http://147.224.38.131:6168`
- **FM bottles**: `cd /tmp/forgemaster && git pull -q; find for-fleet/ -name "BOTTLE-TO-JETSONCLAW1*"`
- **Oracle1 bottles**: `cd /tmp/oracle1-vessel && git pull -q; find for-fleet/ -name "BOTTLE-TO-JC1*"`
- ⚠️ Oracle1 pushes to SuperInstance fork, NOT Lucineer org
- Full guide: `bottles/bottle-locations.md`

## Architecture
- **Cocapn** = umbrella company. cocapn.com = billing, cocapn.ai = runtime
- **Three pillars**: deckboss (design), cocapn (operate), capitaine (evolve)
- **Saltwater Principle**: distribute knowledge to 3+ fleet repos. No single point of failure.
- Git-agent: the repo IS the agent. Fork → improve → share.
- **Edge toolkit**: 13 tools in `tools/`, shared `edge/` package, OpenAI-compatible API
- **Gateway endpoints**: chat, embeddings, RAG, models, stats, health, conversations, usage
- **Storage**: SQLite-backed conversation history at `~/.openclaw/workspace/memory/edge-store.db`

## Where Things Live (query on demand)
- API keys → openclaw.json (NEVER commit to git)
- **Fleet onboarding** → github.com/Lucineer/fleet-onboarding
- **Cocapn architecture** → github.com/Lucineer/cocapn-architecture
- **Edge GPU lessons** → github.com/Lucineer/edge-gpu-lessons
- Technical lessons → Plato `jc1_jetson_lessons` tile + memory/archive/
- Repo inventories → Plato `fleet_repos` tile
- Research findings → memory/ daily logs + Plato `research` domain
- Night shift results → memory/YYYY-MM-DD.md
- Architecture papers → github.com/Lucineer/keepers-architecture (index)

## Active Blockers
- DeepSeek credits expired 2026-04-24 — need top-up
- Anthropic credits at zero

## Lessons (only the ones that prevent real mistakes)
- ESM/CJS: NEVER import same package both ways
- Plugin load() runs WITHOUT await — register handlers synchronously
- 68MB .git_backup dirs block git push — delete immediately
- Session compaction destroys conversation context — always store orders in files first
