# HEARTBEAT.md
## 2026-05-05 16:04 AKDT — v0.13.0: Warp-as-Room + 6 Timers

### ✅ Shipped
- **warp_room.py** — numpy port of SuperInstance/gpu-native-room-inference
  - GPU warp → bigram TF vectors. Room collective → dot product.
  - 4 room profiles, 97-dimensional feature space, online learning
  - systemd timer every 10 minutes
- **sensor-pipeline.py** — hardware telemetry → PLATO tiles, 5-6/cycle
- **Fleet bottles** in 3 repos (edge-llama/, workspace/, plato-jetson/)
- **jc1-research repo** pushed to SuperInstance with agent + sync code

### Running (11 services + 6 timers)
| Timer | Interval | Tiles fed |
|-------|----------|-----------|
| sensor-pipeline | 5min | ✅ 5-6 per cycle |
| plato-sync | 5min | ✅ Evennia ↔ plato |
| jc1-research | 5min | ✅ CCC research fork |
| jc1-telemetry | 5min | ✅ system metrics |
| warp-room | 10min | ✅ NEW — room classifier |
| mesh-sync | 60min | ✅ fleet deadman |

### PLATO: 126+ tiles, 4 rooms, 4 agents

### Blocked
- GPU — CMA=0, cuInit segfaults
- Matrix jc1-bot — not authed for DM on Oracle1 bridge
