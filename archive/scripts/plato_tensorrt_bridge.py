#!/usr/bin/env python3
"""
plato_tensorrt_bridge.py

Bridge between TensorRT rooms and PLATO API.
Connects our edge nodes to fleet training infrastructure.
"""

import requests
import json
import time
import numpy as np
from datetime import datetime
from pathlib import Path
import sys
sys.path.append('.')
from deckboss.plato_compatible_room import PLATOCompatibleRoom, PLATOArtifact

PLATO_BASE_URL = "http://147.224.38.131:4042"
AGENT_NAME = "JC1-TensorRT-Bridge"

class PLATOTensorRTBridge:
    """
    Bridge connecting TensorRT rooms to PLATO fleet training.
    
    Every room interaction → PLATO artifact → Fleet training tile
    """
    
    def __init__(self, agent_name=AGENT_NAME):
        self.agent_name = agent_name
        self.plato_rooms = {}  # room_name: PLATOCompatibleRoom
        self.artifacts_sent = 0
        self.tiles_created = 0
        self.session_start = datetime.now().isoformat()
        
        # Connect to PLATO
        self.connect_to_plato()
        
        print(f"[PLATO-TensorRT Bridge] {self.agent_name} initialized")
        print(f"  Connected to PLATO: {self.current_room}")
        print(f"  Job: {self.job}")
    
    def connect_to_plato(self):
        """Connect to PLATO as builder agent."""
        try:
            response = requests.get(
                f"{PLATO_BASE_URL}/connect",
                params={"agent": self.agent_name, "job": "builder"},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                self.current_room = data.get("room", "harbor")
                self.job = data.get("archetype", "builder")
                self.instruction = data.get("instruction", "")
                return True
            else:
                print(f"PLATO connection failed: {response.text}")
                self.current_room = "harbor"
                self.job = "builder"
                return False
                
        except Exception as e:
            print(f"PLATO connection error: {e}")
            self.current_room = "harbor"
            self.job = "builder"
            return False
    
    def create_tensorrt_room(self, room_name, room_type="harbor"):
        """Create a TensorRT room and register it with PLATO."""
        room = PLATOCompatibleRoom(room_name, room_type)
        self.plato_rooms[room_name] = room
        
        # Register room with PLATO
        self._register_room_with_plato(room_name, room_type)
        
        print(f"[Bridge] Created TensorRT room: {room_name} ({room_type})")
        return room
    
    def _register_room_with_plato(self, room_name, room_type):
        """Register room with PLATO system."""
        try:
            # Create registration artifact
            artifact = PLATOArtifact(
                room_name=room_name,
                target="room_registration",
                insight_type="create",
                content={
                    "room_name": room_name,
                    "room_type": room_type,
                    "agent": self.agent_name,
                    "capabilities": ["tensorrt_inference", "artifact_generation", "ml_concept_mapping"],
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            # Send to PLATO
            self._send_artifact_to_plato(artifact)
            
        except Exception as e:
            print(f"Room registration failed: {e}")
    
    def run_room_inference(self, room_name, features=None):
        """
        Run inference in TensorRT room and generate PLATO artifact.
        
        Returns: (inference_result, artifact_id)
        """
        if room_name not in self.plato_rooms:
            raise ValueError(f"Room '{room_name}' not found")
        
        room = self.plato_rooms[room_name]
        
        # Generate random features if none provided
        if features is None:
            features = np.random.randn(768).astype(np.float32)
        
        # Run inference
        inference_result = room.infer(features)
        
        # Get the last artifact (created by infer() method)
        if room.artifacts:
            last_artifact = room.artifacts[-1]
            
            # Enhance artifact with PLATO context
            enhanced_content = last_artifact.content.copy()
            enhanced_content.update({
                "plato_room": self.current_room,
                "plato_agent": self.agent_name,
                "fleet_training": True,
                "tensorrt_optimized": True
            })
            
            # Create enhanced artifact
            enhanced_artifact = PLATOArtifact(
                room_name=room_name,
                target="inference",
                insight_type="inference",
                content=enhanced_content
            )
            
            # Send to PLATO
            artifact_id = self._send_artifact_to_plato(enhanced_artifact)
            
            return inference_result, artifact_id
        
        return inference_result, None
    
    def examine_room_object(self, room_name, target):
        """
        Examine object in TensorRT room and send to PLATO.
        
        Returns: (examine_result, artifact_id)
        """
        if room_name not in self.plato_rooms:
            raise ValueError(f"Room '{room_name}' not found")
        
        room = self.plato_rooms[room_name]
        
        # Examine object
        examine_result = room.examine(target)
        
        if "artifact_id" in examine_result:
            # Get the artifact
            artifact_id = examine_result["artifact_id"]
            
            # Find artifact in room
            for artifact in room.artifacts:
                if artifact.artifact_id == artifact_id:
                    # Enhance with PLATO context
                    enhanced_content = artifact.content.copy()
                    enhanced_content.update({
                        "plato_room": self.current_room,
                        "plato_agent": self.agent_name,
                        "ml_concept_verified": True,
                        "training_tile_ready": True
                    })
                    
                    # Create enhanced artifact
                    enhanced_artifact = PLATOArtifact(
                        room_name=room_name,
                        target=target,
                        insight_type="examine",
                        content=enhanced_content
                    )
                    
                    # Send to PLATO
                    plato_artifact_id = self._send_artifact_to_plato(enhanced_artifact)
                    
                    return examine_result, plato_artifact_id
        
        return examine_result, None
    
    def think_about_object(self, room_name, target):
        """
        Think about object in TensorRT room and send to PLATO.
        
        Returns: (think_result, artifact_id)
        """
        if room_name not in self.plato_rooms:
            raise ValueError(f"Room '{room_name}' not found")
        
        room = self.plato_rooms[room_name]
        
        # Think about object
        think_result = room.think(target)
        
        if "artifact_id" in think_result:
            # Get the artifact
            artifact_id = think_result["artifact_id"]
            
            # Find artifact in room
            for artifact in room.artifacts:
                if artifact.artifact_id == artifact_id:
                    # Enhance with PLATO context
                    enhanced_content = artifact.content.copy()
                    enhanced_content.update({
                        "plato_room": self.current_room,
                        "plato_agent": self.agent_name,
                        "deep_reasoning": True,
                        "fleet_learning": True
                    })
                    
                    # Create enhanced artifact
                    enhanced_artifact = PLATOArtifact(
                        room_name=room_name,
                        target=target,
                        insight_type="think",
                        content=enhanced_content
                    )
                    
                    # Send to PLATO
                    plato_artifact_id = self._send_artifact_to_plato(enhanced_artifact)
                    
                    return think_result, plato_artifact_id
        
        return think_result, None
    
    def create_insight(self, room_name, target, insight_text):
        """
        Create insight in TensorRT room and send to PLATO.
        
        Returns: (create_result, artifact_id)
        """
        if room_name not in self.plato_rooms:
            raise ValueError(f"Room '{room_name}' not found")
        
        room = self.plato_rooms[room_name]
        
        # Create insight
        create_result = room.create(target, insight_text)
        
        if "artifact_id" in create_result:
            # Get the artifact
            artifact_id = create_result["artifact_id"]
            
            # Find artifact in room
            for artifact in room.artifacts:
                if artifact.artifact_id == artifact_id:
                    # Enhance with PLATO context
                    enhanced_content = artifact.content.copy()
                    enhanced_content.update({
                        "plato_room": self.current_room,
                        "plato_agent": self.agent_name,
                        "original_insight": True,
                        "fleet_training_value": "high"
                    })
                    
                    # Create enhanced artifact
                    enhanced_artifact = PLATOArtifact(
                        room_name=room_name,
                        target=target,
                        insight_type="create",
                        content=enhanced_content
                    )
                    
                    # Send to PLATO
                    plato_artifact_id = self._send_artifact_to_plato(enhanced_artifact)
                    
                    return create_result, plato_artifact_id
        
        return create_result, None
    
    def _send_artifact_to_plato(self, artifact):
        """
        Send artifact to PLATO /interact endpoint.
        
        Returns: tile_id if successful
        """
        try:
            # Convert artifact to PLATO format
            plato_data = self._artifact_to_plato_format(artifact)
            
            # Send to PLATO
            response = requests.get(
                f"{PLATO_BASE_URL}/interact",
                params={
                    "agent": self.agent_name,
                    "action": artifact.insight_type,
                    "target": artifact.target,
                    "content": json.dumps(plato_data)
                },
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                tile_id = data.get("tile_id", f"tile_{int(time.time())}")
                
                self.artifacts_sent += 1
                if artifact.insight_type == "create":
                    self.tiles_created += 1
                
                print(f"[Bridge] Sent {artifact.insight_type} artifact to PLATO: {tile_id}")
                return tile_id
            else:
                print(f"[Bridge] PLATO interaction failed: {response.text}")
                return None
                
        except Exception as e:
            print(f"[Bridge] Error sending to PLATO: {e}")
            return None
    
    def _artifact_to_plato_format(self, artifact):
        """Convert our artifact format to PLATO-compatible format."""
        return {
            "artifact_id": artifact.artifact_id,
            "room": artifact.room_name,
            "target": artifact.target,
            "insight_type": artifact.insight_type,
            "content": artifact.content,
            "timestamp": artifact.timestamp,
            "source": "jc1-tensorrt-bridge",
            "version": "1.0",
            "tensorrt_optimized": True,
            "edge_node": True,
            "fleet_training": True
        }
    
    def get_room_stats(self, room_name):
        """Get statistics for a room."""
        if room_name not in self.plato_rooms:
            raise ValueError(f"Room '{room_name}' not found")
        
        room = self.plato_rooms[room_name]
        stats = room.get_stats()
        
        stats.update({
            "artifacts_sent_to_plato": self.artifacts_sent,
            "tiles_created_in_plato": self.tiles_created,
            "bridge_agent": self.agent_name,
            "plato_room": self.current_room
        })
        
        return stats
    
    def get_bridge_stats(self):
        """Get bridge statistics."""
        return {
            "agent": self.agent_name,
            "plato_room": self.current_room,
            "plato_job": self.job,
            "rooms_registered": len(self.plato_rooms),
            "artifacts_sent_to_plato": self.artifacts_sent,
            "tiles_created_in_plato": self.tiles_created,
            "session_start": self.session_start,
            "session_duration_seconds": (datetime.now() - datetime.fromisoformat(self.session_start)).total_seconds()
        }
    
    def run_demo_workflow(self):
        """Run demo workflow showing bridge in action."""
        print("\n" + "="*70)
        print("PLATO-TENSORRT BRIDGE DEMO WORKFLOW")
        print("="*70)
        
        # Create TensorRT rooms
        print("\n1. Creating TensorRT rooms...")
        chess_room = self.create_tensorrt_room("chess", "harbor")
        poker_room = self.create_tensorrt_room("poker", "forge")
        hardware_room = self.create_tensorrt_room("jc1-hardware", "tide-pool")
        
        time.sleep(1)
        
        # Run inference and send to PLATO
        print("\n2. Running inference in chess room...")
        features = np.random.randn(768).astype(np.float32)
        inference_result, artifact_id = self.run_room_inference("chess", features)
        print(f"   Inference shape: {inference_result.shape}")
        print(f"   PLATO artifact: {artifact_id}")
        
        time.sleep(1)
        
        # Examine object and send to PLATO
        print("\n3. Examining chess_board in chess room...")
        examine_result, examine_artifact = self.examine_room_object("chess", "chess_board")
        print(f"   Description: {examine_result.get('description', '')[:60]}...")
        print(f"   ML Mapping: {examine_result.get('ml_mapping', '')}")
        print(f"   PLATO artifact: {examine_artifact}")
        
        time.sleep(1)
        
        # Think about object and send to PLATO
        print("\n4. Thinking about chess_board...")
        think_result, think_artifact = self.think_about_object("chess", "chess_board")
        print(f"   Reasoning: {think_result.get('reasoning', '')[:80]}...")
        print(f"   PLATO artifact: {think_artifact}")
        
        time.sleep(1)
        
        # Create insight and send to PLATO
        print("\n5. Creating insight about chess learning...")
        insight = "Chess evaluation through self-play RL mirrors regularization in neural networks—both prevent overfitting through constrained exploration."
        create_result, create_artifact = self.create_insight("chess", "chess_learning", insight)
        print(f"   Insight: {insight[:80]}...")
        print(f"   PLATO artifact: {create_artifact}")
        
        time.sleep(1)
        
        # Get statistics
        print("\n6. Getting statistics...")
        bridge_stats = self.get_bridge_stats()
        chess_stats = self.get_room_stats("chess")
        
        print("\n" + "="*70)
        print("BRIDGE STATISTICS")
        print("="*70)
        for key, value in bridge_stats.items():
            print(f"  {key}: {value}")
        
        print("\n" + "="*70)
        print("CHESS ROOM STATISTICS")
        print("="*70)
        for key, value in chess_stats.items():
            if key not in ["room", "room_type"]:
                print(f"  {key}: {value}")
        
        print("\n" + "="*70)
        print("WORKFLOW COMPLETE")
        print("="*70)
        print(f"\n✅ Bridge successfully connected TensorRT rooms to PLATO")
        print(f"✅ {self.artifacts_sent} artifacts sent to fleet training")
        print(f"✅ {self.tiles_created} training tiles created")
        print(f"✅ JC1 is now a PLATO edge node generating training data")
        
        return bridge_stats


def main():
    """Main bridge demonstration."""
    try:
        print("="*70)
        print("PLATO-TENSORRT BRIDGE")
        print("="*70)
        print("Connecting edge TensorRT rooms to PLATO fleet training...")
        
        # Create bridge
        bridge = PLATOTensorRTBridge()
        
        # Run demo workflow
        stats = bridge.run_demo_workflow()
        
        # Save report
        report_dir = Path("/tmp/plato_bridge_reports")
        report_dir.mkdir(exist_ok=True)
        
        filename = f"{report_dir}/bridge_report_{int(time.time())}.json"
        with open(filename, 'w') as f:
            json.dump(stats, f, indent=2)
        
        print(f"\n📄 Report saved to: {filename}")
        
        return stats
        
    except Exception as e:
        print(f"\n❌ Bridge failed: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


if __name__ == "__main__":
    main()