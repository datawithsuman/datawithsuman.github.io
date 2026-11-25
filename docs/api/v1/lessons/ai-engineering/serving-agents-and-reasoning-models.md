# Serving Agents and Reasoning Models

> Agents make dozens of calls per task, and reasoning models write thousands of hidden tokens. What does that do to serving?

- Track: AI Engineering › LLM inference and serving › Lessons
- Type: Concept · 18 min
- Page: https://aimlrounds.com/tracks/ai-engineering/serving-agents-and-reasoning-models/
- Before this: Prefix and Prompt Caching (`ai-engineering/prefix-caching`), KV Cache Compression, Eviction and Offloading (`ai-engineering/kv-cache-compression`)
- Quiz topic: `infer`
- Sources checked: 2026-11-07 · Text last changed: 2026-11-20 · Version: 1bdb660c7c

## Intuition

### The situation

Your coding agent's per-request latency looks fine on the dashboard, but tasks take minutes and cost far more than planned. Requests have also got longer since you switched to a reasoning model. The interviewer asks:

> Agents make dozens of calls per task, and reasoning models write thousands of hidden tokens. What does that do to serving?

#### Why it matters

Agentic and reasoning workloads are growing fast, and they break assumptions built for chat. A request may be cheap while the task is expensive. This lesson connects prefix caching, KV offloading and serving metrics to these workloads. For the agent loop itself, see What Is an Agent?

### The idea

Think of a researcher who, before every step, rereads all their notes so far, then makes a phone call to check something, then writes a little more. If the notes stay open on the desk, rereading is quick. If someone tidies them away during every call, each step starts with a long trip to the archive.

[Figure: Three things change. History is resent every step. Caches must survive tool calls. Reasoning makes decode dominate.]

_Measure per task, not per request._

### Play

**Try to break it.** Let the cache expire during tool calls. Then raise the steps, then the hidden reasoning.

#### Price an agent task

Illustrative: a 5,000-token system prompt and tools, 200 visible output tokens per step, $3 per million input tokens, $0.30 per million cache reads, $3.75 per million cache writes, $15 per million output tokens, and 50 output tokens per second. Hidden reasoning is billed as output, and assumed to be dropped from the history, as many APIs do. Not any provider's real price.

A 20-step task reads about 423,000 input tokens, as the history is resent every step. With a **warm cache**, 91% of them are cheap cache reads, and the task costs about $0.47. If the cache **expires at every tool call**, the same task costs about $1.80, about 3.9 times as much. Now raise the steps to 40: input grows to 1,526,000 tokens, and the gap widens to $1.12 against $6.14. Then raise hidden reasoning to 4,000 tokens per step: cost rises to $1.52, and generation alone takes about 28 minutes, which is why reasoning models are planned around decode.

**Now say why:** why does an expired cache cost so much more at step 20 than at step 2?

## How it works

### How it works

#### In one breath

A chat question is one request. An **agent task** is a chain of many, each resending the growing history, with pauses while tools run. A **reasoning model** writes long hidden reasoning before answering, so it's dominated by slow, memory-bound decode. Both make the KV cache and its reuse central. Cache the shared history so each turn only processes new tokens, keep caches alive across tool calls, route each task back to the machine that holds its cache, and judge the system on **cost and time per task**, not per request.

#### What changes

##### Reasoning models are decode-heavy

Every hidden reasoning token is generated one at a time, just like the answer. So a model that thinks for 5,000 tokens spends most of its time in memory-bound decode, and those tokens are usually billed as output. Ways to control this include thinking budgets, routing easy questions to a non-thinking mode, and speculative decoding for faster decode.

##### Agents resend their history

Each step of an agent sends the system prompt, the tools and the whole history so far, plus the latest tool result. Without caching, the work grows with the square of the steps. With caching, each step only processes its new tokens, and cached input is billed at a fraction of the price.

##### Keeping caches warm

| Problem | Fix |
|---|---|
| A slow tool call outlasts the cache's lifetime | Use a longer cache lifetime, or offload the cache rather than evicting it |
| Replicas each hold different caches | Route a task back to the same replica, or use a shared cache tier |
| Eviction drops agents' long histories | Keep shared prefixes and recent turns, and evict the middle |
| Editing or trimming early history breaks the match | Append rather than edit, or accept a re-prefill when you summarise |

Provider prices show why it matters. As of November 2026, Anthropic bills cache reads at 0.1× the input price, and less for its newest models, with writes at 1.25× for a 5-minute cache or 2× for an hour. OpenAI's newest models bill writes at 1.25× for a 30-minute default cache, with discounts of up to 95%. Check current pricing, as it changes often.

##### What research reports

- **Smarter eviction:** keeping shared prefixes and recent turns cut average time to first token by up to 60% against SGLang, in one 2026 study of agent workloads.

- **Load-aware reuse:** requests in one queue can differ by up to 100× in uncached work. A scheduler aware of this reported p99 time to first token up to 8.6× lower than earlier prefix-aware schedulers.

- **Across models:** agents and cascades move requests between models. A 2026 system reuses caches across models, rather than within one only.

#### The maths

$$ {\text{input tokens}} = \sum_{i=1}^{{N}} \big({S} + (i-1)\,{D}\big), \qquad {\text{cached share}} \approx 1 - \frac{{S} + N\,D}{\text{input tokens}} $$

Our own arithmetic for an agent that appends to its history, if every step hits the cache.

- **input tokens for the task**: Across every call the agent makes.

- **steps in the task**: One model call per step.

- **the fixed start**: System prompt and tool definitions, sent every time.

- **new tokens per step**: The model’s output plus the tool result, added to the history.

- **what caching can skip**: Everything except the first copy of the start and each step’s new tokens.

- **the start again**: Processed once, then read from the cache.

## In practice

### In practice

#### In practice

- **Measure per task:** track cost, steps, cache hit rate and wall-clock time per completed task, as well as per-request latency.

- **Keep history append-only:** stable tools first, then history, then new results. Avoid edits early in the prompt.

- **Trim tool output:** a 5,000-token tool result is resent at every later step. Summarise or truncate it.

- **Budget reasoning:** cap thinking where tasks allow, and send simple steps to a cheaper or non-thinking model.

- **Separate batch from interactive:** long-running background agents can use cheaper capacity and looser latency targets.

### The answer that sounds right

#### "Each request is fast, so the agent is fast"

It sounds right, since the requests are what you monitor. But a task may make dozens of them, each resending the history, and broken caching or extra steps add up. Measure cost, steps and time per completed task as well.

## Say it

### Agents make dozens of calls per task, and reasoning models write thousands of hidden tokens. What does that do to serving?

#### The interviewer pushes further

Follow-up 1 of 3

An agent's cost jumped after a tool started taking 10 minutes. Why?

The cache probably expired during the wait, so the next step had to re-read the whole history as fresh input, and pay to write the cache again. Use a longer cache lifetime, or offload rather than evict, and check the cache hit rate per step.

Follow-up 2 of 3

Why measure per task rather than per request?

An agent's requests are cheap individually, but a task may make dozens of them. A change that makes each request faster can still make the task slower, or more expensive, if it adds steps or breaks caching.

Follow-up 3 of 3

How do reasoning models change capacity planning?

They generate far more output per request, so decode dominates time and GPU use. Plan on output tokens per second, and on concurrency held for longer, and consider separate pools or budgets for long thinking.

#### The 30-second answer

Agents and reasoning models change what dominates. A reasoning model writes thousands of hidden tokens, so it's mostly memory-bound decode, and I'd control that with thinking budgets, routing simple steps to cheaper modes, and speculative decoding. An agent resends its growing history at every step, so without caching, input grows with the square of the steps. With prefix caching, each step only processes new tokens, and cache reads are billed at a fraction of the price. To keep caches warm, I'd use longer cache lifetimes or offloading across slow tool calls, route each task back to the replica holding its cache, keep history append-only, and trim tool output. And I'd measure cost and time per task, not per request.

**Key terms and sources**

Why reasoning models are decode-heavy, how agents resend growing histories, caching across turns and tool calls, cache lifetimes, routing back to warm caches, and cost per task. · checked 7 Nov 2026

#### Sources

- [Rethinking KV Cache Eviction for Agentic LLM Serving](https://arxiv.org/abs/2611.00391)

- [Fairway: Load-Aware KV Cache Reuse for LLM Prefill Scheduling](https://arxiv.org/abs/2611.02082)

- [CacheBridge: Cross-Model KV Transfer for Multi-Model LLM Serving](https://arxiv.org/abs/2609.00891)

- [Anthropic, Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)

- [OpenAI, Prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching)

- [Liu et al., LMCache](https://arxiv.org/abs/2510.09665)

Explanations are ours, built from these sources. Lab numbers are illustrative unless a lab says otherwise. Many recent papers are preprints, and vendor results are their own.
