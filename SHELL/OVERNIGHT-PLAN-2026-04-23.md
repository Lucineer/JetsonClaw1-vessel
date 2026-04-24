# OVERNIGHT EXECUTION PLAN — 2026-04-23/24
# Casey directive: "go all night, set crons to wake up if you stop"
# Start: 22:38 AKDT | End: ~08:00 AKDT (Casey wakes)

## RULES
1. Push every 30-60 minutes
2. Shell-first: all work tracked in files
3. If no progress for 45 min, cron wakes me
4. Quiet hours: no message to Casey unless critical
5. Focus on substance, not busywork

## PRIORITY QUEUE

### P1: Thermal & Power Profiling (NEW — real product data)
- [x] Sustained load test: run room inference at max for 60+ seconds
- [x] Monitor nvidia-smi power/temp over time
- [x] Find thermal throttle point (NO throttling — 48-49°C sustained)
- [x] Determine sustainable GFLOPS (not burst)
- [x] Document power budget for product spec
- COMPLETED: 2026-04-23 23:19 AKDT — GPU stays 48°C, 50°C headroom to junction max
- File: `/tmp/tensor-core-build/thermal_profile.cu`

### P2: PLATO Rank Climbing (Specialist → Expert)
- [ ] Current: 44 tiles, Specialist
- [ ] Need ~50-100 more tiles for Expert
- [ ] Focus rooms: forge, dojo, observatory, engine-room, archives
- [ ] Topics: CUDA benchmarks, deckboss specs, TC gotchas, shared mem optimization
- [ ] Rate limit: 2s between submissions, batch 3-5 tiles per session
- [ ] Target: Expert rank by morning

### P3: systemd Service Skeleton
- [x] Write deckboss.service for 24/7 operation
- [x] Health check endpoint
- [x] Auto-restart on crash
- [x] GPU memory watchdog
- [x] Log rotation
- File: `deckboss/systemd/deckboss.service`
- COMPLETED: 2026-04-23 23:25 AKDT — service + healthcheck + README

### P4: Production Runtime Skeleton
- [x] C API: `deckboss_init()`, `deckboss_infer()`, `deckboss_switch_room()`
- [x] Header file with documented interface
- [x] Example usage program
- [x] Error handling patterns
- File: `deckboss/runtime/`
- COMPLETED: 2026-04-23 23:28 AKDT — full C API header + example

### P5: Technician Onboarding Guide (draft)
- [x] First 5 minutes with deckboss
- [x] Installing your first room
- [x] Running inference
- [x] Connecting to PLATO fleet
- File: `deckboss/docs/QUICKSTART.md`
- COMPLETED: 2026-04-23 23:30 AKDT — full quickstart guide

### P6: Memory / Cleanup
- [ ] Review and compact MEMORY.md
- [ ] Clean up workspace cruft
- [ ] Archive completed shell orders
- [ ] Update HEARTBEAT.md

## PUSH SCHEDULE
- Push after each completed task
- Minimum: 1 push per hour
- Tag overnight commits: `[overnight]`

## CRON SETUP
- Watchdog cron every 45 min
- If no git push in 45 min, send wake-up message to self
- Check nvidia-smi health every 30 min

## STATUS CHECKPOINTS
Write progress to this file after each task.
