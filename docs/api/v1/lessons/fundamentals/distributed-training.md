# Training at Scale: Mixed Precision, Parallelism, ZeRO/FSDP

> Why does a 70B model need 1.1 TB to train, and how is it split?

- Track: Fundamentals › LLMs › Pretraining
- Type: Concept · 25 min
- Page: https://aimlrounds.com/tracks/fundamentals/distributed-training/
- Before this: Anatomy of a Modern LLM (`fundamentals/modern-llm-architecture`)
- Quiz topic: `pre`

## Intuition

### The situation

The team wants to fully fine-tune a 70B model on a cluster of 80 GB GPUs. A colleague says just add more GPUs with data parallel until it fits. The interviewer asks:

> Why does a 70B model need 1.1 TB to train, and how is it split?

**Running example:** the team wants to fully fine-tune (or continue pre-training) a 70B model for the support assistant on a cluster of 80 GB GPUs. How many GPUs, and which strategy?

#### Too big for one GPU, too slow on one GPU

Two separate limits. **Memory:** parameters, gradients, optimizer state and activations must fit. **Time:** Llama 3 405B needed 3.8 × 1025 FLOPs; a single H100 at a realistic 400 TFLOPS would take about 3,000 years. Parallelism has to split both the memory and the work, while keeping communication from dominating.

### The idea

Think of cooks who each keep their own full copy of a huge recipe library. Hiring more cooks never shrinks the library. Split it across everyone's shelves, and each cook fetches the page when needed. That saves a lot of room, in exchange for more walking.

[Figure: Model state per GPU for a 70B model on 64 GPUs. Data parallel 1,120 gigabytes, ZeRO-1 293, ZeRO-2 155, and ZeRO-3 17.5, which is the only one under the 80 gigabyte GPU limit.]

_From the lab: 16 bytes per parameter, before activations. Only ZeRO-3 fits on an 80 GB GPU._

### Play

**Try to break it.** At 70B and 64 GPUs, go from DDP to ZeRO-3. Then change the GPU count under DDP. In the second lab, change the pipeline stages and micro-batches.

#### Model-state memory per GPU

16 bytes per parameter (bf16 weights and gradients, fp32 master weights and Adam moments), sharded over all GPUs as one data-parallel group. Activations, buffers and fragmentation are not included, so leave headroom. GB = 10⁹ bytes.

The naive approach, **plain data parallelism**, keeps everything on every GPU: a 70B model needs **1,120 GB** per GPU no matter how many GPUs you add. **ZeRO-1** (shard only the optimizer state) brings that to 293 GB on 64 GPUs, **ZeRO-2** to 155 GB, and **ZeRO-3/FSDP**, which also shards the weights, to **17.5 GB**, leaving room for activations. Even an 8B model doesn't fit with DDP (128 GB), but fits with ZeRO-1 on 8 GPUs (44 GB). The price of ZeRO-3 is communication: each layer's weights are gathered before use, which is why huge models also use tensor and pipeline parallelism.

##### The pipeline bubble

Forward pass shown (GPipe-style); the backward pass has the same bubble. Bubble fraction = (p − 1) / (m + p − 1).

With **4 stages** and only **4 micro-batches**, GPUs sit idle **42.9%** of the time while the pipeline fills and drains. Splitting the batch into 32 micro-batches cuts the bubble to **8.6%**. Schedules like 1F1B and interleaved stages (Narayanan et al. 2021) shrink it further and limit memory.

**Now say why:** ZeRO-3 clearly uses the least memory, so why do huge runs also need tensor and pipeline parallelism?

## How it works

### How it works

#### In one breath

With **mixed precision** and the Adam optimiser, training needs about **16 bytes per parameter** before any activations: 2 for bf16 weights, 2 for bf16 gradients, and 12 for the fp32 master weights plus Adam's two moments. A 70B model needs 1.1 TB, far beyond one 80 GB GPU. **Data parallelism** copies the model to every GPU and averages gradients, but doesn't save memory. **ZeRO** (and PyTorch **FSDP**) shards the optimizer state, then gradients, then the weights themselves across the data-parallel GPUs, gathering pieces only when needed. **Tensor parallelism** splits each matrix multiply across GPUs in a fast NVLink node; **pipeline parallelism** puts different layers on different GPUs and uses micro-batches to shrink idle "bubbles". Llama 3 405B combined four kinds of parallelism on 16,000 H100s. What you'll be able to do after this: compute training memory per GPU, and explain DP, ZeRO stages, TP, PP and when to use each.

#### Where 16 bytes per parameter come from

- **Mixed precision** (Micikevicius et al. 2018): forward and backward passes in 16-bit (bf16 today, which has fp32's range and needs no loss scaling), with an fp32 **master copy** of the weights for the update, so small updates aren't rounded away.

- **Adam** keeps two fp32 moments per parameter. Total: 2 (bf16 weights) + 2 (bf16 grads) + 4 (fp32 master) + 4 + 4 (Adam m, v) = **16 bytes** (ZeRO paper's accounting).

- **Activations** come on top and grow with batch × sequence length × layers; **activation checkpointing** stores only some of them and recomputes the rest in the backward pass.

| Strategy | What is split | Communication |
|---|---|---|
| Data parallel (DDP) | the batch; full model copy per GPU | all-reduce of gradients each step |
| ZeRO-1 / -2 / -3 (FSDP) | optimizer state / + gradients / + weights, across data-parallel GPUs | ZeRO-1/2 ≈ DDP; ZeRO-3 ≈ 1.5× (gathers weights each layer) |
| Tensor parallel (Megatron) | each weight matrix, column- or row-wise | all-reduce inside every layer: keep within one NVLink node (≤ 8 GPUs) |
| Pipeline parallel | groups of layers per GPU | activations between stages; idle bubbles |
| Sequence / context parallel | the sequence dimension | needed for very long contexts |

## In practice

### In practice

#### 3D and 4D parallelism

- **Rule of thumb:** tensor parallelism inside a node (fast NVLink), pipeline parallelism across nodes, data parallelism / FSDP across everything else; add context parallelism for long sequences and expert parallelism for MoE.

- **Llama 3 405B** used tensor, pipeline, context and data (FSDP) parallelism on up to 16K H100 GPUs, reaching 38–43% model FLOPs utilisation (MFU).

- **For fine-tuning** at smaller scale, FSDP or DeepSpeed ZeRO-3 alone is usually enough; LoRA avoids most optimizer state entirely (AI Engineering › Fine-tuning).

#### Shard what's redundant, keep chatty work local

Data parallelism stores the same state N times; ZeRO/FSDP removes that redundancy, tensor parallelism splits work that needs constant communication across the fastest links, and pipeline parallelism splits layers across slower links at the cost of bubbles.

### The answer that sounds right

#### "Adding GPUs to DDP lets a bigger model fit"

It sounds right, since more GPUs means more memory in total. But DDP keeps everything on every GPU, so a 70B model needs 1,120 GB per GPU however many you add. You need sharding or model parallelism. The weights aren't the main cost either: optimizer state is 12 of the 16 bytes.

## Say it

### Why does a 70B model need 1.1 TB to train, and how is it split?

#### The interviewer pushes further

Follow-up 1 of 3

How much memory to fully fine-tune a 7B model with Adam?

16 × 7B = 112 GB of model state plus activations: more than one 80 GB GPU; use ZeRO/FSDP over several GPUs, an 8-bit optimizer, or LoRA.

Follow-up 2 of 3

Why keep fp32 master weights if we compute in bf16?

bf16 has only 8 bits of mantissa: small updates (learning rate × gradient) would round to zero when added to a bf16 weight.

Follow-up 3 of 3

Why not tensor parallelism across nodes?

It needs an all-reduce inside every layer; across slower inter-node links that communication would dominate the step time.

#### The 30-second answer

Mixed-precision training with Adam needs about 16 bytes per parameter: bf16 weights and gradients plus fp32 master weights and two Adam moments, so a 70B model needs over a terabyte before activations. Data parallelism replicates the model and all-reduces gradients; ZeRO stages 1, 2 and 3, or FSDP, shard optimizer state, gradients and finally weights across data-parallel ranks, cutting per-GPU memory to roughly 16N divided by the number of GPUs at the cost of more communication. Tensor parallelism splits each matmul across GPUs within an NVLink node, pipeline parallelism assigns layers to different GPUs with micro-batches to reduce the bubble of (p−1)/(m+p−1), and large runs like Llama 3 405B combine tensor, pipeline, context and data parallelism.

**Go further**

#### What not to say

- "Adding GPUs to DDP lets a bigger model fit." DDP replicates the model; you need sharding or model parallelism.

- "The weights are the main memory cost." Optimizer state is 12 of the 16 bytes.

**Key terms and sources**

Why a 70B model can't be trained on one GPU, where the memory goes (16 bytes per parameter with mixed-precision Adam), and how data, tensor, pipeline and sequence parallelism plus ZeRO/FSDP sharding split the work across thousands of GPUs · built from Micikevicius et al. (Mixed Precision Training, ICLR 2018), Rajbhandari et al. (ZeRO, SC 2020), Zhao et al. (PyTorch FSDP, VLDB 2023), Shoeybi et al. (Megatron-LM, 2019), Huang et al. (GPipe, NeurIPS 2019), Narayanan et al. (2021) and Meta's Llama 3 report (2024) · checked 29 Oct 2026

#### Sources

1. P. Micikevicius et al., "Mixed Precision Training", ICLR 2018, [arXiv:1710.03740](https://arxiv.org/abs/1710.03740).

2. S. Rajbhandari et al., "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", SC 2020, [arXiv:1910.02054](https://arxiv.org/abs/1910.02054); Y. Zhao et al., "PyTorch FSDP", VLDB 2023, [arXiv:2304.11277](https://arxiv.org/abs/2304.11277).

3. M. Shoeybi et al., "Megatron-LM", 2019, [arXiv:1909.08053](https://arxiv.org/abs/1909.08053); D. Narayanan et al., "Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM", SC 2021, [arXiv:2104.04473](https://arxiv.org/abs/2104.04473).

4. Y. Huang et al., "GPipe", NeurIPS 2019, [arXiv:1811.06965](https://arxiv.org/abs/1811.06965).

5. Llama Team, Meta, "The Llama 3 Herd of Models", 2024, [arXiv:2407.21783](https://arxiv.org/abs/2407.21783) (§3.3).
