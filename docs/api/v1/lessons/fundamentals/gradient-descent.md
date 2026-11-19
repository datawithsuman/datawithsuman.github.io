# Gradient Descent, Momentum & Adam

> Why does a slightly bigger learning rate make training explode?

- Track: Fundamentals › Maths for ML › Calculus and optimisation
- Type: Concept · 25 min
- Page: https://aimlrounds.com/tracks/fundamentals/gradient-descent/
- Before this: Derivatives, Gradients & the Chain Rule (`fundamentals/derivatives-and-chain-rule`)
- Quiz topic: `calc`

## Intuition

### The situation

Someone raises the learning rate slightly, and your training loss explodes to NaN. The interviewer asks:

> Why can a larger learning rate make training diverge, and how do momentum and Adam help?

**Running example:** training two weights of a delivery-time model whose loss is a narrow valley: L(θ) = ½(θ₁² + 10 θ₂²). It's 10 times steeper in θ₂ than in θ₁ (curvatures 1 and 10), the shape you get when features have very different scales. Every run starts at (−4, 2); "converged" means the loss drops below 0.0001.

#### Minimising a loss you can't solve on paper

Linear regression has a formula for the best weights; neural networks, logistic regression and most models don't. What we can always compute is the gradient (previous lesson): the uphill direction. Gradient descent turns that into an algorithm. The art is the step size and how to deal with valleys of very different steepness.

### The idea

Think of walking down a narrow valley in fog. You can only feel the slope under your feet. Take steps that are too big and you bounce from wall to wall, climbing higher each time. Momentum is like a heavy ball that keeps rolling along the valley floor, and Adam adjusts your stride to the steepness in each direction.

[Figure: Oval contour lines of a narrow valley, with a path that zig-zags from wall to wall as it moves towards the centre.]

_Illustrative. Plain gradient descent zig-zags across a valley that's much steeper in one direction than the other._

### Play

**Try to break it.** Choose gradient descent with η = 0.19, then move to η = 0.21. Then try momentum and Adam at 0.21.

#### Same valley, three optimisers

Contours of L = ½(θ₁² + 10θ₂²). Start (−4, 2), minimum at the centre.

| η | 0.01 | 0.05 | 0.1 | 0.19 | 0.21 | 0.3 | 0.5 |
|---|---|---|---|---|---|---|---|
| Gradient descent | > 200 | 111 | 54 | 58 | diverges | diverges | diverges |
| Momentum | 93 | 78 | 103 | 117 | 96 | 112 | diverges |
| Adam | > 200 | 179 | 105 | 84 | 79 | 99 | 85 |

Steps to reach loss < 0.0001. Plain gradient descent is fastest at a well-chosen η but fails completely beyond 0.2. Momentum is stable over a wider range (it diverges only at 0.5 here) and is much better at small η (93 steps vs never). Adam converges for every η from 0.05 to 0.5 because its step size is normalised per parameter: the steep θ₂ and shallow θ₁ directions move at similar speeds. Its weakness shows at η = 0.01: steps are about η in size, so it crawls from 4 units away.

**Now say why:** why does such a small change blow up plain gradient descent, while the other two still converge?

## Maths

### Maths

#### In one breath

**Gradient descent** repeats one step: θ ← θ − η∇L(θ), walking downhill on the loss. The **learning rate** η is everything: too small crawls, too large overshoots and **diverges** (for a quadratic, beyond 2/λmax, where λmax is the steepest curvature). When the loss is a long, narrow valley (**ill-conditioned**), plain gradient descent zig-zags across it. **Momentum** keeps a running velocity so consistent directions build up speed and oscillations cancel. **Adam** also divides each parameter's step by a running estimate of its gradient size, so every direction moves at a similar pace, which makes it robust to the learning rate. In practice gradients come from small random **mini-batches** (SGD), which adds noise.What you'll be able to do after this: write the update rules for GD, momentum and Adam, explain divergence and the 2/λ rule, explain why momentum and Adam help on narrow valleys, and pick a learning rate sensibly.

#### The update rule

$$ \theta_{t+1} = \theta_t - \eta\,\nabla L(\theta_t) $$

Goodfellow et al. §4.3; MML §7.1.

- **new parameters**: Where the weights go after one step.

- **current parameters**: Where they are now.

- **learning rate**: η: how big a step to take. The most important hyperparameter in deep learning.

- **gradient**: Uphill direction; subtracting it goes downhill. Steeper slope → bigger step.

#### Three optimisers

| Optimiser | Update | Idea |
|---|---|---|
| **(S)GD** | θ ← θ − η g | Step against the (mini-batch) gradient |
| **Momentum** | v ← β v + g; θ ← θ − η v | Velocity accumulates consistent directions, damps oscillation (β ≈ 0.9) |
| **Adam** | m ← β₁m + (1 − β₁)g; v ← β₂v + (1 − β₂)g²; θ ← θ − η m̂ / (√v̂ + ε) | Momentum plus per-parameter step scaling by recent gradient size; bias-corrected |

Adam's update and defaults (η = 0.001, β₁ = 0.9, β₂ = 0.999, ε = 10⁻⁸) are from Kingma & Ba, Algorithm 1 p. 2, who describe the effective step as "approximately bounded by the stepsize hyperparameter" and invariant to rescaling the gradient.

#### Why plain gradient descent zig-zags

The ratio of steepest to shallowest curvature is the **condition number** (here 10). Gradient descent's best learning rate is limited by the steep direction, so progress along the shallow direction is slow, and in between it bounces from wall to wall. Fixes: **scale your features** (often the cause of ill-conditioning; see Feature Scaling), use **momentum** (bounces cancel, the valley direction accumulates), use **adaptive methods** like Adam (rescale each direction), and use **normalisation layers** in networks.

#### Nesterov, AdaGrad and RMSProp: how Adam came about

| Method | What it adds | Limitation |
|---|---|---|
| **Momentum** | Keeps a running average of past gradients, which smooths zig-zags. | Can overshoot. |
| **Nesterov** | Measures the gradient at the point momentum is about to reach, so it can correct earlier. | A small change in practice for noisy gradients. |
| **AdaGrad** | Divides each weight's step by the root of its summed squared gradients, which suits rare features. | The sum only grows, so steps can shrink too far. |
| **RMSProp** | Uses a decaying average instead of a sum, so old gradients are forgotten. | No momentum term. |
| **Adam** | Combines momentum with RMSProp's scaling, and corrects for starting at zero. | Can generalise less well in some settings. See AdamW. |

These per-weight scales use squared gradients, not true curvature. For that, see Newton's method.

## In practice

### In practice

#### Mini-batches, schedules and warm-up

- **Stochastic gradient descent:** estimate the gradient from a mini-batch (e.g. 32–4,096 examples) instead of the whole dataset. Much cheaper per step; the noise can even help escape poor regions.

- **Learning-rate schedules:** start larger, decay later (step, cosine, linear decay) so early progress is fast and late steps settle.

- **Warm-up:** start from a small η and ramp up over the first steps; common for Transformers, where Adam's early estimates are noisy.

- **AdamW:** Adam with decoupled weight decay (Loshchilov & Hutter, 2019), the standard for training large language models.

#### Recipe

1. Scale inputs; use sensible initialisation.

2. Start with Adam/AdamW (η ≈ 1e-3 for small nets, smaller for big ones) or SGD + momentum (η ≈ 0.1 with schedules, common for vision).

3. Run a learning-rate range test or a coarse log-scale search (Hyperparameter Tuning).

4. If the loss explodes or turns NaN: lower η, add warm-up or gradient clipping.

5. If it plateaus: decay η, check data and scaling.

### The answer that sounds right

#### "Bigger learning rate, faster training"

Along a direction with curvature λ, one gradient step multiplies the distance to the minimum by (1 − ηλ). If η > 2/λ, that factor is below −1: each step overshoots further than the last, and the loss explodes. The steepest direction sets the limit: here λmax = 10, so any η above **0.2** diverges, while the shallow direction (λ = 1) would happily take steps 10× bigger. With η = 0.21, plain gradient descent blows up to a loss of about 10¹⁷ in 200 steps; with η = 0.1 it converges in 54.

## Say it

### Why can a larger learning rate make training diverge, and how do momentum and Adam help?

#### The interviewer pushes further

Follow-up 1 of 3

Why does Adam need bias correction?

m and v start at zero, so early averages are biased towards zero, most strongly when β₂ is close to 1; dividing by (1 − βᵗ) corrects it. Without it, early steps can be far too large (Kingma & Ba §3, §6.4).

Follow-up 2 of 3

SGD vs Adam: which generalises better?

An active debate: well-tuned SGD with momentum is often preferred for image classification; Adam/AdamW dominates Transformers and LLMs. Tune both if it matters.

Follow-up 3 of 3

What batch size?

Larger batches give less noisy gradients and better hardware use but need larger learning rates (often scaled roughly linearly) and warm-up; very large batches can hurt generalisation.

#### The 30-second answer

Gradient descent updates parameters by subtracting the learning rate times the gradient. The learning rate must be below about 2 over the largest curvature or it diverges, and when curvatures differ a lot, an ill-conditioned problem, plain GD zig-zags and crawls along the shallow direction. Momentum averages gradients into a velocity, which damps oscillation and accelerates consistent directions. Adam combines momentum with per-parameter scaling by a running RMS of the gradient, plus bias correction, so it's robust to learning-rate choice and gradient scale. In practice we use mini-batch SGD or AdamW with learning-rate schedules, warm-up and clipping.

**Go further**

#### What not to say

- "A higher learning rate always trains faster." Past 2/λmax it diverges.

- "Adam needs no tuning." Its learning rate still matters a lot.

**Key terms and sources**

The update rule, the learning rate and when it diverges, ill-conditioning and zig-zags, mini-batch SGD, momentum, and Adam's adaptive step sizes · built from Goodfellow et al., _Deep Learning_ (ch. 4, 8), Deisenroth et al., _MML_ (ch. 7) and Kingma & Ba, "Adam" (2015) · checked 28 Oct 2026

#### Key terms

| Term | Meaning |
|---|---|
| **Learning rate η** | Step size multiplier. |
| **Divergence** | Loss grows each step; for quadratics when η > 2/λmax. |
| **Condition number** | λmax/λmin of the curvature (Hessian). |
| **Momentum** | Exponentially averaged gradient used as velocity. |
| **Adam** | Momentum + per-parameter scaling by RMS gradient, bias-corrected. |
| **SGD** | Gradient estimated from a random mini-batch. |

#### Sources

1. D. Kingma & J. Ba, "Adam: a method for stochastic optimization", ICLR 2015, arXiv:1412.6980.

2. I. Goodfellow, Y. Bengio & A. Courville, _Deep Learning_, MIT Press 2016, ch. 4 and 8, deeplearningbook.org.

3. M. P. Deisenroth, A. A. Faisal & C. S. Ong, _Mathematics for Machine Learning_, CUP 2020, ch. 7.

4. I. Loshchilov & F. Hutter, "Decoupled weight decay regularization", ICLR 2019, arXiv:1711.05101.

The optimisers run live in your browser on the quadratic above.
