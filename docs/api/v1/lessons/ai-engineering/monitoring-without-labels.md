# Monitoring Without Labels: Estimating Performance

> Your fraud model's labels arrive 60 days late. How do you know its accuracy today?

- Track: AI Engineering › MLOps › Lessons
- Type: Concept · 18 min
- Page: https://aimlrounds.com/tracks/ai-engineering/monitoring-without-labels/
- Before this: Drift Detection and Monitoring (`ai-engineering/drift-detection-and-monitoring`)
- Quiz topic: `mlops`
- Sources checked: 2026-11-07 · Text last changed: 2026-11-20 · Version: 808e159b5a

## Intuition

### The situation

Your fraud model's labels arrive after 60 days of chargebacks. The drift dashboard shows several features moved this month, and the risk team asks whether the model is still accurate today. The interviewer asks:

> Your fraud model's labels arrive 60 days late. How do you know its accuracy today?

#### Why it matters

Many models learn the truth late. A fraud label waits for chargebacks, a loan default takes months, and a churn label takes a quarter. Meanwhile, drift monitoring can tell you that inputs changed, but not by how much accuracy changed, if at all. Many shifts don't hurt the model, and some that hurt don't look big. Interviewers ask how you'd estimate performance in that gap.

### The idea

Think of a weather forecaster who says 70% chance of rain. If they're well calibrated, it rains on 7 of every 10 such days. So you can estimate how often they'll be right this week before the week ends, unless the climate itself has changed.

[Figure: Three signals while labels are late. Estimate from calibrated confidence. Use proxy labels. Label a small sample.]

_Confident and wrong is the case estimates can't see._

### Play

**Try to break it.** Raise the share of hard cases. Then let the meaning change too.

#### When the estimate holds, and when it doesn't

Illustrative. Easy predictions have 0.95 confidence and hard ones 0.65, both calibrated in training. "The meaning changes" lowers their real accuracy to 85% and 50% without changing the model's confidence.

At 20% hard cases, the estimate and the real accuracy agree at 89%. Raise hard cases to 50%, as when a fraud team starts seeing a new merchant mix, and both fall to 80%: the estimate tracked the change without a single label. Now switch to **the meaning changes too**. The model is just as confident, so the estimate still says 80%, but real accuracy is 67.5%. That's why estimation needs a small labelled sample beside it.

**Now say why:** why does the estimate follow one change but miss the other?

## How it works

### How it works

#### In one breath

Drift statistics say the inputs moved, not whether accuracy fell. If a model's probabilities are **calibrated**, you can estimate its accuracy without labels: a prediction made with 90% confidence is right about 90% of the time, so averaging confidence over today's predictions estimates today's accuracy. That's **confidence-based performance estimation** (CBPE). It works when only the mix of inputs changes (covariate shift), such as more hard cases. It fails when the meaning changes (concept drift), because the model stays just as confident while being wrong more often. So pair it with proxy labels, a small daily labelled sample, and real labels when they arrive.

#### How estimation works

##### Confidence-based performance estimation

For a binary classifier, each prediction comes with a probability. If those probabilities are calibrated, a prediction of "fraud, 0.8" is right 80% of the time, and one of "not fraud, 0.1" is right 90% of the time. Averaging these over a day's predictions estimates the day's accuracy. Doing the same per cell of the confusion matrix gives estimates of precision, recall, F1 and AUROC too. This is CBPE, and with perfect calibration its estimates are unbiased.

##### Keeping calibration under shift

Calibration measured on the test set can break when the input mix changes. PAPE, presented at NeurIPS 2025, re-calibrates using weights that say how much more common each kind of input has become in production. Across over 900 dataset and model combinations from US census data, its accuracy estimates were on average within about one standard error of the real value (0.97), against 1.62 for simply assuming test-set accuracy still holds, and 1.08 for plain CBPE.

##### Where it fails

- **Concept drift:** if the same inputs now lead to different outcomes, such as a new fraud pattern that looks normal, the model is confidently wrong, and the estimate stays high. The PAPE paper says plainly that it won't work under concept shift.

- **New kinds of input:** inputs unlike anything in training can't be re-weighted.

- **Poor calibration:** estimates are only as good as the probabilities. Check calibration on the test set first.

##### Other signals while labels are late

- **Proxy labels:** early signals that correlate with the truth, such as a customer disputing a payment within days.

- **A small labelled sample:** have people label, say, 200 random predictions a week. It catches concept drift that estimation can't.

- **Business outcomes:** manual review rates, complaints and losses.

#### The maths

$$ {\widehat{\text{acc}}} = \frac{1}{n}\sum_{i=1}^{n} {\max(p_i,\ 1-p_i)} $$

This is valid only if the probabilities are calibrated on today's data. Under concept drift, they aren't, and the estimate is too high.

- **estimated accuracy**: Today’s accuracy, estimated without any labels.

- **confidence in the predicted class**: For a prediction of positive with p = 0.8, the chance it’s right is 0.8. For p = 0.1, it’s 0.9.

## In practice

### In practice

#### In practice

- **Check calibration first:** on the test set, by slice. If it's poor, recalibrate before trusting estimates.

- **Estimate by slice:** per segment, city or product, since averages hide local drops.

- **Alert on estimated performance:** it's in the units the business cares about, unlike drift scores.

- **Label a small random sample:** weekly, to catch concept drift and check the estimates.

- **Reconcile when labels arrive:** compare past estimates with real results, and learn how far to trust them.

### The answer that sounds right

#### "Drift is low, so the model is fine"

It sounds right, since nothing moved much. But concept drift changes outcomes without changing inputs, and a model can stay confident while getting worse. Check a small labelled sample, and watch business outcomes.

## Say it

### Your fraud model's labels arrive 60 days late. How do you know its accuracy today?

#### The interviewer pushes further

Follow-up 1 of 3

Estimated accuracy is stable, but chargebacks are rising. What's happening?

Probably concept drift: a new fraud pattern the model scores confidently as normal. Confidence-based estimates can't see it. Check a labelled sample of recent cases, and look at the slices where chargebacks rose.

Follow-up 2 of 3

Why not just alert on drift scores?

Many drifts don't hurt accuracy, and a drift score isn't in the units that matter. An estimated metric, per slice, ties alerts to impact.

Follow-up 3 of 3

What must be true for CBPE to work?

Calibrated probabilities, and a shift in the input mix only, not in how inputs relate to outcomes. Inputs must also look like ones seen in training.

#### The 30-second answer

Drift scores tell me inputs moved, not whether accuracy fell. If the model's probabilities are calibrated, I can estimate accuracy from them: average the confidence in each predicted class, or estimate the whole confusion matrix, which is CBPE. PAPE re-calibrates for the new input mix and was within about one standard error on census benchmarks. But it assumes only the mix changed. Under concept drift the model stays confident while being wrong, so I'd add proxy labels, a small weekly labelled sample, and reconcile with real labels when they arrive.

**Key terms and sources**

Why drift statistics don't tell you accuracy, how confidence-based estimation (CBPE, PAPE) estimates performance from a model's own probabilities, what it assumes, where it fails, and how to combine it with proxy labels and small labelled samples. · checked 7 Nov 2026

#### Sources

- [Białek, Kivimäki, Kuberski and Perrakis, Estimating Model Performance Under Covariate Shift Without Labels (PAPE), NeurIPS 2025](https://arxiv.org/abs/2401.08348)

- [Kivimäki et al., Performance Estimation in Binary Classification Using Calibrated Confidence (CBPE)](https://arxiv.org/abs/2505.05295)

- [Rabanser, Günnemann and Lipton, Failing Loudly: detecting dataset shift](https://arxiv.org/abs/1810.11953)

- [Guo et al., On Calibration of Modern Neural Networks](https://arxiv.org/abs/1706.04599)

Explanations are ours, built from these sources. Lab numbers are illustrative unless a lab says otherwise. Many recent papers are preprints, and provider policies change.
