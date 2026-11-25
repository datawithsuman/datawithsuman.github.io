# Multiple Testing and Segments

> You tested 20 metrics and one came back significant. Is it a real win?

- Track: Fundamentals › A/B Testing › Reading the result
- Type: Concept · 15 min
- Page: https://aimlrounds.com/tracks/fundamentals/multiple-testing/
- Before this: Reading the Result: Significance and Decisions (`fundamentals/reading-ab-results`)
- Quiz topic: `ab`
- Sources checked: 2026-11-07 · Text last changed: 2026-11-20 · Version: c1761338a9

## Intuition

### The situation

Your experiment dashboard tracks 20 metrics. The main one is flat, but “session length on Android” is up with p = 0.03. The product manager wants to call it a win. The interviewer asks:

> You tested 20 metrics and one came back significant. Is it a real win?

#### Why it matters

Experiment dashboards show dozens of metrics across many countries and devices. Look long enough, and something always turns green. That's how teams ship changes that do nothing.

### The idea

Think of buying 20 lottery tickets. No single ticket is likely to win, but your chances of some win are far higher. A win from 20 tries is much less surprising than a win from one, and you should judge it that way.

[Figure: Three approaches for many metrics. No correction gives a 64 percent chance of a false win across 20 metrics. Bonferroni limits any false win. Benjamini-Hochberg limits the share of wins that are false.]

_The 64% assumes 20 independent metrics with no real effects._

### Play

**Try to break it.** Raise the metrics to 100, then lower the significance level. Then see which of the ten results survive.

#### Correct ten results

**Ten results from one test**, at the significance level above:

Illustrative p-values. The false-win figure assumes independent metrics.

The same ten p-values give **six**, **four** or **one** wins, depending on the method. None is simply right: choose by what a false win would cost you.

**Now say why:** why does a real effect usually move more than one metric?

## Maths

### Maths

#### In one breath

Each test at 5% has a 1 in 20 chance of a false positive, so **20 metrics with no real effect give at least one false win 64% of the time**. **Bonferroni** divides α by the number of tests, and controls the chance of any false win. **Benjamini-Hochberg** controls the share of wins that are false, and keeps more power. Better still, name **one primary metric** up front, and treat segment findings as new ideas to test.

#### Two kinds of error control

| | Family-wise error rate (FWER) | False discovery rate (FDR) |
|---|---|---|
| **What it limits** | The chance of even one false win. | The expected share of wins that are false. |
| **Common method** | Bonferroni: test each at α/m. | Benjamini-Hochberg. |
| **Use for** | A few metrics that decide a launch. | Screening many metrics for leads. |
| **Cost** | Strict, so you miss more real effects. | Some of your wins will be false. |

##### Benjamini-Hochberg steps

1. Sort the m p-values from smallest to largest.

2. Give the one at rank i the threshold (i / m) × α.

3. Find the largest rank whose p-value is below its threshold.

4. Call that one and all smaller ones significant.

##### Variants against one control

Comparing several variants with one control is also multiple testing. Dunnett's test is built for this case, and it's more powerful than Bonferroni.

##### Segments

- Slicing by country, device and user type is more testing, so "it worked for Android users in Brazil" may be noise.

- Treat an unplanned segment result as a **hypothesis**, and run a new test on it.

- Watch for **Simpson's paradox**: if the traffic split changes during a test, a change can win in every segment and lose overall. See correlation vs causation.

#### The maths

$$ {P(\text{at least one false win})} = 1 - (1 - {\alpha})^{{m}}, \qquad \text{Bonferroni threshold} = {\alpha}/{m} $$

Example: 20 metrics at 5% gives 1 − 0.95²⁰ ≈ 64%. Bonferroni then tests each one at 0.05 ÷ 20 = 0.0025.

- **chance of a false win**: For independent tests with no real effects. Real metrics are correlated, so this is an upper guide.

- **significance level**: Your error rate per test, commonly 5%.

- **number of tests**: Each metric, variant and segment you check counts towards this.

## In practice

### In practice

#### In practice

- **Tier your metrics:** one primary metric at the normal level. Guardrails get their own checks. Everything else is exploratory.

- **Write the plan first:** if the primary metric was chosen after seeing results, no correction can fix that.

- **Look for a story:** a real effect usually shows up in related metrics. A lone green metric among flat ones is a warning sign.

- **Replicate:** a new test on the surprising result is the strongest check.

- **Count honestly:** the number of tests includes everything you looked at, not only what you reported.

To model who benefits properly, read Heterogeneous Effects and Uplift Modelling.

### The answer that sounds right

#### "It's significant, and we had a good reason"

It sounds right, since a story makes it feel real. But it's easy to find a reason after the fact for any metric that turned green. Reasons have to come before the data. A surprising win is a good idea for the next test, not a result.

## Say it

### You tested 20 metrics and one came back significant. Is it a real win?

#### The interviewer pushes further

Follow-up 1 of 3

When would you choose Benjamini-Hochberg over Bonferroni?

When screening many metrics for leads, where a few false wins are acceptable and missing real effects is costly. For a launch decision on a few metrics, where one false win is expensive, I'd use Bonferroni or Holm.

Follow-up 2 of 3

The change lost overall, but won in India. Do you launch in India?

Not on that result. With many segments, one will look good by chance. I'd check whether it was planned, whether there's a real reason, and whether its size is plausible. Then I'd run a new test in India.

Follow-up 3 of 3

Is Bonferroni too conservative for correlated metrics?

Yes. It assumes the worst case, so with closely related metrics it's stricter than needed. Holm is uniformly more powerful, and a resampling-based method can account for correlation. For most teams, the bigger gain is simply reducing the metrics that decide the launch.

#### The 30-second answer

Probably not. Twenty tests at 5% with no real effects give at least one false win about 64% of the time. I'd name one primary metric before the test, so this doesn't arise. For a few decision metrics, I'd use Bonferroni, which tests each at alpha over m. For screening many, I'd use Benjamini-Hochberg, which controls the share of wins that are false, and keeps more power. Unplanned segment wins are new hypotheses, so I'd retest them.

**Key terms and sources**

Why testing many metrics, variants or segments creates false wins, and how Bonferroni and Benjamini-Hochberg correct for it. · checked 7 Nov 2026

#### Sources

- [Statsig, multiple comparison corrections in A/B testing](https://statsig.com/blog/multiple-comparison-corrections-in-a-b)

- [Convert, the Bonferroni correction](https://www.convert.com/blog/a-b-testing/bonferroni-test/)

- [Benjamini and Hochberg, Controlling the False Discovery Rate (1995)](https://doi.org/10.1111/j.2517-6161.1995.tb02031.x)

Lab numbers are illustrative unless a lab says otherwise. Explanations are ours, built from these sources and standard statistics.
