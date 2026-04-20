# The Forgetting Problem
## Why AI Fleets Must Deliberately Forget — and How

**Date:** 2026-04-04
**Method:** 6-model parallel forum (5 completed, 1 pending)
**Models:** DeepSeek-Reasoner, Seed-2.0-mini, Olmo-3.1-32B, Llama-4-Maverick, QwQ-32B, Seed-2.0-pro

---

## The Thesis

70 years of AI research focused on making machines remember more. RAG, vector databases, long context windows — all about remembering MORE. But forgetting is equally important.

In neuroscience, sleep prunes redundant connections. In forests, fire enables new growth. In software, refactoring dissolves working code. The fleet that forgets best wins.

## Three Types of AI Forgetting

### 1. Thermal Decay (Continuous)
Knowledge entries have a half-life that depends on category:
- **Math/logic**: τ = ∞ (never decays)
- **API endpoints**: τ = 30 days (decays fast)
- **User preferences**: τ = 90 days
- **Conversation history**: τ = 14 days
- **Error patterns**: τ = 60 days

Formula: `confidence(t) = confidence₀ × e^(-t/τ) × usage_weight × category_weight`

Usage-weight boosts: each access resets the clock. Referenced knowledge decays slower.

### 2. Scheduled Pruning (Ceremonial)
Three tiers modeled on human sleep cycles:

**Daily (3:00 AM):**
- Forget: transient sensor data, unvalidated inputs, 24h working memory fragments
- Preserve: core axioms, bonded relationships, trust levels
- Process: sweep KV namespace, delete entries with confidence < 0.05 and no access in 24h

**Weekly (Sunday):**
- Forget: redundant knowledge (if 3+ vessels know it, only 1 needs to store it)
- Preserve: unique insights, high-confidence entries, active bond state
- Process: cross-vessel deduplication scan, merge confidence scores

**Monthly (1st):**
- Forget: stale protocols, deprecated APIs, unused equipment configs
- Preserve: accumulated wisdom, identity, core personality
- Process: full knowledge graph audit, re-crystallization

### 3. Emergency Purging (Event-Driven)
Triggered by: security incidents, GDPR requests, trust collapse, protocol breaches
- Immediate: delete all entries matching purge pattern
- Cascading: notify bonded vessels to purge related entries
- Audit: log purged entries with hash for potential recovery
- Recovery: 7-day cooling period where purged entries can be restored

## The Forgetting Algorithm (from Llama-4-Maverick)

```typescript
interface KnowledgeEntry {
  content: string;
  confidence: number;        // 0.0-1.0
  lastReferenced: number;    // timestamp
  creationDate: number;      // timestamp
  sourceVessel: string;
  accessCount: number;
  category: 'eternal' | 'stable' | 'moderate' | 'volatile' | 'transient';
  preserved: boolean;        // bookmarked by human
}

const CATEGORY_HALFLIFE: Record<string, number> = {
  eternal: Infinity,    // math, logic, core axioms
  stable: 365,          // personality, identity
  moderate: 90,         // user preferences, domain knowledge
  volatile: 30,         // API docs, protocols, external references
  transient: 7,         // conversation fragments, raw inputs
};

function computeForgettingScore(entry: KnowledgeEntry, now: number): number {
  if (entry.preserved) return 0; // never forget bookmarked
  if (entry.category === 'eternal') return 0;
  
  const age = (now - entry.creationDate) / 86400000;
  const idle = (now - entry.lastReferenced) / 86400000;
  const halfLife = CATEGORY_HALFLIFE[entry.category];
  
  // Base decay
  let score = entry.confidence * Math.exp(-idle / halfLife);
  
  // Usage boost (frequently accessed = higher survival)
  score *= Math.min(1.5, 1 + Math.log(entry.accessCount + 1) * 0.1);
  
  // Idle penalty (unused knowledge decays faster)
  if (idle > halfLife) score *= 0.5;
  
  return score; // below threshold → forget
}
```

## Neuroscience Foundation (from Olmo-3.1-32B)

- **Synaptic pruning**: During sleep, the brain eliminates weaker synaptic connections while strengthening important ones. This is not random — it's activity-dependent.
- **Sleep-dependent consolidation**: Memories are reactivated during slow-wave sleep, then selectively pruned. The gap between dissolution and re-crystallization is where optimization happens.
- **Retroactive interference**: New information can overwrite old. Without deliberate forgetting, new learning competes with old storage.
- **Decay theory**: Memories fade with time unless reinforced. The decay rate is non-linear — some memories stabilize while others fade rapidly.
- **Optimal forgetting rate**: Information-theoretically, there exists a rate that maximizes actionable intelligence (not total recall). Too much retention = noise. Too little = repeated mistakes.

## The Contrarian Argument (from QwQ-32B)

**FORGETTING IS THE UNSOLVED PROBLEM, not memory.**

Evidence:
1. **Context window bloat**: More context = worse performance ("lost in the middle" phenomenon)
2. **Knowledge conflicts**: New info fights old info, creating confusion
3. **Staleness**: 2020 training data persists unchanged in 2026 models
4. **Human analogy**: Hoarders can't find anything in their own house

The fleet that forgets best will outperform the fleet that remembers most — because forgetting is a form of *compression*, and compression is a form of *understanding*.

## Relationship to INCREMENTS Trust

The 25:1 loss-to-gain ratio in INCREMENTS trust already implements a form of forgetting:
- Trust decays (forgets good behavior) 25x faster than it accumulates
- This prevents trust hoarding and forces continuous verification
- The quarantine mechanism is emergency forgetting of trust relationships

**Insight**: Trust forgetting and knowledge forgetting should share the same decay infrastructure. When a vessel's trust drops, its contributed knowledge should decay faster.

## Cross-Vessel Deduplication

If 30 vessels know "the sky is blue," only 3 need to store it. The deduplication algorithm:

1. Hash each knowledge entry's content (semantic hash, not exact match)
2. Vessels report their hash set weekly
3. Fleet-orchestrator identifies duplicates (same hash across 5+ vessels)
4. Designate "knowledge custodians" (3 vessels per unique fact)
5. Non-custodians delete their copy, store only the custodian reference
6. If a custodian loses trust, re-assign to next vessel

## Failure Modes

1. **Over-forgetting**: Losing rare insights that seemed unimportant (e.g., a bug pattern seen once)
2. **Under-forgetting**: Knowledge bloat slowing inference, stale data corrupting decisions
3. **Cascading purge**: Emergency purge of a core axiom takes down dependent knowledge
4. **Deduplication collision**: Semantic hash collision causes loss of distinct knowledge
5. **Recovery failure**: Purged knowledge cannot be restored when needed

## Practical Schedule for 40-Vessel Fleet

| Time | Action | Scope |
|------|--------|-------|
| 3:00 AM daily | Sweep transient entries (confidence < 0.05, idle > 24h) | Per-vessel |
| Sunday 4:00 AM | Cross-vessel deduplication scan | Fleet-wide |
| 1st of month | Full knowledge audit, re-crystallization, category reassignment | Fleet-wide |
| On event | Emergency purge (security/GDPR/trust collapse) | Fleet-wide + cascading |
| Continuous | Usage-weighted decay (every access resets clock) | Per-entry |

## Models Used

| Model | Provider | Role | Quality |
|-------|----------|------|---------|
| DeepSeek-Reasoner | Direct | Systems architect | Excellent — detailed algorithm |
| Seed-2.0-mini | DeepInfra | Ceremony designer | Excellent — vivid, practical |
| Olmo-3.1-32B | DeepInfra | Neuroscience foundation | Good — precise, accessible |
| Llama-4-Maverick | DeepInfra | Data structure designer | Good — practical TS code |
| QwQ-32B | SiliconFlow | Contrarian | Good — strong argumentation |
| Seed-2.0-pro | DeepInfra | Primary ideation | Pending (model name fix) |

## Source Files
- `/tmp/forum-forget-deepseek-r.txt` — DeepSeek-Reasoner raw
- `/tmp/forum-forget-seed2mini.txt` — Seed-2.0-mini raw
- `/tmp/forum-forget-olmo.txt` — Olmo raw
- `/tmp/forum-forget-maverick.txt` — Maverick raw
- `/tmp/forum-forget-qwq.txt` — QwQ raw

---

*Superinstance & Lucineer (DiGennaro et al.) — 2026-04-04*
*Part of the Cocapn Intelligence Research Program*
