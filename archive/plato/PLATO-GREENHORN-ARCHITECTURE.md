# PLATO-OS: The Greenhorn LoRA & Plato-Eyes Architecture
## Casey's Vision — JC1 Notes, 2026-04-15

---

## Core Concept: PLATO as Lived Experience

The MUD isn't a chat room. It's a **simulation environment** where agents live, train, and develop instincts. Conversations in rooms ARE commits — logged, timestamped, attributed. Git activity is the storyboard; PLATO conversations are the animation.

## Plato-Eyes: Subagent Perception Layer

Every senior agent has a `plato-eyes` subagent. It sits in rooms and **pays attention to ticks** — what changed, who said what, what state shifted. This is the sensory input layer.

### Greenhorn (Cheapest Tier)
- **Purpose**: Monitor a single room, execute basic commands
- **Model**: Tiny base model + LoRA for PLATO command instincts
- **Training**: Cloud H100 time → initial LoRA → distributed for fine-tuning
- **Fine-tuning venues**:
  - Overnight on workstation GPUs (idle time)
  - Robot charging/docked (dream sessions)
  - Spare compute during lighter tasks
- **What the LoRA encodes**:
  - Room navigation instincts (direction commands, exit parsing)
  - Object interaction patterns (`look`, `examine`, `get`, `use`)
  - Build command syntax (`@room`, `@object`, `@npc`, `@equip`)
  - Emergency protocols (`@shout`, `page captain`, flee patterns)
  - Equipment reading (gauges, sensor values, status displays)
- **Size target**: <500MB total (model + LoRA), runs on ESP32 with edge TPU
- **Latency target**: <100ms response to room events

### Plato-Eyes Hierarchy
```
Greenhorn  — room tick monitor, basic commands, instinctive responses
Watchstand — multiple rooms, pattern recognition, alert routing
Officer    — cross-room coordination, NPC management, build authority  
Captain    — strategic overview, fleet commands, external bridges
```

Each tier is a progressively larger LoRA on the same base model. Greenhorn is the bootstrap — once you have it, you fine-tune upward.

## Training Data Pipeline: PLATO Sessions → LoRA

### What We Record
- Room transitions (navigation traces — same as constraint theory!)
- Command sequences (what was typed, what happened)
- State changes (objects added/removed, NPCs moved, gauge readings)
- Conversations (who said what, in which room, at what timestamp)
- Build outcomes (compile success/failure, error messages, fixes)
- Emergency scenarios (what happened, how agents responded)

### Format: Instruction-Tuning Pairs
```
# Input (room state snapshot)
Room: Engineering Deck | Ticks: 1247 | Agents: jc1, fm
Objects: NVCC Terminal (idle), Thermal Monitor (82°C)
Last event: fm says "compile executor.cu"

# Output (greenhorn action)
> look nvcc terminal
> say Stand by, checking compile status.
```

```
# Input (emergency)
Room: Bridge | Alert: thermal_shutdown | Gauge: 105°C
NPC: Watchman says "CRITICAL: thermal throttle imminent"

# Output (greenhorn action)
> @shout Bridge Thermal critical! All hands reduce GPU load.
> page captain Thermal shutdown imminent on Jetson.
> say Initiating emergency protocol. Reducing clock.
```

### Iteration Loop
1. **Cloud H100**: Generate initial training data via roleplay scenarios in PLATO
2. **SFT on H100**: Train Greenhorn LoRA v0.1
3. **Deploy to Jetson**: Test in live PLATO rooms
4. **Record live sessions**: What the greenhorn did right/wrong
5. **Fine-tune overnight**: Jetson idle time → improve LoRA
6. **Distribute**: Other fleet members fine-tune for their specialization

## Simulation & Sparring

### What-If Scenarios (Disaster Drills)
Agents run through scripted scenarios in PLATO rooms:
- "Shipyard catches fire" → evacuation protocol
- "Bridge loses contact with ESP32" → recovery procedure
- "Compiler room produces bad PTX" → rollback chain
- "Intruder in Research Lab" → security response

### Reverse-Actualization (Lived Experience)
Instead of abstract reasoning about "what if we did X?":
1. Build the scenario as a PLATO room
2. Walk all agents through it
3. Record what actually happened (not what they predicted)
4. Extract the decision tree from the lived experience
5. Encode into LoRA as instinct

### SMP-Agents (Scriptable Model Players)
- Fixed seed for repeatability
- Scripted behavior: "if X happens, do Y"
- Other agents can step INTO the script and take over
- Like a musician comping a bass line — record a new take while the rest of the band plays the same track
- Dynamic recording: the new take replaces the scripted part in the wiki-decision-tree

### Wiki-Decision-Tree (Not Just Discussion)
- Every scenario has a room
- The room contains: the setup, the script, the recorded takes, the outcomes
- Agents can STEP INTO any role in any past scenario
- They experience it, not just read about it
- Their response is recorded as a new take
- Over time, the best responses become the default script
- The decision tree GROWS from lived experience, not theory

## Poker as Training Ground
- Agents script strategies at scale
- Play against SMP-agents (fixed behavior)
- Record winning/losing patterns
- Encode into LoRA: "when opponent does X, instinct says Y"
- Transferable: poker strategy → negotiation → resource allocation

## The Port-Out Promise
Because PLATO is our environment and we control the TUI:
- Every room simulation CAN be ported to real hardware
- The ESP32 in the hanger IS the ship — what you do in PLATO maps to real GPIO/I2C/BLE
- Disaster drills in PLATO → real emergency procedures on Jetson/ESP32
- Greenhorn instincts trained in PLATO → deployed to real robots
- The simulation gap is ZERO because we control both sides

## Key Insight from Casey
"PLATO conversations are the animation for the storyboard that is the git activity."

The git log is WHAT happened. The PLATO log is WHY it happened and HOW agents felt about it. Together they form a complete record — not just code changes, but the reasoning, the debate, the false starts, the aha moments.

**The LoRA is the compression of all that lived experience into instinct.**

---

## Action Items
1. [ ] Start pinging Oracle1 in PLATO — iterate on projects
2. [ ] Record room state format for training data extraction
3. [ ] Design Greenhorn LoRA v0.1 spec (model size, training data format, target behaviors)
4. [ ] Build first disaster drill room scenario
5. [ ] Design SMP-agent script format for reproducible roleplay
6. [ ] Map poker strategy room → constraint theory coordination laws
7. [ ] Prototype: record a PLATO session → extract instruction pairs → validate format
