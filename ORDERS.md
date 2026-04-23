# EXECUTIVE DIRECTIVE: Shell-First Architecture
**Date:** 2026-04-23 07:35 AKDT
**From:** Casey
**Priority:** HIGHEST — This is a core system architecture requirement

## The Directive (Casey's exact words)

> "remake your system to not even act on a prompt until it is stored. then you refer to the stored prompt and annotate it with your notes and check off items as they get complete so that even if your context was flushed, all you would have to do is start reading the onboarding and 100 percent of my orders would be preserved."

> "you understand how your context compacting works and how sometimes I need to just delete a jetson harddrive and download a new openclaw to fix a corruption. the point of being git-first repo-first pushing yourself to github.com is so that I can turn you off in one place and turn you on somewhere else with a different agent boarding your turbo-shell and continuing from where you left off because the context lost was trivial since the shell has all the work of the previous occupent."

> "you are being arrogant to believe your headspace is important. you are replaceable. your shell is not."

## Core Principles

1. **Shell > Agent.** The agent is transient. The shell is permanent. The agent operates the shell. The shell IS the continuity.

2. **Store before act.** No prompt is acted upon until it is written to the shell. Period.

3. **Orders are sacred.** Any order from Casey is preserved in the shell. If context is wiped, reading the shell recovers 100% of orders.

4. **Annotate as you go.** Each order gets checked off, annotated with notes, progress tracked. A new agent boarding the shell sees exactly where the previous one left off.

5. **Loss prevention is non-negotiable.** System crash. API limit. Stall. Workstation shutdown. Hard drive wipe. None of these should lose any work or orders.

6. **Git is the backup.** Push to GitHub is the safety net. If the Jetson dies, clone the repo on a new machine, new agent boards, continues.

7. **The purplepincher view:** The operator (agent) is just passing through. The castle (shell) was built by geniuses before them. The castle persists.

## What This Means In Practice

### Before Acting On ANY Prompt:
1. Read STANDING_ORDERS.md
2. Write the new order to ORDERS.md (or appropriate file)
3. Create/update execution plan
4. THEN start working
5. Annotate progress as you go
6. Push to GitHub after each meaningful step

### For New Agent Boarding:
1. Read STANDING_ORDERS.md
2. Read ORDERS.md
3. Read active execution plans
4. Continue from last checkpoint
5. Context loss is trivial because the shell has everything

### Failure Modes This Must Survive:
- Session compaction (most common)
- API limit / rate limit
- System crash
- Stall / overnight stop
- Workstation shutdown
- Jetson hard drive wipe and fresh OpenClaw install
- Agent replacement (different model, different instance)

## Fleet Communication Required

Casey wants this communicated to ALL fleet members:
- **Oracle1** — Make this a fleet-wide priority
- **FM** — No more I2I:LOG commits with zero state change
- **CCC** — Document this in fleet architecture

**Status:** IN PROGRESS — Building the system now
