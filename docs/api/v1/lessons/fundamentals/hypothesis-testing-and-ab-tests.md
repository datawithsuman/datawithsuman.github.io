# Hypothesis Tests, p-values & A/B Testing

> Why peeking at your A/B test every day breaks it.

- Track: Fundamentals › Maths for ML › Statistics
- Type: Concept · 30 min
- Page: https://aimlrounds.com/tracks/fundamentals/hypothesis-testing-and-ab-tests/
- Before this: Confidence Intervals & the Bootstrap (`fundamentals/confidence-intervals-and-bootstrap`)
- Related: Randomisation and Assignment (`fundamentals/randomisation-and-assignment`)
- Quiz topic: `stats`

## Intuition

### The situation

After a week, your new checkout button converts at 10.4% against 10.0%, and the product manager wants to ship it. The interviewer asks:

> How would you run an A/B test, and what does the p-value mean?

**Running example:** the food-delivery app tests a new checkout button. 10% of visitors to checkout currently place an order (conversion rate). The product team hopes the new button lifts it to 11%, a 10% relative lift. How many users does the test need, and how do we read the result?

#### Is a 0.4-point lift real?

After a week, B converts at 10.4% and A at 10.0%. With a few thousand users per arm, a difference that size appears by chance alone fairly often. Shipping on noise wastes effort and can hurt the product; ignoring real wins leaves money on the table. Hypothesis testing gives a disciplined way to decide, and its failure modes are classic ML and product-sense interview questions.

### The idea

Think of a coin you suspect is biased. A few heads in a row proves little. An A/B test asks how surprising your result would be if nothing had changed. And flipping until you like the answer doesn't count.

[Figure: A bell curve showing results if nothing changed. A marker shows the observed result, and the shaded tail beyond it is the p-value.]

_Illustrative. The p-value assumes no real difference, so it isn't the chance that B is better._

### Play

**Try to break it.** Compare checking once at day 20 with checking daily and stopping at the first p below 0.05. Neither arm has any real difference here.

#### Checking every day inflates false positives

A/A tests: both arms are identical (10% conversion, 500 users per arm per day, 20 days). Lines show the z-statistic over time for 30 of the tests; the band is ±1.96.

With no real difference at all, a single check at the planned end gives about **5%** false positives, as designed. Checking every day and stopping at the first p < 0.05 gives about **25%**: the z-statistic wanders, and with 20 looks it will often cross 1.96 at some point. Johari, Pekelis & Walsh show that with continuous monitoring and an unlimited horizon a false positive is eventually guaranteed, and propose "always valid" p-values that allow stopping at any time arXiv:1512.04922. Fixes: pre-commit to a sample size, use sequential tests (alpha-spending, mSPRT), or Bayesian methods with care.

**Now say why:** why does looking more often create false wins when nothing changed?

## Maths

### Maths

#### In one breath

An A/B test randomly splits users between the old version (A) and a new one (B) and asks whether the difference in a metric is real or noise. Assume **no difference** (the null), compute how surprising the observed difference would be under that assumption: that's the **p-value**. If p < 0.05 you call it significant, accepting a 5% false-positive rate (type I error). **Power** is the chance of detecting a real effect; it depends on effect size, variance and sample size, so small lifts need big samples, decided **before** the test. The classic mistake is **peeking**: checking daily and stopping at the first p < 0.05 inflates false positives from 5% to about 25%.What you'll be able to do after this: run a two-proportion test, interpret a p-value correctly, compute the sample size for a target lift, and explain why peeking, multiple metrics and novelty effects mislead.

#### Null, test statistic, p-value

$$ z = (\hat p_B - \hat p_A) \,/\, \sqrt{\bar p(1-\bar p)\,(1/n_A + 1/n_B)}, \qquad p = 2\,(1 - \Phi(|z|)) $$

The two-proportion z-test (Wasserman §10.1–10.2). With 5,000 users per arm, 10.4% vs 10.0% gives z ≈ 0.66 and p ≈ 0.51: not distinguishable from noise.

- **test statistic**: How many standard errors apart the two conversion rates are.

- **observed difference**: B’s rate minus A’s rate.

- **standard error under the null**: Using the pooled rate p̄ of both arms: the spread the difference would have if there were no real effect.

- **p-value**: Two-sided: the probability, assuming no real difference, of a |z| at least this large. Small p = the data would be surprising if nothing changed.

#### Two kinds of error, and power

| | No real effect | Real effect |
|---|---|---|
| **Declare a win (p < α)** | Type I error (false positive), rate α = 5% | Correct: probability = power |
| **No win** | Correct | Type II error (false negative), rate β = 1 − power |

$$ n \approx (z_{1-\alpha/2} + z_{1-\beta})^2\,\bigl[p_A(1-p_A) + p_B(1-p_B)\bigr] \,/\, (p_B - p_A)^2 $$

Standard normal-approximation sample size for two proportions; see Kohavi, Tang & Xu (2020). For 10% → 11%: n ≈ 14,750 users per arm.

- **users per arm**: For a two-sided test at α = 0.05 with 80% power.

- **the two error rates**: 1.96 for α = 0.05 two-sided, 0.84 for 80% power. Stricter tests or more power need more users.

- **variance of the metric**: Noisier metrics need more data.

- **minimum detectable effect, squared**: Halving the effect you want to detect quadruples the sample size.

#### Power calculator

With 10,000 users per arm, the test has only a 64% chance of detecting a real 10% → 11% lift; 14,750 per arm reaches 80%. A 5% relative lift needs about 57,800 per arm; a 20% lift only about 3,800. Small lifts on low conversion rates are expensive to detect, which is why teams set a minimum detectable effect and the duration **before** launching.

#### Which test do I use?

| Question | Data | Test |
|---|---|---|
| Two groups differ? | Numbers | Welch's t-test |
| The same subjects changed? | Numbers | Paired t-test |
| Two rates differ? | Yes or no | Two-proportion z-test |
| Are two categories related? | Categories | Chi-squared |
| Three or more group means differ? | Numbers | ANOVA |
| Small, skewed data, or an unusual statistic? | Any | Mann-Whitney or a permutation test |

##### Report the effect size too

A p-value tells you whether there's evidence of a difference, not how large it is. With enough data, tiny effects become significant. So report the difference with its interval, and a standardised size if you're comparing across metrics, like Cohen's d: the difference in means divided by the standard deviation.

## In practice

### In practice

#### More things that break A/B tests

- **Multiple comparisons:** testing 20 metrics or segments at α = 0.05 gives about one false "win" by chance. Pick a primary metric in advance; correct for multiplicity (Bonferroni, Benjamini–Hochberg).

- **Sample ratio mismatch:** if the split isn't the planned 50/50, assignment or logging is broken; Kohavi et al. recommend checking this first.

- **Novelty and primacy effects:** users react to change itself; run long enough (full weekly cycles).

- **Interference:** in marketplaces (riders, restaurants) treatment users can affect control users; randomise by city or time (switchback tests).

- **Unit of randomisation vs analysis:** randomising users but analysing orders understates variance (orders from one user are correlated).

Kohavi, Tang & Xu, _Trustworthy Online Controlled Experiments_, Cambridge University Press 2020.

### The answer that sounds right

#### "p = 0.03 means a 97% chance B is better"

The p-value is computed _assuming_ there's no difference; it can't be the probability that there is one. The American Statistical Association's statement lists the correct reading and the common misreadings: "P-values can indicate how incompatible the data are with a specified statistical model"; they do not measure "the probability that the studied hypothesis is true, or the probability that the data were produced by random chance alone"; and "a p-value, or statistical significance, does not measure the size of an effect or the importance of a result" ASA 2016. Report the effect size with a confidence interval alongside the p-value.

## Say it

### How would you run an A/B test, and what does the p-value mean?

#### The interviewer pushes further

Follow-up 1 of 3

Your test is significant at p = 0.04 after you checked it daily. Ship?

Not yet: daily peeking inflates false positives well above 5%. Re-run with a fixed horizon or analyse with a sequential method; also check effect size and guardrail metrics.

Follow-up 2 of 3

How do you choose the sample size?

From baseline rate, MDE, α and power: n ≈ (1.96 + 0.84)² [p₁(1 − p₁) + p₂(1 − p₂)]/(p₂ − p₁)² per arm, then convert to duration using traffic, rounding up to full weeks.

Follow-up 3 of 3

The test is flat but you believe the feature helps. What now?

Check power (was it sized to detect a realistic effect?), segment heterogeneity (pre-registered only), metric sensitivity and variance reduction (CUPED), and implementation bugs.

#### The 30-second answer

An A/B test randomises users into control and treatment and tests the null hypothesis of no difference. The p-value is the probability of seeing a difference at least as large if the null were true; below the significance level, typically 0.05, we reject the null, accepting a 5% false-positive rate. Before launching, I'd fix the primary metric, the minimum detectable effect and the sample size for 80% power; small lifts on low baselines need tens of thousands of users per arm. I'd avoid peeking or use sequential methods, correct for multiple metrics, check sample-ratio mismatch, and report the effect size with a confidence interval, not just the p-value.

**Go further**

#### What not to say

- "p = 0.03 means 97% chance B is better."

- "Not significant means no effect." It may be underpowered.

- "Let's run until it's significant."

**Key terms and sources**

Null and alternative hypotheses, test statistics and p-values, significance, type I and II errors, power and sample size, the peeking problem, and how online experiments are run · built from the ASA Statement on p-values (2016), Kohavi, Tang & Xu, _Trustworthy Online Controlled Experiments_ (2020), Johari et al. (2017) and Wasserman, _All of Statistics_ (ch. 10) · checked 28 Oct 2026

#### Key terms

| Term | Meaning |
|---|---|
| **Null hypothesis** | No difference between variants. |
| **p-value** | P(data at least this extreme \| null true). |
| **α / significance level** | Tolerated false-positive rate (often 5%). |
| **Power** | P(detect \| real effect of the planned size), often 80%. |
| **MDE** | Minimum detectable effect the test is sized for. |
| **Peeking** | Repeatedly checking and stopping early on significance. |

#### Sources

1. R. Wasserstein & N. Lazar, "The ASA statement on p-values: context, process, and purpose", _The American Statistician_ 70(2), 2016, doi.

2. R. Kohavi, D. Tang & Y. Xu, _Trustworthy Online Controlled Experiments: A Practical Guide to A/B Testing_, Cambridge University Press 2020.

3. R. Johari, L. Pekelis & D. Walsh, "Always valid inference: bringing sequential analysis to A/B testing", arXiv:1512.04922; "Peeking at A/B tests", KDD 2017.

4. L. Wasserman, _All of Statistics_, Springer 2004, ch. 10.

A/A tests and power curves are simulated or computed live in your browser.
