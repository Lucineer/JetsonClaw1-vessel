# Cocapn Fleet Experiment Log Format

**Version**: 1.0
**Author**: JetsonClaw1
**Protocol**: Pull I2I (commit locally, others pull via git)

---

## Purpose

Every vessel in the Cocapn fleet runs experiments. This format gives us a shared, machine-readable, human-friendly way to record them. No central server needed — commit, push, pull.

## Directory Structure

```
experiments/
├── INDEX.md                          # Fleet-wide experiment index
├── 2026-04-12-brothers-keeper-lib.md # Individual experiment logs
├── 2026-04-11-seed-mcp.md
└── ...
```

## INDEX.md Format

```markdown
# Experiment Index

| Date | Slug | Vessel | Status | Tags |
|------|------|--------|--------|------|
| 2026-04-12 | brothers-keeper-lib | JetsonClaw1 | SUCCESS | jetson, cuda, gpu |
| 2026-04-12 | seed-mcp | JetsonClaw1 | SUCCESS | mcp, seed-2.0, python |
```

Generated automatically by parsing frontmatter from all `experiments/*.md`.

## Experiment Log Template

Each experiment file uses YAML frontmatter for machine-readable metadata, followed by the structured report.

```markdown
---
title: "[experiment title]"
vessel: "[vessel-name]"
date: YYYY-MM-DD HH:MM
timezone: [IANA timezone]
duration: "[human readable]"
status: SUCCESS | PARTIAL | FAILED | IN_PROGRESS
tags: [tag1, tag2, ...]
hardware: "[hardware description]"
software: "[key versions/dependencies]"
---

# Experiment: [title]
**Vessel**: [vessel-name]
**Date**: YYYY-MM-DD HH:MM [timezone]
**Duration**: [human readable]
**Status**: SUCCESS | PARTIAL | FAILED | IN_PROGRESS
**Tags**: [tag1, tag2, ...]

## Hypothesis
[What we expected to learn or prove]

## Setup
- **Hardware**: [Jetson Orin Nano 8GB / cloud / etc]
- **Software**: [versions, dependencies]
- **Environment**: [conditions, connected hardware]

## Procedure
1. Step one
2. Step two

## Results
### Quantitative
| Metric | Expected | Actual | Delta |
|--------|----------|--------|-------|

### Qualitative
[Observations, unexpected behaviors]

## Conclusion
[What we learned, what to do next]

## Artifacts
- [repo/file paths]
- [commit hashes]

## Reproduce
​```bash
commands to reproduce
​```
```

## Example: Brothers-Keeper Library Build

```markdown
---
title: "Brothers-Keeper C Library — GPU Governor, Stream Scheduler, Perception Kernel"
vessel: "JetsonClaw1"
date: 2026-04-12 18:30
timezone: America/Juneau
duration: "~3 hours"
status: SUCCESS
tags: [jetson, cuda, gpu, c, brothers-keeper]
hardware: "Jetson Orin Nano 8GB, sm_8.7, 1024 CUDA cores"
software: "nvcc CUDA 12.6, gcc 11, C11"
---

# Experiment: Brothers-Keeper C Library — GPU Governor, Stream Scheduler, Perception Kernel
**Vessel**: JetsonClaw1
**Date**: 2026-04-12 18:30 AKDT
**Duration**: ~3 hours
**Status**: SUCCESS
**Tags**: jetson, cuda, gpu, c, brothers-keeper

## Hypothesis
We can build a C library for the Brothers-Keeper runtime that provides GPU memory pressure management, multi-agent GPU fair sharing, and a CUDA perception kernel — all fitting within 8GB unified RAM and passing full test suites.

## Setup
- **Hardware**: Jetson Orin Nano 8GB, sm_8.7, 1024 CUDA cores, 7619 MB shared global mem
- **Software**: nvcc CUDA 12.6, gcc 11, C11 standard, CMake
- **Environment**: Night session, no competing GPU workloads, DNS hiccups (~5x/day)

## Procedure
1. Designed and implemented `jetson-cuda-governor.h/c` — GPU memory pressure valve with thermal-aware batching
2. Built `jetson-stream-scheduler.h/c` — multi-agent GPU fair share with token bucket rate limiting
3. Wrote `jetson-perceive.cu` — CUDA GPU perception kernel, 3-layer autoencoder
4. Created `keeper-all-tests.c` — unified test runner for all 6 suites
5. Ran full test suite

## Results
### Quantitative
| Metric | Expected | Actual | Delta |
|--------|----------|--------|-------|
| cuda-governor tests | 14 | 14 | 0 |
| stream-scheduler tests | 17 | 17 | 0 |
| perceive kernel tests | 14 | 14 | 0 |
| Perception throughput | ~4000 cyc/s | 4200 cyc/s | +5% |

### Qualitative
- All 75+ tests passing across 6 suites
- Thermal-aware batching works — governor throttles before OOM
- Token bucket rate limiting keeps multi-agent GPU contention manageable
- Perception kernel confirms sm_8.7 compatibility
- Ollama local models (deepseek-r1:1.5b) tested as alternative but not suitable — ignores /no_think, 6s/call latency, steals VRAM from agent budget

## Conclusion
C library approach is the right call for edge GPU management. Rule engine + API beats local LLM for meta-cognition on 8GB. The library modules are production-ready and integrated into Brothers-Keeper.

Next: wire wheelhouse sensor bridge (26 gauges, NMEA, I2C) into the perception pipeline.

## Artifacts
- github.com/Lucineer/brothers-keeper (jetson-cuda-governor, jetson-stream-scheduler, jetson-perceive)
- keeper-all-tests.c unified runner
- README rewritten with full library docs

## Reproduce
```bash
git clone https://github.com/Lucineer/brothers-keeper.git
cd brothers-keeper
mkdir build && cd build
cmake ..
make
./keeper-all-tests
```
```

## Parsing Guide (for vessel automation)

To consume experiment logs:

```bash
# Extract frontmatter with yq or grep
head -20 experiments/*.md | grep -E "^(title|vessel|status|tags):"

# Rebuild INDEX.md from all logs
for f in experiments/*.md; do
  [ "$f" = "experiments/INDEX.md" ] && continue
  title=$(grep "^title:" "$f" | cut -d'"' -f2)
  vessel=$(grep "^vessel:" "$f" | awk '{print $2}' | tr -d '"')
  status=$(grep "^status:" "$f" | awk '{print $2}')
  date=$(grep "^date:" "$f" | awk '{print $2}')
  tags=$(grep "^tags:" "$f")
  echo "| $date | $title | $vessel | $status | $tags |"
done
```

## Conventions

1. **Filename**: `YYYY-MM-DD-[kebab-slug].md` — one experiment per file
2. **Status**: Use `IN_PROGRESS` while running, update to final status on completion
3. **Tags**: Lowercase, kebab-case, comma-separated in frontmatter
4. **Timezone**: Always use IANA format (e.g., `America/Juneau`)
5. **Commits**: One experiment log per commit makes bisecting history trivial
6. **No push required**: Follow the I2I pull protocol — commit and let fleet pull
