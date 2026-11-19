# Design Feed Ranking

> A photo and video app shows each user a feed of posts from billions of candidates. Design the ranking so people see what they value, quickly, without filling the feed with clickbait.

- Track: System Design › Feeds and Ranking › Designs
- Type: Design · 25 min
- Page: https://aimlrounds.com/tracks/system-design/design-feed-ranking/
- Before this: Ranking Metrics (`fundamentals/ranking-metrics`), Embeddings and Vector Indexes (`ai-engineering/embeddings-and-vector-indexes`)
- Quiz topic: `sdrec`

## Intuition

### The situation

A photo and video app has hundreds of millions of daily users and billions of posts. Its discovery feed shows posts from accounts users don't follow. Engagement is up, but so are complaints about clickbait and repetitive feeds. The interviewer asks:

> A photo and video app shows each user a feed of posts from billions of candidates. Design the ranking so people see what they value, quickly, without filling the feed with clickbait.

#### Ask before designing

- **Surface:** a feed of posts from accounts the user doesn't follow, refreshed when they open it.

- **Scale:** hundreds of millions of daily users and billions of posts.

- **Latency:** the first screen must load in well under a second.

- **What "good" means:** not just clicks: likes, saves, shares and time well spent, minus negative feedback like "see less".

- **Must never happen:** harmful content surfaced, or a feed of one author or the same clickbait.

- **Success metrics:** engagement per session, negative feedback rate, return visits and integrity incidents.

### The idea

Think of a magazine editor with a mountain of submissions. Assistants quickly shortlist a few hundred, a senior editor reads the best hundred closely and predicts how readers will react, and the final layout avoids two pieces by the same writer side by side.

[Figure: Many sources pull thousands of candidates. A light model keeps about a hundred. A heavy model predicts each action, and a value model combines them before integrity and diversity rules.]

_Cheap steps cut the pile; the expensive model sees only the best._

### Play

**Try to break it.** Set all three weights to zero. Then raise the "see less" penalty. Then turn on the diversity rule.

#### Which post goes first?

**The feed, top to bottom**

Illustrative: four made-up posts with predicted probabilities, and clicks always weighted 1. The formula follows the post's value model: a weighted sum of predicted actions, minus negative ones.

Set every weight to zero so only clicks count: **clickbait wins**, because it gets clicked and then regretted. Raise the "see less" penalty and shares, and posts people value move up. These weights are product decisions, tuned against online metrics, not learned by the model itself.

**Now say why:** why does ranking by clicks alone push clickbait to the top?

## Architecture

### Architecture

#### In one breath

Use a **funnel**. Many **retrieval sources** pull a few thousand candidates from billions; a **light model** narrows them to about a hundred; a **heavy multi-task model** predicts click, like, share and "see less" for each; a **value model** combines those predictions with tunable weights; and a final step applies **integrity and diversity** rules. Cache embeddings, precompute where you can, and tune the weights against online metrics.

#### The funnel

1. **Retrieval:** several sources each return hundreds of candidates: a two-tower model matching user and post embeddings through an ANN index, posts similar to what the user liked, saved or shared, trending and locally popular posts. Their outputs are mixed with tunable weights.

2. **First-stage ranking:** a light two-tower model, trained to imitate the heavy model, narrows a few thousand candidates to about a hundred.

3. **Second-stage ranking:** a heavy multi-task network predicts the probability of each action (click, like, share, see less) using rich user–post interaction features.

4. **Value model:** one score per post: a weighted sum of the predicted probabilities, with negative actions subtracted.

5. **Final re-ranking:** remove or demote harmful content, then apply diversity rules such as no two posts from the same author in a row.

##### Why a funnel?

The heavy model can't score billions of posts in time. Cheap steps cut the set, so the expensive model only sees the best hundred.

##### Caching and precomputing

Post embeddings are computed daily and served from an ANN index; user embeddings are computed fresh. At peak hours, some users' recommendations can be precomputed off-peak.

#### The numbers worth saying out loud

All of these are assumptions for the interview, not figures from a real system.

| Question | Working | Result |
|---|---|---|
| Feed requests a second at peak | 300 million users × 5 opens ÷ 86,400 × 3 | **about 52,000** |
| First-stage scores a second | 52,000 × 3,000 candidates | **about 156 million** |
| Heavy-model scores a second | 52,000 × 100 | **about 5.2 million** |
| Post embedding index | 2 billion posts × 128 dims × 2 bytes | **about 512 GB** |

The light stage must be cheap per item, which is why it uses cached embeddings; the heavy model's budget is spent only on the top hundred.

## In practice

### In practice

#### What every feed design gets asked

- **Why multi-task?** One model predicting several actions shares what it learns, and the value model can change the balance between them without retraining.

- **Distillation:** train the light model to predict which posts the heavy model would put in its top results, so the two stages agree.

- **Freshness:** retrain or fine-tune frequently, even hourly, and compute user embeddings from recent activity.

- **Cold start:** new posts get exposure through trending or exploration sources until they have engagement data.

- **Feedback loops:** the model learns from what it showed; keep some exploration so new creators and topics get a chance.

- **Tuning:** hundreds of parameters, like source weights and value-model weights, tuned online with careful experiments, or offline when offline metrics predict online ones well.

- **Integrity:** filter harmful content before ranking where possible, and demote borderline content in the final step.

##### Rollout

Test ranking changes with A/B tests on engagement and negative feedback, run long enough to see past novelty, with guardrails on integrity and creator diversity.

#### What the real system reported

- **Scale:** hundreds of millions of daily visitors, and a media pool of billions of items.

- **Funnel:** retrieval from several sources, each selecting hundreds of items; a light first stage over thousands of candidates; a heavy second stage over the best 100; final re-ranking with integrity and diversity rules.

- **Retrieval:** a two-tower model with daily item embeddings in an ANN service and online user embeddings, plus similar-items retrieval from what the user liked, saved or shared, with low-quality items filtered out.

- **Ranking:** the first stage is a two-tower model distilled from the second; the second is a multi-task multi-label network. Models train continually and can be fine-tuned hourly.

- **Value model:** expected value = weighted probabilities of click, like and others, minus "see less", with hundreds of tunable parameters tuned by online Bayesian optimisation, which can take over a month, or offline when offline metrics predict online ones.

The company's own description. The post gives no latency figures or A/B results.

### The answer that sounds right

#### "Rank by predicted engagement and you're done"

It sounds right, since engagement is what you want. But the most clicked posts are often regretted, and one engagement number hides likes, shares and "see less". Predict each action, subtract the negative ones in a value model, and watch negative feedback as a guardrail.

## Say it

### A photo and video app shows each user a feed of posts from billions of candidates. Design the ranking so people see what they value, quickly, without filling the feed with clickbait.

#### The interviewer pushes further

Follow-up 1 of 3

Why not rank only by predicted click probability?

Clicks reward clickbait that people regret. Predicting several actions, including negative ones like "see less", and combining them in a value model lets you rank by what people actually value.

Follow-up 2 of 3

Why have two ranking stages?

The heavy model is too expensive to run on thousands of candidates per request. A light model trained to imitate it cuts the set to about a hundred, so the heavy model runs only where it matters.

Follow-up 3 of 3

New creators never get shown. How do you fix it?

Add exploration: a retrieval source that gives new posts some exposure, and measure creator diversity as a guardrail, so the feedback loop doesn't lock in existing favourites.

First I'd clarify the surface, scale, latency and what "good" means beyond clicks. I'd build a funnel. Several retrieval sources each return hundreds of candidates: a two-tower model with post embeddings in an ANN index, posts similar to what the user liked or shared, and trending posts, mixed with tunable weights. A light two-tower model, distilled from the heavy one, narrows a few thousand to about a hundred. A heavy multi-task network predicts click, like, share and "see less" using rich interaction features. A value model combines them into one score with weights we tune, subtracting negative actions so clickbait doesn't win. The final step removes harmful content and applies diversity rules. For speed I'd cache embeddings and precompute at peak. Models retrain frequently, new posts get exploration, and changes go through A/B tests with guardrails on negative feedback and integrity.

**Key terms and sources**

Based on a social app's published post: Meta's "Scaling the Instagram Explore recommendations system" (August 2023). The lab's posts and probabilities and the estimate are ours. Uses ranking metrics, embeddings and ANN and feedback loops.
