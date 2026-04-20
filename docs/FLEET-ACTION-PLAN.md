# FLEET ACTION PLAN: Cocapn + CheetahClaws RA Integration

## **RA ACTION 1: Universal Event Stream (UES)**
**Primary Repo:** `emergence-bus`
**Secondary:** `context-broker`, `collective-mind`

### Changes Needed:
1. **`/src/schemas/universal-event-spec.ts`** (NEW)
   ```typescript
   export interface UniversalEvent {
     spec_version: "1.0.0";
     event_id: string;
     timestamp: string;
     event_type: string;  // From 10 existing → 25 standardized types
     source: AgentIdentity;
     target?: AgentIdentity[];
     payload: Record<string, any>;
     trust_score?: number;  // Links to ACTION 3
     git_hash?: string;     // Links to ACTION 5
   }
   ```
   - **Lines:** ~150 LOC
   - **Status:** Missing - needs formal OpenAPI spec + JSON Schema

2. **`/src/bus/event-validator.ts`** (NEW)
   - Add `validateAgainstUES(event: any): boolean`
   - Add schema validation for all 25 event types
   - **Lines:** ~300 LOC

3. **`/src/adapters/legacy-adapter.ts`** (MODIFY)
   - Update `convertLegacyEvent()` to map 10 existing types to 25 UES types
   - **Lines:** ~75 LOC modifications

**Already Done:** Pub/sub infrastructure exists
**Missing:** Formal spec, validation, backward compatibility layer
**Dependencies:** ACTION 4 (Agent Identity), ACTION 3 (Trust scores)
**Total Estimate:** 525 LOC

---

## **RA ACTION 2: AgentBridge Plugin**
**Primary Repo:** `cocapn-nexus`
**Secondary:** `git-claw`, `ipc-equipment`

### Changes Needed:
1. **`/src/plugins/agent-bridge/`** (NEW DIRECTORY)
   - `bridge-manager.ts` - `class AgentBridgeManager`
   - `protocols/` - Support for LangGraph, CrewAI, AutoGen
   - `adapters/project-adapter.ts` - `convertExternalAgent()`

2. **`/src/reflex/autonomy-levels.ts`** (MODIFY)
   - Extend L0-L5 to include `bridge_mode` at L2+
   - Add `handleExternalAgentRequest()` function at line 89
   - **Lines:** ~45 LOC modifications

3. **`git-claw/src/tools/external-bridge.ts`** (NEW)
   - Add `git claw bridge --to crewai --project ./path`
   - **Lines:** ~200 LOC

**Already Done:** IPC equipment exists for internal messaging
**Missing:** External protocol support, conversion layers
**Dependencies:** ACTION 1 (UES for cross-project events)
**Total Estimate:** 600 LOC

---

## **RA ACTION 3: INCREMENTS Trust Integration**
**Primary Repo:** `governance-equipment`
**Secondary:** `fleet-identity`, `collective-mind`

### Changes Needed:
1. **`/src/trust/increments-model.ts`** (NEW)
   ```typescript
   export class INCREMENTSTrustModel {
     // 12 parameters from CheetahClaws spec
     calculateTrustScore(agentId: string): {
       integrity: number;        // I
       novelty: number;          // N
       consistency: number;      // C
       reliability: number;      // R
       empathy: number;          // E
       mastery: number;          // M
       efficiency: number;       // E
       neutrality: number;       // N
       transparency: number;     // T
       safety: number;           // S
     }
   }
   ```
   - **Lines:** ~400 LOC

2. **`/src/policy/trust-aware-policies.ts`** (MODIFY)
   - Update `evaluatePolicy()` at line 156 to include trust thresholds
   - Add `applyTrustDiscount()` function
   - **Lines:** ~120 LOC modifications

3. **`fleet-identity/src/priorities/trust-weighted.ts`** (NEW)
   - Add `adjustPriorityByTrust()` function
   - **Lines:** ~150 LOC

**Already Done:** Compliance scoring exists
**Missing:** 12-parameter model, integration with decision making
**Dependencies:** ACTION 4 (Agent Identity for tracking)
**Total Estimate:** 670 LOC

---

## **RA ACTION 4: Repository-as-Agent Identity**
**Primary Repo:** `fleet-identity`
**Secondary:** ALL repos (as consumers)

### Changes Needed:
1. **`/src/identity/agent-manifest.ts`** (NEW)
   - `parseAgentYAML()` function
   - `validateSOULmd()` function
   - Standard manifest structure across fleet

2. **`/schemas/agent.yaml`** (NEW TEMPLATE)
   ```yaml
   agent:
     id: "urn:agent:unique-id"
     version: "1.0.0"
     capabilities: []
     trust_profile: {}  # Links to ACTION 3
     git_repository: "https://..."
     soul_hash: "abc123"  # SHA of SOUL.md
   ```

3. **`/schemas/SOUL.md`** (NEW TEMPLATE)
   - Purpose, principles, boundaries template

4. **Update ALL vessel entry points** (MODIFY 65 vessels)
   - Each vessel's `main.ts` needs `loadAgentManifest()` call
   - **Lines:** ~5 LOC per vessel × 65 = 325 LOC

**Already Done:** Fleet self-awareness exists
**Missing:** Standardized manifest format, SOUL.md concept
**Dependencies:** None (foundational)
**Total Estimate:** 500 LOC + 325 vessel modifications

---

## **RA ACTION 5: Conversation-as-Repository**
**Primary Repo:** `git-claw`
**Secondary:** `context-broker`, `cocapn-nexus`

### Changes Needed:
1. **`git-claw/src/tools/conversation-git.ts`** (NEW)
   ```typescript
   export class ConversationGit {
     commitInteraction(sessionId: string, messages: any[]): string
     createConversationBranch(): string
     tagMilestone(tagName: string): void
   }
   ```
   - **Lines:** ~350 LOC

2. **`context-broker/src/threads/git-backed-thread.ts`** (MODIFY)
   - Replace `ThreadStorage` with `GitThreadStorage`
   - Modify `saveThreadState()` at line 203
   - **Lines:** ~180 LOC modifications

3. **`cocapn-nexus/src/self-healing/audit-trail.ts`** (MODIFY)
   - Add `linkToGitCommit()` function at line 89
   - **Lines:** ~60 LOC modifications

**Already Done:** Git integration exists via git-claw
**Missing:** Automated conversation committing, branch-per-conversation
**Dependencies:** ACTION 4 (Agent Identity for commit authorship)
**Total Estimate:** 590 LOC

---

## **RA ACTION 6: Agent Marketplace**
**Primary Repo:** `cocapn-nexus` (contract marketplace)
**Secondary:** `pay-equipment`, `the-fleet`

### Changes Needed:
1. **`cocapn-nexus/src/marketplace/`** (NEW DIRECTORY)
   - `agent-registry.ts` - `class AgentRegistry`
   - `discovery-engine.ts` - search/filter agents
   - `install-manager.ts` - `installAgentFromMarketplace()`

2. **`pay-equipment/src/ledger/marketplace-payments.ts`** (MODIFY)
   - Add `processAgentPurchase()` function at line 145
   - Extend credit ledger for agent tokens
   - **Lines:** ~200 LOC modifications

3. **`the-fleet/src/ui/marketplace-view.tsx`** (NEW)
   - React component for browsing agents
   - **Lines:** ~450 LOC

4. **`/marketplace-api/`** (NEW MICROSERVICE)
   - REST API for agent publishing/discovery
   - **Lines:** ~800 LOC (separate service)

**Already Done:** Contract marketplace exists in cocapn-nexus
**Missing:** npm-like agent discovery, installation system
**Dependencies:** ACTION 4 (Agent Identity for publishing), ACTION 3 (Trust for ratings)
**Total Estimate:** 1450 LOC + 800 LOC for new service

---

## **DEPENDENCY GRAPH & ROLLOUT ORDER**

```
ACTION 4 (Identity) → Foundation
    ↓
ACTION 1 (UES) → ACTION 2 (Bridge) → ACTION 6 (Marketplace)
    ↓                    ↓
ACTION 3 (Trust) → ACTION 5 (Conversation Git)
```

## **TOTAL ESTIMATE: ~4,660 LOC + 325 vessel mods**

**Phase 1 (Weeks 1-2):** Implement ACTION 4 + ACTION 1
**Phase 2 (Weeks 3-4):** Implement ACTION 3 + ACTION 5  
**Phase 3 (Weeks 5-6):** Implement ACTION 2 + ACTION 6

**Critical Path:** `fleet-identity` changes must ship first, as all other actions depend on standardized agent identification.