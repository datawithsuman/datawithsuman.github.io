# Bayesian Inference and Conjugate Priors

> What does Bayesian inference give you that MLE and MAP don't, and what is a conjugate prior?

- Track: Fundamentals › Maths for ML › Probability
- Type: Concept · 15 min
- Page: https://aimlrounds.com/tracks/fundamentals/bayesian-inference-and-conjugate-priors/
- Before this: Maximum Likelihood & MAP (`fundamentals/mle-and-map`)
- Related: Bandits vs A/B Tests (`fundamentals/bandits-vs-ab-tests`)
- Quiz topic: `prob`

## Intuition

### The situation

A new restaurant has 1 five-star review out of 1. Another has 950 of 1,000. A simple average ranks the new one first. You also need to know how sure you are about each one's real quality. The interviewer asks:

> What does Bayesian inference give you that MLE and MAP don't, and what is a conjugate prior?

#### Why it matters

Knowing how sure you are changes decisions, particularly with little data. This is the basis of Thompson sampling, Bayesian A/B tests and Gaussian processes. It follows on from MLE and MAP.

### The idea

Think of a friend recommending a restaurant. You don't start from nothing: you know most places are decent. One rave barely moves that belief, while a thousand reviews fully replace it. And you hold a range in your head, not a single number. That's Bayesian inference.

[Figure: Three answers for 7 of 10. MLE gives 0.70. MAP gives 0.67. Bayesian gives a distribution with mean 0.64 and a range.]

_For 7 of 10, with a Beta(2, 2) prior._

### Play

**Try to break it.** Set a strong prior of 50 and 50 with 10 trials, then raise the trials to 200.

#### Update a belief

Dashed is the prior, and solid is the posterior. Computed exactly on a fine grid. All values are illustrative.

Set the prior to **50 and 50**, a strong belief of about one half. With 10 trials, it barely moves. Raise the trials to **200**, and the data takes over. With plenty of data, prior choice matters little, and the answers converge.

**Now say why:** why does the prior stop mattering with lots of data?

## Maths

### Maths

#### In one breath

MLE and MAP give one best value. **Bayesian inference** keeps a full distribution over what the value might be, so you know **how uncertain you are**. Start with a prior, multiply by the likelihood, and normalise to get the posterior. A **conjugate prior** makes this easy: a Beta prior with yes-or-no data gives a Beta posterior, so you only add counts. In most real models the normalising integral can't be solved, so we use sampling or variational methods.

#### A belief, updated

##### Three answers to one question

A new restaurant has 7 good orders out of 10. What's its true rate of good orders?

| Method | Answer | Note |
|---|---|---|
| **MLE** | 0.70 | Only the data. With 1 of 1, it would say 100%. |
| **MAP** | 0.67 | Data and prior, but still one value. |
| **Bayesian** | A whole distribution, with mean 0.64 | Also tells you the rate is probably between about 0.39 and 0.86. |

Using a Beta(2, 2) prior, which gently favours the middle.

##### Conjugate priors

A prior is conjugate if the posterior has the same form. For a yes-or-no rate, Beta(α, β) is conjugate. See k successes in n trials, and the posterior is Beta(α + k, β + n − k). You can read α and β as pretend earlier successes and failures, so a stronger prior is simply more pretend data.

| Data | Conjugate prior | Used for |
|---|---|---|
| Yes or no | Beta | Click rates, A/B tests, bandits |
| Categories | Dirichlet | Word counts, topic models, Laplace smoothing |
| Counts | Gamma | Event rates |
| Gaussian mean | Gaussian | Bayesian linear regression |

These all belong to the **exponential family**, where this pattern of adding counts is common.

##### Using the posterior

- **Credible interval:** "given the data and prior, there's a 95% chance the value is in this range". That's the reading many people wrongly give a confidence interval.

- **Prediction:** average over every possible value, weighted by the posterior, rather than trusting one. This accounts for uncertainty.

- **Decisions:** "what's the chance B beats A?" is a direct question you can answer.

##### Why it's usually hard

The denominator, p(data), averages over every possible parameter value. For neural networks, that's an integral over millions of dimensions. So we approximate with sampling, or with variational methods.

#### The maths

$$ p(\theta \mid D) = \frac{p(D \mid \theta)\,p(\theta)}{\int p(D \mid \theta)\,p(\theta)\,d\theta}, \qquad \mathrm{Beta}(\alpha, \beta) \to \mathrm{Beta}(\alpha + k,\; \beta + n - k) $$

Worked example: Beta(2, 2) with 7 successes in 10 gives Beta(9, 5), with a mean of 9/14 ≈ 0.64.

- **the posterior**: Your updated belief about θ, given the data.

- **the likelihood**: How well each value of θ explains the data.

- **the prior**: What you believed beforehand.

- **the evidence**: A normalising integral over every θ. It’s usually what makes this hard.

- **the conjugate update**: With a Beta prior and yes-or-no data, you just add counts, with no integral needed.

## In practice

### In practice

#### In practice

- **New items:** Bayesian averages stop a new item with 1 of 1 from outranking one with 950 of 1,000. They shrink small samples towards a sensible average.

- **Thompson sampling:** sample from each option's posterior, and pick the highest. It explores uncertain options naturally. See bandits.

- **Choosing a prior:** use past data where you can. State it, and test whether your conclusions change with a different one.

- **Deep learning:** full Bayesian networks are costly, so people approximate uncertainty with ensembles or dropout at prediction time.

- **Laplace smoothing:** adding 1 to counts in Naive Bayes is a Dirichlet prior in disguise.

### The answer that sounds right

#### "Priors make it subjective, so avoid them"

It sounds right, as a prior is a choice. But MLE isn't neutral either: it says 1 of 1 means 100%, which nobody believes. You can base a prior on past data, state it openly and test how much it matters. With enough data, its effect fades anyway.

## Say it

### What does Bayesian inference give you that MLE and MAP don't, and what is a conjugate prior?

#### The interviewer pushes further

Follow-up 1 of 3

What's the difference between a credible interval and a confidence interval?

A 95% credible interval says that, given the data and prior, the value has a 95% chance of being in that range. A 95% confidence interval says that this procedure captures the true value in 95% of repeated samples. They can be numerically close, but mean different things, and only the credible interval directly answers what people usually want.

Follow-up 2 of 3

You're ranking items by rating. One has 1 of 1 positive, and another 950 of 1,000. How do you handle that?

Don't use the raw rate. Use a posterior mean with a prior from typical items, or rank by a lower bound on the rate. With Beta(2, 2), the first item gets 3/5 = 0.6, and the second about 0.948, so it correctly ranks higher.

Follow-up 3 of 3

When does the prior stop mattering?

As data grows, the likelihood dominates, because it multiplies with each sample, and the prior stays fixed. So Bayesian answers converge with MLE. The prior matters most with little data, or when it rules out certain values with zero probability, which no amount of data can then fix.

MLE and MAP give one value. Bayesian inference keeps a whole distribution, so I also know how uncertain I am. The posterior is proportional to the likelihood times the prior. A conjugate prior keeps the same form: with a Beta prior and yes-or-no data, I just add successes and failures to its parameters. The posterior gives credible intervals and predictions averaged over uncertainty. With lots of data, the prior stops mattering. For complex models, the normalising integral is intractable, so I'd use sampling or variational methods.

**Key terms and sources**

Updating a full distribution over parameters, Beta-Binomial as a worked example, credible intervals, predictive distributions, and why the evidence integral is hard.

#### Sources

- Deisenroth, Faisal and Ong, Mathematics for Machine Learning

- Murphy, Probabilistic Machine Learning: An Introduction

- MLE and MAP on this site

Explanations are ours, built from these sources. Lab numbers are illustrative, and worked examples were checked by calculation.
