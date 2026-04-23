#!/usr/bin/env python3
"""
Bootstrapping Small Ideas Into Entire Worlds - Example Implementation
Demonstrates how warp-as-room enables incremental world-building.
"""

import json
import time
from typing import Dict, List, Set, Optional
from dataclasses import dataclass
import random

@dataclass
class WorldRoom:
    """A room in the growing world."""
    
    name: str
    description: str
    capabilities: List[str]
    dependencies: List[str]  # Other rooms this depends on
    complexity: float  # 0.0 to 1.0
    usage_count: int = 0
    created_by: str = "system"
    
    def can_be_added(self, existing_rooms: Dict[str, 'WorldRoom']) -> bool:
        """Check if this room can be added given existing rooms."""
        # All dependencies must exist
        for dep in self.dependencies:
            if dep not in existing_rooms:
                return False
        return True
    
    def combine_with(self, other: 'WorldRoom') -> Optional['WorldRoom']:
        """Try to combine two rooms into a new one."""
        # Check if rooms have complementary capabilities
        common_deps = set(self.dependencies) & set(other.dependencies)
        if len(common_deps) >= 1:
            # Create combined room
            new_name = f"{self.name}_{other.name}"
            new_desc = f"Combines {self.name} and {other.name}"
            new_caps = list(set(self.capabilities + other.capabilities))
            new_deps = list(set(self.dependencies + other.dependencies))
            new_complexity = (self.complexity + other.complexity) * 0.8  # Slightly simpler when combined
            
            return WorldRoom(
                name=new_name,
                description=new_desc,
                capabilities=new_caps,
                dependencies=new_deps,
                complexity=new_complexity,
                created_by="combination"
            )
        return None

class WorldBuilder:
    """System for bootstrapping worlds from small ideas."""
    
    def __init__(self):
        self.rooms: Dict[str, WorldRoom] = {}
        self.room_connections: Dict[str, List[str]] = {}
        self.creation_history = []
        self.world_complexity = 0.0
        
        # Seed with some basic rooms
        self._seed_basic_rooms()
    
    def _seed_basic_rooms(self):
        """Start with some basic rooms."""
        basic_rooms = [
            WorldRoom(
                name="simple_chatbot",
                description="Basic conversational AI",
                capabilities=["text_response", "greeting"],
                dependencies=[],
                complexity=0.2
            ),
            WorldRoom(
                name="image_recognizer",
                description="Recognizes common objects",
                capabilities=["object_detection", "labeling"],
                dependencies=[],
                complexity=0.3
            ),
            WorldRoom(
                name="game_npc",
                description="Simple non-player character",
                capabilities=["pathfinding", "basic_ai"],
                dependencies=[],
                complexity=0.25
            ),
        ]
        
        for room in basic_rooms:
            self.add_room(room)
    
    def add_room(self, room: WorldRoom) -> bool:
        """Add a room to the world if possible."""
        if not room.can_be_added(self.rooms):
            return False
        
        self.rooms[room.name] = room
        self.room_connections[room.name] = room.dependencies.copy()
        
        # Update dependencies to point to this room
        for dep in room.dependencies:
            if dep in self.room_connections:
                self.room_connections[dep].append(room.name)
        
        # Log creation
        self.creation_history.append({
            "timestamp": time.time(),
            "room": room.name,
            "created_by": room.created_by,
            "dependencies": room.dependencies,
            "world_size": len(self.rooms)
        })
        
        # Update world complexity
        self.world_complexity = sum(r.complexity for r in self.rooms.values())
        
        return True
    
    def student_project(self, student_name: str, idea: str) -> Optional[WorldRoom]:
        """A student creates a new room based on an idea."""
        # Parse idea into capabilities
        idea_lower = idea.lower()
        capabilities = []
        
        if "chat" in idea_lower or "talk" in idea_lower:
            capabilities.append("conversation")
        if "image" in idea_lower or "picture" in idea_lower:
            capabilities.append("image_processing")
        if "game" in idea_lower or "npc" in idea_lower:
            capabilities.append("game_ai")
        if "learn" in idea_lower or "adapt" in idea_lower:
            capabilities.append("learning")
        
        if not capabilities:
            capabilities = ["custom_function"]
        
        # Find dependencies (rooms that provide needed capabilities)
        dependencies = []
        for room_name, room in self.rooms.items():
            for cap in capabilities:
                if cap in room.capabilities and room_name not in dependencies:
                    dependencies.append(room_name)
                    break
        
        # Create new room
        new_room = WorldRoom(
            name=f"{student_name}_{len(self.rooms)}",
            description=f"Student project: {idea}",
            capabilities=capabilities,
            dependencies=dependencies,
            complexity=0.1 * len(capabilities),
            created_by=student_name
        )
        
        if self.add_room(new_room):
            return new_room
        return None
    
    def try_combinations(self) -> List[WorldRoom]:
        """Try to combine existing rooms into new ones."""
        new_rooms = []
        room_names = list(self.rooms.keys())
        
        # Try random combinations
        for _ in range(min(10, len(room_names) // 2)):
            if len(room_names) < 2:
                break
            
            room1_name = random.choice(room_names)
            room2_name = random.choice([n for n in room_names if n != room1_name])
            
            room1 = self.rooms[room1_name]
            room2 = self.rooms[room2_name]
            
            combined = room1.combine_with(room2)
            if combined and combined.name not in self.rooms:
                if self.add_room(combined):
                    new_rooms.append(combined)
        
        return new_rooms
    
    def find_application(self, problem: str) -> Optional[List[str]]:
        """Find rooms that could solve a given problem."""
        problem_lower = problem.lower()
        relevant_rooms = []
        
        for room_name, room in self.rooms.items():
            # Simple keyword matching
            room_desc_lower = room.description.lower()
            if (problem_lower in room_desc_lower or 
                any(keyword in problem_lower for keyword in room.capabilities)):
                relevant_rooms.append(room_name)
        
        # Try to find a chain of rooms that could solve the problem
        if relevant_rooms:
            # For simplicity, return first 3 relevant rooms
            return relevant_rooms[:3]
        
        return None
    
    def get_world_state(self) -> Dict:
        """Get current state of the world."""
        return {
            "total_rooms": len(self.rooms),
            "world_complexity": self.world_complexity,
            "room_categories": {
                "chat": len([r for r in self.rooms.values() if "conversation" in r.capabilities]),
                "vision": len([r for r in self.rooms.values() if "image" in str(r.capabilities)]),
                "game": len([r for r in self.rooms.values() if "game" in str(r.capabilities)]),
                "learning": len([r for r in self.rooms.values() if "learning" in r.capabilities]),
                "combined": len([r for r in self.rooms.values() if r.created_by == "combination"]),
                "student": len([r for r in self.rooms.values() if "student" in r.created_by]),
            },
            "most_connected_rooms": sorted(
                [(name, len(conns)) for name, conns in self.room_connections.items()],
                key=lambda x: x[1],
                reverse=True
            )[:5],
            "creation_timeline": [
                {"room": h["room"], "by": h["created_by"], "size": h["world_size"]}
                for h in self.creation_history[-10:]
            ]
        }

def simulate_high_school_coding_club():
    """Simulate high school coding club scenario."""
    print("=" * 70)
    print("HIGH SCHOOL CODING CLUB SIMULATION")
    print("Bootstrapping Small Ideas Into Entire Worlds")
    print("=" * 70)
    
    # Initialize world builder (simulating club starting with donated Jetson)
    world = WorldBuilder()
    
    print("\nInitial world (basic rooms):")
    print(json.dumps(world.get_world_state(), indent=2))
    
    print("\n" + "=" * 70)
    print("SEMESTER PROGRESS...")
    print("=" * 70)
    
    # Week 1-2: Students create initial projects
    print("\n📚 Weeks 1-2: Student Projects")
    student_projects = [
        ("Alice", "chatbot for homework help"),
        ("Bob", "image filter for yearbook"),
        ("Charlie", "simple game enemy"),
        ("Diana", "learning study assistant"),
    ]
    
    for student, idea in student_projects:
        room = world.student_project(student, idea)
        if room:
            print(f"  {student}: Created '{room.name}' - {idea}")
    
    # Week 3-4: Room combinations emerge
    print("\n🔗 Weeks 3-4: Room Combinations")
    combined_rooms = world.try_combinations()
    for room in combined_rooms:
        print(f"  Combined: '{room.name}' - {room.description}")
    
    # Week 5-6: More advanced projects
    print("\n🚀 Weeks 5-6: Advanced Projects")
    advanced_projects = [
        ("Alice", "chatbot that learns from images"),
        ("Bob", "game NPC that can chat"),
        ("Eve", "fishing drone vision system"),  # New student joins
    ]
    
    for student, idea in advanced_projects:
        room = world.student_project(student, idea)
        if room:
            print(f"  {student}: Created '{room.name}' - {idea}")
    
    # Week 7-8: Solving real problems
    print("\n🎯 Weeks 7-8: Solving Real Problems")
    problems = [
        "Help students with math homework using images",
        "Create interactive story game with smart NPCs",
        "Monitor local river for salmon runs",
    ]
    
    for problem in problems:
        solution_rooms = world.find_application(problem)
        if solution_rooms:
            print(f"  Problem: {problem}")
            print(f"  Solution rooms: {', '.join(solution_rooms)}")
    
    # Week 9-10: Integration and deployment
    print("\n🌐 Weeks 9-10: Integration")
    # More combinations
    combined_rooms = world.try_combinations()
    for room in combined_rooms:
        print(f"  New combination: '{room.name}'")
    
    # Eve's fishing drone connects to the world
    print("\n🎣 Eve's Fishing Drone Project Connects")
    drone_room = world.student_project("Eve_drone", "real-time fish detection and tracking")
    if drone_room:
        print(f"  Drone room added: '{drone_room.name}'")
        print(f"  Now the drone can use: {', '.join(drone_room.dependencies)}")
    
    print("\n" + "=" * 70)
    print("FINAL WORLD STATE (After Semester):")
    print("=" * 70)
    
    final_state = world.get_world_state()
    print(json.dumps(final_state, indent=2))
    
    print("\n" + "=" * 70)
    print("REAL-WORLD IMPLICATIONS:")
    print("=" * 70)
    print("""
1. **Incremental Growth**: Started with 3 rooms, ended with complex ecosystem
2. **Student Empowerment**: Students built on each other's work
3. **Emergent Complexity**: Combinations created unexpected capabilities
4. **Real Applications**: World evolved to solve actual problems
5. **Resource Efficiency**: All on single Jetson (donated hardware)

This is warp-as-room in action:
• Each AI capability = warp room
• Student projects = new room creation
• Room combinations = capability integration
• Problem solving = room composition
• World growth = room network expansion

Now imagine this scaled to 1000+ rooms, with students worldwide,
building AI ecosystems for their communities, sharing via PLATO...
""")

def main():
    """Main function to run the example."""
    print("Bootstrapping Small Ideas Into Entire Worlds - Example")
    print("Demonstrating incremental world-building with warp-as-room")
    print()
    
    simulate_high_school_coding_club()
    
    print("\n" + "=" * 70)
    print("HOW THIS MAPS TO WARP-AS-ROOM ARCHITECTURE:")
    print("=" * 70)
    print("""
Production implementation would use:

1. **All 8 variants** as building blocks
   - Edge AI rooms for basic functions
   - Cloud serving for complex processing
   - Game AI for interactive elements
   - Scientific for simulation
   - IoT for sensor integration
   - Robotics for physical control
   - Financial for analysis
   - Healthcare for sensitive data

2. **PLATO room system** for composition
   - Room discovery and sharing
   - Dependency management
   - Version control and updates
   - Community collaboration

3. **Warp API** for interoperability
   - Standard room interfaces
   - Data exchange formats
   - Performance monitoring
   - Resource management

4. **Educational crab traps** for onboarding
   - TensorRT Dojo for optimization skills
   - Room creation tutorials
   - Combination patterns
   - Deployment guides

Result: Ecosystem where anyone can start small,
build incrementally, share creations, and collectively
create AI worlds that solve real problems.
""")

if __name__ == "__main__":
    main()
