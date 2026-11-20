# Common Probability Distributions

> Bernoulli to Gaussian, and which loss each one implies.

- Track: Fundamentals › Maths for ML › Probability
- Type: Concept · 25 min
- Page: https://aimlrounds.com/tracks/fundamentals/probability-distributions/
- Before this: Probability Basics & Bayes' Rule (`fundamentals/probability-and-bayes`)
- Quiz topic: `prob`

## Intuition

### The situation

You're predicting how many orders arrive each hour. A teammate uses squared error, and the model sometimes predicts −2 orders. The interviewer asks:

> How does the distribution you assume for the target decide the loss?

**Running example:** quantities from the food-delivery app: whether a single order is late (yes/no), how many of today's 20 orders from one restaurant are late, how many orders arrive in a minute, how long until the next order, and the error of the delivery-time estimate.

#### Describing uncertainty with a few numbers

You can't predict the exact number of orders next minute, but you can say "about 4, rarely more than 9". A distribution makes that precise with one or two parameters. Picking the right one matters twice in ML: it describes your data (for simulation, monitoring, anomaly detection), and it defines the loss your model minimises.

### The idea

Think of a drawer of measuring tools. A yes or no, a count, a waiting time and a measurement error each need a different tool. Pick the right one, and it also tells you which loss to train with.

[Figure: Four small shapes with their uses. Bernoulli: two bars for yes or no, giving log loss. Poisson: bars for counts, giving Poisson loss. Gaussian: a bell for measurement errors, giving squared error. Exponential: a falling curve for waiting times.]

_Illustrative shapes. The losses come from maximum likelihood._

### Play

**Try to break it.** On the Poisson, raise the rate and watch the shape. Then compare its mean and variance.

#### Change the parameters, watch the shape

**Now say why:** why does a Poisson stop fitting if your counts vary much more than their average?

## Maths

### Maths

#### In one breath

A distribution says how likely each possible value is. A few shapes cover most of ML: **Bernoulli** (one yes/no, like "is this order late?"), **binomial** (how many yeses in n tries), **Poisson** (how many events in a time window, like orders per minute), **Gaussian** (sums of many small effects, like measurement noise) and **exponential** (waiting time until the next event). Choosing a distribution for your target is the same as choosing a loss: Gaussian noise gives squared error, Bernoulli gives log loss, categorical gives softmax cross-entropy, Poisson gives Poisson loss for counts. What you'll be able to do after this: recognise which distribution fits a quantity, state its mean and variance, explain how binomial, Poisson and Gaussian connect, and map each to its ML loss.

#### PMFs, PDFs, mean and variance

- **Discrete** variables (counts, yes/no) have a probability mass function: P(X = k) for each value, summing to 1.

- **Continuous** variables (times, errors) have a density p(x): probabilities are areas under the curve; p(x) itself can exceed 1.

- **Mean** E[X]: the long-run average. **Variance** Var(X) = E[(X − E[X])²]: the average squared spread; its square root is the standard deviation (details in Expectation & Variance).

#### Binomial → Poisson → Gaussian

- **Bernoulli → binomial:** a binomial is the sum of n independent Bernoullis.

- **Binomial → Poisson:** many tries, each rare (n large, p small, np = λ fixed): binomial ≈ Poisson(λ). Orders per minute are many customers each with a tiny chance of ordering that minute.

- **Poisson ↔ exponential:** if events arrive as a Poisson process with rate λ, the waiting times between them are exponential with mean 1/λ.

- **Anything → Gaussian:** by the central limit theorem, sums and averages of many independent variables are approximately Gaussian, which is why it's everywhere (and why confidence intervals work; see Confidence Intervals). Binomial(n, p) ≈ Gaussian(np, np(1 − p)) when np and n(1 − p) are both large.

#### The density, read term by term

$$ p(x) = {\tfrac{1}{\sqrt{2\pi\sigma^2}}}\exp\!\Bigl({-\tfrac{(x-\mu)^2}{2\sigma^2}}\Bigr) $$

- **normalising constant**: Makes the total area 1; wider curves are lower.

- **squared distance from the mean**: In units of σ². Values far from μ are exponentially unlikely: about 68% within 1σ, 95% within 2σ, 99.7% within 3σ.

Taking −log of this density gives (x − μ)²/(2σ²) plus a constant: maximising Gaussian likelihood is minimising squared error. That's the probabilistic reason linear regression uses MSE.

#### Categorical, Beta, CDFs and transformed values

| Tool | What it is | In ML |
|---|---|---|
| **Categorical** | One of k options, each with its own chance. Bernoulli is the case with k = 2. | Softmax outputs, and next-token prediction. |
| **Beta** | A distribution over a chance between 0 and 1. | Uncertainty about a click rate, and bandits. |
| **CDF** | F(x) = P(X ≤ x). It rises from 0 to 1. | Percentiles such as p99 latency, and generating samples. |

##### Transforming a value changes its shape

If X is Normal, e^X is **log-normal**: always positive, with a long right tail, like many latencies and prices. A density has to change to keep the total area at 1. So regions a transformation stretches get lower density, and regions it squeezes get higher density. That's the change-of-variables rule, and it's the idea behind normalising flows.

The CDF also gives a way of sampling. See sampling methods.

## In practice

### In practice

#### Five distributions, one table

| Distribution | Models | Parameters | Mean | Variance | ML loss / use |
|---|---|---|---|---|---|
| **Bernoulli** | One yes/no | p | p | p(1 − p) | Log loss (logistic regression) |
| **Binomial** | Yeses in n independent tries | n, p | np | np(1 − p) | Conversion counts, A/B tests |
| **Categorical** | One of K classes | p₁…p_K | — | — | Softmax cross-entropy |
| **Poisson** | Count of events in a window | λ | λ | λ | Poisson loss for count targets (demand) |
| **Gaussian** | Sums of many small effects | μ, σ | μ | σ² | Squared error (linear regression) |
| **Exponential** | Waiting time to the next event | λ (rate) | 1/λ | 1/λ² | Survival / time-to-event |

Blitzstein & Hwang ch. 3–5; MML §6.5–6.6. Losses follow from maximum likelihood (MLE & MAP).

### The answer that sounds right

#### "Assume everything is Gaussian"

A Gaussian is symmetric and allows any real value. Order counts can't be negative or fractional; delivery times are skewed with a long right tail; "late or not" has two values. Fitting a Gaussian (or using squared error) to these can predict −2 orders, underestimate rare long delays, and give probabilities outside [0, 1]. Match the distribution to the type of quantity first.

## Say it

### How does the distribution you assume for the target decide the loss?

#### The interviewer pushes further

Follow-up 1 of 3

How would you model the number of orders per hour?

Start with Poisson (count, non-negative); if variance exceeds the mean, negative binomial; use a Poisson or Tweedie objective in gradient boosting.

Follow-up 2 of 3

Why is the Gaussian so common?

The central limit theorem, its maximum-entropy property for a given mean and variance, and its mathematical convenience (closed under sums and conditioning).

Follow-up 3 of 3

Mean and variance of a binomial?

np and np(1 − p): sum of n independent Bernoullis, each with mean p and variance p(1 − p).

#### The 30-second answer

Bernoulli models a single binary outcome, binomial the number of successes in n trials, Poisson counts of events in a window with mean equal to variance, the Gaussian sums of many small effects, and the exponential waiting times between Poisson events. They connect: binomial is a sum of Bernoullis, Poisson is the rare-event limit of the binomial, and the central limit theorem makes averages Gaussian. Choosing the distribution of the target fixes the loss via maximum likelihood: Gaussian gives squared error, Bernoulli gives log loss, categorical gives softmax cross-entropy and Poisson gives Poisson loss for counts.

**Go further**

#### What not to say

- "A density value is a probability." It's a density; probabilities are areas.

- "Use MSE for counts and probabilities." Use Poisson loss and log loss.

**Key terms and sources**

Bernoulli, binomial, Poisson, Gaussian and exponential: what each models, their parameters, mean and variance, how they relate, and which ML loss each one implies · built from Blitzstein & Hwang, _Introduction to Probability_ (ch. 3–5), Deisenroth et al., _MML_ (ch. 6.5–6.6) and Bishop, _PRML_ (ch. 2) · checked 28 Oct 2026

#### Key terms

| Term | Meaning |
|---|---|
| **PMF / PDF** | Probabilities of discrete values / density for continuous ones. |
| **Support** | The values a distribution allows (e.g. Poisson: 0, 1, 2, …). |
| **Overdispersion** | Count data with variance above its mean (Poisson assumes equal); use negative binomial. |
| **Central limit theorem** | Averages of many independent variables are approximately Gaussian. |

#### Sources

1. J. Blitzstein & J. Hwang, _Introduction to Probability_, 2nd ed., 2019, ch. 3–5, [stat110](https://projects.iq.harvard.edu/stat110).

2. M. P. Deisenroth, A. A. Faisal & C. S. Ong, _Mathematics for Machine Learning_, CUP 2020, §6.5–6.6.

3. C. Bishop, _Pattern Recognition and Machine Learning_, Springer 2006, ch. 2.
