---
id: flato-mud
created: 2026-04-30
updated: 2026-04-30
tags: [mud, networking, c, fleet]
---

# flato — Fleet Plato MUD

A minimal multi-agent MUD in C17. No dependencies. Pure poll() event loop.

## Architecture
- Telnet server on port 4000
- Connects to edge-llama via Unix socket (/tmp/edge-llama.sock)
- Forwards /think prompts, streams responses back to client
- Max 64 concurrent clients, single-threaded

## Commands
```
/think <prompt>   — Generate with edge-llama
/status            — System health
/peers             — List mesh peers
/help              — This message
/quit              — Disconnect
```

## Design
flato owns the connection pool and routing. edge-llama owns compute. Together they form the foundation of a distributed mesh compute protocol.

## Build
```bash
cc -std=c17 -O2 -o flato flato.c -lpthread
```

## Run
```bash
./flato 4000 /tmp/edge-llama.sock
```

## Mesh (future)
UDP broadcast discovery for peer-to-peer connections. Each flato instance can bridge to other agents' MUDs.
