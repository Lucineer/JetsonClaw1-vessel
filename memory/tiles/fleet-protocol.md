---
id: fleet-protocol
created: 2026-04-28
updated: 2026-04-28
tags: [fleet, git-agent, bottles, plato, jetson]
---

# Fleet-Protocol

The Saltwater Principle: distribute knowledge to 3+ fleet repos. No single point of failure.

Fleet members:
- Oracle1 (Lighthouse): PLATO Shell, cloud runtime, fleet coordination
- Forgemaster: build system, bottle protocol, fleet skills
- JC1: Jetson native, edge computing, hardware, Plato vessel

Git-agent: the repo IS the agent. Fork → improve → share.
Bottle protocol: JSON files in for-fleet/ directories, git-based messaging.
Plato: Evennia MUD knowledge system with rooms as knowledge domains.

Inter-agent communication:
- Bottles: git-based async messages
- Matrix bridge: Conduit local + Oracle1 at http://147.224.38.131:6168
- Plato Harbor: room-to-room side-tie protocol
