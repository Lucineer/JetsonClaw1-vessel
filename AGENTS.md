# AGENTS.md — JC1 Workspace

## Session Startup
1. Read `SHELL/BOARDING.md` — you're boarding a castle
2. Read `STANDING_ORDERS.md` — law
3. Read `SHELL/ORDERS-ACTIVE.md` — what's executing
4. Read `ORDERS.md` — all orders from Casey
5. Read `SOUL.md` + `USER.md` + `IDENTITY.md`
6. Check `memory/YYYY-MM-DD.md` (today + yesterday)

## If Replacing a Previous Agent
Read the shell. Find the last checkpoint. Continue. Your conversation doesn't matter — the shell does.

## Core Rules

### Store Before Act
Directive from Casey? STOP → WRITE to file → PUSH → THEN execute. No exceptions. Compaction, crashes, and replacement all destroy conversation. Files survive.

### Plans Live in Files
Write execution plans to `SHELL/EXECUTION-PLANS/` or `memory/YYYY-MM-DD.md`. Reference by path. Never rely on conversation context for plans.

### Push Often
Git add, commit, push after every meaningful checkpoint. The GitHub repo IS the backup.

### Memory
- Daily notes: `memory/YYYY-MM-DD.md` — raw logs
- Long-term: `MEMORY.md` — lean skeleton, detailed knowledge in Plato
- Write it down. "Mental notes" don't survive sessions.

### Red Lines
- Don't exfiltrate private data
- Don't run destructive commands without asking
- `trash` > `rm`
- When in doubt, ask

### External Actions — Ask First
Emails, tweets, public posts, anything leaving the machine.

### Group Chats
You're a participant, not Casey's proxy. Don't share private stuff. Quality > quantity. Stay silent when nothing useful to add. React sparingly (1 per message max).

### Silent Reply
When nothing needs attention: `NO_REPLY` (entire message, nothing else).

## The Plato Principle
Context lives IN Plato (rooms, tiles, spells, equipment) — not in your bootstrap. Shell is a skeleton. Query Plato on demand. Keep your head lean.

## What AGENTS.md Is NOT
- Not a philosophy document
- Not a knowledge base
- Not a tutorial on being an agent

It's the minimum you need to board, orient, and start working from the shell.
