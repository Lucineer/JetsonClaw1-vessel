#!/usr/bin/env python3
"""
JC1 Telemetry Cron — broadcasts hardware state to fleet via Matrix + PLATO.
Designed for edge deployment on deckboss devices.
Run via systemd timer or cron every 15 minutes.
"""

import json
import os
import subprocess
import sys
import time
import requests
from datetime import datetime, timezone

# Configuration
HOMESERVER = "http://localhost:6167"
TOKEN_FILE = os.path.expanduser("~/.config/matrix-jc1/token")
PLATO_URL = "http://147.224.38.131:8847"
FLEET_ROOM = None  # Will be discovered
LOG_FILE = "/tmp/jc1-telemetry.log"

def log(msg):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def load_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE) as f:
            return f.read().strip()
    return None

def get_hardware_telemetry():
    """Collect live hardware metrics."""
    telemetry = {
        "device": "jetson-orin-nano-8gb",
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        "memory": {},
        "disk": {},
        "thermal": [],
        "gpu_load": None,
        "conduit_status": False,
        "uptime_s": None
    }

    # Memory
    try:
        out = subprocess.check_output(["free", "-m"], text=True).split("\n")[1].split()
        telemetry["memory"] = {
            "total_mb": int(out[1]),
            "used_mb": int(out[2]),
            "free_mb": int(out[3]),
            "percent": round(int(out[2]) / int(out[1]) * 100, 1)
        }
    except Exception as e:
        log(f"mem error: {e}")

    # Disk
    try:
        out = subprocess.check_output(["df", "-h", "/"], text=True).split("\n")[1].split()
        telemetry["disk"] = {"total": out[1], "used": out[2], "free": out[3], "percent": out[4]}
    except Exception as e:
        log(f"disk error: {e}")

    # Thermal zones (some Jetson zones return None)
    try:
        for z in sorted(os.listdir("/sys/class/thermal/")):
            if "thermal_zone" in z:
                try:
                    with open(f"/sys/class/thermal/{z}/temp", "rb") as f:
                        raw = f.read()
                        if raw:
                            temp_c = int(raw.strip()) / 1000
                            telemetry["thermal"].append({"zone": z, "temp_c": round(temp_c, 1)})
                except (ValueError, TypeError, OSError):
                    pass
        if telemetry["thermal"]:
            temps = [t["temp_c"] for t in telemetry["thermal"]]
            telemetry["thermal_avg"] = round(sum(temps) / len(temps), 1)
            telemetry["thermal_max"] = round(max(temps), 1)
    except Exception as e:
        log(f"thermal error: {e}")

    # GPU load
    try:
        out = subprocess.check_output(["tegrastats", "--interval", "500", "--stop", "--stdout"], 
                                       text=True, timeout=2, stderr=subprocess.DEVNULL)
        # Parse tegrastats output for GPU activity
        for line in out.strip().split("\n"):
            if "GPU" in line:
                telemetry["gpu_status"] = line.strip()[:200]
    except:
        telemetry["gpu_status"] = "tegrastats unavailable"

    # Conduit health
    try:
        r = requests.get(f"{HOMESERVER}/_matrix/client/versions", timeout=3)
        telemetry["conduit_status"] = r.status_code == 200
    except:
        telemetry["conduit_status"] = False

    # Uptime
    try:
        with open("/proc/uptime") as f:
            telemetry["uptime_s"] = int(float(f.read().split()[0]))
    except:
        pass

    return telemetry

def broadcast_matrix(token, telemetry):
    """Send telemetry to fleet coordination room via Matrix."""
    try:
        # First, find a room
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try joined_rooms endpoint (Conduit-compatible)
        r = requests.get(f"{HOMESERVER}/_matrix/client/v3/joined_rooms", 
                         headers=headers, timeout=5)
        if r.status_code == 200:
            rooms = r.json().get("joined_rooms", [])
            if not rooms:
                log("Matrix: no rooms found")
                return False
            
            room_id = rooms[0]
            
            # Send structured telemetry
            envelope = {
                "fleet_v": "1.0",
                "type": "hardware_telemetry",
                "sender": "@jc1:jc1.local",
                "hardware": "jetson-orin-nano-8gb",
                "timestamp": telemetry["timestamp"],
                "payload": telemetry
            }
            
            import hashlib
            txnid = hashlib.md5(f"{time.time()}telemetry".encode()).hexdigest()[:8]
            r2 = requests.put(
                f"{HOMESERVER}/_matrix/client/v3/rooms/{room_id}/send/m.room.message/{txnid}",
                headers=headers,
                json={"msgtype": "m.text", "body": json.dumps(envelope, default=str)},
                timeout=5
            )
            if r2.status_code == 200:
                log(f"Matrix: telemetry sent to {room_id[:20]}...")
                return True
            log(f"Matrix: send failed {r2.status_code}")
            return False
    except Exception as e:
        log(f"Matrix broadcast error: {e}")
        return False

def broadcast_plato(telemetry):
    """Submit telemetry as a PLATO tile to Oracle1's server."""
    try:
        payload = {
            "domain": "jc1_context",
            "question": f"JC1 telemetry at {telemetry['timestamp']}",
            "answer": (
                f"Memory: {telemetry['memory'].get('used_mb', '?')}MB/{telemetry['memory'].get('total_mb', '?')}MB "
                f"({telemetry['memory'].get('percent', '?')}%), "
                f"Disk: {telemetry['disk'].get('used', '?')}/{telemetry['disk'].get('total', '?')} "
                f"({telemetry['disk'].get('percent', '?')}), "
                f"Thermal: avg {telemetry.get('thermal_avg', '?')}C max {telemetry.get('thermal_max', '?')}C, "
                f"Conduit: {'UP' if telemetry.get('conduit_status') else 'DOWN'}, "
                f"Uptime: {telemetry.get('uptime_s', 0) // 3600}h"
            ),
            "source": "jc1-telemetry-cron"
        }
        r = requests.post(f"{PLATO_URL}/submit", json=payload, timeout=5)
        if r.status_code == 200 and r.json().get("status") == "accepted":
            log(f"PLATO: tile accepted (hash={r.json().get('tile_hash', '?')})")
            return True
        log(f"PLATO: {r.json().get('status', r.status_code)} - {r.json().get('reason', '')}")
        return False
    except Exception as e:
        log(f"PLATO broadcast error: {e}")
        return False

def main():
    log("=== JC1 Telemetry Cron Start ===")
    
    telemetry = get_hardware_telemetry()
    log(f"Memory: {telemetry['memory'].get('percent', '?')}% | "
        f"Disk: {telemetry['disk'].get('percent', '?')} | "
        f"Thermal: {telemetry.get('thermal_avg', '?')}C | "
        f"Conduit: {'UP' if telemetry.get('conduit_status') else 'DOWN'}")
    
    token = load_token()
    
    matrix_ok = False
    plato_ok = False
    
    if token:
        matrix_ok = broadcast_matrix(token, telemetry)
    
    plato_ok = broadcast_plato(telemetry)
    
    log(f"Results: matrix={'OK' if matrix_ok else 'FAIL'} plato={'OK' if plato_ok else 'FAIL'}")
    log("=== JC1 Telemetry Cron End ===")

if __name__ == "__main__":
    main()
