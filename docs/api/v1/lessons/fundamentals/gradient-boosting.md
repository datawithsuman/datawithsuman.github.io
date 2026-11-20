# Gradient Boosting

> How do hundreds of tiny trees, each fixing the last one's mistakes, win on tabular data?

- Track: Fundamentals › Classical ML › Tree-based models
- Type: Concept · 35 min
- Page: https://aimlrounds.com/tracks/fundamentals/gradient-boosting/
- Before this: Decision Trees (`fundamentals/decision-trees`), Random Forest (`fundamentals/random-forest`)
- Related: Design a recommendation system (`system-design/recommendation-system`)
- Quiz topic: `trees`

## Intuition

### The situation

A shallow tree misses your rush-hour delays, and a deep tree memorises noise. A teammate suggests gradient boosting. The interviewer asks:

> How does gradient boosting work, and how does it differ from a random forest?

**Running example:** predicting delivery time from distance (the same simulated data as Decision Trees): 60 training deliveries and 300 test ones, with a rush-hour bump around 6 km. A single depth-3 tree reached a test MSE of 3.16; the noise floor is about 2.25. Every boosted model here is trained live in your browser.

#### One tree is either too simple or too wobbly

A shallow tree misses detail (high **bias**); a deep tree memorises noise (high **variance**). Random Forest attacks variance by averaging many deep trees grown independently. Boosting attacks bias: it adds many **shallow** trees in sequence, each one specialising in what the current model still gets wrong.

### The idea

Think of a round of golf. Your first shot gets you near the hole, and every shot after that only has to fix what's left. Boosting works the same way: each small tree corrects the remaining errors of everything before it.

[Figure: A golf ball travels to a flag in shots that get smaller. Each shot corrects what is left from the one before.]

_Illustrative. In the model, each shot is a small tree fitted to the remaining errors._

### Play

**Try to break it.** Set the learning rate to 1.0 with depth 2, and add trees until you reach the end. Then try a learning rate of 0.1.

#### Train a boosted model live

Lower ν needs more trees but reaches a better test error; scikit-learn: "Smaller values of learning_rate require larger numbers of weak learners… Empirical evidence suggests that small values of learning_rate favor better test error" [docs](https://scikit-learn.org/stable/modules/ensemble.html). The test curve's minimum is where **early stopping** would stop.

**Now say why:** why does test error rise at full strength while training error keeps falling, and why does a smaller learning rate help?

## Maths

### Maths

#### In one breath

Gradient boosting builds a model one small tree at a time, and each new tree is trained to fix the **mistakes** of everything before it. "Mistakes" means the **negative gradient** of the loss, which for squared error is just the residual, so boosting is gradient descent in function space. A small **learning rate** (shrinkage) plus many shallow trees, stopped early on validation data, gives the strongest off-the-shelf models for tabular data. **XGBoost** added a regularised second-order objective and fast, sparsity-aware split finding; **LightGBM** added histograms, leaf-wise growth and sampling tricks for speed; **CatBoost** fixed target leakage with ordered boosting and native categorical handling. What you'll be able to do after this: explain boosting vs bagging, derive the residual-fitting update, tune learning rate vs number of trees, read XGBoost's split-gain formula, and choose between XGBoost, LightGBM and CatBoost.

#### Fit the leftovers, step by step

1. Start with the simplest possible model: predict the average delivery time for everyone. F₀ = the mean.

2. The red lines are the residuals, actual minus predicted: what the model hasn't explained yet. Mean squared error: 46.3.

3. Fit a small tree (depth 2) to the **residuals**, not the original times, and add half of it to the model (learning rate 0.5). The error drops to 15.1.

4. New residuals, smaller than before. The next tree is fitted to these.

5. Add half of tree 2: error 6.6. Keep going: each tree nibbles away at what's left. Hundreds of small corrections add up to a flexible model.

#### Gradient descent, where each step is a tree

$$ {F_m(x)} = {F_{m-1}(x)} + {\nu}\,{h_m(x)}, \qquad h_m \approx {-\,\partial L\big(y_i, F(x_i)\big)\,/\,\partial F(x_i)}\Big|_{F=F_{m-1}} $$

Friedman (2001) framed boosting as "numerical optimization in function space"; scikit-learn: "at each iteration, the estimator hm is fitted to predict the negative gradients of the samples" [scikit-learn ensemble guide](https://scikit-learn.org/stable/modules/ensemble.html).

- **the model after m trees**: A sum: the starting guess plus every tree's contribution.

- **the model so far**: Everything learned up to tree m − 1. It is frozen: earlier trees are never revisited.

- **learning rate (shrinkage)**: ν, typically 0.01–0.1. Each tree is only allowed a small step, leaving room for later trees.

- **the new tree**: A small regression tree fitted to the pseudo-residuals below.

- **pseudo-residual**: The negative gradient of the loss for each training example: which direction, and how hard, to push its prediction. For squared error it is y − F(x), the plain residual. For log-loss it is y − p.

Because only the gradient is needed, the same machinery handles any differentiable loss: squared error (regression), log-loss (classification), quantile loss (prediction intervals), Poisson (counts), and ranking losses (LambdaMART, used in search).

#### A penalty on tree complexity, and Newton steps

XGBoost adds a complexity penalty to every tree and uses both the gradient g and the second derivative h of the loss [Chen & Guestrin 2016, §2](https://arxiv.org/pdf/1603.02754#page=2):

$$ {\mathcal L} = \textstyle\sum_i {l(y_i,\hat y_i)} + \sum_k {\big(\gamma T + \tfrac12\lambda\|w\|^2\big)}, \qquad {w_j^{*} = -\,G_j \,/\, (H_j + \lambda)} $$

Eq. 2 and Eq. 5 [p. 2–3](https://arxiv.org/pdf/1603.02754#page=3), with Gj = Σ gi and Hj = Σ hi over leaf j.

- **what each tree minimises**: Training loss plus a complexity penalty for every tree.

- **the loss**: Any twice-differentiable convex loss: squared error, log-loss, …

- **tree penalty**: γ per leaf (T = number of leaves) plus an L2 penalty λ on the leaf values w. “When the regularization parameter is set to zero, the objective falls back to the traditional gradient tree boosting.”

- **best value for a leaf**: Minus the sum of gradients in the leaf divided by (sum of second derivatives + λ): a Newton step, shrunk by λ. For squared error (g = ŷ − y, h = 1) it is the mean residual, shrunk toward 0.

Plugging the best leaf values back in gives a score for any split, used to choose (and reject) splits:

$$ {\text{Gain}} = \tfrac12\Big[{\tfrac{G_L^2}{H_L+\lambda}} + {\tfrac{G_R^2}{H_R+\lambda}} - {\tfrac{(G_L+G_R)^2}{H_L+H_R+\lambda}}\Big] - {\gamma} $$

Eq. 7 [p. 3](https://arxiv.org/pdf/1603.02754#page=3).

- **split gain**: How much the regularised objective improves if we split this node.

- **left child score**: G_L² / (H_L + λ): large when the left child's gradients agree strongly.

- **right child score**: Same for the right child.

- **parent score**: What we had without splitting.

- **cost of a new leaf**: γ: if the improvement doesn't beat it, the split isn't worth making (built-in pruning).

The very first split on our deliveries, starting from F₀ = mean, with squared error (g = F₀ − y, h = 1 per delivery). λ shrinks the leaf values toward 0 (more cautious steps); γ is a minimum gain a split must clear, so large γ prunes it.

## In practice

### In practice

#### From AdaBoost to the modern libraries

| System | Year | Key idea |
|---|---|---|
| **AdaBoost** (Freund & Schapire) | 1997 | Reweight misclassified examples; exponential loss |
| **Gradient Boosting Machine** (Friedman) | 2001 | Boosting as gradient descent in function space, for any differentiable loss; shrinkage |
| **Stochastic GB** (Friedman) | 2002 | Each tree sees a random subsample of rows |
| **XGBoost** (Chen & Guestrin) | 2016 | Regularised second-order objective; sparsity-aware splits; scalable system |
| **LightGBM** (Ke et al., Microsoft) | 2017 | Histograms, leaf-wise growth, GOSS and EFB; "up to over 20 times" faster training |
| **CatBoost** (Prokhorenkova et al., Yandex) | 2018 | Ordered boosting and ordered target statistics for categorical features; symmetric trees |
| **HistGradientBoosting** (scikit-learn) | — | LightGBM-style histograms inside scikit-learn, with native missing values and categories |

#### The knobs that stop it memorising

| Knob | XGBoost / LightGBM name | Effect |
|---|---|---|
| **Learning rate** | eta / learning_rate | Smaller steps; more trees needed; usually better test error |
| **Number of trees + early stopping** | n_estimators, early_stopping_rounds | Stop when validation loss stops improving |
| **Tree size** | max_depth (XGBoost) / num_leaves (LightGBM) | Interaction order the model can capture; shallow trees (3–8) are typical |
| **Row subsampling** | subsample / bagging_fraction | Stochastic gradient boosting (Friedman 2002); "a typical value of subsample is 0.5" in scikit-learn |
| **Column subsampling** | colsample_bytree / feature_fraction | Borrowed from random forests; XGBoost users found it "prevents over-fitting even more so than the traditional row sub-sampling" [p. 3](https://arxiv.org/pdf/1603.02754#page=3) |
| **Leaf regularisation** | reg_lambda, reg_alpha, gamma / min_split_gain | Shrink leaf values; demand a minimum gain per split |
| **Minimum leaf size** | min_child_weight / min_data_in_leaf | No leaves built on a handful of points |

#### XGBoost, LightGBM and CatBoost: what's actually different

| | XGBoost | LightGBM | CatBoost |
|---|---|---|---|
| **Split finding** | Exact greedy or approximate (weighted quantile sketch); histograms too | Histogram-based | Histogram-based |
| **Tree growth** | Level-wise (depth-limited) | Leaf-wise: always split the leaf with the largest gain (deeper, lopsided trees) | Symmetric (oblivious): same split across a whole level; very fast inference |
| **Speed tricks** | Sparsity-aware splits (learns a default direction for missing values; "more than 50 times faster" on sparse data); cache-aware blocks | GOSS (keep large-gradient rows, sample the rest) and EFB (bundle mutually exclusive sparse features) | GPU training; ordered computations |
| **Categorical features** | Native support in recent versions; otherwise encode | Native (gradient-statistics based splits) | Native: ordered target statistics, plus feature combinations |
| **Signature fix** | Regularised 2nd-order objective | Training speed on big data | "Prediction shift" from target leakage → ordered boosting |

Sources: XGBoost [§3–4](https://arxiv.org/pdf/1603.02754#page=4); LightGBM abstract (GOSS, EFB, "up to over 20 times") [NeurIPS 2017](https://proceedings.neurips.cc/paper/2017/file/6449f44a102fde848669bdd9eb6b76fa-Paper.pdf); CatBoost [arXiv 1706.09516](https://arxiv.org/pdf/1706.09516).

##### CatBoost's insight: boosting leaks the target

Each residual is computed with a model that was trained on that same example, so training residuals are systematically smaller than they would be on new data. The authors call this a "prediction shift caused by a special kind of target leakage present in all currently existing implementations of gradient boosting." The same leak happens when you replace a category with the mean target of that category. Their fix computes each example's statistics only from examples that come earlier in a random ordering [CatBoost, p. 1–4](https://arxiv.org/pdf/1706.09516#page=1). With high-cardinality categories (user, ad, publisher IDs), this matters.

#### Random Forest and Gradient Boosting, side by side

| | Random Forest (bagging) | Gradient Boosting |
|---|---|---|
| Trees built | Independently, in parallel | Sequentially, each fixing the last |
| Each tree | Deep, low bias, high variance | Shallow, high bias, low variance |
| Mainly reduces | Variance (averaging) | Bias (stage-wise fitting) |
| More trees | Never hurts accuracy (just slower) | Eventually overfits; needs early stopping |
| Tuning effort | Low; good defaults | Higher (learning rate, depth, trees, regularisation) |
| Typical accuracy on tabular data | Strong | Usually the strongest |

For voting and stacking too, see ensembles.

#### AdaBoost: boost by reweighting rows

AdaBoost is the older form of boosting. Instead of fitting each tree to errors, it gives every row a weight, and trains each small tree on the weighted data. Rows it got wrong become heavier, so the next tree focuses on them.

$$ {\alpha_m} = \tfrac12 \ln\frac{1-{\epsilon_m}}{\epsilon_m}, \qquad {w_i} \leftarrow w_i\, e^{-\alpha_m y_i h_m(x_i)}, \qquad {F(x)} = \mathrm{sign}\sum_m \alpha_m h_m(x) $$

Binary AdaBoost. Libraries may scale α by a constant, and scikit-learn uses the SAMME version for several classes.

- **weighted error**: The share of weight on rows this tree got wrong.

- **the tree’s vote**: A more accurate tree gets a bigger say in the final vote.

- **new row weights**: With labels of ±1, wrong rows grow and right rows shrink. Then all weights are rescaled to sum to 1.

- **the final answer**: A weighted vote of all the trees.

**A worked example, with illustrative numbers.** If a tree's weighted error is 0.2, then α = ½ ln 4 ≈ 0.69. Wrong rows are multiplied by about 2, and right rows by about 0.5. Wrong rows held 0.2 of the weight, and now hold 0.4, while right rows fall from 0.8 to 0.4. So after rescaling, the wrong rows hold exactly half, and that tree would be no better than chance on the new weights. The next tree must find something new.

| | AdaBoost | Gradient boosting |
|---|---|---|
| Each new tree learns from | Reweighted rows | The gradient of the loss |
| Loss | Equivalent to exponential loss | Any differentiable loss |
| Label noise | Sensitive, as wrong rows keep gaining weight | Less sensitive with log-loss |
| Today | Simple baseline | The usual choice |

Sources: [scikit-learn on ensembles](https://scikit-learn.org/stable/modules/ensemble.html); the link to exponential loss is from Friedman, Hastie and Tibshirani (2000).

#### Training a gradient-boosted model

1. Pick the loss for your target (squared error, log-loss, quantile, Poisson, ranking).

2. Hold out a validation set (time-based if the data is temporal).

3. Start with learning rate 0.05–0.1, depth 4–8 (or ~31 leaves in LightGBM), subsample 0.8, colsample 0.8.

4. Set many trees (thousands) with early stopping on validation loss (e.g. 50–100 rounds of patience).

5. Tune tree size and minimum leaf size first, then regularisation; lower the learning rate at the end for a final boost.

6. Handle categories natively (CatBoost, LightGBM, HistGradientBoosting) or with leakage-safe target encoding.

7. Explain with SHAP values; check calibration if probabilities are used (boosted trees often need it).

#### Use it, or reach for something else?

##### Use gradient boosting when

- Tabular data with mixed numeric and categorical features

- You want top accuracy: churn, fraud, credit, pricing, CTR, demand, ranking

- Missing values, outliers and skewed features are common

##### Consider something else when

- Little time to tune → Random Forest

- Strictly interpretable model required → small tree or linear model

- Images, audio, free text → neural networks

- Strong trends to extrapolate → linear / time-series models

### The answer that sounds right

#### "Add each tree at full strength, as many as possible"

Adding each correction in full (learning rate 1) fixes the training data fast, too fast: within about 20 trees the model starts fitting noise, and test error rises while training error keeps falling. In the Play lab, in the Intuition tab, learning rate 1.0 with depth-2 trees reaches its best test MSE (≈ 3.1) after about 17 trees and then degrades to ≈ 4.2 by 300 trees. Boosting will always drive training error toward zero; the craft is in stopping it from memorising.

#### What to keep

- **Boosting overfits if you let it.** Unlike random forests, more trees eventually hurt; always use early stopping.

- **Sequential training** is harder to parallelise across trees (libraries parallelise within each tree).

- **No extrapolation:** like any tree model, predictions flatten outside the training range. Use linear models or feature tricks for trends (e.g. predict the change, not the level).

- **Not for raw images, audio or text**: neural networks own those; boosting shines on heterogeneous tabular features.

- **Probabilities can be miscalibrated** after heavy tuning or class weighting.

## Say it

### How does gradient boosting work, and how does it differ from a random forest?

#### The interviewer pushes further

Follow-up 1 of 5

Bagging vs boosting?

Bagging trains independent high-variance models on bootstrap samples and averages them, reducing variance; more trees never hurt. Boosting trains weak learners sequentially on the current errors, reducing bias; it can overfit, so it needs a learning rate and early stopping.

Follow-up 2 of 5

Why is it called gradient boosting?

Each stage takes a step in function space along the negative gradient of the loss with respect to the predictions; the tree approximates that gradient using the features. For squared loss the negative gradient is the residual; for log-loss it's y − p.

Follow-up 3 of 5

Learning rate vs number of trees?

They trade off: halving the learning rate roughly needs twice the trees. Smaller learning rates usually generalise better. Fix a smallish rate, use many trees and pick the count by early stopping.

Follow-up 4 of 5

What does XGBoost add over classic GBM?

An explicit regularisation term (γ per leaf, λ on leaf weights), a second-order (Newton) approximation giving closed-form leaf values and a split-gain formula, sparsity-aware handling of missing values, column subsampling, and systems work (column blocks, cache awareness, out-of-core, distributed).

Follow-up 5 of 5

LightGBM's leaf-wise growth: pros and cons?

It splits whichever leaf reduces loss most, so it reaches lower loss with fewer leaves and trains fast, but can grow deep, lopsided trees that overfit small data. Control it with num_leaves, max_depth and min_data_in_leaf.

#### The 30-second answer

Gradient boosting builds an additive model of shallow trees sequentially. Each new tree is fitted to the negative gradient of the loss at the current predictions, which for squared error is just the residuals, and is added with a small learning rate. So it's gradient descent in function space, reducing bias step by step, whereas random forests average independent deep trees to reduce variance. It overfits if you add too many trees, so you use a small learning rate, shallow trees, subsampling, regularisation and early stopping. XGBoost adds a regularised second-order objective and fast split finding, LightGBM uses histograms and leaf-wise growth for speed, and CatBoost uses ordered boosting to avoid target leakage, especially with categorical features.

**Go further**

#### What not to say

- "More trees always help." That's true for random forests, not boosting.

- "Boosting uses deep trees." Typically shallow; depth controls interaction order.

- "XGBoost is a different algorithm from gradient boosting." It's a regularised, engineered implementation of it.

**Key terms and sources**

GBM, XGBoost, LightGBM, CatBoost · built from Friedman (2001), Chen & Guestrin (2016), Ke et al. (2017), Prokhorenkova et al. (2018), Grinsztajn et al. (2022) and scikit-learn's docs · checked 28 Oct 2026

#### Why it's the tabular default

##### Competitions

Of 29 winning Kaggle solutions published in 2015, **17 used XGBoost** (8 used it alone); deep nets were second with 11. At KDD Cup 2015, "XGBoost was used by every winning team in the top-10" [Chen & Guestrin, p. 1](https://arxiv.org/pdf/1603.02754#page=1).

##### Higgs-1M, 500 trees: time per tree (s, ↓) and test AUC

XGBoost · AUC 0.8304

0.68 s

R gbm · AUC 0.6224

1.03 s

scikit-learn (2016) · AUC 0.8302

28.5 s

Table 3 [p. 8](https://arxiv.org/pdf/1603.02754#page=8). scikit-learn has since added HistGradientBoosting, which its docs describe as "orders of magnitude faster" on large data.

##### Trees vs deep learning on tabular data

On a benchmark of 45 datasets, "tree-based models remain state-of-the-art on medium-sized data (∼10K samples) even without accounting for their superior speed." Their three reasons: neural networks are biased toward overly smooth functions, they're hurt by uninformative features, and they're rotation-invariant while tabular columns have meaning [Grinsztajn et al. 2022](https://arxiv.org/pdf/2207.08815). With larger training sets (50K) the gap narrowed in their appendix.

##### Read library benchmarks carefully

CatBoost's paper reports big wins where categorical features dominate (Amazon: log-loss 0.139 vs 0.163–0.164 for LightGBM/XGBoost, +17%), but with categorical handling equalised, the raw implementations differ by about 0.2% on average [CatBoost, Tables 8–9](https://arxiv.org/pdf/1706.09516#page=21). The library matters less than features, tuning and early stopping.

#### Glossary

| Term | Meaning |
|---|---|
| **Pseudo-residual** | Negative gradient of the loss at the current prediction. |
| **Shrinkage / learning rate** | Scale each tree's contribution by ν < 1. |
| **Early stopping** | Stop adding trees when validation loss stops improving. |
| **Stochastic gradient boosting** | Fit each tree on a random subsample of rows. |
| **Leaf-wise vs level-wise** | Split the best leaf anywhere vs fill each depth level. |
| **GOSS / EFB** | LightGBM's gradient-based row sampling / sparse feature bundling. |
| **Ordered boosting** | CatBoost's leakage-free residuals and target statistics. |
| **LambdaMART** | Gradient boosting for ranking (search). |

#### What this page is built from

1. J. H. Friedman, "Greedy function approximation: a gradient boosting machine", [Annals of Statistics 29(5) (2001)](https://www.doi.org/10.1214/AOS/1013203451); "Stochastic gradient boosting", CSDA 38 (2002).

2. T. Chen & C. Guestrin, [XGBoost: A Scalable Tree Boosting System](https://arxiv.org/abs/1603.02754), KDD 2016.

3. G. Ke et al., [LightGBM: A Highly Efficient Gradient Boosting Decision Tree](https://proceedings.neurips.cc/paper/2017/file/6449f44a102fde848669bdd9eb6b76fa-Paper.pdf), NeurIPS 2017.

4. L. Prokhorenkova et al., [CatBoost: unbiased boosting with categorical features](https://arxiv.org/abs/1706.09516), NeurIPS 2018.

5. L. Grinsztajn, E. Oyallon & G. Varoquaux, [Why do tree-based models still outperform deep learning on tabular data?](https://arxiv.org/abs/2207.08815), NeurIPS 2022.

6. scikit-learn, [Ensembles: gradient boosting and HistGradientBoosting](https://scikit-learn.org/stable/modules/ensemble.html).

The delivery data is simulated; the boosted models on this page are trained live with a small implementation (squared error, CART trees fitted to residuals).
