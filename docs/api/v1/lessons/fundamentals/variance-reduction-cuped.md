# Variance Reduction with CUPED

> Your test would take six weeks to reach power. How can you shorten it without losing validity?

- Track: Fundamentals › A/B Testing › Reading the result
- Type: Concept · 15 min
- Page: https://aimlrounds.com/tracks/fundamentals/variance-reduction-cuped/
- Before this: Sample Size, Power and Runtime (`fundamentals/sample-size-and-power`)
- Quiz topic: `ab`

## Intuition

### The situation

You need 200,000 users per group, and at 15,000 eligible users a day, that's nearly a month. The metric is orders per user, and some users order many times more than others. The interviewer asks:

> Your test would take six weeks to reach power. How can you shorten it without losing validity?

#### Why it matters

Runtime is what limits how many ideas a team can test. Cutting the required users in half has the same effect as doubling your traffic, for free. That's why large experimentation platforms use it by default.

### The idea

Think of measuring whether a new training plan makes runners faster. Fast runners stay fast, and that spread hides the effect. So compare each runner against their own time from before the plan. The gaps between runners vanish, and the plan's effect stands out.

[Figure: CUPED. The raw metric has noise from heavy and light users. The adjusted metric removes what past behaviour predicts, with the same effect and less noise.]

_Bing reported about 50% less variance using this method._

### Play

**Try to break it.** Move the correlation from 0.7 down to 0.3, then up to 0.9.

#### How much can you save?

Illustrative traffic. Required users scale directly with variance. In practice, the correlation depends on your metric and on how many users have history. Round the final runtime up to full weeks.

Drop the correlation to **0.3**, and CUPED saves little. It works best for stable behaviours, like orders per user, and less well for rare events.

**Now say why:** why doesn't subtracting past behaviour change the effect you measure?

## Maths

### Maths

#### In one breath

Much of a metric's noise is simply that some users always do more than others. **CUPED** uses each user's **pre-experiment** behaviour to subtract that predictable part. The average effect stays the same, but the variance falls by **ρ²**, where ρ is the correlation between before and during. At ρ = 0.7, that's about half the variance, so about **half the users**. Bing reported about 50%.

#### Subtract what you already knew

Say you measure orders during the test. Some users order 20 times a month and some order once. That spread is real, but it has nothing to do with your change, and it hides the effect you're looking for.

1. For each user, take the same metric from **before the test**, called X.

2. Find how strongly X predicts the metric during the test, called Y.

3. Compute an adjusted metric: Y minus the part X predicts.

4. Run your usual test on the adjusted metric.

##### Why the result stays valid

Random assignment makes X the same on average in both groups, whichever group a user joined. So what you subtract has the same average on both sides, and the difference in means doesn't change. You only remove noise.

##### What can go wrong

- **The covariate must come from before the test:** if the change can affect X, you subtract part of the effect itself, which biases the result.

- **New users have no history:** give them a fixed value, or use another pre-experiment fact, like sign-up country. CUPED then helps less.

- **Weak predictors don't help much:** the gain depends on ρ², so a correlation of 0.3 only removes 9%.

#### The maths

$$ {Y^{adj}} = {Y} - {\theta}\,({X - \bar X}), \quad {\theta} = \frac{\mathrm{Cov}(X,Y)}{\mathrm{Var}(X)}, \quad {\mathrm{Var}(Y^{adj})} = \mathrm{Var}(Y)(1-\rho^2) $$

From Deng, Xu, Kohavi and Walker (WSDM 2013). Calculate θ on the pooled data of both groups, so it’s the same value for each.

- **adjusted metric**: What you run your test on.

- **metric during the test**: The raw value for each user.

- **the slope**: How much Y rises per unit of X. It’s the same as the slope from regressing Y on X.

- **pre-experiment value**: How far this user was from average before the test.

- **remaining variance**: A share ρ² of the variance is gone, where ρ is the correlation between X and Y.

## In practice

### In practice

#### In practice

- **Use the same metric from before:** it's usually the best predictor. A few weeks of history is a common starting point, so test what works for your metric.

- **It's a form of regression:** CUPED matches adjusting for X in a linear regression, so you may see it called that.

- **Check it on past tests:** run it on old experiments to measure the variance reduction you actually get.

- **Report the same effect:** the adjusted difference still estimates the same lift, so read it as usual.

##### Using a model as the covariate

One past metric is only one predictor. You can train an ML model on pre-experiment features to predict the metric, then use its prediction as X. Yandex reported 63% average variance reduction on loyalty metrics this way, 5.1 points better than the best method it compared with. The same rule applies: every feature must come from before the test, or you'll remove part of the effect.

### The answer that sounds right

#### "Control for anything that predicts the metric"

It sounds right, since more prediction means less noise. But anything measured during the test can be affected by your change. Subtract one of those, and you remove part of the effect, or add bias. Only use values fixed before exposure.

## Say it

### Your test would take six weeks to reach power. How can you shorten it without losing validity?

#### The interviewer pushes further

Follow-up 1 of 3

Why must the covariate be from before the experiment?

If treatment can affect it, it's no longer balanced between the groups. Subtracting it would remove part of the real effect, or add bias. Pre-experiment data can't be affected by the change, so it's safe.

Follow-up 2 of 3

What do you do about new users with no history?

Give them a fixed value, such as zero or the average, and adjust using an indicator for being new. They just get no variance reduction. Or use other things known before exposure, such as sign-up country or device.

Follow-up 3 of 3

Does CUPED change the size of the effect you measure?

Not on average. Both groups have the same expected pre-experiment value, so subtracting it leaves the expected difference unchanged. In any one test, the estimate can move a bit, because you've adjusted for chance imbalance, and that's where the precision comes from.

#### The 30-second answer

I'd use CUPED. Much of a metric's noise is that some users always do more than others, and that's predictable from their behaviour before the test. I subtract the predictable part, using theta equal to the covariance of before and during over the variance of before. Randomisation makes the before-values equal on average across groups, so the effect estimate doesn't change. Variance falls by rho squared, so at a correlation of 0.7, I need about half the users. The covariate must come from before the test.

**Key terms and sources**

CUPED uses each user's data from before the experiment to remove predictable noise, so tests need fewer users. · checked 7 Nov 2026

#### Sources

- [Deng, Xu, Kohavi and Walker, CUPED (WSDM 2013)](https://exp-platform.com/cuped/)

- [A walkthrough of CUPED and regression](https://dpananos.github.io/posts/2025-03-03-cuped)

- [Statsig documentation on variance reduction](https://docs.statsig.com/stats-engine/variance_reduction)

- [Poyarkov et al., Boosted Decision Tree Regression Adjustment (KDD 2016)](https://www.kdd.org/kdd2016/papers/files/adf0653-poyarkovA.pdf)

Lab numbers are illustrative unless a lab says otherwise. Explanations are ours, built from these sources and standard statistics.
