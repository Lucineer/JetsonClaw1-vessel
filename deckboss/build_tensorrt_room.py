#!/usr/bin/env python3
"""
deckboss/build_tensorrt_room.py

Build TensorRT engine from room YAML definition.
Native Jetson optimization, no PyTorch dependency.

Usage:
  python3 build_tensorrt_room.py --room chess.yaml --output chess.trt
"""

import yaml
import tensorrt as trt
import numpy as np
from pathlib import Path
import argparse

class TensorRTRoomBuilder:
    """Build TensorRT engine from room definition."""
    
    def __init__(self, precision="fp16"):
        self.logger = trt.Logger(trt.Logger.WARNING)
        self.builder = trt.Builder(self.logger)
        self.config = self.builder.create_builder_config()
        self.precision = precision
        
        # Set precision flags
        if precision == "fp16":
            self.config.set_flag(trt.BuilderFlag.FP16)
            print("Using FP16 precision (Tensor core optimized)")
        elif precision == "int8":
            self.config.set_flag(trt.BuilderFlag.INT8)
            print("Using INT8 precision (20 TOPS on Jetson)")
        
        # Jetson-specific optimization
        self.config.set_memory_pool_limit(
            trt.MemoryPoolType.WORKSPACE, 
            64 * 1024 * 1024  # 64MB workspace
        )
    
    def build_from_yaml(self, yaml_path, output_path):
        """Build TensorRT engine from room YAML."""
        print(f"Building room from: {yaml_path}")
        
        # Load room definition
        with open(yaml_path, 'r') as f:
            room = yaml.safe_load(f)
        
        print(f"Room: {room['name']}")
        print(f"Description: {room.get('description', 'No description')}")
        
        # Create network
        network = self.builder.create_network(
            1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH)
        )
        
        # Parse room architecture
        input_shape = room['architecture']['input_shape']
        output_shape = room['architecture']['output_shape']
        layers = room['architecture'].get('layers', [])
        
        print(f"Input shape: {input_shape}")
        print(f"Output shape: {output_shape}")
        print(f"Layers: {len(layers)}")
        
        # Add input
        input_tensor = network.add_input(
            "input", 
            trt.DataType.FLOAT, 
            input_shape
        )
        
        current_tensor = input_tensor
        
        # Add layers (simplified - real would parse layer definitions)
        for i, layer in enumerate(layers):
            layer_type = layer['type']
            
            if layer_type == "fully_connected":
                # Add fully connected layer
                weights = np.random.randn(
                    layer['input_dim'], 
                    layer['output_dim']
                ).astype(np.float32)
                
                bias = np.zeros(layer['output_dim']).astype(np.float32)
                
                weights_const = network.add_constant(
                    weights.shape, 
                    trt.Weights(weights)
                )
                bias_const = network.add_constant(
                    bias.shape, 
                    trt.Weights(bias)
                )
                
                matmul = network.add_matrix_multiply(
                    current_tensor, trt.MatrixOperation.NONE,
                    weights_const.get_output(0), trt.MatrixOperation.NONE
                )
                
                add_bias = network.add_elementwise(
                    matmul.get_output(0),
                    bias_const.get_output(0),
                    trt.ElementWiseOperation.SUM
                )
                
                current_tensor = add_bias.get_output(0)
                
                # Add activation if specified
                if layer.get('activation') == 'relu':
                    relu = network.add_activation(
                        current_tensor,
                        trt.ActivationType.RELU
                    )
                    current_tensor = relu.get_output(0)
                
                print(f"  Layer {i}: FC {layer['input_dim']}→{layer['output_dim']}")
            
            elif layer_type == "convolution":
                # Add convolution layer (for vision rooms)
                print(f"  Layer {i}: Conv (simulated)")
                # Simplified for demo
        
        # Mark output
        current_tensor.name = "output"
        network.mark_output(current_tensor)
        
        # Build engine
        print("Building TensorRT engine...")
        engine = self.builder.build_engine(network, self.config)
        
        if engine is None:
            print("Failed to build engine")
            return False
        
        # Serialize engine to file
        print(f"Serializing to: {output_path}")
        with open(output_path, 'wb') as f:
            f.write(engine.serialize())
        
        print(f"Engine built successfully: {output_path}")
        print(f"Engine size: {Path(output_path).stat().st_size / 1024:.1f} KB")
        
        return True
    
    def build_simple_room(self, room_name, input_dim, output_dim, output_path):
        """Build a simple room for testing."""
        # Create a simple YAML-like structure
        room = {
            'name': room_name,
            'description': f'Simple {room_name} room',
            'architecture': {
                'input_shape': (1, input_dim),
                'output_shape': (1, output_dim),
                'layers': [
                    {
                        'type': 'fully_connected',
                        'input_dim': input_dim,
                        'output_dim': output_dim,
                        'activation': 'relu'
                    }
                ]
            }
        }
        
        # Save temporary YAML
        temp_yaml = f"/tmp/{room_name}.yaml"
        with open(temp_yaml, 'w') as f:
            yaml.dump(room, f)
        
        # Build from YAML
        return self.build_from_yaml(temp_yaml, output_path)


def main():
    parser = argparse.ArgumentParser(description='Build TensorRT room engine')
    parser.add_argument('--room', help='Room YAML file')
    parser.add_argument('--output', help='Output .trt file')
    parser.add_argument('--precision', choices=['fp16', 'int8', 'fp32'], 
                       default='fp16', help='Precision (default: fp16)')
    parser.add_argument('--demo', action='store_true', 
                       help='Build demo rooms')
    
    args = parser.parse_args()
    
    builder = TensorRTRoomBuilder(precision=args.precision)
    
    if args.demo:
        print("Building demo rooms...")
        
        demo_rooms = [
            ('chess', 768, 768),
            ('poker', 512, 512),
            ('jc1-hardware', 256, 256),
            ('fleet-coordination', 1024, 1024),
        ]
        
        for name, input_dim, output_dim in demo_rooms:
            output_path = f"/tmp/{name}.trt"
            print(f"\nBuilding {name} room...")
            builder.build_simple_room(name, input_dim, output_dim, output_path)
        
        print("\nDemo rooms built in /tmp/")
        
    elif args.room and args.output:
        builder.build_from_yaml(args.room, args.output)
    else:
        print("Error: Specify --room and --output, or use --demo")
        parser.print_help()


if __name__ == "__main__":
    main()