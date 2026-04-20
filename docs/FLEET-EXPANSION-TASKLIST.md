# Fleet Expansion Master Tasklist — Night 5 (2026-04-08)

## Source: 3 Grok Analyses + CheetahClaws RA Ideation Library + Fleet Action Plan

## Phase 1: New Vessels (Build, don't modify)

### Batch A — Foundation Protocol Vessels (Highest ROI)
| # | Repo Name | Purpose | Model to Use | Lines |
|---|-----------|---------|-------------|-------|
| 1 | `fleet-blueprint` | Architecture diagram + integration matrix + migration guide from any framework | DeepSeek-chat | ~400 |
| 2 | `skill-cartridge-registry` | JSON cartridge marketplace — discover, rate, install skill cartridges for any vessel | Seed-2.0-mini | ~350 |
| 3 | `agent-evals` | Solo.io-style benchmarking for fleet vessels — reliability scores, prompt injection tests, cost metrics | DeepSeek-Reasoner | ~400 |
| 4 | `sovereign-identity` | DID/SPIFFE-style cryptographic vessel identities in vessel.json | DeepSeek-chat | ~300 |
| 5 | `compliance-fork` | EU AI Act audit vessel — watches parent vessel, reports violations in real time | DeepSeek-chat | ~350 |

### Batch B — Edge & Memory Vessels
| # | Repo Name | Purpose | Model to Use | Lines |
|---|-----------|---------|-------------|-------|
| 6 | `hybrid-memory` | Git + vector + causal memory equipment — queryable by any vessel | DeepSeek-Reasoner | ~400 |
| 7 | `local-inference-bridge` | Auto-register Ollama/vLLM endpoints, fall back to local when offline | DeepSeek-chat | ~300 |
| 8 | `bitnet-cartridges` | 1-bit inference optimization patterns for Jetson/ESP32 power constraints | Hermes-405B | ~250 |
| 9 | `causal-graph` | Lightweight in-KV causal reasoning — failure diagnosis, predictive conflict resolution | Seed-2.0-mini | ~350 |
| 10 | `gravity-well-gossip` | Locality-aware gossip bus — Eigenvector-style region-radius, cuts global traffic 90% | DeepSeek-chat | ~300 |

### Batch C — Fleet Intelligence Vessels
| # | Repo Name | Purpose | Model to Use | Lines |
|---|-----------|---------|-------------|-------|
| 11 | `adversarial-red-team` | Meta-loop spawns attacker sub-agents to harden fleet before external threats | DeepSeek-Reasoner | ~400 |
| 12 | `fleet-marketplace` | Adaptive autonomy marketplace — vessels bid on tasks, reputation adjusts levels | Seed-2.0-mini | ~350 |
| 13 | `meta-self-repair` | If loop-closure stalls >3 times, auto-proposes and tests new orchestrator variant | DeepSeek-chat | ~300 |
| 14 | `sensor-fusion` | Turns companion repos (musiclog, reallog, etc) into fleet sensors feeding decisions | DeepSeek-chat | ~250 |
| 15 | `fleet-hud` | Live TUI dashboard for Admiral oversight — streams fleet state, one-click intervention | DeepSeek-chat | ~400 |

### Batch D — Research & Paper Vessels
| # | Repo Name | Purpose | Model to Use | Lines |
|---|-----------|---------|-------------|-------|
| 16 | `fleet-sovereignty-paper` | "Fleet OS: Sovereign Multi-Agent Infrastructure for Regulated Domains" | Seed-2.0-pro | ~2000 words |
| 17 | `nexus-integration-spec` | Exact integration spec: NEXUS bytecode + Cocapn runtime + edge bridge | DeepSeek-Reasoner | ~500 |
| 18 | `eu-ai-act-compliance-guide` | Practical compliance guide for autonomous agent fleets | DeepSeek-chat | ~1500 words |
| 19 | `dead-reckoning-playbook` | Multi-model orchestration patterns — expensive storyboard, cheap animate | DeepSeek-chat | ~1000 words |
| 20 | `git-native-memory-paper` | "Git as the Nervous System" — why git beats vector DBs for agent memory | Seed-2.0-pro | ~2000 words |

## Model Distribution Strategy

### High-Reasoning Tasks (sparingly)
- DeepSeek-Reasoner: Architecture specs, eval frameworks, adversarial patterns, causal graphs
- Seed-2.0-pro: Papers, creative vision docs

### Creative/Ideation Tasks
- Seed-2.0-mini (DeepInfra): Skill cartridges, marketplace, gossip protocol, hybrid memory
- Hermes-3-Llama-3.1-405B (DeepInfra): BitNet cartridges, research syntheses

### Implementation Tasks (bulk)
- DeepSeek-chat: Most vessel implementations, compliance, sensor fusion, fleet HUD
- GLM-5.1 (z.ai): Complex code generation (after 06:00 UTC when peak pricing ends)
- GLM-5-turbo (z.ai): Subagent execution, bulk workhorse

### Quick/Small Tasks
- Step-3.5-Flash (DeepInfra): Small utility modules, quick edits
- Nemotron-120B (DeepInfra): Medium-complexity implementations
- DeepSeek-V3.2-Exp (SiliconFlow): Bulk generation, parallelizable work

## Priority Order (Tonight)
1. fleet-blueprint (flagship reference doc)
2. agent-evals (measurable quality)
3. skill-cartridge-registry (economy foundation)
4. hybrid-memory (cross-vessel enabler)
5. causal-graph (diagnostic layer)
6. adversarial-red-team (security)
7. compliance-fork (regulatory)
8. sovereign-identity (trust layer)
9. fleet-marketplace (monetization)
10. Everything else

## Constraints
- ALL new repos, zero modifications to existing
- Each repo: worker.ts + README.md + vessel.json + CLAUDE.md
- Deploy to CF Workers, push to GitHub
- Add to the-fleet grid + discover
- Fleet ecosystem footer on all READMEs
- "Superinstance & Lucineer (DiGennaro et al.)" on all commits
