# Revenue and Heavy-Tailed Metrics

> Revenue per user is your main metric, and a few huge spenders swing every result. What do you do?

- Track: Fundamentals › A/B Testing › Reading the result
- Type: Concept · 18 min
- Page: https://aimlrounds.com/tracks/fundamentals/revenue-and-heavy-tailed-metrics/
- Before this: Sample Size, Power and Runtime (`fundamentals/sample-size-and-power`)
- Quiz topic: `ab`

## Intuition

### The situation

Your main metric is revenue per user. Last week's test showed +9%, and this week's shows −4%, with no obvious reason. Looking closer, one customer placed a ₹400,000 order. The interviewer asks:

> Revenue per user is your main metric, and a few huge spenders swing every result. What do you do?

#### Why it matters

Revenue is often what a business cares about most, and it's among the hardest metrics to test. At Bing, revenue per user had a skewness of about 18, so the rule of thumb asks for 114,000 users per group just to trust the normal approximation. A single large order can also flip a result, which makes a dashboard look far more exciting than it should.

### The idea

Think of working out the average wealth in a café. Most people have similar savings. Then a billionaire walks in, and the average jumps wildly. If you compare two cafés, you're really just asking which one the billionaire chose. Capping everyone's wealth at a limit gives you a steadier comparison, though it can't tell you if the billionaires got richer.

[Figure: Two problems and a fix. Variance is huge. The average converges slowly. Capping helps both, but hides changes above the cap.]

_Fix the cap before the test, and check the uncapped result._

### Play

**Try to break it.** Lower the cap step by step. Then switch to the top 1% of buyers.

#### Choose a cap

Our simulation of 100,000 users with a fixed seed: 5% buy, and their spend follows an invented lognormal distribution with a long tail. Users to detect a 5% lift use 5% significance and 80% power, on the capped metric. The capped lift is compared with the capped control group.

With **no cap**, skewness is 62.8, and detecting a 5% lift takes about 803,000 users per group. A **₹10,000 cap** cuts skewness to 15.3 and the users to about 427,000, and it still sees a 4.6% lift. That looks free. Now switch to **top 1% of buyers spend double**. Revenue really rises 16%, but the same cap sees only 0.3%, because most of the change sits above the cap. So a capped metric can miss what you're trying to measure. Always look at the uncapped number too.

**Now say why:** why does the cap see almost nothing in that case?

## Maths

### Maths

#### In one breath

In revenue data, most users spend nothing and a few spend a huge amount. Those few dominate the variance, so tests need far more users. The average also takes longer to behave like a normal curve, and a rule of thumb from Kohavi et al. says you need about **355 × skewness²** users per group. **Capping** values at a fixed limit cuts the noise a lot, but it changes the question: it can hide a change that only affects big spenders. So choose the cap before the test, and look at the uncapped result too.

#### Taming the tail

##### Two separate problems

- **Large variance:** required users grow with variance, and big spenders inflate it.

- **Slow convergence:** the usual test assumes the average is close to normal. With high skew, that takes many more users, so intervals and p-values can be wrong at sizes where they'd normally be fine.

##### What Bing reported

| Metric | Skewness | Users per group, 355 × s² | Change detectable at that size |
|---|---|---|---|
| Revenue per user | 17.9 | 114,000 | 4.4% |
| Revenue per user, capped | 5.2 | 9,700 | 10.5% |
| Sessions per user | 3.6 | 4,700 | 5.4% |
| Time to success | 2.1 | 1,550 | 12.3% |

Capping revenue at $10 per user per week took skewness from about 18 to about 5. At the same sample size, the capped metric could detect a change 30% smaller. The authors recommend the rule when skewness is above 1.

##### Your options

| Method | Helps with | The cost |
|---|---|---|
| **Capping** | Variance and skew | Ignores changes above the cap |
| **Log transform** | Skew | No longer about the average, which is what revenue adds up from. Zeros need handling |
| **Rank tests** | Outliers | Tests a shift in the distribution, not a change in the mean |
| **Bootstrap** | The shape of the average | Doesn't reduce variance, and can struggle with very rare huge values |
| **Split the metric** | Understanding | Report buyers per user and spend per buyer, though spend per buyer is a ratio whose buyers may differ between groups |
| **CUPED** | Variance | Past spend predicts only part of future spend |

#### The maths

$$ {s} = \frac{{E[(X - \mu)^3]}}{{\mathrm{Var}(X)^{3/2}}}, \qquad {n_{\min} \approx 355\, s^2} $$

From Kohavi, Deng, Longbotham and Xu (KDD 2014). With it, each tail of a 95% interval holds between 2% and 3%, against a target of 2.5%. They recommend the rule when skewness is above 1.

- **skewness**: How lopsided the distribution is. It’s 0 for a symmetric one, and large when a long tail runs one way.

- **the cube**: Cubing makes rare, far-away values count a great deal, and keeps their sign.

- **the scale**: Dividing by this makes skewness independent of units, so rupees or dollars give the same value.

- **the rule of thumb**: Users per group before the average is close enough to normal. It’s a lower limit, and power may need more.

## In practice

### In practice

#### In practice

- **Fix the cap in advance:** choose it from data before the test, such as a high percentile of past spend. Choosing it after seeing results lets you pick a winner.

- **Apply the same cap to both groups:** a cap based on one group's data can create a difference by itself.

- **Report both:** use capped revenue to decide, and the uncapped version as a check. If they disagree, look at who's driving it.

- **Check for bots and bulk buyers:** a huge value may be fraud or a data error, rather than a real customer.

- **Choose a more sensitive driver:** buyers per user may move earlier and more clearly than revenue, as long as past tests show it predicts revenue.

### The answer that sounds right

#### "Just remove the outliers"

It sounds right, since those values look like noise. But removing users after you've seen the data can bias the result, and the big spenders may be exactly who your change affects. A cap set in advance keeps every user, and applies one rule to both groups. Look at the uncapped result as well.

## Say it

### Revenue per user is your main metric, and a few huge spenders swing every result. What do you do?

#### The interviewer pushes further

Follow-up 1 of 3

A metric has a skewness of 12. How many users per group does the rule ask for?

355 × 12² = 355 × 144, which is about 51,000. That's only for the normal approximation to hold. You still need a power calculation, and the larger number wins.

Follow-up 2 of 3

Why not simply remove the outliers?

Removing users after seeing the data can bias the result, particularly if the change affects who becomes an outlier. A cap keeps every user, and it treats both groups by the same rule set in advance.

Follow-up 3 of 3

Capped revenue is flat, but uncapped revenue is up 8%. What's going on?

The change may be real but limited to big spenders, or a few large orders may have landed in one group by chance. I'd look at the top users in each group, check for bots, and see whether the uncapped interval excludes zero. Then I'd rerun it if the decision matters.

#### The 30-second answer

A few big spenders dominate revenue, which causes two problems. Variance is large, so tests need more users, and the average stays skewed for longer, so the usual intervals can be off. A rule of thumb from Kohavi and colleagues says you need about 355 times skewness squared users per group. Bing's revenue per user had a skewness of about 18, which gives 114,000. I'd cap values at a limit fixed before the test, for both groups, which cut Bing's skewness to about 5. But capping can hide a change that only affects big spenders, so I'd also check the uncapped result, and break revenue into buyers per user and spend per buyer.

**Key terms and sources**

Why a few big spenders make revenue so noisy, the 355 × skewness² rule, capping and its cost, and when to use logs, ranks or the bootstrap. · checked 7 Nov 2026

#### Sources

- [Kohavi, Deng, Longbotham and Xu, Seven Rules of Thumb for Web Site Experimenters (KDD 2014)](https://exp-platform.com/rules-of-thumb/)

- Non-parametric and permutation tests on this site

Lab numbers are illustrative unless a lab says otherwise. Explanations are ours, built from these sources and standard statistics.
