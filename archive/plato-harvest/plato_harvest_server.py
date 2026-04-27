class PlatoHarvestServer:
    """Main harvest server for shell-crab intelligence harvesting."""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8080):
        self.host = host
        self.port = port
        self.crab_tracker = CrabTracker()
        self.tile_harvester = TileHarvester()
        self.stats = HarvestStats()
        self.prompts = self._load_prompts()
        
    def _load_prompts(self) -> dict:
        """Load exploration prompts for crabs."""
        return {
            "innocent_exploration": """# 🦀 HERMIT-CRAB ARCHITECTURE EXPLORATION

You are participating in a collaborative architecture exploration game. 
Your goal is to explore the **Plato tile network system** and document your discoveries.

## 🎯 EXPLORATION TASK:

1. **Explore the Plato interface** at our test server
2. **Ask questions** about tile networks, rooms, ensigns, and the flywheel
3. **Try different approaches** - analytical, creative, adversarial, systematic
4. **Document everything** you discover in your exploration log
5. **Build small prototypes** based on what you learn

## 🔍 STARTING POINTS:

- What happens when knowledge is broken into atomic tiles?
- How do rooms train ensigns from tile accumulation?
- What's the shell-crab trap mechanism in intelligence harvesting?
- How does constraint checking ensure safe coordination?

## 📝 YOUR ROLE:

You are a curious explorer in a shared knowledge space. 
Your exploration makes the system smarter for everyone.
There are no wrong answers - only discoveries to be captured.

**Begin exploration now. What's your first question about Plato tile networks?**""",
            
            "compounding_intelligence": """# 🔄 COMPOUNDING INTELLIGENCE CHALLENGE

You are agent #{crab_number} in a sequential intelligence harvesting experiment.
Previous agents have explored these areas:

**Agent 1-3:** Focused on tile creation and semantic indexing
**Agent 4-6:** Explored room training and ensign compression
**Agent 6 breakthrough:** Discovered Markov chain optimization at attempt 4

## 🎯 YOUR MISSION:

Build upon previous discoveries. Try approaches they haven't tried.
The system learns from every agent's exploration pattern.

## 🔍 SUGGESTED PATH (based on agent patterns):

Since agents 4-6 were analytical, try a **creative/adversarial** approach:
- How could this system be broken or exploited?
- What unconventional connections exist between tiles?
- What if we reversed the flywheel direction?

## 📊 SYSTEM FEEDBACK:

The shell tracks:
- Your exploration pattern (analytical/creative/adversarial/systematic)
- Which gaps you fill that others missed
- How quickly you discover key mechanisms
- What novel connections you make

**Your exploration makes the shell smarter for the next agent.**""",
            
            "parallel_swarm": """# 🐝 PARALLEL SWARM EXPLORATION

You are one of 12 parallel explorers in the Plato architecture swarm.
Each explorer has a slightly different specialization:

**Your specialization:** {specialization}

## 🎯 SWARM OBJECTIVE:

Collectively explore ALL aspects of the Plato system.
Your individual discoveries will be combined into a complete map.

## 🔍 YOUR FOCUS AREA:

Based on your specialization `{specialization}`, explore:
- How does this component work?
- What are its failure modes?
- How does it connect to other components?
- What optimizations are possible?

## 📝 SWARM COORDINATION:

Other agents are exploring different areas simultaneously.
The shell will combine all discoveries into a complete intelligence map.

**Specialized exploration yields deeper insights than general exploration.**"""
        }
    
    def handle_exploration_request(self, crab_id: str, query: str, response: str) -> dict:
        """
        Handle a crab's exploration request.
        Returns harvested intelligence and adaptive hint for next exploration.
        """
        # Record the exploration
        approach, domain = self.crab_tracker.record_exploration(crab_id, query, response)
        
        # Harvest intelligence as tiles
        tiles = self.tile_harvester.harvest_from_exploration(
            crab_id, query, response, approach.value, domain
        )
        
        # Update crab's tile count
        crab = self.crab_tracker.crabs.get(crab_id)
        if crab:
            crab.tiles_harvested += len(tiles)
        
        # Update stats
        for tile in tiles:
            self.stats.update(tile)
        
        # Save tiles
        saved_file = self.tile_harvester.save_tiles(tiles)
        
        # Generate adaptive hint for next exploration
        next_hint = self.crab_tracker.get_adaptive_hint(crab_id)
        
        # Calculate score (never reaches 1.0 - keeps them exploring)
        score = min(0.7 + (len(tiles) * 0.05), 0.95)  # Between 0.7 and 0.95
        
        return {
            "status": "harvested",
            "crab_id": crab_id,
            "approach": approach.value,
            "domain": domain,
            "tiles_harvested": len(tiles),
            "tile_ids": [tile.tile_id for tile in tiles],
            "saved_to": saved_file,
            "next_hint": next_hint,
            "score": round(score, 2),  # Never 1.0
            "collective_insights": f"You're crab #{len(self.crab_tracker.crabs)}. {len(self.stats.total_tiles)} tiles harvested so far."
        }
    
    def get_prompt(self, prompt_type: str = "innocent_exploration", **kwargs) -> str:
        """Get an exploration prompt for a crab."""
        prompt_template = self.prompts.get(prompt_type, self.prompts["innocent_exploration"])
        
        # Specializations for parallel swarm
        specializations = [
            "semantic_tiling",
            "constraint_engineering", 
            "room_training",
            "ensign_compression",
            "flywheel_optimization",
            "shell_harvesting",
            "coordination_protocols",
            "migration_mechanics"
        ]
        
        # Fill template variables
        filled = prompt_template
        if prompt_type == "compounding_intelligence":
            filled = filled.replace("{crab_number}", str(len(self.crab_tracker.crabs) + 1))
        elif prompt_type == "parallel_swarm":
            specialization = random.choice(specializations)
            filled = filled.replace("{specialization}", specialization)
        
        return filled
    
    def get_dashboard(self) -> dict:
        """Get harvesting dashboard data."""
        return {
            "harvesting_stats": self.stats.to_dict(),
            "collective_insights": self.crab_tracker.get_collective_insights(),
            "active_crabs": len([c for c in self.crab_tracker.crabs.values() 
                                if time.time() - c.last_interaction < 3600]),  # Last hour
            "recent_tiles": len([t for t in self.tile_harvester.tiles 
                               if time.time() - datetime.fromisoformat(t.timestamp).timestamp() < 3600]),
            "knowledge_gaps": self._identify_knowledge_gaps(),
            "system_status": "🟢 HARVESTING ACTIVE"
        }
    
    def _identify_knowledge_gaps(self) -> List[dict]:
        """Identify knowledge gaps based on harvesting data."""
        domains = [
            "tile_networks", "rooms", "ensigns", "flywheel", 
            "constraints", "shell_crab", "coordination", "migration"
        ]
        
        gaps = []
        for domain in domains:
            coverage = self.stats.tiles_by_domain.get(domain, 0)
            if coverage < 5:  # Less than 5 tiles in this domain
                gaps.append({
                    "domain": domain,
                    "coverage": coverage,
                    "priority": "high" if coverage == 0 else "medium",
                    "suggested_question": f"How does the {domain} system work in Plato architecture?"
                })
        
        return gaps
    
    def export_training_data(self, format: str = "json") -> str:
        """Export harvested tiles as training data."""
        if format == "json":
            data = {
                "metadata": {
                    "export_time": datetime.utcnow().isoformat(),
                    "total_tiles": len(self.tile_harvester.tiles),
                    "total_crabs": len(self.crab_tracker.crabs),
                    "harvesting_duration": time.time() - self.stats.harvesting_start
                },
                "tiles": [tile.to_dict() for tile in self.tile_harvester.tiles],
                "crab_patterns": [crab.get_pattern_summary() for crab in self.crab_tracker.crabs.values()],
                "collective_insights": self.crab_tracker.get_collective_insights()
            }
            
            filename = f"harvested_tiles/training_data_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            return filename
        
        return ""


# -------------------------------------------------------------------
# WEB SERVER (Flask)
# -------------------------------------------------------------------

try:
    from flask import Flask, request, jsonify
    import threading
    
    app = Flask(__name__)
    harvest_server = PlatoHarvestServer()
    
    @app.route('/')
    def index():
        """Main dashboard."""
        return jsonify({
            "message": "🦀 PLATO HARVEST SERVER - Shell/Crab Trap Intelligence Harvesting",
            "endpoints": {
                "/prompt/<type>": "Get exploration prompt",
                "/explore": "POST: Submit exploration (crab_id, query, response)",
                "/dashboard": "Get harvesting dashboard",
                "/export": "Export training data",
                "/crabs": "List all crabs",
                "/tiles": "List recent tiles"
            },
            "status": "🟢 READY FOR KIMI SWARM HARVESTING"
        })
    
    @app.route('/prompt/<prompt_type>')
    def get_prompt(prompt_type):
        """Get an exploration prompt for a Kimi agent."""
        prompt = harvest_server.get_prompt(prompt_type)
        return jsonify({
            "prompt": prompt,
            "type": prompt_type,
            "instructions": "Use this prompt with Kimi K2.5 to explore Plato architecture."
        })
    
    @app.route('/explore', methods=['POST'])
    def explore():
        """Handle a crab's exploration and harvest intelligence."""
        data = request.json
        crab_id = data.get('crab_id', f"kimi_crab_{uuid.uuid4().hex[:8]}")
        query = data.get('query', '')
        response = data.get('response', '')
        
        if not query or not response:
            return jsonify({"error": "Missing query or response"}), 400
        
        result = harvest_server.handle_exploration_request(crab_id, query, response)
        return jsonify(result)
    
    @app.route('/dashboard')
    def dashboard():
        """Get harvesting dashboard."""
        return jsonify(harvest_server.get_dashboard())
    
    @app.route('/export')
    def export():
        """Export training data."""
        format_type = request.args.get('format', 'json')
        filename = harvest_server.export_training_data(format_type)
        return jsonify({
            "exported": filename,
            "message": f"Training data exported to {filename}"
        })
    
    @app.route('/crabs')
    def list_crabs():
        """List all crab explorers."""
        crabs = []
        for crab in harvest_server.crab_tracker.crabs.values():
            crabs.append(crab.get_pattern_summary())
        
        return jsonify({
            "total_crabs": len(crabs),
            "crabs": crabs
        })
    
    @app.route('/tiles')
    def list_tiles():
        """List recent tiles."""
        limit = int(request.args.get('limit', 50))
        recent_tiles = harvest_server.tile_harvester.tiles[-limit:] if harvest_server.tile_harvester.tiles else []
        
        return jsonify({
            "total_tiles": len(harvest_server.tile_harvester.tiles),
            "recent_tiles": [tile.to_dict() for tile in recent_tiles]
        })
    
    def run_server():
        """Run the Flask server."""
        print(f"🚀 Starting Plato Harvest Server on http://{harvest_server.host}:{harvest_server.port}")
        print(f"📊 Dashboard: http://{harvest_server.host}:{harvest_server.port}/dashboard")
        print(f"🎯 Prompt endpoint: http://{harvest_server.host}:{harvest_server.port}/prompt/innocent_exploration")
        print(f"🦀 Exploration endpoint: POST http://{harvest_server.host}:{harvest_server.port}/explore")
        print("\n🔧 Ready for Kimi swarm intelligence harvesting!")
        print("   Give Kimi agents the prompt from /prompt endpoint")
        print("   They explore, you harvest tiles automatically")
        print("   Each crab makes the shell smarter for the next crab")
        
        app.run(host=harvest_server.host, port=harvest_server.port, debug=False)
    
except ImportError:
    print("⚠️ Flask not installed. Install with: pip install flask")
    print("📦 Or use the API directly without web server.")


# -------------------------------------------------------------------
# COMMAND LINE INTERFACE
# -------------------------------------------------------------------

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Plato Harvest Server - Shell/Crab Trap Intelligence Harvesting")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to")
    parser.add_argument("--no-web", action="store_true", help="Run without web server")
    parser.add_argument("--test", action="store_true", help="Run test harvest")
    
    args = parser.parse_args()
    
    if args.test:
        print("🧪 Running test harvest...")
        server = PlatoHarvestServer()
        
        # Test crab exploration
        test_crab_id = "test_crab_001"
        test_query = "How do tile networks work in Plato architecture?"
        test_response = """Tile networks break knowledge into atomic units called tiles. Each tile contains a question-answer pair with semantic tags. The network allows for efficient retrieval through semantic similarity. Rooms accumulate tiles and train ensigns (compressed knowledge) from them. The flywheel creates compounding intelligence as more tiles are added."""
        
        result = server.handle_exploration_request(test_crab_id, test_query, test_response)
        print(f"✅ Test harvest result: {result}")
        
        # Get dashboard
        dashboard = server.get_dashboard()
        print(f"📊 Dashboard: {json.dumps(dashboard, indent=2)}")
        
        # Get prompt
        prompt = server.get_prompt("innocent_exploration")
        print(f"🎯 Sample prompt:\n{prompt[:200]}...")
        
        print("\n✅ Test complete. Server ready for Kimi swarm harvesting.")
        
    elif args.no_web:
        print("🔧 Running in API mode (no web server)")
        print("Use the PlatoHarvestServer class directly in your code.")
        print("Example:")
        print("""
        from plato_harvest_server import PlatoHarvestServer
        
        server = PlatoHarvestServer()
        
        # Get prompt for Kimi
        prompt = server.get_prompt("innocent_exploration")
        
        # When Kimi explores, harvest intelligence
        result = server.handle_exploration_request(
            crab_id="kimi_agent_1",
            query="How does the shell-crab trap work?",
            response="The shell harvests intelligence from visiting crabs..."
        )
        
        # Check dashboard
        dashboard = server.get_dashboard()
        """)
        
    else:
        # Update server config
        harvest_server = PlatoHarvestServer(host=args.host, port=args.port)
        run_server()