#!/usr/bin/env python3
"""
TensorRT On-Device Engine Benchmark Suite (v2)
Jetson Orin Nano 8GB — Native engine building and inference profiling

Creates ONNX models → builds TRT engines on-device → profiles inference
"""

import torch
import torch.nn as nn
import subprocess
import json
import os
import time
import re

OUT_DIR = "/home/lucineer/.openclaw/workspace/tensorrt_build/benchmark_results"
TREXEC = "/usr/src/tensorrt/bin/trtexec"
ENGINE_DIR = "/tmp/trt_benchmark_engines"

os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(ENGINE_DIR, exist_ok=True)


# --- Model definitions ---

class TinyRoom(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(64, 32), nn.GELU(), nn.Linear(32, 64))
    def forward(self, x): return self.net(x)

class SmallRoom(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(128, 64), nn.GELU(), nn.Linear(64, 128))
    def forward(self, x): return self.net(x)

class MediumRoom(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(256, 128), nn.GELU(), nn.Linear(128, 256))
    def forward(self, x): return self.net(x)

class DeepRoom(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(256, 256), nn.GELU(),
            nn.Linear(256, 128), nn.GELU(),
            nn.Linear(128, 256),
        )
    def forward(self, x): return self.net(x)

class WideRoom(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(512, 256), nn.GELU(), nn.Linear(256, 512))
    def forward(self, x): return self.net(x)

class EmbeddingRoom(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(768, 384), nn.GELU(), nn.Linear(384, 768))
    def forward(self, x): return self.net(x)

class AttentionRoom(nn.Module):
    def __init__(self):
        super().__init__()
        D = 256; H = 4; HD = D // H
        self.qkv = nn.Linear(D, D * 3)
        self.proj = nn.Linear(D, D)
        self.ffn = nn.Sequential(nn.Linear(D, D*4), nn.GELU(), nn.Linear(D*4, D))
        self.norm1 = nn.LayerNorm(D)
        self.norm2 = nn.LayerNorm(D)
        self.D, self.H, self.HD = D, H, HD
    def forward(self, x):
        B, S, D = x.shape
        qkv = self.qkv(x).reshape(B, S, 3, self.H, self.HD)
        q, k, v = qkv.unbind(2)
        q, k, v = q.transpose(1,2), k.transpose(1,2), v.transpose(1,2)
        attn = torch.softmax((q @ k.transpose(-2,-1)) * (self.HD ** -0.5), dim=-1)
        out = (attn @ v).transpose(1,2).reshape(B, S, D)
        x = self.norm1(x + self.proj(out))
        return self.norm2(x + self.ffn(x))


MODELS = [
    ("tiny_room_64",       TinyRoom,       64,   1),
    ("small_room_128",     SmallRoom,      128,  1),
    ("medium_room_256",    MediumRoom,     256,  1),
    ("deep_room_256",      DeepRoom,       256,  1),
    ("wide_room_512",      WideRoom,       512,  1),
    ("embedding_room_768", EmbeddingRoom,  768,  1),
    ("attention_room_256", AttentionRoom,  256,  8),
]


def create_onnx(model_cls, input_dim, seq_len, name):
    onnx_path = os.path.join(ENGINE_DIR, f"{name}.onnx")
    model = model_cls().eval()
    if seq_len > 1:
        dummy = torch.randn(1, seq_len, input_dim)
        axes = {"input": {0: "batch", 1: "seq"}, "output": {0: "batch", 1: "seq"}}
    else:
        dummy = torch.randn(1, input_dim)
        axes = {"input": {0: "batch"}, "output": {0: "batch"}}
    torch.onnx.export(model, dummy, onnx_path, opset_version=17,
                      input_names=["input"], output_names=["output"],
                      dynamic_axes=axes)
    return onnx_path


def parse_trtexec_output(text):
    """Parse trtexec combined stdout+stderr output"""
    m = {}
    # Build time
    match = re.search(r"Engine built in ([\d.]+) sec", text)
    if match: m["build_time_sec"] = float(match.group(1))
    # Peak mem
    match = re.search(r"Peak memory usage.*?CPU:\s*([\d.]+)\s*MiB", text)
    if match: m["build_peak_mem_mib"] = float(match.group(1))
    # Throughput
    match = re.search(r"Throughput:\s*([\d.]+)\s*qps", text)
    if match: m["throughput_qps"] = float(match.group(1))
    # Latency line: min = X ms, max = Y ms, mean = Z ms, median = M ms, percentile(90%) = P ms, ...
    match = re.search(
        r"Latency:\s*min\s*=\s*([\d.]+)\s*ms.*?mean\s*=\s*([\d.]+)\s*ms.*?median\s*=\s*([\d.]+)\s*ms.*?percentile\(90%\)\s*=\s*([\d.]+)\s*ms.*?percentile\(99%\)\s*=\s*([\d.]+)\s*ms",
        text, re.DOTALL
    )
    if match:
        m["latency_min_ms"] = float(match.group(1))
        m["latency_mean_ms"] = float(match.group(2))
        m["latency_median_ms"] = float(match.group(3))
        m["latency_p90_ms"] = float(match.group(4))
        m["latency_p99_ms"] = float(match.group(5))
    # GPU compute
    match = re.search(r"GPU Compute Time:\s*min\s*=\s*[\d.]+\s*ms.*?mean\s*=\s*([\d.]+)\s*ms", text, re.DOTALL)
    if match: m["gpu_compute_mean_ms"] = float(match.group(1))
    # Enqueue
    match = re.search(r"Enqueue Time:\s*min\s*=\s*[\d.]+\s*ms.*?mean\s*=\s*([\d.]+)\s*ms", text, re.DOTALL)
    if match: m["enqueue_mean_ms"] = float(match.group(1))
    return m


def benchmark_model(name, onnx_path):
    engine_path = os.path.join(ENGINE_DIR, f"{name}.trt")
    
    cmd = [
        TREXEC,
        f"--onnx={onnx_path}",
        f"--saveEngine={engine_path}",
        "--useSpinWait",
        "--duration=3",
    ]
    
    print(f"  Building + profiling {name}...", end=" ", flush=True)
    t0 = time.time()
    
    try:
        # trtexec writes EVERYTHING to stderr, merge with stdout
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                text=True, timeout=300)
        elapsed = time.time() - t0
        output = result.stdout
        
        if result.returncode != 0:
            print(f"FAILED ({elapsed:.1f}s)")
            # Show last few lines for debugging
            for line in output.strip().split('\n')[-5:]:
                print(f"    {line}")
            return None
        
        metrics = parse_trtexec_output(output)
        metrics["name"] = name
        metrics["total_wall_sec"] = elapsed
        
        if os.path.exists(engine_path):
            metrics["engine_size_mb"] = os.path.getsize(engine_path) / (1024*1024)
        
        # Save per-model result
        with open(os.path.join(OUT_DIR, f"{name}.json"), 'w') as f:
            json.dump(metrics, f, indent=2)
        
        qps = metrics.get('throughput_qps', 0)
        build = metrics.get('build_time_sec', 0)
        print(f"OK ({elapsed:.1f}s) — {qps:.0f} qps, build {build:.2f}s")
        return metrics
        
    except subprocess.TimeoutExpired:
        print("TIMEOUT (>300s)")
        return None
    except Exception as e:
        print(f"ERROR: {e}")
        return None


def main():
    print("=" * 65)
    print("TensorRT On-Device Benchmark Suite v2")
    print("Jetson Orin Nano 8GB — Native Build + Inference Profiling")
    print("=" * 65)
    
    # GPU info
    r = subprocess.run(["/usr/sbin/nvidia-smi", "--query-gpu=name,driver_version,memory.total",
                        "--format=csv,noheader"], capture_output=True, text=True)
    print(f"GPU: {r.stdout.strip()}")
    
    # TRT version
    r = subprocess.run([TREXEC, "--version"], capture_output=True, text=True, timeout=5)
    ver = r.stdout.split('\n')[0] if r.stdout else "unknown"
    print(f"TRT: {ver}")
    print()
    
    results = []
    
    for name, cls, dim, seq in MODELS:
        print(f"[{name}]")
        onnx_path = create_onnx(cls, dim, seq, name)
        metrics = benchmark_model(name, onnx_path)
        if metrics:
            results.append(metrics)
        print()
    
    # Summary table
    print("=" * 65)
    print("BENCHMARK SUMMARY")
    print("=" * 65)
    hdr = f"{'Model':<25} {'Build(s)':>8} {'QPS':>10} {'Mean(ms)':>10} {'P99(ms)':>10} {'Engine(MB)':>11}"
    print(hdr)
    print("-" * len(hdr))
    for r in results:
        def f(v, fmt=".2f"): return f"{v:{fmt}}" if v is not None else "?"
        print(f"{r['name']:<25} {f(r.get('build_time_sec')):>8} {f(r.get('throughput_qps'),'.0f'):>10} "
              f"{f(r.get('latency_mean_ms'),'.4f'):>10} {f(r.get('latency_p99_ms'),'.4f'):>10} "
              f"{f(r.get('engine_size_mb')):>11}")
    
    # Key findings
    print("\n--- KEY FINDINGS ---")
    if results:
        fastest = max(results, key=lambda x: x.get('throughput_qps') or 0)
        print(f"Fastest: {fastest['name']} at {fastest.get('throughput_qps',0):.0f} qps")
        slowest_build = max(results, key=lambda x: x.get('build_time_sec') or 0)
        print(f"Slowest build: {slowest_build['name']} at {slowest_build.get('build_time_sec',0):.2f}s")
        print(f"All engines built natively on-device (no cross-compilation)")
        print(f"SpinWait enabled for stable GPU clocks during measurement")
    
    # Save
    with open(os.path.join(OUT_DIR, "full_summary.json"), 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {OUT_DIR}/")


if __name__ == "__main__":
    main()
