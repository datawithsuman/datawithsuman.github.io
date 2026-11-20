# Choosing the Right Metric

> Which metric would you use for X? Twelve scenarios to practise.

- Track: Fundamentals › Classical ML › Evaluation metrics
- Type: Concept · 25 min
- Page: https://aimlrounds.com/tracks/fundamentals/choosing-the-right-metric/
- Before this: Classification Metrics (`fundamentals/classification-metrics`), Regression Metrics (`fundamentals/regression-metrics`), Ranking Metrics (`fundamentals/ranking-metrics`), Probability Metrics (`fundamentals/probability-metrics`)
- Quiz topic: `metrics`

## Intuition

### The situation

A team raises their recommender's offline NDCG by 4% and ships it. Engagement goes up, but returns and refund complaints go up more. The interviewer asks:

> Which metric would you use?

#### The model improved. The business got worse.

Here's an illustrative story. A team raises their recommender's offline NDCG by 4% and ships it. Engagement goes up; returns and refund complaints go up more, because the model learned to push cheap, clicky items. Nothing was wrong with NDCG. It just wasn't the whole goal. The metric question in interviews ("how would you evaluate this?") is really asking: do you know what success means here, and how would you know you'd achieved it?

### The idea

Think of a shop that rewards staff only for sales. Sales rise, and so do returns. Any metric becomes a target that gets chased, so start from how the output is used, and keep guardrails on what mustn't get worse.

[Figure: Three layers. A model metric to iterate quickly, a business metric that must move, and guardrails that must not get worse.]

_From the lesson's three layers._

### Play

**Try to break it.** Set a new model just slightly above the old one and shrink the test set. Then grow the test set until the difference looks real.

#### Metric differences need error bars

A test set is a sample. An accuracy measured on n examples has a standard error of about √(p(1 − p)/n), so a 95% interval is roughly ±1.96 of those. Before celebrating a new model, check the gap is bigger than the noise:

Normal approximation, treating the two accuracies as independent (conservative). Both models are usually scored on the same test set, so a paired test (McNemar's test on the examples where they disagree, or a paired bootstrap) is tighter and is the standard recommendation (Dietterich, 1998). The point stands: at n = 1,000, a 1-point accuracy gain is inside the noise.

- **Bootstrap** any metric (AUC, NDCG, F1): resample the test set with replacement 1,000 times, recompute, read off the 2.5th and 97.5th percentiles.

- **Rare classes make it worse**: recall on 50 positives moves 2 points per example.

- **Don't tune on the test set**: every look at it is a chance to overfit; keep a validation set for choices and touch the test set once.

**Now say why:** when can you trust that one model really is better?

## How it works

### How it works

#### In one breath

Pick the metric from **what the model's output is used for**: a decision with asymmetric costs, a ranked list, a number, or a probability that feeds another calculation. Pair one **headline model metric** with the **business metric** it's meant to move and a few **guardrails** that must not get worse. Always compare against a baseline, and check whether a difference is bigger than the noise: on 1,000 test examples, 91% vs 90% accuracy is not a real win. What you'll be able to do after this: answer "which metric would you use for X?" for any scenario in under a minute, with a reason, and challenge a claimed improvement that's within noise.

#### Model metric, business metric, guardrails

| Layer | Example (fraud) | Example (search) | Role |
|---|---|---|---|
| **Model metric** (offline) | PR-AUC; recall at 500 alerts/day | NDCG@10 | Fast to compute; used to iterate and choose models |
| **Business metric** (online) | ₹ fraud losses prevented | Conversion, revenue per search | What you actually care about; slow and noisy |
| **Guardrails** | Good customers blocked per 10,000; review queue length | Latency, zero-result rate, return rate | Must not get worse while the main metric improves |

Online experimentation practice formalises this as an overall evaluation criterion plus guardrail metrics (Kohavi, Tang & Xu, _Trustworthy Online Controlled Experiments_, 2020).

#### Start from how the output is used

1. Don't start from the model type. Start from what someone or something does with the output.

2. **A yes/no decision:** the costs of the two errors decide the metric (Classification Metrics, Thresholds & Costs).

3. **A ranked list:** what matters is the top of the list and how many items get used (Ranking Metrics, ROC vs PR).

4. **A number:** which summary of the outcome you want predicted: mean, median, quantile, ratio (Regression Metrics).

5. **A probability used in a calculation:** it must be calibrated, not just well ranked (Probability Metrics).

## In practice

### In practice

#### A metric plan for any project

1. **Write down the decision** the model supports, and who acts on it.

2. **Price the errors** (or rank them): which mistake is worse, roughly by how much?

3. **Choose one headline offline metric** that matches the output type and the error costs.

4. **Name the business metric** it should move, and 2–3 **guardrails** (latency, fairness across segments, complaints, coverage).

5. **Set baselines**: majority class, current system, a simple heuristic.

6. **Report with uncertainty** (CIs or bootstrap) and **by segment** (new vs returning users, regions, rare classes).

7. **Validate online** with an A/B test before declaring victory; re-check when data or costs drift.

#### All six lessons on one table

| Situation | Metric | Lesson |
|---|---|---|
| Balanced classes, equal costs | Accuracy | Classification |
| Misses are costly | Recall (at a precision floor), F2 | Classification, Thresholds |
| False alarms are costly | Precision, F0.5 | Classification, Thresholds |
| Costs known | Expected cost; threshold p* = CFP/(CFP+CFN) | Thresholds |
| One fair number, imbalanced | MCC, balanced accuracy | Thresholds |
| Many classes, rare ones matter | Macro-F1 + per-class recall | Classification |
| Ranking quality, any balance | ROC-AUC (Gini, KS) | ROC vs PR |
| Ranking with rare positives | PR-AUC, precision@k | ROC vs PR |
| Search with graded relevance | NDCG@k | Ranking |
| RAG retrieval | Recall@k, MRR | Ranking |
| Numeric, typical error | MAE (median) | Regression |
| Numeric, big misses costly | RMSE (mean) | Regression |
| Service level / stocking | Pinball loss at α | Regression |
| Forecasts with zeros / many series | WAPE, MASE | Regression |
| Probabilities used in calculations | Log-loss, Brier, ECE + reliability diagram | Probability |

### The answer that sounds right

#### "Optimise the metric everyone reports"

Goodhart's law, in Marilyn Strathern's phrasing: "When a measure becomes a target, it ceases to be a good measure." Optimise accuracy on imbalanced data and you get "never flag". Optimise MAPE and forecasts drift low. Optimise click-through and you get clickbait. Every metric in this section has a way to be gamed, so choose it knowing how, and watch the guardrails.

## Say it

### Which metric would you use?

#### The interviewer pushes further

Follow-up 1 of 3

Model B is 0.4% more accurate than A. Ship it?

Depends on the test-set size and variance: compute a confidence interval or a paired test. Also check per-segment results, latency and cost, and whether accuracy is even the right metric for the task.

Follow-up 2 of 3

Offline metrics improved but online metrics didn't. Why?

The offline metric is a poor proxy for the business goal, training–serving skew, stale or biased labels, feedback effects (the new model changes the data), novelty effects, or a test that's too small. Investigate by segment.

Follow-up 3 of 3

What's a guardrail metric?

A metric that must not get worse while you optimise the main one: latency, error rates, fairness gaps, complaint rate, unsubscribe rate. It protects against Goodhart-style gaming of the headline metric.

#### A 4-step answer template

First, how is the output used: a decision, a ranking, a number, or a probability. Second, which mistake is worse and roughly by how much. That gives me the headline metric, for example recall at a precision floor for fraud, with PR-AUC to compare models. Third, the business metric it should move and the guardrails, like blocked good customers and review queue length. Fourth, baselines and uncertainty: compare with the current system using bootstrap intervals, then confirm with an A/B test.

**Go further**

#### What not to say

- "I'd use accuracy" (without checking balance and costs).

- "The new model is better because its metric is higher" (without error bars or a baseline).

- "Offline metrics are enough" (for anything user-facing).

**Key terms and sources**

A decision guide, 12 interview scenarios, and "is the difference real?" · built from the six metric lessons, Kohavi et al. (2020) and Dietterich (1998) · checked 28 Oct 2026

#### What this page is built from

1. The six lessons of this section and their sources (scikit-learn, Fawcett, Davis & Goadrich, Saito & Rehmsmeier, Elkan, Chicco & Jurman, Hyndman & Koehler, Järvelin & Kekäläinen, Guo et al., Brier, Murphy).

2. R. Kohavi, D. Tang & Y. Xu, _Trustworthy Online Controlled Experiments: A Practical Guide to A/B Testing_, Cambridge University Press, 2020 (overall evaluation criterion, guardrail metrics).

3. T. G. Dietterich, "Approximate statistical tests for comparing supervised classification learning algorithms", _Neural Computation_ 10 (1998) (McNemar's test, paired comparisons).

4. M. Strathern, "Improving ratings: audit in the British University system", _European Review_ 5 (1997) (the common phrasing of Goodhart's law).
