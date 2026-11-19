# Learning-Rate Schedules

> Why do LLMs warm up, then decay the learning rate?

- Track: Fundamentals › Deep Learning › Training deep nets
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/learning-rate-schedules/
- Before this: Gradient Descent, Momentum & Adam (`fundamentals/gradient-descent`)
- Quiz topic: `train`

## Intuition

### The situation

With one constant learning rate, your training stops improving and bounces around the minimum, and a higher rate blows up at the start. The interviewer asks:

> Why do LLMs warm up and then decay the learning rate?

**Running example:** training the delivery model for 1,000 steps with mini-batch SGD. To make the effect visible we use a small stand-in problem with the same behaviour: a 20-dimensional bowl-shaped loss (curvatures from 0.01 to 1) and noisy gradients, like the noise from sampling 32 orders per batch.

#### One learning rate can't be right for the whole run

Mini-batch gradients are noisy. With a constant learning rate η, SGD stops improving at a "noise floor" around the minimum whose height grows with η: the bigger the steps, the more it bounces. Lowering η late in training shrinks the bounce. But η can't be large at the very start either: with a quadratic of curvature λ, any step with η·λ > 2 overshoots and diverges (gradient descent), and real networks are sharpest at the beginning.

### The idea

Think of driving into a parking spot from a long way off. You start gently while you feel out the car, go at full speed on the open road, and slow right down as you reach the spot. Warmup and decay do the same for training.

[Figure: The learning rate over training rises quickly during warmup to a peak, then falls smoothly along a cosine towards a low value.]

_Illustrative. A common recipe is linear warmup, then cosine decay._

### Play

**Try to break it.** Choose the sharp start and a high peak learning rate. Compare constant with warmup + cosine, then try the others.

#### Same peak learning rate, five schedules

Top: learning rate. Bottom: loss (log scale). 1,000 noisy SGD steps on the stand-in problem, fixed seed. "Sharp at the start": curvature begins 4× higher and relaxes over the first ~150 steps, a simplified version of what Gilmer et al. measured in real networks.

With a sharp start and peak 1.0, the schedules that begin at full speed (**constant, step and cosine**) diverge in the first steps. **Warmup + cosine** starts small, survives the sharp phase, and ends at a loss of about **4.6 × 10⁻³**; one-cycle, which also starts low, reaches 1.8 × 10⁻³. Now switch to constant curvature: everything trains, but the constant schedule stalls at a loss of **0.05**, about 40× worse than cosine's 1.3 × 10⁻³, because it never lowers the noise floor. Push the peak above 2: with constant curvature every schedule diverges (η·λ > 2 at the sharpest direction): warmup can't rescue a peak that is too high for the whole run.

**Now say why:** why does the same peak rate survive with warmup but not without it?

## Maths

### Maths

#### In one breath

A big learning rate makes fast progress but, with noisy mini-batch gradients, keeps bouncing around the minimum; a small one settles precisely but crawls. So we **decay** it: large early, small late. **Step decay** drops it by 10× at fixed points, **cosine** lowers it smoothly to near zero. **Warmup** starts tiny and ramps up over the first few hundred or thousand steps, because early in training the loss surface is sharpest and a full-size step can blow up. Modern LLMs use **linear warmup then cosine decay** to about 10% of the peak; **one-cycle** ramps up and then down within a single run.What you'll be able to do after this: explain why decay lowers the final loss, why warmup prevents early divergence, and sketch the schedules used for CNNs and LLMs.

#### The common shapes

$$ \eta_t = \begin{cases} \eta_{\max}\,\dfrac{t}{W} & t < W \\[6pt] \eta_{\min} + \tfrac12(\eta_{\max}-\eta_{\min})\big(1+\cos\big(\pi\tfrac{t-W}{T-W}\big)\big) & t \ge W \end{cases} $$

Others: **step decay** (×0.1 at e.g. 50% and 75% of training, the classic ResNet recipe); **one-cycle** (ramp up for ~30%, then anneal far below the start; Smith & Topin 2018); **inverse square root** (original Transformer); **warmup-stable-decay** (hold the peak, then decay quickly at the end).

- **linear warmup**: From near 0 up to the peak over the first W steps (LLaMA: 2,000 steps).

- **cosine decay**: Then follow half a cosine from the peak down to a floor η_min, often 10% of the peak for LLMs or 0 for CNNs (Loshchilov & Hutter 2017).

#### Why a slow start helps

- **Sharp early landscape:** at initialisation the loss surface is often much sharper than later. Warmup lets training move into flatter regions while steps are still small, after which a large learning rate is stable (Gilmer et al., ICLR 2022 arXiv:2110.04369). Kalra & Barkeshli (NeurIPS 2024) find that warmup's main benefit is letting the network tolerate a larger target learning rate arXiv:2406.09405.

- **Large batches:** Goyal et al. (2017) trained ResNet-50 on ImageNet with batch size 8,192 in one hour by scaling the learning rate linearly with batch size, which only worked with a **gradual warmup** over the first 5 epochs arXiv:1706.02677 (next lesson).

- **Transformers:** post-norm transformers are especially unstable early; pre-norm reduces the need for warmup (normalisation lesson).

## In practice

### In practice

#### What real training runs use

| Setting | Schedule |
|---|---|
| ResNet on ImageNet (He et al. 2016) | SGD + momentum, η = 0.1, ÷10 when error plateaus |
| Large-batch ImageNet (Goyal et al. 2017) | linear warmup 5 epochs, then step decay |
| LLaMA pre-training (Touvron et al. 2023) | AdamW, 2,000 warmup steps, cosine decay to 10% of peak, gradient clipping 1.0 |
| Fine-tuning a pre-trained model | small peak (e.g. 1e-5 to 5e-5), short warmup, linear or cosine decay |

With Adam-type optimisers the schedule multiplies the base learning rate; Adam's per-parameter scaling does not replace the need for decay or warmup.

### The answer that sounds right

#### "Find the best constant learning rate"

Any constant η is a compromise: big enough to make progress, so too big to settle. And the peak η you'd like to use mid-training may be unstable at step 0. The lab shows both failures.

## Say it

### Why do LLMs warm up and then decay the learning rate?

#### The interviewer pushes further

Follow-up 1 of 3

How do you pick the peak learning rate?

An LR range test (increase η exponentially over a short run and pick a value somewhat below where the loss starts to blow up), or sweep a few values on a log scale on a shorter run.

Follow-up 2 of 3

Cosine vs step decay?

Similar final results in many settings; cosine needs only the total length and has no drop points to tune. Step decay is the classic ResNet recipe.

Follow-up 3 of 3

What's the risk of a schedule tied to total steps?

You must know the run length in advance; extending training means re-warming or re-decaying. Warmup-stable-decay schedules avoid this by holding the peak and decaying only at the end.

#### The 30-second answer

With noisy mini-batch gradients, a constant learning rate leaves SGD bouncing around the minimum at a level proportional to the step size, so we decay it, with step decay or a smooth cosine, to settle into a lower loss. At the start, the loss surface is usually sharpest, so a full-size step can diverge; a linear warmup over the first few hundred or thousand steps lets the model reach flatter regions before using the peak rate, and it's essential for large batches and transformers. LLMs typically use AdamW with linear warmup, cosine decay to about 10% of the peak, and gradient clipping.

**Go further**

#### What not to say

- "Adam doesn't need a schedule." Adam-trained transformers rely heavily on warmup and decay.

- "Warmup fixes any learning rate." If the peak is too high for the problem, training diverges after warmup.

**Key terms and sources**

Why the learning rate should change during training: step decay, cosine annealing, linear warmup, warmup + cosine as used for LLMs, and the one-cycle policy · built from Goyal et al. (2017), Loshchilov & Hutter (2017), Smith & Topin (2018), Gilmer et al. (2022), Kalra & Barkeshli (2024) and Touvron et al. (2023) · checked 29 Oct 2026

#### Sources

1. P. Goyal et al., "Accurate, Large Minibatch SGD: Training ImageNet in 1 Hour", arXiv:1706.02677, 2017.

2. I. Loshchilov & F. Hutter, "SGDR: Stochastic Gradient Descent with Warm Restarts", ICLR 2017, arXiv:1608.03983.

3. L. Smith & N. Topin, "Super-Convergence: Very Fast Training of Neural Networks Using Large Learning Rates", arXiv:1708.07120, 2018.

4. J. Gilmer et al., "A Loss Curvature Perspective on Training Instabilities of Deep Learning Models", ICLR 2022, arXiv:2110.04369.

5. D. Kalra & M. Barkeshli, "Why Warmup the Learning Rate? Underlying Mechanisms and Improvements", NeurIPS 2024, arXiv:2406.09405.

6. H. Touvron et al., "LLaMA: Open and Efficient Foundation Language Models", arXiv:2302.13971, 2023.
