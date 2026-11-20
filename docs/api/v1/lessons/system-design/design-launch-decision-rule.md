# Set a Launch Decision Rule

> A launch wins on the main metric, but looks slightly worse on two guardrails. What's your decision rule before the test starts?

- Track: System Design › Experimentation › Designs
- Type: Design · 25 min
- Page: https://aimlrounds.com/tracks/system-design/design-launch-decision-rule/
- Before this: Choosing Metrics: OEC, Drivers and Guardrails (`fundamentals/choosing-ab-metrics`), Multiple Testing and Segments (`fundamentals/multiple-testing`)
- Quiz topic: `sdexp`

## Intuition

### The situation

A test shows orders per user up significantly. Two of five guardrails, latency and cancellations, are slightly negative but not significant. One person wants to ship, and another wants to wait. You realise no one agreed on a rule. The interviewer asks:

> A launch wins on the main metric, but looks slightly worse on two guardrails. What's your decision rule before the test starts?

#### Ask before designing

- **Which metrics matter?** Which do you want to improve, and which only need to stay safe?

- **What's the margin?** For each guardrail, how much harm would you accept for this gain?

- **What's an acceptable mistake?** Set the false-win rate, and the chance of missing a good change.

- **Who decides?** If a person can override the rule, write down when and how.

- **What's outside the test?** If strategy or legal needs affect the decision, a mechanical rule won't cover them.

### The idea

Think of approving a new medicine. It must be proven to work on at least one main outcome. And for each safety measure, you need evidence that it's no worse than an agreed limit. Having no proof of harm isn't enough, because a small trial might simply have missed it.

[Figure: Four checks. Success metrics must beat control. Guardrails must stay within their margins. A harm check finds evidence of damage. Quality checks confirm the test is valid. Ship only if all four pass.]

_Agree on it before you see any data._

### Play

**Try to break it.** Raise the guardrails to 10, and watch how often a harmless change would pass. Then see what correcting it costs.

#### What do extra guardrails cost?

**The decision.** Tick what your test showed:

At α = 5% and β = 20%, using the simple correction from the paper, with one-sided tests. "All pass" assumes independent guardrails, the worst case. Extra users compare the required size with one uncorrected test. Our own calculation.

Raise the guardrails to **10**. Without a correction, a harmless change would pass them all only about **11%** of the time, so nearly every good change would be blocked. That's the risk that goes unnoticed, and why guardrails need power, not α, corrected.

**Now say why:** why does needing all guardrails to pass reduce power, not raise false wins?

## Architecture

### Architecture

#### In one breath

Agree the rule before the test. **Ship if and only if**: at least one success metric significantly wins, every guardrail is significantly **not worse than an agreed margin**, nothing shows clear harm, and the quality checks pass. "Slightly worse" is only a problem if you can't rule out harm beyond the margin. The surprising part is the error control: because you need **all** guardrails to pass, correct **power** for them, not false positives.

#### Four kinds of check

| Type | The question | The test |
|---|---|---|
| **Success** | Did it get better? | Superiority: is the effect above zero? |
| **Guardrail** | Is it no worse than the margin? | Non-inferiority: is the effect above −margin? |
| **Deterioration** | Is there evidence of harm? | Inferiority: is the effect below zero? Run on success and guardrail metrics too. |
| **Quality** | Is the test itself valid? | Checks like sample ratio mismatch. |

##### Ship if and only if

1. At least one success metric is significantly better.

2. All guardrails are significantly non-inferior.

3. No success, guardrail or deterioration metric shows evidence of harm.

4. No quality test invalidates the experiment.

##### Reading "slightly worse"

Say a guardrail's margin is −1%. Its point estimate is −0.2%.

- **Interval from −0.6% to +0.2%:** it stays above −1%, so the guardrail passes, even though the estimate is below zero.

- **Interval from −1.5% to +1.1%:** harm beyond the margin is still possible, so it hasn't passed. You lack evidence, even though nothing is "significant".

##### Correcting the errors

This is what surprises people. The two kinds of metric need opposite corrections:

| | Success metrics | Guardrails |
|---|---|---|
| **You need** | At least one to win | All of them to pass |
| **Danger** | More metrics give more chances of a false win | More metrics give more chances of failing by accident |
| **False-positive rate** | Divide by the number of metrics: α/S | **No correction:** α |
| **Power** | Plan with β/(G+1) | Plan with β/(G+1) |

#### The numbers worth saying out loud

With 1 success metric and 5 guardrails, at α = 5% and β = 20%, using one-sided tests.

| Question | Working | Result |
|---|---|---|
| Corrected β | 0.2 ÷ (5 + 1) | **0.033, so about 97% power per metric** |
| Normal z-term | (1.645 + 0.842)² | **6.2** |
| Corrected z-term | (1.645 + 1.834)² | **12.1** |
| Extra users | 12.1 ÷ 6.2 | **about twice as many** |

That's the real cost of each extra metric, so keep the list short. A guardrail's sample size also depends on its margin: a tighter margin needs far more users, and a margin of half the size needs four times as many.

## In practice

### In practice

#### What the interviewer will push on

- **Setting margins:** a margin should reflect what harm you'd accept for this benefit. Set it before the test, and in the business's terms, such as a change in churn worth a given amount.

- **Why not correct α for guardrails?** You'd only wrongly pass all of them if every one wrongly passed. Needing all of them to pass already limits false positives. Adjusting α would only make it harder to ship.

- **Correlated metrics:** these corrections hold whatever the correlation, but they're conservative. If metrics move together, you can correct less, with care.

- **Deterioration checks:** these catch clear harm, even on metrics you weren't protecting. Run them sequentially during the test, so you can stop early.

- **Overrides:** a rule won't fit everything. If external factors matter, write down who can override it and record why, so people can learn from it later.

- **Metric bloat:** teams keep adding guardrails. Each costs users, so review the list, and remove those that have never affected a decision.

- **Automation:** build the rule into the platform, so the sample size comes from the plan and the result comes from the rule.

#### How the real team approached it

- **Make the rule explicit:** The team writes one rule covering success, guardrails, harm and quality, so the decision is agreed before anyone sees results.

- **Match the test to the job:** Success metrics use superiority tests, and guardrails use non-inferiority tests against a margin.

- **Correct what actually inflates:** Needing at least one win inflates false wins, so that's corrected for success metrics. Needing all guardrails to pass reduces power, so power is corrected instead.

- **Keep it practical:** The approach is built for clarity, and it holds however the metrics are correlated.

- **Know when not to use it:** They say it doesn't fit decisions that depend partly on factors the experiment can't model.

### The answer that sounds right

#### "It's not significantly worse, so the guardrails are fine"

It sounds right, since no alarm went off. But a small or noisy test can fail to detect real harm. Not significant means you haven't shown harm, not that there's none. So test whether the change is significantly no worse than an agreed margin. If the interval still includes unacceptable harm, you don't have evidence that it's safe.

## Say it

### A launch wins on the main metric, but looks slightly worse on two guardrails. What's your decision rule before the test starts?

#### The interviewer pushes further

Follow-up 1 of 3

Why not correct the significance level for guardrails too?

You only wrongly ship if every guardrail wrongly passes. So requiring all of them already limits the false-positive rate to α. Correcting it further would just block good launches. The paper behind this rule shows this formally, and that it's power that needs the correction.

Follow-up 2 of 3

The guardrail's interval crosses the margin, and the win is big. Do you ship?

By the rule, no: you can't rule out unacceptable harm. Practically, you could extend the test if it was underpowered, since that narrows the interval. If leaders want to accept the risk, they can override, but it should be a recorded choice, not a quiet reinterpretation of the data.

Follow-up 3 of 3

How do you choose a margin?

Work from what the harm would cost compared with the expected benefit, such as how much retention you'd give up for a given revenue gain. It's a business decision, set before the test. Note the trade-off: a tighter margin needs many more users, and halving it needs four times as many.

#### The 30-second answer

I'd agree the rule before the test. Ship if and only if at least one success metric significantly wins, all guardrails are significantly non-inferior, no metric shows evidence of harm, and quality checks like sample ratio mismatch pass. For guardrails, slightly worse isn't the question. I'd look at the confidence interval against the margin we agreed. If it stays above the margin, it passes. If it crosses the margin, we can't rule out unacceptable harm, so it hasn't passed, even if nothing's significant. Corrections are the subtle part. For success metrics, you need at least one to win, so more metrics mean more false wins, and I'd divide alpha by the number. For guardrails, you need all to pass, so I wouldn't correct alpha. Instead, power falls, so I'd plan with beta over guardrails plus one. With five guardrails, that needs about twice as many users. Each metric has a cost, so I'd keep the list short and allow documented overrides for factors outside the test.

**Key terms and sources**

Based on a music streaming company's published framework: [Spotify's post](https://engineering.atspotify.com/2024/3/risk-aware-product-decisions-in-a-b-tests-with-multiple-metrics), read in full, and [its paper](https://arxiv.org/abs/2402.11609), read in part. The lab's sample sizes are our own calculations. Uses choosing metrics, multiple testing and sample size. · checked 5 Nov 2026
