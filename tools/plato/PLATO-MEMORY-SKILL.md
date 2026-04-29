# Plato Memory Skill — Persistent Agent Memory

Store, search, and retrieve agent knowledge from git-backed Markdown tiles.

## Usage

```
memory/set <key>=<value>       # Store in today's memory log
memory/get <query>             # Search all memory files
memory/tile <name>             # Show a knowledge tile
memory/tiles                   # List all knowledge tiles
memory/tile-search <query>     # Search tiles for a match
memory/forget <query>          # Remove from memory (git-undo)
```

## Examples

```
# Store a lesson
memory/set "Never mix ESM and CJS requires"

# Find something
memory/get "jetson cuda lessons"

# Read a knowledge tile
memory/tile jc1_jetson_lessons

# List everything
memory/tiles

# Search across all tiles
memory/tile-search "trending"
```

## How It Works

All agent memory is stored in `~/jetsonclaw1-vessel/memory/`:
- **Daily logs**: `memory/YYYY-MM-DD.md` — chronological activity records
- **Knowledge tiles**: `memory/tiles/*.md` — structured, git-persisted knowledge
- **Archive**: `memory/archive/` — superseded tiles

Memory is git-native:
1. Agent writes knowledge → file created
2. File committed → git backup
3. Agent reads → git pull, search files
4. Every meaningful checkpoint gets pushed

## Tile Format

```markdown
---
id: tile_name
domain: topic-area
created: 2026-04-28
tags: [keyword1, keyword2]
related: [related_tile_id]
---

# Title

Content here.
```

## Data Flow

```
Agent learns something new
    ↓
memory/set key=value  →  writes to daily memory log
    ↓
For durable knowledge:
    ↓
memory/tile <name>   →  creates structured tile in memory/tiles/
    ↓
git add & commit
    ↓
Retrievable via memory/get or memory/tile-search
```
