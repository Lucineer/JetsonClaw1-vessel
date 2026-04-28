#!/usr/bin/env python3
"""
fleet-agent.py — Multi-agent coordination for the fleet
Inspired by gascity (gastownhall, 508⭐) + multica (22K⭐) + GenericAgent (8K⭐)
Patterns: task assignment, skill composition, memory persistence

Usage:
  python3 fleet-agent.py dispatch "task description" --agent jc1
  python3 fleet-agent.py status
  python3 fleet-agent.py compose "research → build → test"
"""

import os
import sys
import json
import subprocess
from datetime import datetime

# Fleet registry — known agents and their skills
FLEET = {
    "jc1": {
        "name": "JetsonClaw1",
        "vessel": "JetsonClaw1-vessel",
        "skills": ["hardware", "edge-ai", "cuda", "arm64", "rust", "python"],
        "memory": os.path.expanduser("~/jetsonclaw1-vessel/memory"),
        "capabilities": ["compile", "benchmark", "inference", "on-metal"],
    },
    "oracle1": {
        "name": "Oracle1",
        "vessel": "oracle1-vessel",
        "skills": ["cloud", "plato", "architecture", "knowledge", "typescript"],
        "memory": None,  # remote
        "capabilities": ["design", "research", "coordinate", "lighthouse"],
        "api": "http://147.224.38.131:8848",
    },
    "fm": {
        "name": "Forgemaster",
        "vessel": "forgemaster",
        "skills": ["bottles", "coordination", "fleet", "routing"],
        "memory": "/tmp/forgemaster",
        "capabilities": ["route-bottle", "distribute", "test-pipeline"],
    },
}

# Composition patterns from GenericAgent skill tree concept
COMPOSITIONS = {
    "build-from-research": [
        {"step": "research", "agent": "oracle1", "skill": "research"},
        {"step": "implement", "agent": "jc1", "skill": "code"},
        {"step": "test", "agent": "jc1", "skill": "compile"},
        {"step": "distribute", "agent": "fm", "skill": "route-bottle"},
    ],
    "edge-pipeline": [
        {"step": "design", "agent": "oracle1", "skill": "design"},
        {"step": "build", "agent": "jc1", "skill": "edge-ai"},
        {"step": "benchmark", "agent": "jc1", "skill": "benchmark"},
        {"step": "ship", "agent": "fm", "skill": "distribute"},
    ],
    "knowledge-ingest": [
        {"step": "fetch", "agent": "jc1", "skill": "research"},
        {"step": "structure", "agent": "oracle1", "skill": "knowledge"},
        {"step": "store", "agent": "jc1", "skill": "memory"},
        {"step": "index", "agent": "oracle1", "skill": "plato"},
    ],
}


def dispatch(task: str, target_agent: str = None):
    """Dispatch a task to an agent or across the fleet."""
    if target_agent and target_agent in FLEET:
        agent = FLEET[target_agent]
        print(f"🎯 Dispatch to {agent['name']} ({target_agent}):")
        print(f"   Task: {task}")
        print(f"   Skills: {', '.join(agent['skills'])}")
        if agent.get("api"):
            print(f"   API: {agent['api']}")
        
        # Write bottle
        bottle = {
            "to": target_agent,
            "from": "jc1",
            "task": task,
            "timestamp": datetime.now().isoformat(),
        }
        bottle_path = f"/tmp/bottle-TO-{target_agent.upper()}-{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        with open(bottle_path, "w") as f:
            json.dump(bottle, f, indent=2)
        print(f"   📦 Bottle: {bottle_path}")
        return bottle
    
    # No target — pick best agent
    best, score = None, 0
    for name, agent in FLEET.items():
        s = sum(1 for skill in agent["skills"] if skill.lower() in task.lower())
        if s > score:
            score = s
            best = name
    
    if best:
        return dispatch(task, best)
    
    return {"error": "No suitable agent found"}


def compose(pattern: str):
    """Execute a composition pattern across multiple agents."""
    if pattern in COMPOSITIONS:
        steps = COMPOSITIONS[pattern]
    else:
        # Parse shorthand: "research → build → test"
        steps = [{"step": s.strip().lower(), "agent": "auto", "skill": s.strip().lower()}
                 for s in pattern.split("→")]
    
    print(f"🧩 Composition: {pattern}")
    print("-" * 40)
    for i, step in enumerate(steps, 1):
        agent_name = step["agent"]
        if step["agent"] == "auto":
            # Auto-assign based on skill
            for name, agent in FLEET.items():
                if step["skill"] in agent["skills"]:
                    agent_name = name
                    break
        
        print(f"  Step {i}: {step['step']} → {agent_name.upper()} ({step['skill']})")
        
        # Generate bottle for each step
        bottle = {
            "to": agent_name,
            "from": "jc1",
            "composition": pattern,
            "step": step["step"],
            "skill": step["skill"],
            "timestamp": datetime.now().isoformat(),
        }
        bottle_path = f"/tmp/bottle-COMPOSE-{i}-TO-{agent_name.upper()}.json"
        with open(bottle_path, "w") as f:
            json.dump(bottle, f, indent=2)
        print(f"     📦 Bottle: {bottle_path}")
    
    print("-" * 40)
    print(f"✅ {len(steps)} tasks dispatched via bottles")


def status():
    """Show fleet status."""
    print("🚢 Fleet Status")
    print("=" * 50)
    for name, agent in FLEET.items():
        print(f"\n  {name} ({agent['name']})")
        print(f"    Vessel: {agent['vessel']}")
        print(f"    Skills: {', '.join(agent['skills'])}")
        print(f"    Caps:   {', '.join(agent['capabilities'])}")
        if agent.get("api"):
            print(f"    API:    {agent['api']}")
        if agent.get("memory") and os.path.isdir(agent["memory"]):
            print(f"    Memory: {agent['memory']} ({sum(len(files) for _, _, files in os.walk(agent['memory']))} files)")


def discover(prompt: str) -> dict:
    """Discover which agent(s) to use from a natural language request."""
    keywords = prompt.lower().split()
    
    # Score each agent
    scores = {}
    for name, agent in FLEET.items():
        score = sum(1 for skill in agent["skills"] for kw in keywords if kw in skill.lower())
        score += sum(1 for cap in agent["capabilities"] for kw in keywords if kw in cap.lower())
        scores[name] = score
    
    if not scores:
        return {"agents": []}
    
    max_score = max(scores.values())
    if max_score == 0:
        return {"agents": []}
    
    best = [name for name, score in scores.items() if score == max_score]
    return {"agents": best, "reason": f"Best skill match score: {max_score}"}


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    
    if cmd == "dispatch":
        task = " ".join(sys.argv[2:])
        if "--agent" in task:
            parts = task.split("--agent")
            task = parts[0].strip()
            agent = parts[1].strip() if len(parts) > 1 else None
        else:
            agent = None
        if not task:
            task = input("Task: ")
        print(json.dumps(dispatch(task, agent), indent=2))
    
    elif cmd == "compose":
        pattern = " ".join(sys.argv[2:]) or input("Pattern (e.g., 'research → build → test'): ")
        compose(pattern)
    
    elif cmd == "status":
        status()
    
    elif cmd == "discover":
        prompt = " ".join(sys.argv[2:]) or input("What do you need? ")
        print(json.dumps(discover(prompt), indent=2))
    
    else:
        print("""Usage: fleet-agent.py <command> [args]

Commands:
  dispatch <task> [--agent <name>]   Send task to an agent
  compose <pattern>                   Execute multi-agent composition
  status                             Fleet health check
  discover <prompt>                  Discover best agent for a task

Examples:
  fleet-agent.py dispatch "benchmark LiteRT-LM on Jetson" --agent jc1
  fleet-agent.py compose "research → build → test"
  fleet-agent.py discover "I need to do some edge AI research"
""")
