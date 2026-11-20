# Batch Size and Learning Rate

> You 8× the batch size. What should happen to the learning rate?

- Track: Fundamentals › Deep Learning › Training deep nets
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/batch-size-and-learning-rate/
- Before this: Gradient Descent, Momentum & Adam (`fundamentals/gradient-descent`)
- Quiz topic: `train`

## Intuition

### The situation

You have more GPUs, so you make your batches 8× bigger and keep everything else the same. Your training gets worse. The interviewer asks:

> You make the batch 8× bigger. What should happen to the learning rate?

**Running example:** training the delivery model on 32,000 orders for 2 epochs (64,000 order-visits), using the same stand-in problem as the previous lesson. You have more GPUs and want bigger batches. What happens?

#### Bigger batches mean fewer steps

With a fixed number of epochs, steps = examples ÷ B. Batch 32 gives 2,000 steps; batch 2,048 gives only 31. Each big-batch step is more accurate, but if the learning rate stays the same, 31 steps simply don't get you as far as 2,000. Bigger batches are attractive because they use parallel hardware well (wall-clock time per step barely changes), so we need a rule for adjusting the learning rate.

### The idea

Think of walking somewhere using directions from a poll. A bigger poll gives better directions, but you stop to ask far less often. If each stretch stays the same length, you won't get there. So you take longer strides, up to the point where they stop being safe.

[Figure: With a batch of 32 there are 2,000 steps over two epochs. With a batch of 2,048 there are only 31 steps.]

_From the lesson: 64,000 order-visits over two epochs._

### Play

**Try to break it.** Set a batch of 2,048 with fixed η, and read the final loss. Then try linear and square-root scaling.

#### Same data, same epochs, different batch sizes

Each point: SGD on the stand-in problem (curvatures 0.01–1, so it diverges once η > 2) for 64,000 example-visits, constant learning rate, fixed seed. Lower is better (log scale). The ring marks your selection.

With a **fixed** learning rate, the final loss climbs from **0.027** at B = 32 to **2.77** at B = 2,048: far too few steps. **Linear scaling** keeps it low much longer (0.039 at B = 128, 0.076 at B = 512), but at B = 1,024 the scaled rate is 3.2, above the stability limit of 2, and training **diverges**. **Square-root** scaling never diverges here but falls behind linear in the middle range. The point where linear scaling stops working is this problem's critical batch size: beyond it, more parallel examples per step no longer buy proportionally fewer steps.

**Now say why:** why does a more accurate gradient give a worse result unless you change the learning rate?

## Maths

### Maths

#### In one breath

A mini-batch gradient is an average over B examples, so its **noise shrinks like 1/√B**. A bigger batch gives a cleaner gradient per step but **fewer steps per epoch**. To keep making the same progress per epoch, you raise the learning rate: the **linear scaling rule** (multiply η by k when you multiply B by k) works for SGD up to a point, and needs **warmup**. Past the **critical batch size**, extra batch stops buying fewer steps: the learning rate can't grow further without going unstable, so you just waste compute. For Adam, a **square-root** rule is often closer to right. Large batches were once blamed for worse generalisation; much of that gap closes with proper learning-rate tuning and longer training. What you'll be able to do after this: predict what happens when you change the batch size, rescale the learning rate correctly, and explain the critical batch size.

#### Averaging B examples shrinks the noise

$$ {\hat{g}_B = \frac{1}{B}\sum_{i=1}^{B} \nabla \ell_i}, \qquad {\mathrm{Var}(\hat{g}_B) = \frac{\sigma^2}{B}} $$

An SGD step of size η then moves the weights by η·ĝ: its "signal" scales with η and its noise with η/√B. Doubling both B and η gives one step that moves about as far as two of the original steps with similar total noise: the intuition behind linear scaling (Goyal et al. 2017; Smith et al. 2018).

- **mini-batch gradient**: The average of B per-example gradients: an unbiased estimate of the full-data gradient.

- **its noise**: Per-example gradients vary with variance σ²; averaging B of them divides the variance by B, so the standard deviation falls like 1/√B.

#### Linear scaling, warmup and the critical batch size

- **Linear scaling rule (SGD):** multiply B by k → multiply η by k, keep other hyperparameters. Goyal et al. trained ResNet-50 on ImageNet with batch 8,192 on 256 GPUs in about an hour, matching small-batch accuracy, using this rule plus a 5-epoch **gradual warmup**; without warmup the large-batch run lost accuracy [arXiv:1706.02677](https://arxiv.org/abs/1706.02677).

- **Critical batch size:** McCandlish et al. (2018) predict it from the _gradient noise scale_ (roughly the gradient's variance over its squared size): below it, doubling B nearly halves the steps; above it, returns diminish [arXiv:1812.06162](https://arxiv.org/abs/1812.06162). The noise scale grows during training, so later phases tolerate bigger batches. Shallue et al. (2019) measured the same pattern across many models and datasets.

- **Adam:** Adam normalises the update size, so linear scaling overshoots. Analyses based on stochastic differential equations suggest a **square-root** rule (η ∝ √B) for Adam (Malladi et al., NeurIPS 2022 [arXiv:2205.10287](https://arxiv.org/abs/2205.10287)); in practice, re-tune η when you change B.

## In practice

### In practice

#### In practice

| Situation | What to do |
|---|---|
| Batch doesn't fit in GPU memory | gradient accumulation: sum gradients over k micro-batches, then step (same maths as batch k·b) |
| Scaling to more GPUs (data parallel) | global batch = per-GPU batch × GPUs; scale η (linear for SGD, ~√ for Adam) and add warmup |
| Tiny batches (1–8) | avoid BatchNorm (use LayerNorm/GroupNorm), lower η |
| LLM pre-training | batches measured in tokens (LLaMA: 4M tokens), often increased during training |

For several machines and mixed precision, see Distributed Training.

### The answer that sounds right

#### "Increase the batch, keep everything else the same"

With the learning rate fixed, a 64× bigger batch makes 64× fewer steps of the same size: training ends far from the minimum. The opposite mistake, scaling the learning rate linearly forever, eventually makes η·λ exceed 2 in the sharpest direction and training diverges. Both show up in the lab.

#### Do large batches generalise worse?

Keskar et al. (ICLR 2017) found a generalisation gap for large batches and argued that large-batch training converges to **sharp minima** while small-batch noise helps find **flat** ones [arXiv:1609.04836](https://arxiv.org/abs/1609.04836). Later work showed much of the gap came from under-tuned learning rates and too few updates: Goyal et al. found that optimisation difficulty, not generalisation, was the main issue on ImageNet, and Shallue et al. found no consistent degradation once hyperparameters were re-tuned for each batch size. Treat batch size as a speed/compute knob, and re-tune the learning rate (and warmup) whenever you change it.

## Say it

### You make the batch 8× bigger. What should happen to the learning rate?

#### The interviewer pushes further

Follow-up 1 of 3

Is gradient accumulation exactly the same as a bigger batch?

For the gradient, yes (average the micro-batch gradients). Not for BatchNorm, whose statistics still come from each micro-batch.

Follow-up 2 of 3

Why does a small batch sometimes generalise better?

Its gradient noise acts as a regulariser and may steer towards flatter minima; but with well-tuned learning rates large batches usually match it.

Follow-up 3 of 3

How would you choose a batch size?

The largest that fits memory and keeps the hardware busy, as long as it's below the critical batch size; then tune η (and warmup) for it.

#### The 30-second answer

The batch gradient averages B examples, so its noise falls like one over root B, but for a fixed number of epochs you get B times fewer steps. To keep progress per epoch, scale the learning rate: for SGD the linear scaling rule, multiply η by the same factor as B, with a warmup, which let Goyal et al. train ImageNet with batch 8k in an hour. This works up to a critical batch size, set by the gradient noise scale; beyond that, the learning rate can't grow without instability and extra batch just wastes compute. For Adam, roughly square-root scaling. The claimed large-batch generalisation gap mostly disappears with proper tuning.

**Go further**

#### What not to say

- "A bigger batch always trains faster." Only in wall-clock per step; beyond the critical batch size, total steps stop falling.

- "Linear scaling works for any batch size." It breaks past the critical batch size and without warmup.

**Key terms and sources**

What batch size changes (gradient noise, steps per epoch, hardware use), the linear scaling rule with warmup, square-root scaling for Adam, the critical batch size, and the large-batch generalisation debate · built from Goyal et al. (2017), Keskar et al. (2017), Smith et al. (2018), McCandlish et al. (2018), Shallue et al. (2019) and Malladi et al. (2022) · checked 29 Oct 2026

#### Sources

1. P. Goyal et al., "Accurate, Large Minibatch SGD: Training ImageNet in 1 Hour", [arXiv:1706.02677](https://arxiv.org/abs/1706.02677), 2017.

2. N. Keskar et al., "On Large-Batch Training for Deep Learning: Generalization Gap and Sharp Minima", ICLR 2017, [arXiv:1609.04836](https://arxiv.org/abs/1609.04836).

3. S. Smith, P.-J. Kindermans, C. Ying & Q. Le, "Don't Decay the Learning Rate, Increase the Batch Size", ICLR 2018, [arXiv:1711.00489](https://arxiv.org/abs/1711.00489).

4. S. McCandlish, J. Kaplan, D. Amodei et al., "An Empirical Model of Large-Batch Training", [arXiv:1812.06162](https://arxiv.org/abs/1812.06162), 2018.

5. C. Shallue et al., "Measuring the Effects of Data Parallelism on Neural Network Training", _JMLR_ 20, 2019, [arXiv:1811.03600](https://arxiv.org/abs/1811.03600).

6. S. Malladi, K. Lyu, A. Panigrahi & S. Arora, "On the SDEs and Scaling Rules for Adaptive Gradient Algorithms", NeurIPS 2022, [arXiv:2205.10287](https://arxiv.org/abs/2205.10287).
