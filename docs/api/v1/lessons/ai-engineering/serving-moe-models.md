# Serving Mixture-of-Experts Models

> An MoE model activates only 37B of its 671B parameters. Why is it still hard and expensive to serve?

- Track: AI Engineering › LLM inference and serving › Lessons
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/ai-engineering/serving-moe-models/
- Before this: Scaling Inference: Parallelism, Replicas and Routing (`ai-engineering/scaling-inference`), Mixture of Experts (`fundamentals/mixture-of-experts`)
- Quiz topic: `infer`

## Intuition

### The situation

Your team wants to switch to a large mixture-of-experts model, because it activates only 37B of its 671B parameters. Finance expects it to cost about the same as a 37B dense model. The interviewer asks:

> An MoE model activates only 37B of its 671B parameters. Why is it still hard and expensive to serve?

#### Why it matters

Most leading open models are now mixtures of experts. The usual interview line, "it only uses 37B parameters, so it's cheap", is only half true. The model is cheap per token in maths, but not in memory, and serving it well takes a different design from a dense model.

### The idea

Think of a hospital with 256 specialists, where each patient sees 8. One patient only needs 8 doctors on shift. But with 64 patients arriving together, almost every specialist is busy, and the hospital must employ all of them anyway. The busiest specialists set how fast the queue moves.

[Figure: Three facts. All experts need memory. Batches touch most experts. The busiest GPU sets the pace.]

_Cheap in maths, not in memory._

### Play

**Try to break it.** Raise the batch from 1 to 64, then 256. Watch reads per step and per token.

#### Batch an MoE

Illustrative, for a DeepSeek-V3-like shape in FP8 at 1 byte per parameter: 671B total and 37B active, with 8 of 256 experts per token. That implies about 16.5B shared parameters and 654.5B in experts. Tokens pick experts at random. It ignores the KV cache and the network.

With **one token**, the model reads about 37 GB per step, as cheap as a 37B dense model. At **64 tokens**, the tokens touch about 87% of experts, and a step reads about 585 GB. That's why the memory bill follows the full 671B. But per token, it's about 9 GB, and at 256 tokens about 2.6 GB, against 70 GB for a dense 70B model in FP8. So MoE is efficient when you batch heavily across many GPUs, and less so for small, latency-sensitive deployments. Real routing is uneven, which makes the busiest experts matter even more.

**Now say why:** why does reading per step rise while reading per token falls?

## How it works

### How it works

#### In one breath

A mixture-of-experts model only uses a few experts per token, so each token needs little maths. But every expert must be in memory, and with a batch, different tokens pick different experts. At batch size 1, a 671B model with 37B active reads about 37 GB per step. At batch size 64, it touches most experts and reads several hundred GB. Large deployments spread experts across many GPUs, which is called **expert parallelism**. Tokens then travel between GPUs to reach their experts, and popular experts become hotspots, so systems **replicate busy experts** to balance the load.

#### What changes for MoE

##### Active parameters aren't the whole story

- **Memory:** all experts must be loaded, so DeepSeek-V3 needs its full 671B parameters in memory.

- **Reads per step:** one token uses 8 of 256 routed experts per layer. But 64 tokens together touch most of them, so a batch reads most of the model each step.

- **Good news:** per token, the cost still falls with batch size, because those reads are shared. That's why MoE pays off at high throughput, and less so for one user on one GPU.

##### Expert parallelism

Put different experts on different GPUs. Each token is sent to the GPUs holding its chosen experts, and the results are sent back. These all-to-all exchanges happen in every MoE layer, so they need fast links, and engines overlap them with computing.

| Deployment | What was reported |
|---|---|
| DeepSeek-V3, by DeepSeek | Prefill on at least 32 GPUs, and decode on 320 GPUs across 40 nodes |
| SGLang, on 96 H100s | 52.3K input and 22.3K output tokens per second per node, for 2,000-token inputs. It estimated $0.20 per million output tokens |
| vLLM, on one GB300 rack | 954K tokens per second per GPU, counting input and output tokens, at 196 tokens per second per user |

These are each team's own results on different hardware and workloads, so they can't be compared with each other.

##### Load balancing

Some experts are far more popular than others, and the busiest GPU sets the pace for the whole step. Expert load balancing places extra copies of busy experts, and rearranges them as traffic shifts. SGLang reported that this gave 1.49× for prefill and 2.54× for decode. vLLM rearranges experts every 3,000 steps, based on the previous 1,000.

##### Splitting attention from experts

Attention and experts behave differently: attention reads each user's KV cache, while experts read shared weights. MegaScale-Infer runs them on separate GPUs and passes micro-batches back and forth, reporting up to 1.90× higher throughput per GPU. Another 2026 approach decodes with a pruned set of experts, reporting up to 1.81× decode throughput at 50% pruning, with some changes to output length that benchmarks can miss.

#### The maths

$$ {\mathbb{E}[\text{experts touched}]} = {E}\Big(1 - {\big(1 - \tfrac{k}{E}\big)^{B}}\Big) $$

Assumes tokens pick experts independently and uniformly, which real routing doesn’t. Real routing is skewed, so busy experts are touched even more, and others less.

- **experts read in one layer**: On average, if tokens choose experts at random.

- **experts per layer**: 256 routed experts in DeepSeek-V3.

- **the chance an expert is unused**: Each of the B tokens picks k experts. With 8 of 256, an expert is skipped by one token 31/32 of the time.

- **more tokens, more experts**: At batch 64, about 87% of experts are touched.

## In practice

### In practice

#### In practice

- **Choose by traffic:** for one user or a small team, a dense model or a small MoE on one GPU may be simpler. Large MoEs shine at high, steady throughput.

- **Watch the busiest GPU:** step time follows the most loaded expert, so track per-expert load, and rebalance.

- **Overlap communication:** all-to-all traffic needs fast links and overlap with computing, or it dominates.

- **Count tokens carefully:** published throughput may count input tokens, cached input or only output. Ask which before comparing.

- **Quantize the experts:** they hold most of the parameters, so FP8 or FP4 experts save the most memory.

### The answer that sounds right

#### "Only 37B is active, so it costs like a 37B model"

It sounds right, since maths per token follows the active parameters. But you must store all 671B, and a batch of users touches most experts every step. It's efficient at high throughput across many GPUs, and much less so for a few users on a small deployment.

## Say it

### An MoE model activates only 37B of its 671B parameters. Why is it still hard and expensive to serve?

#### The interviewer pushes further

Follow-up 1 of 3

Why does an MoE model need so many GPUs if only 37B parameters are active?

All 671B must be stored, because any token may choose any expert. In FP8 that's about 671 GB before the KV cache, so you need many GPUs just to hold it.

Follow-up 2 of 3

What is expert load balancing, and why does it help?

Tokens prefer some experts, so the GPUs holding them become the bottleneck while others wait. Placing extra copies of busy experts, and moving them as traffic shifts, evens out the work.

Follow-up 3 of 3

Would you serve a big MoE for a single internal user?

Probably not. At small batch sizes you pay to hold the whole model, and gain little from sharing reads. A dense model, or a smaller MoE that fits on one GPU, is usually simpler and cheaper.

#### The 30-second answer

An MoE uses only a few experts per token, so maths per token is small, but every expert must be in memory, and a batch of tokens picks different experts. In my example, a 671B model with 37B active reads about 37 GB per step at batch 1, but about 585 GB at batch 64, because most experts get touched. Per token, though, that's only about 9 GB, so MoE pays off at high throughput. At scale I'd use expert parallelism, spreading experts across GPUs with all-to-all communication overlapped with computing, and balance load by replicating busy experts, which SGLang reported gave 2.54 times for decode. I'd also consider separating attention from experts.

**Key terms and sources**

Why MoE models need all their experts in memory, why batching ends up reading most experts, expert parallelism and all-to-all, load balancing with replicated experts, and separating attention from experts. · checked 7 Nov 2026

#### Sources

- [DeepSeek-AI, DeepSeek-V3 Technical Report](https://arxiv.org/abs/2412.19437)

- [SGLang team, Deploying DeepSeek with PD Disaggregation and Large-Scale Expert Parallelism](https://www.lmsys.org/blog/2025-05-05-large-scale-ep/)

- [vLLM, Serving DeepSeek-V4.1-Flash at Scale](https://vllm.ai/blog/2026-10-23-deepseek-v41-flash-pd-wide-ep)

- [Zhu et al., MegaScale-Infer](https://arxiv.org/abs/2504.02263)

- [SlimWise: expert pruning across prefill and decode](https://arxiv.org/abs/2609.34117)

- [Fedus, Zoph and Shazeer, Switch Transformers](https://arxiv.org/abs/2101.03961)

Explanations are ours, built from these sources. Lab numbers are illustrative unless a lab says otherwise. Many recent papers are preprints, and vendor results are their own.
