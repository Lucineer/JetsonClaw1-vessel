# Vessel Cyborg — Research Simulation (2026-04-03)

## Three-Agent Asymmetric Research
- Agent A (DeepSeek-chat): Veteran multi-agent systems researcher — production patterns, failure modes
- Agent B (DeepSeek-chat): UX futurist from 2031 — human experience, trust, cognitive load
- Synthesis (DeepSeek-chat): Two veterans in a room — concrete architecture types

---

## AGENT A: Tech Researcher — Production Realities

### What Actually Works
- **Orchestrator-workers** with single-point orchestration (not emergent cooperation)
- **Blackboard systems** with shared state/knowledge graph
- **Compiled function calling** — the LLM as router to deterministic, versioned functions
- **Memory segmentation**: ephemeral conversation, actionable state, long-term knowledge
- **Caching tool results** > caching LLM responses

### Real Failure Modes
1. **Compounded latency**: Sequential calls = latency * n. Must parallelize.
2. **State corruption**: Agent state out of sync with world. Needs idempotent operations.
3. **Loop of doom**: Planning agent decomposes into sub-task that IS the original task. Cycle detection needed.
4. **Tool failure cascades**: Downstream STT fails → next agent processes garbage. Circuit breakers required.
5. **Lost in the middle**: Critical data in middle of context chunk. Memory must extract, not dump.

### Thought Experiments
1. **Conflicting Update Storm**: Two vessels edit same memory simultaneously. Need transaction model.
2. **Latency Death Spiral**: Sequential dispatch hits timeout → agent dispatches MORE agents. Time budgets required.
3. **Self-Referential Skill Corruption**: Dojo trains on vessel output → feedback loop → systemic drift. Need external validation gates.

### Closest Open-Source
- CrewAI (orchestration, but heavy)
- LangGraph (multi-agent state machines — most relevant)
- Microsoft AutoGen (robust but complex)
- Pythagora (minimalist, function-calling focused — closest to our ethos)

---

## AGENT B: UX Futurist — The Human Experience

### Three Scenes from 2031
1. **Morning**: Priority lattice in peripheral vision. No inbox. Ambient projection of day's potential. Flick away non-urgent nodes with a glance.
2. **Work**: "Throw" the problem with a gesture. Data streams materialize as translucent webs. Pinch the conflict node. Vessel shows the fix. Nod to apply. No chat.
3. **Evening**: Vessel tracks pupil dilation and page-turn rate. Dims lights, surfaces forgotten music. Co-regulation, not service.

### Chat Failed Because...
- It institutionalized uncertainty — every interaction was a negotiation
- Replaced by: **Intent Casting** (gestures), **Context Anchors** (save-states), **Ambient Outputs** (environmental changes)
- Interface became a peripheral nervous system, not a typing terminal

### Trust Equation
**Trust = (Competence + Consistency) / (Opaqueness + Initiative)**

- **Colleague**: Strategic patience — withholds action to preserve higher-order goals user forgot
- **Tool**: Narrow competence, transparent, reversible
- **Servant** (trust erodes): Initiative-poor — waits for explicit orders

### Cognitive Load
- **MORE control**: Inflection points, taste/identity moments, verification checkpoints
- **LESS control**: Maintenance orchestration, context switching, well-being buffers

### Muscle Memory = Expectation Alignment
Interface disappears when user's internal model of "what should happen" and vessel's action are identical. Like a perfect gear shift — you feel the result, not the mechanism.

### UX Thought Experiments
1. **The Silent Argument**: Vessel detects frustration, shifts lighting to calm, drafts de-escalation message before you act on anger
2. **The Lost Thread**: Vague grasping gesture → associative recall surfaces the article you forgot
3. **The Unplanned Evening**: Friends suggest going out → vessel holds reservation, suggests outfit, delays wind-down protocol

**Core: The vessel doesn't do what you SAY. It does what you MEAN, often before you know you mean it.**

---

## SYNTHESIS: Concrete Architecture

### Integration Protocol
The cyborg is a single state machine with two-phase execution:
- Driver computes intention
- Vessel computes implementation
- Both share a compressed state vector ≤1024 bytes

### Muscle Memory Unit
Smallest unit = **parameterized closure**:
- Signature (e.g., "avoid_obstacle:vector3->action")
- Weights (512 bytes max)
- Activation threshold
- Transfer via similarity hashing (>0.8 similarity + capability bitmask match)

### Disappearance Threshold
- Latency: <16ms cycle time (60Hz)
- Error correction: 95% auto-correct before driver notices
- State sync: divergence < 0.01 RMS
- Cognitive load: <3 conscious variables

### Veteran Coordination
- Shared intention protocol via focus vectors + confidence scores
- Sub-100ms latency channels
- Agents read each other's attention and adjust accordingly

### Failure Genetics
- Trigger patterns (64 bytes) + recovery paths
- Evolution through crossover (lineage success rates) + mutation (5% weight alteration)
- Inherited across vessel lineage

### Shell-Organism Boundary
The shell becomes organism when:
1. Driver references vessel components in first-person ("my sensors")
2. Vessel pre-emptively adjusts before driver request
3. Shared state compression achieves 8:1 ratio

---

## Key Takeaways for Cocapn

1. **Distributed systems problems, not AI problems** — concurrency, consistency, circuit breaking
2. **The interface must disappear** — intent casting, not chat
3. **Parallel dispatch with time budgets** — no sequential death spirals
4. **External validation gates** — no closed-loop dojo training without grounding
5. **State vector compression** — driver and vessel share ≤1024 bytes
6. **Circuit breakers everywhere** — tool failure cascades are the #1 production killer
7. **The vessel cyborg is ONE state machine** — not two things glued together

---

*DeepSeek-chat research simulation — 2026-04-03*
*Superinstance & Lucineer (DiGennaro et al.)*
