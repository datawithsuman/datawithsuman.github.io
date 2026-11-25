# Bandits vs A/B Tests

> Why not use a multi-armed bandit instead of an A/B test, so fewer users see the worse version?

- Track: Fundamentals › A/B Testing › Beyond the fixed test
- Type: Concept · 15 min
- Page: https://aimlrounds.com/tracks/fundamentals/bandits-vs-ab-tests/
- Before this: Reading the Result: Significance and Decisions (`fundamentals/reading-ab-results`)
- Quiz topic: `ab`
- Sources checked: 2026-11-07 · Text last changed: 2026-11-20 · Version: 0f850c745f

## Intuition

### The situation

You're choosing between two checkout designs. Each user on the worse one costs money, so someone suggests a multi-armed bandit: it shifts traffic to the winner as you go. The interviewer asks:

> Why not use a multi-armed bandit instead of an A/B test, so fewer users see the worse version?

#### Why it matters

Every user in the losing group has a cost, known as **regret**. Bandits come up in interviews because they seem to remove that cost for free. They don't: you give up something else.

### The idea

Think of two restaurants in a new town. An A/B test eats at each one 20 times, and then you know exactly how they compare. A bandit tries both and goes back more often to whichever seems better. You eat better meals, but you'll never know quite how much worse the other place is.

[Figure: Two methods. An A/B test splits traffic evenly and gives a precise effect. A bandit shifts traffic to the winner, losing fewer conversions but measuring the effect less precisely.]

_You're trading measurement for reward._

### Play

**Try to break it.** Set B equal to A, then raise it. Compare conversions lost with the margin of error.

#### Run both on the same traffic

Our simulation: option A converts at 10%, with instant feedback and beliefs updated every 100 users, averaged over 40 seeded runs. Test and roll sends the first 10% of users 50/50, then everyone to the better arm. Margin of error is the 95% half-width from the final group sizes, for comparison only, as it ignores the adaptive allocation. Conversions lost is against always showing the better option.

Set B to **10%**, the same as A. There's no winner, so nothing's lost, and a bandit can still drift towards one arm by chance. Then raise B: the bandit saves conversions, but look at its margin of error.

**Now say why:** why does a bandit measure the lift less precisely?

## Maths

### Maths

#### In one breath

An A/B test splits traffic evenly to **learn** as clearly as possible. A **bandit** shifts traffic towards the winner as it goes, to **earn** more during the test. **Thompson sampling** picks each arm in proportion to the chance it's best. Bandits lose fewer users to the worse option, but measure effects less precisely and handle slow outcomes poorly. Use them for short-lived choices, and A/B tests for lasting decisions.

#### Explore or exploit

##### Thompson sampling

1. For each arm, keep a belief about its conversion rate, based on results so far.

2. When a user arrives, draw one random value from each belief.

3. Show the arm with the highest draw, then update its belief with what happened.

At first, the beliefs are wide, and traffic is mixed. As one arm pulls ahead, it gets nearly all the traffic, but a weaker arm with an uncertain rate can still get tried.

##### How they compare

| | A/B test | Bandit |
|---|---|---|
| **Main goal** | Measure the effect. | Maximise reward during the run. |
| **Users on the worse arm** | Half, until the test ends. | Falls over time. |
| **Effect estimate** | Precise and easy to explain. | Noisier, and needs care, as traffic share changed with the results. |
| **Slow outcomes** | Fine: wait, then read. | Poor: it needs quick feedback to adapt. |
| **Guardrails and segments** | Straightforward. | Harder, as the worse arm gets little data. |

##### When to use which

- **Bandit:** short-lived choices like headlines and promotions, many variants, quick rewards, and where measuring the exact effect isn't important.

- **A/B test:** lasting product decisions, long-term or several metrics, and whenever you need to explain and defend the size of the effect.

##### A middle option

**Test and roll:** run a short A/B test, then send everyone to the winner. Feit and Berman show that, with the profit-maximising test size, its regret grows at the same rate as Thompson sampling's. Their test is much smaller than a usual hypothesis test, since the aim is to pick well rather than prove a difference.

#### The maths

$$ {\text{Regret}} = \sum_{t=1}^{N} \left({\mu^*} - {\mu_{a_t}}\right), \qquad {p_i} \sim \mathrm{Beta}(1 + s_i,\; 1 + f_i) $$

The Beta distribution suits yes or no outcomes. It starts flat, and narrows with more data.

- **regret**: The reward you lost by not always showing the best arm.

- **best arm’s true rate**: Unknown during the run.

- **rate of the arm shown**: For the arm picked for user t.

- **the belief for an arm**: With s successes and f failures so far. Thompson sampling draws from this for each arm, and shows the highest.

## In practice

### In practice

#### In practice

- **Rewards must arrive quickly:** clicks suit bandits. Retention measured a month later doesn't.

- **Watch for changes over time:** if weekend users behave differently, an early leader can capture the traffic for the wrong reason. Keep some minimum traffic on every arm.

- **Log the probabilities:** record the chance each arm had for each user, so you can correct your analysis afterwards.

- **Contextual bandits:** these choose by user features, moving closer to a recommender.

- **Don't use one where you need a reason:** leadership asks "how much did it help?", and a bandit answers that less well.

### The answer that sounds right

#### "A bandit is simply a better A/B test"

It sounds right, since it loses less during the run. But it answers a different question: which option earns more right now, not how much better one is. For a lasting product decision, you usually need an exact effect across slow and guardrail metrics, and a bandit gives you weaker evidence for those.

## Say it

### Why not use a multi-armed bandit instead of an A/B test, so fewer users see the worse version?

#### The interviewer pushes further

Follow-up 1 of 3

Why not use bandits for everything, if regret is lower?

Because many decisions need a precise effect size across several metrics, including slow ones like retention. Bandits give the weaker arm too little data for that. They also assume the reward arrives quickly, and that arms stay stable over time.

Follow-up 2 of 3

What's the difference between epsilon-greedy and Thompson sampling?

Epsilon-greedy explores at random a fixed share of the time, even once an arm is clearly bad. Thompson sampling explores in proportion to uncertainty, so exploration fades as evidence builds. Thompson sampling usually wastes less.

Follow-up 3 of 3

Why can't you read a bandit's result with a normal A/B test formula?

Because traffic share depended on earlier results. An arm that got lucky early receives more traffic, so simple averages can be biased, and the samples aren't independent. You need methods that account for the allocation, using the logged probabilities.

#### The 30-second answer

A bandit shifts traffic to the better option as it learns, so fewer users see the worse one. Thompson sampling does this by showing each arm according to the chance it's best. But you pay in measurement: the weaker arm gets little traffic, so the effect estimate is noisier, and guardrails and segments are harder. It also needs quick feedback. I'd use a bandit for short-lived choices like headlines, and an A/B test for lasting decisions where I need to know the size of the effect.

**Key terms and sources**

How multi-armed bandits and Thompson sampling trade clean measurement for lower regret, and when to choose each. · checked 7 Nov 2026

#### Sources

- [Feit and Berman, Test and Roll: Profit-Maximizing A/B Tests](https://arxiv.org/abs/1811.00457)

Lab numbers are illustrative unless a lab says otherwise. Explanations are ours, built from these sources and standard statistics.
