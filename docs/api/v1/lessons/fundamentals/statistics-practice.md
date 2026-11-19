# Statistics Practice

> Which test would you use, and can you work it out by hand?

- Track: Fundamentals › Maths for ML › Statistics
- Type: Interview · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/statistics-practice/
- Before this: Chi-Squared Tests and ANOVA (`fundamentals/chi-squared-tests-and-anova`)
- Quiz topic: `stats`

How to use this page

Give yourself about 5 minutes per question, as in an interview. Say your approach out loud, then open the answer and compare the method, not just the number.

**Tools for this page:** first ask what kind of data you have and whether samples are independent. Then choose the test, and report the size of the effect as well as whether it's significant.

Question 1 · Easy · mean or median

### What are the mean and median of 1, 2, 3, 4 and 100? Which better describes a typical value?

Answer: **Mean 22, median 3. The median**

1. Mean: 110 ÷ 5 = 22.

2. Median: the middle value when sorted, 3.

3. One extreme value dragged the mean above four of the five values.

Use the mean when the total matters, such as total revenue.

Question 2 · Easy · which test

### You compare 50 users' task times before and after a redesign, on the same users. Which test would you use?

Answer: **A paired t-test**

1. The same users are measured twice, so the two samples aren't independent.

2. A paired test works on each user's difference, which removes differences between users.

3. If the differences are very skewed with so few users, consider Wilcoxon signed-rank.

Pairing usually gives far more power here than a two-sample test.

Question 3 · Easy · which test

### You want to know whether plan type (free, pro or team) is related to churn (yes or no). Which test would you use?

Answer: **A chi-squared test of independence**

1. Both variables are categories, so compare counts.

2. Expected counts come from row total × column total ÷ grand total.

3. It has (3 − 1) × (2 − 1) = 2 degrees of freedom.

If expected counts are very small, use an exact test.

Question 4 · Medium · t-test

### A sample of 16 has mean 52 and standard deviation 8. Is it significantly different from 50 at the 5% level?

Answer: **No. t = 1**

1. Standard error: 8 ÷ √16 = 2.

2. t = (52 − 50) ÷ 2 = 1.

3. With 15 degrees of freedom, the cutoff is about 2.13, and 1 is well below that.

Not significant doesn't prove the mean is 50. The interval is about 47.7 to 56.3.

Question 5 · Medium · chi-squared

### A converts 40 of 100 users, and B converts 60 of 100. What's the chi-squared statistic?

Answer: **8, with p ≈ 0.005**

1. Pooled rate: 100 ÷ 200 = 0.5, so each cell expects 50.

2. Each cell contributes (10)² ÷ 50 = 2.

3. Four cells give 8, with 1 degree of freedom.

The two-proportion z-test gives z ≈ 2.83, and 2.83² = 8.

Question 6 · Medium · multiple groups

### You compare 5 model versions with all pairwise t-tests at 5%. How many tests is that, and what's the risk?

Answer: **10 tests, and up to about a 40% false-win chance**

1. Pairs: 5 × 4 ÷ 2 = 10.

2. If independent: 1 − 0.95¹⁰ ≈ 40%.

3. Use ANOVA first, or a correction such as Tukey's.

Tests that share groups are correlated, so 40% is a rough guide.

Question 7 · Medium · regression

### A regression gives a slope of 3, with a standard error of 1. What's the rough 95% interval, and is it significant?

Answer: **About 1 to 5, so yes**

1. Margin: about 2 × 1 = 2.

2. Interval: 3 − 2 to 3 + 2, or 1 to 5.

3. It excludes 0, and t = 3.

Significant here doesn't mean causal, or even useful.

Question 8 · Hard · difference-in-differences

### Treated goes from 50 to 58 after a launch, and control goes from 40 to 43. What's the estimated effect, and what must be true?

Answer: **5, if trends are parallel**

1. Treated changed by 8, and control by 3.

2. DiD = 8 − 3 = 5.

3. It assumes treated would have also risen by 3 without the launch.

Check that the trends matched before the launch.

**More practice and sources**

8 interview questions, easy to hard · answers hidden until you click · checked 6 Nov 2026

Keep practising

Review t-tests, chi-squared and ANOVA, regression and causal inference.
