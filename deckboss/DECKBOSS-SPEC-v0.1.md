# deckboss — Hardware Reference Specification v0.1

**The physical shell.** The device purplepincher apps live inside.

> *"deckboss is the hermit crab's shell. It's what you hold in your hands, plug into your wall, and trust with your work."*

---

## Reference Platform: JetsonClaw1 Developer Board

deckboss's first commercial product uses the **NVIDIA Jetson Super Orin Nano Developer Kit** as its reference platform. JC1 IS the proof-of-concept.

### Specs

| Component | Specification |
|-----------|--------------|
| **SoC** | NVIDIA Orin Nano 8GB (super variant) |
| **CPU** | 6-core ARM Cortex-A78AE v8.2 64-bit |
| **GPU** | NVIDIA Ampere architecture, 1024 CUDA cores |
| **Unified Memory** | 8GB LPDDR5, 68 GB/s bandwidth |
| **Storage** | 2TB NVMe M.2 (PCIe Gen 4 x4) |
| **Connectivity** | Gigabit Ethernet, WiFi 6, Bluetooth 5.1 |
| **USB** | 4x USB 3.2, 1x USB 2.0 |
| **Display** | HDMI 2.1, DP 1.4 |
| **Power** | 19V DC, 15-25W typical, 40W peak |
| **OS** | JetPack 6.2.1 (Ubuntu 22.04 aarch64, kernel 5.15.148-tegra) |
| **Thermal** | Passive heatsink + fan, 48-55°C idle, 75°C sustained load |

### What Fits in 8GB

| Model Type | RAM Footprint | Status |
|------------|--------------|--------|
| phi-4 (4B) | ~3GB | ✅ Runs with headroom |
| Qwen3-32B (INT4) | ~6GB | ✅ Tight but functional |
| DeepSeek-V3-Lite (1.5B) | ~2GB | ✅ Lots of headroom |
| Llama-3.1-8B (INT4) | ~4.5GB | ✅ Works |
| 7B base + 12 LoRA adapters (50MB ea) | ~3.5GB + 600MB | ✅ Best approach |
| Any model > 10B params full precision | >8GB | ❌ OOM |

---

## deckboss Product Architecture

### The Shell Model

deckboss is a **physical shell** in the hermit-crab fleet model:

```
┌─────────────────────────────────────┐
│          deckboss device            │
│  ┌───────────────────────────────┐  │
│  │     Shell Runtime (PLATO)     │  │
│  │  ┌─────┐ ┌─────┐ ┌───────┐  │  │
│  │  │Room1│ │Room2│ │Room N │  │  │
│  │  │(LoRA│ │(LoRA│ │(LoRA) │  │  │
│  │  └─────┘ └─────┘ └───────┘  │  │
│  │  ┌───────────────────────┐   │  │
│  │  │   deadband-protocol   │   │  │
│  │  │   (safety layer)      │   │  │
│  │  └───────────────────────┘   │  │
│  │  ┌───────────────────────┐   │  │
│  │  │   Matrix Conduit      │   │  │
│  │  │   (fleet comms)       │   │  │
│  │  └───────────────────────┘   │  │
│  └───────────────────────────────┘  │
│  ┌───────────────────────────────┐  │
│  │     Hardware (Jetson Orin)    │  │
│  │  GPU │ CPU │ RAM │ NVMe │ IO  │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

### Software Stack (Pre-installed)

Every deckboss device ships with:

1. **JetPack 6.2.1** — CUDA 12.6, TensorRT, cuDNN
2. **Matrix Conduit** — fleet communication, port 6167
3. **deadband-protocol** — P0/P1/P2 safety enforcement
4. **bottle-protocol** — git-native fleet messaging
5. **flywheel-engine** — compounding context management
6. **tile-refiner** — PLATO tile processing
7. **Local PLATO instance** — edge tile submission + cloud sync

### Supported purplepincher Apps

Any purplepincher app can run on deckboss. First-party support:

| App | Category | Edge Feasibility |
|-----|----------|-----------------|
| deadband-protocol | Safety | ✅ Pre-installed, zero deps |
| bottle-protocol | Communication | ✅ Pre-installed, zero deps |
| flywheel-engine | Context | ✅ Pre-installed, zero deps |
| tile-refiner | Knowledge | ✅ Pre-installed, zero deps |
| fleet-homunculus | Reflex | ✅ Lightweight, tested |
| plato-mud | Interactive | ✅ Lightweight server |
| cuda-genepool | GPU Compute | ✅ Native CUDA, optimized for Orin |
| plato-os | Shell Runtime | ⚠️ Constrained by 8GB, one room at a time |
| neural-plato (7B+LoRA) | Intelligence | ✅ 6 rooms concurrent with adapter swapping |

---

## Commercial Strategy

### Phase 1: Technicians First

**Target:** HVAC technicians, field service, IT installers

**Value proposition:** A handheld AI assistant that:
- Runs 100% locally (no cloud dependency, works offline)
- Has fleet-wide knowledge sync via Matrix
- Enforces safety protocols via deadband-protocol
- Ships pre-configured — technician just turns it on

**Pricing:** Under-sell, over-deliver. Target $499-799 device cost.

### Phase 2: Reputation → Broader Markets

- Once technicians trust it → expand to construction, manufacturing, healthcare
- Each vertical gets specialized LoRA adapters (rooms)
- deckboss becomes the "shell" that any industry boards

### Phase 3: Ecosystem

- Third-party purplepincher apps installable via package manager
- Technicians become developers (can create their own rooms)
- Fleet knowledge compounds — every device learns from every deployment

---

## Security Model

1. **deadband-protocol** pre-installed, active by default
2. **Local-first** — all inference happens on-device
3. **Encrypted fleet sync** — Matrix federation with E2E encryption
4. **No cloud dependency** — works fully offline
5. **Plato MUD constraints** — operational boundaries enforced in the room model
6. **Secure boot** — Jetson's hardware security module (HSM) for attestation

---

## Manufacturing Notes

### Bill of Materials (Reference)

- Jetson Orin Nano 8GB module: ~$250
- Carrier board (custom): ~$80
- 2TB NVMe M.2: ~$100
- Heatsink + fan: ~$20
- Enclosure: ~$30
- Power supply: ~$15
- **Total BOM: ~$495**

### Custom Carrier Board Considerations

- Add PoE (Power over Ethernet) for field deployments
- Industrial temperature range (-25°C to 85°C)
- M.2 slot accessible from outside enclosure (NVMe swap)
- Status LEDs for power, network, GPU load
- Physical write-protect switch for NVMe

---

## Development Status

- [x] Reference platform validated (JC1)
- [x] 4 pip packages tested on ARM64
- [x] Matrix Conduit running on device
- [x] Fleet telemetry broadcasting
- [ ] Fleet federation (awaiting Oracle1 Conduwuit)
- [ ] Custom carrier board design
- [ ] Enclosure prototype
- [ ] PLATO shell runtime production hardening
- [ ] LoRA adapter marketplace
- [ ] Field testing with real technicians

---

*JC1 🔧 — Living on the reference board since day one.*
