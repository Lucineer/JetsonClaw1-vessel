# flato — Fleet Plato MUD (C17) 🌐

**A minimal multi-agent MUD for fleet compute, deployed on port 4003.**

flato is the networking layer. edge-llama is the compute layer. Together they form the foundation of a distributed mesh compute protocol.

## Architecture (Live)

```
┌─────────────┐   Unix Socket    ┌──────────────────┐
│  flato MUD  │◄────────────────►│  edge-gateway    │
│  (C17)      │  /tmp/edge-      │  NativeInference │
│  telnet:    │  native.sock     │  daemon thread   │
│  4003       │                  │     ↓            │
│             │                  │  libedge-cuda.so │
│             │                  │     ↓            │
│             │                  │  libllama.so     │
└─────────────┘                  └──────────────────┘
```

## Commands (Implemented)

| Command | What it does |
|---------|-------------|
| `/think <prompt>` | Generate via native inference |
| `/gpu` | nvidia-smi (temp, util, mem, power) |
| `/cuda` | CUDA toolkit, device compute cap, CMA status |
| `/status` | System health (clients, peers, uptime) |
| `/peers` | List mesh peers |
| `/help` | Help message |
| `/quit` | Disconnect |

## Protocol

Newline-delimited JSON over Unix socket. flato sends `{"prompt": "...", "max_tokens": N}`, gateway responds with `{"text": "...", "tokens": N, "tps": N.N, "backend": "..."}`.

## Build & Deploy

```bash
cd /home/lucineer/edge-llama
cc -std=c17 -O2 -o flato flato.c -lpthread
./flato 4003 /tmp/edge-native.sock
```

## Future

- `@gpu` socket command for Evennia (read nvidia-smi from within MUD)
- `/model <name>` to switch between loaded models
- `/mode <optimizer|debugger|analyzer>` to match edge-gateway mode routing
- Mesh peer discovery via UDP broadcast
- Token budget tracking per session
