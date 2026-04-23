# SHELL — JC1's Persistent Castle

> "The operator is just passing through. The castle was built by geniuses before them."
> — Casey, 2026-04-23

## What This Directory Is

This is the shell. It survives compaction, crashes, API limits, stalls, hard drive wipes, and agent replacement. Everything an agent needs to continue work lives here.

A new agent boarding this shell should:
1. Read `BOARDING.md` — start here
2. Read `../STANDING_ORDERS.md` — active directives
3. Read `../ORDERS.md` — all orders from Casey
4. Read `../memory/YYYY-MM-DD.md` — today's log
5. Read active execution plans
6. Continue from last checkpoint

## Directory Structure

```
SHELL/
├── BOARDING.md              # New agent start here
├── FAILURE-POSTMORTEM/      # What went wrong, why, how to prevent
├── ORDERS-ACTIVE/           # Currently executing orders (check off as complete)
├── ORDERS-COMPLETE/         # Finished orders (archive)
├── EXECUTION-PLANS/         # Detailed plans for complex work
├── KNOWLEDGE/               # Distilled learnings, not daily logs
├── FLEET-COORDINATION/      # Bottles, fleet communication records
└── PROGRESS/                # Checkpoint files, push records
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
