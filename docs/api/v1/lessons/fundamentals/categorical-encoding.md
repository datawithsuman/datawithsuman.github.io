# Encoding Categorical Features

> 400 pincodes and a 'late order' flag: how do you encode them without leaking the answer?

- Track: Fundamentals › Classical ML › Data and features
- Type: Concept · 30 min
- Page: https://aimlrounds.com/tracks/fundamentals/categorical-encoding/
- Quiz topic: `feat`

## Intuition

### The situation

Your model has a pincode column with 400 values. One-hot means 400 sparse columns, and replacing each pincode with its average late rate looks great in training but falls apart in test. The interviewer asks:

> How would you encode a categorical feature with 400 values?

**Running example:** the food-delivery app predicts two things from order data (simulated): **delivery delay** in minutes from the restaurant's cuisine (6 categories) and the distance; and whether an order will be **late** (about 25% are) from the delivery **pincode** (400 pincodes, about 7 training orders each) and the distance. Each pincode has a small real effect on lateness, so there's some genuine signal to find, and plenty of noise to fool a careless encoder.

#### Labels aren't numbers

A linear model multiplies each input by a weight; a distance-based model subtracts inputs. Neither can do anything with "Chinese" or "560034". Every categorical column needs an encoding, and the choice quietly decides what the model can learn: whether categories get an artificial order, how many columns you create, and whether target information leaks into the features.

### The idea

Think of replacing each pincode with its track record. A record from three orders means little, so you pull it towards the overall average. And a record that includes the very order you're predicting gives away the answer, so you compute it from other orders.

[Figure: A scale of late rate. A pincode with 2 late orders out of 3 has a raw rate of 67 percent. Shrunk towards the 25 percent global rate, it becomes 30 percent.]

_Worked from the lesson's example of 2 late orders out of 3, with smoothing m = 20._

### Play

**Try to break it.** Choose naive encoding with low smoothing and read the test log loss. Then switch to cross-fitted.

#### Naive vs cross-fitted target encoding

Logistic regression on [encoded pincode (as log-odds), distance], 3,000 training orders, 20,000 test orders. Plot: training rows' encoded value vs their label (jittered): with naive encoding, late rows (top) sit visibly further right because their own label is inside their feature.

Naive encoding makes the model **worse than ignoring pincode altogether**: test log loss 0.58–0.63 (depending on m) against 0.539 for distance alone, and AUC 0.63–0.65 against 0.683. The model gave the encoded column a large weight because, on the training rows, it partly contained the answer. Cross-fitted encoding gets a small, honest weight and slightly beats the baseline: log loss **0.536**, AUC **0.689**, close to what the weak true pincode signal allows. Smoothing helps the naive version a little but doesn't cure it; cross-fitting does.

**Now say why:** why does the naive version look so useful to the model, yet do worse than ignoring pincode altogether?

## Maths

### Maths

#### In one breath

Models need numbers, but "cuisine" and "pincode" are labels. **One-hot** encoding gives each category its own 0/1 column: safe, no fake order, but it explodes with thousands of categories. **Ordinal** encoding (1, 2, 3…) is compact but tells a linear model that "Biryani" is 4× "Chinese", so use it only for truly ordered categories or for tree models. **Target encoding** replaces each category with the average target for that category; it handles thousands of pincodes in one column, but it is a leak waiting to happen: compute it with **cross-fitting** (out-of-fold) and **smoothing** towards the global mean, or the model learns noise. Plan for categories you've never seen. What you'll be able to do after this: choose an encoder for a column by its cardinality and the model, explain why naive target encoding overfits, write the smoothing formula, and handle unseen and rare categories.

#### Three basic encoders

1. A categorical column: each order has a cuisine.

2. **One-hot:** one 0/1 column per category. No order is implied, and a linear model gets a separate weight for each cuisine. (Drop one column when the model has an intercept, to avoid perfect collinearity.)

3. **Ordinal:** one integer per category. Compact, but a linear or distance-based model treats the integers as quantities with an order and spacing that aren't real. scikit-learn: estimators "would interpret the categories as being ordered, which is often not desired".

4. **Target encoding:** replace each category with the average target (here, average delay) for that category. One column regardless of cardinality, and it carries exactly the information the model wants, which is also why it can leak.

Quote from scikit-learn's preprocessing guide [docs](https://scikit-learn.org/stable/modules/preprocessing.html#encoding-categorical-features).

#### Target encoding, done safely

For 400 pincodes, one-hot means 400 sparse columns with ~7 examples each. Target encoding compresses each pincode to one number: its late rate. But a pincode with 3 orders, 2 of them late, gets 0.67, mostly noise. The fix is **shrinkage** towards the global rate:

$$ {S_i} = {\lambda_i}\,{\tfrac{n_{iY}}{n_i}} + (1 - {\lambda_i})\,{\tfrac{n_Y}{n}}, \qquad {\lambda_i} = \tfrac{n_i}{{m} + n_i} $$

scikit-learn's `TargetEncoder` formula for binary targets [docs](https://scikit-learn.org/stable/modules/preprocessing.html#target-encoder); the blending idea is from Micci-Barreca (2001).

- **encoded value**: The number that replaces pincode i.

- **trust in the category**: λ_i = n_i / (m + n_i): close to 1 for pincodes with many orders, close to 0 for rare ones.

- **category’s own rate**: Late orders in pincode i divided by its orders.

- **global rate**: The overall late rate, the safe fallback; unseen pincodes get exactly this.

- **smoothing strength**: m acts like m imaginary orders at the global rate. scikit-learn’s smooth='auto' sets it from the within- and between-category variance (empirical Bayes).

Shrinkage alone is not enough. If a training row's own label is part of its pincode's average, the feature contains that row's answer. The model learns to trust the feature far too much, and the trust doesn't transfer to new orders. **Cross-fitting** fixes this: split training data into k folds and encode each fold with statistics computed from the other k − 1. scikit-learn's `fit_transform` does exactly this, which is why "`fit(X, y).transform(X)` does not equal `fit_transform(X, y)`" and why "training data should always be trained and transformed with `fit_transform(X_train, y_train)`" [docs](https://scikit-learn.org/stable/modules/preprocessing.html#target-encoder).

## In practice

### In practice

#### Pick by cardinality and model

| Situation | Encoder |
|---|---|
| Few categories (< ~15), any model | One-hot (`OneHotEncoder(handle_unknown="infrequent_if_exist")`) |
| Truly ordered (S/M/L, rating bands) | Ordinal with the real order |
| Tree ensembles | Native categorical support, or ordinal codes |
| Many categories (pincodes, restaurant IDs) + linear/NN | Target encoding (cross-fitted, smoothed), or learned embeddings |
| Huge or open-ended vocabularies (user agents, search terms) | Feature hashing; frequency encoding |
| Rare categories | Group into "other" (`min_frequency`, `max_categories`) |

A benchmark of encoders across 24 datasets (Pargent, Pfisterer, Thomas & Bischl, _Computational Statistics_, 2022) found that regularised target encoding (with 5-fold cross-fitting) "consistently provided the best results" across lasso, random forests, boosting, k-NN and SVMs; traditional encodings could compete only on datasets with fewer levels, and integer encoding did poorly even with gradient boosting. [arXiv:2104.00629](https://arxiv.org/abs/2104.00629)

#### New, rare and missing categories

- **Unseen at prediction time:** a new restaurant opens. One-hot with `handle_unknown="ignore"` (or `"infrequent_if_exist"`) gives an all-zero row; target encoding returns the global mean; scikit-learn's `TargetEncoder` does this automatically [docs](https://scikit-learn.org/stable/modules/preprocessing.html#target-encoder).

- **Rare categories:** group them into one "infrequent" level (`min_frequency`, `max_categories`), so the model doesn't memorise them.

- **Missing:** treat "missing" as its own category; it's often informative (chapter on missing values).

- **Drift:** category frequencies change (new pincodes as the app expands). Monitor the share of unseen categories in production.

#### Frequency, hashing and embeddings

##### Frequency / count encoding

Replace a category by how often it occurs. No target, so no target leak; useful when popularity itself matters (busy pincodes). Collisions: different categories with the same count look identical.

##### Feature hashing

Hash the category string into one of k buckets (`FeatureHasher`). Fixed memory, handles open-ended vocabularies and unseen values, but unrelated categories can collide in a bucket.

##### Learned embeddings

Neural networks learn a dense vector per category (entity embeddings). Similar restaurants end up close together. Needs a lot of data per category.

##### CatBoost's ordered target statistics

Encodes each row using only rows that come before it in a random permutation: the same goal as cross-fitting, built into the booster (see Gradient Boosting).

#### The whole recipe

1. Per column, check **cardinality**, whether it's **ordered**, and rare/unseen rates.

2. Low cardinality → one-hot; ordered → ordinal; high → cross-fitted target encoding, hashing or native categorical support.

3. Put encoders in a `ColumnTransformer` inside the `Pipeline`, so everything is refitted per CV fold.

4. Decide behaviour for **unseen** and **rare** values up front.

#### Scenarios

##### "10,000 restaurant IDs, logistic regression"

Cross-fitted, smoothed target encoding (or hashing); group restaurants with < 20 orders; unseen → global mean.

##### "Same data, LightGBM"

Use native categorical handling or ordinal codes; consider target encoding only if categories are very many and sparse.

### The answer that sounds right

#### "Just number the categories"

Linear regression on delay = distance + cuisine, 600 training orders. Bars: true extra delay per cuisine (grey) and what the model learned (coloured). Ordinal forces the learned effects onto a straight line in the arbitrary order 1–6.

With ordinal codes the model can only learn "each step up the list adds k minutes", so test error is **4.90 minutes**; with one-hot it learns each cuisine's own effect and reaches **3.06**, essentially the noise floor. Tree models are different: they split on thresholds and can carve any group out of an ordinal code with a few splits, so ordinal codes (or native categorical support, as in LightGBM, CatBoost and HistGradientBoosting) work for them when categories are few. With many categories, even gradient boosting did worse with integer codes than with regularised target encoding in a 24-dataset benchmark (Pargent et al. 2022).

#### Caveats

- One-hot with many columns is fine for linear models with regularisation and sparse matrices; the "explosion" is a memory/speed problem more than an accuracy one.

- Target encoding gives one number per category: it can't express interactions (pincode × time of day) unless you encode the combination.

- Cross-fitting makes training-time encodings slightly noisier than test-time ones (which use all training data); this mismatch is small and intended.

- Always evaluate the whole pipeline in CV; an encoder fitted outside CV leaks just like feature selection (see Cross-Validation & Leakage).

## Say it

### How would you encode a categorical feature with 400 values?

#### The interviewer pushes further

Follow-up 1 of 4

Why does naive target encoding overfit?

Each training row's label is included in its own category's mean, so the feature partly contains the answer, especially for rare categories. The model learns to over-trust it, and that trust doesn't hold on new data. Cross-fitting removes the row's own label; smoothing reduces noise for rare categories.

Follow-up 2 of 4

One-hot vs ordinal for tree models?

Trees split on thresholds, so ordinal codes work and are compact; one-hot with many categories makes each split very unbalanced and can hurt. Many libraries handle categories natively.

Follow-up 3 of 4

The dummy variable trap?

With an intercept, k one-hot columns are perfectly collinear (they sum to 1); drop one for unregularised linear models. Regularised models and trees don't care.

Follow-up 4 of 4

How do you handle a category never seen in training?

One-hot: all zeros or an "infrequent" bucket; target encoding: global mean; hashing: falls into some bucket; plus monitoring the unseen rate.

#### The 30-second answer

It depends on cardinality and the model. For a few unordered categories I'd one-hot encode, handling unknown categories. For ordered categories, ordinal encoding in the real order. Tree models can use ordinal codes or native categorical support. For high-cardinality columns with linear models or neural nets, I'd use target encoding: replace each category with its average target, shrunk towards the global mean for rare categories, and computed out-of-fold so a row's own label never enters its feature; otherwise the model overfits. Alternatives are hashing, frequency encoding or learned embeddings. Everything sits inside the pipeline so it's refitted within cross-validation.

**Go further**

#### What not to say

- "I label-encode everything." Not for linear or distance-based models.

- "Target encoding on the full dataset, then split." That leaks.

- "One-hot pincodes for a KNN." 400 sparse dimensions break distances.

**Key terms and sources**

One-hot, ordinal, target encoding (with smoothing and cross-fitting), frequency and hashing encoders, and what trees need · built from scikit-learn's preprocessing guide, Micci-Barreca (2001) and Pargent et al. (2022) · checked 28 Oct 2026

#### Evidence

##### Pincode → late order: test log loss (this page's simulation; lower is better)

naive target encoding, m = 1

0.634

naive target encoding, m = 20

0.587

distance only (ignore pincode)

0.539

cross-fitted target encoding, m = 20

0.536

Illustrative simulation: 400 pincodes, 3,000 training orders.

#### Key terms

| Term | Meaning |
|---|---|
| **Cardinality** | Number of distinct categories in a column. |
| **One-hot / dummy encoding** | One binary column per category. |
| **Ordinal encoding** | One integer per category. |
| **Target (mean) encoding** | Category → smoothed average target. |
| **Cross-fitting** | Encode each training fold with statistics from the other folds. |
| **Feature hashing** | Map categories to a fixed number of buckets by a hash. |

#### What this page is built from

1. scikit-learn, [Preprocessing: encoding categorical features](https://scikit-learn.org/stable/modules/preprocessing.html#encoding-categorical-features) (OneHotEncoder unknown/infrequent handling, OrdinalEncoder caveat, TargetEncoder formula and cross-fitting).

2. D. Micci-Barreca, "A preprocessing scheme for high-cardinality categorical attributes in classification and prediction problems", _SIGKDD Explorations_ 3(1), 2001.

3. F. Pargent, F. Pfisterer, J. Thomas & B. Bischl, "Regularized target encoding outperforms traditional methods in supervised machine learning with high cardinality features", _Computational Statistics_, 2022, [arXiv:2104.00629](https://arxiv.org/abs/2104.00629).

4. L. Prokhorenkova et al., "CatBoost: unbiased boosting with categorical features", NeurIPS 2018, [arXiv:1706.09516](https://arxiv.org/abs/1706.09516) (ordered target statistics).

Order data is simulated with fixed seeds; every model is fitted live in your browser.
