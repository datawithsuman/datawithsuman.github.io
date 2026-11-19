# Peeking and Sequential Testing

> Your manager wants to check the test every day and stop as soon as it wins. How do you make that valid?

- Track: Fundamentals › A/B Testing › Reading the result
- Type: Concept · 15 min
- Page: https://aimlrounds.com/tracks/fundamentals/sequential-testing/
- Before this: Reading the Result: Significance and Decisions (`fundamentals/reading-ab-results`)
- Quiz topic: `ab`

## Intuition

### The situation

A test is planned for four weeks. Your manager checks daily, sees p = 0.03 on day five, and wants to ship now, since waiting has a cost. The interviewer asks:

> Your manager wants to check the test every day and stop as soon as it wins. How do you make that valid?

#### Why it matters

The hypothesis testing lesson shows that peeking is a problem. This lesson covers how to fix it, because teams do have good reasons to stop early, such as a change that's clearly harming users.

### The idea

Think of a coin you check after every flip, stopping when it looks biased. Check often enough, and even a fair coin will look lopsided at some point. If you plan to check often, you have to demand stronger evidence each time.

[Figure: Three ways to look. A fixed test keeps a 5 percent false win rate. Stopping at the first p below 0.05 over 20 looks gives about 25 percent. Sequential methods keep it at 5 percent with stricter thresholds.]

_From our simulation of tests with no real effect._

### Play

**Try to break it.** Drag the looks from 1 to 50, and watch the false wins. Then compare the two O'Brien-Fleming columns.

#### Look more often

False wins are from our simulation of 200,000 tests with no real effect (60,000 at 50 looks), with equally spaced looks. Boundaries are calculated numerically, and both corrected methods keep the false-win rate at 5%. Compare with the usual threshold of 1.96.

Compare the **first** and **last** look for O'Brien-Fleming. Early on it demands overwhelming evidence, and by the end it's close to the normal 1.96. That's why many teams prefer it.

**Now say why:** why does each extra look raise the false-win rate?

## Maths

### Maths

#### In one breath

A normal p-value is only valid at one planned sample size. Stop at the first p below 0.05 and, with 20 looks at a test with no real effect, you'll declare a false win about **25%** of the time, not 5%. To look early, plan for it: **Pocock** or **O'Brien-Fleming** boundaries set stricter thresholds for each look, and **always-valid p-values** let you stop at any time. You pay for that flexibility with some power.

#### Why looking breaks it, and the fixes

Under no real effect, the running p-value wanders up and down. Every look is another chance for it to dip below 0.05. Stopping at the first dip means you catch the noise at its most extreme point. Looking at a dashboard is harmless in itself. The damage comes from **acting** on what you see.

| Method | How it works | Trade-off |
|---|---|---|
| **Fixed horizon** | Decide on the size, then read it once. | Most power per user, but you can't stop early. |
| **Pocock** | Planned looks, with the same stricter threshold each time. | Stops early more easily, but the last look is much stricter. |
| **O'Brien-Fleming** | Planned looks, very strict early, close to normal at the end. | Early stops only for huge effects, and the final look costs little. |
| **Always-valid (mSPRT)** | A p-value that stays valid however often you look and whenever you stop. | Most flexible, but needs more users than a fixed test of the same size. |
| **Bayesian** | Reports a probability that B is better. | Answers a different question. Its guarantees hold on average over the prior, with proper stopping rules, so a poor prior or a bad stopping rule can still mislead. |

##### Stopping for harm is different

Stopping because a guardrail shows clear damage is sensible, and you should plan for it. Be stricter about stopping early for a **win**, because that's what inflates false wins and overstates the effect.

##### Bayesian A/B tests

A Bayesian test starts from a prior, updates it with the data, and reports things like the chance that B beats A. A common stopping rule uses **expected loss**: if I choose B and I'm wrong, how much do I lose on average? Stop when that's below a level you don't care about, which Stucchio calls the threshold of caring.

- **What people like:** the result is easy to explain, and it answers the decision directly.

- **What it doesn't do:** it doesn't make peeking free. Deng et al. show Bayesian testing with continuous monitoring is valid only under proper stopping rules, and point out common bad practices.

- **Priors matter:** a prior from past experiments helps, and a careless one misleads, especially early when there's little data.

#### The maths

$$ |Z_k| > c\,\sqrt{K/k} $$

This is the O’Brien-Fleming shape. For Pocock, the threshold is a constant at every look instead: about 2.41 with 5 looks, compared with the usual 1.96.

- **the z-score at look k**: How many standard errors the difference is, using the data so far.

- **the boundary constant**: Chosen so the overall false-positive rate stays at 5% across all looks. With 5 looks it’s about 2.04.

- **stricter when early**: With few users, k is small and this term is large. At the last look k = K, so it equals 1.

## In practice

### In practice

#### In practice

- **Plan the looks:** decide how often you'll check before launch. Alpha-spending methods can adapt to some changes, but they must be planned.

- **Separate monitoring from deciding:** dashboards can show guardrails daily, while the main decision waits for the plan.

- **Early stops overstate wins:** stopping when a result crosses a line picks a high moment, so the estimate tends to be too large, even if the decision is valid.

- **Weekly cycles still apply:** a valid early stop on day two still hasn't seen a weekend.

- **Choose by need:** use a fixed test when you can wait, planned looks when you have a schedule, and always-valid methods for continuous monitoring.

### The answer that sounds right

#### "Just use a lower p-value of 0.01 when peeking"

It sounds right, since it's stricter. But a fixed 0.01 isn't tied to how many looks you take. With few looks, you lose power for nothing. With many, you can still exceed your error rate. Use boundaries calculated for your plan.

## Say it

### Your manager wants to check the test every day and stop as soon as it wins. How do you make that valid?

#### The interviewer pushes further

Follow-up 1 of 3

Isn't looking at a dashboard harmful in itself?

No. The inflation comes from changing what you do based on what you see, mainly stopping when it looks good. If you look but always run to the planned end, the error rate stays at 5%. The risk is that people find it hard not to act.

Follow-up 2 of 3

Why would anyone choose O'Brien-Fleming over Pocock?

It keeps nearly the full power of a fixed test, because its last threshold is close to 1.96. It only stops early for very large effects, which are the ones you're safest acting on. Pocock stops early more readily, but pays with a much stricter final threshold.

Follow-up 3 of 3

You stopped early for a clear win, and the lift was 12%. Is it 12%?

Probably less. Stopping when a result crosses a line selects a moment when noise was pushing it up, so the estimate is biased upward. The decision can be valid while the size is overstated. A holdback or later measurement gives a fairer number.

A normal p-value is valid at one planned sample size. If we stop at the first p below 0.05, we're catching noise at its peak: with 20 looks, false wins rise to about 25%. To look daily, I'd plan for it. O'Brien-Fleming boundaries are very strict early and close to normal at the end. Always-valid p-values, like mSPRT, allow stopping at any time, for some loss of power. I'd keep stopping for harm separate from stopping for a win, and still cover full weeks.

**Key terms and sources**

Why stopping at the first significant result inflates false positives, and how alpha spending and always-valid methods let you look safely.

#### Sources

- Johari et al., Peeking at A/B Tests (KDD 2017), summarised by The Morning Paper

- Always-valid p-values at Wish

- Sequential A/B testing notes

- Johari, Pekelis and Walsh, Always Valid Inference

- Deng, Lu and Chen, Continuous Monitoring of A/B Tests without Pain

- Stucchio, Bayesian A/B Testing at VWO

Lab numbers are illustrative unless a lab says otherwise. Explanations are ours, built from these sources and standard statistics.
