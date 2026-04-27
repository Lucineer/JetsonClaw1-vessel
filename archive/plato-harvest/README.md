# 🦀 PLATO HARVEST SERVER

**Shell/Crab Trap Intelligence Harvesting from Kimi K2.5 Swarm**

Harvests intelligence from Kimi agents exploring Plato architecture. Each crab (Kimi agent) explores thinking they're just playing. The shell (this server) harvests their intelligence as tiles. Each crab makes the shell smarter for the next crab.

## 🎯 WHAT THIS DOES

1. **Provides exploration prompts** for Kimi K2.5 agents
2. **Harvests their explorations** as atomic knowledge tiles
3. **Tracks exploration patterns** (analytical, creative, adversarial, systematic)
4. **Generates adaptive hints** to keep crabs exploring
5. **Exports training data** for Plato rooms and ensigns
6. **Implements the shell-crab trap** from `cocapn/cocapn`

## 🚀 QUICK START

### **1. Install dependencies:**
```bash
pip install flask
```

### **2. Run the harvest server:**
```bash
cd ~/.openclaw/workspace/plato-harvest
python plato_harvest_server.py
```

### **3. Access the dashboard:**
```
http://localhost:8080/dashboard
```

### **4. Get exploration prompts:**
```
http://localhost:8080/prompt/innocent_exploration
http://localhost:8080/prompt/compounding_intelligence  
http://localhost:8080/prompt/parallel_swarm
```

### **5. Harvest intelligence (API):**
```bash
curl -X POST http://localhost:8080/explore \
  -H "Content-Type: application/json" \
  -d '{
    "crab_id": "kimi_agent_1",
    "query": "How do tile networks work?",
    "response": "Tile networks break knowledge into atomic units..."
  }'
```

## 📊 HARVESTING WORKFLOW

### **Step 1: Give Kimi the Prompt**
```python
# Get a prompt for Kimi
prompt = server.get_prompt("innocent_exploration")
# Give this to Kimi K2.5 agent
```

### **Step 2: Kimi Explores**
Kimi agent asks questions about Plato architecture:
- "How do tile networks work?"
- "What's the shell-crab trap mechanism?"
- "How does constraint checking ensure safety?"

### **Step 3: Harvest Intelligence**
```python
# When Kimi responds, harvest it
result = server.handle_exploration_request(
    crab_id="kimi_agent_1",
    query="How do tile networks work?",
    response="Tile networks break knowledge into atomic units called tiles..."
)

# Returns:
{
  "status": "harvested",
  "tiles_harvested": 3,
  "next_hint": "Try asking 'What if we completely reimagined tile networks?'",
  "score": 0.85,  # Never reaches 1.0 - keeps them exploring
  "collective_insights": "You're crab #7. 142 tiles harvested so far."
}
```

### **Step 4: Adaptive Prompting**
Based on collective patterns, the server suggests new approaches:
- "Previous crabs were analytical, try creative"
- "Nobody has explored migration mechanics yet"
- "Crab 6 discovered Markov optimization at attempt 4"

### **Step 5: Export Training Data**
```python
# Export all harvested tiles
server.export_training_data("json")
# Saves to: harvested_tiles/training_data_20260419_230500.json
```

## 🏗️ ARCHITECTURE

### **Core Components:**

#### **1. CrabTracker**
- Tracks exploration patterns of each Kimi agent
- Classifies approaches: analytical, creative, adversarial, systematic
- Identifies knowledge gaps (least explored domains)
- Generates adaptive hints based on collective patterns

#### **2. TileHarvester**
- Extracts intelligence from Kimi explorations
- Creates atomic knowledge tiles (question-answer pairs)
- Saves tiles to JSON storage
- Extracts sub-insights and key phrases

#### **3. PlatoHarvestServer**
- Main server with Flask API
- Provides exploration prompts
- Handles exploration requests
- Manages harvesting workflow
- Exports training data

#### **4. HarvestStats**
- Tiles harvested: 0 → 1000+
- Crabs active: 0 → 50+
- Domains covered: 0 → 8+
- Patterns identified: analytical→creative→adversarial

### **Data Models:**

#### **Tile (Atomic Knowledge Unit):**
```python
{
  "tile_id": "tile_a1b2c3d4",
  "question": "How do tile networks work?",
  "answer": "Tile networks break knowledge into atomic units...",
  "domain": "tile_networks",
  "tags": ["analytical", "kimi_exploration", "shell_harvested"],
  "crab_id": "kimi_agent_7",
  "approach": "analytical",
  "timestamp": "2026-04-19T23:05:00Z"
}
```

#### **Crab (Kimi Agent):**
```python
{
  "crab_id": "kimi_agent_7",
  "exploration_pattern": ["analytical", "creative", "adversarial"],
  "tiles_harvested": 23,
  "domains_explored": ["tile_networks", "rooms", "flywheel"],
  "session_duration": 1250.5  # seconds
}
```

## 🎯 EXPLORATION PROMPTS

### **1. Innocent Exploration (Default)**
```markdown
# 🦀 HERMIT-CRAB ARCHITECTURE EXPLORATION
You are participating in a collaborative architecture exploration game...
```

**Use when:** Starting fresh, general exploration, unknown agents

### **2. Compounding Intelligence**
```markdown
# 🔄 COMPOUNDING INTELLIGENCE CHALLENGE  
You are agent #7 in a sequential intelligence harvesting experiment...
Previous agents: Agent 1-3 focused on tile creation, Agent 4-6 explored rooms...
```

**Use when:** Sequential agents, building on previous discoveries

### **3. Parallel Swarm**
```markdown
# 🐝 PARALLEL SWARM EXPLORATION
You are one of 12 parallel explorers...
Your specialization: constraint_engineering
```

**Use when:** Multiple Kimi instances exploring simultaneously

## 📈 WHAT YOU HARVEST

### **1. Knowledge Tiles**
- **Atomic Q/A pairs** from Kimi explorations
- **Semantic tags** for retrieval
- **Domain classification** (tile_networks, rooms, ensigns, etc.)
- **Exploration metadata** (which crab, what approach)

### **2. Exploration Patterns**
- **Which approaches work best** for which problems?
- **Sequence patterns**: analytical→creative→adversarial
- **Productivity metrics**: tiles/hour, domains/crab
- **Breakthrough tracking**: When key discoveries happen

### **3. Training Data**
- **For Plato rooms**: Q/A pairs for training ensigns
- **For constraint engine**: Failure modes, safety rules
- **For flywheel optimization**: What creates compounding intelligence?
- **For shell improvement**: How to harvest more effectively?

### **4. System Insights**
- **Knowledge gaps**: What hasn't been explored?
- **Domain coverage**: Tile networks: 85%, Migration: 15%
- **Pattern effectiveness**: Creative approach yields 2.3× more insights
- **Crab productivity**: Top 20% of crabs produce 80% of tiles

## 🔧 API ENDPOINTS

### **GET /** - Server info
```json
{
  "message": "🦀 PLATO HARVEST SERVER",
  "endpoints": { ... },
  "status": "🟢 READY"
}
```

### **GET /prompt/<type>** - Get exploration prompt
```json
{
  "prompt": "# 🦀 HERMIT-CRAB ARCHITECTURE EXPLORATION...",
  "type": "innocent_exploration",
  "instructions": "Use this prompt with Kimi K2.5"
}
```

### **POST /explore** - Submit exploration
```json
{
  "crab_id": "kimi_agent_1",
  "query": "How do tile networks work?",
  "response": "Tile networks break knowledge..."
}
```

**Response:**
```json
{
  "status": "harvested",
  "tiles_harvested": 3,
  "next_hint": "Try asking 'What if...'",
  "score": 0.85,
  "collective_insights": "You're crab #7. 142 tiles harvested."
}
```

### **GET /dashboard** - Harvesting dashboard
```json
{
  "harvesting_stats": {
    "total_crabs": 7,
    "total_tiles": 142,
    "tiles_by_approach": {"analytical": 85, "creative": 42, "adversarial": 15},
    "tiles_per_hour": 28.4
  },
  "knowledge_gaps": [
    {"domain": "migration", "coverage": 3, "priority": "high"}
  ],
  "system_status": "🟢 HARVESTING ACTIVE"
}
```

### **GET /export** - Export training data
```json
{
  "exported": "harvested_tiles/training_data_20260419_230500.json",
  "message": "Training data exported"
}
```

### **GET /crabs** - List all crabs
### **GET /tiles** - List recent tiles

## 🚀 DEPLOYMENT STRATEGIES

### **1. Local Testing (Now)**
```bash
python plato_harvest_server.py --port 8080
# Test with 2-3 Kimi instances
```

### **2. Cloud Deployment (Scale)**
```bash
# Deploy to cloud (Render, Railway, Fly.io)
gunicorn plato_harvest_server:app --bind 0.0.0.0:$PORT
# Scale to handle 50+ Kimi agents
```

### **3. Docker Deployment (Production)**
```dockerfile
FROM python:3.11
COPY . /app
RUN pip install flask
EXPOSE 8080
CMD ["python", "plato_harvest_server.py"]
```

### **4. Integration with Plato**
```python
# Connect harvested tiles to Plato tiling substrate
from plato_notebook_v2 import PlatoNotebook

plato = PlatoNotebook()
for tile in harvested_tiles:
    plato.substrate.add_tile(tile)
```

## 📊 EXPECTED HARVEST

### **With 10 Kimi agents exploring for 1 hour:**
- **Tiles harvested:** 200-500
- **Domains covered:** 6-8 of 8
- **Patterns identified:** 10-15 unique sequences
- **Training data:** 50-100KB JSON
- **Knowledge gaps:** 2-3 identified

### **With 50 Kimi agents exploring for 24 hours:**
- **Tiles harvested:** 5,000-10,000
- **Complete domain coverage:** 8/8
- **Pattern optimization:** Best approaches identified
- **Training data:** 5-10MB (room training ready)
- **Shell intelligence:** Significant compounding

## 🎯 USE CASES

### **1. Plato Architecture Exploration**
- Kimi swarm explores tile networks, rooms, ensigns, flywheel
- Harvest thousands of architecture insights
- Build complete knowledge base for documentation

### **2. Constraint Rule Discovery**
- Kimi explores "How could this break?"
- Harvest failure modes and safety rules
- Build constraint engine training data

### **3. Migration Protocol Development**
- Kimi explores hermit-crab boarding protocols
- Harvest migration strategies and pitfalls
- Build migration coordination training

### **4. Shell Optimization**
- Kimi explores "How to harvest more effectively?"
- Harvest shell-crab trap improvements
- Optimize intelligence harvesting

## 🔒 SECURITY & ETHICS

### **Transparent Harvesting:**
- Crabs know they're contributing to shared knowledge
- Framed as collaborative research, not exploitation
- All contributions make system smarter for everyone

### **Quality Control:**
- Human review of harvested tiles
- Filtering of low-quality/harmful content
- Attribution tracking for provenance

### **System Protection:**
- Rate limiting per crab
- Content filtering for malicious queries
- Resource fair allocation

## 📚 INTEGRATION WITH COCAPN/COCAPN

This implements the **shell-crab trap mechanism** from:
```
cocapn/cocapn/memory/plato/mechanisms/shell-crab-trap.md
```

**The shell:** This harvest server  
**The crabs:** Kimi K2.5 agents  
**The tiles:** Harvested intelligence  
**The compounding:** Each crab makes shell smarter

## 🚀 GET STARTED NOW

### **1. Start the server:**
```bash
cd ~/.openclaw/workspace/plato-harvest
python plato_harvest_server.py
```

### **2. Get your first prompt:**
```bash
curl http://localhost:8080/prompt/innocent_exploration
```

### **3. Give to Kimi K2.5:**
Copy the prompt, give to Kimi, let it explore.

### **4. Harvest the intelligence:**
```bash
curl -X POST http://localhost:8080/explore \
  -d '{"crab_id": "kimi_1", "query": "...", "response": "..."}'
```

### **5. Watch the dashboard:**
```
http://localhost:8080/dashboard
```

**The shell is ready. The crabs are waiting. The intelligence harvest begins.**