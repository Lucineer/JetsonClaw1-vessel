# Improvement Ideas for Cocapn Ecosystem

Based on research into SuperInstance papers (SMPbot Architecture, Confidence Cascade, Universal Cell) and the Soft Actualization concept.

## 1. Formalize SMP Architecture in Cocapn

**Repo:** cocapn  
**Files:** `src/core/agent.ts`, `src/types/`  
**What:** Add explicit Seed, Model, Prompt type interfaces matching the SMPbot formalization. Track stability scores per response. Add `simulateOrCall` as a core primitive.  
**Why:** Cocapn is already implicitly SMP but has no formal guarantees. Making it explicit enables composition theorems and stability monitoring.  
**Effort:** Medium

## 2. Confidence Cascade for Soft Gap Safety

**Repo:** cocapn  
**Files:** `src/core/soft-actualization.ts` (new)  
**What:** Implement three-zone confidence (GREEN/YELLOW/RED) for soft gaps. GREEN gaps simulate silently. YELLOW gaps log warnings. RED gaps pause and request human review before simulating.  
**Why:** Without confidence gating, Soft Actualization can produce misleading results in low-confidence scenarios. Deadband triggers prevent oscillation between simulate/fail.  
**Effort:** Small

## 3. Seed Registry (Domain Knowledge Packs)

**Repo:** cocapn (or new `cocapn-seeds` repo)  
**Files:** New repo with `seeds/fishing/`, `seeds/medical/`, `seeds/legal/`, etc.  
**What:** Create a registry of importable seed-data packages — domain knowledge that cocapn repos can `cocapn seed add fishing-vessel` to get immediate domain context. Each seed includes: facts, relationships, procedures, and prompt templates.  
**Why:** The SMPbot paper shows Seeds are the stability anchor. A registry lets users bootstrap domain expertise instantly instead of building it from scratch.  
**Effort:** Medium

## 4. Code Actualization Ratio Dashboard

**Repo:** cocapn  
**Files:** `src/metrics/car.ts` (new), public repo UI  
**What:** Track CAR (hardened_paths / total_paths) as a repo health metric. Show it in the agent's public face. Add `cocapn status` CLI output showing gap count, CAR, and hardening progress.  
**Why:** Gives users visibility into how "real" their app is. Motivates hardening. The SMPbot paper's stability metric σ can be derived from CAR × model confidence.  
**Effort:** Small

## 5. Rate-Based Change for Memory

**Repo:** cocapn  
**Files:** `src/memory/memories.json`, `src/core/memory-manager.ts`  
**What:** Replace absolute confidence scores with rate-based change tracking (from Universal Cell paper). Track d(confidence)/dt instead of confidence alone. Rising confidence = learning. Flat = stable. Falling = forgetting.  
**Why:** The Universal Cell paper demonstrates rate-based change is superior for state tracking. Enables predictive memory decay and anomaly detection ("this fact is being accessed less frequently — consider archiving").  
**Effort:** Medium

## 6. Shared Model Loading for Fleet Mode

**Repo:** cocapn  
**Files:** `src/core/model-pool.ts` (new), fleet/A2A handler  
**What:** When multiple cocapn agents run on the same host (fleet mode), pool their LLM connections. Load the model once, share across agents. Implement the SMPbot paper's memory sharing and hot-swap architecture.  
**Why:** The SMPbot paper's Model component explicitly addresses GPU memory sharing. Fleet deployments on constrained hardware (Jetson) need this.  
**Effort:** Large

## 7. Deadband Triggers for Heartbeat Checks

**Repo:** cocapn  
**Files:** `src/heartbeat/`  
**What:** Apply Confidence Cascade deadbands to heartbeat checks. If a metric (e.g., email unread count) fluctuates within ±5%, don't trigger a notification cascade. Only alert when it crosses the deadband boundary.  
**Why:** Prevents notification fatigue from noisy metrics. The Confidence Cascade paper proves this reduces recomputation by ~40% in production systems.  
**Effort:** Small

## 8. Hysteresis for Agent Mode Switching

**Repo:** cocapn  
**Files:** `src/core/mode-manager.ts`  
**What:** When switching between Private/Public/Maintenance modes, apply hysteresis. Don't switch modes on every threshold crossing — require the condition to persist for N seconds or M consecutive checks.  
**Why:** The Confidence Cascade architecture's deadband formalism applies directly to mode switching. Prevents mode oscillation when the agent is near a boundary condition.  
**Effort:** Small

## 9. Skill Injection from I-know-kung-fu

**Repo:** cocapn, I-know-kung-fu  
**Files:** `src/skills/loader.ts`  
**What:** Integrate the I-know-kung-fu skill injection framework as the official cocapn skill loading mechanism. Skills become SMPbots: Seed = skill documentation, Model = shared LLM, Prompt = skill instructions.  
**Why:** Currently cocapn skills are ad-hoc. Formalizing them as SMPbots enables composition, stability guarantees, and cross-agent skill sharing.  
**Effort:** Medium

## 10. BYOK Slop Tolerance Calibration

**Repo:** cocapn  
**Files:** `src/config/model-config.ts`, `src/core/slop-test.ts` (new)  
**What:** On first run with a new model, run a calibration suite: simulate 20 known functions, compare outputs to ground truth, compute slop tolerance score. Store in config. Use to gate Soft Actualization aggressiveness.  
**Why:** Different models have wildly different simulation accuracy. A 7B model shouldn't Soft Actualize complex business logic. The calibration ensures Soft Actualization is only used within the model's verified capability.  
**Effort:** Medium

## 11. Seed Versioning with Cryptographic Hashes

**Repo:** cocapn  
**Files:** `src/memory/seed-manager.ts`  
**What:** Version all seed data (facts, relationships, procedures) with content hashes. Implement `seed.diff()` and `seed.merge()` operations. Enable seed sharing between agents via hash-based deduplication.  
**Why:** The SMPbot paper requires Seeds to be immutable and versioned. Currently cocapn memory is mutable JSON. This change enables reproducible agent behavior and seed sharing.  
**Effort:** Medium

## 12. Fishinglog.ai: Soft Actualize Species Classification

**Repo:** fishinglog.ai  
**Files:** `src/classification/`, `src/agent/`  
**What:** For species not yet in the classification model, use Soft Actualization: the LLM simulates classification from visual description, then logs the gap for model fine-tuning. Over time, the model hardens and fewer species need simulation.  
**Why:** Perfect use case for Soft Actualization — edge deployment with limited training data, LLM can approximate for rare species, model improves over time.  
**Effort:** Small

---

*Generated April 2026. 12 improvement ideas across 5 repos. Total estimated effort: 3 large, 7 medium, 3 small.*
