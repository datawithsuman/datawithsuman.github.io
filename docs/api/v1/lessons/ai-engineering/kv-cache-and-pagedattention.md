# KV Cache Management and PagedAttention

> Why did naive serving waste most of its KV memory, and how do blocks fix it?

- Track: AI Engineering › LLM inference and serving › Lessons
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/ai-engineering/kv-cache-and-pagedattention/
- Before this: Prefill vs Decode (`ai-engineering/prefill-vs-decode`)
- Quiz topic: `infer`

## Intuition

### The situation

You serve the 8B assistant on 80 GB GPUs, with about 64 GiB left for the KV cache. A request may stop after 10 tokens or after 2,000, so a colleague reserves the maximum for everyone. Batches stay small and memory looks full. The interviewer asks:

> Why did naive serving waste most of its KV memory, and how do blocks fix it?

**Running example (this track):** the food-delivery app serves its 8B support assistant (Llama 3 8B shape, 128 KiB of KV per token) on 80 GB GPUs, leaving about 64 GiB for the KV cache. Prompts are 200–1,500 tokens; most answers are short, a few are long.

#### Unknown lengths, growing caches

The number of requests that can decode together is limited by KV memory, and decode throughput grows with batch size. But a request's final length is unknown when it starts: it may stop after 10 tokens or after 2,000. Reserve too little and it can't finish; reserve the maximum and memory fills with empty space, so batches stay small.

### The idea

Think of giving every customer a full blank notebook in case they write a lot. Most write one page, and the cupboard fills with empty paper. Instead, keep a shared stack of loose pages, hand one over when needed and keep an index of whose pages are whose. That's how an operating system handles RAM.

[Figure: Requests that fit in 64 gibibytes. Reserving 8k context: 64. Reserving prompt plus 2,048 tokens: 177. 256-token blocks: 376. 16-token blocks: 411.]

_From the lab: 200 simulated requests, at 128 KiB per token._

### Play

**Try to break it.** Switch between the two reservation settings and the two paging settings. Compare the memory holding real tokens with the requests that fit.

#### Reserve memory per request, or page it?

200 simulated requests: prompts 200–1,500 tokens, answer lengths mostly short (mean about 300, capped at 2,048); fixed seed. 128 KiB per token (Llama 3 8B shape, bf16).

Reserving the full **8k context** per request leaves **84.5%** of KV memory empty: only 64 requests fit. Reserving prompt + 2,048 output tokens (a common max-tokens setting) is better, but still only **42.8%** holds real tokens, in line with the 20–38% Kwon et al. measured in real systems. With **16-token pages**, 99.4% of the memory holds tokens and **411** requests fit, 2.3× as many, which is where vLLM's throughput gain comes from. Bigger blocks (256 tokens) waste more in each request's last block (91.0% used, 376 requests) but mean fewer table lookups; small blocks are the usual default.

**Now say why:** 16-token blocks waste so little, so why not make blocks 1 token?

## How it works

### How it works

#### In one breath

Every running request needs its own KV cache, which grows by one token per decode step, and nobody knows in advance how long the answer will be. Early servers reserved one **contiguous** chunk per request for the maximum possible length, so most of it sat empty: Kwon et al. found only **20–38%** of KV memory held real tokens. **PagedAttention** (vLLM) borrows the idea of virtual memory: the cache is split into small fixed-size **blocks** (16 tokens by default), allocated on demand anywhere in GPU memory, and a per-request **block table** maps logical positions to physical blocks; the attention kernel follows that table. Waste drops to the last, partly filled block, so far more requests fit in a batch (vLLM reported 2–4× throughput), and blocks can be **shared** (parallel samples, common prefixes) or **evicted** when memory runs out.What you'll be able to do after this: explain KV-cache fragmentation, how block tables work, and what happens when the cache is full.

#### Blocks and block tables

- **Contiguous allocation** causes three kinds of waste (Kwon et al.): **reserved** slots for future tokens, **internal fragmentation** from over-estimating the length, and **external fragmentation** between differently sized chunks.

- **PagedAttention:** the KV cache is a pool of fixed-size physical blocks. Each request has a block table (logical block 0 → physical block 731, logical block 1 → physical block 12, …). A new block is grabbed only when the current one fills. The attention kernel gathers K and V through the table, so blocks need not be adjacent.

- **Copy-on-write sharing:** parallel samples or beams of the same prompt point to the same prompt blocks and copy only when they diverge; the same mechanism powers prefix caching.

- **When memory runs out:** the scheduler **preempts** some requests, either dropping their blocks and recomputing later or swapping them to CPU memory, and resumes them when blocks free up.

## In practice

### In practice

#### Beyond basic paging

- **Standard everywhere:** vLLM, SGLang, TensorRT-LLM and Hugging Face TGI all use paged KV caches; SGLang organises shared prefixes in a radix tree.

- **KV-cache quantization:** storing K and V in FP8 halves the cache (twice the batch) with small quality cost; see LLM Quantization.

- **Offloading and tiering:** evicted or idle conversations' blocks move to CPU memory or SSD and come back on the next turn (e.g. LMCache with vLLM), useful for long multi-turn chats and agents.

- **Alternatives:** vAttention (Prabhu et al. 2024) keeps the cache virtually contiguous using the GPU's own virtual memory, so unmodified attention kernels work; architecture changes (GQA, MLA, sliding windows) shrink the cache itself.

To shrink, evict or offload the cache itself, read KV Cache Compression, Eviction and Offloading.

#### Allocate KV memory the way an OS allocates RAM

Small fixed-size pages allocated on demand, mapped through a table, remove almost all fragmentation, so the same GPU holds several times more concurrent requests, and pages can be shared, swapped or evicted.

### The answer that sounds right

#### "PagedAttention reduces the KV cache size"

It sounds right, since more requests suddenly fit. But each token still costs the same memory. It reduces the waste around the cache, while GQA, MLA or quantization reduce the cache itself. And outputs don't change either: only where K and V are stored changes. Reserving the maximum length "to be safe" is exactly what limits batch size.

## Say it

### Why did naive serving waste most of its KV memory, and how do blocks fix it?

#### The interviewer pushes further

Follow-up 1 of 3

What happens when a new token needs a block and none are free?

The scheduler preempts lower-priority requests (often the most recent), frees their blocks by swapping to CPU or discarding them for later recomputation, and resumes them once memory is available.

Follow-up 2 of 3

Why not make blocks 1 token, for zero waste?

The block table and gather operations would become large and slow; blocks of 16–32 tokens balance waste against kernel efficiency.

Follow-up 3 of 3

Does PagedAttention change the model's outputs?

No, it only changes where K and V are stored; attention computes the same result.

#### The 30-second answer

Each request's KV cache grows token by token and its final length is unknown, so early servers reserved contiguous memory for the maximum length, and only about 20 to 38 percent held real tokens. PagedAttention, from vLLM, splits the cache into fixed-size blocks, typically 16 tokens, allocated on demand anywhere in memory, with a per-request block table that the attention kernel uses to find them, like virtual memory pages. Waste drops to the last partial block, so batches get much bigger, giving 2 to 4 times throughput; blocks can be shared copy-on-write across samples and prefixes, and when memory runs out the scheduler preempts requests by swapping or recomputing.

**Go further**

#### What not to say

- "PagedAttention reduces the KV cache size." It reduces waste around it; GQA, MLA or quantization reduce the size.

- "Just reserve max length to be safe." That's exactly what limits batch size.

**Key terms and sources**

How serving engines store the KV cache of many concurrent requests: why reserving contiguous memory per request wastes most of it, how PagedAttention splits the cache into fixed-size blocks with a block table (like virtual memory), and what that enables: higher batch sizes, sharing between samples, preemption and offloading · built from Kwon et al. (vLLM / PagedAttention, SOSP 2023), the vLLM documentation, Zheng et al. (SGLang, NeurIPS 2024) and Prabhu et al. (vAttention, 2024) · checked 29 Oct 2026

#### Sources

1. W. Kwon et al., "Efficient Memory Management for Large Language Model Serving with PagedAttention", SOSP 2023, arXiv:2309.06180.

2. vLLM documentation, "Paged Attention" and "Automatic Prefix Caching", docs.vllm.ai.

3. L. Zheng et al., "SGLang: Efficient Execution of Structured Language Model Programs", NeurIPS 2024, arXiv:2312.07104.

4. R. Prabhu et al., "vAttention: Dynamic Memory Management for Serving LLMs without PagedAttention", 2024, arXiv:2405.04437.
