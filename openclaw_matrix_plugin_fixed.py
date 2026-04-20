#!/usr/bin/env python3
"""
OpenClaw Matrix Plugin - Fixed Version
Enables decentralized communication between Plato instances on their own hardware.
"""

import json
import time
import hashlib
import logging
from datetime import datetime
from typing import Dict, List, Optional

# Try to import Matrix SDK
try:
    from matrix_client.client import MatrixClient
    MATRIX_AVAILABLE = True
except ImportError:
    MATRIX_AVAILABLE = False
    print("⚠️  Matrix SDK not installed. Run: pip install matrix-client")

class MatrixOpenClawPlugin:
    """OpenClaw plugin for Matrix.org decentralized communication."""
    
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.client = None
        self.connected = False
        self.hardware_id = self._get_hardware_id()
        
        # Statistics
        self.stats = {
            "messages_sent": 0,
            "messages_received": 0,
            "files_transferred": 0,
            "connections_established": 0,
            "errors": 0
        }
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("MatrixOpenClawPlugin")
        
        print("🚀 Matrix OpenClaw Plugin Initialized")
        print(f"   Hardware ID: {self.hardware_id}")
        print(f"   Matrix Available: {MATRIX_AVAILABLE}")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from file or defaults."""
        default_config = {
            "matrix": {
                "homeserver": "https://matrix.org",
                "user_id": None,
                "access_token": None,
                "device_id": "openclaw_jc1"
            },
            "fleet": {
                "coordination_room": "#fleet-coordination:matrix.org",
                "hardware_rooms": {
                    "jc1": "#jc1-hardware:matrix.org"
                }
            }
        }
        
        return default_config
    
    def _get_hardware_id(self) -> str:
        """Get unique hardware identifier for this instance."""
        try:
            import socket
            import uuid
            
            # Combine hostname and MAC address
            hostname = socket.gethostname()
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                           for elements in range(0, 8*6, 8)][::-1])
            
            # Create hash-based ID
            combined = f"{hostname}_{mac}"
            hw_id = hashlib.md5(combined.encode()).hexdigest()[:12]
            
            return f"jetson_{hw_id}"
        except:
            return "simulated_hardware"
    
    def connect(self) -> bool:
        """Connect to Matrix homeserver."""
        if not MATRIX_AVAILABLE:
            self.logger.error("Matrix SDK not available")
            return False
        
        try:
            homeserver = self.config["matrix"]["homeserver"]
            user_id = self.config["matrix"]["user_id"]
            access_token = self.config["matrix"]["access_token"]
            
            if not user_id or not access_token:
                self.logger.error("Matrix user_id or access_token not configured")
                return False
            
            self.client = MatrixClient(homeserver)
            self.client.access_token = access_token
            self.client.user_id = user_id
            
            # Test connection
            self.client.get_display_name()
            
            self.connected = True
            self.stats["connections_established"] += 1
            
            self.logger.info(f"Connected to Matrix as {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to Matrix: {e}")
            self.stats["errors"] += 1
            return False
    
    def beam_to_ship(self, ship_id: str, message: Dict, files: List = None) -> bool:
        """
        Beam message to another Plato instance (ship).
        """
        if not self.connected:
            self.logger.error("Not connected to Matrix")
            return False
        
        try:
            # Format message for transmission
            formatted_message = self._format_message_for_transmission(message)
            
            # Determine target room
            target_room = self._get_room_for_ship(ship_id)
            
            # Send message
            self.client.send_message(target_room, json.dumps(formatted_message))
            
            self.stats["messages_sent"] += 1
            self.logger.info(f"Beamed message to {ship_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to beam to {ship_id}: {e}")
            self.stats["errors"] += 1
            return False
    
    def sync_fleet_state(self) -> Dict:
        """
        Sync hardware state across fleet.
        """
        if not self.connected:
            return {"error": "Not connected to Matrix"}
        
        try:
            # Get hardware telemetry
            hardware_state = self._get_hardware_state()
            
            # Broadcast to fleet
            self._broadcast_hardware_telemetry(hardware_state)
            
            return {
                "hardware_synced": True,
                "timestamp": datetime.now().isoformat(),
                "hardware_id": self.hardware_id
            }
            
        except Exception as e:
            self.logger.error(f"Failed to sync fleet state: {e}")
            return {"error": str(e)}
    
    def _format_message_for_transmission(self, message: Dict) -> Dict:
        """Format message for Matrix transmission."""
        return {
            "plato_fleet_message": True,
            "version": "1.0",
            "sender": self.client.user_id if self.connected else "unknown",
            "sender_hardware": self.hardware_id,
            "timestamp": datetime.now().isoformat(),
            "message_id": hashlib.md5(str(time.time()).encode()).hexdigest()[:8],
            "content": message
        }
    
    def _get_hardware_state(self) -> Dict:
        """Get current hardware state."""
        # Simulated hardware state for testing
        return {
            "hardware_id": self.hardware_id,
            "timestamp": time.time(),
            "memory": {"used_mb": 4840, "total_mb": 7619, "percent": 63},
            "cpu": {"usage_percent": 45, "temperature_c": 62},
            "simulated": True
        }
    
    def _get_room_for_ship(self, ship_id: str) -> str:
        """Get appropriate room for communicating with a ship."""
        # Default to fleet coordination room
        return self.config["fleet"]["coordination_room"]
    
    def _broadcast_hardware_telemetry(self, telemetry: Dict):
        """Broadcast hardware telemetry to fleet."""
        message = {
            "type": "hardware_telemetry",
            "sender": self.hardware_id,
            "telemetry": telemetry,
            "timestamp": time.time()
        }
        
        formatted = self._format_message_for_transmission(message)
        
        # Broadcast to hardware room
        hw_room = self.config["fleet"]["hardware_rooms"].get("jc1")
        if hw_room and self.connected:
            try:
                self.client.send_message(hw_room, json.dumps(formatted))
                self.logger.debug("Broadcast hardware telemetry")
            except Exception as e:
                self.logger.error(f"Failed to broadcast telemetry: {e}")
    
    def get_stats(self) -> Dict:
        """Get plugin statistics."""
        return {
            **self.stats,
            "connected": self.connected,
            "hardware_id": self.hardware_id,
            "timestamp": datetime.now().isoformat()
        }
    
    def disconnect(self):
        """Disconnect from Matrix."""
        if self.connected and self.client:
            try:
                # Cleanup would go here
                pass
            except:
                pass
        
        self.connected = False
        self.client = None
        self.logger.info("Disconnected from Matrix")

def test_plugin():
    """Test the Matrix plugin."""
    print("🧪 Testing Matrix OpenClaw Plugin")
    print("=" * 40)
    
    plugin = MatrixOpenClawPlugin()
    
    print("\n1. Configuration:")
    print(f"   Hardware ID: {plugin.hardware_id}")
    print(f"   Matrix Available: {MATRIX_AVAILABLE}")
    
    print("\n2. Simulated Operations:")
    
    # Simulate hardware state
    hw_state = plugin._get_hardware_state()
    print(f"   Hardware State: {hw_state.get('hardware_id')}")
    
    # Simulate message formatting
    test_msg = {"type": "test", "content": "Hello Fleet"}
    formatted = plugin._format_message_for_transmission(test_msg)
    print(f"   Message Formatted: {formatted.get('message_id')}")
    
    # Get stats
    stats = plugin.get_stats()
    print(f"\n3. Plugin Stats:")
    print(f"   Messages Sent: {stats['messages_sent']}")
    print(f"   Connected: {stats['connected']}")
    
    print("\n✅ Plugin test complete")
    print("\n📋 Next steps:")
    print("   1. Install matrix-client: pip install matrix-client")
    print("   2. Configure Matrix credentials")
    print("   3. Connect to homeserver")
    print("   4. Start beaming messages to fleet!")
    
    return plugin

if __name__ == "__main__":
    test_plugin()