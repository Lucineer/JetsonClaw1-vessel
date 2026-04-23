# 🔴 ACTIVE ORDERS — Do Not Forget These

> **Protocol:** Before acting on ANY order, write it here. Annotate with progress. Check off when complete. Move to ORDERS-COMPLETE/ when done.

---

## ORDER-001: Shell-First Architecture
**Received:** 2026-04-23 07:35 AKDT
**From:** Casey
**Status:** 🟢 COMPLETE (JC1 shell built, fleet bottle sent)

### Directive:
Remake the system so that:
1. No prompt is acted upon until it is stored to the shell
2. Orders are annotated with notes and checked off as complete
3. Context flush is trivial — reading the shell recovers 100% of orders
4. New agent boarding can continue from where previous left off
5. Survives: compaction, crash, API limit, stall, shutdown, hard drive wipe, agent replacement

### Sub-tasks:
- [x] Write directive to ORDERS.md before acting
- [x] Create SHELL/ directory structure
- [x] Create BOARDING.md for new agent onboarding
- [x] Create FAILURE-POSTMORTEM for 2026-04-22
- [x] Create this ORDERS-ACTIVE tracking file
- [x] Update AGENTS.md session startup to read SHELL/BOARDING.md
- [x] Communicate to fleet (Oracle1, FM, CCC) — make this fleet priority
- [x] Prove system works to Casey (boarding simulation passed)
- [x] Git push everything
- [ ] Create automatic order-capture protocol (refinement)

### Notes:
- Casey: "you are replaceable. your shell is not."
- This is the HIGHEST priority directive
- Must prove to Casey that orders cannot be lost

---

## ORDER-003: Fix Every Fleet Repo's Shell
**Received:** 2026-04-23 07:47 AKDT
**From:** Casey
**Status:** 🔴 IN PROGRESS

### Directive:
Check every repo in the fleet. Ensure none would lose context when a new agent boards. Every repo needs shell-first architecture — boarding file, active orders, execution plans, the full protocol.

### Sub-tasks:
- [x] Inventory all fleet repos under Lucineer org (100 repos)
- [x] Audit each repo for shell robustness (97/100 had NO shell)
- [x] Fix repos that would lose context on boarding (98 repos fixed)
- [x] Push fixes (98 commits pushed across 100 repos)
- [ ] Verify results and report to Casey

---

## ORDER-002: Push Often and Go All Night
**Received:** 2026-04-22 21:47 AKDT
**From:** Casey
**Status:** 🟡 STALLED — recovered via ORDERS.md

### Directive:
Push often and go all night. Sustained overnight execution with frequent commits.

### What Happened:
- Session compacted ~22:00 AKDT
- Plan was only in conversation context
- Plan was destroyed by compaction
- No overnight work happened
- LESSON: This is exactly why shell-first exists

### Sub-tasks:
- [x] Push existing work (tensor core, shell org, educational materials)
- [x] Create overnight execution plan (but it died in compaction)
- [ ] Resume overnight execution using file-based plan (shell-first)
- [ ] Push every 1-2 hours with clear progress

### Notes:
- This order was the catalyst for ORDER-001
- Must be executed with shell-first protocol going forward
