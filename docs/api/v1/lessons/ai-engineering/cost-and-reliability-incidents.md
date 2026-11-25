# Cost and Reliability Incidents

> 9 incidents: an overnight cost spike, rate limits, a retry storm, runaway outputs, a cache leak, bad routing, a provider outage, cut-off streams, long chats.

- Track: AI Engineering › LLMOps › Scenarios
- Type: Interview · 40 min
- Page: https://aimlrounds.com/tracks/ai-engineering/cost-and-reliability-incidents/
- Before this: Cost and Latency: Routing, Caching and Batching (`ai-engineering/cost-and-latency`), LLM API Reliability: Rate Limits, Retries and Fallbacks (`ai-engineering/llm-api-reliability`)
- Quiz topic: `llmops`
- Sources checked: 2026-11-10 · Text last changed: 2026-11-19 · Version: eea5227a54

How to use this page

Give yourself about 5 minutes per question, as in an interview. Each is a cost spike or outage in an LLM product. Say your diagnosis out loud (most likely cause first, how you'd confirm it, then the fix), then open the answer and compare.

**The diagnosis order:** attribute the cost or failure to a feature, model and request type → find what changed (traffic, prompt, model, provider) → check limits, retries and caches → fix the cause and add a budget, alert or test so it can't recur.

Question 1 · Easy · cost spike

### The LLM bill doubled overnight. Traffic is flat. What do you check first?

Answer: **cost per request by feature and model, to find what changed**

1. With flat traffic, cost per request must have risen: longer prompts, more output, a pricier model, or more calls per request.

2. Break cost down by feature, model and token type from logs, and compare with yesterday.

3. Fix the cause (for example an agent loop or a prompt that now includes a whole document), then add per-feature budgets and alerts.

**Follow-up:** Why per-feature, not just total? A total alert tells you something is wrong; a per-feature one tells you where.

Question 2 · Easy · rate limits

### At peak hours, about 5% of requests fail with 'too many requests' errors from the LLM provider. What do you do?

Answer: **you're hitting the provider's rate limits; smooth and limit your traffic**

1. Peak demand exceeds your requests-per-minute or tokens-per-minute quota.

2. Confirm with the error codes and your request rate at those times.

3. Fix: retry with exponential backoff and jitter, queue low-priority work, raise quotas with the provider, and spread load across deployments or regions.

**Follow-up:** Which requests should wait? Batch and background jobs first, so user-facing requests keep their capacity.

Question 3 · Medium · retry storm

### The provider had a short slowdown, but your service stayed down for 20 minutes afterwards, with request volume to the provider 5× normal. Why?

Answer: **a retry storm: clients retried immediately and repeatedly, overloading the provider as it recovered**

1. Every failed call retried at once, multiplying load right when capacity was low.

2. Check retry counts and timing in logs; synchronised spikes give it away.

3. Fix: exponential backoff with jitter, a retry budget, a circuit breaker that stops calling a failing provider, and respect for Retry-After headers.

**Follow-up:** What's a retry budget? A cap on retries as a share of requests, say 10%, so retries can never multiply traffic.

Question 4 · Medium · output length

### A few requests cost 50× the average and take minutes. They all produce enormous outputs. What's missing?

Answer: **limits on output length**

1. Without a maximum output, some prompts make the model ramble or repeat until it hits the model's limit.

2. Find the requests with the most output tokens and read them.

3. Fix: set max output tokens per feature, add stop sequences, and alert on unusually long outputs.

**Follow-up:** Won't limits cut off good long answers? Set them per feature from real needs, and detect truncation so you can handle it.

Question 5 · Medium · cache leak

### To cut costs, you cached answers by question text. A user then saw an answer containing another customer's order details. What went wrong?

Answer: **the cache key ignored who was asking, so personalised answers were shared**

1. Answers that depend on the user's data can't be shared just because the question matches.

2. Find which cached entries contain user-specific data, and which features use the cache.

3. Fix: cache only non-personal answers, or include user or permission scope in the key; purge the cache and treat it as a data incident.

**Follow-up:** What can you still cache safely? Prompt prefixes and answers to general questions with no personal data.

Question 6 · Medium · routing

### Routing simple questions to a small model cut costs by 60%, but complaints about wrong answers on tricky questions doubled. What do you change?

Answer: **the router is sending hard questions to the small model**

1. The router's idea of 'simple' doesn't match real difficulty.

2. Evaluate the router: label a sample of routed questions as easy or hard, and check quality per route.

3. Fix: improve the router, escalate to the large model when the small one is unsure or fails a check, and track quality per route as a guardrail.

**Follow-up:** How do you choose the routing threshold? From the cost and quality curve on your eval set, with quality as a hard floor.

Question 7 · Hard · outage

### Your only LLM provider had a two-hour outage, and your whole product was down. How do you design for this next time?

Answer: **add tested fallbacks and graceful degradation**

1. A single provider is a single point of failure.

2. List which features need an LLM and what an acceptable fallback is for each.

3. Fix: a second approved provider or self-hosted model behind a gateway, tested regularly; cached or simpler responses for some features; clear messages when a feature is unavailable.

**Follow-up:** Why test fallbacks regularly? Prompts tuned for one model may behave differently on another; untested fallbacks fail when you need them.

Question 8 · Hard · streaming

### Under heavy load, long streamed answers get cut off at around 60 seconds, though the model is still generating. What's happening?

Answer: **a proxy or load balancer timeout is closing long-lived connections**

1. Many proxies close connections after a fixed time or an idle period, which long streams can hit.

2. Check where the connection is closed: client, load balancer, gateway or provider, and their timeout settings.

3. Fix: raise timeouts for streaming routes, send keep-alive or heartbeat events, and let clients resume or show partial results clearly.

**Follow-up:** Why does it only happen under load? Generation slows when the server is busy, so streams run past the timeout.

Question 9 · Hard · long chats

### Cost per conversation grows much faster than conversation length: long chats cost far more than you'd expect. Why?

Answer: **every turn resends the whole history, so total tokens grow roughly with the square of the number of turns**

1. Turn 20 sends all 19 previous turns again, and so on, so totals climb quickly.

2. Plot input tokens per turn over a conversation.

3. Fix: use prompt caching for the stable history, summarise or trim older turns, and keep key facts in a compact memory.

**Follow-up:** Does summarising lose information? It can; keep important facts explicitly and test long-conversation quality.

**More practice and sources**

9 interview questions, easy to hard · answers hidden until you click · checked 10 Nov 2026

Keep practising

Uses these lessons: Cost and Latency, LLM API Reliability, Tracing and Observability, Prefix Caching and Agent Infrastructure.
