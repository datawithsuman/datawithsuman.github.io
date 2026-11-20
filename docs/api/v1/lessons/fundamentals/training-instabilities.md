# Training Instabilities: Loss Spikes, z-loss and QK-norm

> Your loss spikes at step 40k. What happened, and what do you do?

- Track: Fundamentals › LLMs › Pretraining
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/training-instabilities/
- Before this: The Next-Token Objective (`fundamentals/next-token-prediction`), BatchNorm vs LayerNorm vs RMSNorm (`fundamentals/normalisation-layers`)
- Quiz topic: `pre`

## Intuition

### The situation

Three weeks into continued pre-training of the assistant, the loss jumps from 2.1 to 7 in a few hundred steps. Each restart costs days of compute. The interviewer asks:

> Your loss spikes at step 40k. What happened, and what do you do?

**Running example:** three weeks into continued pre-training of the assistant on food and support text, the loss jumps from 2.1 to 7 in a few hundred steps. What happened, and what do you do?

#### Spikes, divergence and broken hardware

A **loss spike** is a sudden jump in training loss; sometimes it recovers, sometimes the run **diverges** and never comes back. PaLM's authors found that replaying the same batches from an earlier checkpoint did _not_ reproduce the spike: spikes came from a combination of particular data and a particular parameter state. Spikes get more frequent with larger models and higher learning rates, and every restart costs days of compute.

### The idea

Think of a shop calculator that keeps only a few significant digits. Add 300 to every price, and on paper the differences haven't changed. But the calculator starts rounding, and two different prices read the same. The loss can't see this drift, so nothing stops it.

[Figure: Cross-entropy with drifting logits. The exact loss stays at 0.4496. Computed from bf16 logits, it reads 0.4600 at drift 50, 0.5174 at drift 200 and 0.2974 at drift 300.]

_From the lab. The model's predictions haven't changed, but the computed loss has._

### Play

**Try to break it.** Drag the logit drift from 0 up to 300. Compare the exact loss, the loss from bf16 logits and the z-loss penalty.

#### "The softmax is shift-invariant, so drift is harmless"

Logits [3, 1.5, 1.2, 0.4, 0, −0.5, −1, −2] over 8 candidate tokens, the first one correct, plus drift c. bf16 rounding to 8 significant bits; softmax then computed exactly.

The exact loss is **0.4496** at every drift: the model's predictions haven't changed. But computed from bf16 logits, the loss is already off at drift 50 (0.4600), wrong by 0.07 at drift **200** (0.5174), and at **300** it reads 0.2974: logits that differed by 0.3 now round to the same value, so the gradients point the wrong way. The **z-loss** term sees what cross-entropy can't: it grows from 0.0012 to **9.21** at drift 300 and pushes log Z back towards 0, keeping logits in the range where bf16 is precise.

**Now say why:** if the softmax doesn't change when you shift every logit, why isn't drift harmless?

## Maths

### Maths

#### In one breath

Big runs are fragile. PaLM 540B saw about **20 loss spikes**; OPT-175B needed dozens of manual restarts. Two well-understood failure modes are **output-logit divergence**, where all logits drift to large values (the softmax doesn't care, but low-precision numbers do), and **attention-logit growth**, where query–key dot products blow up and attention collapses onto one token. **z-loss** adds a small penalty 10−4·(log Z)² that keeps the softmax normaliser near 1; **QK-norm** normalises queries and keys before the dot product. Add learning-rate warm-up, gradient clipping, pre-norm, and data cleaning, and when a spike happens anyway, roll back to a checkpoint and skip the offending batches. At 16,000 GPUs, hardware fails too: Llama 3 405B had 466 job interruptions in 54 days. What you'll be able to do after this: diagnose loss spikes, explain z-loss and QK-norm, and describe how large runs recover.

#### Two logit problems

- **Output-logit divergence:** adding the same constant c to every output logit doesn't change the softmax, so cross-entropy gives no signal to stop the logits drifting. But in bf16, which keeps only 8 bits of mantissa, large logits lose precision, so the computed loss and gradients become wrong.

- **Attention-logit growth:** query and key norms grow during training; the dot products become huge, the attention softmax becomes one-hot, and gradients through it vanish or explode. Dehghani et al. saw this when scaling ViT to 22B; Wortsman et al. (2024) reproduced both instabilities in small models trained with high learning rates.

$$ \mathcal{L} = {\mathcal{L}_{CE}} + {10^{-4}}\cdot{\log^2 Z}, \qquad \mathrm{QKNorm:}\;\; s_{ij} = \frac{\mathrm{Norm}(q_i)\cdot \mathrm{Norm}(k_j)}{\sqrt{d}} $$

Chowdhery et al., "PaLM", [arXiv:2204.02311](https://arxiv.org/abs/2204.02311), §5; QK-norm: Dehghani et al., "Scaling Vision Transformers to 22 Billion Parameters", ICML 2023, [arXiv:2302.05442](https://arxiv.org/abs/2302.05442).

- **cross-entropy**: The usual next-token loss.

- **log of the softmax normaliser**: log Z = log Σ exp(logits). It equals the logits’ overall level, which cross-entropy ignores.

- **tiny weight**: 10⁻⁴ in PaLM: enough to pull log Z towards 0 without affecting predictions.

## In practice

### In practice

#### The stability toolkit

- **Architecture:** pre-norm (Anatomy), QK-norm (OLMo 2, Qwen3, Gemma 3), norms after sub-layer outputs (OLMo 2's "reordered norm"), no biases, careful initialisation.

- **Optimisation:** learning-rate warm-up, gradient clipping (global norm 1.0 is common), lower peak learning rates for bigger models, z-loss; watch gradient norms and attention-logit maxima, not just the loss.

- **Data:** OLMo 2 traced spikes to documents with long repeated n-gram sequences and filtered them out.

- **Recovery:** PaLM restarted from a checkpoint about 100 steps before each spike and skipped about 200–500 data batches; OPT-175B logged dozens of restarts and lowered the learning rate mid-run.

- **Hardware:** in 54 days of Llama 3 405B pre-training there were 466 job interruptions, 419 of them unexpected, mostly GPU and memory faults; frequent checkpointing and automated restarts kept effective training time above 90%.

#### Keep every logit in a well-conditioned range

Most instabilities come from quantities the loss doesn't control, like the overall level of output logits and the size of attention logits, growing until low precision or a saturated softmax breaks the gradients; small regularisers and normalisations keep them bounded, and checkpoints handle the rest.

### The answer that sounds right

#### "Spikes are always bad data"

It sounds right, since the spike appears at a particular batch. But PaLM's authors replayed the same batches from an earlier checkpoint and the spike didn't come back. It took particular data and a particular parameter state together. "Just lower the learning rate" isn't the full answer either: it helps, but it slows training, so fix the cause.

## Say it

### Your loss spikes at step 40k. What happened, and what do you do?

#### The interviewer pushes further

Follow-up 1 of 3

Your loss spikes at step 40k. First steps?

Check gradient norm and attention/output logit maxima just before the spike, inspect the batch, roll back to a checkpoint ~100 steps earlier, skip the next few hundred batches or lower the learning rate, and consider z-loss or QK-norm for the next run.

Follow-up 2 of 3

Why does a spike sometimes recover on its own?

Adam's second-moment estimates adapt and the model can return to a stable region, but with lasting damage or, at worst, divergence.

Follow-up 3 of 3

Can you study instabilities without a huge run?

Yes: Wortsman et al. reproduced attention-logit growth and output-logit divergence in small models at high learning rates, and showed QK-layernorm and z-loss fix them there too.

#### The 30-second answer

Large runs suffer loss spikes and divergence, often from logits growing out of control: output logits can drift because softmax is shift-invariant, which breaks bf16 precision, and attention logits can grow until attention becomes one-hot. Defences are z-loss, a 1e-4 penalty on log Z squared that keeps the softmax normaliser near one, QK-norm on queries and keys, pre-norm and extra norms, warm-up, gradient clipping and lower learning rates, plus data cleaning. When a spike happens, you roll back to an earlier checkpoint and skip the batches around it, as PaLM did, and at large scale you also need frequent checkpoints and automatic restarts for hardware failures.

**Go further**

#### What not to say

- "Spikes are always bad data." PaLM found they depended on data and parameter state together.

- "Just lower the learning rate." It helps but slows training; fix the cause.

**Key terms and sources**

What goes wrong in long LLM training runs: sudden loss spikes and divergence, growing output and attention logits, low-precision round-off, and hardware failures; and the standard defences: warm-up, gradient clipping, z-loss, QK-norm, careful norm placement, data fixes, and checkpoint-and-skip recovery · built from Chowdhery et al. (PaLM, 2022), Zhang et al. (OPT, 2022), Dehghani et al. (ViT-22B, 2023), Wortsman et al. (Small-scale proxies, ICLR 2024), Team OLMo (OLMo 2, 2024) and Meta's Llama 3 report (2024) · checked 29 Oct 2026

#### Sources

1. A. Chowdhery et al., "PaLM: Scaling Language Modeling with Pathways", 2022, [arXiv:2204.02311](https://arxiv.org/abs/2204.02311).

2. S. Zhang et al., "OPT: Open Pre-trained Transformer Language Models", 2022, [arXiv:2205.01068](https://arxiv.org/abs/2205.01068).

3. M. Dehghani et al., "Scaling Vision Transformers to 22 Billion Parameters", ICML 2023, [arXiv:2302.05442](https://arxiv.org/abs/2302.05442); M. Wortsman et al., "Small-scale proxies for large-scale Transformer training instabilities", ICLR 2024, [arXiv:2309.14322](https://arxiv.org/abs/2309.14322).

4. Team OLMo, "2 OLMo 2 Furious", 2024, [arXiv:2501.00656](https://arxiv.org/abs/2501.00656).

5. Llama Team, Meta, "The Llama 3 Herd of Models", 2024, [arXiv:2407.21783](https://arxiv.org/abs/2407.21783) (§3.3.4, reliability).
