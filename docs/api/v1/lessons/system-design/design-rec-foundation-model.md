# Design a Shared Recommendation Foundation Model

> A large app runs hundreds of separate recommendation models, one per surface, each trained on its own slice of data. Design one large foundation model that makes all of them better.

- Track: System Design › Recommendation Systems › Designs
- Type: Design · 25 min
- Page: https://aimlrounds.com/tracks/system-design/design-rec-foundation-model/
- Before this: Distillation: How Small Models Learn from Big Ones (`fundamentals/distillation`), The Next-Token Objective (`fundamentals/next-token-prediction`)
- Quiz topic: `sdrec`

## Intuition

### The situation

A large app runs hundreds of recommendation models, one per surface: feed, video, ads and search. Each learns only from its own slice of data, and improvements in one rarely help another. The interviewer asks:

> A large app runs hundreds of separate recommendation models, one per surface, each trained on its own slice of data. Design one large foundation model that makes all of them better.

#### Ask before designing

- **Today:** hundreds of per-surface models (feed, video, ads, search), each seeing only its own data.

- **Data:** long histories of views, clicks, add-to-carts, purchases and searches, up to thousands of events per user.

- **Constraints:** each surface has tight latency; the big model can't run on every request.

- **Must never happen:** a stale teacher quietly making students worse, or one surface's objective hurting another.

- **Success metrics:** per-surface online outcomes (conversions, orders, clicks that lead somewhere), plus training efficiency.

### The idea

Think of a head chef who trains every cook in a restaurant chain. The head chef doesn't cook every dish; they teach recipes and techniques, and each kitchen still cooks fast for its own customers.

[Figure: Long event sequences from every surface train one large next-item model. It transfers to small per-surface models by distillation and shared embeddings, or serves as one retriever.]

_Train big once; serve small everywhere._

### Play

**Try to break it.** Switch between the two systems.

#### Two systems, measured on their own surfaces

From each company's post: ads results were launch figures for a quarter; commerce results were relative lifts in an online A/B test.

Notice the two uses. One is a **teacher** that improves hundreds of existing models; the other is a **new candidate source** added beside existing retrievers. Both avoid serving the giant model on every ranking call.

**Now say why:** why do neither of them run the large model on every ranking request?

## Architecture

### Architecture

#### In one breath

Train one large model on **long sequences of user events** across every surface, predicting the **next item** the way a language model predicts the next token. It's too big to serve everywhere, so **transfer** what it learns: distil it into the smaller per-surface models, share its embeddings with them, or let it serve as one retrieval source among several. Each surface keeps its own objective and latency budget.

#### One teacher, many students

1. **Event sequences:** build each user's sequence of actions across surfaces, with timestamps, without compressing it into one fixed vector.

2. **Foundation model:** a transformer with a causal mask predicts the next item; time gaps and recency are encoded explicitly. Non-sequence features (user and item attributes) feed interaction layers alongside.

3. **Training:** a sampled softmax over millions of items, with negatives shared across the batch and hard negatives that avoid true positives.

4. **Transfer:** the foundation model labels data and produces embeddings for the per-surface models: distillation, shared representations, or both. Large surfaces learn directly; smaller ones through domain models.

5. **Serving:** per-surface models stay small and fast. The foundation model can also serve as one retrieval model among several, with rankers and diversity rules after it.

##### Stale teachers

The teacher is trained less often than students, so its labels age. A small adapter that corrects the teacher's outputs using the newest data keeps students learning from fresh signals.

#### The numbers worth saying out loud

All of these are assumptions for the interview, not figures from a real system.

| Question | Working | Result |
|---|---|---|
| Training events | 500 million users × 2,000 events | **1 trillion** |
| Per-surface models | given | **200** |
| Teacher labels a day | 200 surfaces × 1 billion examples | **200 billion forward passes** |
| Item embeddings | 10 million items × 256 dims × 2 bytes | **about 5 GB** |

Generating teacher labels is a large ongoing cost, so share embeddings where possible and generate labels only for the training data students actually use.

## In practice

### In practice

#### What every foundation-model design gets asked

- **Why one model:** each surface alone sees little data; one model learns from all of them, so an engagement signal on one app can improve predictions on another.

- **Long sequences:** compressing histories into a fixed vector loses signal; attention over thousands of events needs custom kernels and efficient training.

- **Cold start:** item IDs alone don't help new items; content features, or semantic IDs built from content, let new items share what similar items learned.

- **Efficiency:** lighter variants of the model let most experiments run cheaply; large-scale training needs careful parallelism and compilation caching.

- **Ensembles:** as a retriever, train it to find what other retrievers miss, treating their predictions as hard negatives.

- **Rollout:** ship to the largest surfaces first, measure each surface's own metric, and keep the old models as a fallback.

#### What the real systems reported

- **Ads foundation model:** learns from ads and organic activity across apps, with sequences up to thousands of events; transfers to hundreds of smaller models directly and through domain models, by distillation, representation learning and parameter sharing; 23× more effective training compute; 5% more ad conversions on one app and 3% on another's feed.

- **Commerce model:** a next-product transformer trained on searches, views, add-to-carts, favourites and purchases; one retrieval model in an ensemble; +0.94% orders, +5% high-quality clicks and +0.71% conversion in an online test.

From the two posts (Nov 2025 and Feb 2026). Neither reports serving latency figures.

### The answer that sounds right

#### "Replace all the small models with the big one"

It sounds simpler, but each surface scores thousands of items per request in milliseconds, which a huge model can't do. The gains come from teaching the small models, or adding the big one as a retriever, not from serving it everywhere.

## Say it

### A large app runs hundreds of separate recommendation models, one per surface, each trained on its own slice of data. Design one large foundation model that makes all of them better.

#### The interviewer pushes further

Follow-up 1 of 3

Why not serve the foundation model directly?

Latency and cost: per-surface models score thousands of items per request in milliseconds. Distillation and shared embeddings carry most of the gain into those small models.

Follow-up 2 of 3

Students got worse a month after launch. Why?

The teacher's labels went stale as behaviour changed. Retrain the teacher more often, or correct its outputs with an adapter trained on the newest data.

Follow-up 3 of 3

How does this help new items?

Not through ID embeddings, which need history. Use content features or semantic IDs, so a new item starts near similar items.

I'd clarify how many surfaces and models exist, the data available and each surface's latency. I'd train one large transformer on long, time-stamped event sequences across all surfaces, predicting the next item with a sampled softmax and hard negatives, plus interaction layers for non-sequence features. It's too expensive to serve on every request, so its value comes through transfer: it labels data and shares embeddings to distil into the small per-surface models, directly for big surfaces and via domain models for small ones. A small adapter corrects stale teacher outputs with fresh data. It can also act as one more retriever in an ensemble. I'd roll out surface by surface, measure each surface's own metric, and handle new items with content-based features or semantic IDs.

**Key terms and sources**

Based on published posts: a social network's generative ads model (Nov 2025) and a commerce platform's generative recommendations (Feb 2026). The lab uses the posts' reported results; the estimate is ours. Uses distillation, transformers and next-token prediction.
