# Scaling Inference: Parallelism, Replicas and Routing

> How many GPUs for 1,000 users, and why FP8 weights may not help?

- Track: AI Engineering › LLM inference and serving › Lessons
- Type: Concept · 25 min
- Page: https://aimlrounds.com/tracks/ai-engineering/scaling-inference/
- Before this: Serving Metrics and SLOs (`ai-engineering/serving-metrics-and-slos`), Training at Scale: Mixed Precision, Parallelism, ZeRO/FSDP (`fundamentals/distributed-training`)
- Quiz topic: `infer`

## Intuition

### The situation

The premium tier wants 1,000 simultaneous conversations, with up to 8k tokens of context each, on 80 GB GPUs. A colleague says to quantise the weights to FP8 and need half the GPUs. The interviewer asks:

> How many GPUs for 1,000 users, and why may FP8 weights not help?

**Running example:** the premium tier wants 1,000 simultaneous conversations, each with up to 8k tokens of context, on 80 GB GPUs. Which model, which precision, and how many GPUs?

#### Too big for one GPU, too many users for one replica

A 70B model in bf16 is 141 GB: it doesn't fit on one 80 GB GPU. And even when it fits, one replica can only hold so many conversations' KV caches. Scaling inference means splitting each model across GPUs efficiently, then running enough copies, and routing traffic well between them.

### The idea

Think of a hotel. The weights are the lobby and kitchen, and every guest needs their own room, which is the KV cache. Shrink the lobby and each building gets smaller, but it also has fewer rooms. You still need the same total number of rooms, so you end up with more buildings.

[Figure: Serving 1,000 conversations. Llama 3 70B in bf16: 4 GPUs per replica, 54 conversations per replica, 76 GPUs. In fp8: 2 GPUs, 27 conversations, still 76 GPUs. DeepSeek-V3 in fp8: 16 GPUs, 835 conversations, 32 GPUs.]

_From the lab: a memory floor for 1,000 conversations, ignoring activations and throughput limits._

### Play

**Try to break it.** Pick Llama 3 70B, and switch between bf16 and fp8 weights. Then try DeepSeek-V3, and change the number of conversations.

#### "Quantise the weights and we'll need half the GPUs"

80 GB GPUs, 90% usable; GPUs per replica = smallest power of two holding the weights with room for at least 8 conversations; KV cache in bf16 at 8,192 tokens per conversation (8B: 128 KiB/token, 70B: 320, 405B: 504, DeepSeek-V3 with MLA: about 69). Ignores activations and throughput limits: a memory floor, not a full plan.

**Llama 3 70B in bf16** (141 GB) needs a 4-GPU replica, which then holds **54** conversations of 8k tokens; 1,000 users need 19 replicas, **76 GPUs**. Quantise the weights to **fp8** and a replica fits on 2 GPUs, but each now holds only 27 conversations, because the KV cache didn't shrink: still **76 GPUs**. At high concurrency the KV cache is the bottleneck, which is why GQA/MLA, FP8 KV caches and prefix sharing matter as much as weight quantization. The contrast: **DeepSeek-V3** is far bigger (671 GB in fp8, a 16-GPU, two-node replica) but its MLA cache is so small that one replica holds 835 conversations, so 1,000 users fit on 32 GPUs.

**Now say why:** DeepSeek-V3 is far bigger than Llama 3 70B, so why does it need fewer GPUs here?

## How it works

### How it works

#### In one breath

Serving at scale has two separate questions. **1. How many GPUs per replica?** Enough to hold the weights plus room for the KV cache. Inside a replica, **tensor parallelism** splits each layer across GPUs in one NVLink node (low latency, chatty), **pipeline parallelism** splits layers across nodes, and **expert parallelism** spreads MoE experts. **2. How many replicas?** Enough to hold every concurrent conversation's KV cache and meet the SLOs. Often the KV cache dominates: halving the weights with FP8 can leave the total GPU count unchanged. Large systems go further: separate prefill and decode clusters with KV transfer between them (DeepSeek-V3, Kimi's Mooncake, NVIDIA Dynamo, llm-d), with routers that send requests to the replica that already holds their prefix.What you'll be able to do after this: size a deployment from model, precision and concurrency, choose parallelism, and explain disaggregated serving, routing and autoscaling.

#### Parallelism for serving

| Kind | What is split | Use when |
|---|---|---|
| **Tensor parallel (TP)** | each weight matrix across GPUs; all-reduce in every layer | model doesn't fit one GPU; keep within an NVLink node (≤ 8 GPUs); lowers latency too |
| **Pipeline parallel (PP)** | groups of layers per GPU/node | model doesn't fit one node; adds latency per stage, needs enough requests in flight |
| **Expert parallel (EP)** | MoE experts across GPUs; all-to-all token routing | large MoE models (DeepSeek-V3, Kimi K2) |
| **Data parallel (replicas)** | whole copies of the model | more traffic: scale out behind a router |

The same ideas as training parallelism, but serving has no gradients or optimizer state, and latency per token matters.

## In practice

### In practice

#### Disaggregation, routing and autoscaling

- **Disaggregated prefill and decode** (background): separate GPU pools sized and parallelised for each phase, with KV caches transferred over fast networks. DeepSeek-V3's deployment used a minimum of 32 GPUs for prefill and 320 GPUs (expert parallelism across 40 nodes) for decode. Kimi's Mooncake builds the whole service around a distributed KV-cache pool.

- **Open-source stacks:** NVIDIA Dynamo and llm-d (Kubernetes-native) add disaggregation, KV-cache transfer, and smart routing on top of engines like vLLM, SGLang and TensorRT-LLM.

- **Routing:** balance on queue length and KV usage, and send requests with the same prefix to the same replica (prefix-aware routing); sticky sessions keep multi-turn chats on warm caches.

- **Autoscaling:** scale on queue depth, TTFT or KV-cache usage; large models take minutes to load, so keep warm spare capacity, pre-load weights from fast storage, and use request queues to absorb bursts.

**Large MoE serving, 2025–26.** Teams now spread experts across dozens of GPUs, and balance load by copying busy experts. SGLang reported $0.20 per million output tokens for DeepSeek-V3 on 96 H100s, and vLLM 954K tokens per second per GPU, counting input and output, on one GB300 rack. These are their own results. See Serving Mixture-of-Experts Models.

#### Weights decide the replica, KV caches decide the fleet

Split the model just enough to fit (TP within a node, PP or EP beyond), then add replicas until every concurrent conversation's KV cache and the latency SLOs fit, and route traffic so caches stay warm.

### The answer that sounds right

#### "GPU count = model size / GPU memory"

It sounds right, since the weights have to fit. But that ignores the KV cache for concurrent users. Llama 3 70B in fp8 fits on 2 GPUs per replica, but each holds only 27 conversations, so 1,000 users still need 76 GPUs. And don't run tensor parallelism across the data centre: keep it inside a node.

## Say it

### How many GPUs for 1,000 users, and why may FP8 weights not help?

#### The interviewer pushes further

Follow-up 1 of 3

TP across two nodes or PP across two nodes?

PP: tensor parallelism needs an all-reduce in every layer, which is too slow over inter-node links; pipeline stages only pass activations between stages.

Follow-up 2 of 3

Why would TP=8 sometimes beat TP=4 even if the model fits on 4?

Lower latency per token (each GPU reads fewer weights per step) and more KV space per replica; the cost is more communication and fewer replicas.

Follow-up 3 of 3

How do you handle a 5× traffic spike?

Queue with priorities, shed or degrade low-priority traffic (shorter max tokens, smaller model), scale out from warm pools, and rely on prefix caching to cut prefill.

#### The 30-second answer

First I size a replica: weights plus KV headroom, using tensor parallelism within an NVLink node, pipeline parallelism across nodes if needed, and expert parallelism for MoE models. Then I size the fleet: concurrent conversations times KV cache per conversation, divided by the KV space per replica, checked against throughput and latency SLOs from a load test. Often the KV cache dominates, so FP8 weights alone may not cut GPU count, while GQA, MLA or an FP8 cache do. At large scale I'd disaggregate prefill and decode, as DeepSeek and NVIDIA Dynamo do, route with prefix and load awareness, and autoscale on queue depth with warm capacity because models load slowly.

**Go further**

#### What not to say

- "GPU count = model size / GPU memory." That ignores the KV cache for concurrent users.

- "Tensor parallelism across the data centre." Keep it inside a node.

**Key terms and sources**

How a model too big for one GPU is served (tensor, pipeline and expert parallelism), how many replicas a traffic level needs, why the KV cache rather than the weights often decides the GPU count, how large deployments split prefill and decode across clusters (DeepSeek-V3, Mooncake, NVIDIA Dynamo, llm-d), and how routing and autoscaling work · built from Shoeybi et al. (Megatron-LM, 2019), DeepSeek-AI (DeepSeek-V3 Technical Report, 2024), Qin et al. (Mooncake, FAST 2025), Zhong et al. (DistServe, OSDI 2024), and the NVIDIA Dynamo, llm-d and vLLM distributed serving docs · checked 29 Oct 2026

#### Sources

1. M. Shoeybi et al., "Megatron-LM", 2019, arXiv:1909.08053.

2. DeepSeek-AI, "DeepSeek-V3 Technical Report", 2024, arXiv:2412.19437 (§3.4, inference and deployment).

3. R. Qin et al., "Mooncake: A KVCache-centric Disaggregated Architecture for LLM Serving", FAST 2025, arXiv:2407.00079; Y. Zhong et al., "DistServe", OSDI 2024, arXiv:2401.09670.

4. NVIDIA Dynamo documentation; llm-d documentation (llm-d.ai); vLLM distributed serving documentation.
