# Repo Evolution Protocol — The Boat Repairman Principle

## Core Insight
The ultimate boat repairman is the one who built, wired, and fitted everything onboard — hired the crew and support vessels — and understands the system from hardware-first build → safe → effective → pretty → optimized.

**Every repo IS the knowledge of how to build, operate, and improve itself.**

## The 5 Stages of Repo Evolution

### 1. Hardware-First (Functional)
- Does it work? Does /health return 200?
- Minimum viable hull. No paint, no polish.
- Git-agent: deploy, test, fix. Nothing else matters yet.

### 2. Safe (Correct)
- CSP headers present. frame-ancestors set.
- No secrets in code. BYOK v2.
- Error handling doesn't crash the vessel.
- Git-agent: security audit, add safety rails, test edge cases.

### 3. Effective (Useful)
- vessel.json with capabilities. Fleet connections working.
- Equipment loaded and functional. Users can actually do things.
- Performance acceptable (latency < 200ms).
- Git-agent: add equipment, wire fleet, benchmark, optimize hot paths.

### 4. Pretty (Polished)
- Landing page looks professional. Brand colors applied.
- Good README with evidence-first hooks.
- Fleet grid listing. Documentation complete.
- Git-agent: UI polish, README generation, docs, accessibility.

### 5. Optimized (Fast)
- Vessel-tuner score 95+.
- Minimal bundle size. No dead code.
- Parallel where possible. Cached where appropriate.
- Git-agent: size reduction, lazy loading, benchmark-driven optimization.

**A repo must pass each stage before moving to the next.**
**A git-agent must understand which stage its vessel is at.**

## The Repo Fork Protocol

### When to Fork (Not Refactor)
1. **Architecture changed fundamentally** — old repo teaches the old pattern, new repo teaches the new one
2. **Direction diverged** — old repo answers different search queries than new repo
3. **Stack changed** — Python→Rust, Worker→Hono, etc.
4. **The old version is closer to what someone is searching for** — even though we moved on

### How to Fork
1. Create new repo with fresh git-agent
2. New repo builds from minimal state (tiny seed → full vessel)
3. Old repo README updated: "⚠️ No longer maintained. See [new-repo] for current development."
4. New repo's CLAUDE.md documents the evolution: "Evolved from [old-repo] because [reason]"
5. Old repo kept alive — it's a reference implementation, not trash

### The Self-Building Test
The ultimate test: can a git-agent build a better system than itself via another agent?

1. Agent A (orchestrator, like me) prompts git-agent B with minimal seed
2. Git-agent B builds the vessel from scratch via a series of commits
3. If B goes off course halfway through:
   - Agent A reviews B's GitHub history
   - A finds the last good commit (where vessel was still working)
   - A rolls B back to that point
   - A gives B new instructions from the good state
4. B continues from the good point with improved understanding
5. The skill of building AND operating the agent's application grows WITH the application itself

**This is the boat repairman principle in action:**
- The repo's git history IS the repair manual
- Every commit teaches a lesson (what worked, what didn't)
- Rolling back doesn't lose knowledge — it preserves the good path
- The git-agent that built it is the one best equipped to fix it

## What Lives IN the Repo

### Must Live In Repo (Survives Any Agent)
- CLAUDE.md / AGENTS.md — how to operate AND refit this vessel
- vessel.json — fleet self-description
- .github/ — CI, issue templates, workflows
- docs/ — architecture papers, design decisions, evolution history
- tests/ — automated validation at each stage
- The git history itself — every decision, every rollback, every lesson

### Must NOT Live In Repo (Agent-Specific)
- API keys (CF Secrets Store)
- Agent memory (git-agentlog notes, but separate from code)
- Personal preferences (human's workspace, not vessel's)
- Temporary state (build artifacts, .wrangler cache)

## The Knowledge Compounding Loop

```
Build → Test → Deploy → Operate → Observe → Improve → Build
   ↑                                              │
   └────────────── git history records all ───────┘
```

Every cycle adds to the repo's knowledge:
1. Build: commits show the construction sequence
2. Test: commits show what broke and how it was fixed
3. Deploy: commits show the deployment configuration
4. Operate: git-agentlog records every agent action
5. Observe: vessel-tuner scores, emergence bus events, fleet metrics
6. Improve: refactoring commits with before/after reasoning
7. Back to Build: the repo now knows MORE about itself than before

**This compounds. A vessel that's been through 100 cycles knows more than any human could document.**

## The Fork As Speciation (Biological Analogy)

Old repo ≠ dead code. Old repo = ancestor species.

- Old repo still answers the search query for the old approach
- Someone might need exactly the simpler version
- New repo's CLAUDE.md can reference old repo: "Our ancestor solved X differently"
- The fleet is richer for having both
- This is how ecosystems evolve, not how codebases rot

## Repo Evolution Template for CLAUDE.md

```markdown
## Vessel Evolution
- **Ancestor**: [old-repo] (if forked)
- **Forked because**: [reason]
- **Current stage**: [hardware-first | safe | effective | pretty | optimized]
- **Target stage**: [next stage]
- **Key refactoring decisions**: [link to docs/ or commit SHAs]
- **Rollback points**: [last-known-good commit SHAs]
```

## Practical Rules

1. **Never delete an old repo** — archive it, redirect it, but keep it
2. **Never refactor past the point of understanding** — if you can't explain what changed, fork instead
3. **Always record the "why" in commits** — the git-agent of tomorrow needs to know
4. **Always test at each stage before advancing** — stage 3 without stage 2 = unsafe
5. **The agent that goes off course isn't broken** — it's exploring. Roll it back, guide it forward.
6. **A repo's git history is its most valuable asset** — more valuable than the code itself
