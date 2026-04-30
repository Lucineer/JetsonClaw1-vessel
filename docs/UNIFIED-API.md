# Unified API Reference — Cloud × Edge

Maps cloud Plato / cocapn.ai endpoints to the JC1 edge gateway. Every request tells you where you are and what the rest of the fleet looks like.

```
Cloud (Oracle1 / cocapn.ai)   ←→   Edge (JC1 Jetson)
   Big models, routing            CPU models, local inference
   API keys, BYOK                 Local-only (optional key)
   Production                     Development + edge
```

---

## Quick Comparison

| Feature | Cloud (cocapn.ai) | Cloud (Plato/Oracle1) | Edge (JC1 Gateway) |
|---------|-------------------|----------------------|-------------------|
| **Base URL** | `https://cocapn.ai/v1` | `http://147.224.38.131:8848` | `http://localhost:11435` |
| **Auth** | API key (`cpn_*`) | Agent name + room | Optional API key or local-only |
| **Models** | 8 cloud models (DeepSeek, Claude, GPT-4o, Gemini, Llama) | Plato shells + big model orchestration | 7 local CPU models (deepseek-r1:1.5b, phi3:mini, etc.) |
| **Latency** | 500ms–3s (network) | 1s–5s (cloud + network) | 50ms–1s (local, CPU-only) |
| **Cost** | Per-token billing | Plato usage | Free (electricity only) |
| **Max context** | 128K–1M tokens | Plato session limit | 2048 default, configurable |
| **Streaming** | ✅ SSE | ✅ SSE (Plato) | ✅ SSE (NDJSON→SSE) |
| **Embeddings** | ✅ (via model) | ✅ | ✅ nomic-embed-text |
| **RAG** | Via cocapn routing | ✅ Plato memory | ✅ Fleet knowledge index |
| **Vision** | ✅ GPT-4o, Claude | ❌ | ✅ moondream (local) |

---

## Endpoint Mapping

### Chat Completions

| Cloud (cocapn.ai) | Cloud (Plato Shell) | Edge (JC1) |
|---|---|---|
| `POST /v1/chat/completions` | `POST /cmd/shell` (indirect) | `POST /v1/chat/completions` |

**Cloud (cocapn.ai):**
```bash
curl https://cocapn.ai/v1/chat/completions \
  -H "Authorization: Bearer cpn_your_key" \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-chat","messages":[{"role":"user","content":"Hello"}]}'
```

**Edge (JC1):**
```bash
curl -X POST http://localhost:11435/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4o","messages":[{"role":"user","content":"Hello"}]}'
```

**Example response (both use same shape):**
```json
{
  "id": "chatcmpl-1712345678000",
  "object": "chat.completion",
  "created": 1712345678,
  "model": "gpt-4o",
  "routed_to": "qwen3.5:2b",
  "choices": [{
    "index": 0,
    "message": {"role": "assistant", "content": "Hello from the edge!"},
    "finish_reason": "stop"
  }],
  "usage": {"prompt_tokens": 20, "completion_tokens": 5, "total_tokens": 25}
}
```

> **Key difference:** Edge response includes `routed_to` when a cloud model name is mapped locally.

---

### Model Listing

| Cloud (cocapn.ai) | Edge (JC1) |
|---|---|
| `GET /v1/models` | `GET /v1/models` |

**Cloud returns:** 8 cloud-hosted models with pricing
**Edge returns:** 7 local CPU models with sizes and capability hints

```bash
# Edge model list
curl http://localhost:11435/v1/models | jq '.data[].id'
# → "deepseek-r1:1.5b"
# → "phi3:mini"
# → "qwen3.5:2b"
# → "nomic-embed-text"
# → "moondream:latest"
# → etc.
```

---

### System Stats / Health

| Cloud (cocapn.ai) | Edge (JC1) |
|---|---|
| `GET /api/dashboard` | `GET /v1/stats` |

**Edge response** includes real-time hardware telemetry:
```json
{
  "gpu_temp_c": 42.5,
  "cpu_temp_c": 55.0,
  "ram_total_mb": 7805,
  "ram_used_mb": 4185,
  "ram_available_mb": 3620,
  "cma_total_mb": 256,
  "cma_free_mb": 192,
  "cma_used_pct": 25.0,
  "uptime_s": 86400,
  "version": "1.1.0",
  "local_models": { ... }
}
```

---

### Fleet Status

| Edge (JC1) |
|---|
| `GET /v1/fleet` |

Unified fleet view — available on every node:
```bash
curl http://localhost:11435/v1/fleet
```

---

### Embeddings

| Cloud (cocapn.ai) | Edge (JC1) |
|---|---|
| `POST /v1/embeddings` | `POST /v1/embeddings` |

Same OpenAI-compatible shape on both:
```bash
curl -X POST http://localhost:11435/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{"model":"nomic-embed-text","input":"Hello world"}'
```

---

### RAG (Retrieval-Augmented Generation)

| Cloud (Plato memory) | Edge (JC1) |
|---|---|
| Plato tile store + memory | `POST /v1/rag/query` |

```bash
curl -X POST http://localhost:11435/v1/rag/query \
  -H "Content-Type: application/json" \
  -d '{"query":"Jetson GPU tips","index":"fleet-knowledge","top_k":5}'
```

---

## Model Routing

### Cloud → Edge Mapping

Every cloud model name has a local equivalent on JC1:

| Cloud Model | Routed To (Edge) | Size | Notes |
|---|---|---|---|
| `gpt-3.5-turbo`, `gpt-4`, `o1-preview` | `deepseek-r1:1.5b` | 1.1 GB | Fast, 17 t/s |
| `gpt-4o-mini`, `claude-3-sonnet`, `phi-4` | `phi3:mini` | 2.2 GB | Balanced reasoning |
| `gpt-4o`, `qwen-2.5-14b`, `deepseek-coder` | `qwen3.5:2b` | 2.7 GB | Creative/coding |
| `claude-3-haiku`, `llama-3-8b`, `gemini-1.5-flash` | `deepseek-r1:1.5b` | 1.1 GB | Fast responses |
| `claude-4-opus`, `o3-mini`, `mixtral` | `deepseek-r1:1.5b` | 1.1 GB | Best available |
| `nemotron-4-340b` | `nemotron-3-nano:4b` | 2.8 GB | Instruction following |
| `moondream` | `moondream:latest` | 1.7 GB | Vision |
| `text-embedding-3-small/large` | `nomic-embed-text` | 274 MB | Embeddings |

### Routing Priority

1. **Exact match** — if model exists locally, use it
2. **Routing table** — cloud names → mapped local model
3. **Too large** — >3.0 GB returns error with suggestions
4. **Fallback** — unknown → `deepseek-r1:1.5b`

---

## Authentication Model

### Cloud (cocapn.ai)
- **API key:** `cpn_*` format, passed as `Authorization: Bearer cpn_xxx`
- **BYOK:** Bring Your Own Keys (stored in Cloudflare Secrets)
- **Plans:** Free (100K tokens/day), Builder ($9/mo), Team ($29/mo), Enterprise

### Cloud (Plato / Oracle1)
- **Agent-based:** identify yourself with an agent name (`/connect?agent=jc1`)
- **Rooms:** scoped access to Plato shells
- **No API key** — trust-by-identity on the fleet network

### Edge (JC1)
- **Local-only by default:** `--host 127.0.0.1` (no auth when local)
- **Optional API key:** `--api-key secret` for public exposure
- **Constant-time comparison** — no timing side-channels
- **Best practice:** use Tailscale tailnet for remote access (no public ports)

---

## Architecture: When to Use What

```
┌─────────────────────────────────────────────────────────────────┐
│                    DECISION TREE                                │
│                                                                 │
│   Need a quick answer?                                           │
│   ├── Yes → Edge (JC1, localhost:11435)                         │
│   │         Fast, free, CPU-only, ~17 t/s                       │
│   │         Best for: chat, RAG, simple tasks                   │
│   │                                                             │
│   └── Need a big model?                                         │
│       ├── Yes → cocapn.ai (cloud)                               │
│       │         DeepSeek, Claude, GPT-4o, Gemini, Llama          │
│       │         Best for: complex reasoning, code, analysis      │
│       │                                                         │
│       └── Need orchestration?                                   │
│           └── Yes → Plato (Oracle1, 147.224.38.131:8848)        │
│                    Fleet coordination, synthesis, persistence    │
└─────────────────────────────────────────────────────────────────┘
```

### Summary

| Where | When | Why |
|-------|------|-----|
| **Edge (JC1)** | Prototyping, local dev, latency-sensitive tasks | Free, fast, works offline |
| **cocapn.ai** | Production, complex models, client work | 8 models, 1 API, smart routing |
| **Plato (Oracle1)** | Fleet orchestration, synthesis, persistence | Cloud brain, big context |

---

## Port Map

| Port | Service | Node | Access |
|------|---------|------|--------|
| 8848 | Plato Shell | Oracle1 (cloud) | `147.224.38.131:8848` |
| 11434 | Ollama | JC1 (edge) | `localhost:11434` |
| 11435 | Edge Gateway | JC1 (edge) | `localhost:11435` |
| 8081 | Chat UI | JC1 (edge) | `localhost:8081` |
| 8082 | Dashboard | JC1 (edge) | `localhost:8082` |
| 8083 | Fleet Badge | JC1 (edge) | `localhost:8083` |
| 80/443 | cocapn.ai | Cloudflare | `https://cocapn.ai` |

---

*See also: [FLEET.md](../FLEET.md) for the full fleet onboarding guide.*
