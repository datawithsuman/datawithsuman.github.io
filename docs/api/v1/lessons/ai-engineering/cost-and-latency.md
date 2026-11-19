# Cost and Latency: Routing, Caching and Batching

> How do you cut an LLM bill by 80% without losing quality?

- Track: AI Engineering › LLMOps › Lessons
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/ai-engineering/cost-and-latency/
- Before this: LLMOps: What's Different (`ai-engineering/llmops`), Prefix and Prompt Caching (`ai-engineering/prefix-caching`)
- Quiz topic: `llmops`

## Intuition

### The situation

The assistant handles 1 million conversations a month on a large model, with about 2,000 input tokens per request, 1,500 of them the same system prompt. Finance wants the bill cut, and a colleague says just switch to the cheapest model. The interviewer asks:

> How do you cut an LLM bill by 80% without losing quality?

**Running example:** the support assistant handles 1 million conversations a month on a large model. Each request sends ~2,000 input tokens (1,500 of them the shared system prompt and policy) and gets ~200 output tokens. Finance wants the bill cut.

#### Every request pays for the biggest model

Most support questions are easy ("where's my order?"), yet every one goes to the most capable, most expensive model, re-sends the same 1,500-token prompt, and generates a fresh answer even when the same question was answered a minute ago.

### The idea

Think of a clinic that sends everyone to the senior consultant, and rewrites the same intake form for each visit. Reuse the form. Have a nurse handle the simple cases, and pass the hard ones up. You only pay consultant rates for consultant problems, as long as hard cases really do get passed up.

[Figure: Monthly cost. The baseline is 9,000 dollars. Prompt caching alone brings it to 4,950 dollars. Prompt caching with routing and a semantic cache brings it to 1,688 dollars.]

_From the lab, with illustrative prices, 60% routed to the small model and a 20% semantic-cache hit rate._

### Play

**Try to break it.** Turn on prompt caching alone. Then raise the requests routed to the small model and the semantic-cache hit rate.

#### One big model for everything

1 M requests/month, 2,000 input tokens (1,500 cacheable prefix) and 200 output tokens each. Illustrative prices per million tokens: large model $3 input / $15 output; small model $0.15 / $0.60; cached input billed at 10% of the input price. Cache-write premiums and router cost ignored. Check current provider prices.

The baseline is **$9,000** a month. **Prompt caching** alone cuts it to $4,950 (**45%** saved) because 1,500 of every 2,000 input tokens are the same prefix, with zero quality risk. **Routing 60%** of requests to the small model saves 57.2% on its own. Together with prompt caching and a 20% semantic-cache hit rate, the bill falls to **$1,688 (81.2% saved)**; pushing to 80% routing and 30% cache hits reaches $815. The trap: each of those last savings carries quality risk. A router that sends a tricky refund dispute to the small model, or a cache that answers "cancel my order" with the stored reply for "can I cancel an order?", is a bug. Turn them up only as far as the eval set and online metrics allow.

**Now say why:** prompt caching has no quality risk, so what makes the other two savings risky?

## How it works

### How it works

#### In one breath

An LLM app's bill is (requests) × (input tokens × input price + output tokens × output price), and its latency is mostly output tokens × time per token. The big levers: **route** easy requests to a small, cheap model and only hard ones to the big model (RouteLLM cut cost by over 85% on MT-Bench while keeping 95% of GPT-4's quality); **cache** the stable prompt prefix (prompt caching) and, carefully, whole answers to near-identical questions (**semantic caching**); use **batch APIs** (typically 50% off) for anything non-interactive; and keep outputs short, since output tokens are the slow, expensive part. Every saving must be checked on the eval set, because a router or cache that's wrong 5% of the time is a quality regression.What you'll be able to do after this: estimate an LLM app's monthly cost, and apply routing, caching and batching with quality checks.

#### The levers

| Lever | How | Risk |
|---|---|---|
| **Routing** | a small classifier (RouteLLM) or rules send each request to a small or large model | hard requests misrouted to the small model |
| **Cascades** | try the cheap model first; escalate if a checker or confidence score says the answer is weak (FrugalGPT) | extra latency on escalations |
| **Prompt caching** | stable prefix billed at a discount and skipped in prefill | none if the prefix is truly static |
| **Semantic caching** | return a stored answer when a new question's embedding is very close to an old one | "can I cancel?" ≠ "cancel my order"; stale or personalised answers |
| **Batch APIs** | submit non-urgent jobs for asynchronous processing at a discount (often 50%) | hours of latency |
| **Shorter outputs** | concise instructions, max tokens, structured output | too terse answers |

FrugalGPT reported matching GPT-4's performance with up to 98% lower cost on its benchmarks using cascades; results depend heavily on the task mix.

## In practice

### In practice

#### Latency levers, and how to roll out savings

- **Latency:** stream tokens; cut output length (it dominates time); use smaller or distilled models for simple steps; run independent calls in parallel; speculative decoding if you self-host; prompt caching lowers time to first token.

- **Roll out safely:** start with zero-risk savings (prompt caching, shorter outputs, batch API for offline jobs), then add routing with a conservative threshold, shadow-test it against the big model on real traffic, and raise the threshold while quality holds.

- **Semantic cache hygiene:** high similarity thresholds, exclude personalised or time-sensitive answers, include policy version in the cache key, expire entries when documents change.

- **Track** cost per resolved conversation, not just cost per call: a cheaper model that causes more escalations to humans may cost more overall.

**Reasoning models add hidden tokens.** They write reasoning tokens before the answer, billed as output, so the effort setting can change cost and latency more than any prompt edit. See Prompting Reasoning Models. For rate limits, retries and fallbacks, see LLM API Reliability.

#### Pay big-model prices only for big-model problems

Cache what repeats, route what's easy, batch what can wait and keep outputs short, and verify each saving against the same quality evaluation before turning it up.

### The answer that sounds right

#### "Just switch to the cheapest model"

It sounds right, since the price per token is what shows on the bill. But a cheaper model that causes more escalations to humans may cost more overall, so measure the quality and escalation impact. "Cache everything" fails the same way: "can I cancel?" isn't "cancel my order", and personalised or time-sensitive answers must not be shared.

## Say it

### How do you cut an LLM bill by 80% without losing quality?

#### The interviewer pushes further

Follow-up 1 of 3

How would you build the router?

Train a small classifier on preference or correctness data (which model's answer was good enough), or start with rules (intent, length, keywords); calibrate the threshold on the eval set and shadow-test.

Follow-up 2 of 3

Why are output tokens priced higher than input tokens?

Input is processed in parallel during prefill; output is generated one token per memory-bound decode step, using far more GPU time per token.

Follow-up 3 of 3

What's the risk of semantic caching?

Returning an answer to a question that's similar in wording but different in meaning or context (another user's order, an outdated policy); mitigate with strict thresholds, scoping and expiry.

#### The 30-second answer

Cost is requests times input and output tokens times prices, and latency is mostly output length. I'd start with risk-free savings: prompt caching for the static prefix, shorter outputs, and batch APIs for offline work. Then model routing or cascades, sending easy requests to a small model; RouteLLM reported over 85 percent cost reduction on MT-Bench at 95 percent of GPT-4 quality. Semantic caching helps for repeated questions but needs high thresholds and exclusions for personalised or time-sensitive answers. Each lever gets validated on the eval set and online metrics, and I'd track cost per resolved conversation rather than per call.

**Go further**

#### What not to say

- "Just switch to the cheapest model." Measure the quality and escalation impact.

- "Cache everything." Personalised and time-sensitive answers must not be shared.

**Key terms and sources**

How to make an LLM application cheaper and faster without losing quality: where the money goes (input vs output tokens, model tier), model routing and cascades, prompt caching and semantic caching, batch APIs, shorter outputs and streaming, and how to measure the quality cost of each saving · built from Ong et al. (RouteLLM, ICLR 2025), Chen, Zaharia & Zou (FrugalGPT, TMLR 2024), Bang (GPTCache, 2023), the Anthropic and OpenAI prompt caching and batch API documentation, and Leviathan et al. (speculative decoding, 2023) · checked 29 Oct 2026

#### Sources

1. I. Ong et al., "RouteLLM: Learning to Route LLMs with Preference Data", ICLR 2025, arXiv:2406.18665.

2. L. Chen, M. Zaharia & J. Zou, "FrugalGPT: How to Use Large Language Models While Reducing Cost and Improving Performance", TMLR 2024, arXiv:2305.05176.

3. F. Bang, "GPTCache: An Open-Source Semantic Cache for LLM Applications", NLP-OSS 2023.

4. Anthropic and OpenAI documentation: prompt caching and batch processing (pricing varies by model; checked Oct 2026).
