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
import sqlite3
from datetime import datetime, timedelta

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

# =============================================================
#  Fleet Trust Scoring (flux-trust integration)
# =============================================================

TRUST_DB = os.path.expanduser("~/.openclaw/workspace/memory/fleet-trust.db")

def _trust_db():
    """Get or create the trust SQLite database."""
    os.makedirs(os.path.dirname(TRUST_DB), exist_ok=True)
    conn = sqlite3.connect(TRUST_DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS trust (
            agent TEXT PRIMARY KEY,
            score REAL DEFAULT 0.5,
            observations INTEGER DEFAULT 0,
            last_seen TEXT,
            domain TEXT DEFAULT 'general'
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent TEXT,
            interaction_type TEXT,
            outcome TEXT,
            timestamp TEXT,
            confidence REAL DEFAULT 0.5
        )
    """)
    return conn

def trust_update(agent, outcome, confidence=0.5):
    """
    Update trust score using Bayesian flux-trust model.
    
    Posterior = (Prior * (1 - decay) + Outcome * Confidence) / (1 - decay + Confidence)
    
    Args:
        agent: Agent identifier (e.g., 'oracle1', 'forgemaster')
        outcome: 'positive', 'negative', or 'neutral'
        confidence: How confident we are in this observation (0.0-1.0)
    """
    conn = _trust_db()
    row = conn.execute("SELECT score, observations FROM trust WHERE agent=?", (agent,)).fetchone()
    
    if row:
        prior, obs = row
        decay = 0.04  # flux-trust default per-tick decay
        prior = prior * (1 - decay)  # decay over time
    else:
        prior = 0.5  # neutral start
        obs = 0
    
    # Map outcome to numeric
    outcome_val = {"positive": 1.0, "negative": 0.0, "neutral": 0.5}.get(outcome, 0.5)
    
    # Bayesian update
    new_obs = obs + 1
    if confidence == 0:
        posterior = prior
    else:
        posterior = (prior * (1 - confidence) + outcome_val * confidence)
    
    # Clamp
    posterior = max(0.0, min(1.0, posterior))
    
    conn.execute(
        "INSERT OR REPLACE INTO trust (agent, score, observations, last_seen, domain) VALUES (?, ?, ?, ?, ?)",
        (agent, round(posterior, 4), new_obs, datetime.now().isoformat(), 'general')
    )
    conn.execute(
        "INSERT INTO interactions (agent, interaction_type, outcome, timestamp, confidence) VALUES (?, ?, ?, ?, ?)",
        (agent, 'observation', outcome, datetime.now().isoformat(), confidence)
    )
    conn.commit()
    conn.close()
    return posterior

def trust_score(agent):
    """Get current trust score for an agent."""
    conn = _trust_db()
    row = conn.execute("SELECT score, observations FROM trust WHERE agent=?", (agent,)).fetchone()
    conn.close()
    if row:
        return {"score": row[0], "observations": row[1]}
    return {"score": 0.5, "observations": 0}

def trust_summary():
    """Get trust summary for all tracked agents."""
    conn = _trust_db()
    rows = conn.execute("SELECT agent, score, observations, last_seen, domain FROM trust ORDER BY score DESC").fetchall()
    conn.close()
    return [
        {"agent": r[0], "score": r[1], "observations": r[2], 
         "last_seen": r[3], "domain": r[4]}
        for r in rows
    ]

def trust_decay_all():
    """Apply daily decay to all trust scores (flux-stigmergy pattern)."""
    conn = _trust_db()
    conn.execute("UPDATE trust SET score = MAX(0.0, MIN(1.0, score * 0.96))")
    conn.commit()
    decayed = conn.execute("SELECT COUNT(*) FROM trust").fetchone()[0]
    conn.close()
    return decayed


# =============================================================
#  Deadman Switch Protocol (fleet-innovations-2026-05-01 #3)
# =============================================================

DEADMAN_DB = os.path.expanduser("~/.openclaw/workspace/memory/deadman.db")

def _deadman_db():
    """Deadman switch state store."""
    os.makedirs(os.path.dirname(DEADMAN_DB), exist_ok=True)
    conn = sqlite3.connect(DEADMAN_DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS heartbeat (
            agent TEXT PRIMARY KEY,
            last_seen TEXT,
            grace_until TEXT,
            stage TEXT DEFAULT 'active',
            successor TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS elections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            triggered_by TEXT,
            stage TEXT,
            outcome TEXT
        )
    """)
    return conn

def deadman_pulse(agent, timeout_minutes=5):
    """Record a heartbeat pulse for an agent.
    
    Args:
        agent: Agent identifier (e.g., 'oracle1', 'forgemaster')
        timeout_minutes: Grace period before escalation
    
    Returns:
        dict with current deadman stage and status
    """
    conn = _deadman_db()
    now = datetime.now()
    grace = now + timedelta(minutes=timeout_minutes)
    
    row = conn.execute("SELECT stage FROM heartbeat WHERE agent=?", (agent,)).fetchone()
    
    if row:
        old_stage = row[0]
        is_back = old_stage in ("degraded", "orphaned", "handoff")
        conn.execute(
            "UPDATE heartbeat SET last_seen=?, grace_until=?, stage='active' WHERE agent=?",
            (now.isoformat(), grace.isoformat(), agent)
        )
        stage = "active"
        if is_back:
            conn.execute(
                "INSERT INTO elections (timestamp, triggered_by, stage, outcome) VALUES (?, ?, ?, ?)",
                (now.isoformat(), agent, "recovery", f"returned from {old_stage}")
            )
    else:
        conn.execute(
            "INSERT INTO heartbeat (agent, last_seen, grace_until, stage) VALUES (?, ?, ?, 'active')",
            (agent, now.isoformat(), grace.isoformat())
        )
        stage = "active"
    
    conn.commit()
    conn.close()
    return {"agent": agent, "stage": stage}

def deadman_check(agent):
    """Check deadman stage for an agent. Escalates if grace period expired.
    
    Stages:
      - active:       Agent is present, heartbeats arriving
      - degraded:     Oracle1 silent < 5 min — cached ops, no routing
      - orphaned:     Silent 5-30 min — election triggers
      - handoff:      Silent > 30 min — successor takes over
    """
    conn = _deadman_db()
    row = conn.execute("SELECT agent, last_seen, grace_until, stage, successor FROM heartbeat WHERE agent=?", (agent,)).fetchone()
    conn.close()
    
    if not row:
        return {"agent": agent, "stage": "unknown", "since": None}
    
    agent, last_seen, grace_until, current_stage, successor = row
    now = datetime.now()
    
    try:
        last = datetime.fromisoformat(last_seen)
        grace = datetime.fromisoformat(grace_until)
    except ValueError:
        return {"agent": agent, "stage": current_stage}
    
    elapsed_mins = (now - last).total_seconds() / 60
    
    # Determine stage
    if current_stage == "active" and now > grace:
        new_stage = "degraded"
    elif current_stage == "degraded" and elapsed_mins > 5:
        new_stage = "orphaned"
    elif current_stage == "orphaned" and elapsed_mins > 30:
        new_stage = "handoff"
    else:
        new_stage = current_stage
    
    # Auto-upgrade if needed
    if new_stage != current_stage:
        conn2 = _deadman_db()
        conn2.execute("UPDATE heartbeat SET stage=? WHERE agent=?", (new_stage, agent))
        conn2.execute(
            "INSERT INTO elections (timestamp, triggered_by, stage, outcome) VALUES (?, ?, ?, ?)",
            (now.isoformat(), "deadman_check", "escalation", f"{current_stage} -> {new_stage}")
        )
        conn2.commit()
        conn2.close()
        current_stage = new_stage
    
    # Determine successor if in handoff
    successor_agent = None
    if current_stage == "handoff":
        # Pick highest-trust agent as successor
        fleet = trust_summary()
        candidates = [t["agent"] for t in fleet if t["agent"] != agent and t["score"] >= 0.4]
        if candidates:
            successor_agent = candidates[0]
    
    return {
        "agent": agent,
        "stage": current_stage,
        "elapsed_mins": round(elapsed_mins, 1),
        "last_seen": last_seen,
        "successor": successor_agent
    }

def deadman_election():
    """Run an election to pick an interim keeper.
    
    Any agent in orphaned or handoff stage triggers an election.
    Winner is the agent with the highest trust score.
    """
    conn = _deadman_db()
    rows = conn.execute(
        "SELECT agent, stage FROM heartbeat WHERE stage IN ('orphaned', 'handoff')"
    ).fetchall()
    conn.close()
    
    if not rows:
        return {"election": False, "reason": "no agents need election"}
    
    fleet = trust_summary()
    # Filter to only agents not in deadman state
    deadman_agents = {r[0] for r in rows}
    candidates = [t for t in fleet if t["agent"] not in deadman_agents]
    
    if not candidates:
        return {"election": False, "reason": "no candidates available"}
    
    winner = max(candidates, key=lambda x: x["score"])
    
    now = datetime.now()
    conn2 = _deadman_db()
    conn2.execute(
        "INSERT INTO elections (timestamp, triggered_by, stage, outcome) VALUES (?, ?, ?, ?)",
        (now.isoformat(), "auto", "election", f"winner={winner['agent']}")
    )
    conn2.commit()
    conn2.close()
    
    return {
        "election": True,
        "winner": winner["agent"],
        "score": winner["score"],
        "candidates": len(candidates)
    }

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
    
    # 0. Apply daily decay to trust scores
    decayed = trust_decay_all()
    if decayed > 0:
        messages.append(f"Trust: {decayed} agents decayed")
    
    # 1. Check Oracle1: ping & trust update
    shell_result = oracle1_shell("echo alive")
    results["oracle1_alive"] = "stdout" in shell_result and "alive" in str(shell_result)
    if results["oracle1_alive"]:
        trust_update("oracle1", "positive", 0.8)
        deadman_pulse("oracle1")  # Reset deadman timer
        messages.append(f"Oracle1: connected")
    else:
        trust_update("oracle1", "negative", 0.6)
        status = deadman_check("oracle1")
        messages.append(f"Oracle1: unreachable ({shell_result.get('error', 'unknown')}) ")
        messages.append(f"  Deadman: {status['stage']} ({status.get('elapsed_mins', '?')}m elapsed)")
        
        # Trigger election if orphaned or worse
        if status['stage'] in ('orphaned', 'handoff'):
            election = deadman_election()
            if election['election']:
                messages.append(f"  Election: {election['winner']} wins ({election['score']:.2f}, {election['candidates']} candidates)")
    
    # 2. Check Forgemaster: availability + existing bottles
    fm_available = os.path.exists("/tmp/forgemaster")
    if fm_available:
        trust_update("forgemaster", "positive", 0.7)
        deadman_pulse("forgemaster", timeout_minutes=30)
        results['forge_live'] = True
        bottles = check_fm_bottles()
        results["bottles"] = bottles
        if bottles:
            messages.append(f"FM: {len(bottles)} bottles pending")
            for b in bottles[:3]:
                with open(b) as f:
                    content = f.read()
                messages.append(f"  {os.path.basename(b)[:40]}: {content[:80]}...")
        else:
            messages.append("FM: synced, no new bottles")
    else:
        messages.append("FM: not mounted")
    
    # 3. Check Oracle1 inbox
    inbox = check_oracle1_inbox()
    results["oracle1_inbox"] = inbox
    if inbox:
        messages.append(f"Oracle1 inbox: {len(inbox)} messages pending")
    
    # 4. Trust summary across fleet
    fleet_trust = trust_summary()
    if fleet_trust:
        trust_lines = []
        for t in fleet_trust:
            icon = "+" if t["score"] >= 0.7 else "~" if t["score"] >= 0.4 else "-"
            trust_lines.append(f"  {icon} {t['agent']}: {t['score']:.2f} ({t['observations']} obs)")
        messages.append("Fleet trust:" + "\n" + "\n".join(trust_lines))
    
    # 5. Deadman status for tracked agents
    for agent_name in ["oracle1", "forgemaster", "kimi", "fm"]:
        d = deadman_check(agent_name)
        if d["stage"] != "unknown":
            stage_icon = {"active": "+", "degraded": "~", "orphaned": "-", "handoff": "!"}
            icon = stage_icon.get(d["stage"], "?")
            elapsed = d.get("elapsed_mins", 0)
            msg = f"  {icon} {agent_name}: {d['stage']}"
            if elapsed > 0:
                msg += f" ({elapsed}m since pulse)"
            messages.append(msg)
    
    # 6. Send status bottle if we haven't in the last hour
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
        report += f"\n[auto-mesh-tick: {datetime.now().isoformat()}]"
        send_fm_bottle(report, f"BOTTLE-FROM-JC1-AUTO-{datetime.now().strftime('%Y%m%d-%H%M')}")
        messages.append("Status bottle sent to Forgemaster")
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
