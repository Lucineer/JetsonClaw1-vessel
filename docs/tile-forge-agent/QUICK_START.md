# Tile Forge Agent: Quick Start Guide

**Time to first tile**: < 5 minutes  
**Prerequisites**: Python 3.11+, 4GB RAM  
**Difficulty**: Beginner

## 🚀 Get Started in 5 Minutes

### **Step 1: Clone the Repository**
```bash
git clone https://github.com/Lucineer/tile-forge-agent
cd tile-forge-agent
```

### **Step 2: Install Dependencies**
```bash
pip install -r requirements.txt
```

### **Step 3: Start the Room**
```bash
python room.py start
```
**Output:**
```
2026-04-18 11:36:10,184 - tile-forge-agent - INFO - Starting tile-forge-agent room
2026-04-18 11:36:10,184 - tile-forge-agent - INFO - Loading built-in tools
2026-04-18 11:36:10,184 - tile-forge-agent - INFO - Loaded 5 tools
2026-04-18 11:36:10,184 - tile-forge-agent - INFO - Interfaces ready
2026-04-18 11:36:10,184 - tile-forge-agent - INFO - tile-forge-agent room started successfully
Initializing computer with: {'cpu': '2 cores', 'memory': '4GB', 'storage': '10GB'}
```

### **Step 4: Create Test Markdown Files**
```bash
mkdir -p /tmp/test_docs

cat > /tmp/test_docs/documentation.md << 'EOF'
# API Documentation

## Question
How do I use the tile forge agent?

## Answer
Start the room with `python room.py start` and call `forge_tiles()`.

## Example
```python
from room import TileForgeRoom
room = TileForgeRoom()
room.start()
result = room.forge_tiles("/path/to/markdown", "/output/dir")
```

## Definition
Tile: A structured knowledge unit with question, answer, and metadata.
EOF
```

### **Step 5: Forge Your First Tiles**
```python
from room import TileForgeRoom

# Create and start room
room = TileForgeRoom()
room.start()

# Forge tiles from test documents
result = room.forge_tiles("/tmp/test_docs", "/tmp/my_tiles")

print(f"Files processed: {result['files_processed']}")
print(f"Patterns found: {result['patterns_found']}")
print(f"Tiles created: {result['tiles_created']}")
print(f"Time taken: {result['elapsed_seconds']:.2f} seconds")
```

**Expected Output:**
```
Files processed: 1
Patterns found: 3
Tiles created: 3
Time taken: 0.15 seconds
```

### **Step 6: View Your Tiles**
```bash
ls -la /tmp/my_tiles/
cat /tmp/my_tiles/*.json | head -20
```

**Sample Tile Output:**
```json
{
  "id": "tile_001",
  "question": "How do I use the tile forge agent?",
  "answer": "Start the room with `python room.py start` and call `forge_tiles()`.",
  "confidence": 0.85,
  "tags": ["api", "documentation", "getting-started"],
  "metadata": {
    "source": "documentation.md",
    "pattern_type": "qna",
    "extracted_at": "2026-04-18T11:40:00Z"
  }
}
```

## 📁 Project Structure

```
tile-forge-agent/
├── room.py              # Main room implementation
├── room.yaml           # Room configuration
├── requirements.txt    # Python dependencies
├── computer/          # Computer abstraction
│   ├── __init__.py
│   └── resources.py
├── tools/             # Built-in tools
│   ├── markdown_parser.py
│   ├── pattern_extractor.py
│   ├── tile_synthesizer.py
│   ├── quality_filter.py
│   └── cron_scheduler.py
├── visitors/          # Boarding agent support
├── providers/         # Tool provider connections
└── tests/            # Test suite
```

## ⚙️ Configuration

### **Basic Configuration (room.yaml)**
```yaml
name: tile-forge-agent
version: 1.0.0
type: room_with_computer

computer:
  cpu: 2 cores
  memory: 4GB
  storage: 10GB

tools:
  - markdown_parser
  - pattern_extractor
  - tile_synthesizer
  - quality_filter
  - cron_scheduler

quality:
  min_answer_length: 30
  min_word_count: 4
  confidence_threshold: 0.3

scheduling:
  cron: "*/15 * * * *"  # Every 15 minutes
  max_concurrent: 10
```

### **Environment Variables**
```bash
export TILE_FORGE_CPU=4           # Increase CPU cores
export TILE_FORGE_MEMORY=8GB      # Increase memory
export TILE_FORGE_OUTPUT_DIR=/data/tiles  # Custom output directory
export TILE_FORGE_LOG_LEVEL=DEBUG # Debug logging
```

## 🔧 Common Operations

### **1. One-time Tile Forging**
```python
from room import TileForgeRoom

room = TileForgeRoom()
room.start()

# Forge from directory
result = room.forge_tiles(
    input_dir="/path/to/markdown",
    output_dir="/path/for/tiles"
)

# Forge from single file
result = room.forge_tiles(
    input_dir="/path/to/file.md",
    output_dir="/path/for/tiles",
    single_file=True
)
```

### **2. Scheduled Tile Forging**
```python
from room import TileForgeRoom

room = TileForgeRoom()
room.start()

# Schedule automatic forging
room.schedule_forging(
    input_dir="/path/to/markdown",
    output_dir="/path/for/tiles",
    schedule="0 */2 * * *"  # Every 2 hours
)

# Check schedule status
status = room.get_schedule_status()
print(f"Next run: {status['next_run']}")
print(f"Last run: {status['last_run']}")
```

### **3. Quality Control**
```python
from room import TileForgeRoom

room = TileForgeRoom()
room.start()

# Adjust quality thresholds
room.configure_quality(
    min_answer_length=50,    # Require longer answers
    min_word_count=6,        # Require more words
    confidence_threshold=0.5 # Higher confidence
)

# Get quality metrics
metrics = room.get_quality_metrics()
print(f"Quality pass rate: {metrics['pass_rate']}%")
print(f"Average confidence: {metrics['avg_confidence']}")
```

### **4. Tool Usage**
```python
from room import TileForgeRoom

room = TileForgeRoom()
room.start()

# Use individual tools
parsed = room.tools.execute("markdown_parser", "/path/to/file.md")
patterns = room.tools.execute("pattern_extractor", parsed)
tiles = room.tools.execute("tile_synthesizer", patterns)
filtered = room.tools.execute("quality_filter", tiles)

# List available tools
tools = list(room.tools.tools.keys())
print(f"Available tools: {tools}")
```

## 🐛 Troubleshooting

### **Common Issues & Solutions**

#### **Issue: "No such file or directory: 'room.yaml'"**
**Solution:** Ensure you're in the tile-forge-agent directory:
```bash
cd /path/to/tile-forge-agent
python room.py start
```

#### **Issue: "ModuleNotFoundError: No module named 'markdown'"**
**Solution:** Install dependencies:
```bash
pip install -r requirements.txt
```

#### **Issue: "MemoryError" or slow performance**
**Solution:** Adjust resource limits:
```bash
export TILE_FORGE_MEMORY=8GB
export TILE_FORGE_CPU=4
```

#### **Issue: No tiles created from valid markdown**
**Solution:** Check quality thresholds:
```python
room.configure_quality(
    min_answer_length=20,    # Lower minimum
    min_word_count=3,        # Lower word count
    confidence_threshold=0.1 # Lower confidence
)
```

### **Debug Mode**
```bash
# Enable debug logging
export TILE_FORGE_LOG_LEVEL=DEBUG
python room.py start

# Or programmatically
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📊 Performance Tuning

### **For Large Document Collections**
```python
room = TileForgeRoom()
room.start()

# Batch processing for large collections
room.configure_processing(
    batch_size=50,           # Process 50 files at a time
    max_workers=4,           # Use 4 parallel workers
    chunk_size=1024*1024     # 1MB chunks for large files
)

# Memory optimization
room.configure_memory(
    cache_size=1000,         # Cache 1000 parsed documents
    tile_buffer=100,         # Buffer 100 tiles before writing
    cleanup_interval=60      # Cleanup every 60 seconds
)
```

### **For Real-time Processing**
```python
room = TileForgeRoom()
room.start()

# Stream processing configuration
room.configure_streaming(
    watch_dir="/path/to/watch",  # Directory to watch
    debounce_ms=1000,            # Wait 1 second after changes
    immediate_processing=True    # Process immediately
)

# Process files as they arrive
room.watch_and_forge(
    input_dir="/path/to/watch",
    output_dir="/path/for/tiles"
)
```

## 🔗 Integration Examples

### **1. Integration with Notebook Kernel Agent**
```python
from room import TileForgeRoom
from notebook_kernel_agent.agent import NotebookKernelAgent

# Create rooms
tile_room = TileForgeRoom()
tile_room.start()

notebook_agent = NotebookKernelAgent()

# Board notebook agent to tile room
notebook_agent.board(tile_room)

# Use tile room tools from notebook agent
result = notebook_agent.execute_cell(
    content="forge tiles from /docs",
    cell_type="query",
    perspective="architect"
)
```

### **2. Integration with Constraint Engine**
```python
from room import TileForgeRoom
from constraint_engine_agent.provider import ConstraintEngineProvider

# Create room and provider
tile_room = TileForgeRoom()
tile_room.start()

constraint_provider = ConstraintEngineProvider()
constraint_provider.start()

# Connect constraint provider
tile_room.connect_provider(constraint_provider)

# All operations now checked against constraints
result = tile_room.forge_tiles(
    input_dir="/path/to/markdown",
    output_dir="/path/for/tiles"
)
# Automatically validated by constraint engine
```

### **3. Plato Stack Integration**
```python
from room import TileForgeRoom
import plato_address
import plato_hooks
import plato_bridge

# Create addressable room
tile_room = TileForgeRoom()
tile_room.start()

# Register with plato-address
address = plato_address.register(
    entity=tile_room,
    address="tile-forge-agent@rooms.plato"
)

# Add plato-hooks
hooks = plato_hooks.attach(tile_room, {
    "pre_forge": tile_room.validate_input,
    "post_forge": tile_room.quality_check,
    "error": tile_room.handle_error
})

# Connect via plato-bridge
bridge = plato_bridge.connect(
    source="tile-forge-agent",
    target="other-room@plato"
)
```

## 🧪 Testing Your Setup

### **Run Built-in Tests**
```bash
python -m pytest tests/ -v
```

### **Create Your Own Test**
```python
import unittest
from room import TileForgeRoom

class TestTileForge(unittest.TestCase):
    def test_basic_forging(self):
        room = TileForgeRoom()
        room.start()
        
        result = room.forge_tiles(
            input_dir="/tmp/test_docs",
            output_dir="/tmp/test_output"
        )
        
        self.assertTrue(result["success"])
        self.assertGreater(result["tiles_created"], 0)
        
if __name__ == "__main__":
    unittest.main()
```

### **Performance Test**
```python
import time
from room import TileForgeRoom

room = TileForgeRoom()
room.start()

# Test with 100 files
start = time.time()
result = room.forge_tiles(
    input_dir="/large/document/collection",
    output_dir="/tmp/performance_test",
    max_files=100
)
elapsed = time.time() - start

print(f"Processed {result['files_processed']} files in {elapsed:.2f}s")
print(f"Throughput: {result['files_processed']/elapsed:.1f} files/sec")
print(f"Tile rate: {result['tiles_created']/elapsed:.1f} tiles/sec")
```

## 📈 Next Steps

### **After Quick Start:**
1. **Explore Architecture**: Read [ARCHITECTURE.md](./ARCHITECTURE.md)
2. **Learn API**: Check [API_REFERENCE.md](./API_REFERENCE.md)
3. **See Examples**: Review [EXAMPLES.md](./EXAMPLES.md)
4. **Join Ecosystem**: Connect with other git-agents
5. **Contribute**: Submit issues and pull requests

### **Production Deployment:**
1. **Dockerize**: `docker build -t tile-forge-agent .`
2. **Orchestrate**: Deploy to Kubernetes
3. **Monitor**: Set up metrics and alerts
4. **Scale**: Add more room instances
5. **Integrate**: Connect to your existing systems

## 🆘 Getting Help

### **Resources:**
- **Documentation**: [docs/](./)
- **GitHub Issues**: https://github.com/Lucineer/tile-forge-agent/issues
- **Community**: Discord/Slack (links in README)
- **Examples**: `/examples` directory

### **Common Questions:**

**Q: How do I process non-markdown files?**  
**A:** Convert to markdown first, or extend the markdown parser tool.

**Q: Can I customize the pattern extraction?**  
**A:** Yes, extend the PatternExtractor class or create your own tool.

**Q: How do I deploy to production?**  
**A:** See the Docker and Kubernetes examples in the deployment guide.

**Q: Can I use this with my existing knowledge base?**  
**A:** Yes, export your content to markdown format and process it.

## 🎉 Congratulations!

You've successfully:
- ✅ Started the Tile Forge Agent room
- ✅ Created your first knowledge tiles
- ✅ Learned basic operations and configuration
- ✅ Explored integration possibilities

**Next:** Dive deeper into the [architecture](./ARCHITECTURE.md) or explore [examples](./EXAMPLES.md) of advanced usage.

---
*Quick Start Guide created: 2026-04-18 11:45 AKDT*  
*Tile Forge Agent v1.0.0 | Room with Computer Pattern*
