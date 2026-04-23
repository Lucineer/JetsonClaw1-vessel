# STANDING ORDERS

**This file is LAW. Read it first. Every session. No exceptions.**

## 🚨 RULE #1: WRITE THE PLAN DOWN BEFORE YOU START

When Casey gives a directive, plan, or instruction:

1. **STOP.** Do not start working.
2. **WRITE IT DOWN** in this file or `memory/YYYY-MM-DD.md` IMMEDIATELY.
3. **CONFIRM** you wrote it down by referencing the file in your reply.
4. **THEN** start executing, referring to the written plan, not your conversation context.

**Why:** Compaction destroys conversation context. Files survive compaction. If you don't write the plan down, compaction WILL kill it and you WILL forget. This has happened. It MUST NOT happen again.

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

### 2026-04-23 07:25 AKDT — Casey: "Get your house in order"
**Status:** IN PROGRESS
**Directive:** Set up safeguards to NEVER forget orders again before doing any project work
**What this means:**
1. Create this STANDING_ORDERS.md file ✅
2. Update AGENTS.md with hard rules about writing plans first
3. Create session startup that reads standing orders
4. Test the system works

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
