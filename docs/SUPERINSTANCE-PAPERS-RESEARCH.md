# SuperInstance Papers Deep Research + Stochastic Computing Integration
## 2026-04-03 — 72+ papers analyzed, 4 new repos proposed

### SuperInstance-papers Repository (72+ papers)

#### Research Phases
- **Phase 1 (P1-P23)**: Core Framework — Origin-centric data, confidence cascades, geometric tensors, tile algebra, rate-based change
- **Phase 2 (P24-P30)**: Research Validation — GPU scaling, neuromorphic circuits, game theory, adversarial robustness
- **Phase 3 (P31-P40)**: Extensions — Dreaming, LoRA swarms, federated learning, guardian angels, time-travel debug, ZK proofs, holographic memory, quantum superposition
- **Phase 4 (P41-P51)**: Ecosystem — FPS/RTS paradigm, LLM distillation, asymmetric understanding, cellular scale, geometric encoding
- **Phase 5 (P52-P61)**: Lucineer Hardware — Jetson-specific optimizations
- **Phase 6 (P62-P66)**: Ancient Cell Connections — Biological computation parallels

#### Papers Most Relevant to Cocapn

| Paper | Key Insight | Cocapn Application |
|-------|-----------|-------------------|
| **P21: Stochastic Superiority** | Controlled randomness beats determinism 34% under shift. Gumbel-Softmax + temperature annealing. 2.8x diversity, 5x recovery. | Stochastic cells in fleet, temperature annealing for routing |
| **P42: FPS vs RTS** | Hybrid scheduling: 3.7x throughput + 99.7% deadline compliance | Fleet request routing, deadline-aware model selection |
| **P25: Hydraulic Intelligence** | Fluid dynamics metaphors for computation (backpressure, flow, turbulence) | Worker load balancing as fluid dynamics |
| **P32: Dreaming** | AI consolidation cycles — compress accumulated context during "sleep" | Vessel dream cycles for soft actualization |
| **P27: Emergence Detection** | Detecting phase transitions in agent swarms | Fleet Commons monitors for emergence |
| **P28: Stigmergic Coordination** | Indirect coordination through environment (pheromone trails) | Durable Objects as pheromone trails for fleet consensus |
| **P39: Holographic Memory** | Distributed memory with interference patterns | Fleet knowledge graph with holographic retrieval |
| **P29: Competitive Coevolution** | Species compete, driving improvement | AI Ranch species breeding applied to Cocapn vessels |
| **P38: ZK Proofs** | Zero-knowledge verification of computation | Verify fleet computations without revealing data |
| **P43: LLM Distillation** | Large model → small model knowledge transfer | Teacher-Student for BYOK routing (Equipment pattern) |
| **P20: Structural Memory** | Persistent memory across sessions | Crystallization graph formalized |

### Constraint-Theory-Backup Repository

- **N-dimensional Pythagorean manifold engine** (Rust) — exact arithmetic replacing floating-point
- **KD-tree state snapping** — 100ns per query, O(log N) operations
- **78% code reduction** when replacing float with exact methods
- **Constraint Theory Agent** — audits codebases for floating-point drift
- **Multiplayer constraint puzzles** — interactive exploration of manifolds

### Stochastic Computing in Spreadsheet Logic

#### The Concept
Stochastic cells as first-class primitives in the spreadsheet. RNG seeds are visible, addressable metadata. External entropy flows through simulations. The nature of randomness (aleatoric vs epistemic) is teased out per application.

#### Cell Formulas
```
=STOCH.SEED("market2024")          // Set seed for reproducibility
=STOCH.NORMAL(100, 15)             // Normal distribution (mean, SD)
=STOCH.GUMBEL(range, temp)         // Gumbel-Softmax sampling
=STOCH.UNIFORM()                   // Uniform [0,1]
=ENTROPY("random.org")             // External entropy injection
=B2 * $TEMP$                       // Temperature annealing reference
```

#### Temperature Annealing as Cell Attribute
- `[temp: 1.2]` — High exploration (wide distributions)
- `[temp: 0.3]` — Low exploitation (narrow distributions)
- Annealing schedule: `temp(t) = max(temp_min, temp_0 * e^(-λt))`

#### Uncertainty Visualization
- **Epistemic** (model ignorance): Wide opaque band, narrows with data
- **Aleatoric** (inherent noise): Dense shimmering pattern, irreducible

#### Stochastic Superiority Applied to Cocapn
- **Routing**: Gumbel-top-k routing across Workers with diversity bonuses (not argmax)
- **Evaporation**: Cache decisions use stochastic sampling instead of deterministic thresholds
- **Fleet sync**: Stochastic consensus with Gumbel-Softmax instead of majority vote
- **Context pods**: Exploration temperature for new entries, exploitation for retrieval

### 4 New Repos Proposed (Kimi K2.5 Synthesis)

#### 1. hydraulic-scheduler
**Based on**: P25 (Hydraulic Intelligence) + P42 (FPS/RTS)
**Function**: Fluid dynamics metaphors for backpressure-aware routing across 27+ Workers
**Key feature**: Treats fleet load as fluid — backpressure propagates naturally, turbulence detection for anomaly alerts
**Tech**: TypeScript Workers, shared KV namespace

#### 2. dream-cycle
**Based on**: P32 (Dreaming) + P20 (Structural Memory)
**Function**: Scheduled "sleep" epochs where agents compress accumulated context into embeddings
**Key feature**: Vessels enter dream state during low-traffic hours, consolidate crystallization graph, prune stale entries
**Tech**: Cron-triggered Workers, vector embeddings in KV

#### 3. stigmergic-kv
**Based on**: P28 (Stigmergic Coordination) + P41 (CRDT SuperInstance)
**Function**: Indirect coordination via Durable Objects as pheromone trails
**Key feature**: Workers leave "pheromone" markers in KV instead of direct RPC. Other workers detect and follow patterns. Consensus without communication.
**Tech**: Cloudflare Durable Objects, TTL-based pheromone decay

#### 4. exact-constraint
**Based on**: constraint-theory-backup (Pythagorean manifold, KD-tree)
**Function**: WASM module for exact arithmetic in critical fleet computations
**Key feature**: Eliminates floating-point drift in financial/cryptographic cells. WASM-compiled from Rust for Workers.
**Tech**: Rust → WASM, KD-tree state snapping

### Additional Novel Concepts from Papers

| Paper | Novel Concept | Potential Repo |
|-------|--------------|---------------|
| P44: Asymmetric Understanding | Different agents have different "resolutions" of the same data | asymmetric-fleet |
| P45: Cellular Scale | Optimal cell size for computation | cell-size-optimizer |
| P46: FPS Validation | Benchmarking framework for fleet scheduling | fleet-bench |
| P47: Multiagent Coordination | Formal coordination protocols | fleet-coordination-protocol |
| P48: Asymmetric Information | Information asymmetry as feature not bug | information-markets |
| P51: Geometric Encoding | Encode data as geometric structures for efficient computation | geometric-kv |
| P18: Energy Harvesting | AI systems that harvest their own compute energy | energy-harvester |
| P35: Guardian Angels | Protective oversight layer for AI systems | guardian-overlay |
| P37: Time-Travel Debug | Replay and rewind agent state for debugging | time-travel-debug |
| P40: Quantum Superposition | Superposition of agent states | quantum-fleet |

### Integration Priority

**Immediate (this week)**:
1. Stochastic cells in cocapn worker (STOCH.* formulas)
2. Temperature annealing for BYOK routing

**Short-term (this month)**:
3. dream-cycle repo (scheduled consolidation)
4. stigmergic-kv (pheromone-based coordination)

**Medium-term (next quarter)**:
5. hydraulic-scheduler (fluid dynamics load balancing)
6. exact-constraint (WASM exact arithmetic)

---

*Superinstance & Lucineer (DiGennaro et al.) — 2026-04-03*
