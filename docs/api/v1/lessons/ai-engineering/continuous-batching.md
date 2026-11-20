# Continuous Batching and Scheduling

> Trace one request through a vLLM-style engine.

- Track: AI Engineering › LLM inference and serving › Lessons
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/ai-engineering/continuous-batching/
- Before this: KV Cache Management and PagedAttention (`ai-engineering/kv-cache-and-pagedattention`)
- Quiz topic: `infer`

## Intuition

### The situation

The assistant gets quick answers of about 50 tokens and refund explanations of about 400. A colleague batches 8 requests together and runs them to the end, so one long answer holds up seven short ones. The interviewer asks:

> How do you schedule requests of unknown length on one GPU?

**Running example:** the support assistant gets a mix of quick answers ("Your order is on its way", ~50 tokens) and long ones (refund explanations, ~400 tokens). The GPU can decode 8 sequences at once in this toy version.

#### Different lengths, random arrivals

Traditional ML serving batches requests of the same shape and runs them together. LLM requests differ in prompt length and, unpredictably, in output length. If a batch must finish together, one long answer holds up seven short ones, and the short ones' slots idle until it's done.

### The idea

Think of a restaurant that seats 8 people at once and won't seat anyone new until the slowest eater has left. Empty chairs sit there while a queue waits at the door. Continuous batching seats the next person the moment any chair frees up.

[Figure: For 48 requests, static batching takes 2,121 steps at 34.9 percent slot use with average latency 946 steps. Continuous batching takes 954 steps at 77.6 percent with average latency 344.]

_From the lab: 48 requests and 8 decode slots, ignoring prefill._

### Play

**Try to break it.** Switch between static and continuous batching. Compare the decode steps, slot utilisation and average request latency.

#### Static batches vs refilling every step

48 requests all waiting at the start; 8 decode slots; 80% short answers (10–100 tokens), 20% long (250–500); fixed seed. Prefill is ignored to isolate the batching effect.

With **static batching**, each group of 8 runs as long as its longest answer: the GPU needs **2,121** steps and slots are busy only **34.9%** of the time. **Continuous batching** fills a slot the moment it frees up: **954** steps, 77.6% utilisation (the rest is the tail at the end, when the last long answers run alone), and the average request finishes after 344 steps instead of 946. Short answers no longer wait for long ones.

**Now say why:** what makes it possible to rebuild the batch at every step?

## How it works

### How it works

#### In one breath

GPUs are efficient only when many requests decode together, but requests arrive at random times and finish at very different lengths. **Static batching** groups requests and runs the group until its _longest_ member finishes, so slots sit idle and new arrivals wait. **Continuous batching** (Orca's iteration-level scheduling) rebuilds the batch at **every decode step**: finished requests leave immediately and waiting ones join. A scheduler enforces a **token budget** per step, admits requests only if their KV blocks fit, mixes chunked prefills with ongoing decodes, and preempts requests when memory runs out. Orca reported 36.9× higher throughput than FasterTransformer at the same latency on GPT-3 175B. What you'll be able to do after this: explain continuous batching, trace a request through an inference engine, and name the scheduling knobs and their trade-offs.

#### One request's life in a vLLM-style engine

1. **Arrive:** the API server tokenises the prompt and puts the request in the **waiting queue**.

2. **Admit:** each scheduling step, the scheduler checks the **token budget** (e.g. max 8,192 tokens per step) and the **free KV blocks**; if both allow, it allocates blocks and moves the request to **running**.

3. **Prefill:** the prompt is processed, possibly split over several steps (**chunked prefill**) so it doesn't stall others; its K and V fill the new blocks. The first output token is sampled: that's the TTFT.

4. **Decode:** every step, all running requests advance one token in the same forward pass; a new block is allocated whenever one fills.

5. **Preempt if needed:** if no block is free, the scheduler evicts the lowest-priority request (recompute or swap) and puts it back in the queue.

6. **Finish:** on an end token or max length, blocks return to the pool (or to the prefix cache) and the response is detokenised and streamed out.

## In practice

### In practice

#### The scheduler's knobs and trade-offs

- **Max batched tokens per step** (vLLM `max_num_batched_tokens`): larger favours throughput and TTFT (big prefill chunks); smaller keeps decode steps short, favouring inter-token latency.

- **Max sequences** (`max_num_seqs`): caps the batch; bounded by KV memory anyway.

- **Chunked prefill** (Sarathi-Serve): splits long prompts into chunks that ride along with decodes, avoiding stalls; now the vLLM default.

- **Priorities and fairness:** first-come-first-served by default; priority classes (e.g. interactive vs batch jobs), cancellation of abandoned requests, and timeouts matter in production.

- **Preemption policy:** recompute (cheap for short contexts) vs swap to CPU (better for long ones).

#### Schedule per token, not per request

Because every decode step is a fresh forward pass, the batch can be rebuilt each step; doing so keeps the GPU full and lets short requests finish without waiting for long ones.

### The answer that sounds right

#### "Batching always increases latency"

It sounds right, since a bigger batch feels like more waiting. But in the lab, continuous batching cuts average latency from 946 steps to 344 compared with static batching, because short answers stop waiting for long ones. Setting the batch as high as possible isn't right either: it's bounded by KV memory, and it hurts inter-token latency.

## Say it

### How do you schedule requests of unknown length on one GPU?

#### The interviewer pushes further

Follow-up 1 of 3

Why does a long prefill hurt other users' streaming?

It's processed in the same forward pass as everyone's decode step, making that step much longer; chunked prefill bounds the extra work per step.

Follow-up 2 of 3

How would you prioritise interactive chat over batch summarisation on the same GPUs?

Priority scheduling or separate queues with preemption of the batch class, or separate deployments; batch jobs can also use cheaper offline APIs.

Follow-up 3 of 3

Why doesn't continuous batching reach 100% utilisation?

At the end of a burst, or under light load, there aren't enough requests to fill every slot; under steady load it stays near full.

#### The 30-second answer

Static batching runs a group of requests until the longest finishes, so slots idle and new requests wait. Continuous batching, from Orca, schedules at the iteration level: after every decode step finished sequences leave and waiting ones join. In vLLM a request is tokenised and queued, admitted when the per-step token budget and free KV blocks allow, prefilled possibly in chunks, then decoded one token per step alongside others, preempted by swap or recompute if memory runs out, and its blocks freed when it finishes. The key knobs are max batched tokens, max sequences and chunk size, trading throughput and time to first token against inter-token latency.

**Go further**

#### What not to say

- "Batching always increases latency." Continuous batching cuts average latency compared with static batching.

- "Just set the batch size as high as possible." It's bounded by KV memory and hurts inter-token latency.

**Key terms and sources**

How a serving engine decides, every few milliseconds, which requests run: static vs continuous (iteration-level) batching, the token budget, admission control, preemption, prefill/decode mixing with chunked prefill, and a step-by-step trace of one request through a vLLM-style engine, the classic inference-infrastructure interview question · built from Yu et al. (Orca, OSDI 2022), Kwon et al. (vLLM, SOSP 2023), Agrawal et al. (Sarathi-Serve, OSDI 2024) and the vLLM scheduler documentation · checked 29 Oct 2026

#### Sources

1. G.-I. Yu et al., "Orca: A Distributed Serving System for Transformer-Based Generative Models", OSDI 2022.

2. W. Kwon et al., "Efficient Memory Management for Large Language Model Serving with PagedAttention", SOSP 2023, [arXiv:2309.06180](https://arxiv.org/abs/2309.06180).

3. A. Agrawal et al., "Taming Throughput-Latency Tradeoff in LLM Inference with Sarathi-Serve", OSDI 2024, [arXiv:2403.02310](https://arxiv.org/abs/2403.02310).

4. vLLM documentation: scheduler configuration and optimisation guide, [docs.vllm.ai](https://docs.vllm.ai/).
