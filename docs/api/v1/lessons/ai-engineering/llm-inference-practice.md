# LLM Inference Practice

> 7 questions: KV maths, speculative speedup, a caching incident, fleet sizing.

- Track: AI Engineering › LLM inference and serving › Scenarios
- Type: Interview · 35 min
- Page: https://aimlrounds.com/tracks/ai-engineering/llm-inference-practice/
- Before this: Sizing and Cost: Cost per Million Tokens (`ai-engineering/sizing-and-cost`)
- Quiz topic: `infer`

How to use this page

Give yourself about 5 minutes per question, as in an interview. Half of these are napkin maths, half are diagnoses. For the scenarios, say the most likely cause first, then how you'd confirm and fix it; then open the answer and compare.

**The toolkit:** decode step ≈ (weights + batch × KV per sequence) ÷ bandwidth; E2E ≈ TTFT + TPOT × (n − 1); speculative speedup = (1 − α^(γ+1)) / ((1 − α)(γc + 1)); $/M tokens = GPUs × $/h ÷ (tokens/s × 3,600) × 10⁶; KV per token = 2 × layers × KV heads × head dim × bytes.

Question 1 · Easy · paged KV

### With 16-token KV blocks, how many blocks does a request with a 700-token prompt and a 300-token answer use, and how many slots are wasted? What would a contiguous reservation of prompt + 2,048 tokens waste?

Answer: **63 blocks (1,008 slots), 8 wasted; the contiguous reservation wastes 1,748 of 2,748 slots (64%)**

1. 1,000 tokens ÷ 16 = 62.5 → 63 blocks = 1,008 slots; only the last block is partly empty (8 slots).

2. Contiguous: 700 + 2,048 = 2,748 slots reserved, 1,000 used, 1,748 wasted.

3. That waste is why PagedAttention fits several times more requests in the same memory.

**Follow-up:** Two samples (n = 2) from the same prompt: how many prompt blocks do they need? Still 44 (the 700-token prompt), shared copy-on-write; only the answers get separate blocks.

Question 2 · Easy · latency maths

### TTFT is 300 ms and TPOT is 25 ms. How long until a 400-token answer finishes? The product team wants answers to feel 'instant'. Which metric do you improve?

Answer: **0.3 + 0.025 × 399 ≈ 10.3 s end to end; for perceived speed, TTFT (and streaming)**

1. E2E ≈ TTFT + TPOT × (n − 1) = 0.3 + 9.975 ≈ 10.3 s.

2. With streaming, users start reading after 300 ms; 25 ms per token (40 tokens/s) is faster than reading speed.

3. 'Instant' usually means TTFT: prefix caching, shorter prompts, less queueing, chunked prefill.

**Follow-up:** When does E2E matter more than TTFT? Non-streamed uses: tool calls, JSON for another service, and agents chaining many calls.

Question 3 · Medium · speculative decoding

### A draft model has acceptance rate α = 0.7 with the target, costs c = 0.1 of a target step, and proposes γ = 3 tokens. What is the expected speedup at small batch? Would you deploy it at batch size 128?

Answer: **≈ 1.95× at small batch; probably not at batch 128 without measuring**

1. Expected tokens per target pass: (1 − 0.7⁴) / (1 − 0.7) = 0.7599 / 0.3 ≈ 2.53.

2. Cost per step: γc + 1 = 0.3 + 1 = 1.3. Speedup ≈ 2.53 / 1.3 ≈ 1.95×.

3. At batch 128 decode is closer to compute-bound, so verifying extra tokens isn't free; gains shrink and can turn negative. Measure, and let the engine disable speculation under high load.

**Follow-up:** How would you raise α? Use a draft from the same family (or an EAGLE head trained on the target's features), lower the temperature, or use prompt-lookup drafts for quoting-heavy tasks.

Question 4 · Medium · throughput maths

### Estimate batch-1 decode speed for an 8B model in bf16 on an H100 (3.35 TB/s). Why does batch 32 give roughly 20× the throughput but not 32×?

Answer: **about 16 GB ÷ 3.35 TB/s ≈ 4.8 ms ideal (≈ 150 tokens/s at 70% efficiency); batch 32 adds 32 KV caches to every step's reads**

1. Each decode step reads all 16 GB of weights: 16 / 3,350 GB/s ≈ 4.8 ms → ~210 tokens/s ideal, ~150 realistic.

2. At batch 32 the weights are read once for all 32 sequences, but each sequence's KV cache (e.g. 2k tokens × 128 KiB ≈ 0.27 GB) is also read: 32 × 0.27 ≈ 8.6 GB extra per step.

3. Step time ≈ (16 + 8.6) GB / bandwidth, so throughput ≈ 32 × (16 / 24.6) ≈ 21× batch 1.

**Follow-up:** What reduces the KV part? GQA/MLA models, FP8 KV cache, shorter contexts, prefix sharing.

Question 5 · Medium · incident

### After a prompt update, p99 TTFT doubled and input token costs rose 3×, although traffic didn't change. TPOT is unchanged. The diff adds 'Today is {date}, user tier: {tier}' as the first line of the system prompt. What happened?

Answer: **the change broke prefix caching: the shared prefix now differs per request**

1. Prefix caching only matches exactly from the first token; a per-request first line makes every prompt unique, so every request recomputes the whole system prompt.

2. That raises prefill work (TTFT) and API input cost (no cached-token discount); decode is unaffected, so TPOT is unchanged.

3. Fix: move the dynamic line after the static system prompt and tools; confirm with the cache hit rate / cached-token metrics.

**Follow-up:** How would you catch this before release? Track prefix-cache hit rate in staging load tests and alert on drops after deploys.

Question 6 · Hard · sizing

### Design the GPU footprint for 2,000 concurrent chats with up to 8k tokens of context on Llama 3 70B (bf16 weights, 320 KiB of bf16 KV per token) using 80 GB GPUs. Then: what single change halves it?

Answer: **≈ 38 replicas × 4 GPUs = 152 GPUs; an FP8 KV cache brings it to ≈ 19 × 4 = 76**

1. Weights 141 GB → a TP-4 replica (4 × 80 GB, ~288 GB usable at 90%), leaving ~147 GB for KV.

2. KV per 8k conversation: 320 KiB × 8,192 ≈ 2.7 GB → ~54 conversations per replica → 2,000 / 54 ≈ 38 replicas → 152 GPUs.

3. FP8 KV halves the cache (≈ 1.34 GB per conversation) → ~109 per replica → 19 replicas → 76 GPUs. FP8 weights alone would not help as much: the KV cache is the bottleneck.

4. Then validate with a load test against TTFT/TPOT SLOs, add headroom (~20–30%), and use prefix-aware routing.

**Follow-up:** Most chats are much shorter than 8k. How does that change the plan? Paged KV only uses what's needed, so size on the real context distribution (e.g. p95) and let the scheduler preempt the rare long ones.

Question 7 · Hard · cost incident

### You raised the maximum context from 8k to 32k for a 'chat with your order history' feature. Cost per million tokens doubled and p99 TPOT got worse, though traffic is the same. Explain and propose fixes.

Answer: **longer contexts multiply KV memory and reads per sequence: smaller batches and slower steps**

1. Each long conversation holds up to 4× the KV cache, so fewer sequences fit per replica (smaller batch) → less weight-read sharing → higher cost per token.

2. Every decode step reads each sequence's whole cache, so long sequences slow steps for everyone in the batch → worse TPOT; long prefills also stall decodes without chunking.

3. Fixes: retrieve only relevant order history (RAG) or summarise old turns instead of sending everything; FP8 KV cache; prefix caching for repeated history; route long-context requests to a separate pool; chunked prefill; consider a GQA/MLA-heavy model.

**Follow-up:** How would you decide between 'long context' and 'retrieve the relevant parts'? Compare answer quality on a labelled set against cost and latency per request; long context is simpler, retrieval is usually far cheaper per query.

Question 8 · Medium · KV compression

### An 8B model has 128 KiB of bf16 KV cache per token, and 64 GiB free. How many 32,768-token conversations fit in bf16, in FP8, and with a 2-bit cache?

Answer: **16, 32 and 128**

1. One conversation: 32,768 × 128 KiB = 4 GiB.

2. bf16: 64 ÷ 4 = 16.

3. FP8 halves it: 32. 2 bits is an eighth: 128.

Which would you ship first? FP8, as it's widely supported and usually safe. Test long-context tasks before going lower.

Question 9 · Medium · MoE reads

### An MoE has 256 experts per layer, and each token uses 8. Roughly what share of experts does a batch of 64 tokens touch, if choices are random?

Answer: **About 87%**

1. One token skips a given expert with probability 1 − 8/256 = 31/32.

2. 64 tokens all skip it with probability (31/32)⁶⁴ ≈ 0.13.

3. So about 87% of experts are touched.

What does that mean for serving? A batch reads most of the model each step, so memory, not active parameters, decides the hardware.

Question 10 · Hard · built-in drafts

### A model's multi-token prediction head drafts one extra token, accepted 85% of the time. Ignoring the head's cost, how many tokens does each target pass produce on average?

Answer: **About 1.85**

1. With γ = 1 and α = 0.85: (1 − α²) ÷ (1 − α).

2. (1 − 0.7225) ÷ 0.15 = 1.85.

3. That's close to the 1.8× DeepSeek-V3 reported.

Why not draft 5 tokens? Later positions are harder to predict, so acceptance falls, and at large batches extra verification isn't free.

**More practice and sources**

10 interview questions, easy to hard · answers hidden until you click · checked 29 Oct 2026

Keep practising

Uses the pages in this track: Prefill vs Decode, Quantization, KV Cache and PagedAttention, Continuous Batching, Prefix Caching, Speculative Decoding, Serving Metrics, Scaling Inference, Sizing and Cost. Formulas from Leviathan et al. (2023) and Kwon et al. (2023).

New lessons: KV Cache Compression, Serving MoE Models and Serving Agents and Reasoning Models.
