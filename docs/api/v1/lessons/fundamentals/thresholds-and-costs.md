# Thresholds & Misclassification Costs

> Why flag at 0.5, when a missed fraud costs 100 reviews?

- Track: Fundamentals › Classical ML › Evaluation metrics
- Type: Concept · 30 min
- Page: https://aimlrounds.com/tracks/fundamentals/thresholds-and-costs/
- Before this: Classification Metrics (`fundamentals/classification-metrics`)
- Quiz topic: `metrics`

## Intuition

### The situation

Your code flags fraud at 0.5, which treats a missed ₹20,000 fraud and a ₹200 manual review as equally bad. The interviewer asks:

> How do you choose a classification threshold?

**Scenarios with real-world-style costs** (illustrative): fraud (missed fraud ₹20,000; reviewing a false alarm ₹200), cancer screening (a miss is 100× worse than a follow-up test), loan approval (approving a defaulter ₹2,00,000; rejecting a good customer ₹30,000 of lost interest), spam (losing a real email 10× worse than one spam in the inbox). Scores come from the same calibrated model as the earlier lessons.

#### Why flag at 0.5?

Most code says `predict = proba >= 0.5`. That treats a missed ₹20,000 fraud and a ₹200 manual review as equally bad. Change the threshold and the business outcome changes by lakhs. In our fraud scenario, the cost per 100,000 transactions is about **₹28.7 lakh at 0.5** and **₹10.9 lakh at the cost-optimal threshold**: same model, same data, different line.

### The idea

Think of deciding when to call a doctor. A wasted visit costs a little, and a missed illness costs a lot, so you call even when you're only somewhat worried. A threshold works the same way: you act once acting is the cheaper bet.

[Figure: A U-shaped curve of total cost against the threshold. The lowest cost sits well to the left of the usual 0.5 default.]

_Illustrative. When misses cost far more than false alarms, the best threshold sits well below 0.5._

### Play

**Try to break it.** On Fraud, drag the threshold until you find the lowest cost. Then switch to Spam and find it again.

#### Cost, Youden, F1 and F2 on the same model

–

Two patterns to notice. First, the cost curve's minimum lands exactly on CFP/(CFP + CFN), because these probabilities are calibrated. Second, **Youden's J always picks the threshold where the probability equals the prevalence** in this model. It agrees with the cost optimum only when the cost ratio happens to mirror the class ratio: almost exactly in cancer screening (100:1 costs, 99:1 classes), badly in spam and fraud.

**Now say why:** why does the best threshold move so far between the two, even though neither model changed how it works?

## Maths

### Maths

#### In one breath

A model gives scores; a **threshold** turns them into decisions, and the right threshold depends on what each mistake **costs**. If the probabilities are calibrated and you can price the errors, the cost-optimal rule is simple: flag when p ≥ CFP / (CFP + CFN). **Youden's J** (sensitivity + specificity − 1) picks a threshold as if a miss and a false alarm were equally bad _per class_; **F-beta** lets you say recall is β times as important as precision. When you need one fair number on imbalanced data, **MCC** and **balanced accuracy** use all four cells of the confusion matrix. And reweighting classes during training is just threshold moving in disguise. What you'll be able to do after this: turn business costs into a threshold, explain why "0.5" is arbitrary, and choose between Youden, F-beta, MCC, kappa, G-mean and expected cost for a scenario.

#### A cost matrix: put a price on each cell

| | predict positive | predict negative |
|---|---|---|
| actually positive | CTP (often 0) | CFN: the miss |
| actually negative | CFP: the false alarm | CTN (often 0) |

Elkan's observation: from a decision-making point of view, a 2×2 cost matrix has essentially **one** degree of freedom, the ratio of the two error costs [Elkan, IJCAI 2001](https://mlanthology.org/ijcai/2001/elkan2001ijcai-foundations). You don't need exact rupee values; you need a defensible ratio ("a missed fraud costs about 100 reviews").

#### Flag when the expected cost of flagging is lower

For one case with calibrated probability p of being positive: flagging costs (1 − p)·CFP in expectation (it might be a false alarm); not flagging costs p·CFN (it might be a miss). Flag when the first is smaller:

$$ \text{flag if }\ {(1-p)\,C_{FP}} \le {p\,C_{FN}} \iff {p \ge C_{FP} \,/\, (C_{FP} + C_{FN})} $$

Bayes-optimal decision with zero cost for correct decisions; the threshold result is Elkan's (2001) [IJCAI 2001](https://mlanthology.org/ijcai/2001/elkan2001ijcai-foundations). It only holds if p is a calibrated probability (see Probability Metrics).

- **expected cost of flagging**: If you flag, you pay C_FP only when it is actually negative, with probability 1 − p.

- **expected cost of not flagging**: If you let it through, you pay C_FN only when it is actually positive, with probability p.

- **the threshold**: Solve for p: flag whenever p ≥ C_FP / (C_FP + C_FN). Fraud: 200 / 20,200 ≈ 0.0099, so flag anything above 1%. Spam: 10 / 11 ≈ 0.91.

#### Sensitivity + specificity − 1

$$ {J} = {\text{sensitivity}} + {\text{specificity}} - 1 = {\text{TPR} - \text{FPR}} $$

Youden (1950). scikit-learn: balanced accuracy with `adjusted=True` "in the binary case… is also known as Youden's J statistic, or informedness" [docs](https://scikit-learn.org/stable/modules/model_evaluation.html).

- **Youden's J (informedness)**: From 0 (no better than chance) to 1 (perfect). Also called informedness or bookmaker informedness.

- **sensitivity**: Recall on positives.

- **specificity**: Recall on negatives. J gives both classes equal weight regardless of how many cases are in each.

- **on the ROC curve**: TPR − FPR: the vertical distance from the ROC curve to the diagonal. Its maximum is the KS statistic, and the threshold there is the classic “optimal cut-off”.

##### When Youden is right, and when it isn't

Maximising J is equivalent to minimising cost when CFN × prevalence = CFP × (1 − prevalence), i.e. when the total cost at stake in each class is equal. It's a sensible default for diagnostic tests with no cost information, and wrong whenever one error is far more expensive than the class ratio suggests.

#### "Recall is β times as important as precision"

$$ {F_\beta} = (1+{\beta^{2}})\,PR \,/\, (\beta^{2}P + R) = {(1+\beta^2)TP \,/\, \big((1+\beta^2)TP + FP + \beta^2 FN\big)} $$

scikit-learn's formula [docs](https://scikit-learn.org/stable/modules/model_evaluation.html).

- **F-beta**: A weighted harmonic mean of precision and recall.

- **β²**: β = 2 weights recall more (screening, finding all relevant documents); β = 0.5 weights precision more (spam, auto-actions). β = 1 is F1.

- **in counts**: β² multiplies the false negatives: larger β makes misses more expensive. True negatives still never appear.

#### MCC, balanced accuracy, G-mean and Cohen's kappa

$$ {\text{MCC}} = {(TP\cdot TN - FP\cdot FN)} \,/\, {\sqrt{(TP{+}FP)(TP{+}FN)(TN{+}FP)(TN{+}FN)}} $$

Matthews (1975). Chicco & Jurman: MCC "produces a high score only if the prediction obtained good results in all of the four confusion matrix categories", and should be preferred to accuracy and F1 for binary evaluation [BMC Genomics 2020](https://pmc.ncbi.nlm.nih.gov/articles/PMC6941312).

- **Matthews correlation**: The correlation between predictions and truth, from −1 (inverse) through 0 (random) to +1 (perfect). Uses all four cells.

- **agreement minus disagreement**: TP·TN − FP·FN: positive only if the right-diagonal outweighs the wrong one.

- **normaliser**: The geometric mean of all four row and column totals, so MCC is high only if the model does well on both classes.

Three fraud models on 100,000 transactions (0.2% fraud):

Green = best in each row. "Never flag" scores 99.8% accuracy, beating model A, yet every metric designed for imbalance exposes it: balanced accuracy 0.5, MCC 0, kappa 0, G-mean 0. Between the two real models, the metrics disagree, because each encodes a different view of which mistake matters more.

| Metric | Definition | Reach for it when |
|---|---|---|
| **Balanced accuracy** | (sensitivity + specificity) / 2; macro-averaged recall | You want "accuracy" that isn't fooled by imbalance; equals Youden's J rescaled |
| **MCC** | Correlation between prediction and truth | One honest summary of a binary confusion matrix; symmetric in the classes |
| **G-mean** | √(sensitivity × specificity) | Imbalanced-learning papers; punishes neglecting either class |
| **Cohen's kappa** | (accuracy − chance agreement) / (1 − chance agreement) | Originally for agreement between human annotators; scikit-learn notes it's designed for "comparing labelings by different human annotators, not a classifier versus a ground truth" [docs](https://scikit-learn.org/stable/modules/model_evaluation.html) |

## In practice

### In practice

#### Four ways teams choose a threshold

| Approach | What it assumes | Typical use |
|---|---|---|
| **Minimise expected cost** | You can price (or ratio) the errors; probabilities are calibrated | Fraud, credit, insurance, anything with money attached |
| **Fix one rate, optimise the other** | A hard constraint: "recall ≥ 95%", "≤ 500 alerts a day", "precision ≥ 90%" | Screening programmes, alert queues with fixed capacity |
| **Maximise Youden's J** | Sensitivity and specificity matter equally | Diagnostic test cut-offs in medicine |
| **Maximise F1 / F-beta** | Only the positive class matters; β sets recall vs precision | Information retrieval, detection tasks with no clear costs |

#### Reweighting during training is (mostly) a threshold shift

Two common ways to "handle imbalance": give positives weight w in the training loss, or train normally and lower the threshold afterwards. For a well-specified probabilistic model (like logistic regression), weighting positives by w multiplies the predicted odds by w. So a threshold of 0.5 on the weighted model is the same decision as a threshold of 1/(1 + w) on the unweighted one.

##### Prefer threshold moving when

- You need calibrated probabilities (weights distort them)

- Costs change over time: re-pick the threshold, no retraining

- You want one model serving several cost policies

##### Class weights / resampling help when

- The model has limited capacity and should spend it on the rare class (trees, small nets)

- The training loss would otherwise ignore positives entirely

- Then recalibrate before using the probabilities

#### Choosing a threshold in practice

1. Get calibrated probabilities on a validation set (check a reliability curve).

2. Agree the cost ratio CFN : CFP with the business, or the hard constraint (capacity, minimum recall).

3. Start from p* = CFP/(CFP + CFN); verify by computing expected cost across thresholds on validation data.

4. If there are constraints, pick the best threshold that satisfies them.

5. Report the confusion matrix and the money at that threshold, plus a threshold-free metric for model comparison.

6. Re-check when prevalence or costs change (fraud patterns, new pricing); the threshold is a business setting, not a model property.

#### Which criterion, in which situation

| Scenario | Choose the threshold by | Why |
|---|---|---|
| Card fraud | Expected cost (₹), capped by analyst capacity | Clear money on both errors; alerts are a budget |
| Loan approval | Expected profit / cost per decision | Asymmetric and quantifiable; regulators also want a fixed, documented cut-off |
| Cancer screening | Minimum sensitivity (e.g. ≥ 95%), then best specificity; Youden as a no-cost default | Lives can't be priced comfortably; a constraint is easier to agree |
| Spam | High threshold (F0.5 or cost ratio 10:1) | False positives (lost email) are the expensive error |
| Search / retrieval without costs | F1 or F2 | Only the positive class is of interest |
| Reporting one honest score on imbalanced data | MCC (or balanced accuracy) | Uses all four cells; not fooled by the majority class |

### The answer that sounds right

#### "Pick the threshold that maximises F1"

Maximising F1 is popular because it needs no cost numbers. But F1 has a hidden opinion: misses and false alarms are equally costly _relative to the positives_, and true negatives don't matter. In our scenarios, the F1-optimal threshold costs **2.1×** the optimum for fraud and **2.6×** for cancer screening. Any metric you maximise encodes a cost assumption; better to choose the assumption on purpose.

#### What to keep

- **p* = CFP/(CFP + CFN) needs calibrated probabilities.** With an overconfident model, tune the threshold empirically on validation data instead.

- **Costs are often per-case** (a ₹2 lakh fraud vs a ₹500 one). Then use example-dependent costs: flag if p·amount ≥ review cost.

- **Every "optimal threshold" metric hides a cost assumption**: Youden (equal per-class weight), F1 (TN don't matter, P and R equal), accuracy (all errors equal).

- **MCC and kappa are hard to explain** to non-technical stakeholders; translate the chosen operating point into counts and money.

## Say it

### How do you choose a classification threshold?

#### The interviewer pushes further

Follow-up 1 of 4

Missing fraud costs 100× a false alarm. What threshold?

p* = 1/(1 + 100) ≈ 0.0099: flag anything with at least about 1% fraud probability, assuming calibrated probabilities. Then check alert volume against review capacity.

Follow-up 2 of 4

What is Youden's J and when would you use it?

Sensitivity + specificity − 1, i.e. TPR − FPR; its maximum on the ROC curve is a common "optimal" cut-off in diagnostics. It weights the two classes equally regardless of size, so it's right only when the total cost at stake in each class is equal. Use it when there's no cost information.

Follow-up 3 of 4

MCC vs F1?

F1 ignores true negatives and changes if you swap which class is positive; MCC uses all four cells, is symmetric, and is 0 for random or constant predictions. On imbalanced data MCC is the more honest single number.

Follow-up 4 of 4

Class weights or threshold tuning for imbalance?

For calibrated probabilistic models they're nearly equivalent: weighting positives by w ≈ moving the threshold to 1/(1 + w). Threshold tuning keeps probabilities calibrated and lets you change policy without retraining. Weights help low-capacity models focus on the rare class; recalibrate afterwards.

#### The 30-second answer

The threshold is a business decision, not a model property. If the model's probabilities are calibrated and I can estimate the costs of a false positive and a false negative, I flag when p is at least C_FP over C_FP plus C_FN, which minimises expected cost. Without costs, I'd use a constraint like minimum recall, Youden's J if sensitivity and specificity matter equally, or F-beta to weight recall versus precision. For a single summary on imbalanced data I prefer MCC or balanced accuracy over accuracy and F1. Class weighting during training is essentially threshold moving, so I usually train normally, calibrate, then pick the threshold.

**Go further**

#### What not to say

- "The default threshold is 0.5 so that's what we use." It's only optimal when the costs are equal and the probabilities are calibrated.

- "Maximise F1 to choose the threshold." Only if F1's hidden cost assumption fits.

- "Kappa is the standard metric for classifiers." It was designed for annotator agreement; MCC is usually clearer.

**Key terms and sources**

Youden's J, cost matrices, F-beta, MCC, balanced accuracy, G-mean and Cohen's kappa · built from Elkan (2001), Chicco & Jurman (2020), Fawcett (2006) and scikit-learn's docs · checked 28 Oct 2026

#### Glossary

| Term | Meaning |
|---|---|
| **Cost matrix** | Price of each (prediction, truth) outcome. |
| **Cost-optimal threshold** | p* = CFP / (CFP + CFN) for calibrated p. |
| **Youden's J / informedness** | Sensitivity + specificity − 1 = TPR − FPR. |
| **F-beta** | Weighted harmonic mean; β > 1 favours recall. |
| **MCC** | Correlation between predicted and true labels (−1 to 1). |
| **Balanced accuracy** | Mean of per-class recall. |
| **G-mean** | √(sensitivity × specificity). |
| **Cohen's kappa** | Agreement corrected for chance. |
| **Threshold moving** | Changing the decision threshold after training instead of reweighting. |

#### What this page is built from

1. C. Elkan, [The Foundations of Cost-Sensitive Learning](https://mlanthology.org/ijcai/2001/elkan2001ijcai-foundations), IJCAI 2001 (cost matrix, one degree of freedom, optimal threshold); summary in [Cost-sensitive machine learning](https://en.wikipedia.org/wiki/Cost-sensitive_machine_learning).

2. W. J. Youden, "Index for rating diagnostic tests", _Cancer_ 3 (1950); J as informedness in the [ROC article](https://en.wikipedia.org/wiki/Receiver_operating_characteristic).

3. D. Chicco & G. Jurman, [MCC vs F1 and accuracy](https://pmc.ncbi.nlm.nih.gov/articles/PMC6941312), BMC Genomics 2020.

4. scikit-learn, [Metrics and scoring](https://scikit-learn.org/stable/modules/model_evaluation.html): balanced accuracy (adjusted = Youden's J), MCC, Cohen's kappa, F-beta.

5. Interview angle: [DataLemur](https://datalemur.com/blog/machine-learning-interview-questions).

Costs are illustrative round numbers; expected counts and costs are computed exactly from a calibrated two-bell-curve score model.
