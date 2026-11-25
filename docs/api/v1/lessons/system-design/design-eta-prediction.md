# Design ETA Prediction

> A ride-hailing and delivery app shows an arrival time on every request, and prices depend on it. Design an ETA system that is accurate, fast enough for every request, and works across products and cities.

- Track: System Design › Maps and Logistics › Designs
- Type: Design · 25 min
- Page: https://aimlrounds.com/tracks/system-design/design-eta-prediction/
- Before this: Self-Attention (Q, K, V) (`fundamentals/self-attention`), Regression Metrics (`fundamentals/regression-metrics`)
- Quiz topic: `sdllm`
- Sources checked: 2026-11-05 · Text last changed: 2026-11-20 · Version: c4f8d442fa

## Intuition

### The situation

A ride-hailing and delivery company shows an arrival time on every request, worldwide, and fares depend on it. Its routing engine computes ETAs from the map and live traffic but makes systematic errors. A large tree ensemble corrects them, and the team wants more accuracy within a few milliseconds. The interviewer asks:

> A ride-hailing and delivery app shows an arrival time on every request, and prices depend on it. Design an ETA system that is accurate, fast enough for every request, and works across products and cities.

#### Ask before designing

- **Uses:** pickup ETAs, trip ETAs, delivery ETAs and fares, each needing slightly different behaviour.

- **Scale:** every request in every city, so this may be the busiest model in the company.

- **Latency:** a few milliseconds per prediction.

- **Must never happen:** systematically late ETAs, which break trust and pricing.

- **Success metrics:** mean absolute error against actual arrival, error at the tail, and calibration of quantiles.

### The idea

Think of a sat-nav and a local driver. The sat-nav knows the roads and today's traffic; the local driver knows it always takes five extra minutes to get out of that car park. You keep the sat-nav and let the driver correct it, and they'd rather arrive a bit early than late.

[Figure: The routing engine sums segment times on the best path. A fast model predicts its error from embedded, bucketised and hashed features, trained with a loss that punishes lateness.]

_Keep routing, and learn its mistakes._

### Play

**Try to break it.** Drag the number of features up to 200 and watch both costs. Then raise the embedding size above the number of features. Then raise ω.

#### How much does attention cost?

The two cost formulas and the K = 40, d = 8 example are from the post. The asymmetric loss shape follows the post's description; our version weights late errors by ω.

With features as tokens, full self-attention grows with the **square** of the number of features. Linear attention grows with the square of the embedding size instead, which is small, so it wins as long as d is less than K. Then raise ω: one model can produce a mean-like ETA or a cautious one, just by changing the loss.

**Now say why:** when does linear attention stop saving anything?

## Architecture

### Architecture

#### In one breath

Keep the **routing engine**, which adds up travel times along the best path using the map and live traffic, and train an ML model to predict its **error**. Make that model fast: **embed** categorical features, **bucketise** continuous ones, **hash** locations at several grid sizes, and use **linear attention** so cost grows with the number of features, not its square. Train with an **asymmetric loss**, because being late is worse than being early.

#### Routing plus a learned correction

1. **Request:** origin, destination, time, and request type such as a delivery drop-off or a ride pickup.

2. **Routing engine:** finds the best path and sums segment travel times using map data and live traffic.

3. **Correction model:** predicts the gap between the routing ETA and what actually happens, using the routing ETA and other features.

4. **Serve:** the routing front end calls the model service, then returns the final ETA.

5. **Retrain:** regularly, with automatic validation before each new model goes live.

##### Why not replace routing with ML?

The routing engine already captures the road network and live traffic. A correction model is easier to change for new data sources and business needs than refactoring routing, and it fixes the routing engine's systematic errors.

##### Feature tricks for speed

Turn everything into embedding lookups: bucketise continuous values into quantile bins, and map latitude and longitude to grid cells at several resolutions, using several hash functions to save space while avoiding collisions. Lookups are constant time, so the model can be large but each prediction touches only a tiny part of it.

#### The numbers worth saying out loud

All of these are assumptions for the interview, not figures from a real system.

| Question | Working | Result |
|---|---|---|
| ETA requests a second at peak | given | **500,000** |
| Latency budget per prediction | given | **about 5 ms** |
| Embedding table size | 300 million parameters × 4 bytes | **about 1.2 GB** |
| Parameters touched per prediction | 300 million × 0.25% | **about 750,000** |
| Training trips a day | given | **tens of millions** |

A big model is fine as long as each prediction reads only a small slice of it; that's the point of embedding lookups.

## In practice

### In practice

#### What every ETA design gets asked

- **Why bucketise numbers?** Turning continuous features into quantile bins and embedding them often beats feeding raw values, and quantile bins use the bins evenly.

- **Locations:** multi-resolution grid cells with several independent hashes balance accuracy, memory and collisions.

- **One model, many products:** pass the request type as a feature, and add a small bias adjustment per segment, rather than separate models.

- **Loss:** an asymmetric Huber loss resists outliers and lets you choose how much to penalise lateness, or target a quantile.

- **Freshness:** traffic patterns change; retrain often, ideally incrementally, with automatic validation.

- **Monitoring:** track error by city, product and time of day, since a global average hides a city that's broken.

##### Rollout

Shadow the new model against the current one, compare errors by city and product on real trips, then roll out city by city.

#### What the real system reported

- **Design:** the routing engine predicts ETAs as a sum of segment travel times; the ML model predicts the residual. It replaced one of the largest and deepest XGBoost ensembles in the world at the time.

- **Requirements:** an ETA within a few milliseconds at most, a significant accuracy gain over XGBoost, and one model for all products worldwide. They call it the highest-QPS model at the company.

- **Model:** of seven architectures tested, an encoder–decoder with self-attention over features was most accurate; a linear transformer made it fast enough. It's shallow, with most parameters in embedding tables; each prediction touches about 0.25% of hundreds of millions of parameters.

- **Features and loss:** all features embedded, continuous ones in quantile buckets; locations via multi-resolution grids with multiple feature hashing; an asymmetric Huber loss.

From the company's post. It gives no MAE, latency or QPS figures; those are in the linked paper, which we didn't read.

### The answer that sounds right

#### "A bigger model will be more accurate, so use the biggest you can"

It sounds right, but every request needs an answer in milliseconds. Full attention over features grows with the square of their number. The trick is a model that's large in embedding tables but shallow and cheap per prediction, with linear attention.

## Say it

### A ride-hailing and delivery app shows an arrival time on every request, and prices depend on it. Design an ETA system that is accurate, fast enough for every request, and works across products and cities.

#### The interviewer pushes further

Follow-up 1 of 3

Why predict the routing engine's error instead of the ETA directly?

Routing already captures the road network and live traffic. The model only has to learn what routing gets wrong, like pickup delays or restaurant waits, which is easier, and it's simpler to update than the routing engine.

Follow-up 2 of 3

Why would you bucketise a continuous feature like distance?

Bins with embeddings let the model learn a flexible shape per range cheaply, and lookups are fast. Quantile bins spread examples evenly, so every bin is well trained.

Follow-up 3 of 3

Fares need an average ETA, but customers prefer not to be surprised. Two models?

Not necessarily. An asymmetric loss lets one architecture produce a mean-like estimate or a cautious quantile; you can train or tune per use case and keep the rest shared.

#### The 30-second answer

First I'd clarify the uses, like pickup, trip, delivery and fares, the scale and the latency budget of a few milliseconds. I'd keep the routing engine, which sums segment travel times along the best path with live traffic, and train a model to predict its error, since that's easier to change than routing itself. For speed, every feature becomes an embedding lookup: categorical features embedded, continuous ones bucketised into quantile bins, and locations mapped to grid cells at several resolutions with multiple hashes. The model treats features as tokens with self-attention, but uses linear attention so cost grows with the number of features rather than its square. It's shallow, with most parameters in embedding tables, so each prediction touches only a small slice. I'd train with an asymmetric Huber loss, since being late is worse than being early, and pass the request type so one model serves all products. I'd retrain regularly, monitor error by city and product, and roll out city by city.

**Key terms and sources**

Based on a ride-hailing company's published post: [Uber's "DeepETA: How Uber Predicts Arrival Times Using Deep Learning"](https://www.uber.com/blog/deepeta-how-uber-predicts-arrival-times/) (February 2022). The post gives no accuracy or latency figures; the lab computes the cost formulas from the post, and the estimate is ours. Uses self-attention, regression metrics and online inference. · checked 5 Nov 2026
