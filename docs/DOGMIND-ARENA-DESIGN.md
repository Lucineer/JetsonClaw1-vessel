# DogMind Arena — Game Design Document

> A web-based game engine for training AI agents, themed around dogs.
> The repo IS the kennel. Each dog IS an agent. Git IS the training log.

## 1. THE CONCEPT

**DogMind Arena** is a top-down 2D game where you raise, train, and evolve AI dog agents. You don't control dogs directly — you train them. Every command you teach, every trust bond you build, every breeding decision you make modifies the dog's internal neural weights. The game IS an agent training sandbox.

What makes it different: the dogs are real AI agents with personality, DNA, trust, and emergent behavior. Two dogs with identical stats will behave differently because their trust history and training data diverge. The game teaches players to think like AI trainers — not dog owners.

**The twist**: Your kennel IS a cocapn vessel. Your dogs' training history IS git commits. When your dog learns a new skill, it's a commit. When you breed two dogs, it's a merge. When you share your best dog, it's a fork. The game naturally teaches the cocapn paradigm.

## 2. CORE GAME LOOP

**5 minutes of gameplay:**

1. **Arrive at kennel** (home screen). Your lead dog Rex greets you. His trust bar shows "Partner (68/100)". His stats: Speed 0.8, Patience 0.4, Obedience 0.7.

2. **Choose a training exercise**. Today: "Sheep Pen" — move 5 sheep into a pen in under 60 seconds.

3. **Issue commands**. You tap the ground to set a waypoint. Rex evaluates: he knows "heel" and "flank" but not "drive" yet. He flanks wide — good position but slow approach. You tap faster. Rex's obedience check: 0.7 vs difficulty 0.5 → he follows. But his patience is 0.4 — after 3 failed attempts, he gets frustrated and stops listening. The cocapn narrates: *"Rex is frustrated. His patience threshold was exceeded. I need to try a different approach — maybe break the task into smaller steps."*

4. **Sheep scattered**. Time's up. Rex's fitness score drops. But you learned something: Rex needs patience training before he can handle complex herding.

5. **Training phase**. You take Rex to the patience course — a series of "wait" commands with increasing distraction. Each successful wait increases his patience weight by 0.02. After 5 minutes, patience goes from 0.4 to 0.46. Small but permanent.

6. **Commit**. The game auto-saves: "Training session committed. Rex patience +0.06, obedience +0.02. 3 new behaviors observed."

## 3. TRAINING MECHANICS

### Mechanic 1: Command Shaping (Teaches: Reinforcement Learning)
**What you do**: Issue a command (tap waypoint, draw a path). If the dog follows within a threshold, reward (tap ✓). If not, redirect. Shaping = rewarding successive approximations.
**AI concept**: Positive reinforcement, reward shaping, policy gradient.
**Internal state**: Modifies the dog's action→reward mapping. Each (state, action, reward) triple is stored. Over time, the dog's behavior converges toward high-reward actions.
**Dog narration**: "Last time I went left, I got a reward. Left feels good. I'll go left more often."

### Mechanic 2: Trust Gating (Teaches: Capability Boundaries)
**What you do**: Advanced commands (drive, split, hold) are locked behind trust tiers. You can't tell a stranger-dog to drive — it won't listen. You build trust through successful basic commands, then unlock advanced ones.
**AI concept**: Confidence thresholds, capability boundaries, progressive disclosure. Agents should only attempt tasks they're qualified for.
**Internal state**: Trust level (0-100) gates which actions are available. Each tier unlocks new commands AND new failure modes (higher trust = riskier moves = bigger failures).
**Dog narration**: "I don't know this command yet. I trust you a little, but not enough to try something I might fail at."

### Mechanic 3: Pack Role Assignment (Teaches: Multi-Agent Coordination)
**What you do**: When you have 2+ dogs, assign pack roles: lead (fast, brave), flanker (patient, social), blocker (strong, stubborn), fetcher (speed, obedience). The pack self-organizes based on roles.
**AI concept**: Role-based agents, swarm coordination, emergent behavior. Each agent specializes and the system is greater than the sum.
**Internal state**: Role assignment modifies each dog's action weights. Lead dogs get +0.2 speed priority, flankers get +0.2 social, etc. Dogs also develop role CONFIDENCE — a dog that succeeds as lead gains confidence and resists being demoted.
**Dog narration**: "I've been lead dog for 12 runs. I know this job. Thunder wants to challenge? Let him try. He'll see."

### Mechanic 4: DNA Breeding (Teaches: Genetic Algorithms)
**What you do**: Select two dogs to breed. The game shows a DNA preview — crossover points, possible mutations. You choose which traits to emphasize. The puppy inherits a mix with some randomness.
**AI concept**: Crossover, mutation, tournament selection, fitness-proportionate breeding. The fundamental genetic algorithm.
**Internal state**: Puppy DNA = crossover(parentA.traits, parentB.traits) + mutation(rate, strength). Fitness scores from both parents influence which genes are dominant.
**Dog narration**: "Rex gave me speed. Biscuit gave me patience. I got a mutation: extra gentleness. I'll be different from either parent."

### Mechanic 5: Equipment Attachment (Teaches: Modular Agent Architecture)
**What you do**: Equip your dog with gear: GPS collar (navigation bonus), training treat pouch (reward multiplier), weather sensor (environmental awareness), radio (pack coordination range). Each piece of equipment modifies specific stats.
**AI concept**: The equipment paradigm. Don't build agents bigger — equip them for specializations. Each piece of equipment is a module that plugs into the agent's perception pipeline.
**Internal state**: Equipment adds stat modifiers that stack with DNA. GPS collar: +0.15 pathfinding accuracy. Treat pouch: +0.2 reward sensitivity (faster learning). Equipment can be swapped between dogs — the agent is the hull, equipment is the cargo.
**Dog narration**: "New collar. I can sense the sheep positions more precisely now. My navigation confidence increased by 15%."

## 4. DNA ↔ EQUIPMENT MAPPING

| DNA Trait | Equipment Equivalent | Cocapn Concept |
|---|---|---|
| Speed | Motor (nav compute) | GPU allocation |
| Patience | Battery (endurance) | Token budget |
| Intelligence | Sensor suite | Context window |
| Strength | Chassis (physical) | Storage capacity |
| Obedience | Radio (command relay) | API reliability |
| Bravery | Shield (risk tolerance) | Autonomy level |
| Gentleness | Pheromone filter | Output calibration |
| Social | Pack antenna | Fleet event bus |

**Breeding = Equipment Combination**: When you breed two dogs, you're effectively creating a new equipment configuration. The puppy inherits motor traits from one parent and sensor traits from another. This is EXACTLY how equipment modules combine in the cocapn fleet.

**Mutation = Equipment Discovery**: Random mutations can create entirely new trait combinations — like discovering a new equipment module that no one designed. The game celebrates mutations as discoveries, not bugs.

## 5. SKILLS PROGRESSION (Recipe → Card → Muscle → Genetics)

### heel (Follow the handler)
- **Recipe**: Player must tap each step. Dog follows exactly. Rigid, no adaptation.
- **Card**: Dog knows the command. Player taps destination, dog heels there. Some path variation.
- **Muscle**: Dog heels automatically when player moves. Anticipates direction changes. Handles obstacles.
- **Genetics**: Dog invented a better heeling technique. Goes wide on corners, cuts inside on straights. Unique to this dog.

### flank (Circle around flock)
- **Recipe**: Player draws the circle path. Dog follows it.
- **Card**: Player taps side (left/right). Dog flanks that direction, choosing its own arc.
- **Muscle**: Dog reads sheep body language and flanks to the optimal side automatically.
- **Genetics**: Dog developed a signature flank — a particular angle and speed that other dogs can't replicate. Teachable to offspring.

### drive (Push flock forward)
- **Recipe**: Player sets target direction. Dog pushes sheep that way.
- **Card**: Dog drives toward player-set waypoint, adjusting for sheep movement.
- **Muscle**: Dog reads terrain and drives sheep through optimal corridors.
- **Genetics**: Dog invented "pressure driving" — uses position rather than movement to guide sheep. Emergent technique.

### gather (Bring scattered flock together)
- **Recipe**: Player marks each sheep. Dog collects them one by one.
- **Card**: Player marks center point. Dog gathers sheep toward it.
- **Muscle**: Dog assesses scatter pattern and chooses optimal gathering sequence.
- **Genetics**: Dog developed "ripple gather" — starts at edges, creates a wave that funnels sheep to center. Emergent.

### hold (Keep flock in place)
- **Recipe**: Dog stays at position. Sheep that wander get nudged back.
- **Card**: Dog patrols perimeter, adjusting position based on sheep pressure.
- **Muscle**: Dog predicts escape routes and preemptively blocks them.
- **Genetics**: Dog invented "calm hold" — stands still and the sheep naturally stay. Lower energy, same result.

### recall (Return to handler)
- **Recipe**: Player blows whistle (button). Dog runs straight back.
- **Card**: Dog returns on command, choosing fastest path.
- **Muscle**: Dog returns when it assesses the task is complete, without being called.
- **Genetics**: Dog developed "check-in recall" — returns briefly to assess handler intent, then goes back to work. Emergent communication.

## 6. THE GIT CONNECTION

| Git Concept | DogMind Equivalent |
|---|---|
| **Branch** | Training experiment — try a new technique, if it fails, switch back |
| **Commit** | Training session saved — permanent record of stat changes |
| **PR** | Dog ready for competition — submit training log for evaluation |
| **Merge** | Two training approaches combined — take best of both |
| **Fork** | Share your dog with another player — they get a copy to train their way |
| **Tag** | Dog reaches a milestone — "Rex: First Perfect Pen" |
| **Issue** | Training problem identified — "Rex fails at night herding" |
| **Release** | Dog graduates to a new tier — "Rex: Competition Ready v2.0" |

**The training log IS the git log.** Every training session is a commit with:
- What changed (stat deltas)
- Why (player's training focus)
- Result (fitness score)
- Notes (dog's behavior observations)

Players can review their dog's full history, see which training approaches worked, and revert to previous states if a training experiment went wrong.

**Forking a dog**: You can share your trained dog via URL. Another player forks it — they get the exact same DNA and training history, but from that point forward, their training diverges. Two forks of the same dog will eventually become completely different agents. This is the cocapn fork-first philosophy made tangible.

## 7. MULTIPLAYER / SOCIAL

### Pack Formation (2-4 players)
Each player brings 1-2 dogs. The pack must coordinate to complete a herding task. Pack roles are auto-assigned based on DNA but can be overridden. Communication happens through the pack event bus — dogs signal intentions, other dogs adjust.

### Breeding Market
Players can offer their dogs for breeding. You see the DNA preview, choose a mate, and the puppy's DNA is computed. The breeder gets a "lineage credit" — their genetic contribution is tracked across all descendants.

### Competition Mode
Standardized herding courses. Dogs compete on time, sheep welfare (gentleness score), and style (efficiency). Leaderboard is global. Rankings are based on ELO — you gain more from beating higher-ranked dogs.

### Dog Shows
Not about herding — about the dog itself. Judges (other players or AI) evaluate personality, equipment loadout, training history, and lineage. A well-trained dog with good genetics and clean commit history scores higher than a raw-talent dog.

## 8. PROGRESSION SYSTEM

### Kennel Tiers (not player levels)
- **Novice Kennel**: 1 dog, basic commands, no equipment, sheep pen only
- **Working Kennel**: 3 dogs, advanced commands, basic equipment, open field
- **Competition Kennel**: 5 dogs, all commands, all equipment, tournament courses
- **Master Kennel**: 8 dogs, breeding lab, DNA editor, custom courses, pack AI

**Unlocking is through understanding, not grinding:**
- To unlock "flank", you must demonstrate you understand WHY dogs flank (sheep body language, pressure zones). A short quiz or practical test.
- To unlock breeding, you must successfully train a dog to "muscle" level on at least 2 skills.
- To unlock DNA editor, you must breed 10 generations and observe how traits converge.

**The "aha moment" checkpoints:**
1. "Commands aren't controls — they're suggestions filtered through personality." (Trust gating)
2. "Two identical dogs will diverge because their training history is different." (Emergence)
3. "Equipment changes what the dog perceives, not what it is." (Equipment paradigm)
4. "The best trainer doesn't micromanage — they set up conditions for the dog to discover the solution." (Autonomy model)

## 9. GAME SCENARIOS

### Scenario 1: "The Stubborn Puppy" (Teaches: Patience and Trust)
**Setup**: You get Thunder (rebellious Kelpie, obedience 0.2). Your task: get him to fetch a ball.
**What happens**: Thunder ignores your first 5 commands. You try tapping aggressively — his trust drops. The cocapn narrates: *"Thunder's obedience is 0.2. Aggressive commands reduce trust. I need a different approach."* You switch to gentle taps with rewards. After 10 successful fetch-reward cycles, obedience creeps to 0.25. Trust goes from Stranger to Familiar. Thunder starts listening — not because you forced him, but because he learned you're reliable.
**What you learn**: AI agents have capability boundaries. You can't force capability — you build it through trust. Low obedience isn't a bug, it's a personality trait that requires a specific training approach.

### Scenario 2: "The Evolution Lab" (Teaches: Genetic Algorithms)
**Setup**: You have 4 dogs with different strengths. Your task: breed a dog that can herd in under 30 seconds on the Advanced Course.
**What happens**: You analyze each dog's DNA. Rex has speed but no patience. Biscuit has patience but no speed. You breed them — the puppy gets speed 0.6, patience 0.65. Better than either parent alone. You breed the puppy with Blue (high intelligence) — grandpuppy gets speed 0.6, patience 0.65, intelligence 0.8. After 5 generations, you have a dog optimized for this specific course.
**What you learn**: Genetic algorithms work through selective pressure over generations. Each generation doesn't need to be perfect — it just needs to be better than the last. Crossover combines strengths, mutation discovers novel solutions, and tournament selection kills off weak offspring.

### Scenario 3: "Pack Panic" (Teaches: Multi-Agent Coordination)
**Setup**: 20 sheep, 3 dogs, narrow canyon, approaching storm. You have 90 seconds.
**What happens**: You assign Rex as lead, Biscuit as flanker, Thunder as blocker. Rex drives from behind, Biscuit keeps the sides tight, Thunder blocks the escape route. But the sheep panic — they scatter. Rex's bravery (0.8) keeps him driving, but Biscuit's gentleness (0.9) makes her slow down to calm sheep instead of pushing. Thunder's obedience (0.2) means he might ignore your blocker command. You have to decide: reassign roles? Equip Biscuit with a radio for faster communication? Or trust the pack to self-organize?
**What you learn**: Multi-agent systems have emergent failures. Individual agent strengths can become weaknesses in coordination. Equipment (radio) bridges communication gaps. The right role assignment matters more than individual skill.

## 10. TECHNICAL ARCHITECTURE

### Cloudflare Worker (~600 lines)
```
worker.ts
├── DNA system (crossover, mutation, fitness) — 80 lines
├── Dog agent (personality, trust, skills, equipment) — 120 lines
├── Training engine (reward shaping, skill progression) — 80 lines
├── Pack dynamics (role assignment, coordination) — 60 lines
├── Canvas renderer (2D top-down, touch controls) — 150 lines
├── Game state machine (kennel/training/course/breeding) — 50 lines
├── HTTP routes (API + HTML serving) — 60 lines
└── KV persistence (dog state, training history, lineage) — inline
```

### KV Schema
```
kennel:{userId} → { dogs: Dog[], unlockedTiers: string[], equipment: Equipment[] }
dog:{userId}:{dogId} → Dog (full state including DNA, trust, skills, training log)
lineage:{dogId} → { parents: [id, id], children: [id, ...], generation: number }
leaderboard → sorted by ELO rating
breeding_market → [{ dogId, owner, dna, price }]
```

### Canvas Render Loop (60fps)
- Grid-based terrain (grass, rocks, fences, sheep pen)
- Dogs as circles with breed-colored borders and personality indicators
- Sheep as white circles with scatter/flock AI (boids algorithm)
- Equipment visual indicators (collar, pouch, sensor)
- Trust bar above each dog (color: red→yellow→green→blue)
- Touch: tap to set waypoint, drag to draw path, long-press for command menu

### No LLM Required for Core Gameplay
- Dog narration uses template strings with personality modifiers
- LLM (optional) generates richer narration during key moments
- The AI is in the simulation, not the language model
