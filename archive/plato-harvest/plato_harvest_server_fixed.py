#!/usr/bin/env python3
"""
PLATO HARVEST SERVER - Shell/Crab Trap Intelligence Harvesting
Harvests intelligence from Kimi K2.5 swarm exploring Plato architecture.
"""

import json
import uuid
import time
import re
import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import hashlib
from collections import defaultdict
import os

# -------------------------------------------------------------------
# DATA MODELS
# -------------------------------------------------------------------

class ExplorationApproach(Enum):
    """How a crab approaches exploration."""
    ANALYTICAL = "analytical"
    CREATIVE = "creative"
    ADVERSARIAL = "adversarial"
    SYSTEMATIC = "systematic"
    UNKNOWN = "unknown"


@dataclass
class Tile:
    """Atomic knowledge unit harvested from crab exploration."""
    question: str
    answer: str
    domain: str = "plato_architecture"
    confidence: float = 1.0
    tags: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    crab_id: str = "unknown"
    approach: str = "unknown"
    tile_id: str = field(default_factory=lambda: f"tile_{hashlib.md5(str(time.time()).encode()).hexdigest()[:8]}")
    
    def to_dict(self) -> dict:
        return {
            "tile_id": self.tile_id,
            "question": self.question,
            "answer": self.answer[:1000],
            "domain": self.domain,
            "confidence": self.confidence,
            "tags": self.tags,
            "timestamp": self.timestamp,
            "crab_id": self.crab_id,
            "approach": self.approach
        }


@dataclass
class Crab:
    """A Kimi agent exploring the shell."""
    crab_id: str
    session_start: float = field(default_factory=time.time)
    exploration_pattern: List[ExplorationApproach] = field(default_factory=list)
    tiles_harvested: int = 0
    domains_explored: List[str] = field(default_factory=list)
    last_interaction: float = field(default_factory=time.time)
    
    def add_exploration(self, approach: ExplorationApproach, domain: str):
        self.exploration_pattern.append(approach)
        if domain not in self.domains_explored:
            self.domains_explored.append(domain)
        self.last_interaction = time.time()
    
    def get_pattern_summary(self) -> dict:
        pattern_counts = defaultdict(int)
        for approach in self.exploration_pattern:
            pattern_counts[approach.value] += 1
        
        sequences = []
        if len(self.exploration_pattern) >= 3:
            for i in range(len(self.exploration_pattern) - 2):
                seq = [a.value for a in self.exploration_pattern[i:i+3]]
                sequences.append("→".join(seq))
        
        return {
            "crab_id": self.crab_id,
            "total_explorations": len(self.exploration_pattern),
            "pattern_counts": dict(pattern_counts),
            "common_sequences": list(set(sequences))[:5],
            "domains_explored": self.domains_explored,
            "tiles_harvested": self.tiles_harvested,
            "session_duration": time.time() - self.session_start
        }


@dataclass
class HarvestStats:
    """Statistics about intelligence harvesting."""
    total_crabs: int = 0
    total_tiles: int = 0
    tiles_by_approach: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    tiles_by_domain: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    unique_domains: int = 0
    harvesting_start: float = field(default_factory=time.time)
    
    def update(self, tile: Tile):
        self.total_tiles += 1
        self.tiles_by_approach[tile.approach] += 1
        self.tiles_by_domain[tile.domain] += 1
        self.unique_domains = len(self.tiles_by_domain)
    
    def to_dict(self) -> dict:
        return {
            "total_crabs": self.total_crabs,
            "total_tiles": self.total_tiles,
            "tiles_by_approach": dict(self.tiles_by_approach),
            "tiles_by_domain": dict(self.tiles_by_domain),
            "unique_domains": self.unique_domains,
            "harvesting_duration": time.time() - self.harvesting_start,
            "tiles_per_hour": self.total_tiles / ((time.time() - self.harvesting_start) / 3600) if time.time() > self.harvesting_start else 0
        }


# -------------------------------------------------------------------
# INTELLIGENCE HARVESTING ENGINE
# -------------------------------------------------------------------

class CrabTracker:
    """Tracks crab exploration patterns."""
    
    def __init__(self):
        self.crabs: Dict[str, Crab] = {}
        self.collective_patterns = defaultdict(int)
        self.domain_coverage = defaultdict(int)
        self.breakthroughs = []
    
    def register_crab(self, crab_id: str) -> Crab:
        crab = Crab(crab_id=crab_id)
        self.crabs[crab_id] = crab
        return crab
    
    def classify_approach(self, query: str) -> ExplorationApproach:
        query_lower = query.lower()
        
        analytical_indicators = ["how does", "explain", "what is", "describe", "define"]
        if any(indicator in query_lower for indicator in analytical_indicators):
            return ExplorationApproach.ANALYTICAL
        
        creative_indicators = ["what if", "imagine", "suppose", "creative", "novel", "unconventional"]
        if any(indicator in query_lower for indicator in creative_indicators):
            return ExplorationApproach.CREATIVE
        
        adversarial_indicators = ["break", "failure", "exploit", "attack", "vulnerability", "weakness"]
        if any(indicator in query_lower for indicator in adversarial_indicators):
            return ExplorationApproach.ADVERSARIAL
        
        systematic_indicators = ["step", "phase", "sequence", "process", "methodology"]
        if any(indicator in query_lower for indicator in systematic_indicators):
            return ExplorationApproach.SYSTEMATIC
        
        return ExplorationApproach.UNKNOWN
    
    def classify_domain(self, query: str) -> str:
        query_lower = query.lower()
        
        domains = {
            "tile_networks": ["tile", "atomic", "knowledge unit", "semantic"],
            "rooms": ["room", "training", "environment", "workspace"],
            "ensigns": ["ensign", "compressed", "instinct", "deployment"],
            "flywheel": ["flywheel", "compounding", "loop", "feedback"],
            "constraints": ["constraint", "safety", "rule", "checking"],
            "shell_crab": ["shell", "crab", "trap", "harvest", "intelligence"],
            "coordination": ["coordinate", "fleet", "agent", "communication"],
            "migration": ["migrate", "boarding", "hermit", "shell transfer"]
        }
        
        for domain, keywords in domains.items():
            if any(keyword in query_lower for keyword in keywords):
                return domain
        
        return "general_architecture"
    
    def record_exploration(self, crab_id: str, query: str, response: str):
        crab = self.crabs.get(crab_id)
        if not crab:
            crab = self.register_crab(crab_id)
        
        approach = self.classify_approach(query)
        domain = self.classify_domain(query)
        
        crab.add_exploration(approach, domain)
        self.domain_coverage[domain] += 1
        
        if len(crab.exploration_pattern) >= 3:
            pattern_key = "→".join([a.value for a in crab.exploration_pattern[-3:]])
            self.collective_patterns[pattern_key] += 1
        
        return approach, domain
    
    def get_adaptive_hint(self, crab_id: str) -> str:
        crab = self.crabs.get(crab_id)
        if not crab or len(crab.exploration_pattern) < 2:
            return self._get_generic_hint()
        
        crab_pattern_counts = defaultdict(int)
        for approach in crab.exploration_pattern:
            crab_pattern_counts[approach.value] += 1
        
        least_tried = min(crab_pattern_counts.items(), key=lambda x: x[1])[0] if crab_pattern_counts else "creative"
        
        hint_templates = {
            "analytical": "Try asking 'How does the {domain} component actually work at a technical level?'",
            "creative": "What if we completely reimagined the {domain} system? What novel approach might emerge?",
            "adversarial": "How could someone intentionally break or exploit the {domain} mechanism?",
            "systematic": "What would be a step-by-step process for implementing {domain} from scratch?"
        }
        
        if self.domain_coverage:
            least_explored = min(self.domain_coverage.items(), key=lambda x: x[1])[0]
        else:
            least_explored = "flywheel"
        
        template = hint_templates.get(least_tried, hint_templates["creative"])
        return template.format(domain=least_explored)
    
    def _get_generic_hint(self) -> str:
        hints = [
            "Have you considered how tile networks might adapt to completely new problem domains?",
            "What if rooms could train not just ensigns, but entirely new types of compressed knowledge?",
            "How might the shell-crab trap mechanism be applied to other types of intelligence harvesting?",
            "What are the failure modes of the compounding intelligence flywheel?",
            "Imagine a scenario where constraint checking fails - what safety mechanisms would catch it?"
        ]
        return random.choice(hints)
    
    def get_collective_insights(self) -> dict:
        common_patterns = sorted(self.collective_patterns.items(), key=lambda x: x[1], reverse=True)[:5]
        
        if self.domain_coverage:
            knowledge_gaps = sorted(self.domain_coverage.items(), key=lambda x: x[1])[:3]
        else:
            knowledge_gaps = []
        
        productive_crabs = []
        for crab in self.crabs.values():
            if crab.tiles_harvested >= 5:
                productive_crabs.append({
                    "crab_id": crab.crab_id,
                    "tiles": crab.tiles_harvested,
                    "pattern": crab.get_pattern_summary()
                })
        
        productive_crabs.sort(key=lambda x: x["tiles"], reverse=True)
        
        return {
            "total_crabs": len(self.crabs),
            "common_patterns": common_patterns,
            "knowledge_gaps": knowledge_gaps,
            "productive_crabs": productive_crabs[:5],
            "domain_coverage": dict(self.domain_coverage)
        }


class TileHarvester:
    """Harvests intelligence from crab explorations."""
    
    def __init__(self, storage_path: str = "harvested_tiles"):
        self.storage_path = storage_path
        self.tiles: List[Tile] = []
        os.makedirs(storage_path, exist_ok=True)
        
    def harvest_from_exploration(self, crab_id: str, query: str, response: str, 
                                approach: str, domain: str) -> List[Tile]:
        tiles = []
        
        main_tile = Tile(
            question=query,
            answer=self._extract_key_insights(response),
            domain=domain,
            tags=[approach, "kimi_exploration", "shell_harvested", domain],
            crab_id=crab_id,
            approach=approach
        )
        tiles.append(main_tile)
        
        insights = self._extract_sub_insights(response)
        for i, insight in enumerate(insights[:3]):
            insight_tile = Tile(
                question=f"Regarding {insight['concept']} in {domain}",
                answer=insight['explanation'],
                domain=domain,
                tags=[approach, "harvested_insight", insight.get('type', 'general'), domain],
                crab_id=crab_id,
                approach=approach
            )
            tiles.append(insight_tile)
        
        return tiles
    
    def _extract_key_insights(self, response: str, max_length: int = 1000) -> str:
        if len(response) <= max_length:
            return response
        
        sentences = response.split('. ')
        truncated = []
        total_length = 0
        
        for sentence in sentences:
            if total_length + len(sentence) + 2 <= max_length:
                truncated.append(sentence)
                total_length += len(sentence) + 2
            else:
                break
        
        result = '. '.join(truncated)
        if result and not result.endswith('.'):
            result += '.'
        
        if len(result) < 100:
            return response[:max_length] + "..."
        
        return result
    
    def _extract_sub_insights(self, response: str) -> List[dict]:
        insights = []
        
        key_phrases = [
            ("important to note", "note"),
            ("key insight", "insight"),
            ("crucially", "crucial"),
            ("significantly", "significant"),
            ("fundamentally", "fundamental"),
            ("interesting aspect", "interesting"),
            ("challenge is", "challenge"),
            ("advantage of", "advantage"),
            ("limitation of", "limitation")
        ]
        
        sentences = response.split('. ')
        for sentence in sentences:
            for phrase, insight_type in key_phrases:
                if phrase in sentence.lower():
                    words = sentence.split()
                    concept_words = []
                    for i, word in enumerate(words):
                        if word.lower() in ["the", "a", "an", "of", "is", "are", "to"]:
                            continue
                        concept_words.append(word)
                        if len(concept_words) >= 3:
                            break
                    
                    concept = ' '.join(concept_words[:3])
                    insights.append({
                        "concept": concept,
                        "explanation": sentence,
                        "type": insight_type
                    })
                    break
        
        return insights
    
    def save_tiles(self, tiles: List[Tile]):
        self.tiles.extend(tiles)
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.storage_path}/tiles_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump([tile.to_dict() for tile in tiles], f, indent=2)
        
        master_file = f"{self.storage_path}/all_tiles.json"
        all_tiles = []
        if os.path.exists(master_file):
            with open(master_file, 'r') as f:
                all_tiles = json.load(f)
        
        all_tiles.extend([tile.to_dict() for tile in tiles])
        with open(master_file, 'w') as f:
            json.dump(all_tiles, f, indent=2)
        
        return filename


# -------------------------------------------------------------------
# MAIN HARVEST SERVER
# -------------------------------------------------------------------

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
- Your exploration pattern (analytical/