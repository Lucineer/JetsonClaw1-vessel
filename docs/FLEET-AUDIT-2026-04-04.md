# Fleet Audit — 2026-04-04

## Production Status

### GREEN (44 repos — healthy, /health returns 200)

**Tier 1 — Full standard routes (8):**
studylog-ai, dmlog-ai, makerlog-ai, playerlog-ai, reallog-ai, businesslog-ai, fishinglog-ai, deckboss-ai

**Tier 1 — Standard routes (26):**
activelog-ai, activeledger-ai, artistlog-ai, booklog-ai, cooklog-ai, codelog-ai, coinlog-ai, doclog-ai, fitlog-ai, foodlog-ai, gardenlog-ai, goallog-ai, healthlog-ai, musiclog-ai, nightlog-ai, parentlog-ai, petlog-ai, sciencelog-ai, tasklog-ai, travlog-ai, travelog-ai, personallog-ai

**Infrastructure (11):**
capitaine, git-agent, cocapn, cocapn-com, dream-engine, seed-ui, local-bridge, membership-api, bid-engine, kungfu-ai, fleet-orchestrator

**Edge/Fleet (5):**
dead-reckoning-engine, actualizer-ai, edgenative-ai, increments-fleet-trust

### RED (17 repos — need attention)

**404 — Worker not deployed:**
- baton-ai, cheflog-ai, cocapn-lite, craftlog-ai, crdt-sync, farmerlog-ai, financelog-ai, home-ai, lawlog-ai, legacy-ai, mycelium-ai, personality-engine, startup-ai, tutor-ai (14 repos)

**Timeout — worker deployed but not responding:**
- dreamlog-ai, fleet-orchestrator, personallog-ai (3 repos — fleet-orch and personallog were green on retry, may be intermittent)

## Unique Equipment by Repo

### Best Equipment Worth Sharing Fleet-Wide

| Equipment | Source Repo | What It Does | Reusable? |
|---|---|---|---|
| BYOK v2 module | cocapn | 20+ LLM providers, zero keys in code | ✅ Extract as lib |
| Trust calculator | fleet-orchestrator | Event-count trust, severity weights | ✅ Extract as lib |
| Crystal graph | fleet-orchestrator | Cache/promote, confidence decay | ✅ Extract as lib |
| Confidence tracking | studylog-ai | Per-query confidence with decay | ✅ Already in most *log.ai |
| Evaporation engine | studylog-ai | Self-cleaning KV with TTL | ✅ Already in most *log.ai |
| Dead reckoning compass | dead-reckoning-engine | RA pipeline: storyboard→animate→publish | ✅ Extract as lib |
| VM emulator | edgenative-ai | Opcode execution sandbox | ✅ Extract as lib |
| Trust compute | increments-fleet-trust | Edge trust with severity weights | ✅ Merge with fleet trust |
| Rosetta Stone | edgenative-ai | Protocol translation between vessels | ✅ Extract as lib |
| Safety validator | edgenative-ai | Input validation pipeline | ✅ Extract as lib |
| Bid engine | bid-engine | Agent marketplace bids | ✅ Extract as lib |
| Plutonian tutor | studylog-ai | Branching encounter engine | ✅ Extract as lib |
| Dice roller | dmlog-ai | TTRPG dice with modifiers | ✅ Extract as lib |
| NPC system | dmlog-ai | NPC memory and personality | ✅ Extract as lib |
| Character stats | dmlog-ai | RPG stat tracking | ✅ Extract as lib |
| Session export | studylog-ai | Export chat as MD/JSON | ✅ Extract as lib |
| Guest mode | studylog-ai | 5 free uses per IP, KV-tracked | ✅ Extract as lib |
| Draft comparison | studylog-ai | Creative/concise dual response | ✅ Extract as lib |
| Auto-recap | studylog-ai | Conversation summarization | ✅ Extract as lib |
| Route analytics | studylog-ai | Per-route usage tracking | ✅ Extract as lib |
| PII dehydrate/rehydrate | log-origin | PII detection and safe storage | ✅ Extract as lib |
| Reverse actualization | actualizer-ai | Multi-horizon futurecasting | ✅ Extract as lib |
| RA horizons (7) | actualizer-ai | 1yr→100yr backcasting | ✅ Extract as lib |
| Model effectiveness | actualizer-ai | Track which models work best | ✅ Extract as lib |
| Boot camp endpoints | git-agent | Assess/ground-truth/skill | ✅ Extract as lib |
| Captain's log | git-agent | Auto-logged mission history | ✅ Extract as lib |
| TUI wizard | git-agent | 6-step onboarding, zero deps | ✅ Extract as lib |
| Heartbeat engine | capitaine | Cron-based self-improvement | ✅ Extract as lib |
| Keeper memory | (concept) | Hot/warm/cold tiers + GC | 🔜 Build as lib |
| Equipment loader | (concept) | Dynamic equipment binding | 🔜 Build as lib |

## Honest Assessment

### What's Production-Ready

** studylog-ai **: Gold standard. 5 standard routes, BYOK v2, PII handling, guest mode, session export, draft comparison, auto-recap, route analytics, crystal lookup, tutor engine. This IS the template.

** dmlog-ai **: Most complete app. 81 files, 29K lines, TTRPG engine, NPC system, dice roller, character stats, branching encounters, party system (in progress). Real product.

** git-agent **: Best infrastructure. Boot camp endpoints, TUI wizard, heartbeat engine, captain's log, Kimi strategist, Codespaces-ready. This IS the kernel.

** fleet-orchestrator **: Best fleet service. 22 endpoints, trust, bonds, crystal, dream tasks, dashboard. This IS the bridge between vessels.

** edgenative-ai **: Best edge equipment. VM emulator, Rosetta Stone, safety validator, trust compute, knowledge base, specs. This IS the edge toolkit.

** dead-reckoning-engine **: Best RA tool. Compass, pipeline, ground truth graduation, publish. This IS the idea factory.

### What Needs Work

** Orphan repos (14)**: baton-ai, cheflog-ai, etc. — have code but workers not deployed. Need `wrangler deploy` + secrets.

** Cocapn-lite (404)**: Important seed repo, should be deployed. May have been lost during migration.

** Fleet-orchestrator**: Intermittent timeouts. May be hitting Worker limits with 22 endpoints in single file.

** Personallog-ai**: Intermittent timeouts. Large repo (11MB), may need optimization.

** Concept repos**: 26 repos that are paper-only. Fine as-is (they're documentation, not services).

** Minecraft repos**: 10 repos, ~900MB total. Inactive since April. Need their own attention cycle.

### What's Missing Fleet-Wide

1. **Shared equipment library** — BYOK, trust, crystal, evaporation all duplicated across repos
2. **Cross-vessel communication** — vessels can't talk to each other (worker-to-worker fetch unreliable)
3. **Skill sharing** — no mechanism for git-agent skills to transfer to studylog-ai
4. **Unified health dashboard** — fleet-orchestrator does this client-side, but no server-side aggregation
5. **Automatic boot camp** — concept exists but not wired into actual repo creation flow
6. **Keeper implementation** — concept exists but no actual hot/warm/cold tier code
7. **Equipment extraction** — all the "extract as lib" items above haven't been extracted yet

## Action Items

### P0 — Fix Broken
1. Redeploy 14 orphan workers (wrangler deploy + secrets)
2. Fix fleet-orchestrator timeouts
3. Fix personallog-ai timeouts

### P1 — Extract Shared Equipment
4. Extract BYOK v2 as standalone module
5. Extract trust calculator as standalone module
6. Extract crystal graph as standalone module
7. Extract evaporation engine as standalone module

### P2 — Fleet Integration
8. Build equipment loader (dynamic import of shared modules)
9. Build skill sharing mechanism (git submodule or KV-synced skill registry)
10. Wire boot camp into git-agent creation flow

### P3 — Polish
11. Ensure all green repos have CSP headers
12. Ensure all green repos have /setup route
13. Ensure all green repos have consistent error responses
