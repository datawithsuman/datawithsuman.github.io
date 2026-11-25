# Drift Detection and Monitoring

> How do you know a model is degrading before labels arrive?

- Track: AI Engineering › MLOps › Lessons
- Type: Concept · 25 min
- Page: https://aimlrounds.com/tracks/ai-engineering/drift-detection-and-monitoring/
- Before this: Training/Serving Skew and Feature Stores (`ai-engineering/training-serving-skew-and-feature-stores`)
- Quiz topic: `mlops`
- Sources checked: 2026-10-29 · Text last changed: 2026-11-20 · Version: 4d873ce1b9

## Intuition

### The situation

The ETA model was trained when most orders were within 5 km, and the company is expanding into suburbs. A crashed service pages someone, but a degrading model keeps returning numbers. A colleague sets an alert for whenever a statistical test says the data changed. The interviewer asks:

> How do you know a model is degrading before labels arrive?

**Running example:** the ETA model was trained when most orders were within 5 km. The company is expanding into suburbs, and delivery distances are creeping up.

#### No error message when a model gets worse

A crashed service pages someone; a model that's slowly getting less accurate keeps returning numbers with full confidence. Without monitoring, the first signal is customer complaints, weeks later.

### The idea

Think of a smoke alarm so sensitive that it goes off when you make toast. Soon enough, someone takes the battery out. A good alarm goes off when there's actually a problem. With enough data, a statistical test is that over-sensitive alarm.

[Figure: A 10 percent shift over 5,000 orders gives PSI 0.029, which reads stable, and KS p below 0.0001. A 2 percent shift over 50,000 orders gives PSI 0.002 and KS p of 0.0003.]

_From the lab: PSI under 0.1 reads as stable. The KS test flags changes too small to matter._

### Play

**Try to break it.** Set a 10% increase over 5,000 orders. Then a 2% increase over 50,000. Then push the increase to 20% and 30%, and compare PSI with the KS p-value.

#### "Alert whenever a statistical test says the data changed"

Training baseline: 20,000 log-normally distributed delivery distances; live window: fresh samples scaled by the chosen increase. PSI over 10 bins at the baseline's deciles; two-sample KS test with its asymptotic p-value. Fixed seed.

A **10%** increase in distances over **5,000** orders gives PSI **0.029**, comfortably "stable", but the KS test's p-value is below **0.0001**. Push the window to 50,000 orders and even a **2%** change is "significant" (p = 0.0003) while PSI is 0.002: with enough data, a hypothesis test detects differences far too small to matter, so p-value alerts fire constantly and get ignored. PSI reaches "moderate" at about a 20% increase (0.118) and approaches "large" at 30% (0.245). With no change, neither fires. The useful question isn't "did anything change?" but "did it change enough to hurt?": tie alert thresholds to effect sizes that historically moved error, check performance once labels arrive, and look by slice (the suburbs may have shifted a lot while the city average barely moved).

**Now say why:** a 2% shift is "significant", so why not act on it?

## How it works

### How it works

#### In one breath

Models degrade silently because the world changes. **Data drift** (covariate shift): the inputs change, e.g. longer delivery distances after expanding to suburbs. **Concept drift**: the same inputs now mean different outcomes, e.g. the same distance takes longer during monsoon traffic. The best signal is **performance** on fresh labels, but labels often arrive late (an ETA's truth is known within an hour; fraud's, after weeks of chargebacks), so you also watch **proxies**: data quality, input and prediction distributions. Drift statistics need judgement: **PSI** measures how much a distribution moved (rules of thumb: under 0.1 stable, 0.1–0.25 moderate, above 0.25 large); a **KS test** asks whether there's _any_ difference, and with large samples it flags changes too small to matter. Alert on what affects the business, by slice, with owners and runbooks. What you'll be able to do after this: design a monitoring plan, explain data vs concept drift, and interpret PSI and KS sensibly.

#### Layers of monitoring

| Layer | Examples | Needs labels? |
|---|---|---|
| **System** | latency, errors, throughput, fallback rate | no |
| **Data quality** | missing values, schema changes, out-of-range values, stale features | no |
| **Input drift** | feature distributions vs training (PSI, KS, by slice) | no |
| **Prediction drift** | distribution of ETAs vs normal | no |
| **Performance** | MAE vs actual delivery times, by city and hour | yes (delayed) |
| **Business** | late-delivery complaints, cancellations | outcome data |

- **Data drift** changes P(x); **concept drift** changes P(y | x). Drift can be **sudden** (a policy change), **gradual** (suburban expansion) or **recurring** (festivals, monsoon) (Gama et al. 2014).

- Many data "drifts" are actually **pipeline bugs** (a unit change, a broken join): data-quality checks catch those first.

See comparing distributions for how PSI, Jensen-Shannon and Wasserstein differ.

## In practice

### In practice

#### Monitoring that people trust

- **Prioritise:** performance on labels when available; for delayed labels, prediction drift and the most important features' drift as early warnings.

- **Slice everything** by city, segment and new vs existing entities; averages hide local breakage.

- **Calibrate thresholds** on history (how often would this have fired, and did it matter?); prefer effect sizes and sustained changes over single-window p-values. Rabanser et al. found simple univariate tests with multiple-testing correction work well to detect that a shift exists; whether it matters is a separate question.

- **Owners and runbooks:** every alert has an owner and a first step (check pipelines, compare slices, consider retraining or rollback).

- **LLM apps** add output-quality monitoring (sampled judge scores, escalations, user feedback); see LLMOps.

Labels late? You can estimate accuracy from calibrated probabilities while you wait, as long as only the input mix changed. See Monitoring Without Labels.

#### Monitor what hurts, early and by slice

Watch system health, data quality, input and prediction distributions and, as soon as labels allow, real performance; set alert thresholds on changes large enough to matter, not on any statistically detectable change.

### The answer that sounds right

#### "Alert when the KS test is significant"

It sounds right, since significance is what tests are for. But at scale it always is: in the lab, a 2% shift over 50,000 orders gives p = 0.0003, with a PSI of just 0.002. Alerts fire constantly and get ignored. Ask whether it changed enough to hurt. "Monitor accuracy daily" fails too, because labels may not exist yet.

## Say it

### How do you know a model is degrading before labels arrive?

#### The interviewer pushes further

Follow-up 1 of 3

Labels arrive 60 days later (fraud). What do you monitor meanwhile?

Prediction score distribution, feature drift on key features, data quality, proxy labels (early chargebacks, manual review outcomes) and business signals.

Follow-up 2 of 3

Inputs didn't drift but accuracy dropped. What happened?

Concept drift (the relationship changed), a label pipeline change, or a slice-level shift hidden in the average; check performance by slice and the label definition.

Follow-up 3 of 3

How do you avoid alert fatigue?

Fewer, calibrated alerts tied to impact, sustained-change rules, grouping, clear owners, and regular review of alerts that didn't lead to action.

#### The 30-second answer

I'd monitor in layers: system health, data quality like missing values and schema changes, input and prediction distributions compared with training, and real performance once labels arrive, plus business outcomes. Data drift is a change in the inputs; concept drift is a change in how inputs map to outcomes, and only performance monitoring catches the latter directly. Because labels are often delayed, distribution drift is an early warning. I'd use effect-size measures like PSI with calibrated thresholds rather than raw p-values, since with large samples tests like KS flag trivial changes, and I'd monitor by slice with owners and runbooks for every alert.

**Go further**

#### What not to say

- "Alert when the KS test is significant." At scale it always is.

- "Monitor accuracy daily." Labels may not exist yet.

**Key terms and sources**

How to know a production model is degrading: data drift (inputs change), concept drift (the input→output relationship changes), label delay, what to monitor at each layer (system, data quality, input and prediction distributions, performance, business), drift statistics (PSI, KS test) and their pitfalls, and alerting that people won't ignore · built from Lu et al. (Learning under Concept Drift: A Review, IEEE TKDE 2019), Rabanser et al. (Failing Loudly, NeurIPS 2019), Gama et al. (A Survey on Concept Drift Adaptation, ACM CSUR 2014), Breck et al. (ML Test Score, 2017), Shankar et al. (Operationalizing ML, 2022) and Huyen (Designing ML Systems, 2022) · checked 29 Oct 2026

#### Sources

1. J. Lu et al., "Learning under Concept Drift: A Review", IEEE TKDE 2019, [arXiv:2004.05785](https://arxiv.org/abs/2004.05785); J. Gama et al., "A Survey on Concept Drift Adaptation", ACM CSUR 2014.

2. S. Rabanser, S. Günnemann & Z. Lipton, "Failing Loudly: An Empirical Study of Methods for Detecting Dataset Shift", NeurIPS 2019, [arXiv:1810.11953](https://arxiv.org/abs/1810.11953).

3. E. Breck et al., "The ML Test Score", IEEE Big Data 2017; S. Shankar et al., "Operationalizing Machine Learning: An Interview Study", 2022, [arXiv:2209.09125](https://arxiv.org/abs/2209.09125).

4. C. Huyen, _Designing Machine Learning Systems_, O'Reilly 2022 (ch. 8, data distribution shifts and monitoring).
