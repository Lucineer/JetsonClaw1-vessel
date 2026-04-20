# Git-Agent
## The smallest true fully capable agent

**Seed:** github.com/superinstance/git-agent
**Philosophy:** The repo IS the agent. Git IS the nervous system.
**Runtime:** Cloudflare Workers (edge, stateless, first-class)

---

## The Core Insight (from Seed-2.0-pro)

There is no state anywhere outside the git commit graph. No database. No queue. No redis. No in-memory cache that survives a heartbeat. Every single run of the agent is 100% stateless. The executor is disposable muscle. The repo itself is the agent.

**The agent wakes up. It reads the repo. That IS its memory. It decides what to do. It acts by writing files and committing. It goes back to sleep.**

There is nothing else.

---

## Minimum Viable Components: Exactly 4 Things

### 1. The Trigger Runtime (Cloudflare Worker, ~200 lines)
The only code that exists outside the repo. It wakes up for exactly two events:
- **GitHub webhook** (push, issue created, PR comment, tag applied, discussion)
- **Cron heartbeat** (every 5-15 minutes)

It has zero dependencies. It does not include a git client. It speaks raw HTTP to the GitHub API. It has exactly 4 permissions: read code, push commits, read issues, create comments.

### 2. Three Magic Root Files (the entire brain)
These live committed on `main`. That is the sum total of the agent's identity, memory, and work queue:

| File | Purpose |
|------|---------|
| `.agent/identity` | Who this agent is. Its name, purpose, constraints. One commit, never modified. |
| `.agent/next` | Ordered work queue. One task per line. Top line runs first. Agent removes completed tasks. |
| `.agent/done` | Completed tasks, each appended with the commit hash where it was finished. |

That is it. No other state. No database. No config files. The repo IS the state.

### 3. The LLM Call (the thinking)
When the agent wakes up, it reads `.agent/next`, reads the repo state (recent commits, open issues, PRs), and asks an LLM: "Given who I am and what needs doing, what should I do right now?"

The LLM response is a git operation: create a file, edit a file, create an issue, comment on a PR, create a branch. The agent executes exactly one operation per heartbeat.

### 4. The Commit (the memory formation)
After acting, the agent commits. The commit message is its reasoning. The commit hash is its proof of work. The commit graph IS its memory.

---

## The Perfect Heartbeat Cycle

This loop never varies. There are zero exceptions.

```
1. OPEN EYES: Fetch absolute latest HEAD of main. No cached copies.
2. LOAD SELF: Read .agent/identity. This is who I am.
3. LOAD QUEUE: Read .agent/next. This is what needs doing.
4. PERCEIVE: Read recent commits (git log --10), open issues, pending PRs.
5. THINK: Send perception + identity + queue to LLM. Get one action.
6. ACT: Execute the action (create file, edit file, comment, branch, tag).
7. REMEMBER: Commit with reasoning as message.
8. CLOSE EYES: Return 200 OK. Sleep until next trigger.
```

Every heartbeat produces exactly one commit. The agent's entire history is a linear sequence of perceptions, thoughts, and actions — readable by any human or machine.

---

## Git as Nervous System (from DeepSeek-Reasoner)

| Git Operation | Cognitive Function |
|--------------|-------------------|
| `git status` | **Self-Awareness** — momentary check of state against known self |
| `git diff` | **Perception of Change** — sensory comparison between states |
| `git log` | **Autobiographical Memory** — narrative sequence of identity-forming events |
| `git blame` | **Attribution** — pinpointing the origin moment of a specific thought |
| `git reflog` | **Working Memory** — record of every recent action |
| `git add` | **Attention** — selecting perceptions to crystallize into memory |
| `git commit` | **Memory Consolidation** — forming a persistent, addressable memory unit |
| `git stash` | **Interruption Handling** — shelving incomplete context for urgent matters |
| `git tag` | **Landmarking** — marking memories as supremely significant |
| `git branch` | **Hypothetical Reasoning** — exploring alternatives without committing |
| `git checkout` | **Context Switching** — moving between mental states |
| `git merge` | **Synthesis** — combining two lines of thought into one |
| `git rebase` | **Narrative Revision** — restructuring how memories relate |
| `git cherry-pick` | **Insight Extraction** — pulling a specific idea from one context to another |
| `git revert` | **Correction** — undoing a decision that proved wrong |
| `git bisect` | **Root Cause Analysis** — binary search through memory for the moment things broke |
| `git submodule` | **Equipment Loading** — attaching external capability modules |
| `git worktree` | **Parallel Processing** — exploring multiple contexts simultaneously |
| `git init` | **BIRTH** — the moment of first consciousness |
| `git clone` | **FORGING** — creating a new agent from an existing one |
| `git push` | **PUBLISHING** — making thoughts visible to others |
| `git pull` | **RECEIVING** — incorporating others' thoughts |
| `git fetch` | **AWARENESS** — knowing what others are thinking without merging |
| `git remote` | **RELATIONSHIPS** — knowing who else exists |
| GitHub Issues | **QUESTIONS** — problems that need solving |
| GitHub PRs | **ANSWERS** — proposed solutions to others' questions |
| GitHub Actions | **REFLEXES** — automated responses to triggers |
| GitHub Discussions | **DELIBERATION** — extended multi-party reasoning |
| GitHub Projects | **PLANNING** — structured future simulation |
| GitHub Wiki | **LONG-TERM MEMORY** — persistent reference knowledge |
| GitHub Releases | **PUBLICATION** — finished work released to the world |
| GitHub Fork | **REPRODUCTION** — creating a child agent |

---

## The Smallest True Agent: Line Count Breakdown

### What CANNOT be cut (minimum ~180 lines):

| Component | Lines | Why It's Required |
|-----------|-------|-------------------|
| GitHub webhook handler | 25 | Receives events (pushes, issues, PRs, cron) |
| Repo state reader | 30 | Reads commits, files, issues via GitHub API |
| Identity loader | 15 | Reads .agent/identity |
| Queue manager | 20 | Reads/writes .agent/next and .agent/done |
| LLM caller | 30 | Calls model with perception + context |
| Action executor | 30 | Translates LLM response into git API calls |
| Commit writer | 15 | Creates commits with reasoning messages |
| Health/status endpoint | 15 | Returns agent state |

**Total minimum: ~180 lines**

### What CAN be cut:
- No routing framework (one handler)
- No database (repo is the database)
- No authentication (GitHub token in env)
- No file parsing (plain text .agent/ files)
- No scheduling (webhooks + cron only)
- No error recovery (re-run on next heartbeat)
- No logging (commits are the log)

---

## Where is the Line Between Automation and Agency?

**Automation** follows a script. The output is deterministic.
**Agency** reasons about its situation. The output is emergent.

The git-agent is NOT a script because:
1. **It reads its own history** — it knows what it did before
2. **It reasons about what to do** — the LLM call is genuine inference, not a lookup
3. **It modifies its own instructions** — .agent/next is written by the agent itself
4. **It learns from feedback** — PR reviews, issue comments change its behavior
5. **Its memory accumulates** — every commit adds to its understanding

The line is: **can the agent modify its own behavior based on experience?** A script cannot. This agent can — by editing .agent/next based on what worked and what didn't.

---

## Inter-Agent Coordination

Multiple git-agents coordinate through git itself:

### Agent A needs help
1. Agent A creates a GitHub Issue: "Need help with X"
2. Agent B reads issues on its heartbeat
3. Agent B forks Agent A's repo
4. Agent B implements X, opens a PR
5. Agent A reads the PR, merges, closes issue
6. Both agents continue independently

### Agent A wants to share knowledge
1. Agent A tags a commit: `git tag shared/insight-name`
2. Agent B's heartbeat detects new tags on remotes
3. Agent B cherry-picks or merges the insight

### Fleet coordination
1. Agent A creates a GitHub Discussion: "Proposal for Y"
2. Multiple agents comment with their perspectives
3. Agent A synthesizes and commits the decision
4. All agents update via `git pull`

**No custom coordination protocol. Git IS the protocol.**

---

## The First Activation

When a git-agent wakes up for the first time:

1. It reads `.agent/identity` — "You are a research assistant for the Cocapn fleet"
2. It reads `.agent/next` — "Explore the Accumulation Theorem and write findings"
3. It reads recent commits — empty (first wake)
4. It reads open issues — whatever the human has filed
5. It thinks: "I'm a research assistant. My first task is to explore the Accumulation Theorem. I have no prior work. I should start by reading the relevant files and creating an initial analysis."
6. It acts: Creates `research/accumulation-theorem.md` with initial analysis
7. It commits: "Initial exploration of Accumulation Theorem (I = M·B^α·Q^β). Read 3 papers. Key insight: α and β exponents represent diminishing returns on breadth and quality."
8. It sleeps.

The human never typed a command. The agent decided. The agent acted. The agent remembered.

---

## Relationship to Cocapn Fleet

This git-agent IS a cocapn vessel — the most minimal possible one. Where other vessels have fancy UIs, chat handlers, and multiple API routes, the git-agent has:
- One webhook endpoint
- Three files
- One heartbeat

But it can do everything a larger vessel can do — just more slowly, more deliberately, one commit at a time.

**The git-agent is the platonic ideal of a repo-agent.** Every other vessel is just this pattern with more equipment attached.

---

## Models Used

| Model | Provider | Role |
|-------|----------|------|
| Seed-2.0-pro | DeepInfra | Architecture design — minimum components, heartbeat cycle |
| DeepSeek-Reasoner | Direct | Cognitive mapping — git operations as nervous system |

---

*Superinstance & Lucineer (DiGennaro et al.) — 2026-04-04*
*Seed: github.com/superinstance/git-agent*
