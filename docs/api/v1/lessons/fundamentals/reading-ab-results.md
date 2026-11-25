# Reading the Result: Significance and Decisions

> Your A/B test came back significant. How do you decide whether to ship?

- Track: Fundamentals › A/B Testing › Reading the result
- Type: Concept · 15 min
- Page: https://aimlrounds.com/tracks/fundamentals/reading-ab-results/
- Before this: Sample Size, Power and Runtime (`fundamentals/sample-size-and-power`), Confidence Intervals & the Bootstrap (`fundamentals/confidence-intervals-and-bootstrap`)
- Quiz topic: `ab`
- Sources checked: 2026-11-07 · Text last changed: 2026-11-20 · Version: 479c9a97ea

## Intuition

### The situation

Your test ran to plan: 50,000 users per group, 10.0% against 10.4%, and p = 0.04. The product manager says it's significant, so ship it. Building and maintaining the feature isn't free. The interviewer asks:

> Your A/B test came back significant. How do you decide whether to ship?

#### Why it matters

With enough users, tiny effects become significant. A real lift of 0.01% can have a p-value near zero and still not be worth the engineering cost. This lesson turns the numbers from hypothesis tests and confidence intervals into a decision.

### The idea

Think of a bathroom scale that says you lost a tiny amount. You may be confident it's real, but that doesn't mean it matters. Two questions are separate: is it real, and is it big enough to care about? The interval answers both.

[Figure: Reading the interval. Entirely above your bar: ship. Crossing both zero and your bar: not enough data. Entirely below zero: do not ship.]

_Check the interval against zero and against the smallest lift worth shipping._

### Play

**Try to break it.** Set the lift to 0.1 points, then drag the users up to 500,000.

#### Read the interval

Grey line: zero. Dashed line: your bar. Block: the 95% interval. The scale runs from −2 to +3 points.

Illustrative inputs. The formula is the two-proportion z-test, using unpooled standard errors for the interval and the p-value.

Set the lift to **0.1 points**, then drag the users up to 500,000. It becomes highly significant and still isn't worth shipping. That's the difference between statistical and practical significance.

**Now say why:** how can a result be highly significant and still not worth shipping?

## Maths

### Maths

#### In one breath

A low p-value only says the difference is unlikely to be pure chance. It doesn't say the effect is big enough to matter. So read the **confidence interval** against two lines: **zero** and the **smallest lift worth shipping**. Entirely above your bar: ship. Crossing both: you need more data. If a result looks too good, **suspect a bug first**.

#### Two lines, one interval

| Where the interval sits | What it means | Decision |
|---|---|---|
| Entirely above your bar | Real, and large enough to matter. | **Ship**, if guardrails hold. |
| Above zero, but crosses your bar | Probably real, but it might be too small to matter. | **Judgement call**, or more data. |
| Above zero, entirely below your bar | Real, but too small to matter. | **Usually don't ship**, unless it's cheap. |
| Crosses zero and your bar | Could be nothing, could be worthwhile. | **Not enough data.** |
| Crosses zero, entirely below your bar | No meaningful effect, either way. | **Don't ship**, and you've learned something. |
| Entirely below zero | It hurts. | **Don't ship.** |

##### What not to say

- **"p = 0.03, so there's a 97% chance B is better."** The p-value assumes there's no effect. It isn't the chance your idea works.

- **"Not significant, so there's no effect."** You may simply lack the data. Look at how wide the interval is.

- **"The lift is 8%."** Give the interval too. It's an estimate, and significant results tend to overstate the truth.

##### Twyman's law

The more interesting or unusual a figure looks, the more likely it comes from a mistake. If a small change seems to lift revenue by 20%, check the logging, the assignment and the sample ratio before you celebrate.

#### The maths

$$ {(\hat p_T - \hat p_C)} \pm {1.96} \cdot {\sqrt{\frac{\hat p_T(1-\hat p_T)}{n_T} + \frac{\hat p_C(1-\hat p_C)}{n_C}}} $$

Worked example: 50,000 users per group, 10.0% against 10.4%. The difference is 0.40 points with a standard error of 0.19, so the interval is 0.02 to 0.78 points and p ≈ 0.04. Significant, but the interval also includes lifts too small to matter.

- **observed difference**: Treatment’s rate minus control’s rate.

- **95% multiplier**: How many standard errors the interval spans on each side.

- **standard error**: Noise in the difference. It shrinks with more users, so the interval narrows.

## In practice

### In practice

#### In practice

- **Check validity first:** confirm the sample ratio and guardrails before you read the main metric.

- **Set your bar before the test:** it should reflect the cost of building and maintaining the change.

- **Report the interval:** "between 0.02 and 0.78 points" helps people decide far better than "significant".

- **Confirm surprises:** rerun a big or unexpected win to see whether it holds.

- **Most ideas fail:** at Microsoft, about one in three experiments was reported as a success, so a win should earn scrutiny.

### The answer that sounds right

#### "p below 0.05, so ship it"

It sounds right, since that's the agreed rule. But a low p-value only suggests the effect isn't zero. With enough users, tiny effects pass. Here, the interval runs from nearly nothing to 0.78 points, so the real question is whether the low end is worth the cost.

## Say it

### Your A/B test came back significant. How do you decide whether to ship?

#### The interviewer pushes further

Follow-up 1 of 3

What's the difference between statistical and practical significance?

Statistical significance says the effect is unlikely to be only chance. Practical significance says it's large enough to be worth it. With huge samples, a tiny lift can pass the first and fail the second.

Follow-up 2 of 3

The result isn't significant. Is the change useless?

Not necessarily. If the interval is narrow around zero, there's no meaningful effect. If it's wide and includes worthwhile lifts, the test was too small to tell. The width of the interval tells you which.

Follow-up 3 of 3

A small button colour change shows a 20% revenue lift. What do you do?

Suspect it first. I'd check the sample ratio, logging, outliers such as one huge purchase, and whether bots were included. If all of it holds, I'd rerun the test, because results this surprising are usually errors.

#### The 30-second answer

First I'd check the test is valid: sample ratio and guardrails. Then I'd read the confidence interval against zero and against the smallest lift worth shipping. If it's entirely above that bar, ship. If it crosses zero and the bar, I need more data. If it's above zero but below the bar, the effect is real but too small to matter. Significance alone isn't enough, because with enough users tiny effects become significant. And if a result looks too good, I'd suspect a bug first.

**Key terms and sources**

Confidence intervals, statistical against practical significance, and a clear rule for ship, don't ship or get more data. · checked 7 Nov 2026

#### Sources

- [Twyman's law, from Kohavi, Tang and Xu (book excerpt)](https://assets.cambridge.org/97811087/24265/excerpt/9781108724265_excerpt.pdf)

- [Peeking at A/B tests, a summary that cites the one-in-three figure](https://blog.acolyer.org/2017/09/28/peeking-at-ab-tests-continuous-monitoring-without-pain/)

- Hypothesis tests on this site

Lab numbers are illustrative unless a lab says otherwise. Explanations are ours, built from these sources and standard statistics.
