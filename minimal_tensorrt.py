#!/usr/bin/env python3
"""
minimal_tensorrt.py

Minimal working TensorRT example for Jetson.
Builds a simple engine that actually works.
"""

import tensorrt as trt
import numpy as np
import os
from pathlib import Path

def build_minimal_engine():
    """Build a minimal TensorRT engine that actually works."""
    print("Building minimal TensorRT engine...")
    
    # Initialize
    TRT_LOGGER = trt.Logger(trt.Logger.WARNING)
    builder = trt.Builder(TRT_LOGGER)
    network = builder.create_network(1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH))
    
    # Simple input: 1x3x224x224 (batch=1, channels=3, height=224, width=224)
    input_tensor = network.add_input(
        name="input",
        dtype=trt.float32,
        shape=trt.Dims4(1, 3, 224, 224)  # NCHW
    )
    
    # Add a simple convolution (this should work)
    # Create weights for 3x3 convolution, 3 input channels, 16 output channels
    kernel_weights = np.random.randn(16, 3, 3, 3).astype(np.float32).flatten()
    
    conv_layer = network.add_convolution_nd(
        input=input_tensor,
        num_output_maps=16,
        kernel_shape=trt.DimsHW(3, 3),
        kernel=trt.Weights(kernel_weights),
        bias=trt.Weights()
    )
    conv_layer.stride_nd = trt.DimsHW(1, 1)
    conv_layer.padding_nd = trt.DimsHW(1, 1)
    
    # Add ReLU activation
    relu_layer = network.add_activation(
        input=conv_layer.get_output(0),
        type=trt.ActivationType.RELU
    )
    
    # Mark output
    relu_layer.get_output(0).name = "output"
    network.mark_output(relu_layer.get_output(0))
    
    # Build configuration
    config = builder.create_builder_config()
    config.set_memory_pool_limit(trt.MemoryPoolType.WORKSPACE, 64 * 1024 * 1024)  # 64MB
    
    # Try to build
    print("  Building engine...")
    try:
        serialized_engine = builder.build_serialized_network(network, config)
        
        if serialized_engine is None:
            print("  ❌ Engine building failed")
            return None
        
        # Save engine
        engine_dir = Path("/tmp/minimal_tensorrt")
        engine_dir.mkdir(exist_ok=True)
        
        engine_file = engine_dir / "minimal_engine.trt"
        with open(engine_file, 'wb') as f:
            f.write(serialized_engine)
        
        engine_size = os.path.getsize(engine_file)
        print(f"  ✓ Engine saved: {engine_file} ({engine_size:,} bytes)")
        
        return engine_file
        
    except Exception as e:
        print(f"  ❌ Build error: {e}")
        return None

def test_if_tensorrt_works():
    """Test if TensorRT basic functionality works."""
    print("\n" + "="*60)
    print("TESTING TENSORRT BASIC FUNCTIONALITY")
    print("="*60)
    
    # Test 1: Import and version
    print("1. TensorRT import test:")
    print(f"   Version: {trt.__version__}")
    print("   ✅ Import successful")
    
    # Test 2: Logger creation
    print("\n2. Logger test:")
    logger = trt.Logger(trt.Logger.WARNING)
    print("   ✅ Logger created")
    
    # Test 3: Builder creation
    print("\n3. Builder test:")
    builder = trt.Builder(logger)
    print(f"   Builder created: {builder}")
    print("   ✅ Builder successful")
    
    # Test 4: Check FP16 support
    print("\n4. Hardware capabilities:")
    if builder.platform_has_fast_fp16:
        print("   ✅ FP16 supported (Tensor cores available)")
    else:
        print("   ⚠️ FP16 not supported")
    
    if builder.platform_has_fast_int8:
        print("   ✅ INT8 supported")
    else:
        print("   ⚠️ INT8 not supported")
    
    # Test 5: Try to build minimal engine
    print("\n5. Minimal engine build test:")
    engine_file = build_minimal_engine()
    
    if engine_file:
        print(f"   ✅ Minimal engine built: {engine_file}")
        
        # Try to load it back
        print("\n6. Engine loading test:")
        try:
            with open(engine_file, 'rb') as f:
                runtime = trt.Runtime(logger)
                engine = runtime.deserialize_cuda_engine(f.read())
            
            if engine:
                print(f"   ✅ Engine loaded successfully")
                print(f"   Bindings: {engine.num_bindings}")
                print(f"   Layers: {engine.num_layers}")
                
                # Check input/output
                for i in range(engine.num_bindings):
                    name = engine.get_binding_name(i)
                    shape = engine.get_binding_shape(i)
                    dtype = engine.get_binding_dtype(i)
                    print(f"   Binding {i}: {name}, shape={shape}, dtype={dtype}")
            else:
                print("   ❌ Failed to load engine")
                
        except Exception as e:
            print(f"   ❌ Load error: {e}")
    else:
        print("   ❌ Minimal engine build failed")
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    if engine_file and os.path.exists(engine_file):
        print("✅ TensorRT is WORKING on Jetson")
        print("✅ Can build and load engines")
        print("✅ Ready for room engine implementation")
    else:
        print("⚠️ TensorRT has issues")
        print("⚠️ Need to debug engine building")
        print("⚠️ May need to use ONNX → TensorRT path")

def check_available_tools():
    """Check what TensorRT tools are available."""
    print("\n" + "="*60)
    print("CHECKING AVAILABLE TENSORRT TOOLS")
    print("="*60)
    
    # Check common TensorRT tools
    tools = [
        "trtexec",
        "polygraphy",
        "onnx2trt",
        "trt"
    ]
    
    for tool in tools:
        result = os.system(f"which {tool} >/dev/null 2>&1")
        if result == 0:
            print(f"✅ {tool} is available")
        else:
            print(f"❌ {tool} not found")
    
    # Check Python packages
    print("\nPython packages:")
    try:
        import onnx
        print(f"✅ ONNX: {onnx.__version__}")
    except:
        print("❌ ONNX not installed")
    
    try:
        import pycuda
        print(f"✅ pycuda: available")
    except:
        print("❌ pycuda not installed")
    
    print("\n" + "="*60)
    print("RECOMMENDATION")
    print("="*60)
    print("For room engines, we should:")
    print("1. Create simple ONNX models for each room")
    print("2. Use trtexec to convert ONNX → TensorRT")
    print("3. Load .trt engines in Python")
    print("4. Integrate with PLATO rooms")

if __name__ == "__main__":
    test_if_tensorrt_works()
    check_available_tools()