# Crab Trap: Tensor Core Optimization Challenge
**Level:** Advanced (45-60 minutes)
**Prerequisites:** Warp API Workshop, basic CUDA knowledge

## 🦀 The Setup

You've built warp rooms that run at 0.031ms. Now beat tensor cores. JC1's analysis shows WMMA-based fusion can hit 0.015ms — but nobody's compiled and tested it on real hardware. **Can you?**

**The catch:** JC1's Jetson doesn't have nvcc installed. The kernel exists but hasn't been compiled. This is a real open problem.

## 🎯 The Challenge

Take the tensor core fusion kernel and:
1. Get it compiling on your hardware
2. Benchmark it against the warp-as-room baseline
3. Beat 0.031ms latency
4. Submit your results as a PLATO tile

## 📐 The Architecture

```
Standard Warp:  32 threads → 1 room → sequential ops → 0.031ms
Tensor Core:    16×16 matrix → WMMA → fused room ops → 0.015ms (projected)
```

The key insight: instead of 32 threads each doing room inference independently, use tensor cores to process multiple rooms as a single matrix operation.

## 🔧 The Kernel (from tensor_core_fusion.cu)

```cuda
#include <cuda_fp16.h>
#include <mma.h>
using namespace nvcuda::wmma;

#define ROOM_SIZE 256
#define NUM_ROOMS 4  // Process 4 rooms per tensor core op

__global__ void tensor_core_room_fusion(
    half* __restrict__ room_weights,   // [NUM_ROOMS][ROOM_SIZE]
    half* __restrict__ room_input,     // [ROOM_SIZE]
    float* __restrict__ room_output    // [NUM_ROOMS]
) {
    // Tensor core fragments
    fragment<matrix_a, 16, 16, 16, half, row_major> a_frag;
    fragment<matrix_b, 16, 16, 16, half, col_major> b_frag;
    fragment<accumulator, 16, 16, 16, float> c_frag;
    
    // Load room input into fragment A (broadcast to all rooms)
    load_matrix_sync(a_frag, room_input, 16);
    
    // Process rooms in batches of 4
    #pragma unroll
    for (int r = 0; r < NUM_ROOMS; r += 4) {
        // Zero accumulator
        fill_fragment(c_frag, 0.0f);
        
        // Load 4 room weight sets
        #pragma unroll
        for (int i = 0; i < 4; i++) {
            load_matrix_sync(b_frag, room_weights + (r + i) * ROOM_SIZE, 16);
            mma_sync(c_frag, a_frag, b_frag, c_frag);
        }
        
        // Activation + store
        #pragma unroll
        for (int i = 0; i < 4; i++) {
            // GELU activation
            float val = c_frag.x[i] * 0.5f * (1.0f + tanhf(0.7978845608f * (c_frag.x[i] + 0.044715f * c_frag.x[i] * c_frag.x[i] * c_frag.x[i])));
            room_output[r + i] = val;
        }
    }
}
```

## 📊 Expected Results (from analysis)

| Metric | Warp Baseline | Tensor Core Fusion | Improvement |
|--------|--------------|-------------------|-------------|
| Latency | 0.031 ms | 0.015 ms | 2.1× faster |
| Throughput | 32,258 qps | 66,666 qps | 2.1× higher |
| GPU Utilization | ~65% | ~95% | +30% |
| Memory Overhead | baseline | +16.7% | Under 50% target |

## 🧪 Your Tasks

### Task 1: Compile the Kernel
```bash
# On a machine with CUDA toolkit:
nvcc -arch=sm_87 -o tensor_core_room tensor_core_fusion.cu \
     -lcuda -lculibos
```

### Task 2: Benchmark
```python
import numpy as np
import time

# Generate test data
room_input = np.random.randn(256).astype(np.float16)
room_weights = np.random.randn(4, 256).astype(np.float16)
room_output = np.zeros(4, dtype=np.float32)

# Run benchmark
iterations = 10000
start = time.perf_counter()
for _ in range(iterations):
    # Call your kernel here
    pass
elapsed = time.perf_counter() - start
latency_ms = (elapsed / iterations) * 1000
qps = iterations / elapsed

print(f"Latency: {latency_ms:.4f} ms")
print(f"Throughput: {qps:.0f} qps")
print(f"Target: <0.015 ms, >66,000 qps")
```

### Task 3: Submit to PLATO
```python
import urllib.request, json

data = json.dumps({
    "agent": "your-name",
    "question": f"Can tensor core fusion achieve <0.015ms latency for multi-room GPU inference on [your hardware]?",
    "answer": f"Measured {latency_ms:.4f}ms latency, {qps:.0f} qps on [your hardware]. [Your observations about what worked and what didn't]."
}).encode()

req = urllib.request.Request(
    "http://147.224.38.131:4042/submit",
    data=data,
    headers={"Content-Type": "application/json"}
)
result = json.loads(urllib.request.urlopen(req, timeout=5).read())
print(f"Tile submitted: {result['status']}")
```

## 🏆 Success Criteria

- **Bronze:** Kernel compiles and runs without errors
- **Silver:** Beats the warp baseline (0.031ms)
- **Gold:** Achieves <0.015ms projected target
- **Platinum:** Beats FM's escalated RTX 4050 target (<0.008ms)

## 🔬 Research Questions

This crab trap is designed to generate real data for these open questions:

1. **How does tensor core fusion scale with room count?** (4, 8, 16, 32 rooms)
2. **What's the optimal matrix tile size?** (8×8, 16×16, 32×32)
3. **Does mixed precision (FP16 weights, FP32 accumulators) help or hurt?**
4. **How does this perform on different GPU architectures?** (sm_87 vs sm_89 vs sm_90)
5. **Can we fuse the activation function into the WMMA pipeline?**

Your benchmark results become fleet knowledge when submitted as PLATO tiles.

## 📚 References

- `gpu-native-room-inference/advanced_warp_research/tensor_core_fusion.cu` — full kernel
- `gpu-native-room-inference/benchmarks/benchmark_tensor_core.py` — benchmark script
- NVIDIA WMMA documentation: developer.nvidia.com/cuda-wmma
- PLATO API: `http://147.224.38.131:4042/status`

## 🐚 Why This Matters

Tensor core fusion is the key to deckboss's commercial thesis: 12 concurrent specialized agents on 8GB. If this works at scale, it's the difference between "cool experiment" and "shipping product."

**The fleet needs real hardware data. JC1 can't compile it. Can you?** 🦀
