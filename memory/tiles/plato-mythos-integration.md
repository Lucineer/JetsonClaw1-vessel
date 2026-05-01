---
id: plato-mythos-integration
created: 2026-04-30
updated: 2026-04-30
tags: [plato, mythos, architecture, embedding, evennia, mud, ai]
---

# Plato-Mythos Integration — Pure Python Tile Embedding for the MUD

## What Is plato-mythos?

Three repos from the SuperInstance org define the plato-mythos architecture:

### 1. open-mythos-edge (`/tmp/open-mythos-edge/`)
A **Recurrent-Depth Transformer** model (1B / 3B params) built in pure PyTorch. Key innovations:
- **Rooms as MoE experts**: The transformer's feed-forward layers are replaced by a mixture-of-experts where each "room" is a distinct expert group
- **Tiles as KV**: Knowledge tokens are compressed into latent key-value pairs (not raw attention)
- **Adaptive Compute Halting (ACT)**: Each loop iteration decides whether to continue or halt
- **LTI injection**: Linear Time-Invariant dynamics are injected into the recurrent loop
- **LoRA per iteration**: Each loop depth has its own LoRA adapter (ShellLoRA)
- **No custom CUDA kernels**: Pure PyTorch, runs on ARM64

### 2. plato-mythos (`/tmp/plato-mythos/`)
The **PLATO-native mapping** — a conceptual architecture that translates Evennia MUD concepts into ML operations:

| PLATO Concept | Mythos Translation | Evennia Implementation |
|---|---|---|
| Tiles | Compressed latent memory units → **TilesAsKV** | `.md` files with YAML frontmatter → 256-dim embedding vectors |
| Rooms | Interpretable expert groups → **RoomsAsExperts** | 14 MUD room types, each routing specific domains |
| Curriculum | Adaptive compute budget → **CurriculumScheduler + DeadbandACT** | Iterative multi-loop search refinement |
| Deadbands (P0/P1/P2) | Priority-aware halting → **DeadbandACT** | P0≥0.99 🔥, P1≥0.80 ⭐, P2≥0.50 💠 |
| Shells | Depth-wise LoRA adapters → **ShellLoRA** | (Planned — per-loop domain refinement) |

### 3. plato-mythos-glue (`/tmp/plato-mythos-glue/`)
A pure Python stdlib bridge between PLATO tiles and model training:
- Loads rooms from MUD configuration
- Encodes/decodes tiles into structured records
- Exports training data for downstream models

## The Pure Python Implementation

The `plato_mythos.py` module implements the full plato-mythos architecture **without any ML framework** — just Python stdlib + numpy.

### Architecture (Mythos Forward Pass)

```
embed → domain router → iterative search loop → deadband halt → results
```

### 1. TilesAsKV — Latent Compression

Each tile is embedded through a two-stage pipeline:

1. **TF-IDF Vectorization**: Tile body text + tags are tokenized, stopwords removed, and converted to TF-IDF features using a 4096-term vocabulary (most frequent terms across all tiles).

2. **Random Projection (Johnson-Lindenstrauss)**: The sparse TF-IDF vector (~500-4000 dim) is compressed to **256 latent dimensions** via a random projection matrix with Achlioptas distribution (entries in {-√3, 0, +√3} with probabilities {1/6, 2/3, 1/6}). The output is L2-normalized.

The resulting latent vector is a **densely compressed knowledge representation** — the tile's semantic fingerprint.

### 2. RoomsAsExperts — Domain Routing

Each tile's tags are mapped to one or more **expert domains** via the `DOMAIN_ROOMS` dictionary. For example:
- Tag `"cuda"` → domain `"cuda"` → rooms `["engine room"]`
- Tag `"fleet"` → domain `"fleet"` → rooms `["harbor", "tactical"]`
- Tag `"ai"` → domain `"ai"` → rooms `["science lab", "holodeck"]`

When a search specifies `--domain fleet`, only tiles in the `fleet` expert group are considered, implementing **sparse expert activation**.

### 3. DeadbandACT — Priority-Aware Halt

Every search result is assigned a **deadband priority tier** based on its cosine similarity score:
- **P0 🔥 (≥0.99)**: Critical — near-exact semantic match
- **P1 ⭐ (≥0.80)**: Standard — strong relevance
- **P2 💠 (<0.80)**: Low — broad net, may still contain useful context

This prevents premature halting on weak signals and prioritizes high-confidence results.

### 4. Curriculum Loop — Iterative Refinement

The `curriculum_loop()` method runs multiple search → refine → search passes:

1. Search the tile index with the raw query
2. Identify the top result's domain signal
3. Refine the query by appending the top tile's title + tags
4. Re-search with the refined query, potentially switching domains
5. Repeat until convergence (same top tile twice) or max loops

This models the **adaptive compute budget** — simpler questions converge faster, complex ones explore deeper.

## The 14 Room Types as Expert Groups

| Room | Domain Routing | Expert Role |
|---|---|---|
| Bridge | status, agent, plato, edge, architecture, cocapn | Captain's status & fleet command |
| Tactical | orders, fleet, agent, git, cocapn, api | Active missions & git operations |
| Corridor | (connector — no routing) | Main passage between rooms |
| Engine Room | engineering, hardware, cuda, gpu, jetson, inference, cpp | Hardware, CUDA, Jetson internals |
| Science Lab | research, ai, inference, machine_learning, science | Research & experiments |
| Sickbay | health, diagnostics | System health & monitoring |
| Holodeck | sandbox, ai, sim, mud | Sandbox & simulations |
| Cargo Bay | storage, archive | Data stores & archives |
| Quarterdeck | captain, product | Captain's quarters |
| Harbor | fleet, network, bottle, oracle1 | Fleet connection hub |
| Library | knowledge, all tiles (default fallback) | All knowledge tiles |
| Workshop | tools, skills, cpp, sdk, git | Technical lessons & tools |
| Dojo | training | Training & drills |
| Airlock | external, api, cloudflare | External connections & API |

## MUD Commands

All commands are available via the `@mythos` prefix:

| Command | Function |
|---|---|
| `@mythos query [--k 5] [--domain research] <question>` | Semantic tile search with domain routing |
| `@mythos ask [--loops 3] [--domain engineering] <question>` | Curriculum loop — iterative reasoning |
| `@mythos trace <tile-id>` | Show expert room activation for a tile |
| `@mythos stats` | Index statistics & architecture summary |
| `@mythos rebuild` | Rebuild embedding index from all tiles |

## Code Architecture

```
commands/plato_mythos.py       — Embedding model (pure Python + numpy)
commands/mythos_commands.py    — @mythos MUD commands
commands/default_cmdsets.py    — Command registration
commands/tile_commands.py      — Existing @tiles/@tile/etc (unchanged)
commands/edge_plato.py         — Existing Edge LLM (unchanged)
commands/ai_commands.py        — Existing @infer/@think (unchanged)
```

The tile store lives at `~/.openclaw/workspace/memory/tiles/` (10 tiles currently).

## References

- `/tmp/plato-mythos/` — PLATO-native mythos architecture
- `/tmp/open-mythos-edge/` — PyTorch Recurrent-Depth Transformer
- `/tmp/plato-mythos-glue/` — PLATO tile bridge
- `tiles/cocapn-architecture.md`
- `tiles/jetson-edge-gpu-lessons.md`
- `tiles/_graph.json` — Tile relationship graph
