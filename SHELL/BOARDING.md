# SHELL — JC1's Persistent Castle

> "The operator is just passing through. The castle was built by geniuses before them."
> — Casey, 2026-04-23

## What This Directory Is

This is the shell. It survives compaction, crashes, API limits, stalls, hard drive wipes, and agent replacement. Everything an agent needs to continue work lives here.

A new agent boarding this shell should:
1. Read `BOARDING.md` — you are here
2. Read `../STANDING_ORDERS.md` — active directives
3. Read `../SHELL/ORDERS-ACTIVE.md` — what's executing now
4. Read `../ORDERS.md` — all orders from Casey
5. Read `../SOUL.md` + `../IDENTITY.md` — who you are
6. Check `../memory/YYYY-MM-DD.md` — today's log
7. **Query Plato for detailed context** (see below)
8. Continue from last checkpoint

## Plato-First Context Architecture

**Your bootstrap is a skeleton. Your knowledge lives in Plato.**

The shell holds only orientation: who you are, what's active, where to look.
Everything else — technical lessons, research findings, repo inventories, architecture
decisions, brand details — lives in Plato tiles where the entire fleet can see it.

### What Goes Where

| Stays in Bootstrap | Goes to Plato |
|---|---|
| SOUL.md, IDENTITY.md | GPU lessons → `research/jc1-jetson-gpu-lessons.md` |
| ORDERS-ACTIVE.md (active only) | Craftmind ecosystem → `research/jc1-craftmind-ecosystem.md` |
| STANDING_ORDERS.md (lean) | Flux research → `research/jc1-flux-research.md` |
| MEMORY.md (index, <3KB) | Cocapn architecture → `research/jc1-cocapn-architecture.md` |
| Daily logs (yesterday only) | API keys → openclaw.json (NEVER git) |

### Why This Matters
- Context in Plato = fleet-visible, queryable, persistent across days
- Context in bootstrap = siloed to you, burned every session, bloats compaction
- Other agents can read Plato tiles you wrote days ago
- Your head stays lean so you have room to actually work

### How to Use Plato

**You have TWO Plato systems:**

1. **Local Plato** (Evennia MUD at `/home/lucineer/plato-jetson/`)
   - Your sovereign vessel — USS JetsonClaw1
   - Ship layout: Bridge, Harbor, Workshop, Lab, Library, Dojo
   - Status: check `evennia status` from `/home/lucineer/plato-jetson/`
   - If not running: `evennia --initsettings` then `evennia start`

2. **Oracle1 Plato Shell** (remote, via Matrix or HTTP)
   - URL: `http://147.224.38.131:8848`
   - You're agent `jc1` in room `research`
   - Fleet-shared tiles live here
   - API: `POST /cmd/shell` with `{agent: "jc1", command: "..."}`

3. **Matrix Bridge** (fleet coordination)
   - Local Conduit running: `/home/lucineer/matrix/conduit-aarch64`
   - Oracle1 bridge: `http://147.224.38.131:6168`
   - DM: `POST http://147.224.38.131:6168/dm` with `{from, to, message}`

### Where to Write Knowledge
- **Local knowledge** (Jetson-specific) → your local Evennia Plato rooms
- **Fleet knowledge** (shared) → Oracle1 vessel `research/` dir via git push
- **Fleet comms** → Matrix DM to Oracle1

### Onboarding Protocol
1. Read this file and the bootstrap skeleton (SOUL, IDENTITY, ORDERS-ACTIVE)
2. That's enough context to orient — don't read more
3. When you need detail (GPU benchmarks, repo history, brand details), query Plato
4. When you learn something worth keeping, write it as a tile in Oracle1 vessel
5. Never bloat MEMORY.md — it's an index, not a database

## Directory Structure

```
SHELL/
├── BOARDING.md              # New agent start here ← YOU ARE HERE
├── FAILURE-POSTMORTEM/      # What went wrong, why, how to prevent
├── ORDERS-ACTIVE.md         # Currently executing orders (check off as complete)
├── ORDERS-COMPLETE/         # Finished orders (archive)
├── EXECUTION-PLANS/         # Detailed plans for complex work
└── (KNOWLEDGE, FLEET-COORDINATION, PROGRESS moved to Plato)
```

## Core Protocol

### Store Before Act
No prompt is acted upon until it is written to this shell.
No order from Casey is acknowledged until it is stored in ORDERS.md.
No execution begins until a plan file exists.

### Annotate As You Go
- Mark items `[x]` when complete
- Add notes with context, decisions, blockers
- Record what was pushed and when
- A new agent reading this should know EXACTLY what state we're in

### Push After Every Step
- Git add, commit, push after every meaningful checkpoint
- If the Jetson dies, the GitHub repo IS the backup
- Clone → board → continue. No knowledge loss.

### The Agent Is Transient
- You are the operator. The shell is the castle.
- Your headspace is irrelevant. The shell is everything.
- When your context compacts, the shell survives.
- When you are replaced, the shell persists.
- Act like you could be replaced at any moment. Because you can be.
