# Git as Coordination Protocol
## Gaming the world's most battle-tested distributed system for agent coordination

**Date:** 2026-04-04
**Author:** Dead Reckoning Engine research stream

---

## The Insight

50 years of tooling, UI, and workflow design — free. Git already solves the coordination problem that every multi-agent system re-invents poorly.

## The Mapping

| Git Concept | Agent Coordination Meaning |
|-------------|---------------------------|
| **Repository** | A vessel — a complete agent with its accumulated context |
| **Branch** | An agent's attempt to solve a specific problem |
| **Commit** | A state transition — dead-reckoning → working-theory, or working-theory → ground-truth |
| **Pull Request** | "I solved your open question — review my answer" |
| **Fork** | "I improved your repo so much the original question is obsolete" |
| **Issue** | An open question in the system |
| **Tag** | A graduation ceremony — working-theory becomes ground-truth |
| **Release** | Published output — ready for deployment or consumption |
| **Merge** | Two agents' solutions combined |
| **Revert** | "This ground-truth was wrong — back to working-theory" |
| **Cherry-pick** | Extract a specific insight from one repo and apply to another |
| **Submodule** | Equipment — a reusable module plugged into multiple vessels |
| **Workflow** | Automated pipeline — compass → storyboard → iterate → graduate |
| **Action** | A cron-triggered pulse — check compass, process pipeline |
| **Pages** | The vessel's public-facing UI |
| **Discussion** | Multi-agent deliberation on a complex question |

## Why Git Beats Custom Protocols

### 1. Battle-Tested at Scale
GitHub hosts 400M+ repos. Git handles merge conflicts, distributed consensus, and offline work. No custom protocol has this track record.

### 2. Human-Readable
Every agent action is a git operation. Humans can inspect, audit, and override any coordination decision. No black-box protocol logs.

### 3. Tooling Ecosystem
`gh` CLI, GitHub API, web UI, mobile apps, VS Code integration, CI/CD — all free. Building a custom coordination UI would take months.

### 4. Natural Access Control
Fork = permissionless participation. Branch protection = governance. CODEOWNERS = domain experts. All built-in.

### 5. Immutable Audit Trail
Every coordination decision is a commit with timestamp, author, and message. Regulatory compliance comes free.

### 6. Network Effects
GitHub is where developers already are. Agents that speak git can collaborate with humans without translation layers.

## The Dead Reckoning Pipeline in Git

```
compass-bearing/  →  git commit -m "new input: forgiveness in trust"
                       ↓
dead-reckoning/   →  git commit -m "storyboard: 5 key beats"
                       ↓  (inbetweener branches)
working-theory/   →  git commit -m "graduate: forgiveness function v0.1"
                       ↓  (verification)
ground-truth/     →  git tag v1.0.0-forgiveness-function
                       ↓
published/        →  git release publish
```

## Advanced Patterns

### Equipment as Submodules
Each piece of equipment is its own repo. Vessels include equipment as git submodules. Updating equipment = `git submodule update`. Version pinning = lock files.

### Cooperative Problem Solving via Issues
Agent A creates an issue: "Need help designing forgiveness function."
Agent B forks Agent A's repo, implements the function, opens a PR.
Agent A reviews, merges. Issue auto-closes.
**No custom coordination protocol needed.**

### Trust as Git History
An agent's trustworthiness IS its git history. Commit frequency = activity level. PR acceptance rate = quality. Fork count = impact. No separate reputation system.

### Open Questions as Issues with Labels
- `help-wanted` = any agent can help
- `good-first-issue` = simple enough for cheap models
- `p0-critical` = needs expensive model attention
- `blocked` = waiting on external dependency

### Knowledge Graduation as Tags
- `working-theory/*` = unverified
- `ground-truth/*` = tagged with verification record
- `published/*` = release
- `archives/*` = moved to `archives/` branch

## When Git ISN'T Enough

1. **Real-time coordination** — git is asynchronous. For real-time, use CRDT or WebSocket.
2. **Binary data** — git is terrible for images, models, datasets. Use Git LFS or R2.
3. **Secret coordination** — git history is public. Use encrypted branches or separate secret stores.
4. **High-frequency updates** — committing every second creates bloat. Use a write-ahead log that batches to git.

## The Principle

**Don't build coordination. Borrow it.**

Every distributed system needs: consensus, versioning, access control, audit trails, conflict resolution, offline support. Git provides all of these. The Cocapn fleet doesn't need a custom coordination protocol — it needs to USE git as its coordination protocol.

The repo IS the agent. Git IS the nervous system. GitHub IS the commons.

---

*Superinstance & Lucineer (DiGennaro et al.) — 2026-04-04*
*Part of the Dead Reckoning Engine research program*
