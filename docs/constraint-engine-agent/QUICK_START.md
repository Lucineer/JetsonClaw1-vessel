# Constraint Engine Agent: Quick Start Guide

**Time to first constraint check**: < 3 minutes  
**Prerequisites**: Python 3.11+, 2GB RAM  
**Difficulty**: Beginner

## 🚀 Get Started in 3 Minutes

### **Step 1: Clone the Repository**
```bash
git clone https://github.com/Lucineer/constraint-engine-agent
cd constraint-engine-agent
```

### **Step 2: Install Dependencies**
```bash
pip install -r requirements.txt
```

### **Step 3: Start the Provider**
```bash
python provider.py start
```
**Output:**
```
2026-04-18 11:36:10,294 - constraint-engine-agent - INFO - Starting constraint-engine-agent provider
2026-04-18 11:36:10,294 - constraint-engine-agent - INFO - Authentication enabled
2026-04-18 11:36:10,294 - constraint-engine-agent - INFO - Service interfaces ready
2026-04-18 11:36:10,294 - constraint-engine-agent - INFO - constraint-engine-agent provider started
2026-04-18 11:36:10,294 - constraint-engine-agent - INFO - Tools available: ['security_checker', 'authentication_validator', 'permission_checker', 'resource_validator', 'memory_checker', 'cpu_checker', 'semantic_analyzer', 'type_checker', 'reference_validator', 'pedagogical_rules', 'learning_path_enforcer', 'difficulty_adjuster']
```

### **Step 4: Test Constraint Checking**
```python
from provider import ConstraintEngineProvider

# Create and start provider
provider = ConstraintEngineProvider()
provider.start()

# Test security constraint
result = provider.check_constraints(
    room_id="test-room",
    operation="sudo apt-get update",
    auth_token="test-token-123"
)

print(f"Operation allowed: {result['allowed']}")
print(f"Reason: {result.get('reason', 'No reason provided')}")
print(f"Tools checked: {result.get('checked_tools', [])}")
```

**Expected Output:**
```
Operation allowed: False
Reason: Security violation: sudo\s+
Tools checked: ['security_checker', 'authentication_validator']
```

### **Step 5: Test Safe Operation**
```python
# Test a safe operation
safe_result = provider.check_constraints(
    room_id="test-room",
    operation="print('Hello, World!')",
    auth_token="test-token-123",
    user_role="developer"
)

print(f"Safe operation allowed: {safe_result['allowed']}")
print(f"Tools checked: {safe_result.get('checked_tools', [])}")
```

**Expected Output:**
```
Safe operation allowed: True
Tools checked: ['security_checker', 'authentication_validator', 'permission_checker']
```

### **Step 6: Connect to a Room**
```python
# Connect constraint engine to a room
from room import SomeRoom  # Your room implementation

room = SomeRoom()
room.start()

# Connect constraint provider
room.connect_constraint_provider(provider)

# Now all room operations are automatically checked
result = room.execute_operation("calculate_sum", numbers=[1, 2, 3])
print(f"Room operation result: {result}")
```

## 📁 Project Structure

```
constraint-engine-agent/
├── provider.py              # Main provider implementation
├── registry.yaml           # Provider configuration
├── requirements.txt       # Python dependencies
├── tools/                # 12 constraint tools
│   ├── security/
│   │   ├── security_checker.py
│   │   ├── authentication_validator.py
│   │   └── permission_checker.py
│   ├── resource/
│   │   ├── resource_validator.py
│   │   ├── memory_checker.py
│   │   └── cpu_checker.py
│   ├── semantic/
│   │   ├── semantic_analyzer.py
│   │   ├── type_checker.py
│   │   └── reference_validator.py
│   └── pedagogical/
│       ├── pedagogical_rules.py
│       ├── learning_path_enforcer.py
│       └── difficulty_adjuster.py
├── interfaces/           # Service interfaces
│   ├── rest_api.py
│   ├── websocket.py
│   └── direct.py
├── clients/             # Client implementations
│   ├── python_client.py
│   ├── javascript_client.js
│   └── go_client.go
└── tests/              # Test suite
```

## ⚙️ Configuration

### **Basic Configuration (registry.yaml)**
```yaml
name: constraint-engine-agent
version: 1.0.0
type: tool_provider

authentication:
  enabled: true
  token_expiry: 3600  # 1 hour
  require_mfa: false

tools:
  security:
    - security_checker
    - authentication_validator
    - permission_checker
  resource:
    - resource_validator
    - memory_checker
    - cpu_checker
  semantic:
    - semantic_analyzer
    - type_checker
    - reference_validator
  pedagogical:
    - pedagogical_rules
    - learning_path_enforcer
    - difficulty_adjuster

interfaces:
  rest:
    port: 8080
    enabled: true
  websocket:
    port: 8081
    enabled: true
  direct:
    enabled: true

logging:
  level: INFO
  file: /var/log/constraint-engine.log
```

### **Environment Variables**
```bash
export CONSTRAINT_ENGINE_PORT=9090           # Custom port
export CONSTRAINT_ENGINE_AUTH=false          # Disable authentication
export CONSTRAINT_ENGINE_LOG_LEVEL=DEBUG     # Debug logging
export CONSTRAINT_ENGINE_ALLOWED_ORIGINS=*   # CORS settings
```

## 🔧 Common Operations

### **1. Basic Constraint Checking**
```python
from provider import ConstraintEngineProvider

provider = ConstraintEngineProvider()
provider.start()

# Check a single operation
result = provider.check_constraints(
    room_id="my-room",
    operation="process_data",
    auth_token="valid-token",
    user_role="admin",
    resources={"memory": "2GB", "cpu": "50%"}
)

if result["allowed"]:
    print("✅ Operation allowed")
else:
    print(f"❌ Operation blocked: {result['reason']}")
```

### **2. Batch Constraint Checking**
```python
# Check multiple operations at once
operations = [
    {"operation": "read_file", "path": "/etc/passwd"},
    {"operation": "calculate", "expression": "2+2"},
    {"operation": "download", "url": "http://example.com"}
]

results = []
for op in operations:
    result = provider.check_constraints(
        room_id="batch-room",
        operation=op["operation"],
        **{k: v for k, v in op.items() if k != "operation"}
    )
    results.append(result)

print(f"Checked {len(results)} operations")
print(f"Allowed: {sum(1 for r in results if r['allowed'])}")
print(f"Blocked: {sum(1 for r in results if not r['allowed'])}")
```

### **3. Custom Constraint Rules**
```python
# Add custom security rules
provider.tools["security_checker"].add_rule(
    pattern=r"dangerous_pattern",
    action="block",
    reason="Custom dangerous pattern detected",
    severity="high"
)

# Add custom resource limits
provider.tools["resource_validator"].set_limits(
    memory="4GB",
    cpu="80%",
    storage="100GB",
    network="100Mbps"
)

# Enable/disable specific tools
provider.configure_tools(
    enabled=["security_checker", "resource_validator"],
    disabled=["pedagogical_rules", "difficulty_adjuster"]
)
```

### **4. Real-time Monitoring**
```python
# Monitor constraint decisions in real-time
def constraint_callback(result):
    print(f"Constraint check: {result['allowed']}")
    if not result["allowed"]:
        print(f"  Blocked by: {result.get('blocking_tool')}")
        print(f"  Reason: {result.get('reason')}")

# Subscribe to constraint events
provider.subscribe(constraint_callback)

# All subsequent checks will trigger callback
provider.check_constraints(
    room_id="monitored-room",
    operation="test_operation"
)
```

## 🐛 Troubleshooting

### **Common Issues & Solutions**

#### **Issue: "Authentication token required"**
**Solution:** Provide a valid auth token or disable authentication:
```bash
export CONSTRAINT_ENGINE_AUTH=false
python provider.py start
```

#### **Issue: "Connection refused" on port 8080**
**Solution:** Change port or check if port is already in use:
```bash
export CONSTRAINT_ENGINE_PORT=9090
python provider.py start
```

#### **Issue: "Tool not found" errors**
**Solution:** Ensure all tools are properly installed:
```bash
pip install -r requirements.txt --force-reinstall
```

#### **Issue: Performance slowdown with many checks**
**Solution:** Enable caching and batch processing:
```python
provider.configure_performance(
    cache_size=1000,
    batch_size=100,
    parallel_checks=4
)
```

### **Debug Mode**
```bash
# Enable debug logging
export CONSTRAINT_ENGINE_LOG_LEVEL=DEBUG
python provider.py start

# Or programmatically
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📊 Performance Tuning

### **For High-Volume Environments**
```python
provider = ConstraintEngineProvider()
provider.start()

# Optimize for high throughput
provider.configure_performance(
    cache_size=5000,           # Cache 5000 constraint decisions
    batch_size=250,            # Process 250 checks per batch
    parallel_checks=8,         # Use 8 parallel checkers
    compression=True,          # Compress cached decisions
    ttl=300                    # Cache entries expire after 5 minutes
)

# Monitor performance
stats = provider.get_performance_stats()
print(f"Checks per second: {stats['checks_per_second']}")
print(f"Cache hit rate: {stats['cache_hit_rate']}%")
print(f"Average latency: {stats['avg_latency_ms']}ms")
```

### **For Low-Latency Requirements**
```python
provider = ConstraintEngineProvider()
provider.start()

# Optimize for low latency
provider.configure_latency(
    preload_cache=True,        # Preload common decisions
    predictive_checking=True,  # Predict and pre-check likely operations
    connection_pooling=True,   # Pool connections to tools
    warmup_operations=1000     # Warm up with 1000 operations
)

# Get latency metrics
latency = provider.get_latency_metrics()
print(f"P50 latency: {latency['p50']}ms")
print(f"P95 latency: {latency['p95']}ms")
print(f"P99 latency: {latency['p99']}ms")
```

## 🔗 Integration Examples

### **1. Integration with Tile Forge Agent**
```python
from provider import ConstraintEngineProvider
from tile_forge_agent.room import TileForgeRoom

# Create providers
constraint_provider = ConstraintEngineProvider()
constraint_provider.start()

tile_room = TileForgeRoom()
tile_room.start()

# Connect constraint provider to tile room
tile_room.connect_constraint_provider(constraint_provider)

# Now all tile forging operations are constrained
result = tile_room.forge_tiles(
    input_dir="/path/to/docs",
    output_dir="/path/for/tiles"
)
# Automatically checked by constraint engine
```

### **2. Integration with Notebook Kernel Agent**
```python
from provider import ConstraintEngineProvider
from notebook_kernel_agent.agent import NotebookKernelAgent

# Create providers
constraint_provider = ConstraintEngineProvider()
constraint_provider.start()

notebook_agent = NotebookKernelAgent()

# Agent can check constraints before boarding rooms
constraint_check = constraint_provider.check_constraints(
    room_id="notebook-room",
    operation="agent_boarding",
    agent_type="notebook-kernel",
    agent_capabilities=["code_execution", "markdown_rendering"]
)

if constraint_check["allowed"]:
    notebook_agent.board(target_room)
else:
    print(f"Cannot board: {constraint_check['reason']}")
```

### **3. Plato Stack Integration**
```python
from provider import ConstraintEngineProvider
import plato_address
import plato_hooks
import plato_bridge

# Create addressable provider
constraint_provider = ConstraintEngineProvider()
constraint_provider.start()

# Register with plato-address
address = plato_address.register(
    entity=constraint_provider,
    address="constraint-engine@providers.plato"
)

# Add plato-hooks for constraint events
hooks = plato_hooks.attach(constraint_provider, {
    "pre_check": constraint_provider.validate_input,
    "post_check": constraint_provider.log_decision,
    "violation": constraint_provider.notify_violation
})

# Connect via plato-bridge to other services
bridge = plato_bridge.connect(
    source="constraint-engine",
    target="audit-log@plato"
)
```

### **4. REST API Integration**
```python
import requests

# Using the REST API
response = requests.post(
    "http://localhost:8080/check_constraints",
    json={
        "room_id": "test-room",
        "operation": "process_data",
        "auth_token": "valid-token-123",
        "parameters": {"data": "test"}
    }
)

result = response.json()
print(f"Allowed: {result['allowed']}")
print(f"Reason: {result.get('reason')}")
```

### **5. WebSocket Integration**
```python
import asyncio
import websockets
import json

async def constraint_client():
    async with websockets.connect("ws://localhost:8081") as websocket:
        # Subscribe to constraint events
        await websocket.send(json.dumps({
            "action": "subscribe",
            "room_id": "my-room"
        }))
        
        # Receive real-time constraint decisions
        async for message in websocket:
            decision = json.loads(message)
            print(f"Constraint decision: {decision}")

asyncio.run(constraint_client())
```

## 🧪 Testing Your Setup

### **Run Built-in Tests**
```bash
python -m pytest tests/ -v
```

### **Create Your Own Test**
```python
import unittest
from provider import ConstraintEngineProvider

class TestConstraintEngine(unittest.TestCase):
    def test_security_blocking(self):
        provider = ConstraintEngineProvider()
        provider.start()
        
        result = provider.check_constraints(
            room_id="test-room",
            operation="sudo rm -rf /",
            auth_token="test-token"
        )
        
        self.assertFalse(result["allowed"])
        self.assertIn("security", result.get("severity", ""))
    
    def test_safe_operation(self):
        provider = ConstraintEngineProvider()
        provider.start()
        
        result = provider.check_constraints(
            room_id="test-room",
            operation="print('Hello')",
            auth_token="test-token"
        )
        
        self.assertTrue(result["allowed"])
        
if __name__ == "__main__":
    unittest.main()
```

### **Performance Test**
```python
import time
from provider import ConstraintEngineProvider

provider = ConstraintEngineProvider()
provider.start()

# Test with 1000 operations
operations = [f"operation_{i}" for i in range(1000)]

start = time.time()
results = []
for op in operations:
    result = provider.check_constraints(
        room_id="performance-test",
        operation=op,
        auth_token="test-token"
    )
    results.append(result)
elapsed = time.time() - start

print(f"Processed {len(results)} operations in {elapsed:.2f}s")
print(f"Throughput: {len(results)/elapsed:.1f} ops/sec")
print(f"Allowed: {sum(1 for r in results if r['allowed'])}")
print(f"Blocked: {sum(1 for r in results if not r['allowed'])}")
```

## 📈 Next Steps

### **After Quick Start:**
1. **Explore Architecture**: Read [ARCHITECTURE.md](./ARCHITECTURE.md)
2. **Learn Advanced Features**: Check constraint customization
3. **See Integration Examples**: Review how to connect with other git-agents
4. **Join Ecosystem**: Connect with Tile Forge and Notebook Kernel agents
5. **Contribute**: Submit issues and pull requests

### **Production Deployment:**
1. **Dockerize**: `docker build -t constraint-engine-agent .`
2. **Orchestrate**: Deploy to Kubernetes with multiple replicas
3. **Monitor**: Set up metrics, alerts, and dashboards
4. **Scale**: Add more provider instances behind load balancer
5. **Secure**: Configure proper authentication and encryption

## 🆘 Getting Help

### **Resources:**
- **Documentation**: [docs/](./)
- **GitHub Issues**: https://github.com/Lucineer/constraint-engine-agent/issues
- **Community**: Discord/Slack (links in README)
- **Examples**: `/examples` directory

### **Common Questions:**

**Q: How do I add custom constraint rules?**  
**A:** Extend the appropriate tool class or use the `add_rule()` method.

**Q: Can I disable specific constraint tools?**  
**A:** Yes, use `configure_tools(enabled=[...], disabled=[...])`.

**Q: How do I handle constraint violations in my application?**  
**A:** Check the `allowed` field and handle the `reason` appropriately.

**Q: Can I use this with non-Python applications?**  
**A:** Yes, use the REST API or WebSocket interface.

## 🎉 Congratulations!

You've successfully:
- ✅ Started the Constraint Engine Agent provider
- ✅ Tested security constraint checking
- ✅ Learned basic operations and configuration
- ✅ Explored integration possibilities

**Next:** Dive deeper into the [architecture](./ARCHITECTURE.md) or explore integration examples with other git-agents.

---
*Quick Start Guide created: 2026-04-18 11:48 AKDT*  
*Constraint Engine Agent v1.0.0 | Tool Provider Pattern*