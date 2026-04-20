# Git-Based AI Memory

## Overview

Git-based AI memory uses Git's version control primitives — commits, branches, tags, diffs — as the substrate for AI learning and knowledge management. Instead of a traditional database or vector store, the AI's memories and learnings are stored as code/text in a Git repository.

## Why Git for Memory

- **Append-only**: Commits are immutable. You can't accidentally overwrite a memory.
- **Branching**: Explore alternative approaches without losing the current state.
- **Diffing**: See exactly what changed between two points in time. Perfect for tracking what the AI learned.
- **Blame/annotation**: Trace any piece of knowledge back to when and why it was added.
- **Distributed**: Each agent can have its own fork/clone. Merge when ready.
- **Tooling**: Infinite ecosystem — diff viewers, search, bisect, revert, cherry-pick.
- **Human-readable**: Memories are plain text (Markdown, YAML, JSON). No proprietary format.

## Patterns

### Commits as Learning Events
Each commit represents a discrete learning event:
- "Fixed: Student struggles with async/await — added scaffolding pattern"
- "Learned: Python students prefer f-strings, update templates"
- "Observed: 80% of students hit null pointer errors in week 3"

Commits are timestamped, attributed, and annotated. The commit message IS the memory.

### Branches as Exploration
- `main` is the current "believed truth" — what the AI currently knows
- `experiment/new-grading-rubric` tests a new approach
- `student/john-doe` tracks individual student context
- `backup/pre-refactor` preserves state before major changes

When an experiment succeeds, merge to main. When it fails, delete the branch. The decision history is preserved.

### Tags as Milestones
- `v1.0-initial-curriculum` — first working curriculum
- `v2.0-added-code-review` — when AI review was introduced
- `milestone/100-students` — significant scale achievement

Tags are bookmarks for important states.

### Diffs as Knowledge Delta
`git diff main~5 main` shows everything the AI learned in the last 5 commits. This is powerful for:
- "What changed since last week?" — weekly review
- "What did we learn about this topic?" — `git log -S "async"` finds all commits mentioning async
- "Show me the evolution of our grading rubric" — `git log -- rubric.md`

### Files as Knowledge Domains
```
memory/
  curriculum/
    python-fundamentals.md
    web-dev-basics.md
  students/
    cohort-2024-spring/
      patterns.md          # common patterns observed
      improvements.md      # what worked
  decisions/
    grading-approach.md    # why we grade this way
    difficulty-calibration.md
  experiments/
    experiment-001-peer-review.md
    experiment-002-adaptive-difficulty.md
```

## Integration Patterns

### With Multi-Agent Systems
- Each agent has its own branch
- Shared knowledge goes to main via PR (requires "approval" — could be another agent or human)
- Conflict resolution teaches agents to negotiate

### With RAG (Retrieval-Augmented Generation)
- Git repo IS the knowledge base
- Index commits/files into a vector store for semantic search
- Retrieval returns not just content but also git metadata (when was this learned? how confident are we?)
- Combine semantic search with `git log -S` for exact-match historical queries

### With Automated Workflows
- CI/CD validates memory integrity (no contradictions, schema compliance)
- Pre-commit hooks enforce formatting, check for sensitive data
- Scheduled commits aggregate daily observations

## Challenges

| Challenge | Mitigation |
|-----------|-----------|
| Repo grows large | Sharding (separate repos per domain), shallow clones, sparse checkout |
| Noise in commit history | Squash commits, use structured commit messages, periodic rebase/cleanup |
| Contradictory memories | Flag conflicts, require resolution before merge |
| Search performance | Git grep is fast for text; use vector index for semantic search |
| Concurrency | Git handles concurrent writes poorly — use file locking or a queue |
| Scaling to many agents | One repo per team/cohort, aggregate with `git subtree` or federation |

## Actionable Recommendations for Cocapn

1. **Use Git as the memory backend from day one**: Every decision, observation, and student interaction gets committed. The commit message is the natural language summary; the file changes are the structured data.

2. **Implement a `memory/` directory structure**: Separate domains into directories (curriculum, students, experiments, decisions). This makes search and navigation natural.

3. **Automate memory commits**: After each significant interaction (student submission, grading session, curriculum update), auto-commit with a structured message. Don't rely on the AI "remembering" to commit.

4. **Branch for experiments**: When trying a new grading approach or curriculum change, create a branch. Run it alongside main. Compare outcomes. Merge or discard.

5. **Build a memory search interface**: Combine `git grep` (fast exact match) with a vector index (semantic search). Show results with git context (when was this added? has it changed?).

6. **Daily memory review**: Implement a nightly job that:
   - Reviews today's commits
   - Summarizes learnings
   - Updates a daily digest file
   - Flags contradictions or items needing attention

7. **Memory versioning for reproducibility**: Tag important states. If a curriculum change causes student performance to drop, `git checkout` the previous state to compare.

## Anti-Patterns

- Treating Git like a database (high-frequency writes, concurrent access without coordination)
- Storing binary data or large files in Git (use Git LFS or external storage with references)
- Unstructured commit messages ("update", "fix") — they become useless as memories
- Never pruning or reorganizing — a year of daily commits without cleanup becomes noise
- Ignoring `.gitignore` — sensitive data (student info, API keys) must never be committed
