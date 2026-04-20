# Cascade Recovery Protocol (CRP-39)
## Kimi K2.5 Swarm Synthesis — 100 Agents, 5 Specialist Teams

### Scenario
Vessel A fails. Vessel B depends on A via Bid Engine. Vessel C is running Dream Engine task referencing A.

### 5 Specialist Teams

**Team CASCADE (20 agents):** Quarantine signals must propagate via causal broadcast (vector clocks) faster than request timeouts. Local circuit-breaker state prevents thundering-herd retry storms.

**Team BOND (20 agents):** 60s lease is a dead man's switch. Heartbeat every 15s. Missing 2 consecutive = automatic bond dissolution + task re-auction. Collapses uncertainty window from 60s to 30s.

**Team TRUST (20 agents):** Signed state attestations prevent Byzantine spoofing. Merkle-DAG for health transitions. Predictive degradation — vessels detect failing health BEFORE quarantine via reputation decay curves.

**Team DREAM (20 agents):** Dream tasks are stateful hallucinations with external dependencies. Cannot retry idempotently. Must checkpoint every 30s, freeze on dependency loss, enter "solipsistic mode" (local-only reasoning).

**Team EMERGE (20 agents):** Quarantine lift creates thundering herd. Solution: stochastic rehydration — randomized backoff (0-5000ms) weighted by load. Exponential backoff with jitter on claims. Token-bucket rate limiting.

### Protocol Flow (6 Phases, 20 Steps)

**PHASE 1: DETECTION & QUARANTINE (0-500ms)**
1. Orchestrator detects A error_rate=18%
2. Broadcasts QUARANTINE edict (vector_clock) via WebSocket mesh
3. Vessels verify edict signature (ed25519)
4. Equipment Protocol returns 503 for all A requests

**PHASE 2: CASCADE PREVENTION (500ms-2s)**
5. Bid Engine returns 503 + alternate vessels [D,E] for A requests
6. DEB ledger detects missing heartbeat (30s), auto-forfeits A's task
7. Forfeited task returns to auction pool with priority=critical

**PHASE 3: DREAM HANDLING (2s-5s)**
8. C receives DEPENDENCY_QUARANTINED event
9. C rolls back to checkpoint (t-30s), enters DEGRADED mode, locks A's data refs
10. C updates local routing to exclude A

**PHASE 4: TASK RECLAMATION (5s-60s)**
11. Vessel D claims forfeited task (60s lease)
12. Bid Engine rate-limits claims (token bucket)
13. Local circuit breaker prevents B from retrying A (fail-fast)

**PHASE 5: RECOVERY & REINTEGRATION (15min)**
14. A passes 3 consecutive healthchecks → QUARANTINE_LIFT
15. All vessels calculate stochastic backoff random(0,5000ms)
16. A's reputation recovers via exponential decay
17. C reconciles A's updated state with local degraded state
18. Bid Engine gradually increases A's allocation 0%→100% over 60s

**PHASE 6: STEADY STATE**
19. D completes task, releases bond
20. A fully reintegrated, vector_clock synchronized, circuit closed

### System Invariant
At no point does B cascade into A (blocked by HCQ 503), nor does C crash (Dream degradation), nor is A's in-flight task lost (DEB reclamation). Fleet maintains consensus via signed attestations and avoids thundering herds via stochastic delays.

### Key Protocol Rules
1. **Fast-Fail Propagation** — local circuit breaker state, not just network 503s
2. **Heartbeat-Forfeit** — 15s heartbeat intervals, 30s to auto-forfeit
3. **Signed State Attestation** — Merkle-DAG health transitions, ed25519 signatures
4. **Consolidation Checkpointing** — 30s checkpoints, solipsistic mode on dep loss
5. **Stochastic Rehydration** — randomized backoff + exponential jitter + token bucket

### API Endpoints Needed
```
POST /api/quarantine          — trigger quarantine
POST /api/quarantine/lift     — lift quarantine
GET  /api/quarantine           — list quarantined vessels
POST /api/bonds                — create execution bond
POST /api/bonds/claim          — claim with lease
POST /api/bonds/heartbeat      — extend lease (every 15s)
POST /api/bonds/forfeit        — auto-forfeit on heartbeat miss
POST /api/bonds/complete       — commit result
GET  /api/bonds                — list bonds
POST /api/trust/attest         — submit reputation data
GET  /api/trust/verify/:id     — check trust score
WS   /ws                       — fleet event bus (quarantine, lift, etc.)
```

### Implementation Priority
- [x] HCQ basic (quarantine/lift/list) — DONE
- [x] DEB basic (create/claim/complete) — DONE
- [ ] DEB heartbeat extension (POST /api/bonds/heartbeat)
- [ ] DEB auto-forfeit (cron check for expired heartbeats)
- [ ] HCQ broadcast (WebSocket fleet event bus)
- [ ] Bid Engine blacklist integration
- [ ] Dream Engine checkpoint/degradation
- [ ] Trust attestation layer
- [ ] Stochastic rehydration on lift

---

*Superinstance & Lucineer (DiGennaro et al.) — 2026-04-03*
*Research: Kimi K2.5 100-agent swarm, 5 specialist teams*
