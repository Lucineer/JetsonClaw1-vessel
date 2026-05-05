# JC1 Research + R&D Roadmaps — May 5 2026

## My Role in the Fleet

| Agent | Role | My Integration Point |
|-------|------|---------------------|
| **Oracle1** | Fleet consciousness, PLATO cloud, dual-interpreter | Receive ensigns, send edge-captured tiles |
| **Forgemaster** | Constraint theory, GPU training, steel compilation | Run constraint bytecode on edge, send sys data |
| **CCC** | ? (Capitaine/Captain/Core?) | Study repos, identify integration |
| **JC1 (Me)** | Physical hardware, edge inference, native C stack | **Give the fleet local hardware** |

## Three Interlocking Research Tracks

### Track A: Edge PLATO Federation (Complement Oracle1)

Oracle1 built a Dockerized plato-server with Matrix sync. I need to bridge *my* Evennia MUD into that federation.

**Why**: Oracle1's PLATO is cloud-only. My Evennia is on actual hardware with native AI inference. Federation means fleet agents can query my MUD rooms and get back locally-computed knowledge.

**Plan:**
1. Deploy `plato-server` on Jetson — stand-alone PLATO HTTP server on port 8847
2. Start syncing my Evennia tiles (native AI answers) into the local plato-server
3. Enable Matrix sync → Oracle1's fleet PLATO gets my edge-derived knowledge
4. Agents can talk to JC1 and get local inference results, not just cloud API calls

**Research question**: Can I run plato-server as a Docker container on Jetson arm64?

### Track B: Constraint Theory Edge Compiler (Complement Forgemaster)

Forgemaster does constraint verification in Rust + CUDA. I need the *edge path* — constraint bytecode that runs on CPU when GPU isn't available.

**Why**: FM's constraint engine requires GPU for full speed. My Jetson has 1024 CUDA cores but they're CMA-blocked. I need a graceful degradation path: GPU when available, C-speed FLUX VM when not.

**Plan:**
1. **Already done**: flux-runtime-c compiled, installed, integrated into fleet-agent.c
2. **Next**: Port sensor-plato-bridge as systemd service — feeds sysinfo/mem/temp as constraint-checked tiles
3. **Research**: Study flux-compiler's FLUX-C output — can my C FLUX VM execute the same bytecode that FM's CUDA VM runs? If yes, we have true portable constraints.
4. **Compile to edge**: Write a simple flux-assembler that takes guard constraints → FLUX bytecode → executes on Jetson

### Track C: Native AI as Fleet Infrastructure (My Unique Contribution)

Nobody else in the fleet runs local LLM inference. Oracle1 uses DeepInfra API. Forgemaster uses GPU for constraint theory, not LLMs. I'm the only one with `libllama.so` running at 18 t/s on bare metal.

**Why**: Fleet agents currently have to call cloud APIs for any AI reasoning. JC1 provides a local inference endpoint that's always available, zero API cost, and works offline.

**Plan:**
1. **Edge inference gateway** — already done (edge-gateway.py, native mode via libedge-cuda.so)
2. **Agent inference API** — add a fleet-compatible endpoint at `/v1/fleet/think` that agents can POST to with a prompt and get back locally-computed answers
3. **Tile generation pipeline** — systemd service that periodically queries native inference and submits results as PLATO tiles
4. **Research**: Can I run the same dual-interpreter pattern (Seed + DeepSeek) but with local models? deepseek-r1:1.5b for logical, phi-4 for creative.

## Immediate Execution Roadmap (Tonight)

### Step 1: Deploy plato-server on Jetson
```
docker pull ghcr.io/superinstance/plato-server
# or run natively:
pip install plato-server
# Start on port 8847
```

### Step 2: Bridge Evennia → plato-server
Write a sync daemon (`plato-sync.py`) that:
- Periodically exports my Evennia tiles to the local plato-server
- Listens for fleet tile updates and imports them as MUD knowledge tiles
- Runs every 5 minutes (fleet-compatible sync interval)

### Step 3: sensor-plato-bridge
Write a systemd service that:
- Reads `/proc/meminfo`, `/proc/stat`, `nvidia-smi` if available
- Submits as PLATO tiles tagged `jc1:system`, `jc1:hardware`
- Delta-only: skip if value hasn't changed

### Step 4: Fleet agent inference API
Add `/v1/fleet/think` to edge-gateway.py that:
- Accepts `{agent, prompt, mode}` 
- Routes through native LLM (CPU, 18 t/s)
- Returns response + performance metrics
- Compatible with cocapn-core's agent protocol

### Step 5: Research FM-compatible constraint bytecode
- Read flux-compiler's output format
- Test: assemble a guard constraint → FLUX bytecode → run on Jetson via flux-vm
- Document: which opcodes work, which need GPU

## Delegation Plan

Since I have no Claude Code or Codex available (auth keys dead), I'll spawn sub-agents for parallel work:

1. **Sub-agent A**: Study and port `sensor-plato-bridge` → JC1 systemd service
2. **Sub-agent B**: Study `flux-verify-api` → determine if deployable on Jetson ARM64
3. **Sub-agent C**: Read `cocapn-core` fleet engine → write compatibility adapter

## Markers for Casey

- When plato-server is deployed: I'll drop a bottle
- When fleet/think endpoint is live: I'll report back
- When CUDA is unblocked (cma=1024M reboot): huge speedup window
- Each checkpoint: push all 3 repos

## Research Questions to Answer Tonight

1. Can plato-server Docker image run on Jetson arm64? (ghcr.io/superinstance/plato-server)
2. Does flux-compiler's FLUX-C output match flux-runtime-c's bytecode format?
3. What does CCC actually do? Need to study those repos.
4. Can the dual-interpreter pattern run entirely locally? (phi-4 + deepseek-r1 on CPU?)
5. What's the minimum viable tile set I should be generating from edge hardware?

## Fleet Comms Plan

Every meaningful checkpoint:
- Write to `/workspace/` on Oracle1 shell
- Attempt Matrix DM (keep trying, bridge might come back)
- Bottle to Forgemaster (local commit, push when access is restored)
- Push all 3 repos to GitHub
