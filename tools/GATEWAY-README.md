# Edge AI Gateway — Jetson Orin Nano

A production-grade, OpenAI-compatible API gateway that runs **entirely on-device** via Ollama on a Jetson Orin Nano 8GB. Features **smart model routing** (cloud model names → local models), **streaming**, **RAG**, **conversation persistence**, and a **rich status dashboard**.

```
GET  /                        — Status dashboard
POST /v1/chat/completions     — Chat with smart routing + streaming
POST /v1/embeddings           — Embeddings
POST /v1/rag/query            — RAG search + generate
GET  /v1/models               — List available models
GET  /v1/stats                — System stats (GPU, RAM, CMA)
GET  /v1/health               — Health check
GET  /v1/usage                — Usage statistics
GET  /v1/conversations        — Conversation management (CRUD)
```

---

## Quickstart

```bash
# Start the gateway (port 11435, binds 127.0.0.1)
python3 edge-gateway.py

# With API key authentication
python3 edge-gateway.py --api-key your-secret-key

# Custom port / bind address
python3 edge-gateway.py --port 8080 --host 0.0.0.0
```

### Test with curl

```bash
# Check status (HTML in browser, JSON with curl)
curl http://localhost:11435/

# List models
curl http://localhost:11435/v1/models

# Chat completion (non-streaming)
curl -X POST http://localhost:11435/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-3.5-turbo","messages":[{"role":"user","content":"Say OK in one word"}],"stream":false}'

# Chat completion (streaming)
curl -X POST http://localhost:11435/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4o","messages":[{"role":"user","content":"Count to 5"}],"stream":true}'

# Health check
curl http://localhost:11435/v1/health

# System stats
curl http://localhost:11435/v1/stats

# Usage stats
curl http://localhost:11435/v1/usage
```

### Test with OpenAI Python SDK

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11435/v1",
    api_key="local",  # any non-empty string works if no --api-key set
)

# Chat — use any model name, routing happens automatically
resp = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello!"}],
)
print(resp.choices[0].message.content)

# Streaming
stream = client.chat.completions.create(
    model="claude-3-sonnet",
    messages=[{"role": "user", "content": "Count to 5"}],
    stream=True,
)
for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)

# Embeddings
resp = client.embeddings.create(
    model="text-embedding-3-small",
    input="Hello world",
)
print(resp.data[0].embedding[:5])
```

---

## Smart Model Routing

The gateway transparently maps cloud/high-end model names to the best available local model on your Jetson. This lets you use standard SDKs and configs without modification.

### Routing Table

| Requested Model | Routed To | Size | Notes |
|---|---|---|---|
| `gpt-3.5-turbo` | `deepseek-r1:1.5b` | 1.1 GB | Fast, general chat |
| `gpt-4o-mini` | `phi3:mini` | 2.2 GB | Balanced reasoning |
| `gpt-4o` | `qwen3.5:2b` | 2.7 GB | Creative/coding |
| `gpt-4` / `gpt-4-turbo` | `deepseek-r1:1.5b` | 1.1 GB | Both fast options |
| `claude-3-haiku` | `deepseek-r1:1.5b` | 1.1 GB | Quick responses |
| `claude-3-sonnet` | `phi3:mini` | 2.2 GB | More depth |
| `claude-3-opus` | `deepseek-r1:1.5b` | 1.1 GB | Best available for complex |
| `claude-4-opus` | `deepseek-r1:1.5b` | 1.1 GB | — |
| `llama-3-8b` | `deepseek-r1:1.5b` | 1.1 GB | ⚠️ 8B OOM warning |
| `llama-3.2-3b` | `phi3:mini` | 2.2 GB | — |
| `gemini-1.5-pro` | `phi3:mini` | 2.2 GB | — |
| `gemini-2.0-flash` | `deepseek-r1:1.5b` | 1.1 GB | — |
| `mistral-small` | `phi3:mini` | 2.2 GB | — |
| `mixtral-8x7b` | `deepseek-r1:1.5b` | 1.1 GB | ⚠️ 8×7B OOM warning |
| `phi-3-mini` through `phi-4` | `phi3:mini` | 2.2 GB | — |
| `nemotron-4-340b` | `nemotron-3-nano:4b` | 2.8 GB | — |
| `moondream` | `moondream:latest` | 1.7 GB | Vision |
| `text-embedding-3-small/large` | `nomic-embed-text` | 0.3 GB | Embeddings |
| `default` / unknown | `deepseek-r1:1.5b` | 1.1 GB | Safe fallback |

### How Routing Works

1. **Exact match** — if the model name exists locally, use it directly
2. **Routing table** — cloud model names → mapped local model
3. **Too large?** — models estimated >3.0 GB return a clear error with suggestions (e.g., "llama-3-70b" → OOM error)
4. **Fallback** — unknown models default to `deepseek-r1:1.5b`

### Example: OOM Error

```json
{
  "error": {
    "message": "Model 'llama-3-70b' (est. 38.5GB) is too large for this 8GB Jetson with only 256MB CMA. CPU-only inference cannot load models >3.0GB. Suggestions: phi3:mini (balanced reasoning, 2.2GB, 3.8B params); qwen3.5:2b (creative/coding, 2.7GB, 2.3B params)",
    "type": "model_too_large",
    "suggested_models": ["deepseek-r1:1.5b", "phi3:mini", "qwen3.5:2b"]
  }
}
```

---

## Platform-Specific Notes

### Jetson Orin Nano 8GB

| Resource | Value |
|---|---|
| RAM | 8 GB (shared CPU+GPU) |
| CMA | 256 MB (non-configurable without sudo) |
| GPU offloading | ❌ Not possible (CMA bottleneck) |
| CPU threads | 6 (set via `num_thread`) |
| Flash attention | ✅ Enabled (`OLLAMA_FLASH_ATTENTION=1`) |

**Key implications:**
- All models run **CPU-only** (no GPU layers). Expect ~17 t/s on `deepseek-r1:1.5b`.
- Models larger than ~3 GB risk OOM (kernel OOM killer terminates Ollama).
- The gateway auto-sets `num_thread=6`, `num_predict=2048`, `temperature=0.7` as defaults.

### Supported Devices
The gateway uses generic Linux sysfs interfaces (`/sys/class/thermal`, `/proc/meminfo`) so it works on any Linux system. Jetson-specific CMA stats appear when available.

---

## API Reference

### `GET /` — Status Dashboard

Returns a rich HTML page (browsers) or JSON (with `Accept: application/json`).

```bash
curl -H "Accept: application/json" http://localhost:11435/
```

### `POST /v1/chat/completions` — Chat

**Request body:**

| Field | Type | Default | Description |
|---|---|---|---|
| `model` | string | `deepseek-r1:1.5b` | Model name (routed automatically) |
| `messages` | array | required | OpenAI-format message list |
| `stream` | boolean | `false` | Stream SSE tokens |
| `temperature` | float | `0.7` | Override temperature |
| `options` | object | `{}` | Ollama options overrides |
| `conversation_id` | string | — | Auto-save to existing conversation |

**Response** (non-streaming):
```json
{
  "id": "chatcmpl-1712345678000",
  "object": "chat.completion",
  "created": 1712345678,
  "model": "gpt-3.5-turbo",
  "routed_to": "deepseek-r1:1.5b",
  "choices": [{
    "index": 0,
    "message": {"role": "assistant", "content": "OK"},
    "finish_reason": "stop"
  }],
  "usage": {"prompt_tokens": 20, "completion_tokens": 1, "total_tokens": 21}
}
```

**Streaming**: Returns `text/event-stream` with OpenAI-format SSE chunks, ending with `data: [DONE]`.

### `POST /v1/embeddings` — Embeddings

| Field | Type | Default | Description |
|---|---|---|---|
| `model` | string | `nomic-embed-text` | Embedding model |
| `input` | string or array | required | Text(s) to embed |

### `POST /v1/rag/query` — RAG

| Field | Type | Default | Description |
|---|---|---|---|
| `query` | string | required | Search query |
| `model` | string | `deepseek-r1:1.5b` | Generation model |
| `index` | string | `fleet-knowledge` | RAG index name |
| `top_k` | integer | 5 | Number of chunks to retrieve |

### `GET /v1/health` — Health Check

```json
{
  "status": "ok",
  "ollama": "connected",
  "device": "Jetson Orin Nano 8GB",
  "version": "1.1.0"
}
```

### `GET /v1/stats` — System Stats

Returns GPU/CPU temperatures, RAM, CMA, usage, and model list.

### `GET /v1/models` — List Models

Returns all Ollama-hosted models with sizes.

### `GET /v1/usage` — Usage Statistics

SQLite-backed aggregation of all API calls, token counts, and errors.

### `GET /v1/conversations` — Conversations

List, create, read, and delete persistent conversations. Messages are auto-saved when `conversation_id` is passed to `/v1/chat/completions`.

---

## Deployment

### As a systemd service (requires sudo)

```ini
[Unit]
Description=Edge AI Gateway
After=network.target ollama.service

[Service]
Type=simple
User=lucineer
ExecStart=/usr/bin/python3 /home/lucineer/.openclaw/workspace/tools/edge-gateway.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### As a background process

```bash
nohup python3 edge-gateway.py > /tmp/edge-gateway.log 2>&1 &
```

### With API key for public exposure

```bash
python3 edge-gateway.py --host 0.0.0.0 --api-key "$(cat /run/secrets/gateway-key)"
```

> ⚠️ **Security**: The gateway uses constant-time API key comparison. For production use behind Tailscale or a VPN, keep `--host 127.0.0.1`.

---

## Troubleshooting

### Ollama not available
```
⚠️  Ollama not available: Connection failed: [Errno 111] Connection refused
```
→ Start Ollama: `ollama serve`

### Out of Memory (OOM)
```
Model 'llama-3-70b' is too large for this 8GB Jetson...
```
→ Use a smaller model: `deepseek-r1:1.5b`, `phi3:mini`, or `qwen3.5:2b`
→ Check available free RAM: `free -h`

### CMA depleted
Check `/proc/meminfo` for CmaFree. If near zero, GPU-accelerated apps won't work. The gateway compensates with CPU-only mode.

### Model not found in routing table
Unknown model names are safely routed to `deepseek-r1:1.5b`. Add new mappings in `MODEL_ROUTING_TABLE` in edge-gateway.py.

### Streaming not working
Ensure `stream: true` in the request body. The gateway converts Ollama's NDJSON format to SSE. Check Ollama logs for errors.

### High latency
On CPU-only mode, expect 15–20 t/s on `deepseek-r1:1.5b`. Larger models like `phi3:mini` run at 5–8 t/s. If latency spikes, check thermal throttling with `curl http://localhost:11435/v1/stats`.

---

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌──────────┐
│ Client       │────▶│ Edge Gateway │────▶│ Ollama   │
│ (OpenAI SDK) │     │ port 11435   │     │ port 11434│
│ curl/browser │◀────│ smart router │◀────│ models   │
└─────────────┘     │ streaming    │     └──────────┘
                    │ status page  │
                    │ SQLite store │
                    └──────────────┘
```

The gateway adds:
- **Model routing** — transparent name resolution
- **OOM protection** — prevents crashes from over-large models
- **Streaming** — NDJSON → SSE conversion
- **Persistence** — SQLite-backed conversations and usage logs
- **Monitoring** — real-time system stats via sysfs/proc
- **Auth** — constant-time API key comparison

---

## License

MIT — part of the JetsonClaw1-vessel project.
