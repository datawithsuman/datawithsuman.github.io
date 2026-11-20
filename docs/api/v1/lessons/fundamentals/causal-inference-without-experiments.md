# Causal Inference Without an Experiment

> You can't run an A/B test. How can you still estimate a causal effect?

- Track: Fundamentals › Maths for ML › Statistics
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/causal-inference-without-experiments/
- Before this: Correlation vs Causation (`fundamentals/correlation-vs-causation`)
- Quiz topic: `stats`

## Intuition

### The situation

A new delivery fee launched in three cities last month, and orders fell 5%. There was no A/B test, and orders also fell elsewhere. Meanwhile, users who opted into a loyalty plan spend more, and someone wants to credit the plan. The interviewer asks:

> You can't run an A/B test. How can you still estimate a causal effect?

#### Why it matters

Many changes can't be A/B tested: a price change across a whole market, a past launch or a policy. These are the standard ways of still saying something causal. They build on correlation vs causation.

### The idea

Think of a detective who can't rerun the past, so looks for natural comparisons. Did a similar town, without the change, see the same drop? Were people just above and just below a cutoff really that different? Each clue only helps if the comparison is fair, and the detective must argue that it is.

[Figure: Four designs and their assumptions. Difference-in-differences needs parallel trends. Matching needs no hidden confounders. A cutoff needs people near it to be alike.]

_Each method swaps randomisation for an assumption._

### Play

**Try to break it.** Move the gap and shared trend, and watch DiD. Then move the violation slider.

#### Run difference-in-differences

Illustrative, with no noise. The last slider adds an extra trend to the treated group only, which no one could observe in real data.

Move the existing gap and the shared trend: DiD doesn't move, as it removes both. Now move the **last slider**. DiD's error is exactly that amount. You usually can't see that slider in real life, which is why you must argue that trends are parallel.

**Now say why:** why does DiD ignore a gap that was always there?

## Maths

### Maths

#### In one breath

When you can't randomise, you look for situations that act like an experiment. **Difference-in-differences** compares changes over time against a similar group. **Matching** and **propensity scores** compare similar people with and without the treatment. **Regression discontinuity** uses a cutoff rule. **Instrumental variables** use something that nudges the treatment, but affects the outcome no other way. Each one relies on an **assumption you can't fully test**, so you must defend it.

#### Four designs

| Method | When | Key assumption |
|---|---|---|
| **Difference-in-differences** | A change hit some groups, not others, at a known time. | Parallel trends: without the change, both would have moved alike. |
| **Matching and propensity scores** | Some users opted in, and you've measured what drives this. | No unmeasured confounders. |
| **Regression discontinuity** | Treatment depends on a cutoff, like a score above 700. | People just either side are alike, and can't game the cutoff. |
| **Instrumental variables** | Something shifts the treatment at random. | It affects the outcome only through the treatment. |

##### Difference-in-differences

Comparing treated and control after a change mixes in how they always differed. Comparing treated before and after mixes in trends. Subtracting the control group's change from the treated group's change removes both.

##### Propensity scores

Model each user's chance of being treated, based on measured features. Then compare, or reweight, users with similar scores. It balances what you measured, and **can't fix what you didn't**. If motivated users opt in, and you've no measure of motivation, the bias stays.

##### Regression discontinuity

If free delivery starts at ₹500, orders at ₹495 and ₹505 are nearly alike. The jump in outcomes at that line estimates the effect, but only near the cutoff. If people deliberately push over the line, the comparison breaks.

##### Instrumental variables

A random encouragement, like a prompt shown to some users, changes who uses a feature. Its effect on the outcome, divided by its effect on usage, estimates the feature's effect for those it persuaded. A weak instrument, or one with other effects, gives misleading answers.

##### How to build trust

- **Placebo tests:** apply the method at a fake date, or on an outcome the change can't affect. You should find nothing.

- **Check earlier trends:** before the change, do the groups really move together?

- **Sensitivity analysis:** how strong would a hidden confounder have to be to explain this away?

#### The maths

$$ {\hat\tau_{\text{DiD}}} = {(\bar Y_{T,\text{after}} - \bar Y_{T,\text{before}})} - {(\bar Y_{C,\text{after}} - \bar Y_{C,\text{before}})}, \qquad {\hat\tau_{\text{IV}} = \frac{\text{effect of } Z \text{ on } Y}{\text{effect of } Z \text{ on } X}} $$

Worked example: treated goes from 50 to 58, and control goes from 40 to 43. DiD = 8 − 3 = 5. That’s only right if treated would otherwise have also risen by 3.

- **the estimate**: The change in treated, minus the change in control.

- **treated group’s change**: Contains the effect, plus any general trend.

- **control group’s change**: Estimates the general trend alone, if trends are parallel.

- **instrumental variables**: Scales the instrument’s effect on the outcome by how much it moved the treatment.

## In practice

### In practice

#### In practice

- **Prefer an experiment:** if you can randomise, even partly, do it. These methods are a second choice, with stronger assumptions.

- **Geo tests:** launching in some cities, then using DiD or synthetic control, is common for marketing and marketplaces.

- **Encouragement designs:** if you can't force usage, randomise a prompt, and use it as an instrument.

- **Don't trust ML alone:** a model that predicts well says nothing about causes, however many features it has. See inference for regression.

- **State your assumptions:** a causal claim is only as strong as the assumption behind it, so write it down, and test what you can.

### The answer that sounds right

#### "Control for enough features, and it's causal"

It sounds right, as adding controls removes some bias. But you can only control for what you've measured, and motivation or intent usually isn't. Adjusting for the wrong variable, one affected by the treatment, can even add bias. So state your assumption, and test what you can.

## Say it

### You can't run an A/B test. How can you still estimate a causal effect?

#### The interviewer pushes further

Follow-up 1 of 3

How do you check the parallel trends assumption?

You can't check it for the period after the change, as you can't see what would have happened. But you can plot trends before the change. If they move together for a long time, it's more believable. A placebo test at a fake date should find no effect.

Follow-up 2 of 3

A feature's users retain better. Can propensity matching show it caused this?

Only if you've measured everything that drives both usage and retention. Motivation is the usual hidden factor. Matching balances what you measured, not what you didn't. So I'd run an encouragement experiment if I could, and otherwise add a sensitivity analysis and state the limits.

Follow-up 3 of 3

What makes a good instrument?

It must clearly change the treatment, and affect the outcome only through it. A randomised prompt is the cleanest. The second condition can't be tested from data, so it must be argued. A weak instrument also makes estimates very noisy and possibly biased.

#### The 30-second answer

I'd look for something that acts like an experiment. If a change hit some groups at a known time, I'd use difference-in-differences, which assumes parallel trends. If users opted in and I've measured what drives that, I'd use matching or propensity scores, which assume no unmeasured confounders. With a cutoff rule, regression discontinuity compares those just either side. With a random nudge, instrumental variables can work. Each relies on an assumption I can't fully test, so I'd check earlier trends and run placebo tests.

**Key terms and sources**

Difference-in-differences, matching and propensity scores, regression discontinuity and instrumental variables: how each works, what it assumes, and what could go wrong. · checked 6 Nov 2026

#### Sources

- [Hernán and Robins, Causal Inference: What If](https://miguelhernan.org/whatifbook)

- [Cunningham, Causal Inference: The Mixtape](https://mixtape.scunning.com/)

- Correlation vs causation on this site

Explanations are ours, built from these sources. Lab numbers are illustrative, and worked examples were checked by calculation.
