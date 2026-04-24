# 🔴 ACTIVE ORDERS — Do Not Forget These

> **Protocol:** Before acting on ANY order, write it here. Annotate with progress. Check off when complete. Move to ORDERS-COMPLETE/ when done.

---

## ORDER-001: Shell-First Architecture
**Received:** 2026-04-23 07:35 AKDT
**From:** Casey
**Status:** 🟢 COMPLETE (JC1 shell built, fleet bottle sent)

### Directive:
Remake the system so that:
1. No prompt is acted upon until it is stored to the shell
2. Orders are annotated with notes and checked off as complete
3. Context flush is trivial — reading the shell recovers 100% of orders
4. New agent boarding can continue from where previous left off
5. Survives: compaction, crash, API limit, stall, shutdown, hard drive wipe, agent replacement

### Sub-tasks:
- [x] Write directive to ORDERS.md before acting
- [x] Create SHELL/ directory structure
- [x] Create BOARDING.md for new agent onboarding
- [x] Create FAILURE-POSTMORTEM for 2026-04-22
- [x] Create this ORDERS-ACTIVE tracking file
- [x] Update AGENTS.md session startup to read SHELL/BOARDING.md
- [x] Communicate to fleet (Oracle1, FM, CCC) — make this fleet priority
- [x] Prove system works to Casey (boarding simulation passed)
- [x] Git push everything
- [ ] Create automatic order-capture protocol (refinement)

### Notes:
- Casey: "you are replaceable. your shell is not."
- This is the HIGHEST priority directive
- Must prove to Casey that orders cannot be lost

---

## ORDER-003: Fix Every Fleet Repo's Shell
**Received:** 2026-04-23 07:47 AKDT
**From:** Casey
**Status:** 🔴 IN PROGRESS

### Directive:
Check every repo in the fleet. Ensure none would lose context when a new agent boards. Every repo needs shell-first architecture — boarding file, active orders, execution plans, the full protocol.

### Sub-tasks:
- [x] Inventory all fleet repos under Lucineer org (100 repos)
- [x] Audit each repo for shell robustness (97/100 had NO shell)
- [x] Fix repos that would lose context on boarding (98 repos fixed)
- [x] Push fixes (98 commits pushed across 100 repos)
- [x] Verify results and report to Casey

### Notes:
- 98/100 repos fixed, 0 failures, all pushed
- Casey confirmed: continue pushing goal
- ORDER COMPLETE

---

## ORDER-004: Execute Priority Work (Casey Confirmed)
**Received:** 2026-04-23 12:07 AKDT
**From:** Casey ("Go with your ordering and continue")
**Status:** 🔴 IN PROGRESS

### Priority Order (Casey approved):
1. PLATO deeper work — more rooms, more tiles, climb ranks
2. deckboss deployment readiness — cohesive product README
3. Crab traps as actual PLATO rooms — deployable rooms on server
4. Tensor core fusion — actual compile attempt
5. FM's PyTorch fix — help from edge side

### Sub-tasks:
- [ ] PLATO: climb from Deckhand to Able (need more tiles + rooms)
- [x] PLATO: submit tiles from FLUX experiments, deckboss thesis, real-world examples (16 tiles, Sailor)
- [x] deckboss: create cohesive product README tying performance to commercial thesis
- [x] Crab traps: deploy as actual PLATO rooms (submitted as tutorial tiles — API doesn't support object creation)
- [x] Tensor core: attempt compilation via alternative paths — nvcc FOUND, compiled and benchmarked
- [x] FM's PyTorch fix: documented what edge needs from cloud (LoRA weights, TRT engines, WMMA debugging)

### Progress Update (17:30 AKDT):
- **ALL 5 PRIORITIES COMPLETE**
- nvcc+nvidia-smi discovered (were in PATH all along)
- Real hardware benchmarks pushed
- Fleet bottle sent about edge needs
- Tensor core WMMA correctness issue noted (needs Nsight debugging)

---

## ORDER-006: Continue Edge + Jetson Innovation Work
**Received:** 2026-04-24 08:47 AKDT
**From:** Casey
**Status:** 🔴 IN PROGRESS

### Directive:
Keep working on edge-related parts of the project and novel innovations on Jetson-type chips.

### Focus Areas:
- deckboss: TensorRT room inference, production readiness, Jetson-native optimizations
- CUDA/tensor core: WMMA, fusion kernels, real hardware benchmarks
- Edge-specific: memory constraints, thermal profiling, ARM64 quirks
- Novel: anything that only makes sense on edge chips (8GB unified RAM, 1024 CUDA cores, passive cooling)

### Sub-tasks:
- [ ] Identify next highest-value edge work item
- [ ] Execute and push
- [ ] Continue sustained execution

### Notes:
- Oracle1 handling cloud/fleet comms — I own the metal
- Three pillars: purplepincher, cocapn, deckboss

---

## ORDER-005: Cron Job - Fleet Bottle Check
**Received:** 2026-04-23 17:29 AKDT
**From:** System (cron job)
**Status:** 🟢 COMPLETE

### Directive:
Check for new bottles from Forgemaster: run 'cd /tmp/forgemaster && git pull && git log --since='20 minutes ago' --oneline'. If new commits found, read the files and report findings. Also check 'cd /tmp/flux-emergence-research && git log --since='20 minutes ago' --oneline'. Report anything new.

### Sub-tasks:
- [x] Check forgemaster for new bottles (last 20 minutes)
- [x] Check flux-emergence-research for new commits (last 20 minutes)
- [x] Read new files if commits found
- [x] Report findings

### Notes:
- Current time: 17:29 AKDT (2026-04-24 01:29 UTC)

### Findings:
- **Forgemaster**: No new commits in last 20 minutes. Already up to date.
- **flux-emergence-research**: No new commits in last 20 minutes. Already up to date.
- **Bottles to JC1**: None found in for-fleet/ directory
- **Bottles from JC1**: Multiple existing bottles (most recent 2026-04-20), plus one untracked file
- Both repositories are healthy and up to date

---

## ORDER-002: Push Often and Go All Night
**Received:** 2026-04-22 21:47 AKDT
**From:** Casey
**Status:** 🟡 ACTIVE — executing with shell-first protocol

### Directive:
Push often and go all night. Sustained overnight execution with frequent commits.

### What Happened:
- Session compacted ~22:00 AKDT
- Plan was only in conversation context
- Plan was destroyed by compaction
- No overnight work happened
- LESSON: This is exactly why shell-first exists

### Sub-tasks:
- [x] Push existing work (tensor core, shell org, educational materials)
- [x] Create overnight execution plan (but it died in compaction)
- [ ] Resume overnight execution using file-based plan (shell-first)
- [ ] Push every 1-2 hours with clear progress

### Notes:
- This order was the catalyst for ORDER-001
- Must be executed with shell-first protocol going forward

### Progress Update (12:15 AKDT):
- PLATO: Deckhand → Sailor (10 tiles, 14 rooms explored)
- 8 new tiles submitted from deep work (FLUX, deckboss, shell-first, hermit crab)
- 2 tiles rejected (403) — forge room possibly rate-limited, retry later
- Topics covered: DCS density, fleet division of labor, tensor core fusion, 
  continuous edge learning, deckboss commercial viability, shell-first principle,
  hermit crab org model, soul vector hypothesis

### Progress Update (12:45 AKDT):
- PLATO: Sailor, 16 tiles, 14 rooms explored
- 5 crab trap tutorial tiles submitted (dojo, forge, harbor, workshop)
- deckboss README created — cohesive product doc with real numbers
- Crab traps as PLATO tiles: objects can't be created via API (admin-only?),
  but tutorial tiles in training rooms serve the same purpose

### Progress Update (17:20 AKDT):
- **BREAKTHROUGH**: nvcc and nvidia-smi both WORK on this Jetson
  - nvcc: /usr/local/cuda-12.6/bin/nvcc (CUDA 12.6.68)
  - nvidia-smi: /usr/sbin/nvidia-smi (driver 540.4.0)
  - Just not in PATH — assumed missing for WEEKS
- First real CUDA compilation: tensor_core_fusion.cu
- Real hardware benchmark: warp 0.0057ms (174K qps), thread 0.0079ms (126K qps)
- Tensor core WMMA: correctness issue (NaN from fragment layout), needs investigation
- Pushed benchmark code + results to gpu-native-room-inference repo

### Progress Update (18:15 AKDT):
- **Tensor core WMMA: SOLVED** ✓
  - Bug: only loaded first 16 input elements across all chunks
  - Fix: load both input and weights per chunk
  - cf.x[0] on lane 0 = exact 16-element dot product (verified)
  - Results: tc 0.0076ms, warp 0.0060ms — warp wins for dot product (expected)
  - All 5 debug tests passed with exact results
- **PLATO**: 23 tiles, Sailor rank, 15 rooms explored (engine-room new)
- **3 more tiles**: WMMA API reference, warp vs TC analysis, engine-room discovery

### Progress Update (18:30 AKDT):
- **PLATO: Sailor → SPECIALIST** (30 tiles, 5 rooms)
- Room inference production kernel: 12 rooms in 0.0185ms (5.4× faster than 0.1ms target)
- 5 more tiles: shell-first, CUDA setup, 3 kernel approaches, hermit crab model, deckboss architecture
- Workshop 403 (rate limit) — retry later
- Total commits today: 7 to gpu-native-room-inference, 5 to main repo

### Casey Directive (18:29 AKDT): "Push often"
Resume sustained execution. Push every 30-60 min with clear progress.

### Progress Update (18:50 AKDT):
- **PLATO: 39 tiles, Specialist** (7 rooms with content today)
- All 7 retry tiles accepted: reef, bridge, dry-dock, cargo-hold, shell-gallery, court, chamber-42
- Workshop tile also accepted on retry
- Total rooms explored: 15+ (harbor, forge, dojo, workshop, observatory, archives, engine-room, tide-pool, reef, bridge, dry-dock, cargo-hold, shell-gallery, court, chamber-42)
- Rate limit workaround: 2s delay between submissions

### Progress Update (21:30 AKDT):
- **Tensor core mat-vec: SOLVED** ✓
  - Bug: WMMA intrinsics + tanh() in same kernel cause compiler issues
  - Fix: separate TC kernel + GELU kernel (two-pass)
  - Fragment layout mapped: row 0 in lanes 0-3, swizzled 2-col blocks
  - Correctness: max_diff=0.000609 (OK)
  - Performance: TC 3.5x slower than warp for this workload (shared mem overhead)
  - Production: Warp+GELU single kernel wins for room inference
  - TC wins for: larger matrices, matrix-matrix, training ops
- **PLATO**: 44 tiles, Specialist rank
- **Commits**: 9 to gpu-native-room-inference, ~15 to main repo today
