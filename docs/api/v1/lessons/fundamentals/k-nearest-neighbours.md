# k-Nearest Neighbours

> No training at all: how can copying your neighbours work, and when does it fail?

- Track: Fundamentals › Classical ML › Other classic classifiers
- Type: Concept · 30 min
- Page: https://aimlrounds.com/tracks/fundamentals/k-nearest-neighbours/
- Before this: Vectors, Dot Products & Cosine Similarity (`fundamentals/vectors-and-cosine-similarity`), Missing Values & Feature Scaling (`fundamentals/missing-values-and-scaling`)
- Related: RAG End to End (`ai-engineering/rag-end-to-end`)
- Quiz topic: `clf`
- Sources checked: 2026-10-28 · Text last changed: 2026-11-20 · Version: c0e881cad1

## Intuition

### The situation

You want to automate an inspector who judges a new part by recalling similar ones. Your first version, with k = 1, scores 100% on training data. The interviewer asks:

> How does k-NN make a prediction, and what does k control?

**Running example:** the same factory as the SVM lesson: two sensor readings per part, pass or fail, with a curved boundary between the classes (simulated "two moons", 120 training parts, 30% noise). Test accuracy uses 1,000 fresh parts. Every k-NN on this page runs live in your browser by brute-force search.

#### "This part looks like those parts"

An experienced inspector doesn't fit equations. They look at a new part and recall similar ones they've seen: "readings like these usually failed". k-NN is that habit written as an algorithm. It needs no training, makes no assumption about the shape of the boundary, and can follow a curved boundary that a linear model can't. The price is paid at prediction time, and in the choice of what "similar" means.

### The idea

Think of judging a new part by polling the most similar parts you've seen. Ask just one, and an odd neighbour can mislead you. Ask too many, and you're polling parts that aren't similar at all.

[Figure: A new part in the centre with a circle around its five nearest neighbours. Three vote pass and two vote fail, so it's predicted as pass.]

_Illustrative. The answer can change with k, so you pick k by validation._

### Play

**Try to break it.** Start at k = 1, move to about 15, then push k as high as it goes. Watch the shading and the test accuracy.

#### k is a bias–variance dial

Shade = share of the k neighbours voting pass. k = 1: islands around noisy parts. k ≈ 15: follows the moons. k = 119 (all but one training part): the vote loses all local shape and test accuracy falls to 67%.

Small k: low bias, high variance (the boundary jumps with each noisy point). Large k: high bias (the vote reaches into the other moon). Test accuracy on this data peaks at k = 13–15 (89.9% and 89.7%) and drops to 79.1% at k = 61. Pick k by cross-validation; for two classes, use odd k to avoid tied votes (with k = 4, 71 of the 1,000 test parts got an exact 2–2 tie).

**Now say why:** why does accuracy on new parts rise and then fall, when training accuracy starts at 100%?

## Maths

### Maths

#### In one breath

k-NN doesn't learn a model at all. It stores the training set, and to classify a new point it finds the **k closest** stored points and takes a **vote** (or an average, for regression). Small k memorises noise; large k blurs the boundary; you pick k by cross-validation. Because everything is a distance, **feature scaling** is not optional, and in **high dimensions** all distances start to look alike, so "nearest" stops meaning much. Prediction is the expensive part (search the whole set), which is why KD-trees, ball trees and, at scale, approximate nearest-neighbour indexes (the engines behind vector search and RAG) exist. What you'll be able to do after this: explain the bias–variance effect of k, show why scaling matters with numbers, state the Cover–Hart bound, explain distance concentration, and connect k-NN to vector databases.

#### A distance, a neighbourhood, a vote

$$ {d(x, z)} = \Bigl({\sum_{j=1}^{D} |x_j - z_j|}^{{p}}\Bigr)^{1/p} $$

- **distance**: How far query x is from stored point z. The whole method depends on this choice.

- **over every feature**: Each feature’s difference contributes. A feature measured in big units contributes big differences; more on that in the scaling section.

- **the power p**: p = 2: Euclidean (straight line), the default. p = 1: Manhattan (city blocks), a bit more robust to one large difference. scikit-learn’s default metric is Minkowski with p = 2.

Then the prediction is a vote among the k nearest stored points. Read as a probability, it's simply a share:

$$ {\hat P(y=c \mid x)} = \tfrac{1}{k}\,{\sum_{i \in N_k(x)}} {\mathbb{1}[y_i = c]} $$

scikit-learn: neighbours classification "is computed from a simple majority vote of the nearest neighbors of each point" [neighbors guide](https://scikit-learn.org/stable/modules/neighbors.html). For regression, average the neighbours' targets instead.

- **estimated chance of class c**: k-NN’s estimate of how likely the query belongs to class c.

- **the k neighbours**: N_k(x): the k stored points closest to x.

- **count the class-c ones**: Add 1 for each neighbour with label c. With k = 15, 11 pass votes means 11/15 ≈ 0.73.

1. A new part arrives (the diamond). We have its two sensor readings and thirteen stored parts with known labels.

2. k = 1: the single closest part failed, so predict fail.

3. k = 3: the circle grows to the three closest. Two passed, one failed: predict pass.

4. k = 5: two more neighbours, both failed. Now it's 3 fail vs 2 pass: predict fail.

5. Same data, same query, three answers. k is the one knob that matters most, and the sections below show how to set it.

#### Similar inputs have similar labels, locally

k-NN assumes only one thing: the label changes smoothly enough that nearby points usually share it. Everything else follows from making "nearby" meaningful: **how many** neighbours (k), **how much** each counts (weights), **what distance** (and on what feature scale), and **how many dimensions** the distance lives in. The sections below take those one at a time.

##### A guarantee for the simplest version

Cover & Hart (1967): with infinitely many training points, the 1-NN error R is at most twice the best possible (Bayes) error R*. For two classes, R* ≤ R ≤ 2R*(1 − R*). "In this sense, it may be said that half the classification information in an infinite sample set is contained in the nearest neighbor" [IEEE Trans. Inf. Theory 13](https://doi.org/10.1109/TIT.1967.1053964). It's an asymptotic result: with finite data, and especially in high dimensions, it says nothing about how close you are.

#### Let closer neighbours count more

scikit-learn's `weights="distance"` "assigns weights proportional to the inverse of the distance from the query point" [neighbors guide](https://scikit-learn.org/stable/modules/neighbors.html). Switch it on in the Play lab, in the Intuition tab. Two effects to notice:

- **It makes large k forgiving.** At k = 61, test accuracy rises from 79.1% (uniform) to 86.2% (weighted): far neighbours from the other moon count for little.

- **Training accuracy becomes 100% at every k.** Each training point is at distance 0 from itself, with infinite weight. So with weighted votes, training accuracy tells you nothing; only validation does.

At small k, weighting changed little here (k = 5: 89.3% uniform vs 87.6% weighted). It's not a free win; treat it as a hyperparameter.

#### Change the units, change the neighbours

Suppose sensor 1 is logged in centimetres instead of metres: every value ×100. Nothing about the parts changed, but now a 1 cm difference on sensor 1 counts as much as a whole unit on sensor 2. Distance is dominated by sensor 1, and sensor 2 is effectively ignored.

The plot always shows the original readings; only the distance used inside k-NN changes. In centimetres the boundary turns into vertical stripes: only sensor 1 decides.

Test accuracy at k = 15 falls from **89.7%** to **71.3%** after the unit change, and standardising (subtract the mean, divide by the standard deviation, fitted on training data) brings it back to **88.3%**. Standardisation makes every feature equally important by default, which is a choice too: if you know a feature matters more, weight it on purpose.

#### In many dimensions, everyone is about equally far

Take 500 random points in a D-dimensional cube and one random query. In 2-D, the farthest point is dozens of times farther than the nearest. In 1,000-D, the farthest is only about 11% farther. When the nearest and the farthest are nearly the same distance away, "nearest" carries little information.

Histogram for one query: each distance divided by that query's nearest distance. As D grows, the whole histogram squeezes against 1.

Beyer, Goldstein, Ramakrishnan & Shaft (1999) proved this: under broad conditions, as dimensionality grows the distance to the nearest neighbour approaches the distance to the farthest one [ICDT 1999](https://doi.org/10.1007/3-540-49257-7_15). It applies to i.i.d. features like these random cubes. Real data usually lives near a much lower-dimensional surface (images, text embeddings), which is why nearest-neighbour search on **learned embeddings** still works well. The practical moves: reduce dimensions (PCA, embeddings), select features, or use a distance that suits the data (cosine for embeddings). scikit-learn also notes that KD-trees lose their speed advantage as D grows.

## In practice

### In practice

#### Lazy learning, and how the search is made fast

scikit-learn calls k-NN "a type of instance-based learning or non-generalizing learning: it does not attempt to construct a general internal model, but simply stores instances of the training data" [neighbors guide](https://scikit-learn.org/stable/modules/neighbors.html). So "training" is just indexing, and the work moves to query time:

| Search method | Cost | When |
|---|---|---|
| **Brute force** | Compare with all N points: O(D·N) per query | Small N, high D, sparse data. scikit-learn's `auto` picks it when D > 15 or k ≥ N/2 |
| **KD-tree** | About O(D log N) per query for small D | "very fast for low-dimensional (D < 20)" searches; for larger D "the cost increases to nearly O[DN]" |
| **Ball tree** | About O(D log N) | Nested hyperspheres; "can out-perform a KD-tree in high dimensions", depending on the data |
| **Approximate NN** (HNSW, IVF, product quantisation; FAISS and vector databases) | Sub-linear, trades a little recall for big speed-ups | Millions to billions of embedding vectors: semantic search, recommendations, RAG retrieval |

First three rows: scikit-learn's neighbors guide [docs](https://scikit-learn.org/stable/modules/neighbors.html). Approximate methods: ; see the RAG at scale lesson for how retrieval uses them.

#### k-NN, end to end

1. **Scale** features (StandardScaler or a domain weighting), fitted on training data only.

2. **Reduce dimensions** if D is large (PCA, or use embeddings from a model).

3. **Choose the metric:** Euclidean for scaled numeric features, cosine for embeddings, Hamming/Jaccard for binary sets.

4. **Cross-validate k** (odd for binary) and **weights** (uniform vs distance).

5. **Pick the index**: brute force for small N, KD/ball tree for low D, approximate NN (FAISS, HNSW) for millions of vectors.

#### When to use it

##### Use k-NN when

- A quick, assumption-free baseline on small, low-dimensional data

- You have good embeddings: similarity search, "more like this", recommendations

- Data changes constantly and retraining is awkward

##### Reach for something else when

- Many raw features or many irrelevant ones: trees or linear models

- Strict latency on large N without an ANN index

- You need a compact model or feature effects

### The answer that sounds right

#### "Use k = 1: the closest example is the best evidence"

With k = 1 every training part is its own nearest neighbour, so training accuracy is always 100%. That number is meaningless. On our noisy moons, 1-NN scores **85.8%** on new parts, while k = 15 scores **89.7%**. The single nearest neighbour is often one of the noisy parts, and 1-NN copies its mistake into a little island of wrong predictions around it. scikit-learn: "a larger k suppresses the effects of noise, but makes the classification boundaries less distinct" [neighbors guide](https://scikit-learn.org/stable/modules/neighbors.html).

#### Caveats

##### Strengths

- No training; add new data instantly

- Any boundary shape; naturally multi-class

- Easy to explain: "these similar cases"

- The same machinery powers retrieval, recommendations and anomaly detection

##### Weaknesses

- Slow, memory-hungry prediction: the model is the dataset

- Needs scaling and a sensible metric

- Breaks down with many irrelevant or raw high-dimensional features

- Imbalanced classes: the majority dominates votes (weight or resample)

## Say it

### How does k-NN make a prediction, and what does k control?

#### The interviewer pushes further

Follow-up 1 of 6

What happens at k = 1 and k = N?

k = 1: zero training error, a jagged boundary, high variance. k = N: predicts the majority class everywhere, maximum bias.

Follow-up 2 of 6

Why scale features?

Distances add up feature differences, so a feature with a big numeric range dominates. On this page, logging one feature in centimetres dropped test accuracy from 89.7% to 71.3%; standardising restored 88.3%.

Follow-up 3 of 6

Explain the curse of dimensionality for k-NN.

As D grows, data becomes sparse and, for i.i.d. features, the ratio of farthest to nearest distance tends to 1 (Beyer et al. 1999), so the nearest neighbour is barely nearer than a random point. Fix with dimensionality reduction, feature selection, or embeddings where data lies on a low-dimensional manifold.

Follow-up 4 of 6

How is k-NN related to vector databases and RAG?

RAG retrieval is k-NN over embedding vectors with cosine or dot-product similarity. Exact search is O(N·D), so vector databases use approximate indexes (HNSW graphs, IVF clusters, product quantisation) that trade a little recall for orders-of-magnitude speed.

Follow-up 5 of 6

Training and prediction complexity?

Training O(1) for brute force (just store), or about O(D·N log N) to build a tree. Prediction O(D·N) brute force per query, about O(D log N) with a tree in low D.

Follow-up 6 of 6

What does Cover & Hart say?

As N → ∞, 1-NN's error is at most twice the Bayes error (precisely 2R*(1 − R*) for two classes). It's an asymptotic guarantee, not a finite-sample one.

#### The 30-second answer

k-NN stores the training data and predicts a new point by finding its k nearest neighbours under a distance like Euclidean and taking a majority vote, or the average for regression. There's no training; the cost is at prediction time, O(N·D) by brute force, reduced with KD-trees or ball trees in low dimensions or approximate indexes like HNSW at scale. k trades variance for bias and is chosen by cross-validation. Because it's distance-based you must scale features, and in high dimensions distances concentrate so neighbours become less meaningful, so you reduce dimensions or work in a learned embedding space.

**Go further**

#### What not to say

- "k-NN has no hyperparameters." k, the weighting, the metric and the scaling all matter.

- "Training accuracy shows a good k." At k = 1, or with distance weights, it's always 100%.

- "k-NN works fine in any dimension." Not on raw high-dimensional features.

**Key terms and sources**

Lazy learning, choosing k, distance weighting, feature scaling, the curse of dimensionality, KD-trees and vector search · built from Cover & Hart (1967), Beyer et al. (1999) and scikit-learn's neighbors guide · checked 28 Oct 2026

#### What's proven, and what our lab shows

##### Test accuracy on the moons (this page's labs, k-NN uniform vote)

k = 1

85.8%

k = 15

89.7%

k = 61

79.1%

k = 15, sensor 1 in cm

71.3%

k = 15, cm then standardised

88.3%

Simulated data, 120 training and 1,000 test parts; for comparison, the RBF SVM in the previous lesson reached 89.3% on the same data. Illustrative, not a benchmark.

##### Proven: 1-NN is within 2× of optimal, asymptotically

Cover & Hart 1967, as in The core idea. With k growing (k → ∞ while k/N → 0), k-NN is consistent: it converges to the Bayes error (Stone, 1977). Both are statements about the infinite-data limit.

##### Proven: distances concentrate in high dimensions

Beyer et al. 1999, as in the curse of dimensionality section. In our cube simulation, the farthest ÷ nearest ratio (mean of 20 queries) fell from about 87 in 2-D to 3.6 in 10-D, 1.4 in 100-D and 1.11 in 1,000-D.

#### Key terms

| Term | Meaning |
|---|---|
| **Instance-based / lazy learning** | Store the data; do the work at prediction time. |
| **k** | Number of neighbours that vote. Small: variance. Large: bias. |
| **Minkowski p** | p = 2 Euclidean, p = 1 Manhattan. |
| **Distance weighting** | Votes weighted by 1/distance. |
| **Curse of dimensionality** | In high D, data is sparse and distances concentrate. |
| **KD-tree / ball tree** | Space-partitioning indexes for exact search in low D. |
| **ANN (HNSW, IVF, PQ)** | Approximate nearest-neighbour indexes used in vector databases. |

#### What this page is built from

1. T. Cover & P. Hart, "Nearest neighbor pattern classification", _IEEE Trans. Information Theory_ 13(1), 1967, [doi:10.1109/TIT.1967.1053964](https://doi.org/10.1109/TIT.1967.1053964) (the 2× Bayes bound).

2. K. Beyer, J. Goldstein, R. Ramakrishnan & U. Shaft, "When is 'nearest neighbor' meaningful?", ICDT 1999, [doi:10.1007/3-540-49257-7_15](https://doi.org/10.1007/3-540-49257-7_15) (distance concentration).

3. scikit-learn, [Nearest Neighbors user guide](https://scikit-learn.org/stable/modules/neighbors.html) (instance-based learning, k, weights, brute/KD/ball tree costs, algorithm choice).

4. C. Stone, "Consistent nonparametric regression", _Annals of Statistics_, 1977 (k-NN consistency; background).

5. Y. Malkov & D. Yashunin, "Efficient and robust approximate nearest neighbor search using HNSW graphs", [arXiv:1603.09320](https://arxiv.org/abs/1603.09320) (approximate search; background).

All datasets are simulated with fixed seeds; every result on this page is computed live in your browser.
