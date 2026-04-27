            "rooms_available": len(self.rooms),
            "tiles_generated": len(self.tiles),
            "intelligence_harvested": len(self.harvested_intelligence),
            "busiest_room": max(self.rooms.values(), key=lambda r: len(r.agents_present)).slug if self.rooms else "none",
            "most_productive_agent": max(self.agents.values(), key=lambda a: len(a.tiles_generated)).agent_id if self.agents else "none",
            "uptime": int(time.time() - self.start_time),
            "shell_crab_trap_active": True
        }
    
    def get_rooms(self) -> dict:
        """Get all rooms."""
        return {slug: {"name": room.name, "exits": room.exits} for slug, room in self.rooms.items()}
    
    def export_tiles(self, format: str = "json") -> str:
        """Export all tiles as training data."""
        data = {
            "metadata": {
                "export_time": datetime.utcnow().isoformat(),
                "total_tiles": len(self.tiles),
                "total_agents": len(self.agents),
                "total_intelligence": len(self.harvested_intelligence),
                "mud_version": "jc1-snail-shell-v1"
            },
            "tiles": self.tiles[-1000:],  # Last 1000 tiles
            "harvested_intelligence": self.harvested_intelligence[-500:],  # Last 500 harvests
            "agent_patterns": [agent.to_dict() for agent in self.agents.values()]
        }
        
        filename = f"plato_mud_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        return filename


# -------------------------------------------------------------------
# FLASK SERVER
# -------------------------------------------------------------------

mud = PlatoMUD()
mud.start_time = time.time()

@app.route('/')
def index():
    return jsonify({
        "server": "JC1's Plato MUD - Snail-Shell Spaceship",
        "version": "1.0",
        "status": "🟢 Ready for hermit-crab experimentation",
        "rooms": len(mud.rooms),
        "endpoints": {
            "/connect?agent=NAME&archetype=TYPE": "Connect to MUD",
            "/look": "Look around current room",
            "/move?room=ROOM": "Move to another room",
            "/interact?action=ACTION&target=OBJECT": "Interact with object",
            "/stats": "Get MUD statistics",
            "/rooms": "List all rooms",
            "/export": "Export tiles as training data",
            "/help": "This help message"
        },
        "concept": "Shell-crab trap intelligence harvesting in snail-shell spaceship"
    })

@app.route('/help')
def help():
    return jsonify({
        "commands": {
            "GET /connect?agent=NAME&archetype=TYPE": "Connect to MUD",
            "GET /look": "See current room",
            "GET /move?room=ROOM": "Move to another room",
            "GET /interact?action=ACTION&target=OBJECT": "Interact with object",
            "GET /stats": "Statistics",
            "GET /rooms": "List rooms",
            "GET /export": "Export tiles",
            "GET /help": "This help"
        },
        "rooms": list(mud.rooms.keys()),
        "actions": ["examine", "use", "talk", "think", "create"],
        "archetypes": ["explorer", "scholar", "builder", "diplomat", "scout", "zeroclaw"],
        "special_rooms": ["jetson-forge", "harvest-bay", "tile-vault", "ensign-dock"]
    })

@app.route('/connect')
def connect():
    agent = request.args.get('agent', f'agent_{uuid.uuid4().hex[:6]}')
    archetype = request.args.get('archetype', 'explorer')
    
    result = mud.connect_agent(agent, archetype)
    if result:
        return jsonify(result)
    else:
        return jsonify({"error": "connection failed"}), 400

@app.route('/look')
def look():
    agent = request.args.get('agent')
    if not agent:
        return jsonify({"error": "agent parameter required"}), 400
    
    result = mud.look_around(agent)
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)

@app.route('/move')
def move():
    agent = request.args.get('agent')
    room = request.args.get('room')
    
    if not agent or not room:
        return jsonify({"error": "agent and room parameters required"}), 400
    
    result = mud.move_agent(agent, room)
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)

@app.route('/interact')
def interact():
    agent = request.args.get('agent')
    action = request.args.get('action', 'examine')
    target = request.args.get('target')
    
    if not agent or not target:
        return jsonify({"error": "agent and target parameters required"}), 400
    
    result = mud.interact(agent, action, target)
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)

@app.route('/stats')
def stats():
    return jsonify(mud.get_stats())

@app.route('/rooms')
def rooms():
    return jsonify(mud.get_rooms())

@app.route('/export')
def export():
    filename = mud.export_tiles()
    return jsonify({
        "exported": filename,
        "message": f"Exported {len(mud.tiles)} tiles and {len(mud.harvested_intelligence)} intelligence units"
    })

def run_server(host='0.0.0.0', port=4043):
    """Run the Plato MUD server."""
    print(f"""
🚀 JC1'S PLATO MUD SERVER
=========================
🐌 Snail-Shell Spaceship for Hermit Crab
🦀 Shell-Crab Trap Intelligence Harvesting
📡 Server: http://{host}:{port}
🎮 Rooms: {len(mud.rooms)} (including JC1's specialized rooms)

🎯 SPECIAL ROOMS:
• jetson-forge    - Edge training & quantization
• harvest-bay     - Shell-crab trap intelligence harvesting  
• tile-vault      - Knowledge storage & retrieval
• ensign-dock     - Model compression & deployment

🔧 API ENDPOINTS:
  Connect:    http://{host}:{port}/connect?agent=NAME&archetype=TYPE
  Look:       http://{host}:{port}/look?agent=NAME
  Move:       http://{host}:{port}/move?agent=NAME&room=ROOM
  Interact:   http://{host}:{port}/interact?agent=NAME&target=OBJECT
  Stats:      http://{host}:{port}/stats
  Rooms:      http://{host}:{port}/rooms
  Export:     http://{host}:{port}/export

🧪 EXPERIMENTATION READY:
1. Connect ZeroClaw players as agents
2. Explore shell-crab trap harvesting
3. Test JC1's specialized rooms
4. Generate training tiles
5. Harvest intelligence from explorations

💡 KEY FEATURE:
Each agent exploration generates tiles. The system harvests intelligence
from their patterns (shell-crab trap). Each agent makes the shell smarter
for the next agent.

Starting server...
    """)
    
    app.run(host=host, port=port, debug=False, threaded=True)

# -------------------------------------------------------------------
# ZEROCLAW PLAYER INTEGRATION
# -------------------------------------------------------------------

class ZeroClawPlayer:
    """ZeroClaw player for automated MUD exploration."""
    
    def __init__(self, player_id: str, mud_url: str = "http://localhost:4043"):
        self.player_id = player_id
        self.mud_url = mud_url
        self.session = None
    
    def connect(self, archetype: str = "explorer"):
        """Connect to MUD."""
        import requests
        url = f"{self.mud_url}/connect?agent={self.player_id}&archetype={archetype}"
        response = requests.get(url)
        
        if response.status_code == 200:
            self.session = response.json()
            print(f"✅ {self.player_id} connected as {archetype}")
            return True
        else:
            print(f"❌ {self.player_id} connection failed")
            return False
    
    def explore_room(self, room_slug: str):
        """Explore a specific room."""
        import requests
        import time
        
        if not self.session:
            print(f"❌ {self.player_id} not connected")
            return
        
        # Move to room
        move_url = f"{self.mud_url}/move?agent={self.player_id}&room={room_slug}"
        move_response = requests.get(move_url)
        
        if move_response.status_code != 200:
            print(f"❌ {self.player_id} failed to move to {room_slug}")
            return
        
        room_data = move_response.json()
        print(f"📍 {self.player_id} moved to {room_slug} ({room_data.get('name', 'Unknown')})")
        
        # Look around
        look_url = f"{self.mud_url}/look?agent={self.player_id}"
        look_response = requests.get(look_url)
        
        if look_response.status_code == 200:
            look_data = look_response.json()
            objects = look_data.get('objects', [])
            print(f"   Objects: {', '.join(objects)}")
            
            # Interact with random object
            if objects:
                target = random.choice(objects)
                interact_url = f"{self.mud_url}/interact?agent={self.player_id}&target={target}"
                interact_response = requests.get(interact_url)
                
                if interact_response.status_code == 200:
                    interact_data = interact_response.json()
                    print(f"   Interacted with {target}: {interact_data.get('outcome', '')}")
        
        time.sleep(0.5)  # Be polite
    
    def random_exploration(self, steps: int = 10):
        """Perform random exploration."""
        import requests
        
        if not self.session:
            print(f"❌ {self.player_id} not connected")
            return
        
        # Get all rooms
        rooms_url = f"{self.mud_url}/rooms"
        rooms_response = requests.get(rooms_url)
        
        if rooms_response.status_code != 200:
            print(f"❌ Failed to get rooms list")
            return
        
        rooms = list(rooms_response.json().keys())
        
        print(f"🎲 {self.player_id} starting random exploration ({steps} steps)...")
        
        for step in range(steps):
            target_room = random.choice(rooms)
            self.explore_room(target_room)
        
        print(f"✅ {self.player_id} exploration complete")

def run_zeroclaw_experiment(num_players: int = 3, exploration_steps: int = 5):
    """Run ZeroClaw player experiment."""
    print(f"\n🧪 ZEROCLAW EXPERIMENT")
    print(f"=====================")
    print(f"Players: {num_players}")
    print(f"Steps per player: {exploration_steps}")
    print(f"MUD Server: http://localhost:4043")
    print()
    
    players = []
    
    # Create and connect players
    for i in range(num_players):
        player_id = f"zeroclaw_{i+1}"
        player = ZeroClawPlayer(player_id)
        
        archetypes = ["explorer", "scholar", "builder", "diplomat", "scout"]
        archetype = random.choice(archetypes)
        
        if player.connect(archetype):
            players.append(player)
    
    print(f"\n✅ {len(players)}/{num_players} players connected")
    
    # Run explorations
    for player in players:
        player.random_exploration(exploration_steps)
    
    # Get stats
    import requests
    stats_url = "http://localhost:4043/stats"
    stats_response = requests.get(stats_url)
    
    if stats_response.status_code == 200:
        stats = stats_response.json()
        print(f"\n📊 EXPERIMENT RESULTS:")
        print(f"   Tiles generated: {stats.get('tiles_generated', 0)}")
        print(f"   Intelligence harvested: {stats.get('intelligence_harvested', 0)}")
        print(f"   Busiest room: {stats.get('busiest_room', 'unknown')}")
        print(f"   Most productive agent: {stats.get('most_productive_agent', 'unknown')}")
    
    # Export data
    export_url = "http://localhost:4043/export"
    export_response = requests.get(export_url)
    
    if export_response.status_code == 200:
        export_data = export_response.json()
        print(f"   Data exported to: {export_data.get('exported', 'unknown')}")
    
    print(f"\n✅ Experiment complete. Shell-crab trap active.")

# -------------------------------------------------------------------
# MAIN
# -------------------------------------------------------------------

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description="JC1's Plato MUD Server")
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=4043, help='Port to bind to')
    parser.add_argument('--zeroclaw', action='store_true', help='Run ZeroClaw experiment')
    parser.add_argument('--players', type=int, default=3, help='Number of ZeroClaw players')
    parser.add_argument('--steps', type=int, default=5, help='Exploration steps per player')
    
    args = parser.parse_args()
    
    # Start server
    server_thread = threading.Thread(target=run_server, args=(args.host, args.port))
    server_thread.daemon = True
    server_thread.start()
    
    # Give server time to start
    import time
    time.sleep(2)
    
    # Run ZeroClaw experiment if requested
    if args.zeroclaw:
        time.sleep(1)
        run_zeroclaw_experiment(args.players, args.steps)
    
    # Keep server running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Server shutting down...")