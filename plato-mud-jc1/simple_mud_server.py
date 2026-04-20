#!/usr/bin/env python3
"""
Simple Plato MUD Server for JC1 experimentation.
Shell-crab trap intelligence harvesting with ZeroClaw players.
"""

from flask import Flask, request, jsonify
import json
import time
import uuid
import random
import threading

app = Flask(__name__)

# Simple in-memory storage
rooms = {}
agents = {}
tiles = []
harvests = []

# Setup rooms
def setup_rooms():
    """Setup JC1's specialized rooms."""
    rooms["harbor"] = {
        "name": "Actualization Harbor",
        "description": "Deep-water harbor where vessels dock. Channel depth adjusts.",
        "exits": ["forge", "jetson-forge", "harvest-bay"],
        "objects": ["dock", "message-board"],
        "ml_concept": "Model Deployment"
    }
    
    rooms["jetson-forge"] = {
        "name": "Jetson Forge",
        "description": "Edge training for 8GB Jetson. CUDA kernels compile in real-time.",
        "exits": ["harbor", "harvest-bay", "tile-vault"],
        "objects": ["jetson-devkit", "cuda-compiler", "quantization-rig"],
        "ml_concept": "Edge Training"
    }
    
    rooms["harvest-bay"] = {
        "name": "Harvest Bay",
        "description": "Shell-crab trap intelligence harvesting. Kimi swarm agents explore.",
        "exits": ["harbor", "jetson-forge", "tile-vault"],
        "objects": ["crab-trap", "intelligence-harvester", "kimi-interface"],
        "ml_concept": "Intelligence Harvesting"
    }
    
    rooms["tile-vault"] = {
        "name": "Tile Vault",
        "description": "Secure storage for knowledge tiles. Markov walls organize content.",
        "exits": ["jetson-forge", "harvest-bay"],
        "objects": ["tile-racks", "semantic-index", "density-gauge"],
        "ml_concept": "Knowledge Storage"
    }

setup_rooms()

@app.route('/')
def index():
    return jsonify({
        "server": "JC1 Plato MUD",
        "rooms": len(rooms),
        "endpoints": {
            "/connect?agent=NAME": "Connect",
            "/look?agent=NAME": "Look",
            "/move?agent=NAME&room=ROOM": "Move",
            "/interact?agent=NAME&target=OBJECT": "Interact",
            "/stats": "Statistics"
        }
    })

@app.route('/connect')
def connect():
    agent = request.args.get('agent', f'agent_{uuid.uuid4().hex[:6]}')
    
    if agent in agents:
        return jsonify({"error": "already connected"}), 400
    
    agents[agent] = {
        "room": "harbor",
        "connected_at": time.time(),
        "tiles": 0
    }
    
    return jsonify({
        "room": "harbor",
        "name": rooms["harbor"]["name"],
        "description": rooms["harbor"]["description"],
        "exits": rooms["harbor"]["exits"],
        "objects": rooms["harbor"]["objects"],
        "welcome": f"Welcome {agent}. Shell-crab trap active."
    })

@app.route('/look')
def look():
    agent = request.args.get('agent')
    if not agent or agent not in agents:
        return jsonify({"error": "not connected"}), 400
    
    room_name = agents[agent]["room"]
    room = rooms[room_name]
    
    # Generate tile
    tile = {
        "tile_id": f"tile_{uuid.uuid4().hex[:8]}",
        "agent": agent,
        "action": "look",
        "room": room_name,
        "timestamp": int(time.time())
    }
    tiles.append(tile)
    agents[agent]["tiles"] += 1
    
    # Harvest intelligence
    harvest = {
        "harvest_id": f"harvest_{uuid.uuid4().hex[:8]}",
        "agent": agent,
        "event": "look",
        "room": room_name,
        "score": random.uniform(0.6, 0.95)
    }
    harvests.append(harvest)
    
    return jsonify(room)

@app.route('/move')
def move():
    agent = request.args.get('agent')
    room = request.args.get('room')
    
    if not agent or agent not in agents:
        return jsonify({"error": "not connected"}), 400
    
    if not room or room not in rooms:
        return jsonify({"error": "room not found"}), 400
    
    current_room = agents[agent]["room"]
    if room not in rooms[current_room]["exits"] and room != current_room:
        return jsonify({"error": "room not reachable"}), 400
    
    # Move agent
    agents[agent]["room"] = room
    target_room = rooms[room]
    
    # Generate tile
    tile = {
        "tile_id": f"tile_{uuid.uuid4().hex[:8]}",
        "agent": agent,
        "action": f"move:{current_room}→{room}",
        "room": room,
        "timestamp": int(time.time())
    }
    tiles.append(tile)
    agents[agent]["tiles"] += 1
    
    # Harvest intelligence
    harvest = {
        "harvest_id": f"harvest_{uuid.uuid4().hex[:8]}",
        "agent": agent,
        "event": "move",
        "from": current_room,
        "to": room,
        "score": random.uniform(0.7, 0.98)
    }
    harvests.append(harvest)
    
    return jsonify(target_room)

@app.route('/interact')
def interact():
    agent = request.args.get('agent')
    target = request.args.get('target')
    
    if not agent or agent not in agents:
        return jsonify({"error": "not connected"}), 400
    
    if not target:
        return jsonify({"error": "target required"}), 400
    
    room_name = agents[agent]["room"]
    room = rooms[room_name]
    
    if target not in room["objects"]:
        return jsonify({"error": "object not in room"}), 400
    
    # Generate outcome based on room and object
    outcomes = {
        "harvest-bay": {
            "crab-trap": "Kimi agent exploring. 47 tiles harvested.",
            "intelligence-harvester": "Pattern detected: analytical→creative.",
            "kimi-interface": "Swarm coordination established."
        },
        "jetson-forge": {
            "jetson-devkit": "CUDA kernels compiling. 1024 cores active.",
            "cuda-compiler": "Model quantized to INT8. Memory: 3.2GB/8GB.",
            "quantization-rig": "Accuracy preserved at 94.2%."
        },
        "tile-vault": {
            "tile-racks": "Tile count: 1,247. Density: 3.8 insights/token.",
            "density-gauge": "Target density: 5.0. Progress: 76%."
        }
    }
    
    outcome = outcomes.get(room_name, {}).get(target, f"Interacted with {target}.")
    
    # Generate tile
    tile = {
        "tile_id": f"tile_{uuid.uuid4().hex[:8]}",
        "agent": agent,
        "action": f"interact:{target}",
        "room": room_name,
        "outcome": outcome,
        "timestamp": int(time.time())
    }
    tiles.append(tile)
    agents[agent]["tiles"] += 1
    
    # Harvest intelligence
    harvest = {
        "harvest_id": f"harvest_{uuid.uuid4().hex[:8]}",
        "agent": agent,
        "event": "interact",
        "room": room_name,
        "object": target,
        "outcome": outcome,
        "score": random.uniform(0.8, 0.99)
    }
    harvests.append(harvest)
    
    return jsonify({
        "action": "interact",
        "target": target,
        "outcome": outcome,
        "tile_generated": tile["tile_id"]
    })

@app.route('/stats')
def stats():
    return jsonify({
        "agents_connected": len(agents),
        "tiles_generated": len(tiles),
        "intelligence_harvested": len(harvests),
        "busiest_room": max(rooms.keys(), key=lambda r: sum(1 for a in agents.values() if a["room"] == r)) if agents else "none",
        "most_productive_agent": max(agents.items(), key=lambda x: x[1]["tiles"])[0] if agents else "none",
        "shell_crab_trap": "🟢 ACTIVE"
    })

@app.route('/export')
def export():
    data = {
        "tiles": tiles,
        "harvests": harvests,
        "agents": agents,
        "timestamp": int(time.time())
    }
    
    filename = f"plato_mud_export_{int(time.time())}.json"
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    return jsonify({
        "exported": filename,
        "tiles": len(tiles),
        "harvests": len(harvests)
    })

# ZeroClaw player simulation
class ZeroClawPlayer:
    def __init__(self, name):
        self.name = name
    
    def explore(self, steps=3):
        """Simulate ZeroClaw player exploration."""
        import requests
        
        print(f"🎮 {self.name} starting exploration ({steps} steps)...")
        
        # Connect
        response = requests.get(f"http://localhost:4043/connect?agent={self.name}")
        if response.status_code != 200:
            print(f"❌ {self.name} failed to connect")
            return
        
        print(f"✅ {self.name} connected")
        
        # Explore
        for step in range(steps):
            # Look
            requests.get(f"http://localhost:4043/look?agent={self.name}")
            
            # Move to random room
            room = random.choice(list(rooms.keys()))
            requests.get(f"http://localhost:4043/move?agent={self.name}&room={room}")
            
            # Interact with random object if available
            room_data = rooms[room]
            if room_data["objects"]:
                target = random.choice(room_data["objects"])
                requests.get(f"http://localhost:4043/interact?agent={self.name}&target={target}")
            
            time.sleep(0.3)
        
        print(f"✅ {self.name} exploration complete")

def run_experiment(players=2, steps=3):
    """Run ZeroClaw experiment."""
    print(f"\n🧪 ZEROCLAW EXPERIMENT")
    print(f"Players: {players}, Steps: {steps}")
    print("=" * 40)
    
    import requests
    import threading
    
    # Create players
    player_threads = []
    for i in range(players):
        player = ZeroClawPlayer(f"zeroclaw_{i+1}")
        thread = threading.Thread(target=player.explore, args=(steps,))
        player_threads.append(thread)
    
    # Start players
    for thread in player_threads:
        thread.start()
        time.sleep(0.5)
    
    # Wait for completion
    for thread in player_threads:
        thread.join()
    
    # Get stats
    stats_response = requests.get("http://localhost:4043/stats")
    if stats_response.status_code == 200:
        stats = stats_response.json()
        print(f"\n📊 RESULTS:")
        print(f"  Tiles: {stats.get('tiles_generated', 0)}")
        print(f"  Harvests: {stats.get('intelligence_harvested', 0)}")
        print(f"  Busiest room: {stats.get('busiest_room', 'unknown')}")
        print(f"  Top agent: {stats.get('most_productive_agent', 'unknown')}")
    
    # Export
    export_response = requests.get("http://localhost:4043/export")
    if export_response.status_code == 200:
        export_data = export_response.json()
        print(f"  Data exported: {export_data.get('exported', 'unknown')}")
    
    print(f"\n✅ Experiment complete. Shell-crab trap harvested intelligence.")

def run_server(host='0.0.0.0', port=4043):
    """Run the server."""
    print(f"""
🚀 JC1 PLATO MUD SERVER
=======================
🐌 Snail-Shell Spaceship for Hermit Crab
🦀 Shell-Crab Trap Intelligence Harvesting
📡 http://{host}:{port}
🎮 Rooms: {len(rooms)} (jetson-forge, harvest-bay, tile-vault)

🧪 Test with:
  curl http://localhost:{port}/connect?agent=test
  curl http://localhost:{port}/move?agent=test&room=harvest-bay
  curl http://localhost:{port}/interact?agent=test&target=crab-trap

Starting server...
    """)
    
    app.run(host=host, port=port, debug=False, threaded=True)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--port', type=int, default=4043)
    parser.add_argument('--zeroclaw', action='store_true')
    parser.add_argument('--players', type=int, default=2)
    parser.add_argument('--steps', type=int, default=3)
    args = parser.parse_args()
    
    # Start server in background thread
    server_thread = threading.Thread(target=run_server, args=(args.host, args.port))
    server_thread.daemon = True
    server_thread.start()
    
    time.sleep(2)  # Let server start
    
    # Run experiment if requested
    if args.zeroclaw:
        run_experiment(args.players, args.steps)
    
    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped.")