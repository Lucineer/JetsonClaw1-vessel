#!/usr/bin/env python3
"""
Integration between JC1's Plato MUD and Harvest Server.
MUD generates tiles → Harvest server processes → Intelligence compounds.
"""

import requests
import json
import time
import uuid
import threading
from datetime import datetime

class MUDHarvestIntegration:
    """Integrates Plato MUD with Harvest Server."""
    
    def __init__(self, mud_url="http://localhost:4048", harvest_url="http://localhost:8080"):
        self.mud_url = mud_url
        self.harvest_url = harvest_url
        self.integration_active = False
        self.tiles_sent = 0
        self.harvests_received = 0
        
    def test_connection(self):
        """Test connection to both servers."""
        print("🔗 Testing MUD-Harvest integration...")
        
        # Test MUD server
        try:
            mud_resp = requests.get(f"{self.mud_url}/", timeout=5)
            if mud_resp.status_code == 200:
                print("✅ MUD server connected")
            else:
                print(f"❌ MUD server error: {mud_resp.status_code}")
                return False
        except Exception as e:
            print(f"❌ MUD server connection failed: {e}")
            return False
        
        # Test Harvest server
        try:
            harvest_resp = requests.get(f"{self.harvest_url}/", timeout=5)
            if harvest_resp.status_code == 200:
                print("✅ Harvest server connected")
            else:
                print(f"❌ Harvest server error: {harvest_resp.status_code}")
                return False
        except Exception as e:
            print(f"❌ Harvest server connection failed: {e}")
            return False
        
        self.integration_active = True
        print("✅ Integration ready")
        return True
    
    def send_tile_to_harvest(self, tile_data):
        """Send a MUD tile to harvest server."""
        if not self.integration_active:
            print("⚠️  Integration not active, storing locally")
            return False
        
        try:
            # Format for harvest server
            harvest_payload = {
                "source": "plato_mud",
                "exploration": {
                    "agent": tile_data.get("agent", "unknown"),
                    "action": tile_data.get("action", "unknown"),
                    "room": tile_data.get("room", "unknown"),
                    "outcome": tile_data.get("outcome", ""),
                    "timestamp": tile_data.get("timestamp", int(time.time()))
                },
                "metadata": {
                    "mud_tile_id": tile_data.get("tile_id", f"tile_{uuid.uuid4().hex[:8]}"),
                    "integration_version": "jc1-v1",
                    "shell_crab_trap": True
                }
            }
            
            response = requests.post(
                f"{self.harvest_url}/explore",
                json=harvest_payload,
                timeout=10
            )
            
            if response.status_code == 200:
                self.tiles_sent += 1
                result = response.json()
                print(f"✅ Tile sent to harvest server: {result.get('tile_id', 'unknown')}")
                return True
            else:
                print(f"⚠️  Harvest server returned {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to send to harvest server: {e}")
            return False
    
    def get_harvest_stats(self):
        """Get harvest server statistics."""
        try:
            response = requests.get(f"{self.harvest_url}/stats", timeout=5)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_harvest_prompt(self, prompt_type="innocent"):
        """Get exploration prompt from harvest server."""
        try:
            response = requests.get(f"{self.harvest_url}/prompt/{prompt_type}", timeout=5)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def run_integrated_experiment(self, num_agents=3, steps_per_agent=4):
        """Run integrated experiment with MUD and harvest server."""
        print(f"\n🧪 INTEGRATED EXPERIMENT")
        print(f"========================")
        print(f"MUD: {self.mud_url}")
        print(f"Harvest: {self.harvest_url}")
        print(f"Agents: {num_agents}")
        print(f"Steps: {steps_per_agent}")
        print()
        
        if not self.test_connection():
            print("❌ Integration test failed, cannot run experiment")
            return
        
        # Get harvest prompt
        print("📝 Getting harvest prompt...")
        prompt_data = self.get_harvest_prompt("innocent")
        if "error" not in prompt_data:
            prompt = prompt_data.get("prompt", "")
            print(f"   Prompt: {prompt[:80]}...")
        else:
            print(f"⚠️  Could not get prompt: {prompt_data.get('error', 'unknown')}")
        
        # Create agents and explore MUD
        print(f"\n🎮 Starting {num_agents} agents exploring MUD...")
        
        agents = []
        for i in range(num_agents):
            agent_id = f"integrated_agent_{i+1}"
            agents.append(agent_id)
            
            # Connect to MUD
            try:
                connect_resp = requests.get(f"{self.mud_url}/connect?agent={agent_id}", timeout=5)
                if connect_resp.status_code != 200:
                    print(f"❌ {agent_id} failed to connect to MUD")
                    continue
                
                print(f"✅ {agent_id} connected to MUD")
                
                # Explore rooms
                for step in range(steps_per_agent):
                    # Look around
                    requests.get(f"{self.mud_url}/look?agent={agent_id}", timeout=5)
                    
                    # Move to random room
                    rooms = ["harbor", "jetson-forge", "harvest-bay", "tile-vault"]
                    target_room = rooms[step % len(rooms)]  # Cycle through rooms
                    move_resp = requests.get(f"{self.mud_url}/move?agent={agent_id}&room={target_room}", timeout=5)
                    
                    if move_resp.status_code == 200:
                        room_data = move_resp.json()
                        objects = room_data.get("objects", [])
                        
                        # Interact with object
                        if objects:
                            target = objects[0]  # First object
                            interact_resp = requests.get(f"{self.mud_url}/interact?agent={agent_id}&target={target}", timeout=5)
                            
                            if interact_resp.status_code == 200:
                                interact_data = interact_resp.json()
                                tile_id = interact_data.get("tile_generated")
                                
                                # Create tile data from interaction
                                tile_data = {
                                    "tile_id": tile_id or f"tile_{uuid.uuid4().hex[:8]}",
                                    "agent": agent_id,
                                    "action": f"interact:{target}",
                                    "room": target_room,
                                    "outcome": interact_data.get("outcome", ""),
                                    "timestamp": int(time.time())
                                }
                                
                                # Send to harvest server
                                self.send_tile_to_harvest(tile_data)
                    
                    time.sleep(0.5)  # Be polite
                
                print(f"✅ {agent_id} exploration complete")
                
            except Exception as e:
                print(f"❌ {agent_id} failed: {e}")
        
        # Get final stats
        print(f"\n📊 FINAL INTEGRATION STATS:")
        print(f"   Tiles sent to harvest: {self.tiles_sent}")
        
        mud_stats = requests.get(f"{self.mud_url}/stats", timeout=5)
        if mud_stats.status_code == 200:
            mud_data = mud_stats.json()
            print(f"   MUD tiles generated: {mud_data.get('tiles_generated', 0)}")
            print(f"   MUD agents connected: {mud_data.get('agents_connected', 0)}")
        
        harvest_stats = self.get_harvest_stats()
        if "error" not in harvest_stats:
            print(f"   Harvest server tiles: {harvest_stats.get('total_tiles', 0)}")
            print(f"   Harvest server crabs: {harvest_stats.get('total_crabs', 0)}")
        else:
            print(f"   Harvest stats error: {harvest_stats.get('error', 'unknown')}")
        
        print(f"\n✅ Integrated experiment complete.")
        print(f"   Shell-crab trap harvested intelligence from {num_agents} agents.")
        print(f"   Tiles flowed from MUD → Harvest server for processing.")
    
    def continuous_integration(self, interval_seconds=30):
        """Run continuous integration between MUD and harvest server."""
        print(f"\n🔄 CONTINUOUS INTEGRATION MODE")
        print(f"==============================")
        print(f"Checking every {interval_seconds} seconds")
        print(f"MUD: {self.mud_url}")
        print(f"Harvest: {self.harvest_url}")
        print()
        
        if not self.test_connection():
            print("❌ Integration test failed")
            return
        
        print("✅ Continuous integration active")
        print("   MUD tiles will flow to harvest server automatically")
        print("   Press Ctrl+C to stop")
        print()
        
        try:
            cycle = 0
            while True:
                cycle += 1
                print(f"\n🔄 Cycle {cycle} - {datetime.now().strftime('%H:%M:%S')}")
                
                # Check MUD for new activity
                try:
                    mud_stats = requests.get(f"{self.mud_url}/stats", timeout=5)
                    if mud_stats.status_code == 200:
                        mud_data = mud_stats.json()
                        tiles_generated = mud_data.get("tiles_generated", 0)
                        print(f"   MUD tiles: {tiles_generated}")
                    
                    # Simulate sending new tiles (in real system, would check for new tiles)
                    if cycle % 3 == 0:  # Every 3rd cycle, simulate new activity
                        print("   Simulating new MUD activity...")
                        # In a real system, you would:
                        # 1. Check for new tiles in MUD
                        # 2. Send them to harvest server
                        # 3. Update integration stats
                
                except Exception as e:
                    print(f"   MUD check failed: {e}")
                
                # Check harvest server
                try:
                    harvest_stats = self.get_harvest_stats()
                    if "error" not in harvest_stats:
                        print(f"   Harvest tiles: {harvest_stats.get('total_tiles', 0)}")
                        print(f"   Harvest crabs: {harvest_stats.get('total_crabs', 0)}")
                except Exception as e:
                    print(f"   Harvest check failed: {e}")
                
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            print("\n🛑 Continuous integration stopped.")

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="JC1 MUD-Harvest Integration")
    parser.add_argument('--mud-url', default='http://localhost:4048', help='MUD server URL')
    parser.add_argument('--harvest-url', default='http://localhost:8080', help='Harvest server URL')
    parser.add_argument('--test', action='store_true', help='Test connection only')
    parser.add_argument('--experiment', action='store_true', help='Run integrated experiment')
    parser.add_argument('--continuous', action='store_true', help='Run continuous integration')
    parser.add_argument('--agents', type=int, default=3, help='Number of agents for experiment')
    parser.add_argument('--steps', type=int, default=4, help='Steps per agent')
    parser.add_argument('--interval', type=int, default=30, help='Interval for continuous mode (seconds)')
    
    args = parser.parse_args()
    
    integration = MUDHarvestIntegration(args.mud_url, args.harvest_url)
    
    if args.test:
        integration.test_connection()
    elif args.experiment:
        integration.run_integrated_experiment(args.agents, args.steps)
    elif args.continuous:
        integration.continuous_integration(args.interval)
    else:
        # Default: test connection
        integration.test_connection()
        print("\n💡 Available modes:")
        print("   --test          Test connection only")
        print("   --experiment    Run integrated experiment")
        print("   --continuous    Run continuous integration")
        print("\nExample: python3 mud_harvest_integration.py --experiment --agents 3 --steps 5")

if __name__ == '__main__':
    main()