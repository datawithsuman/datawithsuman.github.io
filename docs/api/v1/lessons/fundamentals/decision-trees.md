# Decision Trees

> How does a tree choose its questions, and why does a deep tree memorise noise?

- Track: Fundamentals › Classical ML › Tree-based models
- Type: Concept · 30 min
- Page: https://aimlrounds.com/tracks/fundamentals/decision-trees/
- Quiz topic: `trees`

## Intuition

### The situation

A lender wants loan rules it can read, learned from 160 past borrowers. The interviewer asks:

> How does a decision tree choose its splits?

**Running example:** a lender's loan book, simulated: 160 past borrowers with annual income (₹ lakh) and credit score, and whether they repaid. The true rule is a mix of thresholds, plus 10% label noise (people are unpredictable). Test accuracy is measured on 600 new applicants. A second, 1-D example (delivery time vs distance) shows regression trees.

#### A loan officer's rules, learned from data

An experienced loan officer thinks in rules: "score above 690 and income above ₹6 lakh: approve; score above 780: approve almost regardless; otherwise, be careful." A linear model can't express "and" and "otherwise" without hand-built features. A decision tree learns exactly this kind of nested rule directly from past borrowers, and you can print it and read it.

### The idea

Think of a game of twenty questions. Each yes-or-no question splits the group, and you always ask whichever question leaves each side the least mixed. Then you repeat on each side.

[Figure: A small decision tree. First question: credit score above 690? If no, be careful. If yes, a second question: income above 6 lakh? Yes means approve, no means be careful.]

_Illustrative, based on the lesson's loan officer rules._

### Play

**Try to break it.** Move the threshold until the weighted Gini is as low as you can get it, then snap to the best split. Then switch to the other feature.

#### Move the threshold, watch the impurity

The algorithm does exactly this for every feature, sorts the values once, and sweeps the threshold, which costs about O(features × n log n) per level docs. Then it recurses on each child.

Information gain is mutual information between a split and the label.

**Now say why:** why does the algorithm prefer this threshold, and which feature would it choose first?

## Maths

### Maths

#### In one breath

A decision tree asks a sequence of yes/no questions ("credit score > 690?", "income > ₹6 lakh?") and predicts the majority class (or the mean value) of whatever ends up in each leaf. It's built **greedily**: at every node, try every feature and threshold and keep the split that most reduces **impurity** (Gini, entropy, or squared error). Grown fully, a tree memorises the training data, so you limit depth, require minimum leaf sizes, or **prune**. Trees are readable, need almost no preprocessing, and handle non-linear patterns; they're also unstable and blocky, and those weaknesses are exactly what Random Forest and Gradient Boosting fix.What you'll be able to do after this: compute a split by hand, explain Gini vs entropy, show why a deep tree overfits, describe pruning, and say what trees are bad at.

#### Nodes, splits, leaves, and impurity

A **node** holds some borrowers and asks one question about one feature: xj ≤ t? Yes goes left, no goes right. A **leaf** stops asking and predicts the share of repayers there (classification) or the mean target (regression). To choose questions, we need a number for how mixed a node is, its impurity. For a node where a share p repaid:

$$ H_{\text{Gini}} = \textstyle\sum_k p_k(1-p_k) \qquad H_{\text{ent}} = -\textstyle\sum_k p_k\log p_k \qquad H_{\text{MSE}} = \tfrac{1}{n}\textstyle\sum (y-\bar y)^2 $$

scikit-learn's impurity definitions tree guide.

- **Gini impurity**: Σ p_k(1 − p_k) over classes. The chance two randomly drawn borrowers from this node have different labels. 0 when pure; 0.5 at a 50/50 mix (two classes).

- **entropy**: −Σ p_k log p_k. Bits of surprise. 0 when pure; 1 bit at 50/50. Splitting on entropy “is equivalent to minimizing the log loss” (scikit-learn).

- **regression: squared error**: For numeric targets: the variance of the target in the node. A leaf predicts the mean, which minimises it.

All three are 0 for a pure node and peak at 50/50. Gini and entropy are curved (strictly concave), so a split that makes one child purer always reduces them a bit; plain misclassification error is flat-sided and often can't tell good splits apart. Gini and entropy almost always pick the same split; Gini is slightly cheaper (no logarithm).

#### Greedily pick the split that reduces impurity the most

$$ G(\theta) = \tfrac{n_{L}}{n}\,H(Q_L) + \tfrac{n_{R}}{n}\,H(Q_R), \qquad \theta^{*} = \arg\min_{\theta=(j,t)} G(\theta) $$

scikit-learn's formulation tree guide. Greedy because finding the globally best tree "is known to be NP-complete", so practical algorithms choose the locally best split at each node.

- **split quality**: The impurity after the split: the children's impurities, weighted by how many borrowers go to each. Lower is better.

- **left share**: Fraction of the node's borrowers that answer yes (x_j ≤ t).

- **left impurity**: How mixed the yes-group is.

- **right share**: Fraction that answer no.

- **right impurity**: How mixed the no-group is.

- **the chosen split**: Try every feature j and every threshold t between sorted values; keep the one with the lowest G. Information gain is just parent impurity minus G.

#### Grow big, then cut back the weakest branches

Stopping rules (max depth, min leaf size) decide early and can miss a useful split hiding behind a weak one. CART's alternative: grow a large tree, then prune it with **minimal cost-complexity pruning**:

$$ R_\alpha(T) = R(T) + \alpha\,|\widetilde{T}| $$

scikit-learn: "A non-terminal node with the smallest value of αeff is the weakest link and will be pruned" tree guide. Choose α by cross-validation (scikit-learn's `cost_complexity_pruning_path` lists the candidate α values).

- **penalised risk**: What pruning minimises: the tree's error plus a price per leaf.

- **the tree's error**: Total impurity (or misclassification) of the leaves on the training data.

- **price per leaf**: α ≥ 0 (ccp_alpha in scikit-learn). α = 0 keeps the full tree; a large α prunes it to a stump.

- **number of leaves**: |T̃|: more leaves, more penalty. Branches whose improvement is worth less than α per extra leaf get cut, weakest link first.

#### Predict numbers with a staircase

Delivery time vs distance with a rush-hour bump around 6 km (simulated). Split by squared error; each leaf predicts the mean of its points, so the fit is a step function. Depth 3–4 follows the bump; depth 10 chases noise. Beyond 10 km the tree just repeats its last step: trees "are not good at extrapolation" docs.

## In practice

### In practice

#### CART, ID3, C4.5

| Algorithm | Splits | Notes |
|---|---|---|
| **ID3** (Quinlan, 1986) | Multi-way, categorical features only | Information gain (entropy) |
| **C4.5 / C5.0** (Quinlan) | Multi-way; discretises continuous features | Gain ratio; converts trees to if–then rule sets |
| **CART** (Breiman et al., 1984) | Always binary | Gini or entropy for classification, squared error for regression; cost-complexity pruning. scikit-learn "uses an optimized version of the CART algorithm" |

Summary from scikit-learn's tree guide docs. Every modern tree ensemble (Random Forest, XGBoost, LightGBM, CatBoost) is built on CART-style binary trees.

#### Scaling, categories, missing values, importance

##### No scaling needed

Splits compare a feature with a threshold, so any monotonic transform (log, standardise) gives the same tree. Trees "require little data preparation" docs.

##### Categorical features

CART can split a category set into two groups; scikit-learn's trees currently need encoding (one-hot or ordinal). LightGBM, CatBoost and scikit-learn's HistGradientBoosting handle categories natively.

##### Missing values

scikit-learn trees support NaN with `splitter='best'`: the training split decides which side missing values go to; if none were seen, they go "to the child with the most samples" docs.

##### Feature importance

Impurity-based importance (total impurity decrease per feature) is free but biased toward high-cardinality features and computed on training data. Prefer permutation importance on held-out data for decisions.

#### Training a single tree you can trust

1. Start shallow (scikit-learn suggests `max_depth=3`) to read the structure.

2. Tune max_depth, min_samples_leaf (try 5) or ccp_alpha with cross-validation.

3. For imbalanced classes, use class weights or balanced sampling; trees "create biased trees if some classes dominate".

4. Inspect: print the rules (`export_text`), check that the splits make domain sense.

5. If accuracy matters more than one readable tree, move to an ensemble: Random Forest (variance) or Gradient Boosting (bias).

#### A single tree, or something else?

##### Use a single tree when

- The rules themselves are the product (eligibility checks, triage guidelines)

- You need a quick, explainable baseline

- Regulation demands a transparent model and a small tree is accurate enough

##### Use an ensemble when

- Accuracy matters most: gradient boosting is the tabular default

- You want robustness with little tuning: Random Forest

- Smooth or linear relationships: consider linear models too

### The answer that sounds right

#### "Keep splitting until every leaf is pure"

With enough questions you can isolate every borrower in their own leaf: 100% training accuracy. But 10% of the labels are noise, so a tree that fits every point has memorised the noise. In the lab below, training accuracy climbs to 100% as depth grows, while test accuracy peaks at depth 4 (≈ 84.5%) and then falls. scikit-learn: decision trees "can create over-complex trees that do not generalize the data well. This is called overfitting" tree guide.

#### Each split adds a rectangle

Every boundary is horizontal or vertical: each split looks at one feature. Deep trees carve tiny boxes around single noisy borrowers. Raising min_samples_leaf (no leaf may hold fewer than m borrowers) is a gentler brake than capping depth; scikit-learn suggests "min_samples_leaf=5 as an initial value" docs.

#### A slightly different sample, a different tree

–

Four samples of 160 borrowers from the same population, a depth-4 tree on each. The top split stays near a credit score of 690, but the lower boxes move around a lot. scikit-learn: "small variations in the data might result in a completely different tree being generated. This problem is mitigated by using decision trees within an ensemble" docs. High variance is the price of flexibility, and averaging many trees (Random Forest) is the cure.

#### Strengths and weaknesses, side by side

##### Strengths

- Readable rules ("white box")

- Captures interactions and thresholds automatically

- No scaling; mixed feature types; fast prediction (O(depth))

- The building block of the strongest tabular models

##### Weaknesses

- Overfits unless constrained

- Unstable: small data changes, different tree

- Axis-aligned, blocky boundaries; a diagonal boundary needs many steps

- Can't extrapolate; struggles with XOR / parity-type patterns

## Say it

### How does a decision tree choose its splits?

#### The interviewer pushes further

Follow-up 1 of 5

Gini vs entropy?

Both are concave impurity measures that are 0 for pure nodes and maximal at a uniform mix; they choose the same split in most cases. Gini is slightly faster (no log); entropy corresponds to minimising log-loss. Misclassification rate is a poor splitting criterion because it's not strictly concave.

Follow-up 2 of 5

Why are trees greedy, and what's the downside?

Finding the optimal tree is NP-complete, so each split is chosen locally. A split that looks useless alone (XOR) can enable great splits below it, and greedy search misses it.

Follow-up 3 of 5

How do you stop a tree from overfitting?

Pre-pruning (max_depth, min_samples_leaf, min_impurity_decrease) or post-pruning (cost-complexity with ccp_alpha), chosen by cross-validation, or ensembles.

Follow-up 4 of 5

Do trees need feature scaling? Can they handle missing values?

No scaling: splits are threshold comparisons, invariant to monotonic transforms. Modern implementations (recent scikit-learn trees, XGBoost, LightGBM, HistGradientBoosting) learn which branch missing values take.

Follow-up 5 of 5

What's the complexity?

Training about O(features × n log n) per level; prediction O(depth), about O(log n) for a balanced tree.

#### The 30-second answer

A decision tree recursively splits the data with yes/no questions on single features. At each node it greedily picks the feature and threshold that most reduce impurity (Gini or entropy for classification, squared error for regression), and leaves predict the majority class or mean. Fully grown trees overfit, so we limit depth, set a minimum leaf size, or use cost-complexity pruning tuned by cross-validation. Trees are interpretable and need no scaling, but they're unstable, blocky and can't extrapolate, which is why we usually use them inside ensembles like random forests or gradient boosting.

**Go further**

#### What not to say

- "Trees find the optimal decision rules." They find greedy, locally optimal splits.

- "Impurity-based importance tells you causal impact." It's biased and descriptive only.

- "Deeper is better." Train accuracy, yes; test accuracy usually not.

**Key terms and sources**

CART, Gini and entropy, pruning, regression trees · built from scikit-learn's tree guide, Breiman et al. (1984) and Quinlan (ID3/C4.5) · checked 28 Oct 2026

#### Glossary

| Term | Meaning |
|---|---|
| **Impurity** | How mixed a node is: Gini, entropy, or squared error. |
| **Information gain** | Parent impurity − weighted child impurity. |
| **CART** | Classification and Regression Trees: binary splits, Gini/MSE, cost-complexity pruning. |
| **max_depth / min_samples_leaf** | Pre-pruning limits on tree size. |
| **Cost-complexity pruning** | Minimise error + α × leaves; post-pruning. |
| **Stump** | A depth-1 tree: one split. The classic boosting weak learner. |

#### What this page is built from

1. scikit-learn, Decision Trees user guide (formulation, criteria, pruning, complexity, missing values, ID3/C4.5/CART, practical tips).

2. L. Breiman, J. Friedman, R. Olshen & C. Stone, _Classification and Regression Trees_, Wadsworth, 1984 (CART, cost-complexity pruning; background).

3. J. R. Quinlan, "Induction of decision trees", _Machine Learning_ 1 (1986) (ID3); _C4.5: Programs for Machine Learning_, 1993 (background).

4. Hastie, Tibshirani & Friedman, _The Elements of Statistical Learning_, §9.2 (tree-based methods; background).

Loan and delivery data are simulated with fixed seeds; every tree on this page is grown live in your browser by a small CART implementation (exhaustive search over midpoints).
