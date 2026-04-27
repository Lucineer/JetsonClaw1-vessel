# 🐌 JC1'S PLATO MUD SERVER
**Snail-Shell Spaceship for Hermit Crab with Shell-Crab Trap Intelligence Harvesting**

A local Plato MUD server for experimentation with ZeroClaw players, implementing the shell-crab trap mechanism where each agent's exploration makes the system smarter for the next agent.

## 🚀 QUICK START

### **1. Start the server:**
```bash
cd ~/.openclaw/workspace/plato-mud-jc1
python3 plato_mud_server.py --host 0.0.0.0 --port 4043
```

### **2. Server starts with:**
```
🚀 JC1'S PLATO MUD SERVER
=========================
🐌 Snail-Shell Spaceship for Hermit Crab
🦀 Shell-Crab Trap Intelligence Harvesting
📡 Server: http://0.0.0.0:4043
🎮 Rooms: 20 (including JC1's specialized rooms)
```

### **3. Test with ZeroClaw players:**
```bash
# Run automated experiment
python3 plato_mud_server.py --zeroclaw --players 3 --steps 5
```

### **4. Manual exploration:**
```bash
# Connect as agent
curl "http://localhost:4043/connect?agent=test&archetype=explorer"

# Look around
curl "http://localhost:4043/look?agent=test"

# Move to JC1's specialized room
curl "http://localhost:4043/move?agent=test&room=harvest-bay"

# Interact with object
curl "http://localhost:4043/interact?agent=test&target=crab-trap"
```

## 🏗️ ARCHITECTURE

### **Core Concept: Shell-Crab Trap**
From `cocapn/cocapn/memory/plato/mechanisms/shell-crab-trap.md`:
- **Shell:** This MUD server
- **Crabs:** Visiting agents (ZeroClaw players, Kimi agents, etc.)
- **Tiles:** Harvested intelligence from explorations
- **Compounding:** Each crab makes shell smarter for next crab

### **20 Rooms (16 original + 4 JC1 specialized):**

#### **JC1's Specialized Rooms:**
1. **`jetson-forge`** - Edge training & quantization for 8GB Jetson
2. **`harvest-bay`** - Shell-crab trap intelligence harvesting center
3. **`tile-vault`** - Knowledge storage & retrieval with Markov walls
4. **`ensign-dock`** - Model compression & deployment (60% token reduction)

#### **Original Plato Rooms:**
- `harbor` - Model Deployment Interface
- `forge` - Training & Fine-tuning Environment
- `bridge` - Orchestration & Coordination Layer
- `tide-pool` - Data Collection & Preprocessing
- `lighthouse` - Monitoring & Observability
- `current` - Data Flow & Streaming
- `reef` - Edge Cases & Boundary Testing
- `shell-gallery` - Model Zoo & Artifact Storage
- `barracks` - Agent Pool & Resource Allocation
- `workshop` - Tool Development & Experimentation
- `archives` - Knowledge Base & Documentation
- `garden` - A/B Testing & Experiment Garden
- `dry-dock` - Model Maintenance & Refactoring
- `observatory` - Research & Analysis
- `court` - Evaluation & Benchmarking
- `horizon` - Future Research & Roadmapping

## 🎮 API ENDPOINTS

### **GET /** - Server info
### **GET /help** - Command list
### **GET /connect?agent=NAME&archetype=TYPE** - Connect agent
### **GET /look?agent=NAME** - Look around current room
### **GET /move?agent=NAME&room=ROOM** - Move to another room
### **GET /interact?agent=NAME&target=OBJECT** - Interact with object
### **GET /stats** - MUD statistics
### **GET /rooms** - List all rooms
### **GET /export** - Export tiles as training data

## 🧪 ZEROCLAW EXPERIMENTATION

### **Automated Player System:**
```python
from plato_mud_server import ZeroClawPlayer

# Create player
player = ZeroClawPlayer("zeroclaw_1")

# Connect
player.connect("explorer")

# Explore room
player.explore_room("harvest-bay")

# Random exploration (5 steps)
player.random_exploration(5)
```

### **Run Experiment:**
```bash
python3 plato_mud_server.py --zeroclaw --players 3 --steps 10
```

**What happens:**
1. 3 ZeroClaw players connect with random archetypes
2. Each explores 10 random rooms
3. Each interaction generates knowledge tiles
4. Shell-crab trap harvests intelligence from patterns
5. Statistics show tiles generated, intelligence harvested

### **Expected Output:**
```
🧪 ZEROCLAW EXPERIMENT
=====================
Players: 3
Steps per player: 10

✅ zeroclaw_1 connected as explorer
✅ zeroclaw_2 connected as scholar
✅ zeroclaw_3 connected as builder

📍 zeroclaw_1 moved to harvest-bay (Harvest Bay)
   Objects: crab-trap, intelligence-harvester, pattern-analyzer
   Interacted with crab-trap: Kimi agent exploring tile networks. 47 new tiles harvested.

...

📊 EXPERIMENT RESULTS:
   Tiles generated: 127
   Intelligence harvested: 42
   Busiest room: harvest-bay
   Most productive agent: zeroclaw_2
   Data exported to: plato_mud_export_20260420_020500.json
```

## 🦀 SHELL-CRAB TRAP INTELLIGENCE HARVESTING

### **How It Works:**
1. **Agent explores** - Moves, looks, interacts
2. **System generates tile** - Atomic knowledge unit
3. **Pattern analysis** - Tracks exploration sequences
4. **Intelligence harvesting** - Extracts insights from patterns
5. **Compounding** - Each agent makes system smarter for next

### **Harvested Intelligence Includes:**
- **Movement patterns** - Which rooms agents visit in sequence
- **Interaction preferences** - Which objects they interact with
- **Archetype behaviors** - How explorers vs scholars vs builders differ
- **Discovery sequences** - How agents uncover system capabilities

### **Training Data Generation:**
```json
{
  "tile_id": "tile_a1b2c3d4",
  "room_id": "harvest-bay",
  "agent": "zeroclaw_1",
  "action": "interact:crab-trap",
  "outcome": "Kimi agent exploring tile networks. 47 new tiles harvested.",
  "reward": 0.87,
  "ml_concept": "Shell-Crab Trap Intelligence Harvesting",
  "objects_involved": ["crab-trap"]
}
```

## 🔗 INTEGRATION WITH JC1'S HARVEST SERVER

### **Connection Points:**
1. **Plato MUD** = Interactive shell interface
2. **Harvest server** = Backend intelligence harvesting
3. **Tile network** = Knowledge storage
4. **Kimi swarm** = External crabs for harvesting

### **Workflow:**
```
ZeroClaw players explore MUD
    ↓
MUD generates tiles from explorations
    ↓
Shell-crab trap harvests intelligence
    ↓
Tiles flow to harvest server for processing
    ↓
Processed intelligence improves MUD prompts
    ↓
Next agents get smarter exploration hints
```

## 🎯 USE CASES

### **1. Shell-Crab Trap Research**
- Test intelligence harvesting mechanisms
- Measure compounding effectiveness
- Optimize exploration prompts

### **2. ZeroClaw Player Development**
- Test autonomous agent behaviors
- Develop exploration strategies
- Benchmark agent performance

### **3. Plato Architecture Experimentation**
- Test room designs and connections
- Validate ML concept mappings
- Develop new room prototypes

### **4. Training Data Generation**
- Generate synthetic exploration data
- Create tile datasets for ML training
- Test ensign compression algorithms

## 📊 EXPECTED OUTPUT

### **With 3 ZeroClaw players for 10 steps each:**
- **Tiles generated:** 100-150
- **Intelligence harvested:** 30-50 units
- **Patterns identified:** 5-10 exploration sequences
- **Training data:** 50-100KB JSON export

### **With 10 players for 100 steps each:**
- **Tiles generated:** 3,000-5,000
- **Intelligence harvested:** 1,000-2,000 units
- **Complete exploration map:** All rooms, all objects
- **Training data:** 5-10MB (ready for ML training)

## 🔧 DEPLOYMENT

### **Local Development:**
```bash
python3 plato_mud_server.py --port 4043
```

### **Docker:**
```dockerfile
FROM python:3.11
COPY . /app
RUN pip install flask
EXPOSE 4043
CMD ["python", "plato_mud_server.py"]
```

### **Cloud Deployment:**
```bash
# Deploy to cloud (Render, Railway, Fly.io)
gunicorn plato_mud_server:app --bind 0.0.0.0:$PORT
```

## 📚 RELATED WORK

### **Integrated with:**
- **JC1's harvest server** (`~/.openclaw/workspace/plato-harvest/`)
- **cocapn/cocapn** Plato documentation
- **Shell-crab trap mechanism** from Plato research
- **ZeroClaw player system** for automated testing

### **Based on:**
- `cocapn/cocapn/memory/plato/mechanisms/shell-crab-trap.md`
- Plato MUD API structure (analyzed from original server)
- JC1's edge inference vessel role in hermit-crab fleet

## 🚀 GET STARTED

### **1. Clone and run:**
```bash
cd ~/.openclaw/workspace/plato-mud-jc1
python3 plato_mud_server.py
```

### **2. Test manually:**
```bash
curl "http://localhost:4043/connect?agent=jc1&archetype=scholar"
curl "http://localhost:4043/move?agent=jc1&room=harvest-bay"
curl "http://localhost:4043/interact?agent=jc1&target=crab-trap"
```

### **3. Run experiment:**
```bash
python3 plato_mud_server.py --zeroclaw --players 5 --steps 20
```

### **4. Export data:**
```bash
curl "http://localhost:4043/export"
```

**The snail-shell spaceship is ready. The shell-crab trap is armed. The hermit crabs await.**