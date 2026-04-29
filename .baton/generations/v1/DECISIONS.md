# Key Decisions — Generation 1

## GPU Architecture
1. **INT8 over FP16 for production** — 36% faster, 50% memory, 4.15% avg error. 99.2% top-256 recall sufficient for ranking. Rationale: bandwidth-bound on Jetson, INT8 halves memory traffic.

2. **Reject CUDA Graphs on Jetson** — 4-9× slower. Graph replay overhead (34μs) exceeds raw kernel launch cost (3.5μs) at edge scale. Data-center optimization that hurts on small GPUs.

3. **Reject shared memory tiling** — L2 cache (2MB) provides equivalent locality for sequential access patterns. Extra copy to shared memory adds 13-33% overhead.

4. **Reject cuBLAS/cuSPARSE for room inference** — 34μs framework call overhead dominates at ≤6K rooms. Custom V7 kernel 10-59% faster. Libraries only win at 8K+ rooms.

5. **128-thread blocks > 256-thread blocks** — V17 (128t, 4 rooms/block) 14% faster. Better SM occupancy on Orin's 1024-core configuration.

6. **Multi-tenant batching is the architecture** — Merge all inference into one batch. GPU scheduler makes it 2.61× faster. Never isolate tenants into separate streams.

7. **Variable-dim serving rejected** — 40× slower due to O(n²) cumulative offset calculation. Always pad to uniform dim=256.

## Publishing
8. **Fixed all 6 crate repos before publishing** — Tests had never compiled (written alongside buggy code). Found 4 distinct bugs in cuda-assembler, 3 in cuda-forth, 2 in cuda-biology, 1 in cuda-energy, 1 in cuda-instruction-set.

9. **SuperInstance PAT for Oracle1 vessel** — Casey provided PAT, switched remote to HTTPS with embedded token. Push confirmed working. Stored at ~/.config/superinstance/pat.

## Infrastructure
10. **z.ai GLM-5-turbo as fallback** — DeepSeek credits expired 2026-04-24. Subagents fail on DeepSeek billing. Main session works on GLM.

11. **target/ dirs OOM-kill git push** — Multiple repos had target/ committed. Fixed with .gitignore + git rm --cached + force push. Lesson: always .gitignore before first build.
