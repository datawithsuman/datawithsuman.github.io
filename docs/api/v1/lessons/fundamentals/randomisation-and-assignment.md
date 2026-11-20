# Randomisation and Assignment

> Why do we randomise users in an A/B test, and how should you choose the unit of assignment?

- Track: Fundamentals › A/B Testing › Designing a test
- Type: Concept · 15 min
- Page: https://aimlrounds.com/tracks/fundamentals/randomisation-and-assignment/
- Before this: Hypothesis Tests, p-values & A/B Testing (`fundamentals/hypothesis-testing-and-ab-tests`)
- Related: Correlation vs Causation (`fundamentals/correlation-vs-causation`)
- Quiz topic: `ab`

## Intuition

### The situation

A new reorder button went live last Monday, and orders are up 3% on the week before. Users who turned it on order far more than those who didn't. A colleague says that proves it works. The interviewer asks:

> Why do we randomise users in an A/B test, and how should you choose the unit of assignment?

#### Why it matters

Every other idea in this section relies on this one. A p-value tells you how surprising a difference is. Randomisation is what lets you say your change _caused_ it. See correlation vs causation for why that's hard otherwise.

### The idea

Think of testing a new fertiliser. If you put it only on the sunniest plots, you can't tell whether the fertiliser or the sun made them grow. Flip a coin for each plot, and sun, soil and water even out between the two groups. Any difference left is down to the fertiliser.

[Figure: Three comparisons. Before and after mixes in trends, so it's biased. Opt-in compares keen users, so it's biased. Randomised makes the groups match, so it's fair.]

_Only the coin removes causes you never measured._

### Play

**Try to break it.** Set the true effect to 0, then raise the other two sliders.

#### Three ways to measure the same change

Illustrative, in percentage points of conversion, ignoring random noise. Each biased method adds its bias directly to the effect.

Set the true effect to **0**. Before and after still shows a gain, and so does opt-in, for a change that does nothing. Only the randomised test stays right, whatever you do to the other two sliders.

**Now say why:** why can't a bigger sample fix the before-and-after estimate?

## Maths

### Maths

#### In one breath

Comparing before and after, or people who chose a feature against those who didn't, mixes your effect with other causes. **Random assignment** makes the two groups alike on everything, known and unknown, so the only systematic difference left is your change. Assign with a **salted hash** so a user stays in one group, and pick the **unit** that keeps each person's experience consistent.

#### How assignment works

##### Why randomising works

Each user could have two outcomes: one with the change and one without. You only ever see one of them. If a coin decides who gets the change, then heavy users, new users, weekend users and every trait you never measured end up in both groups in about the same mix. On average, the difference between the groups is the effect of your change.

##### How users get their group

1. Hash the user ID together with an experiment ID (the salt), for example `hash(user_id + experiment_id) mod 100`.

2. Put buckets 0 to 49 in control and 50 to 99 in treatment.

- **Consistent:** the same user always gets the same answer, with no lookup table.

- **Independent:** a different salt reshuffles everyone, so being in treatment in one test says nothing about another.

##### Choosing the unit

| Unit | Good for | Watch out for |
|---|---|---|
| **User** | The default for anything people notice, and for long-term metrics. | Logged-out users rely on cookies or devices, which change. |
| **Session** | Changes people won't notice between visits. | A user can see both versions. |
| **Page view or request** | Invisible backend changes, like a faster ranking model. | Can't measure retention, and it looks odd if the page visibly changes. |
| **Group, like a city** | When users affect each other. See interference. | Far fewer units, so much less power. |

A smaller unit gives more samples, and so more power, but only if the experience stays sensible. Analyse at the unit you randomised, or see ratio metrics.

#### The maths

$$ {\hat\tau} = {\bar Y_T} - {\bar Y_C}, \qquad {SE(\hat\tau)} = \sqrt{\frac{s_T^2}{n_T} + \frac{s_C^2}{n_C}} $$

Because assignment is random, the difference in means is an unbiased estimate of the average effect. This assumes one user’s outcome doesn’t depend on another user’s group.

- **estimated effect**: Your best guess of what the change did.

- **treatment mean**: The average metric among users assigned to the change.

- **control mean**: The average among users assigned to the old version.

- **standard error**: How much that difference would move by chance. Random assignment is what makes this estimate fair.

## In practice

### In practice

#### In practice

- **Log exposure:** record when a user actually reaches the changed experience, not only when they were assigned.

- **Trigger your analysis:** if the change is on the checkout page, users who never reach checkout add only noise. Analyse those who could have seen a difference, in both groups.

- **Assign before anything can differ:** if the change affects who gets logged, the groups stop being comparable. That's a sample ratio mismatch.

- **Run on the same dates:** both groups must run side by side, so seasons and news hit them equally.

- **Ramp up:** start with a small share of traffic to catch breakage, then widen it.

If you can't randomise, read Causal Inference Without an Experiment. For many tests at once, read Running Many Tests at Once.

### The answer that sounds right

#### "We have a million users, so a before-and-after comparison is fine"

It sounds right, since a million users gives a very precise number. But more data shrinks noise, not bias. Precisely measuring a mix of your change and a seasonal rise still gives the wrong answer. Only random assignment removes the other causes.

## Say it

### Why do we randomise users in an A/B test, and how should you choose the unit of assignment?

#### The interviewer pushes further

Follow-up 1 of 3

Why add the experiment ID to the hash?

Without it, the same users would always land in the same bucket in every test. Then one test's treatment group would carry over its effects into the next. A different salt reshuffles users for each experiment, so tests are independent.

Follow-up 2 of 3

Why not assign by page view? You get far more data.

Page views from one user are related, so the extra data is worth less than it looks, and the same person may see both versions. It also can't measure retention. It's fine for invisible backend changes, as long as the analysis accounts for it.

Follow-up 3 of 3

You can't randomise, because the feature launched everywhere. What now?

You can't get the same strength of evidence. Look for a natural experiment, such as a staggered rollout by city, and use a method like difference-in-differences. Then state its assumptions plainly, because hidden causes can remain.

#### The 30-second answer

Randomising makes the groups alike on everything, measured or not, so the only systematic difference is my change, and the difference in means estimates its causal effect. Before and after mixes in trends, and opt-in mixes in who chose it. I'd assign by hashing the user ID with an experiment ID, so it's consistent for a user and independent across tests. I'd default to the user as the unit, go smaller only for changes people can't notice, and use clusters if users affect each other.

**Key terms and sources**

Why random assignment gives a causal answer, how users are hashed into groups, and how to choose between user, session and page-level assignment. · checked 7 Nov 2026

#### Sources

- [Kohavi, Tang and Xu, Trustworthy Online Controlled Experiments (2020), excerpt](https://assets.cambridge.org/97811087/24265/excerpt/9781108724265_excerpt.pdf)

- Correlation vs causation on this site

Lab numbers are illustrative unless a lab says otherwise. Explanations are ours, built from these sources and standard statistics.
