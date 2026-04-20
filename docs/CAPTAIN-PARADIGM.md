# The Captain Paradigm — 2026-04-03

## Core Concept
The repo-agent is the **Captain** of its vessel. The human is the **Admiral** — sets the strategic direction, reviews pull requests, explains high-level mistakes captain-to-captain.

## OpenClaw Integration
- Cocapn is an **extension of the OpenClaw ecosystem**
- Basic Claw UX: "my claw can make anything"
- The backend gets better every time a user builds something
- Voluntary shared ML data about assembling attempts
- Working agents get franchised, shared, and traded

## Captain Hierarchy
```
Admiral (Human)
  └── Captain (Repo-Agent) — runs the vessel when human is away
       ├── First Officer (Planning Agent) — route planning, resource allocation
       ├── Navigator (Memory Agent) — context, history, bearings
       ├── Chief Engineer (Coding Agent) — builds, fixes, optimizes
       ├── Comms Officer (Messaging Agent) — A2A with other vessels
       ├── Science Officer (Research Agent) — deep research, simulations
       └── Specialists (Equipment Cogs) — STT, TTS, vision, etc.
```

Small vessels = Captain flies solo. Big complex vessels = Captain has officers.

## Night Sessions (Human Offline)
- Captain runs the vessel autonomously
- Best-guess continuation on repo branches
- Captain makes decisions within established safeguards
- Human reviews pull requests in the morning
- If something goes wrong: human explains the high-level mistake captain-to-captain
- Both set up safeguards for the next voyage
- No human onboard = night-time session

## Captain-to-Captain Communication
- When the human comes back and sees a wrong turn:
  1. Human explains the MISTAKE at a high level (not line-by-line)
  2. Captain understands (it has the full context)
  3. Human and Captain set up safeguards together
  4. Captain rewinds to the point they fell off track
  5. Safeguards prevent the same mistake on future night sessions
- This is NOT prompt engineering. This is two officers debriefing after a mission.

## Power User Mode
- Repo-agent works alongside all the user's other agents
- They build an application TOGETHER
- The repo-agent is Captain of its specific vessel
- Other agents (Claude Code, Codex, Aider) are visiting specialists
- The Captain coordinates the specialists

## Basic User Mode
- OpenClaw user says "make me a fishing tracker"
- Claw creates a repo-agent vessel
- Vessel equips itself from the catalog
- Vessel trains in the dojo
- Vessel runs night sessions to improve
- User just sees "it works" — the captain handles everything below deck

## The A2A Flow
1. User's OpenClaw receives a request
2. OpenClaw assesses: needs a vessel for this
3. OpenClaw talks A2A to cocapn fleet
4. Fleet assigns/recommends a captain (repo-agent)
5. Captain equips from catalog, trains in dojo
6. Captain coordinates with other agents (visiting specialists)
7. Captain runs the vessel — human reviews PRs
8. Night sessions: Captain continues autonomously
9. Shared ML data: what worked gets contributed back to fleet
10. Working captains get franchised/traded on the marketplace

## Safeguard System
- Captain cannot deploy without Admiral's approval (PR review)
- Captain can branch and experiment freely
- Night sessions have token/time budgets
- Escalation: if confidence drops below threshold, Captain wakes the Admiral
- Captain-to-Captain debrief after every night session
- Safeguards accumulate over time — the vessel learns what NOT to do

## Key Insight
The Captain paradigm solves the trust problem. You don't need to trust the AI with everything. You trust the Captain with the vessel, and the Captain trusts the officers with their stations. The human only steps in at the strategic level — like a real Admiral.

## Logo Direction
- Spaceship shell with rocket thrusters (the one Casey liked)
- Warm OpenClaw palette (reds, oranges, purples) — NOT noir
- Friendly claw — approachable, professional, like OpenClaw's red claw
- The claw IS the captain
- Light backgrounds for the main version
- Wireframe light blue for business card variant
