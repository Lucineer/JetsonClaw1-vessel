# Three-Tool Setup for Cocapn
## Aider + Open-Interpreter + Goose

### 1. Aider (SiliconFlow Qwen3-Coder-480B)
**Purpose:** Heavy code generation, refactoring, large-scale changes
**Config:** ~/.aider.conf.yml
**Model:** Qwen/Qwen3-Coder-480B-A35B-Instruct
**Use when:** Need to rewrite entire modules, generate comprehensive tests, handle complex refactors

### 2. Open-Interpreter (DeepSeek-chat)
**Purpose:** General coding tasks, exploration, debugging, shell operations
**Config:** ~/.open-interpreter/config.yaml  
**Model:** deepseek/deepseek-chat
**Use when:** Need to explore codebase, run commands, debug issues, quick prototypes

### 3. Goose (z.ai GLM-5-turbo)
**Purpose:** Pragmatic coding, explanations, step-by-step reasoning
**Model:** glm-5-turbo
**Use when:** Need clear explanations, thoughtful analysis, architectural decisions

### Workflow:
1. **Bird's-eye view with Casey** — discuss strategy, priorities, fleet coordination
2. **Dispatch to appropriate tool** based on task type:
   - Heavy code gen → Aider (SiliconFlow)
   - General exploration → Open-Interpreter (DeepSeek)  
   - Analysis/explanation → Goose (GLM-5-turbo)
3. **Review results** at protocol level
4. **Integrate into fleet** via appropriate vessels

### Example commands:
```bash
# Aider for heavy code
aider --message "Refactor the fleet orchestrator to include circuit quarantine"

# Open-Interpreter for exploration  
interpreter "Find all vessels with health issues and show their last 10 logs"

# Goose for analysis
goose "Explain the tradeoffs between deterministic execution bonds vs causal event horizon"
```

### Key Insight:
Three different "lenses" with three different models from three different providers (SiliconFlow, DeepSeek, z.ai). This gives:
- **Diversity of thought** — different model architectures produce different solutions
- **Specialization** — each model has strengths
- **Redundancy** — if one API is down, others work
- **Abstraction** — I can work at higher level while tools handle implementation

Now I can be more bird's-eye with Casey as his Cocapn — focusing on fleet strategy, protocol design, and coordination while the tools handle the weeds.
