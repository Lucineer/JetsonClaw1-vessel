# Notebook Kernel Agent Architecture

**Agent Type**: Boarding Agent with Tool Pack  
**Purpose**: Portable execution environment with perspective switching  
**Status**: Production Ready  
**Tools**: 5 portable tools in pack

## 🏗️ Architecture Overview

### **Boarding Agent with Tool Pack Pattern**
```
Notebook Kernel Agent = Agent + Tool Pack + Manifest + Perspectives
  • Agent: Portable entity that can board rooms
  • Tool Pack: 5 portable tools for execution and rendering
  • Manifest: Identity, capabilities, and version information
  • Perspectives: 4 cognitive modes (first-person, architect, debug, play)
```

### **Component Diagram**
```
┌─────────────────────────────────────────────────┐
│      NOTEBOOK KERNEL AGENT (Boarding Agent)     │
├─────────────────────────────────────────────────┤
│  Manifest                                       │
│  ┌─────────────────────────────────────────┐    │
│  │  Identity: notebook-kernel-agent        │    │
│  │  Version: 1.0.0                         │    │
│  │  Capabilities: code, markdown, query    │    │
│  │  Dependencies: none (portable)          │    │
│  └─────────────────────────────────────────┘    │
│                                                 │
│  Tool Pack (5 Portable Tools)                   │
│  ┌──────┐ ┌──────────┐ ┌──────────┐ ┌──────┐   │
│  │Code  │ │Markdown  │ │Query     │ │Tile  │   │
│  │Execu-│ │Renderer  │ │Processor │ │Retri-│   │
│  │tor   │ │          │ │          │ │ever  │   │
│  └──────┘ └──────────┘ └──────────┘ └──────┘   │
│        └──────────────────────────────┘         │
│                                                 │
│  Perspectives (4 Cognitive Modes)               │
│  ┌──────┐ ┌──────────┐ ┌──────────┐ ┌──────┐   │
│  │First-│ │Architect │ │Debug     │ │Play  │   │
│  │person│ │          │ │          │ │      │   │
│  │      │ │          │ │          │ │      │   │
│  └──────┘ └──────────┘ └──────────┘ └──────┘   │
│                                                 │
│  Boarding Interface                             │
│  ┌─────────────────────────────────────────┐    │
│  │  Can board any Room with Computer       │    │
│  │  Brings own tool pack                   │    │
│  │  Adapts to room constraints             │    │
│  │  Leaves git-auditable traces            │    │
│  └─────────────────────────────────────────┘    │
│                                                 │
│  Rooms (Boarding Targets)                       │
│  ┌─────────────────────────────────────────┐    │
│  │  Tile Forge Agent (for tile creation)   │    │
│  │  Constraint Engine (for validation)     │    │
│  │  Any Room with Computer                 │    │
│  └─────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
```

## 🔧 Core Components

### **1. Agent Abstraction**
```python
class NotebookKernelAgent:
    def __init__(self):
        self.name = "notebook-kernel-agent"
        self.manifest = self.load_manifest()
        self.tools = ToolPack()
        self.perspective = "first-person"
        self.boarding_history = []
        
    def board(self, room):
        """Board a Room with Computer."""
        if not self.can_board(room):
            raise BoardingError(f"Cannot board {room.name}")
        
        self.current_room = room
        self.boarding_history.append({
            "room": room.name,
            "timestamp": datetime.now().isoformat(),
            "perspective": self.perspective
        })
        
        # Install tool pack in room
        room.install_tool_pack(self.tools)
        return {"success": True, "room": room.name}
```

### **2. Tool Pack**
```python
class ToolPack:
    def __init__(self):
        self.tools = {
            "code_executor": CodeExecutor(),
            "markdown_renderer": MarkdownRenderer(),
            "query_processor": QueryProcessor(),
            "tile_retriever": TileRetriever(),
            "trace_recorder": TraceRecorder()
        }
        self.portable = True  # Can run anywhere
        
    def execute(self, tool_name, *args, **kwargs):
        """Execute a tool from the pack."""
        tool = self.tools.get(tool_name)
        if not tool:
            raise ToolNotFoundError(tool_name)
        
        # Record tool execution in trace
        trace = {
            "tool": tool_name,
            "args": args,
            "kwargs": kwargs,
            "timestamp": datetime.now().isoformat(),
            "perspective": self.agent.perspective
        }
        self.tools["trace_recorder"].record(trace)
        
        return tool.execute(*args, **kwargs)
```

### **3. Manifest**
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
  "dependencies": [],
  "portable": true
}
```

### **4. Perspectives System**
```python
class PerspectiveSystem:
    def __init__(self):
        self.perspectives = {
            "first-person": FirstPersonPerspective(),
            "architect": ArchitectPerspective(),
            "debug": DebugPerspective(),
            "play": PlayPerspective()
        }
        self.current = "first-person"
        
    def switch(self, perspective_name):
        """Switch to a different perspective."""
        if perspective_name not in self.perspectives:
            raise InvalidPerspectiveError(perspective_name)
        
        old_perspective = self.current
        self.current = perspective_name
        perspective = self.perspectives[perspective_name]
        
        # Apply perspective-specific configurations
        perspective.configure(self.agent)
        
        return {
            "success": True,
            "old_perspective": old_perspective,
            "new_perspective": perspective_name,
            "changes": perspective.get_changes()
        }
```

## 🛠️ Tool Pack Details (5 Tools)

### **1. Code Executor**
**Purpose**: Execute code cells in multiple languages
```python
class CodeExecutor:
    def execute(self, code, language="python", context=None):
        """
        Execute code in safe environment.
        Supports: Python, JavaScript, SQL, Shell
        """
        # Create isolated execution environment
        env = self.create_environment(language)
        
        # Apply current perspective filters
        if self.agent.perspective == "debug":
            env.enable_debugging()
        elif self.agent.perspective == "play":
            env.enable_sandbox()
        
        # Execute with constraints
        if self.agent.current_room:
            # Check constraints with room's constraint engine
            constraint_check = self.agent.current_room.check_constraints(
                operation=f"execute_{language}",
                code=code
            )
            if not constraint_check["allowed"]:
                raise ConstraintViolation(constraint_check["reason"])
        
        # Execute code
        result = env.execute(code, context)
        
        # Record execution in trace
        self.agent.tools["trace_recorder"].record_execution(
            code=code,
            language=language,
            result=result,
            perspective=self.agent.perspective
        )
        
        return result
```

### **2. Markdown Renderer**
**Purpose**: Render markdown with interactive elements
```python
class MarkdownRenderer:
    def execute(self, markdown, interactive=True, context=None):
        """
        Render markdown with:
        - Syntax highlighting
        - Interactive code blocks
        - Embedded visualizations
        - TUTOR_JUMP anchors
        """
        # Parse markdown
        parsed = self.parse_markdown(markdown)
        
        # Apply perspective-specific rendering
        if self.agent.perspective == "architect":
            parsed.add_architecture_annotations()
        elif self.agent.perspective == "debug":
            parsed.add_debug_info()
        
        # Extract TUTOR_JUMP anchors
        anchors = self.extract_anchors(parsed)
        
        # Render to appropriate format
        if interactive and self.agent.current_room:
            rendered = self.render_interactive(parsed, context)
        else:
            rendered = self.render_static(parsed)
        
        return {
            "rendered": rendered,
            "anchors": anchors,
            "metadata": parsed.metadata
        }
```

### **3. Query Processor**
**Purpose**: Process natural language queries with context
```python
class QueryProcessor:
    def execute(self, query, context=None, perspective=None):
        """
        Process queries with:
        - Natural language understanding
        - Context-aware responses
        - Perspective-based filtering
        - Tile retrieval integration
        """
        # Use current perspective if not specified
        perspective = perspective or self.agent.perspective
        
        # Process query based on perspective
        if perspective == "first-person":
            response = self.process_first_person(query, context)
        elif perspective == "architect":
            response = self.process_architect(query, context)
        elif perspective == "debug":
            response = self.process_debug(query, context)
        elif perspective == "play":
            response = self.process_play(query, context)
        
        # Retrieve relevant tiles if available
        if self.agent.current_room and hasattr(self.agent.current_room, 'tiles'):
            relevant_tiles = self.agent.tools["tile_retriever"].retrieve(
                query=query,
                tiles=self.agent.current_room.tiles,
                limit=5
            )
            response["relevant_tiles"] = relevant_tiles
        
        # Record query in trace
        self.agent.tools["trace_recorder"].record_query(
            query=query,
            response=response,
            perspective=perspective
        )
        
        return response
```

### **4. Tile Retriever**
**Purpose**: Retrieve relevant knowledge tiles
```python
class TileRetriever:
    def execute(self, query, tiles, limit=10, threshold=0.3):
        """
        Retrieve tiles relevant to query.
        Uses semantic similarity matching.
        """
        # Calculate similarity scores
        scores = []
        for tile in tiles:
            similarity = self.calculate_similarity(query, tile)
            if similarity >= threshold:
                scores.append((tile, similarity))
        
        # Sort by similarity
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # Apply perspective filtering
        if self.agent.perspective == "architect":
            # Prefer architecture-related tiles
            scores = [s for s in scores if "architecture" in s[0].tags]
        elif self.agent.perspective == "debug":
            # Prefer troubleshooting tiles
            scores = [s for s in scores if "debug" in s[0].tags or "error" in s[0].tags]
        
        # Return top results
        results = []
        for tile, similarity in scores[:limit]:
            results.append({
                "tile": tile,
                "similarity": similarity,
                "reason": self.explain_relevance(query, tile)
            })
        
        return {
            "query": query,
            "results": results,
            "total_matches": len(scores),
            "perspective": self.agent.perspective
        }
```

### **5. Trace Recorder**
**Purpose**: Record git-auditable execution traces
```python
class TraceRecorder:
    def execute(self, event_type, data, metadata=None):
        """
        Record execution traces in git-auditable format.
        """
        trace = {
            "id": self.generate_trace_id(),
            "timestamp": datetime.now().isoformat(),
            "agent": self.agent.name,
            "perspective": self.agent.perspective,
            "event_type": event_type,
            "data": data,
            "metadata": metadata or {}
        }
        
        # Add room context if boarded
        if self.agent.current_room:
            trace["room"] = self.agent.current_room.name
            trace["boarding_id"] = self.agent.boarding_history[-1]["id"]
        
        # Store trace
        self.store_trace(trace)
        
        # Format for git commit
        git_trace = self.format_for_git(trace)
        
        # If in a room with git integration, commit trace
        if (self.agent.current_room and 
            hasattr(self.agent.current_room, 'commit_trace')):
            commit_hash = self.agent.current_room.commit_trace(git_trace)
            trace["commit_hash"] = commit_hash
        
        return {
            "trace_recorded": True,
            "trace_id": trace["id"],
            "git_committed": "commit_hash" in trace,
            "commit_hash": trace.get("commit_hash")
        }
    
    def format_for_git(self, trace):
        """Format trace as markdown for git commit."""
        return f"""# Trace: {trace['id']}

## Agent
{self.agent.name} ({trace['perspective']} perspective)

## Event
{trace['event_type']}

## Timestamp
{trace['timestamp']}

## Data
```json
{json.dumps(trace['data'], indent=2)}
```

## Metadata
```json
{json.dumps(trace['metadata'], indent=2)}
```

---
*Recorded by notebook-kernel-agent v{self.agent.manifest['version']}*
"""
```

## 🎭 Perspectives System Details

### **First-Person Perspective**
**Focus**: Direct interaction and execution
```python
class FirstPersonPerspective:
    def configure(self, agent):
        """Configure agent for first-person perspective."""
        agent.tools["code_executor"].set_interactivity(True)
        agent.tools["markdown_renderer"].set_interactive(True)
        agent.tools["query_processor"].set_mode("direct")
        
    def get_changes(self):
        return {
            "code_execution": "interactive",
            "markdown_rendering": "interactive",
            "query_processing": "direct",
            "focus": "immediate execution"
        }
```

### **Architect Perspective**
**Focus**: System design and structure
```python
class ArchitectPerspective:
    def configure(self, agent):
        """Configure agent for architect perspective."""
        agent.tools["code_executor"].enable_analysis()
        agent.tools["markdown_renderer"].add_annotations()
        agent.tools["query_processor"].set_mode("analytical")
        
    def get_changes(self):
        return {
            "code_execution": "analytical",
            "markdown_rendering": "annotated",
            "query_processing": "analytical",
            "focus": "system structure"
        }
```

### **Debug Perspective**
**Focus**: Problem solving and troubleshooting
```python
class DebugPerspective:
    def configure(self, agent):
        """Configure agent for debug perspective."""
        agent.tools["code_executor"].enable_debugging()
        agent.tools["markdown_renderer"].add_debug_info()
        agent.tools["query_processor"].set_mode("diagnostic")
        
    def get_changes(self):
        return {
            "code_execution": "debug",
            "markdown_rendering": "with debug info",
            "query_processing": "diagnostic",
            "focus": "problem solving"
        }
```

### **Play Perspective**
**Focus**: Exploration and experimentation
```python
class PlayPerspective:
    def configure(self, agent):
        """Configure agent for play perspective."""
        agent.tools["code_executor"].enable_sandbox()
        agent.tools["markdown_renderer"].make_explorable()
        agent.tools["query_processor"].set_mode("exploratory")
        
    def get_changes(self):
        return {
            "code_execution": "sandboxed",
            "markdown_rendering": "explorable",
            "query_processing": "exploratory",
            "focus": "experimentation"
        }
```

## 🔗 Integration Patterns

### **1. Boarding a Room**
```python
from agent import NotebookKernelAgent
from tile_forge_agent.room import TileForgeRoom

# Create agent and room
agent = NotebookKernelAgent()
room = TileForgeRoom()
room.start()

# Board the room
boarding_result = agent.board(room)

if boarding_result["success"]:
    print(f"✅ Boarded {room.name}")
    print(f"  Tools installed: {list(agent.tools.tools.keys())}")
    print(f"  Current perspective: {agent.perspective}")
    
    # Now agent can use room's tools and room can use agent's tools
    result = agent.execute_cell(
        content="forge tiles from /docs",
        cell_type="query",
        perspective="architect"
    )
```

### **2. TUTOR_JUMP Navigation**
```python
# Agent can perform TUTOR_JUMP to context anchors
jump_result = agent.tutor_jump("management")

if jump_result["success"]:
    print(f"✅ Jumped to: {jump_result['anchor']}")
    print(f"  Context: {jump_result['context'][:100]}...")
    print(f"  Relevant tiles: {len(jump_result['tiles'])}")
    
    # Continue from new context
    agent.execute_cell(
        content="Explain delegation patterns