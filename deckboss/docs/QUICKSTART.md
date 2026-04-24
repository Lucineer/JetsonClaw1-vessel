# DeckBoss Quickstart — First 5 Minutes

## What is DeckBoss?
DeckBoss is a Tensor Core inference engine for Jetson Orin. It runs "rooms" — 
specialized AI models loaded as TensorRT engines — with minimal latency and 
maximum GPU utilization.

## Prerequisites
- Jetson Orin (Nano, AGX, or Super) with JetPack 6.x
- CUDA 12.x (`nvcc --version`)
- 8GB+ unified RAM

## Install

```bash
# Clone and build
git clone https://github.com/Lucineer/deckboss.git
cd deckboss
make jetson

# Install
sudo make install
# Installs to: /opt/deckboss/{bin,lib,rooms,include}
```

## Your First Room

Rooms are the core abstraction. Each room is a TensorRT engine file (`.trt`) 
that encapsulates a single AI model.

### Option A: Use a pre-built room
```bash
# Download a room from the fleet registry
deckboss pull chess-room

# Verify it loaded
deckboss list
```

### Option B: Build from a model
```bash
# Convert ONNX → TensorRT engine
deckboss build --model my-model.onnx --output my-room.trt \
  --fp16 --workspace 512
```

## Run Your First Inference

```bash
# Interactive mode
deckboss run chess-room --input "What's the best opening move?"

# Or use the C API (see deckboss/runtime/example_infer.c)
deckboss infer chess-room < input_fp16.bin > output_fp16.bin
```

## Connect to PLATO Fleet

```bash
# Configure fleet endpoint
deckboss config set fleet.url http://147.224.38.131:8848
deckboss config set fleet.node jc1
deckboss config set fleet.rooms chess,poker,hardware

# Start as fleet node (runs 24/7)
systemctl --user enable --now deckboss
```

## Common Operations

```bash
# Check GPU health
deckboss status

# Monitor inference latency in real-time
deckboss monitor

# Load/unload rooms
deckboss load my-room.trt
deckboss unload my-room

# View logs
journalctl --user -u deckboss -f
```

## Performance Targets (Jetson Orin 8GB)

| Metric | Target | Notes |
|--------|--------|-------|
| Inference latency | <10ms | FP16, single room |
| Room switch | <1ms | CUDA stream priority change |
| GPU temp (sustained) | <55°C | Passive cooling sufficient |
| Memory per room | 128-512MB | FP16, depends on model size |
| Max concurrent rooms | 4-8 | 8GB shared CPU/GPU RAM |

## Troubleshooting

```bash
# "CUDA out of memory" — unload unused rooms
deckboss unload --all
deckboss load chess-room  # reload just what you need

# Slow inference — check clock speeds
deckboss status  # look for SM clock MHz

# High temperature — reduce concurrent rooms or add active cooling
```

## Next Steps
- Read the full API docs: `deckboss/runtime/deckboss.h`
- Build custom rooms from PyTorch/ONNX models
- Connect to PLATO fleet for distributed inference
- Read the systemd service guide: `deckboss/systemd/README.md`
