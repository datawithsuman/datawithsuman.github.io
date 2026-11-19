# Class Imbalance

> 2% fraud: should you SMOTE it, weight it, or just move the threshold?

- Track: Fundamentals › Classical ML › Core concepts
- Type: Concept · 30 min
- Page: https://aimlrounds.com/tracks/fundamentals/class-imbalance/
- Before this: Classification Metrics (`fundamentals/classification-metrics`), Thresholds & Misclassification Costs (`fundamentals/thresholds-and-costs`)
- Quiz topic: `mlcore`

## Intuition

### The situation

About 2% of your orders are fraud, and the default threshold flags almost nothing. A teammate wants to balance the classes to 50/50. The interviewer asks:

> How do you handle a 2% positive class?

**Running example:** the food-delivery app's fraud screen. Each order has two risk signals (standardised); about **2%** of orders are fraudulent. Training data: 6,000 simulated orders (106 fraud); a validation set of 4,000 for choosing thresholds; a test set of 20,000 (1.92% fraud). The model is logistic regression throughout, so the only thing that changes between experiments is how we handle the imbalance. This lesson builds on Classification Metrics, ROC-AUC vs PR-AUC and Thresholds & Costs.

#### The rare class is the one you care about

Fraud, churn, defaults, rare diseases, machine failures, click-through: the event you want to catch is the minority. Three things go wrong at once. **Accuracy** rewards ignoring it (always "legit" = 98%). A default threshold of 0.5 flags almost nothing, because with a 2% base rate few orders ever look more than 50% likely to be fraud. And with only ~100 positive examples, the model has little to learn the minority pattern from. People lump all three under "imbalance", but they need different fixes.

### The idea

Think of airport security. Very few bags are dangerous, but you don't pretend half of them are. You keep an honest risk score for every bag, then decide how risky a bag must be to open, based on what a miss and a search each cost.

[Figure: Orders ranked from low risk to high risk. The default cut at 0.5 catches almost nothing. A much lower cut catches far more of the rare fraud.]

_Illustrative. Ranking orders and deciding where to cut are two separate jobs._

### Play

**Try to break it.** Start at a threshold of 0.5 and read the recall and the cost. Then slide it down until the cost is as low as you can get.

#### Move the threshold, not the data

Same trained model, only the cut changes. Try 0.31 (best F1 on validation) and 0.02–0.03 (the cost-optimal t* ≈ 0.024 from the Maths tab).

On the test orders, the default 0.5 costs ₹2,44,000 (most fraud slips through), the F1-best 0.31 costs ₹1,96,960, and the cost-optimal 0.02 costs ₹1,03,560 while catching 84% of fraud: the same model, less than half the cost, and no resampling involved.

Elor & Averbuch-Elor (2022) tested this at scale on 73 imbalanced datasets: with a tuned threshold, "balancing the data and optimizing the decision threshold yield comparable prediction performance" except for very weak classifiers, and they recommend tuning the threshold because it is simpler and cheaper to compute. For the strong models (XGBoost, CatBoost), balancing didn't improve AUC at all: "best prediction is achieved by using a strong classifier and balancing the data is not required nor beneficial" arXiv:2201.08528, §4–5. scikit-learn's `TunedThresholdClassifierCV` chooses the threshold by cross-validation.

**Now say why:** why did this help so much without touching the model or the data?

## Maths

### Maths

#### In one breath

When 2% of orders are fraud, a model that always says "legit" is 98% accurate and useless. The usual reflex is to "fix the imbalance" by reweighting or resampling the training data. On our data, and in recent large studies, that reflex mostly **doesn't improve ranking** (AUC is unchanged), **breaks the probabilities** (the model now thinks fraud is 10× more common than it is), and only **moves the decision threshold**, something you can do directly. The reliable recipe: use a proper metric (PR-AUC, log loss, cost), train a strong model on the real data, then **choose the threshold** from costs or a validation set. Resampling still helps weak learners and fixed-threshold systems, and only inside the training fold.What you'll be able to do after this: explain why accuracy fails, compare weights/resampling/SMOTE/thresholds with numbers, undo resampling's damage to probabilities, and answer "how would you handle imbalanced data?" without the standard wrong answer.

#### Probabilities, thresholds and the base rate

A probabilistic classifier outputs p = P(fraud | order). A good one is **calibrated**: among orders it scores 0.3, about 30% are fraud, so its average prediction matches the base rate (here 1.9%). Turning p into a decision needs a **threshold** t: flag if p ≥ t. Ranking quality (AUC) doesn't depend on t; precision, recall and F1 do. The cost-optimal threshold, if a missed fraud costs CFN and a false alarm CFP, is:

$$ t^{*} = C_{FP} \,/\, (C_{FP} + C_{FN}) $$

Derived in Thresholds & Costs. Note what this says: the imbalance doesn't need "fixing" to catch fraud; a calibrated model plus the right threshold already accounts for both the base rate and the costs.

- **best threshold**: Flag an order when its fraud probability exceeds this. Requires calibrated probabilities.

- **cost of a false alarm**: E.g. ₹20 of a reviewer’s time and an annoyed honest customer.

- **cost of a missed fraud**: E.g. a ₹800 chargeback. With these numbers t* = 20/820 ≈ 0.024: flag anything with more than a 2.4% fraud chance.

#### Separate ranking from deciding

A classifier does two jobs: **rank** orders by risk, and **decide** where to cut. Imbalance mostly hurts the decision (a default cut of 0.5 is wrong for rare events), and the decision is cheap to fix after training. Ranking is only hurt when there are too few minority examples to learn from, and reweighting or duplicating the same ~100 fraud cases adds no new information about them. So: get the best ranking you can on the real distribution, keep the probabilities honest, and choose the cut with the costs. Reach for resampling only when you can't control the cut, or your model is weak.

#### Correct the probabilities back

Undersampling is sometimes necessary for speed (billions of negatives, as in click prediction). Then correct the predicted probabilities for the sampling rate. If you kept a fraction β of the negatives:

$$ p = \beta\,q \,/\, \bigl(\beta\,q - q + 1\bigr) $$

Prior-shift correction for undersampling, e.g. Dal Pozzolo et al., "Calibrating probability with undersampling for unbalanced classification" (IEEE SSCI 2015). Applying it is equivalent to subtracting log(1/β) from the model's log-odds.

- **corrected probability**: The fraud probability on the real, imbalanced population.

- **model output**: What the model trained on the undersampled data predicts.

- **negatives kept**: β = negatives kept / negatives available. Here 106 / 5,894 ≈ 0.018.

On our data the correction brings the average prediction from 21.3% back to 2.9% and log loss from 0.378 to 0.062, close to the uncorrected model's 0.057, with the same AUC. Class weights can be undone the same way (shift the intercept by log of the weight ratio). Better still: calibrate on untouched validation data (`CalibratedClassifierCV`).

## In practice

### In practice

#### The menu of fixes

| Approach | What it does | Tools |
|---|---|---|
| **Better metric** | Judge by PR-AUC, recall at fixed precision, log loss, expected cost; not accuracy | scikit-learn metrics |
| **Threshold moving** | Keep the model, choose t from costs or validation | `TunedThresholdClassifierCV`, manual |
| **Class weights** | Multiply the loss of minority errors | `class_weight="balanced"`, `scale_pos_weight` |
| **Random over/undersampling** | Duplicate minority / drop majority rows (training fold only) | imbalanced-learn |
| **SMOTE and variants** | Synthesise minority points between minority neighbours | imbalanced-learn |
| **More minority data / better features** | Address the real bottleneck: few examples | labelling, data collection |

imbalanced-learn describes the problem as the decision function tending "to favour the class with the larger number of samples" imbalanced-learn. Whether that "favouring" is a bug or correct Bayesian behaviour is exactly the question this lesson answers.

#### Five ways to handle the same 2% fraud

Plot: test orders grouped by predicted probability (10 bins); each dot compares the average prediction with the actual fraud rate in that bin. On the diagonal = calibrated. Logistic regression in every case; trained in your browser.

| Method | AUC | Mean predicted | Log loss | F1 @ 0.5 | Best t | F1 @ best t |
|---|---|---|---|---|---|---|
| No correction | 0.934 | 1.9% | 0.057 | 0.315 | 0.31 | 0.430 |
| Class weights | 0.934 | 21.4% | 0.336 | 0.182 | 0.96 | 0.426 |
| Oversample | 0.934 | 21.4% | 0.337 | 0.182 | 0.96 | 0.428 |
| Undersample | 0.934 | 21.3% | 0.378 | 0.173 | 0.98 | 0.432 |
| Undersample + correction | 0.934 | 2.9% | 0.062 | 0.426 | 0.55 | 0.431 |

Every method ranks equally well (AUC 0.934), and every method reaches the same F1 (~0.43) once its threshold is tuned. The difference is all in the probabilities: the three corrections inflate the average fraud prediction elevenfold and multiply log loss by about six. At the default 0.5 threshold they flag over 3,000 of 20,000 orders with 10% precision, worse F1 than not correcting at all. The resampled models only "need" a threshold of 0.96–0.98 to get back to where the plain model was at 0.31.

#### Synthetic minority points, and when they help

1. A few fraud orders (red) among many legit ones.

2. SMOTE (Chawla et al., 2002) picks a minority point and finds its k nearest minority neighbours (default k = 5).

3. It places a synthetic fraud order at a random point on the segment to one neighbour.

4. Repeat until the minority class is as large as you asked for. Unlike duplication, the new points fill the space between real ones.

SMOTE spawned more than 100 variants (Borderline, SVM-SMOTE, ADASYN…). The 2022 evidence is sobering: with a fixed threshold, the sophisticated SMOTE variants were "not more effective than the simple random oversampler" for strong boosted trees, and with a tuned threshold, balancing at all brought them no gain; SMOTE did help weak learners (MLP, SVM, decision trees, AdaBoost) and fixed-threshold setups Elor & Averbuch-Elor 2022. Synthetic points can also land in the majority region and blur the boundary, and on categorical or high-dimensional data, interpolation can create impossible rows.

#### The whole recipe

1. **Pick the metric from the decision:** expected cost, recall at a precision floor, or PR-AUC; log loss/Brier if probabilities matter. Not accuracy.

2. **Split with stratification** (and groups/time if relevant) so every fold has minority cases.

3. **Train a strong model on the real distribution** (gradient boosting, well-regularised logistic regression).

4. **Check calibration**; calibrate on validation data if needed.

5. **Choose the threshold** from costs (t* = CFP/(CFP + CFN)) or by validation.

6. **Only then** try class weights or resampling, inside the CV pipeline, and keep them only if the chosen metric improves. Correct the probabilities if you use them.

7. **Collect more minority examples** if recall is capped: that's the one fix that adds information.

#### Scenarios

##### Fraud screen with a review team of fixed size

Rank by score and review the top N per day: only ranking matters (PR-AUC, precision@N). No resampling or threshold tuning needed.

##### Ad click prediction feeding a bid

Probabilities feed money: calibration is critical. Undersample negatives for speed if you must, then apply the prior correction and check log loss.

### The answer that sounds right

#### "Balance the classes to 50/50 and the model will notice fraud"

The standard advice is to oversample fraud, undersample legit orders, or weight fraud 50× in the loss. It does change the output: at threshold 0.5 the model now flags far more orders. But look at what it costs (see Compare the fixes, in the In practice tab): the model now believes 21% of orders are fraud, when the true rate is 1.9%. Its ranking of orders is **exactly as good as before** (AUC 0.934 in every case). All the "fix" did was distort the probabilities so that 0.5 lands where a lower threshold would have landed on the original model. van den Goorbergh et al. (2022) found the same in clinical risk models: all correction methods "led to poor calibration, but not to better discrimination" JAMIA 2022.

#### Caveats

- **When resampling/weights do help:** weak or high-bias models, systems where you can't set the threshold, extremely rare classes where the loss barely "sees" the minority during training (e.g. neural nets with mini-batches containing no positives), and undersampling for compute.

- Our demo uses a linear model, where reweighting mostly shifts the intercept. With flexible models, weights can also change the shape of the boundary, for better or worse; always validate.

- "Imbalance" is often a proxy for the real problem: few minority examples, overlapping classes, or label noise. Resampling fixes none of these.

- Never resample before the train/test split, and never evaluate on resampled data.

## Say it

### How do you handle a 2% positive class?

#### The interviewer pushes further

Follow-up 1 of 5

Does oversampling or SMOTE improve the model?

It changes where the model cuts, not how well it ranks: AUC is typically unchanged for strong models, and probabilities become miscalibrated. It can help weak learners or when the threshold is fixed. It must happen inside the training fold only.

Follow-up 2 of 5

Class weights vs threshold tuning?

For a linear model, weights mostly shift the intercept, which is equivalent to a threshold change but corrupts probabilities. Threshold tuning keeps calibration and can be re-tuned without retraining.

Follow-up 3 of 5

Why is accuracy misleading, and what would you use?

The majority-class baseline already scores 98%. Use precision/recall/F1 at a chosen threshold, PR-AUC for ranking, log loss/Brier for probabilities, or business cost.

Follow-up 4 of 5

How do you fix probabilities after undersampling?

Apply the prior correction p = βq / (βq − q + 1) with β the fraction of negatives kept, or recalibrate on untouched validation data.

Follow-up 5 of 5

When is imbalance a real problem?

When there are very few minority examples to learn from, classes overlap heavily, or the training procedure rarely sees positives (mini-batches). Then more data, better features, focal loss or sampling-for-batches help.

#### The 30-second answer

First I'd pick a metric that reflects the decision, such as expected cost, recall at a fixed precision or PR-AUC, because accuracy is meaningless with a 2% base rate. Then I'd stratify the splits, train a strong model on the real distribution, check calibration, and choose the threshold from the error costs or on validation data, since the default 0.5 is the main thing imbalance breaks. Class weights and resampling mostly just shift the threshold while distorting the probabilities; recent studies found they don't improve AUC for strong models and that a tuned threshold matches them. I'd use them inside the training folds only for weak models or fixed-threshold systems, correct the probabilities afterwards, and prioritise getting more minority examples.

**Go further**

#### What not to say

- "Always SMOTE imbalanced data." It often doesn't help strong models and breaks calibration.

- "Balance the test set too." Evaluate on the real distribution.

- "Resample, then split." That leaks copies of test rows into training.

**Key terms and sources**

Why rare classes are hard, what actually goes wrong, and what each fix really does: class weights, over- and undersampling, SMOTE, threshold moving and prior correction · built from Elor & Averbuch-Elor (2022), van den Goorbergh et al. (2022), Chawla et al. (2002) and the scikit-learn / imbalanced-learn docs · checked 28 Oct 2026

#### Evidence

##### F1 on 73 datasets, CatBoost (Elor & Averbuch-Elor 2022, Table 3)

no balancing, threshold 0.5

0.444

no balancing, tuned threshold

0.532

random oversampling

0.525

SMOTE

0.529

Mean F1, higher is better; ± about 0.02 p. 5. For a weak MLP the picture flips: baseline 0.303 with a tuned threshold vs 0.411 with SMOTE.

##### Clinical risk models

van den Goorbergh et al. (JAMIA 2022), logistic regression with random under/oversampling and SMOTE on ovarian-tumour data plus simulations: corrections strongly overestimated the minority-class probability, did not improve AUROC, and the sensitivity/specificity gains were matched by simply shifting the threshold PMC9382395. A 2024 follow-up extended this to machine-learning models with the same conclusion for calibration arXiv:2404.19494.

#### Key terms

| Term | Meaning |
|---|---|
| **Base rate / prevalence** | Share of the minority class in the population. |
| **Calibration** | Predicted probabilities match observed frequencies. |
| **Threshold moving** | Choosing the probability cut-off instead of using 0.5. |
| **Class weights** | Scaling each class's contribution to the loss. |
| **Random over/undersampling** | Duplicate minority / drop majority training rows. |
| **SMOTE** | Synthetic minority points interpolated between minority neighbours. |
| **Prior correction** | Mapping resampled-model probabilities back to the true base rate. |

#### What this page is built from

1. Y. Elor & H. Averbuch-Elor, "To SMOTE, or not to SMOTE?", arXiv:2201.08528, 2022 (73 datasets, strong vs weak classifiers, threshold tuning, Table 3).

2. R. van den Goorbergh, M. van Smeden, D. Timmerman & B. Van Calster, "The harm of class imbalance corrections for risk prediction models", _JAMIA_ 29(9), 2022, PMC9382395.

3. A. Carriero et al., "The harms of class imbalance corrections for machine learning based prediction models: a simulation study", arXiv:2404.19494, 2024.

4. N. Chawla, K. Bowyer, L. Hall & W. Kegelmeyer, "SMOTE: synthetic minority over-sampling technique", _JAIR_ 16, 2002.

5. A. Dal Pozzolo, O. Caelen, R. Johnson & G. Bontempi, "Calibrating probability with undersampling for unbalanced classification", IEEE SSCI 2015 (prior correction).

6. imbalanced-learn and scikit-learn threshold tuning docs.

Fraud data is simulated with fixed seeds; all models are trained live in your browser (logistic regression by Newton's method).
