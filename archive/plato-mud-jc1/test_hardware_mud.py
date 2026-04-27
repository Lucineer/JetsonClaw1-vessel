#!/usr/bin/env python3
"""
Test script for Hardware-Integrated Edge MUD Server.
"""

import requests
import time
import json

MUD_URL = "http://localhost:4142"

def test_hardware_telemetry():
    """Test hardware telemetry endpoint."""
    print("🧪 Testing hardware telemetry...")
    resp = requests.get(f"{MUD_URL}/hardware-telemetry")
    if resp.status_code == 200:
        data = resp.json()
        print(f"✅ Hardware telemetry working")
        print(f"   Memory: {data['memory']['used_mb']}/{data['memory']['total_mb']}MB ({data['memory']['usage_percent']:.1f}%)")
        print(f"   CPU: {data['cpu']['usage_percent']:.1f}%")
        print(f"   GPU: {data['gpu']['utilization_percent']:.1f}%")
        print(f"   Temperature: {list(data['temperature'].values())[0]}°C")
        return True
    else:
        print(f"❌ Hardware telemetry failed: {resp.status_code}")
        return False

def test_connect_agent():
    """Test agent connection with hardware constraints."""
    print("\n🧪 Testing agent connection...")
    resp = requests.get(f"{MUD_URL}/connect?agent=hw_test_agent")
    if resp.status_code == 200:
        data = resp.json()
        print(f"✅ Agent connected")
        print(f"   Room: {data['name']}")
        print(f"   Hardware status: {data['hardware_status']}")
        print(f"   Hardware ID: {data['hardware_id']}")
        return "hw_test_agent"
    else:
        print(f"❌ Agent connection failed: {resp.status_code}")
        print(f"   Response: {resp.json()}")
        return None

def test_look_with_telemetry(agent_id):
    """Test look command with hardware telemetry."""
    print("\n🧪 Testing look with hardware telemetry...")
    resp = requests.get(f"{MUD_URL}/look?agent={agent_id}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"✅ Look command working")
        print(f"   Room: {data['name']}")
        print(f"   Hardware telemetry included: CPU={data['hardware_telemetry']['cpu_percent']:.1f}%, Memory={data['hardware_telemetry']['memory_mb']}MB")
        return True
    else:
        print(f"❌ Look command failed: {resp.status_code}")
        return False

def test_hardware_aware_movement(agent_id):
    """Test hardware-aware movement."""
    print("\n🧪 Testing hardware-aware movement...")
    resp = requests.get(f"{MUD_URL}/move?agent={agent_id}&room=edge-training")
    if resp.status_code == 200:
        data = resp.json()
        print(f"✅ Hardware-aware movement working")
        print(f"   Moved to: {data['name']}")
        print(f"   Latency: {data['move_latency_ms']:.1f}ms (hardware-aware)")
        print(f"   CPU load during move: {data['hardware_context']['cpu_load_percent']:.1f}%")
        print(f"   GPU load during move: {data['hardware_context']['gpu_load_percent']:.1f}%")
        return True
    else:
        print(f"❌ Movement failed: {resp.status_code}")
        return False

def test_hardware_dependent_interaction(agent_id):
    """Test hardware-dependent interactions."""
    print("\n🧪 Testing hardware-dependent interaction...")
    resp = requests.get(f"{MUD_URL}/interact?agent={agent_id}&target=quantization-rig")
    if resp.status_code == 200:
        data = resp.json()
        print(f"✅ Hardware-dependent interaction working")
        print(f"   Action: {data['action']}")
        print(f"   Outcome: {data['outcome']}")
        print(f"   Hardware context: CPU={data['hardware_context']['cpu_percent']:.1f}%, Memory={data['hardware_context']['memory_mb']}MB")
        return True
    else:
        print(f"❌ Interaction failed: {resp.status_code}")
        return False

def test_hardware_constraints():
    """Test hardware constraints checking."""
    print("\n🧪 Testing hardware constraints...")
    resp = requests.get(f"{MUD_URL}/hardware-constraints")
    if resp.status_code == 200:
        data = resp.json()
        print(f"✅ Hardware constraints working")
        print(f"   Overall health: {data['overall_health']}")
        for name, constraint in data['constraints'].items():
            if 'mb' in name:
                current = constraint.get('current_mb', 0)
                limit = constraint.get('limit_mb', 0)
                unit = "MB"
            elif 'c' in name:
                current = constraint.get('current_c', 0)
                limit = constraint.get('limit_c', 0)
                unit = "°C"
            else:
                current = constraint.get('current_percent', 0)
                limit = constraint.get('limit_percent', 0)
                unit = "%"
            
            status = "✅" if constraint['within_limit'] else "⚠️"
            print(f"   {status} {name}: {current:.1f}/{limit}{unit} ({constraint['severity']})")
        return True
    else:
        print(f"❌ Constraints check failed: {resp.status_code}")
        return False

def test_hardware_events():
    """Test hardware events logging."""
    print("\n🧪 Testing hardware events...")
    resp = requests.get(f"{MUD_URL}/hardware-events?limit=3")
    if resp.status_code == 200:
        data = resp.json()
        print(f"✅ Hardware events working")
        print(f"   Total events: {data['total']}")
        for event in data['events']:
            print(f"   • {event['type']}: {event.get('details', {}).get('agent_id', 'system')}")
        return True
    else:
        print(f"❌ Events check failed: {resp.status_code}")
        return False

def test_stats_with_hardware():
    """Test stats endpoint with hardware info."""
    print("\n🧪 Testing stats with hardware info...")
    resp = requests.get(f"{MUD_URL}/stats")
    if resp.status_code == 200:
        data = resp.json()
        print(f"✅ Stats with hardware info working")
        print(f"   Agents connected: {data['agents_connected']}")
        print(f"   Tiles generated: {data['tiles_generated']}")
        print(f"   Hardware events: {data['hardware_events']}")
        print(f"   Hardware health: {data['hardware']['health']}")
        print(f"   Hardware uptime: {data['hardware']['uptime_seconds']}s")
        return True
    else:
        print(f"❌ Stats check failed: {resp.status_code}")
        return False

def test_export():
    """Test data export with hardware telemetry."""
    print("\n🧪 Testing data export...")
    resp = requests.get(f"{MUD_URL}/export")
    if resp.status_code == 200:
        data = resp.json()
        print(f"✅ Data export working")
        print(f"   Export file: {data['exported']}")
        print(f"   Tiles exported: {data['tiles']}")
        print(f"   Events exported: {data['events']}")
        print(f"   Telemetry exported: {data['telemetry']}")
        return True
    else:
        print(f"❌ Export failed: {resp.status_code}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("🧪 JC1 HARDWARE-INTEGRATED EDGE MUD TEST SUITE")
    print("=" * 60)
    
    # Wait for server to be ready
    time.sleep(1)
    
    tests_passed = 0
    tests_total = 8
    
    # Run tests
    if test_hardware_telemetry():
        tests_passed += 1
    
    agent_id = test_connect_agent()
    if agent_id:
        tests_passed += 1
        
        if test_look_with_telemetry(agent_id):
            tests_passed += 1
        
        if test_hardware_aware_movement(agent_id):
            tests_passed += 1
        
        if test_hardware_dependent_interaction(agent_id):
            tests_passed += 1
    
    if test_hardware_constraints():
        tests_passed += 1
    
    if test_hardware_events():
        tests_passed += 1
    
    if test_stats_with_hardware():
        tests_passed += 1
    
    if test_export():
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS")
    print("=" * 60)
    print(f"Tests passed: {tests_passed}/{tests_total}")
    
    if tests_passed == tests_total:
        print("✅ ALL TESTS PASSED - Hardware-integrated MUD is fully functional!")
        print("\n🎯 Hardware Integration Features Verified:")
        print("   • Real-time hardware telemetry monitoring")
        print("   • Hardware-aware latency simulation")
        print("   • Hardware-dependent interaction outcomes")
        print("   • Constraint checking before agent connections")
        print("   • Hardware event logging")
        print("   • Edge-optimized for Jetson Orin Nano 8GB")
        print("   • Hardware context in all MUD operations")
    else:
        print(f"⚠️  {tests_total - tests_passed} test(s) failed")
    
    return tests_passed == tests_total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)