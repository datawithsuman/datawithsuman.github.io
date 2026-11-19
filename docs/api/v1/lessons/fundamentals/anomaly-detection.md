# Anomaly Detection

> How do you find fraud when you have no examples of fraud?

- Track: Fundamentals › Classical ML › Unsupervised learning
- Type: Concept · 30 min
- Page: https://aimlrounds.com/tracks/fundamentals/anomaly-detection/
- Before this: Random Forest (`fundamentals/random-forest`), k-Nearest Neighbours (`fundamentals/k-nearest-neighbours`)
- Quiz topic: `unsup`

## Intuition

### The situation

Fraud patterns keep changing, glitches are new every time, and you have almost no labelled examples. A normal classifier has nothing to learn from. The interviewer asks:

> How would you detect anomalies without labels?

**Running example:** the food-delivery app watches orders for fraud and glitches using two standardised signals: order value and distance. Two simulated days: on day 1 normal orders form one cloud and 10 anomalies sit far outside it (500 orders); on day 2 normal orders come from a dense city-centre cluster and a spread-out suburban cluster, and the 10 anomalies sit just outside the dense cluster, unusual for the city centre but closer than many suburban orders are to their own centre.

#### Find the odd ones out, without examples of "odd"

Fraud patterns change, glitches are new every time, and labelled anomalies are rare. A classifier needs examples of both classes; anomaly detection instead learns what "normal" looks like and scores how far each point departs from it. The output is a ranked list for a human or an automatic rule, not a certainty.

### The idea

Think of playing twenty questions to single out one person in a crowd. Someone in a strange costume takes only a few questions, while someone ordinary takes many. Isolation Forest counts those questions, and fewer means more unusual.

[Figure: A dense cloud of normal orders and one far-off point. Two random cuts are enough to isolate the far-off point, while points in the cloud would need many more.]

_Illustrative. Short average paths across many random trees mean a high anomaly score._

### Play

**Try to break it.** Isolate the anomaly and count the splits. Then isolate a normal order and compare.

#### Anomalies are "few and different", so they're easy to isolate

Each split picks a random feature and a random cut between that feature's min and max among the points still in the box. The shaded box is the region still containing the chosen point.

Liu, Ting & Zhou (2008) built Isolation Forest on this: a point far from the crowd ends up alone after a few random cuts, while a point in the middle needs many. scikit-learn: "Random partitioning produces noticeably shorter paths for anomalies. Hence, when a forest of random trees collectively produce shorter path lengths for particular samples, they are highly likely to be anomalies" docs. Here, over 100 trees, the anomaly needs **4.8** splits on average and the normal order **11.4**.

$$ s(x) = 2^{-\,\mathbb{E}[h(x)] \,/\, c(\psi)} $$

Liu, Ting & Zhou, "Isolation forest", ICDM 2008. Each tree is grown on a random subsample of ψ = 256 points (scikit-learn's default `max_samples`), to depth ⌈log₂ ψ⌉; 100 trees by default. Subsampling helps: fewer normal points crowd around the anomalies. On day 1: s = 0.72 for the anomaly, 0.46 for the normal order.

- **anomaly score**: Close to 1: very likely an anomaly. Well below 0.5: normal. Around 0.5 everywhere: no clear anomalies.

- **average path length**: Splits needed to isolate x, averaged over the trees (with a correction for points left in unsplit leaves).

- **normaliser**: c(ψ) ≈ 2 ln(ψ − 1) + 1.15 − 2(ψ − 1)/ψ: the average path length of an unsuccessful search in a binary search tree of ψ points, so scores are comparable across sample sizes. For the default ψ = 256, c ≈ 10.2.

**Now say why:** why do random splits find unusual points so quickly, with no labels at all?

## How it works

### How it works

#### In one breath

Anomaly detection finds the few points that don't look like the rest, usually without labels. **Isolation Forest** builds random trees with random splits: odd points get isolated after very few splits, so a short average path means "anomaly"; it's fast and a strong default. **Local Outlier Factor (LOF)** compares each point's density with its neighbours' and catches points that are odd _for their neighbourhood_, even next to a dense cluster. **One-Class SVM** learns a boundary around normal data (good for novelty detection on clean training data, sensitive to outliers and tuning). A Gaussian / **Mahalanobis** score works only when normal data is one elliptical blob. Every method gives a score; the threshold (contamination) is a business decision, and evaluation needs at least a few labelled anomalies.What you'll be able to do after this: explain why isolation works, when LOF beats Isolation Forest, choose a threshold, and design an evaluation for a detector with almost no labels.

#### Outlier detection vs novelty detection

##### Outlier detection (unsupervised)

"The training data contains outliers which are defined as observations that are far from the others." The detector fits the dense regions and ignores the deviants. Example: score yesterday's orders, some of which were fraud.

##### Novelty detection (semi-supervised)

"The training data is not polluted by outliers and we are interested in detecting whether a new observation is an outlier." Example: learn from a week of verified-clean orders, then score each new order.

Definitions from scikit-learn's outlier-detection guide docs. All its detectors share an API: `score_samples` gives a continuous score; `predict` returns −1 for outliers using a threshold set by `contamination`.

#### Unusual compared with its neighbours

LOF (Breunig, Kriegel, Ng & Sander, SIGMOD 2000) estimates each point's local density from the distances to its k nearest neighbours, then divides the neighbours' average density by the point's own. A point inside any cluster, dense or sparse, has density similar to its neighbours (LOF ≈ 1). A point just outside a dense cluster has much lower density than its dense neighbours (LOF ≫ 1), even if it's closer to them than suburban points are to each other. scikit-learn: "The question is not, how isolated the sample is, but how isolated it is with respect to the surrounding neighborhood", and "taking n_neighbors=20 appears to work well in general" docs. The cost: O(n²) distances without an index, and it's mainly an outlier (not novelty) detector unless you set `novelty=True`.

#### A boundary around normal

Schölkopf et al. (2001) adapted the SVM to one class: in kernel feature space, separate the data from the origin with maximum margin, which in input space becomes a closed boundary around the bulk of the data. The `nu` parameter "corresponds to the probability of finding a new, but regular, observation outside the frontier", and the RBF kernel's γ sets how tight the boundary hugs the data, with "no exact formula or algorithm to set its bandwidth parameter" docs. It's best for novelty detection with clean training data; it scales poorly (kernel SVM cost), so scikit-learn points to `SGDOneClassSVM` with kernel approximation for large data. See the SVM lesson for kernels and γ.

## In practice

### In practice

#### The main families

| Method | Idea | Good at |
|---|---|---|
| **Statistical** (z-score, Mahalanobis, `EllipticEnvelope`) | Distance from one fitted Gaussian | One elliptical blob, few features |
| **Isolation Forest** | Anomalies are isolated by few random splits | Fast, high-dimensional, global outliers |
| **LOF** | Density relative to neighbours | Local outliers, clusters of different density |
| **One-Class SVM** | Boundary around normal data (kernel) | Novelty detection with clean training data |
| **Reconstruction** (PCA, autoencoders) | Normal data reconstructs well; anomalies don't | High-dimensional signals, images, logs |

scikit-learn's own comparison: Isolation Forest and LOF "perform reasonably well on the data sets considered"; One-Class SVM "is known to be sensitive to outliers and thus does not perform very well for outlier detection" docs. Density-based ideas from DBSCAN and GMMs (low p(x)) also work as detectors.

#### Contamination, thresholds and evaluation

Isolation Forest on day 1 (10 true anomalies = 2%). The model's scores don't change; only the cut-off does.

- **Contamination** is not learned: it's your guess of the anomaly rate, or better, your review capacity ("we can check 50 orders a day"). It only sets the threshold on the score.

- **Evaluate with labels where you can:** even 50 confirmed fraud cases let you measure precision@k and PR-AUC (see Ranking Metrics). With none, have analysts review a sample of top-scored and random items.

- **Once you have enough labels, consider supervised learning:** a classifier trained on confirmed cases usually beats an unsupervised detector on the patterns it has seen; keep the detector for new patterns.

- **Scale features** for distance-based methods (LOF, One-Class SVM, Mahalanobis); Isolation Forest doesn't need it.

#### The whole recipe

1. **Define "anomaly"** with the business: global outliers, local ones, or new patterns? This picks the method.

2. **Engineer features** that make anomalies visible (ratios, per-user baselines, time-of-day); scale them for distance methods.

3. **Start with Isolation Forest**; try LOF if anomalies are local or segments differ in density.

4. **Set the threshold** from review capacity or costs; monitor the flag rate.

5. **Collect feedback** on flagged items; measure precision@k; move to supervised models as labels accumulate.

#### Scenarios

##### "Detect fraudulent restaurant payouts, no labels"

Features relative to each restaurant's own history (z-scores per restaurant), then Isolation Forest; analysts review the top 50 a day; feed confirmations into a supervised model.

##### "Server metrics, find new failure modes"

Novelty detection: train on healthy periods (Isolation Forest, or reconstruction error from PCA/autoencoder); alert on high scores; tune threshold to on-call capacity.

### The answer that sounds right

#### "Flag anything more than 3 standard deviations from the mean"

A z-score (or its multivariate version, the Mahalanobis distance) assumes normal data is a single elliptical blob. On day 1 that's true and it works perfectly. On day 2, the wide suburban cluster inflates the overall spread, so points near the dense city centre look perfectly ordinary by distance from the global mean, while ordinary suburban orders look extreme. The Mahalanobis score drops to ROC-AUC 0.59 on day 2 and none of its top 10 flags are real anomalies (see the lab below). "Far from the average" isn't the same as "unusual where it is".

#### Global vs local anomalies

Darker = higher anomaly score. Orange rings: the 10 highest-scoring orders. Red ×: the true anomalies.

| | Isolation Forest | LOF | Mahalanobis |
|---|---|---|---|
| Day 1 (global anomalies): AUC · top-10 hits | 1.00 · 9 | 1.00 · 9 | 1.00 · 9 |
| Day 2 (local anomalies): AUC · top-10 hits | 0.91 · 0 | 1.00 · 9 | 0.59 · 0 |

On day 1 all three work. On day 2 Isolation Forest still ranks anomalies above most normal orders (AUC 0.91), but its top 10 are all genuine suburban orders on the far edge of the sparse cluster: in absolute terms they're the most isolated points. LOF compares each point with its own neighbourhood and puts 9 real anomalies in its top 10. If your anomalies are "unusual for their segment", use LOF, or score each segment separately.

#### Caveats

- "Anomalous" isn't "bad": a big corporate order is unusual and legitimate. Detectors find rare, not wrong.

- Isolation Forest uses axis-parallel splits, so it has blind spots along diagonals (Extended Isolation Forest addresses this).

- In high dimensions, irrelevant features dilute every method; feature selection and domain features matter most.

- Contamination set too high creates a stream of false alarms; too low misses anomalies. Revisit it as the data drifts.

## Say it

### How would you detect anomalies without labels?

#### The interviewer pushes further

Follow-up 1 of 4

Why does Isolation Forest work?

Anomalies are few and different, so random axis-parallel cuts separate them from the rest quickly; normal points in dense regions need many cuts. The average path length over many trees, normalised by c(ψ), gives the score s = 2^(−E[h]/c).

Follow-up 2 of 4

Isolation Forest vs LOF?

IF: global, fast (subsampled trees), scales to high dimensions, no distances. LOF: local density comparison, handles clusters of different density, but O(n²) distances and needs scaling.

Follow-up 3 of 4

How do you evaluate without labels?

Get a small labelled set (analyst review of top-k and random samples), measure precision@k and PR-AUC, check stability over time, and track how many flags lead to action.

Follow-up 4 of 4

Outlier vs novelty detection?

Outlier detection: training data contains anomalies; novelty detection: training data is clean and you score new points. It changes which methods and settings fit (e.g., LOF novelty=True, One-Class SVM).

#### The 30-second answer

Anomaly detection scores how unusual each point is relative to normal data, usually without labels. Isolation Forest builds random trees with random splits; anomalies are isolated in few splits, so a short average path length means a high anomaly score. It's fast, needs no scaling and is a good default for global outliers. LOF compares a point's local density with its neighbours' and catches anomalies that are unusual for their neighbourhood, for example next to a dense cluster. One-Class SVM learns a boundary around clean training data for novelty detection. Statistical scores like Mahalanobis assume a single Gaussian blob. The threshold, or contamination, is set from review capacity or costs, and evaluation needs at least some labelled cases, using precision at k.

**Go further**

#### What not to say

- "Contamination is learned from data." It's your assumption or capacity.

- "Anything 3σ from the mean is an anomaly." Only for one Gaussian-like blob.

- "Anomaly detection replaces a fraud classifier." With labels, supervised usually wins on known patterns.

**Key terms and sources**

Outlier vs novelty detection, Isolation Forest, Local Outlier Factor, One-Class SVM, Mahalanobis distance, contamination and thresholds, and evaluating without labels · built from Liu, Ting & Zhou (2008), Breunig et al. (2000), Schölkopf et al. (2001) and scikit-learn's outlier-detection guide · checked 28 Oct 2026

#### Evidence

##### Day 2 (local anomalies): ROC-AUC (this page's simulation)

Mahalanobis

0.59

Isolation Forest

0.91

LOF

1.00

Higher is better; 500 orders, 10 anomalies. Illustrative: on other data, Isolation Forest is often the stronger and much faster choice.

#### Key terms

| Term | Meaning |
|---|---|
| **Outlier vs novelty detection** | Training data contains anomalies / is clean. |
| **Path length** | Random splits needed to isolate a point. |
| **Local outlier factor** | Neighbours' density ÷ own density. |
| **Contamination** | Assumed anomaly share; sets the threshold. |
| **Mahalanobis distance** | Distance from the mean in units of the covariance. |

#### What this page is built from

1. F. T. Liu, K. M. Ting & Z.-H. Zhou, "Isolation forest", IEEE ICDM 2008 (path-length score, subsampling ψ = 256).

2. M. Breunig, H.-P. Kriegel, R. Ng & J. Sander, "LOF: identifying density-based local outliers", SIGMOD 2000.

3. B. Schölkopf, J. Platt, J. Shawe-Taylor, A. Smola & R. Williamson, "Estimating the support of a high-dimensional distribution", _Neural Computation_ 13, 2001 (One-Class SVM).

4. scikit-learn, Novelty and outlier detection (definitions, API, Isolation Forest, LOF, One-Class SVM, contamination, comparison).

Order data is simulated with fixed seeds; every detector runs live in your browser.
