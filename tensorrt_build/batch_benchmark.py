#!/usr/bin/env python3
"""
TensorRT Batch Multi-Room Inference Benchmark
Tests the REAL production workload: inferencing multiple rooms simultaneously

deckboss needs to evaluate many rooms per input — how many can we run in parallel?
"""

import torch
import torch.nn as nn
import subprocess
import json
import os
import time
import re

TREXEC = "/usr/src/tensorrt/bin/trtexec"
ENGINE_DIR = "/tmp/trt_batch_bench"
OUT_DIR = "/home/lucineer/.openclaw/workspace/tensorrt_build/benchmark_results"
os.makedirs(ENGINE_DIR, exist_ok=True)


class BatchRoom(nn.Module):
    """Single room: 256→128→256"""
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(256, 128), nn.GELU(), nn.Linear(128, 256))
    def forward(self, x): return self.net(x)


class MultiRoomStack(nn.Module):
    """N rooms stacked as a batch — each input goes through its own room"""
    def __init__(self, num_rooms):
        super().__init__()
        self.num_rooms = num_rooms
        # Share weights across rooms (like deckboss room switching)
        self.room = nn.Sequential(nn.Linear(256, 128), nn.GELU(), nn.Linear(128, 256))
    
    def forward(self, x):
        # x: [batch * num_rooms, 256]
        return self.room(x)


def create_multi_room_onnx(num_rooms, dim=256):
    name = f"multi_room_{num_rooms}"
    onnx_path = os.path.join(ENGINE_DIR, f"{name}.onnx")
    model = MultiRoomStack(num_rooms).eval()
    dummy = torch.randn(1, num_rooms, dim)
    torch.onnx.export(model, dummy, onnx_path, opset_version=17,
                      input_names=["input"], output_names=["output"],
                      dynamic_axes={"input": {0: "batch"}, "output": {0: "batch"}})
    return onnx_path, name


def create_pipeline_onnx(num_rooms, dim=256):
    """Sequential room pipeline: input → room1 → room2 → ... → roomN"""
    name = f"pipeline_{num_rooms}"
    onnx_path = os.path.join(ENGINE_DIR, f"{name}.onnx")
    
    layers = []
    for _ in range(num_rooms):
        layers.extend([nn.Linear(dim, 128), nn.GELU(), nn.Linear(128, dim)])
    
    model = nn.Sequential(*layers).eval()
    dummy = torch.randn(1, dim)
    torch.onnx.export(model, dummy, onnx_path, opset_version=17,
                      input_names=["input"], output_names=["output"],
                      dynamic_axes={"input": {0: "batch"}, "output": {0: "batch"}})
    return onnx_path, name


def parse_trtexec(text):
    m = {}
    match = re.search(r"Engine built in ([\d.]+) sec", text)
    if match: m["build_time_sec"] = float(match.group(1))
    match = re.search(r"Throughput:\s*([\d.]+)\s*qps", text)
    if match: m["throughput_qps"] = float(match.group(1))
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
    match = re.search(r"GPU Compute Time:\s*min\s*=\s*[\d.]+\s*ms.*?mean\s*=\s*([\d.]+)\s*ms", text, re.DOTALL)
    if match: m["gpu_compute_mean_ms"] = float(match.group(1))
    match = re.search(r"Peak memory usage.*?GPU:\s*([\d.]+)\s*MiB", text)
    if match: m["gpu_peak_mem_mib"] = float(match.group(1))
    return m


def benchmark(name, onnx_path):
    engine_path = os.path.join(ENGINE_DIR, f"{name}.trt")
    cmd = [TREXEC, f"--onnx={onnx_path}", f"--saveEngine={engine_path}",
           "--useSpinWait", "--duration=3"]
    
    print(f"  {name}...", end=" ", flush=True)
    t0 = time.time()
    try:
        r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           text=True, timeout=300)
        elapsed = time.time() - t0
        if r.returncode != 0:
            print(f"FAILED")
            return None
        metrics = parse_trtexec(r.stdout)
        metrics["name"] = name
        metrics["total_wall_sec"] = elapsed
        if os.path.exists(engine_path):
            metrics["engine_size_mb"] = os.path.getsize(engine_path) / (1024*1024)
        qps = metrics.get('throughput_qps', 0)
        lat = metrics.get('latency_mean_ms', 0)
        print(f"{qps:.0f} qps, {lat:.4f}ms mean")
        return metrics
    except subprocess.TimeoutExpired:
        print("TIMEOUT")
        return None
    except Exception as e:
        print(f"ERROR: {e}")
        return None


def main():
    print("=" * 70)
    print("TensorRT Batch + Pipeline Multi-Room Benchmark")
    print("Jetson Orin Nano 8GB — Production workload simulation")
    print("=" * 70)
    print()
    
    results = []
    
    # Test 1: Batch multi-room (parallel evaluation)
    print("--- BATCH MULTI-ROOM (shared weights, N rooms per batch) ---")
    for n in [1, 2, 4, 8, 16, 32, 64]:
        onnx_path, name = create_multi_room_onnx(n)
        m = benchmark(name, onnx_path)
        if m:
            m["mode"] = "batch"
            m["num_rooms"] = n
            results.append(m)
    print()
    
    # Test 2: Pipeline rooms (sequential)
    print("--- PIPELINE ROOMS (sequential, input flows through N rooms) ---")
    for n in [1, 2, 4, 8]:
        onnx_path, name = create_pipeline_onnx(n)
        m = benchmark(name, onnx_path)
        if m:
            m["mode"] = "pipeline"
            m["num_rooms"] = n
            results.append(m)
    print()
    
    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    print("\nBatch (parallel rooms, shared weights):")
    print(f"  {'Rooms':>5} {'QPS':>10} {'Mean(ms)':>10} {'P99(ms)':>10} {'Per-room(ms)':>14} {'Engine(MB)':>10}")
    batch = [r for r in results if r.get('mode') == 'batch']
    for r in sorted(batch, key=lambda x: x.get('num_rooms', 0)):
        per_room = r.get('latency_mean_ms', 0) / r.get('num_rooms', 1)
        print(f"  {r['num_rooms']:>5} {r.get('throughput_qps',0):>10.0f} "
              f"{r.get('latency_mean_ms',0):>10.4f} {r.get('latency_p99_ms',0):>10.4f} "
              f"{per_room:>14.5f} {r.get('engine_size_mb',0):>10.2f}")
    
    print("\nPipeline (sequential rooms):")
    print(f"  {'Rooms':>5} {'QPS':>10} {'Mean(ms)':>10} {'P99(ms)':>10} {'Per-room(ms)':>14} {'Engine(MB)':>10}")
    pipe = [r for r in results if r.get('mode') == 'pipeline']
    for r in sorted(pipe, key=lambda x: x.get('num_rooms', 0)):
        per_room = r.get('latency_mean_ms', 0) / r.get('num_rooms', 1)
        print(f"  {r['num_rooms']:>5} {r.get('throughput_qps',0):>10.0f} "
              f"{r.get('latency_mean_ms',0):>10.4f} {r.get('latency_p99_ms',0):>10.4f} "
              f"{per_room:>14.5f} {r.get('engine_size_mb',0):>10.2f}")
    
    # Key insight
    print("\n--- KEY INSIGHT ---")
    if batch:
        single = next((r for r in batch if r['num_rooms'] == 1), None)
        big = next((r for r in batch if r['num_rooms'] == max(r['num_rooms'] for r in batch)), None)
        if single and big:
            scaling = big.get('throughput_qps', 0) / single.get('throughput_qps', 1)
            print(f"Batch scaling: {big['num_rooms']}x batch = {scaling:.2f}x throughput vs 1x")
            print(f"Per-room cost drops from {single.get('latency_mean_ms',0):.4f}ms to "
                  f"{big.get('latency_mean_ms',0)/big['num_rooms']:.5f}ms")
    
    with open(os.path.join(OUT_DIR, "batch_pipeline_summary.json"), 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved: {OUT_DIR}/batch_pipeline_summary.json")


if __name__ == "__main__":
    main()
