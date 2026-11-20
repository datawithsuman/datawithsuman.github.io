# DBSCAN

> How do you find curved clusters and flag the points that belong nowhere?

- Track: Fundamentals › Classical ML › Unsupervised learning
- Type: Concept · 30 min
- Page: https://aimlrounds.com/tracks/fundamentals/dbscan/
- Before this: k-Means Clustering (`fundamentals/k-means`)
- Quiz topic: `unsup`

## Intuition

### The situation

Your deliveries follow curved roads, and stray GPS pings land everywhere. k-means cuts straight across both roads. The interviewer asks:

> How does DBSCAN find clusters, and what is its main weakness?

**Running example:** the same food-delivery app, now looking at **where** orders are delivered. Simulated GPS points (standardised): 200 deliveries along two curved roads that wrap around each other (the "two moons" shape), plus 20 stray pings scattered at random (GPS errors). A second map has a dense city-centre cluster beside a sparse suburb. We want the roads found as two clusters and the stray pings flagged.

#### Clusters that aren't round, and points that belong nowhere

Deliveries follow roads, so the clusters are long and curved, and a k-means centroid in the middle of a curve sits where nobody lives. k-means on the two roads scores ARI 0.21: it cuts straight across both (see the k-means lesson). It also forces every GPS error into some cluster. We need a method that follows dense regions wherever they go and is allowed to say "this point is noise".

### The idea

Think of finding crowds at a fair. Wherever people stand packed together, you can walk from person to person and stay in the same crowd. Someone standing alone belongs to no crowd at all.

[Figure: Two curved roads of dense points wrap around each other. A few scattered grey points don't belong to either and are marked as noise.]

_Illustrative, based on the lesson's two roads and stray GPS pings._

### Play

**Try to break it.** Try eps at 0.25, 0.30 and 0.35. Watch how many clusters it finds and how many points become noise.

#### eps is everything

Big dots: core points. Small dots: border points. Grey: noise. The circle (top left) shows eps to scale.

With min_samples = 10: eps = 0.30 finds both roads exactly (ARI 1.0) and flags 4 stray pings as noise; the other 16 strays lie close enough to a road to be absorbed as border points. eps = 0.25 breaks a road into pieces (3 clusters); eps = 0.35 merges both roads into one. A 20% change in eps flips the answer. scikit-learn: eps "is crucial to choose appropriately for the data set and distance function and usually cannot be left at the default value" [clustering guide](https://scikit-learn.org/stable/modules/clustering.html#dbscan).

**Now say why:** why does such a small change in eps swing the result from fragments, to two roads, to one blob?

## Maths

### Maths

#### In one breath

DBSCAN says a cluster is a region where points are packed densely, separated from other clusters by sparse space. A point with at least **min_samples** neighbours within radius **eps** is a **core** point; core points within eps of each other join the same cluster, points near a core point join it as **border** points, and everything else is **noise**. So it finds clusters of **any shape**, figures out how many there are, and flags outliers, none of which k-means can do. Its weakness is one global density: **eps** is hard to set, and when clusters have different densities, no single eps works. **HDBSCAN** fixes that by trying all densities and keeping the most stable clusters. What you'll be able to do after this: classify points as core/border/noise by hand, pick eps with a k-distance plot, explain why DBSCAN finds curved clusters, and say when to switch to HDBSCAN.

#### Core, border and noise

1. Eight delivery points. Two settings: eps (a radius) and min_samples (how many points must be inside that radius).

2. Draw a circle of radius eps around a point. It contains 5 points including itself, at least min_samples = 4, so it's a **core point**: it's inside a dense region.

3. Check every point the same way: four more have at least 4 points within eps, so they are cores too. Core points within eps of each other are linked, and everything linked forms one cluster, whatever its shape.

4. These two points have too few neighbours to be cores (3 and 2 inside their circles), but each lies within eps of a core point, so they join the cluster as **border points**. Border points belong to a cluster but can't extend it.

5. The lone point has no core within eps. It's **noise** (label −1 in scikit-learn): DBSCAN refuses to force it into a cluster.

Definitions from scikit-learn: a core sample has "min_samples other samples within a distance of eps"; "Any sample that is not a core sample, and is at least eps in distance from any core sample, is considered an outlier by the algorithm" [clustering guide](https://scikit-learn.org/stable/modules/clustering.html#dbscan). (scikit-learn's min_samples counts the point itself.) Original algorithm: Ester, Kriegel, Sander & Xu, KDD 1996.

#### A cluster is a connected dense region

$$ {N_\varepsilon(p) = \{\,q : d(p,q) \le \varepsilon\,\}} \qquad {|N_\varepsilon(p)| \ge \text{min\_samples}} \qquad {p \to p_1 \to \dots \to q} $$

- **eps-neighbourhood**: All points within distance eps of p, including p itself.

- **core condition**: p is a core point if its neighbourhood holds at least min_samples points: p sits in a dense region.

- **density-reachable**: q belongs to p’s cluster if you can walk from p to q in eps-sized hops, where every point you hop from is a core point.

A cluster is a maximal set of points that are density-connected through core points. The number of clusters comes out of the data; nobody sets k. The algorithm is a flood fill: pick an unvisited core point, start a cluster, and keep adding the neighbours of every core point you reach.

#### The k-distance plot

For every point, compute the distance to its k-th nearest neighbour (k = min_samples − 1, so the circle around it holds min_samples points), sort those distances and plot them. Points inside clusters have small k-distances; noise points have large ones. The curve is flat, then bends sharply upward: eps near the bend separates "dense enough" from "noise". This heuristic is from the original DBSCAN paper.

Sorted distance from each of the 220 points to its k-th nearest neighbour. The dashed line marks eps = 0.30, the value that worked above.

For k = 9 the curve is nearly flat up to about the 85th percentile (0.25), then climbs: 0.30 at the 90th, 0.36 at the 95th, 0.48 at the 99th. The bend sits close to the eps that separated the roads. It's a guide, not a guarantee: with clusters of different densities there is no single bend.

## In practice

### In practice

#### The density-based family

| Method | Idea | Settings |
|---|---|---|
| **DBSCAN** (1996) | One density threshold; core/border/noise | eps, min_samples |
| **OPTICS** (1999) | Orders points by reachability; extract clusters at many eps | min_samples (max eps) |
| **HDBSCAN** (2013) | Hierarchy over all densities; keeps the most stable clusters | min_cluster_size, min_samples |

All three are in scikit-learn (`DBSCAN`, `OPTICS`, `HDBSCAN`) [clustering guide](https://scikit-learn.org/stable/modules/clustering.html). Typical uses: geospatial data (pickup hotspots, store locations), anomaly detection (noise points are the anomalies), and clustering embeddings after UMAP (see t-SNE & UMAP).

#### Speed, scaling and determinism

- **Cost:** one neighbourhood query per point. With a KD-tree or ball tree in low dimensions that's roughly O(n log n); otherwise O(n²). scikit-learn's implementation can build a full pairwise matrix that "will consume n² floats" when trees can't be used [clustering guide](https://scikit-learn.org/stable/modules/clustering.html#dbscan).

- **Scale features:** eps is one radius in every direction, so unscaled features make it meaningless. For GPS, use haversine distance in metres.

- **High dimensions:** distances concentrate (see k-NN), so density is hard to define; reduce dimensions first.

- **Order:** core points and noise are deterministic, but a border point within eps of two clusters goes to whichever reaches it first, so "results can differ when data is provided in a different order" [clustering guide](https://scikit-learn.org/stable/modules/clustering.html#dbscan).

#### The whole recipe

1. **Scale** features or choose a meaningful distance (haversine for GPS, cosine for embeddings).

2. **Set min_samples** from domain sense (a common rule of thumb: about 2 × dimensions, at least 4 or 5); larger means fewer, denser clusters and more noise.

3. **Pick eps** at the bend of the k-distance plot; try a few values around it.

4. **Inspect noise:** is it really noise, or a sparse cluster? If densities differ, switch to HDBSCAN.

#### When to use it

##### Use DBSCAN / HDBSCAN when

- Clusters have odd shapes (geography, trajectories)

- You expect noise and want outliers flagged

- You don't know how many clusters there are

- HDBSCAN: densities vary

##### Reach for something else when

- Clusters are round and k is known: k-means is simpler and faster

- You need soft membership: GMM

- Very high-dimensional raw features: reduce first

### The answer that sounds right

#### "Link every pair of points closer than some distance"

Linking any two points within distance eps (single linkage cut at eps) follows curves too. But one chain of stray GPS pings between the two roads links them into one cluster, and isolated pings become their own tiny "clusters". DBSCAN's fix is the min_samples rule: only **core** points can extend a cluster, and a stray ping in a sparse area isn't a core, so it can't act as a bridge. Density, not just distance, decides what's connected.

#### A dense centre and a sparse suburb

120 deliveries packed in the city centre, 60 spread across a suburb next to it. min_samples = 5.

eps = 0.15 finds the centre but throws away **54 of the 60** suburb deliveries as noise. eps = 0.4 keeps the suburb but merges it with the centre into one cluster. The compromise, eps = 0.3, keeps them apart but hands 11 suburb deliveries to the centre and drops 7 as noise. scikit-learn: "DBSCAN assumes that the clustering criterion (i.e. density requirement) is globally homogeneous" and "may struggle to successfully capture clusters with different densities" [clustering guide](https://scikit-learn.org/stable/modules/clustering.html#hdbscan).

**Go deeper: how HDBSCAN removes eps**

HDBSCAN (Campello, Moulavi & Sander, PAKDD 2013) "explores all possible density scales": it replaces raw distance with a **mutual reachability distance** (the larger of the two points' core distances and their actual distance, which pushes sparse points apart), builds a single-linkage tree on it (via a minimum spanning tree), and condenses the tree, dropping splits smaller than `min_cluster_size`. It then keeps the clusters that persist longest as density changes (their **stability**). Each cluster effectively gets its own eps. scikit-learn: it "relies solely on the choice of min_samples, which tends to be a more robust hyperparameter" [clustering guide](https://scikit-learn.org/stable/modules/clustering.html#hdbscan). In practice it's the better default; use plain DBSCAN when you know the density scale (e.g. "a hotspot is ≥ 10 orders within 200 m").

#### Caveats

##### Strengths

- Any cluster shape

- No k: the number of clusters comes from the data

- Built-in outlier detection (noise label)

- Few parameters with physical meaning (a radius and a count)

##### Weaknesses

- Very sensitive to eps

- Can't score new points without refitting (scikit-learn)

- One global density: fails on clusters of different densities

- Struggles in high dimensions

- Border points between clusters are assigned arbitrarily

## Say it

### How does DBSCAN find clusters, and what is its main weakness?

#### The interviewer pushes further

Follow-up 1 of 5

How do you choose eps and min_samples?

min_samples from domain sense or ~2 × dimensions; eps from the bend of the sorted k-distance plot with k = min_samples − 1, then check the clusters and noise share. If no single bend exists, use HDBSCAN.

Follow-up 2 of 5

DBSCAN vs k-means?

DBSCAN: any shape, no k, noise label, but eps-sensitive and single-density. k-means: round clusters, needs k, every point assigned, fast and simple.

Follow-up 3 of 5

What are border points and why are they ambiguous?

Non-core points within eps of a core. A border point near two clusters goes to whichever cluster reaches it first, so it can depend on data order.

Follow-up 4 of 5

How would you use it for anomaly detection?

Run it on a batch, and treat noise points (label −1) as candidates. scikit-learn's DBSCAN only labels the data it was fitted on, and can't score new points, so you refit on each batch. To score new points one by one, use a method built for that, such as LOF in novelty mode or Isolation Forest. HDBSCAN also gives outlier scores (GLOSH).

Follow-up 5 of 5

Complexity?

About O(n log n) with spatial indexes in low dimensions, O(n²) worst case or in high dimensions.

#### The 30-second answer

DBSCAN is density-based clustering. A point with at least min_samples neighbours within radius eps is a core point; clusters are groups of core points reachable from each other through eps-hops, plus border points within eps of a core; everything else is noise. It finds arbitrarily shaped clusters, infers the number of clusters, and flags outliers. The catch is eps: results are very sensitive to it, you pick it from the bend of a k-distance plot, and because it's one global density it fails when clusters have different densities. HDBSCAN fixes that by building a hierarchy over all densities and keeping the most stable clusters, so it only needs a minimum cluster size.

**Go further**

#### What not to say

- "DBSCAN needs the number of clusters." It doesn't.

- "DBSCAN handles clusters of any density." Any shape, yes; different densities, no.

- "Noise points are errors to delete." They might be a real sparse cluster.

**Key terms and sources**

Density-based clustering: core, border and noise points, eps and min_samples, the k-distance plot, varying density and HDBSCAN · built from Ester et al. (1996), scikit-learn's clustering guide and Campello et al. (2013) · checked 28 Oct 2026

#### Evidence

##### Two roads, ARI by method (this page's simulation)

k-means, k = 2 (best of 10)

0.21

DBSCAN, eps 0.25

0.76

DBSCAN, eps 0.30

1.00

DBSCAN, eps 0.35

0.00

ARI on the 200 road deliveries, min_samples = 10. Illustrative.

##### Recognition

The DBSCAN paper (Ester, Kriegel, Sander & Xu, KDD 1996) received the SIGKDD Test of Time award in 2014; it remains one of the most-cited clustering papers.

#### Key terms

| Term | Meaning |
|---|---|
| **eps** | Neighbourhood radius. |
| **min_samples** | Points needed within eps (including itself) to be a core point. |
| **Core / border / noise** | Dense point / non-dense point near a core / everything else. |
| **Density-reachable** | Reachable by eps hops through core points. |
| **k-distance plot** | Sorted distances to the k-th neighbour; its bend suggests eps. |
| **HDBSCAN** | Hierarchical DBSCAN over all densities; picks stable clusters. |

#### What this page is built from

1. M. Ester, H.-P. Kriegel, J. Sander & X. Xu, "A density-based algorithm for discovering clusters in large spatial databases with noise", KDD 1996, pp. 226–231 (DBSCAN, k-distance heuristic).

2. scikit-learn, [Clustering user guide: DBSCAN, HDBSCAN, OPTICS](https://scikit-learn.org/stable/modules/clustering.html#dbscan) (definitions, eps sensitivity, memory, ordering, global density assumption).

3. R. Campello, D. Moulavi & J. Sander, "Density-based clustering based on hierarchical density estimates", PAKDD 2013 (HDBSCAN).

4. M. Ankerst et al., "OPTICS: ordering points to identify the clustering structure", SIGMOD 1999 (background).

GPS data is simulated with fixed seeds; DBSCAN runs live in your browser.
