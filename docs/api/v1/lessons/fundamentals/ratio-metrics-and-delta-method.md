# Ratio Metrics and the Delta Method

> You randomise by user but measure click-through rate per page view. What goes wrong, and how do you fix it?

- Track: Fundamentals › A/B Testing › Reading the result
- Type: Concept · 15 min
- Page: https://aimlrounds.com/tracks/fundamentals/ratio-metrics-and-delta-method/
- Before this: Reading the Result: Significance and Decisions (`fundamentals/reading-ab-results`)
- Quiz topic: `ab`

## Intuition

### The situation

You randomise by user and track click-through rate as total clicks divided by total page views. A colleague runs a standard two-proportion test on page views and finds p = 0.01. The interviewer asks:

> You randomise by user but measure click-through rate per page view. What goes wrong, and how do you fix it?

#### Why it matters

Click-through rate, revenue per order and pages per session are all ratios of two things that vary by user. They're among the most common metrics in ML, and getting this wrong creates wins that don't exist.

### The idea

Think of surveying a town by asking one person a hundred questions, and calling it a hundred opinions. Their answers are all related. You have one person's view, not a hundred. Page views from one user work the same way.

[Figure: Two ways to count. Treating each page view as independent makes the standard error too small. Treating the user as the unit with the delta method gives an honest standard error.]

_Uncertainty should reflect the number of randomised users._

### Play

**Try to break it.** Set the correlation to 0.1, then raise the views per user to 50.

#### How wrong does the simple formula get?

Uses the design effect 1 + (m − 1)ρ, a simplified model that assumes all users have the same number of views. Real users vary, which usually makes it worse.

Even a small correlation matters. Set it to **0.1** and raise the views to **50**: a test you think has a 5% false-positive rate is wrong far more often.

**Now say why:** why do extra page views add less information than extra users?

## Maths

### Maths

#### In one breath

If you assign by **user** but count **page views**, the page views aren't independent: one person's views look alike. The usual formula treats them as separate samples, so the standard error comes out **too small**, and false positives rise well above 5%. Fix it with the **delta method**, or by bootstrapping whole users, so your uncertainty reflects the number of users.

#### Two units

- **Randomisation unit:** what the coin was flipped for, usually the user.

- **Analysis unit:** what the metric counts per, like a page view.

When they differ, you have fewer independent samples than you think. A thousand views from 100 people carry much less information than a thousand views from a thousand people, because each person's views are correlated.

##### Three ways to handle it

| Method | How | When |
|---|---|---|
| **Delta method** | A formula using each user's clicks and views, and how they vary together. | The standard choice: quick, and works at scale. |
| **Bootstrap by user** | Resample whole users many times, and recompute the ratio. | Simple and flexible, but slower. |
| **Change the metric** | Use a per-user metric, like clicks per user. | Simplest, if it answers your question. |

##### Careful: two different ratios

The **ratio of totals** (all clicks ÷ all views) and the **mean of ratios** (average each user's CTR) answer different questions. Heavy users dominate the first, and each user counts equally in the second. Decide which you mean before you start.

#### The maths

$$ {\mathrm{Var}\!\left(\frac{\bar Y}{\bar X}\right)} \approx \frac{1}{{n}\,\mu_X^2}\left({\sigma_Y^2} - {2R\,\sigma_{XY}} + {R^2\sigma_X^2}\right), \quad R = \frac{\mu_Y}{\mu_X} $$

The delta method approximates a ratio with a straight-line version, then computes the variance of that. It works well with the large samples typical of online tests.

- **variance of the ratio**: How noisy click-through rate is across users.

- **number of users**: The count of randomised units, not page views. This is the key fix.

- **variance of the top**: How much clicks per user vary.

- **how they move together**: Users with more views tend to have more clicks, and this covariance matters.

- **variance of the bottom**: How much views per user vary.

## In practice

### In practice

#### In practice

- **Spot the mismatch:** if the metric's denominator isn't your randomisation unit, you need this.

- **Store per-user totals:** keep clicks and views per user per group, and the delta method can be computed from those.

- **Watch the denominator:** a change can shift views as well as clicks. If treatment changes who views how often, the ratio can move even if nothing improved, so look at both parts.

- **Test your pipeline:** A/A tests show this clearly: if far more than 5% come back significant, suspect a unit mismatch. See trust checks.

### The answer that sounds right

#### "More page views means more data, so it's fine"

It sounds right, since the sample looks huge. But a thousand views from a hundred people aren't a thousand independent facts. The formula thinks they are, so it reports too much certainty. Effective sample size is closer to the number of users.

## Say it

### You randomise by user but measure click-through rate per page view. What goes wrong, and how do you fix it?

#### The interviewer pushes further

Follow-up 1 of 3

How would you detect this problem in your platform?

Run A/A tests, where both groups get the same experience. If far more than 5% come back significant on a ratio metric, the variance is being underestimated. Comparing the simple formula with a per-user bootstrap also shows it directly.

Follow-up 2 of 3

Why not simply average each user's CTR?

That's a valid metric, but a different one. It treats a user with one view the same as one with a thousand, and users with no views have no CTR. It answers what the typical user does, not what share of all views get clicked.

Follow-up 3 of 3

Can you use the delta method for revenue per order?

Yes, it's the same setup. Revenue is the top, orders are the bottom and the user is the unit. Just remember that if treatment changes how many orders people place, the ratio can move for reasons other than order value, so check orders per user too.

#### The 30-second answer

If I randomise by user but measure per page view, those views aren't independent, because one person's behaviour repeats. The standard formula treats them as separate, so the standard error's too small, and false positives rise above 5%. I'd use the delta method, which computes the variance from per-user clicks and views and how they vary together. Or I'd bootstrap whole users. The key is that uncertainty should reflect the number of randomised users, not page views.

**Key terms and sources**

Why ratio metrics break standard A/B test formulas when the analysis unit differs from the randomisation unit, and how the delta method fixes it. · checked 7 Nov 2026

#### Sources

- [Deng, Knoblich and Lu, Applying the Delta Method in Metric Analytics (2018), via the deltatest package notes](https://ftp.fau.de/cran/web/packages/deltatest/readme/README.html)

- [Ratio metrics in A/B testing, DataCamp](https://campus.datacamp.com/courses/ab-testing-in-python/practical-considerations-and-making-decisions?ex=8)

- [Deng, Knoblich and Lu, Applying the Delta Method in Metric Analytics](https://arxiv.org/abs/1803.06336)

Lab numbers are illustrative unless a lab says otherwise. Explanations are ours, built from these sources and standard statistics.
