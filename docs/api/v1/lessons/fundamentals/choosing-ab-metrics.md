# Choosing Metrics: OEC, Drivers and Guardrails

> How do you choose the metrics for an A/B test, and what is a guardrail metric?

- Track: Fundamentals › A/B Testing › Designing a test
- Type: Concept · 15 min
- Page: https://aimlrounds.com/tracks/fundamentals/choosing-ab-metrics/
- Before this: Randomisation and Assignment (`fundamentals/randomisation-and-assignment`)
- Related: Choosing the Right Metric (`fundamentals/choosing-the-right-metric`)
- Quiz topic: `ab`

## Intuition

### The situation

Your team has built a new home page. One person wants to judge it on clicks, another on revenue and a third on time spent. It's also a little slower to load. The interviewer asks:

> How do you choose the metrics for an A/B test, and what is a guardrail metric?

#### Why it matters

The metric decides what your team optimises. Pick revenue alone, and the easy win is to fill the page with ads. The test would call that a success, while people slowly stop coming back.

### The idea

Think of a doctor judging a new diet. One number decides: long-term health. Other readings explain why it changed, like weight and sleep. And some limits must never be crossed, like blood pressure, however good the rest looks.

[Figure: Three jobs for metrics. The overall evaluation criterion decides. Drivers explain why. Guardrails protect what must not break.]

_Illustrative examples of each type._

### Play

**Try to break it.** Raise orders by 5%, then push latency past 100 ms. Then lower orders and improve everything else.

#### Would you ship this?

Illustrative limits: at most 100 ms added latency and at most 0.2 points more cancellations. Treat these as measured results. In a real test, you'd use the confidence interval.

A win with a broken guardrail isn't an automatic yes or no. It's a trade-off for people to discuss, and it often means fixing the harm and running the test again.

**Now say why:** why is “no significant change” not enough to pass a guardrail?

## Maths

### Maths

#### In one breath

Decide your metrics before the test starts. One **overall evaluation criterion (OEC)** decides success, and it should move within the test and predict long-term value. **Driver metrics** explain why it moved. **Guardrails** are limits you mustn't break, like latency or cancellations. A rise in the wrong metric can be a bad sign, so choosing it badly can reward a broken product.

#### Three jobs for metrics

| Type | Job | Example for a food-delivery app |
|---|---|---|
| **OEC** | Decides whether you ship. | Completed orders per user. |
| **Driver** | Explains why the OEC moved. | Menu views, add-to-cart rate, checkout starts. |
| **Guardrail: business** | Protects what must not get worse. | App latency, cancellations, refunds, crashes. |
| **Guardrail: trust** | Tells you whether the test itself is valid. | Sample ratio mismatch. |

##### What makes a good OEC

- **It predicts long-term value:** it should causally lead to what you really care about, like retention.

- **It's sensitive:** it moves enough to detect within a few weeks. Annual revenue is what you care about, but it can't guide a two-week test.

- **It's hard to game:** clicks and time spent can rise because something got more confusing.

- **It's per randomisation unit:** a per-user metric is simple to analyse. See ratio metrics otherwise.

If several things matter, agree on how to trade them off before the test, so nobody picks the winner afterwards.

#### The maths

$$ CI_{low}(\Delta) > -m $$

A guardrail is a non-inferiority check. “No significant change” isn’t enough, because a small test can miss real harm. For a metric where higher is worse, flip the sign. A 95% two-sided interval is the stricter choice. A one-sided test at 5%, as in the launch decision rule, matches a 90% interval, so agree on one before the test. A 95% two-sided interval is the stricter choice. A one-sided test at 5%, as in the launch decision rule, matches a 90% interval, so agree on one before the test. A 95% two-sided interval is the stricter choice. A one-sided test at 5%, as in the launch decision rule, matches a 90% interval, so agree on one before the test. A 95% two-sided interval is the stricter choice. A one-sided test at 5%, as in the launch decision rule, matches a 90% interval, so agree on one before the test.

- **lower end of the interval**: The worst change in the guardrail that the data still considers plausible, from the 95% confidence interval.

- **allowed margin**: The most harm you agreed to accept, set before the test, like 0.2 points more cancellations.

## In practice

### In practice

#### In practice

- **A real warning:** a Bing bug showed users very poor search results. Queries per user rose over 10% and revenue per user over 30%, since people searched more and clicked more ads to find what they needed. Bing moved to an OEC that includes sessions per user.

- **Write it down first:** record the OEC, the guardrails, their limits and the runtime before launch.

- **Keep it short:** dozens of decision metrics invite cherry-picking. See multiple testing.

- **Check drivers point the same way:** if orders rise but add-to-cart doesn't, suspect a bug.

- **Use a proxy with care:** check from past tests that it predicts the long-term metric.

### The answer that sounds right

#### "Revenue is what the business wants, so use revenue"

It sounds right, since revenue is the goal. But short-term revenue can rise while the product gets worse. A Bing bug showed worse results, and revenue per user rose over 30%. Use a metric that predicts long-term value, with revenue as one input.

## Say it

### How do you choose the metrics for an A/B test, and what is a guardrail metric?

#### The interviewer pushes further

Follow-up 1 of 3

Why not just use revenue as the OEC?

Short-term revenue can rise while the product gets worse. More ads raise revenue today and drive people away later. A Bing bug even raised revenue per user by showing worse results. So balance revenue against metrics of the user's experience, like sessions per user.

Follow-up 2 of 3

A guardrail shows no significant change. Is it safe?

Not necessarily, because the test may be too small to detect harm. Check whether the confidence interval rules out harm larger than your agreed margin. If the interval is too wide to say, you need more data.

Follow-up 3 of 3

Your OEC is flat, but one driver metric rose a lot. Do you ship?

No, not on that alone. Either the driver doesn't lead to the outcome you care about, or users shifted activity without gaining anything. Ask why it didn't flow through, and treat it as a lead for a new test.

I'd fix three kinds of metric before launch. One overall evaluation criterion decides success: it must move within the test, predict long-term value and be hard to game. Driver metrics explain why it moved. Guardrails set limits on what mustn't get worse, like latency and cancellations, plus trust checks like sample ratio mismatch. For a guardrail I'd check the confidence interval against an agreed margin, because no significant change doesn't prove no harm.

**Key terms and sources**

The overall evaluation criterion, driver metrics and guardrails: what to decide on, what explains it and what must not break.

#### Sources

- Kohavi et al., Trustworthy Online Controlled Experiments Explained: Five Puzzling Outcomes (KDD 2012)

- Book chapter on metrics and the OEC

- Book chapter on guardrail metrics

Lab numbers are illustrative unless a lab says otherwise. Explanations are ours, built from these sources and standard statistics.
