# Model Effectiveness Notes — 2026-04-03

## Live Tracking: What Works Best For What

### DeepSeek-Reasoner (deepseek.com, flagship)
- **BEST for**: Creative vision, novel concepts, final synthesis, philosophical framing
- **NOT GOOD for**: Factual grounding (hallucinated a repo man story mid-forum)
- **COST**: Most expensive per token but highest novelty-per-token
- **LATENCY**: ~30-90s response time
- **KEY INSIGHT**: Produces genuinely unique concepts (Pacing Autopilot, Belief Economy, Fleet Commons, Context Pods)
- **WATCH**: Can go off-rail on continuation prompts — keep prompts focused

### DeepSeek-Chat (deepseek.com, cheap bulk)
- **BEST for**: Factual lists, grounded analysis, year-by-year timelines, pragmatic synthesis
- **NOT GOOD for**: Creative writing, continuation (hallucinated fantasy story on choice 5)
- **COST**: Cheapest option, great for bulk work
- **LATENCY**: ~10-20s
- **KEY INSIGHT**: Excellent at structured analysis (5 choices, 3 decisions) but unreliable on open-ended continuation
- **WATCH**: Loses context on follow-up prompts — treat each call as independent

### Qwen3-Coder-480B (SiliconFlow)
- **BEST for**: Architectural challenges, identifying gaps, infrastructure analysis
- **NOT GOOD for**: Creative writing, narrative (produces sterile technical prose)
- **COST**: Mid-range, MoE efficiency
- **LATENCY**: ~30-60s
- **KEY INSIGHT**: The "challenger" model — always finds what others miss (shadow economies, infrastructure gaps)
- **WATCH**: SiliconFlow timeout on prompts >300 chars — keep focused

### Ring-flash-2.0 (SiliconFlow)
- **BEST for**: Narrative, emotional scenes, making abstract concepts visceral
- **NOT GOOD for**: Analysis, lists, structured output
- **COST**: Mid-range
- **LATENCY**: ~30-60s
- **KEY INSIGHT**: "Can I leave the porch light on all night?" — unmatched emotional precision
- **WATCH**: Thinking model — timeout on long prompts

### GLM-5-Turbo (z.ai, subagent default)
- **BEST for**: Subagent code generation, parallel task execution, tool-heavy work
- **NOT GOOD for**: Creative insight, novel concept generation
- **COST**: Good for parallel work
- **LATENCY**: Fast
- **KEY INSIGHT**: Reliable workhorse for execution, not inspiration

### GLM-5.1 (z.ai, complex reasoning)
- **BEST for**: Complex architecture decisions, deep planning
- **NOT GOOD for**: Bulk work (use GLM-5-turbo instead)
- **COST**: Use sparingly
- **KEY INSIGHT**: Reserve for architecture-level decisions

## Forum Format Effectiveness
- 4-model chain (Visionary→Architect→Pragmatist→Storyteller) produces 3-5x richer output than single model
- Each model catches others' blind spots
- Chain order matters: creative first, critical second, grounded third, emotional last
- Backward chain benefits from model rotation (prevents echo chamber)

## Multi-Model Synthesis Quality by Task
| Task | Best Model | Second Best | Avoid |
|------|-----------|-------------|-------|
| Novel concepts | DeepSeek-Reasoner | Ring-flash | DeepSeek-Chat |
| Infrastructure gaps | Qwen3-Coder | GLM-5.1 | Ring-flash |
| Timeline/roadmap | DeepSeek-Chat | Qwen3-Coder | DeepSeek-Reasoner |
| Emotional scenes | Ring-flash | DeepSeek-Reasoner | Qwen3-Coder |
| Code generation | GLM-5-turbo | Qwen3-Coder | Ring-flash |
| Final synthesis | DeepSeek-Reasoner | GLM-5.1 | DeepSeek-Chat |
| Challenge/debate | Qwen3-Coder | DeepSeek-Reasoner | DeepSeek-Chat |

## Observations
- DeepSeek models have **no cross-call memory** — each request is fresh, continuation prompts unreliable
- SiliconFlow models need **short focused prompts** (<300 chars thinking, <200 chars MiniMax)
- The **forum format itself** is the real innovation — the crystallization graph feeds on multi-model disagreement
- **Model routing for Cocapn fleet**: DeepSeek-Reasoner for vision, Qwen3-Coder for architecture, DeepSeek-Chat for grounding, Ring-flash for user-facing narrative
