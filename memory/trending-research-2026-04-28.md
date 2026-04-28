# Trending GitHub Research → Implementation Plan
**Date:** 2026-04-28
**Source:** GitHub trending (today + weekly) across Python, Rust, TypeScript, Go, C

## Key Findings: What's Trending Now

### AI Agent Ecosystem (exploding)
- **skills / agent-skills** — Skill files for coding agents. 35K+25K stars collectively. The "CLAUDE.md as skill" pattern is dominant.
- **GenericAgent** — Self-evolving agent with skill tree from 3.3K-line seed. 6x less token consumption.
- **multica** — Managed agent platform. Assign tasks, track progress, compound skills.
- **pi-mono** — Full agent toolkit: CLI, TUI, Slack bot, unified LLM API, vLLM.

### Memory & Knowledge Management
- **memsearch** (Zilliz) — Persistent unified memory layer for AI agents. Markdown + Milvus. 1:1 maps to Plato tiles.
- **RAG-Anything** — All-in-one RAG framework. 19K⭐.
- **claude-context** — MCP for full-codebase context.
- **FalkorDB** — GraphDB for LLM knowledge graphs. C, GraphBLAS.
- **codebase-memory-mcp** — Single-binary MCP server for code knowledge graphs.

### Agent Memory Systems
- **beads** (22K⭐) — "Memory upgrade for your coding agent". Go.
- **gascity** — Orchestration SDK for multi-agent workflows. Go.

### Edge Computing
- **LiteRT-LM** — Already using this (Google's edge LLM inference)
- **vllm-project/semantic-router** — Intelligent model routing. Go. "Mixture-of-Models at Cloud, Data Center and Edge"
- **box64** — x86_64 emulator for ARM64. Useful for Jetson.

### Model Routing & Cost Optimization
- **manifest** (5.7K⭐) — Smart model routing, cut costs 70%. Maps to cocapn.ai's core value prop.
- **ds2api** (2.2K⭐) — DeepSeek → Universal API proxy. Similar to our cocapn-chat.
- **sub2api** (16K⭐) — Subscription aggregation for API access.

## Implementation Plan: Build Into Our Stack

### High Priority (building now)

1. **Plato-memsearch bridge** — Integrate memsearch (or similar) into Plato's tile/room system as the backing vector store
2. **Cocapn manifest integration** — Add smart model routing to cocapn-chat (route to cheapest capable model)
3. **Plato skill tree** — Borrow GenericAgent's skill tree pattern for agent skills in Plato
4. **beads-for-Plato** — Port beads memory pattern to our Evennia MUD knowledge system
5. **Edge semantic router** — Integrate vllm semantic-router for Jetson model selection

### Medium Priority

6. **claude-context MCP for Plato** — Code search across fleet repos via Plato rooms
7. **RAG-Anything integration** — As Plato's document ingestion pipeline
8. **gascity multi-agent orchestration** — Port to our fleet coordination patterns
9. **FalkorDB GraphRAG** — Knowledge graph layer for Plato

### Infrastructure

10. **box64 edge** — Use for running x86_64 binaries on Jetson
11. **opensre patterns** — Monitoring patterns for fleet health
