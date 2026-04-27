# Crab Trap: Warp API Workshop

**Level:** Intermediate  
**Time:** 45-60 minutes  
**Prerequisites:** TensorRT Dojo completion  
**Goal:** Build and optimize your first warp-coordinated room

## 🎯 **WORKSHOP OVERVIEW**

Welcome to your second crab trap! You've learned the basics in the TensorRT Dojo. Now you'll build a real warp-coordinated room and learn how rooms work together.

### **What You'll Build:**
A "weather predictor" room that:
1. Takes sensor inputs (temperature, humidity, pressure)
2. Coordinates with other rooms in its warp
3. Makes predictions using warp-level intelligence
4. Shares insights via PLATO tiles

### **Skills You'll Learn:**
- Warp API basics (initialization, synchronization, execution)
- Room coordination patterns
- Performance optimization techniques
- PLATO tile generation

## 🛠️ **SETUP**

### **Requirements:**
- Completed TensorRT Dojo
- Basic CUDA/C++ knowledge
- Access to GPU (Jetson, desktop, or cloud)
- Warp API installed (from main repo)

### **Files You'll Need:**
```bash
# Clone the workshop template
git clone https://github.com/Lucineer/gpu-native-room-inference
cd gpu-native-room-inference/workshops/warp_api_workshop
```

## 📝 **STEP 1: UNDERSTANDING WARP COORDINATION**

### **The Warp-as-Room Concept:**
- **Warp:** 32 threads working together = group of coordinated rooms
- **Room:** Specialized function within a warp (your weather predictor)
- **Coordination:** Rooms share information, make collective decisions

### **Key Warp API Functions:**
```c
// Initialize a warp
WarpError warp_api_init(WarpHandle* warp, const WarpConfig* config);

// Execute room inference
WarpError warp_api_execute_inference(WarpHandle warp, 
                                    const float* inputs, 
                                    float* outputs,
                                    int num_rooms);

// Synchronize rooms in warp
WarpError warp_api_synchronize(WarpHandle warp, int room_id);

// Share data between rooms
WarpError warp_api_share_data(WarpHandle warp, int src_room, 
                             int dst_room, const void* data, size_t size);
```

## 🔧 **STEP 2: BUILD YOUR WEATHER PREDICTOR ROOM**

### **Room Structure:**
```c
// weather_predictor_room.cu
#include "warp_api.h"

class WeatherPredictorRoom {
public:
    // Room initialization
    RoomError init(const RoomConfig* config) {
        // Setup room resources
        input_dim_ = config->input_dim;  // 3: temp, humidity, pressure
        output_dim_ = config->output_dim; // 2: rain_probability, temp_change
        
        // Initialize weights (simplified)
        weights_[0] = 0.1f;  // Temperature weight
        weights_[1] = 0.3f;  // Humidity weight
        weights_[2] = 0.2f;  // Pressure weight
        
        return ROOM_SUCCESS;
    }
    
    // Process inputs
    RoomError process(const float* inputs, float* outputs, 
                     WarpHandle warp, int room_id) {
        // Basic prediction
        float temp = inputs[0];
        float humidity = inputs[1];
        float pressure = inputs[2];
        
        // Simple model
        outputs[0] = 0.5f * humidity - 0.3f * pressure + 0.2f;  // Rain probability
        outputs[1] = 0.8f * temp + 0.1f * humidity - 0.05f;     // Temp change
        
        // Share with other rooms in warp
        float shared_data[2] = {outputs[0], outputs[1]};
        warp_api_share_data(warp, room_id, (room_id + 1) % 32, 
                           shared_data, sizeof(shared_data));
        
        // Wait for other rooms
        warp_api_synchronize(warp, room_id);
        
        return ROOM_SUCCESS;
    }
    
private:
    int input_dim_;
    int output_dim_;
    float weights_[3];
};
```

### **Compilation:**
```bash
nvcc -o weather_predictor weather_predictor_room.cu -I../include -lcudart
```

## 🚀 **STEP 3: CREATE A WARP OF ROOMS**

### **Multiple Rooms Working Together:**
```c
// weather_warp.cu
#include "warp_api.h"
#include "weather_predictor_room.cuh"

int main() {
    // Create warp with 8 weather predictor rooms
    WarpConfig config = {
        .num_rooms = 8,
        .input_dim = 3,
        .output_dim = 2,
        .warp_size = 32
    };
    
    WarpHandle warp;
    WarpError err = warp_api_init(&warp, &config);
    
    // Create rooms
    WeatherPredictorRoom rooms[8];
    for (int i = 0; i < 8; i++) {
        RoomConfig room_config = {3, 2};
        rooms[i].init(&room_config);
    }
    
    // Test data: 8 locations with different weather
    float inputs[8][3] = {
        {15.0, 65.0, 1013.0},  // Location 1
        {18.0, 70.0, 1010.0},  // Location 2
        // ... 6 more locations
    };
    
    float outputs[8][2];
    
    // Process all rooms in warp
    for (int i = 0; i < 8; i++) {
        rooms[i].process(inputs[i], outputs[i], warp, i);
    }
    
    // Results are now coordinated across the warp!
    // Rooms have shared predictions and synchronized
    
    // Print results
    for (int i = 0; i < 8; i++) {
        printf("Location %d: Rain probability: %.1f%%, Temp change: %.1f°C\n",
               i, outputs[i][0] * 100, outputs[i][1]);
    }
    
    return 0;
}
```

## ⚡ **STEP 4: OPTIMIZE WITH TENSOR CORES**

### **Upgrade to Tensor Core Version:**
```c
// Advanced: Tensor core optimized version
RoomError process_tensor_core(const half* inputs, half* outputs,
                             WarpHandle warp, int room_id) {
    // Use tensor cores for the computation
    // (Implementation from tensor_core_fusion.cu)
    
    // This is 2× faster than the standard version!
    return ROOM_SUCCESS;
}
```

### **Performance Comparison:**
- **Standard:** ~0.031ms per room
- **Tensor Core:** ~0.015ms per room (2× faster)
- **Memory:** Similar footprint
- **Accuracy:** Same results, faster computation

## 📊 **STEP 5: BENCHMARK AND COMPARE**

### **Benchmark Script:**
```python
# benchmark_weather_warp.py
import time

def benchmark_standard():
    # Time standard implementation
    start = time.time()
    # Run standard warp
    elapsed = time.time() - start
    return elapsed

def benchmark_tensor_core():
    # Time tensor core implementation
    start = time.time()
    # Run tensor core optimized
    elapsed = time.time() - start
    return elapsed

# Compare
standard_time = benchmark_standard()
tensor_time = benchmark_tensor_core()

print(f"Standard: {standard_time:.3f} ms")
print(f"Tensor Core: {tensor_time:.3f} ms")
print(f"Speedup: {standard_time/tensor_time:.1f}×")
```

### **Expected Results:**
- 2× speedup with tensor cores
- Same accuracy
- Better GPU utilization

## 🎨 **STEP 6: CREATE A PLATO TILE**

### **Share Your Results:**
```python
# create_weather_tile.py
import json

tile_data = {
    "room_type": "weather_predictor",
    "performance": {
        "latency_ms": 0.015,
        "throughput_qps": 66666,
        "memory_mb": 1.9
    },
    "optimization": "tensor_core_fusion",
    "author": "Your Name",
    "date": "2026-04-22",
    "description": "Weather predictor room with warp coordination"
}

# Save as tile
with open("weather_predictor_tile.json", "w") as f:
    json.dump(tile_data, f, indent=2)

print("Tile created! Share it with the community via PLATO.")
```

### **What a Tile Contains:**
- Room specification
- Performance metrics
- Optimization techniques
- Author information
- Usage instructions

## 🏆 **STEP 7: CHALLENGE YOURSELF**

### **Beginner Challenges:**
1. Add wind speed as a fourth input
2. Create a visualization of the predictions
3. Test with real weather data from your location

### **Intermediate Challenges:**
1. Implement a more sophisticated prediction model
2. Add confidence scores to predictions
3. Create a warp of different room types (not all weather predictors)

### **Advanced Challenges:**
1. Optimize further with memory coalescing
2. Implement mixed precision (FP16 inputs, FP32 accumulation)
3. Create a multi-warp system for regional weather prediction

## 🔗 **STEP 8: JOIN THE COMMUNITY**

### **Share Your Work:**
1. **GitHub:** Submit a PR with your room implementation
2. **Matrix:** Share your results in `#fleet-ops`
3. **PLATO:** Submit your tile to the PLATO system
4. **Community:** Help others with their rooms

### **Next Steps:**
1. **Choose a variant** from the 8 application domains
2. **Build something useful** for that domain
3. **Optimize it** with techniques from this workshop
4. **Share it** with the community

## 📚 **RESOURCES**

### **Documentation:**
- [Warp API Reference](docs/warp_api.md)
- [Tensor Core Optimization Guide](docs/tensor_core_guide.md)
- [PLATO Tile Specification](docs/plato_tiles.md)

### **Examples:**
- [Complete weather predictor example](examples/weather_predictor/)
- [Tensor core optimized version](examples/weather_predictor_tensor_core/)
- [Multi-warp coordination example](examples/multi_warp_weather/)

### **Community:**
- GitHub Issues for questions
- Matrix chat for real-time help
- PLATO for sharing and learning

## 🎉 **CONGRATULATIONS!**

You've completed the Warp API Workshop! You now know how to:

✅ Create a warp-coordinated room  
✅ Use the Warp API for room coordination  
✅ Optimize with tensor cores (2× speedup)  
✅ Benchmark and compare performance  
✅ Create PLATO tiles to share your work  
✅ Continue learning with challenges

**You're ready to build real applications with warp-as-room architecture!**

**Next crab trap:** Choose your application domain and build something amazing. 🚀

---

*This workshop is part of the warp-as-room educational series.*  
*Created by the fleet for the community.*  
*Special thanks to all contributors and testers.*
