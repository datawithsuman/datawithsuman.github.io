# LoRA and QLoRA: Parameter-Efficient Fine-Tuning

> How do you fine-tune an 8B model on one 24 GB GPU?

- Track: Fundamentals › LLMs › Post-training
- Type: Concept · 25 min
- Page: https://aimlrounds.com/tracks/fundamentals/lora-and-qlora/
- Before this: SFT and Instruction Tuning (`fundamentals/supervised-fine-tuning`)
- Quiz topic: `post`
- Sources checked: 2026-10-29 · Text last changed: 2026-11-20 · Version: 8b5e8de8ac

## Intuition

### The situation

The team has 20,000 good support conversations and wants the 8B assistant to follow the company's tone and format, on a single 24 GB GPU if possible. Full fine-tuning needs about 128 GB. The interviewer asks:

> How do you fine-tune an 8B model on one 24 GB GPU?

**Running example:** the team has 20,000 high-quality support conversations and wants the 8B assistant to follow the company's tone and reply format exactly, on a single 24 GB GPU if possible.

#### Full fine-tuning is heavy and brittle

Updating all 8 B weights needs multi-GPU training, produces a full 16 GB copy of the model per task, and can erase general abilities. Most behaviour changes (tone, format, a domain's style) are "small" changes to a big model; can we train only a small change?

### The idea

Think of sticky notes on a printed textbook. You don't reprint the book to change its tone. You freeze it and add a few small notes, which you can peel off or swap for another set. QLoRA also shrinks the book itself, by printing it more compactly.

[Figure: Memory for weights and optimizer with Llama 3 8B. Full fine-tuning needs 128.5 gigabytes. LoRA needs 16.7. QLoRA needs 5.1. Both fit on a 24 gigabyte GPU.]

_From the lab: weights and optimizer, with LoRA at rank 16 on all linear layers. Activations come on top._

### Play

**Try to break it.** Switch between full fine-tuning, LoRA and QLoRA. Then raise the rank to 64, and switch between attention only and all linear layers.

#### Will it fit on a 24 GB GPU?

Llama 3 8B shape (32 layers, d = 4,096, 8 KV heads, FFN 14,336). Full: 16 bytes/parameter (mixed-precision Adam). LoRA: bf16 base (2 B/param) + adapters with 16 B/param. QLoRA: NF4 base ≈ 0.55 B/param including scales. Activations, which depend on batch size and sequence length, come on top.

**Full fine-tuning** needs about **128.5 GB** for weights, gradients and Adam states: several GPUs with FSDP. **LoRA** with rank 16 on all linear layers trains **41.9 M** parameters, just **0.52%** of the model; the frozen bf16 base dominates memory at 16.7 GB, which fits a 24 GB card with room for modest activations. **QLoRA** stores the base in 4-bit and drops to about **5.1 GB**. Rank barely moves memory (r = 64 on all layers: 167.8 M parameters, 7.1 GB with QLoRA) because the adapters are tiny next to the base. The trap is assuming a bigger rank or more trainable parameters always helps: for style and format tasks, r = 8–16 is usually enough, and data quality matters far more.

**Now say why:** why does the rank barely move the memory, and what does?

## Maths

### Maths

#### In one breath

Full fine-tuning updates every weight and needs about 16 bytes per parameter of GPU memory with Adam: ~128 GB for an 8B model. **LoRA** freezes the pretrained weights and learns a small **low-rank update** for chosen matrices: W + (α/r)·B·A, where B and A have rank r (8–64). Only A and B are trained, often well under 1% of the parameters, so optimizer state shrinks to almost nothing and the adapter file is megabytes. **QLoRA** also stores the frozen base in 4-bit NF4, so an 8B model fine-tunes in a few GB and a 65B model on a single 48 GB GPU. Adapters can be merged into the weights (no inference cost) or swapped per customer on one base model. The trade-off: LoRA typically learns somewhat less than full fine-tuning on hard new skills (code, maths), but also forgets less of what the base model knew. What you'll be able to do after this: explain LoRA's maths, size LoRA and QLoRA runs, and choose rank and target modules.

#### A low-rank update to frozen weights

$$ h = {W_0}\,x + {\frac{\alpha}{r}}\,{B A}\,x, \qquad B\in\mathbb{R}^{d_{out}\times r},\; A\in\mathbb{R}^{r\times d_{in}},\; r \ll d $$

Hu et al., "LoRA: Low-Rank Adaptation of Large Language Models", ICLR 2022, [arXiv:2106.09685](https://arxiv.org/abs/2106.09685): on GPT-3 175B, 10,000× fewer trainable parameters and 3× less GPU memory than full fine-tuning, with comparable quality and no added inference latency once merged.

- **frozen pretrained weight**: d_out × d_in, never updated (and in QLoRA stored in 4-bit NF4).

- **low-rank update**: B is d_out × r and A is r × d_in. With r = 16 on a 4096 × 4096 matrix that’s 131k trainable numbers instead of 16.8M. B starts at zero, so training starts from the original model.

- **scaling**: α / r scales the update; α is often set to r or 2r so changing the rank doesn’t require retuning the learning rate.

- **QLoRA** (Dettmers et al. 2023): the frozen base is quantized to **4-bit NormalFloat**, with double quantization of the scales and paged optimizers to survive memory spikes; gradients flow through the 4-bit weights into the bf16 adapters.

- **Target modules:** attention projections only (original LoRA) or all linear layers including the FFN (now common, usually better).

## In practice

### In practice

#### What LoRA learns, and how it's served

- **Learns less, forgets less** (Biderman et al. 2024): on large-scale code and maths training, LoRA underperformed full fine-tuning, but it preserved the base model's other abilities better, acting like a regulariser. For format, tone and narrow tasks, LoRA usually matches full fine-tuning.

- **QLoRA results:** fine-tuned a 65B model on a single 48 GB GPU while matching 16-bit fine-tuning quality on the paper's benchmarks; its Guanaco models were rated close to ChatGPT on the Vicuna benchmark, which the authors themselves caution is an unreliable chatbot benchmark.

- **Variants:** DoRA splits weights into magnitude and direction for slightly better results; rsLoRA changes the scaling for high ranks.

- **Serving:** merge the adapter for a single task (zero overhead), or keep adapters separate and load many per base model (S-LoRA, vLLM multi-LoRA) for per-customer or per-task variants.

- Fine-tuning teaches _behaviour_ well and _new facts_ poorly; use RAG for knowledge (how to choose).

#### Freeze the model, learn a small low-rank change

Most task adaptation lives in a low-dimensional subspace, so training rank-r updates on frozen (even 4-bit) weights gives most of fine-tuning's benefit at a fraction of the memory, storage and risk.

### The answer that sounds right

#### "Fine-tune it on our docs so it knows them"

It sounds right, since fine-tuning changes the model. But fine-tuning teaches behaviour well and new facts poorly, so use retrieval for knowledge. LoRA isn't always as good as full fine-tuning either: on large-scale code and maths training it underperformed. For format, tone and narrow tasks, it usually matches.

## Say it

### How do you fine-tune an 8B model on one 24 GB GPU?

#### The interviewer pushes further

Follow-up 1 of 3

Why initialise B to zero?

So BA = 0 at the start and training begins exactly from the pretrained model; A is random so gradients flow.

Follow-up 2 of 3

How do you choose rank and targets?

Start with all linear layers at r = 16, α = 16–32; increase rank only if evals plateau on a hard task. Tune learning rate (higher than full fine-tuning, e.g. 1e-4 to 2e-4) and epochs (1–3) first.

Follow-up 3 of 3

Does QLoRA make the final model 4-bit?

No: the adapter is trained in bf16 on top of a 4-bit base; you can merge into a bf16 copy of the base for serving, or serve the 4-bit base plus adapter.

#### The 30-second answer

LoRA freezes the pretrained weights and learns a low-rank update B times A for selected matrices, scaled by alpha over r, with B initialised to zero. With rank 8 to 64 that's well under 1 percent of the parameters, so gradients and optimizer state are tiny; an 8B model trains in about 17 GB instead of about 128. QLoRA stores the frozen base in 4-bit NormalFloat with double quantization and paged optimizers, so even a 65B model fine-tunes on one 48 GB GPU. Adapters can be merged for zero inference overhead or served many-per-base. LoRA tends to learn a bit less than full fine-tuning on hard new skills but forgets less, and it's for behaviour and format, not for adding knowledge.

**Go further**

#### What not to say

- "LoRA is always as good as full fine-tuning." Not on large new-skill training.

- "Fine-tune it on our docs so it knows them." Use retrieval for knowledge.

**Key terms and sources**

How to fine-tune large models cheaply: LoRA's low-rank update (rank, alpha, target modules), why it needs a fraction of the memory, QLoRA's 4-bit NF4 base model, what LoRA learns and forgets compared with full fine-tuning, and serving many adapters on one base model · built from Hu et al. (LoRA, ICLR 2022), Dettmers et al. (QLoRA, NeurIPS 2023), Biderman et al. (LoRA Learns Less and Forgets Less, TMLR 2024), Liu et al. (DoRA, ICML 2024), Sheng et al. (S-LoRA, MLSys 2024) and the Hugging Face PEFT documentation · checked 29 Oct 2026

#### Sources

1. E. Hu et al., "LoRA: Low-Rank Adaptation of Large Language Models", ICLR 2022, [arXiv:2106.09685](https://arxiv.org/abs/2106.09685).

2. T. Dettmers et al., "QLoRA: Efficient Finetuning of Quantized LLMs", NeurIPS 2023, [arXiv:2305.14314](https://arxiv.org/abs/2305.14314).

3. D. Biderman et al., "LoRA Learns Less and Forgets Less", TMLR 2024, [arXiv:2405.09673](https://arxiv.org/abs/2405.09673).

4. S.-Y. Liu et al., "DoRA: Weight-Decomposed Low-Rank Adaptation", ICML 2024, [arXiv:2402.09353](https://arxiv.org/abs/2402.09353); Y. Sheng et al., "S-LoRA: Serving Thousands of Concurrent LoRA Adapters", MLSys 2024, [arXiv:2311.03285](https://arxiv.org/abs/2311.03285).

5. Hugging Face PEFT documentation (LoRA configuration, target modules).
