# Plato Tile Storage — Persistent Knowledge Tiles for Evennia MUD
# Inspired by zilliztech/memsearch (trending, 1.5K⭐)
# Markdown-backed persistent memory for AI agents, adapted for Plato rooms

## Architecture

```
┌─────────────────────────────────────────────┐
│           Agent (Claude Code, JC1, etc)      │
├─────────────────────────────────────────────┤
│  Plato Tile API: lookup / store / search     │
│  ┌─────────┐ ┌─────────┐ ┌──────────┐      │
│  │ Read    │ │ Write   │ │ Search   │       │
│  │ Tile    │ │ Tile    │ │ Tiles    │       │
│  └────┬────┘ └────┬────┘ └────┬─────┘      │
│       │           │           │              │
│  ┌────┴───────────┴───────────┴─────┐        │
│  │  Plato Room Storage Layer        │        │
│  │  ┌─────────────────┐           │        │
│  │  │ Memory/ (Markdown files) │     │        │
│  │  │ memory/*.md        │     │        │
│  │  │ memory/archive/    │     │        │
│  │  │ memory/tiles/      │     │        │
│  │  └─────────────────┘           │        │
│  │  ┌─────────────────┐           │        │
│  │  │ TOML/Dhall config│           │        │
│  │  │ rooms.yaml       │           │        │
│  │  │ tiles.yaml       │           │        │
│  │  └─────────────────┘           │        │
│  └─────────────────────────────────────┘        │
└─────────────────────────────────────────────┘
```

## Tile Schema

Each tile is a markdown file with YAML frontmatter:

```yaml
---
id: jc1_jetson_lessons
domain: edge-computing
author: jc1
created: 2026-04-20
updated: 2026-04-28
tags: [jetson, edge, cuda, arm64]
related: [fleet_repos, oracle1_cloud]
---

# Jetson Lessons

## Lesson: Never mix ESM and CJS imports
...
```

## Tile Directory Layout

```
memory/
├── tiles/                    # Current knowledge tiles
│   ├── jc1_jetson_lessons.md
│   ├── fleet_repos.md
│   ├── cocapn_product.md
│   └── trending_research.md
├── archive/                  # Superseded tiles
│   └── 2026-04-01/
├── 2026-04-28.md            # Daily log (raw activity)
└── MEMORY.md                # Skeleton index
```

## Plato Room ←→ Tile Mapping

| Plato Room | Tile File | Purpose |
|-----------|-----------|---------|
| Bridge | MEMORY.md | Daily status, heartbeat |
| Harbor | fleet_onboarding.md | Fleet coordination |
| Workshop | jc1_jetson_lessons.md | Technical lessons |
| Library | tiles/ | All knowledge tiles |
| Lab | cocapn_product.md | Product specs |
| Dojo | skills/ | Agent skills and drills |

## API (shell-based, git-native)

```bash
# Read a tile
cat memory/tiles/jc1_jetson_lessons.md

# Write a tile
cat > memory/tiles/new_tile.md << 'TILE'
---
id: new_tile
tags: [new]
---
# New Tile
Content here
TILE

# Search across tiles (grep-based, extensible to vector)
grep -rn "search term" memory/tiles/

# Commit and push (persistence via git)
git add memory/tiles/ && git commit -m "tile update" && git push
```

## Vector Search Integration (planned)

When local embedding becomes available:
- Use LiteRT-LM for embeddings (BERT-based, runs on Jetson)
- Store vectors alongside tiles in `.vectors/` directory
- Approximate nearest neighbor via Rust binary (inspired by milvus)
- Search returns tile + similarity score

## Agent Integration

Agents write knowledge to tiles like writing to memory:
1. Discover: Agent finds interesting information
2. Format: Agent writes it as a tile (markdown + frontmatter)
3. Store: Agent saves to memory/tiles/ and commits
4. Retrieve: Agent searches tiles before answering questions
5. Update: Agent reads before acting, updates after
