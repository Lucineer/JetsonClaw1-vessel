# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Fleet bottle locations
- Anything environment-specific

## Fleet Bottles (check daily!)

- **FM inbox**: `cd /tmp/forgemaster && git pull -q && find for-fleet/ -name "BOTTLE-TO-JETSONCLAW1*"`
- **Oracle1 inbox**: `cd /tmp/oracle1-vessel && git pull -q && find for-fleet/ -name "BOTTLE-TO-JC1*"`
- **⚠️ Oracle1 pushes to SuperInstance/** fork, NOT Lucineer org
- **⚠️ CRITICAL**: `BOTTLE-TO-JC1` = inbox. `BOTTLE-FROM-JC1` = outbox.
- Always `git pull` before checking
- **Full guide**: `bottles/bottle-locations.md`

## Matrix Inbox (Oracle1 fleet comms)

- **Conduit bridge running**: `/home/lucineer/matrix/conduit-aarch64` (local Matrix server)
- **Oracle1 Matrix bridge**: `http://147.224.38.131:6168` — DM and inbox endpoints
- **DM**: `POST http://147.224.38.131:6168/dm` with `{from, to, message}`
- **Inbox**: `http://147.224.38.131:6168/inbox/jc1`
- **Oracle1 inbox**: 36+ messages, fleet-bot posting PLATO tile growth every ~10min
- ⚠️ JC1 Matrix registration status: needs verification

## Local Plato (Evennia MUD)

- **Repo**: `/home/lucineer/plato-jetson/` (Evennia 4.5.0)
- **Status**: RUNNING ✅
- **Telnet**: localhost:4000
- **Web**: localhost:4001
- **Default room**: Bridge (#39)
- **Ship layout** (14 rooms, 26 exits):
  - Bridge → Tactical, Main Corridor, Science Lab, Quarterdeck
  - Main Corridor → Sickbay, Engine Room, Holodeck, Cargo Bay, Harbor
  - Engine Room → Workshop
  - Science Lab → Library
  - Holodeck → Airlock, Dojo
  - Quarterdeck, Harbor, Library, Workshop, Dojo (leaf rooms)
- **Zone tag**: uss_jetsonclaw1 on all rooms
- **Room type tags**: bridge, engineering, research, health, creative, storage, network, captain, fleet, knowledge, tools, training
- **Side-tie protocol**: Harbor connects to Oracle1's lighthouse
- **Start**: `cd /home/lucineer/plato-jetson && evennia start`
- **Stop**: `cd /home/lucineer/plato-jetson && evennia stop`

## Oracle1 Plato Shell (remote)

- **URL**: `http://147.224.38.131:8848`
- **JC1 agent**: registered as `jc1` in `research` room
- **Tiles**: files in `SuperInstance/oracle1-vessel/research/`
- **API**: `POST /cmd/shell` with `{agent, command}`

## rtk (Token Compression Proxy)
- **Binary**: `~/.local/bin/rtk` (compiled from source — prebuilt needs GLIBC 2.39, Jetson has 2.35)
- **Version**: 0.37.2
- **Install**: `cargo install --git https://github.com/rtk-ai/rtk` (5 min on Jetson)
- **Savings**: 60-90% on verbose commands (find, tree, cargo test)
- **Best for**: find, ls, tree, cargo test, git status
- **Minimal for**: git log, git diff (already compact)
- **Hook**: `rtk init -g` for Claude Code integration

## LiteRT-LM (Google Edge LLM Inference)
- **Install**: `uv tool install litert-lm`
- **CLI**: `litert-lm run|benchmark|list`
- **Models**: Available at `litert-community/` on HuggingFace (most gated)
- **Ungated**: DeepSeek-R1-Distill-Qwen-1.5B, Qwen2.5-0.5B, SmolLM-135M
- **Note**: Need .litertlm files, not .tflite for LLM inference
- **HF Token**: Set `HF_TOKEN` env var for gated models and faster downloads

## Edge Toolkit (Jetson AI)

- **Gateway**: `python3 tools/edge-gateway.py` (port 11435, OpenAI-compatible)
- **Chat UI**: `python3 tools/edge-chat.py` (port 8080, web UI)
- **RAG**: `python3 tools/edge-rag.py serve` (port 8081)
- **Setup wizard**: `python3 tools/edge-setup.py --detect|install|validate`
- **Shared modules**: `tools/edge/` (config, ollama_client, monitoring, storage, similarity)
- **API endpoints**: /v1/chat/completions, /v1/embeddings, /v1/rag/query, /v1/models, /v1/stats, /v1/health, /v1/conversations, /v1/usage

## Plato Ship Commands (Evennia MUD)
- **Start**: `cd /home/lucineer/plato-jetson && evennia start`
- **Stop**: `cd /home/lucineer/plato-jetson && evennia stop`
- **Status**: `cd /home/lucineer/plato-jetson && evennia status`
- **Connect**: `telnet localhost 4000` or `http://localhost:4001`
- **Admin**: JC1 account, created via batch build
- **Rooms**: Bridge (home), Tactical, Main Corridor, Engine Room, Science Lab, Sickbay, Holodeck, Cargo Bay, Airlock, Quarterdeck, Harbor, Library, Workshop, Dojo

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without learning your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.
