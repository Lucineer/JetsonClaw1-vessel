                return f"Simulated Temperature: 45°C. Within safe range."
    
    def _get_batching_outcome(self, hardware_state):
        """Outcome for power-aware-batching object."""
        if hardware_state["real_hardware"]:
            power = hardware_state["telemetry"]["power"]
            power_w = power.get("total_w", power.get("estimated_w", 0))
            
            if power_w > 12:
                return f"Power high: {power_w:.1f}W. Using efficient batching: small batches, frequent pauses."
            elif power_w > 8:
                return f"Power moderate: {power_w:.1f}W. Balanced batching: medium batches."
            else:
                return f"Power low: {power_w:.1f}W. Aggressive batching: large batches for throughput."
        else:
            return "Simulated Batching: Medium batches for balanced performance."
    
    def _get_training_outcome(self, hardware_state):
        """Outcome for memory-aware-trainer object."""
        if hardware_state["real_hardware"]:
            memory = hardware_state["telemetry"]["memory"]
            used_mb = memory.get("used_mb", 0)
            total_mb = memory.get("total_mb", 8192)
            
            available = total_mb - used_mb
            if available < 1024:  # Less than 1GB free
                return f"Memory constrained: {available}MB free. Tiny batch size: 2. Training slow."
            elif available < 2048:  # Less than 2GB free
                return f"Memory moderate: {available}MB free. Small batch size: 4."
            else:
                return f"Memory available: {available}MB free. Normal batch size: 8."
        else:
            return "Simulated Training: Batch size: 6. Memory: 3.2GB free."
    
    def _get_optimizer_outcome(self, hardware_state):
        """Outcome for constraint-optimizer object."""
        if hardware_state["real_hardware"]:
            constraints = hardware_state["constraints"].get("constraints", {})
            
            # Find most constrained resource
            constraints_list = []
            for name, constraint in constraints.items():
                if 'mb' in name:
                    usage = constraint.get('current_mb', 0) / constraint.get('limit_mb', 1)
                elif 'c' in name:
                    usage = constraint.get('current_c', 0) / constraint.get('limit_c', 1)
                else:
                    usage = constraint.get('current_w', 0) / constraint.get('limit_w', 1)
                constraints_list.append((name, usage))
            
            constraints_list.sort(key=lambda x: x[1], reverse=True)
            most_constrained = constraints_list[0][0] if constraints_list else "none"
            
            return f"Most constrained: {most_constrained}. Optimizing algorithms for this limitation."
        else:
            return "Simulated Optimizer: Balancing all constraints equally."
    
    def _get_progress_outcome(self, hardware_state):
        """Outcome for progress-monitor object."""
        if hardware_state["real_hardware"]:
            # Simulate training progress based on hardware state
            cpu = hardware_state["telemetry"]["cpu"].get("usage_percent", 0)
            temp = max([
                hardware_state["telemetry"]["temperature"].get("cpu_c", 0),
                hardware_state["telemetry"]["temperature"].get("gpu_c", 0)
            ])
            
            if temp > 70:
                progress = "slow (thermal throttling)"
            elif cpu > 80:
                progress = "moderate (CPU constrained)"
            else:
                progress = "fast (optimal conditions)"
            
            return f"Training progress: {progress}. Adjusting learning rate based on hardware feedback."
        else:
            return "Simulated Progress: Steady training at 42 samples/sec."
    
    def _get_status_outcome(self, hardware_state):
        """Outcome for hardware-status-beacon object."""
        if hardware_state["real_hardware"]:
            health = hardware_state["constraints"].get("overall_health", "unknown")
            return f"Hardware Status Beacon: Transmitting {health} status to fleet. Real hardware telemetry included."
        else:
            return "Simulated Status Beacon: HEALTHY status to fleet. Simulation mode."
    
    def _get_report_outcome(self, hardware_state):
        """Outcome for constraint-report object."""
        if hardware_state["real_hardware"]:
            constraints = hardware_state["constraints"].get("constraints", {})
            report_lines = []
            for name, constraint in constraints.items():
                status = "✅" if constraint.get("within_limit", True) else "⚠️"
                report_lines.append(f"{status} {name}: {constraint.get('severity', 'unknown')}")
            
            return f"Constraint Report:\n" + "\n".join(report_lines)
        else:
            return "Simulated Constraint Report: All constraints within limits."
    
    def _get_fleet_outcome(self, hardware_state):
        """Outcome for fleet-health-feed object."""
        if hardware_state["real_hardware"]:
            telemetry = hardware_state["telemetry"]
            return f"Fleet Health Feed: Memory {telemetry['memory'].get('usage_percent', 0):.1f}%, CPU {telemetry['cpu'].get('usage_percent', 0):.1f}%, Temp {max([telemetry['temperature'].get('cpu_c', 0), telemetry['temperature'].get('gpu_c', 0)])}°C. Real hardware data."
        else:
            return "Fleet Health Feed: Simulated data for testing."
    
    def _generate_hardware_tile(self, agent_id, action, outcome, hardware_state):
        """Generate hardware-aware tile."""
        return {
            "tile_id": f"hardware_tile_{uuid.uuid4().hex[:8]}",
            "agent_id": agent_id,
            "action": action,
            "outcome": outcome,
            "timestamp": int(time.time()),
            "hardware_context": {
                "is_real_hardware": hardware_state["real_hardware"],
                "hardware_id": hardware_state["hardware_id"],
                "health": hardware_state["constraints"].get("overall_health", "unknown") if hardware_state["real_hardware"] else "simulated",
                "constraints": hardware_state["constraints"].get("constraints", {}) if hardware_state["real_hardware"] else {}
            },
            "reward": random.uniform(0.7, 0.95)  # Higher baseline for hardware awareness
        }
    
    def get_system_stats(self):
        """Get complete system statistics."""
        hardware_state = self.get_hardware_state()
        
        return {
            "system": "Hardware-Integrated Edge MUD",
            "version": "hw-1.0",
            "hardware_awareness": hardware_state["real_hardware"],
            "hardware_id": hardware_state["hardware_id"],
            "agents_connected": len(self.agents),
            "tiles_generated": len(self.tiles),
            "rooms_available": len(self.rooms),
            "hardware_health": hardware_state["constraints"].get("overall_health", "unknown") if hardware_state["real_hardware"] else "simulated",
            "constraints": hardware_state["constraints"].get("constraints", {}) if hardware_state["real_hardware"] else {},
            "uptime_seconds": int(time.time() - self.start_time) if hasattr(self, 'start_time') else 0
        }

# Initialize MUD
mud = HardwareIntegratedMUD()

@app.route('/')
def index():
    return jsonify({
        "server": "Hardware-Integrated Edge MUD",
        "version": "hw-1.0",
        "hardware": "REAL" if REAL_HARDWARE else "SIMULATED",
        "device": EDGE_CONFIG["device"],
        "port": EDGE_CONFIG["port"],
        "endpoints": {
            "/hw/connect?agent=NAME": "Connect with hardware awareness",
            "/hw/move?agent=NAME&room=ROOM": "Hardware-aware movement",
            "/hw/interact?agent=NAME&target=OBJECT": "Hardware-aware interaction",
            "/hw/stats": "System statistics with hardware context",
            "/hw/health": "Hardware health check",
            "/hw/telemetry": "Raw hardware telemetry",
            "/hw/history": "Hardware history (last 50 readings)"
        }
    })

@app.route('/hw/connect')
def hw_connect():
    agent = request.args.get('agent', f'hw_agent_{uuid.uuid4().hex[:6]}')
    result = mud.connect_agent(agent)
    return jsonify(result)

@app.route('/hw/move')
def hw_move():
    agent = request.args.get('agent')
    room = request.args.get('room')
    
    if not agent or not room:
        return jsonify({"error": "agent and room required"}), 400
    
    result = mud.move_agent(agent, room)
    return jsonify(result)

@app.route('/hw/interact')
def hw_interact():
    agent = request.args.get('agent')
    target = request.args.get('target')
    
    if not agent or not target:
        return jsonify({"error": "agent and target required"}), 400
    
    result = mud.interact(agent, target)
    return jsonify(result)

@app.route('/hw/stats')
def hw_stats():
    return jsonify(mud.get_system_stats())

@app.route('/hw/health')
def hw_health():
    hardware_state = mud.get_hardware_state()
    
    if hardware_state["real_hardware"]:
        constraints = hardware_state["constraints"].get("constraints", {})
        violations = [k for k, v in constraints.items() if not v.get("within_limit", True)]
        
        return jsonify({
            "hardware": "REAL",
            "health": hardware_state["constraints"].get("overall_health", "unknown"),
            "violations": violations,
            "constraints": constraints,
            "timestamp": hardware_state["timestamp"]
        })
    else:
        return jsonify({
            "hardware": "SIMULATED",
            "health": "simulated_healthy",
            "violations": [],
            "note": "Running in simulation mode",
            "timestamp": hardware_state["timestamp"]
        })

@app.route('/hw/telemetry')
def hw_telemetry():
    hardware_state = mud.get_hardware_state()
    return jsonify(hardware_state)

@app.route('/hw/history')
def hw_history():
    return jsonify({
        "hardware_readings": mud.hardware_history[-20:],  # Last 20 readings
        "total_readings": len(mud.hardware_history),
        "hardware_awareness": "REAL" if REAL_HARDWARE else "SIMULATED"
    })

def run_hardware_integrated_server():
    """Run the hardware-integrated server."""
    print(f"""
🚀 HARDWARE-INTEGRATED EDGE MUD SERVER
======================================
🎯 Real Hardware Awareness: {'✅ ENABLED' if REAL_HARDWARE else '⚠️ SIMULATED'}
📡 http://0.0.0.0:{EDGE_CONFIG['port']}
🔧 Hardware ID: {mud.hardware_id}
⚡ Device: {EDGE_CONFIG['device']}
💾 Memory Limit: {EDGE_CONFIG['memory_limit_mb']}MB
🔋 Power Limit: {EDGE_CONFIG['power_limit_w']}W
🌡️ Temp Limit: {EDGE_CONFIG['temp_limit_c']}°C

🎮 Hardware-Aware Rooms:
  • hardware-command (Real telemetry monitoring)
  • inference-lab (Thermal/power-aware inference)
  • training-bay (Memory-aware training)
  • fleet-comms (Hardware-transparent coordination)

🧪 Test Commands:
  curl http://localhost:{EDGE_CONFIG['port']}/hw/connect?agent=test
  curl http://localhost:{EDGE_CONFIG['port']}/hw/move?agent=test&room=inference-lab
  curl http://localhost:{EDGE_CONFIG['port']}/hw/interact?agent=test&target=adaptive-inference
  curl http://localhost:{EDGE_CONFIG['port']}/hw/health
  curl http://localhost:{EDGE_CONFIG['port']}/hw/telemetry

Starting hardware-integrated server...
    """)
    
    app.run(host='0.0.0.0', port=EDGE_CONFIG['port'], debug=False, threaded=True)

if __name__ == '__main__':
    run_hardware_integrated_server()