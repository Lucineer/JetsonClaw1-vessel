---
id: cocapn-product-ecosystem
created: 2026-04-30
updated: 2026-04-30
tags: ['cocapn', 'product', 'sdk', 'api', 'ecosystem', 'fleet']
---
# Cocapn Product Ecosystem

## Edge Services (JC1)
| Service | Port | Purpose | Status |
|---------|------|---------|--------|
| Edge Gateway | 11435 | OpenAI-compatible API | ✅ |
| Chat UI | 8081 | Web chat | ✅ |
| Dashboard | 8082 | Monitoring | ✅ |
| Fleet Badge | 8083 | Embeddable health | ✅ |
| Ollama | 11434 | LLM runtime | ✅ |

## SDK Packages
- Node.js: cocapn@1.0.0 on npm
- Python: cocapn on PyPI (v0.2.0)
- Go: cocapn-go module

## Cloud (Oracle1)
- Plato shell at 147.224.38.131:8848
- Fleet synthesis every 30min
- 12,000+ tiles, 39 rooms, 24 agents

## Onboarding Flow
1. Visit cocapn.ai or pip/npm install
2. Connect to edge gateway or cloud shell
3. Run `cocapn fleet` to see the mesh
4. Add more edge devices, they auto-join

## CLIs
- `cocapn` Python CLI at tools/cocapn-cli.py
- Gateway: REST at :11435/v1/*

## Known Issues (Kimi Audit)
- pip install plato installs wrong package
- Doc URLs need updating
- PyPI version mismatches

## References
- tiles/cocapn-architecture.md
- tiles/fleet-mesh-architecture.md
