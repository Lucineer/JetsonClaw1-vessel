# SiliconFlow Model Capabilities — Experimental Results (2026-04-03)

## Quick Reference Card

| Model | Type | Speed | Token Efficiency | Best For | Avoid |
|-------|------|-------|-----------------|----------|-------|
| **Qwen/Qwen3-Coder-480B-A35B-Instruct** | Non-thinking | Fast ⚡ | **Best** (35% less than DeepSeek) | Code gen, systems architecture, structured analysis | Long creative prose |
| **deepseek-chat** (Direct API) | Non-thinking | Fast ⚡ | **Cheapest** token-for-token | Code, math, reliable workhorse | Creative/speculative tasks |
| **deepseek-reasoner** (Direct API) | Thinking | Medium | 193 reasoning tokens | **Unconventional insights**, counter-culture thinking, anthropological | Quick factual queries |
| **inclusionAI/Ring-flash-2.0** | Thinking | Medium | Medium (801 reasoning tokens) | **Vivid storytelling**, user experience imagination, speculative fiction | Short factual queries |
| **ByteDance-Seed/Seed-OSS-36B-Instruct** | Thinking | Slow 🐢 | High reasoning overhead (1014+) | **Adversarial/security thinking**, deep multi-step reasoning, cybersecurity | Quick answers (overthinks) |
| **MiniMaxAI/MiniMax-M2.5** | Thinking | Slow 🐢 | High reasoning overhead (462+) | **Business pragmatism**, real-world deployment, detail-oriented planning | Complex prompts (times out >300 chars) |
| **moonshotai/Kimi-K2.5** | Thinking | Slow 🐢 | High reasoning overhead (72 for hello!) | **Long context reads**, deep analysis of large documents | Short queries (wastes tokens on reasoning) |
| **moonshotai/Kimi-K2-Instruct-0905** | Non-thinking | Fast ⚡ | Good | Quick questions, concise responses, snappy alternatives to K2.5 | Deep reasoning tasks |
| **zai-org/GLM-5** (SiliconFlow) | Non-thinking | Timeout | N/A | — | ❌ Times out on SiliconFlow (use z.ai endpoint instead) |
| **stepfun-ai/Step-3.5-Flash** | Non-thinking | Timeout | N/A | — | ❌ Empty responses, may need different model ID |
| **baidu/ERNIE-4.5-300B-A47B** | Non-thinking | Timeout | N/A | — | ❌ Empty responses |
| **black-forest-labs/FLUX.2-flex** | Image gen | Medium | N/A | **Image generation** via SiliconFlow Images API | — |

## Routing Rules (Experimental)

### For Code Tasks
1. **Qwen3-Coder-480B** — First choice. 35% fewer tokens, high quality
2. **deepseek-chat** — Reliable fallback
3. **GLM-5-turbo** (z.ai) — For subagent tasks needing orchestration context

### For Creative/Speculative Tasks
1. **Ring-flash-2.0** — Best storyteller, vivid user experience imagination
2. **DeepSeek** — Psychological depth, poetic language
3. **Kimi-K2.5** — When you need to process large context (1M window)

### For Architecture/Planning
1. **Qwen3-Coder-480B** — Systems thinking, structural design
2. **GLM-5.1** (z.ai) — Complex multi-factor decisions (use sparingly)

### For Security/Adversarial
1. **Seed-OSS-36B** — Naturally thinks in attack vectors
2. **DeepSeek** — Dark/contrarian perspectives

### For Business/Deployment
1. **MiniMax-M2.5** — Pragmatic, detail-oriented (keep prompts short)
2. **DeepSeek** — Broader strategic thinking

### For Quick Questions
1. **Kimi-K2-Instruct-0905** — Snappy, no reasoning overhead
2. **Qwen3-Coder-480B** — Fast and efficient
3. **deepseek-chat** — Always reliable

### For Image Generation (all via `/v1/images/generations`)
1. **FLUX.1-schnell** — **Best for logos/icons**. Fastest (~12s), most precise, clean output. **Almost free** — cheapest option.
2. **Z-Image-Turbo** — **Fastest** (~8s). Good for abstract concepts. Note: different response format (`images` array + `timings` field). Extremely cheap.
3. **FLUX.2-flex** — **Best for artistic/creative**. More expressive, less precise. ~14s.

## Known Issues
- **Thinking models (Ring, Seed, MiniMax, Kimi K2.5)** timeout on prompts >300 chars on SiliconFlow — keep prompts focused
- **GLM-5 on SiliconFlow** times out — use z.ai endpoint instead
- **Step-3.5-Flash** returns empty responses — model ID may be wrong
- **ERNIE-4.5** returns empty — may need Chinese-language prompts or different config
- **MiniMax-M2.5** most sensitive to prompt length — keep under 200 chars for reliable results
- **Kimi K2.5** has massive reasoning overhead even for simple queries — use K2-Instruct for short tasks

## Token Cost Comparison (Same LRU Cache Task)
| Model | Total Tokens | Reasoning Tokens | Effective Output |
|-------|-------------|-----------------|-----------------|
| Qwen3-Coder-480B | **205** | 0 | 205 (100%) |
| DeepSeek-chat | 320 | 0 | 320 (100%) |
| Kimi K2-Instruct | 39 | 0 | 39 (100%) |
| Ring-flash-2.0 | 75 | 60 | 15 (20%) |
| Seed-OSS-36B | 81 | 51 | 30 (37%) |
| MiniMax-M2.5 | 223 | 170 | 53 (24%) |
| Kimi K2.5 | 92 | 72 | 20 (22%) |

→ Non-thinking models deliver 3-5x more output per token for straightforward tasks
→ Thinking models worth the overhead ONLY for complex reasoning, security analysis, or creative speculation

## Dynamic Routing Logic (To Implement)
```
IF task == "code" → Qwen3-Coder-480B
IF task == "quick_q" → Kimi-K2-Instruct
IF task == "creative_vision" → Ring-flash-2.0
IF task == "security" → Seed-OSS-36B
IF task == "business" AND prompt_length < 200 → MiniMax-M2.5
IF task == "long_context" → Kimi-K2.5
IF task == "reliable" OR model_failed → deepseek-chat
IF task == "complex_planning" → GLM-5.1 (z.ai)
IF task == "subagent" → GLM-5-turbo (z.ai)
IF task == "image" → FLUX.2-flex
```
