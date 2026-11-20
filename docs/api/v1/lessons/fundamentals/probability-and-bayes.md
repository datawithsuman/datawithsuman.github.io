# Probability Basics & Bayes' Rule

> A 99% accurate fraud flag fires. Is it really fraud?

- Track: Fundamentals › Maths for ML › Probability
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/probability-and-bayes/
- Quiz topic: `prob`

## Intuition

### The situation

Your fraud alarm catches 90% of fraud and wrongly flags 5% of legitimate orders, and 1% of orders are fraud. A teammate says a flagged order is 90% likely to be fraud. The interviewer asks:

> Why can an accurate test for a rare event still produce mostly false positives?

**Running example:** the food-delivery app's fraud alarm. 1% of orders are fraudulent. The alarm catches 90% of fraud (sensitivity) and wrongly flags 5% of legitimate orders (false-positive rate). An order just triggered the alarm. How likely is it to be fraud? (Practise more in Bayes' Rule Practice.)

#### Reasoning backwards from evidence

We usually know how evidence behaves given the truth (the alarm's accuracy was measured on known fraud). We need the reverse: the truth given the evidence. Getting this wrong is common enough to have a name, the base-rate fallacy, and it's behind many over-confident ML decisions: "the model is 95% accurate, so a positive is 95% likely to be right" is false for rare events.

### The idea

Think of a guard at a packed stadium looking for a few pickpockets. Even a good guard stops plenty of innocent people, simply because there are so many more of them. Bayes' rule is how you count both groups before you trust the flag.

[Figure: A bar of 585 flagged orders out of 10,000. A small red part, 90 orders, is real fraud. A much larger part, 495 orders, is legitimate.]

_From the lesson's fraud alarm, counted over 10,000 orders._

### Play

**Try to break it.** Raise sensitivity from 90% to 99%. Then put it back and cut false alarms from 5% to 1%.

#### Natural frequencies make Bayes obvious

Each square is one order (expected counts). Red: fraud; teal: legit; orange outline: flagged. Raise the fraud rate to 10% or cut false alarms to 1% and watch the posterior jump.

Two levers move the answer: the base rate and the false-alarm rate. With a 10% fraud rate the same alarm is right 66.7% of the time; with a 1% fraud rate but a 1% false-alarm rate, 47.6%. Improving sensitivity from 90% to 99% barely helps (16.7%). For rare events, **specificity matters more than sensitivity** for the precision of alerts.

**Now say why:** why does cutting false alarms help so much more than catching more fraud?

## Maths

### Maths

#### In one breath

A probability is a number between 0 and 1 for how likely an event is. **Conditional probability** P(A | B) restricts attention to the cases where B happened. **Independence** means knowing B tells you nothing about A. **Bayes' rule** turns P(B | A), which is often easy to measure ("how often does a fraudulent order trigger the alarm?"), into P(A | B), which is what you want ("this order triggered the alarm: is it fraud?"). The key ingredient people forget is the **base rate**, the prior P(A): when the event is rare, even an accurate test produces mostly false alarms. The easiest way to get Bayes right under pressure is to imagine 10,000 cases and count. What you'll be able to do after this: compute conditional probabilities, apply Bayes' rule by counting, explain why base rates dominate for rare events, and connect it to precision, Naive Bayes and Bayesian updating.

#### Joint, conditional, independent

$$ {P(A\mid B)} = {P(A \cap B)} \,/\, {P(B)}, \qquad {A \perp B \iff P(A\cap B) = P(A)P(B)} $$

Blitzstein & Hwang, _Introduction to Probability_, ch. 2 (free at [stat110](https://projects.iq.harvard.edu/stat110)).

- **conditional probability**: Among the cases where B happened, the share where A also happened.

- **both happen**: P(A and B): the joint probability.

- **restrict to B**: Divide by P(B): we only look inside the B cases.

- **independence**: A and B are independent if P(A | B) = P(A), equivalently P(A and B) = P(A) P(B).

#### The law of total probability

$$ {P(B)} = {P(B\mid A)P(A)} + {P(B\mid \neg A)P(\neg A)} $$

- **overall flag rate**: How often the alarm fires, across everything.

- **via fraud**: P(flag | fraud) P(fraud) = 0.9 × 0.01 = 0.009.

- **via legitimate orders**: P(flag | legit) P(legit) = 0.05 × 0.99 = 0.0495.

Sum over every way B can happen. Here P(flag) = 0.009 + 0.0495 = 0.0585: the alarm fires on 5.85% of orders, almost all of them legitimate.

#### Posterior ∝ likelihood × prior

$$ {P(A\mid B)} = {P(B\mid A)}\,{P(A)} \,/\, {P(B)} $$

0.9 × 0.01 / 0.0585 = 0.154. In odds form: posterior odds = prior odds × likelihood ratio = (1/99) × (0.9/0.05) = 18/99 ≈ 0.18, i.e. 15.4%.

- **posterior**: What we want: P(fraud | flag).

- **likelihood**: How likely the evidence is if the hypothesis is true: P(flag | fraud) = 0.9.

- **prior / base rate**: How common fraud is before seeing evidence: 0.01. The term people forget.

- **evidence**: P(flag), from the law of total probability: 0.0585.

#### Conditional independence

Two events can be linked overall, yet independent once you know a third. Two orders may both tend to be late on the same day, because of rain. Once you know the weather, one order's delay tells you nothing more about the other.

This assumption is what makes models with many variables workable, as in Naive Bayes. See joint, marginal and conditional distributions, with a lab on this.

## In practice

### In practice

#### Bayes in ML

- **Precision is a posterior:** precision = P(actually positive | predicted positive), which collapses for rare classes exactly as above (Classification Metrics, Class Imbalance).

- **Naive Bayes classifiers** apply Bayes' rule with independent features (Naive Bayes).

- **Prior shift:** a model trained at one base rate gives wrong probabilities at another; Bayes' rule corrects them (the undersampling correction in Class Imbalance).

- **Bayesian inference:** priors over parameters, updated by data (MLE & MAP).

### The answer that sounds right

#### "The alarm is 90% accurate, so a flagged order is 90% likely to be fraud"

That confuses P(flag | fraud) = 0.9 with P(fraud | flag). Count 10,000 orders: 100 are fraud and the alarm catches 90 of them. 9,900 are legitimate and 5% of them, 495, are flagged too. Of the 585 flagged orders, only 90 are fraud: **15.4%**. The rare base rate means false alarms outnumber real catches more than 5 to 1. Kahneman & Tversky's taxi-cab experiments showed people routinely ignore base rates this way.

## Say it

### Why can an accurate test for a rare event still produce mostly false positives?

#### The interviewer pushes further

Follow-up 1 of 3

Two tests in a row are positive. What now?

If the tests are conditionally independent given the truth, use the first posterior as the new prior: 0.154 → 0.154 × 0.9 / (0.154 × 0.9 + 0.846 × 0.05) ≈ 0.77.

Follow-up 2 of 3

Is independence the same as mutually exclusive?

No. Mutually exclusive events (can't both happen) are strongly dependent: if one happens, the other's probability drops to 0.

Follow-up 3 of 3

How does this relate to precision and recall?

Recall is P(flag | positive) (sensitivity); precision is P(positive | flag), the Bayes posterior, which depends on prevalence.

#### The 30-second answer

Bayes' rule says the posterior equals likelihood times prior divided by the evidence: P(A | B) = P(B | A) P(A) / P(B), with P(B) from the law of total probability. The classic trap is ignoring the prior: for a rare event, even an accurate test produces mostly false positives because the many negatives each have a small chance of being flagged. I solve these by imagining a population, say 10,000, and counting. In ML this is why precision collapses on imbalanced data, why Naive Bayes works, and how we correct probabilities when base rates change.

**Go further**

#### What not to say

- "P(A | B) = P(B | A)." That's the confusion of the inverse.

- "A 95%-accurate test means a positive is 95% reliable." Depends on the base rate.

**Key terms and sources**

Events, joint and conditional probability, independence, the law of total probability, Bayes' rule, base rates, and where Bayes shows up in ML · built from Blitzstein & Hwang, _Introduction to Probability_ (ch. 1–2), Deisenroth et al., _MML_ (ch. 6) and Kahneman & Tversky's base-rate studies · checked 28 Oct 2026

#### Key terms

| Term | Meaning |
|---|---|
| **Conditional probability** | P(A \| B) = P(A ∩ B)/P(B). |
| **Independence** | P(A ∩ B) = P(A)P(B). |
| **Prior / likelihood / posterior** | Belief before evidence / P(evidence \| hypothesis) / belief after. |
| **Base-rate fallacy** | Ignoring the prior when judging P(hypothesis \| evidence). |
| **Likelihood ratio** | P(B \| A)/P(B \| ¬A): how much the evidence shifts the odds. |

#### Sources

1. J. Blitzstein & J. Hwang, _Introduction to Probability_, 2nd ed., CRC 2019, ch. 1–2, [projects.iq.harvard.edu/stat110](https://projects.iq.harvard.edu/stat110).

2. M. P. Deisenroth, A. A. Faisal & C. S. Ong, _Mathematics for Machine Learning_, CUP 2020, ch. 6.

3. D. Kahneman & A. Tversky, "On the psychology of prediction", _Psychological Review_ 80, 1973 (base-rate neglect; background).
