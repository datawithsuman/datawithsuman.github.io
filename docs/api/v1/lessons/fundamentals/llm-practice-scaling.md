# LLM Practice 1: Pretraining and Scaling Maths

> 9 back-of-the-envelope questions: parameters, KV cache, FLOPs, memory, MoE, image tokens.

- Track: Fundamentals › LLMs › Evaluating LLMs and practice
- Type: Interview · 35 min
- Page: https://aimlrounds.com/tracks/fundamentals/llm-practice-scaling/
- Before this: Training at Scale: Mixed Precision, Parallelism, ZeRO/FSDP (`fundamentals/distributed-training`), Mixture of Experts (`fundamentals/mixture-of-experts`)
- Quiz topic: `llmgen`
- Sources checked: 2026-10-29 · Text last changed: 2026-11-19 · Version: c3f3fc66a9

How to use this page

Give yourself about 5 minutes per question, as in an interview. These are back-of-the-envelope questions interviewers love. Work them out on paper with round numbers first, then open the answer and compare.

**The formulas:** params per layer ≈ attention (2d² + 2·d·kv_heads·head_dim) + SwiGLU FFN (3·d·d_ff); KV cache = 2 × layers × kv_heads × head_dim × tokens × bytes; training FLOPs ≈ 6·N·D; compute-optimal D ≈ 20·N, so N ≈ √(C/120); mixed-precision Adam ≈ 16 bytes per parameter.

Question 1 · Easy · parameter count

### A model has d = 4,096, 32 layers, full multi-head attention, a SwiGLU FFN with hidden size 11,008, a 32,000-token vocabulary and untied input/output embeddings. How many parameters?

Answer: **about 6.74 B (this is Llama 2 7B)**

1. Attention per layer: 4d² = 4 × 4,096² ≈ 67.1 M (Q, K, V, O, all full size with MHA).

2. FFN per layer: 3 × 4,096 × 11,008 ≈ 135.3 M. Per layer ≈ 202.4 M; × 32 layers ≈ 6.48 B.

3. Embeddings: 2 × 32,000 × 4,096 ≈ 0.26 B. Total ≈ 6.74 B; norms add only ~0.3 M.

**Follow-up:** Which change would cut the most parameters: GQA with 8 KV heads, or tying the embeddings? GQA saves 2 × 4,096 × (4,096 − 1,024) × 32 ≈ 0.81 B; tying saves 0.13 B.

Question 2 · Easy · KV cache

### For that same model (32 layers, 32 heads of size 128, bf16), how much KV cache does one 4,096-token conversation need? How many fit next to the 13.5 GB of weights on an 80 GB GPU?

Answer: **0.5 MiB per token → 2 GiB per conversation → about 30 conversations**

1. Per token: 2 (K and V) × 32 layers × 32 heads × 128 × 2 bytes = 524,288 bytes = 0.5 MiB.

2. × 4,096 tokens = 2 GiB per conversation.

3. (80 − 13.5) GB ≈ 61.9 GiB free → about 30 conversations, before activations and fragmentation. With GQA-8 it would be 4× as many.

**Follow-up:** Why does this limit throughput rather than just memory? Each decode step reads the whole cache; more conversations per batch amortise the weight reads, so a bigger cache budget means higher tokens per second.

Question 3 · Medium · training compute

### Llama 2 7B was trained on 2 T tokens. Estimate the training FLOPs and the A100 GPU-hours at 40% utilisation (A100 bf16 peak = 312 TFLOPS). Meta reported 184,320 GPU-hours. How close are you?

Answer: **8.4 × 10²² FLOPs ≈ 187,000 GPU-hours: within 2% of the reported figure**

1. C ≈ 6 N D = 6 × 7 × 10⁹ × 2 × 10¹² = 8.4 × 10²² FLOPs.

2. Effective throughput per GPU: 0.4 × 312 × 10¹² ≈ 1.25 × 10¹⁴ FLOP/s.

3. 8.4 × 10²² / 1.25 × 10¹⁴ ≈ 6.7 × 10⁸ GPU-seconds ≈ 187,000 GPU-hours, vs 184,320 reported in the Llama 2 paper.

**Follow-up:** How many days on 2,048 GPUs? 187,000 / 2,048 ≈ 91 hours ≈ 3.8 days, ignoring restarts and evaluation.

Question 4 · Medium · Chinchilla

### You have a budget of 10²³ training FLOPs. What model size and token count are compute-optimal under the Chinchilla rule of ~20 tokens per parameter?

Answer: **about 29 B parameters on about 580 B tokens**

1. C = 6ND and D = 20N, so C = 120N² and N = √(C/120) = √(8.3 × 10²⁰) ≈ 2.9 × 10¹⁰.

2. D = 20N ≈ 5.8 × 10¹¹ tokens.

3. Check: 6 × 2.9 × 10¹⁰ × 5.8 × 10¹¹ ≈ 1.0 × 10²³. ✓

**Follow-up:** Your model will serve 1 billion requests a month. Would you still pick 29 B? Probably not: train a smaller model (say 7–8 B) on many more tokens; it loses a little loss but is ~4× cheaper per request (Sardana et al. 2024).

Question 5 · Medium · training memory

### You want to fully fine-tune a 13 B model with Adam in mixed precision on 8 × 80 GB GPUs. Does it fit with plain data parallelism? With ZeRO-3 / FSDP?

Answer: **DDP: no (208 GB per GPU); ZeRO-3: 26 GB per GPU of model state, so yes, with room for activations**

1. Mixed-precision Adam ≈ 16 bytes/parameter: 2 (bf16 weights) + 2 (grads) + 12 (fp32 master + Adam m, v).

2. DDP replicates everything: 16 × 13 B = 208 GB per GPU, far above 80 GB.

3. ZeRO-3 shards all of it across 8 GPUs: 208 / 8 = 26 GB each, leaving ~50 GB for activations (use activation checkpointing for long sequences).

**Follow-up:** What if you only had one 80 GB GPU? Use LoRA/QLoRA: freeze the base (in 4-bit for QLoRA) and train small adapters, so optimizer state is tiny.

Question 6 · Hard · MoE parameters

### An MoE model has 32 layers, d = 4,096, GQA with 8 KV heads of size 128, 8 SwiGLU experts per layer with hidden size 14,336, top-2 routing, and a 32,000-token vocabulary (untied). Estimate total and active parameters per token.

Answer: **about 46.7 B total, about 12.9 B active (this is Mixtral 8x7B)**

1. One expert: 3 × 4,096 × 14,336 ≈ 176.2 M. All experts: 8 × 176.2 M × 32 layers ≈ 45.1 B.

2. Attention per layer: 2d² + 2 × 4,096 × 1,024 ≈ 41.9 M; × 32 ≈ 1.34 B. Embeddings: 2 × 32,000 × 4,096 ≈ 0.26 B. Total ≈ 46.7 B.

3. Active: 2 experts × 176.2 M × 32 ≈ 11.3 B, plus attention and embeddings ≈ 12.9 B.

**Follow-up:** How much GPU memory does it need for inference in bf16? All 46.7 B parameters must be loaded: ≈ 93 GB, more than one 80 GB GPU, even though compute per token is like a 13 B model.

Question 7 · Hard · loss spike

### Pre-training a 7 B model: loss starts at 10.4 with a 32,000-token vocabulary, falls smoothly to 2.3 by step 20k, then at step 31k jumps to 7 within 200 steps. Gradient norm and the maximum attention logit had been creeping up for the previous 2k steps. Is the start healthy? What do you do now, and for the next run?

Answer: **the start is healthy (ln 32,000 ≈ 10.4); the spike looks like attention-logit growth: roll back, skip data, and add QK-norm / z-loss / lower LR**

1. Initial loss ≈ ln(vocab) means a well-initialised, uniform output; fine.

2. Rising gradient norm and attention logits before the spike suggest attention-logit growth (softmax saturating), not just one bad batch.

3. Now: restore a checkpoint a few hundred steps before 31k, skip the next few hundred batches, optionally lower the learning rate (PaLM's recipe).

4. Next run: QK-norm, z-loss (10⁻⁴ log² Z), gradient clipping, and monitor max attention logits and per-layer gradient norms.

**Follow-up:** How would you tell bad data from optimisation instability? Replay the same batches from an earlier checkpoint: if the spike doesn't reproduce, it's the interaction of parameters and data (as PaLM found), not the data alone.

Question 8 · Medium · memory bandwidth

### An 8B model in 16-bit serves 32 conversations of 4,096 tokens on one H100 (989 TFLOPS, 3.35 TB/s). Cache is 128 KiB per token. What limits a decode step, and what's the best tokens per second?

Answer: **Memory: about 9.9 ms per step, or about 3,200 tokens a second**

1. Maths: 2 × 8B × 32 = 5.1 × 10¹¹ operations, ÷ 989 × 10¹² ≈ 0.52 ms.

2. Memory: 16 GB of weights + 32 × 4,096 × 131,072 bytes ≈ 33.2 GB, ÷ 3.35 TB/s ≈ 9.9 ms.

3. Memory takes about 19 times longer, so it sets the limit: 32 tokens ÷ 9.9 ms ≈ 3,200 a second.

What would a chip with twice the compute do here? Almost nothing, since the step is waiting on memory.

Question 9 · Easy · image tokens

### A model uses 14-pixel patches on an 896 × 896 image. How many patches is that? After 4 × 4 average pooling, how many image tokens remain, and how much KV cache do they need at 128 KiB per token?

Answer: **4,096 patches, 256 tokens and 32 MiB**

1. 896 ÷ 14 = 64, and 64 × 64 = 4,096 patches.

2. Pooling each 4 × 4 group gives 16 × 16 = 256 tokens.

3. 256 × 128 KiB = 32 MiB. Without pooling, it would be 512 MiB.

This is the shape Gemma 3 uses. What might you lose? Fine detail, such as small text, which is why it offers pan and scan.

**More practice and sources**

9 interview questions, easy to hard · answers hidden until you click · checked 29 Oct 2026

Keep practising

Uses the methods in this track: Anatomy, Attention Variants, MoE, Scaling Laws, Training at Scale, Training Instabilities. Llama 2 figures from Touvron et al. (2023); Mixtral from Jiang et al. (2024). Part 2: Post-training and Generation.

New lessons: GPUs and memory bandwidth and Vision-Language Models.
