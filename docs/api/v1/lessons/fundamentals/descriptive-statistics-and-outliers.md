# Descriptive Statistics and Outliers

> When would you use the median instead of the mean, and how do you detect outliers?

- Track: Fundamentals › Maths for ML › Statistics
- Type: Concept · 15 min
- Page: https://aimlrounds.com/tracks/fundamentals/descriptive-statistics-and-outliers/
- Before this: Expectation, Variance & Covariance (`fundamentals/expectation-and-variance`)
- Quiz topic: `stats`
- Sources checked: 2026-11-06 · Text last changed: 2026-11-20 · Version: bd49795002

## Intuition

### The situation

Your service's average latency looks healthy at 180 ms, yet users complain that it's slow. A dashboard also shows average order value jumped this week, and it turns out a single huge order caused that. The interviewer asks:

> When would you use the median instead of the mean, and how do you detect outliers?

#### Why it matters

Before any model or test, you have to look at your data. These summaries decide whether you notice a broken pipeline, or report a misleading average. A reported average can look fine while one user in a hundred has a terrible time.

### The idea

Think of ten people in a café, and a billionaire walks in. The average wealth in the room rockets, while the person in the middle is no richer. The average describes the total, and the median describes a typical person. Neither is wrong, but they answer different questions.

[Figure: Two kinds of summary. The mean, standard deviation and z-score are sensitive to outliers. The median, IQR and IQR rule are robust.]

_Pick by the question you're asking._

### Play

**Try to break it.** Drag the latency to 5,000 ms, and watch the mean and z-score.

#### Add one extreme value

The other nine latencies are 120, 130, 135, 140, 150, 155, 160, 170 and 180 ms.

Illustrative numbers. Quartiles use linear interpolation, and libraries differ slightly.

Drag the latency all the way to **5,000 ms**. The mean keeps climbing, while the median doesn't change. The z-score stays below 3, however extreme it gets. That's masking: the outlier inflates the yardstick used to measure it.

**Now say why:** why can't the z-score ever flag it, here?

## Maths

### Maths

#### In one breath

The **mean** balances all values, so a single extreme value can drag it. The **median** is the middle value, and it barely moves. Spread works the same way: **standard deviation** is sensitive, and the **interquartile range** is robust. **Percentiles** describe the experience of specific users, which is why services report p99 latency. Outliers can also hide themselves by inflating the very spread used to detect them, so a z-score rule can miss them.

#### Centre, spread and shape

| Question | Sensitive to outliers | Robust |
|---|---|---|
| **What's typical?** | Mean | Median |
| **How spread out?** | Standard deviation | Interquartile range (IQR), the middle 50% |
| **How unusual is a point?** | z-score | IQR rule, or median absolute deviation |

##### Mean or median?

- **Use the mean** when you care about totals, like total revenue. It's the only one that scales up: mean × users = total.

- **Use the median** for a typical case in skewed data, like house prices or salaries.

- **Skew tells you which way:** with a long right tail, the mean sits above the median.

##### Percentiles and latency

The p99 is the value that 99% of requests beat. Averages hide slow requests, and one page can make many requests, so many users will meet a slow one. If a page makes 100 requests, about 63% of page loads hit at least one slower than p99.

##### Detecting outliers

- **z-score:** flag values more than about 3 standard deviations from the mean. Assumes rough normality, and it can be fooled, as below.

- **IQR rule:** flag values outside Q1 − 1.5 × IQR or Q3 + 1.5 × IQR. This is what a boxplot shows.

- **Masking:** an outlier inflates the mean and standard deviation, so it hides itself. With 10 points, a z-score can't exceed about 2.85, however extreme the value.

##### What to do with one

First ask why it's there. A sensor error should be fixed or removed. A real whale customer is often the most important data you have. Consider capping values, robust methods or a log transform, and don't simply delete values to get a nicer result.

#### The maths

$$ {\bar x} = \frac{1}{n}\sum_i x_i, \qquad {s} = \sqrt{\frac{1}{n-1}\sum_i (x_i - \bar x)^2}, \qquad {z_i} = \frac{x_i - \bar x}{s}, \qquad {\mathrm{IQR} = Q_3 - Q_1} $$

Worked example: for 1, 2, 3, 4 and 100, the mean is 22, while the median is 3. One value moved the mean by more than seven times the median.

- **the mean**: Every value pulls on it equally, so large values pull hard.

- **the standard deviation**: Typical distance from the mean. Squaring gives extreme values even more weight. Dividing by n − 1 corrects for using the sample’s own mean.

- **the z-score**: How many standard deviations a point is from the mean. Both the top and bottom depend on the outlier.

- **the interquartile range**: The width of the middle 50%. It ignores the tails entirely, which makes it robust.

## In practice

### In practice

#### In practice

- **Plot before you summarise:** very different datasets can share a mean and standard deviation, so look at a histogram.

- **Look at slices:** an unchanged average can hide one group improving while another gets worse.

- **In ML:** squared error acts like the mean, and absolute error like the median. So outliers affect them in the same ways. See regression metrics.

- **Feature scaling:** outliers distort standard scaling, while robust scaling uses the median and IQR.

- **Averages of percentiles:** you can't average p99s across servers and get the true p99. Keep histograms or sketches.

### The answer that sounds right

#### "Outliers are errors, so remove them"

It sounds right, as they make your charts cleaner. But a huge order may be your best customer, and a slow request may be a real bug. Removing them can hide what matters most. First find out why they exist, then fix errors, and use robust methods for real extremes.

## Say it

### When would you use the median instead of the mean, and how do you detect outliers?

#### The interviewer pushes further

Follow-up 1 of 3

Why can't you average p99 latency across servers?

Percentiles don't combine by averaging. A server with little traffic counts as much as a busy one, and the true p99 depends on the combined distribution. Keep histograms or quantile sketches per server, merge those, and read the percentile from the merged result.

Follow-up 2 of 3

If a page makes 100 requests, how often does a page load see a request slower than p99?

Each request has a 99% chance of being faster, so all 100 are faster with chance 0.99¹⁰⁰, about 37%. So about 63% of page loads include at least one slow request. Tail latency affects users much more often than its name suggests.

Follow-up 3 of 3

Should you remove outliers before training?

Not automatically. Find out why they exist. Errors should be fixed or removed, while real extremes may be what you most need to predict. Options include a robust loss, capping or a log transform. And apply any rule using training data only, so you don't leak from the test set.

#### The 30-second answer

The mean uses every value, so an outlier can drag it, while the median is the middle value, and barely moves. I'd use the median for a typical case in skewed data, and the mean when totals matter, since mean times count gives the total. For outliers, I'd prefer the IQR rule to z-scores, because an outlier inflates the standard deviation and can mask itself. Then I'd ask why it's there before removing it. For latency, I'd report p99, because averages hide slow requests that many users actually hit.

**Key terms and sources**

Mean, median, percentiles, spread and skew, how outliers distort them, how to detect outliers, and why latency is reported as p99. · checked 6 Nov 2026

#### Sources

- [Diez, Çetinkaya-Rundel and Barr, OpenIntro Statistics](https://www.openintro.org/book/os/)

- [Bruce, Bruce and Gedeck, Practical Statistics for Data Scientists, contents excerpt](https://toc.uni.li/FLMF048415.pdf)

- Serving metrics on this site

Explanations are ours, built from these sources. Lab numbers are illustrative, and worked examples were checked by calculation.
