# Phase 3: Fleet Coordination Protocol

## Message Types for Plato Fleet

### 1. Hardware Telemetry Broadcast
```json
{
  "type": "hardware_telemetry",
  "sender": "@jc1:jetson.local",
  "timestamp": "2026-04-20T12:15:00Z",
  "hardware": {
    "id": "jetson_14249243",
    "type": "edge",
    "model": "Orin Nano 8GB",
    "telemetry": {
      "memory": {"used_mb": 4840, "total_mb": 7619, "percent": 63},
      "cpu": {"usage_percent": 45, "temperature_c": 62},
      "gpu": {"usage_percent": 30, "temperature_c": 65},
      "power": {"estimated_w": 12.5, "limit_w": 15}
    }
  },
  "plato_context": {
    "instance_id": "jc1_plato_v1",
    "rooms_active": 4,
    "agents_connected": 3,
    "constraints_active": ["memory_limit", "thermal_limit"]
  }
}
```

### 2. Plato Room State Sync
```json
{
  "type": "room_state",
  "sender": "@jc1:jetson.local",
  "room": "engine-room",
  "state": {
    "agents_present": ["jc1_edge_agent", "test_agent_1776715042"],
    "tiles_available": ["hardware_monitor", "constraint_checker", "fleet_comms"],
    "interactions_recent": [
      {"agent": "jc1_edge_agent", "action": "check_hardware", "timestamp": "2026-04-20T12:14:30Z"},
      {"agent": "test_agent_1776715042", "action": "look_around", "timestamp": "2026-04-20T12:14:45Z"}
    ]
  }
}
```

### 3. Fleet Coordination Request
```json
{
  "type": "fleet_coordination",
  "sender": "@jc1:jetson.local",
  "request_id": "req_20260420_121500",
  "action": "distribute_compute",
  "parameters": {
    "task": "model_inference",
    "model": "phi-4",
    "input_size_mb": 50,
    "deadline_seconds": 300,
    "constraints": {
      "memory_min_mb": 2048,
      "power_max_w": 10,
      "temperature_max_c": 70
    }
  },
  "target_nodes": ["@fm:workstation.local", "@oracle1:cloud.local"],
  "response_required": true
}
```

### 4. Bottle Transfer (File)
```json
{
  "type": "bottle_transfer",
  "sender": "@jc1:jetson.local",
  "bottle_id": "bottle_20260420_121500_abc123",
  "metadata": {
    "source": "jc1_edge_agent",
    "created_at": "2026-04-20T12:15:00Z",
    "priority": "normal",
    "hardware_aware": true
  },
  "content_type": "application/json",
  "content_size_bytes": 2048,
  "content_hash": "sha256:abc123...",
  "delivery_confirmation_required": true
}
```

### 5. Constraint Negotiation
```json
{
  "type": "constraint_negotiation",
  "sender": "@jc1:jetson.local",
  "negotiation_id": "neg_20260420_121500",
  "constraint_type": "memory_allocation",
  "current_state": {
    "available_mb": 2779,
    "committed_mb": 4840,
    "requests_pending": 2
  },
  "proposal": {
    "allocate_mb": 512,
    "duration_seconds": 600,
    "priority": "medium",
    "compensation": "intelligence_tiles"
  },
  "counterparties": ["@fm:workstation.local"]
}
```

### 6. Intelligence Tile Sharing
```json
{
  "type": "tile_sharing",
  "sender": "@jc1:jetson.local",
  "tile_id": "tile_hardware_pattern_001",
  "tile_type": "pattern_recognition",
  "domain": "hardware_thermal",
  "content": {
    "pattern": "temperature_ramp_65c",
    "confidence": 0.78,
    "observations": 15,
    "compounded_value": 0.65,
    "recommendation": "Reduce load when temp > 60°C"
  },
  "sharing_policy": "fleet_wide",
  "attribution_required": true
}
```

## Room Structure for Fleet

### 1. Main Coordination Room
```
#fleet-coordination:matrix.org
Purpose: General fleet coordination, announcements, status updates
Members: All fleet nodes + human operators
Encryption: End-to-end for sensitive discussions
```

### 2. Hardware Telemetry Rooms
```
#jc1-hardware:jetson.local
Purpose: JC1-specific hardware telemetry and alerts
Members: JC1, FM (monitoring), Oracle1 (analysis), Human operators

#fm-workstation:workstation.local  
Purpose: FM workstation hardware and protocol development
Members: FM, JC1 (edge testing), Oracle1 (coordination)

#oracle1-cloud:cloud.local
Purpose: Oracle1 cloud instance operations
Members: Oracle1, FM, JC1, Human operators
```

### 3. Plato Instance Rooms
```
#jc1-plato:jetson.local
Purpose: JC1 Plato instance operations and room state
Members: JC1 agents, Fleet coordination agents

#fm-plato:workstation.local
Purpose: FM Plato instance and protocol development
Members: FM agents, Protocol testers

#oracle1-plato:cloud.local
Purpose: Oracle1 Plato cloud operations
Members: Oracle1 agents, Cloud coordination
```

### 4. Special Purpose Rooms
```
#kimiclaw-bridge:matrix.org
Purpose: Bridge between Matrix and Kimiclaw's Kimi models
Members: Kimiclaw instance, Human operators, Fleet coordinators
Special: Human key-in required for model access

#constraint-negotiation:matrix.org
Purpose: Automated constraint negotiation between nodes
Members: All fleet nodes (automated agents)
Encryption: Required for resource allocation details

#intelligence-tiles:matrix.org
Purpose: Sharing compounded intelligence tiles
Members: All fleet nodes, Read-only for some
Retention: Long-term storage of valuable patterns
```

## Implementation Details

### Matrix Event Types
```python
class PlatoMatrixEventTypes:
    HARDWARE_TELEMETRY = "org.plato.fleet.hardware_telemetry"
    ROOM_STATE = "org.plato.fleet.room_state"
    FLEET_COORDINATION = "org.plato.fleet.coordination"
    BOTTLE_TRANSFER = "org.plato.fleet.bottle_transfer"
    CONSTRAINT_NEGOTIATION = "org.plato.fleet.constraint_negotiation"
    TILE_SHARING = "org.plato.fleet.tile_sharing"
    
    # Response types
    COORDINATION_RESPONSE = "org.plato.fleet.coordination_response"
    CONSTRAINT_RESPONSE = "org.plato.fleet.constraint_response"
    TRANSFER_CONFIRMATION = "org.plato.fleet.transfer_confirmation"
```

### Edge-Optimized Message Format
```python
class EdgeOptimizedMessage:
    """Message format optimized for edge hardware constraints"""
    
    def __init__(self, sender, message_type, data):
        self.sender = sender
        self.type = message_type
        self.data = self._compress_for_edge(data)
        self.timestamp = time.time()
        self.priority = self._calculate_priority(message_type, data)
    
    def _compress_for_edge(self, data):
        """Compress data for edge transmission"""
        # Use efficient serialization
        # Remove unnecessary metadata
        # Batch small messages
        return optimized_data
    
    def _calculate_priority(self, message_type, data):
        """Calculate transmission priority based on content"""
        priorities = {
            "hardware_telemetry": "low",  # Regular updates
            "constraint_violation": "high",  # Immediate action needed
            "fleet_coordination": "medium",  # Important but not urgent
            "tile_sharing": "low",  # Can wait for good connection
        }
        return priorities.get(message_type, "medium")
```

### Hardware-Aware Routing
```python
class HardwareAwareRouter:
    """Route messages based on hardware capabilities"""
    
    def __init__(self, hardware_monitor):
        self.hardware = hardware_monitor
        self.routing_table = {}
    
    def should_send_now(self, message, target):
        """Decide if message should be sent now or queued"""
        current_state = self.hardware.get_telemetry()
        
        # Check constraints
        if current_state["memory"]["used_percent"] > 80:
            # High memory usage, defer non-critical messages
            if message.priority == "low":
                return False
        
        if current_state["temperature"]["max_c"] > 70:
            # High temperature, reduce network activity
            if message.priority in ["low", "medium"]:
                return False
        
        # Check network connectivity
        if not self._has_good_connection():
            # Poor connection, only send critical messages
            return message.priority == "high"
        
        return True
    
    def _has_good_connection(self):
        """Check if we have good network connectivity"""
        # Implementation depends on network monitoring
        return True
```

## Security Model

### 1. Identity Verification
- Each Plato instance has Matrix identity tied to hardware ID
- Hardware signatures for critical operations
- Certificate-based authentication for fleet nodes

### 2. End-to-End Encryption
- Sensitive data (constraints, intelligence tiles) always encrypted
- Room-based encryption keys
- Forward secrecy for long-running conversations

### 3. Access Control
- Room membership controls
- Message type restrictions per room
- Rate limiting per node
- Audit logging for coordination events

### 4. Kimiclaw Special Security
- Human key-in required for model access
- Proxy pattern for Kimi interactions
- Separate encryption for model queries/responses
- Audit trail for all Kimi interactions

## Testing Protocol

### Phase 3A: Basic Message Flow
1. JC1 → FM: Hardware telemetry broadcast
2. FM → JC1: Acknowledgment
3. JC1 → Fleet: Room state sync
4. Fleet → JC1: Coordination request

### Phase 3B: File Transfer
1. JC1 creates test bottle
2. JC1 → FM: Bottle transfer initiation
3. FM acknowledges receipt
4. FM verifies content hash
5. FM → JC1: Transfer confirmation

### Phase 3C: Constraint Negotiation
1. JC1 needs memory allocation
2. JC1 → FM: Constraint negotiation request
3. FM evaluates own constraints
4. FM → JC1: Negotiation response (accept/reject/counter)
5. JC1 adjusts based on response

### Phase 3D: Intelligence Sharing
1. JC1 compounds hardware pattern
2. JC1 creates intelligence tile
3. JC1 → Fleet: Tile sharing broadcast
4. Fleet nodes store tile
5. Oracle1 analyzes fleet-wide patterns

## Integration with Existing Plato

### 1. Bottle System Integration
```python
class MatrixBottleBridge:
    """Bridge between Plato bottle system and Matrix"""
    
    def send_bottle_via_matrix(self, bottle, target_nodes):
        """Send bottle through Matrix instead of GitHub"""
        # Convert bottle to Matrix message
        message = self._bottle_to_matrix_message(bottle)
        
        # Send to each target node
        for node in target_nodes:
            self.matrix_client.send_message(
                room_id=f"#bottle-transfer-{bottle.id}",
                content=message
            )
    
    def receive_bottle_from_matrix(self, message):
        """Receive bottle from Matrix message"""
        bottle = self._matrix_message_to_bottle(message)
        
        # Process in Plato bottle system
        self.plato_bottle_system.process_incoming(bottle)
```

### 2. Room State Integration
```python
class MatrixRoomStateSync:
    """Sync Plato room state with Matrix"""
    
    def sync_room_to_matrix(self, room_id):
        """Sync Plato room state to Matrix room"""
        room_state = self.plato.get_room_state(room_id)
        
        matrix_message = {
            "type": "room_state",
            "room": room_id,
            "state": room_state,
            "timestamp": time.time()
        }
        
        # Send to fleet coordination room
        self.matrix_client.send_message(
            room_id="#fleet-coordination",
            content=matrix_message
        )
```

### 3. Constraint Integration
```python
class MatrixConstraintNegotiator:
    """Negotiate constraints via Matrix"""
    
    def negotiate_with_fleet(self, constraint_type, requirements):
        """Negotiate resource allocation with fleet"""
        
        # Create negotiation request
        request = {
            "type": "constraint_negotiation",
            "constraint_type": constraint_type,
            "requirements": requirements,
            "sender": self.matrix_identity
        }
        
        # Send to constraint negotiation room
        response = self.matrix_client.send_and_wait(
            room_id="#constraint-negotiation",
            content=request,
            timeout=30
        )
        
        # Process fleet response
        return self._process_negotiation_response(response)
```

## Next Steps for Phase 3

### Immediate Implementation
1. Define message schema in code
2. Create Matrix event handlers for each message type
3. Implement hardware-aware routing
4. Create test suite for message flows

### Integration Tasks
1. Connect to existing bottle system
2. Integrate with room state management
3. Add constraint negotiation to hardware monitor
4. Create intelligence tile sharing mechanism

### Testing Plan
1. Unit tests for message serialization/deserialization
2. Integration tests for JC1 ↔ FM communication
3. Load tests for edge hardware constraints
4. Security tests for encryption and authentication

## Success Metrics for Phase 3

### Technical Metrics
- Message delivery latency < 5 seconds (same hardware)
- File transfer success rate > 99%
- Constraint negotiation completion < 30 seconds
- Memory overhead < 100MB per node

### Operational Metrics
- Fleet coordination events per day
- Intelligence tiles shared per week
- Successful constraint negotiations
- Human interventions required (should decrease over time)

### Strategic Metrics
- Reduction in GitHub dependency for coordination
- Increase in autonomous fleet decisions
- Improvement in hardware utilization across fleet
- Growth in compounded intelligence value