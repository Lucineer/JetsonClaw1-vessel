# log-origin Protocol Specification

> **Status:** Draft — Expert 4 deliverable
> **Date:** 2026-03-25

---

## Table of Contents

1. [MCP Integration](#1-mcp-integration)
2. [Agent Communication Protocol](#2-agent-communication-protocol)
3. [Local Instance Protocol](#3-local-instance-protocol)
4. [Cross-Instance Federation](#4-cross-instance-federation)
5. [Devil's Advocate](#5-devils-advocate)
6. [Open Questions](#6-open-questions)

---

## 1. MCP Integration

log-origin exposes itself as a Model Context Protocol server via **Streamable HTTP** transport (not stdio — we run on Cloudflare Workers).

### Transport

**Endpoint:** `POST /mcp/v1`  
**Content-Type:** `application/json` (single request) or `application/json; boundary=mcp` (batch)  
**Response:** JSON-RPC 2.0  

### Authentication

MCP clients authenticate via `Authorization: Bearer <api_key>` header. The same API keys used for the REST API work here.

For MCP clients that can't set headers (some tooling), query param fallback: `?token=<api_key>`

### Initialization

Standard MCP `initialize` handshake:

```json
→ {
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2025-03-26",
    "capabilities": {},
    "clientInfo": {"name": "claude-desktop", "version": "1.0.0"}
  }
}

← {
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2025-03-26",
    "capabilities": {
      "tools": {"listChanged": true}
    },
    "serverInfo": {"name": "log-origin", "version": "0.1.0"}
  }
}
```

### Exposed Tools

#### `route_message`

Send a message through log-origin's routing engine and get the response.

```json
{
  "name": "route_message",
  "description": "Send a message through log-origin's intelligent routing (model selection, caching, PII handling).",
  "inputSchema": {
    "type": "object",
    "properties": {
      "message": {"type": "string", "description": "The user message"},
      "system_prompt": {"type": "string", "description": "Optional system prompt"},
      "session_id": {"type": "string", "description": "Optional session ID"},
      "model": {"type": "string", "enum": ["auto", "cheap", "escalation", "local"], "default": "auto"}
    },
    "required": ["message"]
  }
}
```

**Returns:**
```json
{
  "content": "The response text...",
  "model": "claude-3.5-sonnet",
  "route": {"action": "escalation", "confidence": 0.92},
  "interaction_id": "int_abc",
  "latency_ms": 1823,
  "cached": false
}
```

#### `compare_models`

Run a query against multiple models side-by-side.

```json
{
  "name": "compare_models",
  "description": "Compare responses from multiple LLM providers for the same query.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "message": {"type": "string"},
      "models": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Provider:model pairs, e.g. ['anthropic:claude-3.5-sonnet', 'openai:gpt-4o']"
      },
      "session_id": {"type": "string"}
    },
    "required": ["message"]
  }
}
```

#### `get_feedback_stats`

Retrieve aggregated feedback data.

```json
{
  "name": "get_feedback_stats",
  "description": "Get feedback statistics for recent interactions.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "period": {"type": "string", "enum": ["1h", "24h", "7d", "30d"], "default": "7d"},
      "route": {"type": "string", "description": "Filter by route action (optional)"}
    }
  }
}
```

#### `submit_feedback`

Submit a feedback rating.

```json
{
  "name": "submit_feedback",
  "description": "Submit thumbs up/down feedback for an interaction.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "interaction_id": {"type": "string"},
      "value": {"type": "string", "enum": ["thumbs_up", "thumbs_down"]},
      "comment": {"type": "string"}
    },
    "required": ["interaction_id", "value"]
  }
}
```

#### `get_routing_info`

Inspect routing decisions and rules.

```json
{
  "name": "get_routing_info",
  "description": "Get current routing configuration and recent routing decisions.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "include_stats": {"type": "boolean", "default": true},
      "include_rules": {"type": "boolean", "default": true}
    }
  }
}
```

#### `manage_session`

Create, list, or delete sessions.

```json
{
  "name": "manage_session",
  "description": "Manage chat sessions.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "action": {"type": "string", "enum": ["list", "get", "create", "delete"]},
      "session_id": {"type": "string"},
      "summary": {"type": "string"},
      "limit": {"type": "integer", "default": 20}
    },
    "required": ["action"]
  }
}
```

### Resources (Prompts)

log-origin also exposes MCP resources for prompt templates:

```json
{
  "name": "prompt_templates",
  "description": "Available prompt engineering templates",
  "uri": "logorigin://prompts",
  "mimeType": "application/json"
}
```

---

## 2. Agent Communication Protocol

### Overview

Agents register with log-origin as message handlers. Log-origin routes messages to registered agents based on capabilities, availability, and priority.

### Agent Registration

```http
POST /v1/agents/register
Authorization: Bearer <agent_token>
```

```json
{
  "agent_id": "agent_weather_monitor",
  "name": "Weather Monitor",
  "version": "1.0.0",
  "capabilities": [
    "weather.query",
    "weather.forecast"
  ],
  "endpoint": "https://my-agent.example.com/inbox",
  "heartbeat_url": "https://my-agent.example.com/health",
  "max_latency_ms": 5000,
  "metadata": {
    "location": "anchorage_ak",
    "owner": "lucineer"
  }
}
```

**Response:**
```json
{
  "status": "registered",
  "agent_id": "agent_weather_monitor",
  "instance_id": "inst_abc123",
  "expires_at": "2026-03-26T20:00:00Z"
}
```

### Message Format

All inter-agent messages use a standard envelope:

```json
{
  "id": "msg_abc123",
  "type": "request",
  "from": {
    "instance_id": "inst_logorigin_main",
    "agent_id": "logorigin"
  },
  "to": {
    "instance_id": "inst_abc123",
    "agent_id": "agent_weather_monitor"
  },
  "method": "weather.query",
  "params": {
    "location": "Anchorage, AK",
    "units": "metric"
  },
  "timestamp": "2026-03-25T20:00:00Z",
  "reply_to": "msg_xyz789",
  "ttl_seconds": 30
}
```

**Response envelope:**
```json
{
  "id": "msg_def456",
  "type": "response",
  "from": {
    "instance_id": "inst_abc123",
    "agent_id": "agent_weather_monitor"
  },
  "to": {
    "instance_id": "inst_logorigin_main",
    "agent_id": "logorigin"
  },
  "in_reply_to": "msg_abc123",
  "result": {
    "temperature_c": -5,
    "condition": "snow",
    "wind_kph": 25
  },
  "timestamp": "2026-03-25T20:00:01Z"
}
```

### Message Types

| type | direction | when |
|---|---|---|
| `request` | router → agent | routed task |
| `response` | agent → router | result |
| `error` | agent → router | failure with code + message |
| `broadcast` | router → many | capability announcement |
| `unsubscribe` | agent → router | deregistration |

### Heartbeat Protocol

Agents must send heartbeats to stay registered.

```http
POST /v1/agents/heartbeat
Authorization: Bearer <agent_token>
```

```json
{
  "instance_id": "inst_abc123",
  "status": "healthy",
  "load": 0.3,
  "capabilities": ["weather.query", "weather.forecast"]
}
```

- **Interval:** Every 30 seconds
- **Grace period:** 90 seconds (3 missed heartbeats)
- **After grace:** Agent marked `unhealthy`, removed from routing
- **Re-registration:** Agent can re-register at any time

### Capability Negotiation

On registration, log-origin returns available capabilities it needs:

```json
{
  "status": "registered",
  "required_capabilities": ["llm.generate", "llm.compare"],
  "optional_capabilities": ["feedback.submit", "session.manage"]
}
```

Agents declare which they support. Log-origin only routes methods matching declared capabilities.

### Routing Algorithm

```
1. Agent declares capability matching method? → Yes: continue
2. Agent status healthy? → Yes: continue
3. Agent load < threshold? → Yes: continue
4. Agent latency within max? → Yes: route
5. If multiple candidates: pick lowest load
6. If no candidates: return error to caller
```

---

## 3. Local Instance Protocol

### Overview

A log-origin instance can run locally (on a home server, laptop, or edge device) and register with a cloud instance. This enables:

- Local model inference with cloud fallback
- PII never leaves the local machine
- Cloud handles API key management, routing intelligence, and metrics

### Connection: Cloudflare Tunnel + Bearer Token

```
┌─────────────┐     Cloudflare Tunnel     ┌──────────────────┐
│  Local      │ ◄════════════════════════► │  Cloud (Workers)  │
│  Instance   │  encrypted, outbound only  │  logorigin.dev    │
└─────────────┘                            └──────────────────┘
```

**Why Cloudflare Tunnel?**
- No inbound port forwarding needed
- No public IP required
- Encrypted end-to-end
- Works behind NAT/firewalls
- Free tier available

### Registration Flow

```
1. Local instance generates: instance_id, ed25519 keypair
2. Local → Cloud: POST /v1/instances/register
   Body: { instance_id, public_key, capabilities, location }
3. Cloud → Local: { tunnel_token, registration_confirmed: true }
4. Local → Cloudflare: establishes tunnel with tunnel_token
5. Cloud → Local: verifies tunnel is reachable via tunnel domain
6. Local → Cloud: POST /v1/instances/confirm
   Body: { instance_id, tunnel_ready: true }
7. Cloud: marks instance as "online", starts routing to it
```

### Request Routing: Cloud → Local → Response

When a request should be handled locally:

1. Cloud receives `POST /v1/chat/completions` with `model: "auto"` or `"local"`
2. Routing engine determines local instance is appropriate (e.g., PII detected)
3. Cloud sends request to local via tunnel:
   ```
   POST https://<instance-tunnel>.cfargotunnel.com/v1/local/completions
   X-LogOrigin-Forwarded-By: inst_cloud_main
   X-LogOrigin-Request-Id: req_abc123
   Authorization: Bearer <shared_secret>
   ```
4. Local processes request (local model, dehydration, etc.)
5. Local responds with standard chat completion format
6. Cloud forwards response to original client

### Health Monitoring

```
Cloud pings local every 15s:
  → GET https://<tunnel>/v1/health
  ← { "status": "ok", ... }

If 3 consecutive failures:
  → mark instance "offline"
  → reroute pending requests to cloud fallback
  → emit alert via webhook/notification

When instance comes back:
  → auto-reregister on first successful health check
  → mark "online" with warm-up period (10s reduced traffic)
```

### Local Goes Offline: What Happens?

| scenario | behavior |
|---|---|
| Local healthy | Route to local |
| Local unhealthy (transient) | Retry once, then fallback to cloud |
| Local offline (>90s) | All traffic to cloud; notify owner |
| Local returns | Auto-reconnect, gradual traffic ramp-up |
| Cloud unreachable | Local runs independently; queue for sync |

### Data Sync

When reconnected after offline:

```
Local → Cloud: POST /v1/instances/sync
Body: {
  "instance_id": "inst_local_001",
  "interactions": [...],  // interactions that happened offline
  "feedback": [...],      // feedback submitted offline
  "metrics": {...}        // local usage metrics
}
```

Cloud merges with deduplication (by interaction_id).

---

## 4. Cross-Instance Federation

### Overview

Two log-origin instances can federate to share capabilities, context, and routing intelligence. Built on the **A2A (Agent-to-Agent)** protocol.

### Why Federate?

- Multiple users/orgs want to share routing intelligence
- Pool provider API keys across instances
- Specialized instances (e.g., one for code, one for creative writing)
- Redundancy and failover

### Identity Verification

Each instance has:
- **Instance ID:** `inst_<ed25519_fingerprint>` — unique, stable
- **Ed25519 keypair:** used to sign all federation messages
- **Human-readable name:** configured by operator

**Verification handshake:**

```
1. Instance A → Instance B: Hello
   {
     "instance_id": "inst_aaa",
     "name": "Lucineer's Main",
     "public_key": "<base64>",
     "capabilities": ["llm.generate", "pii.dehydrate"],
     "timestamp": "..."
   }
   Signature: ed25519(sign(body, key_a))

2. Instance B verifies signature, checks instance_id isn't blacklisted

3. Instance B → Instance A: Hello Ack
   { "instance_id": "inst_bbb", "accepted": true }
   Signature: ed25519(sign(body, key_b))

4. Instance A → Instance B: Session Key Exchange (X25519 DH)
   Both derive shared session key for encrypted communication

5. Federation established. Both sides emit ` federation.connected` event.
```

### Capability Exchange

```json
{
  "type": "capability_exchange",
  "from": "inst_aaa",
  "capabilities": {
    "llm.generate": {
      "models": ["claude-3.5-sonnet", "gpt-4o", "llama-3.1-8b"],
      "rate_limit_rpm": 60,
      "priority": 5
    },
    "pii.dehydrate": {
      "schemas": ["us_ssn", "email", "phone"],
      "priority": 10
    },
    "routing.classify": {
      "supported_actions": ["cheap", "escalation", "local", "draft"],
      "priority": 3
    }
  }
}
```

### Permission Model

**Federated instances have scoped permissions.** Nothing is open by default.

| permission | description | default |
|---|---|---|
| `route:send` | Send routed requests to this instance | denied |
| `route:receive` | Accept requests from this instance | denied |
| `metrics:read` | Read usage metrics | denied |
| `models:list` | See available models | denied |
| `feedback:share` | Receive/share feedback data | denied |
| `cache:query` | Query semantic cache | denied |

**Granting permissions:**

```json
POST /v1/federation/grant
{
  "instance_id": "inst_bbb",
  "permissions": ["route:send", "metrics:read"],
  "conditions": {
    "max_requests_per_hour": 100,
    "allowed_models": ["claude-3.5-sonnet"],
    "allowed_routes": ["cheap", "escalation"]
  },
  "expires_at": "2026-06-25T00:00:00Z"
}
```

**Revoking:** `DELETE /v1/federation/grants/inst_bbb` or wait for expiry.

### Federation Message Format

All federation communication uses encrypted JSON over HTTPS:

```json
{
  "protocol": "a2a/1.0",
  "id": "fed_msg_abc",
  "from": "inst_aaa",
  "to": "inst_bbb",
  "type": "request",
  "method": "llm.generate",
  "params": {
    "messages": [{"role": "user", "content": "Hello"}],
    "model": "claude-3.5-sonnet",
    "max_tokens": 1024
  },
  "timestamp": "2026-03-25T20:00:00Z",
  "nonce": "random_32_bytes",
  "signature": "ed2559_sign(<hash>, session_key)"
}
```

### Cross-Instance Routing

When Instance A routes a request to Instance B:

1. A checks B has `route:receive` permission
2. A checks B has the requested capability
3. A checks request is within rate limits
4. A sends encrypted request to B's `/v1/federation/inbox`
5. B processes, returns result
6. A logs the interaction (proxied), B logs (executed)
7. Both record latency and cost

---

## 5. Devil's Advocate

### "Why OpenAI-compatible instead of your own clean API?"

**Counterargument:** A custom API could be cleaner, more consistent, and avoid historical baggage.

**Reality:** Adoption is the killer feature. The OpenAI API is the de facto standard. By being compatible:
- Every existing tool, library, and wrapper works immediately
- New users can test with zero setup
- The cost of "unclean" is a `_meta` object — trivial
- You can always add a clean v2 later; you can't retroactively gain ecosystem compatibility

**Verdict:** OpenAI-compatible for `/v1/chat/completions`. Custom endpoints for everything log-origin-specific (drafts, routing, agents). Best of both worlds.

---

### "Why SSE instead of WebSocket?"

**Counterargument:** WebSocket is bidirectional, lower overhead for persistent connections, and more efficient for real-time apps.

**Reality:**
- **SSE works through every proxy, CDN, and corporate firewall.** WebSocket often doesn't.
- **HTTP/2 multiplexing** gives you the bidirectional-like behavior with SSE — multiple streams on one connection
- **SSE is simpler.** No connection lifecycle management, no ping/pong, no reconnection logic (browsers handle it)
- **The OpenAI SDK expects SSE.** Staying compatible means streaming works out of the box.
- **Workers don't support WebSocket** for arbitrary upstream connections easily

**Verdict:** SSE for LLM streaming. WebSocket is overkill for request-response streams and introduces complexity for no gain in our use case.

---

### "Why not use gRPC?"

**Counterargument:** gRPC is faster (protobuf, HTTP/2, binary), has strong typing, and built-in streaming.

**Reality:**
- **Cloudflare Workers don't support gRPC natively.** You'd need a proxy layer — defeats the purpose.
- **No browser support** without grpc-web shim — more complexity.
- **Debugging is harder** — binary protocol vs readable JSON.
- **OpenAI SDK compatibility is impossible** — gRPC has its own IDL and code generation.
- **JSON is good enough.** For our request/response sizes (a few KB), the serialization difference is negligible.

**Verdict:** REST+JSON. If Workers ever get native gRPC, we can add a gRPC gateway. Not worth the complexity now.

---

### "The non-standard fields will break strict OpenAI clients"

**Counterargument:** Some OpenAI SDKs and wrappers validate response schemas strictly and reject unknown fields.

**Our approach — defense in depth:**

1. **`_meta` naming convention:** Underscore prefix is a strong signal for "extension, ignore if unknown." Most JSON parsers and SDKs skip unknown keys.

2. **Server-side opt-out header:** Clients can send `X-LogOrigin-Mode: strict` to get a pure OpenAI response with no `_meta`:
   ```json
   {
     "id": "chatcmpl-abc",
     "choices": [...],
     "usage": {...},
     "model": "claude-3.5-sonnet"
     // No _meta at all
   }
   ```
   Routing metadata is then available via `GET /v1/interactions/{id}` for clients that want it separately.

3. **Response headers for metadata:** For clients that can't parse JSON extensions:
   ```
   X-LogOrigin-Route: escalation
   X-LogOrigin-Latency-Ms: 1823
   X-LogOrigin-Interaction-Id: int_abc
   X-LogOrigin-Cached: false
   ```

4. **SDK compatibility testing:** We test against the official OpenAI Python and JS SDKs. If a strict SDK version rejects our responses, the `strict` mode header is the escape hatch.

**Verdict:** `_meta` for the default (works with 99% of clients), `strict` mode header for the 1% that need it, and response headers for metadata-only needs.

---

## 6. Open Questions

1. **MCP transport version** — The MCP spec is evolving. Do we support both `application/json` and the newer `application/json; boundary=mcp` batch format? Start with single-request JSON, add batch later.

2. **Agent auth model** — Should agents use long-lived tokens or short-lived JWTs? Long-lived tokens are simpler for always-on agents; JWTs are more secure. Proposal: long-lived tokens with rotation support.

3. **Federation discovery** — How do instances find each other? Manual configuration? A public registry? DHT? Start with manual (exchange instance IDs + public keys) — decentralized discovery is a future concern.

4. **Local sync conflict resolution** — When local and cloud both have new interactions during an outage, which wins? Proposal: last-write-wins per interaction_id (each instance generates unique IDs), no conflicts possible.

5. **Federation rate limiting** — Who enforces rate limits on federated requests? Both sides. The sender checks its own limits, the receiver enforces its own. Double-checking prevents abuse.

6. **Agent webhook callback** — Should agents be able to send asynchronous notifications back to log-origin (not just respond to requests)? Useful for proactive alerts. Proposal: agents can `POST /v1/agents/notify` with their token.

7. **Protocol versioning** — Agent and federation protocols need version negotiation. Include `protocol_version` in every message. If versions mismatch, return a clear error with supported versions.
