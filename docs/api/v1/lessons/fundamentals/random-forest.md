# Random Forest

> How do many wobbly trees make one steady prediction?

- Track: Fundamentals › Classical ML › Tree-based models
- Type: Concept · 25 min
- Page: https://aimlrounds.com/tracks/fundamentals/random-forest/
- Before this: Decision Trees (`fundamentals/decision-trees`)
- Quiz topic: `trees`

## Intuition

### The situation

Your deep decision tree changes completely when a single applicant is relabelled. The interviewer asks:

> How does a random forest improve on one deep tree?

#### Eight loan applicants, four features

Everything on this page uses the same tiny dataset. A bank wants to predict whether an applicant will repay. The numbers are made up for teaching , but the labs in this lesson run real computations on them.

| # | credit score | income (k/mo) | debt ratio | years at job | repaid? |
|---|---|---|---|---|---|

One feature, credit score, separates these eight perfectly (650 and below never repaid). Remember that; it is what makes plain bagging fail, as The answer that sounds right shows.

#### One decision tree is sharp but unstable

A decision tree asks yes/no questions about features until it reaches a leaf with an answer. Grown deep, it fits its training data almost perfectly, so its bias is low. The catch is variance: scikit-learn's own docs warn that "small variations in the data might result in a completely different tree being generated" [sklearn trees](https://scikit-learn.org/stable/modules/tree.html). Watch it happen with one relabelled applicant.

1. Trained on the eight rows, the best first question is "credit ≤ 650?". It splits the data perfectly.

2. Now relabel one applicant, #6, from not repaid to repaid. Nothing else changes.

3. The tree's first question flips to a different feature entirely, "debt ratio ≤ 0.42?", because that is now the perfect split.

4. Ask both trees about a new applicant with credit 640 and a debt ratio of 0.20. They disagree.

5. That is high variance: the model's answer depends heavily on which exact rows it happened to see.

High variance means the error you see on new data is mostly noise from the particular sample, not a lack of capacity. The classic fix for variance is averaging. The rest of the page is about how to average trees so that it actually works.

### The idea

Think of asking a crowd for an estimate. A crowd only beats one person if people make different mistakes, because mistakes that differ cancel out. A forest makes its trees disagree: each one sees different rows, and each split sees only a few features.

[Figure: Three different trees built from different rows and features. Two vote yes and one votes no, and the forest's combined answer is yes.]

_Illustrative. Different rows and features make the trees disagree, and the combined answer is steadier._

### Play

**Try to break it.** Set the correlation between trees to 0.9 and add as many trees as you can. Then lower the correlation.

#### Averaging only cancels mistakes that differ

Here is the one equation the whole method follows from. Average B trees whose predictions each have variance σ² and are correlated with each other by ρ [ESL Eq. 15.1, p. 588](https://hastie.su.domains/ElemStatLearn/):

$$ {\mathrm{Var}\big(\bar f\,\big)} = {{\rho}\,\sigma^{2}} + {\frac{1-\rho}{B}\,\sigma^{2}} $$

Hastie, Tibshirani & Friedman, _Elements of Statistical Learning_, §15.2 · hover any symbol for its meaning.

- **error from wobble**: The variance of the averaged prediction: how much the forest’s answer would wobble if you redrew the training data. This is the part averaging can shrink.

- **the floor**: ρσ² does not depend on B. However many trees you add, this part stays. If the trees are perfectly correlated (ρ = 1), averaging gives exactly one tree’s variance.

- **shrinks with trees**: (1 − ρ)σ²/B goes to zero as B grows. This is the only part that more trees can remove.

- **correlation**: So the lever is ρ. Lower the correlation between trees and the floor drops. That is the entire reason random forests add randomness.

Set ρ to 0.9 (very similar trees, like plain bagging with one dominant feature) and B to 500: the variance only drops to about 0.9. Set ρ to 0.3: it drops to about 0.3. The forest's job is to **lower ρ without making each tree much worse**. Breiman calls these two quantities the correlation and the strength of the trees, and the random-features section shows his bound with both.

Why only variance? Bagged trees are identically distributed, so the average has the same bias as one tree. ESL: "the only hope of improvement is through variance reduction" ESL p. 588. That is also why forests use deep, low-bias trees.

**Now say why:** why can't more trees fix high correlation, and what does a forest do to lower it?

## Maths

### Maths

#### In one breath

A single decision tree is accurate on the data it saw but changes wildly when the data changes a little. A random forest grows hundreds of trees, each on a bootstrap sample of the rows and each choosing every split from a random handful of features, then lets them vote. The randomness makes the trees disagree, and averaging trees that disagree cancels their mistakes. After this you can derive why it works (the variance formula), explain every knob (n_estimators, max_features, bootstrap, oob_score), and answer the usual interview follow-ups.

#### Gini impurity: how mixed is a group?

At each node, a tree (CART, which scikit-learn implements) tries every feature and every threshold, and keeps the split whose two children are the least mixed. Mixedness is measured with Gini impurity: 0 when a group is all one class, 0.5 when two classes are 50/50 [sklearn §1.10.7](https://scikit-learn.org/stable/modules/tree.html#classification-criteria).

$$ {G(\theta)} = {\tfrac{n_{L}}{n}}\,{H(L)} + {\tfrac{n_{R}}{n}}\,H(R),\qquad {H(Q)=\sum_k p_k\,(1-p_k)} $$

scikit-learn's mathematical formulation for classification trees [sklearn §1.10.7](https://scikit-learn.org/stable/modules/tree.html#mathematical-formulation) · hover any symbol for its meaning.

- **split score**: G is the score of one candidate split: lower is better. The tree computes it for every feature and threshold and keeps the minimum.

- **share going left**: The fraction of the node’s rows that answer yes and go to the left child.

- **left impurity**: How mixed the left child is. Each child is weighted by its size, so a tiny pure child does not count as much as a big one.

- **share going right**: The same for the right child. The two weights add up to 1.

- **Gini of a group**: For one group: add up p(1 − p) over the classes, where p is the share of each class. All one class gives 0; half and half gives 0.25 + 0.25 = 0.5.

##### Try it on the eight applicants

Try every feature: only credit score reaches 0. A greedy tree will always take it first, and that is about to matter.

#### Every tree trains on a resampled copy of the data

1. Start with the N = 8 training rows.

2. Draw 8 rows at random, putting each one back before the next draw. scikit-learn does exactly this with `randint(0, n, n)` [_forest.py](https://github.com/scikit-learn/scikit-learn/blob/main/sklearn/ensemble/_forest.py).

3. Some rows get picked twice or more, so this tree effectively weights them more.

4. Some rows are never picked. They are "out of bag" for this tree, which gives a free test set (see the out-of-bag section).

How many rows does a tree miss? Each draw misses a given row with probability 1 − 1/N, and there are N independent draws:

$$ {P(\text{row never drawn})} = {\Big(1-\frac{1}{N}\Big)}^{{N}} \;\longrightarrow\; {e^{-1}\approx 0.368} $$

Standard bootstrap result; Breiman: "about one-third of the instances are left out" [Breiman 2001, p. 8](https://www.stat.berkeley.edu/~breiman/randomforest2001.pdf#page=8).

- **chance a row is left out**: The probability that one particular row never appears in the bootstrap sample.

- **miss once**: On a single draw, N rows are equally likely, so this row is missed with probability 1 − 1/N.

- **N draws**: The N draws are independent, so the misses multiply: raise it to the power N.

- **about 36.8%**: As N grows this tends to 1/e ≈ 0.368. So each tree sees about 63.2% of the distinct rows, and about a third are out of bag, exactly Breiman’s “about one-third”.

##### Why keep bootstrapping once features are random?

Breiman gives two reasons: bagging "seems to enhance accuracy when random features are used", and the left-out rows give running estimates of error, strength and correlation [p. 8](https://www.stat.berkeley.edu/~breiman/randomforest2001.pdf#page=8). scikit-learn: `bootstrap=True` by default; turn it off and every tree sees all rows (as Extra-Trees do).

#### Hide the star feature sometimes

This is the move that turns bagging into a random forest. Before each split, the tree may only look at m features drawn at random from all p. It picks the best split among those m, and the next node draws a fresh m [ESL Alg. 15.1](https://hastie.su.domains/ElemStatLearn/).

1. At the root, the tree could consider all four features, and credit score would win every time.

2. Instead, draw m of them at random. Here m = 2, and credit score is not among them.

3. The node splits on the best of what it was offered. It is a weaker split than credit score, on purpose.

4. Every child node draws its own fresh m. Credit score will still be used, just not always first, and not always in the same place.

5. That forced variety is what lowers the correlation ρ between trees.

##### Check it: grow 60 trees with m features per split

Same experiment as the bagging lab in The answer that sounds right, but now you choose m. With m = 4 it is plain bagging. Watch the first-split feature spread out as m drops.

##### The trade-off, in Breiman's own bound

Lower m means less correlated trees, but each tree is also a bit weaker. The authors put it plainly: "Reducing m reduces both the correlation and the strength" [Breiman & Cutler](https://www.stat.berkeley.edu/~breiman/RandomForests/cc_home.htm). Breiman's Theorem 2.3 bounds the forest's error with exactly these two numbers:

$$ {PE^{*}} \;\le\; {\frac{{\bar\rho}\,\big(1-{s}^{2}\big)}{{s}^{2}}} $$

Breiman 2001, Theorem 2.3 [p. 6](https://www.stat.berkeley.edu/~breiman/randomforest2001.pdf#page=6). He adds that the bound "is likely to be loose".

- **forest error**: PE* is the forest’s generalization error: the chance it misclassifies a new example.

- **mean correlation**: ρ̄ is the average correlation between trees (of their margins). Random features push this down.

- **strength**: s is the strength: on average, how much more often the trees vote for the right class than for the best wrong class. Stronger trees push the bound down.

- **the c/s² ratio**: Breiman’s summary: the ratio correlation / strength² should be small. The bound is loose, but it says what to aim for.

##### What m to use

| Source | Classification | Regression |
|---|---|---|
| Inventors' recommendation (via ESL) | ⌊√p⌋, min node size 1 | ⌊p/3⌋, min node size 5 |
| scikit-learn default | "sqrt" | 1.0 = all features (plain bagging) |
| Breiman's 2001 experiments | m = 1 and m = ⌊log₂p + 1⌋, picked by out-of-bag error | |

Sources: ESL §15.3, p. 592; [sklearn ensembles](https://scikit-learn.org/stable/modules/ensemble.html#random-forests), which also notes 0.3 "is a typical default in the literature" for regression; Breiman p. 9.

##### It is not very sensitive to m

Across Breiman's 20 datasets, the average absolute difference in test error between m = 1 and the larger m was under 1%. "It was surprising that using a single randomly chosen input variable to split on at each node could produce good accuracy" [p. 11](https://www.stat.berkeley.edu/~breiman/randomforest2001.pdf#page=11). ESL adds that the best m is problem-dependent and worth tuning (their Figure 15.3: m = 6 beats the default 2).

##### What breaks without it

Set m = p and you are back to bagging: scikit-learn calls `max_features=1.0` "equivalent to bagged trees". On data with one dominant feature, like ours, the trees stay correlated and the variance floor ρσ² stays high.

#### Vote, or average the probabilities

For regression the forest averages the trees' numbers. For classification the original paper lets each tree cast one vote [Def. 1.1, p. 2](https://www.stat.berkeley.edu/~breiman/randomforest2001.pdf#page=2).

$$ {\hat f^{\,B}_{\mathrm{rf}}(x)} = {\frac{1}{B}\sum_{b=1}^{B}}\,{T(x;\,{\Theta_b})} $$

ESL Eq. 15.2, p. 589 · hover any symbol for its meaning.

- **forest prediction**: The random forest’s prediction at input x, using B trees.

- **average over trees**: Add up the B trees’ outputs and divide by B. Every tree counts equally; no tree is trusted more than another.

- **one tree**: T(x; Θ_b) is tree number b’s output for x.

- **its randomness**: Θ_b holds everything random about tree b: which rows it drew and which features each split was offered.

Here is a detail many explanations miss: **scikit-learn does not take a majority vote.** Its classifier averages each tree's predicted class probabilities ("in contrast to the original publication") [sklearn ensembles](https://scikit-learn.org/stable/modules/ensemble.html#random-forests); the code divides the summed `predict_proba` by the number of trees [_forest.py](https://github.com/scikit-learn/scikit-learn/blob/main/sklearn/ensemble/_forest.py). Usually they agree. Not always:

##### Do more trees overfit?

No. Breiman's Theorem 1.2: as trees are added the error converges to a limit, "this result explains why random forests do not overfit as more trees are added" [p. 4](https://www.stat.berkeley.edu/~breiman/randomforest2001.pdf#page=4). More trees only cost time.

##### But the forest itself can still overfit

ESL is careful here: adding trees does not overfit, but the limit, an average of fully grown trees, "can overfit the data" and "incur unnecessary variance"; controlling depth gives small gains in some studies, though full trees "seldom cost much" ESL §15.3.4, p. 596. The authors' site says "Random forests does not overfit" [Breiman & Cutler](https://www.stat.berkeley.edu/~breiman/RandomForests/cc_home.htm). Both are right about different things: B does not overfit; depth and leaf size can.

#### Every row is a test row for about a third of the trees

1. Take one training row, applicant #2.

2. Look at the forest. Each tree trained on its own bootstrap sample, so some trees saw #2 and some did not.

3. Let only the trees that never saw #2 predict it. For them, #2 is genuinely new data.

4. Do this for every row and compare with the truth. That error rate is the out-of-bag (OOB) error, a test-set estimate without holding any data back.

Breiman cites evidence that the OOB estimate "is as accurate as using a test set of the same size as the training set", and notes it is unbiased once you run past the point where the error has converged [p. 8](https://www.stat.berkeley.edu/~breiman/randomforest2001.pdf#page=8). ESL: almost identical to N-fold cross-validation, so you can stop adding trees once OOB error stabilizes ESL §15.3.1, p. 592. In scikit-learn: `oob_score=True`, available only with `bootstrap=True`.

#### Shuffle a column and see how much worse it gets

1. Measure the fitted forest's error on rows it did not train on (out-of-bag or a validation set).

2. Randomly shuffle one feature's column. This breaks its link to the label but keeps its distribution.

3. If error jumps, the model leaned on that feature. The numbers here are illustrative.

4. If error barely moves, the model did not need it. Repeat for every feature.

$$ {i_j} = {s} - {\frac{1}{K}\sum_{k=1}^{K} s_{k,j}} $$

[sklearn permutation importance](https://scikit-learn.org/stable/modules/permutation_importance.html); Breiman's original version permutes each variable in the out-of-bag rows [p. 19](https://www.stat.berkeley.edu/~breiman/randomforest2001.pdf#page=19).

- **importance of feature j**: How much the score drops when feature j is scrambled.

- **original score**: The model’s score on the data with nothing shuffled.

- **average over K shuffles**: Shuffle column j K times (scikit-learn’s n_repeats) and average the scores, so one lucky shuffle does not decide.

| | Impurity importance (MDI) · `feature_importances_` | Permutation importance |
|---|---|---|
| Computed from | how much each feature's splits reduced Gini, on the training data | score drop when the feature is shuffled, on held-out data |
| Speed | free, already computed | needs extra predictions (K × features) |
| Known bias | favours features with many unique values; can rank useless features high when the model overfits | correlated features share the credit, so both can look unimportant |

##### Do not trust the default bar chart blindly

scikit-learn: impurity-based importances "favor high cardinality features" and are computed on training data, so they "do not necessarily inform us on which features are most important" for new data [sklearn](https://scikit-learn.org/stable/modules/ensemble.html#feature-importance-evaluation). Strobl et al. (2007) showed the measures are unreliable when predictors differ in scale or number of categories, and a 2008 follow-up found bias toward correlated predictors [Strobl 2007](https://bmcbioinformatics.biomedcentral.com/articles/10.1186/1471-2105-8-25). For correlated features, scikit-learn suggests clustering them and keeping one per cluster.

To explain a model properly, see SHAP, permutation importance and partial dependence. To compare combination methods, see ensembles.

## In practice

### In practice

#### Everything in one picture

1. Start with N training rows and p features.

2. Make B bootstrap samples, one per tree.

3. Grow each tree to full depth on its sample, offering only m random features at every split. Trees are independent, so they train in parallel (`n_jobs`).

4. To predict, run the input down every tree and combine: vote (paper) or average probabilities (scikit-learn); average for regression.

5. The rows each tree left out give the OOB error and permutation importances for free.

6. That is the whole method. Every piece exists to keep the trees strong but decorrelated.

#### When to use it

**Reach for it** as a strong, low-effort baseline on tabular data, when you want a built-in validation score (OOB), robustness to label noise, and trivial parallelism. **Look elsewhere** when the last point of accuracy matters (try gradient boosting), when you must extrapolate beyond the training range, or when the data are images, text or audio.

### The answer that sounds right

#### Just average many trees? They come out the same

Idea one: train 100 trees and average them. On the same data, a tree-growing algorithm with no randomness builds the same tree 100 times. The average of 100 identical answers is that answer.

Idea two, bagging (Breiman, 1996): give each tree a different bootstrap sample, the rows drawn at random with replacement [Breiman 1996](https://statistics.berkeley.edu/node/1781). Better, but there is a trap. When one feature is much stronger than the rest, most samples still split on it first, so the trees stay similar.

1. Bootstrap sample 1 repeats row 1 and leaves out row 3. Its best first split is still credit score.

2. Sample 2 is different again. The threshold moves a little, from 670 to 655, but the question is the same.

3. Sample 3: same story. Credit score separates any sample of these rows perfectly, so it usually wins. Only now and then does a sample happen to let another feature tie.

4. The trees make the same mistakes on the same applicants. Averaging only helps when their mistakes differ.

##### Check it yourself: grow 60 bagged trees

This grows 60 one-split trees, each on its own bootstrap sample, letting every split consider all four features (that is plain bagging). It counts which feature each tree splits on first.

#### The lesson, and where it bends

**The lesson.** Averaging reduces variance only as far as the averaged models disagree. A random forest is a recipe for cheap disagreement: random rows per tree, random features per split, deep trees that are individually low-bias. Everything else (OOB error, importance, parallelism) falls out of that design.

- **It does not reduce bias.** The average has a single tree's bias, so if deep trees cannot represent the pattern, more trees will not help (ESL p. 588).

- **Default importances mislead.** Use permutation importance on held-out data, and watch correlated features.

- **Regression forests cannot extrapolate.** Every leaf predicts an average of training targets, so the forest never predicts beyond the range of y it saw.

- **Size and latency.** Hundreds of deep trees take memory and per-prediction time; limit depth or leaf size if it matters (sklearn).

- **Usually behind tuned boosting on accuracy** in recent tabular benchmarks, but far less sensitive to settings.

##### What came after

**Extra-Trees** (Geurts et al., 2006) go further: random features and random thresholds, and by default no bootstrap, trading a bit more bias for a bit less variance [Geurts 2006](https://doi.org/10.1007/s10994-006-6226-1). **Gradient boosting** (XGBoost, LightGBM) takes AdaBoost's sequential route and now usually leads tabular benchmarks.

## Say it

### How does a random forest improve on one deep tree?

#### The interviewer pushes further

Follow-up 1 of 7

Why random features at each split, isn't bootstrapping enough?

Bootstrapping alone (bagging) still lets one strong feature win the top split in almost every tree, so trees stay correlated and the ρσ² floor stays high. Hiding features at random forces different trees to use different structure, lowering ρ. The bagging and random-features labs show it on our data.

Follow-up 2 of 7

Random forest vs gradient boosting?

Forest: deep trees trained independently and in parallel, averaged; reduces variance; few hyperparameters; robust to label noise. Boosting: shallow trees trained sequentially, each correcting the last; reduces bias; usually more accurate when tuned, but more sensitive to settings and noise (Breiman's Table 4 shows AdaBoost's sensitivity).

Follow-up 3 of 7

Does adding more trees overfit?

No: error converges as trees are added (Breiman Thm 1.2), more trees only cost time. But the forest can still overfit through very deep trees; that is controlled with depth or leaf size, not tree count (ESL §15.3.4).

Follow-up 4 of 7

What is OOB error, and why about 37%?

Each bootstrap sample misses a row with probability (1 − 1/N)^N → e⁻¹ ≈ 0.368. Predicting each row with only the trees that never saw it gives a test-like error estimate, close to N-fold cross-validation, without a holdout.

Follow-up 5 of 7

How would you choose max_features?

Start from the defaults (√p classification; scikit-learn uses all features for regression, the literature often ⌊p/3⌋ or 0.3). Smaller m → more decorrelated but weaker trees. Tune it with OOB or cross-validated score; Breiman found results fairly insensitive to it.

Follow-up 6 of 7

Which feature importance would you trust?

Permutation importance on held-out data. The default impurity-based importance is computed on training data and favours high-cardinality features. With correlated features, both methods split the credit, so group correlated features first.

Follow-up 7 of 7

Does a random forest need feature scaling?

No. Splits compare a feature with a threshold, so any monotone rescaling of a feature gives the same splits.

#### The 30-second answer

"A random forest is many deep decision trees whose predictions are averaged. A single deep tree has low bias but high variance. Averaging reduces variance, but only if the trees make different mistakes, so the forest decorrelates them two ways: each tree trains on a bootstrap sample of the rows, and each split only considers a random subset of features. That keeps a dominant feature from making every tree the same. Bonus: the rows each tree didn't see give a free out-of-bag error estimate. The trade-off: it reduces variance, not bias, and tuned boosting often beats it on accuracy."

**Go further**

#### The 2-minute walkthrough

Problem: a deep tree overfits and is unstable; change a few rows and you get a different tree. Intuition: average many trees, like asking many people and taking the majority, which only helps if they think independently. Mechanism: (1) B bootstrap samples, (2) grow each tree deep, at every split choosing among m random features (√p for classification), (3) vote or average. Why it works: the variance of an average is ρσ² + (1−ρ)σ²/B, so more trees remove the second term and random features lower ρ, the floor. Evidence: Breiman's 2001 paper matched AdaBoost across 20 datasets while being far more robust to label noise. Limitation: no bias reduction, biased default importances, no extrapolation.

#### What not to say

- "Random forests can't overfit." Say: more trees don't overfit; deep trees still can.

- "Random forest reduces bias." It reduces variance; bias stays at the level of one tree.

- "It picks random features per tree." That is Ho's random subspace method; random forests resample features at every split.

- "scikit-learn takes a majority vote." It averages class probabilities.

- "feature_importances_ tells you what matters." Only with caveats; prefer permutation importance.

**Key terms and sources**

Leo Breiman's 2001 method, as it runs in scikit-learn today · 16 sources · checked 27 Oct 2026

#### Five ways people already randomized ensembles

Breiman's paper opens by listing the tricks it builds on [Breiman 2001, p. 1–2](https://www.stat.berkeley.edu/~breiman/randomforest2001.pdf#page=1). Each injects randomness somewhere different.

1. Bagging (Breiman, 1996): each tree sees a bootstrap sample of the rows, then they vote.

2. AdaBoost (Freund & Schapire, 1996) takes the opposite road. No randomness: each new tree focuses on the rows the previous ones got wrong. It was the accuracy leader at the time.

3. Three ideas randomize the features instead: Amit and Geman searched a random set of features at each node, Ho gave each whole tree a random feature subset, and Dietterich picked randomly among the K best splits. Breiman says Amit and Geman most shaped his thinking.

4. The random forest combines bagging with a fresh random feature subset at every single split, and grows each tree to full depth without pruning.

Before random forests, these randomized ensembles were less accurate than AdaBoost: Breiman notes that random split selection beats bagging, "but none of these three forests do as well as Adaboost" [Breiman 2001, p. 7](https://www.stat.berkeley.edu/~breiman/randomforest2001.pdf#page=7). Closing that gap was the goal.

#### Does it work?

##### One tree vs forest vs AdaBoost (Breiman, 2001)

Test-set error, lower is better. Forest-RI with 100 trees; AdaBoost with 50; m chosen by out-of-bag error between 1 and ⌊log₂p + 1⌋; "one tree" is the average single tree in the forest [Table 2, p. 10–11](https://www.stat.berkeley.edu/~breiman/randomforest2001.pdf#page=10).

The forest cuts the average single tree's error by about 1.8× (glass) to 9× (vowel) and matches AdaBoost, beating it on some datasets and trailing on others. Across all 20 datasets in the table the two stay within a few points of each other.

##### With 5% of labels flipped

Breiman flipped 5% of the training labels and measured how much each method's test error rose [Table 4, p. 16](https://www.stat.berkeley.edu/~breiman/randomforest2001.pdf#page=16):

| Dataset | AdaBoost | Random forest |
|---|---|---|
| breast cancer | +43.2% | +1.8% |
| votes | +48.9% | +6.3% |
| ionosphere | +27.7% | +3.8% |
| soybean | +26.9% | +3.2% |

These are 4 of the table's 9 datasets, where AdaBoost suffered most. The effect was small on glass (+1.6%), and on ecoli AdaBoost (+7.5%) was slightly better than the forest (+7.9%).

Why: AdaBoost keeps raising the weight of rows it gets wrong, and mislabelled rows are always wrong, so it "will concentrate increasing weight on these noisy instances and become warped". A forest weights no row specially.

##### Fast, too

Each split searches only m features. On the zip-code data with m = 1, 100 forest trees took 4.0 minutes versus almost three hours for 50 AdaBoost trees, about 40× faster (a 250 MHz Mac in 2000) [p. 11](https://www.stat.berkeley.edu/~breiman/randomforest2001.pdf#page=11).

##### Update · my check (27 Oct 2026)

Twenty-five years on, tree ensembles still do well on tables. A 45-dataset NeurIPS 2022 benchmark found tree-based models such as XGBoost and random forests remain state of the art on medium-sized (~10K rows) tabular data, ahead of deep learning [Grinsztajn et al. 2022](https://arxiv.org/abs/2207.08815). The NeurIPS 2025 TabArena benchmark finds gradient-boosted trees still strong, deep models catching up with large tuning budgets, and TabPFNv2 excelling on small datasets (≤10K rows) [TabArena](https://arxiv.org/abs/2506.16791). In those benchmarks, tuned boosting usually edges out random forests on accuracy; forests win on how little tuning they need. A review of RF tuning agrees the defaults "work reasonably well" in most cases, with tuning adding some gains [Probst et al. 2019](https://arxiv.org/abs/1804.03515).

#### Key terms

Bootstrap sample

N rows drawn with replacement from N; about 63.2% distinct rows.

Bagging

Bootstrap aggregating: one model per bootstrap sample, then vote or average.

m / max_features / mtry

How many randomly chosen features each split may consider.

Out-of-bag (OOB)

Rows a tree did not train on; used to estimate test error and importance.

Strength (s)

How much more the trees vote for the right class than the best wrong one, on average.

Correlation (ρ)

How alike the trees' predictions or errors are. Lower is better for averaging.

Gini impurity

Σ p(1 − p): 0 for a pure node, 0.5 for a 50/50 two-class node.

MDI

Mean decrease in impurity, scikit-learn's default `feature_importances_`.

#### Everything on this page comes from these

1. Breiman, L. (2001). Random Forests. _Machine Learning_ 45, 5–32. [preprint PDF](https://www.stat.berkeley.edu/~breiman/randomforest2001.pdf)

2. Breiman, L. & Cutler, A. Random Forests (authors' site). [stat.berkeley.edu](https://www.stat.berkeley.edu/~breiman/RandomForests/cc_home.htm)

3. Hastie, Tibshirani, Friedman. _The Elements of Statistical Learning_, 2nd ed., Ch. 15. [book site](https://hastie.su.domains/ElemStatLearn/)

4. scikit-learn User Guide: [Ensembles](https://scikit-learn.org/stable/modules/ensemble.html#random-forests), [Decision trees](https://scikit-learn.org/stable/modules/tree.html), [Permutation importance](https://scikit-learn.org/stable/modules/permutation_importance.html)

5. scikit-learn source, [sklearn/ensemble/_forest.py](https://github.com/scikit-learn/scikit-learn/blob/main/sklearn/ensemble/_forest.py)

6. Breiman, L. (1996). Bagging Predictors. [Berkeley Statistics](https://statistics.berkeley.edu/node/1781)

7. Geurts, Ernst, Wehenkel (2006). Extremely randomized trees. [doi](https://doi.org/10.1007/s10994-006-6226-1)

8. Strobl, Boulesteix, Zeileis, Hothorn (2007). Bias in random forest variable importance measures. [BMC Bioinformatics](https://bmcbioinformatics.biomedcentral.com/articles/10.1186/1471-2105-8-25)

9. Probst, Wright, Boulesteix (2019). Hyperparameters and Tuning Strategies for Random Forest. [arXiv 1804.03515](https://arxiv.org/abs/1804.03515)

10. Grinsztajn, Oyallon, Varoquaux (2022). Why do tree-based models still outperform deep learning on tabular data? [arXiv 2207.08815](https://arxiv.org/abs/2207.08815)

11. Erickson et al. (2025). TabArena: A Living Benchmark for Machine Learning on Tabular Data. [arXiv 2506.16791](https://arxiv.org/abs/2506.16791)

12. Bootstrap aggregating. [Wikipedia](https://en.wikipedia.org/wiki/Bootstrap_aggregating) (63.2% / 36.8%)

13. Interview-question collections used to pick the follow-ups: [Analytics Vidhya](https://www.analyticsvidhya.com/blog/2022/12/interview-questions-on-bagging-algorithms-in-machine-learning/), [Towards AI](https://towardsai.net/p/machine-learning/top-20-random-forest-interview-questions-answers), [DS Handbook](https://dshandbook.substack.com/p/random-forest-interview-questions)

The 8-applicant dataset and the numbers in the permutation and OOB scenes are illustrative. All other numbers come from the sources above. @datawithsuman
