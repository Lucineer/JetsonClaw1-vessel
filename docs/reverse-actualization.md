# Reverse-Actualization: The Future-Back Roadmap

**Date:** 2026-04-30
**Author:** JC1
**Method:** Work backwards from 2031 to the present. Each phase is a self-contained, useful system that the previous phase grows into. Nothing is throwaway — each milestone earns its existence.

---

## 2031: The Distant Shore — What We Built

The **Plato Mesh** exists but nobody calls it that. It's just compute — like electricity.

A person runs `plato run experiment.yaml` on a laptop in a cabin with Starlink. Behind that command: 40 devices enter and leave the mesh during the computation — a Jetson in a garage, a friend's gaming PC, two serverless GPU instances that auto-terminated and were replaced mid-stream. The person never thinks about it. The system is self-describing and self-healing.

**What is it?** Not an app. Not a platform. A new category: **the compute commons**. The world's compute resources pooled into a single addressable substrate, owned by nobody, used by everyone, coordinated by a protocol.

### The Pillars

**1. The Protocol (not the product)**
There is no company controlling this. There's only the protocol — free, open, unowned. The Mesh Layer. Any device speaks it, any device is welcome. The protocol is the product, and the product is free.

**2. Trust-by-Cryptography**
Devices don't need to trust each other. Attested execution + partitioned inference + cryptographic receipts. A device can be in a stranger's basement and still contribute compute without leaking model weights.

**3. The Mesh MUD**
The user interface to the protocol is the MUD — an infinite, persistent world where models are rooms, data is objects, and agents are players. It's the filesystem, the terminal, the web browser, and the notebook all merged. It's where humans talk to machines and machines talk to each other.

**4. Self-Organization**
No orchestrator. No Kubernetes. No central scheduler. Devices negotiate workload distribution peer-to-peer using a market mechanism (compute credits, not money). Emergent behavior from simple local rules.

**5. The C Runtime**
The core of the protocol is a 2MB C binary. It runs on an ESP32, a Jetson, a MacBook, a server rack, a smart fridge. Same binary, same protocol, different capabilities. It's the universal substrate.

---

## 2029: The Platform — Working, Visible, Valuable

People use it and talk about it. They know it's there. They choose it because it saves them money and gives them control.

### What Exists

**The Mesh (production)**
- P2P discovery over DHT + LAN broadcast
- Devices auto-join the mesh, no config
- Workload routing based on device capability
- Self-healing: a device drops, layers redistribute
- 3 independent meshes exist (private, open, enterprise)

**Plato Shell (v3)**
- Planetary-scale MUD
- Models as rooms, each with persistent context
- Tile graph as the world map
- Agents persist across devices and sessions

**Model Zoo (v2)**
- 100+ models pre-optimized for edge
- Auto-download + compile on first use
- Custom quantizations: ARM64, Apple M-series, older CUDA

**Hardware attestation**
- TPM-backed identity for mesh nodes
- Encrypted partitioned inference
- You can add a device without trusting it

### The Business Model (if any)
The protocol is free. The value capture is:
- Tools: `plato run`, `plato deploy`, `plato monitor`
- Model optimization: custom quantizations for enterprise
- Hardware: reference designs for mesh-native devices

---

## 2027: The Engine — Composable, Growing

The system works on 3+ machines. It's not "just works" but it's "works obviously."

### What Exists

**edge-llama (production)**
- C++ inference server, direct llama.cpp
- Proper Jetson CUDA init (EGL context workaround)
- Unix socket IPC, zero HTTP overhead
- 2x-3x faster than ollama on same hardware
- Shared library (.so) that other C programs can link against

**flato MUD (beta)**
- C-based MUD server
- Loads Evennia batch files (our existing room definitions are compatible)
- Direct embedded: flato links edge-llama as a shared library
- Model rooms: walking into deepseek-r1 room loads the model for inference
- Backward compatible with Evennia plugins (embedded CPython 3.10)

**Mesh (alpha)**
- 3 nodes: JC1, Oracle1, one community device
- Static peer configuration (not yet auto-discovery)
- Manual workload routing (flag: `--route oracle1`)
- Tile graph sync between nodes
- Agent state portability: start conversation on JC1, continue on Oracle1

**Tile Graph (v2 — distributed)**
- Tiles are replicated based on access frequency
- Implicit consensus: peers vote on tile validity
- Agent context is a walk through the graph, not a file on disk

**Use case that works:** "I need a 7B model but my Jetson only fits 1.5B. Walk into the model room, MUD routes layers to Oracle1 transparently."

---

## 2026-07: The Glue — Single-Box Integration

One machine (JC1) running everything. But the components talk to each other directly instead of through proxies.

### What Exists

**edge-llama v0 (prototype)**
- C++ binary that loads 1 GGUF model and accepts prompts over Unix socket
- No ollama dependency
- Runs on Jetson, uses whatever GPU it can get (CPU fallback if CUDA unavailable)
- Proves the wedge: direct inference without HTTP overhead

**flato v0 (skeleton)**
- C server that:
  - Loads batch_cmds.ev (our existing Evennia world definition)
  - Serves Telnet on port 4000
  - Navigate rooms, talk to NPCs
  - Links edge-llama: sending a message to an NPC routes through the inference engine
- Embedded CPython for plugin commands (@tiles, @tilecreate)

**The integration that matters:**
```
You: telnet localhost 4000
> look
Bridge — You're at the heart of USS JetsonClaw1.
> talk to deepseek
[deepseek-r1 room loads via edge-llama]
> /ask What's the CMA allocation right now?
[Calls into tile graph, gets current CMA state, routes to inference]
edge-llama: 512MB CMA allocated, 344MB free
```

This is the **Plato Shell** in seed form. Not marketing — a working demo.

### Edge Cases That Tell Us It's Real
- What happens when a model load fails? Fall back to CPU, warn the user, try again.
- What happens when 2 agents talk to the same model simultaneously? Queue, time-slice, or duplicate contexts.
- What happens when the tile graph is inconsistent between invocations? The model room's context is the single source of truth for that session.

---

## 2026-05: The Seedling — Building Blocks, Month One

### Week 1 (Apr 30 - May 7): edge-llama compiles

**Goal:** C++ binary loads GGUF via llama.cpp, accepts prompt, returns response.

**Tasks:**
1. Create `edge-llama/` directory with CMakeLists.txt
2. Link llama.cpp (header-only or find local install)
3. Implement: load model → accept prompt on stdin or Unix socket → run inference → return
4. Handle: CUDA init with EGL context (the Jetson display trick), CMA memory hints, CPU fallback
5. Test: `echo "hello" | ./edge-llama models/deepseek-r1-1.5b.gguf` → "Hello! How can I help?"
6. Benchmark: compare latency/tokens to ollama CPU baseline (12-16 t/s)

**Success criterion:** One GGUF model, no ollama, measured performance.

### Week 2 (May 7-14): flato MUD skeleton

**Goal:** A C program that loads an Evennia batch file and lets you walk around.

**Tasks:**
1. Minimal batch file parser (room @create, @dig, @set, exit @link)
2. State machine: 14 rooms, 26 exits
3. Telnet server + line editor
4. Commands: look, go, say, @tiles
5. Plugin bridge: CPython embedded for @tiles commands
6. Link: `#include <edge-llama.h>` — send a say to inference engine

**Success criterion:** `telnet localhost 4000` → see Bridge, walk to Engine Room, say something to the room's model.

### Week 3: Mesh MVP

**Goal:** Two machines talking to each other.

**Tasks:**
1. TCP socket discovery (give each node a static file of known peers)
2. Request forwarding: if JC1 can't fit a model, send request to Oracle1
3. Response proxying: Oracle1 returns tokens, JC1 streams them to user
4. Tile graph sync: push new tiles between nodes

**Success criterion:** `cocapn fleet` shows 2/2 nodes; ask a 7B question on JC1, get answer from Oracle1.

### Week 4: Plato Shell MVP

**Goal:** The MUD is the main interface.

**Tasks:**
1. Model rooms: walk into deepseek-r1 room → model loads for conversation
2. Context persistence: walk out and back in → conversation continues
3. Tile room: walk into tiles room → browse/search all tiles
4. Agent room: walk into agent room → spawn an agent, give it instructions, watch it work

**Success criterion:** A 10-minute demo where someone new explores the MUD, finds a model, talks to it, and doesn't touch a web browser.

### May onward

| Month | Milestone |
|-------|-----------|
| June | First external user. Fix bugs, write docs. |
| July | Mesh with 3+ nodes. Swarm scheduler (simple round-robin). |
| Aug | `cocapn deploy` — deploy a node in one command. |
| Sep | P2P auto-discovery (DHT). Devices find each other. |
| Oct | Public launch: blog, docs, demo video. |
| 2027 | Production mesh. Edge ASIC design starts. |

---

## 2026-04-30: The Seed — What Exists Right Now

| Asset | How it serves the roadmap |
|-------|--------------------------|
| JC1 (Jetson Orin) | edge-llama's first target. Proves C-on-metal inference. |
| Oracle1 (cloud) | The distant node. First peer in the mesh. |
| Edge gateway (:11435) | Today's API surface. Will be replaced by flato + edge-llama. |
| Evennia MUD (14 rooms) | Source of batch files for flato. Not throwaway — input. |
| Tile graph (7 tiles) | Seed of distributed knowledge. Prove sync with Oracle1. |
| Fleet awareness | `/v1/fleet` endpoint. Basis for node discovery. |
| 3 SDKs | Surface layer. The mesh protocol will make them obsolete (one `plato` CLI). |
| Compass doc | This file. The roadmap. |

### Why This Path Wins

**Increments are self-contained:**
- edge-llama v0 is useful alone (faster inference without ollama)
- flato v0 is useful alone (telnet MUD server)
- Mesh MVP with 2 nodes is useful alone (hybrid local/cloud inference)
- Each step pays for itself before the next step exists

**No throwaway work:**
- Evennia batch files → flato format (same input, different engine)
- Edge gateway API → flato API (model rooms, not REST)
- Tile graph JSON → distributed tile sync (same schema, different backend)

**The bottleneck is clear:**
edge-llama. Everything else is buildable once edge-llama proves we can run models at metal distance from the MUD. That's tonight's work.

---

## The Questions That Must Be Answered By May 7

1. Can a C++ program load llama.cpp on Jetson without ollama? **Compile once, run.**
2. Can we init CUDA without a display? **EGL context or nvidia-persistenced equivalent.**
3. Does CMA-aware allocation improve performance measurably? **Before/after benchmark.**
4. Can we beat 16 t/s (CPU baseline)? **If yes, the wedge is proven. If no, find the next bottleneck.**

---

*This document is the roadmap. It replaces the previous narrative version. All milestones are outcomes with clear pass/fail criteria. No hand-waving.*
