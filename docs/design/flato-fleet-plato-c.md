# flato — Fleet Plato MUD (C17)

**A minimal multi-agent MUD for fleet compute.**

flato is the networking layer. edge-llama is the compute layer. Together they form the foundation of a distributed mesh compute protocol.

## Architecture

```
┌─────────────┐     Unix Socket     ┌──────────────┐
│  flato MUD  │◄───────────────────►│  edge-llama  │
│  (C17)      │   /tmp/edge-llama   │  inference   │
│  telnet:    │   .sock             │  server      │
│  0.0.0.0:   │                     │              │
│  4000       │                     │              │
└─────┬───────┘                     └──────────────┘
      │
      │ TCP/IP
      ▼
┌─────────────┐
│ mesh peers  │
│ (fleet)     │
└─────────────┘
```

## Protocol (Telnet-based)

```
> /think <prompt>        # Send prompt to edge-llama, stream response
> /tile <name>           # Create knowledge tile from conversation
> /graph                 # Show tile graph
> /peer                  # List mesh peers
> /bridge <peer>         # Bridge to another agent's MUD
> /status                # System health
```

## C17 Design

```c
// flato.h — Core types

typedef struct {
    int fd;                    // Client socket
    char buf[8192];            // Read buffer
    size_t len;                // Buffer length
    enum { AWAITING_INPUT, GENERATING } state;
    int32_t tokens[2048];      // Token history
    int n_tokens;
} Client;

typedef struct {
    int listen_fd;             // Telnet server socket
    Client clients[16];        // Max concurrent clients
    int n_clients;
    // Mesh
    struct sockaddr_in peers[32];
    int n_peers;
    // Edge-llama bridge
    int llama_fd;              // Unix socket to edge-llama
} Server;

// Event loop: poll() on all fds
// When client sends prompt: forward tokens to edge-llama via socket
// When edge-llama responds: stream bytes to client
```

## Build

```c
cc -std=c17 -O2 -o flato flato.c -lpthread
```

No dependencies. Not even libevent. Pure poll()/send()/recv().

## Design Notes

- flato owns the telnet connection pool and mesh routing
- edge-llama owns compute — it's a stateless inference pipe
- A single flato instance can drive multiple edge-llama processes (model sharding)
- Mesh peers share the same flato protocol — discoverable via UDP broadcast
- Knowledge tiles created during /think sessions persist to GGUF models via fine-tuning (future)
