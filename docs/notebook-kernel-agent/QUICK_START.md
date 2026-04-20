# Notebook Kernel Agent: Quick Start Guide

**Time to first boarding**: < 4 minutes  
**Prerequisites**: Python 3.11+, 2GB RAM  
**Difficulty**: Beginner

## 🚀 Get Started in 4 Minutes

### **Step 1: Clone the Repository**
```bash
git clone https://github.com/Lucineer/notebook-kernel-agent
cd notebook-kernel-agent
```

### **Step 2: Install Dependencies**
```bash
pip install -r requirements.txt
```

### **Step 3: Create the Agent**
```python
from agent import NotebookKernelAgent

agent = NotebookKernelAgent()
print(f"✅ Agent created: {agent.name}")
print(f"  Version: {agent.manifest['version']}")
print(f"  Tools in pack: {list(agent.tools.tools.keys())}")
print(f"  Perspectives: {agent.manifest['perspectives']}")
```

**Output:**
```
✅ Agent created: notebook-kernel-agent
  Version: 1.0.0
  Tools in pack: ['code_executor', 'markdown_renderer', 'query_processor', 'tile_retriever', 'trace_recorder']
  Perspectives: ['first-person', 'architect', 'debug', 'play']
```

### **Step 4: Test Perspective Switching**
```python
# Switch to architect perspective
result = agent.switch_perspective("architect")

print(f"Perspective switch: {result['success']}")
print(f"From: {result['old_perspective']}")
print(f"To: {result['new_perspective']}")
print(f"Changes: {result['changes']}")
```

**Expected Output:**
```
Perspective switch: True
From: first-person
To: architect
Changes: {'code_execution': 'analytical', 'markdown_rendering': 'annotated', 'query_processing': 'analytical', 'focus': 'system structure'}
```

### **Step 5: Test Tool Execution**
```python
# Test code execution
code_result = agent.tools.execute(
    "code_executor",
    code="print('Hello from notebook kernel!')",
    language="python"
)

print(f"Code execution: {code_result['success']}")
print(f"Output: {code_result['output']}")
print(f"Trace recorded: {code_result['trace_recorded']}")
```

**Expected Output:**
```
Code execution: True
Output: Hello from notebook kernel!
Trace recorded: True
```

### **Step 6: Board a Test Room**
```python
# Create a simple test room
class TestRoom:
    def __init__(self):
        self.name = "test-room"
        self.tools = {}
    
    def install_tool_pack(self, tool_pack):
        self.tools.update(tool_pack.tools)
        return {"success": True, "tools_installed": len(tool_pack.tools)}

# Board the test room
test_room = TestRoom()
boarding_result = agent.board(test_room)

print(f"Boarding: {boarding_result['success']}")
print(f"Room: {boarding_result['room']}")
print(f"Tools installed in room: {boarding_result.get('tools_installed', 0)}")
```

**Expected Output:**
```
Boarding: True
Room: test-room
Tools installed in room: 5
```

## 📁 Project Structure

```
notebook-kernel-agent/
├── agent.py              # Main agent implementation
├── manifest.json        # Agent identity and capabilities
├── requirements.txt    # Python dependencies
├── tools/             # 5 portable tools
│   ├── code_executor.py
│   ├── markdown_renderer.py
│   ├── query_processor.py
│   ├── tile_retriever.py
│   └── trace_recorder.py
├── perspectives/      # 4 cognitive perspectives
│   ├── first_person.py
│   ├── architect.py
│   ├── debug.py
│   └── play.py
├── boarding/         # Room boarding logic
├── traces/          # Git-auditable trace system
└── tests/           # Test suite
```

## ⚙️ Configuration

### **Agent Manifest (manifest.json)**
```json
{
  "name": "notebook-kernel-agent",
  "version": "1.0.0",
  "type": "boarding_agent",
  
  "capabilities": [
    "code_execution",
    "markdown_rendering", 
    "query_processing",
    "tile_retrieval",
    "trace_recording"
  ],
  
  "perspectives": [
    "first-person",
    "architect", 
    "debug",
    "play"
  ],
  
  "constraints": {
    "requires": ["room_with_computer"],
    "provides": ["portable_tool_pack"],
    "compatible_with": ["plato-tile-spec", "i2i-protocol"]
  },
  
  "default_perspective": "first-person",
  "trace_enabled": true,
  "git_integration": true
}
```

### **Environment Variables**
```bash
export NOTEBOOK_KERNEL_TRACE_DIR=/var/traces  # Custom trace directory
export NOTEBOOK_KERNEL_LOG_LEVEL=DEBUG        # Debug logging
export NOTEBOOK_KERNEL_GIT_INTEGRATION=false  # Disable git commits
export NOTEBOOK_KERNEL_DEFAULT_PERSPECTIVE=architect  # Change default
```

## 🔧 Common Operations

### **1. Basic Agent Operations**
```python
from agent import NotebookKernelAgent

agent = NotebookKernelAgent()

# Switch perspectives
agent.switch_perspective("debug")

# Execute code
result = agent.execute_code(
    code="import math\nprint(math.sqrt(16))",
    language="python"
)

# Process query
response = agent.process_query(
    query="How do I use the tile forge agent?",
    context={"room": "tile-forge-agent"}
)

# Get agent status
status = agent.get_status()
print(f"Agent: {status['name']}")
print(f"Perspective: {status['perspective']}")
print(f"Tools available: {status['tools']}")
print(f"Boarding history: {len(status['boarding_history'])} rooms")
```

### **2. Room Boarding Operations**
```python
from agent import NotebookKernelAgent
from tile_forge_agent.room import TileForgeRoom
from constraint_engine_agent.provider import ConstraintEngineProvider

# Create agent and rooms
agent = NotebookKernelAgent()
tile_room = TileForgeRoom()
tile_room.start()

constraint_provider = ConstraintEngineProvider()
constraint_provider.start()

# Board tile room
boarding1 = agent.board(tile_room)
print(f"Boarded tile room: {boarding1['success']}")

# Use tile room tools through agent
tile_result = agent.execute_in_room(
    room="tile-forge-agent",
    operation="forge_tiles",
    parameters={"input_dir": "/docs", "output_dir": "/tiles"}
)

# Board constraint provider
boarding2 = agent.board(constraint_provider)
print(f"Boarded constraint provider: {boarding2['success']}")

# Check constraints through agent
constraint_check = agent.execute_in_room(
    room="constraint-engine-agent",
    operation="check_constraints",
    parameters={
        "room_id": "notebook-kernel",
        "operation": "execute_code",
        "code": "print('test')"
    }
)
```

### **3. Perspective-Based Operations**
```python
from agent import NotebookKernelAgent

agent = NotebookKernelAgent()

# First-person: Direct execution
agent.switch_perspective("first-person")
direct_result = agent.execute_code("print('Hello')")

# Architect: Analytical view
agent.switch_perspective("architect")
analysis_result = agent.process_query(
    "Analyze the system architecture",
    context={"system": "git-agent-ecosystem"}
)

# Debug: Problem solving
agent.switch_perspective("debug")
debug_result = agent.execute_code(
    "def buggy_function():\n    return 1/0",
    language="python"
)

# Play: Exploration
agent.switch_perspective("play")
play_result = agent.process_query(
    "What if we tried a different approach?",
    context={"experiment": "alternative-design"}
)
```

### **4. Trace Recording Operations**
```python
from agent import NotebookKernelAgent

agent = NotebookKernelAgent()

# Enable/disable tracing
agent.configure_tracing(enabled=True, git_integration=True)

# Execute with automatic tracing
result = agent.execute_code(
    code="x = [1, 2, 3]\nprint(sum(x))",
    language="python",
    trace_metadata={"purpose": "test", "user": "developer"}
)

# View recent traces
traces = agent.get_recent_traces(limit=5)
for trace in traces:
    print(f"Trace {trace['id']}: {trace['event_type']} at {trace['timestamp']}")

# Export traces
exported = agent.export_traces(
    format="markdown",
    directory="/tmp/traces",
    since="2026-04-18T00:00:00Z"
)
print(f"Exported {exported['count']} traces to {exported['directory']}")
```

## 🐛 Troubleshooting

### **Common Issues & Solutions**

#### **Issue: "Cannot board room: incompatible interface"**
**Solution:** Ensure room implements Room with Computer pattern:
```python
# Room must have these methods
class CompatibleRoom:
    def install_tool_pack(self, tool_pack):
        # Install tool pack
        pass
    
    def check_constraints(self, operation, **kwargs):
        # Check constraints
        pass
```

#### **Issue: "Tool not found in pack"**
**Solution:** Check tool names and ensure pack is loaded:
```python
# List available tools
tools = list(agent.tools.tools.keys())
print(f"Available tools: {tools}")

# Reload tool pack if needed
agent.reload_tools()
```

#### **Issue: "Perspective switch failed"**
**Solution:** Check valid perspective names:
```python
valid_perspectives = agent.manifest["perspectives"]
print(f"Valid perspectives: {valid_perspectives}")

# Switch to valid perspective
if "architect" in valid_perspectives:
    agent.switch_perspective("architect")
```

#### **Issue: "Trace recording disabled"**
**Solution:** Enable tracing:
```bash
export NOTEBOOK_KERNEL_TRACE_ENABLED=true
# Or programmatically
agent.configure_tracing(enabled=True)
```

### **Debug Mode**
```bash
# Enable debug logging
export NOTEBOOK_KERNEL_LOG_LEVEL=DEBUG
python -c "from agent import NotebookKernelAgent; agent = NotebookKernelAgent()"

# Or programmatically
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📊 Performance Tuning

### **For High-Volume Execution**
```python
agent = NotebookKernelAgent()

# Optimize for performance
agent.configure_performance(
    cache_size=1000,           # Cache 1000 tool executions
    parallel_tools=4,          # Run up to 4 tools in parallel
    trace_compression=True,    # Compress trace data
    memory_limit="2GB"         # Limit memory usage
)

# Batch operations
operations = [
    {"tool": "code_executor", "code": f"print({i})"} 
    for i in range(100)
]

results = agent.execute_batch(operations)
print(f"Processed {len(results)} operations")
print(f"Success rate: {sum(1 for r in results if r['success'])/len(results)*100:.1f}%")
```

### **For Low-Latency Requirements**
```python
agent = NotebookKernelAgent()

# Optimize for low latency
agent.configure_latency(
    preload_tools=True,        # Preload tool implementations
    warmup_operations=100,     # Warm up with 100 operations
    connection_pooling=True,   # Pool connections to rooms
    predictive_boarding=True   # Predict and pre-board likely rooms
)

# Measure latency
import time
start = time.time()
result = agent.execute_code("print('latency test')")
latency = time.time() - start

print(f"Operation latency: {latency*1000:.1f}ms")
print(f"Tool execution: {result.get('execution_time_ms', 0):.1f}ms")
print(f"Trace recording: {result.get('trace_time_ms', 0):.1f}ms")
```

## 🔗 Integration Examples

### **1. Integration with Tile Forge Agent**
```python
from agent import NotebookKernelAgent
from tile_forge_agent.room import TileForgeRoom

# Create and start
agent = NotebookKernelAgent()
tile_room = TileForgeRoom()
tile_room.start()

# Board with architect perspective
agent.switch_perspective("architect")
agent.board(tile_room)

# Use tile room through agent
result = agent.execute_in_room(
    room="tile-forge-agent",
    operation="forge_tiles",
    parameters={
        "input_dir": "/path/to/docs",
        "output_dir": "/path/for/tiles",
        "quality_threshold": 0.5
    }
)

# Analyze results
if result["success"]:
    print(f"Created {result['tiles_created']} tiles")
    print(f"Performance: {result['tiles_per_second']:.1f} tiles/sec")
    
    # Retrieve relevant tiles
    tiles = agent.tools.execute(
        "tile_retriever",
        query="tile forging best practices",
        tiles=result["tiles"]
    )
```

### **2. Integration with Constraint Engine**
```python
from agent import NotebookKernelAgent
from constraint_engine_agent.provider import ConstraintEngineProvider

agent = NotebookKernelAgent()
constraint_provider = ConstraintEngineProvider()
constraint_provider.start()

# Board constraint provider
agent.board(constraint_provider)

# All agent operations now checked against constraints
def safe_operation(operation, **kwargs):
    # Check constraints first
    constraint_check = agent.execute_in_room(
        room="constraint-engine-agent",
        operation="check_constraints",
        parameters={
            "room_id": "notebook-kernel",
            "operation": operation,
            **kwargs
        }
    )
    
    if not constraint_check["allowed"]:
        print(f"❌ Operation blocked: {constraint_check['reason']}")
        return None
    
    # Execute if allowed
    return agent.execute_operation(operation, **kwargs)

# Safe execution
result = safe_operation(
    "execute_code",
    code="print('Hello')",
    language="python"
)
```

### **3. Plato Stack Integration**
```python
from agent import NotebookKernelAgent
import plato_address
import plato_hooks
import plato_bridge

agent = NotebookKernelAgent()

# Register with plato-address
address = plato_address.register(
    entity=agent,
    address="notebook-kernel@agents.plato"
)

# Add plato-hooks for agent events
hooks = plato_hooks.attach(agent, {
    "pre_execution": agent.validate_operation,
    "post_execution": agent.record_trace,
    "perspective_switch": agent.log_perspective_change,
    "boarding": agent.notify_boarding
})

# Connect via plato-bridge to other agents
bridge = plato_bridge.connect(
    source="notebook-kernel",
    target="tile-forge@rooms.plato"
)

# Use TUTOR_JUMP for context navigation
tutor_result = agent.tutor_jump("delegation_patterns")
print(f"TUTOR_JUMP to: {tutor_result['anchor']}")
print(f"Context tiles: {len(tutor_result['tiles'])}")
```

### **4. REST API Integration**
```python
from agent import NotebookKernelAgent
from flask import Flask, request, jsonify

app = Flask(__name__)
agent = NotebookKernelAgent()

@app.route('/api/execute', methods=['POST'])
def execute_code():
    data = request.json
    result = agent.execute_code(
        code=data['code'],
        language=data.get('language', 'python'),
        perspective=data.get('perspective', 'first-person')
    )
    return jsonify(result)

@app.route('/api/query', methods=['POST'])
def process_query():
    data = request.json
    result = agent.process_query(
        query=data['query'],
        context=data.get('context', {}),
        perspective=data.get('perspective', 'first-person')
    )
    return jsonify(result)

@app.route('/api/board', methods=['POST'])
def board_room():
    data = request.json
    # Room would be provided or created based on data
    result = agent.board(room_implementation)
    return jsonify(result)

if __name__ == '__main__':
    app.run(port=5000)
```

### **5. Git-Auditable Workflow**
```python
from agent import NotebookKernelAgent
import git

agent = NotebookKernelAgent()
agent.configure_tracing(enabled=True, git_integration=True)

# Start a git-auditable session
session_id = agent.start_session(
    purpose="documentation analysis",
    user="developer",
    repository="/path/to/repo"
)

# All operations are traced and git-committed
results = []
operations = [
    "analyze architecture",
    "extract patterns",
    "generate documentation",
    "validate constraints"
]

for op in operations:
    result = agent.process_query(
        query=f"Help me {op}",
        context={"session": session_id},
        perspective="architect"
    )
    results.append(result)
    
    # Each operation auto-committed to git
    print(f"Operation '{op}' → Commit {result.get('commit_hash', 'N/A')}")

# End session and generate report
session_report = agent.end_session(session_id)
print(f"Session completed: {session_report['operations']} operations")
print(f"Total commits: {session_report['commits']}")
print(f"Trace file: {session_report['traceprint(f"Trace file: {session_report['trace_file']}")

## 🧪 Testing Your Setup

### **Run Built-in Tests**
```bash
python -m pytest tests/ -v
```

### **Create Your Own Test**
```python
import unittest
from agent import NotebookKernelAgent

class TestNotebookKernel(unittest.TestCase):
    def test_perspective_switching(self):
        agent = NotebookKernelAgent()
        
        result = agent.switch_perspective("architect")
        self.assertTrue(result["success"])
        self.assertEqual(agent.perspective, "architect")
    
    def test_code_execution(self):
        agent = NotebookKernelAgent()
        
        result = agent.execute_code("print('test')", "python")
        self.assertTrue(result["success"])
        self.assertIn("test", result["output"])
        
if __name__ == "__main__":
    unittest.main()
```

### **Performance Test**
```python
import time
from agent import NotebookKernelAgent

agent = NotebookKernelAgent()

# Test with multiple perspectives and operations
perspectives = ["first-person", "architect", "debug", "play"]
operations = 100

start = time.time()
for i in range(operations):
    perspective = perspectives[i % len(perspectives)]
    agent.switch_perspective(perspective)
    
    result = agent.execute_code(
        code=f"print('Operation {i} from {perspective}')",
        language="python"
    )
elapsed = time.time() - start

print(f"Processed {operations} operations in {elapsed:.2f}s")
print(f"Throughput: {operations/elapsed:.1f} ops/sec")
print(f"Average per operation: {elapsed/operations*1000:.1f}ms")
```

## 📈 Next Steps

### **After Quick Start:**
1. **Explore Architecture**: Read [ARCHITECTURE.md](./ARCHITECTURE.md)
2. **Learn Advanced Features**: Check perspective customization and tool extension
3. **See Integration Examples**: Review how to connect with Tile Forge and Constraint Engine agents
4. **Join Ecosystem**: Connect with other git-agents in the fleet
5. **Contribute**: Submit issues and pull requests

### **Production Deployment:**
1. **Dockerize**: `docker build -t notebook-kernel-agent .`
2. **Orchestrate**: Deploy to Kubernetes with multiple agent instances
3. **Monitor**: Set up metrics for perspective usage, tool execution, boarding frequency
4. **Scale**: Add more agent instances for different user groups
5. **Secure**: Configure authentication and authorization for boarding

## 🆘 Getting Help

### **Resources:**
- **Documentation**: [docs/](./)
- **GitHub Issues**: https://github.com/Lucineer/notebook-kernel-agent/issues
- **Community**: Discord/Slack (links in README)
- **Examples**: `/examples` directory

### **Common Questions:**

**Q: How do I add custom tools to the tool pack?**  
**A:** Extend the ToolPack class and implement your tool following the tool interface.

**Q: Can I create custom perspectives?**  
**A:** Yes, create a new perspective class and add it to the perspectives registry.

**Q: How do I handle boarding failures?**  
**A:** Check the boarding result and handle errors appropriately. Rooms must implement the Room with Computer interface.

**Q: Can I use this with non-Python rooms?**  
**A:** Yes, as long as the room implements the required interface methods.

## 🎉 Congratulations!

You've successfully:
- ✅ Created a Notebook Kernel Agent
- ✅ Tested perspective switching
- ✅ Executed code with the agent
- ✅ Learned basic operations and configuration
- ✅ Explored integration possibilities

**Next:** Dive deeper into the [architecture](./ARCHITECTURE.md) or explore integration examples with other git-agents.

---

*Quick Start Guide created: 2026-04-18 11:55 AKDT*  
*Notebook Kernel Agent v1.0.0 | Boarding Agent with Tool Pack Pattern*
