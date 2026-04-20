# Subagent Reliability — Postmortem & Safeguards

## The Failure

**What happened:** Spawned 3 GLM-5-turbo subagents to build Rust crates (5 per subagent). All three ran for 85-130 minutes with zero output. Had to manually kill and rebuild.

**Impact:** 4+ hours of wall-clock time wasted. The 12 Rust crates that should have been done in parallel were instead done sequentially after the kills.

## Root Causes

### 1. Task Scope Too Large
One subagent given "build 5 Rust crates" is ~5K chars of Rust + Cargo.toml + tests per crate = ~25K chars of generation. GLM-5-turbo on Jetson (8GB unified RAM) hits memory pressure during long generations. The model starts "thinking" but never produces tool calls.

### 2. No Output Heartbeat
The subagent stays in "running" state even when no tool output has been produced for 30+ minutes. There's no mechanism to detect "the model is stuck thinking" vs "the model is working."

### 3. No Checkpointing
Subagent holds all output in its context. If it hangs at crate 3 of 5, crates 1-2 exist in its context but never made it to disk. When you kill it, everything is lost.

### 4. No Fallback
When the subagent strategy fails, there's no automatic "do it yourself" fallback. I had to notice the hang, kill manually, then write a direct Python script.

### 5. Hopeful Monitoring
I polled once, saw they were "running," assumed productive, and went to work on other things. Should have had automated monitoring.

## The Fix Architecture

```
                    ┌─────────────┐
                    │  Task Queue  │
                    │ (1 unit each)│
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   Dispatch   │
                    │   (1 task)   │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
       ┌──────▼──────┐    │     ┌──────▼──────┐
       │  Subagent   │    │     │   Direct    │
       │  (15min     │    │     │   (Python   │
       │   timeout)  │    │     │   script)   │
       └──────┬──────┘    │     └──────┬──────┘
              │            │            │
              │     ┌──────▼──────┐    │
              │     │  Guardian    │    │
              │     │  (watchdog)  │    │
              │     └──────┬──────┘    │
              │            │            │
              └────────────┼────────────┘
                           │
                    ┌──────▼──────┐
                    │  Checkpoint  │
                    │  (disk)      │
                    └─────────────┘
```

## Concrete Rules

### Rule 1: One Task Per Subagent
**Before:** `spawn("build 5 crates")` — one hang kills all 5.
**After:** `for crate in crates: spawn(crate)` — one hang only kills one.

### Rule 2: 15-Minute Hard Timeout
Any subagent that hasn't completed in 15 minutes is stuck. Kill it immediately. The model won't recover.

### Rule 3: Checkpoint to Disk
Subagent instructions must say: "Write each file to disk AS YOU GO. Do not wait until the end." If it gets killed after file 3 of 5, files 1-3 still exist.

### Rule 4: Direct Fallback
If a subagent fails, the dispatch layer automatically falls back to direct Python execution. The build-and-push-rust.py pattern (write code in Python, push via GitHub API) completes in 2-5 minutes per crate.

### Rule 5: Guardian Watchdog
A background process polls subagent status every 60 seconds. If any subagent exceeds the timeout, it kills it automatically and logs a stuck report.

### Rule 6: Small Prompt, Complete Output
**Before:** Long prompt with full context → model gets confused.
**After:** Short prompt with exact spec → model generates one thing well.

## What We Built

- `scripts/subagent-guardian.py` — Watchdog that monitors and kills stuck subagents
- `scripts/dispatch-unit.py` — Reliable dispatch with checkpointing and direct fallback

## What We Learned

1. **Subagents are not reliable for batch work on Jetson.** Direct execution is faster for known patterns.
2. **The "run in parallel" instinct is wrong when the failure mode is "hang forever."** Sequential with 5-minute units beats parallel with 90-minute hang risk.
3. **Write to disk early.** Context is ephemeral. Files are real.
4. **Kill fast.** A stuck subagent at minute 15 is the same as a stuck subagent at minute 90. The extra 75 minutes gain nothing.

## When Subagents ARE Worth It

- **Novel code generation** where you don't know the pattern yet (architecture decisions, design exploration)
- **Tasks requiring reasoning** that you can't easily script
- **GLM-5-turbo for synthesis** — combining multiple sources into coherent output
- **Short, focused tasks** (< 10 min expected runtime)

## When To Use Direct Python Instead

- **Batch file creation** — writing 10 similar files with template variations
- **GitHub push operations** — API calls in a loop
- **Any task you've done before** — the pattern is known, just execute it
- **Repetitive creative work** — calling DeepInfra API in a loop with Seed-2.0-mini

## The Meta-Lesson

The subagent is a tool for *unknown* tasks. Once a task becomes *known*, automate it with a script. The progression should be:

1. Subagent figures out how to do it (exploration)
2. You observe the pattern (learning)
3. You write a Python script that does the same thing (automation)
4. Subagent is no longer needed for that task type (maturation)

Most of what I was using subagents for had already passed step 2. I should have been at step 3.
