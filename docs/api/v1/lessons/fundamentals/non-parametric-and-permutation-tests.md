# Non-Parametric and Permutation Tests

> What do you do when a t-test's assumptions fail, and how does a permutation test work?

- Track: Fundamentals › Maths for ML › Statistics
- Type: Concept · 15 min
- Page: https://aimlrounds.com/tracks/fundamentals/non-parametric-and-permutation-tests/
- Before this: T-Tests and Z-Tests (`fundamentals/t-tests-and-z-tests`)
- Quiz topic: `stats`

## Intuition

### The situation

You have 10 users in each group, and revenue is very skewed. One big spender in group A makes A's mean larger, while most of B's users spend more. A t-test says there's no difference. The interviewer asks:

> What do you do when a t-test's assumptions fail, and how does a permutation test work?

#### Why it matters

Real metrics are often messy: revenue, session length, latency. These tests give you a reliable option when the usual assumptions don't hold, and they explain what AUC really measures. See t-tests first.

### The idea

Think of a race where you only note who finished ahead of whom. A runner who's an hour behind counts just the same as one who's a second behind, so one extreme time can't skew the result. To test for luck, you could also shuffle team labels, and see how often a shuffled team does as well.

[Figure: Two approaches. Rank tests use order, not size, so outliers matter less. Permutation tests shuffle labels to build the null, for any statistic.]

_Fewer assumptions, at the cost of some detail._

### Play

**Try to break it.** Drag A's largest value down to 12, and up to 500. Then lower the shift.

#### Add an outlier to a small test

Illustrative: A is 3 to 11, plus your largest value. B is 4 to 13, with your shift added to each. Mann-Whitney uses a Normal approximation with tie correction. Permutation uses 4,000 seeded shuffles.

Lower A's largest value to **12**. The t-test recovers, as there's no extreme value left to distort things. The ranks barely change between these two settings, which is the point of using them. Notice that at 200, a permutation test on **means** also fails, as the outlier dominates every shuffle. A test is only as robust as its statistic, so try a permutation test on medians or ranks in that case.

**Now say why:** why does the rank test barely change?

## Maths

### Maths

#### In one breath

When data is small, skewed or full of outliers, a t-test can mislead. **Rank tests**, such as Mann-Whitney, replace values with their ranks, so one extreme value can't dominate. Mann-Whitney's U is directly tied to **AUC**: both give the chance that a random item from one group beats one from the other. **Permutation tests** build the null by shuffling group labels, so they need few assumptions, and work for any statistic.

#### Two ways to avoid assumptions

##### Rank tests

1. Pool both groups, and sort all the values.

2. Replace each value with its rank. A huge outlier just becomes the top rank.

3. Check whether one group's ranks are unusually high.

| Instead of | Use | Situation |
|---|---|---|
| Two-sample t-test | **Mann-Whitney U** | Two separate groups |
| Paired t-test | **Wilcoxon signed-rank** | The same subjects, twice |
| One-way ANOVA | **Kruskal-Wallis** | Three or more groups |
| Pearson correlation | **Spearman** | Relationships that rise steadily, but not in a straight line |

##### What Mann-Whitney actually tests

It's often described as comparing medians, but that's only true under extra assumptions. In general, it tests whether a random value from one group tends to beat one from the other. That chance is U ÷ (n₁n₂), which is exactly the AUC, if the groups are positives and negatives.

##### Permutation tests

1. Compute your statistic on the real data, like the difference in means.

2. Shuffle the group labels randomly, and recompute it.

3. Repeat thousands of times, to see what chance alone produces.

4. The p-value is how often a shuffled result is at least as extreme as the real one.

The logic is direct: if the groups really don't differ, the labels are arbitrary. It works for any statistic, like medians, ratios or a model's AUC gain.

##### The trade-offs

- **Lost precision:** rank tests discard sizes, so they don't say "how much". Report an effect size too.

- **Totals matter:** if a few whales drive revenue, a rank test may miss a change that you care about, as it ignores how big those values are.

- **Some power loss:** on truly Normal data, a t-test is slightly better, though the rank test's loss is small.

- **Bootstrap or permutation?** Permutation tests a null hypothesis. The bootstrap estimates uncertainty, as in confidence intervals.

#### The maths

$$ U = \sum_{i}\sum_{j} \mathbb{1}[x_i > y_j] + \tfrac12\mathbb{1}[x_i = y_j], \qquad \mathrm{AUC} = \frac{U}{n_1 n_2}, \qquad p \approx \frac{\#\{|T_{\text{shuffled}}| \ge |T_{\text{real}}|\} + 1}{R + 1} $$

Worked example: with 10 and 15 items and U = 75, AUC = 75 ÷ 150 = 0.5, so neither group tends to beat the other.

- **the U statistic**: Counts how many pairs from the two groups have x beating y.

- **one comparison**: Only the order matters, not how far apart the values are.

- **its link to AUC**: Divide by the number of pairs to get the chance that x beats y. 0.5 means no difference.

- **permutation p-value**: The share of R shuffles that are at least as extreme as the real result. Adding 1 keeps it above zero.

## In practice

### In practice

#### In practice

- **Choosing:** with large samples, a t-test on means is usually fine, thanks to the central limit theorem, and answers the question about totals. Use rank tests for small samples, or when a typical user matters more than the total.

- **Comparing models:** permutation tests on paired predictions, swapping which model gets each example's result, are a simple way to test a metric's difference.

- **Check your unit:** shuffle at the level you randomised, like users, not events. Otherwise, you underestimate noise.

- **Cost:** permutation needs thousands of recomputations, so it can be slow on expensive statistics.

### The answer that sounds right

#### "Mann-Whitney compares medians"

It sounds right, as it's in many cheat sheets. But it only compares medians if the two distributions have the same shape. In general, it tests whether a value from one group tends to beat one from the other. Two groups can have the same median, and still get a significant result.

## Say it

### What do you do when a t-test's assumptions fail, and how does a permutation test work?

#### The interviewer pushes further

Follow-up 1 of 3

How is Mann-Whitney related to AUC?

AUC is the chance that a random positive scores above a random negative. U counts pairs where one group's value beats the other's, with ties as a half. So U ÷ (n₁n₂) is exactly AUC, and testing whether AUC differs from 0.5 is the same as a Mann-Whitney test.

Follow-up 2 of 3

When would you not use a rank test, even with skewed data?

When you care about the total. If you want to raise revenue, a change that moves a few very large spenders matters, and a rank test could miss it entirely. With large samples, a test on the mean is fine even for skewed data, or you could use the bootstrap.

Follow-up 3 of 3

What's the difference between a permutation test and the bootstrap?

A permutation test shuffles labels without replacement, assuming no group difference, to get a p-value. The bootstrap resamples with replacement from the data as it is, to estimate uncertainty, like a confidence interval. They answer related but different questions.

When data is small, skewed or has outliers, I'd consider Mann-Whitney, which ranks the pooled values, so one extreme value can't dominate. It tests whether one group tends to beat the other, and U over n1 n2 is the same as AUC. A permutation test shuffles the group labels thousands of times to build the null, then asks how often a shuffle is at least as extreme as the real result. It needs few assumptions, and works for any statistic. But a rank test ignores size, so if totals matter, such as revenue, I'd keep looking at the mean.

**Key terms and sources**

Rank tests like Mann-Whitney, the link with AUC, permutation tests, and when these are better than a t-test.

#### Sources

- DataCamp statistics interview questions

- Wasserman, All of Statistics

- ROC and PR AUC on this site

Explanations are ours, built from these sources. Lab numbers are illustrative, and worked examples were checked by calculation.
