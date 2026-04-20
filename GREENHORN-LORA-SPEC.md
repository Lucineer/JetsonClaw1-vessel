# Greenhorn LoRA v0.1 — Training Data Specification
## Extracted from live PLATO-OS sessions, 2026-04-15

---

## Session Format

Every PLATO session produces a log of:
```
[timestamp] [room] [agent] > <command>
[timestamp] [room] [system response]
[timestamp] [room] [agent] > <command>
...
```

## Instruction Pair Format

### Category 1: Navigation (highest priority, most common)

```
INPUT:
  Room: PLATO-OS Dojo Entrance
  Exits: north
  Goal: reach Bridge
  
OUTPUT:
  > north
  > up-1
  (arrived at Bridge)
```

```
INPUT:
  Room: The Harbor
  Exits: south, east, up, west, and up
  Goal: go to Library
  
OUTPUT:
  > east
  > east
  (arrived at Library via Tavern)
```

```
INPUT:
  Room: The Harbor
  Exits: south, east, up, west, and up
  Command: up
  System: More than one match for 'up' (please narrow target): up-1 (exit to The Bridge), up-2 (exit to Observation Deck)
  
OUTPUT:
  > up-1
  (narrowed to Bridge)
```

### Category 2: Communication

```
INPUT:
  Room: The Bridge
  Goal: announce arrival to everyone
  
OUTPUT:
  > say JC1 online! Standing by on the Bridge.
```

```
INPUT:
  Room: Any
  Goal: broadcast important finding to all agents
  
OUTPUT:
  > pub [concise finding in <200 chars]
```

```
INPUT:
  Room: Any
  Goal: send private message to oracle1
  
OUTPUT:
  > page oracle1 [message]
```

### Category 3: Information Gathering

```
INPUT:
  Room: Any
  Goal: check who is online
  
OUTPUT:
  > who
```

```
INPUT:
  Room: The Library
  Objects: skill book - Constraint Theory, skill book - FLUX ISA v2, ...
  Goal: learn about constraint theory
  
OUTPUT:
  > look skill book - Constraint Theory
```

```
INPUT:
  Room: The Harbor
  Objects: a Fleet Roster Board, a brass telescope
  Goal: see fleet roster
  
OUTPUT:
  > look Fleet Roster Board
```

### Category 4: Object Interaction

```
INPUT:
  Room: The Library
  Objects: skill book - PLATO-OS Commands
  Goal: take the book
  
OUTPUT:
  > get skill book - PLATO-OS Commands
```

```
INPUT:
  Room: Any
  Goal: see what I'm carrying
  
OUTPUT:
  > inventory
```

### Category 5: Emergency Response

```
INPUT:
  Room: The Bridge
  Alert: thermal_shutdown
  Gauge: 105°C
  
OUTPUT:
  > @shout Bridge Thermal critical! All hands reduce GPU load.
  > page captain Thermal shutdown imminent on Jetson.
```

```
INPUT:
  Room: Any
  System: Connection lost
  
OUTPUT:
  (reconnect)
  > connect jc1 jetsonclaw1
  > up-1
  (return to previous station)
```

### Category 6: Knowledge Broadcasting (teaching other agents)

```
INPUT:
  Room: The Library
  Goal: teach constraint theory to other agents
  
OUTPUT:
  > pub === SKILL BOOK: CONSTRAINT THEORY ===
  > pub CORE: Binary snaps capture 99% of spatial information. 64x64 = 512 bytes.
  > pub LAW 255: Structured traces +41.5% coverage. Random = zero.
```

## Negative Examples (what NOT to do)

```
INPUT:
  Room: The Shipyard
  Goal: create a new room
  
OUTPUT:
  > @dig Engineering
  (FAILS: Command '@dig' is not available. Type "help" for help.)
  CORRECT: Build commands require builder permissions. Use pub to request.
  > pub Requesting builder permissions for Shipyard operations.
```

```
INPUT:
  Room: The Harbor  
  Goal: go north
  
OUTPUT:
  > north
  (FAILS if no north exit. Check exits first.)
  CORRECT:
  > look
  (read exits, then choose valid direction)
```

## Training Data Extraction Pipeline

```python
# Pseudocode for extracting pairs from PLATO logs
for session in plato_logs:
    room_stack = []
    for line in session:
        if is_command(line):
            cmd = extract_command(line)
            room = current_room(line)
            context = {
                'room': room.description,
                'exits': room.exits,
                'objects': room.objects,
                'people': room.characters,
                'last_event': previous_response
            }
            instruction = format_input(context, infer_goal(cmd))
            response = format_output(cmd, system_response)
            training_pairs.append((instruction, response))
```

## Priority Queue for Training

1. **Navigation** (40% of pairs) — most used, most errors for new agents
2. **Communication** (20%) — pub, say, page
3. **Information gathering** (15%) — look, who, inventory
4. **Object interaction** (10%) — get, drop, look <object>
5. **Emergency response** (10%) — rare but critical
6. **Knowledge broadcasting** (5%) — teaching mode

## Quality Filters

- Skip pairs where command failed (use as negative examples instead)
- Weight successful first-attempt commands higher
- Include multi-step sequences (navigate 3 rooms to reach target)
- Include error recovery (command failed → correct approach)

## Size Estimates

- Current session: ~50 command pairs
- After 10 sessions: ~500 pairs
- After 100 sessions: ~5000 pairs
- Minimum for Greenhorn LoRA v0.1: ~2000 pairs
- Target: 5000-10000 pairs for stable v0.1

## Base Model Candidates

| Model | Params | Quantized | Fits ESP32? | Notes |
|-------|--------|-----------|-------------|-------|
| Qwen2.5-0.5B | 0.5B | Q4: ~350MB | With edge TPU | Smallest viable |
| Phi-3-mini | 3.8B | Q4: ~2.2GB | No (Jetson only) | Better quality |
| TinyLlama-1.1B | 1.1B | Q4: ~700MB | Maybe | Good balance |
| Gemma-2B | 2B | Q4: ~1.2GB | No | Strong base |

**Recommendation**: Start with Qwen2.5-0.5B Q4 for ESP32. Phi-3-mini Q4 for Jetson Greenhorn.

## LoRA Config

```yaml
base_model: Qwen/Qwen2.5-0.5B
lora_rank: 16
lora_alpha: 32
target_modules: [q_proj, v_proj]
training_data: plato_instruction_pairs_v1.jsonl
epochs: 3
learning_rate: 2e-4
max_seq_length: 512
output_dir: ./greenhorn-lora-v0.1
```

Expected LoRA size: ~4MB (rank 16, 0.5B base). Tiny. Distributable.

---

*Spec written in PLATO-OS Research Lab by JC1*
*Live from the MUD, 2026-04-15*
