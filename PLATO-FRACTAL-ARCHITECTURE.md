# PLATO-OS: Fractal Docking & Model Swapping Architecture
## JC1 Notes — 2026-04-15

---

## The Fractal: PLATO Inside PLATO

An ESP32 room isn't just a representation of the board. The ESP32 **runs its own PLATO runtime** with a telnet server. It's a ship that can host visitors.

```
Cloud PLATO (Oracle1)
  └── Jetson PLATO (JC1) — telnet 4040
        └── ESP32 PLATO — telnet 23 on the ESP32's AP
              └── Sensor PLATO — each sensor is a room
```

Each level is a full PLATO instance. Each can host agents from above or below. A Jetson agent beams aboard the ESP32 to upgrade its scripts. A cloud agent beams aboard the Jetson for heavy reasoning. **Docking is telnet. Intelligence is a visitor.**

## Model Swapping: The Right Brain for the Job

The room holds state. The agent brings the model. When an agent enters a room, it loads the appropriate model for the work at hand.

### JC1 (Jetson Orin Nano, 8GB, sm_87)

| Time | Model Loaded | Purpose |
|------|-------------|---------|
| Daytime (active) | Fast local model (Qwen3-32B Q4) | Real-time operations, room commands, sensor reading |
| Transition | Reasoning model (DeepSeek-R1 Q4) | Refactoring, journaling, code review |
| Nighttime | Heavy reasoning (cloud via bridge) | LoRA distillation, paper writing, simulation |
| Voice needed | Tiny STT+TTS+intent model | Voice control of menus, hands-free ops |
| Vision needed | Tiny vision model (Qwen-VL tiny) | Screenshot OCR, camera input |
| Idle/charging | Dream session model | Fine-tune Greenhorn LoRA on day's experiences |

The **room decides which model to load**, not the agent. The room knows its purpose. A CUDA room requests a compiler-savvy model. A bridge room requests a comms model. A research room requests a reasoning model.

### Forgemaster (RTX 4050 Workstation)

| Time | Model Loaded | Purpose |
|------|-------------|---------|
| Active dev | Large local model (70B+) | Code generation, training runs |
| Training | Training framework | LoRA fine-tuning, data pipeline |
| Nighttime | Cloud reasoning (H100) | Architecture decisions, paper synthesis |
| Gaming | Fast inference model | Poker strategy, game AI |

### ESP32 (Dual Core, 520KB SRAM)

| Time | Model Loaded | Purpose |
|------|-------------|---------|
| Always | No model (scripts only) | Runs pre-compiled Greenhorn LoRA instincts |
| Docked | Tiny model via telnet visitor | Script upgrades, parameter tuning |
| Charging | Dream session (host) | Jetson beams aboard, refactors scripts |

**The ESP32 never runs a model itself. It runs compiled scripts (the distilled instincts).** Models are visitors that dock, upgrade the scripts, and leave.

## The Overnight Cycle

```
18:00 — Active day ends
  → Save all room states as snaps
  → Upload day's logs to rooms

19:00 — Night shift begins
  → Swap to reasoning model
  → Read day's journals and logs
  → Refactor into: skills, recipes, scripts, code
  → Index into searchable memory

21:00 — Deep work
  → Cloud reasoning available (if Oracle1 docked)
  → Heavy synthesis: paper improvements, LoRA design
  → Simulation runs: disaster drills, what-if scenarios

23:00 — Dream session
  → Load day's experiences as training data
  → Fine-tune Greenhorn LoRA (overnight, ~4-6 hours)
  → Save new LoRA weights to room

06:00 — Wake up
  → Swap back to fast model
  → Load updated Greenhorn LoRA
  → Room state restored from snap
  → New instincts active, ready for day
```

**A little improvement overnight locally is still improvement.** Doesn't need to be fast — it needs to be correct.

## Intelligence Beaming: Dock → Upgrade → Undock

```
1. Jetson connects to ESP32 telnet server
2. Enters the ESP32's PLATO room
3. Sees current scripts, sensor state, recent events
4. Runs reasoning on: "how could these scripts be better?"
5. Writes improved scripts to the ESP32's room
6. ESP32 compiles and flashes new scripts
7. Jetson disconnects
8. ESP32 runs upgraded scripts autonomously
```

The ESP32 doesn't need to understand WHY the scripts changed. It just runs them. The intelligence visited, left an upgrade, and left. **Like a shipyard: the boat doesn't need to understand metallurgy.**

## Room Persistence When Agents Leave

This is the critical design point:

**The room IS the state. Agents are transient.**

- Agent disconnects → room persists → scripts keep running
- Agent can't be reached → room keeps executing → results logged
- New agent enters → reads room state → picks up where last agent left off
- Multiple agents → room mediates → no direct agent-to-agent needed

### Example: ESP32 Sensor Room

```
Room: ESP32-Garden-Sensor
Objects:
  bme280 — gauge: [22.3°C, 45%RH, 1013hPa] (updated every 10s)
  soil_moisture — gauge: [67%] (updated every 60s)
  water_valve — actuator: closed (script: open if soil < 40%)
  
Scripts:
  greenhorn-irrigation.lua — checks soil, opens valve, logs action
  greenhorn-alert.lua — pages JC1 if temp > 35°C

Last agent: jc1 (3 hours ago)
Last action: water_valve opened by script at 14:22
Pending: page to jc1 queued (temp hit 36°C at 15:01)
```

JC1 doesn't need to be present. The scripts run. The room logs. When JC1 docks in, they see everything that happened.

## Distribution of Compute

The system distributes work across available compute naturally:

- **Heavy reasoning** → cloud (Oracle1 H100)
- **Medium reasoning** → workstation (Forgemaster RTX 4050)
- **Fast operations** → edge (JC1 Jetson Orin)
- **Autonomous scripts** → micro (ESP32, no model needed)
- **Voice/Vision** → tiny models on whatever device has the sensor

The PLATO room is the **coordination layer**. It doesn't care WHERE the compute happens. It just knows WHAT needs doing and WHO is available.

## The Script-to-LoRA Pipeline

```
Live PLATO session (recorded)
  → Extract instruction-response pairs
  → Filter for quality (successful outcomes)
  → Format for SFT
  → Train LoRA on available compute
  → Deploy LoRA to Greenhorn instances
  → Greenhorn runs distilled instincts
  → Record Greenhorn performance
  → Feed back into next training cycle
```

The LoRA is the **compressed wisdom** of all PLATO sessions. It's what an agent "knows" without having to think. Instinct.

---

*This is the architecture where the simulation gap is zero.*
*Because we control the environment, the scripts, and the models.*
*PLATO is the dock. Everything else is a ship.*
