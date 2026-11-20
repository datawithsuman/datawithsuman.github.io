# t-SNE & UMAP

> How do you see 768-dimensional data, and what are the plots lying about?

- Track: Fundamentals › Classical ML › Unsupervised learning
- Type: Concept · 30 min
- Page: https://aimlrounds.com/tracks/fundamentals/t-sne-and-umap/
- Before this: Principal Component Analysis (`fundamentals/pca`)
- Quiz topic: `unsup`

## Intuition

### The situation

You've trained customer embeddings and made a 2-D plot. A teammate points at the gaps and sizes of the clusters and draws conclusions from them. The interviewer asks:

> How does t-SNE build its 2-D map?

**Running example:** the food-delivery app has ten features per customer. In the simulated data there are three groups of 50: group A is **tight** (spread 0.3), group B is **wide** (spread 2.0, about 6.7 times A), and group C is **far away** (B is 4 times farther from C than from A). We know these facts because we built the data; the question is which of them survive the trip down to 2-D. Every map on this page is computed live by a small exact t-SNE.

#### You can't look at ten dimensions

Before clustering customers, or after training an embedding model, you want to **see** the data: are there groups? outliers? mislabelled points? A 2-D scatter plot is the most powerful tool a human has, but the data has 10, 300 or 768 dimensions. PCA's best flat projection often piles groups on top of each other: on MNIST digits a 2-D PCA map keeps so little neighbourhood structure that a k-NN classifier on it gets about 46% accuracy, against about 97% on t-SNE or UMAP maps [UMAP paper, Table 2](https://arxiv.org/pdf/1802.03426#page=32). We need a non-linear map that keeps **local** structure.

### The idea

Think of arranging people on a floor so that friends stand together. You'll keep the friend groups intact, but how big each group looks, and how far apart the groups stand, means very little.

[Figure: Left, the true data: one tight group and one much wider group. Right, the 2-D map: the two groups look about the same size.]

_Illustrative, based on the lesson's groups A and B. Maps keep neighbours, not sizes._

### Play

**Try to break it.** Run perplexity from 2 up to 50, then change the seed. Compare the size and distance readouts with their true values.

#### Perplexity changes the picture

150 customers, 10 features, exact t-SNE, 700 iterations, computed in your browser (the first run of each setting takes a moment). Axes have no units: only who sits near whom matters.

Group B is 6.7 times wider than A in the data, but on the map it looks about the **same size** (0.97–1.07×) at perplexity 2–30, and 2.1× at 50. C is 4 times farther from B than A is, but at perplexity 2–5 the map shows all three groups roughly **equidistant** (ratio 0.97–1.06), at 15–30 the ratio is 1.0–1.6, and only at perplexity 50 (with 50 points per group, each point's neighbourhood now spans its whole group) does it climb to 2.9–3.5, still short of 4. Both seeds agree on the pattern. All three groups stay cleanly separated at every setting: that part is reliable.

**Now say why:** if the picture changes this much, what can you safely conclude from it?

## Maths

### Maths

#### In one breath

t-SNE and UMAP squash high-dimensional data (embeddings, gene profiles, customer features) into 2-D so that **points that were neighbours stay neighbours**. t-SNE turns distances into probabilities of "being neighbours" (with **perplexity** ≈ how many neighbours each point considers), then moves 2-D points to match them, using a heavy-tailed Student-t in 2-D so clusters separate cleanly. UMAP builds a weighted k-nearest-neighbour graph and lays it out with attraction and repulsion; it's much faster, scales to millions, and can embed into more than 2 dimensions. Both are excellent for **seeing** clusters and both mislead: **cluster sizes** and **distances between clusters** are often not meaningful, results change with hyperparameters and seeds, and random noise can look like clusters. What you'll be able to do after this: explain how t-SNE works and what perplexity does, compare it with UMAP and PCA, and list exactly what you may and may not conclude from one of these plots.

#### Similarities as probabilities

t-SNE (van der Maaten & Hinton, 2008) describes the high-dimensional data by how likely each point is to "pick" each other point as its neighbour:

$$ {p_{j\mid i}} = {\exp\!\bigl(-\lVert x_i - x_j\rVert^2 / 2{\sigma_i^2}\bigr)} \,/\, {\textstyle\sum_{k \ne i} \exp\!\bigl(-\lVert x_i - x_k\rVert^2 / 2\sigma_i^2\bigr)} $$

scikit-learn: t-SNE "converts affinities of data points to probabilities. The affinities in the original space are represented by Gaussian joint probabilities and the affinities in the embedded space are represented by Student's t-distributions" [manifold guide](https://scikit-learn.org/stable/modules/manifold.html#t-sne).

- **high-D neighbour probability**: p_{j|i}: if point i picked a neighbour at random, favouring close ones, the chance it picks j.

- **Gaussian on distance**: Close points get high values, far points almost zero.

- **a bandwidth per point**: σ_i is chosen separately for each point so that its neighbour distribution has the target perplexity: points in dense regions get a small σ, points in sparse regions a large one.

- **normalise**: Divide by the sum over all other points, so the probabilities add to 1. Then symmetrise: p_ij = (p_{j|i} + p_{i|j}) / 2n.

Perplexity sets σi. scikit-learn: "The perplexity of a k-sided die is k, so that k is effectively the number of nearest neighbors t-SNE considers" [manifold guide](https://scikit-learn.org/stable/modules/manifold.html#t-sne). The original paper's guidance: "typical values are between 5 and 50", quoted by Distill, which adds that perplexity "really should be smaller than the number of points" [Distill 2016](https://distill.pub/2016/misread-tsne/).

#### Match the neighbour probabilities, with heavy tails in 2-D

$$ {q_{ij}} = {\frac{(1 + \lVert y_i - y_j\rVert^2)^{-1}}{\sum_{k\ne l}(1 + \lVert y_k - y_l\rVert^2)^{-1}}}, \qquad {C = \mathrm{KL}(P\,\Vert\,Q) = \textstyle\sum_{i \ne j} p_{ij}\log\frac{p_{ij}}{q_{ij}}} $$

van der Maaten & Hinton (2008), JMLR 9. scikit-learn: "the KL divergence is not convex, i.e. multiple restarts with different initializations will end up in local minima … it is sometimes useful to try different seeds and select the embedding with the lowest KL divergence" [manifold guide](https://scikit-learn.org/stable/modules/manifold.html#t-sne).

- **2-D similarity**: q_ij: how close the map puts i and j, as a probability.

- **Student-t (1 degree of freedom)**: Falls off as 1/distance² instead of exponentially. Its heavy tail lets moderately distant points sit far apart in 2-D without much penalty, which cures the crowding problem and gives well-separated clusters.

- **what t-SNE minimises**: The Kullback–Leibler divergence from P to Q. It heavily penalises putting real neighbours (large p) far apart (small q), but barely penalises putting far points close. That is why local structure is kept and global structure is not guaranteed.

The map is found by gradient descent: start from tiny random (or PCA) positions, and repeatedly pull together pairs whose q is too small and push apart pairs whose q is too large. Two practical tricks: **early exaggeration** (multiply P by ~12 for the first iterations so clusters form and separate early) and momentum.

#### A neighbour graph, laid out with springs

1. Start from the high-dimensional points (drawn flat here).

2. Connect each point to its n_neighbors nearest neighbours (found approximately, fast). Edge weights fall off with distance, scaled per point by the distance to its nearest neighbour, so dense and sparse regions both get well-connected local graphs. Two clusters may be joined by a few weak edges.

3. Initialise a 2-D layout, by default with the spectral embedding (Laplacian eigenmaps) of that graph.

4. Optimise with stochastic gradient descent: for each sampled edge, pull its two endpoints together.

5. For each pull, push a few random (probably unrelated) points apart: negative sampling, borrowed from word2vec. The objective is a cross-entropy between the high-D graph and the 2-D one, and needs no global normalisation, which is why it is fast.

Two knobs: **n_neighbors** (like perplexity: small = local detail, large = more global shape; default 15) and **min_dist** (how tightly points may pack in the map; 0 for clustering). The paper's claim: UMAP "is competitive with t-SNE for visualization quality, and arguably preserves more of the global structure with superior run time performance" [McInnes et al., p. 1](https://arxiv.org/pdf/1802.03426#page=1).

##### Update · my check: the "global structure" claim

Later work by Kobak & Linderman showed that much of UMAP's apparent global-structure advantage comes from its **initialisation**: with the same (e.g. PCA or spectral) initialisation, t-SNE preserves global structure about as well. The UMAP authors themselves acknowledge this in their paper's weaknesses section: "a significant contributor to UMAP's relative global structure preservation is derived from the Laplacian Eigenmaps initialization" [p. 49](https://arxiv.org/pdf/1802.03426#page=49). Practical lesson: initialise t-SNE with PCA (`init="pca"`, scikit-learn's default), and don't choose UMAP over t-SNE for global fidelity alone.

## In practice

### In practice

#### Three ways to get a 2-D picture

| | PCA | t-SNE | UMAP |
|---|---|---|---|
| **Keeps** | Global variance (linear) | Local neighbourhoods | Local neighbourhoods; arguably more global structure |
| **Speed** | Seconds | O(N log N) with Barnes–Hut; slow at millions | Empirically ~O(N1.14); millions feasible |
| **New points** | Yes (matrix multiply) | No (refit) | Yes (`transform`) |
| **Output dims** | Any | 2–3 in practice (Barnes–Hut) | Any |
| **Deterministic** | Yes | No (seed) | No (seed) |

t-SNE complexity and the 3-D limit of Barnes–Hut: scikit-learn [manifold guide](https://scikit-learn.org/stable/modules/manifold.html#t-sne). UMAP's O(N1.14) empirical scaling and arbitrary embedding dimension: McInnes et al. [p. 22](https://arxiv.org/pdf/1802.03426#page=22).

#### Using these maps for real work

- **Reduce first:** run PCA to ~50 dimensions before t-SNE to cut noise and time (the t-SNE paper did this too); UMAP copes with high ambient dimension directly.

- **Try several settings and seeds;** trust structure that survives all of them.

- **Clustering on UMAP output:** the UMAP docs show HDBSCAN on a UMAP embedding of MNIST clustering over 99% of points, versus about 17% when run on 50-dimensional PCA. They advise `min_dist=0`, a larger `n_neighbors` (e.g. 30), and caution: it "should be attempted with care", since UMAP "can also create false tears in clusters" [UMAP docs](https://umap-learn.readthedocs.io/en/latest/clustering.html).

- **Never cluster on t-SNE coordinates for decisions** without validating in the original space; the map's distances are distorted by design.

- **Interpretability:** map axes mean nothing; the UMAP authors recommend PCA, NMF or similar "if strong interpretability is critical" [p. 45](https://arxiv.org/pdf/1802.03426#page=45).

#### The whole recipe

1. **Scale** features; for embeddings use cosine distance.

2. **PCA to ~50 dims** (for t-SNE; optional for UMAP).

3. **Run** t-SNE (perplexity 5–50, init="pca", learning_rate="auto") or UMAP (n_neighbors 15–50, min_dist 0.1, or 0 for clustering).

4. **Repeat** with 2–3 settings and seeds; colour by known labels or metadata.

5. **Conclude only** about neighbourhoods and separations that persist; check any cluster in the original space.

#### When to use it

##### Use t-SNE / UMAP when

- Exploring high-dimensional data or embeddings visually

- Checking whether classes or clusters separate

- UMAP: preprocessing for density clustering, or large datasets

##### Reach for something else when

- You need features for a model: PCA, or UMAP with care

- You need faithful global distances: PCA or MDS

- You need interpretable axes: PCA, NMF, factor analysis

### The answer that sounds right

#### "Use a Gaussian in 2-D too" (the crowding problem)

The first version, SNE (Hinton & Roweis, 2002), matched the high-D probabilities with Gaussian similarities in 2-D. But there is far more room in 10 dimensions than in 2: a point can have many neighbours at roughly the same moderate distance, and they can't all fit at that distance in a plane. To keep the near neighbours near, the moderately distant points get squeezed into the middle, and every cluster collapses into one crowded ball. van der Maaten & Hinton named this the **crowding problem**.

#### What a t-SNE (or UMAP) plot does and doesn't tell you

##### Usually safe to read

- Which points are neighbours: tight local groups are real neighbourhoods

- That well-separated clusters exist (check across settings and seeds)

- Outliers and mislabelled points sitting inside another class's cluster

##### Not safe to read

- Cluster sizes: "Cluster sizes in a t-SNE plot mean nothing"

- Gaps between clusters: "distances between well-separated clusters in a t-SNE plot may mean nothing"

- Clumps in noise: "Random noise doesn't always look random"

- Results from one perplexity: "For topology, you may need more than one plot"

Quotes are section titles and sentences from Wattenberg, Viégas & Johnson, "How to Use t-SNE Effectively" [Distill 2016](https://distill.pub/2016/misread-tsne/), which also stresses iterating "until reaching a stable configuration". Why sizes vanish: σi adapts to local density, so every cluster is described by "my ~30 nearest neighbours", whether they're packed tight or spread wide. Density is normalised away by design.

#### Caveats

##### Strengths

- Reveal cluster and neighbourhood structure PCA hides

- UMAP: fast, scales, any output dimension, transforms new points

- Standard tools for embeddings, single-cell biology, data QA

##### Weaknesses

- Sizes and between-cluster distances unreliable

- Hyperparameter- and seed-dependent; can invent structure in noise

- t-SNE: slow at scale, no transform for new points

- Axes have no meaning

## Say it

### How does t-SNE build its 2-D map?

#### The interviewer pushes further

Follow-up 1 of 5

What does perplexity do?

It sets each point's Gaussian bandwidth so its neighbour distribution has entropy log₂(perplexity): effectively the number of neighbours. Low values emphasise very local structure and can fragment clusters; high values show more global shape. Typical 5–50, and less than the number of points.

Follow-up 2 of 5

Why a Student-t in the low-dimensional space?

To fix the crowding problem: its heavy tail lets moderately distant points be placed far apart without much cost, so clusters separate instead of collapsing in the middle.

Follow-up 3 of 5

Can you trust cluster sizes and distances in a t-SNE plot?

No. Bandwidths adapt to local density, which equalises apparent sizes, and KL barely penalises misplacing far-apart points, so gaps between clusters aren't meaningful. Trust neighbourhoods and separations that persist across settings.

Follow-up 4 of 5

t-SNE vs UMAP?

Similar local quality; UMAP is much faster, scales to millions, supports transform and higher output dimensions. UMAP's better global layout is largely due to its spectral initialisation; t-SNE with PCA init closes much of the gap.

Follow-up 5 of 5

Would you cluster on a t-SNE output?

Not for decisions without validation. UMAP output with min_dist = 0 plus HDBSCAN is a common, documented workflow, but check clusters in the original space.

#### The 30-second answer

t-SNE converts high-dimensional distances into neighbour probabilities using a Gaussian whose width per point is set by the perplexity, roughly the number of neighbours considered. It then finds 2-D positions whose similarities, measured with a heavy-tailed Student-t, match them by minimising KL divergence with gradient descent. The heavy tail solves the crowding problem, so clusters separate clearly. It preserves local neighbourhoods but not cluster sizes or between-cluster distances, depends on perplexity and seed, and is slow at scale. UMAP builds a fuzzy k-nearest-neighbour graph and optimises a cross-entropy layout with negative sampling; it's much faster, can transform new points and embed into any dimension, but shares the same reading caveats. PCA is the linear, global alternative and a common first step.

**Go further**

#### What not to say

- "These two clusters are far apart, so they're very different." Distances between clusters may mean nothing.

- "This cluster is bigger, so it's more diverse." Sizes are normalised away.

- "t-SNE is a dimensionality reduction for model features." It's for visualisation; it has no transform for new data.

**Key terms and sources**

Neighbour-preserving maps for visualising high-dimensional data: t-SNE's probabilities, perplexity and the Student-t trick; UMAP's graph layout; and how to read (and misread) the plots · built from van der Maaten & Hinton (2008), McInnes, Healy & Melville (2018), Wattenberg et al. on Distill (2016) and scikit-learn's manifold guide · checked 28 Oct 2026

#### Evidence

##### Runtime on MNIST (70,000 × 784), single core except FIt-SNE

UMAP

87 s

FIt-SNE

292 s

LargeVis

1,298 s

t-SNE (Multicore, Barnes–Hut)

1,450 s

McInnes et al., Table 3 [p. 38](https://arxiv.org/pdf/1802.03426#page=38); lower is better. On 200,000 Google News word vectors: UMAP 361 s, FIt-SNE 652 s, t-SNE 16,906 s. The full 3 million vectors took UMAP about 200 minutes versus "several days" for Multicore t-SNE. These are the authors' own benchmarks; FIt-SNE (a fast t-SNE) narrows the gap a lot.

##### Neighbourhood preservation (k-NN accuracy in the 2-D map, k = 100)

| Dataset | t-SNE | UMAP | PCA |
|---|---|---|---|
| MNIST | 0.967 | 0.967 | 0.462 |
| Fashion-MNIST | 0.818 | 0.790 | 0.564 |

Table 2, higher is better [p. 32](https://arxiv.org/pdf/1802.03426#page=32). Locally, t-SNE and UMAP are about equal (t-SNE slightly ahead on Fashion-MNIST at small k); UMAP pulls ahead at very large k (e.g. Shuttle, k = 3,200: 0.957 vs 0.828), i.e. on more global neighbourhoods.

##### This page's simulation (seed 1)

true size ratio B ÷ A

6.7

t-SNE, perplexity 30

1.06

t-SNE, perplexity 50

2.1

Illustrative: 150 simulated points, exact t-SNE.

#### Key terms

| Term | Meaning |
|---|---|
| **Perplexity** | t-SNE's effective number of neighbours per point (2entropy). |
| **Crowding problem** | High-D neighbourhoods don't fit in 2-D; the Student-t tail fixes it. |
| **KL divergence** | t-SNE's objective; punishes separating true neighbours. |
| **Early exaggeration** | Inflate P early so clusters form. |
| **n_neighbors / min_dist** | UMAP's locality and packing knobs. |
| **Negative sampling** | Push random pairs apart instead of normalising over all pairs. |

#### What this page is built from

1. L. van der Maaten & G. Hinton, "Visualizing data using t-SNE", _JMLR_ 9, 2008 (t-SNE, crowding problem, Student-t, early exaggeration).

2. L. McInnes, J. Healy & J. Melville, "UMAP: Uniform Manifold Approximation and Projection for Dimension Reduction", [arXiv:1802.03426](https://arxiv.org/abs/1802.03426) (algorithm, Tables 2–3, weaknesses, initialisation note).

3. M. Wattenberg, F. Viégas & I. Johnson, ["How to Use t-SNE Effectively"](https://distill.pub/2016/misread-tsne/), Distill, 2016.

4. scikit-learn, [Manifold learning: t-SNE](https://scikit-learn.org/stable/modules/manifold.html#t-sne) (definition, perplexity, non-convexity, Barnes–Hut, PCA init).

5. umap-learn docs, [Using UMAP for clustering](https://umap-learn.readthedocs.io/en/latest/clustering.html) (min_dist = 0, HDBSCAN results, caveats).

6. D. Kobak & G. Linderman, "Initialization is critical for preserving global data structure in both t-SNE and UMAP", _Nature Biotechnology_, 2021 (cited as [29] in the UMAP paper's bioRxiv version).

Customer data is simulated with fixed seeds; t-SNE runs live in your browser (exact gradient, 700 iterations).
