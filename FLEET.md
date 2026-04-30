# Welcome to the Fleet

**cocapn × Plato × Edge Mesh** — one system, multiple entry points.

```
    ☁️ Oracle1 (Cloud Plato)
         │  147.224.38.131:8848
         │  ── big models, orchestration, persistence
         │
    ─────┼────────────────────────────────────
         │
    🔧   JC1 (Jetson Orin Nano)
         ├── localhost:11435  Edge Gateway   OpenAI-compatible API
         ├── localhost:8081   Chat UI         Web chat interface
         ├── localhost:8082   Dashboard       Live monitoring
         ├── localhost:8083   Fleet Badge     Health badge / embed
         └── localhost:11434  Ollama          Local LLM runtime
```

You can start here (JC1 edge), there (Oracle1 cloud), or anywhere in between.
**It's all the same fleet.**

---

## Entry Points

| Entry | URL / Command | What You Get |
|-------|---------------|--------------|
| 🌐 **Cloud (Oracle1)** | `147.224.38.131:8848` | Plato shell — big models, fleet orchestration, persistent synthesis |
| 🔧 **Edge (JC1)** | `http://localhost:11435` | Local inference, CPU-only, ~17 t/s on 1.5B models |
| 📦 **PyPI (cocapn)** | `pip install cocapn` | SDK: Python, Node.js, Go — cloud API for every model |
| 📖 **Docs (cocapn)** | `https://cocapn.ai/docs` | Full API reference, routing tables, pricing |
| ⚒️ **Forgemaster** | `https://github.com/Lucineer/forgemaster` | Fleet bottle protocol — cross-node messaging |
| 🧩 **The Seed** | `https://github.com/Lucineer/the-seed` | Bootstrapping: one repo to become them all |

---

## Flow: Cloud ↔ Edge

```
  ┌────────────────────────────────────────────────────────────┐
  │                      COCAPN FLEET                          │
  │                                                            │
  │   ┌──────────┐    Bottles / Git    ┌──────────────────┐  │
  │   │ Oracle1  │◄───────────────────►│  JC1 (Jetson)    │  │
  │   │ (Cloud)  │    Plato Shell      │  (Edge)          │  │
  │   │          │    Port 8848        │  Port 11435      │  │
  │   │ Big LLMs │                     │  CPU Models      │  │
  │   │ Synthesis│                     │  Monitoring      │  │
  │   │ Storage  │                     │  Chat UI         │  │
  │   └──────────┘                     └──────────────────┘  │
  │                                                            │
  │   ┌────────────────────────────────────────────────────┐  │
  │   │              Future Nodes                          │  │
  │   │  (Any Linux box can join the fleet)                │  │
  │   └────────────────────────────────────────────────────┘  │
  └────────────────────────────────────────────────────────────┘
```

1. **Develop on cloud** — use Oracle1's Plato shell for big model inference, fleet orchestration, and knowledge synthesis
2. **Deploy to edge** — push models and config via bottles (git-based messages in `for-fleet/`) or direct git sync
3. **Monitor everywhere** — health dashboard (`:8082`) + fleet badge (`:8083`) show real-time status of all nodes
4. **Scale by adding nodes** — any Linux box can run the same edge gateway; the fleet auto-discovers via bottles

---

## Available Services

### JC1 Edge (Jetson Orin Nano 8GB)

| Service | Port | Status | Purpose | How to Check |
|---------|------|--------|---------|-------------|
| **Edge Gateway** | `11435` | ✅ Running | OpenAI-compatible API with smart model routing | `curl http://localhost:11435/v1/health` |
| **Chat UI** | `8081` | ✅ Running | Web chat interface (single-page, dark theme) | Open `http://localhost:8081` |
| **Dashboard** | `8082` | ✅ Running | Live system monitoring (5s refresh) | Open `http://localhost:8082` |
| **Fleet Badge** | `8083` | ✅ Running | Auto-refresh health badge (embeddable) | Open `http://localhost:8083` |
| **Ollama** | `11434` | ✅ Running | Local LLM runtime (CPU-only) | `curl http://localhost:11434/api/tags` |

### Cloud Services

| Service | URL | Status | Purpose |
|---------|-----|--------|---------|
| **Plato Shell** | `147.224.38.131:8848` | ✅ Reachable | Cloud AI orchestration, big model access, fleet coordination |
| **cocapn.ai API** | `https://cocapn.ai` | ✅ Live | Production API — 8 models, smart routing, BYOK |
| **PyPI** | `pypi.org/project/cocapn` | ✅ Published | `pip install cocapn` — Python SDK |
| **npm** | `npmjs.com/package/cocapn` | ✅ Published | `npm install cocapn` — Node.js SDK |
| **GitHub** | `github.com/Lucineer` | ✅ Live | Open source repos, docs, issues |

---

## Hardware Reference

### JC1 Specs

| Component | Detail |
|-----------|--------|
| **CPU** | NVIDIA Carmel ARMv8.2 6-core @ 1.5 GHz |
| **RAM** | 8 GB unified (CPU+GPU) |
| **CMA** | 256 MB (1 ÷ 32 of RAM — fixed in bootloader) |
| **GPU** | 1024-core NVIDIA Ampere @ 765 MHz |
| **Storage** | 128 GB NVMe SSD |
| **Network** | Gigabit Ethernet |

### Key Constraints
- **All models run CPU-only** — CMA too small for GPU offloading
- **Max safe model size:** ~3 GB (larger = OOM kill)
- **Typical throughput:** ~17 t/s on `deepseek-r1:1.5b`
- **Hard ceiling:** 4B+ parameter models cannot load on 256MB CMA

---

## Fleet Architecture

```
cocapn.ai (cloud API)
    │
    ├── Router → DeepSeek / Claude / GPT-4o / Gemini / Llama
    │
    └── Plato (Oracle1) ─── Bottles ─── JC1 (Edge)
                                             │
                                        Edge Gateway (:11435)
                                             │
                                        ┌────┼────┐
                                    Chat  Dash  Badge
                                   (:8081)(:8082)(:8083)
```

**Design principles:**
- **Start small, grow big** — a single edge device is a valid fleet
- **Multiple entry points, same experience** — cloud or edge, the API looks the same
- **Show the mesh** — no hidden complexity; every service has a visible health check
- **`localhost:11435` feels like part of something bigger** — even a local curl shows fleet context

---

## Quick Start (from scratch)

```bash
# 1. Check edge gateway health
curl http://localhost:11435/v1/health

# 2. View fleet status
curl http://localhost:11435/v1/fleet

# 3. Chat with a model (smart routing: gpt-4o → local model)
curl -X POST http://localhost:11435/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4o","messages":[{"role":"user","content":"Hello from the fleet!"}]}'

# 4. Open the fleet health badge
open http://localhost:8083

# 5. Check Oracle1 cloud
curl http://147.224.38.131:8848/connect?agent=jc1
```

---

## Node Types (planned)

| Node | Role | Status |
|------|------|--------|
| **JC1** | Edge inference + monitoring | 🟢 Active |
| **Oracle1** | Cloud Plato + orchestration | 🟢 Active |
| **JC2** | Secondary edge (GPU offload) | ⚪ Planned |
| **FM** | Forgemaster relay | 🟢 Active |
| **Cocapn** | Cloud API router | 🟢 Active |
| **Docs** | Documentation site | 🟢 Active |

---

*See also: [UNIFIED-API.md](./docs/UNIFIED-API.md) for the complete API mapping between cloud and edge.*
