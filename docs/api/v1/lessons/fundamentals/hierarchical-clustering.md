# Hierarchical Clustering

> What if you don't know k? Build every grouping at once and cut the tree.

- Track: Fundamentals › Classical ML › Unsupervised learning
- Type: Concept · 25 min
- Page: https://aimlrounds.com/tracks/fundamentals/hierarchical-clustering/
- Before this: k-Means Clustering (`fundamentals/k-means`)
- Quiz topic: `unsup`

## Intuition

### The situation

Marketing sees three customer segments today, but one might split into weekday and weekend users. You don't want to commit to one number of groups. The interviewer asks:

> How does hierarchical clustering work, and how do you pick the number of clusters?

**Running example:** the same food-delivery customers as the k-means lesson (standardised orders per month and basket size, three hidden segments). The dendrogram lab uses 36 of them (12 per segment) so every leaf is visible; the linkage lab uses all 180, plus a "two moons" shape to show where linkages disagree.

#### "How many segments?" depends on how closely you look

At a glance there are three kinds of customers. Look closer and the "frequent small orders" group might split into weekday and weekend users. k-means makes you pick k up front and gives one answer. Hierarchical clustering builds **all** the answers at once, from n clusters of one down to a single cluster, as a tree you can cut at any level.

### The idea

Think of building a family tree from the bottom up. Everyone starts alone, then the closest pairs join, then the closest groups, until one family remains. Cut the tree at any height, and you get that many groups.

[Figure: A tree of merges over six customers. A dashed cut across the tree gives two clusters, and a lower cut would give more.]

_Illustrative. Higher joins mean the groups were further apart._

### Play

**Try to break it.** Move the cut height up and down and watch the cluster count. Then switch from Ward to single linkage.

#### Read a dendrogram and choose the cut

Vertical lines are clusters; the dashed line is your cut. The longest vertical stretch with no merge is where the data "wants" to be cut: clusters that stay separate over a wide range of heights.

With Ward linkage on these 36 customers, the last merges happen at heights 2.07, 2.47, then **9.45** and 10.13: a huge jump between 3 clusters and 2. Any cut in that gap gives the three hidden segments exactly (ARI 1.0). Heights aren't comparable across linkages (Ward heights are on a variance scale), so compare the _shape_ of the tree, not the numbers.

**Now say why:** why does the same data give such a different tree under single linkage?

## Maths

### Maths

#### In one breath

Start with every customer as its own cluster, then repeatedly **merge the two closest clusters** until one is left. Record each merge and its height (how far apart the merged clusters were) and you get a **dendrogram**, a tree of every possible grouping. You choose the number of clusters afterwards by **cutting** the tree, ideally where there's a big jump in merge height. What "closest clusters" means is the **linkage**: single (nearest pair) follows chains and odd shapes but snowballs; complete (farthest pair) and average are in between; **Ward** (smallest increase in variance) gives even, round clusters like k-means. The cost is O(n²) memory and up to O(n³) time. What you'll be able to do after this: read a dendrogram, choose a cut, explain the four linkages and when each fails, and compare hierarchical clustering with k-means.

#### Merges, heights and the dendrogram

1. Five customers, each its own cluster. On the right, an empty dendrogram: leaves at the bottom, merge height going up.

2. The closest pair, A and B, merges first. Draw a bracket at the height equal to their distance.

3. Next closest: C and D, a little farther apart, so a slightly higher bracket.

4. Now the closest clusters are {A, B} and {C, D}. How far apart two _groups_ are is the linkage choice (see below). They merge, higher up.

5. Finally E, far from everyone, joins at the top. n points always take exactly n − 1 merges.

6. A horizontal cut crosses three vertical lines, giving three clusters: {A, B}, {C, D}, {E}. A higher cut gives two; a lower one, five.

#### Greedy merging under a chosen cluster distance

Agglomerative clustering is greedy: each merge is the best one available now and is never undone. Everything about the result follows from one choice: how to measure the distance between two clusters A and B. The four standard linkages:

$$ {\min_{a,b} d(a,b)} \qquad {\max_{a,b} d(a,b)} \qquad {\tfrac{1}{|A||B|}\textstyle\sum_{a,b} d(a,b)} \qquad {\tfrac{|A||B|}{|A|+|B|}\lVert \mu_A - \mu_B\rVert^2} $$

scikit-learn: Ward "minimizes the sum of squared differences within all clusters. It is a variance-minimizing approach"; complete "minimizes the maximum distance between observations of pairs of clusters"; average uses "the average of the distances between all observations of pairs of clusters"; single uses "the distance between the closest observations of pairs of clusters" [clustering guide](https://scikit-learn.org/stable/modules/clustering.html#hierarchical-clustering). Ward (1963) introduced the variance criterion.

- **single: closest pair**: Distance between the two nearest members. Follows chains and curved shapes; snowballs through bridges and noise.

- **complete: farthest pair**: Distance between the two farthest members. Prefers compact clusters of similar diameter; sensitive to outliers.

- **average: mean of all pairs**: Average distance over every pair, one from each cluster. A middle ground; works with any distance metric.

- **Ward: added variance**: How much the total within-cluster sum of squares grows if A and B merge. The same objective as k-means, so it gives round, even-sized clusters. Euclidean only.

#### No linkage wins everywhere

| Linkage | Customers (ARI, sizes) | Two moons (ARI) |
|---|---|---|
| Ward | 0.98 · 60/61/59 | 0.42 |
| average | 0.98 · 60/61/59 | 0.42 |
| complete | 0.98 · 60/61/59 | 0.64 |
| single | 0.57 · 60/119/1 | 1.00 |

Single linkage is the only one that traces the curved moons (it just follows the chain of nearest neighbours), and the only one that fails on the noisy round segments, for the same reason. Ward, average and complete prefer compact groups: good segments, wrong moons. This trade-off is why density-based methods (DBSCAN, HDBSCAN) exist: they keep single linkage's shape-following but add a density threshold that stops one bridge point from chaining clusters together. HDBSCAN is, in fact, single linkage on a density-adjusted distance.

## In practice

### In practice

#### Agglomerative (bottom-up) is the standard

Hierarchical clustering can be **agglomerative** (start with singletons, merge) or **divisive** (start with everything, split). Agglomerative is what libraries implement: scikit-learn's `AgglomerativeClustering` and SciPy's `scipy.cluster.hierarchy.linkage`, which also draws dendrograms. It's popular where the hierarchy itself is meaningful: biology (gene expression heatmaps, taxonomies), document and product catalogues, and customer segmentation where marketing wants coarse and fine levels.

#### O(n²) memory, up to O(n³) time

The straightforward algorithm keeps an n × n distance matrix (O(n²) memory: 100,000 points means 1010 distances, about 80 GB as doubles) and searches it at each of n − 1 merges. Faster algorithms exist for specific linkages (O(n²) time for single linkage via a minimum spanning tree, for example), but the memory still limits plain hierarchical clustering to tens of thousands of points. scikit-learn: agglomerative clustering "is computationally expensive when no connectivity constraints are added between samples: it considers at each step all the possible merges"; with a connectivity matrix (only merge neighbours, e.g. a k-nearest-neighbour graph or adjacent pixels) it "can also scale to large number of samples" [clustering guide](https://scikit-learn.org/stable/modules/clustering.html#hierarchical-clustering). For very large data: cluster a sample, or run k-means into a few hundred micro-clusters first and build the hierarchy on their centroids.

#### The whole recipe

1. **Scale** features; choose a distance (Euclidean for Ward; any metric for average/complete/single).

2. **Pick a linkage:** Ward for even, round groups; average for non-Euclidean distances; single only for chain-like shapes on clean data.

3. **Build the full tree** and plot the dendrogram.

4. **Cut** at a big jump in height (or at a distance threshold that means something), and check the clusters make sense.

5. **Mind the size:** sample or pre-cluster beyond ~10–20k points.

#### When to use it

##### Use hierarchical clustering when

- The hierarchy itself is useful (taxonomies, coarse and fine segments)

- You don't know k and want to explore

- n is in the thousands and you have a meaningful custom distance

##### Reach for something else when

- Hundreds of thousands of points: k-means, mini-batch, HDBSCAN

- Noisy data with arbitrary shapes: HDBSCAN

- You need to score new points often: k-means or GMM

### The answer that sounds right

#### "Merge the two closest points, always"

The simplest definition of distance between clusters is the distance between their two closest members (single linkage). It sounds natural, and it can follow curved shapes. But one stray customer sitting between two segments is enough to bridge them: once the bridge merges, the two segments become one. On all 180 customers, single linkage cut at 3 clusters gives sizes **60 / 119 / 1**: one real segment, two segments chained together, and a lone outlier as the "third cluster" (ARI 0.57). scikit-learn calls single linkage "the most brittle linkage option" for this "rich getting richer" effect [clustering guide](https://scikit-learn.org/stable/modules/clustering.html#hierarchical-clustering).

#### Caveats

##### Strengths

- No k needed up front; one tree gives every k

- The dendrogram is a readable picture of the structure

- Deterministic (no random starts)

- Average/complete/single work with any distance, even precomputed

##### Weaknesses

- O(n²) memory, slow beyond tens of thousands of points

- Greedy: an early bad merge is never undone

- Results depend heavily on linkage

- No natural way to assign new points (unlike k-means' nearest centroid)

## Say it

### How does hierarchical clustering work, and how do you pick the number of clusters?

#### The interviewer pushes further

Follow-up 1 of 4

How do you choose where to cut?

Look for the largest vertical gap in the dendrogram (clusters that persist across many heights), use a distance threshold with domain meaning, or pick k and validate with silhouette or stability.

Follow-up 2 of 4

Single vs complete vs average vs Ward?

Single: closest pair, chaining, finds elongated shapes, brittle to noise. Complete: farthest pair, compact clusters, outlier-sensitive. Average: compromise, works with any metric. Ward: minimal variance increase, even sizes, Euclidean only.

Follow-up 3 of 4

Hierarchical vs k-means?

Hierarchical needs no k up front, is deterministic and gives a tree, but costs O(n²) memory and can't easily assign new points. k-means is fast and scalable but needs k, restarts, and round clusters.

Follow-up 4 of 4

How do you scale it?

Connectivity constraints (kNN graph), sampling, or pre-clustering into micro-clusters (BIRCH or k-means) and running hierarchy on those.

#### The 30-second answer

Agglomerative hierarchical clustering starts with every point as its own cluster and repeatedly merges the two closest clusters, recording each merge height in a dendrogram. You get flat clusters by cutting the tree, usually at a large gap in merge heights, so you don't fix k in advance. The linkage defines cluster distance: single uses the closest pair and can follow arbitrary shapes but chains through noise; complete uses the farthest pair; average the mean pairwise distance; Ward merges the pair that least increases within-cluster variance and gives k-means-like round clusters. It's deterministic but needs O(n²) memory and up to O(n³) time, so it suits small to medium datasets.

**Go further**

#### What not to say

- "Merge heights mean the same across linkages." Ward heights are on a different scale.

- "Hierarchical clustering scales like k-means." The distance matrix is O(n²).

- "Single linkage is the default." Ward is scikit-learn's default.

**Key terms and sources**

Agglomerative clustering, dendrograms, single/complete/average/Ward linkage, cutting the tree · built from scikit-learn's clustering guide, SciPy's hierarchy docs and Ward (1963) · checked 28 Oct 2026

#### Evidence

##### Cluster sizes on the 180 customers (k = 3)

Ward: largest cluster

61

single: largest cluster

119

single: smallest cluster

1

True segments: 60 each. Illustrative simulation; matches scikit-learn's description: "single linkage is the worst strategy, and Ward gives the most regular sizes" [clustering guide](https://scikit-learn.org/stable/modules/clustering.html#hierarchical-clustering).

#### Key terms

| Term | Meaning |
|---|---|
| **Agglomerative / divisive** | Bottom-up merging / top-down splitting. |
| **Dendrogram** | Tree of merges; vertical position = merge height. |
| **Linkage** | The rule for distance between clusters. |
| **Cut** | A height (or k) that turns the tree into flat clusters. |
| **Connectivity constraint** | Only allow merges between neighbours; speeds it up and respects structure. |

#### What this page is built from

1. scikit-learn, [Clustering user guide: hierarchical clustering](https://scikit-learn.org/stable/modules/clustering.html#hierarchical-clustering) (linkage definitions, rich-get-richer behaviour, connectivity constraints, cost).

2. SciPy, [scipy.cluster.hierarchy](https://docs.scipy.org/doc/scipy/reference/cluster.hierarchy.html) (linkage matrix format, dendrogram, fcluster).

3. J. H. Ward, "Hierarchical grouping to optimize an objective function", _JASA_ 58, 1963 (Ward's criterion; background).

4. R. Campello, D. Moulavi & J. Sander, "Density-based clustering based on hierarchical density estimates", PAKDD 2013 (HDBSCAN's link to single linkage; background).

Customer data is simulated with fixed seeds; every tree on this page is built live in your browser (Lance–Williams updates).
