# Prefill vs Decode

> Why does an LLM read your prompt fast but write its answer slowly?

- Track: AI Engineering › LLM inference and serving › Lessons
- Type: Concept · 30 min
- Page: https://aimlrounds.com/tracks/ai-engineering/prefill-vs-decode/
- Before this: Attention Variants: MQA, GQA and MLA (`fundamentals/attention-variants-mqa-gqa-mla`)
- Quiz topic: `infer`

## Intuition

### The situation

One user sends a 2,000-token document and asks for a 300-token summary. The first word comes quickly, and then the rest crawls. A colleague says to buy a faster GPU. The interviewer asks:

> Why does an LLM read your prompt fast but write its answer slowly?

**Running example, used on every chapter:** one user sends a 2,000-token document and asks for a 300-token summary. The model is Llama 3.1 8B in 16-bit on one H100 (989 TFLOP/s dense BF16, 3.35 TB/s memory bandwidth, 80 GB). All times are ideal ceilings from those specs: real engines reach less, but the shape holds.

#### The first word comes fast. The rest crawls.

Ask a chatbot to summarise a long document and you see the same pattern every time: a short wait, then the answer streams out word by word. That isn't the UI being dramatic. It is the model doing two completely different kinds of work, and the second kind takes almost all the time.

1. Prefill takes the whole 2,000-token prompt through the model in a single forward pass. Drawn to scale, it's this thin sliver: about 34 ms.

2. That pass also produces the first answer token. The time until it shows up is the **time to first token** (TTFT).

3. Every later token needs its own full pass through the model, because token 2 depends on token 1. 300 tokens means 300 passes at about 4.8 ms each.

4. So for this request, decode is about 1.44 s of the 1.47 s total. And as you'll see, during that time the GPU's maths units sit almost idle.

The same pattern shows up in measurements, not just my arithmetic. Profiling Llama-2-7B on an RTX 4090, the AWQ authors found that reading a 200-token prompt took **10 ms** while generating 20 tokens took **310 ms** AWQ, Fig. 3, p. 5.

So "how fast is this LLM?" has two answers. The services that run LLMs track them separately:

##### TTFT · time to first token

How long until the first word. Set by prefill, grows with prompt length. Matters most for chat, voice and code completion.

##### TPOT / ITL · time per output token

The gap between streamed tokens (also called TBT, time between tokens). Set by decode. 10 ms per token = 100 tokens per second for that user.

DistServe, p. 1–2 · Splitwise, Table II, p. 2

### The idea

Think of a chef who works at incredible speed, with ingredients arriving down one narrow corridor. For prefill, one delivery feeds thousands of portions, so the chef is the limit. For decode, a whole delivery comes in for a single portion, so the corridor is the limit.

[Figure: Prefill: one read of the weights feeds 2,000 tokens, about 2,000 FLOPs per byte, so it is compute-bound. Decode: one read feeds one token, about 1 FLOP per byte, so it is memory-bound. An H100's balance point is about 295 FLOPs per byte.]

_Rough figures from the lesson, for Llama 3.1 8B on one H100 serving one user._

### Play

**Try to break it.** Switch between 16, 8 and 4 bits. Watch the ideal time per token, and how busy the tensor cores are.

#### Decode time ≈ bytes to read ÷ bandwidth

For one user, a decode step does 2 FLOPs per weight but has to read 2 bytes per weight. The tensor cores finish their 16 GFLOPs in 0.016 ms, then wait 4.8 ms for the bytes. So the speed limit is set by bytes, and anything that shrinks them speeds decode up directly.

$$ t_{\text{step}} \approx \big(bP + B\,n_{\text{ctx}}\,\text{KV}_{\text{tok}}\big)\,\big/\,\text{BW} \;\Rightarrow\; 16.1\ \text{GB} / 3.35\ \text{TB/s} \approx 4.8\ \text{ms} $$

Memory-bound estimate (my derivation, standard in the inference literature) · hover any symbol.

- **one decode step**: Time to produce one more token for every user in the batch.

- **the weights**: P × b bytes. Read once per step, no matter how many users share the step. 16.1 GB here.

- **everyone's KV cache**: Each of the B users has a cache of n_ctx tokens × 128 KiB. Unlike the weights, it is not shared: every user adds their own bytes.

- **bandwidth**: 3.35 TB/s on an H100. Decode speed is tied to this number, not to FLOPs.

- **one user, short chat**: B = 1 and a small cache: about 16.1 GB ÷ 3.35 TB/s = 4.8 ms per token, or about 209 tokens per second at best.

##### Try it: shrink the bytes

Weights only, batch of 1, Llama 3.1 8B on an H100. Halving the bytes halves the ideal time. In practice one precision step down (16 → 8 bits) is typically 30–50% faster, not 2×, because of kernels, the KV cache and other overheads (Inference Engineering, P. Kiely, ch. 5.1). AWQ's 4-bit TinyChat kernels measured about 3.2–3.3× over Hugging Face FP16 AWQ, p. 2.

##### What breaks: the KV cache keeps growing

Every generated token adds 128 KiB to every user's cache, and decode re-reads the whole cache each step. Splitwise: "each active generated token that is being processed accesses the KV cache of its entire context so far", which makes the token phase "limited by memory capacity" Insight V, p. 5. Long contexts slow decode even when the weights are tiny. That's why GQA, KV-cache quantization and paged cache memory exist.

**Now say why:** the tensor cores are almost idle, so what is decode actually waiting for?

## How it works

### How it works

#### In one breath

Every LLM request runs in two phases. **Prefill** reads the whole prompt in one pass and is limited by the GPU's maths. **Decode** writes the answer one token per pass and is limited by how fast memory can feed the weights. Almost every inference trick (batching, quantization, chunked prefill, disaggregation) is a fix for one phase or for the two getting in each other's way.What you'll be able to do after this: estimate TTFT and tokens per second on a napkin, explain why decode is memory-bound, and pick the right fix when an LLM feels slow.

#### A GPU is a fast calculator behind a narrow pipe

You need three ideas: where the weights live, the KV cache, and the ratio between maths speed and memory speed. Think of a chef (the maths units) working at an incredible pace, while ingredients (the weights) arrive from a storeroom down a single corridor.

1. The weights live in the GPU's high-bandwidth memory (HBM). Llama 3.1 8B in 16-bit is 8.03 billion numbers × 2 bytes ≈ 16.1 GB.

2. The maths units can't compute on HBM directly. For every forward pass, all 16.1 GB has to stream through a 3.35 TB/s pipe. That alone takes 16.1 ÷ 3.35 ≈ 4.8 ms.

3. The tensor cores do roughly 2 FLOPs per weight for each token they process: a multiply and an add.

4. Divide the two speeds: the H100 can do about 295 FLOPs in the time one byte arrives. This ratio is the GPU's **ridge point**. Work that does fewer FLOPs per byte is **memory-bound**. Work that does more is **compute-bound**.

5. Next to the weights sits the **KV cache**: for every token seen so far, each layer's key and value vectors, saved so they are never recomputed. Decode reads it every step, and it grows by one entry per token.

The KV cache is why the model doesn't redo the whole prompt for every new token. Attention needs every past token's key and value, so prefill computes them once and stores them. Its size per token comes from the model's shape:

$$ \text{KV}_{\text{tok}} = 2\cdotL\cdotH_{kv}\cdotd_h\cdotb = 131{,}072\ \text{bytes} $$

Standard formula; model shape from the Llama 3.1 8B config (32 layers, 8 KV heads, head size 128, bfloat16) · hover any symbol for its meaning.

- **bytes per token**: How much KV cache one token adds, across the whole model.

- **K and V**: One key vector and one value vector per head. That is the 2.

- **layers**: Every layer has its own attention, so its own cache. Llama 3.1 8B has 32 layers.

- **KV heads**: Number of key/value heads. Llama 3.1 8B uses grouped-query attention: 32 query heads share 8 KV heads, which makes the cache 4× smaller.

- **head size**: Numbers per head vector: 128 for this model.

- **bytes each**: 2 in 16-bit. Quantizing the cache to 8-bit halves everything.

- **the answer**: 2 × 32 × 8 × 128 × 2 = 131,072 bytes = 128 KiB per token. Our 2,300-token conversation holds about 0.30 GB of KV cache.

**Go deeper: why 2 FLOPs per parameter per token**

A linear layer computes y = Wx. Each weight wij is used once per token: multiply it by xj, add it to yi. That is 2 FLOPs. Linear layers hold almost all of a transformer's parameters, so a forward pass costs about 2·P FLOPs per token, plus attention, which costs about 2·L·d·n per token at context length n (small until the context gets long). This is the standard estimate used in the inference literature; the attention term is why very long prompts make prefill grow faster than linearly DistServe, p. 13.

#### Both phases read the same weights. Only prefill gets to reuse them.

Every forward pass streams all the weights from memory once. What changes is how many tokens share that one read. Prefill pushes thousands of prompt tokens through together, so each weight byte gets used thousands of times. Decode pushes one token per user, so each byte is used once (per user) and thrown away. The number that captures this is arithmetic intensity: FLOPs done per byte read.

$$ I = 2PN\,\big/\,bP = 2N/b \qquad I_{\text{prefill}}\approx 2000 \quad I_{\text{decode}}\approx 1 $$

Weights-only roofline estimate (my derivation from the standard 2·P FLOPs rule). AWQ's profile of Llama-2-7B reports the same picture: intensity ≈ 1 for 16-bit decode and ≥ 165 for the prompt stage AWQ, Fig. 3b, p. 5.

- **intensity**: FLOPs per byte moved from memory. Compare it with the GPU ridge point (295 on an H100) to know which limit you hit.

- **maths done**: About 2 FLOPs per parameter for each of the N tokens in the pass.

- **bytes read**: The weights, read once per pass: P parameters × b bytes each (2 in 16-bit). KV cache reads are ignored here; they only make decode worse.

- **it is just tokens per pass**: P cancels: intensity is about 2N ÷ b. In 16-bit that is simply N, the number of tokens sharing the read.

- **prefill: N = 2,000**: Our 2,000-token prompt gives about 2,000 FLOPs per byte, well above 295. Compute-bound: the maths units are the limit.

- **decode: N = 1**: One user decoding gives 1 FLOP per byte, about 300× below the ridge. Memory-bound: the maths units are idle 99.7% of the time.

Everything below follows from this one line. Prefill is fixed by doing maths faster or doing less of it. Decode is fixed by moving fewer bytes or by making more tokens share each byte. And when you mix them on one GPU, they fight.

#### Prefill time ≈ maths needed ÷ maths speed

Once the prompt is a few hundred tokens long, the weights stream in faster than the tensor cores can use them, so the clock is set by FLOPs. Drag the prompt length and watch where the limit switches.

Ideal H100 ceiling for Llama 3.1 8B (P = 8.03 B, L = 32, d = 4,096). Below about 300 tokens, prefill is actually memory-bound too. Above it, every extra token costs maths, and at very long prompts the n² attention term takes a growing share.

The papers see the same switch point on real hardware. DistServe found a single 512-token prompt "can fully engage an A100" for a 13B model p. 4. Sarathi-Serve notes the theory says about 200 tokens on an A100 (whose ridge is lower, about 153), but in practice it happens at about 500–600 tokens because of fixed overheads p. 6, footnote 2.

##### What breaks: batching prefills doesn't help

Once one prompt saturates compute, adding a second prompt to the same pass just doubles the time. DistServe: "adding more requests to the batch no longer improves GPU efficiency. Instead, it proportionally extends the total processing time" p. 4. That's why prefill fixes are about doing less maths (prefix caching, shorter prompts) or faster maths (FP8 tensor cores, more GPUs via tensor parallelism), not bigger batches.

#### Serve many users in one step

If one read of the weights feeds 64 users instead of 1, the expensive part of the step is paid once and split 64 ways. This is why **continuous batching** (Orca's iteration-level scheduling, used by vLLM and every modern engine) is the single biggest throughput win in serving. But each user brings their own KV cache, and that part is never shared. Play with both dials.

–

Ideal H100 model, Llama 3.1 8B in 16-bit: step = max(compute, (weights + all KV) ÷ 3.35 TB/s). The purple bar is the share of each step spent reading KV cache. 80 GB − 16.1 GB of weights leaves about 64 GB for caches (ignoring activations and allocator overhead).

Three things to notice. Up to a point, total throughput climbs almost linearly while each user's speed barely drops: the step time is still "read the weights". Sarathi-Serve measured exactly this flat region: LLaMA2-70B's linear layers take about the same time for 128 to 512 tokens per batch Fig. 6, p. 6. With long contexts, the KV cache reads take over and per-user speed falls. And the batch often runs out of _memory capacity_ for caches long before it reaches the compute ridge.

##### Why "295" is only a rule of thumb

Weights-only, a 16-bit decode batch reaches the ridge at about 295 users. But each user also reads their own cache: at 2,300 tokens that is about 0.3 GB per user per step against 16.1 GB of shared weights. Per user, the cache adds bytes without adding much maths, so intensity never reaches the ridge, and the step stays memory-bound however big the batch. Real engines hit KV memory limits first, which is why PagedAttention (removing cache fragmentation so more requests run at once) mattered so much: with iteration-level batching it reached an order of magnitude more throughput than FasterTransformer Sarathi-Serve, p. 3 and 7.

#### Chunked prefill: hide prompt work in decode's idle maths

Decode steps leave the tensor cores mostly idle. Sarathi-Serve's insight: fill that idle compute with a slice of someone's prompt. Each step gets a token budget. First every running decode gets its one token, then the leftover budget goes to a chunk of a waiting prompt. Steps stay roughly the same size, so streaming users never see a multi-second freeze §4.2, Algorithm 3, p. 8–9.

1. Each iteration has a fixed budget of tokens, chosen so one step stays under the latency target. Here, 512.

2. Running decodes go in first: 32 users, one token each. They never wait.

3. The rest of the budget goes to a chunk of the waiting prompt: 480 tokens of a new 8,000-token document.

4. The prompt finishes over about 17 steps instead of one huge one.

5. No step is ever "one giant prefill", so nobody's stream freezes. The decode tokens ride along on maths that was idle anyway.

##### Try it: pick the token budget

Illustrative ideal model: 32 users decoding with 1,500-token contexts, one new 8,000-token prompt, Llama 3.1 8B on an H100. A step = max(compute, memory). Normal decode gap with no prompt waiting: about 6.7 ms.

Smaller budgets mean smoother streams, but chunking isn't free, and the ideal model above hides the costs:

##### What breaks with chunks that are too small

- Each chunk's attention re-reads the KV cache of all earlier chunks: N chunks means O(N²) cache loads instead of O(N) DistServe, p. 4. Sarathi-Serve found attention prefill stays compute-bound even with small chunks, but fixed overheads like kernel launches add up p. 9.

- Tile quantization: GPUs compute in tiles, so a chunk of 257 tokens can make prefill 32% slower than a chunk of 256 Sarathi-Serve, p. 9.

- DistServe's critique: chunking "trades TTFT for TPOT and cannot eliminate the interference" p. 3.

##### What it buys

Naively mixing a full prefill into a decode batch raised time-between-tokens by up to **28.3×** over a decode-only batch, while chunking kept it tightly bounded p. 8. Sarathi-Serve reports 2.6× higher serving capacity for Mistral-7B on one A100 and up to 3.7× for Yi-34B on two A100s, versus vLLM at the time abstract. vLLM V1 now turns chunked prefill on by default and schedules decodes first; a smaller `max_num_batched_tokens` (e.g. 2,048) gives better inter-token latency, a larger one better TTFT vLLM docs.

#### Disaggregation: give each phase its own GPUs

If the two phases want opposite things, stop sharing. A prefill pool runs prompts and produces the KV cache. It sends the cache to a decode pool, which streams the answer. Each pool gets its own GPU count, batch policy and parallelism, tuned for TTFT or for TPOT DistServe, p. 4.

1. A router assigns each request a prefill machine and a decode machine (Splitwise uses join-the-shortest-queue) p. 6.

2. The prefill pool only ever runs prompts. It can use more tensor parallelism to cut TTFT without slowing anyone's stream.

3. The KV cache is copied to the decode machine. Splitwise sends it layer by layer while the prompt is still computing, to hide the transfer p. 7.

4. The decode pool only ever decodes, so it can pack huge continuous batches and never stalls for a prompt.

5. Each pool scales on its own. DistServe searches for the best GPU split and parallelism per phase given the TTFT and TPOT targets p. 10.

##### Worked example: DistServe's opening experiment

A 13B model on A100s, 512-token prompts, 64-token answers, with SLOs on both TTFT and TPOT. The metric is goodput: the highest request rate per GPU at which 90% of requests meet both SLOs p. 2.

##### Requests per second per GPU within SLO (↑ better)

both phases on one GPU

1.6

a GPU doing prefill only

5.6

a GPU doing decode only

10

2 prefill + 1 decode GPU

3.3

Two prefill GPUs (2 × 5.6 = 11.2) can feed one decode GPU (10 rps), so 3 GPUs serve 10 rps: 3.3 per GPU, 2.1× the colocated 1.6 DistServe, Fig. 1, p. 2.

##### What it costs

- A KV cache copy per request. With prefill and decode on the same node, DistServe measured transmission at under 0.1% of total latency for OPT-175B, and 95% of transfers under 30 ms, using intra-node NVLink p. 11. Across slower links it matters more.

- Small setups lose. With one or a few GPUs there is little to rebalance, and DistServe says a non-disaggregated system can be the better choice p. 13. The Modular inference handbook reports 20–30% slowdowns on small or mistuned setups, and notes short or already-cached prompts are often faster prefilled locally.

- It is a latency tool, not a raw throughput tool. vLLM's docs say plainly: disaggregated prefill "DOES NOT improve throughput"; it lets you tune TTFT and tail ITL separately vLLM docs.

## In practice

### In practice

#### Four ways to schedule the two phases, each with a cost

A real server has many users at once: some mid-answer (decoding), some just arrived (needing prefill). How a server interleaves them decides whether you get high throughput, smooth streaming, or both. Here are the four families, following Sarathi-Serve's taxonomy Sarathi-Serve, p. 2.

1. **Request-level batching** finishes a whole batch before starting new prompts. Streams stay smooth, but the batch shrinks as requests finish and newcomers queue, so throughput is poor p. 2.

2. **Iteration-level batching** (Orca) lets requests join and leave every step, and prefill-first schedulers run new prompts as soon as memory allows. Throughput jumps, but while a long prefill runs, every streaming user freezes. Sarathi-Serve calls this a **generation stall**, and measured stalls lasting several seconds in vLLM Fig. 1, p. 1.

3. **Chunked prefill with stall-free batching** cuts each prompt into chunks and builds every step from all running decodes plus one chunk, up to a fixed token budget. Decodes never wait for a whole prefill §4.2, p. 8.

4. **Disaggregation** runs prefill and decode on separate GPUs and ships the KV cache between them. No interference at all, and each pool can be sized and parallelised for its own job, at the price of more machines and a transfer DistServe, p. 4.

The How it works tab takes the last two apart, starting with the one principle that explains all four.

#### Which fix helps which phase

Put the two phases side by side and every common optimisation falls into place.

| Technique | Helps | Why it works |
|---|---|---|
| Continuous batching | Decode | One weight read feeds many users' tokens |
| Weight quantization (8/4-bit) | Decode | Fewer bytes to read per token |
| KV cache, GQA, KV quantization, PagedAttention | Decode | Never recompute the past; shrink and pack the cache so bigger batches fit |
| Speculative decoding | Decode | A small draft model proposes several tokens; the big model checks them in one pass, raising tokens per weight read |
| FlashAttention | Prefill | Faster, memory-efficient attention for long prompts |
| Prefix caching | Prefill | Skip recomputing a shared prefix (system prompt, documents) |
| FP8 / INT8 compute (W8A8) | Prefill | Low-precision tensor cores do more maths per second |
| Tensor parallelism | Prefill (mostly) | Splits the maths across GPUs, cutting TTFT; costs communication |
| Chunked prefill | Both | Hides prompt work in decode's idle compute, no stalls |
| Disaggregation | Both | Separates them entirely; each pool tuned for its own metric |

And one formula ties the user's experience together. A request's total latency is TTFT plus TPOT for every token after the first DistServe, footnote 1, p. 2:

$$ T_{\text{request}} = \text{TTFT} + \text{TPOT}\cdot(n_{\text{out}}-1) \approx 1.47\ \text{s} $$

- **what the user waits**: End-to-end latency for the full answer.

- **prefill**: Time to first token: queueing plus the prefill pass. About 34 ms ideal in our example.

- **decode, per token**: Time per output token. About 4.8 ms ideal for one user; more under a big batch or long context.

- **how many more tokens**: The answer length after the first token. 299 in our example, which is why decode dominates.

- **our request**: 34 ms + 4.8 ms × 299 ≈ 1.47 s. Halve TPOT and you save 0.7 s; halve TTFT and you save 17 ms.

#### How much do the fixes buy?

##### Serving capacity vs vLLM under latency SLOs (↑ better, × the baseline)

Sarathi-Serve · Mistral-7B, 1 A100

2.6×

Sarathi-Serve · Yi-34B, 2 A100s

3.7×

Sarathi-Serve · Falcon-180B, pipeline

5.6×

DistServe · OPT-66B code completion

5.7×

DistServe · OPT-66B summarization

4.3×

DistServe · OPT chatbot (13B–175B)

2.0–4.6×

Sarathi-Serve: capacity under P99 time-between-tokens SLOs abstract. DistServe: per-GPU request rate with 90% of requests meeting both TTFT and TPOT SLOs p. 10–11. Splitwise (cluster-level, simulated on production traces): 1.4× throughput at 20% lower cost, or 2.35× throughput at the same cost and power abstract.

##### Read these numbers fairly

- The baseline is 2023–24 vLLM, which then used prefill-first scheduling. Today's vLLM has chunked prefill on by default, so the gap against a current baseline is smaller.

- They measure capacity _under latency targets_, not raw tokens per second. With loose SLOs the gains shrink: Sarathi-Serve reports 3.5× under a strict 100 ms SLO (Mistral-7B) but 1.65× under a relaxed 1 s SLO (Yi-34B) p. 12.

- The two papers each compare against a system without the other's idea, so the bars aren't a head-to-head. DistServe's own comparison with DeepSpeed-MII (which does chunked prefill) shows 1.6–7.4× on the chatbot workload p. 10.

##### Update · my check (28 Oct 2026)

Disaggregation moved from paper to default. NVIDIA says production platforms such as NVIDIA Dynamo use concepts that came from DistServe's lab (NVIDIA blog), and coverage of the authors' 2025 retrospective lists NVIDIA, llm-d, vLLM and Mooncake among adopters (secondary source, 36Kr). On Blackwell B200s, each GPU has about 180 GB and 8 TB/s, from NVIDIA's 8-GPU system figures, so the same arithmetic gives roughly 2.4× faster decode than an H100. Checked again on 7 Nov 2026: vLLM still labels its disaggregated prefill "experimental", and chunked prefill is on by default in vLLM V1 (vLLM docs).

#### Your LLM feels slow. Diagnose it.

1. **Measure TTFT and TPOT separately**, at P50 and P90/P99. One blended "latency" number hides which phase is the problem.

2. **High TTFT?** Look at prefill: long prompts, no prefix caching, prompts queued behind other work. Try prefix caching, chunked prefill, shorter prompts, or more tensor parallelism.

3. **High TPOT?** Look at decode: big model, long contexts, oversized batches. Try weight and KV quantization, speculative decoding, or a smaller model.

4. **Spiky TPOT** (fine on average, bad at P99)? Prefills are stalling decodes. Turn on chunked prefill and lower the token budget; at scale with strict SLOs, consider disaggregation.

5. **Low throughput while the GPU looks "busy"?** Probably memory-bound decode at small batch sizes. Batch more users (continuous batching) and free KV memory so the batch can grow.

#### What to keep, and where the simple story bends

**The lesson:** prefill reuses each weight read across thousands of tokens and is compute-bound; decode uses each read for one token per user and is memory-bound. Measure TTFT and TPOT separately, and pick fixes by phase.

##### Where it bends

- **The numbers here are ideal ceilings.** Real kernels reach maybe 60–80% of peak bandwidth or FLOPs, and there's scheduling and framework overhead. Use them for napkin estimates and for direction, not for SLAs.

- **Long contexts change decode.** At long contexts, KV cache reads, not weights, dominate each decode step (see the batching section). GQA, KV quantization and attention kernels matter more than weight quantization there.

- **Mixture-of-experts models** read only the active experts per token, which lowers bytes per token at batch 1. But at big batches, different users hit different experts, so more of the model gets read each step.

- **Short prompts are not compute-bound.** Below about 300 tokens on an H100, even prefill is limited by reading the weights (see the prefill section).

- **Disaggregation and chunking aren't rivals.** DistServe notes that when throughput matters more than strict latency, chunked prefill's fuller batches can be preferable p. 13; at long contexts the KV transfer grows linearly while prefill maths grows faster, which keeps disaggregation attractive p. 13.

### The answer that sounds right

#### "Just buy a faster GPU" speeds up the wrong phase

The obvious move when generation is slow: get the newer chip with far more FLOPs. Splitwise (Microsoft) measured exactly this on production traces. Going from an A100 to an H100 buys **3.43× more compute** but only **1.64× more memory bandwidth** Splitwise, Table I, p. 1. Look at what each phase got:

##### Llama-70B, coding traces, P50 latency · H100 time as a fraction of A100 time (lower = faster)

TTFT (prefill)

0.51×

TBT (decode)

0.70×

Prefill got about 2× faster. Decode got only about 1.4× faster, close to the bandwidth gain, nowhere near the compute gain. The conversation trace shows the same split (0.54× vs 0.70×) Splitwise, Table IV, p. 5.

##### What breaks: you pay for maths decode can't use

Splitwise also capped H100 power from 700 W to 350 W per GPU. Prefill latency rose sharply, while decode latency barely moved Fig. 9, p. 5. Their conclusion: token generation "does not need the compute capability of the latest GPUs and can be run with lower power and cost" abstract. Decode is waiting on memory, so more FLOPs mostly sit idle.

## Say it

### Why does an LLM read your prompt fast but write its answer slowly?

#### The interviewer pushes further

Follow-up 1 of 6

Why does batching raise throughput but not per-user speed?

In the memory-bound region a step takes about as long as reading the weights, whether it serves 1 user or 64. So total tokens per second grows almost linearly with batch size while each user's speed stays roughly flat. It stops when the KV caches fill memory or, with short contexts, when you reach the compute ridge. With long contexts, per-user speed does fall, because each user adds their own cache reads.

Follow-up 2 of 6

Estimate the max tokens per second for a model on one GPU.

For one user: bandwidth ÷ bytes of weights. Llama 3.1 8B in 16-bit is 16.1 GB; an H100 moves 3.35 TB/s, so about 209 tokens/s at best. In 4-bit it's about 4 GB, so roughly 830 tokens/s in theory, less in practice. Then add the KV cache term for long contexts and discount for real-world efficiency.

Follow-up 3 of 6

Does quantization speed up prefill?

Weight-only quantization (W4A16) mostly doesn't: prefill is compute-bound and the maths still runs in 16-bit after dequantizing. To speed up prefill you need low-precision compute, i.e. quantized activations too (W8A8 with SmoothQuant, or FP8).

Follow-up 4 of 6

Chunked prefill or disaggregation?

Chunked prefill first: it's a scheduler setting, works on one GPU, and removes stalls. Disaggregation pays off at scale with long prompts and strict TTFT and TPOT targets, where you can size the pools separately and have fast interconnects for the KV transfer. On small or mistuned setups it can be slower, and it doesn't raise raw throughput.

Follow-up 5 of 6

What does the KV cache cost, and how do you shrink it?

2 × layers × KV heads × head size × bytes per token: 128 KiB per token for Llama 3.1 8B, so 0.26 GB for a 2,000-token prompt, per user. Shrink it with GQA or MQA (fewer KV heads), KV quantization (8 or 4 bits), paging to avoid fragmentation (PagedAttention), and eviction or windowing for very long contexts.

Follow-up 6 of 6

Why would someone put decode on older GPUs?

Decode doesn't use the compute, so the newest GPU's extra FLOPs are mostly wasted there. Splitwise found A100s could match or beat H100s on cost and energy for token generation and proposed H100 prefill with A100 decode (Splitwise-HA) p. 5.

#### The 30-second answer

LLM inference has two phases. Prefill processes the whole prompt in one forward pass, so each weight read is reused across thousands of tokens and it's compute-bound; it sets time to first token. Decode generates one token per pass, so each pass reads all the weights and the KV cache for very little maths; it's memory-bandwidth-bound and sets time per output token. That's why batching and quantization help decode, why faster FLOPs help prefill, and why mixing the two on one GPU needs chunked prefill or disaggregation.

**Go further**

#### The 2-minute walkthrough

Start with the symptom: the first word is fast, the rest streams. Explain prefill vs decode and the KV cache that links them. Then the roofline: an H100 does about 295 FLOPs per byte of bandwidth; prefill of a 2,000-token prompt does about 2,000 FLOPs per byte, decode for one user about 1. Napkin numbers for an 8B model in 16-bit: 16 GB of weights ÷ 3.35 TB/s ≈ 4.8 ms per token, about 200 tokens/s per user at best. Fixes by phase: batching and quantization for decode; prefix caching and FP8 for prefill. Then the collision: prefill-first scheduling causes generation stalls; chunked prefill (Sarathi-Serve, on by default in vLLM V1) packs decodes plus a prompt chunk into each step; disaggregation (Splitwise, DistServe) splits the phases across GPU pools for goodput under SLOs. Close with the limit: the KV cache grows with context and batch, so at long contexts it, not the weights, dominates decode.

#### What not to say

- "Decode is slow because attention is quadratic." For a single new token, attention is linear in context; the problem is reading weights and cache.

- "Bigger batches make each user faster." They raise total throughput; per-user speed stays flat or drops.

- "Disaggregation increases throughput." It improves goodput under latency SLOs; vLLM's docs say it does not improve raw throughput.

- "An H100 is 3× faster for LLMs than an A100." For decode, the gain tracks bandwidth (about 1.6×), not FLOPs.

**Key terms and sources**

Built from Splitwise, DistServe, Sarathi-Serve, AWQ, the vLLM docs and NVIDIA's H100 specs · checked 28 Oct 2026 · updated 29 Oct 2026

#### Glossary

| **Prefill** | The pass that processes the whole prompt in parallel, builds the KV cache and produces the first token. |
|---|---|
| **Decode** | Generating the answer one token per forward pass, reading the KV cache. |
| **TTFT** | Time to first token: queueing + prefill. |
| **TPOT / ITL / TBT** | Time per output token, inter-token latency, time between tokens: the streaming gap. |
| **KV cache** | Saved keys and values for every past token in every layer, so attention never recomputes them. |
| **Arithmetic intensity** | FLOPs done per byte read from memory. |
| **Ridge point** | Peak FLOPs ÷ peak bandwidth (≈ 295 on an H100). Below it you're memory-bound; above it, compute-bound. |
| **Continuous batching** | Requests join and leave the running batch every iteration (Orca's iteration-level scheduling). |
| **Generation stall** | Streaming users freezing while a long prefill runs on the same GPU. |
| **Chunked prefill** | Splitting a prompt into chunks that share each step with running decodes, under a token budget. |
| **Disaggregation** | Prefill and decode on separate GPU pools, with the KV cache transferred between them. |
| **Goodput** | Requests per second (per GPU) served while meeting the latency SLOs. |

#### Each fix has its own lesson

- KV Cache Management and PagedAttention: how the cache for many users is stored without waste.

- Continuous Batching and Scheduling: the scheduler behind "batching decode", step by step.

- Prefix and Prompt Caching: skipping prefill for repeated prompts.

- Speculative Decoding: several tokens per memory-bound decode step.

- Serving Metrics and SLOs: TTFT, TPOT and goodput under real load.

- Scaling Inference and Sizing and Cost: disaggregation at cluster scale, GPU counts and cost per token.

#### What this page is built from

1. Patel et al., Splitwise: Efficient Generative LLM Inference Using Phase Splitting, Microsoft / UW, ISCA 2024.

2. Zhong et al., DistServe: Disaggregating Prefill and Decoding for Goodput-optimized LLM Serving, PKU / UCSD, OSDI 2024.

3. Agrawal et al., Taming Throughput-Latency Tradeoff in LLM Inference with Sarathi-Serve, Microsoft Research India / Georgia Tech, OSDI 2024.

4. Lin et al., AWQ: Activation-aware Weight Quantization, MIT, MLSys 2024 (Fig. 3 bottleneck profile).

5. vLLM docs: Optimization and tuning (chunked prefill) and Disaggregated prefilling.

6. NVIDIA, H100 specifications (989 TFLOP/s dense BF16, 3.35 TB/s, SXM).

7. Meta, Llama 3.1 8B config (layers, KV heads, head size).

8. P. Kiely, _Inference Engineering_ (Baseten), ch. 1.4, 2.2, 2.4, 5.1: latency metrics, ops:byte, precision speedups.

9. Modular, LLM inference handbook: prefill-decode disaggregation (small-setup slowdowns, local prefill for short prompts).

10. NVIDIA blog, UC San Diego lab and DistServe's influence on Dynamo; 36Kr coverage of the 2025 disaggregation retrospective (secondary).

11. Interview angle: techinterview.org, GPTQ, AWQ and FP8 in the LLM inference interview.

Napkin numbers (4.8 ms, 34 ms, 209 tokens/s, 295 FLOPs/byte, 128 KiB per token) are my arithmetic from the specs above and are ideal ceilings.
