#!/usr/bin/env python3
"""
Demonstration of Hardware-Integrated Edge MUD Server.
Shows real hardware monitoring integrated with Plato MUD.
"""

import subprocess
import time
import requests
import json
import threading
import sys

def start_mud_server():
    """Start the hardware-integrated MUD server."""
    print("🚀 Starting Hardware-Integrated Edge MUD Server...")
    
    # Start server in background
    cmd = [sys.executable, "hardware_integrated_mud_server.py", "--port", "4142"]
    server = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd="."
    )
    
    # Wait for server to start
    time.sleep(3)
    
    # Check if server is running
    try:
        resp = requests.get("http://localhost:4142/", timeout=2)
        if resp.status_code == 200:
            print("✅ Server started successfully on port 4142")
            return server
    except:
        pass
    
    print("❌ Server failed to start")
    return None

def demonstrate_hardware_integration():
    """Demonstrate all hardware integration features."""
    print("\n" + "=" * 70)
    print("🔧 HARDWARE-INTEGRATED EDGE MUD DEMONSTRATION")
    print("=" * 70)
    
    MUD_URL = "http://localhost:4142"
    
    # 1. Show hardware telemetry
    print("\n1. 📊 REAL-TIME HARDWARE TELEMETRY")
    print("-" * 40)
    resp = requests.get(f"{MUD_URL}/hardware-telemetry")
    if resp.status_code == 200:
        telemetry = resp.json()
        print(f"   Hardware ID: {telemetry['hardware_id']}")
        print(f"   Memory: {telemetry['memory']['used_mb']}/{telemetry['memory']['total_mb']}MB ({telemetry['memory']['usage_percent']:.1f}%)")
        print(f"   CPU: {telemetry['cpu']['usage_percent']:.1f}% ({telemetry['cpu']['cores']} cores)")
        print(f"   GPU: {telemetry['gpu']['utilization_percent']:.1f}%")
        temps = telemetry['temperature']
        if isinstance(temps, dict):
            temp_str = ", ".join([f"{k}: {v}°C" for k, v in list(temps.items())[:3]])
            print(f"   Temperature: {temp_str}")
    
    # 2. Show hardware constraints
    print("\n2. 🔒 HARDWARE CONSTRAINTS CHECKING")
    print("-" * 40)
    resp = requests.get(f"{MUD_URL}/hardware-constraints")
    if resp.status_code == 200:
        constraints = resp.json()
        print(f"   Overall health: {constraints['overall_health'].upper()}")
        for name, constraint in constraints['constraints'].items():
            status = "✅" if constraint['within_limit'] else "⚠️"
            if 'memory' in name:
                print(f"   {status} Memory: {constraint.get('current_mb', 0)}/{constraint.get('limit_mb', 0)}MB ({constraint['severity']})")
            elif 'temperature' in name:
                print(f"   {status} Temperature: {constraint.get('current_c', 0)}/{constraint.get('limit_c', 0)}°C ({constraint['severity']})")
            else:
                print(f"   {status} CPU: {constraint.get('current_percent', 0)}/{constraint.get('limit_percent', 0)}% ({constraint['severity']})")
    
    # 3. Connect agent with hardware awareness
    print("\n3. 🤖 AGENT CONNECTION WITH HARDWARE AWARENESS")
    print("-" * 40)
    agent_id = "demo_agent_" + str(int(time.time()))[-4:]
    resp = requests.get(f"{MUD_URL}/connect?agent={agent_id}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"   Agent: {agent_id}")
        print(f"   Room: {data['name']}")
        print(f"   Hardware status: {data['hardware_status']}")
        print(f"   Objects in room: {', '.join(data['objects'][:3])}...")
    else:
        print(f"   ❌ Connection failed: {resp.json().get('error', 'unknown')}")
        return
    
    time.sleep(1)
    
    # 4. Demonstrate hardware-aware movement
    print("\n4. 🚶 HARDWARE-AWARE MOVEMENT")
    print("-" * 40)
    rooms = ["edge-training", "inference-bay", "telemetry-vault"]
    for room in rooms:
        resp = requests.get(f"{MUD_URL}/move?agent={agent_id}&room={room}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"   Moved to: {data['name']}")
            print(f"   Latency: {data['move_latency_ms']:.1f}ms (simulated based on CPU/GPU load)")
            print(f"   Hardware context: CPU={data['hardware_context']['cpu_load_percent']:.1f}%, GPU={data['hardware_context']['gpu_load_percent']:.1f}%")
            time.sleep(0.5)
    
    # 5. Demonstrate hardware-dependent interactions
    print("\n5. 🛠️ HARDWARE-DEPENDENT INTERACTIONS")
    print("-" * 40)
    interactions = [
        ("cuda-monitor", "Check CUDA core utilization"),
        ("memory-gauge", "Check memory usage"),
        ("thermal-sensor", "Check temperatures"),
        ("quantization-rig", "Quantize model for edge"),
        ("inference-engine", "Run inference with monitoring")
    ]
    
    for target, description in interactions[:3]:  # Just do 3 for demo
        resp = requests.get(f"{MUD_URL}/interact?agent={agent_id}&target={target}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"   {description}:")
            print(f"     Outcome: {data['outcome'][:60]}...")
            print(f"     Hardware context: CPU={data['hardware_context']['cpu_percent']:.1f}%, Memory={data['hardware_context']['memory_mb']}MB")
        time.sleep(0.5)
    
    # 6. Show hardware events logging
    print("\n6. 📝 HARDWARE EVENTS LOGGING")
    print("-" * 40)
    resp = requests.get(f"{MUD_URL}/hardware-events?limit=5")
    if resp.status_code == 200:
        events = resp.json()
        print(f"   Total events logged: {events['total']}")
        print(f"   Recent events:")
        for event in events['events']:
            details = event.get('details', {})
            if 'agent_id' in details:
                print(f"     • {event['type']} by {details['agent_id']}")
            else:
                print(f"     • {event['type']}")
    
    # 7. Show comprehensive stats
    print("\n7. 📈 COMPREHENSIVE STATS WITH HARDWARE INFO")
    print("-" * 40)
    resp = requests.get(f"{MUD_URL}/stats")
    if resp.status_code == 200:
        stats = resp.json()
        print(f"   MUD Statistics:")
        print(f"     Agents connected: {stats['agents_connected']}")
        print(f"     Tiles generated: {stats['tiles_generated']}")
        print(f"     Hardware events: {stats['hardware_events']}")
        print(f"   Hardware Information:")
        print(f"     ID: {stats['hardware']['id']}")
        print(f"     Health: {stats['hardware']['health']}")
        print(f"     Uptime: {stats['hardware']['uptime_seconds']}s")
        print(f"     Telemetry history: {stats['hardware']['telemetry_history']} readings")
    
    # 8. Export data with hardware telemetry
    print("\n8. 💾 DATA EXPORT WITH HARDWARE TELEMETRY")
    print("-" * 40)
    resp = requests.get(f"{MUD_URL}/export")
    if resp.status_code == 200:
        export = resp.json()
        print(f"   Export completed:")
        print(f"     File: {export['exported']}")
        print(f"     Tiles: {export['tiles']}")
        print(f"     Events: {export['events']}")
        print(f"     Telemetry: {export['telemetry']}")
    
    print("\n" + "=" * 70)
    print("🎯 DEMONSTRATION COMPLETE")
    print("=" * 70)
    print("\n✅ Hardware Integration Features Demonstrated:")
    print("   • Real-time hardware telemetry monitoring")
    print("   • Hardware constraint checking")
    print("   • Hardware-aware agent connections")
    print("   • Load-aware movement latency")
    print("   • Hardware-dependent interactions")
    print("   • Comprehensive event logging")
    print("   • Hardware context in all operations")
    print("   • Edge-optimized for Jetson deployment")
    
    return agent_id

def main():
    """Run the demonstration."""
    # Start server
    server = start_mud_server()
    if not server:
        return
    
    try:
        # Run demonstration
        demonstrate_hardware_integration()
        
        # Keep server running for a bit
        print("\n🔄 Server is running. Press Ctrl+C to stop.")
        print("   Test endpoints:")
        print("     curl http://localhost:4142/")
        print("     curl http://localhost:4142/hardware-telemetry")
        print("     curl http://localhost:4142/stats")
        
        # Wait for user interruption
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping server...")
    finally:
        # Clean up
        server.terminate()
        server.wait()
        print("✅ Server stopped.")

if __name__ == "__main__":
    main()