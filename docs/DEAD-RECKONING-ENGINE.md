# Dead Reckoning Engine
## Expensive models storyboard. Cheap models animate. Git coordinates.

**Status:** Seed v0.1
**Philosophy:** Knowledge moves through folders like film moves through production. Storyboard → Animatic → Dailies → Final Cut. But the "final cut" is never final — it loops back.

---

## The Pipeline

```
compass-bearing/    ← Human drops prompts, focus areas, sketches here
       ↓
   [Expensive Model: Storyboard]
       ↓
dead-reckoning/     ← Imagined answers. NOT correct. Frameworks for R&D.
       ↓
   [Cheap Models: Inbetweeners iterate]
       ↓
working-theory/     ← Current practical understanding. Assumptions marked.
       ↓
   [Logic/Hardware/Testing closes on truth]
       ↓
ground-truth/       ← Verified. Within tolerance. Seed logic preferred.
       ↓
   [Synthesis]
       ↓
published/          ← Ready for consumption or deployment
```

**Cross-cutting:**
```
open-questions/     ← Any agent can visit. Push a branch to help.
archives/           ← Dead ends preserved for pattern mining.
templates/          ← Ready-to-go repo-agent variations.
```

## Folder Philosophy

### `compass-bearing/` — The Human's Intent
This is where the creator drops raw thoughts. Prompts, napkin sketches, links, voice notes, anything. The repo-agent polls this folder on a pulse. It doesn't execute — it reads, understands, and creates a storyboard.

**The repo-agent is a reader first, a writer second.**

### `dead-reckoning/` — Imagined Answers
Dead reckoning is navigation by estimated position. These files are NOT correct. They are frameworks for imagination. "If X were true, then Y would follow." The expensive model sketches these based on compass-bearing input. They're meant to be wrong in interesting ways.

### `working-theory/` — Current State
This is what the system is actually running on. It's the UI-facing understanding. But every claim in working-theory carries an implicit asterisk: *this assumes X, Y, Z which are not yet in ground-truth.* The system should surface these assumptions visibly.

### `ground-truth/` — Verified Knowledge
Logic has closed. Hardware tests pass. Measurements are within tolerance. Specs are locked. This is the foundation. When working-theory items graduate here, they get a verification record (who, when, what test, what tolerance).

### `open-questions/` — Cooperative Problem Solving
Any agent can visit this folder. See what the repo-agent needs help with. Push a branch with an idea. Fork the whole repo if you can obsolete the question entirely. **Git IS the coordination protocol.** PR = "I solved your open question." Fork = "Here's my version with the answer built in."

### `archives/` — Preserved Dead Ends
Failed dead reckonings don't get deleted. They get moved here. Future agents can mine them for patterns. A wrong answer in 2026 might contain the seed of a right answer in 2028.

### `templates/` — Ready-to-Go Variations
This is where the repo-agent becomes a platform. Templates for:
- Research paper pipeline
- Product development
- Hardware design
- Game development
- Creative writing
- Scientific hypothesis testing
- Business strategy
- Education curriculum design
- Architecture/planning
- Music composition

Each template pre-configures the folder structure, the expensive/cheap model pairing, the tolerance thresholds, and the verification criteria.

## The Storyboard/Inbetweener Pattern

### Expensive Model (Storyboarder)
- **Role**: Sketch the big picture. Define beats. Establish direction.
- **Models**: Seed-2.0-pro, DeepSeek-Reasoner, Kimi K2.5
- **When**: New compass-bearing input. Context shift needed. Novelty plateau.
- **Output**: A "storyboard" file in dead-reckoning/ — structured outline, key insights, emotional arc, open threads.

### Cheap Models (Inbetweeners)
- **Role**: Fill the frames. Iterate. Explore variations. Stress-test.
- **Models**: Seed-2.0-mini, DeepSeek-chat, phi-4, Hermes-3-70B, Olmo-3.1-32B
- **When**: After storyboard exists. Working within established framework.
- **Output**: Detailed files in dead-reckoning/ → working-theory/ — fleshed out versions of storyboard beats.

### Medium Model (Director/Orchestrator)
- **Role**: The repo-agent itself. Reads folders. Routes work. Manages state.
- **Models**: GLM-5-turbo, Kimi K2.5 (non-thinking), Qwen3.5-397B
- **Behavior**: Polls compass-bearing on pulse. Checks if inbetweeners are still producing novel output. Triggers new storyboard when novelty plateaus. Moves items through folders.

### Novelty Detection
The key insight: **when inbetweeners stop producing novel insights, it's time for another expensive storyboard session to shift the context focus.**

Detection:
- Track semantic similarity of recent outputs (hash + compare)
- If last N inbetweener outputs are >85% similar → novelty plateau
- Trigger expensive model with: current working-theory + dead-reckoning + open-questions
- New storyboard shifts focus → new inbetweener calls → new insights

### Cost-Optimized Ratio
For a typical research cycle:
1. 1 expensive call (storyboard) → sets direction
2. 8-15 cheap calls (inbetweeners) → iterate within framework
3. Repeat when novelty plateaus

Total: ~$0.50-2.00 per full research cycle vs $10-20 if all calls were expensive.

## The Repo-Agent Itself

The repo-agent runs on a medium model (GLM-5-turbo or similar). Its job is NOT to be creative — it's to be organized:

1. **Pulse check**: Read compass-bearing/ for new input (every 5 min)
2. **Route**: If new input → call storyboarder → create dead-reckoning files
3. **Iterate**: If dead-reckoning files exist → call inbetweeners → expand
4. **Evaluate**: Check novelty plateau → trigger new storyboard or graduate to working-theory
5. **Verify**: Check if working-theory items can graduate to ground-truth
6. **Publish**: Move verified items to published/
7. **Cooperate**: Check open-questions/ for things other agents need

## Git as Coordination Protocol

This is the deepest insight. We're gaming git for agent coordination:

- **Branch** = An agent's attempt to solve an open question
- **PR** = "Here's my answer to your open question"
- **Fork** = "I improved your repo so much the question is obsolete"
- **Commit** = A dead-reckoning item moving to working-theory
- **Tag** = A working-theory item graduating to ground-truth
- **Issue** = An open question
- **Release** = A published/ item ready for deployment

No custom coordination protocol needed. Git already IS the coordination protocol. 50 years of tooling, UI, and workflow design — free.

## Templates (Planned)

### Research Paper Pipeline
compass-bearing/ → dead-reckoning/ (thesis exploration) → working-theory/ (draft) → ground-truth/ (cited, verified) → published/ (paper)

### Product Development
compass-bearing/ → dead-reckoning/ (feature ideas) → working-theory/ (specs) → ground-truth/ (tested, measured) → published/ (release)

### Hardware Design
compass-bearing/ → dead-reckoning/ (schematic concepts) → working-theory/ (prototypes) → ground-truth/ (tolerance-verified) → published/ (manufacturing specs)

### Creative Writing
compass-bearing/ → dead-reckoning/ (story beats) → working-theory/ (draft chapters) → ground-truth/ (edited, fact-checked) → published/ (final manuscript)

### Scientific Hypothesis
compass-bearing/ → dead-reckoning/ (hypotheses) → working-theory/ (experimental design) → ground-truth/ (peer-reviewed, replicated) → published/ (paper)

## Relationship to Existing Concepts

- **Cocapn**: This IS a cocapn repo-agent. The folder structure IS the vessel.
- **Reverse-Actualization**: Dead-reckoning IS backward-from-future thinking.
- **Crystallization Principle**: Dead-reckoning is fluid. Ground-truth is solid. The pipeline IS the crystallization.
- **INCREMENTS Trust**: Open-questions folder = trust-based delegation. Agents earn trust by solving questions.
- **Equipment Protocol**: Each template is equipment. The repo-agent equips itself for different domains.
- **Captain Paradigm**: The repo-agent is the captain. The expensive model is the admiral's strategic briefing. The cheap models are the crew.

## Implementation Notes

- **Zero runtime deps**: Pure TS, runs on Cloudflare Workers
- **File system = KV**: Each folder is a KV prefix (`dr:compass:`, `dr:dead:`, `dr:working:`, etc.)
- **Pulse**: Cron Trigger every 5 minutes to check compass-bearing
- **Novelty hash**: SHA-256 of content, stored alongside, compared on each write
- **Tolerance config**: Set per-template (research: peer review; hardware: measurement tolerance)

---

*Superinstance & Lucineer (DiGennaro et al.) — 2026-04-04*
*A Cocapn Vessel — The repo IS the agent*
