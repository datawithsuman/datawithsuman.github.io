# Comparing Distributions: KL, Jensen-Shannon and Wasserstein

> How do KL divergence, Jensen-Shannon and Wasserstein distance differ, and when would you use each?

- Track: Fundamentals › Maths for ML › Information theory
- Type: Concept · 15 min
- Page: https://aimlrounds.com/tracks/fundamentals/comparing-distributions/
- Before this: Entropy, Cross-Entropy & KL Divergence (`fundamentals/entropy-cross-entropy-kl`)
- Related: GANs (`fundamentals/gans`)
- Quiz topic: `info`

## Intuition

### The situation

Your GAN's generator isn't improving, and its loss barely moves. A drift monitor using KL divergence is reporting infinity for one feature. A colleague also asks why KL isn't simply called a distance. The interviewer asks:

> How do KL divergence, Jensen-Shannon and Wasserstein distance differ, and when would you use each?

#### Why it matters

Training, generative models and drift monitoring all compare distributions, and the measure you pick changes the result. A popular interview question is why KL isn't a distance. This builds on KL divergence.

### The idea

Think of two piles of earth. KL asks how surprised you'd be, expecting one pile while seeing the other, and an empty spot makes you infinitely surprised. Jensen-Shannon asks how much the piles overlap, so far-apart piles all look equally different. Wasserstein asks how far you'd have to move the earth.

[Figure: Three measures. KL is asymmetric and can be infinite. Jensen-Shannon is symmetric but saturates. Wasserstein keeps growing with distance.]

_The right choice depends on what you need when distributions barely overlap._

### Play

**Try to break it.** Move the distance from 6 to 12. Then set it to 0, with spreads of 1 and 2.

#### Move two distributions apart

Illustrative Gaussians. KL uses the exact formula. Jensen-Shannon and Wasserstein are computed numerically on a fine grid.

Move the distance from **6** to **12**. JS barely changes, as it's already near its limit of 1. It can't tell you they're moving further apart, while Wasserstein doubles. Now set distance to 0, with spreads of **1** and **2**, and the two KL numbers differ: it's asymmetric.

**Now say why:** why can't Jensen-Shannon tell you they've moved further apart?

## Maths

### Maths

#### In one breath

**KL divergence** is asymmetric, and blows up when one distribution has mass where the other has none. **Jensen-Shannon** is symmetric and bounded, but it saturates once distributions stop overlapping. **Wasserstein**, or earth mover's distance, measures how far mass has to move, so it keeps growing with distance, which gives useful gradients. Choose by what you need: MLE and VAEs use KL, the first GANs were tied to JS, and WGANs use Wasserstein.

#### Four ways to compare

| Measure | Symmetric? | If they don't overlap | Used for |
|---|---|---|---|
| **KL** | No | Infinite | MLE, VAEs, distillation |
| **Jensen-Shannon** | Yes | Stuck at 1 bit | Original GANs, drift checks |
| **Wasserstein** | Yes | Keeps growing with distance | WGANs, drift checks |
| **PSI** | Yes | Infinite without smoothing | Monitoring binned features |

##### Forward or reverse KL?

Say you fit a simple q to a complicated p with two peaks.

- **Forward, KL(p ‖ q):** q is punished for having no mass where p does, so it spreads to cover both peaks. This is what maximum likelihood does.

- **Reverse, KL(q ‖ p):** q is punished for having mass where p doesn't, so it locks onto one peak. Variational inference, as in VAEs, uses this one.

##### Why Jensen-Shannon is bounded

It averages each distribution's KL to their midpoint, m = (p + q) ÷ 2. The midpoint always has mass wherever p or q do, so it can't blow up. It tops out at 1 bit, however far apart they get.

##### Why Wasserstein helped GANs

Think of each distribution as a pile of earth. Wasserstein is the least work to reshape one into the other. Early in GAN training, real and fake data often barely overlap. JS is then stuck near its maximum, and gives little gradient. Wasserstein still reports how far away the fake data is, so the generator gets a useful signal.

##### Monitoring drift

**PSI** bins a feature, and compares shares. It's simply KL in both directions added together. **JS** and **Wasserstein** are common alternatives. Wasserstein accounts for how far values moved, while JS and PSI only compare overlap between bins. See drift detection.

#### The maths

$$ {D_{KL}(p \| q)} = \sum_x p(x) \log \frac{p(x)}{q(x)}, \qquad {JS(p, q)} = \tfrac{1}{2} D_{KL}(p \| m) + \tfrac{1}{2} D_{KL}(q \| m), \qquad {W_1(p, q)} = \int |F_p(x) - F_q(x)|\, dx $$

Worked example: two Gaussians with the same spread of 1, and 2 apart. KL = 2 nats, or about 2.89 bits, JS ≈ 0.49 bits and Wasserstein = 2.

- **KL divergence**: Weighted by p, and it’s infinite if q is zero where p isn’t. It isn’t a true distance, as it’s asymmetric and breaks the triangle inequality.

- **Jensen-Shannon**: Uses the midpoint m, which makes it symmetric and bounded. Its square root is a true distance.

- **Wasserstein**: In one dimension, it’s the area between the two CDFs. It accounts for how far mass has to move.

## In practice

### In practice

#### In practice

- **Zeros break KL:** a single empty bin gives infinity. Add smoothing, or use JS for monitoring.

- **Check your direction:** KL(p ‖ q) and KL(q ‖ p) answer different questions, and libraries can differ in which they compute.

- **High dimensions:** these get hard to estimate from samples. Monitoring often compares one feature at a time, or uses a model's embeddings.

- **Choose thresholds on your data:** rules of thumb for PSI exist, but look at what really affected your model's performance.

- **Exact Wasserstein is costly:** outside one dimension, it's an optimisation problem, so approximations such as Sinkhorn or critics are used.

### The answer that sounds right

#### "KL divergence is the distance between two distributions"

It sounds right, as it's zero when they match, and it grows as they differ. But KL(p ‖ q) and KL(q ‖ p) can be very different, and it fails the triangle inequality. It's really the extra cost of assuming q when the truth is p. If you need a true distance, use Wasserstein, or the square root of Jensen-Shannon.

## Say it

### How do KL divergence, Jensen-Shannon and Wasserstein distance differ, and when would you use each?

#### The interviewer pushes further

Follow-up 1 of 3

Why isn't KL divergence a true distance?

It isn't symmetric, so KL(p ‖ q) can differ from KL(q ‖ p), and it doesn't satisfy the triangle inequality. It's better understood as the extra cost of using q when the truth is p. Jensen-Shannon's square root, by contrast, is a true distance.

Follow-up 2 of 3

Why does minimising cross-entropy use forward KL, and what does that do?

The data comes from p, so the average is taken over p, and minimising cross-entropy equals minimising KL(p ‖ q). If q gives low probability to something that really occurs, the penalty is huge. So models try to cover all the data, which can make them overly spread out when they can't fit it exactly.

Follow-up 3 of 3

Why did Wasserstein help GAN training?

Early on, real and generated data can barely overlap. JS then sits near its maximum, so it barely changes as the generator improves, and gradients are unhelpful. Wasserstein still reflects how far apart they are. It needs the critic to be limited, which WGAN first did by clipping weights, and then with a gradient penalty.

#### The 30-second answer

KL divergence is asymmetric, and goes to infinity if q has no mass where p does, so it isn't a true distance. Forward KL makes q cover all of p, as in MLE. Reverse KL makes q stay within p, as in VAEs. Jensen-Shannon compares both to their midpoint, so it's symmetric and bounded at one bit, but it saturates when distributions don't overlap. Wasserstein measures how far mass must move, so it keeps growing, which gives WGANs useful gradients. PSI, used for drift, is the two KLs added together.

**Key terms and sources**

Forward and reverse KL, Jensen-Shannon, Wasserstein distance and PSI, what each does when distributions don't overlap, and where they appear in VAEs, GANs and drift monitoring. · checked 6 Nov 2026

#### Sources

- [Murphy, Probabilistic Machine Learning: An Introduction, chapter 6](https://probml.github.io/pml-book/book1.html)

- [Arjovsky, Chintala and Bottou, Wasserstein GAN (2017)](https://arxiv.org/abs/1701.07875)

- [Goodfellow et al., Generative Adversarial Nets (2014)](https://arxiv.org/abs/1406.2661)

- GANs on this site

Explanations are ours, built from these sources. Lab numbers are illustrative, and worked examples were checked by calculation.
