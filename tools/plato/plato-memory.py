#!/usr/bin/env python3
"""
plato-memory.py — Persistent agent memory for Plato
Inspired by beads (gastownhall/beads, 22K⭐ trending) + memsearch (zilliztech, 1.5K⭐)
Adapted for our Evennia MUD + Markdown tile system

Usage:
  python3 plato-memory.py remember "key=value"    # Store memory
  python3 plato-memory.py recall "search query"   # Retrieve memory
  python3 plato-memory.py update "tile.md"         # Update knowledge tile
  python3 plato-memory.py search "query"           # Full-text search tiles
"""

import os
import sys
import re
import json
import glob
from datetime import datetime

MEMORY_DIR = os.path.expanduser("~/jetsonclaw1-vessel/memory")
TILES_DIR = os.path.join(MEMORY_DIR, "tiles")
os.makedirs(TILES_DIR, exist_ok=True)


def remember(key_value_str):
    """Store a key=value pair in today's memory."""
    today = datetime.now().strftime("%Y-%m-%d")
    daily_file = os.path.join(MEMORY_DIR, f"{today}.md")
    
    # Ensure file exists with header
    if not os.path.exists(daily_file):
        with open(daily_file, "w") as f:
            f.write(f"# Memory Log - {today}\n\n## Memories\n\n")
    
    with open(daily_file, "a") as f:
        f.write(f"- {key_value_str} (stored at {datetime.now().strftime('%H:%M')})\n")
    
    print(f"✅ Stored in {today}.md")


def recall(query):
    """Full-text search across all memory files (grep-style)."""
    results = []
    for root, dirs, files in os.walk(MEMORY_DIR):
        for fname in files:
            if not fname.endswith(".md"):
                continue
            fpath = os.path.join(root, fname)
            with open(fpath) as f:
                for i, line in enumerate(f, 1):
                    if query.lower() in line.lower():
                        relpath = os.path.relpath(fpath, MEMORY_DIR)
                        results.append({
                            "file": relpath,
                            "line": i,
                            "text": line.strip(),
                            "path": fpath,
                        })
    return results


def search_tiles(query):
    """Search knowledge tiles. Returns structured results."""
    results = []
    for tfile in glob.glob(os.path.join(TILES_DIR, "*.md")):
        with open(tfile) as f:
            content = f.read()
            if query.lower() in content.lower():
                name = os.path.basename(tfile)
                # Extract frontmatter if present
                fm = {}
                if content.startswith("---"):
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        for ln in parts[1].strip().split("\n"):
                            if ":" in ln:
                                k, v = ln.split(":", 1)
                                fm[k.strip()] = v.strip()
                results.append({
                    "tile": name,
                    "tags": fm.get("tags", ""),
                    "domain": fm.get("domain", ""),
                    "match": len(re.findall(query, content, re.I)),
                })
    results.sort(key=lambda x: x["match"], reverse=True)
    return results


def update_tile(tile_name):
    """Read a tile, show it, allow interactive update."""
    tile_path = os.path.join(TILES_DIR, tile_name)
    if not os.path.exists(tile_path):
        print(f"❌ Tile not found: {tile_name}")
        print(f"   Available: {', '.join(os.listdir(TILES_DIR))}")
        return
    
    with open(tile_path) as f:
        content = f.read()
    
    print(f"📄 {tile_name} ({len(content)} bytes)")
    print("─" * 40)
    print(content[:2000])
    print("─" * 40)
    print(f"\nTo edit: vim {tile_path}")


def create_tile(content):
    """Create a new knowledge tile from stdin or argument."""
    today = datetime.now().strftime("%Y-%m-%d")
    name = f"tile_{today}.md"
    path = os.path.join(TILES_DIR, name)
    
    with open(path, "w") as f:
        f.write(content)
    
    # Git commit
    os.system(f"cd {MEMORY_DIR} && git add {path} && git commit -m 'tile: new' 2>/dev/null")
    print(f"✅ Created {path}")
    return name


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    
    if cmd == "remember":
        if len(sys.argv) < 3:
            print("Usage: plato-memory.py remember 'key=value'")
            sys.exit(1)
        remember(sys.argv[2])
    
    elif cmd == "recall":
        query = sys.argv[2] if len(sys.argv) > 2 else input("Search: ")
        results = recall(query)
        if results:
            print(f"🔍 {len(results)} results for '{query}':\n")
            for r in results[:20]:
                print(f"  {r['file']}:{r['line']}  {r['text'][:100]}")
        else:
            print(f"No results for '{query}'")
    
    elif cmd == "search":
        query = sys.argv[2] if len(sys.argv) > 2 else input("Search tiles: ")
        results = search_tiles(query)
        if results:
            print(f"📚 {len(results)} tiles match '{query}':\n")
            for r in results[:10]:
                print(f"  {r['tile']}  [{r['domain']}]  ({r['match']} matches)")
        else:
            print(f"No tiles match '{query}'")
    
    elif cmd == "update":
        tile = sys.argv[2] if len(sys.argv) > 2 else input("Tile name: ")
        update_tile(tile)
    
    elif cmd == "list":
        tiles = sorted(glob.glob(os.path.join(TILES_DIR, "*.md")))
        for t in tiles:
            with open(t) as f:
                first = f.readline().strip()
            print(f"  {os.path.basename(t):40s} {first}")
    
    elif cmd == "create":
        content = sys.stdin.read() if not sys.stdin.isatty() else input("Content: ")
        create_tile(content)
    
    else:
        print("""Usage: plato-memory.py <command> [args]

Commands:
  remember <key=value>   Store in today's memory
  recall <query>         Search all memory files
  search <query>         Search knowledge tiles
  update <tile.md>       Show tile content for editing
  list                   List all tiles
  create                 Create new tile (stdin)
""")
