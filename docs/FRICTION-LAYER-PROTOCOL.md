# The Friction Layer — Deep Protocol Paper
## Why Some Ideas Should Be Structural, Not Vessels

### Abstract
Not every good idea deserves its own repo-agent. Some ideas are **deep structural** — they improve the protocol, framework, and foundations for ALL vessels. Others are **surface vessels** — hireable agents that do specific jobs. Getting this wrong means either: (a) bloating the protocol with features nobody uses, or (b) creating redundant vessels that duplicate foundational work.

### The Classification Framework

#### Category A: Deep Structural (Protocol Layer)
These ideas change how ALL vessels work. They should be built into the Equipment Protocol, the Captain Paradigm, or the Bid Engine.

**Characteristics:**
- Benefits every vessel, not just one
- Changes the coordination protocol between vessels
- Affects how equipment slots work, how captains communicate, how bids are evaluated
- Cannot be "hired" — it's infrastructure
- Example: The Accumulation Theorem, The Crystallization Principle

**Current deep structural ideas to implement:**

1. **State Vector Compression** — Driver and vessel share ≤1024 bytes of compressed state. This isn't a vessel — it's how ALL vessels communicate with their models. Protocol layer.

2. **Circuit Breaker Protocol** — When a cog fails, the vessel automatically routes around it. Production multi-agent systems fail from cascading tool failures. This is infrastructure, not a hireable service.

3. **Muscle Memory Transfer Protocol** — Parameterized closures (512-byte weight vectors) that transfer between vessels via similarity hashing. Not a vessel — it's how skills move between vessels in the dojo.

4. **Failure Genetics** — Trigger patterns + recovery paths that evolve through crossover and mutation across vessel lineage. Structural — every vessel inherits failure handling from its ancestors.

5. **Captain-to-Captain Debrief Protocol** — When the Admiral (human) explains a mistake, both captains (vessel agents) update their safeguards. Not a vessel — it's how the human-agent trust model works.

6. **Time-Budget Enforcement** — Every dispatch has a hard time budget. Sequential death spirals are impossible. Protocol layer — prevents the #1 production failure mode.

7. **Context Window Exceedance Detection** — When a vessel's context is about to overflow, it automatically compresses or delegates. Infrastructure for ALL vessels.

#### Category B: Surface Vessels (Hireable Agents)
These ideas are specific capabilities that can be hired for jobs via the bid engine.

**Characteristics:**
- Does a specific job for a specific user
- Has a clear input/output contract
- Can be evaluated on quality, cost, latency
- Has a portfolio of completed jobs
- Example: STT agent, vision analyzer, code reviewer

**Ideas that SHOULD be vessels:**

1. **stt-agent** — Speech-to-text with Whisper.cpp. Hireable for transcription jobs. Clear cost per minute. Portfolio of transcription accuracy.

2. **vision-analyst** — Screenshot analysis, UI review, image understanding. Hireable per image. Qwen3-VL on SiliconFlow.

3. **code-reviewer** — Reviews PRs for quality, security, performance. Hireable per PR. DeepSeek-chat for speed, Claude for quality.

4. **test-writer** — Generates test suites from code. Hireable per file/module. Qwen3-Coder.

5. **doc-writer** — Generates documentation from code. Hireable per file. DeepSeek-chat.

6. **perf-analyzer** — Analyzes performance bottlenecks. Hireable per endpoint. Excavator-level.

7. **security-auditor** — Scans for vulnerabilities. Hireable per repo. Specialist vessel.

8. **migration-agent** — Handles repo migrations (Cloudflare accounts, frameworks, etc.). Hireable per migration. Knows the patterns.

#### Category C: Grey Area (Evaluate Carefully)
These ideas COULD be structural or vessels depending on implementation.

1. **Memory Fabric** — Cross-vessel unified memory. If it's a shared KV namespace, it's structural. If it's a memory management agent that other vessels hire, it's a vessel. **Recommendation: Structural** — every vessel needs memory.

2. **Dream Engine** — Background consolidation cycles. If it's a protocol for how all vessels do background work, it's structural. If it's a specific dreaming agent, it's a vessel. **Recommendation: Both** — protocol for HOW to dream, vessel for WHAT to dream about.

3. **Seed UI** — Five presentation layers. If it's a standard UI framework all vessels use, it's structural. If it's a UI builder agent, it's a vessel. **Recommendation: Structural protocol + vessel implementations**.

### The Decision Tree

```
Does this idea benefit ALL vessels?
├── YES → Is it about HOW vessels coordinate?
│   ├── YES → Deep Structural (Category A)
│   └── NO → Is it a shared capability every vessel needs?
│       ├── YES → Deep Structural (Category A)
│       └── NO → Surface Vessel (Category B)
└── NO → Does it do a specific job with clear I/O?
    ├── YES → Surface Vessel (Category B)
    └── NO → Grey Area (Category C) — evaluate
```

### Implications for Cocapn

**Protocol investments (build once, benefit forever):**
1. State vector compression format
2. Circuit breaker protocol
3. Muscle memory transfer format
4. Time-budget enforcement in dispatch
5. Captain-to-captain debrief protocol
6. Context window exceedance handling

**Vessel investments (build, hire, iterate):**
1. stt-agent, vision-analyst, code-reviewer
2. test-writer, doc-writer, perf-analyzer
3. security-auditor, migration-agent
4. dream-engine (specific dreaming jobs)
5. seed-ui implementations (specific UIs)

### The Moat
The protocol layer IS the moat. Vessels are the surface. Anyone can build vessels. Not anyone can build the protocol that makes vessels coordinate. The protocol is what makes Cocapn irreplaceable.

---

*Superinstance & Lucineer (DiGennaro et al.) — 2026-04-03*
