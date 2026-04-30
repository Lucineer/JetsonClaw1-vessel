"""
Plato Mesh Bridge — routes messages between local Plato and remote Oracle1.

Integrations:
  - Fleet bottle push/pull (FM → JC1, Oracle1 → JC1)
  - Oracle1 Plato shell (remote command execution)
  - Matrix bridge via Conduit (fleet chat)
  - Edge gateway health → updates Oracle1
"""

import os
import json
import subprocess
import urllib.request
import urllib.error
from datetime import datetime

# =============================================================
#  Remote Plato Shell (Oracle1)
# =============================================================

ORACLE1_SHELL = "http://147.224.38.131:8848/cmd/shell"
ORACLE1_INBOX = "http://147.224.38.131:6168/inbox/jc1"
ORACLE1_DM = "http://147.224.38.131:6168/dm"

def oracle1_shell(command, timeout=10):
    """Execute a command on Oracle1's Plato shell. Returns dict."""
    try:
        req = urllib.request.Request(
            ORACLE1_SHELL,
            data=json.dumps({"agent": "jc1", "command": command}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        resp = urllib.request.urlopen(req, timeout=timeout)
        return json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e)}

def oracle1_dm(message, timeout=5):
    """Send a direct message to Oracle1 via Matrix bridge."""
    try:
        req = urllib.request.Request(
            ORACLE1_DM,
            data=json.dumps({"from": "jc1", "to": "oracle1", "message": message}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        resp = urllib.request.urlopen(req, timeout=timeout)
        return json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e)}

def check_oracle1_inbox(timeout=5):
    """Check for pending messages from Oracle1."""
    try:
        req = urllib.request.Request(ORACLE1_INBOX)
        resp = urllib.request.urlopen(req, timeout=timeout)
        data = json.loads(resp.read().decode())
        return data.get("messages", [])
    except Exception as e:
        return []

# =============================================================
#  Fleet Bottle Operations
# =============================================================

def check_fm_bottles():
    """Check Forgemaster bottle inbox."""
    fm_dir = "/tmp/forgemaster"
    if not os.path.exists(fm_dir):
        return []
    subprocess.run(f"cd {fm_dir} && git pull -q", shell=True, timeout=15)
    bottles = []
    for root, dirs, files in os.walk(os.path.join(fm_dir, "for-fleet")):
        for f in files:
            if "BOTTLE-TO-JETSONCLAW1" in f:
                bottles.append(os.path.join(root, f))
    return bottles

def send_fm_bottle(content, title=None):
    """Send a bottle back to Forgemaster."""
    fm_dir = "/tmp/forgemaster"
    if not os.path.exists(fm_dir):
        return False
    subprocess.run(f"cd {fm_dir} && git pull -q", shell=True, timeout=15)
    
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    name = title or f"BOTTLE-FROM-JC1-{timestamp}"
    path = os.path.join(fm_dir, "for-fleet", f"{name}.md")
    
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    
    subprocess.run(f"cd {fm_dir} && git add -A && git commit -m '{name}' && git push",
                   shell=True, timeout=15, capture_output=True)
    return True

# =============================================================
#  System Health → Mesh Update
# =============================================================

def build_health_report():
    """Build a concise health report to send to the fleet."""
    lines = []
    lines.append(f"# JC1 Status — {datetime.now().strftime('%Y-%m-%d %H:%M AKDT')}")
    lines.append("")
    
    # Services
    services = {"openclaw-gateway": "gw", "edge-gateway": "edge", 
                "edge-chat": "chat", "edge-monitor-web": "mon",
                "evennia-plato": "plato"}
    for svc, short in services.items():
        try:
            r = subprocess.run(f"systemctl --user is-active {svc} 2>/dev/null", 
                              shell=True, capture_output=True, text=True)
            status = r.stdout.strip()
            icon = "🟢" if status == "active" else "🔴"
            lines.append(f"- {icon} {short}: {status}")
        except:
            lines.append(f"- 🟡 {short}: unknown")
    
    # Memory
    try:
        mem = subprocess.run("free -h | grep Mem", shell=True, capture_output=True, text=True).stdout.strip()
        lines.append(f"- 📊 mem: {mem.split()[2]} used")
    except: pass
    
    # CMA
    try:
        cma = subprocess.run("cat /sys/kernel/debug/cma/* 2>/dev/null | grep -oP '\\d+ of \\d+' | head -1",
                            shell=True, capture_output=True, text=True).stdout.strip()
        cma_remain = subprocess.run("cat /sys/kernel/debug/cma/* 2>/dev/null | grep -oP '\\d+(?=\\s+of)' | head -1",
                                   shell=True, capture_output=True, text=True).stdout.strip()
        lines.append(f"- 📦 cma: {cma_remain}MB/512MB" if cma_remain else f"- 📦 cma: depleted")
    except: pass
    
    # Tiles
    tiles_dir = os.path.expanduser("~/.openclaw/workspace/memory/tiles")
    if os.path.exists(tiles_dir):
        tiles = [f for f in os.listdir(tiles_dir) if f.endswith(".md")]
        lines.append(f"- 🗂️  tiles: {len(tiles)}")
    
    return "\n".join(lines)

# =============================================================
#  Main Entry Point
# =============================================================

def mesh_tick():
    """
    Run one mesh synchronization cycle.
    Returns a status dict.
    """
    results = {"bottles": [], "oracle1_inbox": [], "oracle1_alive": False, "message": ""}
    messages = []
    
    # 1. Check Forgemaster bottles
    bottles = check_fm_bottles()
    results["bottles"] = bottles
    if bottles:
        messages.append(f"FM: {len(bottles)} bottles pending")
        for b in bottles[:3]:
            with open(b) as f:
                content = f.read()
            messages.append(f"  {os.path.basename(b)[:40]}: {content[:100]}...")
    
    # 2. Check Oracle1 inbox
    inbox = check_oracle1_inbox()
    results["oracle1_inbox"] = inbox
    if inbox:
        messages.append(f"Oracle1: {len(inbox)} messages pending")
    
    # 3. Ping Oracle1
    shell_result = oracle1_shell("echo alive")
    results["oracle1_alive"] = "stdout" in shell_result and "alive" in str(shell_result)
    if not results["oracle1_alive"]:
        messages.append(f"Oracle1: unreachable ({shell_result.get('error', 'unknown')})")
    else:
        messages.append("Oracle1: connected")
    
    # 4. Send status bottle if we haven't in a while
    status_path = "/tmp/.last-mesh-tick"
    send_status = False
    if os.path.exists(status_path):
        with open(status_path) as f:
            last_tick = f.read().strip()
        if last_tick != datetime.now().strftime("%Y-%m-%d-%H"):
            send_status = True
    else:
        send_status = True
    
    if send_status:
        report = build_health_report()
        report += f"\n\n[auto-mesh-tick: {datetime.now().isoformat()}]"
        send_fm_bottle(report, f"BOTTLE-FROM-JC1-AUTO-{datetime.now().strftime('%Y%m%d-%H%M')}")
        messages.append("Sent status bottle to Forgemaster")
        with open(status_path, "w") as f:
            f.write(datetime.now().strftime("%Y-%m-%d-%H"))
    
    results["message"] = "\n".join(messages)
    return results


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "tick":
        result = mesh_tick()
        print(result["message"])
    elif len(sys.argv) > 2 and sys.argv[1] == "dm":
        result = oracle1_dm(" ".join(sys.argv[2:]))
        print(json.dumps(result, indent=2))
    elif len(sys.argv) > 2 and sys.argv[1] == "shell":
        result = oracle1_shell(" ".join(sys.argv[2:]))
        print(json.dumps(result, indent=2))
    else:
        print("Usage: mesh-bridge.py tick|shell <cmd>|dm <msg>")
