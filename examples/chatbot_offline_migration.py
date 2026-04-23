#!/usr/bin/env python3
"""
Chatbot That Slowly Moves Offline - Example Implementation
Demonstrates progressive offloading using warp specialization.
"""

import json
import time
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class ChatbotMode(Enum):
    CLOUD = "cloud"
    HYBRID = "hybrid"
    OFFLINE = "offline"

@dataclass
class ConversationRoom:
    """A warp room specialized for conversation topics."""
    
    topic: str
    weights: List[float]  # Simplified representation
    usage_count: int = 0
    last_used: float = 0
    offline_capable: bool = False
    confidence_threshold: float = 0.7
    size_kb: float = 10.0  # Estimated size
    
    def should_go_offline(self, total_usage: int) -> bool:
        """Determine if this room should be compiled for offline use."""
        usage_frequency = self.usage_count / max(total_usage, 1)
        return (usage_frequency > 0.05 and
                self.size_kb < 50.0 and
                not self.offline_capable)
    
    def compile_for_offline(self) -> 'ConversationRoom':
        """Create offline-optimized version."""
        return ConversationRoom(
            topic=f"{self.topic}_offline",
            weights=[w * 0.9 for w in self.weights],  # Quantized
            usage_count=self.usage_count,
            last_used=self.last_used,
            offline_capable=True,
            confidence_threshold=self.confidence_threshold * 0.9,
            size_kb=self.size_kb * 0.7
        )

class ProgressiveOffloadingChatbot:
    """Chatbot that progressively moves functionality offline."""
    
    def __init__(self, total_storage_mb: float = 100.0):
        self.mode = ChatbotMode.CLOUD
        self.cloud_rooms: Dict[str, ConversationRoom] = {}
        self.offline_rooms: Dict[str, ConversationRoom] = {}
        self.total_storage_mb = total_storage_mb
        self.used_storage_mb = 0.0
        self.conversation_history = []
        self.offline_percentage = 0.0
        self._initialize_common_rooms()
    
    def _initialize_common_rooms(self):
        """Start with some common conversation topics."""
        common_topics = [
            ("greetings", [0.9, 0.1, 0.2]),
            ("weather", [0.1, 0.8, 0.3]),
            ("medication", [0.2, 0.1, 0.9]),
            ("family", [0.3, 0.7, 0.4]),
            ("appointments", [0.4, 0.3, 0.8]),
        ]
        
        for topic, weights in common_topics:
            self.cloud_rooms[topic] = ConversationRoom(
                topic=topic,
                weights=weights,
                usage_count=10,
                last_used=time.time(),
                offline_capable=False
            )
    
    def process_message(self, message: str, user_context: Dict, 
                       connectivity: bool) -> Tuple[str, Dict]:
        """Process a user message."""
        # Update mode
        if not connectivity:
            self.mode = ChatbotMode.OFFLINE
        elif self.offline_percentage > 0.7:
            self.mode = ChatbotMode.HYBRID
        else:
            self.mode = ChatbotMode.CLOUD
        
        # Find relevant rooms
        relevant_rooms = self._find_relevant_rooms(message, user_context)
        
        # Choose response
        if self.mode == ChatbotMode.CLOUD:
            response, metadata = self._cloud_response(message, relevant_rooms)
        elif self.mode == ChatbotMode.HYBRID:
            response, metadata = self._hybrid_response(message, relevant_rooms)
        else:
            response, metadata = self._offline_response(message, relevant_rooms)
        
        # Update usage
        for room in relevant_rooms[:3]:
            if room.topic in self.cloud_rooms:
                self.cloud_rooms[room.topic].usage_count += 1
                self.cloud_rooms[room.topic].last_used = time.time()
            elif room.topic in self.offline_rooms:
                self.offline_rooms[room.topic].usage_count += 1
                self.offline_rooms[room.topic].last_used = time.time()
        
        # Log
        self.conversation_history.append({
            "message": message,
            "response": response,
            "mode": self.mode.value,
            "timestamp": time.time(),
            "rooms_used": [r.topic for r in relevant_rooms[:3]]
        })
        
        # Evaluate offloading
        if len(self.conversation_history) % 10 == 0:
            self._evaluate_offloading()
        
        return response, metadata
    
    def _find_relevant_rooms(self, message: str, context: Dict) -> List[ConversationRoom]:
        """Find rooms relevant to the message."""
        message_lower = message.lower()
        relevant = []
        all_rooms = {**self.cloud_rooms, **self.offline_rooms}
        
        for room in all_rooms.values():
            score = 0.0
            if room.topic in message_lower:
                score += 0.5
            if room.topic in context.get("recent_topics", []):
                score += 0.3
            score += min(room.usage_count * 0.01, 0.2)
            
            if score > 0.3:
                relevant.append(room)
        
        relevant.sort(key=lambda r: r.usage_count, reverse=True)
        return relevant
    
    def _cloud_response(self, message: str, rooms: List[ConversationRoom]) -> Tuple[str, Dict]:
        """Generate response using cloud rooms."""
        if not rooms:
            return "I need to check that online. One moment...", {"source": "cloud_fallback"}
        
        primary_room = rooms[0]
        responses = {
            "greetings": "Hello! How can I help you today?",
            "weather": "Let me check the current weather for you...",
            "medication": "I'll fetch your medication schedule.",
            "family": "Would you like to see recent family photos?",
            "appointments": "Checking your upcoming appointments...",
        }
        
        response = responses.get(primary_room.topic, "I'll look that up for you.")
        metadata = {
            "source": "cloud",
            "primary_room": primary_room.topic,
            "confidence": 0.9,
            "rooms_considered": len(rooms)
        }
        
        return response, metadata
    
    def _hybrid_response(self, message: str, rooms: List[ConversationRoom]) -> Tuple[str, Dict]:
        """Generate response using mix of cloud and offline rooms."""
        offline_rooms = [r for r in rooms if r.offline_capable]
        cloud_rooms = [r for r in rooms if not r.offline_capable]
        
        if offline_rooms:
            primary_room = offline_rooms[0]
            responses = {
                "greetings_offline": "Hello! (responding offline)",
                "weather_offline": "Based on recent data: partly cloudy, 45°F",
                "medication_offline": "Your next dose is at 2 PM today.",
                "family_offline": "Showing cached family photos...",
                "appointments_offline": "You have a doctor's appointment tomorrow at 10 AM.",
            }
            
            response = responses.get(primary_room.topic, "I can help with that offline.")
            source = "offline"
        else:
            response = "I need to check that online briefly..."
            source = "cloud"
            primary_room = cloud_rooms[0] if cloud_rooms else None
        
        metadata = {
            "source": source,
            "primary_room": primary_room.topic if primary_room else None,
            "offline_rooms": len(offline_rooms),
            "cloud_rooms": len(cloud_rooms)
        }
        
        return response, metadata
    
    def _offline_response(self, message: str, rooms: List[ConversationRoom]) -> Tuple[str, Dict]:
        """Generate response using only offline rooms."""
        offline_rooms = [r for r in rooms if r.offline_capable]
        
        if not offline_rooms:
            return "I'm offline right now. I'll help when connected.", {"source": "offline_fallback"}
        
        primary_room = offline_rooms[0]
        responses = {
            "greetings_offline": "Hello! I'm operating offline.",
            "weather_offline": "Last weather: partly cloudy, 45°F",
            "medication_offline": "Your medication schedule (cached).",
            "family_offline": "Cached family photos available.",
            "appointments_offline": "Appointments from last sync.",
        }
        
        response = responses.get(primary_room.topic, "I can help with that offline.")
        
        metadata = {
            "source": "offline",
            "primary_room": primary_room.topic,
            "confidence": 0.8,
            "available_offline": len(offline_rooms)
        }
        
        return response, metadata
    
    def _evaluate_offloading(self):
        """Evaluate which rooms should move offline."""
        total_usage = sum(r.usage_count for r in self.cloud_rooms.values())
        
        for topic, room in list(self.cloud_rooms.items()):
            if room.should_go_offline(total_usage):
                offline_room = room.compile_for_offline()
                
                # Check storage
                new_storage = self.used_storage_mb + (offline_room.size_kb / 1024)
                if new_storage <= self.total_storage_mb:
                    self.offline_rooms[offline_room.topic] = offline_room
                    self.used_storage_mb = new_storage
                    
                    # Update statistics
                    offline_count = len(self.offline_rooms)
                    total_count = len(self.cloud_rooms) + offline_count
                    self.offline_percentage = offline_count / total_count if total_count > 0 else 0.0
    
    def get_system_state(self) -> Dict:
        """Get current state of the chatbot."""
        return {
            "mode": self.mode.value,
            "cloud_rooms": len(self.cloud_rooms),
            "offline_rooms": len(self.offline_rooms),
            "offline_percentage": self.offline_percentage,
            "used_storage_mb": self.used_storage_mb,
            "total_storage_mb": self.total_storage_mb,
            "total_conversations": len(self.conversation_history),
            "recent_topics": list(self.cloud_rooms.keys())[:5]
        }

def simulate_elderly_care_scenario():
    """Simulate elderly care facility scenario."""
    print("=" * 70)
    print("ELDERLY CARE FACILITY CHATBOT SIMULATION")
    print("Progressive Offloading from Cloud to Offline")
    print("=" * 70)
    
    # Initialize chatbot (simulating rural Alaska facility)
    chatbot = ProgressiveOffloadingChatbot(total_storage_mb=50.0)
    
    # Simulate conversations over time
    conversations = [
        ("Day 1: Hello!", {"recent_topics": []}, True),
        ("Day 1: What's the weather?", {"recent_topics": ["greetings"]}, True),
        ("Day 2: When is my medication?", {"recent_topics": ["weather"]}, True),
        ("Day 3: Show me family photos", {"recent_topics": ["medication"]}, True),
        ("Day 4: What appointments do I have?", {"recent_topics": ["family"]}, True),
        ("Day 5: Hello again", {"recent_topics": ["appointments"]}, True),
        ("Day 6: How's the weather?", {"recent_topics": ["greetings"]}, True),
        ("Day 7: Medication time?", {"recent_topics": ["weather"]}, True),
        ("Day 8: Internet outage - Hello?", {"recent_topics": ["medication"]}, False),
        ("Day 9: Still offline - Weather?", {"recent_topics": ["greetings"]}, False),
        ("Day 10: Back online - Family photos?", {"recent_topics": ["weather"]}, True),
        ("Day 11: Appointments please", {"recent_topics": ["family"]}, True),
    ]
    
    print("\nInitial chatbot state:")
    print(json.dumps(chatbot.get_system_state(), indent=2))
    
    print("\n" + "=" * 70)
    print("SIMULATING CONVERSATIONS...")
    print("=" * 70)
    
    for i, (message, context, connectivity) in enumerate(conversations):
        print(f"\n{i+1}. {message}")
        print(f"   Connectivity: {'✅ Online' if connectivity else '❌ Offline'}")
        
        response, metadata = chatbot.process_message(message, context, connectivity)
        
        print(f"   Response: {response}")
        print(f"   Source: {metadata['source']}")
        if 'primary_room' in metadata and metadata['primary_room']:
            print(f"   Room used: {metadata['primary_room']}")
        
        # Show offloading progress periodically
        if (i + 1) % 4 == 0:
            state = chatbot.get_system_state()
            print(f"\n   📊 Progress: {state['offline_percentage']*100:.1f}% offline")
            print(f"   Offline rooms: {state['offline_rooms']}/{state['cloud_rooms'] + state['offline_rooms']}")
    
    print("\n" + "=" * 70)
    print("FINAL CHATBOT STATE:")
    print("=" * 70)
    
    final_state = chatbot.get_system_state()
    print(json.dumps(final_state, indent=2))
    
    print("\n" + "=" * 70)
    print("REAL-WORLD IMPLICATIONS:")
    print("=" * 70)
    print("""
1. **Progressive Offloading**: Frequently used rooms moved offline automatically
2. **Connectivity Resilience**: Chatbot works during internet outages
3. **Storage Awareness**: Only compiles rooms that fit available storage
4. **Usage-Based Optimization**: Rooms optimized based on actual usage patterns
5. **Seamless Transitions**: Users don't notice cloud/offline switching

This is warp-as-room in action:
• Each conversation topic = warp room
• Room compilation = optimization for offline
• Usage tracking = determines which rooms to offload
• Mode switching = dynamic room selection based on connectivity

Now imagine this scaled to 1000+ rooms, running on Jetson in rural clinic,
handling medical queries, family connections, daily routines...
""")

def main():
    """Main function to run the example."""
    print("Chatbot That Slowly Moves Offline - Example")
    print("Demonstrating progressive offloading using warp specialization")
    print()
    
    simulate_elderly_care_scenario()
    
    print("\n" + "=" * 70)
    print("HOW THIS MAPS TO WARP-AS-ROOM ARCHITECTURE:")
    print("=" * 70)
    print("""
Production implementation would use:

1. **Cloud serving variant** for initial cloud processing
   - High-throughput warp rooms in cloud
   - Room usage tracking and analytics
   - Decision making for offloading

2. **Edge AI variant** for offline capability
   - Lightweight warp rooms compiled for edge
   - Local inference without cloud dependency
   - Storage-constrained optimization

3. **IoT variant** for deployment
   - Low-power operation for always-on devices
   - Intermittent connectivity handling
   - Battery-aware room activation

4. **PLATO integration** for knowledge sync
   - Room compilation recipes as tiles
   - Usage patterns shared across fleet
   - Offline room updates when connected

Result: Chatbot that starts cloud-based, learns usage patterns,
progressively offloads to edge, provides continuous service
even with intermittent connectivity.
""")

if __name__ == "__main__":
    main()
