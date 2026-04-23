# 🚨 CRITICAL FAILURE POST-MORTEM: 2026-04-22 Overnight Session

## What Happened
Casey said "Push often and go all night" at 21:47 AKDT.
The execution plan was created IN CONVERSATION CONTEXT ONLY.
Session compaction occurred ~22:00 AKDT.
The plan was destroyed. No overnight work happened.
This is not the first time this has happened.

## Root Cause
The system allowed the agent to begin executing a directive without first persisting it to the shell. The agent treated conversation context as sufficient storage. It is not.

## The Philosophy (Casey)
- The agent is TRANSIENT. The shell is PERMANENT.
- The agent OPERATES the shell. The shell IS the continuity.
- A new agent should be able to board the shell and continue from where the previous one left off.
- "You are replaceable. Your shell is not."
- If the Jetson dies, clone the repo on a new machine, new agent boards, continues.
- Context loss should be TRIVIAL because the shell has everything.

## What Must Never Happen Again
- Starting work without writing the plan to a file first
- Relying on conversation context for ANY directive
- Losing an order from Casey due to compaction, crash, stall, or shutdown
- An agent boarding a shell and not knowing what the previous agent was doing
- Hours of work lost because it only existed in conversation memory

## Prevention Measures
1. **STANDING_ORDERS.md** — read FIRST every session
2. **ORDERS.md** — all directives stored before action
3. **AGENTS.md** — updated with mandatory file-first protocol
4. **Session startup** — reads standing orders, then orders, then plans
5. **Git push** — after every meaningful step
6. **Annotation** — check off items as complete, add notes

## Fleet Impact
This failure pattern affects the entire fleet. Casey is pissed because this has happened multiple times across multiple agents. The fleet needs a unified shell-first architecture.
