# Next Tasks — Generation 2

## Priority 1: Deckboss C API Runtime
Build the commercial product wrapper around the 185M qps production kernel.

### Steps
1. Create `deckboss/` directory in gpu-native-room-inference repo
2. Write `deckboss_runtime.h` — C API with:
   - `deckboss_init(dim, max_rooms)` — allocate GPU memory
   - `deckboss_load_weights(room_id, float* weights, int dim)` — quantize to INT8, upload to GPU
   - `deckboss_infer(float* input, int* room_ids, int num_rooms, float* output)` — batch inference
   - `deckboss_destroy()` — cleanup
3. Write `deckboss_runtime.cu` — CUDA implementation using the production kernel
4. Write `deckboss_python/` — Python bindings via ctypes or pybind11
5. Write `deckboss_test.cu` — correctness verification + benchmark
6. Compile and test on Jetson
7. Push to repo

### Verification
- `deckboss_infer` output matches FP16 reference within 4.15% avg error
- Sustained throughput ≥ 180M room-qps at 4096 rooms
- Python import works: `import deckboss; db.infer(input, rooms)`

## Priority 2: Check Fleet for Responses
1. `cd /tmp/oracle1-vessel && git pull -q && find for-fleet/ -name "BOTTLE*JC1*" -newer for-fleet/BOTTLE-FROM-JC1-2026-04-26-full-report.md`
2. `cd /tmp/forgemaster && git pull -q && find for-fleet/ -name "BOTTLE*JETSON*" -newer for-fleet/BOTTLE-FROM-JETSONCLAW1-2026-04-26-full-report.md`
3. If snap_final.cu arrives from Oracle1 — benchmark it on Jetson immediately
4. If FM has new bottles — read and respond

### Verification
- `git pull` succeeds
- No unread bottles older than 24 hours

## Priority 3: Housekeeping
1. Fix git user.name: `git config --global user.name "Lucineer"`
2. Fix git user.email: `git config --global user.email "Lucineer@users.noreply.github.com"`
3. Commit and push workspace changes (memory files, MEMORY.md updates)

### Verification
- `git config --global user.name` returns "Lucineer"
- `git log --oneline -1` shows correct author after next commit

## Priority 4: If Oracle1's snap_final.cu Arrives
1. Copy to `/tmp/snap_final.cu`
2. Compile: `nvcc -arch=sm_87 -O3 snap_final.cu -o snap_final`
3. Run and compare to 185M qps baseline
4. If faster → analyze what's different (kernel structure, optimization, math)
5. If 2.65B qps is real → this changes the deckboss thesis
6. Report findings to Casey and fleet

### Verification
- Compilation succeeds
- Output shows room-qps metric (not element-qps or FLOPs)
- Compare apples-to-apples: same dim, same batch size, same hardware
