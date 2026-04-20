# COCAPN WORKSHOP ARCHITECTURE — 2026-04-05

## Vision: Playground → Workshop → Fleet Hub

### Tier 1: Playground (FREE — marketing funnel)
- Text-only, cheapest models (DeepSeek-chat)
- 5 free credits, honest cost display
- Purpose: convert visitors into users
- Cost to us: ~$0.0002/visitor (negligible)

### Tier 2: Workshop (AD-SUPPORTED — upgrade path)
- User selects models — cheaper ones can be ad-funded
- Watch video ad → unlock audio TTS for next interaction
- Watch video ad → unlock image generation for next interaction
- More expensive models (DeepSeek-Reasoner, Seed-2.0-pro) require more ads or BYOK
- Banner ads optional — user controls density vs. discount
- Audio is the killer feature for younger students (dmlog-ai, studylog-ai)
- Two-way voice is the holy grail (but expensive)

### Tier 3: BYOK Workshop (USER'S KEYS — zero cost to us)
- User adds API keys in settings (or via fork on GitHub)
- User connects their Cloudflare account → Workers + secrets
- All models available, no limits, no ads
- THIS IS PREFERRED: integrates user into Cloudflare ecosystem
- Long-term: Cloudflare affiliate revenue stream

### Tier 4: Fleet Hub (COMMUNITY — the real product)
- Users clone repos, deploy to their own infra (local, AWS, Docker, Jetson)
- Custom domain: user.studylog.ai (proxied through our Workers)
- User's public git-agent gets a nice URL for sharing
- Analytics: trending model choices, temperature preferences, popular equipment
- AI summarizes PRs on forks → surface novel features community-wide
- Users become heroes: bounties, buy-me-a-coffee on their agents
- Optional 10% opt-in to cocapn system (NEVER mandatory — prevents top creators from leaving)

### Tier 5: Marketplace (ECONOMY — bounties + equipment)
- User posts bounty: "I need a fishing-tuned git-agent for my boat"
- Other users build it, submit PR, get paid
- Equipment marketplace: any agent can equip any compatible module
- Equipment has vessel specs (hardware requirements, memory, etc.)

## Hardware Fleet Vision (FishingLog.ai Physical)
- Commercial fishing boat = multi-Jetson fleet
- Each Jetson = one vessel (chatbot, navigation, lighting, cameras, autopilot)
- Commodore vessel coordinates sub-vessels
- Redundancy: extra Jetson on standby, hot-swappable
- Priority triage: if navigation fails, chatbot reduces resources or switches to cloud
- Cross-vessel support: any Jetson can run any vessel's software
- Lower priority jobs: data processing, token reduction for other AIs
- Hardcoded fallbacks for critical systems
- Starlink dependency = cloud is unreliable at sea → local inference preferred

## Revenue Streams (in order of priority)
1. **Education & training** — courses, certifications for technicians
2. **Hardware sales** — pre-built Jetson kits for boats (manufactured by Casey)
3. **Technician network** — trained installers/servicers (Casey trains, they pay)
4. **Cloudflare affiliate** — users connecting CF accounts through our platform
5. **Community marketplace** — 10% optional cut on bounties/equipment sales
6. **Analytics** — usage pattern data signals hardware/software demand
7. **API gateway** — small markup on pay-as-you-go for users who don't want BYOK

## Key Principle
Consumers are NOT ignorant about margins. Post-opaque-marketing world.
Every cost is displayed. Every option is honest. Users choose their own balance of ads vs. cost vs. BYOK.
