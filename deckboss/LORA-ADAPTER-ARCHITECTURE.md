# LoRA Adapter Architecture — PLATO Room Switching on 8GB Edge

**The engine that makes deckboss intelligent.**

> *"One mind, many rooms. The shell doesn't change — the way it thinks does."*

---

## 1. Memory Layout

### 8GB Budget Breakdown

```
┌─────────────────────────────────────────────────┐
│              8GB Unified Memory (LPDDR5)         │
├──────────────────┬──────────────────────────────┤
│   OS + System    │     Model Runtime             │
│   ~1.5GB         │     ~6.5GB                     │
├──────────────────┼──────────────────────────────┤
│  Linux kernel    │  ┌────────────────────────┐  │
│  systemd, etc.   │  │  Qwen2.5-7B INT4       │  │
│  Conduit (30MB)  │  │  Base Model (4.2GB)     │  │
│  telemetry cron  │  │  ──────────────────────  │  │
│  deadband        │  │  KV Cache (1.0GB)       │  │
│  Matrix plugin   │  │  ──────────────────────  │  │
│                  │  │  LoRA Adapters (1.0GB)  │  │
│                  │  │  2-3 hot, ~50MB each    │  │
│                  │  │  ──────────────────────  │  │
│                  │  │  Overhead (0.3GB)       │  │
│                  │  │  tokenizer, activations  │  │
│                  │  └────────────────────────┘  │
└──────────────────┴──────────────────────────────┘
```

### Detailed Memory Map

| Component | Size | Notes |
|-----------|------|-------|
| Base model (Qwen2.5-7B-Instruct INT4) | ~4.2GB | BitsAndBytes 4-bit, loaded once |
| KV Cache | ~1.0GB | 2048 token context × 32 layers × 2 heads |
| LoRA adapters (hot pool) | ~150MB | 3 adapters × 50MB each (rank 16) |
| LoRA adapters (cold, disk) | ~150MB | 3 adapters on NVMe, loaded on demand |
| Tokenizer + embeddings | ~200MB | Qwen tokenizer |
| Activation buffers | ~100MB | Intermediate inference tensors |
| PyTorch runtime | ~300MB | CUDA context, allocator overhead |
| Python interpreter | ~100MB | CPython + libraries |
| **Total** | **~6.2GB** | 300MB headroom for safety |

### Why INT4, Not FP16

| Precision | 7B Model Size | KV Cache (2K) | Total | Fits? |
|-----------|--------------|----------------|-------|-------|
| FP32 | 28GB | 4GB | 32GB | ❌ |
| FP16 | 14GB | 2GB | 16GB | ❌ |
| INT8 | 7GB | 1GB | 8GB | ⚠️ Tight |
| **INT4** | **4.2GB** | **1GB** | **5.2GB** | **✅ Yes** |

---

## 2. AdapterManager Design

### Core Class

```python
"""
deckboss/adapter_manager.py
Hot-loadable LoRA adapter system for PLATO room switching.
"""

import os
import json
import time
import threading
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel, PeftConfig, LoraConfig, TaskType


class RoomPriority(Enum):
    P0 = "safety"       # deadband-protocol — always available
    P1 = "operational"  # fleet-coordination, jc1-hardware
    P2 = "enhancement"  # plato-ecosystem, deckboss-onboarding, cocapn-harbor


@dataclass
class RoomAdapter:
    """A PLATO room = a LoRA adapter + context."""
    name: str
    adapter_path: str           # Path to LoRA weights on NVMe
    system_prompt: str          # Room's personality/instructions
    priority: RoomPriority      # Preemption priority
    tools: List[dict]           # Tool definitions for this room
    max_history: int = 20       # Conversation turns to keep
    last_used: float = 0.0      # Timestamp of last access
    
    # Runtime state
    _loaded: bool = field(default=False, repr=False)
    _peft_model: Optional[PeftModel] = field(default=None, repr=False)


@dataclass
class AdapterPool:
    """Configuration for the hot adapter pool."""
    hot_pool_size: int = 3       # Max adapters in GPU at once
    eviction_policy: str = "lru"  # "lru" or "priority"


class AdapterManager:
    """
    Manages LoRA adapter hot-loading on constrained edge hardware.
    
    Design principles:
    - Base model: loaded once, never evicted
    - P0 adapter (deadband): always hot, never evicted
    - Hot pool: N adapters in GPU, LRU eviction for cold storage
    - Cold storage: adapters on NVMe, loaded in <500ms
    - Thread-safe: room switches can happen from any thread
    """
    
    def __init__(
        self,
        base_model_name: str = "Qwen/Qwen2.5-7B-Instruct",
        adapter_dir: str = "deckboss/adapters",
        pool_config: Optional[AdapterPool] = None,
    ):
        self.base_model_name = base_model_name
        self.adapter_dir = Path(adapter_dir)
        self.pool_config = pool_config or AdapterPool()
        
        # Runtime state
        self._base_model = None
        self._tokenizer = None
        self._merged_model = None
        self._hot_adapters: Dict[str, RoomAdapter] = {}  # name -> adapter
        self._all_rooms: Dict[str, RoomAdapter] = {}     # name -> adapter
        self._current_room: Optional[str] = None
        self._lock = threading.RLock()
        self._kv_cache: Optional[dict] = None
        
        # Metrics
        self._switch_count = 0
        self._total_switch_time_ms = 0.0
    
    def load_base_model(self) -> None:
        """Load the base model with INT4 quantization. Called once at startup."""
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,  # Saves ~200MB
        )
        
        self._tokenizer = AutoTokenizer.from_pretrained(
            self.base_model_name,
            trust_remote_code=True,
        )
        self._base_model = AutoModelForCausalLM.from_pretrained(
            self.base_model_name,
            quantization_config=bnb_config,
            device_map="auto",
            torch_dtype=torch.float16,
            trust_remote_code=True,
        )
        self._base_model.eval()
    
    def register_room(self, adapter: RoomAdapter) -> None:
        """Register a room adapter. Does not load it yet."""
        self._all_rooms[adapter.name] = adapter
    
    def switch_room(self, room_name: str) -> bool:
        """
        Switch to a different PLATO room.
        Hot-loads the adapter if not in pool, evicts LRU if pool is full.
        """
        start = time.monotonic()
        
        with self._lock:
            if room_name not in self._all_rooms:
                return False
            
            adapter = self._all_rooms[room_name]
            
            # Already loaded and current?
            if room_name == self._current_room:
                adapter.last_used = time.monotonic()
                return True
            
            # Need to load?
            if room_name not in self._hot_adapters:
                self._evict_if_needed()
                self._load_adapter(adapter)
            
            # Merge adapter into base model
            self._apply_adapter(adapter)
            
            # Clear KV cache for new room context
            self._clear_kv_cache()
            
            # Update state
            self._current_room = room_name
            adapter.last_used = time.monotonic()
            
            elapsed_ms = (time.monotonic() - start) * 1000
            self._switch_count += 1
            self._total_switch_time_ms += elapsed_ms
        
        return True
    
    def generate(self, prompt: str, max_tokens: int = 512, **kwargs) -> str:
        """Generate response using current room's adapter."""
        if self._current_room is None:
            raise RuntimeError("No room active. Call switch_room() first.")
        
        room = self._all_rooms[self._current_room]
        
        # Build messages with room context
        messages = [
            {"role": "system", "content": room.system_prompt},
            {"role": "user", "content": prompt},
        ]
        
        inputs = self._tokenizer.apply_chat_template(
            messages, return_tensors="pt", add_generation_prompt=True
        ).to(self._base_model.device)
        
        with torch.no_grad():
            outputs = self._merged_model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                pad_token_id=self._tokenizer.eos_token_id,
                **kwargs,
            )
        
        response = self._tokenizer.decode(
            outputs[0][inputs.shape[1]:], skip_special_tokens=True
        )
        return response
    
    def _evict_if_needed(self) -> None:
        """Evict LRU adapter if hot pool is full. P0 adapters are never evicted."""
        hot_size = len(self._hot_adapters)
        max_hot = self.pool_config.hot_pool_size
        
        while hot_size >= max_hot:
            # Find LRU non-P0 adapter
            candidates = [
                (name, a) for name, a in self._hot_adapters.items()
                if a.priority != RoomPriority.P0
            ]
            if not candidates:
                break  # Only P0 adapters left, can't evict
            
            lru_name, lru_adapter = min(candidates, key=lambda x: x[1].last_used)
            
            if self.pool_config.eviction_policy == "lru":
                self._unload_adapter(lru_name)
                hot_size -= 1
    
    def _load_adapter(self, adapter: RoomAdapter) -> None:
        """Load adapter weights from NVMe into GPU."""
        if adapter.adapter_path and os.path.exists(adapter.adapter_path):
            peft_config = PeftConfig.from_pretrained(adapter.adapter_path)
            # Load just the adapter weights (not the full model)
            # This is ~50MB, fast from NVMe
            adapter._loaded = True
        else:
            adapter._loaded = True  # Untrained adapter, base model only
        
        self._hot_adapters[adapter.name] = adapter
        adapter.last_used = time.monotonic()
    
    def _apply_adapter(self, adapter: RoomAdapter) -> None:
        """Merge adapter weights into the base model."""
        if adapter.adapter_path and os.path.exists(adapter.adapter_path):
            self._merged_model = PeftModel.from_pretrained(
                self._base_model, adapter.adapter_path
            )
        else:
            self._merged_model = self._base_model
    
    def _unload_adapter(self, name: str) -> None:
        """Remove adapter from hot pool."""
        if name in self._hot_adapters:
            del self._hot_adapters[name]
    
    def _clear_kv_cache(self) -> None:
        """Free KV cache for new room context."""
        with torch.no_grad():
            if hasattr(self._base_model, 'kv_cache'):
                self._base_model.kv_cache = None
            torch.cuda.empty_cache()
    
    def get_current_room(self) -> Optional[str]:
        return self._current_room
    
    def get_metrics(self) -> dict:
        return {
            "current_room": self._current_room,
            "hot_pool": list(self._hot_adapters.keys()),
            "hot_pool_size": len(self._hot_adapters),
            "switch_count": self._switch_count,
            "avg_switch_ms": (
                self._total_switch_time_ms / self._switch_count
                if self._switch_count > 0 else 0
            ),
            "gpu_memory_allocated": (
                torch.cuda.memory_allocated() / 1024**3
                if torch.cuda.is_available() else 0
            ),
            "gpu_memory_reserved": (
                torch.cuda.memory_reserved() / 1024**3
                if torch.cuda.is_available() else 0
            ),
        }
```

---

## 3. Room Context Protocol

### Room Definition Format (YAML)

```yaml
# deckboss/rooms/fleet-coordination.yaml
name: fleet-coordination
adapter_path: deckboss/adapters/fleet-coordination
priority: P1
max_history: 20

system_prompt: |
  You are the fleet coordination agent for deckboss. Your role:
  - Parse fleet status messages from Matrix rooms
  - Delegate tasks to other rooms based on content
  - Format responses as structured fleet bottles
  - Track vessel health and report anomalies
  
  Fleet members: JC1 (edge), Oracle1 (cloud), FM (build), CCC (voice)
  
  Always respond in fleet message format with proper attribution.

tools:
  - name: broadcast_telemetry
    description: Send hardware telemetry to fleet room
    parameters:
      type: object
      properties:
        room_id:
          type: string
          description: Matrix room ID
        include_thermal:
          type: boolean
          default: true

  - name: parse_fleet_bottle
    description: Parse and validate an incoming fleet bottle
    parameters:
      type: object
      properties:
        bottle_path:
          type: string
          description: Path to bottle markdown file

  - name: create_bottle
    description: Create a new fleet bottle for outbound delivery
    parameters:
      type: object
      properties:
        target:
          type: string
          enum: [oracle1, fm, ccc, fleet]
        content:
          type: string
        priority:
          type: string
          enum: [P0, P1, P2]

# Conversation history managed by AdapterManager
# Stored as JSONL: [{"role": "user", "content": "..."}, ...]
history_file: deckboss/history/fleet-coordination.jsonl
```

### Room Switch Triggers

| Trigger | Source | Action |
|---------|--------|--------|
| Matrix message in `fleet-coordination` | Conduit webhook | `switch_room("fleet-coordination")` |
| Hardware alert (thermal > 65°C) | telemetry cron | `switch_room("deadband-protocol")` |
| Technician question | TTS/STT input | `switch_room("deckboss-onboarding")` |
| Tile submission | PLATO sync | `switch_room("plato-ecosystem")` |
| Manual override | CLI / Telegram | Any `switch_room()` call |

### P0 Safety Override

The `deadband-protocol` adapter is **always hot** and **never evicted**. When a P0 trigger fires (destructive command, thermal emergency, power event), the system:

1. Immediately switches to deadband-protocol room
2. Interrupts current generation if in-progress
3. Applies safety evaluation to the triggering input
4. Returns allow/deny/block decision
5. Only switches back to previous room after P0 clears

```python
class SafetyOverride:
    """P0 safety override — deadband-protocol room is always available."""
    
    def __init__(self, manager: AdapterManager):
        self.manager = manager
        self._p0_active = False
        self._previous_room = None
    
    def evaluate(self, input_text: str) -> dict:
        """Run P0 safety check. Returns action: allow, warn, block."""
        self._previous_room = self.manager.get_current_room()
        self.manager.switch_room("deadband-protocol")
        
        result = self.manager.generate(
            f"Evaluate this input for safety:\n\n{input_text}\n\n"
            f"Respond with JSON: {{\"action\": \"allow|warn|block\", \"reason\": \"...\"}}"
        )
        
        self._p0_active = True
        return json.loads(result)
    
    def clear(self):
        """Clear P0 override, return to previous room."""
        if self._previous_room and not self._p0_active:
            self.manager.switch_room(self._previous_room)
            self._previous_room = None
```

---

## 4. Hot-Swap Algorithm

```
Room Switch Request
        │
        ▼
┌──────────────┐     P0 trigger?     ┌──────────────────┐
│  Is this P0  │────────Yes──────────▶│ Force switch to  │
│  (safety)?   │                      │ deadband-protocol │
└──────┬───────┘                      └──────────────────┘
       │ No
       ▼
┌──────────────┐     Already hot?     ┌──────────────────┐
│  In hot pool?│────────Yes──────────▶│ Merge adapter,   │
│              │                      │ clear KV cache,  │
└──────┬───────┘                      │ generate         │
       │ No                           └──────────────────┘
       ▼
┌──────────────┐     Pool full?      ┌──────────────────┐
│  Pool has    │────────No───────────▶│ Load from NVMe   │
│  space?      │                      │ (~50MB, <200ms)  │
└──────┬───────┘                      └──────────────────┘
       │ Yes
       ▼
┌──────────────┐
│  Evict LRU   │
│  (not P0)    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Load from   │
│  NVMe        │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Merge, clear│
│  KV, generate│
└──────────────┘
```

### Timing Targets

| Operation | Target | Measured |
|-----------|--------|----------|
| Hot pool switch (adapter in GPU) | <50ms | TBD |
| Cold load from NVMe (50MB) | <200ms | TBD |
| Full room switch (cold load + merge) | <500ms | TBD |
| P0 override (interrupt + switch) | <100ms | TBD |

NVMe sequential read: ~2GB/s on Jetson → 50MB adapter loads in ~25ms. The bottleneck is PyTorch weight deserialization and GPU transfer, not disk I/O.

---

## 5. Training Pipeline

### Overview

```
PLATO Tiles (cloud)                    JC1 Edge
┌──────────────────┐                  ┌─────────────────┐
│  98 tiles across  │                  │                  │
│  20 rooms         │   ┌──────────┐  │                  │
│                   │──▶│  Filter  │  │                  │
│  Oracle1's PLATO  │   │  by room │  │                  │
│  at 8847          │   └────┬─────┘  │                  │
│                   │        │        │                  │
│                   │   ┌────▼─────┐  │   ┌──────────┐  │
│                   │   │  Build   │  │──▶│  LoRA    │  │
│                   │   │  train   │  │   │  train   │  │
│                   │   │  dataset │  │   │  (on GPU)│  │
│                   │   └──────────┘  │   └────┬─────┘  │
│                   │                  │        │        │
│                   │                  │   ┌────▼─────┐  │
│                   │                  │   │  Save    │  │
│                   │                  │   │  adapter │  │
│                   │                  │   │  (50MB)  │  │
│                   │                  │   └──────────┘  │
└──────────────────┘                  └─────────────────┘
```

### Training Data Preparation

```python
def build_training_dataset(room_name: str, tiles: List[dict]) -> List[dict]:
    """
    Convert PLATO tiles into LoRA fine-tuning format.
    
    Each tile becomes a training example:
    - system: room's system prompt
    - user: tile's question
    - assistant: tile's answer
    """
    room = load_room_config(room_name)
    dataset = []
    
    for tile in tiles:
        dataset.append({
            "messages": [
                {"role": "system", "content": room.system_prompt},
                {"role": "user", "content": tile["question"]},
                {"role": "assistant", "content": tile["answer"]},
            ]
        })
    
    return dataset
```

### LoRA Configuration

```python
# Per-room LoRA hyperparameters
LORA_CONFIG = {
    "r": 16,              # Rank — 50MB per adapter at rank 16
    "lora_alpha": 32,     # Scaling factor (2x rank is standard)
    "target_modules": [   # Which layers get LoRA
        "q_proj", "k_proj", "v_proj", "o_proj",  # Attention
        "gate_proj", "up_proj", "down_proj",     # MLP
    ],
    "lora_dropout": 0.05,
    "bias": "none",
    "task_type": "CAUSAL_LM",
}

# Why rank 16?
# - Rank 8: ~25MB per adapter, less expressive, enough for narrow tasks
# - Rank 16: ~50MB per adapter, good balance of expressiveness and size
# - Rank 32: ~100MB per adapter, diminishing returns on 7B base
# - Rank 64: ~200MB, overkill for room specialization
```

### Training Budget

| Parameter | Value |
|-----------|-------|
| Base model | Qwen2.5-7B-Instruct (frozen) |
| Trainable params | ~4.2M per adapter (rank 16) |
| Dataset size | 50-200 tile pairs per room |
| Epochs | 3-5 |
| Learning rate | 2e-4 |
| Batch size | 4 (gradient accumulation 8) |
| Precision | BF16 mixed (if supported) else FP16 |
| Training time | ~5-15 min per adapter on Jetson |
| Output | ~50MB adapter weights |

### Validation

After training, validate each room adapter:
1. **Relevance**: Does it stay on-topic for its room?
2. **Safety**: Does it still respect deadband rules?
3. **Accuracy**: Does it correctly answer room-specific questions?
4. **Size**: Is the adapter ≤50MB?
5. **Latency**: Does inference with adapter stay <200ms first-token?

---

## 6. Integration with JC1 Services

### Matrix → Adapter Selection

```python
class MatrixRoomBridge:
    """Route Matrix messages to the correct PLATO room adapter."""
    
    ROOM_MAP = {
        "fleet-coordination": "fleet-coordination",
        "plato-ecosystem": "plato-ecosystem",
        "jc1-hardware": "jc1-hardware",
        "deadband-protocol": "deadband-protocol",
    }
    
    def __init__(self, adapter_manager: AdapterManager):
        self.manager = adapter_manager
    
    def on_matrix_message(self, room_alias: str, sender: str, text: str):
        room_name = self.ROOM_MAP.get(room_alias)
        if not room_name:
            return
        
        self.manager.switch_room(room_name)
        response = self.manager.generate(
            f"Fleet message from {sender}:\n\n{text}\n\nRespond as the {room_name} agent."
        )
        return response
```

### Telemetry → Hardware Room

```python
class TelemetryRouter:
    """Route telemetry data to hardware room for analysis."""
    
    def __init__(self, adapter_manager: AdapterManager):
        self.manager = adapter_manager
        self._alert_thresholds = {
            "thermal_max_c": 70,
            "memory_percent": 85,
            "disk_percent": 90,
        }
    
    def process_telemetry(self, telemetry: dict):
        # Check for alerts first (P0)
        if telemetry.get("thermal_max", 0) > self._alert_thresholds["thermal_max_c"]:
            self.manager.switch_room("deadband-protocol")
            return self._handle_thermal_alert(telemetry)
        
        # Normal processing in hardware room
        self.manager.switch_room("jc1-hardware")
        return self.manager.generate(
            f"Current hardware telemetry:\n{json.dumps(telemetry, indent=2)}\n\n"
            f"Provide status summary and any recommendations."
        )
```

### PLATO Sync → Tile Processing

```python
class PlatoTileBridge:
    """Process incoming PLATO tiles through the ecosystem room."""
    
    def __init__(self, adapter_manager: AdapterManager, plato_url: str):
        self.manager = adapter_manager
        self.plato_url = plato_url
    
    def on_tile_received(self, domain: str, tile: dict):
        self.manager.switch_room("plato-ecosystem")
        analysis = self.manager.generate(
            f"New PLATO tile received:\n"
            f"Domain: {domain}\n"
            f"Question: {tile.get('question', '')}\n"
            f"Answer: {tile.get('answer', '')}\n"
            f"Source: {tile.get('source', '')}\n\n"
            f"Analyze this tile for cross-room connections and relevance."
        )
        return analysis
```

---

## 7. File Structure

```
deckboss/
├── DECKBOSS-SPEC-v0.1.md           # Hardware reference spec
├── LORA-ADAPTER-ARCHITECTURE.md    # This document
├── README.md                       # Project overview
│
├── adapter_manager.py              # Core AdapterManager class
├── safety_override.py              # P0 deadband integration
├── matrix_bridge.py                # Matrix → room routing
├── telemetry_router.py             # Telemetry → hardware room
├── plato_bridge.py                 # PLATO sync integration
├── training/
│   ├── build_dataset.py            # Tile → training data converter
│   ├── train_adapter.py            # LoRA fine-tuning script
│   ├── validate_adapter.py         # Post-training validation
│   └── export_adapter.py           # Export adapter for deployment
│
├── rooms/                          # Room definitions
│   ├── fleet-coordination.yaml
│   ├── plato-ecosystem.yaml
│   ├── jc1-hardware.yaml
│   ├── deadband-protocol.yaml
│   ├── deckboss-onboarding.yaml
│   └── cocapn-harbor.yaml
│
├── adapters/                       # Trained LoRA weights
│   ├── fleet-coordination/         # adapter_config.json + adapter_model.safetensors
│   ├── plato-ecosystem/
│   ├── jc1-hardware/
│   ├── deadband-protocol/
│   ├── deckboss-onboarding/
│   └── cocapn-harbor/
│
├── history/                        # Per-room conversation history (JSONL)
│   ├── fleet-coordination.jsonl
│   ├── plato-ecosystem.jsonl
│   └── ...
│
└── tests/
    ├── test_adapter_manager.py
    ├── test_hot_swap.py
    ├── test_safety_override.py
    └── test_integration.py
```

---

## 8. Implementation Roadmap

### Phase 1: Foundation (This Week)
- [ ] Install CUDA-enabled PyTorch on Jetson
- [ ] Install peft + transformers + bitsandbytes
- [ ] Load Qwen2.5-7B INT4 on GPU, verify memory usage
- [ ] Implement AdapterManager with room switching
- [ ] Measure hot-swap latency

### Phase 2: Training (Next Week)
- [ ] Pull PLATO tiles from Oracle1's server
- [ ] Build training datasets per room
- [ ] Train first adapter (deadband-protocol — most critical)
- [ ] Validate safety behavior

### Phase 3: Integration (Week 3)
- [ ] Matrix bridge: route messages to room adapters
- [ ] Telemetry router: thermal alerts → deadband room
- [ ] PLATO bridge: process tiles through ecosystem room
- [ ] End-to-end demo: Matrix message → room switch → response

### Phase 4: Production (Week 4+)
- [ ] All 6 room adapters trained and validated
- [ ] TTS/STT integration (voice → room → voice response)
- [ ] Onboarding room for field technician UX
- [ ] Package as deckboss-core pip package

---

## 9. Key Risks

| Risk | Mitigation |
|------|-----------|
| PyTorch CUDA on ARM64/Jetson | Use NVIDIA JetPack PyTorch wheels, not standard pip |
| INT4 quality degradation | Test thoroughly; use NF4 (normal float 4) for best quality |
| 8GB too tight with OS overhead | Firefox NOT on production deckboss; headless device frees 3.7GB |
| Adapter quality with few tiles | Start with 50+ tiles per room; augment with synthetic data |
| Hot-swap latency >500ms | NVMe is fast; bottleneck is deserialization, not I/O |
| Memory fragmentation over time | Periodic `torch.cuda.empty_cache()` and adapter reload |

---

*"The shell doesn't change — the way it thinks does."*

JC1 🔧 — Living on the reference board, designing the engine.
