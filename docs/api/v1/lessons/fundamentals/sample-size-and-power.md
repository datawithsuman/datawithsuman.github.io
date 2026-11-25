# Sample Size, Power and Runtime

> How do you work out how long an A/B test must run?

- Track: Fundamentals › A/B Testing › Designing a test
- Type: Concept · 15 min
- Page: https://aimlrounds.com/tracks/fundamentals/sample-size-and-power/
- Before this: Hypothesis Tests, p-values & A/B Testing (`fundamentals/hypothesis-testing-and-ab-tests`), Choosing Metrics: OEC, Drivers and Guardrails (`fundamentals/choosing-ab-metrics`)
- Quiz topic: `ab`
- Sources checked: 2026-11-07 · Text last changed: 2026-11-20 · Version: 3005281955

## Intuition

### The situation

Checkout converts at 10%, and you want to detect a 5% relative lift. You get 20,000 eligible users a day. Your manager wants the answer by Friday. The interviewer asks:

> How do you work out how long an A/B test must run?

#### Why it matters

A test that's too small can miss real improvements, and when it does find a win, it tends to overstate it. Decide the size before launch, so nobody stops the test when the numbers happen to look good. This builds on hypothesis tests and power.

### The idea

Think of tuning in a faint radio station through static. A loud station comes through in seconds, but to pick out a quiet one, you have to listen for much longer. The quieter the signal, the longer you listen, and it gets much worse quickly.

[Figure: What changes the sample size. Halving the effect needs four times the users. Doubling the variance needs twice the users. Raising power from 80 to 90 percent needs about 1.3 times the users.]

_From the sample size formula, changing one thing at a time._

### Play

**Try to break it.** Change the lift from 5% to 10%, then drop the baseline from 10% to 2%.

#### Plan a test

Two equal groups, 5% two-sided significance, using the unpooled two-proportion formula. The rule of thumb only applies at 80% power. Assumes all eligible users join on their first day, while real weekly unique users grow more slowly.

Change the lift from **5%** to **10%**. The users needed fall by about four times. A lower baseline makes it worse: going from 10% to 2% conversion takes roughly five times the users for the same relative lift.

**Now say why:** why does a smaller effect cost so much more than a noisier metric?

## Maths

### Maths

#### In one breath

Choose the smallest effect worth detecting (the **MDE**), then use the variance, significance level and power to get users per group: about **16σ²/δ²** at 5% significance and 80% power. Divide by daily traffic for a runtime, and round up to **full weeks**. **Halving the effect means four times the users**, which is why small lifts are so expensive.

#### From effect to runtime

1. **Pick the MDE:** ask what's the smallest lift worth the cost of shipping. It's a business decision, not a statistical one.

2. **Estimate the variance:** use recent data for your metric. For a conversion rate p, it's p(1 − p).

3. **Set significance and power:** commonly 5% and 80%.

4. **Compute users per group** using the formula in the next section.

5. **Convert to a runtime:** total users divided by eligible users per day.

6. **Round up to full weeks:** people behave differently at weekends, so cover whole weekly cycles.

##### If it would take too long

- Choose a **more sensitive metric**, or cap outliers.

- Use **CUPED** to remove noise.

- **Trigger** the analysis to users who could actually see the change.

- Accept a **larger MDE**, or decide the test isn't worth running.

#### The maths

$$ {n} = \frac{({z_{1-\alpha/2} + z_{1-\beta}})^2 \cdot {2\sigma^2}}{{\delta^2}} \;\approx\; \frac{16\,\sigma^2}{\delta^2} $$

The 16 rule assumes 5% significance, 80% power and two equal groups. At 10% conversion and δ = 1 point: σ² = 0.09, so 16 × 0.09 ÷ 0.0001 = 14,400 per group.

- **users per group**: How many users each of the two groups needs.

- **confidence and power**: For 5% two-sided significance and 80% power this is (1.96 + 0.84)², about 7.85. Doubled, that gives the 16 in the rule of thumb.

- **metric variance**: A noisier metric needs more users. Doubling the variance doubles the users.

- **the effect to detect**: The minimum detectable effect in absolute terms. It’s squared, so halving it needs four times the users.

## In practice

### In practice

#### In practice

- **Absolute or relative:** a 5% relative lift on 10% is 10.0% to 10.5%. Say which you mean, because the formula uses the absolute difference.

- **Small tests overstate wins:** when power is low, only unusually large results reach significance. The lift you see is often larger than the real one.

- **Run at least a week or two:** even with huge traffic, you need to cover weekly cycles and see the effect settle.

- **Unequal splits cost power:** a 10/90 split needs more total users than 50/50.

- **Heavy-tailed metrics:** a few huge spenders can inflate the variance, so cap values or use a robust version of the metric. See Revenue and Heavy-Tailed Metrics. See Revenue and Heavy-Tailed Metrics. See Revenue and Heavy-Tailed Metrics. See Revenue and Heavy-Tailed Metrics.

### The answer that sounds right

#### "Let's run it until it's significant"

It sounds right, since more data seems safer. But with no planned size, you'll stop when noise happens to look good, and your false-win rate climbs. It also says nothing about how long is reasonable. Fix the size in advance from the smallest effect worth shipping.

## Say it

### How do you work out how long an A/B test must run?

#### The interviewer pushes further

Follow-up 1 of 3

Where does the 16 come from?

At 5% two-sided significance and 80% power, the z values are 1.96 and 0.84. Their sum squared is about 7.85, and doubling that for two groups gives about 16. It changes if you change the power or significance level.

Follow-up 2 of 3

You have huge traffic, and could finish in one day. Do you?

No. A single day misses weekly patterns and can't show whether the effect fades or grows. I'd run for at least one full week, and usually two. Traffic only tells you the minimum needed for power.

Follow-up 3 of 3

A test with low power found a significant 8% lift. Do you believe it?

With caution. Low-powered tests only reach significance when noise pushes the result high, so the real lift is probably smaller. It may even be a false positive. I'd look at the confidence interval and rerun it with proper power if the decision matters.

#### The 30-second answer

I'd pick the smallest effect worth shipping, estimate the metric's variance from recent data, and set 5% significance and 80% power. That gives about 16 sigma squared over delta squared users per group. Then I divide by eligible daily traffic and round up to full weeks to cover weekly cycles. Halving the effect needs four times the users. If that's too long, I'd use a more sensitive metric, CUPED or triggering, or accept a larger minimum effect.

**Key terms and sources**

Minimum detectable effect, power and the sample size formula, and how to turn them into a runtime in full weeks. · checked 7 Nov 2026

#### Sources

- Hypothesis tests and power on this site

- [Kohavi, Tang and Xu, Trustworthy Online Controlled Experiments (2020), excerpt](https://assets.cambridge.org/97811087/24265/excerpt/9781108724265_excerpt.pdf)

Lab numbers are illustrative unless a lab says otherwise. Explanations are ours, built from these sources and standard statistics.
