#!/usr/bin/env python3
"""
edge-monitor-web.py — Real-time monitoring dashboard for Jetson Orin Nano edge AI.

Web-based dashboard that shows:
  - CPU/GPU temperatures (from tegrastats or thermal zones)
  - RAM usage
  - GPU memory (CMA)
  - Gateway usage stats (proxied from edge-gateway)
  - Available models (proxied from edge-gateway)
  - Active conversations (proxied from edge-gateway)
  - Running edge services (process check)

Usage:
  python3 edge-monitor-web.py                # Start on port 8082
  python3 edge-monitor-web.py --port 9090    # Custom port

Dependencies: none (stdlib only)
"""

import json
import os
import re
import sys
import glob
import subprocess
import time
from http.server import HTTPServer, BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import urlopen, Request
from urllib.error import URLError
from datetime import datetime
from pathlib import Path

# Import shared monitoring
sys.path.insert(0, os.path.dirname(__file__))
from edge.monitoring import get_snapshot as get_edge_snapshot
from edge.config import OLLAMA_URL

# ── Config ──────────────────────────────────────────────────────────────────
DEFAULT_PORT = 8082
DEFAULT_HOST = "127.0.0.1"
GATEWAY_URL = "http://localhost:11435"
REFRESH_MS = 5000  # Dashboard auto-refresh interval

# Edge services to monitor
EDGE_SERVICES = {
    "edge-gateway": {"script": "edge-gateway.py", "port": 11435},
    "edge-chat": {"script": "edge-chat.py", "port": 8081},
    "edge-rag": {"script": "edge-rag.py", "port": 8081},
}

# ── System Stats ────────────────────────────────────────────────────────────


def read_tegrastats():
    """Run tegrastats once and parse the output line."""
    try:
        # Use 2s timeout for more reliable capture
        result = subprocess.run(
            ["timeout", "2", "tegrastats", "--interval", "100"],
            capture_output=True, text=True, timeout=4
        )
        if result.returncode == 0 and result.stdout.strip():
            lines = result.stdout.strip().split("\n")
            return _parse_tegrastats(lines[-1])
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        pass
    return {}


def _parse_tegrastats(line):
    """Parse a tegrastats line into structured data."""
    data = {}

    # RAM: "RAM 3800/7620MB (lfb 50x4MB)"
    m = re.search(r"RAM\s+(\d+)/(\d+)MB", line)
    if m:
        data["ram_used_mb"] = int(m.group(1))
        data["ram_total_mb"] = int(m.group(2))

    # SWAP: "SWAP 1418/28386MB"
    m = re.search(r"SWAP\s+(\d+)/(\d+)MB", line)
    if m:
        data["swap_used_mb"] = int(m.group(1))
        data["swap_total_mb"] = int(m.group(2))

    # CPU per-core: "CPU [10%@729,0%@729,...]"
    m = re.search(r"CPU\s+\[([^\]]+)\]", line)
    if m:
        cores_str = m.group(1)
        core_data = []
        for c in cores_str.split(","):
            parts = c.strip().split("@")
            if len(parts) == 2:
                util_pct = int(parts[0].replace("%", ""))
                freq_mhz = int(parts[1])
                core_data.append({"util_pct": util_pct, "freq_mhz": freq_mhz})
        data["cpu_cores"] = core_data
        if core_data:
            data["cpu_avg_pct"] = round(
                sum(c["util_pct"] for c in core_data) / len(core_data), 1
            )
            data["cpu_max_pct"] = max(c["util_pct"] for c in core_data)

    # GPU frequency: "GR3D_FREQ 0%"
    m = re.search(r"GR3D_FREQ\s+(\d+)%", line)
    if m:
        data["gpu_freq_pct"] = int(m.group(1))

    # Temperatures
    for sensor in ["cpu", "gpu", "soc0", "soc1", "soc2", "tj"]:
        m = re.search(rf"{sensor}@([\d.]+)C", line)
        if m:
            data[f"temp_{sensor}_c"] = round(float(m.group(1)), 1)

    # Power
    for rail in ["VDD_IN", "VDD_CPU_GPU_CV", "VDD_SOC"]:
        m = re.search(rf"{rail}\s+(\d+)mW", line)
        if m:
            data[f"power_{rail.lower()}_mw"] = int(m.group(1))

    return data


def read_thermal_zones():
    """Fallback thermal readings from sysfs."""
    temps = {}
    for tz_path in sorted(glob.glob("/sys/class/thermal/thermal_zone*")):
        try:
            with open(os.path.join(tz_path, "type"), "rb") as f:
                raw = f.read()
            if not raw:
                continue
            name = raw.decode().strip()
            with open(os.path.join(tz_path, "temp"), "rb") as f:
                raw = f.read()
            if not raw:
                continue
            val = raw.decode().strip()
            if val and val != "0":
                temps[name] = round(int(val) / 1000.0, 1)
        except (OSError, ValueError):
            pass
    return temps


def read_cma():
    """Read CMA (GPU memory) from /proc/meminfo."""
    result = {}
    try:
        with open("/proc/meminfo", "rb") as f:
            raw = f.read().decode()
        for line in raw.split("\n"):
            parts = line.split(":")
            if len(parts) != 2:
                continue
            key = parts[0].strip()
            val_kb = int(parts[1].strip().split()[0])
            if "CmaTotal" in key:
                result["cma_total_mb"] = val_kb // 1024
            elif "CmaFree" in key:
                result["cma_free_mb"] = val_kb // 1024
        if "cma_total_mb" in result and "cma_free_mb" in result:
            t = result["cma_total_mb"]
            f = result["cma_free_mb"]
            result["cma_used_mb"] = t - f
            result["cma_used_pct"] = round((1 - f / t) * 100, 1) if t > 0 else 0
    except Exception:
        pass
    return result


def get_meminfo():
    """Read RAM and swap from /proc/meminfo as fallback."""
    result = {}
    try:
        with open("/proc/meminfo", "rb") as f:
            raw = f.read().decode()
        for line in raw.split("\n"):
            parts = line.split(":")
            if len(parts) != 2:
                continue
            key = parts[0].strip()
            val_kb = int(parts[1].strip().split()[0])
            if key == "MemTotal":
                result["ram_total_mb"] = val_kb // 1024
            elif key == "MemAvailable":
                result["ram_available_mb"] = val_kb // 1024
            elif key == "SwapTotal":
                result["swap_total_mb"] = val_kb // 1024
            elif key == "SwapFree":
                result["swap_free_mb"] = val_kb // 1024
        if "ram_total_mb" in result and "ram_available_mb" in result:
            result["ram_used_mb"] = result["ram_total_mb"] - result["ram_available_mb"]
        if "swap_total_mb" in result and "swap_free_mb" in result:
            result["swap_used_mb"] = result["swap_total_mb"] - result["swap_free_mb"]
    except Exception:
        pass
    return result


def get_system_stats():
    """Get combined system stats from tegrastats + fallbacks."""
    data = read_tegrastats()
    data.update(read_cma())

    # Fallback RAM/Swap from /proc/meminfo if tegrastats didn't get them
    if not data.get("ram_total_mb"):
        data.update(get_meminfo())

    # Fallback temps if tegrastats didn't cover them
    if not data.get("temp_gpu_c") or not data.get("temp_cpu_c"):
        zones = read_thermal_zones()
        if "gpu-thermal" in zones and not data.get("temp_gpu_c"):
            data["temp_gpu_c"] = zones["gpu-thermal"]
        if "cpu-thermal" in zones and not data.get("temp_cpu_c"):
            data["temp_cpu_c"] = zones["cpu-thermal"]
        if "tj-thermal" in zones and not data.get("temp_tj_c"):
            data["temp_tj_c"] = zones["tj-thermal"]

    data["timestamp"] = datetime.now().isoformat()
    return data


# ── Gateway Proxy ───────────────────────────────────────────────────────────


def proxy_gateway(endpoint):
    """Fetch data from the edge-gateway API."""
    url = f"{GATEWAY_URL}{endpoint}"
    try:
        req = Request(url, method="GET")
        resp = urlopen(req, timeout=5)
        return json.loads(resp.read().decode())
    except (URLError, OSError, json.JSONDecodeError) as e:
        return {"error": str(e)}


# ── Process Check ───────────────────────────────────────────────────────────


def check_processes():
    """Check which edge services are running via PID."""
    results = []
    for name, info in EDGE_SERVICES.items():
        running = False
        pid = None
        try:
            # pgrep -f matches on command line
            proc = subprocess.run(
                ["pgrep", "-f", info["script"]],
                capture_output=True, text=True, timeout=3
            )
            if proc.returncode == 0 and proc.stdout.strip():
                pids = proc.stdout.strip().split("\n")
                running = True
                pid = int(pids[0])
        except Exception:
            pass

        results.append({
            "name": name,
            "script": info["script"],
            "port": info["port"],
            "running": running,
            "pid": pid,
        })
    return results


# ── HTTP Handler ────────────────────────────────────────────────────────────

DASHBOARD_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>JC1 Edge Monitor — Jetson Orin Nano</title>
<style>
  :root {
    --bg: #0d1117;
    --card: #161b22;
    --border: #30363d;
    --text: #c9d1d9;
    --text-dim: #8b949e;
    --green: #3fb950;
    --yellow: #d29922;
    --red: #f85149;
    --blue: #58a6ff;
    --orange: #d76f2c;
    --purple: #bc8cff;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    background: var(--bg);
    color: var(--text);
    padding: 20px;
    min-height: 100vh;
  }
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    padding-bottom: 16px;
    border-bottom: 1px solid var(--border);
  }
  .header h1 {
    font-size: 1.5rem;
    font-weight: 600;
  }
  .header .subtitle {
    color: var(--text-dim);
    font-size: 0.85rem;
    margin-top: 2px;
  }
  .status-dot {
    display: inline-block;
    width: 8px; height: 8px;
    border-radius: 50%;
    margin-right: 6px;
  }
  .status-dot.online { background: var(--green); box-shadow: 0 0 6px var(--green); }
  .status-dot.offline { background: var(--red); box-shadow: 0 0 6px var(--red); }
  .status-dot.warning { background: var(--yellow); box-shadow: 0 0 6px var(--yellow); }
  .last-updated {
    font-size: 0.8rem;
    color: var(--text-dim);
    text-align: right;
  }
  .last-updated .time { color: var(--blue); }

  /* Grid */
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 16px;
    margin-bottom: 16px;
  }
  .card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 16px;
  }
  .card h2 {
    font-size: 0.9rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-dim);
    margin-bottom: 12px;
  }
  .card h2 .icon { margin-right: 6px; }

  /* Gauges */
  .gauge-row {
    display: flex;
    gap: 16px;
    margin-bottom: 12px;
  }
  .gauge {
    flex: 1;
    text-align: center;
  }
  .gauge-label {
    font-size: 0.75rem;
    color: var(--text-dim);
    margin-bottom: 4px;
  }
  .gauge-value {
    font-size: 1.6rem;
    font-weight: 700;
    font-variant-numeric: tabular-nums;
  }
  .gauge-value .unit {
    font-size: 0.8rem;
    font-weight: 400;
    color: var(--text-dim);
  }

  /* Progress bars */
  .bar-section { margin-bottom: 12px; }
  .bar-section:last-child { margin-bottom: 0; }
  .bar-header {
    display: flex;
    justify-content: space-between;
    font-size: 0.8rem;
    margin-bottom: 4px;
  }
  .bar-header .label { color: var(--text-dim); }
  .bar-track {
    height: 12px;
    background: #21262d;
    border-radius: 6px;
    overflow: hidden;
    position: relative;
  }
  .bar-fill {
    height: 100%;
    border-radius: 6px;
    transition: width 0.5s ease;
    position: relative;
  }
  .bar-fill.green { background: var(--green); }
  .bar-fill.yellow { background: var(--yellow); }
  .bar-fill.orange { background: var(--orange); }
  .bar-fill.red { background: var(--red); }
  .bar-fill.blue { background: var(--blue); }
  .bar-fill.purple { background: var(--purple); }

  /* Model list */
  .model-list {
    list-style: none;
  }
  .model-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 6px 0;
    border-bottom: 1px solid var(--border);
    font-size: 0.85rem;
  }
  .model-item:last-child { border-bottom: none; }
  .model-name {
    font-family: 'SF Mono', 'Fira Code', 'Fira Mono', Menlo, Consolas, monospace;
    font-size: 0.8rem;
  }
  .model-size {
    color: var(--text-dim);
    font-size: 0.75rem;
  }

  /* Stats row */
  .stat-row {
    display: flex;
    justify-content: space-between;
    padding: 6px 0;
    border-bottom: 1px solid var(--border);
    font-size: 0.85rem;
  }
  .stat-row:last-child { border-bottom: none; }
  .stat-label { color: var(--text-dim); }
  .stat-value {
    font-weight: 600;
    font-variant-numeric: tabular-nums;
  }

  /* Services */
  .service-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid var(--border);
  }
  .service-row:last-child { border-bottom: none; }
  .service-name { font-size: 0.85rem; }
  .service-port {
    color: var(--text-dim);
    font-size: 0.75rem;
    font-family: monospace;
  }
  .service-status {
    display: flex;
    align-items: center;
    font-size: 0.8rem;
  }

  /* Conversation list */
  .conv-list {
    max-height: 240px;
    overflow-y: auto;
  }
  .conv-item {
    padding: 6px 0;
    border-bottom: 1px solid var(--border);
    font-size: 0.8rem;
  }
  .conv-item:last-child { border-bottom: none; }
  .conv-title {
    font-weight: 500;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .conv-meta {
    color: var(--text-dim);
    font-size: 0.7rem;
    margin-top: 2px;
  }

  /* Loading / Error */
  .loading {
    color: var(--text-dim);
    font-size: 0.85rem;
    text-align: center;
    padding: 20px;
  }
  .error {
    color: var(--red);
    font-size: 0.8rem;
  }

  @media (max-width: 700px) {
    .grid { grid-template-columns: 1fr; }
    .gauge-row { flex-wrap: wrap; }
  }
</style>
</head>
<body>
  <div class="header">
    <div>
      <h1>🖥️ JC1 Edge Monitor</h1>
      <div class="subtitle">Jetson Orin Nano 8GB — Edge AI Toolkit</div>
    </div>
    <div class="last-updated">
      <div>Last updated</div>
      <div class="time" id="lastUpdate">—</div>
    </div>
  </div>

  <div class="grid">
    <!-- Temperatures -->
    <div class="card">
      <h2><span class="icon">🌡️</span>Temperatures</h2>
      <div class="gauge-row">
        <div class="gauge">
          <div class="gauge-label">GPU</div>
          <div class="gauge-value" id="tempGpu">--<span class="unit">°C</span></div>
        </div>
        <div class="gauge">
          <div class="gauge-label">CPU</div>
          <div class="gauge-value" id="tempCpu">--<span class="unit">°C</span></div>
        </div>
        <div class="gauge">
          <div class="gauge-label">SoC</div>
          <div class="gauge-value" id="tempSoc">--<span class="unit">°C</span></div>
        </div>
      </div>
      <div class="bar-section">
        <div class="bar-header">
          <span class="label">GPU Frequency</span>
          <span id="gpuFreq">--</span>
        </div>
        <div class="bar-track">
          <div class="bar-fill blue" id="gpuFreqBar" style="width:0%"></div>
        </div>
      </div>
      <div class="bar-section">
        <div class="bar-header">
          <span class="label">CPU Load (avg)</span>
          <span id="cpuLoad">--</span>
        </div>
        <div class="bar-track">
          <div class="bar-fill purple" id="cpuLoadBar" style="width:0%"></div>
        </div>
      </div>
    </div>

    <!-- Memory -->
    <div class="card">
      <h2><span class="icon">💾</span>Memory</h2>
      <div class="bar-section">
        <div class="bar-header">
          <span class="label">RAM</span>
          <span id="ramLabel">-- / -- MB</span>
        </div>
        <div class="bar-track">
          <div class="bar-fill" id="ramBar" style="width:0%"></div>
        </div>
      </div>
      <div class="bar-section">
        <div class="bar-header">
          <span class="label">GPU CMA</span>
          <span id="cmaLabel">-- / -- MB</span>
        </div>
        <div class="bar-track">
          <div class="bar-fill green" id="cmaBar" style="width:0%"></div>
        </div>
      </div>
      <div class="bar-section">
        <div class="bar-header">
          <span class="label">Swap</span>
          <span id="swapLabel">-- / -- MB</span>
        </div>
        <div class="bar-track">
          <div class="bar-fill yellow" id="swapBar" style="width:0%"></div>
        </div>
      </div>
    </div>

    <!-- Gateway Usage -->
    <div class="card">
      <h2><span class="icon">📊</span>Gateway Usage</h2>
      <div class="stat-row">
        <span class="stat-label">Total Requests</span>
        <span class="stat-value" id="totalReqs">--</span>
      </div>
      <div class="stat-row">
        <span class="stat-label">Chat Requests</span>
        <span class="stat-value" id="chatReqs">--</span>
      </div>
      <div class="stat-row">
        <span class="stat-label">Prompt Tokens</span>
        <span class="stat-value" id="promptTokens">--</span>
      </div>
      <div class="stat-row">
        <span class="stat-label">Completion Tokens</span>
        <span class="stat-value" id="completionTokens">--</span>
      </div>
      <div class="stat-row">
        <span class="stat-label">Errors</span>
        <span class="stat-value" id="errors">--</span>
      </div>
      <div class="stat-row">
        <span class="stat-label">Power</span>
        <span class="stat-value" id="powerLabel">-- mW</span>
      </div>
    </div>

    <!-- Models -->
    <div class="card">
      <h2><span class="icon">🤖</span>Models (<span id="modelCount">0</span>)</h2>
      <ul class="model-list" id="modelList">
        <li class="loading">Loading...</li>
      </ul>
    </div>

    <!-- Services -->
    <div class="card">
      <h2><span class="icon">⚙️</span>Services</h2>
      <div id="serviceList">
        <div class="loading">Loading...</div>
      </div>
    </div>

    <!-- Conversations -->
    <div class="card">
      <h2><span class="icon">💬</span>Active Conversations</h2>
      <div class="conv-list" id="convList">
        <div class="loading">Loading...</div>
      </div>
    </div>
  </div>

<script>
"use strict";
function fmtBytes(bytes) {
  if (bytes >= 1e9) return (bytes / 1e9).toFixed(1) + ' GB';
  if (bytes >= 1e6) return (bytes / 1e6).toFixed(1) + ' MB';
  if (bytes >= 1e3) return (bytes / 1e3).toFixed(1) + ' KB';
  return bytes + ' B';
}

function tempColor(c) {
  if (c === null || c === undefined) return '';
  if (c >= 75) return 'var(--red)';
  if (c >= 60) return 'var(--orange)';
  if (c >= 50) return 'var(--yellow)';
  return 'var(--green)';
}

function barColorClass(pct) {
  if (pct >= 90) return 'red';
  if (pct >= 75) return 'orange';
  if (pct >= 50) return 'yellow';
  return 'green';
}

async function fetchJSON(url) {
  const resp = await fetch(url);
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
  return resp.json();
}

async function refresh() {
  const now = new Date();
  document.getElementById('lastUpdate').textContent = now.toLocaleTimeString();

  try {
    // System stats
    const sys = await fetchJSON('/api/system');
    const tempGpu = sys.temp_gpu_c;
    const tempCpu = sys.temp_cpu_c;
    const tempSoc = sys.temp_tj_c || sys.temp_soc0_c;

    document.getElementById('tempGpu').innerHTML = (tempGpu ?? '--') + '<span class="unit">°C</span>';
    document.getElementById('tempGpu').style.color = tempColor(tempGpu);

    document.getElementById('tempCpu').innerHTML = (tempCpu ?? '--') + '<span class="unit">°C</span>';
    document.getElementById('tempCpu').style.color = tempColor(tempCpu);

    document.getElementById('tempSoc').innerHTML = (tempSoc ?? '--') + '<span class="unit">°C</span>';
    document.getElementById('tempSoc').style.color = tempColor(tempSoc);

    // GPU freq
    const gpuFreq = sys.gpu_freq_pct ?? 0;
    document.getElementById('gpuFreq').textContent = gpuFreq + '%';
    document.getElementById('gpuFreqBar').style.width = gpuFreq + '%';

    // CPU load
    const cpuAvg = sys.cpu_avg_pct ?? 0;
    document.getElementById('cpuLoad').textContent = cpuAvg + '%';
    document.getElementById('cpuLoadBar').style.width = cpuAvg + '%';

    // RAM
    const ramUsed = sys.ram_used_mb ?? 0;
    const ramTotal = sys.ram_total_mb ?? 1;
    const ramPct = Math.round((ramUsed / ramTotal) * 100);
    document.getElementById('ramLabel').textContent = ramUsed + ' / ' + ramTotal + ' MB';
    const ramBar = document.getElementById('ramBar');
    ramBar.style.width = ramPct + '%';
    ramBar.className = 'bar-fill ' + barColorClass(ramPct);

    // CMA (GPU memory)
    const cmaUsed = sys.cma_used_mb ?? 0;
    const cmaTotal = sys.cma_total_mb ?? 1;
    const cmaPct = sys.cma_used_pct ?? Math.round((cmaUsed / cmaTotal) * 100);
    document.getElementById('cmaLabel').textContent = cmaUsed + ' / ' + cmaTotal + ' MB';
    const cmaBar = document.getElementById('cmaBar');
    cmaBar.style.width = (cmaTotal > 0 ? cmaPct : 0) + '%';
    cmaBar.className = 'bar-fill ' + barColorClass(cmaPct);

    // Swap
    const swapUsed = sys.swap_used_mb ?? 0;
    const swapTotal = sys.swap_total_mb ?? 1;
    const swapPct = swapTotal > 0 ? Math.round((swapUsed / swapTotal) * 100) : 0;
    document.getElementById('swapLabel').textContent = swapUsed + ' / ' + swapTotal + ' MB';
    const swapBar = document.getElementById('swapBar');
    swapBar.style.width = swapPct + '%';
    swapBar.className = 'bar-fill ' + barColorClass(swapPct);

    // Power
    const powerMw = sys.power_vdd_in_mw ?? sys.power_vdd_in_mw1 ?? 0;
    document.getElementById('powerLabel').textContent = powerMw ? powerMw + ' mW' : '--';

  } catch (e) {
    console.warn('System API:', e);
  }

  try {
    // Gateway usage
    const usage = await fetchJSON('/api/gateway');
    if (usage && usage.data && usage.data.length > 0) {
      const stats = usage.data[0];
      document.getElementById('totalReqs').textContent = stats.requests ?? '--';
      document.getElementById('chatReqs').textContent = stats.endpoint ?? '--';
      document.getElementById('promptTokens').textContent = stats.total_prompt_tokens ?? '--';
      document.getElementById('completionTokens').textContent = stats.total_completion_tokens ?? '--';
      document.getElementById('errors').textContent = stats.errors ?? '--';
    }
  } catch (e) {
    console.warn('Gateway API:', e);
  }

  try {
    // Models
    const models = await fetchJSON('/api/models');
    const list = document.getElementById('modelList');
    if (models && models.data) {
      document.getElementById('modelCount').textContent = models.data.length;
      if (models.data.length === 0) {
        list.innerHTML = '<li class="loading">No models loaded</li>';
      } else {
        list.innerHTML = models.data.map(m =>
          `<li class="model-item">
            <span class="model-name">${escHtml(m.id)}</span>
            <span class="model-size">${fmtBytes(m.size || 0)}</span>
          </li>`
        ).join('');
      }
    }
  } catch (e) {
    console.warn('Models API:', e);
  }

  try {
    // Processes
    const procs = await fetchJSON('/api/processes');
    const container = document.getElementById('serviceList');
    if (Array.isArray(procs)) {
      container.innerHTML = procs.map(s =>
        `<div class="service-row">
          <div>
            <div class="service-name">${escHtml(s.name)}</div>
            <div class="service-port">port ${s.port}</div>
          </div>
          <div class="service-status">
            <span class="status-dot ${s.running ? 'online' : 'offline'}"></span>
            ${s.running ? 'Online' : 'Offline'}
          </div>
        </div>`
      ).join('');
    }
  } catch (e) {
    console.warn('Processes API:', e);
  }

  try {
    // Conversations
    const convs = await fetchJSON('/api/conversations');
    const convContainer = document.getElementById('convList');
    if (convs && convs.data) {
      if (convs.data.length === 0) {
        convContainer.innerHTML = '<div class="conv-item" style="color:var(--text-dim)">No conversations</div>';
      } else {
        convContainer.innerHTML = convs.data.slice(0, 10).map(c =>
          `<div class="conv-item">
            <div class="conv-title">${escHtml(c.title || c.id || 'Untitled')}</div>
            <div class="conv-meta">${escHtml(c.model || '')}${c.updated ? ' · ' + new Date(c.updated).toLocaleString() : ''}</div>
          </div>`
        ).join('');
      }
    }
  } catch (e) {
    console.warn('Conversations API:', e);
  }
}

function escHtml(s) {
  if (!s) return '';
  const d = document.createElement('div');
  d.textContent = s;
  return d.innerHTML;
}

// Initial load
refresh();

// Auto-refresh every 5 seconds
setInterval(refresh, 5000);
</script>
</body>
</html>
"""


class MonitorHandler(BaseHTTPRequestHandler):
    """HTTP handler for the monitoring dashboard."""

    def _json_response(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(body)

    def _html_response(self, html, status=200):
        body = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache, max-age=0")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        try:
            if self.path == "/" or self.path == "/index.html":
                self._html_response(DASHBOARD_HTML)

            elif self.path == "/api/system":
                data = get_system_stats()
                self._json_response(data)

            elif self.path == "/api/gateway":
                data = proxy_gateway("/v1/usage")
                self._json_response(data)

            elif self.path == "/api/models":
                data = proxy_gateway("/v1/models")
                self._json_response(data)

            elif self.path == "/api/conversations":
                data = proxy_gateway("/v1/conversations")
                self._json_response(data)

            elif self.path == "/api/processes":
                data = check_processes()
                self._json_response(data)

            else:
                self._json_response({"error": "Not found"}, 404)
        except Exception as e:
            self._json_response({"error": str(e)}, 500)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, fmt, *args):
        """Quiet logging — only log requests to stderr in a compact format."""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0]} {args[1]} {args[2]}")


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
        else:
            i += 1

    print(f"🖥️  Edge Monitor Dashboard")
    print(f"   Listening on http://{host}:{port}")
    print(f"   API endpoints:")
    print(f"     GET /              — Dashboard UI")
    print(f"     GET /api/system    — System stats (tegrastats + CMA)")
    print(f"     GET /api/gateway   — Gateway usage (proxy)")
    print(f"     GET /api/models    — Available models (proxy)")
    print(f"     GET /api/conversations — Conversations (proxy)")
    print(f"     GET /api/processes — Running edge services")

    server = ThreadingHTTPServer((host, port), MonitorHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Stopping edge monitor dashboard")
        server.shutdown()


if __name__ == "__main__":
    main()
