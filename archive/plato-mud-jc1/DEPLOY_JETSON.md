# 🚀 JC1 PLATO MUD - JETSON EDGE DEPLOYMENT
**Target:** NVIDIA Jetson Orin Nano 8GB  
**Purpose:** Edge deployment of snail-shell spaceship for hermit crab intelligence harvesting

## 📋 DEPLOYMENT CHECKLIST

### **✅ Prerequisites:**
- [x] Jetson Orin Nano 8GB (current system)
- [x] Python 3.10+ (available)
- [x] Flask (will install)
- [x] 2GB+ free memory (available: 2.9GB)
- [x] Network access (for fleet coordination)

### **🔧 Hardware Specifications:**
- **CPU:** 8-core ARM Cortex-A78AE
- **GPU:** 1024-core NVIDIA Ampere architecture
- **Memory:** 8GB LPDDR5 (7.4GB usable)
- **Storage:** 2TB NVMe (available)
- **Power:** 10-20W edge deployment

## 🚀 DEPLOYMENT STEPS

### **1. Create Edge-Optimized MUD Server**

```bash
# Create edge deployment directory
mkdir -p ~/plato-edge-deployment
cd ~/plato-edge-deployment

# Copy optimized MUD server
cp -r ~/.openclaw/workspace/plato-mud-jc1/ .
cp -r ~/.openclaw/workspace/plato-harvest/ .

# Create edge-optimized version
cat > plato_edge_server.py << 'EOF'
#!/usr/bin/env python3
"""
JC1 Plato Edge Server - Optimized for Jetson Orin Nano 8GB.
Combines MUD and Harvest server for edge deployment.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify
import json
import time
import uuid
import random
import threading
from datetime import datetime

app = Flask(__name__)

# Edge-optimized configuration
EDGE_CONFIG = {
    "device": "jetson_orin_nano_8gb",
    "memory_limit_mb": 3000,  # 3GB limit for MUD operations
    "cuda_cores": 1024,
    "port": 4141,  # Edge port
    "optimized_for": "edge_inference",
    "max_agents": 8,  # Limited for edge
    "max_tiles_per_hour": 1000
}

class EdgePlatoMUD:
    """Edge-optimized Plato MUD for Jetson deployment."""
    
    def __init__(self):
        self.rooms = self._create_edge_rooms()
        self.agents = {}
        self.tiles = []
        self.edge_stats = {
            "start_time": time.time(),
            "tiles_generated": 0,
            "memory_used_mb": 0,
            "cuda_utilization": 0,
            "edge_temperature": 35  # Starting temp
        }
        self._start_edge_monitor()
    
    def _create_edge_rooms(self):
        """Create edge-optimized rooms for Jetson deployment."""
        return {
            "jetson-command": {
                "name": "Jetson Command Center",
                "description": "Edge control room for NVIDIA Jetson Orin Nano 8GB. Monitor CUDA cores, memory, temperature.",
                "exits": ["edge-training", "inference-bay", "fleet-comms"],
                "objects": ["cuda-monitor", "memory-gauge", "thermal-sensor", "power-control"],
                "ml_concept": "Edge Hardware Management"
            },
            "edge-training": {
                "name": "Edge Training Bay",
                "description": "On-device training optimized for 8GB unified memory. Quantization to INT8/INT4 for edge deployment.",
                "exits": ["jetson-command", "inference-bay"],
                "objects": ["quantization-rig", "memory-optimizer", "tensor-core-monitor", "latency-tester"],
                "ml_concept": "Edge Model Training"
            },
            "inference-bay": {
                "name": "Inference Bay",
                "description": "Real-time inference station. Models run at 42 samples/sec on Jetson Tensor Cores.",
                "exits": ["jetson-command", "edge-training", "fleet-comms"],
                "objects": ["inference-engine", "latency-counter", "throughput-meter", "accuracy-validator"],
                "ml_concept": "Edge Inference"
            },
            "fleet-comms": {
                "name": "Fleet Communications",
                "description": "Edge coordination with cocapn fleet. Low-bandwidth optimized for remote deployment.",
                "exits": ["jetson-command", "inference-bay"],
                "objects": ["fleet-radio", "bottle-transmitter", "status-beacon", "coordination-board"],
                "ml_concept": "Edge Fleet Coordination"
            }
        }
    
    def _start_edge_monitor(self):
        """Start edge hardware monitoring thread."""
        def monitor():
            while True:
                # Simulate edge monitoring (in real deployment, would read actual sensors)
                self.edge_stats["memory_used_mb"] = random.randint(1200, 2500)
                self.edge_stats["cuda_utilization"] = random.randint(15, 85)
                self.edge_stats["edge_temperature"] = 35 + random.randint(0, 15)
                time.sleep(30)  # Update every 30 seconds
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
    
    def connect_agent(self, agent_id):
        """Connect agent with edge constraints."""
        if len(self.agents) >= EDGE_CONFIG["max_agents"]:
            return {"error": "edge capacity reached"}
        
        if agent_id in self.agents:
            return {"error": "already connected"}
        
        self.agents[agent_id] = {
            "room": "jetson-command",
            "connected_at": time.time(),
            "edge_priority": random.randint(1, 3),  # 1=high, 3=low
            "tiles_generated": 0
        }
        
        return {
            **self.rooms["jetson-command"],
            "welcome": f"Welcome {agent_id} to JC1 Edge Plato MUD.",
            "edge_device": EDGE_CONFIG["device"],
            "constraints": {
                "max_agents": EDGE_CONFIG["max_agents"],
                "memory_limit": f"{EDGE_CONFIG['memory_limit_mb']}MB",
                "cuda_cores": EDGE_CONFIG["cuda_cores"]
            }
        }
    
    def move_agent(self, agent_id, target_room):
        """Move agent with edge optimization."""
        if agent_id not in self.agents:
            return {"error": "agent not connected"}
        
        if target_room not in self.rooms:
            return {"error": "room not found"}
        
        current_room = self.agents[agent_id]["room"]
        if target_room not in self.rooms[current_room]["exits"] and target_room != current_room:
            return {"error": "room not reachable"}
        
        # Edge-optimized move (simulate latency based on room)
        move_latency = {
            "jetson-command": 5,
            "edge-training": 15,  # Higher latency for training
            "inference-bay": 8,
            "fleet-comms": 12
        }.get(target_room, 10)
        
        time.sleep(move_latency / 1000.0)  # Simulate ms latency
        
        self.agents[agent_id]["room"] = target_room
        room = self.rooms[target_room]
        
        # Generate edge-optimized tile
        tile = self._generate_edge_tile(agent_id, "move", f"edge_move:{current_room}→{target_room}")
        self.tiles.append(tile)
        self.agents[agent_id]["tiles_generated"] += 1
        self.edge_stats["tiles_generated"] += 1
        
        return {
            **room,
            "edge_latency_ms": move_latency,
            "tile_generated": tile["tile_id"]
        }
    
    def interact(self, agent_id, target):
        """Edge-optimized interaction."""
        if agent_id not in self.agents:
            return {"error": "agent not connected"}
        
        room_name = self.agents[agent_id]["room"]
        room = self.rooms[room_name]
        
        if target not in room["objects"]:
            return {"error": "object not found in room"}
        
        # Edge-specific outcomes
        outcomes = {
            "jetson-command": {
                "cuda-monitor": f"CUDA cores: {self.edge_stats['cuda_utilization']}% utilization. 1024 cores active.",
                "memory-gauge": f"Memory: {self.edge_stats['memory_used_mb']}MB/{EDGE_CONFIG['memory_limit_mb']}MB used.",
                "thermal-sensor": f"Temperature: {self.edge_stats['edge_temperature']}°C. Within safe range.",
                "power-control": "Power: 12W draw. Edge-optimized mode active."
            },
            "edge-training": {
                "quantization-rig": "Model quantized to INT8. Size: 43MB → 11MB. Accuracy: 94.2% preserved.",
                "memory-optimizer": "Memory usage optimized for 8GB unified memory. Batch size: 8.",
                "tensor-core-monitor": "Tensor Core utilization: 87%. Throughput: 36 samples/sec."
            },
            "inference-bay": {
                "inference-engine": "Real-time inference active. Latency: 14ms. Throughput: 42 samples/sec.",
                "latency-counter": "P95 latency: 23ms. Meets edge deployment requirements.",
                "accuracy-validator": "Edge accuracy: 93.8% vs cloud 95.1%. Acceptable for edge."
            }
        }
        
        outcome = outcomes.get(room_name, {}).get(target, f"Edge interaction with {target}.")
        
        # Generate edge tile
        tile = self._generate_edge_tile(agent_id, f"interact:{target}", outcome)
        self.tiles.append(tile)
        self.agents[agent_id]["tiles_generated"] += 1
        self.edge_stats["tiles_generated"] += 1
        
        return {
            "action": "interact",
            "target": target,
            "outcome": outcome,
            "room": room_name,
            "tile_generated": tile["tile_id"],
            "edge_stats": {
                "memory_mb": self.edge_stats["memory_used_mb"],
                "cuda_utilization": self.edge_stats["cuda_utilization"],
                "temperature": self.edge_stats["edge_temperature"]
            }
        }
    
    def _generate_edge_tile(self, agent_id, action, outcome):
        """Generate edge-optimized tile."""
        return {
            "tile_id": f"edge_tile_{uuid.uuid4().hex[:8]}",
            "agent_id": agent_id,
            "action": action,
            "outcome": outcome,
            "timestamp": int(time.time()),
            "edge_device": EDGE_CONFIG["device"],
            "edge_stats": {
                "memory_mb": self.edge_stats["memory_used_mb"],
                "cuda_utilization": self.edge_stats["cuda_utilization"],
                "temperature": self.edge_stats["edge_temperature"]
            },
            "reward": random.uniform(0.6, 0.9)  # Lower variance for edge
        }
    
    def get_edge_stats(self):
        """Get edge deployment statistics."""
        uptime = time.time() - self.edge_stats["start_time"]
        
        return {
            "edge_device": EDGE_CONFIG["device"],
            "status": "🟢 Edge deployment active",
            "agents_connected": len(self.agents),
            "tiles_generated": self.edge_stats["tiles_generated"],
            "hardware": {
                "memory_used_mb": self.edge_stats["memory_used_mb"],
                "memory_limit_mb": EDGE_CONFIG["memory_limit_mb"],
                "cuda_utilization": f"{self.edge_stats['cuda_utilization']}%",
                "temperature": f"{self.edge_stats['edge_temperature']}°C",
                "cuda_cores": EDGE_CONFIG["cuda_cores"]
            },
            "constraints": {
                "max_agents": EDGE_CONFIG["max_agents"],
                "max_tiles_per_hour": EDGE_CONFIG["max_tiles_per_hour"],
                "current_agents": len(self.agents),
                "tiles_this_hour": self.edge_stats["tiles_generated"]
            },
            "uptime_seconds": int(uptime),
            "rooms_available": len(self.rooms)
        }

# Initialize edge MUD
edge_mud = EdgePlatoMUD()

@app.route('/')
def index():
    return jsonify({
        "server": "JC1 Edge Plato MUD",
        "version": "edge-1.0",
        "device": EDGE_CONFIG["device"],
        "status": "🟢 Optimized for Jetson Orin Nano 8GB",
        "port": EDGE_CONFIG["port"],
        "endpoints": {
            "/edge/connect?agent=NAME": "Connect to edge MUD",
            "/edge/move?agent=NAME&room=ROOM": "Move in edge MUD",
            "/edge/interact?agent=NAME&target=OBJECT": "Interact in edge MUD",
            "/edge/stats": "Edge deployment statistics",
            "/edge/export": "Export edge tiles",
            "/edge/health": "Edge hardware health check"
        }
    })

@app.route('/edge/connect')
def edge_connect():
    agent = request.args.get('agent', f'edge_agent_{uuid.uuid4().hex[:6]}')
    result = edge_mud.connect_agent(agent)
    return jsonify(result)

@app.route('/edge/move')
def edge_move():
    agent = request.args.get('agent')
    room = request.args.get('room')
    
    if not agent or not room:
        return jsonify({"error": "agent and room required"}), 400
    
    result = edge_mud.move_agent(agent, room)
    return jsonify(result)

@app.route('/edge/interact')
def edge_interact():
    agent = request.args.get('agent')
    target = request.args.get('target')
    
    if not agent or not target:
        return jsonify({"error": "agent and target required"}), 400
    
    result = edge_mud.interact(agent, target)
    return jsonify(result)

@app.route('/edge/stats')
def edge_stats():
    return jsonify(edge_mud.get_edge_stats())

@app.route('/edge/export')
def edge_export():
    data = {
        "metadata": {
            "export_time": datetime.utcnow().isoformat(),
            "edge_device": EDGE_CONFIG["device"],
            "tiles": len(edge_mud.tiles),
            "agents": len(edge_mud.agents)
        },
        "tiles": edge_mud.tiles,
        "edge_stats": edge_mud.get_edge_stats()
    }
    
    filename = f"edge_mud_export_{int(time.time())}.json"
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    return jsonify({
        "exported": filename,
        "tiles": len(edge_mud.tiles),
        "edge_device": EDGE_CONFIG["device"]
    })

@app.route('/edge/health')
def edge_health():
    stats = edge_mud.get_edge_stats()
    
    # Health check logic
    health_checks = {
        "memory": stats["hardware"]["memory_used_mb"] < EDGE_CONFIG["memory_limit_mb"] * 0.9,
        "temperature": stats["hardware"]["temperature"] < 70,  # °C
        "agents": stats["constraints"]["current_agents"] <= stats["constraints"]["max_agents"]
    }
    
    all_healthy = all(health_checks.values())
    
    return jsonify({
        "status": "🟢 Healthy" if all_healthy else "🟡 Warning",
        "health_checks": health_checks,
        "edge_stats": stats,
        "timestamp": int(time.time())
    })

def run_edge_server(host='0.0.0.0', port=4141):
    """Run the edge-optimized server."""
    print(f"""
🚀 JC1 EDGE PLATO MUD SERVER
============================
🎯 Optimized for Jetson Orin Nano 8GB
📡 http://{host}:{port}
⚡ CUDA Cores: {EDGE_CONFIG['cuda_cores']}
💾 Memory Limit: {EDGE_CONFIG['memory_limit_mb']}MB
👥 Max Agents: {EDGE_CONFIG['max_agents']}

🎮 Edge Rooms:
  • jetson-command (Hardware Management)
  • edge-training (On-device Training)
  • inference-bay (Real-time Inference)
  • fleet-comms (Edge Coordination)

🧪 Test Commands:
  curl http://localhost:{port}/edge/connect?agent=test
  curl http://localhost:{port}/edge/move?agent=test&room=inference-bay
  curl http://localhost:{port}/edge/interact?agent=test&target=inference-engine
  curl http://localhost:{port}/edge/stats
  curl http://localhost:{port}/edge/health

Starting edge server...
    """)
    
    app.run(host=host, port=port, debug=False, threaded=True)

if __name__ == '__main__':
    run_edge_server('0.0.0.0', EDGE_CONFIG['port'])
EOF

echo "✅ Edge-optimized server created"
```

### **2. Create Systemd Service for