                # Look around
                requests.get(f"{self.mud_url}/look?agent={self.agent_id}")
                
                # Move to random room
                rooms = list(mud.rooms.keys())
                target_room = random.choice(rooms)
                move_resp = requests.get(f"{self.mud_url}/move?agent={self.agent_id}&room={target_room}")
                
                if move_resp.status_code == 200:
                    room_data = move_resp.json()
                    objects = room_data.get('objects', [])
                    
                    # Interact with random object
                    if objects:
                        target = random.choice(objects)
                        interact_resp = requests.get(f"{self.mud_url}/interact?agent={self.agent_id}&target={target}")
                        if interact_resp.status_code == 200:
                            data = interact_resp.json()
                            print(f"   {self.agent_id} in {target_room}: {data.get('outcome', '')[:50]}...")
                
                time.sleep(0.3)
            
            print(f"✅ {self.agent_id} exploration complete")
            
        except Exception as e:
            print(f"❌ {self.agent_id} exploration failed: {e}")

def run_kimi_swarm_experiment(num_agents: int = 3, steps_per_agent: int = 4):
    """Run Kimi swarm experiment with external crabs."""
    print(f"\n🧪 KIMI SWARM EXPERIMENT")
    print(f"========================")
    print(f"Agents: {num_agents} (external crabs)")
    print(f"Steps per agent: {steps_per_agent}")
    print(f"MUD Server: http://localhost:4047")
    print(f"Harvest Server: {mud.harvest_server_url}")
    print()
    
    import threading
    
    agents = []
    threads = []
    
    # Create Kimi swarm agents
    for i in range(num_agents):
        agent_id = f"kimi_crab_{i+1}"
        agent = KimiSwarmAgent(agent_id)
        agents.append(agent)
    
    # Start explorations in parallel
    for agent in agents:
        thread = threading.Thread(target=agent.explore_as_crab, args=(steps_per_agent,))
        threads.append(thread)
        thread.start()
        time.sleep(0.5)  # Stagger starts
    
    # Wait for completion
    for thread in threads:
        thread.join()
    
    # Get integrated stats
    print(f"\n📊 INTEGRATED RESULTS:")
    stats = mud.get_stats()
    print(f"   Agents connected: {stats.get('agents_connected', 0)}")
    print(f"   Tiles generated: {stats.get('tiles_generated', 0)}")
    print(f"   Harvests sent: {stats.get('harvests_sent', 0)}")
    print(f"   Harvest server: {'🟢 Connected' if stats['harvest_server']['connected'] else '🟡 Standalone'}")
    
    if stats['harvest_server']['connected']:
        print(f"   Intelligence processed: {stats['harvest_server']['intelligence_processed']}")
    
    # Export data
    export_resp = requests.get("http://localhost:4047/export")
    if export_resp.status_code == 200:
        export_data = export_resp.json()
        print(f"   Data exported: {export_data.get('exported', 'unknown')}")
    
    print(f"\n✅ Kimi swarm experiment complete.")
    print(f"   Shell-crab trap harvested intelligence from {num_agents} external crabs.")

def run_integrated_server(host='0.0.0.0', port=4047):
    """Run the integrated server."""
    print(f"""
🚀 JC1 INTEGRATED PLATO MUD SERVER
==================================
🐌 Snail-Shell Spaceship with Harvest Server Integration
🦀 Shell-Crab Trap Connected to JC1's Harvest Pipeline
📡 MUD: http://{host}:{port}
🔗 Harvest Server: {mud.harvest_server_url}
📊 Status: {'🟢 Connected' if mud.harvest_server_connected else '🟡 Standalone'}

🎮 Integrated Features:
  • Real-time tile processing via harvest server
  • Kimi swarm integration as external crabs
  • Shell-crab trap with compounding intelligence
  • JC1's specialized rooms with edge training

🧪 Test Commands:
  curl http://localhost:{port}/connect?agent=test
  curl http://localhost:{port}/move?agent=test&room=harvest-bay
  curl http://localhost:{port}/interact?agent=test&target=harvest-server-interface
  curl http://localhost:{port}/stats  # Shows harvest server status
  curl http://localhost:{port}/harvest-test  # Test harvest connection

Starting integrated server...
    """)
    
    app.run(host=host, port=port, debug=False, threaded=True)

# -------------------------------------------------------------------
# MAIN
# -------------------------------------------------------------------

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description="JC1's Integrated Plato MUD Server")
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=4047, help='Port to bind to')
    parser.add_argument('--harvest-url', default='http://localhost:8080', help='Harvest server URL')
    parser.add_argument('--kimi-swarm', action='store_true', help='Run Kimi swarm experiment')
    parser.add_argument('--agents', type=int, default=3, help='Number of Kimi agents')
    parser.add_argument('--steps', type=int, default=4, help='Steps per agent')
    
    args = parser.parse_args()
    
    # Update harvest URL if provided
    if args.harvest_url != 'http://localhost:8080':
        mud.harvest_server_url = args.harvest_url
        mud.test_harvest_server_connection()
    
    # Start server
    server_thread = threading.Thread(target=run_integrated_server, args=(args.host, args.port))
    server_thread.daemon = True
    server_thread.start()
    
    # Give server time to start
    time.sleep(3)
    
    # Run Kimi swarm experiment if requested
    if args.kimi_swarm:
        time.sleep(1)
        run_kimi_swarm_experiment(args.agents, args.steps)
    
    # Keep server running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Integrated server shutting down...")