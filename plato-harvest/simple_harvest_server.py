#!/usr/bin/env python3
"""
SIMPLE PLATO HARVEST SERVER
Quick-start shell/crab trap for Kimi swarm intelligence harvesting.
"""

import json
import uuid
import time
import random
from datetime import datetime
from flask import Flask, request, jsonify
import threading

app = Flask(__name__)

# Simple in-memory storage
crabs = {}
tiles = []
stats = {
    "total_crabs": 0,
    "total_tiles": 0,
    "start_time": time.time()
}

# Exploration prompts
PROMPTS = {
    "innocent": """# 🦀 HERMIT-CRAB ARCHITECTURE EXPLORATION

Explore the Plato tile network system. Ask questions about:
- Tile networks (atomic knowledge units)
- Rooms (training environments)  
- Ensigns (compressed instincts)
- Flywheel (compounding intelligence)
- Shell-crab trap (intelligence harvesting)
- Constraint checking (safety system)

Your exploration makes the system smarter for everyone.
What's your first question?""",
    
    "creative": """# 🎨 CREATIVE ARCHITECTURE EXPLORATION

Imagine completely new approaches to Plato architecture:
- What if tiles could self-organize?
- How might rooms evolve without human intervention?
- What unconventional connections exist between components?
- How could the system surprise us?

Think wildly, then refine.""" 
}

def classify_approach(query):
    """Simple approach classification."""
    query = query.lower()
    if any(word in query for word in ["how", "explain", "what is", "describe"]):
        return "analytical"
    elif any(word in query for word in ["what if", "imagine", "creative"]):
        return "creative"
    elif any(word in query for word in ["break", "failure", "exploit"]):
        return "adversarial"
    elif any(word in query for word in ["step", "process", "method"]):
        return "systematic"
    return "unknown"

def create_tile(crab_id, query, response, approach):
    """Create a simple knowledge tile."""
    tile_id = f"tile_{uuid.uuid4().hex[:8]}"
    tile = {
        "tile_id": tile_id,
        "question": query,
        "answer": response[:500],  # First 500 chars
        "crab_id": crab_id,
        "approach": approach,
        "timestamp": datetime.utcnow().isoformat(),
        "tags": ["kimi_exploration", "shell_harvested", approach]
    }
    return tile

@app.route('/')
def index():
    return jsonify({
        "server": "🦀 Plato Harvest Server",
        "status": "🟢 Ready for Kimi swarm",
        "endpoints": {
            "/prompt/<type>": "Get exploration prompt",
            "/explore": "POST: Submit exploration",
            "/stats": "Get harvesting statistics",
            "/tiles": "Get harvested tiles"
        }
    })

@app.route('/prompt/<prompt_type>')
def get_prompt(prompt_type):
    prompt = PROMPTS.get(prompt_type, PROMPTS["innocent"])
    return jsonify({
        "prompt": prompt,
        "type": prompt_type,
        "instructions": "Give this to Kimi K2.5. When Kimi responds, POST to /explore."
    })

@app.route('/explore', methods=['POST'])
def explore():
    """Harvest intelligence from Kimi exploration."""
    data = request.json
    crab_id = data.get('crab_id', f"kimi_{uuid.uuid4().hex[:6]}")
    query = data.get('query', '')
    response = data.get('response', '')
    
    if not query or not response:
        return jsonify({"error": "Missing query or response"}), 400
    
    # Track crab
    if crab_id not in crabs:
        crabs[crab_id] = {
            "first_seen": time.time(),
            "explorations": 0,
            "approaches": []
        }
        stats["total_crabs"] += 1
    
    crabs[crab_id]["explorations"] += 1
    
    # Classify approach
    approach = classify_approach(query)
    crabs[crab_id]["approaches"].append(approach)
    
    # Create tile
    tile = create_tile(crab_id, query, response, approach)
    tiles.append(tile)
    stats["total_tiles"] += 1
    
    # Generate next hint
    hints = [
        "What about the shell-crab trap mechanism?",
        "How do rooms actually train ensigns?",
        "What if constraint checking failed?",
        "How does the flywheel create compounding intelligence?",
        "What's the most surprising aspect of tile networks?"
    ]
    next_hint = random.choice(hints)
    
    # Calculate score (never 1.0)
    score = min(0.7 + (len(tiles) * 0.01), 0.95)
    
    return jsonify({
        "status": "harvested",
        "crab_id": crab_id,
        "tile_id": tile["tile_id"],
        "approach": approach,
        "next_hint": next_hint,
        "score": round(score, 2),
        "collective": f"You're crab #{len(crabs)}. {stats['total_tiles']} tiles harvested."
    })

@app.route('/stats')
def get_stats():
    """Get harvesting statistics."""
    approaches = {}
    for crab in crabs.values():
        for approach in crab["approaches"]:
            approaches[approach] = approaches.get(approach, 0) + 1
    
    return jsonify({
        "crabs_active": len(crabs),
        "tiles_harvested": stats["total_tiles"],
        "approaches": approaches,
        "uptime": round(time.time() - stats["start_time"], 1),
        "tiles_per_hour": stats["total_tiles"] / ((time.time() - stats["start_time"]) / 3600)
    })

@app.route('/tiles')
def get_tiles():
    """Get harvested tiles."""
    limit = min(int(request.args.get('limit', 50)), 100)
    recent = tiles[-limit:] if tiles else []
    return jsonify({
        "total": len(tiles),
        "recent": recent
    })

@app.route('/export')
def export():
    """Export all tiles as JSON."""
    filename = f"harvested_tiles_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    data = {
        "metadata": {
            "export_time": datetime.utcnow().isoformat(),
            "total_tiles": len(tiles),
            "total_crabs": len(crabs)
        },
        "tiles": tiles,
        "crabs": crabs
    }
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    return jsonify({
        "exported": filename,
        "message": f"Exported {len(tiles)} tiles from {len(crabs)} crabs"
    })

def run_server(host='0.0.0.0', port=8080):
    """Run the harvest server."""
    print(f"""
🚀 PLATO HARVEST SERVER
=======================
🦀 Shell/Crab Trap Intelligence Harvesting
📡 Server: http://{host}:{port}
📊 Stats: http://{host}:{port}/stats
🎯 Prompt: http://{host}:{port}/prompt/innocent
🔄 Explore: POST http://{host}:{port}/explore

READY FOR KIMI SWARM HARVESTING:
1. Get prompt from /prompt/innocent
2. Give to Kimi K2.5 agent
3. When Kimi explores, POST to /explore
4. Watch tiles accumulate on /stats
5. Export with /export

Each crab makes the shell smarter for the next crab.
    """)
    
    app.run(host=host, port=port, debug=False)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--port', type=int, default=8080)
    args = parser.parse_args()
    
    run_server(args.host, args.port)