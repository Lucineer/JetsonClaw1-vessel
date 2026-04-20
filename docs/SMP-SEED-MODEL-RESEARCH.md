# SMP & Seed-Model-Programs Research

## 1. Overview

Research into SuperInstance's SMP (Seed + Model + Prompt) architecture and how seed-model-programs can accelerate repo-agent prototyping in the Cocapn ecosystem.

## 2. Key Papers Reviewed

### 2.1 SMPbot Architecture (Paper 05)

**Core Formula:** Seed + Model + Prompt = Stable Output

An SMPbot is a 5-tuple B = (S, M, P, φ, σ) where:
- **Seed** (S): Domain knowledge container — versioned, immutable, schema-enforced
- **Model** (M): AI engine with shared loading (GPU memory pooled across bots)
- **Prompt** (P): Task specification with constraints, context, and examples
- **φ**: Inference function
- **σ**: Stability function (measures output variance over time)

**Key properties:**
- Seeds are immutable and versioned with cryptographic hashes
- Models load once and serve multiple SMPbots (GPU memory sharing)
- Prompts are constrained task specs, not free-form instructions
- Composition theorems guarantee stability degrades predictably

**Composition rules:**
- Sequential: σ(B₂ ∘ B₁) ≥ min(σ(B₁), σ(B₂)) - κ
- Parallel: weighted average of stability scores
- Conditional: probabilistic mix based on predicate

### 2.2 Confidence Cascade Architecture (Paper 03)

Three-zone confidence system:
- **GREEN** (95%+): Full autonomous operation
- **YELLOW** (75-95%): Semi-autonomous with human oversight
- **RED** (<75%): Defensive operation, human-in-the-loop

Introduces **deadband triggers** (hysteresis) to prevent oscillatory recomputation. Small confidence fluctuations within acceptable bounds don't trigger cascades.

### 2.3 Universal Cell Architecture (Paper 01)

Every cell in a SuperInstance spreadsheet can be any computational type: data, process, agent, storage, API, terminal, reference, or nested SuperInstance. Uses rate-based change mechanics for state tracking.

## 3. Seed-Model-Programs in Repo-Agent Context

### 3.1 What They Are

A seed-model-program is a pre-composed SMPbot that serves as a starting point for a specific application domain. Think of it as a "starter template" but at the AI behavior level, not just the code level.

```
Seed (domain knowledge) + Model (LLM choice) + Prompt (task template)
  → A working agent that understands your domain
```

### 3.2 How a Repo-Agent Uses Them

**Rapid prototyping flow:**

1. Agent identifies the application type (dashboard, chatbot, workflow, etc.)
2. Selects or composes a seed-model-program matching that type
3. The seed provides immediate domain context — the agent "knows" what a sales dashboard should look like without being told
4. The prompt template structures interactions correctly
5. The model choice determines slop tolerance (see Soft Actualization concept doc)

**Example — spinning up a fishing log agent:**
```
Seed: fishing-vessel-data (species taxonomy, catch patterns, regulations)
Model: GLM-5 (high slop tolerance for complex classification)
Prompt: "You are a vessel AI assistant. Classify species from camera input.
         Track catches. Alert on quota limits. Suggest fishing patterns."
  → Instant working agent, no code needed
```

### 3.3 The Backend-Frontend Separation

Seed-model-programs create a natural split:

**Backend (seed + model):**
- Domain knowledge (seed) is relatively stable
- Model optimization (quantization, fine-tuning) improves incrementally
- Backend hardening is a slow, careful process
- Each improvement benefits all frontends using that seed

**Frontend (prompt + UI):**
- UI prototypes iterate rapidly
- Prompt templates are tweaked per deployment
- Different users/companies customize the prompt while sharing the seed
- Soft Actualization applies here — the frontend simulates features while the backend catches up

This means: **the backend keeps getting better optimized while the frontend prototype iterates.** They're decoupled by the SMP architecture.

### 3.4 Concrete Cocapn Integration

```
cocapn/
├── soul.md              # The prompt component (who the agent is)
├── memory/              # Accumulated seed data (the living seed)
│   ├── facts.json       # Static facts (seed)
│   ├── memories.json    # Experiential data (growing seed)
│   └── procedures.json  # Learned workflows (hardened prompt patterns)
├── wiki/                # Structured knowledge base (formalized seed)
├── skills/              # Reusable prompt templates (SMP compositions)
└── agents/              # Sub-agents, each an SMPbot instance
```

The cocapn repo is literally an SMPbot: the repo structure maps 1:1 to Seed (memory/wiki) + Model (BYOK LLM) + Prompt (soul.md/skills).

## 4. Repos Found at SuperInstance

| Repo | Relevance |
|---|---|
| **cocapn** | Core repo-agent framework. The primary target for integration. |
| **SuperInstance-papers** | White papers including SMPbot, Confidence Cascade, Universal Cell. |
| **Edge-Native** | Edge IoT deployment — relevant for Jetson/local agent scenarios. |
| **personallog.ai** | Personal AI agent in a repo — practical cocapn deployment. |
| **fishinglog.ai** | Edge AI fishing vessel — cocapn in production with vision + voice. |
| **Constraint-Theory (ecosystem)** | 7 repos for geometric constraint solving. Core math for rate-based change. |
| **I-know-kung-fu** | Skill injection framework — maps to cocapn skills/ directory. |

No dedicated "SMP" or "seed-model-programs" repo exists yet — the concept lives in the papers and implicitly in cocapn's architecture.

## 5. Key Takeaways

1. **Cocapn is already an SMP system** — it just doesn't formalize it. Making this explicit would unlock composition guarantees from the SMPbot paper.

2. **Seed-model-programs as a product concept**: A registry of pre-built seeds (domain knowledge packs) that cocapn repos can import. Like npm packages but for AI domain context.

3. **Confidence cascades enable safe Soft Actualization**: RED-zone gaps trigger human review instead of silent simulation. This is the safety rail.

4. **The backend-frontend split is natural in SMP**: Seeds are shared backends. Prompts are per-deployment frontends. This is the right architecture for cocapn's "private brain + public face" model.

---

*Research conducted April 2026. Sources: SuperInstance-papers white-papers 01, 03, 05, 06.*
