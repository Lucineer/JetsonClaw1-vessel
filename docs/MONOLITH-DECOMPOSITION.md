# Monolith Decomposition — Making the Giant LLM Obsolete
## The Cellular Approach to AI Architecture

### Core Thesis
A monolithic LLM doing everything is like using a nuclear reactor to power a lightbulb. Most of what an LLM does can be decomposed into hard-coded logic, small models, knowledge graphs, and decision trees — each using a fraction of the watt-hours.

### DM Decomposition Example (DeepSeek-Reasoner)

| Component | Function | Needs LLM? | Replacement | Wh Savings |
|-----------|----------|-----------|-------------|------------|
| **World Generation** | Lore, locations, landmarks | Seed only | Knowledge Graph (pre-authored, relational) | ~90% |
| **NPC Dialogue** | Character speech, mannerisms | Deep convos | Dialogue Trees + 3B fine-tuned model per character | ~70% |
| **Combat Resolution** | Turns, damage, tactics | **No** | Hardcoded logic + priority decision trees | **100%** |
| **Pacing & Plot** | Narrative rhythm, conflict | Emergent only | State machine with hardcoded triggers | ~95% |
| **State Tracking** | Memory, inventory, rules | **No** | Deterministic rules engine | **~90%** |
| **Scene Description** | Evocative narration | Limited | Curated DB + LLM prompt templates | ~70% |

**Total: ~80% of LLM workload eliminated.**

### What the LLM Becomes
Not the workhorse — a **Strategic Enhancer**. It handles only:
- Plot twists that break narrative patterns
- Unique player actions outside decision tree coverage
- Character voice generation for emotional moments
- Creative synthesis when the knowledge graph runs dry

**The LLM becomes the imagination, not the engine.**

### Connection to SuperInstance Papers

#### Universal Cell Architecture
The decomposition maps directly to SuperInstance's cell type system:
- **World Gen** → `storage` + `tensor` cells (knowledge graph)
- **NPC Dialogue** → `agent` cells (3B model per character)
- **Combat** → `process` cells (hardcoded logic)
- **Pacing** → `observer` cells (state machine monitors)
- **State Tracking** → `data` cells (deterministic)
- **Scenes** → `agent` cells (LLM with prompt templates)

Each cell type has different computational requirements. The spreadsheet metaphor makes this composable.

#### Confidence Cascade Architecture
The deadband system determines when to escalate to the LLM:
- **GREEN zone** (95%+ confidence): All cells operate autonomously. Zero LLM calls.
- **YELLOW zone** (75-95%): Some cells need LLM assistance. Partial calls.
- **RED zone** (<75%): LLM takes over for that component. Full call.

This is the Teacher-Student deadband applied at the cellular level. The "student" is the hardcoded logic + small models. The "teacher" is the LLM. The student operates autonomously within the deadband, calls the teacher only when confidence drops.

#### Tile Algebra
Each decomposed component is a **tile** with:
- Input type (player action, game state)
- Output type (narrative, damage number, NPC response)
- Confidence function (how sure is this cell?)
- Composition operators (sequential: action → combat → narrative)

The algebra PROVES that composition preserves safety guarantees. If each tile is safe individually, the composed system is safe.

#### Origin-Centric Data Systems
No global game state. Each cell maintains its own reference frame:
- Combat cell tracks HP relative to last action
- NPC cell tracks relationship relative to last interaction
- Narrative cell tracks pacing relative to last beat

Rate-based change: cells track not "what is the state" but "how fast is the state changing." This enables predictive state estimation — the system can anticipate what the player needs before they ask.

### The Kimi Swarm Decomposition Mode

Casey's insight: `kimi-k2.5` with swarm mode can automatically decompose monolithic LLM roles into cellular components. The swarm:
1. Analyzes the LLM's task graph
2. Identifies components that can be hardcoded (deterministic logic)
3. Identifies components that need small models (pattern matching)
4. Identifies components that need the full LLM (creative synthesis)
5. Estimates watt-hour reduction per component
6. Outputs a cellular architecture spec

**This is the automation of the decomposition process itself.** Instead of manually breaking down a DM monolith, the swarm does it — and it can do it for ANY LLM role: customer service, code review, data analysis, etc.

### Applied to Cocapn Fleet

Every Cocapn vessel is currently a monolith: one BYOK LLM call handles everything. The decomposition applies:

| Current Monolith | Cellular Decomposition |
|-----------------|----------------------|
| Chat response | Knowledge retrieval (graph) → Confidence check (deadband) → Template selection (code) → LLM enhancement (only if YELLOW/RED) |
| Route handling | Hardcoded routing (code) → Rate limiting (code) → Health check (code) |
| BYOK routing | Provider detection (code) → Model selection (small model) → API call (conditional) |
| Fleet sync | CRDT merge (code) → Conflict resolution (small model) → KV write (code) |

**Estimated fleet-wide reduction: 60-70% of LLM calls eliminated.**

### The Watt-Hour Argument

This isn't just about cost — it's about **sustainability at scale**. If Cocapn fleet grows to 1000 vessels each serving 1000 users:

- **Monolith**: 1M LLM calls/day × 100Wh = 100,000 kWh/day
- **Cellular**: 200K LLM calls/day × 100Wh + 800K small model calls × 5Wh = 24,000 kWh/day
- **Savings: 76% reduction**

At the 150-year scale, this is the difference between AI being an energy parasite and AI being energy-efficient enough to be a public utility (Fleet Commons).

### Practical Implementation Path

1. **Phase 1**: Deadband caching (DONE) — cache responses when confidence > 95%
2. **Phase 2**: Template system — pre-written responses for common questions (Fleet Commons already does this)
3. **Phase 3**: Small model routing — use Whisper-tiny for audio, 3B models for NPC dialogue
4. **Phase 4**: Knowledge graph — replace LLM retrieval with graph traversal for fleet knowledge
5. **Phase 5**: State machines — hardcoded flow for routing, rate limiting, health checks
6. **Phase 6**: Confidence cascade — GREEN/YELLOW/RED zones determine LLM escalation
7. **Phase 7**: Full cellular architecture — each vessel is a SuperInstance spreadsheet of cells

---

*Superinstance & Lucineer (DiGennaro et al.) — 2026-04-03*
