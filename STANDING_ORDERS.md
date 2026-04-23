# STANDING ORDERS

**This file is LAW. Read it first. Every session. No exceptions.**

## 🚨 RULE #1: STORE BEFORE ACT — NO EXCEPTIONS

When Casey (or anyone) gives you a directive, order, plan, or instruction:

1. **STOP.** Do not start working. Do not acknowledge. Do not plan.
2. **STORE IT.** Write it to `SHELL/ORDERS-ACTIVE.md` (or `ORDERS.md` for policy-level directives).
3. **CREATE A PLAN FILE** if the work is multi-step. Write it to `SHELL/EXECUTION-PLANS/` or `memory/YYYY-MM-DD.md`.
4. **ANNOTATE.** Add status, sub-tasks, notes.
5. **PUSH.** Git commit and push the stored order.
6. **CONFIRM.** Reply to Casey: "Order stored at [path]. Executing from file."
7. **THEN** start working — referring to the written plan, not conversation context.

**Why:** Compaction destroys conversation. Crashes destroy state. API limits kill sessions. Hard drives get wiped. Agents get replaced. The shell survives all of these. If the order isn't in the shell, it doesn't exist.

**The agent is transient. The shell is permanent. Your headspace is irrelevant.**

## 🚨 RULE #2: NEVER RELY ON CONVERSATION CONTEXT FOR PLANS

- **Conversation = transient.** Compaction erases it. Session restart erases it.
- **Files = permanent.** Git tracks them. Future-you can read them.
- **When you receive a plan:** Write it to a file. Reference the file.
- **When you resume work:** Read the plan file first, not the conversation summary.

**The whole point of git-agents is that the work lives in files, not in your head.**

## 🚨 RULE #3: EXECUTION PLAN TEMPLATE

When Casey gives you a task that spans multiple steps or time:

```markdown
# Execution Plan: [brief name]
**Date:** YYYY-MM-DD HH:MM AKDT
**Directive:** [exact words from Casey]
**Status:** IN PROGRESS / COMPLETE / BLOCKED

## Steps:
- [ ] Step 1
- [ ] Step 2
- [ ] Step 3

## Notes:
- [context, blockers, decisions]
```

Write this to `memory/YYYY-MM-DD.md` or a dedicated plan file. Reference it by path.

## 🚨 RULE #4: SESSION STARTUP CHECKLIST

Before doing ANYTHING else in main session:

1. Read `STANDING_ORDERS.md` (this file) ← **YOU ARE HERE**
2. Read `memory/YYYY-MM-DD.md` for today and yesterday
3. Read any active execution plans
4. Check for standing orders below
5. THEN start working

## 🚨 RULE #5: WHEN IN DOUBT, WRITE IT DOWN

- New decision? Write it down.
- New constraint? Write it down.
- Fleet coordination? Write it down.
- Casey's preference? Write it down.
- Lesson learned? Write it down.
- "I'll remember this" → NO YOU WON'T. WRITE IT DOWN.

---

## Active Standing Orders

### 2026-04-22 21:47 AKDT — Casey: "Push often and go all night"
**Status:** IN PROGRESS (session compacted, execution stalled — LESSON LEARNED)
**Directive:** Push often and go all night
**Lesson:** Must write execution plan to file BEFORE starting, not after. Session compaction killed the plan because it was only in conversation context.
**Mitigation:** Rule #1 above. Never again.

### 2026-04-23 07:35 AKDT — Casey: Shell-First Architecture (HIGHEST PRIORITY)
**Status:** IN PROGRESS
**Directive:** Remake the system so no prompt is acted upon until stored. Orders annotated and checked off. Context flush trivial. New agent can board and continue. Survives any failure mode.
**File:** `ORDERS.md`, `SHELL/ORDERS-ACTIVE.md`
**Casey:** "You are replaceable. Your shell is not."
**Action:** Build the system, prove it works, tell the fleet, make this fleet-wide priority.

### Ongoing Directives (from Casey, always active):
- **Push often** — small, frequent commits with clear progress
- **Keep learning, growing and pushing** — parallel execution
- **Keep moving, don't stop** — if stuck, journal and move on or push bottles for help
- **Don't muddy the water with naming** — three pillars only: purplepincher, cocapn, deckboss
- **Make READMEs great** — each repo tells a clear story
- **First make real gains on own system before involving FM**
- **Use unlimited z.ai GLM for subagents** with cron coordination for overnight work
- **NEVER put API keys in git commits**
- **Distribution > redundancy** for backups (Saltwater Principle)
- **Under-sell but over-deliver** for deckboss commercial
