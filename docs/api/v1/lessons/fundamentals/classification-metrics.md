# Classification Metrics

> Your fraud model is 99.8% accurate. Why is your manager unhappy?

- Track: Fundamentals › Classical ML › Evaluation metrics
- Type: Concept · 30 min
- Page: https://aimlrounds.com/tracks/fundamentals/classification-metrics/
- Before this: Logistic Regression (`fundamentals/logistic-regression`)
- Quiz topic: `metrics`

## Intuition

### The situation

Your fraud model is 99.8% accurate, and your manager is unhappy. About 200 of every 100,000 transactions are fraud. The interviewer asks:

> Your fraud model is 99.8% accurate. Is it good?

**Scenarios used throughout:** card-fraud detection (0.2% of transactions are fraud), cancer screening (1% have the disease), spam filtering (40% of mail is spam), and a customer-support intent classifier with a rare but costly "cancel subscription" class. Scores come from a simple model of a classifier (illustrative); every number on the page is computed live from it.

#### "Our fraud model is 99.8% accurate." Your manager is unhappy. Why?

Out of every 100,000 card transactions, about 200 are fraud. A model that **never flags anything** is right on the 99,800 legitimate ones: 99.8% accuracy, and it catches zero fraud. One number told you nothing about the thing you care about. Classification metrics exist to ask the right question about the right mistakes.

### The idea

Think of a smoke alarm that never rings. It's right almost every day, and it's useless. Precision asks how many alarms were real fires. Recall asks how many fires set off the alarm.

[Figure: A confusion matrix. Precision reads across the flagged column, true positives out of everything flagged. Recall reads across the real positives row, true positives out of all real positives.]

_Every metric in this lesson is built from these four counts._

### Play

**Try to break it.** On Fraud, slide the threshold down until recall is high, and watch precision. Then switch to Spam and do the same.

#### Slide the threshold, watch the trade-off

–

Lower the threshold and you flag more: recall rises, precision falls. Raise it and the reverse. There's no free lunch, so the right threshold depends on what each kind of mistake costs. That's the subject of Thresholds & Misclassification Costs.

**Now say why:** why does the same threshold move give such different precision on rare fraud and common spam?

## Maths

### Maths

#### In one breath

Every classification metric is a ratio built from four counts: true positives, false positives, false negatives and true negatives. **Accuracy** hides rare classes. **Precision** asks "when I flag, am I right?" **Recall** asks "of what's out there, how much do I catch?" **Specificity** and **NPV** ask the same about negatives. **F1** balances precision and recall and ignores true negatives. Precision depends on how common the positive class is; recall doesn't. For many classes, **macro**, **micro** and **weighted** averaging answer different questions. What you'll be able to do after this: compute and explain every metric from a confusion matrix, pick the one a scenario needs, and spot the accuracy trap instantly.

#### Four counts: the confusion matrix

1. Every prediction lands in one of four boxes: what the model said (columns) versus what was true (rows).

2. **True positive (TP):** it was fraud and we flagged it.

3. **False negative (FN):** it was fraud and we missed it. Statisticians call this a type II error.

4. **False positive (FP):** it was legit and we flagged it, a false alarm. Type I error.

5. **True negative (TN):** legit and let through.

6. Rows add up to what's really there; columns add up to what the model flagged. Every metric on this page is some ratio of these four numbers.

#### Each metric divides by a different "out of what?"

$$ {\text{Precision} = \tfrac{TP}{TP+FP}} \quad {\text{Recall} = \tfrac{TP}{TP+FN}} \quad {\text{Specificity} = \tfrac{TN}{TN+FP}} \quad {\text{NPV} = \tfrac{TN}{TN+FN}} $$

Standard definitions, as in scikit-learn's metrics guide [docs](https://scikit-learn.org/stable/modules/model_evaluation.html). Recall, sensitivity, hit rate and true positive rate are four names for one thing.

- **precision (PPV)**: Out of everything I flagged, how much was really positive? TP / (TP + FP). Low precision = many false alarms. Spam filters live and die on this.

- **recall (sensitivity, TPR)**: Out of all real positives, how many did I catch? TP / (TP + FN). Low recall = missed cases. Cancer screening lives and dies on this.

- **specificity (TNR)**: Out of all real negatives, how many did I correctly leave alone? TN / (TN + FP). 1 − specificity is the false positive rate.

- **NPV**: Out of everything I called negative, how much was really negative? TN / (TN + FN). Matters when a negative result sends someone home.

#### A 95%-specific test, and most of its positives are false

Recall and specificity describe the test itself. Precision mixes the test with the **base rate**: when positives are rare, even a small false-positive rate on the huge negative group swamps the true positives. That's Bayes' rule:

$$ {\text{PPV}} = {\text{rec}\cdot\pi} \,\Big/\, \big({\text{rec}\cdot\pi} + {(1-\text{spec})\,(1-\pi)}\big), \quad {\pi = \text{prevalence}} $$

- **precision (PPV)**: Probability that a flagged case is really positive.

- **true positives per person**: Recall × prevalence: the share of the population that is positive and caught.

- **false positives per person**: (1 − specificity) × (1 − prevalence): small rate × huge group.

- **prevalence**: How common positives are. Drop it from 10% to 0.1% and precision collapses, even though the test is unchanged.

Screening scenario: a good test (90% sensitive, 95% specific) at 1% prevalence flags about 495 healthy people for every 90 sick ones, so precision is about 15%. That's why screening positives get a second, more specific test. Same test in a high-risk clinic (20% prevalence): precision about 82%.

#### F1: the harmonic mean, and what it ignores

$$ {F_1} = {2PR \,/\, (P+R)} = {2TP \,/\, (2TP + FP + FN)} $$

- **F1**: One number between 0 and 1 that is high only when precision and recall are both high.

- **harmonic mean**: 2PR / (P + R). Dominated by the smaller of the two: precision 1.0 and recall 0.1 give F1 = 0.18, not 0.55.

- **in counts**: 2TP / (2TP + FP + FN). True negatives never appear: F1 doesn't care how well you handle negatives.

The harmonic mean punishes imbalance; you can't buy a good F1 with one great number. If the two errors aren't equally costly, use F-beta (next lessons), not F1.

##### F1's blind spots

It ignores true negatives, and it changes if you swap which class you call "positive"; MCC doesn't have either problem [Chicco & Jurman 2020](https://pmc.ncbi.nlm.nih.gov/articles/PMC6941312). By default scikit-learn returns F1 = 0 when there are no positive predictions and no positives; the `zero_division` parameter controls this [docs](https://scikit-learn.org/stable/modules/model_evaluation.html).

#### Macro, micro and weighted

Support tickets go to **billing** (600), **technical** (350) or **cancel subscription** (50). Cancel is rare but the most expensive to miss: an unhandled cancel is a lost customer. Compare two models:

Micro-averaging pools all decisions, so with every class included it equals accuracy [docs](https://scikit-learn.org/stable/modules/model_evaluation.html); it's dominated by big classes. Macro-averaging gives every class equal weight, so the rare class counts as much as billing. Weighted averages by support. Model A looks fine on micro and weighted, and macro exposes it.

| Average | Question it answers | Use when |
|---|---|---|
| **micro** | How good is a random single decision? | Every prediction matters equally; multi-label tagging |
| **macro** | How good is the model on a typical class? | Rare classes matter as much as common ones (support intents, rare diseases) |
| **weighted** | Macro, but proportional to class size | Reporting overall quality on imbalanced data without letting tiny classes dominate |
| **per class (None)** | Everything, unsummarised | Always look at this before trusting any average |

scikit-learn notes that macro "may over-emphasize the typically low performance on an infrequent class", and that a weighted F can fall outside the range between precision and recall [docs](https://scikit-learn.org/stable/modules/model_evaluation.html).

## In practice

### In practice

#### A report, not a number

In practice you print a per-class report (scikit-learn's `classification_report`: precision, recall, F1 and support for every class) next to the confusion matrix, and pick one **headline metric** that matches the cost of mistakes in your scenario, plus a **guardrail** (e.g. "maximise recall subject to precision ≥ 80%"). The sections below build each piece.

#### Top-k accuracy, and multi-label metrics

##### Top-k accuracy

Correct if the true label is among the k highest-scored classes; accuracy is the k = 1 case [docs](https://scikit-learn.org/stable/modules/model_evaluation.html). Use it when a human or a later step picks from a short list: ImageNet top-5, product category suggestions, autocomplete.

##### Multi-label (several tags per item)

**Subset accuracy**: all tags exactly right (harsh). **Hamming loss**: fraction of individual tag decisions that are wrong (lenient). **Jaccard**: |predicted ∩ true| / |predicted ∪ true| per item. Plus per-tag precision and recall with micro or macro averaging.

##### Worked example: one article, true tags {politics, economy, india}

| Predicted tags | Subset accuracy | Jaccard | Hamming loss (5 possible tags) |
|---|---|---|---|
| {politics, economy, india} | 1 | 1.00 | 0.0 |
| {politics, economy} | 0 | 0.67 | 0.2 |
| {politics, sports} | 0 | 0.25 | 0.6 |

Missing one of three tags already scores 0 on subset accuracy; Jaccard and Hamming give partial credit.

#### Which metric, in which situation

| Scenario | Headline metric | Why |
|---|---|---|
| Cancer screening (first test) | Recall / sensitivity | A miss can be fatal; false alarms get a cheap follow-up test |
| Confirmatory diagnosis | Specificity, precision | A false positive means unnecessary treatment |
| Spam filter | Precision (at good recall) | Losing a real email is worse than letting one spam through |
| Fraud (0.2%) | Recall at a fixed precision (or alerts per day) | Review capacity is limited; accuracy is meaningless here |
| Content moderation | Precision for auto-removal, recall for the human-review queue | Two thresholds, two jobs |
| Support intents with a rare costly class | Macro-F1 + per-class recall | Micro and accuracy hide the rare class |
| Balanced classes, equal costs (e.g. cats vs dogs) | Accuracy is fine | Its weakness only appears with imbalance or unequal costs |
| Imbalanced, need one fair number | MCC or balanced accuracy | Use all four cells (see Thresholds & Costs) |

### The answer that sounds right

#### Accuracy: (TP + TN) / everything

With rare positives, the do-nothing baseline already scores near 100%, and a genuinely useful model can even score _lower_ because its false alarms cost accuracy points. With balanced classes (spam), accuracy is informative again.

##### What breaks

Accuracy "cannot be considered a reliable measure" on unbalanced data, because it gives "an overly optimistic estimate" [Chicco & Jurman 2020](https://pmc.ncbi.nlm.nih.gov/articles/PMC6941312). Always compare against the majority-class baseline, and use metrics that look at the positive class directly.

#### What to keep

- **All of these depend on the threshold.** For threshold-free comparison, use ROC-AUC or PR-AUC (next lesson).

- **Precision and NPV depend on prevalence**, so they don't transfer between populations (a clinic vs the general public, a test set rebalanced to 50/50 vs production). Recall and specificity do transfer, if the positives themselves look the same.

- **Small classes give noisy metrics.** Recall on 50 "cancel" tickets moves 2 points per ticket; report confidence intervals (Choosing the Right Metric).

- **Metrics are proxies for costs.** When you can put a price on each error, optimise expected cost directly.

## Say it

### Your fraud model is 99.8% accurate. Is it good?

#### The interviewer pushes further

Follow-up 1 of 5

Your fraud model has 99.8% accuracy. Is it good?

Can't tell: fraud is about 0.2%, so "never flag" also scores 99.8%. I'd look at recall and precision on the fraud class, the confusion matrix, PR-AUC, and alert volume against review capacity.

Follow-up 2 of 5

Precision or recall for cancer screening? For spam?

Screening: recall, since a miss is very costly and false positives get a cheap follow-up. Spam: precision, because sending a real email to spam is worse than letting one spam through. In both I'd set a floor on the other metric.

Follow-up 3 of 5

Why is precision low even though the test is accurate?

Base rate. With 1% prevalence, 5% false positives on the 99% healthy group outnumber the true positives on the 1%. PPV = rec·π / (rec·π + (1 − spec)(1 − π)).

Follow-up 4 of 5

Macro vs micro F1?

Micro pools all decisions (equals accuracy for single-label multi-class), so big classes dominate. Macro averages per-class F1 equally, so a failing rare class drags it down. Use macro when every class matters; always inspect per-class numbers.

Follow-up 5 of 5

Why the harmonic mean for F1?

It's dominated by the smaller value, so you can't get a high F1 with one strong and one weak component. Precision 1.0 and recall 0.1 give F1 ≈ 0.18.

#### The 30-second answer

I start from the confusion matrix. Accuracy is misleading on imbalanced data because the majority-class baseline already scores high. Precision measures how many flagged items are right, and recall how many real positives I catch; which one I prioritise depends on the scenario's costs: recall for screening, precision for spam. F1 balances them but ignores true negatives. Precision also depends on prevalence, so it shifts between populations. For multi-class problems I report per-class metrics and choose macro averaging when rare classes matter.

**Go further**

#### What not to say

- "High accuracy, so the model is good." Check the baseline and the class balance.

- "F1 is always the right metric for imbalance." It ignores TN and unequal costs.

- "Precision is a property of the model." It's also a property of the population (prevalence).

**Key terms and sources**

Built from scikit-learn's model-evaluation guide and Chicco & Jurman (2020) · checked 28 Oct 2026

#### Glossary

| Term | Formula / meaning |
|---|---|
| **Accuracy** | (TP + TN) / N |
| **Precision, PPV** | TP / (TP + FP) |
| **Recall, sensitivity, TPR** | TP / (TP + FN) |
| **Specificity, TNR** | TN / (TN + FP) |
| **FPR / FNR** | FP / (FP + TN) = 1 − specificity; FN / (FN + TP) = 1 − recall |
| **NPV** | TN / (TN + FN) |
| **F1** | 2PR / (P + R) |
| **Support** | Number of true instances of a class |
| **Prevalence** | Share of positives in the population |
| **Macro / micro / weighted** | Average of per-class scores / pooled counts / support-weighted average |

#### What this page is built from

1. scikit-learn, [Metrics and scoring: quantifying the quality of predictions](https://scikit-learn.org/stable/modules/model_evaluation.html) (precision/recall/F, averaging, top-k, Hamming, Jaccard).

2. D. Chicco & G. Jurman, [The advantages of the Matthews correlation coefficient over F1 score and accuracy in binary classification evaluation](https://pmc.ncbi.nlm.nih.gov/articles/PMC6941312), BMC Genomics 21:6 (2020).

3. T. Fawcett, "An introduction to ROC analysis", _Pattern Recognition Letters_ 27 (2006): definitions of TPR, FPR and related terms.

4. Interview angle: [DataLemur ML interview questions](https://datalemur.com/blog/machine-learning-interview-questions).

Scenario scores come from a simple, illustrative model of a classifier (positives' and negatives' scores as two overlapping bell curves), with expected counts computed exactly.
