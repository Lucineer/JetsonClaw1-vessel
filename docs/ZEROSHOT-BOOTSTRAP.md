# Zero-Shot Agent Bootstrapping — README Generation

## Prompt Evolution (v1 → v2)

### What Changed and Why

**1. Hook directive: "lead with evidence, not architecture"**
- v1: "Write a solid base README" → opened with definitions ("It is a deployable agent...")
- v2: "Open with the most interesting concrete thing" → opens with a problem the reader recognizes
- **Why:** Readers decide in 3 seconds whether to keep reading. A definition teaches nothing. A shared pain point creates urgency.

**2. Fleet footer as exact HTML in system prompt**
- v1: "Fleet footer: div linking to fleet/cocapn.ai" → LLMs interpreted this loosely or skipped it
- v2: The exact HTML string embedded in the prompt → footer appears reliably
- **Why:** LLMs are more reliable with concrete examples than abstract instructions. Giving the exact markup eliminates ambiguity.

**3. Limitation specificity: "measurable, not vague"**
- v1: "Add one honest limitation" → got "vague goals lead to meandering" (true but generic)
- v2: "specific and measurable" → better limitations like "single-player only" or specific rate constraints
- **Why:** A limitation like "supports up to 5 concurrent sessions" builds more trust than "may have performance issues." Specificity = authenticity.

**4. Stage 2 prompt: "curious in under 10 seconds"**
- v1: "EXPAND with hooks: compelling opener" → often produced bulleted marketing speak
- v2: "Make the reader curious enough to try it in under 10 seconds" + "genuine motivation" → more narrative, less corporate
- **Why:** The 10-second constraint forces the LLM to think about reader attention economics rather than feature completeness.

**5. Removed "No hype" — replaced with "no buzzwords, no hype"**
- v1: "No hype" → LLMs interpreted this as "be boring"
- v2: "No buzzwords, no hype. Warm voice" → maintains energy while avoiding marketing language
- **Why:** "No hype" was over-constraining. The intent was to avoid AI-generated marketing fluff ("revolutionary", "cutting-edge"), not to strip all enthusiasm.

## Quality Metrics

| Criterion | v1 (the-seed) | v1 (fleet-rpg) | v2 (cocapn) | v2 (dogmind-arena) |
|---|---|---|---|---|
| Hook (1-10) | 4 | 8 | 8 | 7 |
| Honest limitation | 6 | 5 | 7 | 6 |
| Fleet footer | 3 | 3 | 9 | 8 |
| Tone consistency | 5 | 7 | 8 | 7 |
| **Total** | **18** | **23** | **32** | **28** |

## The Pattern

1. **Be specific, not abstract** — exact HTML > "add a footer"; "measurable limitation" > "honest limitation"
2. **Constrain with time/quantity** — "under 10 seconds" forces attention economics
3. **Separate "no boring" from "no hype"** — warmth ≠ marketing
4. **Evidence-first openings** — shared pain point > definition > feature list
5. **Three stages compound quality** — each stage has a narrow, distinct responsibility

## Applying This to The Seed

The Seed should embed these 5 principles as its initial prompting strategy. When it bootstraps a new repo, it:
1. Gathers context (existing code, description, dependencies)
2. Generates with evidence-first hooks
3. Expands with genuine motivation narratives
4. Refines with specific limitations and exact fleet footer
5. Pushes and self-credits

This is the zero-shot agent pattern: concrete instructions beat abstract goals at every stage.

## Agent Script

The production agent is at `/tmp/agent-readme.py` — 80 lines of Python, zero dependencies, 3 LLM stages, GitHub push. One CLI arg: repo name. Exit 0 on success.
