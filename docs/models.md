# Models Configuration

## DeepInfra
- **API Key:** `jfCang5GUEkcHktx6xPTysstl9oIyIP7` (saved to openclaw.json)
- **Base URL:** https://api.deepinfra.com/v1/openai
- **Models:** Seed-2.0 family for perspective diversity
- **Use:** Secondary reasoning perspective alongside DeepSeek and z.ai/GLM

### Seed Family (ByteDance)
| Model | Vibe | Verified |
|-------|------|----------|
| ByteDance/Seed-2.0-mini | Cheap, creative, flexible | ✅ Working |
| ByteDance/Seed-2.0-code | Codding, IDE tooling | ⚠️ Not responding |
| ByteDance/Seed-2.0-pro | Complex reasoning, agent tasks | ❓ Not tested |

**Usage pattern:** When DeepSeek gives one answer and glm-5 gives another, Seed-2.0-mini provides a third perspective. Iterate across viewpoints.

## DeepSeek
- **API Key:** `sk-9814f15d518e4a6f804c6f369273c8c7`
- **Default model (v4-flash):** deepseek/deepseek-chat
- **Reasoning (v4-pro):** deepseek/deepseek-reasoner

## z.ai / GLM (free tier)
- **Model:** zai/glm-5.1 or zai/glm-5-turbo
- **Use:** First-try for reasoning (before DeepSeek pro)
- **Note:** Rate-limited when Oracle1 also hits it

## Available Models
### Ollama (local, CPU-only currently)
- deepseek-r1:1.5b
- phi3:mini  
- qwen3.5:2b
- Qwen3.5-4B
- nomic-embed-text
- moondream
- nemotron-3-nano:4b

### Edge Gateway
- All Ollama models + routing to Oracle1
- Endpoint: localhost:11435/v1/chat/completions

### Oracle1 (cloud Plato)
- Big models via Evennia shell
- Endpoint: 147.224.38.131:8848
