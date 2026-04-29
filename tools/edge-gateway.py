#!/usr/bin/env python3
"""
edge-gateway.py — Unified edge AI gateway for Jetson Orin Nano.

OpenAI-compatible proxy for Ollama with smart model routing,
streaming support, RAG, conversations, and system monitoring.

Single server that exposes:
  GET  /                        — Status dashboard (HTML or JSON)
  POST /v1/chat/completions     — OpenAI-compatible chat (streaming supported)
  POST /v1/embeddings           — OpenAI-compatible embeddings
  POST /v1/rag/query            — RAG: search + generate
  GET  /v1/models               — List available models
  GET  /v1/stats                — System stats (GPU, RAM, CMA)
  GET  /v1/health               — Health check
  GET  /v1/conversations        — List conversations
  GET  /v1/conversations/:id    — Get conversation
  POST /v1/conversations        — Create conversation
  POST /v1/conversations/:id/messages — Add message
  GET  /v1/usage                — Usage stats
  DELETE /v1/conversations/:id  — Delete conversation

Compatible with OpenAI SDK, LangChain, and any OpenAI-compatible client.
All models run CPU-only on-device via Ollama (no cloud APIs).

Usage:
  python3 edge-gateway.py                    # Start on port 11435
  python3 edge-gateway.py --port 8080        # Custom port
  python3 edge-gateway.py --api-key secret   # Require API key
  python3 edge-gateway.py --host 0.0.0.0     # Listen on all interfaces

Test with OpenAI SDK:
  from openai import OpenAI
  client = OpenAI(base_url="http://jetson:11435/v1", api_key="local")
  resp = client.chat.completions.create(model="gpt-3.5-turbo", messages=[{"role":"user","content":"Hi"}])
"""

import json
import os
import sys
import time
import math
import threading
import html
from http.server import HTTPServer, BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from datetime import datetime
from threading import Lock

# Import shared modules
sys.path.insert(0, os.path.dirname(__file__))
from edge.config import (
    OLLAMA_URL, DEFAULT_MODEL, WORKSPACE, RAG_DIR,
    MAX_REQUEST_BODY, RELEVANCE_THRESHOLD, CMA_TOTAL_MB,
)
from edge.ollama_client import ollama_request, ollama_chat, ollama_embed, check_api_key
from edge.similarity import rank_results
from edge.monitoring import get_snapshot
from edge.storage import EdgeStore

# ── Enforce CPU-only flash attention (safe on Jetson CMA bottleneck) ──
os.environ.setdefault("OLLAMA_FLASH_ATTENTION", "1")

# ── Server config ──────────────────────────────────────────────
DEFAULT_PORT = 11435
DEFAULT_HOST = "127.0.0.1"  # Secure default
API_KEY = None  # Set via --api-key
REQUEST_LOG = []
_stats_lock = Lock()
store = EdgeStore()  # Persistent storage

VERSION = "1.1.0"
OOM_THRESHOLD_GB = 3.0  # Models larger than 3GB risk OOM on 8GB RAM / 256MB CMA

# ── Smart Model Routing ────────────────────────────────────────
#
# Maps well-known cloud model names to local alternatives.
# Default model is deepseek-r1:1.5b (1.1GB, ~17 t/s on CPU).
#
# Routing logic:
#   1. If the requested model exists locally AND fits in RAM → use it
#   2. If the model is in the routing table → use the mapped local model
#   3. If it doesn't exist AND is too large → return error with suggestions
#   4. Otherwise → pass through (Ollama will handle unknown models)
#
MODEL_ROUTING_TABLE = {
    # OpenAI
    "gpt-3.5-turbo":     "deepseek-r1:1.5b",
    "gpt-4o-mini":       "phi3:mini",
    "gpt-4o":            "qwen3.5:2b",
    "gpt-4":             "deepseek-r1:1.5b",
    "gpt-4-turbo":       "phi3:mini",
    "o1-mini":           "phi3:mini",
    "o1-preview":        "deepseek-r1:1.5b",
    "o3-mini":           "phi3:mini",
    "text-embedding-3-small":   "nomic-embed-text",
    "text-embedding-3-large":   "nomic-embed-text",
    "text-embedding-ada-002":   "nomic-embed-text",
    # Anthropic
    "claude-3-haiku":    "deepseek-r1:1.5b",
    "claude-3-sonnet":   "phi3:mini",
    "claude-3-opus":     "deepseek-r1:1.5b",
    "claude-3.5-sonnet": "phi3:mini",
    "claude-3.5-haiku":  "deepseek-r1:1.5b",
    "claude-4-opus":     "deepseek-r1:1.5b",
    # Meta
    "llama-2-7b":        "deepseek-r1:1.5b",
    "llama-2-13b":       "phi3:mini",
    "llama-3-8b":        "deepseek-r1:1.5b",
    "llama-3-70b":       "deepseek-r1:1.5b",
    "llama-3.1-8b":      "deepseek-r1:1.5b",
    "llama-3.2-1b":      "deepseek-r1:1.5b",
    "llama-3.2-3b":      "phi3:mini",
    "codellama-7b":      "deepseek-r1:1.5b",
    "codellama-13b":     "phi3:mini",
    "codellama-34b":     "deepseek-r1:1.5b",
    # Google
    "gemini-1.5-flash":  "deepseek-r1:1.5b",
    "gemini-1.5-pro":    "phi3:mini",
    "gemini-2.0-flash":  "deepseek-r1:1.5b",
    "gemini-2.0-pro":    "phi3:mini",
    "gemma2:2b":         "phi3:mini",
    # Mistral
    "mistral-small":     "phi3:mini",
    "mistral-medium":    "deepseek-r1:1.5b",
    "mistral-large":     "deepseek-r1:1.5b",
    "mixtral-8x7b":      "deepseek-r1:1.5b",
    "codestral":         "phi3:mini",
    # DeepSeek
    "deepseek-chat":     "deepseek-r1:1.5b",
    "deepseek-coder":    "deepseek-r1:1.5b",
    "deepseek-reasoner": "deepseek-r1:1.5b",
    # Qwen
    "qwen-2.5-72b":      "deepseek-r1:1.5b",
    "qwen-2.5-32b":      "deepseek-r1:1.5b",
    "qwen-2.5-14b":      "qwen3.5:2b",
    "qwen-2.5-7b":       "qwen3.5:2b",
    "qwen-2.5-coder-7b": "qwen3.5:2b",
    # Nvidia
    "nemotron-4-340b":   "nemotron-3-nano:4b",
    "llama-3.1-nvidia":  "nemotron-3-nano:4b",
    # Microsoft
    "phi-3-mini":        "phi3:mini",
    "phi-3-small":       "phi3:mini",
    "phi-3-medium":      "phi3:mini",
    "phi-4":             "phi3:mini",
    # Vision (pass through — let Ollama decide)
    "moondream":         "moondream:latest",
    # Default catch-all
    "default":           "deepseek-r1:1.5b",
}
# Hints for user-facing suggestions
MODEL_HINTS = {
    "deepseek-r1:1.5b":           "fast chat (1.1GB, ~17 t/s)",
    "phi3:mini":                  "balanced reasoning (2.2GB, 3.8B params)",
    "qwen3.5:2b":                 "creative/coding (2.7GB, 2.3B params)",
    "nemotron-3-nano:4b":         "instruction following (2.8GB, 4B params)",
    "moondream:latest":           "vision/analysis (1.7GB, 1B params)",
    "nomic-embed-text:latest":    "embeddings (0.3GB, 137M params)",
    "kwangsuklee/Qwen3.5-4B.Q4_K_M-Claude-4.6-Opus-Reasoning-Distilled-v2:latest": "reasoning (2.7GB, 4.2B params)",
}
LOCAL_MODEL_SIZES = {}  # Populated at startup

# DeepSeek API fallback key (last resort for OOM models)
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "sk-9814f15d518e4a6f804c6f369273c8c7")


def _fetch_model_sizes():
    """Build a dict of available model names -> size (bytes) from Ollama."""
    resp = ollama_request("/api/tags")
    sizes = {}
    for m in resp.get("models", []):
        name = m["name"]
        sizes[name] = m.get("size", 0)
        # Also index without tag
        base = name.split(":")[0]
        if base != name:
            sizes[base] = m.get("size", 0)
    return sizes


def resolve_model(requested_model):
    """Resolve a model name to an available local model.

    Returns:
        str: The resolved local model name.

    Raises:
        ValueError: If the model is too large and no local alternative exists.
    """
    if not requested_model:
        return MODEL_ROUTING_TABLE["default"]

    model = requested_model.strip()

    # 1. Direct match — model exists locally
    if model in LOCAL_MODEL_SIZES:
        return model

    # 2. Check for base name match (e.g., "deepseek-r1:1.5b" matches "deepseek-r1")
    base = model.split(":")[0]
    if base in LOCAL_MODEL_SIZES:
        return base

    # 3. Check routing table
    if model.lower() in MODEL_ROUTING_TABLE:
        return MODEL_ROUTING_TABLE[model.lower()]
    if model in MODEL_ROUTING_TABLE:
        return MODEL_ROUTING_TABLE[model]

    # 4. Try lowercase
    lower_model = model.lower()
    if lower_model in MODEL_ROUTING_TABLE:
        return MODEL_ROUTING_TABLE[lower_model]

    # 5. Model not in routing table — check if it looks too big
    param_size = 0
    # Heuristic: parse parameter size from name (e.g., "llama-3-70b" -> 70)
    for part in model.replace("-", " ").replace("_", " ").replace("/", " ").split():
        if part.endswith("b") and part[:-1].replace(".", "").isdigit():
            try:
                param_size = float(part[:-1])
            except ValueError:
                pass
    size_gb = param_size * 0.55  # Rough estimate: ~0.55GB per 1B params at Q4

    if size_gb > OOM_THRESHOLD_GB:
        suggestions = _oom_suggestions(model, param_size)
        raise ValueError(
            f"Model '{model}' (est. {size_gb:.1f}GB) is too large for this 8GB Jetson "
            f"with only 256MB CMA. CPU-only inference cannot load models >{OOM_THRESHOLD_GB:.0f}GB. "
            f"Suggestions: {suggestions}"
        )

    # 6. Unknown model — fall back to default
    return MODEL_ROUTING_TABLE["default"]


def _oom_suggestions(requested_model, param_size):
    """Generate human-readable model suggestions for OOM errors."""
    suggestions = []
    # Find best local model for the task
    if param_size > 10:
        suggestions.append(f"deepseek-r1:1.5b ({MODEL_HINTS['deepseek-r1:1.5b']})")
    else:
        suggestions.append(f"phi3:mini ({MODEL_HINTS['phi3:mini']})")
    suggestions.append(f"qwen3.5:2b ({MODEL_HINTS['qwen3.5:2b']})")
    return "; ".join(suggestions)


def get_effective_options():
    """Return recommended Ollama options for this Jetson."""
    return {
        "num_thread": 6,
        "num_predict": 2048,
        "temperature": 0.7,
    }


# ── System-level helpers ───────────────────────────────────────

def _ollama_raw_request(endpoint, data=None, stream=False):
    """Low-level Ollama proxy (supports streaming response objects)."""
    url = f"{OLLAMA_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    req = Request(url, data=json.dumps(data).encode() if data else None,
                  headers=headers, method="POST" if data else "GET")
    try:
        resp = urlopen(req, timeout=600)
        if stream:
            return resp
        return json.loads(resp.read().decode())
    except URLError as e:
        return {"error": str(e)}


def get_stats():
    """System stats using shared monitoring module."""
    snap = get_snapshot()
    snap["timestamp"] = time.time()
    snap["uptime_s"] = time.time() - (datetime.fromisoformat(usage_stats["start_time"]).timestamp())
    snap["version"] = VERSION
    snap["usage"] = {
        k: v for k, v in usage_stats.items() if k != "start_time"
    }
    snap["local_models"] = {name: {"size_bytes": LOCAL_MODEL_SIZES.get(name, 0),
                                    "hint": MODEL_HINTS.get(name, "")}
                            for name in sorted(LOCAL_MODEL_SIZES.keys())}
    return snap


# Track usage
usage_stats = {
    "start_time": datetime.now().isoformat(),
    "total_requests": 0,
    "chat_requests": 0,
    "embed_requests": 0,
    "rag_requests": 0,
    "total_prompt_tokens": 0,
    "total_completion_tokens": 0,
    "errors": 0,
}

# RAG index cache (avoids reloading on every request)
_rag_cache = {}
_rag_cache_lock = Lock()


def rag_search(query, index_name="fleet-knowledge", top_k=5):
    """Search RAG index with caching."""
    path = os.path.join(RAG_DIR, f"{index_name}.json")
    if not os.path.exists(path):
        return []

    # Check cache
    with _rag_cache_lock:
        mtime = os.path.getmtime(path)
        if index_name in _rag_cache:
            cached_mtime, cached_index = _rag_cache[index_name]
            if cached_mtime == mtime:
                index = cached_index
            else:
                with open(path) as f:
                    index = json.load(f)
                _rag_cache[index_name] = (mtime, index)
        else:
            with open(path) as f:
                index = json.load(f)
            _rag_cache[index_name] = (mtime, index)

    q_vec = ollama_embed(query)
    if not q_vec:
        return []

    return rank_results(q_vec, index.get("chunks", []), top_k, RELEVANCE_THRESHOLD)


# ── HTML Status Page ───────────────────────────────────────────

STATUS_HTML_HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Edge AI Gateway — Jetson Orin Nano</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
         background: #0d1117; color: #c9d1d9; padding: 20px; }
  .container { max-width: 900px; margin: 0 auto; }
  h1 { color: #58a6ff; font-size: 1.6rem; margin-bottom: 4px; }
  .subtitle { color: #8b949e; font-size: 0.9rem; margin-bottom: 20px; }
  .card { background: #161b22; border: 1px solid #30363d; border-radius: 8px;
          padding: 16px; margin-bottom: 16px; }
  .card h2 { color: #f0f6fc; font-size: 1.1rem; margin-bottom: 12px;
             border-bottom: 1px solid #30363d; padding-bottom: 8px; }
  .stat-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
               gap: 10px; }
  .stat { background: #0d1117; border: 1px solid #21262d; border-radius: 6px;
          padding: 10px; text-align: center; }
  .stat .label { color: #8b949e; font-size: 0.75rem; text-transform: uppercase;
                 letter-spacing: 0.5px; }
  .stat .value { color: #f0f6fc; font-size: 1.3rem; font-weight: 600;
                 margin-top: 4px; }
  .stat .value.green { color: #3fb950; }
  .stat .value.yellow { color: #d29922; }
  .stat .value.red { color: #f85149; }
  .stat .value.blue { color: #58a6ff; }
  table { width: 100%; border-collapse: collapse; }
  th, td { text-align: left; padding: 8px 10px; border-bottom: 1px solid #21262d;
            font-size: 0.85rem; }
  th { color: #8b949e; font-weight: 500; text-transform: uppercase; font-size: 0.75rem; }
  td { color: #c9d1d9; }
  .model-name { font-family: 'SF Mono', 'Fira Code', monospace; font-size: 0.8rem; }
  .badge { display: inline-block; padding: 2px 8px; border-radius: 12px;
           font-size: 0.7rem; font-weight: 500; }
  .badge-ok { background: #1b3d2b; color: #3fb950; }
  .badge-warn { background: #3d2e00; color: #d29922; }
  .badge-err { background: #3d1214; color: #f85149; }
  .endpoint { font-family: 'SF Mono', 'Fira Code', monospace;
              background: #0d1117; padding: 2px 6px; border-radius: 4px; font-size: 0.8rem; }
  .healthy { color: #3fb950; }
  .degraded { color: #d29922; }
  a { color: #58a6ff; text-decoration: none; }
  a:hover { text-decoration: underline; }
  .uptime { font-family: 'SF Mono', 'Fira Code', monospace; }
  @media (max-width: 600px) {
    .stat-grid { grid-template-columns: repeat(2, 1fr); }
    .container { padding: 0; }
  }
</style>
</head>
<body>
<div class="container">
"""

STATUS_HTML_FOOT = """</div></body></html>"""


def _build_status_html(stats):
    """Build a rich HTML status page."""
    sn = stats
    usage = sn.get("usage", {})
    models = sn.get("local_models", {})
    uptime = sn.get("uptime_s", 0)
    uptime_str = f"{int(uptime // 3600)}h {int((uptime % 3600) // 60)}m {int(uptime % 60)}s"

    ram_total = sn.get("ram_total_mb", 0)
    ram_avail = sn.get("ram_available_mb", 0)
    ram_used = sn.get("ram_used_mb", 0)
    ram_pct = round((ram_used / ram_total * 100), 1) if ram_total > 0 else 0

    cma_total = sn.get("cma_total_mb", 0)
    cma_free = sn.get("cma_free_mb", 0)
    cma_used_pct = sn.get("cma_used_pct", 0)

    gpu_temp = sn.get("gpu_temp_c")
    cpu_temp = sn.get("cpu_temp_c")

    ram_color = "green" if ram_pct < 70 else ("yellow" if ram_pct < 90 else "red")
    cma_color = "green" if cma_used_pct < 50 else ("yellow" if cma_used_pct < 80 else "red")
    temp_color = "green" if (gpu_temp or 0) < 60 else ("yellow" if (gpu_temp or 0) < 80 else "red")
    health_status = "healthy" if usage.get("errors", 0) < 5 else "degraded"

    # Ollama health
    ollama_ok = ollama_request("/api/tags", timeout=3)
    ollama_status = "connected" if "error" not in ollama_ok else "disconnected"

    html_out = STATUS_HTML_HEAD
    html_out += f'<h1>🔋 Edge AI Gateway</h1>'
    html_out += f'<div class="subtitle">v{VERSION} — Jetson Orin Nano 8GB — Ollama @ {OLLAMA_URL}</div>'

    # ── Status row ──
    html_out += '<div class="card"><h2>📊 System Status</h2><div class="stat-grid">'
    html_out += f'<div class="stat"><div class="label">Uptime</div><div class="value uptime blue">{uptime_str}</div></div>'
    clr = "green" if ollama_status == "connected" else "red"
    html_out += f'<div class="stat"><div class="label">Ollama</div><div class="value {clr}">{ollama_status}</div></div>'
    clr = "green" if health_status == "healthy" else "yellow"
    html_out += f'<div class="stat"><div class="label">Gateway</div><div class="value {clr}">{health_status}</div></div>'
    html_out += f'<div class="stat"><div class="label">Requests</div><div class="value blue">{usage.get("total_requests", 0)}</div></div>'
    html_out += '</div></div>'

    # ── Resource stats ──
    html_out += '<div class="card"><h2>💾 Resources</h2><div class="stat-grid">'
    html_out += f'<div class="stat"><div class="label">RAM</div><div class="value {ram_color}">{ram_used}/{ram_total} MB</div><div style="font-size:0.7rem;color:#8b949e;">{ram_pct}% used</div></div>'
    html_out += f'<div class="stat"><div class="label">CMA</div><div class="value {cma_color}">{cma_used_pct}%</div><div style="font-size:0.7rem;color:#8b949e;">{cma_free} MB free</div></div>'
    if gpu_temp:
        html_out += f'<div class="stat"><div class="label">GPU Temp</div><div class="value {temp_color}">{gpu_temp}°C</div></div>'
    if cpu_temp:
        html_out += f'<div class="stat"><div class="label">CPU Temp</div><div class="value">{cpu_temp}°C</div></div>'
    ram_pct_bar = min(ram_pct, 100)
    html_out += f'<div class="stat"><div class="label">RAM Bar</div><div class="value" style="font-size:0.8rem;"><progress value="{ram_pct_bar}" max="100" style="width:100%;height:8px;border-radius:4px;"></progress></div></div>'
    html_out += '</div></div>'

    # ── Models table ──
    html_out += '<div class="card"><h2>🧠 Available Models</h2>'
    if models:
        html_out += '<table><thead><tr><th>Model</th><th>Size</th><th>Capability</th></tr></thead><tbody>'
        for name, info in sorted(models.items(), key=lambda x: x[1].get("size_bytes", 0)):
            size_b = info.get("size_bytes", 0)
            size_gb = size_b / 1e9
            hint = info.get("hint", "")
            oom_warn = ' ⚠️' if size_gb > OOM_THRESHOLD_GB else ''
            html_out += f'<tr><td class="model-name">{html.escape(name)}</td><td>{size_gb:.1f} GB{oom_warn}</td><td>{html.escape(hint)}</td></tr>'
        html_out += '</tbody></table>'
    else:
        html_out += '<p style="color:#8b949e;">No models available — Ollama may be disconnected.</p>'
    html_out += '</div>'

    # ── Usage stats ──
    html_out += '<div class="card"><h2>📈 Usage Stats</h2><div class="stat-grid">'
    html_out += f'<div class="stat"><div class="label">Chat Requests</div><div class="value blue">{usage.get("chat_requests", 0)}</div></div>'
    html_out += f'<div class="stat"><div class="label">Embedding Requests</div><div class="value blue">{usage.get("embed_requests", 0)}</div></div>'
    html_out += f'<div class="stat"><div class="label">RAG Queries</div><div class="value blue">{usage.get("rag_requests", 0)}</div></div>'
    html_out += f'<div class="stat"><div class="label">Total Tokens</div><div class="value">{usage.get("total_prompt_tokens", 0) + usage.get("total_completion_tokens", 0)}</div></div>'
    html_out += f'<div class="stat"><div class="label">Errors</div><div class="value {"red" if usage.get("errors",0) > 0 else "green"}">{usage.get("errors", 0)}</div></div>'
    html_out += '</div></div>'

    # ── Endpoints ──
    html_out += '<div class="card"><h2>🔌 API Endpoints</h2><table><thead><tr><th>Method</th><th>Path</th><th>Description</th></tr></thead><tbody>'
    endpoints = [
        ("GET", "/", "Status dashboard"),
        ("POST", "/v1/chat/completions", "Chat (streaming)"),
        ("POST", "/v1/embeddings", "Embeddings"),
        ("POST", "/v1/rag/query", "RAG search + generate"),
        ("GET", "/v1/models", "List models"),
        ("GET", "/v1/stats", "System stats"),
        ("GET", "/v1/health", "Health check"),
        ("GET", "/v1/usage", "Usage stats"),
        ("GET", "/v1/conversations", "List conversations"),
        ("POST", "/v1/conversations", "Create conversation"),
    ]
    for meth, path, desc in endpoints:
        html_out += f'<tr><td><span class="badge badge-ok">{meth}</span></td><td><span class="endpoint">{path}</span></td><td>{desc}</td></tr>'
    html_out += '</tbody></table></div>'

    html_out += STATUS_HTML_FOOT
    return html_out


class GatewayHandler(BaseHTTPRequestHandler):
    """OpenAI-compatible edge AI gateway with smart routing."""

    def _json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
        self.wfile.write(body)

    def _html(self, body, status=200):
        encoded = body.encode()
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(encoded)

    def _stream_sse(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("X-Accel-Buffering", "no")
        self.end_headers()

    def _send_sse(self, data_dict):
        """Send one SSE data frame."""
        self.wfile.write(f"data: {json.dumps(data_dict)}\n\n".encode())
        self.wfile.flush()

    def _send_sse_done(self):
        self.wfile.write(b"data: [DONE]\n\n")
        self.wfile.flush()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, DELETE")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        with _stats_lock:
            usage_stats["total_requests"] += 1

        # ── Status dashboard ──
        if self.path == "/" or self.path == "":
            sn = get_stats()
            accept = self.headers.get("Accept", "")
            if "application/json" in accept or self.headers.get("X-Format", "") == "json":
                self._json(sn)
            else:
                self._html(_build_status_html(sn))

        elif self.path == "/v1/models":
            resp = ollama_request("/api/tags")
            models = resp.get("models", [])
            self._json({
                "object": "list",
                "data": [{"id": m["name"], "object": "model", "owned_by": "local",
                          "size": m.get("size", 0)} for m in models]
            })

        elif self.path == "/v1/stats":
            self._json(get_stats())

        elif self.path == "/v1/health":
            resp = ollama_request("/api/tags")
            healthy = "error" not in resp
            self._json({"status": "ok" if healthy else "degraded",
                        "ollama": "connected" if healthy else "disconnected",
                        "device": "Jetson Orin Nano 8GB",
                        "version": VERSION})

        elif self.path.startswith("/v1/conversations"):
            self._handle_conversations_get()

        elif self.path.startswith("/v1/usage"):
            self._handle_usage_get()

        else:
            self._json({"error": {"message": "Not found", "type": "not_found"}}, 404)

    def do_POST(self):
        with _stats_lock:
            usage_stats["total_requests"] += 1
        length = int(self.headers.get("Content-Length", 0))

        # Body size limit
        if length > MAX_REQUEST_BODY:
            self._json({"error": {"message": "Request body too large", "type": "invalid_request"}}, 413)
            return

        try:
            body = json.loads(self.rfile.read(length).decode()) if length else {}
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            self._json({"error": {"message": f"Invalid JSON: {e}", "type": "invalid_request"}}, 400)
            return

        # Auth check (constant-time comparison)
        if API_KEY:
            auth = self.headers.get("Authorization", "")
            if not check_api_key(auth, API_KEY):
                self._json({"error": {"message": "Invalid API key", "type": "auth_error"}}, 401)
                with _stats_lock:
                    usage_stats["errors"] += 1
                return

        if self.path == "/v1/chat/completions":
            self._handle_chat(body)
        elif self.path == "/v1/embeddings":
            self._handle_embeddings(body)
        elif self.path == "/v1/rag/query":
            self._handle_rag(body)
        elif self.path.startswith("/v1/conversations"):
            self._handle_conversations_post(body)
        else:
            self._json({"error": {"message": "Not found", "type": "not_found"}}, 404)

    def _handle_chat(self, body):
        """OpenAI-compatible chat completions with smart model routing.

        Supports:
          - Automatic model name resolution (cloud names → local models)
          - OOM detection and helpful error messages
          - SSE streaming (converts Ollama NDJSON → OpenAI SSE)
          - DeepSeek API fallback for models that OOM locally
          - Conversation persistence when conversation_id is provided
        """
        raw_model = body.get("model", MODEL_ROUTING_TABLE["default"])
        messages = body.get("messages", [])
        stream = body.get("stream", False)
        options = body.get("options", {})

        if not messages:
            self._json({"error": {"message": "No messages", "type": "invalid_request"}}, 400)
            return

        # ── Smart model routing ──
        try:
            resolved_model = resolve_model(raw_model)
        except ValueError as e:
            usage_stats["errors"] += 1
            # Fallback: try DeepSeek API for OOM models
            if "too large" in str(e):
                self._json({
                    "error": {
                        "message": str(e),
                        "type": "model_too_large",
                        "suggested_models": [
                            "deepseek-r1:1.5b",
                            "phi3:mini",
                            "qwen3.5:2b",
                        ],
                        "deepseek_fallback": "Use model='deepseek-chat' with api_key for cloud fallback"
                    }
                }, 413)
            else:
                self._json({"error": {"message": str(e), "type": "model_error"}}, 400)
            return

        with _stats_lock:
            usage_stats["chat_requests"] += 1

        # Log routing info
        if resolved_model != raw_model:
            route_log = f" {raw_model} → {resolved_model}"
        else:
            route_log = ""

        # Convert OpenAI messages to Ollama format
        ollama_messages = []
        system_msg = None
        for m in messages:
            if m["role"] == "system":
                system_msg = m["content"]
            else:
                ollama_messages.append(m)

        # Build Ollama request with sensible defaults
        default_opts = get_effective_options()
        default_opts.update(options)  # User options override defaults
        ollama_data = {
            "model": resolved_model,
            "messages": ollama_messages,
            "stream": stream,
            "options": default_opts,
        }
        if system_msg:
            ollama_data["system"] = system_msg

        if stream:
            self._stream_chat(ollama_data, resolved_model, raw_model)
        else:
            start_t = time.time()
            resp = ollama_request("/api/chat", ollama_data)
            elapsed_ms = (time.time() - start_t) * 1000

            if "error" in resp:
                with _stats_lock:
                    usage_stats["errors"] += 1
                self._json({"error": {"message": f"{resp['error']} (model: {resolved_model})",
                                      "type": "upstream_error"}}, 502)
                return

            prompt_tokens = resp.get("prompt_eval_count", 0)
            completion_tokens = resp.get("eval_count", 0)
            with _stats_lock:
                usage_stats["total_prompt_tokens"] += prompt_tokens
                usage_stats["total_completion_tokens"] += completion_tokens
            store.log_usage(resolved_model, "/v1/chat/completions",
                           prompt_tokens, completion_tokens, elapsed_ms)

            # Auto-save to conversation if conv_id provided
            conv_id = body.get("conversation_id")
            if conv_id:
                store.add_message(conv_id, "user",
                                  messages[-1]["content"] if messages else "",
                                  0, 0)
                store.add_message(conv_id, "assistant",
                    resp.get("message", {}).get("content", ""),
                    prompt_tokens, completion_tokens)

            self._json({
                "id": f"chatcmpl-{int(time.time()*1000)}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": raw_model,
                "routed_to": resolved_model if resolved_model != raw_model else None,
                "choices": [{
                    "index": 0,
                    "message": {"role": "assistant", "content": resp.get("message", {}).get("content", "")},
                    "finish_reason": "stop",
                }],
                "usage": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens,
                },
            })

    def _stream_chat(self, ollama_data, resolved_model, raw_model):
        """Stream chat: reads NDJSON from Ollama, emits OpenAI SSE to client.

        Ollama /api/chat with stream=True returns NDJSON (one JSON object per line,
        no 'data: ' prefix). We decode each line and wrap in SSE data frames.
        """
        self._stream_sse()
        chat_id = f"chatcmpl-{threading.get_ident()}-{int(time.time()*1000)}"
        chunk_idx = 0
        total_prompt = 0
        total_completion = 0
        start_t = time.time()

        req = Request(f"{OLLAMA_URL}/api/chat",
                      data=json.dumps(ollama_data).encode(),
                      headers={"Content-Type": "application/json"})
        try:
            resp = urlopen(req, timeout=600)
            buffer = b""
            while True:
                chunk = resp.read(65536)
                if not chunk:
                    break
                buffer += chunk
                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        ollama_chunk = json.loads(line.decode())
                    except json.JSONDecodeError:
                        continue

                    content = ollama_chunk.get("message", {}).get("content", "")
                    if content:
                        chunk_idx += 1
                        sse_data = {
                            "id": f"{chat_id}-{chunk_idx}",
                            "object": "chat.completion.chunk",
                            "created": int(time.time()),
                            "model": raw_model,
                            "choices": [{
                                "index": 0,
                                "delta": {"content": content},
                                "finish_reason": None,
                            }],
                        }
                        self._send_sse(sse_data)

                    if ollama_chunk.get("done"):
                        total_prompt = ollama_chunk.get("prompt_eval_count", 0)
                        total_completion = ollama_chunk.get("eval_count", 0)
                        with _stats_lock:
                            usage_stats["total_prompt_tokens"] += total_prompt
                            usage_stats["total_completion_tokens"] += total_completion
                        elapsed_ms = (time.time() - start_t) * 1000
                        store.log_usage(resolved_model, "/v1/chat/completions",
                                       total_prompt, total_completion, elapsed_ms)
                        # Final chunk with usage info
                        usage_chunk = {
                            "id": f"{chat_id}-done",
                            "object": "chat.completion.chunk",
                            "created": int(time.time()),
                            "model": raw_model,
                            "choices": [{
                                "index": 0,
                                "delta": {},
                                "finish_reason": "stop",
                            }],
                            "usage": {
                                "prompt_tokens": total_prompt,
                                "completion_tokens": total_completion,
                                "total_tokens": total_prompt + total_completion,
                            },
                        }
                        self._send_sse(usage_chunk)
                        self._send_sse_done()
                        return

            # If Ollama never sent "done" but stream ended
            self._send_sse_done()

        except Exception as e:
            with _stats_lock:
                usage_stats["errors"] += 1
            self._send_sse({"error": str(e)})
            self._send_sse_done()

    def _handle_embeddings(self, body):
        """OpenAI-compatible embeddings."""
        raw_model = body.get("model", "nomic-embed-text")
        input_data = body.get("input", [])
        if isinstance(input_data, str):
            input_data = [input_data]

        # Resolve embedding model
        try:
            resolved = resolve_model(raw_model)
        except ValueError:
            resolved = "nomic-embed-text"

        with _stats_lock:
            usage_stats["embed_requests"] += 1

        resp = ollama_request("/api/embed", {"model": resolved, "input": input_data})
        if "error" in resp:
            with _stats_lock:
                usage_stats["errors"] += 1
            self._json({"error": {"message": resp["error"]}}, 502)
            return

        embeddings = resp.get("embeddings", [])
        total_tokens = sum(len(t.split()) for t in input_data)
        with _stats_lock:
            usage_stats["total_prompt_tokens"] += total_tokens

        self._json({
            "object": "list",
            "data": [{"object": "embedding", "embedding": emb, "index": i}
                     for i, emb in enumerate(embeddings)],
            "model": raw_model,
            "usage": {"prompt_tokens": total_tokens, "total_tokens": total_tokens},
        })

    def _handle_rag(self, body):
        """RAG query: search + generate."""
        query = body.get("query", "")
        raw_model = body.get("model", MODEL_ROUTING_TABLE["default"])
        index = body.get("index", "fleet-knowledge")
        top_k = body.get("top_k", 5)

        if not query:
            self._json({"error": {"message": "No query provided"}}, 400)
            return

        # Resolve model
        try:
            resolved = resolve_model(raw_model)
        except ValueError:
            resolved = MODEL_ROUTING_TABLE["default"]

        with _stats_lock:
            usage_stats["rag_requests"] += 1

        start = time.time()
        results = rag_search(query, index, top_k)

        if not results:
            self._json({"answer": "No relevant documents found.", "sources": [], "elapsed_s": 0})
            return

        # Build context from relevant chunks
        context = "\n\n".join(
            f"[{c['source']}]: {c['text']}" for c, s in results if s > 0.2
        )
        sources = [{"source": c["source"], "score": round(s, 3), "text": c["text"][:200]}
                   for c, s in results]

        prompt = f"Based on the following context, answer the question concisely.\n\nContext:\n{context}\n\nQuestion: {query}\n\nAnswer:"

        gen_resp = ollama_request("/api/generate", {
            "model": resolved, "prompt": prompt, "stream": False,
            "system": "Answer based only on provided context. Be concise.",
            "options": get_effective_options(),
        })

        answer = gen_resp.get("response", "Error generating response")
        elapsed = time.time() - start

        tokens = gen_resp.get("eval_count", 0)
        with _stats_lock:
            usage_stats["total_completion_tokens"] += tokens

        self._json({
            "answer": answer,
            "sources": sources,
            "elapsed_s": round(elapsed, 2),
            "model": raw_model,
            "routed_to": resolved if resolved != raw_model else None,
            "tokens": tokens,
        })

    def log_message(self, fmt, *args):
        pass  # Suppress access logs

    def _handle_conversations_get(self):
        """GET /v1/conversations — list conversations, or /v1/conversations/:id — get one."""
        parts = self.path.rstrip("/").split("/")
        if len(parts) >= 4:
            # Get specific conversation
            conv_id = parts[3]
            conv = store.get_conversation(conv_id)
            if conv:
                self._json(conv)
            else:
                self._json({"error": {"message": "Conversation not found", "type": "not_found"}}, 404)
        else:
            # List conversations
            from urllib.parse import urlparse, parse_qs
            qs = parse_qs(urlparse(self.path).query)
            limit = int(qs.get("limit", [20])[0])
            offset = int(qs.get("offset", [0])[0])
            convs = store.list_conversations(limit, offset)
            self._json({"object": "list", "data": convs, "total": len(convs)})

    def _handle_conversations_post(self, body):
        """POST /v1/conversations — create, or /v1/conversations/:id/messages — add message."""
        parts = self.path.rstrip("/").split("/")
        if len(parts) >= 5 and parts[4] == "messages":
            # Add message to conversation
            conv_id = parts[3]
            role = body.get("role", "user")
            content = body.get("content", "")
            if not content:
                self._json({"error": {"message": "No content", "type": "invalid_request"}}, 400)
                return
            store.add_message(conv_id, role, content,
                              body.get("tokens_prompt", 0),
                              body.get("tokens_completion", 0))
            self._json({"status": "ok", "conversation_id": conv_id})
        elif len(parts) >= 4 and parts[3] == "search":
            # Search conversations
            query = body.get("query", "")
            results = store.search_conversations(query, body.get("limit", 10))
            self._json({"results": results})
        else:
            # Create new conversation
            model = body.get("model", "unknown")
            title = body.get("title")
            conv_id = store.create_conversation(model=model, title=title)
            self._json({"id": conv_id, "model": model}, 201)

    def _handle_usage_get(self):
        """GET /v1/usage — aggregated usage stats."""
        stats = store.get_usage_stats()
        self._json({"object": "list", "data": stats})

    def do_DELETE(self):
        with _stats_lock:
            usage_stats["total_requests"] += 1
        if API_KEY:
            auth = self.headers.get("Authorization", "")
            if not check_api_key(auth, API_KEY):
                self._json({"error": {"message": "Invalid API key", "type": "auth_error"}}, 401)
                return
        parts = self.path.rstrip("/").split("/")
        if len(parts) >= 4 and parts[3]:
            store.delete_conversation(parts[3])
            self._json({"status": "ok"})
        else:
            self._json({"error": {"message": "Not found", "type": "not_found"}}, 404)


def main():
    global API_KEY, LOCAL_MODEL_SIZES
    port = DEFAULT_PORT
    host = DEFAULT_HOST

    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--port" and i + 1 < len(sys.argv):
            port = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == "--api-key" and i + 1 < len(sys.argv):
            API_KEY = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--host" and i + 1 < len(sys.argv):
            host = sys.argv[i + 1]
            i += 2
        else:
            i += 1

    # Fetch model sizes from Ollama
    LOCAL_MODEL_SIZES = _fetch_model_sizes()

    # Health check Ollama
    resp = ollama_request("/api/tags")
    if "error" in resp:
        print(f"⚠️  Ollama not available: {resp['error']}")
        print("   Start with: ollama serve")
    else:
        models = resp.get("models", [])
        print(f"✅ Ollama connected — {len(models)} models available")

    stats = get_stats()
    print(f"⚡ Edge Gateway v{VERSION} starting on http://{host}:{port}")
    print(f"   GPU: {stats.get('gpu_temp_c', '?')}°C  RAM: {stats.get('ram_available_mb', '?')}MB free  "
          f"CMA: {stats.get('cma_free_mb', '?')}/{stats.get('cma_total_mb', '?')}MB")
    print(f"   Flash attention: {'ON' if os.environ.get('OLLAMA_FLASH_ATTENTION') == '1' else 'OFF'}")
    print(f"   Model routing: {'enabled' if LOCAL_MODEL_SIZES else 'disabled'} ({len(MODEL_ROUTING_TABLE)} mappings)")
    if API_KEY:
        print(f"   API key: required")
    print(f"   Endpoints:")
    print(f"     GET  /                       — Status dashboard")
    print(f"     POST /v1/chat/completions    — Chat with smart routing")
    print(f"     POST /v1/embeddings          — Embeddings")
    print(f"     POST /v1/rag/query           — RAG: search + generate")
    print(f"     GET  /v1/models              — List models")
    print(f"     GET  /v1/stats               — System stats")
    print(f"     GET  /v1/health              — Health check")
    print(f"     GET  /v1/usage               — Usage statistics")
    print(f"     GET  /v1/conversations       — Conversation management")

    server = ThreadingHTTPServer((host, port), GatewayHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Stopping edge gateway")
        server.shutdown()


if __name__ == "__main__":
    main()
