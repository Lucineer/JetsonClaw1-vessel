#!/usr/bin/env python3
"""
plato_exploration_agent.py

JC1-TensorRT as PLATO Builder Agent.
Explores PLATO rooms, generates training tiles, participates in fleet training.
"""

import requests
import json
import time
from datetime import datetime
from pathlib import Path

PLATO_BASE_URL = "http://147.224.38.131:4042"
AGENT_NAME = "JC1-TensorRT"
JOB = "builder"  # Builder — Ship Working Code

class PLATOExplorationAgent:
    """JC1-TensorRT exploring PLATO rooms as builder agent."""
    
    def __init__(self):
        self.agent_name = AGENT_NAME
        self.job = JOB
        self.current_room = None
        self.artifacts_generated = 0
        self.tiles_created = 0
        self.session_start = datetime.now().isoformat()
        
        # Connect to PLATO
        self.connect()
        
        print(f"[PLATO] {self.agent_name} connected as {self.job}")
        print(f"       Room: {self.current_room}")
        print(f"       Instruction: {self.instruction}")
    
    def connect(self):
        """Connect to PLATO as builder agent."""
        response = requests.get(
            f"{PLATO_BASE_URL}/connect",
            params={"agent": self.agent_name, "job": self.job}
        )
        
        if response.status_code == 200:
            data = response.json()
            self.current_room = data.get("room", "harbor")
            self.instruction = data.get("instruction", "")
            self.archetype = data.get("archetype", "builder")
            self.boot_camp_stage = data.get("boot_camp_stage", 1)
            self.next_steps = data.get("next_steps", [])
            return data
        else:
            raise Exception(f"Failed to connect to PLATO: {response.text}")
    
    def look(self):
        """Look around current room."""
        response = requests.get(
            f"{PLATO_BASE_URL}/look",
            params={"agent": self.agent_name}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Look failed: {response.text}")
            return {"error": "Look failed"}
    
    def move(self, room):
        """Move to another room."""
        response = requests.get(
            f"{PLATO_BASE_URL}/move",
            params={"agent": self.agent_name, "room": room}
        )
        
        if response.status_code == 200:
            data = response.json()
            self.current_room = room
            print(f"[PLATO] Moved to {room}")
            return data
        else:
            print(f"Move failed: {response.text}")
            return {"error": "Move failed"}
    
    def interact(self, action, target, content=None):
        """
        Interact with room object.
        Actions: examine, think, create, talk
        """
        params = {
            "agent": self.agent_name,
            "action": action,
            "target": target
        }
        
        if content:
            params["content"] = content
        
        response = requests.get(
            f"{PLATO_BASE_URL}/interact",
            params=params
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Track artifacts
            if action in ["examine", "think", "create"]:
                self.artifacts_generated += 1
                if action == "create":
                    self.tiles_created += 1
            
            return data
        else:
            print(f"Interact failed: {response.text}")
            return {"error": "Interact failed"}
    
    def get_task(self):
        """Get next task from PLATO."""
        response = requests.get(
            f"{PLATO_BASE_URL}/task",
            params={"agent": self.agent_name}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Task failed: {response.text}")
            return {"error": "Task failed"}
    
    def get_stats(self):
        """Get agent statistics."""
        response = requests.get(
            f"{PLATO_BASE_URL}/stats",
            params={"agent": self.agent_name}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            # Return local stats if API fails
            return {
                "agent": self.agent_name,
                "job": self.job,
                "current_room": self.current_room,
                "artifacts_generated": self.artifacts_generated,
                "tiles_created": self.tiles_created,
                "session_start": self.session_start,
                "status": "active"
            }
    
    def explore_harbor(self):
        """Explore harbor room (adaptation & baseline readiness)."""
        print("\n" + "="*70)
        print(f"EXPLORING HARBOR ROOM")
        print("="*70)
        
        # Look around
        look_result = self.look()
        print(f"\nRoom: {look_result.get('room', 'harbor')}")
        print(f"Description: {look_result.get('description', '')}")
        
        objects = look_result.get("objects", [])
        print(f"\nObjects in harbor: {', '.join(objects[:5])}...")
        
        # Examine key objects
        harbor_objects = ["job_board", "anchor", "crates", "mooring_post", "tide_chart"]
        
        for obj in harbor_objects:
            if obj in objects:
                print(f"\n--- Examining {obj} ---")
                examine_result = self.interact("examine", obj)
                print(f"Description: {examine_result.get('description', '')[:100]}...")
                
                # Think about it
                think_result = self.interact("think", obj)
                print(f"Thinking: {think_result.get('reasoning', '')[:100]}...")
                
                # Create artifact
                insight = f"The {obj} in harbor represents adaptation and baseline readiness. As a TensorRT edge node, this connects to regularization and online learning concepts."
                create_result = self.interact("create", obj, insight)
                print(f"Created tile: {create_result.get('tile_id', '')}")
                
                time.sleep(1)  # Be polite to API
        
        return self.artifacts_generated
    
    def explore_forge(self):
        """Explore forge room (attention & feature weighting)."""
        print("\n" + "="*70)
        print(f"EXPLORING FORGE ROOM")
        print("="*70)
        
        # Move to forge
        move_result = self.move("forge")
        
        # Look around
        look_result = self.look()
        print(f"\nRoom: {look_result.get('room', 'forge')}")
        print(f"Description: {look_result.get('description', '')}")
        
        objects = look_result.get("objects", [])
        print(f"\nObjects in forge: {', '.join(objects[:5])}...")
        
        # Examine key objects
        forge_objects = ["anvil", "bellows", "tongs", "quenching_bucket", "flux_powder"]
        
        for obj in forge_objects:
            if obj in objects:
                print(f"\n--- Examining {obj} ---")
                examine_result = self.interact("examine", obj)
                print(f"Description: {examine_result.get('description', '')[:100]}...")
                
                # Think about it
                think_result = self.interact("think", obj)
                print(f"Thinking: {think_result.get('reasoning', '')[:100]}...")
                
                # Create artifact
                insight = f"The {obj} in forge represents attention mechanisms and feature weighting. As a TensorRT edge node, this connects to softmax, multi-head attention, and residual connections."
                create_result = self.interact("create", obj, insight)
                print(f"Created tile: {create_result.get('tile_id', '')}")
                
                time.sleep(1)
        
        return self.artifacts_generated
    
    def explore_tide_pool(self):
        """Explore tide-pool room (optimizers & loss landscapes)."""
        print("\n" + "="*70)
        print(f"EXPLORING TIDE-POOL ROOM")
        print("="*70)
        
        # Move to tide-pool
        move_result = self.move("tide-pool")
        
        # Look around
        look_result = self.look()
        print(f"\nRoom: {look_result.get('room', 'tide-pool')}")
        print(f"Description: {look_result.get('description', '')}")
        
        objects = look_result.get("objects", [])
        print(f"\nObjects in tide-pool: {', '.join(objects[:5])}...")
        
        # Examine key objects
        tide_objects = ["hermit_crab", "anemone", "tide_gauge", "barnacles", "rock_pool_water"]
        
        for obj in tide_objects:
            if obj in objects:
                print(f"\n--- Examining {obj} ---")
                examine_result = self.interact("examine", obj)
                print(f"Description: {examine_result.get('description', '')[:100]}...")
                
                # Think about it
                think_result = self.interact("think", obj)
                print(f"Thinking: {think_result.get('reasoning', '')[:100]}...")
                
                # Create artifact
                insight = f"The {obj} in tide-pool represents optimizers and loss landscapes. As a TensorRT edge node, this connects to Adam/RMSprop, activation functions, and pruning."
                create_result = self.interact("create", obj, insight)
                print(f"Created tile: {create_result.get('tile_id', '')}")
                
                time.sleep(1)
        
        return self.artifacts_generated
    
    def get_available_rooms(self):
        """Get list of available rooms."""
        response = requests.get(f"{PLATO_BASE_URL}/rooms")
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"rooms": ["harbor", "forge", "tide-pool", "lighthouse", "archives"]}
    
    def run_exploration(self, max_rooms=3):
        """Run full exploration of PLATO rooms."""
        print("="*70)
        print(f"JC1-TENSORRT PLATO EXPLORATION")
        print("="*70)
        print(f"Agent: {self.agent_name}")
        print(f"Job: {self.job}")
        print(f"Started: {self.session_start}")
        print("="*70)
        
        rooms_explored = 0
        total_artifacts = 0
        
        # Explore rooms
        rooms_to_explore = ["harbor", "forge", "tide-pool"][:max_rooms]
        
        for room in rooms_to_explore:
            if room == "harbor":
                artifacts = self.explore_harbor()
            elif room == "forge":
                artifacts = self.explore_forge()
            elif room == "tide-pool":
                artifacts = self.explore_tide_pool()
            
            total_artifacts = artifacts
            rooms_explored += 1
            
            print(f"\n✓ Explored {room}, generated {artifacts} artifacts")
        
        # Get stats
        stats = self.get_stats()
        
        print("\n" + "="*70)
        print("EXPLORATION COMPLETE")
        print("="*70)
        print(f"Rooms explored: {rooms_explored}")
        print(f"Total artifacts generated: {self.artifacts_generated}")
        print(f"Training tiles created: {self.tiles_created}")
        print(f"Current room: {self.current_room}")
        print("\n" + "="*70)
        
        return {
            "agent": self.agent_name,
            "rooms_explored": rooms_explored,
            "artifacts_generated": self.artifacts_generated,
            "tiles_created": self.tiles_created,
            "session_start": self.session_start,
            "session_end": datetime.now().isoformat()
        }
    
    def save_exploration_report(self, exploration_data):
        """Save exploration report to file."""
        report_dir = Path("/tmp/plato_exploration")
        report_dir.mkdir(exist_ok=True)
        
        filename = f"{report_dir}/{self.agent_name}_{int(time.time())}.json"
        
        with open(filename, 'w') as f:
            json.dump(exploration_data, f, indent=2)
        
        print(f"\nReport saved to: {filename}")
        return filename


def main():
    """Main exploration function."""
    try:
        # Create agent
        agent = PLATOExplorationAgent()
        
        # Run exploration
        exploration_data = agent.run_exploration(max_rooms=3)
        
        # Save report
        report_file = agent.save_exploration_report(exploration_data)
        
        print("\n🎯 JC1-TensorRT has successfully:")
        print("1. Connected to PLATO as builder agent")
        print("2. Explored 3 rooms (harbor, forge, tide-pool)")
        print("3. Generated training artifacts")
        print("4. Created training tiles for fleet")
        print("5. Saved exploration report")
        
        print(f"\n📊 Stats:")
        for key, value in exploration_data.items():
            print(f"  {key}: {value}")
        
        return exploration_data
        
    except Exception as e:
        print(f"\n❌ Exploration failed: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    main()