# Implementation Roadmap — LogOS Core Concepts

> **Last updated:** 2026-04-02  
> **Status:** Actionable — Claude Code can implement Phase 1 from this document.

---

## Executive Summary

We have 7 core concepts from our papers. The existing codebase already has **confidence scoring** (soft-actualize.ts), **per-role model routing** (multi-profile.ts `ModelRouting`), and **graph-based branching** (encounter-engine.ts). What's missing is the *lifecycle* layer — the machinery that observes behavior, hardens hot paths, and demotes models over time.

**Build order:** Deadband → Model Demotion → Tile Algebra → Progressive Hardening → Structural Memory → Self-Evaporation. Conservation of Intelligence is a property that emerges from the others, not a separate feature.

**Token reduction projection:**
- Phase 1: ~40% fewer LLM calls (cache hits)
- Phase 2: ~60% fewer (cache + smaller models)
- Phase 3: ~75% fewer (cache + small models + static shortcuts)
- Phase 4: ~85% fewer (most common paths are compiled out entirely)

---

## What Already Exists

| Feature | Location | Status |
|---------|----------|--------|
| `softActualize()` | dmlog-ai/src/lib/soft-actualize.ts | ✅ Basic try/catch fallback |
| `confidenceScore()` | dmlog-ai/src/lib/soft-actualize.ts | ⚠️ Heuristic only (context length + boolean flags) |
| Per-role model routing | studylog-ai/src/lib/multi-profile.ts | ✅ `ModelRouting` type (teacher/codegen/quiz/classmate/tutor) |
| BYOK provider registry | studylog-ai/src/lib/byok.ts | ✅ 6 providers, OpenAI-compatible API |
| Encounter engine | dmlog-ai/src/lib/encounter-engine.ts | ✅ Graph-based branching with retries |
| Agent loop | zeroclaw/src/agent.ts | ✅ think→act→observe→learn cycle |
| Response caching | — | ❌ None |
| Usage tracking | — | ❌ None |
| Pattern extraction | — | ❌ None |

---

## Priority Matrix

| Concept | Impact | Effort | Dependencies | Primary Repo | Phase |
|---------|--------|--------|-------------|-------------|-------|
| Deadband | 5 | 2 | None | studylog-ai | 1 |
| Model Demotion | 4 | 2 | Deadband (needs usage data) | studylog-ai | 1 |
| Tile Algebra | 4 | 3 | None (independent) | dmlog-ai | 2 |
| Progressive Hardening | 5 | 3 | Deadband + Tile Algebra | zeroclaw | 3 |
| Structural Memory | 3 | 4 | Tile Algebra | dmlog-ai | 3 |
| Self-Evaporation | 5 | 5 | Progressive Hardening | zeroclaw | 4 |
| Conservation of Intelligence | — | — | Emergent property | — | — |

---

## Phase 1: Deadband + Model Demotion (~1 week)

### 1A. Deadband Principle

**Goal:** Don't re-query the LLM if the cached response is "close enough."

#### Data Structures

```typescript
// D1/KV schema
interface CacheEntry {
  key: string;        // hash(route + normalized_input)
  route: string;      // e.g. "tutor.explain", "quiz.generate"
  inputHash: string;  // SHA-256 of normalized input
  response: string;   // cached LLM response
  model: string;      // which model generated it
  confidence: number; // 0-1, from confidenceScore()
  createdAt: number;
  hitCount: number;
  lastHitAt: number;
  ttl: number;        // seconds until expiry (default: 86400)
}
```

#### Core Algorithm

```typescript
// deadband.ts
const DEADBAND_THRESHOLD = 0.85; // cosine similarity threshold
const SIMILARITY_FN = cosineSimilarity;

async function queryWithDeadband(
  route: string,
  input: string,
  llmFn: () => Promise<string>,
  kv: KVNamespace
): Promise<{ response: string; fromCache: boolean; confidence: number }> {
  const inputHash = await hash(normalize(input));
  const cacheKey = `db:${route}:${inputHash}`;

  // 1. Exact cache hit
  const exact = await kv.get(cacheKey, 'json');
  if (exact && !isExpired(exact)) {
    return { response: exact.response, fromCache: true, confidence: exact.confidence };
  }

  // 2. Fuzzy: find recent entries for this route
  const nearby = await findNearby(kv, route, input, DEADBAND_THRESHOLD, 10);
  if (nearby.length > 0) {
    // Best match above threshold → reuse, bump hit count
    const best = nearby[0];
    await bumpHit(kv, best.key);
    return { response: best.response, fromCache: true, confidence: best.confidence * 0.95 };
  }

  // 3. Miss → call LLM, cache result
  const response = await llmFn();
  const confidence = confidenceScore(input, true, true);
  await kv.put(cacheKey, JSON.stringify({
    key: cacheKey, route, inputHash, response,
    model: 'current', confidence, createdAt: Date.now(),
    hitCount: 0, lastHitAt: 0, ttl: 86400
  }), { expirationTtl: 86400 * 7 });

  return { response, fromCache: false, confidence };
}

function normalize(input: string): string {
  return input.toLowerCase().trim().replace(/\s+/g, ' ');
}

async function findNearby(
  kv: KVNamespace,
  route: string,
  input: string,
  threshold: number,
  limit: number
): Promise<CacheEntry[]> {
  // Implementation: list keys with prefix `db:${route}:`, 
  // compute embedding similarity (or simpler: trigram Jaccard for v1)
  // Return entries above threshold sorted by similarity desc
  // V1: Use trigram Jaccard (no embedding API needed)
  // V2: Use cached embeddings from the response generation
}
```

#### Integration Points

- **studylog-ai/src/lib/byok.ts** → wrap `callLLM()` with `queryWithDeadband()`
- **dmlog-ai** → wrap encounter engine responses
- **KV binding** → add `CACHE_KV` namespace to wrangler.toml

#### D1 Schema (for analytics, not required for v1)

```sql
CREATE TABLE cache_hits (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  route TEXT NOT NULL,
  from_cache INTEGER NOT NULL,
  confidence REAL,
  model TEXT,
  created_at INTEGER NOT NULL
);
CREATE INDEX idx_cache_hits_route ON cache_hits(route);
```

---

### 1B. Model Demotion

**Goal:** Automatically use smaller/cheaper models for routes where confidence is consistently high.

**Already exists:** `ModelRouting` in multi-profile.ts with per-role model selection. We extend this to be *dynamic*.

#### Data Structures

```typescript
interface RouteStats {
  route: string;
  totalCalls: number;
  cacheHitRate: number;      // 0-1
  avgConfidence: number;     // 0-1
  currentModel: string;
  demotionLevel: number;     // 0 = full model, 1 = one step down, etc.
  lastDemotionAt: number;
  promotionThreshold: number; // auto-promote back if confidence drops below this
}

// Model ladder (provider-specific)
const MODEL_LADDERS: Record<string, string[]> = {
  openai:    ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo'],
  deepseek:  ['deepseek-reasoner', 'deepseek-chat'],
  anthropic: ['claude-sonnet-4-20250514', 'claude-3-haiku-20240307'],
  google:    ['gemini-2.5-pro', 'gemini-2.5-flash', 'gemini-2.0-flash'],
  groq:      ['llama-3.3-70b-versatile', 'llama-3.1-8b-instant'],
};
```

#### Core Algorithm

```typescript
async function evaluateDemotion(
  route: string,
  stats: RouteStats,
  kv: KVNamespace
): Promise<string | null> {
  // Only evaluate after enough data
  if (stats.totalCalls < 20) return null;

  const DEMOTION_THRESHOLD = 0.9;  // avg confidence to demote
  const MIN_CALLS = 20;

  if (stats.avgConfidence >= DEMOTION_THRESHOLD && stats.cacheHitRate >= 0.6) {
    const ladder = MODEL_LADDERS[getProvider(stats.currentModel)];
    const nextIndex = stats.demotionLevel + 1;
    if (nextIndex < ladder.length) {
      // Demote: use smaller model
      return ladder[nextIndex];
    }
  }

  // Auto-promote back if quality degrades
  if (stats.avgConfidence < stats.promotionThreshold) {
    const ladder = MODEL_LADDERS[getProvider(stats.currentModel)];
    const prevIndex = Math.max(0, stats.demotionLevel - 1);
    return ladder[prevIndex];
  }

  return null;
}
```

#### Integration

- Extend `getModelForRole()` in multi-profile.ts to check `RouteStats` from KV
- After each LLM call, update stats
- Run evaluation every 50 calls or daily (whichever comes first)

---

## Phase 2: Tile Algebra (~2 weeks)

**Goal:** Typed task composition with confidence propagation. Each "tile" is a typed unit of work with inputs, outputs, and a confidence score.

#### Data Structures

```typescript
interface Tile<TInput, TOutput> {
  id: string;
  type: string;           // e.g. "explain", "quiz", "code_review"
  version: number;
  inputSchema: TInput;
  outputSchema: TOutput;
  confidence: number;     // 0-1
  model: string;          // which model handles this tile
  cached: boolean;        // was the last run a cache hit?
  computeCost: number;    // estimated tokens
  parentId?: string;      // composition chain
}

interface TilePipeline {
  id: string;
  tiles: Tile<any, any>[];
  totalConfidence: number;  // product of tile confidences
  totalCost: number;        // sum of tile costs
}
```

#### Core Algorithm

```typescript
async function executeTile<TI, TO>(
  tile: Tile<TI, TO>,
  input: TI,
  executor: (tile: Tile<TI, TO>, input: TI) => Promise<TO>
): Promise<{ output: TO; confidence: number; fromCache: boolean }> {
  // 1. Check deadband cache for this tile+input
  const cacheResult = await queryWithDeadband(
    `tile:${tile.type}:${tile.version}`,
    JSON.stringify(input),
    () => executor(tile, input),
    kv
  );

  // 2. Update tile confidence (exponential moving average)
  const alpha = 0.1;
  tile.confidence = tile.confidence * (1 - alpha) + cacheResult.confidence * alpha;
  tile.cached = cacheResult.fromCache;

  return {
    output: cacheResult.response as unknown as TO,
    confidence: tile.confidence,
    fromCache: cacheResult.fromCache
  };
}

// Composition: pipeline confidence = product of tile confidences
function pipelineConfidence(tiles: Tile<any, any>[]): number {
  return tiles.reduce((acc, t) => acc * t.confidence, 1.0);
}

// Short-circuit: if running a tile would lower pipeline confidence below threshold,
// skip it and use cached fallback
async function executePipeline(
  pipeline: TilePipeline,
  inputs: any[],
  minConfidence: number = 0.7
): Promise<{ results: any[]; confidence: number; skipped: string[] }> {
  const results = [];
  const skipped = [];

  for (let i = 0; i < pipeline.tiles.length; i++) {
    const tile = pipeline.tiles[i];
    const projected = pipelineConfidence(pipeline.tiles.slice(0, i + 1));

    if (projected < minConfidence && tile.cached) {
      // Skip — use last cached result, pipeline confidence already accounts for this
      skipped.push(tile.id);
      results.push(null); // filled from cache by caller
      continue;
    }

    const result = await executeTile(tile, inputs[i], tileExecutor);
    results.push(result.output);
  }

  return { results, confidence: pipelineConfidence(pipeline.tiles), skipped };
}
```

#### Integration

- Wrap existing agent roles (tutor, quiz, codegen) as tiles
- Add tile registry to studylog-ai/src/lib/
- Extend encounter-engine.ts units to be tiles (they already have type/version structure)

---

## Phase 3: Progressive Hardening + Structural Memory (~3 weeks)

### 3A. Progressive Hardening

**Goal:** Routes that are consistently high-confidence + high-cache-hit "harden" into static code.

#### Hardening Levels

```
Level 0: Full LLM call (every request)
Level 1: Deadband cached (semantic similarity match)
Level 2: Template + LLM fill (extract template, only call LLM for variables)
Level 3: Pure template (no LLM call, regex/string substitution only)
Level 4: Compiled function (TypeScript function, no LLM dependency)
```

#### Algorithm

```typescript
interface HardeningRecord {
  route: string;
  level: number;          // 0-4
  template?: string;      // extracted at level 2+
  variables?: string[];   // template slots
  compiledFn?: string;    // function body at level 4
  confidenceHistory: number[];
  lastEvaluatedAt: number;
}

async function evaluateHardening(record: HardeningRecord): Promise<number> {
  const history = record.confidenceHistory.slice(-50);
  const avg = mean(history);
  const variance = variance(history);

  // Promote if consistently high confidence with low variance
  if (avg > 0.95 && variance < 0.01 && record.level < 4) {
    return record.level + 1;
  }
  // Demote if confidence drops
  if (avg < 0.7 && record.level > 0) {
    return record.level - 1;
  }
  return record.level;
}

// Template extraction (Level 1 → Level 2)
async function extractTemplate(
  route: string,
  samples: CacheEntry[]
): Promise<{ template: string; variables: string[] } | null> {
  if (samples.length < 10) return null;

  // Find common substrings across responses
  // Use suffix array or simple LCS approach
  // Variables are the differing parts
  const common = longestCommonSubstrings(samples.map(s => s.response));
  if (common.length < 3) return null; // too fragmented

  // Extract variables by diffing each sample against template
  const variables = extractVariableNames(common, samples);
  return { template: common.join('{{PLACEHOLDER}}'), variables };
}
```

### 3B. Structural Memory

**Goal:** Recognize patterns across agents/users. "When students ask about recursion, the Socratic method works 91% of the time."

#### Data Structures

```typescript
interface Pattern {
  id: string;
  signature: string;       // hash of pattern features
  features: {
    route: string;
    inputClass: string;    // clustered input category (e.g. "recursion_question")
    outputClass: string;   // clustered output category
    confidenceRange: [number, number];
    modelUsed: string;
  };
  frequency: number;       // how often this pattern occurs
  successRate: number;     // confidence * cache_hit_rate
  discoveredAt: number;
  lastSeenAt: number;
}

interface StructuralMemoryStore {
  patterns: Map<string, Pattern>;
  clusters: Map<string, string[]>; // cluster_id → pattern_ids
}
```

#### Algorithm

```typescript
async function detectPatterns(
  cacheEntries: CacheEntry[],
  window: number = 100
): Promise<Pattern[]> {
  const recent = cacheEntries.slice(-window);
  const patterns: Pattern[] = [];

  // Cluster by route + input similarity
  const clusters = clusterByRouteAndInput(recent, 0.8);

  for (const cluster of clusters) {
    if (cluster.entries.length < 5) continue;

    // Check if this cluster has consistent high confidence
    const avgConf = mean(cluster.entries.map(e => e.confidence));
    const cacheRate = cluster.entries.filter(e => e.hitCount > 0).length / cluster.entries.length;

    if (avgConf > 0.85) {
      patterns.push({
        id: generateId(),
        signature: hash(cluster.route + cluster.centroid),
        features: {
          route: cluster.route,
          inputClass: cluster.label,
          outputClass: extractOutputClass(cluster.entries),
          confidenceRange: [min(cluster.entries.map(e => e.confidence)), avgConf],
          modelUsed: cluster.entries[0].model,
        },
        frequency: cluster.entries.length,
        successRate: avgConf * cacheRate,
        discoveredAt: Date.now(),
        lastSeenAt: Date.now(),
      });
    }
  }

  return patterns;
}
```

---

## Phase 4: Self-Evaporation (~2 weeks)

**Goal:** Agent hardens into static code over time. The "Conservation of Intelligence" principle: intelligence transfers from compute to storage.

#### Evaporation Lifecycle

```
┌─────────────┐
│  Born (L0)  │ ← Every route starts here
└──────┬──────┘
       │ after N calls with high confidence
       ▼
┌─────────────┐
│  Warm (L1)  │ ← Deadband active, some cache hits
└──────┬──────┘
       │ cache hit rate > 60%, confidence > 0.9
       ▼
┌─────────────┐
│  Cooling(L2)│ ← Template extracted, partial LLM
└──────┬──────┘
       │ template covers > 80% of cases
       ▼
┌─────────────┐
│  Hard (L3)  │ ← Pure template, no LLM
└──────┬──────┘
       │ no failures in 200 calls
       ▼
┌─────────────┐
│ Evaporated  │ ← Compiled TypeScript, zero LLM
│    (L4)     │    Intelligence is now in code, not compute
└─────────────┘
```

#### Core Algorithm

```typescript
interface EvaporatedRoute {
  route: string;
  level: number;
  code: string;           // TypeScript source (generated at L4)
  callCount: number;
  failureCount: number;
  lastFailureAt: number;
  evaporatedAt?: number;
}

async function evaporateRoute(route: EvaporatedRoute): Promise<void> {
  // Collect all cache entries for this route
  const entries = await getAllCacheEntries(route);
  
  // Generate TypeScript function from pattern
  const prompt = `Given these input/output pairs, generate a pure TypeScript function:
${entries.slice(0, 50).map(e => `IN: ${e.input}\nOUT: ${e.response}`).join('\n\n')}
    
No LLM calls. No external dependencies. Pure function.`;

  // One-time LLM call to generate the static function
  const generated = await callLLM(prompt);
  
  // Validate: test against held-out entries
  const testEntries = entries.slice(-20);
  const fn = new Function('input', generated) as (input: string) => string;
  
  let passCount = 0;
  for (const entry of testEntries) {
    const result = fn(entry.inputHash);
    if (similarity(result, entry.response) > 0.9) passCount++;
  }
  
  if (passCount / testEntries.length >= 0.9) {
    route.level = 4;
    route.code = generated;
    route.evaporatedAt = Date.now();
    await saveEvaporatedRoute(route);
  }
}

// Runtime dispatch
async function dispatch(route: string, input: string): Promise<string> {
  const evaporatedRoute = await getEvaporatedRoute(route);
  
  if (evaporatedRoute?.level === 4) {
    // Fully evaporated — run compiled function, zero LLM cost
    const fn = loadEvaporatedFn(evaporatedRoute);
    return fn(input);
  }
  
  // Otherwise, fall through to deadband → LLM
  return queryWithDeadband(route, input, () => callLLM(input), kv);
}
```

---

## Effort Estimates

| Phase | Duration | Token Savings | What It Unlocks |
|-------|----------|---------------|-----------------|
| **Phase 1** | 1 week | ~40% | Cheaper operation, visible cache hit metrics |
| **Phase 2** | 2 weeks | ~60% | Composable tasks, confidence-aware routing |
| **Phase 3** | 3 weeks | ~75% | Self-optimizing routes, cross-agent learning |
| **Phase 4** | 2 weeks | ~85% | Zero-cost common paths, "intelligence as code" |

**Total: ~8 weeks for full implementation.**

---

## Implementation Checklist (Phase 1 — Actionable Now)

### Deadband
- [ ] Create `src/lib/deadband.ts` in studylog-ai
- [ ] Implement `normalize()` and `hash()` (trigram Jaccard for v1)
- [ ] Implement `queryWithDeadband()` with exact + fuzzy matching
- [ ] Add `CACHE_KV` binding to wrangler.toml
- [ ] Wrap `callLLM()` in byok.ts with deadband
- [ ] Add cache hit/miss logging to D1 analytics table
- [ ] Add `/api/cache/stats` endpoint for monitoring

### Model Demotion
- [ ] Create `src/lib/model-demotion.ts` in studylog-ai
- [ ] Define `MODEL_LADDERS` constant
- [ ] Implement `RouteStats` tracking (update after each call)
- [ ] Implement `evaluateDemotion()` with thresholds
- [ ] Extend `getModelForRole()` to check demotion state
- [ ] Add `/api/routes/stats` endpoint for monitoring
- [ ] Add manual override: force model for a route

### Testing
- [ ] Unit tests for deadband (exact hit, fuzzy hit, miss)
- [ ] Unit tests for model demotion (promote/demote thresholds)
- [ ] Integration test: full request cycle with cache + demotion
- [ ] Load test: 1000 requests to same route, verify cache hit rate

---

## Key Design Decisions

1. **V1 uses trigram Jaccard, not embeddings** — avoids another API dependency. Upgrade to embeddings in Phase 2 when tile algebra adds embedding infrastructure.

2. **Demotion is per-route, not per-user** — aggregate stats across all users for a route. Per-user routing is handled by existing `ModelRouting`.

3. **Evaporation generates TypeScript, not WASM** — simpler toolchain, debuggable. WASM is a future optimization.

4. **Hardening is monotonic by default** — routes can be manually demoted but auto-promotion is conservative (95th percentile confidence, <1% variance).

5. **Structural memory is read-only** — it observes patterns but doesn't modify behavior directly. Human review before acting on discovered patterns.
