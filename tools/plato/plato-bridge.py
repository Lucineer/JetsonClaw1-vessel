"""
plato-bridge.py — Bridge between Evennia MUD and our git-backed memory system.
Maps Plato commands to tile/memory operations and vice versa.

Inspired by: memsearch (zilliztech, trending 1.5K⭐) + beads (gastownhall, 22K⭐)
Adapted for: Evennia MUD rooms → Plato tiles → git persistence

Usage:
  Inside Evennia (MUD): tile/tile read/write/search/ls
  From shell:           python3 plato-bridge.py <command> [args]
  From agent:           memory/get, memory/set, memory/tile
"""

import os
import sys
import json
import glob
import subprocess
from datetime import datetime

WORKSPACE = os.path.expanduser("~/jetsonclaw1-vessel")
MEMORY_DIR = os.path.join(WORKSPACE, "memory")
TILES_DIR = os.path.join(MEMORY_DIR, "tiles")

# Plato room → tile directory mapping
ROOM_TILES = {
    "bridge": {"dir": MEMORY_DIR, "desc": "Captain's status and heartbeat"},
    "library": {"dir": TILES_DIR, "desc": "All knowledge tiles"},
    "harbor": {"dir": os.path.join(MEMORY_DIR, "tiles"), "desc": "Fleet knowledge"},
    "workshop": {"dir": TILES_DIR, "desc": "Technical lessons"},
    "lab": {"dir": TILES_DIR, "desc": "Research and experiments"},
    "dojo": {"dir": os.path.join(WORKSPACE, "tools"), "desc": "Skills and drills"},
}


def ensure_dirs():
    """Create directory structure if missing."""
    os.makedirs(TILES_DIR, exist_ok=True)
    os.makedirs(os.path.join(MEMORY_DIR, "archive"), exist_ok=True)


def room_list(room_name):
    """List tiles in a specific Plato room."""
    if room_name in ROOM_TILES:
        room = ROOM_TILES[room_name]
        files = sorted(glob.glob(os.path.join(room["dir"], "*.md")))
        print(f"\n📚 {room_name.title()} — {room['desc']}")
        print("=" * 40)
        for f in files:
            with open(f) as fh:
                first = fh.readline().strip().strip("#").strip()
            size = os.path.getsize(f)
            print(f"  {os.path.basename(f):35s} {first[:40]:40s} {size//1024}KB")
        print(f"\n  Total: {len(files)} tiles")
    else:
        # List all rooms
        print("🏛️  Plato Rooms & Their Knowledge")
        print("=" * 50)
        for name, room in sorted(ROOM_TILES.items()):
            count = len(glob.glob(os.path.join(room["dir"], "*.md")))
            print(f"  {name:12s} — {room['desc']:30s} ({count} tiles)")


def tile_read(tile_name):
    """Read a knowledge tile."""
    for root in [TILES_DIR, MEMORY_DIR]:
        path = os.path.join(root, tile_name)
        if not tile_name.endswith(".md"):
            path += ".md"
        if os.path.exists(path):
            with open(path) as f:
                return f.read()
    return f"❌ Tile not found: {tile_name}"


def tile_search(query):
    """Search across all tiles with context."""
    results = []
    for root in [TILES_DIR, os.path.join(MEMORY_DIR, "archive")]:
        for fpath in glob.glob(os.path.join(root, "*.md")):
            with open(fpath) as f:
                content = f.read()
                if query.lower() in content.lower():
                    name = os.path.basename(fpath)
                    # Find context around first match
                    lines = content.split("\n")
                    for i, line in enumerate(lines):
                        if query.lower() in line.lower():
                            start = max(0, i - 1)
                            end = min(len(lines), i + 2)
                            context = "\n".join(lines[start:end])
                            results.append({
                                "file": name,
                                "line": i + 1,
                                "context": context.strip(),
                                "path": fpath,
                            })
                            break
    return results


def tile_create(title, content, tags=None):
    """Create a new knowledge tile."""
    ensure_dirs()
    safe_name = title.lower().replace(" ", "_").replace("/", "-")[:50]
    path = os.path.join(TILES_DIR, f"{safe_name}.md")

    fm_lines = [
        "---",
        f"id: {safe_name}",
        f"created: {datetime.now().strftime('%Y-%m-%d')}",
        f"updated: {datetime.now().strftime('%Y-%m-%d')}",
        f"tags: [{', '.join(tags or ['new'])}]",
        "---",
        "",
        f"# {title}",
    ]

    full = "\n".join(fm_lines) + "\n\n" + content
    with open(path, "w") as f:
        f.write(full)

    # Git commit
    subprocess.run(
        f"cd {WORKSPACE} && git add {path} && git commit -m 'tile: {safe_name}'",
        shell=True, capture_output=True
    )

    return safe_name


def tile_delete(tile_name, archive=True):
    """Archive or delete a tile."""
    path = os.path.join(TILES_DIR, tile_name if tile_name.endswith(".md") else f"{tile_name}.md")
    if not os.path.exists(path):
        return f"❌ Tile not found: {tile_name}"

    if archive:
        archive_dir = os.path.join(MEMORY_DIR, "archive")
        os.makedirs(archive_dir, exist_ok=True)
        dest = os.path.join(archive_dir, tile_name.replace(".md", f"-archived-{datetime.now().strftime('%Y%m%d')}.md"))
        os.rename(path, dest)
        return f"📦 Archived: {tile_name} → {os.path.basename(dest)}"
    else:
        os.remove(path)
        return f"🗑️ Deleted: {tile_name}"


def recent(count=5):
    """Show most recently modified tiles."""
    tiles = sorted(glob.glob(os.path.join(TILES_DIR, "*.md")), key=os.path.getmtime, reverse=True)[:count]
    print(f"🆕 {count} Most Recent Tiles")
    print("=" * 50)
    for t in tiles:
        mtime = datetime.fromtimestamp(os.path.getmtime(t))
        with open(t) as f:
            title = f.readline().strip("#").strip()
        print(f"  {os.path.basename(t):40s} {mtime.strftime('%m-%d %H:%M'):12s} {title[:30]}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"

    if cmd == "ls":
        room = sys.argv[2] if len(sys.argv) > 2 else None
        room_list(room)

    elif cmd == "read":
        tile = sys.argv[2] if len(sys.argv) > 2 else input("Tile name: ")
        print(tile_read(tile))

    elif cmd == "search":
        query = sys.argv[2] if len(sys.argv) > 2 else input("Search: ")
        results = tile_search(query)
        if results:
            print(f"🔍 {len(results)} results:\n")
            for r in results[:10]:
                print(f"  📄 {r['file']}:{r['line']}")
                print(f"     ...{r['context'][:80]}")
                print()
        else:
            print(f"No results for '{query}'")

    elif cmd == "create":
        title = sys.argv[2] if len(sys.argv) > 2 else input("Title: ")
        tags = sys.argv[3].split(",") if len(sys.argv) > 3 else []
        content = sys.stdin.read() if not sys.stdin.isatty() else input("Content (multi-line, end with Ctrl+D or EOF):\n")
        safe = tile_create(title, content, tags)
        print(f"✅ Created: {safe}.md")

    elif cmd == "recent":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        recent(n)

    elif cmd == "delete":
        tile = sys.argv[2] if len(sys.argv) > 2 else input("Tile name: ")
        archive = sys.argv[3] != "--hard" if len(sys.argv) > 3 else True
        print(tile_delete(tile, archive))

    else:
        print("""🏛️  Plato Bridge — Memory System CLI

Commands:
  ls [room]          List tiles (optionally in a Plato room)
  read <tile>        Read a knowledge tile
  search <query>     Search across all tiles
  create <title>     Create a new tile (read content from stdin)
  recent [n]         Show N most recent tiles
  delete <tile>      Archive a tile (use --hard to delete)

Plato Rooms:
""")
        room_list(None)
