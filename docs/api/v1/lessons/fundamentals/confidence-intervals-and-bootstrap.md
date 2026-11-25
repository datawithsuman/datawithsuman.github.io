# Confidence Intervals & the Bootstrap

> What does 95% confidence actually promise?

- Track: Fundamentals › Maths for ML › Statistics
- Type: Concept · 25 min
- Page: https://aimlrounds.com/tracks/fundamentals/confidence-intervals-and-bootstrap/
- Before this: Expectation, Variance & Covariance (`fundamentals/expectation-and-variance`)
- Quiz topic: `stats`
- Sources checked: 2026-10-28 · Text last changed: 2026-11-20 · Version: 8759dbb2f1

## Intuition

### The situation

You report 87% accuracy on 500 test rows, and a stakeholder asks how sure you are. The interviewer asks:

> What does a 95% confidence interval actually mean, and when would you use the bootstrap?

**Running example:** delivery times in minutes, simulated from a right-skewed distribution (log-normal: median 30 minutes, true mean 34.0 minutes, a long tail of slow deliveries). Operations samples n deliveries and reports the average delivery time with a 95% interval.

#### A number without an error bar is a guess

"Average delivery time: 33.1 minutes" from 30 deliveries could easily be 36 on the next 30. "Model accuracy 87.2%" on 500 test rows has an uncertainty of about ±3 points. Interviewers and stakeholders ask "how sure are you?" and a confidence interval is the standard answer, provided you know what it means and when it's off.

### The idea

Think of throwing a ring at a hidden peg. Once it lands, it either circles the peg or it doesn't. The 95% describes how good your throw is: about 95 of every 100 throws land around the peg.

[Figure: Eight horizontal intervals around a vertical line marking the true mean. Seven cross the line. One misses it and is drawn in red.]

_Illustrative. Each line is one sample's interval, and most of them cover the true mean._

### Play

**Try to break it.** Start at n = 10 and read the coverage. Then move up to n = 100.

#### Draw 100 samples, build 100 intervals

Each horizontal line is one sample's 95% t-interval; the orange vertical line is the true mean (34.0 min). Red lines miss it.

With skewed data the t-interval under-covers for small n: about 92.5% at n = 10 and 93.7% at n = 30 instead of 95%, approaching 95% by n = 50–100 as the central limit theorem kicks in. Intervals also narrow like 1/√n. For heavy tails or tiny samples, report this caveat, transform the data (log), or use the bootstrap.

**Now say why:** why do intervals on skewed data miss more often when the sample is small?

## Maths

### Maths

#### In one breath

Any number computed from a sample (a mean, a median, an accuracy) would come out different on another sample. Its spread across samples is the **sampling distribution**; its standard deviation is the **standard error**, σ/√n for a mean. The **central limit theorem** says means are roughly Gaussian for large n, so mean ± 1.96 × SE gives a **95% confidence interval**: a procedure that captures the true value in about 95% of repeated samples (not "95% chance the truth is in this one interval"). With small or skewed samples coverage drops below 95%. The **bootstrap** resamples your own data thousands of times to get intervals for any statistic, no formula needed. What you'll be able to do after this: compute a CI for a mean, state its correct interpretation, explain when it's unreliable, and build a bootstrap CI for a median or a model metric.

#### Standard error and the CLT

$$ {\mathrm{SE}(\bar x)} = {s}\,/\,\sqrt{n}, \qquad {\bar x \pm t_{0.975,\,n-1}\,\mathrm{SE}} $$

Wasserman, _All of Statistics_ §6.3.2, §7; the central limit theorem (Blitzstein & Hwang §10.3) makes x̄ approximately Gaussian for large n whatever the shape of the data.

- **standard error of the mean**: How much the sample mean varies from sample to sample. Shrinks like 1/√n: four times the data halves it.

- **sample standard deviation**: Spread of individual deliveries, estimated from the sample.

- **95% interval**: Sample mean ± about 2 standard errors (1.96 from the Gaussian; a slightly larger t value for small n).

#### Resample your own data to see the sampling distribution

Efron (1979) noticed that if your sample is representative, drawing samples _from your sample_ (n draws with replacement) mimics drawing new samples from the population. Compute the statistic on each of, say, 2,000 resamples; the spread of those values estimates its sampling distribution. The simplest 95% interval takes the 2.5th and 97.5th percentiles (the percentile bootstrap); refinements such as BCa correct for bias and skew.

One sample of 50 deliveries, 2,000 bootstrap resamples. There's no simple formula for the standard error of a median or a 90th percentile; the bootstrap doesn't need one.

#### Small samples: the t-interval

With a small sample, your estimate of the spread is itself uncertain, so 1.96 standard errors is too narrow. Use the t-distribution's multiplier instead: about 2.13 with 15 degrees of freedom, and 2.78 with 4. It approaches 1.96 as the sample grows.

See t-tests and z-tests for why, and the central limit theorem for why these intervals work at all.

## In practice

### In practice

#### Error bars for models and metrics

- **Test-set metrics:** accuracy p on n test rows has SE ≈ √(p(1 − p)/n): 87% on 500 rows is ±2.9 points (95%). Small test sets can't separate models 1–2 points apart.

- **Bootstrap a metric:** resample test rows to get intervals for AUC, F1 or MAE; resample both models' predictions together to compare them fairly (paired).

- **Bagging:** the bootstrap is literally how random forests make each tree's training set (Random Forest).

- **A/B tests:** intervals for the difference between variants (next lesson).

### The answer that sounds right

#### "There's a 95% chance the true mean is in my interval"

In the frequentist framework, the true mean is a fixed number; this particular interval either contains it or doesn't. The 95% describes the **procedure**: if you repeated the sampling many times, about 95% of the intervals built this way would contain the truth. The lab in the Intuition tab shows 100 such intervals at once. (A Bayesian credible interval does support the "95% probability" reading, given a prior.)

#### Caveats

- Both methods assume independent observations; repeated orders from the same customer need clustered or block resampling.

- The bootstrap can't invent information: with n = 10 the interval is unreliable too; extreme statistics (max, min) bootstrap badly.

- "Statistically significant" isn't "important": a tiny difference can have a tight interval with lots of data.

## Say it

### What does a 95% confidence interval actually mean, and when would you use the bootstrap?

#### The interviewer pushes further

Follow-up 1 of 3

How many test examples do I need to measure accuracy to ±1 point?

95% half-width 1.96√(p(1 − p)/n) ≤ 0.01; at p ≈ 0.85, n ≈ 1.96² × 0.1275 / 0.0001 ≈ 4,900.

Follow-up 2 of 3

When does the bootstrap fail?

Tiny samples, dependent data (use block bootstrap), statistics at the extremes (max), and heavy-tailed distributions without enough data.

Follow-up 3 of 3

Confidence interval vs credible interval?

Frequentist: a procedure with 95% coverage over repetitions. Bayesian: given the prior and data, the parameter lies in the interval with 95% posterior probability.

#### The 30-second answer

A statistic like a sample mean varies from sample to sample; its standard deviation is the standard error, s over root n for a mean. By the central limit theorem the mean is roughly Gaussian, so mean plus or minus about two standard errors is a 95% confidence interval, meaning the procedure captures the true value in 95% of repeated samples, not that this interval has a 95% probability. With small or skewed samples, coverage falls short. The bootstrap resamples the observed data with replacement thousands of times to estimate the sampling distribution of any statistic, such as a median, AUC or F1, and the percentiles give an interval.

**Go further**

#### What not to say

- "There's a 95% chance the true value is in this interval" (for a frequentist CI).

- "Non-overlapping intervals are needed for a significant difference." Overlapping CIs can still differ significantly; test the difference directly.

**Key terms and sources**

Sampling distributions, standard error, the central limit theorem, what a 95% confidence interval does and doesn't mean, coverage with skewed data, and bootstrap intervals for any statistic · built from Wasserman, _All of Statistics_ (ch. 6–8), Efron (1979), Efron & Tibshirani, _An Introduction to the Bootstrap_, and Blitzstein & Hwang (ch. 10) · checked 28 Oct 2026

#### Key terms

| Term | Meaning |
|---|---|
| **Sampling distribution** | How a statistic varies across repeated samples. |
| **Standard error** | Std dev of a statistic; s/√n for a mean. |
| **Central limit theorem** | Means of many independent draws are approximately Gaussian. |
| **Coverage** | How often the interval procedure contains the truth. |
| **Bootstrap** | Resampling the data with replacement to estimate sampling variability. |

#### Sources

1. L. Wasserman, _All of Statistics_, Springer 2004, ch. 6–8.

2. B. Efron, "Bootstrap methods: another look at the jackknife", _Annals of Statistics_ 7(1), 1979; B. Efron & R. Tibshirani, _An Introduction to the Bootstrap_, Chapman & Hall 1993.

3. J. Blitzstein & J. Hwang, _Introduction to Probability_, 2nd ed., 2019, §10.3 (central limit theorem), [stat110](https://projects.iq.harvard.edu/stat110).

Delivery times are simulated (log-normal) with fixed seeds; intervals and bootstraps are computed live in your browser.
