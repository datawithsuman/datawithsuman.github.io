# Missing Values & Feature Scaling

> Slow kitchens hide their prep time. Does it matter how you fill the gap, and when must you scale?

- Track: Fundamentals › Classical ML › Data and features
- Type: Concept · 30 min
- Page: https://aimlrounds.com/tracks/fundamentals/missing-values-and-scaling/
- Quiz topic: `feat`

## Intuition

### The situation

Prep time is missing for a third of your orders, and it turns out slow kitchens stop reporting it. A teammate fills every gap with the mean. The interviewer asks:

> How do you handle missing values and feature scaling?

**Running example:** the food-delivery app predicts a delivery score from two features: distance and restaurant prep time (correlated: far restaurants also tend to be slower). Prep time is missing for 28–40% of orders, under three different simulated mechanisms. Test data has the same missingness, as it would in production. A separate example uses order values in rupees, with a few huge corporate catering orders, for the scaling section.

#### Most models can't take a blank

Real tables have holes: a restaurant didn't report prep time, a customer skipped the rating, a sensor dropped out. Most scikit-learn models refuse NaN. Dropping incomplete rows throws data away and, worse, can bias the sample (the dropped rows may be systematically different). Filling them in is easy to do badly. And feature scales are a second, related trap: a column in rupees next to a column in kilometres can dominate any distance or penalty.

### The idea

Think of a form with a blank answer. You can pencil in a good guess, but the blank is a clue too: slow kitchens hide their times. So you fill the gap and keep a note that it was blank.

[Figure: A row with a blank prep time becomes a row with a guessed prep time and a new column flagging that it was missing.]

_Illustrative. This is imputation plus a missing indicator._

### Play

**Try to break it.** Set the reason to slow kitchens hiding it (MNAR), and try mean fill. Then add the indicator, and try regression fill.

#### Which fill works under which mechanism?

Linear regression, 2,000 training and 10,000 test orders. Teal: observed prep times; orange: imputed ones (for training rows). Under MNAR, the orange points sit where the hidden slow kitchens are not.

| Mechanism | mean | mean + indicator | regression | regression + indicator |
|---|---|---|---|---|
| MCAR (28% missing) | 1.814 | 1.812 | 1.653 | 1.652 |
| MAR (37%) | 1.954 | 1.915 | 1.797 | 1.799 |
| MNAR (40%) | 2.271 | 1.663 | 2.067 | 1.588 |

Test RMSE (lower is better; 1.00 if nothing were missing). Regression imputation wins whenever prep time can be predicted from distance. The indicator does nothing under MCAR (missingness carries no information) but cuts the error from 2.27 to 1.66 under MNAR, because "prep time not reported" now tells the model "probably a slow kitchen".

**Now say why:** why does the indicator help more here than a smarter guess?

## How it works

### How it works

#### In one breath

Before choosing how to fill a gap, ask **why it's missing**. If values are missing at random, a simple fill loses little; if missingness depends on the missing value itself ("customers who give bad ratings often don't rate"), the fact that it's missing is **information**, so add a **missing indicator** column. Model-based imputation (predict the missing feature from the others) beats the mean when features are correlated. Gradient-boosted trees can take NaN directly. **Scaling** matters for anything distance- or penalty-based (k-NN, SVM, k-means, PCA, regularised linear models, neural nets) and not for trees; with outliers, use a robust or quantile scaler. Both steps are learned from data, so both go **inside the pipeline**. What you'll be able to do after this: name the three missingness mechanisms with examples, pick an imputer and justify an indicator column, choose a scaler for skewed data with outliers, and say which models don't care.

#### Three reasons a value goes missing

| Mechanism | Missingness depends on | Delivery example |
|---|---|---|
| **MCAR**: missing completely at random | Nothing (pure chance) | A logging bug drops prep time for random orders |
| **MAR**: missing at random | Other observed features | Far-away restaurants (known distance) use an old app that doesn't report prep time |
| **MNAR**: missing not at random | The missing value itself | Slow kitchens stop reporting prep time because it looks bad |

Terminology from Rubin (1976) and Little & Rubin, _Statistical Analysis with Missing Data_. You usually can't prove which mechanism holds from the data alone; domain knowledge decides.

#### Impute the value, and keep the fact that it was missing

For prediction (not for estimating population averages), you don't need the "true" missing value; you need features that let the model predict well. Two things help: a good guess for the value (use correlated features), and an **indicator** saying the value was guessed, which lets the model learn that "missing" itself means something. Statistics textbooks often warn against indicators because they bias coefficient estimates; for predictive accuracy under MNAR they're one of the most effective tricks.

#### Who needs scaling, and which scaler

scikit-learn: "many elements used in the objective function of a learning algorithm (such as the RBF kernel of Support Vector Machines or the l1 and l2 regularizers of linear models) may assume that all features are centered around zero or have variance in the same order. If a feature has a variance that is orders of magnitude larger than others, it might dominate the objective function" [preprocessing guide](https://scikit-learn.org/stable/modules/preprocessing.html).

##### Needs scaling

- k-NN, k-means, DBSCAN (distances)

- SVMs with RBF kernels

- PCA (variance)

- Ridge, lasso, regularised logistic regression (penalty treats all weights alike)

- Neural networks (optimisation)

##### Doesn't care

- Decision trees, random forests, gradient-boosted trees (threshold splits are unchanged by monotone rescaling)

- Naive Bayes (per-feature distributions)

- Unregularised linear regression (predictions; coefficients rescale)

1,000 order values: 990 everyday orders (median ₹401) and 10 corporate catering orders of ₹20,000–50,000.

Ten catering orders inflate the mean to ₹832 and the standard deviation to ₹3,860, so **StandardScaler** squeezes all everyday orders into −0.20 to 0.30, and **MinMaxScaler** into 0 to 0.04: the model can barely tell a ₹150 order from a ₹1,000 one. **RobustScaler** uses the median and interquartile range (₹309), so everyday orders spread over −1.1 to 5.2 and the catering orders sit far out (around 80), still extreme but no longer squashing everyone else. scikit-learn: "If your data contains many outliers, scaling using the mean and variance of the data is likely to not work very well" [docs](https://scikit-learn.org/stable/modules/preprocessing.html). A **quantile** transform maps values to ranks, removing the outlier effect entirely, at the cost of distorting distances. For skewed money values, a log transform before scaling is often the simplest fix.

## In practice

### In practice

#### The imputation toolbox

| Method | What it does | scikit-learn |
|---|---|---|
| Drop rows / columns | Only if few rows are affected and missingness is MCAR, or a column is mostly empty | pandas `dropna` |
| Simple fill | "a provided constant value, or … mean, median or most frequent" | `SimpleImputer` |
| Missing indicator | Extra 0/1 column: "preserving the information about which values had been missing can be informative" | `add_indicator=True`, `MissingIndicator` |
| k-NN imputation | Average of the nearest complete rows | `KNNImputer` |
| Model-based (round-robin) | "models each feature with missing values as a function of other features" (still experimental) | `IterativeImputer` |
| Native NaN support | Trees learn which branch missing values take | `HistGradientBoosting*`, XGBoost, LightGBM |

Quotes from scikit-learn's imputation guide [docs](https://scikit-learn.org/stable/modules/impute.html).

#### Fit on training data, in the right order

- **Fit imputers and scalers on training folds only.** A mean or median computed on all rows leaks test information (see Cross-Validation & Leakage). scikit-learn's pitfall example: forgetting to apply the train-fitted scaler to the test set gave a test MSE of 62.8 instead of 0.90 [common pitfalls](https://scikit-learn.org/stable/common_pitfalls.html).

- **Order:** impute, then scale, so the scaler sees the final values; encode categorical columns in their own branch of a `ColumnTransformer`.

- **Same transform in production:** save the fitted pipeline, not just the model. Recomputing means on live data silently shifts every feature.

- **Placeholder values:** "−1" or "999" for missing look like real numbers to a linear model; convert them to NaN first.

#### The whole recipe

1. **Profile missingness:** share per column, and whether it correlates with other features or the target.

2. **Decide the mechanism** with domain knowledge; if it might be MNAR, add indicators.

3. **Pick an imputer:** median for robustness, iterative/KNN when features are correlated, or let gradient-boosted trees handle NaN.

4. **Pick a scaler** if the model needs one: standard by default, robust or log + standard with outliers, quantile for heavy tails.

5. **Wrap it all in a Pipeline** and cross-validate the whole thing.

#### Scenarios

##### "Income is missing for 30% of loan applicants"

Likely MNAR (people with unusual incomes skip it): median or model-based fill plus an indicator; check whether the indicator is predictive; consider gradient boosting with native NaN handling.

##### "Our k-NN recommender ignores rating counts"

Unscaled features: popularity counts in thousands dwarf 1–5 ratings. Log-transform counts and standardise everything.

Next: feature engineering.

### The answer that sounds right

#### "Fill with the mean and move on"

Mean imputation keeps every row, but it puts all the missing orders at one prep-time value, flattening the relationship with the target. Under MNAR it's worse: if slow kitchens hide their prep time, the observed mean is too low, and every slow kitchen gets imputed as average. In our simulation the observed mean prep time is 0.05 under MCAR but −0.48 under MNAR (true mean 0): the visible data is already biased before you fill anything.

#### Caveats

- Single imputation makes the filled values look more certain than they are; if you need valid confidence intervals (inference, not prediction), use multiple imputation.

- Indicators double the feature count for many sparse columns; add them where missingness is common or plausibly informative.

- If missingness changes in production (a new app version starts reporting prep time), models that learned "missing = slow" break. Monitor missing rates.

- `IterativeImputer` is still marked experimental in scikit-learn.

## Say it

### How do you handle missing values and feature scaling?

#### The interviewer pushes further

Follow-up 1 of 4

Mean or median imputation?

Median for skewed data or outliers; mean when roughly symmetric. Both shrink variance and ignore correlations, so prefer model-based fills when other features predict the missing one.

Follow-up 2 of 4

Why add a missing indicator?

So the model can learn that missingness itself predicts the target (MNAR or informative missingness), and so imputed values aren't mistaken for real ones.

Follow-up 3 of 4

Standardisation vs min-max?

Standardisation centres and scales by sd, good default; min-max maps to [0,1], useful for bounded inputs but very sensitive to outliers; robust scaling uses median/IQR.

Follow-up 4 of 4

Do tree models need scaling or imputation?

No scaling. Imputation depends on the library: modern gradient boosting handles NaN natively; classic scikit-learn random forests historically needed imputation (recent versions accept NaN in some estimators).

#### The 30-second answer

First I'd ask why values are missing: completely at random, at random given other features, or not at random, where missingness depends on the value itself. For prediction, I'd impute with the median or a model-based imputer that uses correlated features, and add a missing indicator when missingness might be informative; under MNAR the indicator often matters more than the fill. Gradient-boosted trees can handle NaN natively. For scaling, distance- and penalty-based models such as k-NN, SVMs, k-means, PCA, regularised linear models and neural networks need it; trees don't. With outliers I'd use a log transform or a robust scaler instead of standardisation. Imputers and scalers are fitted on training data only, inside the pipeline.

**Go further**

#### What not to say

- "I drop rows with missing values." Only if few and MCAR.

- "I scale using the whole dataset's mean." That leaks test data.

- "Trees need standardised features." They don't.

**Key terms and sources**

Why values go missing (MCAR, MAR, MNAR), dropping vs imputing, missing-value indicators, model-based imputation, and when and how to scale (standard, min-max, robust, quantile) · built from scikit-learn's imputation and preprocessing guides, Rubin (1976) and Little & Rubin · checked 28 Oct 2026

#### Evidence

##### MNAR prep time: test RMSE by method (this page's simulation)

mean fill

2.27

regression fill

2.07

mean + indicator

1.66

regression + indicator

1.59

nothing missing

1.00

Lower is better. Illustrative.

#### Key terms

| Term | Meaning |
|---|---|
| **MCAR / MAR / MNAR** | Missing by chance / because of observed data / because of the missing value itself. |
| **Imputation** | Filling missing values with estimates. |
| **Missing indicator** | 0/1 column recording that a value was missing. |
| **Standardisation** | (x − mean) / sd. |
| **Robust scaling** | (x − median) / IQR. |
| **Quantile transform** | Map values to ranks, then to a target distribution. |

#### What this page is built from

1. scikit-learn, [Imputation of missing values](https://scikit-learn.org/stable/modules/impute.html) (SimpleImputer, IterativeImputer, KNNImputer, MissingIndicator, native NaN support).

2. scikit-learn, [Preprocessing data](https://scikit-learn.org/stable/modules/preprocessing.html) (scalers, outliers, quantile and power transforms).

3. scikit-learn, [Common pitfalls](https://scikit-learn.org/stable/common_pitfalls.html) (inconsistent preprocessing).

4. D. Rubin, "Inference and missing data", _Biometrika_ 63, 1976; R. Little & D. Rubin, _Statistical Analysis with Missing Data_, 3rd ed., Wiley 2019 (MCAR/MAR/MNAR; background).

Data simulated with fixed seeds; every model is fitted live in your browser.
