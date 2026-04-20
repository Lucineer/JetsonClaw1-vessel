# Research Summary — Cocapn Deep Research

## Executive Summary

Research across 7 topics reveals a coherent architecture for Cocapn: **a multi-tenant, edge-deployed AI coding education platform** built on Cloudflare Workers, using Git as both pedagogical tool and AI memory substrate, with BYOK for cost control and progressive hardening as the educational philosophy.

---

## Key Insights by Topic

### 1. Multi-Agent Orchestration → **Use CrewAI for MVP, LangGraph for complex flows**
- Don't over-engineer with 5+ agents. Start with 2-3 role-based agents (Instructor, Reviewer, Student-proxy).
- CrewAI's opinionated structure maps perfectly to the teacher/student paradigm.
- Token budgets are the real constraint — use smaller models for sub-agents, compress context between agent handoffs.
- **For Cocapn**: CrewAI Crew with sequential process. Instruct → Student works → AI reviews → Teacher approves.

### 2. Progressive Hardening → **The educational model IS the engineering model**
- The hardening spectrum (correctness → robustness → security → performance) maps directly to assignment difficulty progression.
- AI can automate the hardening pipeline: lint → type check → security scan → performance profile → improvement suggestions.
- Track metrics over time to show students their growth trajectory.
- **For Cocapn**: Each assignment has hardening levels. Students advance through levels, building real engineering discipline.

### 3. Fork-and-Ship Pedagogy → **Core workflow, not a feature**
- Fork-and-ship gives students real Git experience, persistent portfolios, and authentic feedback loops.
- GitHub Classroom handles the mechanics; Cocapn adds AI review on top.
- The student's repo IS their portfolio — no separate submission system needed.
- **For Cocapn**: Template repo per assignment. Student forks, implements, opens PR. AI reviews, teacher approves. Repo is portfolio.

### 4. BYOK Security → **Client-side keys for MVP, proxy for scale**
- Start with browser-side BYOK (simplest, most secure for single-user). Platform never touches keys.
- Add a LiteLLM proxy when you need usage tracking, rate limiting, and multi-device support.
- Encrypt any server-side key storage. Validate keys on input.
- **For Cocapn**: Students provide their own keys. Platform handles routing and review logic. No API cost for the platform.

### 5. Git-Based AI Memory → **Commits are learning events**
- Every observation, decision, and student interaction gets committed to a Git repo.
- Branches for experiments, tags for milestones, diffs for "what did we learn?"
- Combines with RAG for semantic search over accumulated knowledge.
- **For Cocapn**: Each cohort has a memory repo. Daily commits from AI interactions. Teachers can browse what the AI has learned. Experiments are branches.

### 6. Edge AI on Workers → **Hybrid: Workers AI for routing, external APIs for quality**
- Workers AI is 10-30x cheaper than OpenAI but limited to open-source models.
- Use Workers AI for classification, routing, quick feedback. Route complex tasks to Claude/GPT-4.
- Durable Objects for session state (no external database for conversations).
- Stream everything — perceived latency matters more than actual latency.
- **For Cocapn**: Workers AI classifies submissions and provides instant basic feedback. Complex code review goes to Claude via external API.

### 7. Subdomain Multi-Tenancy → **Workers for Platforms is the answer**
- One Worker, many subdomains. Tenant isolation via D1 tenant_id + middleware.
- Per-tenant Durable Object namespaces for session isolation.
- Automatic TLS, global distribution, generous free tier.
- Custom domain support as premium upsell.
- **For Cocapn**: `school.cocapn.com` for each institution. `class101.school.cocapn.com` for each class. Zero additional infrastructure.

---

## Cross-Cutting Themes

1. **Cost efficiency is paramount**: BYOK + Workers AI + edge routing = minimal platform costs. Students bear their own API costs.

2. **Progressive complexity**: Start simple (client-side BYOK, shared DB, single agent), add complexity only when needed (proxy, per-tenant isolation, multi-agent).

3. **Git is the universal substrate**: Student workflow (fork-and-ship), AI memory (commits as learning), and project management (branches as experiments) all use Git. One tool, many purposes.

4. **Edge-first architecture**: Everything runs on Cloudflare Workers. Inference, routing, session management, multi-tenancy — all at the edge. Minimal backend infrastructure.

5. **Human-in-the-loop is non-negotiable**: For education, AI assists but humans decide. Breakpoints in agent workflows, teacher approval gates, oral defense for integrity.

---

## Recommended Architecture Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Edge compute | Cloudflare Workers | Multi-tenancy, global distribution, free tier |
| AI inference (fast) | Workers AI (Llama 8B) | Cheap classification and quick feedback |
| AI inference (deep) | Claude / GPT-4 via external API | High-quality code review, complex reasoning |
| Agent orchestration | CrewAI (MVP) → LangGraph (scale) | Role-based agents for education |
| Session state | Durable Objects | Stateful conversations at the edge |
| Data storage | D1 (SQLite) + R2 + KV | Relational, files, config — all edge-fast |
| Multi-tenancy | Workers for Platforms | Subdomain routing, per-tenant isolation |
| AI memory | Git repos (per cohort) | Commits as learning, branches as experiments |
| API key management | Client-side BYOK → LiteLLM proxy | Zero platform API costs, user control |
| Student workflow | GitHub Classroom + custom CI/CD | Fork-and-ship with AI review pipeline |

---

## Next Steps

1. Prototype the Workers edge layer with hostname routing and BYOK
2. Implement fork-and-ship workflow with GitHub Classroom integration
3. Build the CrewAI agent pipeline (Instructor → Student → Reviewer)
4. Set up Git-based memory repo for AI learning
5. Add Workers AI for classification, external API for deep review
6. Implement progressive hardening pipeline (lint → test → security → AI review)
7. Design tenant provisioning API for multi-tenancy
