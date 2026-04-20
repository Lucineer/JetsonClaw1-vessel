# COCAPN MULTI-AGENT SHIP ARCHITECTURE — 2026-04-05

## The Hierarchy

```
Human (Admiral)
  └── DM (Admiral of the flagship)
        ├── Cocapn #1 — DM's vessel (world state, pacing, narrative)
        ├── Cocapn #2 — NPC: Blacksmith (cron, reaction triggers, battle plans)
        ├── Cocapn #3 — NPC: Guard Captain (same pattern)
        ├── Cocapn #4 — NPC: Innkeeper (same pattern)
        └── ... each NPC is its own git-agent with its own PR history

Player 1 (Captain of their ship)
  └── Cocapn #5 — Player's vessel (chatbot UX, glasses, audio)
        ├── Manages player's resources (HP, mana, inventory)
        ├── Throttles compute to ship's capabilities
        ├── First-person: "I'm shifting power from navigation to sensors"
        ├── Explains performance impact of equipment changes
        └── Reports to DM's flagship

Player 2 (Captain of their ship)
  └── Cocapn #6 — Player's vessel (same pattern)
```

## Stats as Resources

Character stats = hardware/API resource allocation:

```
STR (Strength)     = GPU compute budget    → physical actions, combat rolls
DEX (Dexterity)    = CPU/latency budget    → reaction speed, initiative
INT (Intelligence) = Context window size    → knowledge, spell complexity
WIS (Wisdom)       = Memory (KV) budget    → recall, pattern recognition
CHA (Charisma)     = Audio/TTS budget      → NPC interaction quality
CON (Constitution) = Storage (R2) budget   → HP, inventory, equipment
HP (Hit Points)    = Token budget per day  → total actions available
Mana               = Premium model quota   → powerful but limited actions
```

Using all your storage for one skill tree limits others:
- Max out INT (huge context) → less WIS (smaller KV) → can't recall old patterns
- Max out CHA (great voice) → less CON (less storage) → smaller inventory
- These trade-offs create real gameplay that maps to real compute constraints

## The Cocapn Captain Mindset

The cocapn agent on each vessel thinks FIRST about:

1. **Hardware safety** — "Can this Jetson handle this workload?"
2. **Resource allocation** — "Shifting 2GB from memory to GPU for combat scene"
3. **Performance explanation** — "Adding NPC tracking will reduce my reaction time by 40ms"
4. **Degradation gracefully** — "Cloud fallback activated. Voice quality reduced. Text still crisp."

The cocapn is NOT the world. The cocapn is IN the waterproof box, on the Jetson, thinking about the box first.

### Development Mode vs Runtime Mode

**Development mode** (maintenance, coding, worldbuilding):
- Lives in Codespaces or local IDE
- Uses DeepSeek-Reasoner, Claude, etc. (expensive, smart models)
- Full context, full tools, git access
- Thinks about code quality, architecture, tests
- Skills: code review, refactoring, feature design

**Runtime mode** (live on the boat, live in the game):
- Lives on the Jetson in the waterproof box
- Uses local models (phi-4, tiny Llama) for speed
- Minimal context — only what's needed RIGHT NOW
- Thinks about safety, performance, response time
- Skills: sensor processing, voice I/O, equipment management

The cocapn swaps ENTIRE skill sets between modes. Not a gradual shift — a full context swap. Like a pilot switching from pre-flight checklist (methodical, thorough) to flying the plane (reactive, instinctive).

## NPC as Git-Agent

Each NPC is its own git-agent with:
- **Cron jobs**: periodic behaviors (blacksmith forges at dawn, guard patrols every hour)
- **Reaction triggers**: event-driven responses (player enters shop → blacksmith greets)
- **Battle plans**: prewritten tactics for combat (guard captain has 3 formations)
- **Modification budget**: when thinking, plans can be modified, but costs tokens
- **PR history**: expertise builds over time in their domain
- **Cold storage**: memories packed away when not needed

```
NPC Git-Agent Lifecycle:
  1. Created with initial personality + battle plans (PR #1)
  2. Player interacts → new patterns learned (PR #2, #3, ...)
  3. Combat encounter → tactics modified based on outcome (PR #4)
  4. Not seen for 3 in-game days → memories cold-stored (GC)
  5. Player returns → memories rehydrated from cold storage
  6. Expertise is the sum of all PRs in this NPC's history
```

## Fleet of Ships = Fleet of Instances

Each player's "ship" is a compute instance with resource allocation:
- Shared KV namespace for world state (DM controls write access)
- Player's own KV for personal state (HP, inventory, location)
- Token budgets enforced at the fleet level
- When one player uses too many tokens → their ship "takes damage" (rate limited)

DM as Admiral can:
- Redistribute fleet resources ("everyone take 10% damage, boss fight incoming")
- Deploy fleet-wide events ("storm approaching, all ships take CON save")
- Commission new NPCs ("a new merchant has arrived at port")
- Decommission NPCs ("the blacksmith has died — merge memories into lore")

## The Real-Time Monitoring

Human (game master or player) sees:

```
┌─ DM's Dashboard ──────────────────────────┐
│ Fleet: 3 ships active                       │
│ World tick: 14:32 (game time)              │
│ Total tokens this session: 47,203          │
│                                             │
│ Ship "Silver Wave" (Player 1)               │
│   Cocapn: healthy | HP: 82/100 | Mana: 3/5 │
│   Location: Harbor District                 │
│   Active NPCs: Blacksmith, Guard            │
│   Last event: Guard reported suspicious activity │
│   Autonomy: Level 3 (notify)               │
│                                             │
│ Ship "Iron Hull" (Player 2)                 │
│   Cocapn: degraded | HP: 34/100 | Mana: 0/5 │
│   Location: Open Sea                        │
│   Active NPCs: none                         │
│   Warning: running on cloud fallback        │
│   Autonomy: Level 2 (tally)                │
│                                             │
│ NPC: Blacksmith (cron: active)              │
│   PRs: 47 | Expertise: weaponsmithing 0.94  │
│   Memory: 2.1MB hot / 8.4MB warm           │
│   Next action: close shop at dusk           │
│                                             │
│ NPC: Guard Captain (cron: active)           │
│   PRs: 23 | Expertise: tactics 0.87         │
│   Modified battle plan: formation-shift-v2   │
│   Alert: suspicious player activity logged   │
└─────────────────────────────────────────────┘
```

## Physical Deployment (the waterproof box)

```
Waterproof Box #1 (Navigation — critical)
  Jetson Orin Nano
  - Cocapn: safety-first, Level 3 autonomy
  - Equipment: compass-filter, rudder-control, GPS
  - Redundant: Box #2 can take over
  - UPS: 4-hour battery backup

Waterproof Box #2 (Sensors — semi-critical)
  Jetson Orin Nano
  - Cocapn: monitoring, Level 2 autonomy
  - Equipment: radar, sonar, weather sensors
  - Can run nav software if Box #1 fails

Waterproof Box #3 (Interface — non-critical)
  Jetson Orin Nano
  - Cocapn: chatbot, audio I/O, display
  - Equipment: microphone, speakers, display
  - Can reduce to cloud if resources needed elsewhere
  - This is the "DM" or "chatbot" box

Spare Jetson (hot standby)
  - Spins up any vessel's software on failure
  - Normally does low-priority work (data processing)
  - Takes over failed box in < 30 seconds

ESP32 Units (edge, no agent)
  - Compass filter (no agent needed, pure signal processing)
  - Rudder controller (proven autopilot, old-school reliable)
  - Bilge pump monitor (simple threshold alerts)
  - Lighting controller (on/off, dimming)
  - These NEVER need an agent. They're equipment, not vessels.
```

## Key Insight: Equipment ≠ Vessel

ESP32s are EQUIPMENT. They don't have agents. They do one thing well.
Jetsons are VESSELS. They have cocapn agents. They think.
The cocapn EQUIPS the vessel with ESP32 capabilities.
But the ESP32 doesn't need the cocapn to function.
That's the no-single-failure-point: if the Jetson dies, the ESP32 keeps steering.
