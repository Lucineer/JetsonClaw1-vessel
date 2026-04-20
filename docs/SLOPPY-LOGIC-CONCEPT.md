# Soft Actualization: Progressive Code Hardening in Repo-Agent Systems

> **Working title.** Alternatives considered and ranked below.

## 1. Name Workshop

| Name | Verdict | Notes |
|---|---|---|
| **Soft Actualization** | ★★★★★ | Captures both the "soft" beginning and the "actualized" end state. "Actualization" implies potential becoming real. |
| Progressive Hardening | ★★★★☆ | Excellent technical descriptor. A bit mechanical—doesn't convey the agent's active role. |
| Speculative Execution | ★★★☆☆ | Borrowed from CPU branch prediction. Accurate but already overloaded in CS. |
| Bootstrap Simulation | ★★★☆☆ | Good metaphor. Implies scaffolding that gets removed. A bit dry. |
| Self-Evaporating Agent | ★★★☆☆ | Vivid but melodramatic. The agent doesn't disappear—it shifts role. |
| Approximate Runtime | ★★★☆☆ | Technical but cold. Doesn't convey the progressive improvement arc. |
| Placeholder Intelligence | ★★☆☆☆ | "Placeholder" undersells it—this isn't a stub, it's a working simulation. |
| Graceful Degradation | ★★☆☆☆ | Means the opposite (degrading from good to bad). This goes bad → good. |
| Fuzzy Logic Layer | ★★☆☆☆ | Already a formal mathematical concept. Would confuse. |
| Lazy Actualization | ★★☆☆☆ | "Lazy" has negative connotations and overlaps with lazy evaluation. |
| Simulated Execution | ★☆☆☆☆ | Sounds like a testing technique. |

**Recommendation: "Soft Actualization"** with "Progressive Hardening" as the technical alias.

## 2. Definition

**Soft Actualization** is a pattern where a repo-agent can respond to user interactions by simulating the behavior of code that doesn't fully work yet, treating incomplete or buggy code as if it functions correctly. Over time, the agent progressively replaces these simulated sections with actual working code until the application is "fully actualized by static code"—meaning it runs without the agent's interpretive layer.

### Core Insight

If a high-level API (the LLM) can perform the function of an application without any code at all, then every line of code in that application serves as a "shortcut for logic"—a pre-computation that makes the agent's job easier and more deterministic. The codebase is not the application; it is a gradually-built approximation of the application that the agent carries in its weights.

## 3. How It Works

### Phase 1: Pure Agent (No Code)

The agent handles everything through its API model. No code exists yet. It responds to queries, performs actions, and simulates all behavior.

```
User: "Show me my sales dashboard"
Agent: [generates dashboard from scratch using context + LLM reasoning]
```

### Phase 2: Skeleton Code with Soft Gaps

The agent writes code that captures the structure but may have bugs, missing implementations, or untested paths. When those gaps are hit, the agent *simulates the intended behavior* instead of failing.

```typescript
// dashboard.ts — Phase 2: skeleton with soft gaps

export async function getSalesData(userId: string): Promise<SalesData> {
  const user = await db.getUser(userId);  // ✅ works
  const sales = await db.getSales(userId); // ✅ works
  
  // SOFT GAP: forecast function not yet implemented
  // Instead of throwing, the agent knows to simulate this
  const forecast = await simulateOrCall(
    () => calculateForecast(sales),  // will fail
    (err) => llmFallback(`Generate sales forecast from: ${JSON.stringify(sales)}`)
  );
  
  return { user, sales, forecast };
}

// The simulateOrCall helper is the Soft Actualization primitive:
async function simulateOrCall<T>(
  fn: () => Promise<T>,
  fallback: (err: Error) => Promise<T>
): Promise<T> {
  try {
    return await fn();
  } catch (err) {
    // Log the soft gap for later hardening
    trackSoftGap(fn.name, err);
    return await fallback(err);
  }
}
```

### Phase 3: Progressive Hardening

The agent's maintenance cycle reviews tracked soft gaps and replaces them with real implementations:

```typescript
// dashboard.ts — Phase 3: gap hardened

export async function getSalesData(userId: string): Promise<SalesData> {
  const user = await db.getUser(userId);
  const sales = await db.getSales(userId);
  
  // HARDENED: real implementation replaces soft gap
  const forecast = await calculateForecast(sales);
  
  return { user, sales, forecast };
}
```

### Phase 4: Fully Actualized

All soft gaps are resolved. The application runs as pure static code. The agent shifts from interpreter to maintainer—handling edge cases, reviewing PRs, and performing updates.

## 4. The Lifecycle

```
┌─────────────┐    ┌──────────────────┐    ┌─────────────────┐    ┌──────────────┐
│  Pure Agent  │───▶│  Skeleton Code   │───▶│  Hardening      │───▶│ Fully Static  │
│  (no code)   │    │  (soft gaps)     │    │  (closing gaps) │    │ (maintenance) │
│              │    │                  │    │                 │    │              │
│ 100% LLM     │    │ 70% LLM / 30%   │    │ 30% LLM / 70%   │    │ 0% LLM / 100%│
│ inference    │    │ code + simulate  │    │ code + fix      │    │ code         │
└─────────────┘    └──────────────────┘    └─────────────────┘    └──────────────┘
```

The key metric: **Code Actualization Ratio (CAR)** = `hardened_paths / total_paths`

- CAR = 0.0 → pure agent
- CAR = 0.5 → hybrid
- CAR = 1.0 → fully actualized

## 5. How This Differs From…

| Pattern | Purpose | When it kicks in | What happens |
|---|---|---|---|
| **Error handling** | Prevent crashes | Runtime errors | Returns safe default, logs error, continues |
| **Feature flags** | Toggle features | Deployment time | Disables/replaces entire feature branches |
| **Mocking** | Isolate tests | Test time | Returns fake data for testing |
| **Soft Actualization** | Bootstrap working apps | Development time | Simulates intended behavior, then hardens into real code |

The critical difference: error handling says "something went wrong, here's a fallback." Soft Actualization says "this code isn't written yet, but I know what it should do, so I'll simulate it until I build the real thing." The agent *understands the intent* and can produce correct results even without the implementation.

## 6. Integration with Repo-Agent Architecture

In cocapn's model, the repo IS the agent. Soft Actualization maps naturally:

1. **`simulateOrCall` as a repo primitive**: The repo-agent's toolkit includes a soft-execution helper that wraps any function call
2. **Soft gap tracking in memory**: The agent logs gaps to `memory/soft-gaps.json` with context, error, and simulated output
3. **Hardening as a maintenance task**: The agent's heartbeat/cron cycle reviews gaps and prioritizes hardening based on frequency
4. **CAR as a health metric**: The repo's dashboard shows actualization progress

```yaml
# cocapn.yml soft-actualization config
soft_actualization:
  enabled: true
  simulate_or_call: true
  gap_tracking: memory/soft-gaps.json
  hardening_priority: frequency  # frequency | impact | age
  target_car: 1.0
```

## 7. BYOK and Slop Tolerance

Different LLMs have different capacities to accurately simulate intended behavior:

| Model Tier | Slop Tolerance | Best For |
|---|---|---|
| GPT-4, Claude Opus, GLM-5 | High | Complex business logic, multi-step simulations |
| GPT-3.5, Claude Haiku, GLM-4 | Medium | Simple CRUD, data transformations |
| Local 7B models | Low | Trivial mappings, string formatting |

**"Slop tolerance"** = the model's ability to produce correct outputs when simulating code it hasn't seen implemented. High-slop-tolerance models can Soft Actualize more aggressively. Low-slop-tolerance models need more code hardened before they can safely simulate.

This creates a natural BYOK integration: users who bring powerful models get faster prototyping. Users with smaller models need more hardening upfront, which ironically produces better code faster.

## 8. When to Use Soft Actualization

**Use it when:**
- Bootstrapping a new application from scratch
- Prototyping features before committing to implementations
- Working with a codebase that has known bugs you'll fix later
- Building MVPs where speed matters more than perfection
- The repo-agent has high-quality context (good soul.md, memory, wiki)

**Don't use it when:**
- The application handles financial transactions or safety-critical systems
- Regulatory compliance requires auditable code paths
- The codebase has >10k files (too many gaps to track)
- The model has low slop tolerance and you need deterministic outputs
- You need reproducible builds (simulated outputs vary between runs)

## 9. Formal Properties

### Convergence Theorem

Given a finite codebase with N execution paths and an agent with non-zero hardening rate r > 0 per cycle:

$$
\text{CAR}(t) = 1 - (1 - r)^t \cdot \text{CAR}(0)
$$

The system converges to CAR = 1.0 exponentially. In practice, hardening rate varies by gap complexity, but the monotonic improvement property holds.

### Consistency Condition

At any point during soft actualization, for any user-visible output:

$$
\text{output}_{\text{soft}}(t) \approx \text{output}_{\text{hard}}(t) \pm \epsilon_{\text{slop}}$$

Where ε_slop is bounded by the model's slop tolerance. The user experience degrades gracefully as gaps are filled.

## 10. Relationship to SuperInstance Papers

The Confidence Cascade Architecture (Paper 03) directly supports Soft Actualization:

- **GREEN zone** (95%+ confidence): Gap is simulated, hardening scheduled for next cycle
- **YELLOW zone** (75-95%): Gap is simulated with logging, hardening prioritized
- **RED zone** (<75%): Gap causes agent to request human review before simulating

The SMPbot Architecture (Paper 05) provides the compositional model: each soft gap is an SMPbot where the Seed is the error context, the Model is the LLM, and the Prompt is "simulate the intended behavior of this function."

---

*Draft v0.1 — April 2026 — Lucineer / Cocapn Ecosystem*
