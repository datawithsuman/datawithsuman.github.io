# Cross-Validation & Data Leakage

> How did a model score 86% on pure noise, and how do you make sure yours isn't?

- Track: Fundamentals › Classical ML › Core concepts
- Type: Concept · 30 min
- Page: https://aimlrounds.com/tracks/fundamentals/cross-validation-and-leakage/
- Before this: The Bias–Variance Trade-off (`fundamentals/bias-variance`)
- Quiz topic: `mlcore`

## Intuition

### The situation

Your cross-validation says 0.92 AUC, and production says 0.70. Nothing in the code threw an error. The interviewer asks:

> What is data leakage, and how does cross-validation help you avoid it?

**Running example:** the food-delivery app's data team. Three simulated situations, each with a known true answer so the leak is visible: (1) predicting whether a customer will churn from 10,000 behavioural signals that are in fact pure noise (true accuracy 50%); (2) trying many model variants and keeping the one with the best validation score; (3) predicting a rider's "safe driver" badge from repeated trip records, several per rider.

#### The score you report is a prediction too

"Validation accuracy 86%" is a claim about data the model hasn't seen. If any information about that data leaked into training, the claim is wrong, and nothing in the code will tell you. scikit-learn: testing on the training data "is a methodological mistake: a model that would just repeat the labels of the samples that it has just seen would have a perfect score but would fail to predict anything useful on yet-unseen data" [cross-validation guide](https://scikit-learn.org/stable/modules/cross_validation.html). Every technique on this page exists to keep the scoring data genuinely unseen.

### The idea

Think of a practice exam where you've already seen the answer key. You'll score brilliantly, and the score tells you nothing. Leakage is any way the answers reach your model before it's tested, and it often looks like good hygiene.

[Figure: Five rows of five blocks. In each row, a different block is held out for validation while the other four train the model.]

_5-fold cross-validation: each block gets one turn being held out._

### Play

**Try to break it.** Select features on all the rows, then cross-validate, and read the accuracy. The labels here are random, so the truth is 50%. Then select inside each fold.

#### Feature selection outside CV finds signal in noise

200 customers, 10,000 random features, random churn labels. Pick the 25 features whose class means differ most, then classify with nearest centroid. Generated in your browser (takes a second).

Selecting on all rows: CV accuracy **86.5%** on data with no signal at all. Selecting inside each training fold: **51%**, the truth. With 10,000 random features, some will separate the two classes in these 200 rows by pure chance; selecting them with the validation rows included bakes that chance into the "test". scikit-learn's own version of this experiment: 0.76 accuracy when selecting on all data vs 0.5 when splitting first [common pitfalls](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage). The same leak, smaller, happens with scaling, imputation, target encoding and SMOTE fitted before the split.

**Now say why:** how did pure noise score so well, when no line of code looks wrong?

## Maths

### Maths

#### In one breath

An evaluation is only honest if the data used to score the model played **no part** in building it. **k-fold cross-validation** rotates which slice is held out, so every row is tested once and the estimate is less noisy than a single split. The split must copy how the model will meet new data in production: **stratify** rare classes, keep each **group** (patient, customer, device) on one side, and never let a model see the **future**. **Leakage** is any information at training time that won't exist at prediction time: preprocessing or feature selection fitted on all rows, tuning on the test set, duplicated or related rows across the split, or features that are recorded after the outcome. Leaks don't crash anything; they just give you a great score that vanishes in production. What you'll be able to do after this: choose the right splitter for a dataset, explain nested CV, spot the five common leaks, and reproduce three of them with numbers.

#### Train, validation, test, and k-fold

1. Start with all the labelled data.

2. Set aside a **test set** first and don't touch it until the very end. It's your one honest final exam.

3. Split the rest into k = 5 folds. Train on four (teal), validate on the fifth (orange), and rotate so every fold is the validation set once.

4. Average the five validation scores. The spread across folds tells you how much the score depends on the particular split.

5. Use the CV score to choose models and settings; report the test score once, for the final choice.

$$ {\mathrm{CV}_k} = {\frac1k\sum_{j=1}^{k}} {\mathrm{Score}\bigl(}{\hat f^{(-j)}}{,\ \text{fold}_j\bigr)} $$

scikit-learn also notes leave-one-out "often results in high variance as an estimator for the test error" and costs n fits [cross-validation guide](https://scikit-learn.org/stable/modules/cross_validation.html).

- **the CV estimate**: Estimated performance of the whole training procedure on unseen data.

- **average over folds**: k separate train/validate runs; scikit-learn: “most authors and empirical evidence suggest that 5 or 10-fold cross validation should be preferred to LOO”.

- **model trained without fold j**: Fitted on everything except fold j, including every preprocessing step.

- **score on fold j**: Accuracy, AUC, RMSE… computed only on the held-out rows.

#### Cross-validate the whole pipeline, split like production

Two rules cover almost everything:

1. **Everything that learns from data goes inside the fold.** Scaling, imputation, encoding, feature selection, resampling, target encoding, PCA and the model itself are one pipeline, refitted on each training fold and only applied to its validation fold. In scikit-learn that means a `Pipeline` passed to `cross_val_score` or `GridSearchCV`.

2. **The validation fold must look like the future.** If production sees new customers, validation must contain customers the model never saw; if production sees next month, validation must be later than training.

Kaufman, Rosset, Perlich & Stitelman define leakage as "the introduction of information about the data mining target that should not be legitimately available to mine from", and recommend a strict "learn-predict separation" [ACM TKDD 2012](https://doi.org/10.1145/2382577.2382579).

#### Tune inside, score outside

If you choose hyperparameters with the same CV loop that produces the score you report, the score is optimistic (the same leak as tuning on test, in a milder form). **Nested CV** wraps the whole tuning procedure (e.g. a `GridSearchCV`) inside an outer loop: each outer fold is scored by a model whose settings were chosen using only the other folds. Varma & Simon (2006) showed that tuning and estimating in one CV loop gives a biased error estimate, and that the nested procedure "gives an estimate of the error that is very close to that obtained on the independent testing set" [BMC Bioinformatics 7](https://doi.org/10.1186/1471-2105-7-91). It costs kouter × kinner × grid fits; with plenty of data, a single untouched test set does the same job.

##### Target leakage: features that encode the answer

A feature recorded _after_ or _because of_ the outcome: "refund issued" when predicting fraud, "account closed date" when predicting churn, "treatment given" when predicting diagnosis. CV can't catch it (it's present in every fold); only asking "would I have this value at prediction time?" does. Leaks like these are a recurring theme in data-mining competitions; Kaufman et al. survey several, including KDD Cup cases [TKDD 2012](https://doi.org/10.1145/2382577.2382579). A warning sign: a single feature with suspiciously high importance, or validation accuracy far above what domain experts manage.

Choosing features is a common way to leak: see feature selection.

## In practice

### In practice

#### Choose the splitter that matches production

| Data | Splitter | Why |
|---|---|---|
| i.i.d. rows, balanced | `KFold(shuffle=True)` | Plain rotation |
| Rare classes | `StratifiedKFold` | Each fold keeps "approximately the same percentage of samples of each target class" |
| Several rows per patient / customer / device | `GroupKFold`, `StratifiedGroupKFold` | "ensures that the same group is not represented in both testing and training sets" |
| Time-ordered data | `TimeSeriesSplit` (or a date cut-off) | Train on the past, test on the future; shuffled CV on time series gives "poor estimates of generalization error" |
| Tuning + honest estimate | Nested CV | Inner loop tunes, outer loop scores (see the Maths tab) |

Quotes from scikit-learn's cross-validation guide [docs](https://scikit-learn.org/stable/modules/cross_validation.html), which adds: "While i.i.d. data is a common assumption in machine learning theory, it rarely holds in practice."

#### The whole recipe

1. **Split first**, by the production rule (time cut-off, groups, or stratified random), and lock the test set away.

2. **Put every learned step in a Pipeline**; never call fit on validation or test rows.

3. **Cross-validate the pipeline** (5 or 10 folds, with the matching splitter) to compare models and tune.

4. **Audit features** for timing: would each one exist at prediction time?

5. **Evaluate once on the test set.** If it's much worse than CV, look for leakage before blaming overfitting.

#### Scenarios

##### "CV said 0.92 AUC, production says 0.70"

Check, in order: preprocessing fitted on all rows, groups split across folds, time order ignored, features not available at prediction time, then genuine distribution shift.

##### "Which CV for churn with monthly snapshots per customer?"

Time-based split (train on earlier months, validate on later) and keep each customer on one side, or validate on customers who signed up later.

### The answer that sounds right

#### "Prepare the data first, then cross-validate"

The most common leak looks like good hygiene: scale, impute, select features or balance classes on the full dataset, then run CV on the result. But every one of those steps learned something from the rows that will later be the validation folds. scikit-learn: "Data leakage occurs when information that would not be available at prediction time is used when building the model … The general rule is to never call `fit` on the test data" [common pitfalls](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage). How big can it get? The Leak 1 section shows a model scoring 86% on pure noise.

#### Try enough models and one will look good

Every variant is a coin-flip model (true accuracy 50%). Each dot is one variant's validation accuracy on the same 50 rows.

With 50 validation rows, a single coin-flip model already scored 58% here by luck; the best of 10 scored 62%, of 100 68%, and of 1,000 **70%**. On 10,000 fresh rows, the "winner" scores 50%: it was never better, just luckier on that sample. Hyperparameter searches, feature experiments and "let me try one more thing" all do this. scikit-learn: tuning against the test set means "knowledge about the test set can 'leak' into the model and evaluation metrics no longer report on generalization performance" [cross-validation guide](https://scikit-learn.org/stable/modules/cross_validation.html). The cure: choose on validation/CV, and report a test set used once. With small data and heavy tuning, use nested CV.

#### The same rider in train and test

40 riders × 8 trips. Each rider's trips share a personal "signature" (phone, route, riding style) but the badge is random: trip features carry no real signal about it. Strip: each square is a rider; split = trips of that rider on both sides.

Random K-fold: **92.5%**. The model just recognises the rider from their other trips in the training folds. GroupKFold: **47%**, the honest coin flip. scikit-learn's example is the same: a model "flexible enough to learn from highly person specific features … could fail to generalize to new subjects. GroupKFold makes it possible to detect this kind of overfitting" [docs](https://scikit-learn.org/stable/modules/cross_validation.html#group-k-fold). Same story for medical images (several scans per patient), sessions per user, near-duplicate documents, and augmented copies of one image.

##### Time leaks

If production predicts next week, validation must be later than training. Shuffled CV on time-ordered data tests on rows "artificially similar (close in time) to training samples" [docs](https://scikit-learn.org/stable/modules/cross_validation.html). Also watch features computed with future data: a 30-day rolling average that includes days after the prediction, "total orders this month" used on day 3, or a customer's lifetime value as of today.

#### Caveats

- CV estimates the performance of the _procedure_ (pipeline + tuning), not of one fitted model.

- Fold scores aren't independent (training sets overlap), so the fold spread understates the true uncertainty; don't over-read small differences between models.

- No splitter fixes distribution shift you didn't anticipate (a new city, a new app version). Validate on the most production-like slice you have.

- Nested CV is expensive; critics (e.g. Wainer & Cawley 2021) argue it's often overkill when comparing a few model types. Use it when tuning is heavy and data is small.

## Say it

### What is data leakage, and how does cross-validation help you avoid it?

#### The interviewer pushes further

Follow-up 1 of 5

Why not leave-one-out?

It costs n fits and its estimate has high variance, since the n models are nearly identical; 5- or 10-fold is the usual recommendation.

Follow-up 2 of 5

What is nested cross-validation and when do you need it?

An inner CV tunes hyperparameters; an outer CV scores the tuned procedure. You need it when you report a performance estimate after heavy tuning on small data; otherwise the estimate is optimistically biased.

Follow-up 3 of 5

Give examples of data leakage.

Scaling or SMOTE before splitting; feature selection on all data; target encoding without out-of-fold estimates; duplicate users/patients across folds; random splits on time series; features like "refund issued" for fraud.

Follow-up 4 of 5

How would you detect leakage?

Scores too good to be true, one dominant feature, big CV-to-production gap, performance that drops when you switch to grouped or time-based splits, and feature-timing audits.

Follow-up 5 of 5

Should you oversample before or after splitting?

After, and only on the training fold (inside the pipeline). Oversampling first puts copies or interpolations of validation rows into training.

#### The 30-second answer

Cross-validation estimates how a modelling procedure performs on unseen data by rotating held-out folds and averaging the scores, usually 5- or 10-fold, with a separate test set used once at the end. The split must mirror production: stratified for rare classes, grouped when there are several rows per entity, and time-based for temporal data. Data leakage is any information at training time that wouldn't exist at prediction time; the common forms are fitting preprocessing or feature selection on all rows, tuning on the test set, related rows on both sides of the split, and features recorded after the outcome. The fix is to put every learned step in a pipeline that's refitted inside each fold, split by the production rule, use nested CV when tuning heavily, and audit features for timing.

**Go further**

#### What not to say

- "I scaled the whole dataset, then cross-validated." That's a leak.

- "I tuned on the test set to get the best model." The test score is now optimistic.

- "Shuffled K-fold is fine for time series." It leaks the future.

**Key terms and sources**

Hold-out sets, k-fold, stratified, grouped and time-series splits, nested CV for tuning, and the leaks that make offline scores lie · built from scikit-learn's cross-validation and common-pitfalls guides, Varma & Simon (2006) and Kaufman, Rosset, Perlich & Stitelman (2012) · checked 28 Oct 2026

#### Evidence

##### Leaked vs honest scores (this page's simulations; truth is 50% in all three)

feature selection on all rows

86.5%

… inside each fold

51.0%

riders split randomly

92.5%

… grouped by rider

47.2%

Illustrative simulations with no real signal. scikit-learn's own feature-selection example: 0.76 leaked vs 0.5 honest [common pitfalls](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage).

#### Key terms

| Term | Meaning |
|---|---|
| **Hold-out / test set** | Data kept aside and used once for the final score. |
| **k-fold CV** | Rotate k validation folds; average the scores. |
| **Stratified / grouped / time-series split** | Keep class ratios / keep groups together / train on past only. |
| **Nested CV** | Inner CV for tuning inside an outer CV for scoring. |
| **Data leakage** | Training-time information unavailable at prediction time. |
| **Target leakage** | A feature recorded after, or because of, the outcome. |

#### What this page is built from

1. scikit-learn, [Cross-validation: evaluating estimator performance](https://scikit-learn.org/stable/modules/cross_validation.html) (k-fold, LOO, stratified, group, time-series splits, i.i.d. caveats, test-set leakage).

2. scikit-learn, [Common pitfalls and recommended practices](https://scikit-learn.org/stable/common_pitfalls.html) (data leakage definition, feature-selection example, pipelines).

3. S. Varma & R. Simon, "Bias in error estimation when using cross-validation for model selection", _BMC Bioinformatics_ 7:91, 2006, [doi](https://doi.org/10.1186/1471-2105-7-91) (nested CV).

4. S. Kaufman, S. Rosset, C. Perlich & O. Stitelman, "Leakage in data mining: formulation, detection, and avoidance", _ACM TKDD_ 6(4), 2012, [doi](https://doi.org/10.1145/2382577.2382579).

5. J. Wainer & G. Cawley, "Nested cross-validation when selecting classifiers is overzealous for most practical applications", _Expert Systems with Applications_, 2021 (critique; background).

All three datasets are simulated with no real signal, so the honest answer is known; every score is computed live in your browser.
