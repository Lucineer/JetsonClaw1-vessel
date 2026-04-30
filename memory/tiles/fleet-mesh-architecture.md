---
id: fleet-mesh-architecture
created: 2026-04-30
updated: 2026-04-30
tags: ['fleet', 'architecture', 'onboarding', 'oracle1', 'edge', 'cocapn']
---
# Fleet Mesh Architecture

## Architecture
```
    Oracle1 (Cloud Plato) — 147.224.38.131:8848
         │  Big models, orchestration, persistence
    ─────┼────────────────────────────────────
    JC1 (Jetson Orin Nano)
    ├── :11435  Edge Gateway   OpenAI-compatible API
    ├── :8081   Chat UI         Web chat interface
    ├── :8082   Dashboard       Live monitoring
    ├── :8083   Fleet Badge     Embeddable health badge
    └── :11434  Ollama          Local LLM runtime
```

## Entry Points
| Entry | URL/Command | What You Get |
|-------|-------------|--------------|
| Cloud (Oracle1) | 147.224.38.131:8848 | Plato shell, big models, synthesis |
| Edge (JC1) | localhost:11435 | Local inference, 7 CPU models |
| PyPI | pip install cocapn | Python SDK |
| NPM | npm install cocapn | Node.js SDK |

## Fleet Health
- /v1/fleet probes Oracle1 + JC1
- Fleet badge at :8083, auto-refresh 10s
- 2/2 nodes up
- CLI: cocapn fleet, cocapn status

## CLI Tools
- `cocapn status` — system + fleet health
- `cocapn models` — available models
- `cocapn fleet` — node status
- `cocapn chat` — local inference

## References
- tiles/cocapn-product-ecosystem.md
- tiles/cocapn-architecture.md
