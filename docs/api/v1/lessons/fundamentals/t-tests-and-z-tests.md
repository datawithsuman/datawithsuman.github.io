# T-Tests and Z-Tests

> What's the difference between a t-test and a z-test, and when would you use a paired test?

- Track: Fundamentals › Maths for ML › Statistics
- Type: Concept · 15 min
- Page: https://aimlrounds.com/tracks/fundamentals/t-tests-and-z-tests/
- Before this: Hypothesis Tests, p-values & A/B Testing (`fundamentals/hypothesis-testing-and-ab-tests`)
- Quiz topic: `stats`

## Intuition

### The situation

You compared two models on the same 10 folds, and a colleague ran an unpaired test, finding no significant difference. Someone else used a z-test on just 8 samples, and is very confident. The interviewer asks:

> What's the difference between a t-test and a z-test, and when would you use a paired test?

#### Why it matters

The t-test is the most commonly used statistical test. It's the basis of comparing model scores and user metrics, and a common interview question. This builds on hypothesis tests, and gives you what the z-test leaves out.

### The idea

Think of two runners. You could compare a group of runners on one shoe with another group on another shoe, but people differ hugely. Better, have the same people run in both pairs. Their own speed cancels out, so you can see the difference between the shoes. That's why pairing helps.

[Figure: Three tests. A z-test assumes a known spread. A t-test estimates the spread, with heavier tails. A paired test uses differences within the same subjects.]

_Choose by what you know, and how the data was collected._

### Play

**Try to break it.** Set the samples to 3, and compare t with z. Then raise the correlation.

#### Run the same data as unpaired and paired

Calculated exactly from the summary numbers. The z-test uses the same statistic, wrongly treating the sample's spread as known, so its p-value is too small at low n.

Set the samples to **3**: t's cutoff rises to 2.78, and z's p-value is too low. Raise them to **200**, and the cutoff is nearly 1.96. Then drag the correlation up. The difference and spreads don't change, yet the paired test gets much stronger.

**Now say why:** why does correlation between pairs make the test stronger?

## Maths

### Maths

#### In one breath

Both tests ask how many standard errors a difference is from zero. A **z-test** assumes you know the population's spread. A **t-test** estimates it from the sample, which adds uncertainty, so it uses a **t-distribution with heavier tails**. With a large sample, they match. Use a **paired test** when measuring the same things twice, as removing differences between subjects makes it far more sensitive. Use **Welch's** version as your default for two groups.

#### Which test, and why

| Test | Question | Example |
|---|---|---|
| **One-sample** | Does this mean differ from a target? | Is average delivery time different from 30 minutes? |
| **Two-sample (Welch)** | Do two separate groups differ? | Do users on A and B spend different amounts? |
| **Paired** | Did the same subjects change? | Two models scored on the same 50 test folds. |
| **Two-proportion z** | Do two rates differ? | Conversion in an A/B test. |

##### Why t has heavier tails

With a small sample, your estimate of the spread is itself noisy. Sometimes it's too small, making the statistic look bigger than it should. The t-distribution allows for this, by making extreme values more likely. The smaller the sample, the stronger the correction: the 5% cutoff is 2.78 with 4 degrees of freedom, and approaches 1.96 as the sample grows.

##### Degrees of freedom

These count how many values are free to vary. After you've used the sample's mean, the last value is fixed, so a one-sample test has n − 1. Think of it as how much information you have left to estimate the spread.

##### Why pairing is powerful

People or test sets differ a lot from each other. A paired test works on each subject's difference, so those differences cancel. The more correlated the pairs, the larger the gain. When comparing two models, always use the same test data, and pair the results.

##### What the tests assume

- **Independence:** this is the serious one. Correlated rows make it far too optimistic.

- **Roughly Normal averages:** fine with large samples, thanks to the central limit theorem. With small, skewed samples, consider a non-parametric test.

- **Equal variances:** the classic version assumes this, and Welch's doesn't, so prefer Welch's.

#### The maths

$$ t = \frac{\bar x_1 - \bar x_2}{\sqrt{s_1^2/n_1 + s_2^2/n_2}}, \qquad t_{\text{paired}} = \frac{\bar d}{s_d / \sqrt{n}}, \qquad s_d^2 = s_1^2 + s_2^2 - 2\rho s_1 s_2 $$

Worked example: n = 16, mean 52, s = 8, testing against 50. SE = 8 ÷ 4 = 2, so t = 1, with 15 degrees of freedom. That’s not significant.

- **the t statistic**: How many standard errors apart the two means are.

- **the observed difference**: The signal you’re checking.

- **the standard error**: Noise in the difference, using spreads estimated from the sample.

- **the paired version**: Works on each pair’s difference, and has n − 1 degrees of freedom.

- **why pairing helps**: Strong positive correlation ρ makes the spread of the differences much smaller.

## In practice

### In practice

#### In practice

- **In A/B tests with many users:** t and z give almost the same answer, so the difference rarely matters at scale.

- **Comparing models:** use the same test set, and a paired test on per-example or per-fold results. Cross-validation folds overlap, so they aren't truly independent, and results can be overconfident.

- **Check independence first:** treating many events from one user as separate samples is the most common way these tests go wrong.

- **One-sided tests:** only use them if you decided the direction beforehand, and the other direction would truly make no difference.

### The answer that sounds right

#### "Use a t-test whenever the sample is under 30"

It sounds right, as it's a popular rule. But you almost never know the true spread, so a t-test is the right choice at any size, and it simply converges to z. Thirty also doesn't guarantee Normal averages, as skewed data can need far more. The more important question is whether your samples are independent.

## Say it

### What's the difference between a t-test and a z-test, and when would you use a paired test?

#### The interviewer pushes further

Follow-up 1 of 3

Why does the t-test use n − 1 degrees of freedom?

Estimating the spread uses the sample's own mean, which uses up one piece of information. Given the mean, the last value is determined. So you have n − 1 values free to vary, and this sets the shape of the t-distribution, which has heavier tails with fewer degrees of freedom.

Follow-up 2 of 3

How would you test whether model B is better than model A?

Score both on the same test examples, and compare with a paired test on per-example results, like a paired t-test, a McNemar test for accuracy or a bootstrap of the differences. Pairing removes the difficulty of each example. Report the effect size too, not only significance.

Follow-up 3 of 3

When does a t-test mislead you?

When samples aren't independent, like many clicks from one user, as it underestimates noise. Also with small samples from very skewed or heavy-tailed data, and when you've run many tests, or stopped early. Independence is the most serious, as a larger sample doesn't fix it.

Both ask how many standard errors a difference is from zero. A z-test assumes the population's spread is known, while a t-test estimates it, adding uncertainty, so it uses a t-distribution with heavier tails. With large samples, they match. For two groups, I'd default to Welch's t-test, which doesn't assume equal variances. If I'm measuring the same subjects twice, like two models on the same test folds, I'd use a paired test: differences between subjects cancel, which makes it much more sensitive. The key assumption is independence.

**Key terms and sources**

One-sample, two-sample and paired t-tests, degrees of freedom, Welch's correction, how the t differs from z, and when to use each.

#### Sources

- Diez, Çetinkaya-Rundel and Barr, OpenIntro Statistics

- Bruce, Bruce and Gedeck, Practical Statistics for Data Scientists, contents excerpt

- Wasserman, All of Statistics

Explanations are ours, built from these sources. Lab numbers are illustrative, and worked examples were checked by calculation.
