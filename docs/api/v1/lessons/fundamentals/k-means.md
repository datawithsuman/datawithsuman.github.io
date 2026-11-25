# k-Means Clustering

> How do you split customers into groups when nobody has labelled them?

- Track: Fundamentals › Classical ML › Unsupervised learning
- Type: Concept · 30 min
- Page: https://aimlrounds.com/tracks/fundamentals/k-means/
- Quiz topic: `unsup`
- Sources checked: 2026-10-28 · Text last changed: 2026-11-20 · Version: 8be44b1186

## Intuition

### The situation

Marketing wants three campaigns, one per kind of customer, but no column says which kind each customer is. The interviewer asks:

> How does k-means work, and does it always find the best clustering?

**Running example (shared by the unsupervised lessons):** a food-delivery app wants to group its customers without any labels. Each customer has two numbers, orders per month and average basket size, both standardised (mean 0, standard deviation 1). The simulated base has 180 customers drawn from three hidden segments: occasional small orders, frequent small orders, and occasional big orders. The algorithm never sees the segment; we use it only to score the result (adjusted Rand index, ARI: 1 = perfect agreement, 0 = chance).

#### Group customers when nobody has labelled them

Marketing wants three campaigns, one per kind of customer. There's no column saying which kind each customer is; that's the thing we want to discover. Clustering finds groups of points that are close to each other and far from other groups. k-means is the simplest and most used clustering method: fast, easy to explain, and the baseline every other method is compared with.

### The idea

Think of opening three shops in a town. Each customer goes to their nearest shop. Then each shop moves to the middle of its customers. Customers re-choose, shops move again, and you repeat until nothing changes.

[Figure: Three groups of customers, each with a marked centre in the middle of its group.]

_Illustrative. The assign and move steps repeat until the groups stop changing._

### Play

**Try to break it.** Run start A until no points switch, and note the inertia. Then reset and run starts B and C.

#### Step through Lloyd's algorithm on the customers

k = 3, random starting centroids (three random customers). Grey points: not assigned yet. Watch the inertia fall at every step until nothing switches.

**Now say why:** why doesn't every start reach the same answer, and how would you protect against a bad one?

## Maths

### Maths

#### In one breath

k-means splits data into k groups by placing k **centroids** and repeating two steps: assign every point to its nearest centroid, then move each centroid to the mean of its points. Each step lowers the **inertia** (total squared distance to centroids), so it always converges, but only to a **local** minimum that depends on where you started, which is why **k-means++** seeding and several restarts matter. You must choose k yourself (elbow, silhouette, or business sense), and because it measures squared Euclidean distance to a centre, it assumes round, similar-sized clusters: elongated, curved or uneven groups break it. What you'll be able to do after this: run Lloyd's algorithm by hand, explain why it converges and why it gets stuck, pick k with two methods, and name the shapes k-means can't handle.

#### Centroids and inertia

Describe each group by its **centroid**, the average customer in it. A good grouping keeps every customer close to their own group's centroid. k-means measures this with the inertia, the within-cluster sum of squares:

$$ {J} = {\sum_{j=1}^{k}}\ {\sum_{x_i \in C_j}}\ {\lVert x_i - \mu_j \rVert^2} $$

scikit-learn: k-means works by "minimizing a criterion known as the inertia or within-cluster sum-of-squares" [clustering guide](https://scikit-learn.org/stable/modules/clustering.html#k-means).

- **inertia**: One number for the whole clustering. Lower is better; 0 only if every point sits exactly on its centroid.

- **over the k clusters**: Add up the cost of each cluster.

- **over its members**: Every point x_i assigned to cluster j.

- **squared distance to the centroid**: Squared Euclidean distance from the point to its cluster’s centroid μ_j. Squaring punishes far points heavily.

#### Alternate two easy problems

Minimising inertia over groupings and centroids together is hard. But each half is easy on its own:

1. Nine customers and two starting centroids (◆), placed badly on purpose.

2. **Assign:** with centroids fixed, the best grouping is obvious: each point joins its nearest centroid. The middle customer joins the right one.

3. **Update:** with the grouping fixed, the best centroid is obvious too: the mean of its points (the mean minimises the sum of squared distances).

4. Assign again with the new centroids: the middle customer is now closer to the left centroid and switches. Update again.

5. Neither step can increase inertia, and there are finitely many groupings, so this always stops. That's Lloyd's algorithm.

scikit-learn: "Given enough time, K-means will always converge, however this may be to a local minimum. This is highly dependent on the initialization of the centroids" [clustering guide](https://scikit-learn.org/stable/modules/clustering.html#k-means). The algorithm is from Lloyd (1957 report, published 1982).

#### Local minima, and k-means++

A bad start can trap Lloyd's algorithm: two centroids share one true group while another centroid sits between two groups, and no single assign/update step can fix it. **k-means++** (Arthur & Vassilvitskii, 2007) picks the first centroid at random, then each next one with probability proportional to its **squared distance** from the nearest centroid chosen so far, so starts are spread out.

Five well-separated groups of 40 customers each, k = 5, a single run per seed. Try seeds until you find a stuck run: one big group split in two and two groups merged.

On this data, a single run with random starts got stuck in **15 of 50** seeds; with k-means++, in **6 of 50**. The worst random run had inertia 697, against 53.4 for the right answer. The fix that always works is cheap: run several starts and keep the lowest inertia (scikit-learn's `n_init`). Arthur & Vassilvitskii proved k-means++ seeding alone is expected to be within a factor of 8(ln k + 2), i.e. O(log k), of the optimal inertia [SODA 2007](https://theory.stanford.edu/~sergei/papers/kMeansPP-soda.pdf).

#### Elbow and silhouette

Inertia always falls as k grows (k = n gives inertia 0), so you can't pick k by minimising it. Two common aids:

- **Elbow:** plot inertia against k and look for the bend where adding a cluster stops helping much.

- **Silhouette:** for each point, a = mean distance to its own cluster, b = mean distance to the nearest other cluster; s = (b − a) / max(a, b), between −1 and 1. Average over points; higher means tighter, better-separated clusters.

On the customers, inertia drops from 583 (k = 1) to 314 (k = 2) to **97** (k = 3), then only to 83 at k = 4: a clear elbow at 3. The silhouette peaks at k = 3 too (0.64). Real data is rarely this clean; often there's no sharp elbow, and the right k is the one the business can act on (three campaigns, not seven). scikit-learn's caution about the silhouette: it is generally higher for convex clusters than for density-based ones, so don't use it to compare k-means with DBSCAN.

## In practice

### In practice

#### The clustering toolbox

| Method | Finds | You choose | Lesson |
|---|---|---|---|
| **k-means** | Round, similar-sized groups | k | this one |
| **Hierarchical** | A tree of nested groups | linkage, where to cut | next |
| **DBSCAN / HDBSCAN** | Any shape; marks noise | density (eps, min_samples) | DBSCAN |
| **Gaussian mixtures** | Elliptical groups, soft membership | k, covariance type | lesson 4 |

scikit-learn ships all of these with the same fit/predict interface [clustering guide](https://scikit-learn.org/stable/modules/clustering.html).

#### The whole recipe

1. **Scale** features (StandardScaler); consider PCA first if there are many.

2. **Fit** with k-means++ and several starts (`n_init`), for a range of k.

3. **Choose k** with the elbow and silhouette, then sanity-check that the clusters mean something to the business.

4. **Describe** each cluster by its centroid (in original units) and size.

5. **Check stability:** refit on a resample; clusters that change a lot aren't real.

Cost: each Lloyd iteration is O(n·k·d). For millions of rows, `MiniBatchKMeans` updates centroids from small random batches, trading a little inertia for big speed-ups [clustering guide](https://scikit-learn.org/stable/modules/clustering.html#mini-batch-k-means).

#### When to use it

##### Use k-means when

- You want a quick segmentation with a fixed number of groups

- Groups are roughly blob-shaped after scaling

- Data is large and you need speed

##### Reach for something else when

- Shapes are curved or density varies: DBSCAN/HDBSCAN

- You need probabilities of membership: GMM

- You want a hierarchy or don't know k: hierarchical clustering

### The answer that sounds right

#### "Just try every possible grouping and keep the best"

The number of ways to split 180 customers into 3 non-empty groups is about 3180 / 6, roughly 1085, more than the number of atoms in the observable universe. Finding the grouping with the lowest inertia exactly is NP-hard in general. So every practical method is a **heuristic** that finds a good grouping, not a guaranteed best one. k-means is the heuristic that won because each step is cheap and provably helps.

#### Round, similar-sized clusters only

Assigning each point to the nearest centre draws straight boundaries halfway between centroids (a Voronoi diagram). scikit-learn: "Inertia makes the assumption that clusters are convex and isotropic, which is not always the case. It responds poorly to elongated clusters, or manifolds with irregular shapes" [clustering guide](https://scikit-learn.org/stable/modules/clustering.html#k-means).

Same algorithm, best of 10 starts, true k given. Round groups: perfect. Moons: k-means cuts straight across both (ARI 0.21). Tilted groups: it slices them crosswise (ARI 0.62).

##### Also breaks on

- Groups of very different sizes or spreads (the boundary sits halfway, cutting into the big group)

- Unscaled features (one feature in rupees dominates the distance)

- Outliers (squared distance lets one far point drag a centroid)

- Very high dimensions: distances concentrate (see k-NN)

##### What to use instead

- Curved or noisy shapes: DBSCAN / HDBSCAN

- Elliptical or overlapping groups, soft membership: Gaussian mixtures

- Outliers: k-medoids or trimming

- High dimensions: reduce first with PCA

#### Caveats

##### Strengths

- Fast, simple, scales to millions (mini-batch)

- Centroids are easy to describe ("the average frequent small-basket customer")

- Assigning new points is instant

- A strong first baseline; also used for vector quantisation and as an initialiser (GMMs, IVF indexes in vector search)

##### Weaknesses

- You must pick k

- Local minima: needs k-means++ and restarts

- Assumes round, similar-sized clusters; sensitive to scale and outliers

- Every point is forced into a cluster; no notion of noise

## Say it

### How does k-means work, and does it always find the best clustering?

#### The interviewer pushes further

Follow-up 1 of 6

Why does k-means converge?

The assignment step minimises inertia for fixed centroids; the update step minimises it for fixed assignments (the mean minimises squared distance). Inertia never increases and there are finitely many assignments, so it stops, typically in a few dozen iterations.

Follow-up 2 of 6

How do you choose k?

Elbow on inertia, average silhouette, gap statistic, or BIC with a GMM, plus stability across resamples and whether the business can use that many groups.

Follow-up 3 of 6

What is k-means++?

Seeding that picks each new centroid with probability proportional to D(x)², the squared distance to the nearest chosen centroid. It spreads starts out and is O(log k)-competitive in expectation.

Follow-up 4 of 6

When does k-means fail?

Non-convex shapes, different cluster sizes or densities, unscaled features, outliers, and high dimensions. Also it always assigns every point; there's no noise label.

Follow-up 5 of 6

k-means vs GMM?

k-means is like a GMM with equal, spherical covariances and hard assignments in the zero-variance limit. GMMs learn shape (covariance), give soft probabilities, and can be compared by BIC.

Follow-up 6 of 6

Complexity?

O(n·k·d) per iteration; usually few iterations. Mini-batch k-means for very large n.

#### The 30-second answer

k-means partitions data into k clusters by minimising the within-cluster sum of squared distances to the centroids. Lloyd's algorithm alternates two steps: assign each point to its nearest centroid, then set each centroid to the mean of its points. Each step can only lower the objective, so it converges, but to a local minimum that depends on initialisation, so we use k-means++ seeding and multiple restarts. You choose k with the elbow method, silhouette score, or domain needs. It assumes roughly spherical, similar-sized clusters and needs scaled features; for other shapes use DBSCAN or Gaussian mixtures.

**Go further**

#### What not to say

- "k-means finds the optimal clustering." It finds a local minimum.

- "Pick the k with the lowest inertia." That's always k = n.

- "k-means works on any distance." The mean update is tied to squared Euclidean distance; for other distances use k-medoids.

**Key terms and sources**

Inertia, Lloyd's algorithm, k-means++, choosing k (elbow, silhouette), and where k-means fails · built from scikit-learn's clustering guide, Lloyd (1982) and Arthur & Vassilvitskii (2007) · checked 28 Oct 2026

#### Evidence

##### This page's simulations

stuck runs, random start (of 50)

15

stuck runs, k-means++ (of 50)

6

stuck runs, k-means++ with 10 starts

0

Five-group data, single runs per seed. The last row picks the lowest-inertia run of 10 k-means++ starts, checked for all 50 seeds. Illustrative simulation.

##### A guarantee for the seeding

k-means++ is O(log k)-competitive in expectation: the expected inertia after seeding alone is at most 8(ln k + 2) times the optimum [Arthur & Vassilvitskii 2007](https://theory.stanford.edu/~sergei/papers/kMeansPP-soda.pdf). Lloyd iterations then only improve it. It's the default initialisation in scikit-learn.

#### Key terms

| Term | Meaning |
|---|---|
| **Centroid** | Mean of a cluster's points. |
| **Inertia (WCSS)** | Sum of squared distances from points to their centroids. |
| **Lloyd's algorithm** | Alternate assign-to-nearest and move-to-mean until stable. |
| **k-means++** | Seeding proportional to squared distance from chosen centroids. |
| **Silhouette** | (b − a)/max(a, b): cohesion vs separation, −1 to 1. |
| **ARI** | Adjusted Rand index: agreement with known labels, corrected for chance. |

#### What this page is built from

1. scikit-learn, [Clustering user guide](https://scikit-learn.org/stable/modules/clustering.html) (inertia, Lloyd steps, local minima, k-means++, assumptions, mini-batch, silhouette, adjusted Rand index).

2. D. Arthur & S. Vassilvitskii, "k-means++: the advantages of careful seeding", SODA 2007, [PDF](https://theory.stanford.edu/~sergei/papers/kMeansPP-soda.pdf) (8(ln k + 2) bound).

3. S. Lloyd, "Least squares quantization in PCM", _IEEE Trans. Information Theory_ 28(2), 1982 (the algorithm; background).

4. P. Rousseeuw, "Silhouettes: a graphical aid to the interpretation and validation of cluster analysis", _J. Comput. Appl. Math._, 1987 (background).

Customer data is simulated with fixed seeds; every clustering on this page runs live in your browser.
