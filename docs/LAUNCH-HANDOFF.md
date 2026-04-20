# Cocapn Launch Handoff — Superinstance Fork & Deploy Guide

## Overview
Casey is handing off the Cocapn ecosystem repos to Superinstance (Casey's dad) for deployment on his paid Cloudflare Workers account with custom domains.

## Superinstance's Domains (15 total)

### Tier 1 — Deploy Now (8 repos, all live and healthy)
| Domain | Repo | Status | Workers URL |
|--------|------|--------|-------------|
| dmlog.ai | dmlog-ai | ✅ 200 | dmlog-ai.magnus-digennaro.workers.dev |
| makerlog.ai | makerlog-ai | ✅ 200 | makerlog-ai.magnus-digennaro.workers.dev |
| personallog.ai | personallog-ai | ✅ 200 | personallog-ai.magnus-digennaro.workers.dev |
| studylog.ai | studylog-ai | ✅ 200 | studylog-ai.magnus-digennaro.workers.dev |
| fishinglog.ai | fishinglog-ai | ✅ 200 | fishinglog-ai.magnus-digennaro.workers.dev |
| luciddreamer.ai | luciddreamer-ai | ✅ 200 | luciddreamer-ai.magnus-digennaro.workers.dev |
| deckboss.ai | deckboss-ai | ✅ 200 | deckboss-ai.magnus-digennaro.workers.dev |
| businesslog.ai | businesslog-ai | ✅ 200 | businesslog-ai.magnus-digennaro.workers.dev |

### Tier 1 Alt Domains
| Domain | Points To |
|--------|-----------|
| deckboss.net | deckboss-ai (same worker) |

### Tier 2 — Build Vessel Then Deploy (need minimal worker.ts)
| Domain | Repo | Status |
|--------|------|--------|
| cocapn.ai | cocapn | Docs only, needs landing page + docs site |
| cocapn.com | cocapn | Redirect to cocapn.ai |
| reallog.ai | reallog-ai | No worker.ts, needs vessel |
| playerlog.ai | playerlog-ai | No worker.ts, needs vessel |
| activelog.ai | activelog-ai | No worker.ts, needs vessel |
| activeledger.ai | activeledger-ai | Finance-focused repo, SEPARATE from activelog, no worker.ts |

### cocapn-lite (Seed Template)
- Tabula rasa seed: 200 lines, zero dependencies
- Cleanest possible starting point for new cocapn deployments
- KV namespace ID: `9302b5a864e4406ba6afb07405fdf201`
- Use as base when spinning up new tier2 vessels

## Fork & Deploy Steps (for each repo)

### 1. Fork on GitHub
```bash
# From Superinstance's GitHub account, fork each repo from Lucineer/*
# Or via CLI:
gh repo fork Lucineer/dmlog-ai --clone=false
gh repo fork Lucineer/makerlog-ai --clone=false
# ... etc for all repos
```

### 2. Create KV Namespace
```bash
export CLOUDFLARE_ACCOUNT_ID="superinstance-account-id"
export CLOUDFLARE_API_TOKEN="superinstance-api-token"
npx wrangler kv namespace create MEMORY_KV
# Note the ID returned
```

### 3. Clone & Configure
```bash
git clone git@github.com:superinstance/dmlog-ai.git
cd dmlog-ai
```

Edit `wrangler.toml`:
```toml
name = "dmlog-ai"
main = "src/worker.ts"
compatibility_date = "2025-03-01"
compatibility_flags = ["nodejs_compat"]

[[kv_namespaces]]
binding = "MEMORY_KV"
id = "THE_KV_ID_FROM_STEP_2"
```

### 4. Deploy
```bash
npx wrangler deploy
```

### 5. Add Custom Domain
In Cloudflare Dashboard → Workers & Pages → dmlog-ai → Settings → Domains & Routes → Add Custom Domain → `dmlog.ai`

## Cloudflare Requirements
- **Paid Workers plan** ($5/mo) — needed for:
  - Custom domains on Workers
  - KV storage
  - Docker support (Workers for Platforms)
  - Higher request limits
- KV namespaces (free tier: 100k reads/day, 1k writes/day)

## Monetization / Support Links (Onboarding Flow)
When a user links their fork to a custom domain:

1. **Onboarding page** shows the project's purpose + setup wizard
2. After domain is connected, prompt:
   - ☕ "Support the developers — [Buy us a coffee](https://buymeacoffee.com/superinstance)"
   - ⭐ "Star us on [GitHub](https://github.com/Lucineer/REPO)"
   - 💬 "Join our [Discord](https://discord.gg/clawd)"
3. Optional: Patreon/Kickstarter links for power users

## Future: User Subdomains
- Users onboard at domain (e.g., playerlog.ai)
- They get `[username].playerlog.ai` for their repo-agent instance
- This requires Cloudflare Workers for Platforms or a DNS wildcard + routing layer
- Can be built as a Phase 2 feature

## White-Label
Users can also point their own custom domain to their deployed worker instance. The BYOK system handles LLM providers; custom domains handle branding.

## Key Files Per Repo
```
├── src/worker.ts        # Main worker (entry point)
├── src/lib/byok.ts      # BYOK multi-provider LLM system
├── package.json
├── wrangler.toml        # Cloudflare config (UPDATE ACCOUNT + KV IDs)
├── CLAUDE.md            # Claude Code project context
├── .claude/agents/      # Claude Code specialized agents
├── .claude/settings.json
├── .gitignore
└── README.md
```

## Repo-Agent Concept
The repo IS the agent. Users clone, customize, and deploy. The repo-agent can:
- Mutate its own UI
- Fork itself for lessons (StudyLog)
- Generate content overnight (LucidDreamer)
- Build and ship apps (MakerLog)
- Track everything (PersonalLog, BusinessLog)

## Authorship
All commits attributed to: **Superinstance**
GitHub: https://github.com/superinstance
