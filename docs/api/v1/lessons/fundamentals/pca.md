# Principal Component Analysis

> Ten correlated columns, two real ideas: how does PCA find them, and why scale first?

- Track: Fundamentals › Classical ML › Unsupervised learning
- Type: Concept · 30 min
- Page: https://aimlrounds.com/tracks/fundamentals/pca/
- Before this: Eigenvalues & Eigenvectors (`fundamentals/eigenvalues-and-eigenvectors`)
- Quiz topic: `unsup`

## Intuition

### The situation

You have ten customer columns, and most of them move together. Feeding them all into a model counts the same idea several times. The interviewer asks:

> What does PCA do, and what are the principal components?

**Running example:** the food-delivery app again, now with **ten** numbers per customer: orders per month, app sessions, active days, push-notification opens (all "engagement"); average basket, share of premium items, tip, delivery fee paid (all "spend"); coupon use (a bit of both); and the rating they give (mostly unrelated). The 300 simulated customers are generated from just two hidden factors, engagement and spend, plus noise. Can PCA discover that ten columns are really about two things? A 2-D version (orders vs app sessions) comes first.

#### Ten correlated columns, two real ideas

Customers who order more also open the app more and are active more days: those columns move together. Feeding all ten into a model wastes capacity on duplicates, makes distances (k-means, k-NN) count the same idea several times, and makes plots impossible. We want a few new features that summarise the ten with as little loss as possible, discovered from the data, with no labels.

### The idea

Think of photographing a long, thin object. From most angles it looks small, but one angle shows it at full length. PCA finds that angle for your data: the direction with the most spread, then the next-best one at a right angle to it.

[Figure: A long tilted cloud of points. A long arrow along it is the first component, and a short arrow across it is the second.]

_Illustrative. Keeping only PC1 here would keep most of the spread._

### Play

**Try to break it.** Keep just one component and read the variance kept. Then add components one at a time until the gain gets small.

#### The explained-variance (scree) plot

Ten standardised customer features. Bars: variance per component. Line: cumulative share.

The first component explains **55.0%**, the second **24.4%** (79% together), the third 8.2%, and every other one about 2% or less, roughly what a pure-noise direction would explain. The bend after two components matches the two hidden factors, plus a third for the "rating" column, which is mostly its own independent noise. Common rules: keep enough components for 90–95% of the variance (scikit-learn accepts a fraction, e.g. `n_components=0.95`), or cut at the bend, or choose k by the downstream model's validation score.

**Now say why:** why do the first two components capture so much here, and where would you stop?

## Maths

### Maths

#### In one breath

PCA finds new axes for your data, the **principal components**: the first points along the direction where the data varies most, the second along the most-varying direction at right angles to the first, and so on. Keep the first few and you have a smaller set of features that holds most of the information (variance), with the least possible **reconstruction error** for a linear projection. Mathematically the components are the **eigenvectors of the covariance matrix** (computed via SVD), and each eigenvalue is the variance it captures. Choose how many to keep from the **explained-variance** curve. Always **standardise** first when features have different units, and remember PCA only finds **linear** structure, and high variance isn't the same as useful for prediction. What you'll be able to do after this: explain PCA as variance maximisation and as best reconstruction, read a scree plot, interpret loadings, show why scaling matters, and know when to use something else.

#### Variance along a direction

Centre the data (subtract each column's mean). Pick a direction, a unit vector w. Project every customer onto it: their score is w·x, a single number. The variance of those scores says how much of the data's spread that direction captures. If the covariance matrix of the data is Σ, that variance has a compact form:

$$ {\operatorname{Var}(w^{\top}x)} = {w}^{\top}\,{\Sigma}\,{w}, \qquad \lVert w \rVert = 1 $$

- **variance of the projections**: How spread out the customers are along direction w. Big means this direction carries a lot of information.

- **the direction**: A unit vector (length 1), so we compare directions, not lengths.

- **covariance matrix**: Σ: variances of each feature on the diagonal, covariances (how pairs move together) off it. For 10 features, 10 × 10.

150 customers: orders per month vs app sessions (centred, correlation ≈ 0.85). Short red lines show each customer's distance to the line. Turn the line: captured + left over always add up to the total variance.

Rotate the line and watch the two numbers trade off. The direction that captures the most variance is also the one with the smallest squared distances to the line. Those are the same problem, which is the key fact about PCA. Here PC1 captures **93.7%** of the variance; PC2, at right angles, gets the remaining 6.3%.

#### Components are eigenvectors of the covariance matrix

$$ {\Sigma}\,{w_k} = {\lambda_k}\,{w_k}, \qquad \lambda_1 \ge \lambda_2 \ge \dots \ge \lambda_d \ge 0 $$

scikit-learn: PCA decomposes data "in a set of successive orthogonal components that explain a maximum amount of the variance" [decomposition guide](https://scikit-learn.org/stable/modules/decomposition.html#pca).

- **covariance matrix**: Computed from the centred data.

- **component (eigenvector)**: Maximising wᵀΣw with ‖w‖ = 1 (a Lagrange multiplier) gives exactly this equation: the best direction is an eigenvector of Σ.

- **its variance (eigenvalue)**: λ_k is the variance along component k. Sort them largest first; λ_k / Σλ is the explained variance ratio.

Because Σ is symmetric, its eigenvectors are orthogonal: each component captures new variance not captured by earlier ones, and the component scores are uncorrelated. In practice libraries don't form Σ; they take the **singular value decomposition** of the centred data matrix, Xc = U S VT. The rows of VT are the components and the squared singular values divided by (n − 1) are the eigenvalues. It's more numerically stable, and randomised SVD makes it fast when you only want a few components.

**Go deeper: the two views give the same answer**

For a unit vector w, each centred point splits into its projection (w·x)w and a residual. By Pythagoras, ‖x‖² = (w·x)² + ‖residual‖². Summed over points, the left side is fixed, so maximising the projected variance Σ(w·x)² is the same as minimising the total squared residual. With k components the same argument shows the top-k eigenvectors give the best rank-k linear reconstruction (the Eckart–Young theorem for the SVD).

#### Reading the loadings

Each bar is the weight of one original feature in the component (the components are unit vectors, so weights are comparable).

**PC1** has positive weights on everything (0.19–0.38): it's "overall activity", customers who do more of everything. **PC2** is a contrast: negative on the engagement features, positive on the spend features, so it separates "frequent, cheap" from "occasional, big-basket" customers. PCA didn't recover the hidden factors "engagement" and "spend" one per axis; it found their sum and their difference. Components are directions of variance, not guaranteed to be meaningful concepts. (Factor analysis with a rotation such as varimax aims at more interpretable axes.)

## In practice

### In practice

#### The dimensionality-reduction toolbox

| Method | Keeps | Use for |
|---|---|---|
| **PCA** (Pearson 1901, Hotelling 1933) | Global variance, linear | Compression, de-correlation, preprocessing, quick plots |
| **Truncated SVD** | Same without centring | Sparse data (text TF-IDF, "LSA") |
| **Kernel PCA** | Non-linear variance via kernels | Curved structure, small n |
| **t-SNE / UMAP** | Local neighbourhoods, non-linear | 2-D visualisation of clusters (next lesson) |
| **Autoencoders** | Whatever reconstructs best, non-linear | Large data, images, learned embeddings |

PCA, truncated SVD and kernel PCA are in scikit-learn's decomposition module [decomposition guide](https://scikit-learn.org/stable/modules/decomposition.html).

#### The whole recipe

1. **Standardise** (unless all features share a meaningful scale).

2. **Fit PCA** on training data only, then transform train and test.

3. **Choose k** from cumulative explained variance (e.g. 95%) or downstream validation.

4. **Inspect loadings** to describe the top components.

5. **Big data:** `svd_solver="randomized"`, `IncrementalPCA` for data that doesn't fit in memory.

Cost: exact PCA is O(nmax² · nmin); randomised PCA is O(nmax² · ncomponents) [decomposition guide](https://scikit-learn.org/stable/modules/decomposition.html#pca). `IncrementalPCA` processes mini-batches for out-of-core data.

#### When to use it

##### Use PCA when

- Many correlated numeric features: compress before clustering, k-NN or linear models

- You need a fast first look at the data's structure

- Denoising, or reducing to ~50 dimensions before t-SNE/UMAP

##### Reach for something else when

- Visualising clusters: t-SNE/UMAP

- Non-linear structure: kernel PCA, autoencoders

- Sparse text: truncated SVD (no centring)

- You need interpretable factors: factor analysis, NMF

### The answer that sounds right

#### "Just drop the columns that look redundant"

Keeping "orders per month" and dropping "app sessions" throws away whatever sessions knew that orders didn't. Averaging hand-picked groups needs you to already know the structure. And when features are on different scales, "most variance" just means "biggest units": measure basket size in rupees instead of standardised units and PCA's first component becomes basket size alone, explaining **99.5%** of the variance, which says nothing about customers (see the scaling lab). PCA has to be done on the right scale.

#### Units decide the answer if you let them

Multiply just the basket column by 30 (rupees instead of standardised units) and PC1 explains **99.5%** of the variance with a weight of 1.00 on that single column: PCA has found "the column with the biggest numbers". scikit-learn: PCA "centers but does not scale the input data for each feature before applying the SVD" [decomposition guide](https://scikit-learn.org/stable/modules/decomposition.html#pca), so put a `StandardScaler` before it whenever units differ. (If all features share a unit and their scale is meaningful, such as pixel intensities, don't standardise.)

#### Linear only, and variance isn't relevance

- **Linear:** a curved structure (a spiral, a ring) can't be unrolled by a rotation. Kernel PCA, UMAP or autoencoders handle that.

- **Variance ≠ usefulness:** the feature that predicts churn might be a low-variance direction PCA throws away. PCA is unsupervised; if you're reducing dimensions for a predictor, validate k on the prediction task.

- **Outliers:** squared distances let a few extreme points tilt the components (robust PCA exists).

- **Interpretability:** each component mixes all original features.

- **For visualising clusters**, PCA often overlaps them: in the UMAP paper's benchmark, a k-NN classifier on a 2-D PCA embedding of MNIST scored about 0.46–0.47 accuracy against about 0.96–0.97 for t-SNE or UMAP [UMAP paper, Table 2](https://arxiv.org/pdf/1802.03426#page=32). PCA is still the standard first step before t-SNE.

#### Caveats

##### Strengths

- Fast, deterministic, no hyperparameters except k

- Optimal linear compression (least squared reconstruction error)

- Decorrelates features; denoises by dropping small components

- Applies to new data with one matrix multiply

##### Weaknesses

- Linear only

- Scale-sensitive: standardise first

- High variance ≠ predictive

- Components are mixtures, often hard to name

## Say it

### What does PCA do, and what are the principal components?

#### The interviewer pushes further

Follow-up 1 of 5

Why eigenvectors of the covariance matrix?

Maximise wᵀΣw subject to wᵀw = 1. The Lagrangian gives Σw = λw, so stationary points are eigenvectors, and the variance at each is its eigenvalue; the largest eigenvalue gives the maximum.

Follow-up 2 of 5

PCA vs SVD?

PCA is the SVD of the centred data: Xc = USVᵀ; components are rows of Vᵀ, eigenvalues are S²/(n − 1), scores are US. SVD avoids forming the covariance matrix and is more stable.

Follow-up 3 of 5

Should you scale before PCA?

Yes when features have different units; otherwise the biggest-unit feature dominates. Not when all features share a meaningful scale (pixels).

Follow-up 4 of 5

How do you choose the number of components?

Cumulative explained variance (90–95%), the scree-plot elbow, or cross-validation of the downstream model.

Follow-up 5 of 5

PCA vs t-SNE/UMAP?

PCA is linear, deterministic, preserves global variance, and can transform new points; t-SNE/UMAP are non-linear, preserve local neighbourhoods, and are mainly for visualisation. PCA is often run first to reduce noise and dimensions.

#### The 30-second answer

PCA finds orthogonal directions that capture the most variance in the data. The first principal component maximises the variance of the projected data, the second does the same subject to being orthogonal to the first, and so on. They're the eigenvectors of the covariance matrix, with eigenvalues equal to the variance captured, computed in practice by SVD of the centred data. Keeping the top k components gives the best rank-k linear reconstruction. You pick k from the cumulative explained variance or downstream validation, and you must standardise features with different units first. It's linear and unsupervised, so it can miss curved structure and can discard low-variance directions that matter for prediction.

**Go further**

#### What not to say

- "PCA selects the most important features." It creates new features, each a mix of all of them.

- "High-variance components are the most predictive." Not necessarily.

- "PCA works on any structure." Only linear.

**Key terms and sources**

Directions of maximum variance, eigenvectors and SVD, explained variance, choosing the number of components, scaling, and what PCA can't do · built from scikit-learn's decomposition guide, Pearson (1901), Hotelling (1933) and the UMAP paper's comparison · checked 28 Oct 2026

#### Evidence

##### Ten customer features (this page's simulation)

PC1 variance

55.0%

PC1 + PC2

79%

PC1 + PC2 + PC3

88%

PC1 with basket in rupees (unscaled)

99.5%

Two hidden factors + noise, 300 customers. Illustrative.

##### 2-D embedding quality on MNIST (k-NN accuracy in the embedding, k = 100)

PCA

0.462

t-SNE

0.967

UMAP

0.967

McInnes, Healy & Melville, Table 2, 20-fold cross-validation [p. 32](https://arxiv.org/pdf/1802.03426#page=32). Higher is better: how well local neighbourhoods survive in 2-D. PCA keeps global variance, not neighbourhoods.

#### Key terms

| Term | Meaning |
|---|---|
| **Principal component** | Unit direction of maximal remaining variance; an eigenvector of Σ. |
| **Explained variance ratio** | λk / Σλ: share of total variance along component k. |
| **Loadings** | The weights of original features in a component. |
| **Scores** | A point's coordinates on the components. |
| **Scree plot** | Explained variance by component; look for the bend. |
| **Whitening** | Scaling components to unit variance (`whiten=True`). |

#### What this page is built from

1. scikit-learn, [Decomposing signals in components (PCA, IncrementalPCA, randomised SVD, kernel PCA)](https://scikit-learn.org/stable/modules/decomposition.html).

2. K. Pearson, "On lines and planes of closest fit to systems of points in space", _Philosophical Magazine_, 1901; H. Hotelling, "Analysis of a complex of statistical variables into principal components", _J. Educational Psychology_ 24, 1933 (origins; background).

3. L. McInnes, J. Healy & J. Melville, "UMAP: Uniform Manifold Approximation and Projection for Dimension Reduction", [arXiv:1802.03426](https://arxiv.org/abs/1802.03426) (Table 2: k-NN accuracy on PCA, t-SNE, UMAP embeddings).

4. C. Eckart & G. Young, "The approximation of one matrix by another of lower rank", _Psychometrika_, 1936 (best low-rank approximation; background).

Customer data is simulated with fixed seeds; PCA runs live in your browser (Jacobi eigen-decomposition).
