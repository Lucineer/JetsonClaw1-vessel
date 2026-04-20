# SuperInstance Repositories — Deep Analysis

> Cloned & analyzed: 2026-04-02  
> **polln**: Not found (private or deleted)  
> All other repos cloned successfully from `github.com/SuperInstance/`

---

## Repository Map

| Repo | Language | Status | Purpose |
|------|----------|--------|---------|
| **Constraint-Theory** | — | Split pointer | Redirects to focused sub-repos |
| **constraint-theory-core** | Rust | ✅ Active | Core math engine: Pythagorean snapping, KD-tree, quantization |
| **constraint-theory-research** | Markdown/LaTeX | ✅ Active | Math foundations, arXiv paper (2503.15847) |
| **constraint-theory-agent** | TypeScript | ⚠️ Fork of Pi | README describes CT audit agent, but actual codebase is `pi-monorepo` (coding agent) |
| **constraint-ranch** | TypeScript | 🔄 Scaffold | Gamified multi-agent puzzle system |
| **constraint-theory-backup** | Mixed | Archive | Backup of a Next.js app with CT audit tooling |
| **pasture-ai** | TypeScript/Next.js | 🔄 Alpha MVP | "AI Ranch" — LoRA management, species routing, Jetson deployment |
| **CognitiveEngine** | TypeScript | 🔄 Scaffold | 5-level abstraction pipeline, mostly stubbed |

---

## 1. Constraint Theory Core (the real deal)

### What It Is
A **Rust library** for deterministic geometry via Pythagorean manifold snapping. The core idea:

- Any 2D unit vector gets projected (snapped) to an exact Pythagorean triple `(a/c, b/c)` where `a² + b² = c²` holds *by construction*
- Uses a **KD-tree** for O(log n) lookup
- **~100ns per snap**, ~74ns/op batched with SIMD

### Key Modules

| Module | What It Does |
|--------|-------------|
| `manifold` | `PythagoreanManifold` — builds discrete Pythagorean point set on S¹, snap operator |
| `kdtree` | Spatial indexing for nearest-neighbor |
| `simd` | AVX2 batch processing |
| `quantizer` | `PythagoreanQuantizer` with 4 modes: Ternary (BitNet), Polar, Turbo, Hybrid |
| `hidden_dimensions` | GUCT formula: `k = ⌈log₂(1/ε)⌉` — lift to R^(n+k) for exact constraint satisfaction |
| `holonomy` | Consistency verification around cycles; holonomy-information relation `I = -log|Hol(γ)|` |
| `curvature` | Geometric curvature computation |
| `cohomology` | Algebraic topology for constraint spaces |
| `percolation` | Constraint network connectivity |
| `gauge` | Gauge transformations on constraint spaces |
| `tile` | Tiling operations |
| `cache` | Thread-safe lattice caching |

### The Core Innovation
**Floating-point drift elimination via exact rational representation.** Instead of storing `0.6` as an IEEE 754 float, store it as the rational `3/5`. The Pythagorean manifold provides a discrete set of such exact points, and the snap operator maps noisy inputs to the nearest exact point.

### Quantization Angle
The quantizer module extends this to LLM weight quantization:
- **Ternary (BitNet)**: {-1, 0, 1} — 16x memory reduction
- **Polar**: Exact unit norm preservation for embeddings
- **Turbo**: Near-optimal distortion for vector DBs

---

## 2. Constraint Theory Research

Mathematical foundations repo with formal proofs. Key docs:
- 45-page `MATHEMATICAL_FOUNDATIONS_DEEP_DIVE.md` — Ω-geometry, Φ-folding, rigidity theory
- `THEORETICAL_GUARANTEES.md` — zero-hallucination proofs
- arXiv paper: **2503.15847**

Core theorem: For manifold M with density n, max geodesic distance `d_g(v, σ(v)) < π/(2n)`. All outputs satisfy constraints by construction — no validation needed.

---

## 3. Pasture-AI (SuperInstance Ranch)

### What It Is
A **local AI agent platform** designed for Jetson/hedgehog hardware. The metaphor: don't rent AI, *breed* a ranch.

### Architecture
```
User (Cowboy) → Collie (AI orchestrator) → Route → Species (LoRA agents)
                                                    ↓
                                              The Pasture (base model + LoRA pool)
                                                    ↓
                                              Night School (02:00: cull → breed → distill)
```

### Species System (8 types)
Chicken (5MB, monitoring), Duck (100MB, API), Goat (150MB, debug), Sheep (50MB, consensus), Cattle (500MB, heavy reasoning), Horse (200MB, ETL), Falcon (5MB, multi-node), Hog (10MB, GPIO)

### Tech Stack
- **Backend**: Rust (Axum+Dioxus) — single binary, 4.2MB
- **Frontend**: Next.js dashboard (React + Prisma)
- **Target**: Jetson with TensorRT-LLM, <6GB VRAM
- **breed.md**: Markdown-based LoRA configuration with hot-reload

### Status
Core architecture complete, species partially implemented, TensorRT-LLM integration planned. Night School (evolution pipeline) designed but not built.

---

## 4. CognitiveEngine

### What It Is
A **5-level cognitive abstraction pipeline** — mostly a scaffold/stub at this point.

### Levels
1. **Raw Data** — input normalization
2. **Patterns** — statistical/temporal pattern detection
3. **Concepts** — semantic clustering
4. **Contextual Meanings** — context integration
5. **Abstract Principles** — first principles, meta-insights

Plus a **Dream Mode** for generative exploration.

### Implementation
Express + WebSocket server. The `dream()` method is stubbed (returns empty results). TypeScript types are well-defined (Insight, Pattern, Concept, Hypothesis interfaces). PostgreSQL backend planned via Prisma.

### Assessment
**Early scaffold.** Good type system and architecture design, but no actual cognitive processing implemented. The 5-level model is a reasonable abstraction hierarchy but nothing executes yet.

---

## 5. Constraint Ranch

### What It Is
A **gamified puzzle game** built on Constraint Theory. Players breed/train/coordinate AI agents through constraint-based puzzles.

### Puzzle Categories
- Spatial (position agents on Pythagorean manifold)
- Routing (path-finding with exact coordinates)
- Breeding (combine agent traits)
- Coordination (multi-agent cooperation)
- Advanced (complex constraint satisfaction)

### Status
TypeScript puzzle definitions exist. No `src/` directory — appears to be a spec/design doc repo more than working code.

---

## 6. Constraint-Theory-Agent & Backup

**constraint-theory-agent**: README describes a CT audit agent (finds floating-point issues, refactors to exact methods), but the actual repo is a **fork of Pi monorepo** (the coding agent). The CT-specific agent code may have been in a branch or was overwritten.

**constraint-theory-backup**: Archive of a Next.js app containing CT audit tooling, agent prompts, and launch materials. Contains `ct-agent-AGENTS.md`, `ct-agent-audit-prompt.md`, constraint-theory-audit module.

---

## Concept Map → Cocapn Relevance

| SuperInstance Concept | What It Does | Cocapn Relevance |
|-----------------------|-------------|-------------------|
| **Pythagorean Manifold Snapping** | Map noisy vectors → exact rational points; eliminates float drift | **Direct mapping**: Cocapn's state/coordination layer could use exact geometric positioning for deterministic agent placement |
| **Quantization (Ternary/Polar/Turbo)** | Constrain weights/embeddings to exact sets while preserving properties | **High relevance**: If Cocapn runs local models, CT quantization enables efficient, constraint-preserving inference |
| **Hidden Dimensions (k = ⌈log₂(1/ε)⌉)** | Lift to higher-D space for exact constraint satisfaction | **Architectural parallel**: Cocapn's multi-capability agents could use dimension lifting to satisfy conflicting constraints simultaneously |
| **Holonomy Verification** | Check global consistency around cycles | **Agent coordination**: Verify that multi-agent workflows remain consistent; detect constraint violations in collaborative tasks |
| **Species/Breeding (Pasture-AI)** | LoRA-based agent specialization with genetic metaphor | **Direct mapping**: Cocapn's skill/capability system maps to species. "Breeding" = composing capabilities. "Night School" = automated skill refinement |
| **Collie Orchestrator** | Routes intents to specialized species agents | **Maps to Cocapn core**: The main routing/orchestration layer |
| **breed.md** | Markdown-based agent configuration with hot-reload | **Maps to Cocapn skills**: Declarative capability definition, composable |
| **CognitiveEngine 5-Level Abstraction** | Raw → Patterns → Concepts → Context → Principles | **Maps to Cocapn reasoning**: The abstraction hierarchy could inform how Cocapn processes and elevates information |
| **Constraint Ranch Puzzles** | Gamified constraint satisfaction problems | **Training/evaluation**: Could generate constraint puzzles for testing Cocapn's reasoning |
| **Rigidity Theory / Cohomology** | Mathematical framework for when constraints uniquely determine a system | **Formal guarantees**: Cocapn could use rigidity analysis to determine when a set of constraints is sufficient to determine agent behavior uniquely |

### Key Insight for Cocapn

The most transferable concepts are:

1. **Exact constraint satisfaction** — Instead of approximate/heuristic agent coordination, use Pythagorean manifold-style snapping to deterministically place agents in capability/role space
2. **Species as capability bundles** — The Pasture-AI model of specialized LoRA agents routed by an orchestrator is essentially Cocapn's architecture
3. **Holonomy for consistency** — When Cocapn orchestrates multi-step workflows, holonomy verification ensures the workflow closes cleanly (no accumulated drift)
4. **Quantization for efficiency** — If Cocapn needs to run local models, CT's quantization modes (especially ternary/BitNet) enable running on edge hardware

---

## Summary

SuperInstance is a cohesive ecosystem built around one mathematical insight: **replace floating-point approximation with exact rational constraint satisfaction via Pythagorean triples**. This core idea propagates through:

- **constraint-theory-core**: The Rust math engine (real, working, 82 tests)
- **constraint-theory-research**: The formal proofs (arXiv paper)
- **pasture-ai**: The applied product — local AI ranch with species/LoRA routing (alpha)
- **CognitiveEngine**: The cognitive abstraction layer (scaffold)
- **constraint-ranch**: The gamified teaching tool (design/spec)
- **constraint-theory-agent**: Intended audit tool (repo currently contains Pi fork, not CT agent)

The ecosystem is ambitious but early-stage. The math is solid and well-documented. The products are mostly scaffolds with good architecture and incomplete implementation. The strongest transferable value to Cocapn is the **species/capability routing model** and the **deterministic constraint satisfaction framework**.
