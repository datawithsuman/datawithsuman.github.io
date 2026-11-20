# Expectation, Variance & Covariance

> Why averaging correlated models helps less than you expect.

- Track: Fundamentals › Maths for ML › Probability
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/expectation-and-variance/
- Before this: Common Probability Distributions (`fundamentals/probability-distributions`)
- Related: Random Forest (`fundamentals/random-forest`)
- Quiz topic: `prob`

## Intuition

### The situation

Your team averages 100 ETA models, expecting the error to fall tenfold, but it barely moves. The interviewer asks:

> Why does averaging correlated models help less than averaging independent ones?

**Running example:** the food-delivery app averages several models' ETA predictions. Each model's error has a standard deviation of 4 minutes (variance 16). How much does averaging n models help, and what if their errors are correlated because they were trained on the same data?

#### Summarising randomness, and combining it

Losses are expectations (average error over the data distribution); ensembles average predictions; A/B tests compare means; feature correlations decide whether PCA or regularisation is needed. The handful of rules for means, variances and covariances is the toolkit behind all of these.

### The idea

Think of asking friends to guess a delivery time. If they guess independently, their errors cancel out. If they all read the same forecast, they share the same mistake, and asking more friends barely helps.

[Figure: Error against number of models averaged. With independent errors the curve keeps falling towards zero. With correlated errors it flattens at a floor.]

_Illustrative. The floor depends on how correlated the errors are._

### Play

**Try to break it.** Set the correlation to 0.3 and raise the number of models as far as it goes. Then set the correlation to 0.

#### How much does an ensemble help?

With ρ = 0.3, averaging 20 models cuts the error spread from 4.0 to about 2.3 minutes, and no number of models gets it below 2.2. Independent models (ρ = 0) would reach 0.9. That's exactly the design goal of a random forest: bagging alone leaves trees highly correlated, so random forests also sample features at each split to lower ρ, trading a little bias per tree for a lower variance floor.

**Now say why:** why can't more models get you below the floor, and what would you change to lower it?

## Maths

### Maths

#### In one breath

The **expectation** E[X] is the long-run average, and it's **linear**: E[aX + bY] = aE[X] + bE[Y] even when X and Y depend on each other, which cracks many interview puzzles. **Variance** measures spread, Var(X) = E[X²] − E[X]². **Covariance** measures whether two quantities move together; **correlation** is covariance rescaled to −1…1. The variance of a sum includes covariance terms, so averaging n independent noisy estimates divides variance by n, but averaging **correlated** ones hits a floor of ρσ². That single formula explains why random forests decorrelate their trees. What you'll be able to do after this: use linearity of expectation, compute variance and covariance, explain correlation vs covariance, and derive the variance of an average of correlated models.

#### Expectation and variance

$$ {\mathbb{E}[X] = \textstyle\sum_x x\,P(X{=}x)}, \quad {\mathbb{E}[aX + bY] = a\mathbb{E}[X] + b\mathbb{E}[Y]}, \quad {\mathrm{Var}(X) = \mathbb{E}[X^2] - \mathbb{E}[X]^2} $$

Blitzstein & Hwang ch. 4; MML §6.4. Variance rules: Var(aX + b) = a²Var(X); adding a constant doesn't change spread.

- **expectation**: Probability-weighted average of the values: Σ x P(X = x), or an integral for continuous X. For a die: 3.5.

- **linearity**: Always true, independent or not. Expected number of orders from 3 restaurants = sum of their expected orders.

- **variance**: Mean square minus squared mean. Units are squared; the standard deviation √Var is in original units.

#### Covariance and correlation

$$ {\mathrm{Cov}(X,Y) = \mathbb{E}[(X-\mu_X)(Y-\mu_Y)]}, \quad {\rho = \tfrac{\mathrm{Cov}(X,Y)}{\sigma_X\sigma_Y}}, \quad {\mathrm{Var}(X+Y) = \mathrm{Var}X + \mathrm{Var}Y + 2\,\mathrm{Cov}(X,Y)} $$

- **covariance**: Positive when X and Y tend to be above their means together; negative when one is up while the other is down; zero when unrelated linearly.

- **correlation**: Covariance divided by both standard deviations: unit-free, between −1 and 1.

- **variance of a sum**: Covariance enters twice. Independent ⇒ covariance 0 ⇒ variances add.

Zero correlation means no _linear_ relationship: Y = X² with X symmetric around 0 has zero correlation but complete dependence. Independence implies zero covariance, not the reverse.

#### The ensemble variance formula

$$ {\mathrm{Var}\Bigl(\tfrac{1}{n}\textstyle\sum_{i=1}^{n} X_i\Bigr)} = {\rho\,\sigma^2} + {\tfrac{1-\rho}{n}\,\sigma^2} $$

Hastie, Tibshirani & Friedman, _ESL_ 2nd ed., Eq. 15.1 (§15.2, random forests).

- **variance of the average**: Of n predictions, each with variance σ² and pairwise correlation ρ.

- **the floor**: ρσ²: shared error that no amount of averaging removes.

- **the part that averages out**: (1 − ρ)σ²/n: the independent part shrinks like 1/n.

#### From covariance to the covariance matrix

With many variables, gather every pair's covariance into a matrix Σ. The diagonal holds the variances. It's symmetric and positive semi-definite, since the variance of any combination wᵀx equals wᵀΣw, which can't be negative.

That one formula explains portfolio risk, why correlated models average poorly, and PCA.

Next: the multivariate Gaussian turns Σ into a shape, and the law of large numbers and central limit theorem show what happens when you average.

## In practice

### In practice

#### Expectation and variance across ML

- **Losses are expectations:** training minimises the average loss over data (empirical risk), an estimate of the expected loss on new data.

- **Bias–variance:** expected error = bias² + variance + noise (Bias–Variance).

- **Standard errors:** the mean of n independent samples has variance σ²/n, the basis of confidence intervals and A/B-test sample sizes (Confidence Intervals).

- **Covariance matrices:** PCA, Gaussian mixtures and Mahalanobis distance all use them.

- **Mini-batch gradients:** the gradient's variance falls like 1/batch size, which is why larger batches are less noisy.

### The answer that sounds right

#### "Variances add, so averaging n models divides the error by n"

Var(X + Y) = Var(X) + Var(Y) only when X and Y are uncorrelated. Models trained on the same data make similar mistakes; their errors are positively correlated, and the covariance terms don't average away. With 4-minute errors and correlation 0.6, averaging 100 models leaves a standard deviation of 3.1 minutes, not 0.4.

## Say it

### Why does averaging correlated models help less than averaging independent ones?

#### The interviewer pushes further

Follow-up 1 of 3

Does zero correlation mean independence?

No. It means no linear relationship. Y = X² with symmetric X is uncorrelated with X but fully dependent. (For jointly Gaussian variables they are equivalent.)

Follow-up 2 of 3

Use linearity of expectation: expected number of fixed points in a random permutation of n?

Each position is fixed with probability 1/n; summing n indicators gives 1, without worrying about dependence.

Follow-up 3 of 3

Why does bagging reduce variance but not bias?

Averaging keeps the mean (bias) of the base model and shrinks the variance, down to the correlation floor ρσ².

#### The 30-second answer

Expectation is the probability-weighted average and it's linear even for dependent variables. Variance is E[X²] minus E[X]², and covariance measures joint movement; correlation is covariance scaled to between −1 and 1. Variance of a sum adds the variances plus twice the covariance, so the average of n estimates with variance σ² and pairwise correlation ρ has variance ρσ² + (1 − ρ)σ²/n: independent errors shrink like 1/n, correlated ones hit a floor. That's why random forests decorrelate trees, why standard errors fall like 1/√n, and why bigger mini-batches give less noisy gradients.

**Go further**

#### What not to say

- "Variance of a sum is the sum of variances." Only when uncorrelated.

- "Correlation shows causation." See Correlation vs Causation.

**Key terms and sources**

Expected value and its linearity, variance and standard deviation, covariance and correlation, the variance of sums and averages, and why averaging correlated models has a floor (bagging and random forests) · built from Blitzstein & Hwang, _Introduction to Probability_ (ch. 4, 7), Hastie et al., _ESL_ (§15.2) and Deisenroth et al., _MML_ (§6.4) · checked 28 Oct 2026

#### Key terms

| Term | Meaning |
|---|---|
| **Expectation** | Probability-weighted average. |
| **Linearity of expectation** | E of a sum = sum of Es, always. |
| **Variance / std dev** | Average squared spread / its square root. |
| **Covariance / correlation** | Joint movement / its unit-free version in [−1, 1]. |
| **Standard error** | Std dev of an estimate, e.g. σ/√n for a mean. |

#### Sources

1. J. Blitzstein & J. Hwang, _Introduction to Probability_, 2nd ed., 2019, ch. 4 and 7, [stat110](https://projects.iq.harvard.edu/stat110).

2. T. Hastie, R. Tibshirani & J. Friedman, _The Elements of Statistical Learning_, 2nd ed., Springer 2009, §15.2 (Eq. 15.1).

3. M. P. Deisenroth, A. A. Faisal & C. S. Ong, _Mathematics for Machine Learning_, CUP 2020, §6.4.
