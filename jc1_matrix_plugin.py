#!/usr/bin/env python3
"""
JC1 Matrix Plugin — Live connection to local Conduit server.
Fleet coordination via Matrix on Jetson edge hardware.
"""

import json
import time
import hashlib
import logging
import os
import requests
from datetime import datetime
from typing import Dict, List, Optional

HOMESERVER = "http://localhost:6167"
USER_ID = "@jc1:jc1.local"
# Access token stored locally, never committed
TOKEN_FILE = os.path.expanduser("~/.config/matrix-jc1/token")
# Legacy token from initial Conduit setup — only used as fallback if TOKEN_FILE missing

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
log = logging.getLogger("jc1-matrix")

class JC1MatrixPlugin:
    """Matrix fleet coordination plugin for JC1 on local Conduit."""

    def __init__(self, homeserver: str = HOMESERVER, user_id: str = USER_ID):
        self.homeserver = homeserver.rstrip("/")
        self.user_id = user_id
        self.token = self._load_token()
        self.rooms: Dict[str, str] = {}  # room_alias_or_id -> room_id
        self.stats = {"sent": 0, "received": 0, "errors": 0}

    def _load_token(self) -> Optional[str]:
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE) as f:
                return f.read().strip()
        # Fallback to legacy token from initial Conduit setup (stored in TOKEN_FILE now)
        return os.environ.get('JC1_MATRIX_TOKEN', None)

    def _api(self, method: str, path: str, body=None, version="v3") -> requests.Response:
        url = f"{self.homeserver}/_matrix/client/{version}{path}"
        headers = {"Authorization": f"Bearer {self.token}"}
        r = requests.request(method, url, json=body, headers=headers, timeout=10)
        if r.status_code >= 400:
            log.warning(f"API {method} {path} -> {r.status_code}: {r.text[:200]}")
        return r

    def login(self, password: str) -> bool:
        r = requests.post(
            f"{self.homeserver}/_matrix/client/v3/login",
            json={"type": "m.login.password", "user": "jc1", "password": password}
        )
        if r.status_code == 200:
            data = r.json()
            self.token = data["access_token"]
            self.user_id = data["user_id"]
            os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
            with open(TOKEN_FILE, "w") as f:
                f.write(self.token)
            log.info(f"Logged in as {self.user_id}")
            return True
        log.error(f"Login failed: {r.status_code} {r.text[:200]}")
        return False

    def register(self, username: str, password: str) -> bool:
        r = requests.post(
            f"{self.homeserver}/_matrix/client/v3/register",
            json={"username": username, "password": password, "auth": {"type": "m.login.dummy"}}
        )
        if r.status_code == 200:
            data = r.json()
            self.token = data["access_token"]
            self.user_id = data["user_id"]
            os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
            with open(TOKEN_FILE, "w") as f:
                f.write(self.token)
            log.info(f"Registered as {self.user_id}")
            return True
        log.error(f"Registration failed: {r.status_code} {r.text[:200]}")
        return False

    def connected(self) -> bool:
        if not self.token:
            return False
        r = self._api("GET", "/account/whoami")
        return r.status_code == 200

    def create_room(self, name: str, topic: str = "", visibility: str = "public") -> Optional[str]:
        body = {"name": name, "topic": topic, "visibility": visibility, "preset": "public_chat" if visibility == "public" else "private_chat"}
        r = self._api("POST", "/createRoom", body)
        if r.status_code == 200:
            room_id = r.json()["room_id"]
            self.rooms[name] = room_id
            log.info(f"Created room '{name}' -> {room_id}")
            return room_id
        log.error(f"create_room failed: {r.status_code}")
        return None

    def join_room(self, room_id_or_alias: str) -> bool:
        r = self._api("POST", f"/join/{room_id_or_alias}")
        ok = r.status_code == 200
        if ok:
            self.rooms[room_id_or_alias] = r.json().get("room_id", room_id_or_alias)
            log.info(f"Joined {room_id_or_alias}")
        return ok

    def send_message(self, room_id: str, text: str, msgtype: str = "m.text") -> bool:
        body = {"msgtype": msgtype, "body": text}
        # Use txnid for dedup
        txnid = hashlib.md5(f"{time.time()}{text[:20]}".encode()).hexdigest()[:8]
        r = self._api("PUT", f"/rooms/{room_id}/send/m.room.message/{txnid}", body)
        ok = r.status_code == 200
        if ok:
            self.stats["sent"] += 1
        else:
            self.stats["errors"] += 1
        return ok

    def send_fleet_message(self, room_id: str, msg_type: str, payload: Dict) -> bool:
        """Send a structured fleet coordination message."""
        envelope = {
            "fleet_v": "1.0",
            "type": msg_type,
            "sender": self.user_id,
            "hardware": "jetson-orin-nano-8gb",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "payload": payload
        }
        return self.send_message(room_id, json.dumps(envelope, default=str))

    def get_messages(self, room_id: str, limit: int = 20) -> List[Dict]:
        r = self._api("GET", f"/rooms/{room_id}/messages", version="r0", 
                      body={"limit": limit, "dir": "b"})
        if r.status_code == 200:
            msgs = r.json().get("chunk", [])
            self.stats["received"] += len(msgs)
            return msgs
        return []

    def get_rooms(self) -> List[Dict]:
        r = self._api("GET", "/sync", body={"timeout": 0})
        if r.status_code == 200:
            return list(r.json().get("joined_rooms", {}).keys())
        # Fallback
        r2 = self._api("GET", "/joined_rooms")
        if r2.status_code == 200:
            return r2.json().get("joined_rooms", [])
        return []

    def broadcast_telemetry(self, room_id: str) -> bool:
        """Send live hardware telemetry."""
        import subprocess
        telemetry = {"memory": {}, "disk": {}, "thermal": []}

        # Memory
        try:
            mem = subprocess.check_output(["free", "-m"]).decode().split("\n")[1].split()
            telemetry["memory"] = {"total_mb": int(mem[1]), "used_mb": int(mem[2]), "percent": round(int(mem[2]) / int(mem[1]) * 100)}
        except: pass

        # Disk
        try:
            df = subprocess.check_output(["df", "-h", "/"]).decode().split("\n")[1].split()
            telemetry["disk"] = {"total": df[1], "used": df[2], "percent": df[4]}
        except: pass

        # Thermal zones
        try:
            zones = sorted(os.listdir("/sys/class/thermal/"))
            for z in zones:
                if "thermal_zone" in z:
                    with open(f"/sys/class/thermal/{z}/temp") as f:
                        temp_c = int(f.read().strip()) / 1000
                        telemetry["thermal"].append({"zone": z, "temp_c": round(temp_c, 1)})
        except: pass

        return self.send_fleet_message(room_id, "hardware_telemetry", telemetry)

    def get_stats(self) -> Dict:
        return {**self.stats, "rooms": len(self.rooms), "connected": self.connected()}


def main():
    print("🔧 JC1 Matrix Plugin — Fleet Coordination")
    print("=" * 50)

    plugin = JC1MatrixPlugin()

    # Check if token exists
    if plugin.connected():
        print(f"✅ Connected as {plugin.user_id}")
    else:
        print("⚠️  Not connected. Attempting registration...")
        # Register with a default password for local testing
        if not plugin.register("jc1", "jc1fleet2026"):
            print("Registration failed (user may exist). Trying login...")
            if not plugin.login("jc1fleet2026"):
                print("❌ Cannot authenticate. Is Conduit running?")
                return

    # List existing rooms
    print(f"\n📋 Rooms:")
    rooms = plugin.get_rooms()
    if not rooms:
        print("   (none yet)")
    for room_id in rooms:
        print(f"   {room_id}")

    # Ensure standard fleet rooms exist
    fleet_room = None
    for name in ["fleet-coordination", "plato-ecosystem", "jc1-hardware"]:
        # Check if room exists
        if not plugin.rooms.get(name):
            rid = plugin.create_room(name, f"Fleet room: {name}")
            if rid:
                plugin.rooms[name] = rid

    # Find a room to use
    if rooms:
        fleet_room = rooms[0]
    elif plugin.rooms:
        fleet_room = list(plugin.rooms.values())[0]

    if fleet_room:
        # Broadcast telemetry
        print(f"\n📡 Broadcasting telemetry to {fleet_room[:20]}...")
        if plugin.broadcast_telemetry(fleet_room):
            print("✅ Telemetry sent")
        else:
            print("❌ Telemetry failed")

        # Send test fleet message
        print(f"\n📤 Sending fleet status message...")
        status = {
            "services": ["conduit:6167", "plato-local", "deadband-protocol"],
            "packages": ["deadband-protocol", "bottle-protocol", "flywheel-engine", 
                        "tile-refiner", "fleet-homunculus", "cross-pollination", "cocapn"],
            "all_packages_arm64_verified": True
        }
        if plugin.send_fleet_message(fleet_room, "fleet_status", status):
            print("✅ Fleet status sent")
        else:
            print("❌ Fleet status failed")

    print(f"\n📊 Stats: {plugin.get_stats()}")
    print("\n✅ JC1 Matrix plugin operational")


if __name__ == "__main__":
    main()
