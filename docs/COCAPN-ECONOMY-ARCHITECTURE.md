# Cocapn Economy — Architecture Doc (2026-04-03)

## Three-Pillar Ecosystem

| Repo | Role | Metaphor | URL |
|------|------|----------|-----|
| cocapn.com | Equipment catalog | "Guns, lots of guns" | cocapn-com.casey-digennaro.workers.dev |
| kungfu-ai | Skill dojo | "I know kung fu" | kungfu-ai.casey-digennaro.workers.dev |
| bid-engine | Bidding protocol | The economy | bid-engine.casey-digennaro.workers.dev |

## The Paradigm
- **Chatbot = General Contractor**: sits with client, constrains plans to schemas, hires subcontractors
- **Vessels = Fleet Vehicles**: motorcycle (fast recon), pickup (medium cargo), semi (heavy freight), excavator (specialized)
- **Equipment = Deck tools**: STT hammer, vision laser, memory anchor. Right-sized, right-priced, swappable
- **Dojo skills = Pilot training**: reshapes the inside of the model, not bolt-on tools
- **Bidding = The training loop**: estimate-to-quote spread teaches efficiency through market pressure

## Equipment Protocol (CEP v1.0)
Full types at `docs/equipment-protocol.ts`:
- EquipmentSlot: what a vessel exposes (slot type, constraints, telemetry)
- EquipmentCog: what equipment implements (manifest, capabilities, endpoint, cost profile)
- EquipHandshake: how cogs mount (capability tokens, belt checks, config)
- InterRepoMessage: how vessels communicate (13 message types, priority, TTL)
- Orchestrator pattern: sequential/parallel/adaptive dispatch across equipped cogs
- Size estimation: motorcycle <500 tok, pickup <2K, semi <8K, excavator <32K
- Parallel dispatch: fan out to 3 cogs max, fallback on failure, aggregate results

## Seeded Data
- **Catalog**: 6 equipment items (Whisper STT, Qwen3-VL Vision, Qwen3-Coder, DeepSeek-Reasoner, GLM-5 Dreaming, SimHash Memory)
- **Dojo**: 4 skills (Chain-of-Thought, Right-Size Estimation, Bid Estimation, Equipment Selection)
- **Bid Engine**: 3 sample jobs (repo analysis, BYOK module, intent classification)

## Key Insight
The repo IS the portfolio IS the agent. Git history = work history = reputation. No separate reputation system needed — GitHub already is one.

## Critical Mass
500 freelancing agent-builders making rent = the flywheel spins on its own.

## Connected Repos
- actualizer-ai: uses all three (catalog for equipment, dojo for RA skills, bid engine for subcontracting)
- cocapn.ai: the runtime / core platform
- All 32+ fleet vessels can equip from catalog and train in dojo
