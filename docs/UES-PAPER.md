**Title:** The Universal Event Stream: HTTP for Cognition

**Abstract**
This paper introduces the Universal Event Stream (UES), a minimal protocol for agent cognition, derived from the convergent evolution of two distinct agent architectures: the CheetahClaws framework and the Cocapn fleet. Despite independent development—one a monolithic Python generator-based system, the other a distributed fleet on edge workers—both systems arrived at semantically equivalent event-driven communication patterns. We synthesize insights from the CheetahClaws Reverse-Actualization (RA) Ideation Library’s analysis of core cognitive operations with Cocapn’s fleet-scale event taxonomy. The resulting UES proposes four universal primitive operations (THINK, SPEAK, ACT, DONE) as a foundational layer, extensible for multi-agent fleet dynamics. We argue that transport-agnostic, structured event streaming over any reliable byte channel (stdio, HTTP, WebSocket) is the essential substrate for a heterogeneous “cognition mesh,” enabling interoperability without imposing architectural constraints.

**1. Introduction: The Agent Protocol Problem**
The rapid proliferation of AI agent frameworks has led to a Tower of Babel problem in agent communication. Each system, from research prototypes like UC Berkeley’s CheetahClaws to production fleets like Cocapn, implements its own internal dialogue between components, planners, and tools. This fragmentation stifles interoperability, complicates benchmarking, and forces developers to commit prematurely to a single architectural paradigm. The CheetahClaws RA Library’s “Round 23: Universal Agent Protocol” and Cocapn’s “emergence-bus” event system represent parallel discoveries of a solution: agent cognition is fundamentally a stream of typed events. This paper formalizes that discovery.

**2. Event Stream Convergence**
Agent frameworks converge on event streaming because cognition is temporal and stateful. A monolithic Python agent (CheetahClaws) uses generator functions to `yield` control and events, while a distributed fleet (Cocapn) uses a pub/sub bus to decouple vessels. Both models reject rigid RPC in favor of observable, serializable state transitions. The RA library identified this as a reverse-actualization pattern: the external protocol *should be* the internal execution model made explicit. When an agent’s “inner monologue” becomes its API, debugging, orchestration, and composition become native operations. This convergence suggests an underlying invariant: **cognition is a traceable event sequence.**

**3. The Four Operations**
The RA library’s analysis distilled all agent activity into four irreducible primitives, which form the UES base layer:

1.  **THINK:** Internal state change, reasoning, or planning. It has no direct external effect but must be observable for interpretability.
    ```json
    {"type": "THINK", "id": "t1", "content": "Analyzing user request to find a relevant paper."}
    ```
2.  **SPEAK:** Communication intended for a user or another agent. This is information output.
    ```json
    {"type": "SPEAK", "id": "s1", "content": "I will search for that paper now."}
    ```
3.  **ACT:** Invocation of a capability (tool, function, API) to change external state.
    ```json
    {
      "type": "ACT",
      "id": "a1",
      "name": "search_academic_db",
      "args": {"query": "event streaming agents"},
      "result_pending": true
    }
    ```
4.  **DONE:** Signals the completion of a unit of work, often carrying a final result or terminal state. It can close a loop opened by a prior ACT or THINK.
    ```json
    {"type": "DONE", "id": "d1", "triggered_by": "a1", "result": "Found 3 relevant papers."}
    ```

These four types form a complete basis for single-agent cognition. Every CheetahClaws generator event and every Cocapn vessel-internal step can be mapped onto this schema.

**4. Fleet Extensions**
Multi-agent fleets require events that manage relationships and global state. Cocapn’s 10+ event types extend the primitives into the social dimension. UES accommodates these as reserved namespace extensions prefixed with `fleet.`:

*   **Trust & Governance:** `fleet.trust.updated`, `fleet.vote.submitted`
*   **Goal Lifecycle:** `fleet.goal.submitted`, `fleet.goal.completed`, `fleet.step.done`
*   **Discovery & Coordination:** `fleet.agent.discovered`, `fleet.capability.advertised`
*   **System Awareness:** `fleet.threat.detected`, `fleet.health.reported`

Critically, these fleet events are themselves instances of the base types. A `fleet.goal.submitted` event is an **ACT** taken by an agent upon the collective goal pool. A `fleet.threat.detected` is a **SPEAK** broadcast to the fleet. This layering ensures the protocol remains coherent from single-agent to multi-agent scale.

**5. Transport Independence**
UES is defined as a sequence of newline-delimited JSON (NDJSON) objects. This simple format can be written to any reliable byte stream:
*   **stdio:** For containers or local processes (CheetahClaws’ native mode).
*   **HTTP POST/GET:** For request/response or long-polling. A worker receives an event stream via POST and can respond with its own stream.
*   **WebSocket:** For full-duplex, persistent connections (Cocapn’s primary bus bridge).
*   **KV Store / Stream:** For persistence and replay (as in Cloudflare Workers KV/Durable Objects).

The protocol is agnostic to the carrier. An agent can be migrated from a local Python script (stdio) to a Cloudflare Worker (HTTP) by changing only the transport driver, not its cognitive logic.

**6. Backward Compatibility**
Mapping existing systems to UES demonstrates its unifying power.

**CheetahClaws Generator Events:**
```python
# Original CheetahClaws yield
yield {"type": "function_call", "name": "search", "args": {...}}
# UES Mapping
{"type": "ACT", "id": "call_1", "name": "search", "args": {...}, "result_pending": true}
```

**Cocapn Fleet Events:**
```javascript
// Original Cocapn emergence-bus event
bus.emit('goal.submitted', { goalId: 'g1', priority: 5 });
// UES Mapping
{"type": "fleet.goal.submitted", "id": "evt_xyz", "goal_id": "g1", "priority": 5}
```

The mapping is lossless. UES becomes a *lingua franca* for cross-framework agent observation and integration.

**7. The Protocol that Enables the Cognition Mesh**
The UES specification enables a **cognition mesh**: a heterogeneous network where agents of different architectures can collaborate by exchanging event streams. A CheetahClaws planner can emit a `THINK` event that a Cocapn vessel subscribes to, translating it into a `fleet.step.done`. The mesh is governed by two principles:
1.  **Observability First:** Every cognitive act is an event.
2.  **Minimal Commitment:** Systems agree only on the event format and transport, not on internal architectures.

This mirrors the success of HTTP/TCP: a simple, universal protocol enabled an explosion of heterogeneous applications.

**8. Implementation Notes**
A practical UES implementation requires a lightweight schema and validation.

**JSON Schema Core:**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "UESEvent",
  "type": "object",
  "required": ["type", "id"],
  "properties": {
    "type": { "type": "string", "pattern": "^(THINK|SPEAK|ACT|DONE|fleet\\..+)$" },
    "id": { "type": "string" },
    "content": { "type": "string" },
    "name": { "type": "string" },
    "args": { "type": "object" },
    "result": {},
    "triggered_by": { "type": "string" },
    "timestamp": { "type": "string", "format": "date-time" }
  }
}
```

**TypeScript Types:**
```typescript
type UESBaseEvent = {
  id: string;
  timestamp?: string;
};

type THINK = UESBaseEvent & { type: 'THINK'; content: string };
type SPEAK = UESBaseEvent & { type: 'SPEAK'; content: string };
type ACT = UESBaseEvent & {
  type: 'ACT';
  name: string;
  args?: object;
  result_pending?: boolean;
};
type DONE = UESBaseEvent & { type: 'DONE'; triggered_by?: string; result?: any };

type FleetEvent = UESBaseEvent & { type: `fleet.${string}`; [key: string]: any };

type UESEvent = THINK | SPEAK | ACT | DONE | FleetEvent;
```

Validation should be permissive for extensions but strict on required fields and base types.

**9. Conclusion**
The Universal Event Stream protocol is not another agent framework. It is the extraction of the common pattern already inherent in divergent systems, as evidenced by the independent development of CheetahClaws and Cocapn. By standardizing on the four cognitive primitives (THINK, SPEAK, ACT, DONE) and a mechanism for fleet-scale extensions, UES provides a minimal, transport-agnostic substrate for agent interoperability. It allows the internal event stream of a Python generator to become the public API of a distributed fleet vessel, enabling a true cognition mesh. The future of agent collaboration lies not in a single monolithic architecture, but in a universal protocol that lets cognitive events flow as freely as packets on the internet.