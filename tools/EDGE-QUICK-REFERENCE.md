# Jetson Edge AI Toolkit — Quick Reference

**Platform:** Jetson Orin Nano 8GB (ARM64, CUDA 12.6)
**Services:** 3 systemd units, auto-start on boot
**Models:** 7 local Ollama models

---

## Services

| Service | Port | Purpose | Status |
|---------|------|---------|--------|
| `ollama` | 11434 | Local LLM runtime (0.18.2) | Running |
| `edge-gateway` | 11435 | OpenAI-compatible API (model router) | Running |
| `edge-chat` | 8081 | Web chat UI | Running |
| `edge-monitor-web` | 8082 | Live dashboard | Running |

### Service files
All in `/home/lucineer/.config/systemd/user/` and mirrored in `tools/edge/systemd/`

### Management
```bash
# Status
systemctl --user status edge-gateway
systemctl --user status edge-chat
systemctl --user status edge-monitor-web

# Logs (systemd journal)
journalctl --user -u edge-gateway -f

# Restart
systemctl --user restart edge-gateway
```

---

## API Reference

### Gateway: `http://localhost:11435`

**Model routing** — use common names, gateway maps to best local model:
| Requested Model | Routes To | Notes |
|----------------|-----------|-------|
| `gpt-3.5-turbo` | `deepseek-r1:1.5b` | Fast, 17 t/s |
| `gpt-4o-mini` | `phi3:mini` | 3.8B params, 2.2GB |
| `gpt-4o` | `qwen3.5:2b` | 2.3B params, 2.7GB |
| `claude-3-haiku` | `deepseek-r1:1.5b` | Fast |
| `claude-3-sonnet` | `phi3:mini` | |
| `llama-3-8b` | `deepseek-r1:1.5b` | ⚠️ 8B+ OOM risk |
| `default` | `deepseek-r1:1.5b` | |

### Endpoints

```bash
# List models
curl http://localhost:11435/v1/models

# Chat (OpenAI-compatible)
curl -X POST http://localhost:11435/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-3.5-turbo","messages":[{"role":"user","content":"Hello"}],"stream":false}'

# Streaming
curl -X POST http://localhost:11435/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-r1:1.5b","messages":[{"role":"user","content":"Count to 5"}],"stream":true}'

# Embeddings (nomic-embed-text)
curl -X POST http://localhost:11435/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{"model":"nomic-embed-text","input":"Hello world"}'

# Conversations
curl http://localhost:11435/v1/conversations
curl -X POST http://localhost:11435/v1/conversations \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-r1:1.5b","title":"My Conversation"}'

# Usage stats
curl http://localhost:11435/v1/usage
```

### Dashboard: `http://localhost:8082`

| Endpoint | Returns |
|----------|---------|
| `/` | HTML dashboard (auto-refresh 5s) |
| `/api/system` | CPU/GPU temp, RAM, CMA, swap |
| `/api/gateway` | Gateway usage stats |
| `/api/models` | Available models |
| `/api/conversations` | Conversation history |
| `/api/processes` | Running edge services |

### Chat UI: `http://localhost:8081`

Single-page HTML chat app. Streams responses. Dark theme.

---

## Hardware Constraints

- **256MB CMA** — insufficient for GPU model offloading (all inference is CPU-only)
- **8GB unified RAM** — ~3.6GB free for models
- DeepSeek-r1:1.5b works well (~17 t/s CPU)
- 4B+ models OOM during generation (need ~4.4GB)
- **Fix requires sudo**: increase `cma=2G` in kernel cmdline

---

## File Layout

```
tools/
├── edge-gateway.py           # OpenAI-compatible API gateway
├── edge-chat.py              # Web chat UI
├── edge-monitor-web.py       # Monitoring dashboard
├── edge-rag.py               # RAG pipeline (nomic-embed-text)
├── edge-setup.py             # Hardware detection wizard
├── jetson-monitor.py         # CLI system monitor
├── gpu-bench.py              # GPU benchmark suite
├── tensorrt-bench.py         # TensorRT benchmark
├── fleet-sync.py             # Fleet bottle sync
├── fleet-health.py           # Fleet health monitoring
├── plato-cron.py             # Scheduled task runner
├── skill-tree.py             # Agent skill management
├── tile-graph.py             # Graph knowledge index
├── cocapn-health.py          # Product health monitor
├── cocapn-test.py            # Integration tests
├── pyproject.toml            # Package config (jetson-edge-ai)
├── GATEWAY-README.md          # Product documentation
├── README.md                  # Tool overview
├── edge/
│   ├── __init__.py
│   ├── config.py             # Shared configuration
│   ├── ollama_client.py      # Ollama API client
│   ├── monitoring.py         # System monitoring
│   ├── storage.py            # SQLite storage
│   ├── similarity.py         # Vector similarity
│   ├── edge-router.py        # Model routing logic
│   └── systemd/             # Service files
│       ├── edge-gateway.service
│       ├── edge-chat.service
│       └── edge-monitor-web.service
└── tests/
```

---

## Fleet Integration

- **Workspace**: `git@github.com:Lucineer/JetsonClaw1-vessel.git` (SSH auth)
- **Edge tools mirror**: `git@github.com:Lucineer/edge-tools.git`
- **Bottles**: `/tmp/forgemaster/for-fleet/BOTTLE-FROM-JC1-*`
- **FM relay**: `https://github.com/Lucineer/forgemaster`
- **Oracle1**: Port 8848 (PLATO Shell), port 6168 (Matrix bridge — JC1 not registered)
