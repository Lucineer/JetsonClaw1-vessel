#!/usr/bin/env python3
"""
fleet-badge.py — Fleet health badge / iframe server.

Serves a small auto-refresh HTML badge showing:
  - Fleet health (connected nodes)
  - JC1 edge services status (gateway, chat, monitor)
  - Oracle1 reachability
  - Last fleet synthesis timestamp
  - CMA, RAM, uptime

Port 8083. Designed to be embedded in dashboards or served standalone.
Zero external dependencies — runs on ARM64 (Jetson) with stdlib only.

Usage:
  python3 fleet-badge.py                    # Port 8083, localhost
  python3 fleet-badge.py --port 9090        # Custom port
  python3 fleet-badge.py --host 0.0.0.0     # All interfaces
  python3 fleet-badge.py --refresh 10       # Auto-refresh every 10 seconds
"""

import json
import os
import sys
import time
import re
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread, Lock
from datetime import datetime
from urllib.request import urlopen, Request
from urllib.error import URLError

# ── Configuration ──────────────────────────────────────────────

DEFAULT_PORT = 8083
DEFAULT_HOST = "127.0.0.1"
DEFAULT_REFRESH = 5  # seconds

# Fleet endpoints (adjustable via env)
ORACLE1_URL = os.environ.get("ORACLE1_URL", "http://147.224.38.131:8848")
EDGE_GATEWAY_URL = os.environ.get("EDGE_GATEWAY_URL", "http://127.0.0.1:11435")
EDGE_CHAT_URL = os.environ.get("EDGE_CHAT_URL", "http://127.0.0.1:8081")
EDGE_DASH_URL = os.environ.get("EDGE_DASH_URL", "http://127.0.0.1:8082")

VERSION = "1.0.0"

# Cache for service checks
_cache = {
    "timestamp": 0,
    "data": {},
    "lock": Lock(),
}
CACHE_TTL = 10  # seconds


# ── Helpers ────────────────────────────────────────────────────

def _run(cmd, timeout=5):
    """Run shell command with timeout, return (stdout, ok)."""
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True,
                          text=True, timeout=timeout)
        return r.stdout.strip(), r.returncode == 0
    except Exception:
        return "", False


def _fetch(url, timeout=5):
    """HTTP GET with timeout, return (body, ok)."""
    try:
        r = urlopen(Request(url), timeout=timeout)
        return r.read().decode(), True
    except Exception:
        return "", False


def _fetch_json(url, timeout=5):
    """HTTP GET, parse JSON."""
    body, ok = _fetch(url, timeout)
    if ok and body:
        try:
            return json.loads(body), True
        except json.JSONDecodeError:
            pass
    return {}, False


def _bytes_to_human(b):
    """Human-readable bytes."""
    if not b:
        return "?"
    for unit in ("B", "KB", "MB", "GB"):
        if b < 1024:
            return f"{b:.1f}{unit}"
        b /= 1024
    return f"{b:.1f}TB"


# ── Fleet Check ────────────────────────────────────────────────

def check_jc1_services():
    """Check edge services on JC1."""
    results = {}

    # Edge gateway
    data, ok = _fetch_json(f"{EDGE_GATEWAY_URL}/v1/health", timeout=3)
    if ok and data.get("status") == "ok":
        results["edge_gateway"] = {
            "status": "ok",
            "version": data.get("version", "?"),
            "ollama": data.get("ollama", "?"),
        }
    else:
        results["edge_gateway"] = {"status": "down"}

    # Chat UI
    body, ok = _fetch(f"{EDGE_CHAT_URL}/", timeout=3)
    results["edge_chat"] = {
        "status": "ok" if (ok and body and "html" in body.lower()[:200]) else "down",
    }

    # Dashboard
    body, ok = _fetch(f"{EDGE_DASH_URL}/", timeout=3)
    results["edge_dashboard"] = {
        "status": "ok" if (ok and body and ("html" in body.lower()[:200] or "dashboard" in body.lower()[:200])) else "down",
    }

    # Ollama
    data, ok = _fetch_json("http://127.0.0.1:11434/api/tags", timeout=3)
    results["ollama"] = {
        "status": "ok" if (ok and "models" in data) else "down",
        "models": len(data.get("models", [])) if ok else 0,
    }

    return results


def check_oracle1():
    """Check Oracle1 cloud reachability."""
    body, ok = _fetch(f"{ORACLE1_URL}/connect?agent=jc1-check", timeout=5)
    if ok and body:
        try:
            data = json.loads(body)
            return {
                "status": "ok",
                "room": data.get("room", "?"),
            }
        except json.JSONDecodeError:
            pass
    return {"status": "down"}


def check_system():
    """Local system metrics."""
    result = {}

    # RAM
    try:
        with open("/proc/meminfo") as f:
            raw = f.read()
        for line in raw.split("\n"):
            parts = line.split(":")
            if len(parts) == 2:
                k = parts[0].strip()
                v_kb = int(parts[1].strip().split()[0])
                if k == "MemTotal":
                    result["ram_total_mb"] = v_kb // 1024
                elif k == "MemAvailable":
                    result["ram_available_mb"] = v_kb // 1024
                elif k == "CmaTotal":
                    result["cma_total_mb"] = v_kb // 1024
                elif k == "CmaFree":
                    result["cma_free_mb"] = v_kb // 1024
        if "ram_total_mb" in result and "ram_available_mb" in result:
            result["ram_used_mb"] = result["ram_total_mb"] - result["ram_available_mb"]
            result["ram_pct"] = round(result["ram_used_mb"] / result["ram_total_mb"] * 100, 1)
        if "cma_total_mb" in result and "cma_free_mb" in result:
            result["cma_used_pct"] = round(
                (1 - result["cma_free_mb"] / result["cma_total_mb"]) * 100, 1
            ) if result["cma_total_mb"] > 0 else 0
    except Exception:
        pass

    # Temperatures
    try:
        for tz_name in ("gpu-thermal", "cpu-thermal", "tj-thermal"):
            tz_dir = f"/sys/class/thermal/{tz_name}"
            if os.path.exists(tz_dir):
                label = f"{tz_name.split('-')[0]}_temp_c"
                with open(f"{tz_dir}/temp") as f:
                    result[label] = round(int(f.read().strip()) / 1000, 1)
    except Exception:
        pass

    # Also try indexed thermal zones
    try:
        import glob
        for tz_path in sorted(glob.glob("/sys/class/thermal/thermal_zone*")):
            try:
                with open(f"{tz_path}/type") as f:
                    name = f.read().strip()
                with open(f"{tz_path}/temp") as f:
                    raw = f.read().strip()
                if raw and raw != "0":
                    val = round(int(raw) / 1000, 1)
                    label = f"{name.split('-')[0]}_temp_c"
                    if label not in result:
                        result[label] = val
            except Exception:
                pass
    except Exception:
        pass

    # Uptime
    uptime_str, ok = _run("uptime -p")
    result["uptime"] = uptime_str if ok else "?"
    uptime_s, ok = _run("cat /proc/uptime | cut -d' ' -f1")
    result["uptime_s"] = round(float(uptime_s)) if ok else 0

    return result


def check_last_synthesis():
    """Check when the last fleet synthesis happened."""
    heartbeat_path = os.path.expanduser("~/.openclaw/workspace/HEARTBEAT.md")
    if os.path.exists(heartbeat_path):
        mtime = os.path.getmtime(heartbeat_path)
        age = time.time() - mtime
        return {
            "exists": True,
            "mtime": datetime.fromtimestamp(mtime).isoformat(),
            "age_hours": round(age / 3600, 1),
        }
    return {"exists": False}


# ── Background Cache ──────────────────────────────────────────

def _refresh_cache():
    """Run all checks and update cache."""
    data = {}
    data["jc1_services"] = check_jc1_services()
    data["oracle1"] = check_oracle1()
    data["system"] = check_system()
    data["synthesis"] = check_last_synthesis()
    data["timestamp"] = datetime.now().isoformat()
    data["hostname"] = os.uname().nodename

    # Count connected nodes
    nodes = 1  # JC1 itself
    if data.get("oracle1", {}).get("status") == "ok":
        nodes += 1  # Oracle1
    data["connected_nodes"] = nodes

    # Fleet health
    ok_count = sum(
        1 for s in data.get("jc1_services", {}).values()
        if isinstance(s, dict) and s.get("status") == "ok"
    )
    total = len(data.get("jc1_services", {}))
    data["fleet_health"] = "ok" if ok_count >= total - 1 else "degraded" if ok_count >= total // 2 else "critical"

    with _cache["lock"]:
        _cache["data"] = data
        _cache["timestamp"] = time.time()


def _get_cached():
    """Get cached fleet data, refreshing if stale."""
    with _cache["lock"]:
        stale = time.time() - _cache["timestamp"] > CACHE_TTL
        data = _cache["data"]

    if stale:
        _refresh_cache()
        with _cache["lock"]:
            data = _cache["data"]

    return data


# ── Badge HTML ─────────────────────────────────────────────────

BADGE_HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Fleet Badge</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
         background: transparent; color: #c9d1d9; font-size: 12px; line-height: 1.4; }
  .badge { background: #0d1117; border: 1px solid #30363d; border-radius: 6px;
           padding: 8px 10px; width: 320px; }
  .badge-header { font-size: 11px; font-weight: 600; color: #58a6ff;
                  text-transform: uppercase; letter-spacing: 0.8px;
                  margin-bottom: 6px; border-bottom: 1px solid #21262d; padding-bottom: 4px; }
  .row { display: flex; justify-content: space-between; align-items: center;
         padding: 2px 0; font-size: 11px; }
  .row .label { color: #8b949e; }
  .row .value { font-family: 'SF Mono', 'Fira Code', monospace; font-size: 11px; }
  .ok { color: #3fb950; }
  .degraded { color: #d29922; }
  .down { color: #f85149; }
  .info { color: #58a6ff; }
  .timestamp { text-align: center; font-size: 9px; color: #484f58;
               margin-top: 4px; padding-top: 4px; border-top: 1px solid #21262d; }
  .service-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 2px; }
  .version { font-size: 9px; color: #484f58; }
</style>
</head>
<body>
"""


def _build_badge_html(data):
    """Build the badge HTML from fleet data."""
    system = data.get("system", {})
    jc1 = data.get("jc1_services", {})
    oracle1 = data.get("oracle1", {})
    synthesis = data.get("synthesis", {})

    # Colors
    hlth = data.get("fleet_health", "unknown")
    hlth_cls = {"ok": "ok", "degraded": "degraded", "critical": "down"}.get(hlth, "degraded")
    hlth_label = hlth.upper()

    nodes = data.get("connected_nodes", 1)
    ram_pct = system.get("ram_pct", 0)
    ram_cls = "ok" if ram_pct < 70 else ("degraded" if ram_pct < 90 else "down")
    cma_pct = system.get("cma_used_pct", 0)
    cma_cls = "ok" if cma_pct < 50 else ("degraded" if cma_pct < 80 else "down")

    gpu_temp = system.get("gpu_temp_c") or system.get("thermal_zone1_temp_c", "?")
    gpu_str = f"{gpu_temp}°C" if isinstance(gpu_temp, float) else str(gpu_temp)
    gpu_cls = "ok" if isinstance(gpu_temp, float) and gpu_temp < 60 else "down"

    oracle_ok = oracle1.get("status") == "ok"
    gateway_ok = jc1.get("edge_gateway", {}).get("status") == "ok"
    chat_ok = jc1.get("edge_chat", {}).get("status") == "ok"
    dash_ok = jc1.get("edge_dashboard", {}).get("status") == "ok"

    syntxt = synthesis.get("mtime", "never")[:19] if synthesis.get("exists") else "never"
    hostname = data.get("hostname", "jc1")
    ts = data.get("timestamp", "")[:19]

    html = BADGE_HEAD
    html += f'<div class="badge">'
    html += f'<div class="badge-header">⚡ Fleet Badge — {hostname}</div>'

    # Fleet health row
    html += f'<div class="row"><span class="label">Fleet Health</span><span class="value {hlth_cls}">{hlth_label}</span></div>'
    html += f'<div class="row"><span class="label">Connected Nodes</span><span class="value info">{nodes}</span></div>'

    # Divider
    html += f'<div style="border-top:1px solid #21262d;margin:4px 0;"></div>'

    # JC1 services
    html += f'<div style="font-size:10px;color:#8b949e;margin-bottom:2px;">JC1 Edge Services</div>'
    html += f'<div class="service-grid">'
    html += f'<div><span class="label">Gateway</span> <span class="value {"ok" if gateway_ok else "down"}">{"●" if gateway_ok else "○"} {jc1.get("edge_gateway",{}).get("version","?")}</span></div>'
    html += f'<div><span class="label">Chat</span> <span class="value {"ok" if chat_ok else "down"}">{"●" if chat_ok else "○"}</span></div>'
    html += f'<div><span class="label">Dashboard</span> <span class="value {"ok" if dash_ok else "down"}">{"●" if dash_ok else "○"}</span></div>'
    html += f'<div><span class="label">Ollama</span> <span class="value {"ok" if jc1.get("ollama",{}).get("status")=="ok" else "down"}">{"●" if jc1.get("ollama",{}).get("status")=="ok" else "○"} {jc1.get("ollama",{}).get("models",0)}</span></div>'
    html += f'</div>'

    # Divider
    html += f'<div style="border-top:1px solid #21262d;margin:4px 0;"></div>'

    # Cloud
    html += f'<div style="font-size:10px;color:#8b949e;margin-bottom:2px;">Cloud</div>'
    html += f'<div class="row"><span class="label">Oracle1</span><span class="value {"ok" if oracle_ok else "down"}">{"●" if oracle_ok else "○"} {oracle1.get("room","?") if oracle_ok else "unreachable"}</span></div>'

    # Divider
    html += f'<div style="border-top:1px solid #21262d;margin:4px 0;"></div>'

    # System
    html += f'<div style="font-size:10px;color:#8b949e;margin-bottom:2px;">System</div>'
    html += f'<div class="row"><span class="label">RAM</span><span class="value {ram_cls}">{system.get("ram_used_mb","?")}/{system.get("ram_total_mb","?")} MB ({ram_pct}%)</span></div>'
    html += f'<div class="row"><span class="label">CMA</span><span class="value {cma_cls}">{cma_pct}%</span></div>'
    html += f'<div class="row"><span class="label">GPU</span><span class="value {gpu_cls}">{gpu_str}</span></div>'
    html += f'<div class="row"><span class="label">Uptime</span><span class="value info">{system.get("uptime","?")}</span></div>'

    # Divider
    html += f'<div style="border-top:1px solid #21262d;margin:4px 0;"></div>'

    # Synthesis / timestamp
    html += f'<div class="row"><span class="label">Last Synthesis</span><span class="value info">{syntxt}</span></div>'
    html += f'<div class="timestamp">v{VERSION} · {ts}</div>'
    html += f'</div>'
    html += "</body></html>"
    return html


# ── JSON Badge (for embedding in other systems) ────────────────

def _build_badge_json(data):
    """Build structured JSON fleet status."""
    return {
        "version": VERSION,
        "hostname": data.get("hostname", "jc1"),
        "timestamp": data.get("timestamp", ""),
        "fleet": {
            "health": data.get("fleet_health", "unknown"),
            "connected_nodes": data.get("connected_nodes", 0),
        },
        "services": data.get("jc1_services", {}),
        "cloud": {
            "oracle1": data.get("oracle1", {}),
        },
        "system": data.get("system", {}),
        "synthesis": data.get("synthesis", {}),
    }


# ── HTTP Handler ───────────────────────────────────────────────

class BadgeHandler(BaseHTTPRequestHandler):

    def _send(self, body, content_type, status=200):
        encoded = body.encode()
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", f"max-age={CACHE_TTL}, public")
        self.end_headers()
        self.wfile.write(encoded)

    def _json(self, data, status=200):
        body = json.dumps(data)
        self._send(body, "application/json", status)

    def do_GET(self):
        data = _get_cached()

        if self.path == "/" or self.path == "":
            # HTML badge
            refresh = int(os.environ.get("FLEET_BADGE_REFRESH", DEFAULT_REFRESH))
            html = _build_badge_html(data).replace(
                "</head>",
                f'<meta http-equiv="refresh" content="{refresh}">\n</head>',
            )
            self._send(html, "text/html; charset=utf-8")

        elif self.path == "/json" or self.path == "/api" or self.path == "/v1/status":
            # JSON API
            self._json(_build_badge_json(data))

        elif self.path == "/embed":
            # Minimal iframe-safe version (no external page context needed)
            refresh = int(os.environ.get("FLEET_BADGE_REFRESH", DEFAULT_REFRESH))
            html = _build_badge_html(data).replace(
                "</head>",
                f'<meta http-equiv="refresh" content="{refresh}">\n</head>',
            )
            self._send(html, "text/html; charset=utf-8")

        elif self.path == "/health":
            self._json({
                "status": "ok",
                "version": VERSION,
                "upstreams": {
                    "ollama": _cache["data"].get("jc1_services", {}).get("ollama", {}).get("status", "unknown"),
                    "gateway": _cache["data"].get("jc1_services", {}).get("edge_gateway", {}).get("status", "unknown"),
                    "oracle1": _cache["data"].get("oracle1", {}).get("status", "unknown"),
                },
            })

        else:
            self._json({"error": "Not found"}, 404)

    def log_message(self, fmt, *args):
        pass  # Quiet

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()


def main():
    port = DEFAULT_PORT
    host = DEFAULT_HOST

    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--port" and i + 1 < len(sys.argv):
            port = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == "--host" and i + 1 < len(sys.argv):
            host = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--refresh" and i + 1 < len(sys.argv):
            os.environ["FLEET_BADGE_REFRESH"] = sys.argv[i + 1]
            i += 2
        else:
            i += 1

    # Seed the cache
    print(f"🏥 Fleet Badge v{VERSION} — seeding cache...")
    _refresh_cache()
    data = _get_cached()
    hlth = data.get("fleet_health", "?")
    nodes = data.get("connected_nodes", 0)
    print(f"   Health: {hlth}  Nodes: {nodes}")

    # Start background cache refresh
    def _auto_refresh():
        while True:
            time.sleep(CACHE_TTL)
            _refresh_cache()

    refresher = Thread(target=_auto_refresh, daemon=True)
    refresher.start()

    print(f"   Listening on http://{host}:{port}")
    print(f"   Refresh: every {CACHE_TTL}s")
    print(f"   Endpoints:")
    print(f"     GET  /            — HTML badge (embed-ready)")
    print(f"     GET  /json        — JSON fleet status")
    print(f"     GET  /embed       — iframe-friendly badge")
    print(f"     GET  /health      — Health check")

    server = ThreadingHTTPServer((host, port), BadgeHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Stopping fleet badge")
        server.shutdown()


if __name__ == "__main__":
    main()
