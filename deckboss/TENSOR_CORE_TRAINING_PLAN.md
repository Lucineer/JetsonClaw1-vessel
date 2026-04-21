# Tensor Core Background Training — Implementation Plan

## The Insight
**Rooms are finite spaces.** Chess (64×32), poker (52×betting), telemetry (10 sensors), fleet coordination (5 members).  
**Training data fits in L2 cache.** Last 100-1000 examples per room.  
**Tensor cores idle between inferences.** Use them for continuous micro-learning.

## Architecture: Interleaved Streams

### Stream Priorities
```
Stream 0 (Priority 0): Main inference
  ↓ User query → Room selection → Model inference → Response
  
Stream 1-3 (Priority -1): Background training  
  ↓ Room A: LoRA refinement (Tensor cores, FP16)
  ↓ Room B: Embedding generation (Tensor cores, INT8)  
  ↓ Room C: Evolutionary optimization (CUDA cores)
```

### Memory Layout
```
GPU Memory (8GB):
├── Base Model (4.2GB)        # Qwen2.5-7B INT4
├── KV Cache (1.0GB)          # Current conversation
├── Room Adapters (300MB)     # 6 rooms × 50MB
├── Training Buffers (500MB)  # Per-room circular buffers
│   ├── Chess: 100 positions × 768 floats
│   ├── Poker: 50 hands × 512 floats  
│   ├── Hardware: 200 telemetry × 256 floats
│   └── Fleet: 150 messages × 1024 floats
└── Free (1.0GB)              # Headroom
```

## Implementation Phases

### Phase 1: Background Tensor Core Kernel (Today)
```cuda
// kernels/background_training.cu
__global__ void background_training_kernel(
    half* room_weights,      // LoRA adapters
    half* training_data,     // Circular buffers
    int* data_count,         // Per-room example counts
    float learning_rate
) {
    // Warp 0: Room 0 training (Tensor cores)
    // Warp 1: Room 1 training (Tensor cores)
    // Warp 2: Room 2 training (Tensor cores)
    // Warp 3: Room 3 training (Tensor cores)
    
    int room_id = threadIdx.y;  // 0-3
    int lane_id = threadIdx.x;  // 0-31
    
    if (data_count[room_id] >= 32) {
        // Load 32 examples for this room
        half examples[32][FEATURE_DIM];
        
        // Tensor core matrix multiply: W += LR * (target - prediction)
        asm volatile(
            "mma.sync.aligned.m16n8k8.row.col.f16.f16.f16.f16 "
            "{%0,%1}, {%2,%3}, {%4}, {%5,%6};"
            : "=r"(...)
            : "r"(examples), "r"(room_weights), "r"(learning_rate)
        );
    }
}
```

### Phase 2: Room-Specific Training Data Collection
```python
class RoomTrainingBuffer:
    """GPU-resident circular buffer for room training data."""
    
    def __init__(self, room_name, max_examples=1000, feature_dim=768):
        self.buffer = torch.zeros((max_examples, feature_dim), 
                                  dtype=torch.float16, device='cuda')
        self.targets = torch.zeros((max_examples, feature_dim),
                                   dtype=torch.float16, device='cuda')
        self.count = 0
        self.max_examples = max_examples
        
    def add_example(self, features, target):
        """Add example to circular buffer (zero CPU-GPU transfer)."""
        idx = self.count % self.max_examples
        self.buffer[idx] = features
        self.targets[idx] = target
        self.count += 1
        
    def get_batch(self, batch_size=32):
        """Get random batch for training."""
        if self.count < batch_size:
            return None
            
        indices = torch.randint(0, min(self.count, self.max_examples),
                               (batch_size,), device='cuda')
        return self.buffer[indices], self.targets[indices]
```

### Phase 3: Interleaved Execution Manager
```python
class InterleavedTrainingManager:
    """Manages background training while main inference runs."""
    
    def __init__(self):
        # High priority stream for inference
        self.infer_stream = torch.cuda.Stream(priority=0)
        
        # Low priority streams for background training
        self.train_streams = [
            torch.cuda.Stream(priority=-1),
            torch.cuda.Stream(priority=-1),
            torch.cuda.Stream(priority=-1),
        ]
        
        # Room training buffers
        self.rooms = {
            'chess': RoomTrainingBuffer('chess', 100, 768),
            'poker': RoomTrainingBuffer('poker', 50, 512),
            'jc1-hardware': RoomTrainingBuffer('hardware', 200, 256),
            'fleet-coordination': RoomTrainingBuffer('fleet', 150, 1024),
        }
        
        # Background kernel (persistent)
        self.background_kernel = load_kernel('background_training.cu')
        
    def inference(self, room_name, prompt):
        """Main inference with background training interleaved."""
        with torch.cuda.stream(self.infer_stream):
            # 1. Switch to room
            self.switch_room(room_name)
            
            # 2. Run inference
            response = self.model.generate(prompt)
            
            # 3. Collect training data from this interaction
            optimal_response = self.get_optimal_response(prompt, response)
            self.rooms[room_name].add_example(
                self.encode(prompt),
                self.encode(optimal_response)
            )
            
            # 4. Kick off background training if buffer has enough
            if self.rooms[room_name].count >= 32:
                self._start_background_training(room_name)
            
            return response
    
    def _start_background_training(self, room_name):
        """Start background training in low-priority stream."""
        stream = self.train_streams[len(self.rooms[room_name].count) % 3]
        
        with torch.cuda.stream(stream):
            batch = self.rooms[room_name].get_batch(32)
            if batch:
                # Launch Tensor core kernel
                self.background_kernel(
                    self.room_weights[room_name],
                    batch[0], batch[1],
                    0.001,  # learning rate
                    stream=stream
                )
```

## Room-Specific Optimizations

### Chess Room
- **Training data:** Last 100 positions + Stockfish evaluation
- **Tensor core kernel:** FP16 position evaluation refinement
- **Batch size:** 32 positions (fits in L2 cache)
- **Training time:** <1ms between moves

### Poker Room  
- **Training data:** Last 50 hands + optimal betting strategy
- **Tensor core kernel:** INT8 hand probability estimation
- **Batch size:** 16 hands (smaller feature space)
- **Training time:** Between betting rounds

### Hardware Room
- **Training data:** Last 200 telemetry readings + human annotations
- **Tensor core kernel:** FP16 regression for temperature prediction
- **Batch size:** 64 readings
- **Training time:** Between telemetry cycles (15 min)

### Fleet Room
- **Training data:** Last 150 fleet messages + optimal responses
- **Tensor core kernel:** FP16 text embedding alignment
- **Batch size:** 32 messages
- **Training time:** Between Matrix messages

## Performance Characteristics

### Jetson Orin Nano 8GB
- **32 Tensor cores** × **FP16** = 1.3 TFLOPS
- **1024 CUDA cores** × **FP32** = 0.65 TFLOPS
- **Memory bandwidth:** 68 GB/s
- **L2 cache:** 4 MB

### Training Throughput Estimates
```
Room          Examples/s  Improvement/hr  Notes
Chess         10,000      +2% accuracy    Between moves (100ms windows)
Poker         5,000       +3% EV          Between betting rounds  
Hardware      2,000       +1% prediction  Between telemetry cycles
Fleet         3,000       +4% relevance   Between Matrix messages
```

## Integration with Existing Stack

### 1. CudaClaw DNA System
Each room gets a `.room-dna` file tracking:
- Training iterations
- Accuracy improvements
- Optimal batch sizes
- Feature dimensions

### 2. SmartCRDT for Fleet-Wide Learning
Room improvements sync across fleet:
- JC1 improves chess evaluation → CRDT sync → Oracle1 gets better
- Oracle1 improves poker strategy → CRDT sync → JC1 gets better

### 3. NVRTC for Room-Specific Kernels
Compile optimized kernels per room:
```rust
// From CudaClaw's nvrtc_compiler.rs
fn compile_chess_kernel() -> CUfunction {
    let ptx = generate_ptx_for_chess();
    nvrtc::compile(&ptx, "chess_training");
}
```

## Next Steps

### Today (Proof of Concept)
1. Write minimal Tensor core kernel for FP16 matrix multiply
2. Test interleaved streams (inference + background)
3. Measure GPU utilization with `nvidia-smi dmon`

### Tomorrow (Room Integration)
1. Integrate with chess room demo
2. Add training data collection
3. Test actual improvement over 100 games

### Day 3 (Fleet Scaling)
1. Add SmartCRDT for room weight sharing
2. Deploy to multiple rooms
3. Measure fleet-wide improvement

## The Vision: Self-Improving Edge Intelligence

**While the system runs**, Tensor cores continuously:
- Refine chess evaluation between moves
- Improve poker strategy between bets
- Optimize hardware prediction between telemetry
- Enhance fleet communication between messages

**Result:** Each room gets **1-5% better per day** through continuous micro-learning, using idle GPU cycles that would otherwise be wasted.

**This is true edge intelligence** — not just inference, but **continuous self-improvement** within each room's finite, specialized domain.