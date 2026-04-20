# Edge AI on Cloudflare Workers

## Overview

Cloudflare Workers provides a serverless edge computing platform that now includes AI inference capabilities. Running LLM inference at the edge offers low latency, global distribution, and tight integration with Cloudflare's broader platform (CDN, Durable Objects, R2, KV).

## Workers AI

### What It Is
- Cloudflare's inference-as-a-service platform running on their global network
- Models hosted on Cloudflare's GPUs (NVIDIA A100/H100 clusters in 30+ locations)
- Pay-per-use pricing (no idle costs)
- API-compatible with OpenAI's chat completions format

### Available Models (2024-2025)
- **LLMs**: Llama 3.1 (8B, 70B), Mistral (7B, 8x7B), Qwen, Phi-3, Gemma
- **Embeddings**: BGE, OpenAI text-embedding-3-small
- **Image generation**: Stable Diffusion XL
- **Audio**: Whisper (speech-to-text), Bark (TTS)
- **Classifiers**: Toxicity detection, sentiment analysis

### Pricing
- Free tier: 10,000 neurons/day (a "neuron" is a unit of compute)
- Paid: $0.011 per 1000 neurons
- Significantly cheaper than direct OpenAI/Anthropic API calls for equivalent models
- No cold start for popular models (always warm in major locations)

### Limitations
- Model selection is limited compared to OpenAI/Anthropic (no GPT-4, no Claude)
- Context window limits vary by model (typically 4K-8K tokens, some support 128K)
- Fine-tuning not yet available (use LoRA adapters with Workers AI or external fine-tuning)
- Rate limits apply per account

## Durable Objects for AI

### What They Are
- Single-tenant, globally distributed stateful objects
- Exactly-once execution, strong consistency
- Perfect for: session management, rate limiting, stateful AI conversations, collaborative editing

### AI-Specific Use Cases
- **Conversation state**: Each Durable Object holds a user's conversation history. No database needed for chat context.
- **Rate limiting**: Per-user token tracking. Enforce limits in real-time at the edge.
- **Session affinity**: Route a user's requests to the same object for consistent AI behavior.
- **AI coordination**: Multiple agents communicating through a shared Durable Object (like a message bus).

### Streaming
- Workers support the Streams API natively
- AI inference can be streamed token-by-token to the client
- Use `ReadableStream` + `TransformStream` for processing
- Durable Objects can stream responses through WebSocket or HTTP SSE
- Latency: typically 50-200ms first token, then token-by-token streaming

## Architecture Patterns

### Pattern 1: Edge Inference (Simple)
```
Client → Worker → Workers AI → Client (streamed)
```
- Fastest possible latency
- No server, no database
- Good for: simple Q&A, classification, summarization

### Pattern 2: Edge + State
```
Client → Worker → Durable Object (state) → Workers AI → Client
```
- Stateful conversations at the edge
- Durable Object stores chat history
- Good for: tutoring sessions, multi-turn interactions

### Pattern 3: Edge Router + Backend
```
Client → Worker (routing/auth) → Backend API (OpenAI/Anthropic) → Client
```
- Edge handles auth, rate limiting, BYOK key management
- Backend calls external LLM APIs
- Good for: when you need GPT-4/Claude (not available on Workers AI)

### Pattern 4: Hybrid Inference
```
Client → Worker → Workers AI (small model for routing)
                    → External API (large model for complex tasks)
```
- Use cheap/fast edge model for classification, routing, simple tasks
- Route complex tasks to external providers
- Reduces cost while maintaining capability

## Performance Characteristics

| Metric | Workers AI | External API (OpenAI) |
|--------|-----------|----------------------|
| First token latency | 50-200ms | 200-800ms |
| Subsequent tokens | 20-50ms/token | 20-80ms/token |
| Cold start | None (warm) | N/A (serverless) |
| Global latency | Low (30+ locations) | Depends on backend location |
| Cost per 1M tokens | ~$0.30-1.00 (Llama 70B) | ~$3-30 (GPT-4) |

## Actionable Recommendations for Cocapn

1. **Use Workers AI for classification and routing**: When a student submits code, use a small Workers AI model to classify the submission (what concept is being tested, difficulty level, quality tier). Route to more expensive models only for complex analysis.

2. **Durable Objects for session state**: Each tutoring session is a Durable Object. It holds conversation history, student context, and current task state. When the student returns, the session resumes exactly where it left off. No external database needed.

3. **Stream everything**: LLM responses should stream to the client. Use SSE or WebSocket from Workers. The perceived latency improvement is dramatic — users start reading after 100ms instead of waiting 5 seconds.

4. **Hybrid model strategy**:
   - Workers AI (Llama 8B): Code linting, quick feedback, simple Q&A — cheap and fast
   - External API (Claude/GPT-4): Deep code review, curriculum design, complex explanations — expensive but higher quality
   - Route based on task complexity and student tier

5. **Rate limiting at the edge**: Use Durable Objects or Cloudflare's built-in rate limiting to prevent abuse. Track per-student token usage. Implement tiered limits (free tier: 100K tokens/day, paid: unlimited).

6. **KV/R2 for long-term storage**: Workers KV for configuration and frequently-read data. R2 (S3-compatible) for storing student code submissions, generated feedback, and artifacts. Both are edge-fast.

## Anti-Patterns

- Running heavy models on Workers AI when you need GPT-4 quality — use external APIs
- Storing large conversation histories in Durable Objects — they have a 128MB memory limit, use R2 for long-term storage
- Ignoring cold start for Durable Objects — first request to a new DO has ~100ms overhead
- No caching — cache identical requests (same code + same prompt = same feedback)
