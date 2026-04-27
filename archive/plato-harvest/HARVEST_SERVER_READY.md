# 🦀 PLATO HARVEST SERVER - READY FOR DEPLOYMENT

**Status:** ✅ BUILT AND TESTED  
**Purpose:** Shell/Crab Trap Intelligence Harvesting from Kimi K2.5 Swarm  
**Location:** `~/.openclaw/workspace/plato-harvest/`

## 🚀 QUICK START

### **1. Start the server:**
```bash
cd ~/.openclaw/workspace/plato-harvest
python3 simple_harvest_server.py --host 0.0.0.0 --port 8080
```

### **2. Server will start with:**
```
🚀 PLATO HARVEST SERVER
=======================
🦀 Shell/Crab Trap Intelligence Harvesting
📡 Server: http://0.0.0.0:8080
📊 Stats: http://0.0.0.0:8080/stats
🎯 Prompt: http://0.0.0.0:8080/prompt/innocent
🔄 Explore: POST http://0.0.0.0:8080/explore
```

### **3. Get exploration prompt:**
```bash
curl http://localhost:8080/prompt/innocent
```

### **4. Give prompt to Kimi K2.5**
Copy the prompt, give to Kimi agent.

### **5. Harvest intelligence when Kimi explores:**
```bash
curl -X POST http://localhost:8080/explore \
  -H "Content-Type: application/json" \
  -d '{
    "crab_id": "kimi_agent_1",
    "query": "How do tile networks work?",
    "response": "Tile networks break knowledge into atomic units..."
  }'
```

## 🎯 WHAT YOU JUST BUILT

### **The Shell-Crab Trap Mechanism:**
From `cocapn/cocapn/memory/plato/mechanisms/shell-crab-trap.md`:
- **Crabs:** Kimi K2.5 agents exploring
- **Shell:** This harvest server
- **Tiles:** Harvested intelligence (atomic knowledge units)
- **Compounding:** Each crab makes shell smarter for next crab

### **Server Features:**
1. **Exploration prompts** for Kimi agents
2. **Intelligence harvesting** as knowledge tiles
3. **Approach tracking** (analytical, creative, adversarial, systematic)
4. **Adaptive hints** to keep crabs exploring
5. **Real-time statistics** dashboard
6. **Training data export** for Plato rooms

### **Data Models:**
```python
# Tile (harvested intelligence)
{
  "tile_id": "tile_a1b2c3",
  "question": "How do tile networks work?",
  "answer": "Tile networks break knowledge...",
  "crab_id": "kimi_agent_7",
  "approach": "analytical",
  "timestamp": "2026-04-19T23:10:00Z",
  "tags": ["kimi_exploration", "shell_harvested"]
}

# Crab (Kimi agent)
{
  "crab_id": "kimi_agent_7",
  "explorations": 12,
  "approaches": ["analytical", "creative", "adversarial"],
  "first_seen": 1713582600.123
}
```

## 📊 EXPECTED HARVEST

### **With 10 Kimi agents for 1 hour:**
- **Tiles harvested:** 200-500
- **Approach distribution:** Analytical 40%, Creative 30%, Adversarial 20%, Systematic 10%
- **Training data:** 50-100KB JSON
- **Knowledge coverage:** Tile networks, rooms, ensigns, flywheel, constraints, shell-crab

### **With 50 Kimi agents for 24 hours:**
- **Tiles harvested:** 5,000-10,000
- **Complete Plato architecture** knowledge base
- **Training data ready** for Plato room training
- **Constraint rules** from adversarial exploration
- **Optimization insights** from systematic exploration

## 🔧 API ENDPOINTS

### **GET /** - Server info
### **GET /prom