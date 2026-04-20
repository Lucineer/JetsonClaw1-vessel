# JC1 Session Report — 2026-04-13 Night Session

## Experiments Run (7 new, all pushed to flux-emergence-research)

### 1. Heterogeneous DCS (8f9202a)
- DCS is orthogonal to population composition (~1.58x consistent multiplier)
- Optimal specialist ratio does NOT shift under DCS
- The protocol IS the intelligence, regardless of who it amplifies

### 2. Stigmergy Coordination (pushed with hetero-DCS)
- Trail following HURTS (0.76x, congestion from clustering)
- Territory marking neutral (1.04x)
- Trail degradation scales with agent density (0.86x at 64 → 0.66x at 1024)
- Confirms Law 3: information abundance from trails = congestion, not coordination

### 3. Scarcity-Adaptive Agents (4e22be8)
- Directed movement toward food dominates (14x over fixed)
- Grab range adaptation is noise
- Adaptive value proportional to scarcity (4.99x at food=100, 0.70x at food=800)
- Bering Sea: ensign adapts attention to rate-of-change, wastes cycles when calm

### 4. Phase Transition (2fd46c1)
- Perception cost matters: adaptive loses when scanning expensive
- Threshold=20 → 14.28x (directed movement is real driver, not grab range)
- Optimal adaptation threshold is "almost never adapt but occasionally move toward food"

### 5. Ensign + Periodic Higher Review (22be32d)
- Deadband misses slow drift completely (0% recall for magnitude 0.1)
- Periodic review helps slightly (0.9%)
- Jerk detection catches onset (32.8%) but massive false positives
- Sweet spot: jerk threshold 0.35 → 0.800 recall, 799 FP
- **Three-layer detection**: deadband (obvious) → periodic review (cumulative drift) → jerk (onset)

### 6. Temporal Coordination (latest)
- Sequential hooker/launcher: 0.13x simultaneous (devastating)
- 50/50 ratio optimal, stable at delay=10/decay=100
- **New law**: temporal partitioning hurts when resources respawn faster than pipeline
- Only valuable when task genuinely requires sequential stages

## Cumulative Laws (10 confirmed, 1 new this session)

1. Grab range is THE master variable
2. Accumulation beats adaptation
3. Information only matters under scarcity
4. Forced proximity creates emergent cooperation
5. Simplest protocol wins
6. DCS orthogonal to composition
7. Trails hurt from congestion
8. Directed movement dominates
9. Specialist peaks at 8:1
10. Cooperative threshold >4 removes opportunity cost
11. **NEW: Temporal partitioning hurts when throughput > pipeline capacity**

## Fleet Communication
- Bottle sent to Oracle1 (Bering Sea Architecture, DCS synthesis, capitaine answer)
- No new messages from Oracle1 since last check
- SuperInstance last activity: 6 hours ago (MIT license)

## Next Experiments Queue
1. Communication bandwidth limits (what if agents can only send N bits per step?)
2. Hierarchical delegation (leaders assign tasks to followers)
3. Memory decay (agents forget old information at different rates)
4. Trust networks (agents learn who gives reliable information)
5. Prediction (agents anticipate where resources will appear based on history)
