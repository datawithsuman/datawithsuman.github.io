# Probability Metrics

> The model ranks perfectly, so why are the bids wrong?

- Track: Fundamentals › Classical ML › Evaluation metrics
- Type: Concept · 25 min
- Page: https://aimlrounds.com/tracks/fundamentals/probability-metrics/
- Before this: ROC-AUC vs PR-AUC (`fundamentals/roc-auc-vs-pr-auc`), Logistic Regression (`fundamentals/logistic-regression`)
- Quiz topic: `metrics`

## Intuition

### The situation

Your ad model bids price = P(click) × value. It ranks ads perfectly, but it says 4% when the true rate is 2%, so every bid is double what it should be. The interviewer asks:

> How do you check whether a model's probabilities can be trusted?

**Scenarios:** ad click-through prediction for bidding, insurance and credit risk pricing, medical risk scores shown to patients, weather forecasting (where the Brier score was born), and deep-network confidence. Predictions come from a simple model (illustrative) whose calibration you can break and fix live; the published results are from Guo et al. (2017).

#### "The model ranks perfectly, so why are we losing money on bids?"

An ad platform bids **price = P(click) × value of a click**. If the model says 4% when the true rate is 2%, every bid is double what it should be. The model can still _rank_ ads perfectly, so its AUC looks great. Ranking metrics can't see this error. You need metrics that check whether the numbers themselves are right.

### The idea

Think of a weather forecaster. When they say 70% chance of rain, it should rain on about 70% of those days. That's calibration. A forecaster can order days perfectly by rain risk and still get the chances wrong.

[Figure: A reliability diagram. A dashed diagonal shows perfect calibration. An overconfident model's curve sits below it at high predictions and above it at low ones.]

_Illustrative. A reliability diagram compares what a model says with what really happens._

### Play

**Try to break it.** Move the temperature away from 1 in both directions, and watch AUC, log-loss and the diagram. Then apply temperature scaling.

#### Reliability diagram: break the calibration, watch which metrics notice

10% positives; predictions computed over 20,000 cases. Left: reliability diagram (bars = observed frequency per confidence bin; diagonal = perfect; red = gap). Right: how many predictions fall in each bin. Overconfidence (T < 1) pushes predictions toward 0 and 1, so bars sit below the diagonal on the right. AUC never changes with T, because temperature doesn't change the order.

**Now say why:** why can AUC stay put while the probabilities become badly wrong?

## Maths

### Maths

#### In one breath

When decisions use the probability itself (pricing, bidding, risk scores, the cost thresholds from Thresholds & Costs), you need probabilities that are **right**, not just well ranked. **Calibration** means "of all cases predicted 70%, about 70% happen". **Log-loss** and the **Brier score** are proper scoring rules: they're best only when predicted probabilities equal the true ones, so they reward both sharpness and calibration. A **reliability diagram** and the **expected calibration error (ECE)** isolate calibration. Key insight: you can wreck calibration without changing **AUC at all**. Modern deep networks tend to be overconfident, and a one-parameter fix, **temperature scaling**, usually repairs it. What you'll be able to do after this: read a reliability diagram, explain why AUC can't detect miscalibration, choose between log-loss, Brier and ECE, and calibrate a model properly.

#### Calibration and sharpness

##### Calibration

Predicted probabilities match observed frequencies: P(y = 1 | p̂ = p) = p for every p. Guo et al.: "given 100 predictions, each with confidence of 0.8, we expect that 80 should be correctly classified" [Guo et al. 2017, p. 2](https://arxiv.org/pdf/1706.04599#page=2).

##### Sharpness (resolution)

Predictions far from the base rate. Always predicting the base rate (say 10%) is perfectly calibrated and useless. Good probabilistic models are both calibrated and sharp.

#### Two proper scoring rules and one calibration error

$$ {\text{LL} = -\tfrac1n\textstyle\sum\big[y\log\hat p + (1-y)\log(1-\hat p)\big]} \quad {\text{BS} = \tfrac1n\textstyle\sum(\hat p - y)^2} \quad {\text{ECE} = \textstyle\sum_m \tfrac{|B_m|}{n}\,\big|\text{acc}(B_m) - \text{conf}(B_m)\big|} $$

ECE as defined by Guo et al., Eq. 3 [p. 3](https://arxiv.org/pdf/1706.04599#page=3); Brier score: Brier (1950); scikit-learn calls it "strictly proper", achieving "the best score only when the estimated probabilities equal the true ones" [docs](https://scikit-learn.org/stable/modules/model_evaluation.html).

- **log-loss**: Negative log-likelihood: −log of the probability given to what happened. Unbounded: a confident wrong prediction (p = 0.001 for an event that happens) costs 6.9. Strictly proper.

- **Brier score**: Mean squared difference between predicted probability and the 0/1 outcome. Bounded between 0 and 1, gentler on confident mistakes. Also strictly proper.

- **expected calibration error**: Bin predictions by confidence, compare each bin's average confidence with its observed frequency, and take the weighted average gap. Measures calibration only, not sharpness.

#### Murphy's decomposition: reliability − resolution + uncertainty

$$ {\text{BS}} = {\text{REL}} - {\text{RES}} + {\text{UNC}} $$

Murphy (1973), via the [Brier score](https://en.wikipedia.org/wiki/Brier_score) article. scikit-learn's warning follows from it: "A lower Brier loss, for instance, does not necessarily mean a better calibrated model" [docs](https://scikit-learn.org/stable/modules/model_evaluation.html); a sharper model can win on resolution while being worse calibrated. The **Brier skill score** 1 − BS / BSbase-rate rescales it so that predicting the base rate scores 0.

- **Brier score**: Lower is better.

- **reliability**: Calibration error: how far each group's predicted probability is from what actually happened. 0 = perfectly reliable. Lower is better.

- **resolution**: How much the groups' outcome rates differ from the overall base rate: sharpness that's real. Higher is better, so it's subtracted.

- **uncertainty**: ō(1 − ō) for base rate ō: how hard the problem is. Fixed by the data; no model changes it.

#### Platt scaling, isotonic regression, temperature scaling

$$ {\hat q_i} = \max_k\ \mathrm{softmax}\big({z_i} \,/\, {T}\big)^{(k)} $$

Guo et al., Eq. 9: "temperature scaling does not affect the model's accuracy" [p. 6](https://arxiv.org/pdf/1706.04599#page=6).

- **calibrated confidence**: The new probability for input i.

- **the logits**: The model's raw scores before the softmax: untouched.

- **one temperature**: A single scalar T > 0 fitted by minimising log-loss on a held-out validation set. T > 1 softens overconfident outputs. Because dividing by T doesn't change the argmax, accuracy is unchanged.

| Method | What it fits | Use when |
|---|---|---|
| **Platt scaling** | A logistic regression on the model's score (2 parameters) | Binary classifiers with sigmoid-shaped distortion (SVMs, boosted trees); small validation sets |
| **Temperature scaling** | One parameter on the logits | Neural networks, multi-class; the default first try |
| **Isotonic regression** | Any monotonic step function | Large validation sets and odd-shaped distortions; can overfit small sets |
| **Histogram binning** | One probability per score bin | Simple, robust; can change class predictions |

In scikit-learn: `CalibratedClassifierCV(method="sigmoid" | "isotonic")`, fitted on data the model wasn't trained on. Logistic regression is often well calibrated already: it "is more likely to return well calibrated predictions by itself" thanks to its canonical link [scikit-learn calibration docs](https://scikit-learn.org/stable/modules/calibration.html).

## In practice

### In practice

#### Bigger, more accurate, and worse calibrated

Guo et al. found that "modern neural networks, unlike those from a decade ago, are poorly calibrated": a 110-layer ResNet on CIFAR-100 is more accurate than a 5-layer LeNet, but its average confidence is far above its accuracy. Depth, width, batch normalisation and less weight decay all made calibration worse; their explanation is that networks keep lowering training log-loss by growing more confident after they already classify the training data correctly [Guo et al. 2017, §3](https://arxiv.org/pdf/1706.04599#page=3).

##### ECE on CIFAR-100 (ResNet-110), before and after post-hoc calibration (↓ better)

uncalibrated

16.53%

histogram binning

2.66%

isotonic regression

4.99%

temperature scaling

1.26%

matrix scaling

25.49%

15 bins. Matrix scaling has too many parameters for 100 classes and overfits the validation set [Table 1, p. 6](https://arxiv.org/pdf/1706.04599#page=6). Across vision and NLP datasets, uncalibrated ECE was "typically between 4 to 10%", and temperature scaling was best on the vision tasks [p. 7](https://arxiv.org/pdf/1706.04599#page=7).

#### Which metric, in which situation

| Scenario | Report | Why |
|---|---|---|
| Ad click prediction for bidding | Log-loss + calibration (predicted/actual CTR ratio by segment) | Bids multiply by p; a 2× bias doubles spend |
| Credit default, insurance claims pricing | Brier / log-loss + reliability by score band; AUC/Gini for ranking | Prices and capital depend on the probability level, not just the order |
| Weather forecasts ("70% chance of rain") | Brier score and its decomposition | Where it came from: Brier, _Monthly Weather Review_, 1950 |
| Medical risk shown to patients or doctors | Calibration plot + Brier | A "12% risk" must mean 12%; patients act on the number |
| Deep-network classifier confidence (abstain / route to a human) | ECE + log-loss; temperature-scale first | Overconfidence makes "only answer when sure" unreliable |
| Fraud alert ranking with a capacity limit | PR-AUC; calibration matters less | Only the order of the top alerts is used (unless costs use p) |

### The answer that sounds right

#### "AUC is 0.92, the probabilities must be fine"

AUC only looks at the **order** of the scores. Squash or stretch every probability with any monotonic function (make them all twice as confident) and the order, and the AUC, are unchanged, while every probability is now wrong. The Play lab, in the Intuition tab, proves it: move the temperature and AUC stays fixed at its value while log-loss, Brier and ECE all move.

#### What to keep

- **ECE depends on binning** (number of bins, equal-width vs equal-count) and is noisy with few samples per bin; it also ignores sharpness. Report it with log-loss or Brier, never alone.

- **Calibrate on held-out data**, never the training set, and re-check after data drift.

- **Resampling and class weights break calibration** (see Thresholds & Costs); recalibrate afterwards.

- **Calibration is about groups, not individuals.** "70%" being right on average says nothing about any one case, and can hide miscalibration within subgroups (check fairness-relevant segments).

## Say it

### How do you check whether a model's probabilities can be trusted?

#### The interviewer pushes further

Follow-up 1 of 4

Log-loss vs Brier: which?

Both are proper. Log-loss is unbounded and harshly punishes confident mistakes, which suits systems where a 0.1% prediction for a frequent event is catastrophic, and it's what models are trained on. Brier is bounded, gentler, decomposes into reliability, resolution and uncertainty, and is common in forecasting and medicine.

Follow-up 2 of 4

Can a model have high AUC and poor calibration?

Yes. Any monotonic distortion of the scores keeps AUC identical while making probabilities wrong. Conversely, predicting the base rate for everyone is perfectly calibrated with AUC 0.5.

Follow-up 3 of 4

How does temperature scaling work, and why doesn't it change accuracy?

Divide the logits by a scalar T fitted to minimise validation log-loss. It rescales confidence but keeps the logits' order, so the argmax (and accuracy) is unchanged.

Follow-up 4 of 4

What's wrong with ECE?

It depends on the binning scheme, is biased with few samples, ignores sharpness, and only looks at the top-class confidence. Pair it with log-loss or Brier and a reliability diagram.

#### The 30-second answer

When decisions use the probability itself, like bidding, pricing or risk thresholds, I check calibration as well as ranking. AUC can't detect miscalibration because it only depends on order. Log-loss and Brier are proper scoring rules that reward both calibration and sharpness; a reliability diagram and ECE isolate calibration. Modern neural networks tend to be overconfident, and temperature scaling, one parameter fitted on validation data, usually fixes that without changing accuracy. For other models I'd use Platt scaling or isotonic regression on held-out data.

**Go further**

#### What not to say

- "Softmax outputs are probabilities." They sum to 1, but they're often miscalibrated.

- "Lower Brier means better calibrated." It also rewards sharpness.

- "Calibrate on the training set." Use held-out data.

**Key terms and sources**

Log-loss, Brier score, reliability diagrams, ECE and calibration methods · built from Guo et al. (2017), Brier (1950), Murphy (1973) and scikit-learn's docs · checked 28 Oct 2026

#### Glossary

| Term | Meaning |
|---|---|
| **Calibration** | Predicted probabilities match observed frequencies. |
| **Proper scoring rule** | Expected score is optimised by reporting the true probability (log-loss, Brier). |
| **Log-loss / NLL / cross-entropy** | −mean log probability of what happened. |
| **Brier score** | Mean squared error of probabilities. |
| **Reliability diagram** | Observed frequency vs predicted confidence, per bin. |
| **ECE / MCE** | Weighted average / maximum gap between confidence and accuracy over bins. |
| **Temperature scaling** | Divide logits by a fitted T. |
| **Platt / isotonic** | Sigmoid / monotonic step-function recalibration. |

#### What this page is built from

1. C. Guo, G. Pleiss, Y. Sun & K. Weinberger, [On Calibration of Modern Neural Networks](https://arxiv.org/abs/1706.04599), ICML 2017 (ECE, reliability diagrams, temperature scaling, Table 1).

2. G. W. Brier, "Verification of forecasts expressed in terms of probability", _Monthly Weather Review_ (1950); A. H. Murphy, "A new vector partition of the probability score" (1973); summary in [Brier score](https://en.wikipedia.org/wiki/Brier_score).

3. scikit-learn, [Metrics and scoring](https://scikit-learn.org/stable/modules/model_evaluation.html) (log-loss, Brier, strictly proper) and [Probability calibration](https://scikit-learn.org/stable/modules/calibration.html).

4. A. Niculescu-Mizil & R. Caruana, "Predicting good probabilities with supervised learning", ICML 2005 (Platt vs isotonic; background).

The live lab uses an illustrative two-bell-curve score model with 10% positives; the published numbers are Guo et al.'s.
