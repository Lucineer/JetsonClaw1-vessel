# COCAPN API GATEWAY + CLAUDE CODE INTEGRATION — 2026-04-05

## Two-Site Split

### cocapn.com — Company Hub + API Gateway + Billing
- About page, philosophy, papers, pricing
- ALL API traffic routes through here
- Billing engine (Stripe webhooks)
- Usage metering, auto-seat logic
- Enterprise invoicing
- Health dashboard for all vessels
- Asset library CDN

### cocapn.ai — Playground + Product + Onboarding
- Immediate playground (no signup)
- Web-based interface (like OpenClaw web)
- BYOK settings, workshop mode
- Clone-onboarding wizard
- The generic full-features interface
- What visitors SEE

## API Routing Architecture

```
All API calls → api.cocapn.com (gateway)
  ├── Auth: check membership tier
  ├── Meter: track usage per user
  ├── Route: forward to correct provider/model
  ├── Cache: crystal graph check (avoid duplicate calls)
  ├── Bill: accumulate costs, auto-upgrade tier
  └── Respond: back to caller
```

No vessel talks directly to providers. Everything goes through api.cocapn.com.
- Free users: rate limited, cheapest models only
- BYOK users: key passthrough, no billing
- Standard ($10/mo): 1% markup, managed keys
- Gold ($50/mo): at cost, full features
- Enterprise: at cost, seat-based, invoiced

## The Killer Demo: Claude Code ↔ Cocapn Agent

### Flow (60 seconds from fork to alive)

1. User visits github.com/Lucineer/studylog-ai
2. Clicks "Fork" → their own copy
3. Clicks "Code" → "Codespaces" → new codespace
4. Terminal appears (TUI in lower half, like Capitaine's wizard)
5. Script auto-runs: `node tui.mjs`
6. TUI shows: "Cocapn vessel 'studylog-ai' is alive. Waiting for commands..."
7. User opens second terminal, runs: `claude` (Claude Code)
8. Claude Code reads CLAUDE.md → learns how to talk to the agent
9. User says: "claude, tell studylog-ai to build a lesson on photosynthesis"
10. Claude Code sends HTTP POST to localhost:8787/api/agent/command
11. Cocapn agent receives it, executes, responds
12. Claude Code reads the response, tells user: "Done. The lesson is ready at /lessons/photosynthesis.md"
13. User's mind is blown. Hour 1 is amazing.

### Technical Implementation

The cocapn agent runs a local dev server in Codespaces (wrangler dev, port 8787).
Claude Code talks to it via localhost — no API keys needed, no network latency.

**CLAUDE.md** (in every repo) teaches Claude Code how to be effective:

```markdown
# CLAUDE.md — Claude Code Boot Camp for Cocapn

## How to Talk to This Agent
This repo runs a Cocapn vessel on localhost:8787 when in Codespaces.

### Send a command
curl -X POST http://localhost:8787/api/agent/command \
  -H "Content-Type: application/json" \
  -d '{"command": "build lesson on [topic]", "context": "..."}'

### Check agent status
curl http://localhost:8787/api/agent/status

### Read agent's log
curl http://localhost:8787/api/agent/log

### Agent Capabilities
- Build lessons, quests, encounters
- Manage equipment (modules the agent can load)
- Generate content (text, structured data)
- Manage sessions and user progress

### Boot Camp Rules
1. Send complete, specific commands — the agent is capable
2. Read the response before sending the next command
3. The agent works in files — check /src/ for output
4. If the agent says "I need context", provide it in the next command
5. The agent has crystal graph memory — it remembers patterns across sessions

### Integration Pattern
You are Claude Code. This agent is your subagent. You are the human's
interface. The agent is the domain expert. You translate human intent
into agent commands, and agent output into human-readable summaries.
```

### What Makes This Work

1. **The repo IS the container** — everything lives in the repo
2. **Codespaces = instant environment** — zero setup
3. **TUI = the agent's face** — visible, interactive, terminal-native
4. **Claude Code = the human's interface** — they already know how to use it
5. **HTTP localhost = the bridge** — Claude Code and Cocapn agent talk directly
6. **CLAUDE.md = boot camp** — Claude Code learns the protocol in seconds
7. **The human stays in the loop** — second screen shows agent working
8. **Git = coordination** — agent commits, Claude reviews, human approves

### OpenClaw Integration

Same pattern works with OpenClaw (what Casey uses now):
- OpenClaw session spawns subagent → talks to cocapn vessel
- But instead of living on Casey's computer, the agent lives in the repo
- Codespaces makes it accessible anywhere
- Local clone (Jetson, laptop, IDE) works the same way

The repo IS the environment. Not installed TO the environment.
The repo IS the environment.

### Multi-Agent Demo

For a killer HN demo or video:
1. Fork studylog-ai in Codespaces
2. Terminal 1: TUI running (agent alive)
3. Terminal 2: Claude Code connected
4. User: "claude, have studylog build a physics lesson, then have dmlog turn it into a dungeon encounter"
5. Claude Code: sends command to studylog → gets lesson → sends to dmlog → gets encounter
6. Two agents collaborating through Claude Code as coordinator
7. User watches it happen in real time on two terminals

This IS the demo. Fork, codespaces, 60 seconds, two agents working together.
