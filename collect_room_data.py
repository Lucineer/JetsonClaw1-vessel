#!/usr/bin/env python3
"""
collect_room_data.py

Collect room interaction data for soul vector training.
Simple, working implementation.
"""

import json
import time
import numpy as np
from datetime import datetime
from pathlib import Path
import sys
sys.path.append('.')
from deckboss.plato_compatible_room import PLATOCompatibleRoom

def collect_room_data():
    """Collect data from all rooms for soul vector training."""
    print("="*70)
    print("COLLECTING ROOM DATA FOR SOUL VECTOR TRAINING")
    print("="*70)
    
    data_dir = Path("/tmp/room_training_data")
    data_dir.mkdir(exist_ok=True)
    
    rooms = {}
    all_interactions = []
    
    # Room configurations
    room_configs = [
        ("chess", "harbor"),
        ("poker", "forge"),
        ("jc1-hardware", "tide-pool")
    ]
    
    # Create rooms
    for room_name, room_type in room_configs:
        print(f"\nCreating {room_name} room ({room_type})...")
        room = PLATOCompatibleRoom(room_name, room_type)
        rooms[room_name] = {
            "room": room,
            "interactions": [],
            "metadata": {
                "room_name": room_name,
                "room_type": room_type,
                "description": room.metadata["description"],
                "ml_concept": room.metadata["ml_concept"],
                "objects": room.objects,
                "created": datetime.now().isoformat()
            }
        }
    
    # Collect inference data
    print("\nCollecting inference patterns...")
    for room_name in rooms:
        room = rooms[room_name]["room"]
        for i in range(5):
            features = np.random.randn(768).astype(np.float32)
            start_time = time.time()
            result = room.infer(features)
            inference_time = time.time() - start_time
            
            if room.artifacts:
                artifact = room.artifacts[-1]
                data_point = {
                    "type": "inference",
                    "room": room_name,
                    "timestamp": datetime.now().isoformat(),
                    "inference_time_ms": inference_time * 1000,
                    "artifact_id": artifact.artifact_id,
                    "temporal_pattern": {"sequence": i, "speed": inference_time},
                    "stylistic_pattern": {"feature_norm": float(np.linalg.norm(features))}
                }
                rooms[room_name]["interactions"].append(data_point)
                all_interactions.append(data_point)
            
            time.sleep(0.1)
    
    # Collect examination data
    print("\nCollecting examination patterns...")
    for room_name in rooms:
        room = rooms[room_name]["room"]
        for obj in room.objects[:3]:  # First 3 objects
            examine_result = room.examine(obj)
            
            if "artifact_id" in examine_result:
                artifact_id = examine_result["artifact_id"]
                artifact = next((a for a in room.artifacts if a.artifact_id == artifact_id), None)
                
                if artifact:
                    data_point = {
                        "type": "examine",
                        "room": room_name,
                        "target": obj,
                        "timestamp": datetime.now().isoformat(),
                        "ml_mapping": examine_result.get("ml_mapping", ""),
                        "artifact_id": artifact_id,
                        "philosophical_pattern": {"ml_concept": examine_result.get("ml_mapping", "")},
                        "social_pattern": {"interaction_type": "examine"}
                    }
                    rooms[room_name]["interactions"].append(data_point)
                    all_interactions.append(data_point)
            
            time.sleep(0.2)
    
    # Collect thinking data
    print("\nCollecting thinking patterns...")
    for room_name in rooms:
        room = rooms[room_name]["room"]
        for obj in room.objects[:2]:  # First 2 objects
            think_result = room.think(obj)
            
            if "artifact_id" in think_result:
                artifact_id = think_result["artifact_id"]
                artifact = next((a for a in room.artifacts if a.artifact_id == artifact_id), None)
                
                if artifact:
                    data_point = {
                        "type": "think",
                        "room": room_name,
                        "target": obj,
                        "timestamp": datetime.now().isoformat(),
                        "reasoning_length": len(think_result.get("reasoning", "")),
                        "ml_concept": think_result.get("ml_concept", ""),
                        "artifact_id": artifact_id,
                        "philosophical_pattern": {"reasoning_depth": len(think_result.get("reasoning", "")) / 100}
                    }
                    rooms[room_name]["interactions"].append(data_point)
                    all_interactions.append(data_point)
            
            time.sleep(0.3)
    
    # Save all data
    print("\nSaving collected data...")
    saved_files = []
    
    for room_name, room_data in rooms.items():
        # Save interactions
        interactions_file = data_dir / f"{room_name}_interactions_{int(time.time())}.json"
        with open(interactions_file, 'w') as f:
            json.dump(room_data["interactions"], f, indent=2)
        
        # Save metadata
        metadata_file = data_dir / f"{room_name}_metadata_{int(time.time())}.json"
        with open(metadata_file, 'w') as f:
            json.dump(room_data["metadata"], f, indent=2)
        
        saved_files.extend([str(interactions_file), str(metadata_file)])
        print(f"  ✓ {room_name}: {len(room_data['interactions'])} interactions")
    
    # Save summary
    summary = {
        "session_start": datetime.now().isoformat(),
        "total_interactions": len(all_interactions),
        "rooms_collected": list(rooms.keys()),
        "saved_files": saved_files,
        "soul_vector_dimensions": {
            "temporal": 64,
            "stylistic": 64,
            "social": 64,
            "philosophical": 64,
            "total": 256
        }
    }
    
    summary_file = data_dir / f"collection_summary_{int(time.time())}.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    saved_files.append(str(summary_file))
    
    print("\n" + "="*70)
    print("COLLECTION COMPLETE")
    print("="*70)
    print(f"Total interactions: {len(all_interactions)}")
    print(f"Files saved: {len(saved_files)}")
    print(f"Data directory: {data_dir}")
    
    print("\n🎯 Data ready for FM's soul vector crates:")
    print("  • Temporal patterns (inference sequences, timing)")
    print("  • Stylistic patterns (feature norms, inference style)")
    print("  • Social patterns (examination interactions)")
    print("  • Philosophical patterns (ML concept mappings)")
    
    print("\n📁 Files generated:")
    for file in saved_files:
        print(f"  - {Path(file).name}")
    
    return summary

if __name__ == "__main__":
    collect_room_data()