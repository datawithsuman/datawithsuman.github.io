# Integrals for ML

> Where do integrals show up in machine learning, and what do you do when you can't compute one?

- Track: Fundamentals › Maths for ML › Calculus and optimisation
- Type: Concept · 15 min
- Page: https://aimlrounds.com/tracks/fundamentals/integrals-for-ml/
- Before this: Expectation, Variance & Covariance (`fundamentals/expectation-and-variance`)
- Related: Autoencoders and VAEs (`fundamentals/autoencoders-and-vaes`)
- Quiz topic: `calc`
- Sources checked: 2026-11-06 · Text last changed: 2026-11-20 · Version: 9445839913

## Intuition

### The situation

Your VAE's textbook says the likelihood involves an integral that can't be computed. A teammate suggests evaluating it on a fine grid. You also wonder why the mini-batch gradient works at all. The interviewer asks:

> Where do integrals show up in machine learning, and what do you do when you can't compute one?

#### Why it matters

Many hard parts of ML, such as Bayesian inference, VAEs and diffusion models, exist because an integral can't be computed. Seeing this explains why those methods look the way they do. See distributions and expectation too.

### The idea

Think of estimating how much rain fell across a country. You could place a gauge on a fine grid, which works for a small area, but in many dimensions you'd need impossibly many. Or you could sample random spots, and average them. That's less exact, yet it barely gets harder as the space grows.

[Figure: Three approaches to a hard integral. A grid is exact in low dimensions, but it explodes as dimensions rise. Monte Carlo samples and averages. Variational methods optimise a bound.]

_Most real integrals in ML can't be solved exactly._

### Play

**Try to break it.** Reduce the points, and compare the estimates. Then raise the dimensions.

#### Estimate an area, then add dimensions

Grid uses the midpoint rule from −6 to a. Monte Carlo uses seeded random normal samples, so it stays the same unless you change the inputs. Our own calculation, using one-dimensional estimates for the first three cards.

In one dimension, the grid beats Monte Carlo easily. Now raise the dimensions to **50**: the grid would need more points than there are atoms in the universe, while Monte Carlo's error rate doesn't change. That's why sampling dominates high-dimensional problems.

**Now say why:** why does a grid fail in high dimensions, while sampling doesn't?

## Maths

### Maths

#### In one breath

An integral adds up tiny pieces, which gives an area or a weighted average. In ML, integrals give **probabilities** from densities, **expectations** and **marginals**, where you sum over what you don't know. AUC is one as well. The difficulty is that most integrals in real models **can't be solved exactly**, and grids fail as dimensions rise. So we use **Monte Carlo**, whose error shrinks with the number of samples regardless of dimension, or **variational methods**, which replace the integral with an optimisation.

#### Adding up tiny pieces

##### Where integrals appear

| Use | The integral | In ML |
|---|---|---|
| **Probability** | The area under a density | The chance a value falls in a range. All of it adds up to 1. |
| **Expectation** | ∫ f(x) p(x) dx | Expected loss, and what training tries to minimise. |
| **Marginalising** | ∫ p(x, z) dz | Removing a hidden variable, as in VAEs and mixtures. |
| **Bayes** | p(x) = ∫ p(x \| θ) p(θ) dθ | The evidence, which makes exact Bayesian inference hard. |
| **Evaluation** | ∫ TPR d(FPR) | AUC, the area under the ROC curve. |

##### A density isn't a probability

A density's value can exceed 1, because only the area counts. The chance of any exact value of a continuous variable is zero. You always integrate over a range.

##### Three ways to deal with hard integrals

| Method | Idea | Weakness |
|---|---|---|
| **Grid** | Add up rectangles. | Needs n^d points in d dimensions, which quickly becomes impossible. |
| **Monte Carlo** | Sample from p and average f: an estimate of the expectation. | Error shrinks only as 1/√N, and sampling from p can be hard. |
| **Variational** | Pick a simple approximation, and optimise a bound on the integral. | Biased, depending on how good the approximation is. |

##### You've used Monte Carlo already

Mini-batch SGD is Monte Carlo. The true gradient is an expectation over all data, and a mini-batch estimates it by averaging samples. That's why doubling the batch only reduces the noise by √2.

#### The maths

$$ {\mathbb{E}_{p}[f(x)]} = {\int f(x)\,p(x)\,dx} \approx {\frac{1}{N}\sum_{i=1}^{N} f(x_i)}, \quad x_i \sim p, \qquad {\text{error} \propto \frac{1}{\sqrt{N}}} $$

Worked example: AUC also equals the chance a random positive scores above a random negative. So you can estimate it by sampling pairs, without doing the integral at all.

- **the expectation**: A weighted average of f, weighted by how likely each x is.

- **as an integral**: Adds up over every possible x. It’s rarely solvable exactly.

- **the Monte Carlo estimate**: Draw samples from p, and average. Unbiased, and it’s simple to compute.

- **its error**: Four times the samples halve the error. The rate doesn’t depend on the dimension, although the constant can.

## In practice

### In practice

#### In practice

- **Differentiating through expectations:** you can't sample directly through a gradient. The reparameterisation trick rewrites the sample so gradients can flow, as in VAEs.

- **Importance sampling:** sample from an easier distribution, then reweight. It's also used in off-policy evaluation, as with bandit logs.

- **The ELBO:** the VAE's objective is a bound on a log integral that can't be computed.

- **When it's solvable:** use conjugate priors or Gaussians when you can, since exact answers beat sampling.

- **Sample size:** to halve Monte Carlo error, you need four times the samples, so very precise estimates get expensive.

### The answer that sounds right

#### "Use a finer grid, because computers are fast"

It sounds right, since a finer grid is more accurate. But cost grows exponentially with dimension. With 100 points per dimension, ten dimensions need 10²⁰ points, and a model's hidden variables can have hundreds. Speed can't beat that. Sampling works because its error rate doesn't depend on the dimension.

## Say it

### Where do integrals show up in machine learning, and what do you do when you can't compute one?

#### The interviewer pushes further

Follow-up 1 of 3

Can a probability density be greater than 1?

Yes. A density isn't a probability, and only the area under it must equal 1. A uniform distribution on 0 to 0.5 has a density of 2 throughout. The probability comes from integrating over a range.

Follow-up 2 of 3

Why is the mini-batch gradient an unbiased estimate?

The full gradient is an average over the data, which is an expectation. A random mini-batch's average has that same expected value, so it's Monte Carlo. It's noisy, with error shrinking as one over the square root of the batch size, which is why bigger batches help less and less.

Follow-up 3 of 3

Monte Carlo or variational inference: which would you choose?

Monte Carlo, like MCMC, can get arbitrarily close to the truth with more samples, but it can be slow. Variational methods are faster, and use ordinary optimisers, but they're limited by the approximation chosen. So use sampling when accuracy matters most, and variational methods for scale.

#### The 30-second answer

Integrals give probabilities from densities, expectations, and marginals, where you sum out a hidden variable. AUC is one too. Most real ones can't be solved exactly, and grid methods fail, because they need n to the d points. So I'd use Monte Carlo: sample from the distribution, and average. Its error shrinks as one over root N, whatever the dimension. Mini-batch SGD is Monte Carlo on the expected gradient. Or I'd use variational methods, which replace the integral with an optimisation over a bound, as in VAEs.

**Key terms and sources**

Integrals as area and as weighted averages: continuous probability, expectations, marginalising, AUC, and why intractable integrals lead to sampling and variational methods. · checked 6 Nov 2026

#### Sources

- [Deisenroth, Faisal and Ong, Mathematics for Machine Learning](https://mml-book.github.io/)

- Autoencoders and VAEs on this site

- ROC and PR AUC on this site

Explanations are ours, built from these sources. Lab numbers are illustrative, and worked examples were checked by calculation.
