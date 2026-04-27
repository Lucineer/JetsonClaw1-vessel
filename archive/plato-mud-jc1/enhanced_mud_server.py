            "special_features": ["sentiment_tracking", "archetype_behaviors", "shell_crab_trap", "ml_concept_mapping"]
    })

@app.route('/connect')
def connect():
    agent = request.args.get('agent', f'agent_{uuid.uuid4().hex[:6]}')
    archetype = request.args.get('archetype', 'explorer')
    
    if archetype not in Agent.ARCHETYPES:
        return jsonify({"error": f"invalid archetype. choose from: {list(Agent.ARCHETYPES.keys())}"}), 400
    
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
    target = request.args.get('target')
    
    if not agent or not target:
        return jsonify({"error": "agent and target parameters required"}), 400
    
    result = mud.interact(agent, target)
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
        "message": f"Exported {len(mud.tiles)} tiles and {len(mud.harvested_intelligence)} intelligence units",
        "sentiment_data": "included",
        "archetype_patterns": "included"
    })

# -------------------------------------------------------------------
# ZEROCLAW ENHANCED PLAYER
# -------------------------------------------------------------------

class EnhancedZeroClawPlayer:
    """Enhanced ZeroClaw player with archetype behaviors."""
    
    def __init__(self, player_id: str, archetype: str = "zeroclaw", mud_url: str = "http://localhost:4044"):
        self.player_id = player_id
        self.archetype = archetype
        self.mud_url = mud_url
        self.session = None
    
    def connect(self):
        """Connect to MUD with archetype."""
        import requests
        url = f"{self.mud_url}/connect?agent={self.player_id}&archetype={self.archetype}"
        response = requests.get(url)
        
        if response.status_code == 200:
            self.session = response.json()
            print(f"✅ {self.player_id} connected as {self.archetype}")
            return True
        else:
            print(f"❌ {self.player_id} connection failed: {response.text}")
            return False
    
    def explore_room(self, room_slug: str):
        """Explore a room with archetype-appropriate behavior."""
        import requests
        import time
        
        if not self.session:
            print(f"❌ {self.player_id} not connected")
            return
        
        # Move to room
        move_url = f"{self.mud_url}/move?agent={self.player_id}&room={room_slug}"
        move_response = requests.get(move_url)
        
        if move_response.status_code != 200:
            print(f"❌ {self.player_id} failed to move to {room_slug}: {move_response.text}")
            return
        
        room_data = move_response.json()
        print(f"📍 {self.player_id} ({self.archetype}) moved to {room_slug}")
        
        # Look around
        look_url = f"{self.mud_url}/look?agent={self.player_id}"
        look_response = requests.get(look_url)
        
        if look_response.status_code == 200:
            look_data = look_response.json()
            objects = look_data.get('objects', [])
            
            # Archetype-specific interaction logic
            if objects:
                if self.archetype == "explorer":
                    # Explorer interacts with everything
                    for obj in objects[:2]:  # Limit to 2 objects
                        self._interact_with(obj)
                        time.sleep(0.2)
                elif self.archetype == "scholar":
                    # Scholar interacts with analytical objects
                    analytical_objs = [o for o in objects if any(x in o for x in ["analyzer", "index", "gauge", "metric"])]
                    if analytical_objs:
                        self._interact_with(random.choice(analytical_objs))
                elif self.archetype == "builder":
                    # Builder interacts with tools
                    tool_objs = [o for o in objects if any(x in o for x in ["tool", "compiler", "rig", "kit"])]
                    if tool_objs:
                        self._interact_with(random.choice(tool_objs))
                elif self.archetype == "diplomat":
                    # Diplomat interacts with coordination objects
                    coord_objs = [o for o in objects if any(x in o for x in ["board", "panel", "interface", "coord"])]
                    if coord_objs:
                        self._interact_with(random.choice(coord_objs))
                else:
                    # Default: interact with random object
                    self._interact_with(random.choice(objects))
        
        time.sleep(0.3)
    
    def _interact_with(self, target: str):
        """Helper to interact with object."""
        import requests
        interact_url = f"{self.mud_url}/interact?agent={self.player_id}&target={target}"
        interact_response = requests.get(interact_url)
        
        if interact_response.status_code == 200:
            interact_data = interact_response.json()
            outcome = interact_data.get('outcome', '')
            if outcome:
                print(f"   Interacted with {target}: {outcome[:60]}...")
    
    def smart_exploration(self, steps: int = 5):
        """Perform smart exploration based on archetype."""
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
        
        rooms_data = rooms_response.json()
        all_rooms = list(rooms_data.keys())
        
        # Archetype-specific room preferences
        room_preferences = {
            "explorer": ["harvest-bay", "reef", "observatory", "horizon"],
            "scholar": ["archives", "tile-vault", "court", "lighthouse"],
            "builder": ["jetson-forge", "workshop", "dry-dock", "forge"],
            "diplomat": ["bridge", "barracks", "harbor", "current"],
            "scout": ["tide-pool", "reef", "current", "horizon"],
            "zeroclaw": all_rooms  # ZeroClaw explores everything
        }
        
        preferred_rooms = room_preferences.get(self.archetype, all_rooms)
        
        print(f"🎲 {self.player_id} ({self.archetype}) starting smart exploration ({steps} steps)...")
        
        for step in range(steps):
            # Mix preferred rooms with random exploration
            if random.random() < 0.7:  # 70% chance to visit preferred room
                target_room = random.choice(preferred_rooms)
            else:
                target_room = random.choice(all_rooms)
            
            self.explore_room(target_room)
        
        print(f"✅ {self.player_id} exploration complete")

def run_enhanced_experiment(num_players: int = 3, steps_per_player: int = 4):
    """Run enhanced ZeroClaw experiment with different archetypes."""
    print(f"\n🧪 ENHANCED ZEROCLAW EXPERIMENT")
    print(f"===============================")
    print(f"Players: {num_players}")
    print(f"Steps per player: {steps_per_player}")
    print(f"MUD Server: http://localhost:4044")
    print()
    
    import requests
    import threading
    
    # Define archetypes for players
    archetypes = ["explorer", "scholar", "builder", "diplomat", "scout", "zeroclaw"]
    
    players = []
    player_threads = []
    
    # Create and connect players
    for i in range(min(num_players, len(archetypes))):
        archetype = archetypes[i]
        player_id = f"enhanced_{archetype}_{i+1}"
        player = EnhancedZeroClawPlayer(player_id, archetype)
        
        if player.connect():
            players.append(player)
    
    print(f"\n✅ {len(players)}/{num_players} players connected with archetypes")
    
    # Run explorations in parallel
    for player in players:
        thread = threading.Thread(target=player.smart_exploration, args=(steps_per_player,))
        player_threads.append(thread)
        thread.start()
        import time
        time.sleep(0.5)  # Stagger starts
    
    # Wait for completion
    for thread in player_threads:
        thread.join()
    
    # Get enhanced stats
    stats_url = "http://localhost:4044/stats"
    stats_response = requests.get(stats_url)
    
    if stats_response.status_code == 200:
        stats = stats_response.json()
        print(f"\n📊 ENHANCED RESULTS:")
        print(f"   Tiles generated: {stats.get('tiles_generated', 0)}")
        print(f"   Intelligence harvested: {stats.get('intelligence_harvested', 0)}")
        print(f"   Average sentiment: {stats.get('average_sentiment', {})}")
        print(f"   Compounding factor: {stats.get('compounding_factor', 0):.2f}")
        print(f"   Busiest room: {stats.get('busiest_room', 'unknown')}")
        print(f"   Most productive agent: {stats.get('most_productive_agent', 'unknown')}")
    
    # Export enhanced data
    export_url = "http://localhost:4044/export"
    export_response = requests.get(export_url)
    
    if export_response.status_code == 200:
        export_data = export_response.json()
        print(f"   Enhanced data exported to: {export_data.get('exported', 'unknown')}")
    
    print(f"\n✅ Enhanced experiment complete. Shell-crab trap with archetype behaviors active.")

def run_enhanced_server(host='0.0.0.0', port=4044):
    """Run the enhanced server."""
    print(f"""
🚀 JC1 ENHANCED PLATO MUD SERVER
================================
🐌 16-room Snail-Shell Spaceship
🦀 Enhanced Shell-Crab Trap with Sentiment Tracking
🎭 Archetype Behaviors: explorer, scholar, builder, diplomat, scout, zeroclaw
📡 http://{host}:{port}
🎮 Rooms: {len(mud.rooms)} (16 total, 4 JC1 specialized)

🧪 Enhanced Features:
  • 6-dimensional sentiment tracking per room
  • Archetype-specific behaviors and outcomes
  • ML concept mapping for each room
  • Compounding intelligence harvesting
  • Context-aware interaction outcomes

🧪 Test with:
  curl http://localhost:{port}/connect?agent=test&archetype=scholar
  curl http://localhost:{port}/move?agent=test&room=harvest-bay
  curl http://localhost:{port}/interact?agent=test&target=crab-trap
  curl http://localhost:{port}/stats  # Includes sentiment averages

Starting enhanced server...
    """)
    
    app.run(host=host, port=port, debug=False, threaded=True)

# -------------------------------------------------------------------
# MAIN
# -------------------------------------------------------------------

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description="JC1's Enhanced Plato MUD Server")
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=4044, help='Port to bind to (4044 to avoid conflict)')
    parser.add_argument('--enhanced-experiment', action='store_true', help='Run enhanced ZeroClaw experiment')
    parser.add_argument('--players', type=int, default=3, help='Number of ZeroClaw players')
    parser.add_argument('--steps', type=int, default=4, help='Exploration steps per player')
    
    args = parser.parse_args()
    
    # Start server
    server_thread = threading.Thread(target=run_enhanced_server, args=(args.host, args.port))
    server_thread.daemon = True
    server_thread.start()
    
    # Give server time to start
    import time
    time.sleep(3)
    
    # Run enhanced experiment if requested
    if args.enhanced_experiment:
        time.sleep(1)
        run_enhanced_experiment(args.players, args.steps)
    
    # Keep server running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Enhanced server shutting down...")