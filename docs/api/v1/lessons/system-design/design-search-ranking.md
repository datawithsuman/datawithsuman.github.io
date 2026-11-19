# Design Search Ranking with Deep Learning

> A travel marketplace ranks thousands of available homes for each search. A boosted-tree ranker has stopped improving. Design the move to deep learning, and say what to expect.

- Track: System Design › Ads and Search Ranking › Designs
- Type: Design · 25 min
- Page: https://aimlrounds.com/tracks/system-design/design-search-ranking/
- Before this: Ranking Metrics (`fundamentals/ranking-metrics`), Learning-Rate Schedules (`fundamentals/learning-rate-schedules`)
- Quiz topic: `sdrec`

## Intuition

### The situation

A travel marketplace ranks thousands of available homes for each guest search. A boosted-tree ranker once gave one of the biggest booking gains in its history, but improvements have stalled. The team wants to move to deep learning. The interviewer asks:

> A travel marketplace ranks thousands of available homes for each search. A boosted-tree ranker has stopped improving. Design the move to deep learning, and say what to expect.

#### Ask before designing

- **Goal:** more bookings. A search session ends with a guest booking one listing, or not.

- **Candidates:** thousands of available listings per search, filtered by place and dates; we rank, not retrieve.

- **Current state:** a gradient-boosted tree model whose gains have plateaued.

- **Constraints:** scoring must fit the search latency budget; the existing serving stack is in Java.

- **Success metrics:** NDCG offline on booked listings, and bookings in an online A/B test.

### The idea

Think of moving a successful restaurant to a new, bigger kitchen. The first weeks, food comes out no better and sometimes worse. What finally helps isn't fancier equipment, but the right recipe, far more practice and fixing the slow supply line.

[Figure: Logs give booked and not-booked listings per search. A network trains on those pairs, weighted by NDCG change, over normalised features. Changes are tested offline, then on bookings.]

_The objective, the data and the pipeline matter more than the architecture._

### Play

**Try to break it.** Step through all seven ideas, noting which worked.

#### Pick an idea and see what happened

**What the paper reports**

All outcomes as reported in the paper; it describes them qualitatively or with the figures shown here.

Step through the ideas. The wins were less about clever architecture and more about **the right objective, more data and a faster pipeline**. Several popular ideas didn't transfer, because a home can be booked at most 365 nights a year, so there's little data per listing.

**Now say why:** why did an embedding per listing overfit here, when item embeddings work for videos?

## Architecture

### Architecture

#### In one breath

Rank to get **booked listings to the top**. Train a neural network with a **pairwise** loss on booked versus not-booked listings from the same search, weighted by how much swapping them changes NDCG. Expect the move from boosted trees to be slow: **normalise features** carefully, feed the network **far more data**, and fix the **training pipeline**. Ideas that work elsewhere, like an ID embedding per listing, can fail in a marketplace where each item has few bookings.

#### From logs to a ranked list

1. **Logs:** each search, the listings shown and what the guest viewed and booked.

2. **Training pairs:** within each search, pair the booked listing with listings not booked.

3. **Model:** a small feed-forward network over normalised features and embeddings, trained with a pairwise loss weighted by the change in NDCG from swapping the pair (the LambdaRank idea).

4. **Serve:** the search server scores the candidates and returns them in order.

5. **Test:** offline NDCG first, then an online A/B test on bookings.

##### Features that suit a network

Trees don't care about scale; networks do. Map each feature to a small range, using a z-score for bell-shaped features or a log ratio to the median for skewed ones, and prefer smooth distributions. Location becomes a log offset from the map centre, and a hashed city-plus-map-cell feature lets the network learn where in a city guests prefer to stay.

#### The numbers worth saying out loud

All of these are assumptions for the interview, not figures from a real system.

| Question | Working | Result |
|---|---|---|
| Searches a day | given | **20 million** |
| Listings scored a day | 20 million × 1,000 candidates | **20 billion** |
| Booked searches a day | 20 million × 2% | **400,000** |
| Training pairs a day | 400,000 × 20 non-booked | **8 million** |

Bookings are scarce compared with searches, so months of logs are needed to reach the billion-plus pairs a network benefits from.

## In practice

### In practice

#### What every search ranking design gets asked

- **Objective:** pairwise or listwise losses that target the top of the list beat plain regression on booked versus not.

- **Data:** networks need far more examples than trees; plot learning curves to see if more data will close the gap between training and test.

- **Sparse items:** per-item embeddings overfit when each item has few positives; share signal through attributes and categories.

- **Related signals:** views are plentiful but not the same as bookings; multi-task learning can boost views without moving bookings.

- **Pipeline:** data loading can starve GPUs; efficient formats and caching static features as embeddings can make training many times faster.

- **Interpretability:** per-feature attribution is hard for networks; comparing feature distributions of top- versus bottom-ranked listings is a practical check.

##### Rollout

Ship a simple network that matches the trees first, to prove the pipeline; then improve one change at a time, each with an A/B test on bookings.

#### What the real system reported

- **Starting point:** replacing a hand-made scoring function with boosted trees was one of the biggest booking gains in the company's history, but later gains saturated.

- **Evolution:** a single-hidden-layer network (32 units) was booking-neutral; LambdaRank-style pairwise training was the first breakthrough; hybrids with tree leaves and a factorisation machine followed; finally, 10× more data and a network with two hidden layers (127 and 83 units) over 195 features replaced the complexity.

- **Failures:** listing ID embeddings overfitted, since even popular listings are booked at most 365 times a year; a multi-task model raised long views a lot but bookings stayed neutral.

- **Engineering:** GPU use was near 25% until the pipeline moved to protobufs and a dataset API, giving a 17× speed-up and about 90% GPU use; a custom Java scoring library met the latency budget.

- **Lesson:** deep learning wasn't a drop-in replacement for trees; it meant rethinking the whole system around the model.

From the paper (KDD 2019).

### The answer that sounds right

#### "Swap the trees for a neural network and it will win"

It sounds right, since deep learning wins elsewhere. But a network fed the same features and data often just matches the trees. Gains came from a ranking objective, careful normalisation, much more data and a faster pipeline, and several popular ideas failed here.

## Say it

### A travel marketplace ranks thousands of available homes for each search. A boosted-tree ranker has stopped improving. Design the move to deep learning, and say what to expect.

#### The interviewer pushes further

Follow-up 1 of 3

Your first network is no better than the boosted trees. Is deep learning a failure here?

Not yet. Check feature normalisation, switch to a ranking objective, add much more data and look at learning curves. A first network that matches the trees is useful: it proves the pipeline end to end.

Follow-up 2 of 3

Why might an embedding per listing hurt?

Each listing has few bookings, at most one per night, so its embedding memorises noise. Item embeddings work when items have lots of interactions, like videos or words.

Follow-up 3 of 3

Long views went up a lot, but bookings didn't. Why?

Views aren't bookings: people browse expensive or unusual homes they won't book. Optimise the real goal, and treat views as a helper signal only if they actually move it.

First I'd clarify the goal, bookings, the candidate set per search, the current model and the latency budget. Training data comes from search logs: within each search, I'd pair the booked listing with listings not booked, and train a network with a pairwise loss weighted by the change in NDCG, so it focuses on the top of the list. I'd normalise every feature to a small range, prefer smooth distributions, and represent location as offsets plus a hashed city-and-area feature. I'd start with a simple network that matches the trees, to prove the pipeline, then add data, since networks need far more of it, and watch learning curves. I'd fix the training pipeline early, because data loading often starves GPUs. I'd be careful with per-listing embeddings, which overfit when bookings are scarce, and with proxy signals like views. Every change is tested offline on NDCG, then online on bookings.

**Key terms and sources**

Based on a home-sharing marketplace's published paper: "Applying Deep Learning To Airbnb Search" (KDD 2019). The lab reports the paper's own outcomes; the estimate is ours. Uses ranking metrics, training deep nets and explaining models.
