# Law of Large Numbers and Central Limit Theorem

> What's the difference between the law of large numbers and the central limit theorem?

- Track: Fundamentals › Maths for ML › Probability
- Type: Concept · 15 min
- Page: https://aimlrounds.com/tracks/fundamentals/law-of-large-numbers-and-clt/
- Before this: Expectation, Variance & Covariance (`fundamentals/expectation-and-variance`)
- Related: Hypothesis Tests, p-values & A/B Testing (`fundamentals/hypothesis-testing-and-ab-tests`)
- Quiz topic: `prob`

## Intuition

### The situation

Order value is very skewed, with a few huge orders. A teammate says you can't use a normal test on it, since the data isn't Normal. Another says that 30 samples is always enough. The interviewer asks:

> What's the difference between the law of large numbers and the central limit theorem?

#### Why it matters

These results justify almost every error estimate you use: confidence intervals, A/B tests, mini-batch gradients and Monte Carlo. It's also a very common interview question, and one that's often answered wrongly. This uses expectation and variance.

### The idea

Think of asking people to guess the weight of an ox. One guess can be far off. The average of many guesses gets close to the truth, and that's the first law. If many groups each did this, their averages would form a neat bell shape around the truth, however odd the individual guesses were. That's the second.

[Figure: Two results. The law of large numbers says the average reaches the true mean. The central limit theorem says the error is approximately Normal, with spread sigma over root n.]

_Both are about averages, not about the data itself._

### Play

**Try to break it.** Set the samples to 1, then raise them. Then try the rare event at 30 samples.

#### Average a skewed distribution

Our simulation: 3,000 averages from a seeded random source. The exponential has mean 1. The rare event happens 5% of the time. Skew near 0 means symmetrical.

Set the samples to **1**, so you see the raw shape. Then raise them, and it turns into a hill. Try the **rare event** at 30 samples: it's still lumpy and skewed, as a 5% event needs a much larger sample. There's no universal magic number.

**Now say why:** why isn't 30 samples enough for a rare event?

## Maths

### Maths

#### In one breath

The **law of large numbers** says a sample average gets close to the true mean as the sample grows. The **central limit theorem** goes further, describing the error: averages are **approximately Normal**, with a spread of **σ/√n**, whatever the shape of the original data, as long as its variance is finite. So you need four times the data to halve the error. It's about **averages**, not the data itself, and heavy tails can break it.

#### Two results about averages

| | Law of large numbers | Central limit theorem |
|---|---|---|
| **Question** | Where does the average go? | What does the error look like? |
| **Answer** | To the true mean. | Approximately Normal, with spread σ/√n. |
| **Used for** | Trusting that averages work at all. | Building intervals and tests. |

##### What people get wrong

- **"With enough data, the data becomes Normal."** No. The data keeps its shape. It's the average of many samples that looks Normal.

- **"30 samples is always enough."** It's a rule of thumb. Very skewed data, like revenue, can need far more.

- **"Luck evens out in the short run."** After ten heads, the next flip is still 50/50. Later flips don't compensate. A long run simply dilutes the early streak.

##### When they fail

- **Heavy tails:** with infinite variance, like the Cauchy distribution, averages may never settle down.

- **Dependence:** strongly correlated samples hold less information than their count suggests, so errors shrink more slowly.

- **Changing distributions:** if the world keeps shifting, there's no single mean to converge to.

##### Where you've seen √n

- **Mini-batches:** four times the batch size halves gradient noise.

- **A/B tests:** halving the detectable effect needs four times the users.

- **Monte Carlo:** ten times the accuracy needs a hundred times the samples.

#### The maths

$$ \bar X_n \to \mu, \qquad \bar X_n \;\approx\; \mathcal{N}\!\left(\mu,\; \frac{\sigma^2}{n}\right), \qquad SE = \frac{\sigma}{\sqrt{n}} $$

Example: for daily order values with σ = 200 and n = 400, the standard error is 200 ÷ 20 = 10. To get it to 5, you need 1,600 orders.

- **the sample average**: The mean of n independent samples.

- **the true mean**: The law of large numbers says the average reaches this as n grows.

- **the central limit theorem**: For large n, the average’s distribution is approximately Normal, whatever the original shape.

- **the standard error**: How far the average typically is from the truth. It’s why precision gets expensive.

## In practice

### In practice

#### In practice

- **Skewed metrics:** revenue often has a few huge values, and the Normal approximation can need many samples. Cap values, or use the bootstrap.

- **Correlated data:** repeated events from one user aren't independent. See ratio metrics for what to do.

- **Small-sample tests:** with very few samples, use a t-distribution, as the variance itself is uncertain.

- **Check it:** a quick simulation or bootstrap shows whether Normality is reasonable for your metric.

### The answer that sounds right

#### "With enough data, everything becomes Normal"

It sounds right, as people often hear this version. But more data shows the true shape more clearly, including its skew. Only the average, across repeated samples, becomes Normal. So your revenue is still skewed, while the test on average revenue may be fine with enough samples.

## Say it

### What's the difference between the law of large numbers and the central limit theorem?

#### The interviewer pushes further

Follow-up 1 of 3

Does the central limit theorem mean my data becomes Normal with more samples?

No. More samples just show the data's true shape more clearly, and that can be very skewed. It's the distribution of the average, if you repeated the sampling many times, that becomes Normal.

Follow-up 2 of 3

Why does it matter that variance is finite?

The theorem's scale uses σ. With infinite variance, like the Cauchy distribution, single extreme values can dominate any average. The average of Cauchy samples has the same distribution as one sample, so more data doesn't help at all.

Follow-up 3 of 3

After ten heads in a row with a fair coin, is tails due?

No, it's still 50/50, as flips are independent. The law of large numbers doesn't work by correcting past results. The early streak simply becomes a smaller share of a growing total. Believing otherwise is the gambler's fallacy.

The law of large numbers says the sample average approaches the true mean as the sample grows. The central limit theorem describes the error: averages are approximately Normal, with a spread of sigma over root n, whatever the data's original shape, if variance is finite. So four times the data halves the error. It's about averages, not the data, which keeps its shape. Thirty samples isn't a universal rule, as very skewed data needs more. And it can fail with heavy tails or strong dependence.

**Key terms and sources**

Why sample averages settle down, why averages look Normal whatever the data's shape, the square-root rule, and where these results fail.

#### Sources

- Blitzstein and Hwang, Introduction to Probability

- Murphy, Probabilistic Machine Learning: An Introduction

- Hypothesis tests on this site

Explanations are ours, built from these sources. Lab numbers are illustrative, and worked examples were checked by calculation.
