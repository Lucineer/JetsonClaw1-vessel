#!/usr/bin/env python3
"""cocapn — Edge AI Fleet CLI for JC1

Usage:
  python3 cocapn-cli.py status       Show system + fleet status
  python3 cocapn-cli.py models       List AI models
  python3 cocapn-cli.py chat [msg]   Send a prompt (default: deepseek-r1:1.5b)
  python3 cocapn-cli.py fleet        Show fleet health

Environment:
  COCAPN_GATEWAY  Override gateway URL (default: http://127.0.0.1:11435)
"""
import argparse, json, os, sys, urllib.request, urllib.error

GATEWAY = os.environ.get("COCAPN_GATEWAY", "http://127.0.0.1:11435")
ORACLE1 = "http://147.224.38.131:8848"

def _req(method, url, data=None, timeout=5):
    try:
        body = json.dumps(data).encode() if data else None
        r = urllib.request.urlopen(
            urllib.request.Request(url, data=body, method=method,
                headers={"Content-Type": "application/json"}),
            timeout=timeout)
        return json.loads(r.read().decode())
    except Exception as e:
        return {"error": str(e)}

def cmd_status(args):
    r = _req("GET", f"{GATEWAY}/v1/health")
    if "error" in r:
        print(f"⚠️  Gateway offline: {r['error']}")
    else:
        print(f"✅ Edge Gateway: {r.get('status', 'unknown')}")
    try:
        with open("/proc/meminfo") as f:
            mem = f.read()
        cma_total = [l for l in mem.split("\n") if "CmaTotal" in l]
        cma_free = [l for l in mem.split("\n") if "CmaFree" in l]
        if cma_total:
            ct = int(cma_total[0].split()[1]) / 1024
            cf = int(cma_free[0].split()[1]) / 1024
            print(f"  CMA: {ct:.0f}MB / {cf:.1f}MB free")
    except:
        pass
    f = _req("GET", f"{GATEWAY}/v1/fleet")
    if "nodes" in f:
        up = sum(1 for n in f["nodes"].values() if n.get("status") == "ok")
        print(f"  Fleet: {up}/{f['nodes_total']} nodes up")

def cmd_models(args):
    r = _req("GET", f"{GATEWAY}/v1/models")
    if "error" in r:
        print(f"⚠️  {r['error']}")
        return
    models = r.get("data", r.get("models", []))
    for m in models:
        name = m.get("id", m.get("name", "?"))
        size = m.get("size", m.get("details", {}).get("parameter_size", ""))
        print(f"  {name:55s} {size}")

def cmd_chat(args):
    prompt = args.prompt or "Hello"
    r = _req("POST", f"{GATEWAY}/v1/chat/completions",
             {"model": args.model,
              "messages": [{"role": "user", "content": prompt}],
              "stream": False}, timeout=30)
    if "error" in r:
        print(f"⚠️  {r['error']}")
        return
    msg = r.get("choices", [{}])[0].get("message", {}).get("content", "")
    print(msg)

def cmd_fleet(args):
    f = _req("GET", f"{GATEWAY}/v1/fleet")
    if "nodes" in f:
        for nid, n in f["nodes"].items():
            status = "✅" if n.get("status") == "ok" else "⚠️"
            print(f"  {status} {n.get('name', nid):12s} — {n.get('role', '?')}")
        print(f"\n  {f.get('nodes_up', 0)}/{f.get('nodes_total', 0)} nodes up")

def main():
    p = argparse.ArgumentParser(description="cocapn — Edge AI Fleet CLI")
    p.set_defaults(func=lambda _: p.print_help())
    sub = p.add_subparsers(title="commands")

    for name, help_text, func in [
        ("status", "Show system and fleet status", cmd_status),
        ("models", "List available AI models on the edge gateway", cmd_models),
        ("chat", "Send a chat prompt to a local model", cmd_chat),
        ("fleet", "Show fleet health (JC1 + Oracle1)", cmd_fleet),
    ]:
        sp = sub.add_parser(name, help=help_text)
        if name == "chat":
            sp.add_argument("prompt", nargs="?", default="Hello")
            sp.add_argument("--model", "-m", default="deepseek-r1:1.5b", help="Model to use")
        sp.set_defaults(func=func)

    args = p.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
