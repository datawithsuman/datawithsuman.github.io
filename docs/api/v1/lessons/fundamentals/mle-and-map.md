# Maximum Likelihood & MAP

> Why L2 regularisation is a Gaussian prior in disguise.

- Track: Fundamentals › Maths for ML › Probability
- Type: Concept · 25 min
- Page: https://aimlrounds.com/tracks/fundamentals/mle-and-map/
- Before this: Common Probability Distributions (`fundamentals/probability-distributions`)
- Related: Regularized Linear Models (`fundamentals/regularized-linear-models`)
- Quiz topic: `prob`
- Sources checked: 2026-10-28 · Text last changed: 2026-11-20 · Version: f1022db2f8

## Intuition

### The situation

A new restaurant's first order was late. Its estimated late rate is now 100%, and it drops to the bottom of your rankings. The interviewer asks:

> What is the difference between MLE and MAP?

**Running example:** a new restaurant joins the food-delivery app. We want its late-delivery rate θ. So far it has n orders, k of them late. Across the platform, 25% of orders are late. How should we estimate θ after 3 orders? After 100?

#### From data to a parameter, with a principle

Every model has parameters to set from data. "Choose the parameters under which the data you saw would be most likely" is a principle that works for coin flips, regressions, neural networks and language models alike, and it explains where the standard losses come from. Its weakness with little data motivates priors, and priors explain regularisation.

### The idea

Think of judging a new restaurant after one late order. The data alone says it's always late, but your experience with other restaurants says that's unlikely. MLE trusts only the data. MAP blends in that experience, and as orders pile up, the data takes over.

[Figure: A scale from 0 to 100 percent late. The platform average is at 25 percent, MAP at 42 percent and MLE at 100 percent.]

_From the lesson's example: 3 orders, all late, with a prior worth 10 imaginary orders at 25%._

### Play

**Try to break it.** Set 3 orders, all late, and compare MLE with MAP. Then raise the orders to 100.

#### Watch the prior fade as data arrives

Curves are scaled to the same height. Teal: likelihood; violet: prior; green: posterior. With few orders the posterior sits near the prior; with 100 it follows the data.

After 3 late orders, MLE says 100% late; MAP with m = 10 says 42%. After 100 orders with half late, MLE says 50% and MAP 47.7%: the data now dominates. MAP behaves sensibly at both ends, which is why ranking systems, CTR estimates and target encodings shrink small-sample rates.

**Now say why:** why do the two estimates start far apart and then nearly agree?

## Maths

### Maths

#### In one breath

The **likelihood** of a parameter is how probable the observed data would be if that parameter were true. **Maximum likelihood (MLE)** picks the parameter that makes the data most probable; in practice we maximise the **log**-likelihood (sums instead of products). Most ML losses are negative log-likelihoods in disguise: Gaussian noise → squared error, Bernoulli labels → log loss. MLE overfits small samples (one order, one late → "100% late"). **MAP** adds a **prior** belief and maximises likelihood × prior; with a Gaussian prior on weights that is exactly **L2 regularisation**, with a Laplace prior it's **L1**, and for rates it's smoothing towards a global average. What you'll be able to do after this: write a likelihood, derive MSE and log loss from MLE, compute MLE and MAP for a rate, and explain regularisation as a prior.

#### Likelihood and log-likelihood

$$ {\mathcal{L}(\theta)} = {\textstyle\prod_{i=1}^{n} \theta^{y_i}(1-\theta)^{1-y_i}} = \theta^{k}(1-\theta)^{n-k}, \qquad {\ell(\theta) = k\log\theta + (n-k)\log(1-\theta)} $$

MML §8.3; PRML §2.1. Setting dℓ/dθ = k/θ − (n − k)/(1 − θ) = 0 gives θ̂MLE = k/n.

- **likelihood of θ**: A function of the parameter θ, with the data fixed: how probable this exact data is under θ.

- **independent observations multiply**: Each order contributes θ if late, 1 − θ if on time.

- **log-likelihood**: Logs turn the product into a sum: numerically stable and easy to differentiate. Same maximiser.

The likelihood is **not** a probability distribution over θ (it needn't integrate to 1); it compares how well different θ explain the same data.

#### Posterior ∝ likelihood × prior

$$ {\hat\theta_{\text{MAP}}} = \arg\max_\theta\ \bigl[{\log p(\text{data}\mid\theta)} + {\log p(\theta)}\bigr] $$

- **MAP estimate**: The most probable parameter after seeing the data: the peak of the posterior.

- **log-likelihood**: How well θ explains the data. Grows with n.

- **log-prior**: What we believed before. Fixed size, so it matters a lot for small n and fades for large n.

For a rate with a Beta prior equivalent to "m imaginary orders at the platform rate 25%", the MAP estimate is (k + 0.25m)/(n + m): the observed rate shrunk towards 25%, with m controlling how hard. That is the same smoothing formula as target encoding (Encoding Categorical Features) and Laplace smoothing in Naive Bayes.

#### L2 and L1 come from priors on the weights

$$ \hat w_{\text{MAP}} = \arg\min_w\ {-\log p(y\mid X, w)} + {\lambda \lVert w\rVert_2^2} \quad\text{or}\quad + {\lambda \lVert w\rVert_1} $$

PRML §3.3 (Gaussian prior and ridge); MML §9.3; see Regularized Linear Models.

- **negative log-likelihood**: The usual loss: squared error or log loss.

- **Gaussian prior → L2**: −log of a zero-mean Gaussian prior on w is ‖w‖²/(2τ²) + const: ridge / weight decay, with λ = 1/(2τ²) up to scaling. A tighter prior (small τ) means stronger regularisation.

- **Laplace prior → L1**: −log of a Laplace prior is ‖w‖₁/b + const: the lasso, whose sharp peak at zero favours exact zeros.

Full Bayesian inference goes one step further: instead of the single peak, keep the whole posterior and average predictions over it (e.g. Bayesian linear regression, Gaussian processes). MAP is the cheap, point-estimate version.

#### Beyond one best value: the full posterior

MAP picks the peak of the posterior, and discards the rest. Two parameters can share a peak, while one is far more uncertain. With 7 of 10, and with 700 of 1,000, a rate of 0.7 looks the same as a point estimate, but you should trust the second far more.

Keeping the whole distribution gives you intervals, better predictions and natural exploration. See Bayesian inference and conjugate priors.

## In practice

### In practice

#### Every common loss is a negative log-likelihood

| Assume the target is… | Negative log-likelihood is… | Model |
|---|---|---|
| Gaussian around the prediction, fixed σ | Σ (y − ŷ)² / 2σ² + const: **squared error** | Linear regression |
| Bernoulli with probability p̂ | −Σ [y log p̂ + (1 − y) log(1 − p̂)]: **log loss** | Logistic regression, binary classifiers |
| Categorical over K classes | −Σ log p̂true class: **cross-entropy** | Softmax classifiers, language models (next-token loss) |
| Laplace around the prediction | Σ \|y − ŷ\|: **absolute error** | Robust (median) regression |
| Poisson with rate λ̂ | Σ (λ̂ − y log λ̂): **Poisson loss** | Count regression |

PRML §1.2.5, §3.1.1, §4.3.2; Murphy, _Probabilistic Machine Learning: An Introduction_, ch. 4. Training a language model by minimising next-token cross-entropy is maximum likelihood over the training text.

### The answer that sounds right

#### "Just use the observed rate"

The MLE k/n is unbiased but wild for small n. A restaurant with 1 order that happened to be late gets θ̂ = 100% late and drops to the bottom of rankings; one with 2 on-time orders gets 0%, a perfect record. Neither is believable: we know most restaurants are near the platform's 25%. The fix is to combine the data with that knowledge.

## Say it

### What is the difference between MLE and MAP?

#### The interviewer pushes further

Follow-up 1 of 3

Derive the MLE of a Bernoulli parameter.

ℓ(θ) = k log θ + (n − k) log(1 − θ); setting the derivative to zero gives θ̂ = k/n.

Follow-up 2 of 3

Why does minimising MSE correspond to MLE?

With y = f(x) + ε, ε ~ N(0, σ²), the negative log-likelihood is Σ(y − f(x))²/(2σ²) plus a constant, so maximising likelihood minimises the sum of squared errors.

Follow-up 3 of 3

MLE vs MAP vs full Bayesian?

MLE: data only, point estimate. MAP: data + prior, point estimate (peak). Bayesian: keep the whole posterior and integrate predictions over it, giving uncertainty.

#### The 30-second answer

Maximum likelihood chooses parameters that make the observed data most probable; we maximise the log-likelihood because products of probabilities become sums. Common losses are negative log-likelihoods: assuming Gaussian noise gives squared error, Bernoulli labels give log loss and categorical labels give cross-entropy, which is also how language models are trained. MLE can overfit small samples, so MAP adds a prior and maximises likelihood times prior; a Gaussian prior on weights gives L2 regularisation and a Laplace prior gives L1, and for rates a Beta prior gives smoothing towards a global average.

**Go further**

#### What not to say

- "The likelihood is the probability of the parameter." It's the probability of the data given the parameter.

- "MAP is always better." With a poor prior it biases estimates; with lots of data MAP ≈ MLE anyway.

**Key terms and sources**

Likelihood vs probability, log-likelihood, maximum likelihood estimation, why MLE gives MSE and log loss, priors and MAP estimation, and why MAP is regularisation · built from Deisenroth et al., _MML_ (ch. 8.3), Bishop, _PRML_ (ch. 1–3) and Murphy, _Probabilistic Machine Learning_ (ch. 4) · checked 28 Oct 2026

#### Key terms

| Term | Meaning |
|---|---|
| **Likelihood** | p(data \| θ) as a function of θ. |
| **MLE** | θ that maximises the likelihood. |
| **Prior / posterior** | p(θ) before data / p(θ \| data) after. |
| **MAP** | θ that maximises the posterior. |
| **Conjugate prior** | A prior whose posterior has the same family (Beta for Bernoulli rates). |
| **Shrinkage** | Pulling noisy estimates towards a common value. |

#### Sources

1. M. P. Deisenroth, A. A. Faisal & C. S. Ong, _Mathematics for Machine Learning_, CUP 2020, §8.3, §9.3, [mml-book.github.io](https://mml-book.github.io/).

2. C. Bishop, _Pattern Recognition and Machine Learning_, Springer 2006, ch. 1–4.

3. K. Murphy, _Probabilistic Machine Learning: An Introduction_, MIT Press 2022, ch. 4, [probml.github.io](https://probml.github.io/pml-book/book1.html).
