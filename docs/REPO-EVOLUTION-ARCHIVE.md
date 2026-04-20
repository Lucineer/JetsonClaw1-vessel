# Repo Evolution Archive — Superseded Repos

## Purpose
When a repo's architecture fundamentally changes, we FORK to a new repo (not refactor in place).
The old repo stays alive as a reference. This doc tracks all evolutions.

## Evolution History

| Old Repo | New Repo | Why | Status |
|----------|----------|-----|--------|
| cocapn-lite | the-seed | Seed architecture supersedes lite (self-contained, self-evolving) | Archive cocapn-lite |
| (future) | (future) | | |

## Archive README Template
For each superseded repo, add to its README.md:

```markdown
> ⚠️ **This project is no longer actively maintained.**
>
> This vessel has been superseded by **[new-repo]** which implements [improvement reason].
> The code here still works and may be useful if you need [old approach].
> For current development, see: github.com/Lucineer/[new-repo]

---

[rest of original README preserved below]
```

## Rules
1. Never delete old repos — archive them
2. Always link old → new in README
3. Old repo still deployed and functional
4. New repo starts fresh with improved git-agent procedure
5. The old repo's git history IS the training data for the new repo's agent
