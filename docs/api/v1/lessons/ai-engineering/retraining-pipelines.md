# Retraining Pipelines and Continuous Training

> How often should you retrain, and what stops a bad retrain?

- Track: AI Engineering › MLOps › Lessons
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/ai-engineering/retraining-pipelines/
- Before this: Drift Detection and Monitoring (`ai-engineering/drift-detection-and-monitoring`), Deployment Patterns: Shadow, Canary, A/B and Rollback (`ai-engineering/deployment-patterns`)
- Quiz topic: `mlops`

## Intuition

### The situation

The ETA model's error grows slowly as the city changes, and jumps during festivals, the monsoon or a policy change. One colleague says quarterly is fine, and another says to retrain automatically every day and deploy. The interviewer asks:

> How often should you retrain, and what stops a bad retrain?

**Running example:** the ETA model's error grows slowly as the city changes (new restaurants, roads, habits), and jumps during a few events each year (festivals, monsoon, a new delivery policy). How often should it be retrained?

#### A model starts going stale the day it ships

The model learned last quarter's world. Retraining manually is slow and error-prone, and teams that rely on someone remembering to do it end up with models that are months stale. But retraining isn't free, and an unchecked automatic retrain can ship a worse model.

### The idea

Think of servicing a delivery bike. Regular servicing handles slow wear, and a warning light handles sudden faults. But nobody puts it back on the road without checking it, or you might ride out on a bad repair. Schedule, triggers and a gate.

[Figure: Quarterly retraining: 7.54 minutes of drift-peak error and 45 days stale after a shift. Monthly: average 5.85 minutes, 12 retrains and 15 days stale. Monthly with triggers: 5.63 minutes, 16 retrains and 2 days stale.]

_From the lab's illustrative model. Quarterly error is where the drift peaks, and the others are yearly averages._

### Play

**Try to break it.** Set the schedule to quarterly, monthly and weekly, watching the error and the cost. Then add triggers on sudden shifts.

#### "Retrain every quarter, it's fine"

Illustrative model: error is 5.0 minutes right after training and grows 0.04 minutes per day; four sudden shifts a year each add 1.5 minutes of error until the next retrain (a trigger retrains within 2 days).

**Monthly** retraining averages **5.85 minutes** of error for 12 retrains a year; **weekly** brings it to 5.20 but costs 52 retrains; **quarterly** lets error drift up to 7.54. The schedule mostly controls slow drift. Sudden shifts are different: with a schedule alone, the model is stuck with the old world for half a cycle on average (**15 days** monthly, 45 days quarterly). Adding **triggers** that retrain within about 2 days of a detected shift cuts that, bringing the monthly plan to **5.63** minutes for just 4 extra retrains. The trap in the other direction: retraining automatically on whatever data arrived. If the shift is a broken data feed, the trigger trains on garbage; that's what the validation and "beat production" gates are for.

**Now say why:** if the shift is really a broken data feed, what does an automatic trigger do?

## How it works

### How it works

#### In one breath

Because the world drifts, most models need regular retraining. **Scheduled** retraining (weekly, monthly) is simple and predictable; **triggered** retraining reacts to monitoring (performance drop, large drift, a known event). The retraining job is a **pipeline**, not a person: validate the new data, train, evaluate against the **current production model** on the same recent test set and key slices, and only then promote through the usual staged rollout. Retraining more often lowers average error but costs compute and review time, and automated retraining on **bad data** (a broken pipeline, a fraud wave, the model's own feedback) can make things worse fast. So: automate the pipeline, gate every new model, and combine a schedule with triggers for sudden changes. What you'll be able to do after this: choose a retraining strategy, design an automated pipeline with gates, and name the risks of automatic retraining.

#### An automated retraining pipeline

1. **Trigger:** schedule, performance or drift alert, new data volume, or a known event.

2. **Data validation:** schema, ranges, missing rates, label sanity, comparison with the previous window; stop on anomalies.

3. **Build the training set:** a sliding window (e.g. last 90 days) or all data with recent examples weighted more; point-in-time features.

4. **Train** with recorded config, seeds and data snapshot (tracking).

5. **Evaluate against production:** same recent test set, key slices, fairness and latency checks; must beat (or match) the current model.

6. **Register and roll out** via shadow/canary with automatic rollback; humans approve when the change is large or the domain is high-risk.

Google's MLOps maturity levels describe the progression: level 0 manual, level 1 an automated training pipeline (continuous training), level 2 automated CI/CD of the pipeline itself.

## In practice

### In practice

#### Risks and good practice

- **Bad-data retrains:** pipeline bugs, label delays (training on incomplete labels), adversarial waves (fraud); validate data and compare with the previous model before promoting.

- **Feedback loops:** models trained on data shaped by their own predictions (recommendations, pricing) reinforce themselves; keep exploration or holdout traffic for unbiased data.

- **Window choice:** short windows adapt fast but forget rare seasons; long windows are stable but slow; weighting recent data is a middle ground.

- **Warm-start vs from scratch:** fine-tuning the previous model is cheaper; periodic full retrains avoid accumulating quirks.

- **Measure the value:** track how much each retrain improved the target metric; if it rarely helps, retrain less.

For how models shape their own training data, and how exploration and logged probabilities fix it, see Feedback Loops and Unbiased Training Data.

#### Automate retraining, but gate every model it produces

A schedule handles slow drift and triggers handle sudden shifts, but every retrained model must pass data validation and beat production before it ships.

### The answer that sounds right

#### "Retrain automatically and deploy"

It sounds right, since fresher models track the world better. But if the shift is a broken data feed, the trigger trains on garbage. Pipeline bugs, delayed labels and feedback loops all do this, so every retrained model must pass data validation and beat production. More frequent isn't always better either: weigh the gain per retrain against its cost and risk.

## Say it

### How often should you retrain, and what stops a bad retrain?

#### The interviewer pushes further

Follow-up 1 of 3

How do you choose the retraining frequency?

Measure how fast performance decays (train on old data, test on successive weeks), compare the gain per retrain with its cost, and add triggers for sudden changes.

Follow-up 2 of 3

The retrained model is worse than production. What now?

Don't ship it; investigate data changes (pipeline bugs, label delays, distribution shift), check slices, and keep production running.

Follow-up 3 of 3

What is online / continual learning, and when would you use it?

Updating the model incrementally as data arrives; useful for fast-changing domains (ads, feeds), but harder to validate and roll back, so most teams use frequent batch retrains.

#### The 30-second answer

I'd automate retraining as a pipeline: a trigger, which can be a schedule, a performance or drift alert, or a known event; data validation; building a point-in-time training set over a sliding or weighted window; training with full tracking; evaluating against the current production model on the same recent test set and key slices; then registering and rolling out through shadow or canary with automatic rollback. A schedule handles gradual drift; triggers handle sudden shifts. The risks are retraining on bad or incomplete data and feedback loops, so gates and holdout data matter as much as the training itself.

**Go further**

#### What not to say

- "Retrain automatically and deploy." Gate it.

- "More frequent is always better." Weigh gains against cost and risk.

**Key terms and sources**

When and how to retrain production models: scheduled vs triggered retraining, what goes into an automated training pipeline (data checks, training, evaluation against the current model, approval, staged deployment), training windows and sample weighting, the cost–freshness trade-off, and failure modes such as training on bad data or feedback loops · built from Google Cloud (MLOps: Continuous delivery and automation pipelines in ML, maturity levels 0–2), Breck et al. (ML Test Score, 2017), Polyzotis et al. (Data Validation for ML, MLSys 2019), Huyen (Designing ML Systems, 2022, ch. 9), Gama et al. (ACM CSUR 2014) and Sculley et al. (NeurIPS 2015) · checked 29 Oct 2026

#### Sources

1. Google Cloud, "MLOps: Continuous delivery and automation pipelines in machine learning" (maturity levels 0–2).

2. E. Breck et al., "The ML Test Score", IEEE Big Data 2017; N. Polyzotis et al., "Data Validation for Machine Learning", MLSys 2019.

3. C. Huyen, _Designing Machine Learning Systems_, O'Reilly 2022 (ch. 9, continual learning).

4. J. Gama et al., "A Survey on Concept Drift Adaptation", ACM CSUR 2014; D. Sculley et al., NeurIPS 2015 (feedback loops).
