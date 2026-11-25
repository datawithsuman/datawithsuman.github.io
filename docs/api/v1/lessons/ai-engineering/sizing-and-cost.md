# Sizing and Cost: Cost per Million Tokens

> What does a million tokens cost to self-host, and when is an API cheaper?

- Track: AI Engineering › LLM inference and serving › Lessons
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/ai-engineering/sizing-and-cost/
- Before this: Scaling Inference: Parallelism, Replicas and Routing (`ai-engineering/scaling-inference`)
- Quiz topic: `infer`
- Sources checked: 2026-10-29 · Text last changed: 2026-11-20 · Version: beed7025f4

## Intuition

### The situation

Finance asks what it costs per million output tokens to self-host the 8B assistant on rented H100s, and whether the 70B would be affordable for the premium tier. A colleague says an H100 costs about $4 an hour, so tokens are almost free. The interviewer asks:

> What does a million tokens cost to self-host, and when is an API cheaper?

**Running example:** finance asks what it costs per million output tokens to self-host the 8B assistant on rented H100s, and whether the 70B would be affordable for the premium tier.

#### GPU-hours are easy to price; tokens per GPU-hour are not

An on-demand H100 rents for roughly $3–4 per hour at the median in November 2026, and rental prices rose about 30% over the previous year, by one index. A B200 costs roughly $7.50–9.50. Whether that becomes $0.30 or $15 per million tokens depends on batch size, sequence lengths, model size, precision, engine and how busy the GPU actually is.

### The idea

Think of hiring a bus. The hourly price is fixed, so the cost per passenger depends on how full it is and how much of the day it's running. Packing it does slow everyone down a little. That's batch size, utilisation and your latency target.

[Figure: An 8B model on one H100 at 50 percent utilisation. Batch 1: 15.42 dollars per million tokens, each user sees 144 tokens a second. Batch 32: 73 cents, 95 tokens a second. Batch 128: 37 cents, 47 tokens a second.]

_From the lab: decode only, for the 8B model at 50% utilisation. Use it for comparing, not as a quote._

### Play

**Try to break it.** Raise the batch size from 1 to 32 to 128, watching cost and the speed each user sees. Then change the utilisation, and switch to the 70B.

#### "One GPU, one request at a time"

Napkin model: decode only, 2,048-token average context, 70% of 3.35 TB/s bandwidth per GPU, compute cap at 50% of 989 TFLOPS; KV per token 128 KiB (8B) / 320 KiB (70B). Ignores prefill and input-token cost, so real costs are higher; use it for relative comparisons.

One request at a time (**batch 1**), the 8B model streams a fast 144 tokens/s, but the GPU is reading 16 GB of weights for a single token each step: **$15.42** per million tokens at 50% utilisation. At **batch 32**, 3,052 tokens/s for **$0.73**, with each user still seeing 95 tokens/s. At **batch 128**, $0.37, but each user's stream slows to 47 tokens/s and the KV cache, not the weights, now dominates the reads. **Utilisation** matters as much: the same batch-32 setup costs $0.36 when busy all day and $1.82 at 20%. The **70B in fp8** on 2 GPUs costs about $2.73 at batch 32: roughly 4× the 8B, for a bigger quality jump only if your evaluations show one.

**Now say why:** what stops you from pushing the batch size as high as it will go?

## Maths

### Maths

#### In one breath

Self-hosting cost is simple arithmetic: **$ per million tokens = GPUs × $/GPU-hour ÷ (tokens per second × 3,600) × 106**. The hard part is tokens per second. In decode, each step reads the weights once for the whole batch plus every sequence's KV cache, so step time ≈ bytes read ÷ memory bandwidth. A batch of 1 wastes almost all of it; a batch of 128 shares the weight reads across 128 users, cutting cost per token ~40× while each user's stream slows down. Then multiply by real **utilisation**: a GPU that's busy half the day costs twice as much per token. Self-hosting beats an API only with steady, high-volume traffic (or privacy and control needs); for spiky or small workloads, paying per token is usually cheaper. What you'll be able to do after this: estimate throughput and $/M tokens on a napkin, explain the batch-size and utilisation effects, and argue self-host vs API and engine choice.

#### A napkin model of decode throughput

$$ t_{step} \approx \frac{{W} + {B \cdot L \cdot kv}}{{\text{bandwidth}}}, \qquad {\text{tokens/s} = B / t_{step}} $$

Pope et al., "Efficiently Scaling Transformer Inference", MLSys 2023, [arXiv:2211.05102](https://arxiv.org/abs/2211.05102), analyse these memory and compute bounds in detail.

- **weights, read once per step**: All sequences in the batch share one read of the weights: 16 GB for an 8B model in bf16.

- **KV caches, read per sequence**: Each sequence’s own cache is read every step: batch size × context × bytes per token.

- **memory bandwidth**: About 3.35 TB/s on an H100; real kernels reach perhaps 60–80% of it.

- **tokens per second**: One token per sequence per step, unless the step becomes compute-bound at very large batches (then compute, 2 × parameters FLOPs per token, sets the limit).

## In practice

### In practice

#### Self-host or API, and which engine

- **Self-host when** traffic is steady and large enough to keep GPUs busy, data must stay in your environment, you need a fine-tuned or open model, or latency control matters. **Use an API when** traffic is small or spiky, you need frontier quality, or you don't want to run GPU infrastructure. Include engineering and on-call time, idle capacity, and input-token (prefill) costs in the comparison.

- **Cost levers:** bigger batches (within the latency SLO), quantization, prefix caching, speculative decoding at low load, smaller or distilled models, routing easy requests to a small model, and batch/offline APIs for non-interactive work.

| Engine | Strengths | Typical use |
|---|---|---|
| **vLLM** | PagedAttention, continuous batching, broad model and hardware support, OpenAI-compatible server | default choice for GPU serving |
| **SGLang** | RadixAttention prefix reuse, fast structured output, strong for agents and shared prompts | prefix-heavy, multi-call and structured workloads |
| **TensorRT-LLM** | compiled, highly tuned NVIDIA kernels (FP8/FP4, in-flight batching) | maximum performance on NVIDIA, more setup |
| **llama.cpp / Ollama** | GGUF quantized models on CPU, Apple silicon and small GPUs | local, edge and on-device |

#### Share the weight reads, keep the GPU busy

Cost per token falls with batch size (weight reads are shared) and with utilisation (idle hours are paid for anyway); the latency SLO caps the batch and traffic patterns cap utilisation.

### The answer that sounds right

#### "Self-hosting is always cheaper than an API"

It sounds right, since a GPU-hour looks cheap against per-token pricing. But throughput and utilisation decide that. In the lab, the same batch-32 setup costs $0.36 when busy all day and $1.82 at 20% utilisation. Self-hosting only wins at high, steady use, and you also have to count engineering and on-call time, idle capacity and input-token costs.

## Say it

### What does a million tokens cost to self-host, and when is an API cheaper?

#### The interviewer pushes further

Follow-up 1 of 3

Estimate batch-1 decode speed for a 70B model in fp8 on one H100.

~70 GB of weights per token ÷ ~2.3 TB/s effective bandwidth ≈ 30 ms per token ≈ 33 tokens/s (and the KV cache must also fit, so in practice 2 GPUs).

Follow-up 2 of 3

Why are input tokens usually cheaper than output tokens in API pricing?

Prefill processes many input tokens per forward pass at high compute efficiency; decode produces one token per sequence per pass and is memory-bound.

Follow-up 3 of 3

Traffic is 10× higher during the day than at night. How do you reduce cost?

Autoscale replicas, fill night capacity with batch jobs (evals, offline summarisation), use spot or reserved capacity sensibly, or send overflow to an API.

#### The 30-second answer

Cost per million tokens is GPUs times price per hour divided by tokens per hour. Decode is memory-bound, so a step takes roughly the weights plus all sequences' KV caches divided by bandwidth: at batch 1 an 8B model on an H100 makes about 150 tokens a second, and at batch 32 to 128 the weight reads are shared and throughput rises 20 to 40 times, at the cost of slower per-user streaming. Then I divide by real utilisation, because idle GPU hours still cost money. Self-hosting wins with steady high volume or data and customisation needs; otherwise a per-token API is often cheaper. For the engine I'd default to vLLM, SGLang for prefix-heavy or agent workloads, TensorRT-LLM for peak NVIDIA performance, and llama.cpp for local or edge.

**Go further**

#### What not to say

- "An H100 costs $4/hour, so a token costs almost nothing." Throughput and utilisation decide that.

- "Self-hosting is always cheaper than an API." Only at high, steady utilisation.

**Key terms and sources**

How to estimate what serving an LLM costs: throughput from first principles (memory bandwidth vs compute), why batch size and utilisation dominate cost per million tokens, the latency each user feels, self-hosting vs paying per token for an API, and how to choose an inference engine (vLLM, SGLang, TensorRT-LLM, llama.cpp) · built from Pope et al. (Efficiently Scaling Transformer Inference, MLSys 2023), Kwon et al. (vLLM, SOSP 2023), NVIDIA H100 specifications, public GPU rental price surveys (Oct 2026) and the vLLM, SGLang, TensorRT-LLM and llama.cpp documentation · checked 29 Oct 2026

#### Sources

1. R. Pope et al., "Efficiently Scaling Transformer Inference", MLSys 2023, [arXiv:2211.05102](https://arxiv.org/abs/2211.05102).

2. W. Kwon et al., "Efficient Memory Management for Large Language Model Serving with PagedAttention", SOSP 2023, [arXiv:2309.06180](https://arxiv.org/abs/2309.06180).

3. NVIDIA H100 Tensor Core GPU datasheet (3.35 TB/s HBM3, 989 TFLOPS dense BF16, SXM).

4. GPU rental price surveys, Nov 2026: [GetDeploying price trends](https://getdeploying.com/gpu-price-trends) (H100 median about $3.87, up 30% over 12 months) and the [Ornn compute price index](https://data.ornn.com/) (H100 SXM $3.13, B200 $9.46 on 5 Nov). Indices differ by provider mix.

5. vLLM, SGLang, TensorRT-LLM and llama.cpp documentation.
