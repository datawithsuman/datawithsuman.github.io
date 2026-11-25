# LLM Serving Incidents

> 9 incidents: out of memory, slow first tokens, cache misses, a bad quantization, noisy neighbours, MoE hot spots, reasoning costs.

- Track: AI Engineering › LLM inference and serving › Scenarios
- Type: Interview · 40 min
- Page: https://aimlrounds.com/tracks/ai-engineering/llm-serving-incidents/
- Before this: Serving Metrics and SLOs (`ai-engineering/serving-metrics-and-slos`), Prefix and Prompt Caching (`ai-engineering/prefix-caching`)
- Quiz topic: `infer`
- Sources checked: 2026-11-10 · Text last changed: 2026-11-19 · Version: 56ab065d0a

How to use this page

Give yourself about 5 minutes per question, as in an interview. Each is a production symptom from a self-hosted LLM service. Say your diagnosis out loud (most likely cause first, how you'd confirm it, then the fix), then open the answer and compare.

**The diagnosis order:** reproduce with the same prompt mix → read the dashboards by phase (queue, prefill, decode) → check memory (weights, KV cache) → check what changed (config, version, traffic) → fix the cause, then add a load test or alert for it.

Question 1 · Easy · memory

### The team raised the model's maximum context from 8k to 32k tokens. The server now runs out of GPU memory under normal load, though the weights haven't changed. What happened?

Answer: **the KV cache needed per request grew about 4×, so far fewer requests fit**

1. KV cache size grows with context length × concurrent requests; weights are a fixed cost, the cache is not.

2. Confirm on the engine's memory metrics: KV cache usage hits its limit or the scheduler preempts requests at peak.

3. Fix: cap concurrent long requests, lower the default max length where users don't need it, quantize the KV cache, or add GPUs; set the memory limit so the cache can't starve other work.

**Follow-up:** Why not just let requests wait in the queue? You can, with admission control, but then latency climbs; decide which traffic deserves 32k and route it to a separate pool.

Question 2 · Easy · latency

### At peak hours, time to first token jumps from 0.5 s to 6 s, but tokens per second during generation stays normal. Where do you look?

Answer: **queueing and prefill contention, not decode**

1. TTFT includes waiting in the queue plus prefill; normal decode speed rules out the generation phase.

2. Check queue length and waiting time per request, and whether a few very long prompts arrived together.

3. Fix: autoscale on queue depth or waiting time, enable chunked prefill so long prompts don't block others, and add admission control with clear limits.

**Follow-up:** Average latency looks fine. Why do users complain? Averages hide the tail; track p95 and p99 TTFT and set the SLO on them.

Question 3 · Medium · caching

### After a product change, the prefix cache hit rate dropped from 70% to almost zero and costs rose. The change added each user's first name to the start of the system prompt. Why does that matter?

Answer: **the cache matches exact token prefixes, so a changing first line breaks reuse for everything after it**

1. Prefix caching only reuses the computed KV cache for an identical leading sequence of tokens.

2. Compare request prefixes before and after: the first tokens now differ per user.

3. Fix: keep the long stable instructions first and move per-user details to the end of the prompt; monitor hit rate as a release check.

**Follow-up:** Where else does this bite? Timestamps, request IDs or shuffled tool lists at the top of prompts all break caching the same way.

Question 4 · Medium · quantization

### To cut cost, the team quantized the model to 4-bit. Chat quality looks the same, but accuracy on maths and code tasks dropped noticeably. What went wrong, and what do you do?

Answer: **quantization error hurts some skills more than others, and the eval only checked chat**

1. Low-bit weights add small errors that some tasks, like multi-step maths and code, are more sensitive to.

2. Run the full task eval, by category, on both versions to find where accuracy dropped.

3. Fix: use a better method with calibration data from your own traffic, keep sensitive layers at higher precision, or use 8-bit for those workloads; gate future changes on the per-task eval.

**Follow-up:** Could you serve two versions? Yes: route maths and code requests to the higher-precision model, and keep 4-bit for the bulk of chat.

Question 5 · Medium · noisy neighbour

### One customer starts sending 100,000-token documents. Everyone else's p99 latency triples, although average load barely changed. Why?

Answer: **head-of-line blocking: huge prefills occupy the GPU and delay other requests**

1. A single very long prefill takes a large share of compute and KV memory for a long time.

2. Confirm by correlating latency spikes with those requests, and by checking batch composition.

3. Fix: chunked prefill, separate pools or priorities for long-context requests, and per-tenant rate and token limits.

**Follow-up:** How do you price this fairly? Charge or rate-limit by tokens, not by requests, since one request can cost as much as thousands of short ones.

Question 6 · Medium · speculative decoding

### Speculative decoding sped up your chat product by 2×, but when you turned it on for a code-review workload, it got slower. Why?

Answer: **the draft model's guesses are rarely accepted on this workload, so the extra work doesn't pay off**

1. Speed-up depends on the acceptance rate; if the big model rejects most drafted tokens, you pay for drafting and verifying with little gain.

2. Measure acceptance rate per workload; higher temperature and unfamiliar content lower it.

3. Fix: turn it off for that workload, use a draft model trained on similar data, or draft fewer tokens per step.

**Follow-up:** Does speculative decoding change the output? No, done correctly the output follows the big model's distribution; only speed changes.

Question 7 · Hard · upgrade

### After upgrading the serving engine to a new version, evaluation scores dropped by two points, though the model weights are identical. What do you check?

Answer: **changed defaults or numerics in the engine, such as sampling parameters, templates or kernels**

1. Diff the effective configuration: sampling defaults (temperature, top-p, repetition penalty), the chat template, stop tokens and max length.

2. Run the eval with fixed seeds and greedy decoding on both versions to separate numerics from sampling.

3. Fix: pin every setting explicitly, treat engine upgrades like model upgrades with a gating eval, and canary before full rollout.

**Follow-up:** Why can results differ even with greedy decoding? Batch size and kernel changes alter floating-point order, which can flip close token choices.

Question 8 · Hard · MoE

### You serve a Mixture-of-Experts model across 8 GPUs with expert parallelism. One GPU is at 100% while others sit at 40%, and throughput is far below plan. What's happening?

Answer: **expert load imbalance: real traffic routes most tokens to a few experts on one GPU**

1. Routing depends on the content; a workload heavy in one domain can overload the GPUs holding its popular experts.

2. Check per-expert token counts and per-GPU utilisation.

3. Fix: replicate the hottest experts, rebalance their placement across GPUs, and size the cluster for real traffic rather than uniform routing.

**Follow-up:** Why not just add GPUs? Without rebalancing, the hot GPU stays the bottleneck and new GPUs sit idle.

Question 9 · Hard · reasoning model

### You switched an assistant to a reasoning model. Answers are better, but cost per request rose 6× and some replies take 40 seconds. What do you do?

Answer: **control hidden thinking tokens: set reasoning effort and budgets, and route easy requests elsewhere**

1. Reasoning models generate many hidden tokens before answering; those are decode tokens you pay for and wait for.

2. Measure thinking tokens per request type; most simple questions don't need long reasoning.

3. Fix: route easy requests to a non-reasoning model, set low reasoning effort or a token budget by default, stream an early acknowledgement, and set timeouts.

**Follow-up:** How do you decide which requests need reasoning? Use a cheap classifier or rules, and check on an eval that quality holds for the requests you route away.

**More practice and sources**

9 interview questions, easy to hard · answers hidden until you click · checked 10 Nov 2026

Keep practising

Uses the lessons in this section: Prefill vs Decode, KV Cache, Continuous Batching, Prefix Caching, Speculative Decoding, Serving Metrics, Serving MoE and Serving Reasoning Models.
