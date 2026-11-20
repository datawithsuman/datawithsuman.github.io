# Attention Variants: MQA, GQA and MLA

> How many conversations fit on one GPU, and how do GQA and MLA raise that?

- Track: Fundamentals › LLMs › Modern architecture
- Type: Concept · 25 min
- Page: https://aimlrounds.com/tracks/fundamentals/attention-variants-mqa-gqa-mla/
- Before this: Anatomy of a Modern LLM (`fundamentals/modern-llm-architecture`), Multi-Head Attention (`fundamentals/multi-head-attention`)
- Quiz topic: `arch`

## Intuition

### The situation

Your 8B assistant runs on one 80 GB GPU, and its weights take about 16 GB. Customers chat with 8k tokens of history each. A colleague assumes the weights decide how many fit at once. The interviewer asks:

> How many conversations fit on one GPU, and how do GQA and MLA raise that?

Where this lesson sits: the attention box, specifically how many K and V heads it keeps.

Background: Self-Attention · Multi-Head Attention · Prefill vs Decode.

**Running example:** the support assistant (an 8B model) runs on one 80 GB GPU. Its weights take about 16 GB in bf16. How many customers can chat at once, with 8k tokens of conversation history each?

#### Every past token leaves keys and values behind

To generate token t, attention needs the keys and values of tokens 1…t−1 in every layer. Recomputing them every step would be quadratic, so they are cached. Each decode step must then read the whole cache from GPU memory, plus all the weights, to produce one token per sequence: decoding is **memory-bandwidth bound**, and the cache, not the weights, grows with users and context length.

### The idea

Think of 32 researchers who each keep a private copy of the same catalogue. Their questions differ, but the catalogues are nearly identical. Share one copy per group of four and you free up most of the shelf space, and they can still ask their own questions.

[Figure: Conversations that fit on one GPU at 8k context. MHA fits 16, GQA-8 fits 64, MLA fits 227 and MQA fits 512.]

_From the lab: the Llama 3 8B shape, with bf16 cache. GQA-8 is what Llama 3 uses._

### Play

**Try to break it.** Switch between MHA, GQA-8, MQA and MLA at 8k context. Then raise the context per conversation and the number of conversations.

#### How many conversations fit on one GPU?

Shape: Llama 3 8B (32 layers, 32 query heads, head size 128), bf16 cache, 80 GB GPU with ~16 GB of weights. MLA uses DeepSeek-V2's latent sizes (512 + 64 per token per layer) applied to this shape, for illustration; DeepSeek's own models have different dimensions. Activations and fragmentation are ignored.

With full **MHA**, each token costs 512 KiB, so one 8k conversation needs **4 GiB** and only **16** conversations fit in the 64 GB left after the weights (64 GiB). At 128k context a single conversation takes the whole 64 GiB. **GQA-8**, what Llama 3 actually uses, cuts that 4×: 1 GiB per conversation, **64** at once. **MQA** is 32× smaller than MHA (512 conversations) and **MLA** about 14× (227). The trap is assuming the smallest cache wins: MQA gives every query head the same keys and values, which costs quality and can make training less stable; that's why GQA became the default and MLA tries to get small caches without the quality loss.

**Now say why:** if MQA has the smallest cache of all, why did GQA become the default?

## Maths

### Maths

#### In one breath

During generation an LLM stores the keys and values of every previous token, the **KV cache**, so it doesn't recompute them. With standard multi-head attention (MHA) every head has its own K and V, and the cache grows with layers × heads × head size × context × batch. **MQA** shares one K/V head across all query heads (smallest cache, some quality loss); **GQA** shares one K/V head per group of query heads (Llama 3: 32 query heads, 8 KV heads, 4× smaller cache, near-MHA quality); **MLA** (DeepSeek-V2/V3) caches one small compressed latent vector per token and rebuilds K and V from it. Because decoding is limited by memory bandwidth, a smaller cache means more users per GPU, longer contexts and faster tokens. What you'll be able to do after this: compute a model's KV cache size and explain the MHA → GQA → MQA → MLA trade-off.

#### The KV-cache formula

$$ \text{KV cache} = {2}\times{L}\times{n_{kv}\times d_{head}}\times{(\text{context}\times\text{batch})}\times{\text{bytes}} $$

For the Llama 3 8B shape (32 layers, head size 128, 8 KV heads, bf16): 2 × 32 × 8 × 128 × 2 bytes = 128 KiB per token.

- **K and V**: Two tensors are cached: keys and values.

- **layers**: Every layer has its own cache.

- **KV heads × head size**: The only term the variants change: MHA keeps all 32 heads, GQA 8 groups, MQA 1 head; MLA replaces this term with one small latent.

- **tokens in flight**: Context length times batch size: every token of every conversation.

- **bytes per number**: 2 for bf16/fp16, 1 for an FP8 cache.

- **MQA** (Shazeer 2019): all query heads share a single K and V head.

- **GQA** (Ainslie et al. 2023): query heads are split into G groups, each sharing one K/V head. G = number of heads is MHA; G = 1 is MQA.

- **MLA** (DeepSeek-V2, 2024): K and V are projected down to a shared latent c (512 numbers per token) plus a small 64-dimensional RoPE key; only these are cached, and the up-projections are folded into the query and output matrices at inference.

## In practice

### In practice

#### Quality vs cache size

- **GQA** (Ainslie et al., EMNLP 2023): converting an MHA checkpoint to GQA and "uptraining" with about 5% of the original pre-training compute gave quality close to MHA with speed close to MQA. Llama 2 70B, Llama 3 (all sizes), Mistral and Qwen use GQA.

- **MLA** (DeepSeek-V2): reduced the KV cache by 93.3% compared with DeepSeek 67B and raised maximum generation throughput 5.76×; the paper's ablation reports MLA matching or beating MHA quality. DeepSeek-V3 and Kimi K2 use it. The cost is extra compute to decompress.

- Other levers stack on top: quantising the cache to FP8 (2× smaller), sliding-window layers that keep only recent tokens (Long Context), and paged memory in serving engines like vLLM.

#### Many queries can share keys and values

Query heads need to be diverse to look for different things, but the keys and values they search over are highly redundant across heads. Sharing them (GQA, MQA) or compressing them into a low-rank latent (MLA) keeps most of the model's quality while cutting the memory that decoding has to read at every step.

To go past this, read Attention Alternatives.

### The answer that sounds right

#### "The smallest cache wins, so MQA is strictly better"

It sounds right, since MQA fits 512 conversations where GQA-8 fits 64. But giving every query head the same keys and values costs quality and can make training less stable. That's why GQA became the default, and why MLA tries to get a small cache without the quality loss. And the weights usually aren't the limit either: at long context, the KV cache dominates.

## Say it

### How many conversations fit on one GPU, and how do GQA and MLA raise that?

#### The interviewer pushes further

Follow-up 1 of 3

Does GQA reduce compute or memory?

Mainly memory and memory traffic: fewer K/V projections and a smaller cache to read each step. Attention FLOPs for the query side stay the same.

Follow-up 2 of 3

Can you convert an MHA model to GQA?

Yes: mean-pool the K and V heads within each group, then uptrain briefly (about 5% of pre-training compute in the GQA paper).

Follow-up 3 of 3

Why does MLA need a separate RoPE key?

RoPE rotates keys by position, which would stop the up-projection from being folded into the query matrix; DeepSeek adds a small decoupled key that carries the rotary position instead.

#### The 30-second answer

During decoding we cache keys and values for every token, layer and head; the cache size is 2 × layers × KV heads × head dimension × tokens × bytes, and since decoding is memory-bandwidth bound it limits batch size and context. MQA shares one K/V head across all query heads, which is smallest but loses quality; GQA shares one K/V head per group, for example 8 groups for 32 query heads in Llama 3, giving a 4× smaller cache with near-MHA quality; and DeepSeek's MLA caches a compressed latent per token and reconstructs K and V, cutting the cache by over 90% with comparable quality. For an 8B Llama-3-style model that's 128 KiB per token, so 1 GiB for an 8k conversation.

**Go further**

#### What not to say

- "The weights are what limits batch size." At long context the KV cache usually dominates.

- "MQA is strictly better because it's smallest." It trades quality and stability for memory.

**Key terms and sources**

Why the KV cache, not the weights, limits how many users an LLM can serve at long context, and how multi-query, grouped-query and multi-head latent attention shrink it: what each one shares or compresses, what it costs in quality, and how to size the cache for a real model · built from Shazeer (MQA, 2019), Ainslie et al. (GQA, EMNLP 2023), DeepSeek-AI (DeepSeek-V2, 2024) and Meta's Llama 3 report (2024) · checked 29 Oct 2026

#### Sources

1. N. Shazeer, "Fast Transformer Decoding: One Write-Head is All You Need", 2019, [arXiv:1911.02150](https://arxiv.org/abs/1911.02150).

2. J. Ainslie et al., "GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints", EMNLP 2023, [arXiv:2305.13245](https://arxiv.org/abs/2305.13245).

3. DeepSeek-AI, "DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model", 2024, [arXiv:2405.04434](https://arxiv.org/abs/2405.04434).

4. Llama Team, Meta, "The Llama 3 Herd of Models", 2024, [arXiv:2407.21783](https://arxiv.org/abs/2407.21783).

5. W. Kwon et al., "Efficient Memory Management for Large Language Model Serving with PagedAttention" (vLLM), SOSP 2023, [arXiv:2309.06180](https://arxiv.org/abs/2309.06180).
