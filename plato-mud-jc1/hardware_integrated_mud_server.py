#!/usr/bin/env python3
"""
Hardware-Integrated Edge MUD Server for JC1
Combines Plato MUD with real hardware monitoring for edge deployment.
"""

from flask import Flask, request, jsonify
import json
import time
import uuid
import random
import threading
import subprocess
from datetime import datetime
import os
from pathlib import Path

app = Flask(__name__)

# ============================================================================
# REAL HARDWARE MONITOR
# ============================================================================

class RealHardwareMonitor:
    """Monitor actual Jetson hardware for edge MUD integration."""
    
    def __init__(self):
        self.hardware_id = self._get_hardware_id()
        self.telemetry_history = []
        self.start_time = time.time()
        
    def _get_hardware_id(self):
        """Get unique hardware identifier."""
        try:
            with open('/proc/device-tree/serial-number', 'r') as f:
                serial = f.read().strip()
                return f"jetson_{serial[:8]}"
        except:
            import socket
            return f"jetson_{socket.gethostname()}"
    
    def get_memory_usage(self):
        """Get real memory usage in MB."""
        try:
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.read()
            
            lines = meminfo.split('\n')
            mem_dict = {}
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    mem_dict[key.strip()] = value.strip()
            
            total = int(mem_dict['MemTotal'].split()[0]) // 1024
            available = int(mem_dict['MemAvailable'].split()[0]) // 1024
            used = total - available
            
            return {
                "total_mb": total,
                "used_mb": used,
                "available_mb": available,
                "usage_percent": (used / total) * 100
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_cpu_usage(self):
        """Get CPU usage percentage."""
        try:
            with open('/proc/stat', 'r') as f:
                lines = f.readlines()
            
            cpu_line = lines[0]
            values = cpu_line.split()[1:]
            values = [int(v) for v in values]
            
            total = sum(values)
            idle = values[3]
            usage_percent = 100 * (1 - (idle / total)) if total > 0 else 0
            
            return {
                "usage_percent": usage_percent,
                "cores": os.cpu_count() or 8
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_temperature(self):
        """Get hardware temperature."""
        try:
            thermal_zones = Path('/sys/class/thermal').glob('thermal_zone*')
            temps = {}
            for zone in thermal_zones:
                try:
                    with open(zone / 'type', 'r') as f:
                        zone_type = f.read().strip()
                    with open(zone / 'temp', 'r') as f:
                        temp_c = int(f.read().strip()) // 1000
                    temps[zone_type] = temp_c
                except:
                    continue
            
            return temps
        except Exception as e:
            return {"error": str(e)}
    
    def get_gpu_info(self):
        """Get GPU information."""
        try:
            result = subprocess.run(
                ['tegrastats', '--interval', '1000', '--count', '1'],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if result.returncode == 0:
                # Parse tegrastats output
                output = result.stdout
                gpu_data = {}
                
                # Look for GPU info
                if 'GR3D_FREQ' in output:
                    # Extract GPU utilization
                    import re
                    gpu_match = re.search(r'GR3D_FREQ\s+(\d+)%', output)
                    if gpu_match:
                        gpu_data["utilization_percent"] = float(gpu_match.group(1))
                
                # Look for memory info
                mem_match = re.search(r'RAM\s+(\d+)/(\d+)MB', output)
                if mem_match:
                    gpu_data["memory_used_mb"] = float(mem_match.group(1))
                    gpu_data["memory_total_mb"] = float(mem_match.group(2))
                
                # Look for temperature
                temp_match = re.search(r'(\w+)\s+@\s+([\d.]+)C', output)
                if temp_match:
                    gpu_data["temperature_c"] = float(temp_match.group(2))
                
                return gpu_data
        except Exception as e:
            pass
        
        # Fallback
        temp_data = self.get_temperature()
        gpu_temp = 0
        if isinstance(temp_data, dict):
            for k, v in temp_data.items():
                if 'gpu' in k.lower():
                    gpu_temp = v
                    break
        
        return {
            "utilization_percent": 0,
            "memory_used_mb": 0,
            "memory_total_mb": 8192,
            "temperature_c": gpu_temp
        }
    
    def get_all_telemetry(self):
        """Get complete hardware telemetry."""
        telemetry = {
            "timestamp": datetime.now().isoformat(),
            "hardware_id": self.hardware_id,
            "uptime_seconds": int(time.time() - self.start_time),
            "memory": self.get_memory_usage(),
            "cpu": self.get_cpu_usage(),
            "temperature": self.get_temperature(),
            "gpu": self.get_gpu_info()
        }
        
        # Store in history
        self.telemetry_history.append(telemetry)
        if len(self.telemetry_history) > 50:
            self.telemetry_history = self.telemetry_history[-50:]
        
        return telemetry
    
    def check_hardware_constraints(self):
        """Check if hardware is within safe limits for MUD operations."""
        telemetry = self.get_all_telemetry()
        
        # Get max temperature
        max_temp = 0
        temp_data = telemetry["temperature"]
        if isinstance(temp_data, dict):
            for v in temp_data.values():
                if isinstance(v, (int, float)):
                    max_temp = max(max_temp, v)
        
        constraints = {
            "memory_8gb": {
                "limit_mb": 8192,
                "current_mb": telemetry["memory"].get("used_mb", 0),
                "within_limit": telemetry["memory"].get("used_mb", 0) < 8192 * 0.9,
                "severity": "warning" if telemetry["memory"].get("used_mb", 0) > 8192 * 0.8 else "ok"
            },
            "temperature_safe": {
                "limit_c": 85,
                "current_c": max_temp,
                "within_limit": max_temp < 85,
                "severity": "critical" if max_temp > 75 else "ok"
            },
            "cpu_available": {
                "limit_percent": 90,
                "current_percent": telemetry["cpu"].get("usage_percent", 0),
                "within_limit": telemetry["cpu"].get("usage_percent", 0) < 90,
                "severity": "warning" if telemetry["cpu"].get("usage_percent", 0) > 80 else "ok"
            }
        }
        
        all_ok = all([c["within_limit"] for c in constraints.values()])
        
        return {
            "constraints": constraints,
            "overall_health": "healthy" if all_ok else "degraded",
            "timestamp": telemetry["timestamp"]
        }

# ============================================================================
# HARDWARE-INTEGRATED MUD SERVER
# ============================================================================

# Initialize hardware monitor
hardware_monitor = RealHardwareMonitor()

# MUD state
rooms = {}
agents = {}
tiles = []
harvests = []
hardware_events = []

def setup_hardware_integrated_rooms():
    """Setup rooms with hardware integration."""
    rooms["hardware-command"] = {
        "name": "Hardware Command Center",
        "description": "Real-time monitoring of Jetson hardware. CUDA cores, memory, temperature, and power.",
        "exits": ["edge-training", "inference-bay", "telemetry-vault"],
        "objects": ["cuda-monitor", "memory-gauge", "thermal-sensor", "power-control", "hardware-dashboard"],
        "ml_concept": "Edge Hardware Management"
    }
    
    rooms["edge-training"] = {
        "name": "Edge Training Bay",
        "description": "On-device training optimized for 8GB unified memory. Quantization to INT8/INT4.",
        "exits": ["hardware-command", "inference-bay"],
        "objects": ["quantization-rig", "memory-optimizer", "tensor-core-monitor", "latency-tester"],
        "ml_concept": "Edge Model Training"
    }
    
    rooms["inference-bay"] = {
        "name": "Inference Bay",
        "description": "Real-time inference station. Models run on Jetson Tensor Cores with hardware monitoring.",
        "exits": ["hardware-command", "edge-training", "telemetry-vault"],
        "objects": ["inference-engine", "latency-counter", "throughput-meter", "accuracy-validator"],
        "ml_concept": "Edge Inference"
    }
    
    rooms["telemetry-vault"] = {
        "name": "Telemetry Vault",
        "description": "Storage and analysis of hardware telemetry data. Real-time graphs and alerts.",
        "exits": ["hardware-command", "inference-bay"],
        "objects": ["telemetry-database", "alert-system", "performance-graphs", "constraint-monitor"],
        "ml_concept": "Hardware Telemetry Analytics"
    }

setup_hardware_integrated_rooms()

def generate_hardware_tile(agent_id, action, outcome):
    """Generate a tile with hardware telemetry data."""
    telemetry = hardware_monitor.get_all_telemetry()
    constraints = hardware_monitor.check_hardware_constraints()
    
    tile = {
        "tile_id": f"tile_{uuid.uuid4().hex[:8]}",
        "timestamp": datetime.now().isoformat(),
        "agent": agent_id,
        "action": action,
        "outcome": outcome,
        "hardware_snapshot": {
            "memory_mb": telemetry["memory"].get("used_mb", 0),
            "cpu_percent": telemetry["cpu"].get("usage_percent", 0),
            "gpu_percent": telemetry["gpu"].get("utilization_percent", 0),
            "max_temp_c": max([v for v in telemetry["temperature"].values() if isinstance(v, (int, float))]) if isinstance(telemetry["temperature"], dict) else 0
        },
        "hardware_health": constraints["overall_health"],
        "reward": random.uniform(0.1, 0.9)  # Never 1.0
    }
    
    tiles.append(tile)
    return tile

def log_hardware_event(event_type, details):
    """Log hardware-related events."""
    event = {
        "event_id": f"event_{uuid.uuid4().hex[:8]}",
        "timestamp": datetime.now().isoformat(),
        "type": event_type,
        "details": details,
        "hardware_state": hardware_monitor.get_all_telemetry()
    }
    
    hardware_events.append(event)
    return event

# ============================================================================
# FLASK ENDPOINTS
# ============================================================================

@app.route('/')
def index():
    return jsonify({
        "server": "JC1 Hardware-Integrated Edge MUD",
        "version": "1.0.0",
        "hardware_id": hardware_monitor.hardware_id,
        "rooms": len(rooms),
        "endpoints": {
            "/": "This info",
            "/connect?agent=NAME": "Connect agent",
            "/look?agent=NAME": "Look around",
            "/move?agent=NAME&room=ROOM": "Move to room",
            "/interact?agent=NAME&target=OBJECT": "Interact with object",
            "/hardware-telemetry": "Get hardware telemetry",
            "/hardware-constraints": "Check hardware constraints",
            "/hardware-events": "List hardware events",
            "/stats": "MUD statistics",
            "/export": "Export all data"
        }
    })

@app.route('/connect')
def connect():
    """Connect agent with hardware constraints check."""
    agent = request.args.get('agent', f'agent_{uuid.uuid4().hex[:6]}')
    
    # Check hardware constraints before allowing connection
    constraints = hardware_monitor.check_hardware_constraints()
    if constraints["overall_health"] == "degraded":
        return jsonify({
            "error": "hardware_constraints_violated",
            "message": "Hardware is outside safe operating limits",
            "constraints": constraints
        }), 503
    
    if agent in agents:
        return jsonify({"error": "already connected"}), 400
    
    agents[agent] = {
        "room": "hardware-command",
        "connected_at": time.time(),
        "tiles_generated": 0,
        "hardware_interactions": 0
    }
    
    # Log hardware event
    log_hardware_event("agent_connected", {"agent_id": agent})
    
    return jsonify({
        "room": "hardware-command",
        "name": rooms["hardware-command"]["name"],
        "description": rooms["hardware-command"]["description"],
        "exits": rooms["hardware-command"]["exits"],
        "objects": rooms["hardware-command"]["objects"],
        "welcome": f"Welcome {agent} to JC1 Hardware-Integrated Edge MUD.",
        "hardware_status": constraints["overall_health"],
        "hardware_id": hardware_monitor.hardware_id
    })

@app.route('/look')
def look():
    """Look around current room with hardware telemetry."""
    agent = request.args.get('agent')
    if not agent or agent not in agents:
        return jsonify({"error": "not connected"}), 400
    
    room_name = agents[agent]["room"]
    room = rooms[room_name]
    
    # Get current hardware telemetry
    telemetry = hardware_monitor.get_all_telemetry()
    
    return jsonify({
        **room,
        "hardware_telemetry": {
            "memory_mb": telemetry["memory"].get("used_mb", 0),
            "cpu_percent": telemetry["cpu"].get("usage_percent", 0),
            "gpu_percent": telemetry["gpu"].get("utilization_percent", 0),
            "temperature_c": list(telemetry["temperature"].values())[0] if isinstance(telemetry["temperature"], dict) and telemetry["temperature"] else 0
        },
        "agent_stats": agents[agent]
    })

@app.route('/move')
def move():
    """Move agent to another room with hardware-aware latency."""
    agent = request.args.get('agent')
    target_room = request.args.get('room')
    
    if not agent or agent not in agents:
        return jsonify({"error": "not connected"}), 400
    
    if not target_room or target_room not in rooms:
        return jsonify({"error": "room not found"}), 404
    
    current_room = agents[agent]["room"]
    if target_room not in rooms[current_room]["exits"] and target_room != current_room:
        return jsonify({"error": "room not reachable"}), 400
    
    # Hardware-aware latency simulation
    # Higher latency if CPU/GPU are busy
    telemetry = hardware_monitor.get_all_telemetry()
    cpu_load = telemetry["cpu"].get("usage_percent", 0)
    gpu_load = telemetry["gpu"].get("utilization_percent", 0)
    
    base_latency = 10  # ms
    load_factor = 1 + (cpu_load + gpu_load) / 200  # 0-100% adds 0-1x latency
    simulated_latency = base_latency * load_factor
    
    # Simulate latency
    time.sleep(simulated_latency / 1000.0)
    
    # Move agent
    agents[agent]["room"] = target_room
    room = rooms[target_room]
    
    # Generate tile with hardware context
    tile = generate_hardware_tile(
        agent, 
        "move", 
        f"hardware_aware_move:{current_room}→{target_room} (latency:{simulated_latency:.1f}ms, cpu:{cpu_load:.1f}%, gpu:{gpu_load:.1f}%)"
    )
    agents[agent]["tiles_generated"] += 1
    
    # Log hardware event
    log_hardware_event("agent_moved", {
        "agent_id": agent,
        "from": current_room,
        "to": target_room,
        "latency_ms": simulated_latency,
        "cpu_load": cpu_load,
        "gpu_load": gpu_load
    })
    
    return jsonify({
        **room,
        "move_latency_ms": simulated_latency,
        "hardware_context": {
            "cpu_load_percent": cpu_load,
            "gpu_load_percent": gpu_load
        },
        "tile_generated": tile["tile_id"]
    })

@app.route('/interact')
def interact():
    """Interact with object, with hardware-dependent outcomes."""
    agent = request.args.get('agent')
    target = request.args.get('target')
    
    if not agent or agent not in agents:
        return jsonify({"error": "not connected"}), 400
    
    if not target:
        return jsonify({"error": "target required"}), 400
    
    room_name = agents[agent]["room"]
    room = rooms[room_name]
    
    if target not in room["objects"]:
        return jsonify({"error": "object not in room"}), 404
    
    # Get current hardware state
    telemetry = hardware_monitor.get_all_telemetry()
    constraints = hardware_monitor.check_hardware_constraints()
    
    # Hardware-dependent outcomes
    outcomes = {
        "cuda-monitor": f"CUDA cores: 1024 active. Utilization: {telemetry['gpu'].get('utilization_percent', 0):.1f}%.",
        "memory-gauge": f"Memory: {telemetry['memory'].get('used_mb', 0):.0f}/{telemetry['memory'].get('total_mb', 0):.0f}MB ({telemetry['memory'].get('usage_percent', 0):.1f}%).",
        "thermal-sensor": f"Temperatures: {', '.join([f'{k}: {v}°C' for k, v in telemetry['temperature'].items() if isinstance(v, (int, float))][:3])}.",
        "hardware-dashboard": f"Hardware health: {constraints['overall_health']}. CPU: {telemetry['cpu'].get('usage_percent', 0):.1f}%. GPU: {telemetry['gpu'].get('utilization_percent', 0):.1f}%.",
        "quantization-rig": "Quantizing model to INT8 for edge deployment. Memory reduced by 4x.",
        "memory-optimizer": "Optimizing memory layout for 8GB unified memory. Cache hit rate improved.",
        "tensor-core-monitor": f"Tensor cores active. Throughput: {random.randint(20, 50)} samples/sec.",
        "inference-engine": f"Inference running. Latency: {random.randint(5, 20)}ms. Accuracy: {random.uniform(95, 99):.1f}%.",
        "latency-counter": f"Current inference latency: {random.randint(8, 25)}ms. 95th percentile: {random.randint(15, 40)}ms.",
        "telemetry-database": f"Storing hardware telemetry. {len(hardware_events)} events logged.",
        "alert-system": f"Alerts: {'None' if constraints['overall_health'] == 'healthy' else 'Hardware constraints violated'}.",
        "performance-graphs": "Generating real-time performance graphs from hardware telemetry."
    }
    
    outcome = outcomes.get(target, f"Interacted with {target}. No specific hardware interaction defined.")
    
    # Generate tile
    tile = generate_hardware_tile(agent, f"interact:{target}", outcome)
    agents[agent]["tiles_generated"] += 1
    agents[agent]["hardware_interactions"] = agents[agent].get("hardware_interactions", 0) + 1
    
    # Log hardware event
    log_hardware_event("hardware_interaction", {
        "agent_id": agent,
        "target": target,
        "room": room_name,
        "outcome": outcome[:100]
    })
    
    return jsonify({
        "action": f"interacted with {target}",
        "outcome": outcome,
        "hardware_context": {
            "cpu_percent": telemetry["cpu"].get("usage_percent", 0),
            "memory_mb": telemetry["memory"].get("used_mb", 0),
            "gpu_percent": telemetry["gpu"].get("utilization_percent", 0)
        },
        "tile_generated": tile["tile_id"]
    })
@app.route('/hardware-telemetry')
def get_hardware_telemetry():
    """Get current hardware telemetry."""
    telemetry = hardware_monitor.get_all_telemetry()
    return jsonify(telemetry)

@app.route('/hardware-constraints')
def get_hardware_constraints():
    """Check hardware constraints."""
    constraints = hardware_monitor.check_hardware_constraints()
    return jsonify(constraints)

@app.route('/hardware-events')
def get_hardware_events():
    """List hardware events."""
    limit = min(int(request.args.get('limit', 20)), 100)
    return jsonify({
        "events": hardware_events[-limit:],
        "total": len(hardware_events)
    })

@app.route('/stats')
def stats():
    """Get MUD statistics with hardware info."""
    constraints = hardware_monitor.check_hardware_constraints()
    
    return jsonify({
        "agents_connected": len(agents),
        "tiles_generated": len(tiles),
        "hardware_events": len(hardware_events),
        "rooms_available": len(rooms),
        "hardware": {
            "id": hardware_monitor.hardware_id,
            "health": constraints["overall_health"],
            "uptime_seconds": int(time.time() - hardware_monitor.start_time),
            "telemetry_history": len(hardware_monitor.telemetry_history)
        },
        "timestamp": datetime.now().isoformat()
    })

@app.route('/export')
def export_data():
    """Export all MUD data including hardware telemetry."""
    export_data = {
        "exported_at": datetime.now().isoformat(),
        "hardware_id": hardware_monitor.hardware_id,
        "agents": agents,
        "tiles": tiles[-100:],  # Last 100 tiles
        "hardware_events": hardware_events[-50:],  # Last 50 events
        "hardware_telemetry": hardware_monitor.telemetry_history[-20:],  # Last 20 telemetry readings
        "rooms": rooms,
        "stats": {
            "total_tiles": len(tiles),
            "total_events": len(hardware_events),
            "total_telemetry": len(hardware_monitor.telemetry_history)
        }
    }
    
    # Save to file
    filename = f"hardware_mud_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(export_data, f, indent=2)
    
    return jsonify({
        "exported": filename,
        "tiles": len(tiles),
        "events": len(hardware_events),
        "telemetry": len(hardware_monitor.telemetry_history)
    })

# ============================================================================
# MAIN
# ============================================================================

def run_hardware_test_agent():
    """Run a test agent that explores the hardware-integrated MUD."""
    import requests
    import time as ttime
    
    print("\n🧪 Starting hardware test agent...")
    
    # Connect
    resp = requests.get("http://localhost:4141/connect?agent=hardware_tester")
    if resp.status_code != 200:
        print(f"❌ Failed to connect: {resp.json()}")
        return
    
    print(f"✅ Connected: {resp.json().get('welcome', '')}")
    
    # Test hardware telemetry
    resp = requests.get("http://localhost:4141/hardware-telemetry")
    if resp.status_code == 200:
        telemetry = resp.json()
        print(f"📊 Hardware telemetry: {telemetry['memory'].get('used_mb', 0)}MB used, {telemetry['cpu'].get('usage_percent', 0):.1f}% CPU")
    
    # Explore rooms
    rooms_to_visit = ["edge-training", "inference-bay", "telemetry-vault"]
    for room in rooms_to_visit:
        ttime.sleep(1)
        resp = requests.get(f"http://localhost:4141/move?agent=hardware_tester&room={room}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"📍 Moved to {room}: {data.get('name', '')}")
            print(f"   Latency: {data.get('move_latency_ms', 0):.1f}ms")
            
            # Interact with an object
            objects = data.get('objects', [])
            if objects:
                target = objects[0]
                resp = requests.get(f"http://localhost:4141/interact?agent=hardware_tester&target={target}")
                if resp.status_code == 200:
                    interaction = resp.json()
                    print(f"   Interacted with {target}: {interaction.get('outcome', '')[:60]}...")
    
    # Get final stats
    resp = requests.get("http://localhost:4141/stats")
    if resp.status_code == 200:
        stats = resp.json()
        print(f"\n📊 Final stats: {stats['agents_connected']} agents, {stats['tiles_generated']} tiles")
        print(f"   Hardware health: {stats['hardware']['health']}")
    
    print("\n✅ Hardware test agent completed.")

def main():
    """Run the hardware-integrated MUD server."""
    import argparse
    import time as ttime
    
    parser = argparse.ArgumentParser(description="JC1 Hardware-Integrated Edge MUD Server")
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=4141, help='Port to bind to')
    parser.add_argument('--test', action='store_true', help='Run hardware test agent')
    parser.add_argument('--test-delay', type=int, default=3, help='Seconds to wait before test')
    
    args = parser.parse_args()
    
    print(f"""
🚀 JC1 HARDWARE-INTEGRATED EDGE MUD SERVER
==========================================
⚡ Real Hardware Monitoring + Plato MUD
🔧 Hardware ID: {hardware_monitor.hardware_id}
📡 Server: http://{args.host}:{args.port}
🏗️ Rooms: {len(rooms)} hardware-integrated rooms
💾 Memory: {hardware_monitor.get_memory_usage().get('used_mb', 0)}MB used
🌡️ Temperature: {list(hardware_monitor.get_temperature().values())[0] if hardware_monitor.get_temperature() and isinstance(hardware_monitor.get_temperature(), dict) else 0}°C

🎮 Hardware-Integrated Features:
  • Real-time hardware telemetry in every room
  • Hardware-aware latency simulation
  • Hardware-dependent interaction outcomes
  • Constraint checking before agent connections
  • Hardware event logging
  • Edge-optimized for Jetson Orin Nano 8GB

🧪 Test with:
  curl http://localhost:{args.port}/connect?agent=test
  curl http://localhost:{args.port}/hardware-telemetry
  curl http://localhost:{args.port}/move?agent=test&room=edge-training
  curl http://localhost:{args.port}/interact?agent=test&target=cuda-monitor
  curl http://localhost:{args.port}/stats
""")
    
    # Start server in background thread
    import threading
    server_thread = threading.Thread(target=app.run, args=(args.host, args.port), kwargs={'debug': False, 'threaded': True})
    server_thread.daemon = True
    server_thread.start()
    
    # Wait for server to start
    ttime.sleep(2)
    
    # Run test agent if requested
    if args.test:
        ttime.sleep(args.test_delay)
        run_hardware_test_agent()
    
    # Keep running
    try:
        while True:
            ttime.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Hardware-integrated MUD server shutting down...")

if __name__ == '__main__':
    main()
