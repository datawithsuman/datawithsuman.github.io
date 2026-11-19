# ROC-AUC vs PR-AUC

> Why can a 0.98 ROC-AUC fraud model still be nearly useless?

- Track: Fundamentals › Classical ML › Evaluation metrics
- Type: Concept · 25 min
- Page: https://aimlrounds.com/tracks/fundamentals/roc-auc-vs-pr-auc/
- Before this: Classification Metrics (`fundamentals/classification-metrics`)
- Quiz topic: `metrics`

## Intuition

### The situation

Model A gets 70% recall at 40% precision, and model B gets 60% at 55%. Your threshold could change next quarter, so you need a comparison that doesn't depend on it. The interviewer asks:

> When would you use PR-AUC instead of ROC-AUC?

**Scenarios:** fraud detection (0.2% fraud), credit default ranking (about 5% default), rare-disease screening, and ad click prediction. Scores come from the same simple model as Classification Metrics: positives' and negatives' scores as two overlapping bell curves, separated by d standard deviations (illustrative, computed exactly).

#### Precision and recall change with the threshold. How do you compare models?

Model A gets recall 70% at precision 40%; model B gets recall 60% at precision 55%. Which is better? It depends on the threshold each was run at, and the threshold depends on business costs that may change next quarter. You want a score for the model's **ranking** itself: how well it orders cases from most to least likely, across every possible threshold.

### The idea

Think of ranking a huge pile of CVs. ROC-AUC asks how often a good CV ranks above a bad one, across the whole pile. PR-AUC asks how good the top of the pile is, which is all you'll actually read. When good CVs are rare, the two tell different stories.

[Figure: Two small charts for the same model with rare positives. The ROC curve hugs the top left and looks excellent. The precision-recall curve falls away quickly and looks much weaker.]

_Illustrative, for a model with rare positives._

### Play

**Try to break it.** Keep the model quality fixed and push the prevalence of positives down as far as it goes. Watch both scores.

#### Change the class balance, watch which curve cares

The ROC curve (left) doesn't move when you change prevalence, because both of its axes are rates within a class. The PR curve (right) sinks, because precision mixes in how many negatives there are. A random model's PR-AUC equals the prevalence; scikit-learn: "With random predictions, the AP is the fraction of positive samples" docs.

**Now say why:** why does one score hold steady while the other collapses?

## Maths

### Maths

#### In one breath

Threshold metrics judge one operating point; curves judge them all. The **ROC curve** plots recall against false positive rate as the threshold sweeps. Its area (**ROC-AUC**) is the probability that a random positive is scored above a random negative, and it **doesn't change with class balance**. The **precision–recall curve** plots precision against recall, and its area (**average precision, PR-AUC**) **drops as positives get rarer**, because precision does. So ROC-AUC measures ranking quality in general, and PR-AUC measures how useful the top of the ranking is when positives are rare. Gini (2·AUC − 1) and KS are the credit-scoring dialects of the same idea.What you'll be able to do after this: read both curves, explain AUC as a probability, say which to report for a given scenario, and explain why a 0.98 ROC-AUC fraud model can still be nearly useless.

#### Sweep the threshold, plot each point

1. Axes: false positive rate (share of negatives flagged) across, true positive rate (share of positives caught) up. A model that guesses at random lies on the diagonal.

2. A strict threshold flags only the most confident cases: few false alarms, low recall. Bottom-left.

3. Loosen it: recall rises faster than false alarms if the model ranks well.

4. Very lenient: almost everything is flagged. Top-right.

5. Joining every threshold gives the ROC curve. The area under it is the ROC-AUC, here 0.921 for a model whose classes are separated by 2 standard deviations.

#### AUC = the chance a random positive outranks a random negative

$$ \text{AUC} = P\big(s(x^{+}) > s(x^{-})\big) = \tfrac{1}{n_{+}n_{-}}\textstyle\sum_{i\in +}\sum_{j\in -}\mathbb 1[s_i > s_j] $$

The probability interpretation and its equivalence to the Wilcoxon–Mann–Whitney statistic Fawcett 2006, via the ROC article.

- **ROC-AUC**: The area under the ROC curve, between 0 and 1. 0.5 = random ordering; 1 = every positive above every negative.

- **a ranking probability**: Pick one positive and one negative at random: AUC is the probability the positive gets the higher score. That's why it is threshold-free and prevalence-free.

- **how it's computed**: Count positive–negative pairs ranked correctly (ties count half) and divide by the number of pairs: the Mann–Whitney U statistic, normalised.

Green: positives' scores; red: negatives'. The overlap is where ranking mistakes happen. AUC says nothing about where you'd put a threshold, or whether the scores are calibrated probabilities. Multiply every score by 10 and AUC is unchanged.

#### PR-AUC: how good is the top of the list?

$$ \text{AP} = \sum_{n}(R_n - R_{n-1})\,P_n $$

scikit-learn's definition, which deliberately does not interpolate: linear interpolation of the PR curve "provides an overly-optimistic measure of classifier performance" docs. Davis & Goadrich (2006) showed why straight-line interpolation is wrong in PR space.

- **average precision**: A step-wise area under the precision–recall curve.

- **recall gained**: How much recall increases from threshold n−1 to n: the width of each step.

- **precision there**: The precision at threshold n: the height of the step. AP is the precision averaged over the points where you catch new positives.

Two facts connect the curves. Davis and Goadrich proved that one curve dominates another in ROC space if and only if it dominates in PR space, so if model A is better everywhere, both views agree. But "an algorithm that optimizes the area under the ROC curve is not guaranteed to optimize the area under the PR curve" Davis & Goadrich, ICML 2006. When curves cross, the two areas can rank models differently, and PR-AUC weights the high-score region your business actually uses.

#### Gini, KS and partial AUC

##### Gini (credit risk)

Gini = 2·AUC − 1: twice the area between the ROC curve and the diagonal, rescaled so random = 0 and perfect = 1 ROC article. Banks report scorecards in Gini. Not the same as the Gini impurity used in decision trees.

##### KS statistic (credit risk)

The maximum gap between the cumulative score distributions of "goods" and "bads", equal to max(TPR − FPR) over thresholds: the furthest vertical distance from the ROC curve to the diagonal. That's the same point Youden's J picks. Practitioner rules of thumb vary (often 0.3–0.7 is called acceptable in credit risk) and aren't a formal standard.

##### Partial AUC: only the region you'll use

If you can only ever tolerate a 1% false positive rate (screening a whole population, fraud alerts), the rest of the ROC curve is irrelevant. Partial AUC integrates only up to that FPR; scikit-learn exposes it as `roc_auc_score(..., max_fpr=0.01)` (standardised) docs.

##### Multi-class AUC

One-vs-rest (each class vs all others, then average) or one-vs-one (every pair of classes, then average; Hand & Till 2001). In scikit-learn: `multi_class='ovr'` or `'ovo'`, with macro or prevalence-weighted averaging docs.

## In practice

### In practice

#### Which curve, in which situation

| Scenario | Report | Why |
|---|---|---|
| Fraud detection (0.2%) | PR-AUC + precision@k (alerts per day) | Positives are rare and analysts only see the top of the list; ROC-AUC looks great regardless |
| Rare-disease screening | PR-AUC, plus sensitivity at a fixed specificity | Same imbalance problem; clinicians pick an operating point |
| Credit default ranking (≈5%) | ROC-AUC / Gini, KS | Industry standard for ranking power; cut-offs set later by policy |
| Ad click prediction | ROC-AUC **and** log-loss | AUC for ranking ads; log-loss because bids use the probability itself (see Probability Metrics) |
| Balanced problem (≈50/50) | ROC-AUC | Both curves tell a similar story; ROC is easier to compare across datasets |
| Comparing across test sets with different class balance | ROC-AUC | PR-AUC changes with prevalence, so it isn't comparable between datasets |
| Only low false-positive rates are usable | Partial AUC (max_fpr) | Ignore the region you'll never operate in |

### The answer that sounds right

#### "ROC-AUC is 0.98, ship it"

ROC-AUC uses the false positive _rate_: false alarms divided by all negatives. With 99,800 legitimate transactions, a 1% false positive rate is still 998 false alarms, and against 200 frauds that wrecks precision, yet it barely moves ROC. Saito and Rehmsmeier showed that on imbalanced data "the visual interpretability of ROC plots… can be deceptive with respect to conclusions about the reliability of classification performance" Saito & Rehmsmeier 2015. See it in the Play lab, in the Intuition tab: push prevalence down and ROC-AUC doesn't move, while PR-AUC collapses.

#### What to keep

- **AUC measures ranking, not calibration.** A model with perfect AUC can output probabilities that are all wrong by a factor of 10.

- **AUC hides the operating point.** Two models with equal AUC can differ a lot at the threshold you'll actually use. Report the metric at your operating point too.

- **AUC estimates are noisy, and the measure itself has critics.** Hand (2009) argues AUC implicitly uses different cost assumptions for different classifiers when comparing them, and proposed the H-measure as a coherent alternative Hand 2009, via the ROC article. Bootstrap confidence intervals are cheap; use them.

- **PR-AUC isn't comparable across different prevalences**, so always quote the baseline (the prevalence) next to it.

## Say it

### When would you use PR-AUC instead of ROC-AUC?

#### The interviewer pushes further

Follow-up 1 of 4

Why doesn't ROC-AUC change with class imbalance?

Both axes are rates within a class: TPR divides by positives, FPR by negatives. Changing how many negatives there are doesn't change either rate. Precision divides by everything flagged, so it mixes the classes and moves with prevalence.

Follow-up 2 of 4

Your fraud model has ROC-AUC 0.98. Is it good?

Maybe not. At 0.2% prevalence even a 1% FPR means about 5 false alarms per real fraud. I'd check PR-AUC (against a 0.002 baseline), precision at the recall we need, and alert volume against analyst capacity.

Follow-up 3 of 4

What's the AUC of a random model, and of a model that's always wrong?

Random: 0.5 ROC-AUC, and PR-AUC equal to the prevalence. AUC 0 means a perfectly inverted ranking: flip the scores and you have a perfect model. An AUC below 0.5 usually means a sign bug.

Follow-up 4 of 4

Gini vs AUC vs KS?

Gini = 2·AUC − 1, the same information rescaled. KS = max(TPR − FPR), the best single-threshold separation (also where Youden's J peaks). Credit risk teams report Gini and KS; ML teams usually report AUC.

#### The 30-second answer

ROC-AUC is the probability that a random positive gets a higher score than a random negative. It's threshold-free and doesn't depend on class balance, which makes it good for comparing ranking quality. PR-AUC, or average precision, summarises precision across recall levels; its baseline is the prevalence, so it drops when positives are rare. With heavy imbalance, like fraud, ROC-AUC can look excellent while precision at any useful recall is poor, so I'd report PR-AUC plus precision at the operating point. Neither one measures calibration.

**Go further**

#### What not to say

- "AUC 0.9 means 90% accuracy." It's a ranking probability, not accuracy at any threshold.

- "PR-AUC 0.3 is bad." Compare it with the prevalence: 0.3 against a 0.002 baseline is strong.

- "High AUC means good probabilities." AUC ignores calibration.

**Key terms and sources**

Built from Fawcett (2006), Davis & Goadrich (2006), Saito & Rehmsmeier (2015), Hand (2009) and scikit-learn's docs · checked 28 Oct 2026

#### Glossary

| Term | Meaning |
|---|---|
| **ROC curve** | TPR vs FPR across all thresholds. |
| **ROC-AUC** | Area under it = P(random positive outscores random negative). |
| **PR curve** | Precision vs recall across thresholds. |
| **Average precision (PR-AUC)** | Σ (Rn − Rn−1) Pn; baseline = prevalence. |
| **Gini** | 2·AUC − 1. |
| **KS statistic** | max(TPR − FPR) = largest gap between the classes' cumulative score distributions. |
| **Partial AUC** | Area over a restricted FPR range. |
| **DET curve** | A ROC variant plotting false negative rate vs false positive rate on normal-deviate axes (used in biometrics and speaker verification). |

#### What this page is built from

1. T. Fawcett, "An introduction to ROC analysis", _Pattern Recognition Letters_ 27 (2006) 861–874; summarised in Receiver operating characteristic (AUC as probability, Mann–Whitney, Gini, partial AUC, Youden).

2. J. Davis & M. Goadrich, The relationship between Precision-Recall and ROC curves, ICML 2006.

3. T. Saito & M. Rehmsmeier, The precision-recall plot is more informative than the ROC plot when evaluating binary classifiers on imbalanced datasets, PLOS ONE 10(3) (2015).

4. D. J. Hand, "Measuring classifier performance: a coherent alternative to the area under the ROC curve", _Machine Learning_ 77 (2009).

5. scikit-learn, Metrics and scoring: average_precision_score, roc_auc_score (max_fpr, ovr/ovo), DET curves.

6. Credit-scoring KS and Gini usage: Experian; SHAP stability in credit risk (KS ranges).
