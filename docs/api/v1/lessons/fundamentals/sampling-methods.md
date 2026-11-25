# Sampling Methods: Inverse Transform, Importance Sampling and MCMC

> How do you draw samples from a hard distribution, and when would you use importance sampling or MCMC?

- Track: Fundamentals › Maths for ML › Probability
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/sampling-methods/
- Before this: Markov Chains (`fundamentals/markov-chains`), Integrals for ML (`fundamentals/integrals-for-ml`)
- Quiz topic: `prob`
- Sources checked: 2026-11-06 · Text last changed: 2026-11-20 · Version: 0d1c853b58

## Intuition

### The situation

You're evaluating a rare failure that happens about 3 times in 100,000. Simple simulation almost never sees one. Separately, you need samples from a Bayesian posterior, whose normalising constant you can't compute. The interviewer asks:

> How do you draw samples from a hard distribution, and when would you use importance sampling or MCMC?

#### Why it matters

Monte Carlo needs samples, as in Integrals for ML. These are the standard ways of getting them. They also appear in LLM decoding, off-policy evaluation, Bayesian inference and diffusion models.

### The idea

Think of surveying a rare group. Knocking on random doors finds almost nobody, so you go where they are, then correct for having looked there. That's importance sampling. MCMC is more like a wanderer told to linger longer in nicer places: over time, where they've been shows you the whole map.

[Figure: Three methods. Inverse transform uses a known inverse CDF. Importance sampling reweights samples from an easier distribution. MCMC walks, using only ratios.]

_Choose by what you know about the distribution._

### Play

**Try to break it.** Raise a to 5, and compare the estimates. Then try step sizes of 0.05 and 30.

#### Rare events and random walks

Our seeded simulation. The target is a standard Normal in both parts. Importance sampling proposes from a Normal centred on a. Effective samples use the lag-1 correlation only, a rough estimate of (1 − c)/(1 + c).

Try a Metropolis step size of **0.05**: nearly every move is accepted, yet the walk hardly goes anywhere. Try **30**: it rarely moves at all. A high acceptance rate isn't the goal. Mixing is.

**Now say why:** why isn't a very high acceptance rate good?

## Maths

### Maths

#### In one breath

Computers produce uniform random numbers, and we need samples from other distributions. **Inverse transform** passes a uniform value through the inverse CDF, if you know it. **Rejection sampling** proposes and throws some away. **Importance sampling** keeps every sample and reweights it, which is ideal for rare events. **MCMC** builds a Markov chain that spends time in each place in proportion to its probability, and it only needs the distribution **up to a constant**. That's what makes hard Bayesian models possible.

#### Four methods

| Method | Idea | Needs | Weakness |
|---|---|---|---|
| **Inverse transform** | Take u from a uniform, and return F⁻¹(u). | The inverse CDF | Rarely available in many dimensions. |
| **Rejection** | Propose from an easy shape above the target. Keep with chance p/(Mq). | A bound M | Rejects nearly everything in high dimensions. |
| **Importance** | Sample from q, and weight each sample by p/q. | A good q | A poor q gives a few huge weights. |
| **MCMC** | A random walk with a rule to accept or reject moves. | p up to a constant | Samples are correlated, and it can be slow. |

##### Metropolis-Hastings

1. From the current point x, propose a nearby x′.

2. Compute the ratio p(x′) / p(x). The unknown normalising constant cancels, and that's the key insight.

3. Accept with chance min(1, ratio). Otherwise, stay put, and count x again.

Uphill moves are always accepted. Downhill moves sometimes are, so it explores the whole distribution, and doesn't only climb to a peak. Over time, visits match p.

##### Spotting failure

- **Step size:** too small, and everything is accepted, while the chain barely moves. Too large, and nearly everything is rejected.

- **Burn-in:** discard early samples, before the chain has reached the target.

- **Correlated samples:** 10,000 correlated samples may hold far less information than that. Report the effective sample size.

- **Multiple peaks:** a chain can get stuck on one. Start several from different points, and compare.

##### Where you'll see these

- **LLM decoding:** top-k and top-p sampling draw from a categorical distribution.

- **Off-policy evaluation:** importance weights correct logged data for a new policy.

- **Diffusion models:** their samplers follow a process related to Langevin MCMC.

#### The maths

$$ {\mathbb{E}_p[f(x)]} = \mathbb{E}_q\!\left[f(x)\,{\frac{p(x)}{q(x)}}\right], \qquad {A(x \to x') = \min\!\left(1,\; \frac{\tilde p(x')\,q(x \mid x')}{\tilde p(x)\,q(x' \mid x)}\right)} $$

Worked example: for a Normal variable, P(X > 4) is about 0.00003. Plain sampling needs millions of draws to see it often. Sampling near 4 and reweighting takes far fewer.

- **importance sampling**: Rewrite an average under p as an average under an easier q.

- **the weight**: Corrects for sampling from the wrong distribution. Regions q over-samples are weighted down.

- **acceptance rule**: The Metropolis-Hastings chance of moving. p̃ needs only be known up to a constant, as it cancels. With a symmetric proposal, the q terms cancel too.

## In practice

### In practice

#### In practice

- **Use a library:** samplers like NUTS, a form of Hamiltonian Monte Carlo, tune themselves, and they handle many dimensions far better than plain Metropolis.

- **Check importance weights:** if a few samples hold most of the total weight, your estimate is unreliable, however many samples you have. Effective sample size shows this.

- **Off-policy care:** in logged data, a new policy may favour actions rarely logged. Weights become large, so clip them, or use a doubly robust method.

- **Choose by need:** sampling for accuracy, and variational methods for speed at scale.

### The answer that sounds right

#### "I'll just take more samples"

It sounds right, and for ordinary averages, it often works. But for an event with a chance of 3 in 100,000, you'd need millions of samples to see it enough times. In MCMC, more samples from a stuck chain only repeat the same region. Fix the method first: use a better proposal.

## Say it

### How do you draw samples from a hard distribution, and when would you use importance sampling or MCMC?

#### The interviewer pushes further

Follow-up 1 of 3

Why doesn't MCMC need the normalising constant?

The acceptance rule uses a ratio of p at two points, and the constant appears on the top and the bottom, so it cancels. That's the point of the method, since in Bayesian inference, the posterior's constant is exactly the intractable integral.

Follow-up 2 of 3

How would you estimate a very rare event's probability?

Plain sampling almost never sees it, so the estimate is zero or very noisy. Use importance sampling: propose from a distribution centred on the rare region, then reweight each hit by p/q. The estimate stays unbiased with far lower variance, if q is well chosen.

Follow-up 3 of 3

What's the best acceptance rate for Metropolis?

It isn't 100%. Very high acceptance usually means tiny steps, and a walk that explores slowly. A known rule of thumb for many-dimensional Gaussian targets is about 23%, and somewhat higher for low dimensions. In practice, look at effective sample size rather than acceptance alone.

#### The 30-second answer

For a simple distribution with a known inverse CDF, I'd use inverse transform. For rare events, I'd use importance sampling: sample from a distribution that hits the region, and reweight by p over q. For hard distributions known only up to a constant, I'd use MCMC. Metropolis-Hastings proposes a move, and accepts with chance min of 1 and the ratio, so the constant cancels. I'd tune the step size, discard burn-in, and check effective sample size, because samples are correlated. Multiple chains help detect stuck ones.

**Key terms and sources**

How computers sample: inverse transform, rejection and importance sampling, Metropolis-Hastings, and how to spot when MCMC is failing. · checked 6 Nov 2026

#### Sources

- [Blitzstein and Hwang, Introduction to Probability](https://www.oreilly.com/library/view/-/9781466575578/)

- [Deisenroth, Faisal and Ong, Mathematics for Machine Learning](https://mml-book.github.io/)

- [Murphy, Probabilistic Machine Learning: An Introduction](https://probml.github.io/pml-book/book1.html)

- Integrals for ML on this site

Explanations are ours, built from these sources. Lab numbers are illustrative, and worked examples were checked by calculation.
