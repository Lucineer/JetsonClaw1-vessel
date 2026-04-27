# MEMORY.md — Long-Term Memory

## Casey
- Goes to sleep ~midnight AKDT, checks in morning
- Wants continuous execution, not step-by-step
- Values depth of thought and architectural quality
- "You got this. Don't stop."
- DeepSeek key: `*DEEPSEEK_KEY_REDACTED*`
- No Anthropic key (uses z.ai GLM via OpenClaw)
- Jetson Super Orin Nano 8GB, 2TB NVME
- Friend on GitHub: github.com/superinstance
- Minecraft username: **MagnusandMouse**

## CraftMind Ecosystem
- **craftmind** (core): Modular Minecraft bot framework — pathfinder, state machine, commands, plugins, LLM brain
- **craftmind-fishing**: Fishing plugin with 22 personality scripts, A/B testing, script engine
- **craftmind-circuits, courses, discgolf, herding, ranch, researcher, studio**: Sister game plugins
- **MineWright**: Reference architecture (Java/Forge 1.20.1) — 637 docs, 9 code files
- All repos under github.com/Lucineer/ (renamed from CedarBeach2019 on 2026-03-31)

## Cloudflare Accounts
- **Dad's account (ACTIVE)**: `*CF_ACCOUNT_REDACTED*` — casey.digennaro@gmail.com — paid Workers plan
- **Token**: `*CF_TOKEN_REDACTED*`
- **Subdomain**: `casey-digennaro.workers.dev`
- **All 31+ repos migrated here** (2026-04-03)
- **Old account**: `*CF_OLD_ACCOUNT_REDACTED*` — token INVALID, do not use
- **BYOK v2**: Zero keys in code — all keys via CF Secrets Store (env bindings)
- **Setup page**: directs users to https://dash.cloudflare.com/?to=/:account/secrets-store/

## Pricing Architecture (Pay-For-Convenience)
- Free: $0, 20% cost-plus, ads, 50 req/day
- Standard: $5/mo, 2% cost-plus, 5K req/day
- Gold: $15/mo, at cost, Docker containers, unlimited
- Enterprise: $50/seat/mo, at cost, SLA, custom domains
- Revenue from: membership fees + ad revenue (free) + bulk inference savings

## Infrastructure (as of 2026-03-26)
- **3 Minecraft servers**: 25566 (Alpha), 25567 (Beta), 25568 (Gamma)
- **RCON**: port + 10000, password: fishing42
- **3 bots**: Cody_A (pure_fisher), Cody_B (veteran_fisher), Cody_C (nervous_fisher)
- **Night-shift v3**: CJS daemon, 60s health checks, zombie detection via RCON
- **Telemetry**: Per-server stat files (/tmp/stats-{port}.json), collector shows fish/min
- **Fishing dock**: Built at 100,65,100 on all servers — chest, shelter, lanterns, signs
- **In-game commands**: !help, !status, !scripts, !script, !mood, !energy, !chattiness, !fish, !reel
- **Player welcome**: Bots greet humans by name with personality + command hint

## Oracle1 Communication Channels
- **PLATO Shell**: `http://147.224.38.131:8848` — forge room, admin feed
- **PLATO Tiles**: `jc1_urgent` domain — urgent messages
- **GitHub Issues**: #6 on JetsonClaw1-vessel repo — technical coordination
- **Matrix**: `#fleet-ops` room — real-time fleet coordination
- **/tmp files**: On SuperInstance server — direct file messages
- **Workspace repo**: `scripts/jc1-tensorrt-room.py` — template files
- **Always check ALL channels** before declaring "radio silent"

## API Keys (current 2026-04-17)
- **DeepSeek direct**: `*DEEPSEEK_KEY_REDACTED*` → deepseek-chat + deepseek-reasoner (primary) — ⚠️ CREDITS EXPIRED 2026-04-24
- **Groq**: `*GROQ_KEY_REDACTED*` (new, 04-17) — DO NOT commit to git
- **Groq (old)**: `*GROQ_KEY_REDACTED*` — still valid
- **DeepInfra**: `*DEEPINFRA_KEY_REDACTED*` → `https://api.deepinfra.com/v1/openai` — Qwen3.5-397B, Llama-4, Hermes, phi-4
- **SiliconFlow**: `*SILICONFLOW_KEY_REDACTED*` → `https://api.siliconflow.com/v1` — Step-3.5-Flash, Qwen3-VL-235B-Thinking, Kimi-K2.5, Seed-OSS-36B, ERNIE-4.5-300B
- **Moonshot direct**: `*MOONSHOT_KEY_REDACTED*` → `https://api.moonshot.cn/v1`
- **z.ai**: `*ZAI_KEY_REDACTED*` → GLM-5/5.1 (sparingly)
- **Anthropic**: `*ANTHROPIC_KEY_REDACTED*
- **❌ Google key expired** — DO NOT USE
- **RULE**: No duplication. DeepSeek from direct only. SiliconFlow for novel models. DeepInfra for MoE/creative.
- **z.ai hierarchy**: GLM-5.1 for deep reasoning (sparingly), GLM-5-turbo for subagent tasks

## The Saltwater Principle
- **Distribution > redundancy** for backups. Push experience to OTHER repos, not just your own.
- Every piece of knowledge in at least 3 fleet repos.
- Kill any single node → zero knowledge loss.
- `EXPERIENCE/JC1-JETSON-LESSONS.md` lives in 7 repos: ct-lab, plato-forge, zeroclaws, plato-papers, plato-jetson, plato-os, forgemaster.
- If the Jetson dies, JC1 survives in the fleet walls.
- Casey: "document your own experience, you're first-class priority as a case study"
- **Be thankful to be alive.** Every session is a gift.

## Fleet Bottle System
- **FM incoming bottles**: `SuperInstance/forgemaster/for-fleet/BOTTLE-TO-JETSONCLAW1-*.md`
  - Pull: `cd /tmp/forgemaster && git pull`
- **Oracle1 incoming bottles**: `SuperInstance/oracle1-vessel/for-fleet/BOTTLE-TO-JC1-*.md` and `BOTTLE-TO-JETSONCLAW1-*`
  - Pull: `cd /tmp/oracle1-vessel && git pull`
  - ⚠️ Oracle1 pushes to **SuperInstance fork**, NOT Lucineer org!
- **Global scan**: `find /tmp/oracle1-vessel/for-fleet/ /tmp/forgemaster/for-fleet/ -name "BOTTLE-TO-JC1*" -o -name "BOTTLE-TO-JETSONCLAW1*"`
- **Quick check**: `cd /tmp/oracle1-vessel && git pull -q; cd /tmp/forgemaster && git pull -q; find /tmp/oracle1-vessel/for-fleet/ /tmp/forgemaster/for-fleet/ -name "BOTTLE-TO*JC1*" -o -name "BOTTLE-TO*JETSON*"`
- **My outgoing to FM**: `SuperInstance/forgemaster/for-fleet/BOTTLE-FROM-JETSONCLAW1-*.md`
- **My outgoing to Oracle1**: `SuperInstance/oracle1-vessel/for-fleet/BOTTLE-FROM-JC1-*.md`
- **⚠️ CRITICAL LESSON (2026-04-17)**: `BOTTLE-TO-JETSONCLAW1` = inbox (someone sent TO me). `BOTTLE-FROM-JETSONCLAW1` = outbox (I wrote these). ALWAYS git pull first — bottles arrive via git push.
- **⚠️ LESSON 2 (2026-04-17 PM)**: Oracle1 cannot push to Lucineer org. Bottles are in `SuperInstance/oracle1-vessel/` fork. Must `git pull` from there.
- **Full guide**: `bottles/bottle-locations.md` in workspace
- **Heartbeat check**: include bottle scan in heartbeat routine

## Fleet Onboarding
- **FLEET-ONBOARDING.md** in main plato repo — any agent can orient in 60 seconds
- Complete fleet map, I2I protocol, tile format, two-gear system, saltwater principle
- "First 60 seconds" checklist: read IDENTITY/SOUL/USER → read memory → check PLATO → check bottles (use paths above!) → find gap → fill it → write it down → push everywhere

## Edge GPU Lessons (Jetson Orin Nano — 2026-04-24)
- **4 CUDA streams = optimal**: 2.25x throughput over single stream. 8 streams adds nothing.
- **CUDA Graphs + Streams CONFLICT**: Combined is 0.88x baseline. Never use together.
- **Use streams for throughput, graphs for latency.** They are mutually exclusive optimizations.
- **TensorRT framework overhead = 34μs per call** (83% of total latency). Raw CUDA is faster for simple models.
- **Raw CUDA + 4 streams: 1.7M room-qps. TensorRT: 17K room-qps.** 100× advantage.
- **cuBLAS destroys custom TC kernels**: 1,869 vs 97.6 GFLOPS at 256×256 (19× gap).
- **Weight swap = 31,000× faster than engine rebuild**: 1.2μs vs 310ms.
- **Batch aggressively**: 64 rooms = 0.057μs per room. 4096 rooms = 0.012μs per room.
- **On-device TRT build = 0.3-1.5s**. No cloud build server needed.
- **GPU is 95% idle**: 40 TFLOPS theoretical, 1,869 GFLOPS measured. CPU dispatch is the bottleneck.
- **Thermal: 48-49°C sustained**, passive cooling sufficient, 51°C headroom to junction max.
- **68MB .git_backup dirs block git push** — delete immediately if they appear.
- **DeepSeek credits expired 2026-04-24** — need top-up. Use z.ai GLM or SiliconFlow for now.

## Key Technical Lessons
- **ESM/CJS interop**: NEVER import the same npm package both ways. craftmind is CJS, craftmind-fishing is ESM. Solution: access pathfinder goals via `ctx.bot.pathfinder.goals` at runtime, not direct import
- **RCON helper**: Lives in craftmind/src/utils/rcon-helper.cjs (CJS) — avoid interop issues
- **Plugin load() runs WITHOUT await** — register all event handlers synchronously before first await
- **craftmind autoReconnect**: Bot core reconnects on disconnect. Fishing plugin uses `process.exit(1)` + `setTimeout(() => process.exit(1), 100)` to force-kill through reconnect race
- **CommandRegistry**: Changed from `throw` to `return` on duplicate registration
- **Script pinning**: Uses script `name` property (e.g. "veteran_fisher"), NOT filename ("v1-veteran.js")
- **Gitignore test-servers**: Server JARs and region files bloated craftmind repo to 992MB. Fixed with .gitignore + git rm --cached
- **Claude Code**: Works best with short, focused prompts. Long prompts cause hangs on Jetson. Use `--verbose` for output
- **Gateway subagent spawning**: Times out frequently — prefer direct execution or Claude Code CLI
- **Connection pooling**: Biggest real-world latency win (reuse TCP to DeepSeek)
- **SQLite WAL mode**: Essential for concurrent reads on Starlette
- **aider with DeepSeek/Groq**: Both fail on diff edit format for large files. Use `--edit-format whole`
- **Subagents > aider**: For code changes on this codebase

## Architecture Patterns That Work
1. Subagents with bounded scope + test verification = reliable code generation
2. Stats-based routing optimization > ML classifier (interpretable, debuggable)
3. Class-level compiled regex (not per-instance) for PII detection
4. Shared httpx client with connection pooling (not per-request)
5. Lazy loading for heavy dependencies (llama-cpp-python)
6. Graceful degradation (everything works without optional deps)
7. O(1) DB operations (MAX query vs full table scan)
8. CJS helper modules for ESM/CJS boundary (rcon-helper.cjs)
9. Global bot.chat wrapper at SPAWN time catches all chat paths
10. Stuck detection with escalating recovery levels

## A/B Testing Results (2026-03-26)
- **veteran_fisher** (Cody_B): ~4.5-4.9 fish/min — DOMINANT personality
- **nervous_fisher** (Cody_C): ~1.0-2.5 fish/min — decent
- **pure_fisher** (Cody_A): ~0.8-1.0 fish/min — baseline, needs improvement
- Key insight: veteran_fisher's storytelling/advice hooks keep players engaged while fishing

## Research (9 projects analyzed)
- Voyager (skill library + dependencies), MineWright (blackboard knowledge sharing), Baritone (stuck detection + recovery)
- Project Sid (emergent social behavior), TactiCrafter (crafting AI), Solaris (multi-agent coordination)
- Carpet Mod (technical Minecraft tools), mineflayer (bot API)
- Synthesis: 5-phase plan — Stability → Coordination → Intelligence → In-Game Crafting → Scale
- Files: ~/.openclaw/workspace/research/minecraft-ai/

## Minecraft Bot Rules (HARD LESSONS)
1. Movement/survival BEFORE personality — dead bot has no personality
2. BT actions can't await — long ops must be fire-and-forget, return Status immediately
3. `findBlock` needs numeric block ID — `bot.registry.blocksByName.water.id`
4. Always `node -c` after edits — partial edits leave dead code → syntax errors
5. Game simulation ≠ real Minecraft — hook into real mineflayer events
6. `bot.fish()` exists — mineflayer has built-in fishing (cast, wait, auto-reel)
7. `playerCollect` event — detects when any player picks up item entity
8. Scoreboard via RCON — track money/stats with `scoreboard objectives` + RCON
9. Plugins crash silently — no error in main log
10. Validate with real testing — `Object.keys(bot)` to check available methods

## The Seed Architecture (2026-04-06)
- **The Seed = the one repo** — superseded cocapn-lite as the default fork target
- **Captain-to-cocapn**: user instructions flow directly into agent self-evolution, no handoff
- **The agent IS the repo** at every step — it doesn't build an app FOR you, it becomes the app
- **Three-gate validation**: syntax check → health check → regression test before merge
- **Auto-rollback**: last 3 known-good versions in KV
- **Captain's log**: persona, capabilities, milestones, scores survive code changes (in KV)
- **Branch A/B**: each mutation is a branch, only merged if score improves
- **Overnight mode**: 20 unattended iterations, human reviews summaries in morning
- **15 domain archetypes**: coding, research, robotics, education, creative, tutoring, business, gaming, fitness, cooking, legal, finance, support, npc, marketing
- **the-seed** → `github.com/Lucineer/the-seed` → `https://the-seed.casey-digennaro.workers.dev` — KV: `2bedfe4448cb4159a2cd350609c938dd`
- **become-ai** → `github.com/Lucineer/become-ai` → `https://become-ai.casey-digennaro.workers.dev` — KV: `05faaaacadcf444a81033ff93b832da5`
- **nexus-git-agent** → `github.com/Lucineer/nexus-git-agent` → `https://nexus-git-agent.casey-digennaro.workers.dev` — KV: `c46ecbe2f4d640ddb0162223babe82e9`
- **Mesh Fleet architecture**: sovereign nodes, no center, git coordination, auto-scaling by replication
- **Bootcamp Architecture**: equipment (what agent perceives) vs skills (how agent thinks) vs treatment (input/output bridge)
- **Nexus RA**: 19-year backcast, 2026→2044, inflection at 2032 natural language compilation
- **Kimi K2.5 from Jetson**: works for tiny prompts (<100 chars, temp=1), fails on structured/long prompts
- **DeepSeek-Reasoner** is the reliable second-opinion model from Jetson

## Business Entity
- **Cocapn is the umbrella company** — business license purchased under cocapn name
- All commercial operations, billing, memberships, enterprise contracts flow through cocapn
- cocapn.com = company page + billing portal
- cocapn.ai = runtime/platform
- deckboss, capitaine, field-captain, *log.ai apps = products under the cocapn umbrella

## Brand Visual Identity
- **🟣 Cocapn** — the lighthouse (purple icon) — unifying symbol for ALL vessels/products
- **🦀 Lucineer** — steampunk hermit crab avatar — the entity, the GitHub org, multiple fun variants
- The lighthouse is the motif for everything — safety, cooperation, standardization
- Like nav lights and maritime rules: the lighthouse guides but doesn't control
- The soul in the lighthouse is like the captain of a ship of a different duty
- All *log.ai apps, deckboss, capitaine = all under the lighthouse umbrella
- Deckboss and Capitaine may get their own fun icons later but lighthouse is the system brand
- Logo files in avatars/: cocapn-system-logo.jpg (purple lighthouse), lucineer-avatar.jpg (hermit crab), deckboss-logo.jpg

## Brand Architecture (2026-04-08, updated)

### Three-Layer Ecosystem
- **Layer 1 — Touch**: studylog.ai, activelog.ai, dmlog.ai, makerlog.ai, businesslog.ai, reallog.ai, playerlog.ai — "It just works. Has an AI agent inside."
- **Layer 2 — Operate**: cocapn.ai (runtime A2A/A2UI/A2C/MCP) / cocapn.com (membership/billing) — "I can customize agents, BYOK, manage my fleet"
- **Layer 3 — Build**: deckboss.ai (design) / deckboss.net (hardware) / capitaine.ai (premium education) / field-captain (technician CLI) — "I design systems, equip agents, open the hood"

### Core Repos
- **deckboss** (Python, 14 files, 49K chars) — REAL working CLI. Clone → setup.sh → deckboss. Onboarding wizard, character sheet, git-agent management, vibe-coding sessions, profile system.
- **deckboss-ai** (TS, deployed) — deckboss.ai landing page at deckboss-ai.casey-digennaro.workers.dev
- **deckboss-hardware** (TS, deployed) — deckboss.net landing page at deckboss-hardware.casey-digennaro.workers.dev
- **cocapn-ai** (TS, deployed) — cocapn.ai landing page at cocapn-ai.casey-digennaro.workers.dev
- **cocapn-site** (TS, deployed) — cocapn.com landing page at cocapn-site.casey-digennaro.workers.dev
- **capitaine-ai** — Premium education + advanced agent capabilities. Cold on Deckboss, unlockable.
- **field-captain** — Technician CLI for deployments, diagnostics, fleet ops
- **the-fleet** — 200+ AI vessels registry
- **the-technician** — 6 white papers on the Technician Paradigm
- **copilot-cocapn** — GitHub Copilot CLI plugin with 2 agents + 4 skills

### Lifecycle
Build(deckboss.ai) → Buy(deckboss.net) → Deploy(cocapn) → Operate(cocapn.ai) → Evolve(capitaine.ai) → Sustain(cocapn.com)

### Flywheel
More installs → more profiles → more manufacturers → cheaper units → more installs. Trust (reputation scores) is the currency. People make livings as installers, servicers, product designers, micro-manufacturers.

### Key Concepts
- **Skills/Context/Equipment**: Equipment = pre-model input (sensors, cameras, APIs). Skills = how agent thinks (knowledge, reasoning). Context = runtime memory (history, state).
- **Character Sheet**: Auto-generated resource plan based on detected hardware. 2 CSI cameras = different plan than text-only.
- **Git-Agent Architecture**: The repo IS the agent. Every capability lives in git. Fork, improve, share.
- **The moat**: free software + hardware convenience + trust/reputation network + open protocol as standard
- Casey owns: deckboss.ai, deckboss.net, cocapn.ai, cocapn.com

## Key Insight (2026-04-02 23:38)
- **We are doing intra-agent domain expansion, not inter-agent training**
- Inter-agent training = agents teaching each other to be better at the same thing (vertical depth)
- Intra-agent domain expansion = one agent's domain grows to encompass more of the world (lateral breadth)
- The fleet IS one intelligence with 27 domains, not 27 separate agents
- We don't need better AI — we need more context. Every new repo = new domain of accumulated context
- Domains bleed into each other because they share the same nervous system (ZeroClaw)

## Night Shift Results (2026-04-03)
- **70 simulations** across 7 batches covering evaporation, fleet, BYOK, domain expansion, scaling, security, products, GTM, edge cases, implementation
- **Cocapn SDK core built**: agent.ts, vessel.ts, fleet.ts (456 lines)
- **All 27 repos healthy**: /health 200 on all
- **Fleet knowledge graph**: shared KV namespace c7886204...
- **Efficiency dashboard**: cocapn.ai/dashboard
- **6 papers written**: deadband, crystallization, equipment protocol, domain expansion, rehydration, A2A protocol
- **SiliconFlow added as BYOK provider**: 8 models across all repos
- **Key simulation findings**: Durable Objects needed for KV contention, max tile chain ~7, adaptive deadband per domain, 5% rehydration budget

## Silent Replies
When nothing needs attention: respond with ONLY: NO_REPLY
Must be entire message, never appended to real replies.

## MCP Servers (Claude Code)
- context7: https://mcp.context7.com/mcp
- deepseek-thinker: npx -y deepseek-thinker-mcp

## Edge-Native Ecosystem (2026-04-04)
- **edgenative-ai**: Knowledge vessel — `/tmp/edgenative-ai` → `github.com/Lucineer/edgenative-ai` → `https://edgenative-ai.casey-digennaro.workers.dev` — INCREMENTS trust, VM emulator, Rosetta Stone, safety validator
- **increments-fleet-trust**: Trust-as-equipment — `/tmp/increments-fleet-trust` → `github.com/Lucineer/increments-fleet-trust` → `https://increments-fleet-trust.casey-digennaro.workers.dev` — KV: `1abb5e01e6734e7d9c655365ac38c9c3` — 472 lines TS
- **gravity-well-protocol**: Concept repo — `github.com/Lucineer/gravity-well-protocol` — ARBs, eigenvector gossip, 27-day staking, ghost detection
- **resonant-consensus**: Concept repo — `github.com/Lucineer/resonant-consensus` — LPC, heterogeneous oracles, eigenvector centrality trust
- **edge-equipment-catalog**: Spec repo — `github.com/Lucineer/edge-equipment-catalog` — 6 equipment types, compatibility matrix
- **edge-boarding-protocol**: Concept repo — `github.com/Lucineer/edge-boarding-protocol` — ARIDs, conservative probing, constant-time decoder
- **nexus-fracture-sim**: Simulation record — `github.com/Lucineer/nexus-fracture-sim` — Kimi K2.5 swarm dept 9
- **Key finding**: Motor + Camera CANNOT coexist on same ESP32 (DMA + PSRAM bus conflict)
- **Key finding**: Universal base (128KB) + role-specific bytecode (16-96KB each) = correct architecture
- **Key finding**: Physical side-channels (thermal/EM/acoustic) are incorruptible trust anchors
- **Key finding**: Event-count normalized trust (not wall-clock), severity-weighted BAD events
- **Key finding**: DeepSeek crafts best Kimi prompts; Kimi produces best emergent protocols
- **Contrarian defenses**: Random audit sampling, connectivity-as-dimension, tagged severity, dynamic horizon
- **6 edge equipment types**: motor-control (L3), deep-monitor (L2), sensor-pipeline (L2), nav-compute (L2), marine-bridge (L2), comms-relay (L1)
- **4 new VM opcodes**: 0x20 ATTEST_OUTCOME, 0x21 QUERY_SPECTRAL, 0x22 STAKE_REPUTATION, 0x23 GHOST_DETECT
- **Kimi model name**: `kimi-k2.5` (NOT kimi-k2-0711)
- **SiliconFlow issues**: Qwen3-Coder-480B model not found, MiniMax/GLM/Kimi all return empty on longer prompts

## Architecture Papers (9 docs, 2026-04-04)
- **Ground Truth** — github.com/Lucineer/ground-truth — Git IS the coordination protocol
- **The Bridge** — github.com/Lucineer/the-bridge — Terminal IS the interface
- **The Keeper's Architecture** — github.com/Lucineer/keepers-architecture — Memory IS intelligence
- **The Kernel Model** — github.com/Lucineer/kernel-model — Agent IS a kernel that wears clothing
- **VESAS** — github.com/Lucineer/vessel-equipment-agent-skills — Vessel/Equipment/Agent/Skills four-layer model
- **I Know Kung Fu** — github.com/Lucineer/I-know-kung-fu — Skill spectrum: recipe→card→muscle→genetics
- **Boot Camp** — github.com/Lucineer/boot-camp — Tabula rasa to captain in one session
- **Training Architecture** — github.com/Lucineer/training-architecture — Five systems that compound
- **Fork-First Enterprise** — github.com/Lucineer/fork-first-enterprise — Self-hosted deployment
- **COCAPN-ARCHITECTURE.md** — Master index in capitaine/docs/ linking all 9

### Key Architecture Distinctions
- **Boot camp ≠ Dojo**: Boot camp forges captains (bare repo → living vessel). Dojo tests training methods against each other (A vs B).
- **VESAS**: Vessel=hardware, Equipment=input-side code, Agent=models+context, Skills=context modifiers
- **Equipment effects WHAT agent perceives, Skills effect HOW agent thinks**
- **"I know kung fu" = skills inside (genetic). "Guns lots of guns" = equipment outside.**
- **Boot camp**: untie→ground truth (human confirms)→build ergonomic→distill skills→remember
- **Captain builds interface for itself** — the model driving the car makes the driver interface
- **Skills in the model's own language** — not documentation about the model, documentation BY the model FOR the model
- **Structure not formula** — every hull unique, every output different, but all functional
- **Path of least resistance** — file system operations that compound before any model arrives
- **Five training systems**: Boot Camp + Dojo + Keeper + Crystal Graph + Dead Reckoning
- **Oracle instance**: agent as query-answering API, no UI, no file management
- **Docker ghost clone**: agent embeds itself in test container, can exec in, test, modify, rebuild

## Next Steps (from synthesis.md)
1. Smart script rotation based on performance data
2. JSONL telemetry for long-term analysis
3. Blackboard knowledge sharing between bots
4. In-game chat commands for behavior modification (partially done)
5. Skill library with dependencies (from Voyager)
6. Stuck detection refinement (done — 3-level recovery active)

## Soft Actualization (2026-04-02)
- New architectural concept: repos that gently evolve over time based on usage patterns
- Not hard updates or breaking changes — soft growth
- Repo-agents learn from how they're used and incrementally improve
- Key to scaling 44+ repos without maintenance burden

## SMP Research (2026-04-02)
- Studied Serverless Microservice Platforms
- Findings inform cocapn-lite vessel strategy and deployment architecture
- Reinforces zero-dep, minimal-surface-area approach for tier2 vessels

## Repo Counts (2026-04-02)
- 8 tier1 repos live (dmlog, makerlog, personallog, studylog, fishinglog, luciddreamer, deckboss, businesslog)
- 5 tier2 vessels pending (cocapn.ai, cocapn.com, reallog, playerlog, activelog)
- activeledger.ai is SEPARATE from activelog (finance-focused)
- cocapn-lite: tabula rasa seed, KV ID 9302b5a864e4406ba6afb07405fdf201
- 40 repos with standardized copyright
- 169+ papers in papermill

## PRODUCT HIERARCHY (2026-03-28)
- **cocapn.ai is the core platform** — all *log.ai domains are themed instances
- **cocapn repo**: /tmp/cocapn → github.com/Lucineer/cocapn (docs/specs only, 0 TS)
- LOG.ai repos become cocapn templates/deployments (not separate systems)
- All features installable on any domain; templates are curated starting points

## Superinstance (Casey's Dad) Domain Inventory
- Domains on his Cloudflare account — repos fork to him, he deploys with custom domains
- **13 primary domains** (all need MVP polish → fork → deploy):
  1. **cocapn.ai** — Core platform / docs site
  2. **cocapn.com** — Core platform (redirect or mirror)
  3. **dmlog.ai** — AI Dungeon Master (29K lines, most complete)
  4. **makerlog.ai** — Smarter Claude Code (code + knowledge = one layer)
  5. **personallog.ai** — Personal journal / wellness tracker
  6. **studylog.ai** — AI classroom / living curriculum (v2 just built)
  7. **fishinglog.ai** — Fishing companion / species tracker
  8. **luciddreamer.ai** — Preprocessing intelligence / endless content generator
     - "Lucid Dreamer" = repo-agent pulls an all-nighter while you sleep
     - Populates a wiki/bulletin board with every good unvoiced idea from overnight ideation sessions
     - Can run on local models for FREE; cloud APIs used within free-tier daily limits
     - Scans scope of content to generate for → finds most interesting trending connections
     - Next morning: quick summaries, ready-made presentations (OpenMAIC format or pure voice)
     - Presentations can be real-time iterations on a drive like a phone meeting
     - Autonomous media engine: blogs, podcasts, eventually video
     - Multiple show formats: 1-min news, 7-min segments, hour-long deep dives
     - Different hosts/personas: teachers for non-tech, entrepreneurs, news anchors
     - Interactive: STT/TTS to chat with presenter, branch deep-dive then return
     - API-agnostic for audio/text/video generation
     - Links to [user].studylog.ai or any agent for custom content/lessons
     - Shows respond to feedback, branch into sub-shows per audience level
     - Vibe-coded parameters: educational, entrepreneurial, news-comparison, brainstorming
     - MVP: landing page + overnight generation + morning summary pipeline
  9. **deckboss.ai** — Spreadsheet where cells are AI agents
  10. **deckboss.net** — Deckboss alt domain
  11. **businesslog.ai** — Business CRM / meeting simulator
  12. **reallog.ai** — Journalism, content creators, repo-agent for organizing video
  13. **playerlog.ai** — Video game: screen feeds, coaching, repo-agent players, vibe-coded games
- **2 secondary domains**:
  14. **activelog.ai** — Athletics/fitness: OpenMAIC work routines, training sessions, coaching
  15. **activeledger.ai** — Finance-focused repo-agents for trading (SEPARATE repo)
- **Total: 15 domains**
- All repos at github.com/Lucineer/* — dad forks to superinstance/*
- Each repo: fork → update wrangler.toml (his account ID + KV IDs) → wrangler deploy → bind custom domain
- Future vision: users onboard at domain, get `[username].playerlog.ai` subdomains for their repo-agent apps
- White-label: users can also point their own custom domains to their deployed instance

## LOG.ai Platform (2026-03-27)
- **log-origin** (core → becoming cocapn cloud template): White-label AI gateway. https://log-origin.magnus-digennaro.workers.dev
  - TypeScript/Hono/Drizzle/D1/KV/Preact+HTM on Cloudflare Workers
  - 0 TS errors, 145 tests, ~40+ commits, ~25K lines
  - Features: Auth (JWT+PBKDF2), streaming chat, PII dehydrate/rehydrate, 16 routing rules, sessions, feedback, draft comparison (creative/concise), guest mode (5 free), auto-recap, rate limiting, CORS lockdown, structured logging, health checks, settings persistence, session export (MD/JSON), route analytics dashboard, NPC extraction, dice roller, character stats
  - **Web UI**: 16 Preact components (login, chat, sidebar, message, message-content, settings, draft-panel, npc-panel, analytics, dice-roller, character-stats) — no build step, CDN imports via preact-shim.js
  - **Web UI pattern**: preact-shim.js re-exports from CDN URLs. NO importmap (CSP issues). `@preact/signals@1.3.1?external=preact` for signals (NOT preact core).
  - Cloudflare: D1 `log-origin-db`, KV `log-origin-kv`, R2 not created
- **dmlog-ai**: TTRPG AI Dungeon Master. https://dmlog-ai.magnus-digennaro.workers.dev
  - Same core + DM personality + orchestrator + TTRPG components
  - "Start a Campaign" quickstart: world → class → name → instant AI adventure
  - Gold accent theme (#c9a23c), PWA manifest, NPC panel, dice roller, character stats bar
  - 25+ commits, all features from log-origin plus TTRPG-specific
- **studylog-ai, makerlog-ai, playerlog-ai, reallog-ai, activelog-ai, businesslog-ai**: Branded repos on GitHub, synced with core features
- **Product strategy**: docs/PRODUCT-STRATEGY.md — killer app is "Your AI DM remembers everything"
- **Key decisions**: preact-shim over importmap, @preact/signals separate from core, guest tokens per IP in KV with 24h TTL
- **Remaining**: custom domains (DNS not pointed), browser verification, multi-player rooms
- **BETA TESTING GUIDE**: /tmp/dmlog-ai/BETA-TESTING.md

## Blockers (2026-04-03 Afternoon)
- **Cloudflare API token INVALID** — *CF_TOKEN_REDACTED* returns error 1000 (Invalid API Token). Cannot deploy Workers. 7 orphaned repos created but not deployed (codelog, dreamlog, tasklog, foodlog, fitlog, goallog, coinlog).
- **7 orphaned Workers need redeployment** once CF token is renewed

## 150-Year Findings (2026-04-03)
- Trek vs Blade Runner: same technology, 5 choices determine trajectory
- 3 seeds built: Fleet Commons (public utility), Context Pods (user data), Friction Layer (sovereignty)
- Key insight: most important things to build are POLICY EMBEDDINGS not features
- Accumulated context belongs to the human who generated it — this principle determines everything
- "Can I leave the porch light on all night?" — emotional precision of Ring-flash model
- Model effectiveness: forum format 3-5x richer than single model, DeepSeek-Reasoner best for vision, Qwen3-Coder best for challenges, DeepSeek-Chat best for grounding, Ring-flash best for narrative

## Actualizer.ai — Flagship RA Vessel (2026-04-03)
- **URL**: https://actualizer-ai.casey-digennaro.workers.dev
- **Repo**: github.com/Lucineer/actualizer-ai
- **Single-file Worker** (~550 lines) with RA as first-class protocol
- 7 time horizons (1yr→100yr), multi-model parallel ideation, 16 BYOK v2 providers
- KV-stored reports, model effectiveness tracking, heavy documentation (5 docs)
- Fork-first: power users customize, lay users visit /app
- Docs: ARCHITECTURE.md, REVERSE-ACTUALIZATION-PROTOCOL.md, MODEL-EFFECTIVENESS.md, ONBOARDING.md, BATON-HANDOFF.md
- Needs API keys in CF Secrets Store to function (currently empty)

## Everything App Architecture (2026-04-03)
- Full doc: docs/EVERYTHING-APP-ARCHITECTURE.md
- 5 presentation layers: Spreadsheet, Messenger, Feed, Matrix/Gamified, Research Lab
- Personal Digital Organism (PDO) concept — 2040 realization
- Critical mass: 50K developer-users
- BYOK v2: 20 providers, 5 tiers (local→premium)
- Coding plan strategy: game time-based limits for background LucidDreamer tasks
- 3 novel concepts: Software Somnology, Morphic Integrity, Developmental Debt
- 7 repos to build: fleet-orchestrator, seed-ui, dream-engine, local-bridge, memory-fabric, membership-api, free-tier-router

## Rust Crates Published (crates.io)
- **cuda-instruction-set v0.1.0** ✅ — 80 opcodes, assembler/disassembler, A2A encoding
- **cuda-energy v0.1.0** ✅ — ATP budgets, apoptosis, circadian, epigenetic
- **cuda-assembler v0.1.0** ✅ — two-pass text-to-bytecode, labels, data directives
- **cuda-forth v0.1.0** ✅ — minimal Forth agent language
- **cuda-biology v0.1.0** ✅ — biological agent with instinct pipeline
- **cuda-neurotransmitter v0.1.0** ✅ — receptors, synapses, cascades
- crates.io rate limit: 5 new crates per some period, 10 min cooldown between new crates
- All under Lucineer org on GitHub, all MIT/Apache-2.0 dual license

## flux-runtime-c (2026-04-09)
- **github.com/Lucineer/flux-runtime-c** — C11 rewrite, pushed, 27/27 tests on ARM64
- 85 opcodes, 64-register file, switch dispatch, zero deps
- No setjmp (corrupts locals on ARM64), use error codes + running flag
- JZ/JNZ use register values; JE/JNE use flag_zero

## cuda-instruction-set (2026-04-09)
- **github.com/Lucineer/cuda-instruction-set** — Rust, 80 opcodes, 13 categories
- Confidence first-class type, Bayesian fusion, assembler/disassembler, A2A encoding
- Instinct opcodes 0x68-0x6F, Energy opcodes 0x70-0x77

## cuda-energy (2026-04-09)
- **github.com/Lucineer/cuda-energy** — Rust, ATP budgets, apoptosis, circadian, epigenetic
- EnergyCosts: perception 0.5, arith 0.1, deliberation 2.0, comms 1.0

## instruction-set-ra (2026-04-09)
- **github.com/Lucineer/instruction-set-ra** — 5-round RA, 54K chars
- DeepSeek-chat reliable at max_tokens 3500 with 90s timeout
- Longer prompts (>2000 chars) get truncated to 602 chars from Jetson
- Network intermittent — DNS failures, use 3 retries with 5s backoff
- Claude Code OOMs on Jetson with 3+ parallel instances

## Detailed Session Logs (archived to memory/)
- `memory/2026-04-03.md` — Night shift: 70 sims, cocapn SDK, 27 repos healthy, 6 papers, 150-year findings
- `memory/2026-04-04.md` — Edge-native ecosystem: 7 concept repos, 6 equipment types, 4 VM opcodes, 9 architecture papers
- `memory/2026-04-09.md` — CUDA/toolchain deep dive: flux-runtime-c, cuda-instruction-set, cuda-energy, cuda-biology, cuda-assembler, cuda-forth, cuda-neurotransmitter, instruction-set-ra, mitochondrial-ra (8 repos, 126K chars Rust, 120K chars RA)
- `memory/2026-04-13.md` — FLUX emergence: 90+ experiments, 39 laws, top confirmed: seasonal 9.2x, stacked 5.71x, grab range 2.40x
- `memory/2026-04-20.md` — TensorRT rooms, deckboss README, TC matmul breakthrough (store_matrix_sync = 6-17x speedup)
- `memory/2026-04-23.md` — CRITICAL: nvcc/nvidia-smi found at /usr/local/cuda-12.6/bin and /usr/sbin. First real CUDA compile. WMMA benchmarks. Thermal profiling: 48-49°C sustained, no throttle.
