# Chi-Squared Tests and ANOVA

> When would you use a chi-squared test or ANOVA, and why not just run many t-tests?

- Track: Fundamentals › Maths for ML › Statistics
- Type: Concept · 15 min
- Page: https://aimlrounds.com/tracks/fundamentals/chi-squared-tests-and-anova/
- Before this: T-Tests and Z-Tests (`fundamentals/t-tests-and-z-tests`)
- Quiz topic: `stats`

## Intuition

### The situation

You've tested five versions of a recommendation model. A colleague ran t-tests on every pair, and celebrates one significant result. Another wants to know whether a user's plan type is related to whether they churn. The interviewer asks:

> When would you use a chi-squared test or ANOVA, and why not just run many t-tests?

#### Why it matters

Not every question is about two means. You might compare several model versions, or check whether two categories are related. These are the standard tools, and knowing which to choose is a common interview question.

### The idea

Think of noise in a classroom. If you wonder whether groups differ, you could compare every pair of students, and something will look different by chance. Or you could ask once: is the difference between groups larger than the ordinary variation within them? That single question is ANOVA.

[Figure: Choosing a test. Chi-squared compares observed and expected counts for categories. ANOVA compares the variation between groups with the variation within them.]

_Chi-squared is for counts, and ANOVA is for group means._

### Play

**Try to break it.** Set the gap to 0, and raise the groups to 20. Then raise the gap.

#### Compare many groups

Illustrative: each group has a standard deviation of 1, and means rise evenly. The false-win figure assumes independent tests with no real differences, so treat it as a guide. Pairwise tests that share groups are correlated.

Set the gap to **0** and raise the groups to **20**. All groups are identical, yet pairwise testing almost guarantees you'll "find" a difference. ANOVA doesn't, as its F statistic stays low.

**Now say why:** why does F stay small when the groups are identical?

## Maths

### Maths

#### In one breath

The **chi-squared test** compares the counts you got with the counts you'd expect, so it suits categories, like plan type against churn. **ANOVA** compares means across many groups at once, by asking whether differences between groups are large compared with the noise within them. Running every pair of t-tests instead inflates false positives. A significant ANOVA only says that **some group differs**, so you follow up to find which.

#### Two tests for two situations

| Your data | Question | Test |
|---|---|---|
| Two categories | Are they related? | Chi-squared test of independence |
| One category | Does it match an expected split? | Chi-squared goodness of fit, as in SRM checks |
| A number, across 3 or more groups | Do the means differ? | One-way ANOVA |

##### Chi-squared, in steps

1. Work out each cell's expected count if the two variables were unrelated: row total × column total ÷ grand total.

2. For each cell, compute (observed − expected)² ÷ expected, and add them up.

3. Compare with a chi-squared distribution with (rows − 1)(columns − 1) degrees of freedom.

Use counts, not percentages. If expected counts are very small, under about 5, use Fisher's exact test. For a 2 × 2 table, chi-squared equals the two-proportion z-test squared.

##### ANOVA, in one idea

Split total variation into two parts. **Between groups** measures how far group means are from the overall mean. **Within groups** measures the noise inside each group. If the groups really are the same, the two should be about equal, and their ratio, the **F statistic**, is close to 1.

##### After a significant result

ANOVA doesn't say which group differs. Follow up with pairwise tests, corrected for multiple comparisons, such as Tukey's test. With only two groups, ANOVA gives the same answer as a t-test, since F = t².

#### The maths

$$ {\chi^2} = \sum_{\text{cells}} \frac{({O} - {E})^2}{{E}}, \qquad {F} = \frac{{\text{variance between groups}}}{{\text{variance within groups}}} $$

Worked example: A converts 40 of 100, and B converts 60 of 100. Expected is 50 in each cell. χ² = 4 × 10²/50 = 8, with 1 degree of freedom, so p ≈ 0.005.

- **chi-squared**: The total surprise across all cells. Larger means a bigger gap from what you’d expect.

- **observed counts**: What you actually saw.

- **expected counts**: What you’d see if the variables were unrelated.

- **the F statistic**: A signal-to-noise ratio. Around 1 means no sign of a real difference.

- **between groups**: How spread out the group means are.

- **within groups**: Ordinary noise inside each group.

## In practice

### In practice

#### In practice

- **A/B/n tests:** if you only compare each variant with control, Dunnett's test or a simple correction is often better than ANOVA. See multiple testing.

- **Feature selection:** chi-squared and F scores give quick filters for feature importance, but they only see simple relationships.

- **Effect sizes:** with large samples, tiny differences become significant. Report how large the relationship is, like Cramér's V or η².

- **Independence:** both assume independent observations. Repeated events from one user break this.

### The answer that sounds right

#### "ANOVA was significant, so the best-looking group wins"

It sounds right, as ANOVA found a difference. But it only says the groups aren't all equal. It doesn't say which differs, or that the top group beats the next one. Follow up with corrected pairwise comparisons, and look at effect sizes.

## Say it

### When would you use a chi-squared test or ANOVA, and why not just run many t-tests?

#### The interviewer pushes further

Follow-up 1 of 3

What's the connection between chi-squared and the two-proportion z-test?

For a 2 × 2 table, they're the same test: chi-squared equals z squared, with the same p-value. Chi-squared generalises to more rows and columns. The z-test also gives you a direction, and a confidence interval for the difference.

Follow-up 2 of 3

Why does ANOVA use variances to compare means?

If all group means were equal, their spread would only reflect noise, and it would match the noise inside groups. If the means differ, their spread grows beyond that. So comparing the two variances tests whether the means differ. It's the same logic as signal against noise.

Follow-up 3 of 3

ANOVA is significant, but no pairwise test is. What's going on?

It can happen. ANOVA pools evidence across all groups, while corrected pairwise tests are stricter, each with less power. It suggests something differs, without enough data to say which. You could look at a planned contrast, such as a trend across ordered groups, or collect more data.

#### The 30-second answer

I'd use chi-squared for categories: it compares observed counts with those expected if the variables were unrelated. I'd use ANOVA to compare a number's mean across three or more groups: it compares variation between groups with variation within them. Running all the pairwise t-tests instead inflates false positives. With five groups, that's ten tests, and up to a 40% chance of a false win. A significant ANOVA only says some group differs, so I'd follow up with corrected pairwise tests, like Tukey's.

**Key terms and sources**

Chi-squared tests for categories, ANOVA for comparing many group means, why repeated t-tests inflate false positives, and how to follow up. · checked 6 Nov 2026

#### Sources

- [Diez, Çetinkaya-Rundel and Barr, OpenIntro Statistics](https://www.openintro.org/book/os/)

- [Bruce, Bruce and Gedeck, Practical Statistics for Data Scientists, contents excerpt](https://toc.uni.li/FLMF048415.pdf)

- [KDnuggets on statistical concepts for interviews](https://www.kdnuggets.com/2021/02/10-statistical-concepts-data-science-interviews.html)

Explanations are ours, built from these sources. Lab numbers are illustrative, and worked examples were checked by calculation.
