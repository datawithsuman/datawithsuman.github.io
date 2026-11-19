# Prefix and Prompt Caching

> Why are repeated system prompts nearly free, until a timestamp breaks them?

- Track: AI Engineering › LLM inference and serving › Lessons
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/ai-engineering/prefix-caching/
- Before this: KV Cache Management and PagedAttention (`ai-engineering/kv-cache-and-pagedattention`)
- Quiz topic: `infer`

## Intuition

### The situation

Every support request starts with the same 2,000-token system prompt, followed by about 200 tokens from the customer. A colleague turns on prompt caching, but also adds the current time at the top of every prompt. The bill goes up. The interviewer asks:

> Why are repeated system prompts nearly free, until a timestamp breaks them?

**Running example:** every support request starts with the same system prompt (tone, refund policy, tool definitions), followed by about 200 tokens from the customer.

#### Recomputing the same prompt thousands of times

With a 2,000-token system prompt and a 200-token question, more than 90% of every request's prefill is identical work. Prefill drives time to first token and, with APIs, most of the input bill. Agents and multi-turn chats make it worse: each turn resends the whole history.

### The idea

Think of a running total down a long column. Each line depends on everything above it. Two sheets with the same first 2,000 lines have the same totals, so you can copy them. Change line 1 and every total after it changes, so nothing can be reused.

[Figure: With the system prompt first, it is reused: 90.8 percent of prefill is saved. With a timestamp first, nothing after it matches: nothing is saved and input costs 125 percent.]

_From the lab: 1,000 requests, with Anthropic-style pricing._

### Play

**Try to break it.** Compare no caching, a timestamp at the start and the shared system prompt first. Then change the system prompt length.

#### Put the timestamp first, or last?

1,000 requests, each = system prompt + 200 unique customer tokens, all within the cache lifetime. Cost uses Anthropic-style pricing: first write 1.25×, cached reads 0.1×, uncached input 1×. The timestamp case writes a new cache entry every time and never reads it.

With the shared **2,000-token system prompt first**, all but the first request reuse it: only **202,000** of 2.2 million prefill tokens are computed (**90.8%** saved) and input costs **18.3%** of the uncached price. Longer shared prefixes save more: 97.5% at 8,000 tokens. Now put "Current time: 14:32:07" at the **start** of the prompt: every request has a different first token, nothing matches, and with explicit caching you pay the write premium for nothing (**125%**). Move the timestamp after the system prompt and the savings return.

**Now say why:** the rest of the prompt is identical, so why does one different first token stop every match?

## How it works

### How it works

#### In one breath

Most production prompts start with the same text: a long system prompt, tool definitions, few-shot examples, a shared document, or the conversation so far. Because each token's K and V depend only on the tokens before it, the KV cache of an identical **prefix** can be computed once and **reused**, skipping that part of prefill. Engines do this automatically: vLLM hashes each full KV block together with everything before it, and SGLang keeps prefixes in a radix tree (RadixAttention). API providers expose it as **prompt caching**, billing cached input at a fraction of the normal price (Anthropic: reads at 10% of the base input price, writes at a 25% premium). The catch: only an **exact prefix** matches, so anything that changes per request (a timestamp, user name, shuffled tools) must go **after** the shared part.What you'll be able to do after this: explain how prefix caching works, structure prompts for high hit rates, and estimate the savings.

#### How engines find a reusable prefix

- **Why it works:** in a causal model, the K and V at position t depend only on tokens 1…t. Two requests that share their first n tokens have identical KV for those n positions.

- **vLLM automatic prefix caching:** each full KV block is identified by a hash of its tokens _and_ all tokens before it; a new request reuses every leading block whose hash is already cached. Unused cached blocks are evicted least-recently-used.

- **SGLang RadixAttention:** cached prefixes are stored in a radix tree, so any shared prefix (including branches like many few-shot variants) is found; the SGLang paper reports up to 6.4× higher throughput on workloads with heavy sharing.

- **API prompt caching:** Anthropic uses cache breakpoints. Writes cost 1.25× the base input price for a 5-minute cache, or 2× for an hour, and reads cost 0.1×, or less on its newest models. Its newest models can cache from 512 tokens. OpenAI caches automatically from 1,024 tokens. Its newest models bill writes at 1.25× for a 30-minute default, with discounts of up to 95%. These change often, so check current pricing (checked 7 Nov 2026).

## In practice

### In practice

#### Getting high hit rates in production

- **Order prompts from most to least stable:** tools and system prompt → shared documents / few-shot examples → conversation history → the new message. Keep tool definitions in a fixed order and avoid per-request values early on.

- **Multi-turn chats and agents:** each turn extends the previous prompt, so the whole history hits the cache if it's sent unchanged; editing or summarising early turns breaks the match.

- **Cache-aware routing:** with many replicas, send requests sharing a prefix to the same replica (e.g. consistent hashing on the prefix, or routers in llm-d and NVIDIA Dynamo that track which replica holds which prefixes); random load balancing scatters prefixes and kills hit rates.

- **Measure:** track cache hit rate and cached-token counts (vLLM metrics; API responses report cached tokens), and watch eviction under memory pressure.

#### Identical prefixes have identical KV; compute them once

Prefix caching turns repeated prompt text into a near-free lookup, but only for an exact match from the first token, so the stable parts of a prompt must come first.

### The answer that sounds right

#### "Caching works for any repeated text in the prompt"

It sounds right, since the text is the same. But only an exact prefix from the first token counts, because a chunk's K and V depend on everything before it. It doesn't speed up decode either: it skips prefill work, while decode still reads the whole cache each step. And with round-robin load balancing, each replica computes the same prefix again.

## Say it

### Why are repeated system prompts nearly free, until a timestamp breaks them?

#### The interviewer pushes further

Follow-up 1 of 3

Why can't you reuse a matching chunk in the middle of a prompt?

Its K and V depend on everything before it; with a different preceding context they'd be different. (Research methods approximate this for RAG chunks, at some accuracy cost.)

Follow-up 2 of 3

How does prefix caching interact with load balancing?

Round-robin scatters requests with the same prefix across replicas, each computing it again; route by prefix hash or with a cache-aware router.

Follow-up 3 of 3

Does prefix caching speed up decode?

No, it skips prefill work (TTFT and input cost); decode still reads the whole cache each step.

#### The 30-second answer

In a causal model the keys and values of a token depend only on the tokens before it, so requests that share a prefix share its KV cache. Serving engines exploit this: vLLM hashes each KV block together with its whole prefix and reuses matching blocks, and SGLang stores prefixes in a radix tree. That skips most of prefill for repeated system prompts, documents and conversation history, cutting time to first token and cost; APIs bill cached input at a large discount, for example 10 percent of the normal price on Anthropic. It only works for exact prefixes, so I put stable content first and per-request content last, and with multiple replicas I'd use prefix-aware routing.

**Go further**

#### What not to say

- "Caching works for any repeated text in the prompt." Only an exact prefix from the first token.

- "Caching changes the model's answers." The reused KV is identical to recomputing it (up to floating-point noise).

**Key terms and sources**

Reusing the KV cache of repeated prompt prefixes (system prompts, few-shot examples, documents, earlier conversation turns): how vLLM's automatic prefix caching and SGLang's RadixAttention find matches, how API providers price cached input, how to structure prompts so the cache actually hits, and cache-aware routing across replicas · built from Zheng et al. (SGLang / RadixAttention, NeurIPS 2024), the vLLM automatic prefix caching docs, Anthropic and OpenAI prompt caching documentation, and Gim et al. (Prompt Cache, MLSys 2024) · checked 29 Oct 2026

#### Sources

1. L. Zheng et al., "SGLang: Efficient Execution of Structured Language Model Programs", NeurIPS 2024, arXiv:2312.07104.

2. vLLM documentation, "Automatic Prefix Caching", docs.vllm.ai.

3. Anthropic, "Prompt caching" documentation; OpenAI, "Prompt caching" guide (pricing and minimum lengths vary by model; checked Oct 2026).

4. I. Gim et al., "Prompt Cache: Modular Attention Reuse for Low-Latency Inference", MLSys 2024, arXiv:2311.04934.
