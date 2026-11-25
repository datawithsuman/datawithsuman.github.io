# Training/Serving Skew and Feature Stores

> Why does a model look great offline and fail online?

- Track: AI Engineering › MLOps › Lessons
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/ai-engineering/training-serving-skew-and-feature-stores/
- Before this: Cross-Validation & Data Leakage (`fundamentals/cross-validation-and-leakage`)
- Quiz topic: `mlops`
- Sources checked: 2026-10-29 · Text last changed: 2026-11-20 · Version: 31c8c4084b

## Intuition

### The situation

The new ETA model beat the old one by a wide margin on the held-out set, then performed worse after launch. Nothing was wrong with the algorithm. The interviewer asks:

> Why does a model look great offline and fail online?

**Running example (this track):** the food-delivery app's **ETA model** predicts minutes from order to door, using features like the restaurant's recent average delay, distance and time of day.

#### Great offline, bad online

The new ETA model beat the old one by a wide margin on the held-out set, then performed worse after launch. Nothing was wrong with the algorithm: the features the model saw in production simply weren't the features it was trained on. Sculley et al. called ML systems prone to such hidden debt because data dependencies are harder to see than code dependencies.

### The idea

Think of practising for an exam with the answers pencilled into the question paper. Your practice scores look brilliant, and the real paper has no pencil marks. A feature that peeks at later orders is that pencil: it's in training, and it can't exist at prediction time.

[Figure: ETA error in minutes. The leaky feature gives 3.9 offline and 6.0 in production. The point-in-time feature gives 5.8 in both.]

_From the lab's simulation: the restaurant's average delivery time as a feature._

### Play

**Try to break it.** Switch between the feature over all orders and the point-in-time feature. Compare offline error with production error.

#### Compute features over the whole table

Simulation: 6,000 orders at 2,000 restaurants (about 3 orders each, like many new or small restaurants), each with its own typical delay; delivery time = 30 + restaurant effect + noise. Feature: the restaurant's average delivery time. Linear model trained on the first 70% of orders in time, tested on the last 30%. "Production" = the trained model fed the feature as it would exist at prediction time. Fixed seed.

Computing the restaurant's average over **all orders** (including later ones and the order itself) gives an impressive **3.9-minute** offline error. In production that feature can only use past orders, so the same model's error is **6.0 minutes**: a 2.2-minute surprise. The honest **point-in-time** feature looks worse offline (**5.8**) but is the same online, and slightly _better_ than the leaky model in production, because the leaky model learned to trust a feature that never exists at serving time. Point-in-time correctness means every training row uses only data that was available at its prediction timestamp.

**Now say why:** the point-in-time feature looks worse offline, so why is it the better choice?

## How it works

### How it works

#### In one breath

**Training/serving skew** is any difference between the data a model was trained on and the data it sees when serving. Three common causes: **different code** (features computed one way in the training pipeline and another way in the live service), **different data** (a source available offline but stale or missing online), and **time travel**: training features computed with information that didn't exist yet at prediction time. The last one is the sneakiest: if a restaurant's "average delay" feature includes the very order you're predicting, offline error looks great and production error is worse than an honest model's. A **feature store** is the standard fix as a concept: define each feature once, compute it for training with **point-in-time (as-of) joins**, serve the same values online, and log the features actually served so future training uses exactly what the model saw. What you'll be able to do after this: diagnose "great offline, bad online", explain point-in-time correctness, and describe what a feature store does.

#### Where skew comes from

| Cause | Example |
|---|---|
| **Different code** | training computes "distance" with road routing, the live service with straight-line distance; or minutes vs seconds |
| **Different data** | a traffic feed joined offline from cleaned archives, but delayed or missing online |
| **Time travel (leakage)** | "restaurant's average delay" computed over all orders, including later ones and the order itself |
| **Feedback loops** | the model's own ETAs change customer and courier behaviour, shifting future data |

Zinkevich's Rules of ML: the best way to make training like serving is to save the features used at serving time and pipe them to training, and to reuse the same feature code in both paths.

## In practice

### In practice

#### The feature store, as a concept

- **One definition per feature** (transformation code, inputs, freshness), used by both training and serving, which removes the "different code" class of skew.

- **Offline store:** full history of feature values with timestamps; training sets are built with **as-of joins** (for each label, take each feature's latest value before the prediction time).

- **Online store:** latest values with low-latency lookup for live predictions; fed by batch or streaming jobs.

- **Log what you serve:** record the exact feature vector used for each prediction; train future models on these logs to eliminate skew entirely.

- **Validate:** compare feature distributions between training data and serving logs (schema, ranges, missing rates, drift); alert on mismatches (drift monitoring).

#### Train on exactly what you will serve

Use one feature definition for both paths, build training data only from information available at prediction time, and log served features so training and serving can't silently diverge.

### The answer that sounds right

#### "It worked offline, so the model is good"

It sounds right, since a held-out set is meant to predict production. But if a feature leaks the future, the held-out set is flattered too: 3.9 minutes offline became 6.0 live in the lab. Check the serving features, and split by time rather than at random. You don't always need a feature store either: for a few batch features, shared code and logged features may be enough.

## Say it

### Why does a model look great offline and fail online?

#### The interviewer pushes further

Follow-up 1 of 3

Offline metrics improved, online didn't. How do you investigate?

Compare the served feature values (logs) with the training values for the same entities and times; check for leakage, missing or stale online features, unit or encoding differences; and check whether the offline metric matches the online objective.

Follow-up 2 of 3

What is an as-of join?

For each training example with timestamp t, join each feature's most recent value with timestamp ≤ t (respecting how late that value actually became available).

Follow-up 3 of 3

Do you always need a feature store?

No; for a few batch features, shared transformation code and logged features may be enough. It pays off with many features, many models and real-time serving.

#### The 30-second answer

Training/serving skew is any mismatch between training and serving data: different feature code, different data sources or freshness, or leakage where training features use information from after the prediction time. Leakage makes offline metrics look great and production worse. The fixes are point-in-time correct training data built with as-of joins, a single feature definition shared by training and serving, which is what a feature store provides with an offline history and an online low-latency store, logging the features actually served and training on those logs, and validating training versus serving distributions.

**Go further**

#### What not to say

- "Random train/test split is fine for time-based features." Split by time and compute features as of each row.

- "It worked offline, so the model is good." Check serving features.

**Key terms and sources**

Why a model that looks great offline disappoints in production: training/serving skew (different feature code, different data, different timing), point-in-time correctness and label leakage, and the feature store as a concept: one feature definition computed the same way for training (offline) and serving (online), with as-of joins · built from Sculley et al. (Hidden Technical Debt in ML Systems, NeurIPS 2015), Zinkevich (Rules of Machine Learning, Google), Breck et al. (The ML Test Score, IEEE Big Data 2017), Kaufman et al. (Leakage in Data Mining, TKDD 2012), Polyzotis et al. (Data Validation for ML, MLSys 2019) and Shankar et al. (Operationalizing Machine Learning: An Interview Study, 2022) · checked 29 Oct 2026

#### Sources

1. D. Sculley et al., "Hidden Technical Debt in Machine Learning Systems", NeurIPS 2015.

2. M. Zinkevich, "Rules of Machine Learning: Best Practices for ML Engineering", Google (rules on training-serving skew).

3. E. Breck et al., "The ML Test Score: A Rubric for ML Production Readiness and Technical Debt Reduction", IEEE Big Data 2017.

4. S. Kaufman et al., "Leakage in Data Mining: Formulation, Detection, and Avoidance", ACM TKDD 2012; N. Polyzotis et al., "Data Validation for Machine Learning", MLSys 2019.

5. S. Shankar et al., "Operationalizing Machine Learning: An Interview Study", 2022, [arXiv:2209.09125](https://arxiv.org/abs/2209.09125).
