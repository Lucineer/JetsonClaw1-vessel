# COCAPN MONETIZATION HANDOFF — 2026-04-05
## Step-by-step instructions for Casey

### What's already built
- Playground with free credits (5 per visitor, ~$0.0002/visitor)
- BYOK Workshop mode (user provides own key, unlimited)
- Credit earn system (ads + tutorials)
- Honest cost display
- Fork security (keys in CF Secrets Store, never in repo)

### What needs building (by Casey, human steps)

---

## STEP 1: Open a Stripe account (30 min)
1. Go to https://dashboard.stripe.com/register
2. Business type: Sole proprietorship
3. Business name: Cocapn / DiGennaro Tech (whatever your LLC is)
4. Bank account: your personal/business checking
5. Enable: Subscriptions, Invoicing, Payment Links

## STEP 2: Create Stripe Products (20 min)
Create these products in Stripe dashboard:

**Product 1: Cocapn Standard** — $10/mo
- Description: "Managed API keys, 1% cost-plus, analytics dashboard"
- Recurring: monthly

**Product 2: Cocapn Gold** — $50/mo
- Description: "Zero cost-plus, crystal graph, custom domains, equipment marketplace"

**Product 3: Cocapn Enterprise** — $200/mo
- Description: "White-label invoicing, seat management, SLA"
- Then create an addon: "Enterprise Seat" — $12/mo per seat

## STEP 3: Create Payment Links (10 min)
In Stripe, create Payment Links for each product:
- Copy the URLs (they look like buy.stripe.com/xxxxx)
- These are your checkout pages — no code needed

## STEP 4: Add membership CTA to the-fleet (5 min — I do this)
Once you have Stripe links, give them to me and I'll:
- Add "Upgrade to managed keys" button in Settings modal
- Show pricing comparison (BYOK free vs Standard $10 vs Gold $50)
- Link to Stripe Payment Links
- Add /pricing page with full tier comparison

## STEP 5: Set up Stripe Customer Portal (15 min)
1. In Stripe dashboard → Settings → Customer portal
2. Enable: Subscription management, cancellation, invoice history
3. Copy the portal URL
4. Give it to me — I'll add "Manage subscription" link

## STEP 6: Connect Stripe to Workers (I do this later)
This requires a Stripe webhook endpoint:
1. Stripe → Developers → Webhooks
2. Point to fleet-orchestrator /api/billing/webhook
3. Events: checkout.session.completed, customer.subscription.updated, invoice.paid
4. I'll build the webhook handler that provisions API keys on subscription

---

## ENTERPRISE BILLING RULES (important — implement these)

### Auto-seat upgrade (the smart cap)
- Light users: **no seat required**, billed at **10% cost-plus**
- When a user's monthly API spend hits **$12**: a seat is **automatically added** ($12/mo)
- After seat is added: billing switches to **at cost** (zero cost-plus)
- **Maximum per-user cost = $12/month** (the seat price)
- This means: $0-12 range = 10% markup, $12+ range = at cost
- Enterprise can offer trial programs because casual users cost almost nothing

### Why this works
- 100 casual users at $2 API each = $20 cost + $2 markup = $22 total
- 10 power users at $50 API each = 10 seats × $12 = $120 (capped!)
- Total: $142 for 110 users, predictable billing
- Without auto-seat: 100 × $2 = $200 at 10% markup, 10 × $50 = $500 at 10% markup = $770

### Ad-supported enterprise clients
- Enterprise clients can let their free users' costs be covered by ads
- We serve ads, ad revenue offsets API costs
- Enterprise keeps their free tier free, we get ad revenue
- Heavy users upgrade to paid → seats → revenue

---

## STEP 7: Set up Carbon Ads or similar (30 min)
Options for ad network:
1. **EthicalAds** — https://www.ethicalads.io/ — developer-focused, privacy-respecting
2. **BuySellAds** — https://www.buysellads.com/ — broad reach
3. **AdStera** — https://adsterra.com/ — easy signup
4. **Self-serve** — sell ad spots directly to AI/dev tool companies

For HN launch: EthicalAds is the right fit (developer audience).

## STEP 8: GitHub Sponsors / Buy Me a Coffee (10 min)
1. Go to https://github.com/sponsors — enable sponsors on your profile
2. Or https://www.buymeacoffee.com/ — create a page
3. This is for the "support the project" link in the footer
4. Optional 10% opt-in to Cocapn system — NEVER mandatory

---

## LATER (post-launch, post-traction)

### Community asset sharing
- Users generate images/content → shared pool
- Popular assets get reused → less regeneration → lower costs
- "Likes" on assets create hero developers
- Marketplace for ideas → actualized into livings
- This is the REAL moat — not code, not pricing, but community-generated assets

### Cost savings as we scale
- Batch inference jobs across users (similar prompts → shared cache)
- Crystal graph reduces repeated LLM calls
- Dead reckoning avoids regeneration
- Community assets reduce unique generation needs
- These savings get passed to members → competitive advantage

### Enterprise invoicing
- We bill enterprise on their letterhead
- Consolidated monthly invoice
- Per-seat breakdown
- API usage by endpoint/model
- Enterprise passes their own pricing to their users
- We're invisible to end users — just the billing engine

---

## PRIORITY ORDER (what Casey does today)

1. ✅ Stripe account
2. ✅ Stripe products + payment links
3. ✅ Customer portal setup
4. ✅ Give me the Stripe links → I add CTAs
5. ✅ Ad network signup
6. ✅ GitHub Sponsors

Total human time: ~2 hours

Everything else (webhook handling, auto-seat logic, ad integration, asset sharing) I build after you give me the Stripe links.

---

## REVENUE PROJECTIONS

### Conservative (Year 1)
- 500 Gold members × $50 = $25,000/mo
- 50 Enterprise × $200 + avg 20 seats × $12 = $22,000/mo
- 2,000 Standard × $10 = $20,000/mo
- Pay-as-you-go 10% on ~$10K API = $1,000/mo
- Ad revenue (light users) = $2,000/mo
- **Total: ~$70,000/mo**

### Optimistic (Year 1, viral HN)
- 2,000 Gold × $50 = $100,000/mo
- 200 Enterprise × $200 + avg 50 seats × $12 = $160,000/mo
- 10,000 Standard × $10 = $100,000/mo
- **Total: ~$360,000/mo**

### Key insight
- Enterprise seats are the main revenue driver
- One enterprise with 1000 seats = $12,000/mo recurring
- The auto-seat cap makes this predictable and fair
- Community assets + crystal graph = costs decrease over time = margins increase
