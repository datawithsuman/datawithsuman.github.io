# Design Short-Video Recommendations

> A short-video app must learn what each user likes within minutes of their first swipes, while new videos and users arrive constantly. Design the recommendation system.

- Track: System Design › Recommendation Systems › Designs
- Type: Design · 25 min
- Page: https://aimlrounds.com/tracks/system-design/design-short-video-recs/
- Before this: Embeddings and Representation Learning (`fundamentals/embeddings`), Classification Metrics (`fundamentals/classification-metrics`)
- Quiz topic: `sdrec`

## Intuition

### The situation

A short-video app has tens of millions of daily users swiping through a full-screen feed. Interests shift within a session, and new videos and users arrive every minute. The interviewer asks:

> A short-video app must learn what each user likes within minutes of their first swipes, while new videos and users arrive constantly. Design the recommendation system.

#### Ask before designing

- **Surface:** a full-screen feed, one video at a time; every swipe, watch time, like and share is feedback.

- **Freshness:** interests shift within a session, and new videos must be shown within minutes of upload.

- **Scale:** tens of millions of daily users, billions of IDs, a model of several terabytes.

- **Must never happen:** a broken data stream silently training the model on junk, or the feed collapsing into one topic.

- **Success metrics:** offline AUC on next actions, and online watch time, retention and negative feedback.

### The idea

Think of a street musician who changes songs as the crowd reacts. They don't wait for tomorrow's review; they notice who stops and who walks away, and adjust right now.

[Figure: Serve with retrieve-then-rank. Log actions and features. Join them into examples. Train online and push changed embeddings to serving every few minutes.]

_Close the feedback loop in minutes, not days._

### Play

**Try to break it.** Shorten the sync interval from 5 hours to 30 minutes. Then raise the IDs updated per minute.

#### Sync interval and what it costs

From the paper: Table 2 (Criteo, DeepFM, average AUC in %) and section 3.2.2 (4 KB × 100,000 ≈ 400 MB). On a live ads model, online training beat batch by 14 to 18% in AUC over seven days.

Shorten the interval: AUC keeps rising. Then raise the IDs updated per minute: the bandwidth grows fast. That's why only **changed** embeddings are synced every minute or so, and dense weights only daily.

**Now say why:** why sync only changed embeddings every minute, but dense weights daily?

## Architecture

### Architecture

#### In one breath

Retrieve, then rank, like any recommender, but make the ranker **learn continuously**. Stream user actions and features, **join** them into training examples, train **online**, and push changed parameters to serving every few minutes. Give every user and video ID its **own embedding** instead of hashing IDs into shared slots, and keep memory in check by admitting only IDs seen often enough and **expiring** IDs that go quiet.

#### A loop that closes in minutes, not days

1. **Serve:** retrieve a few thousand candidates (popular, followed, similar to recent watches), then rank them with a deep model on user, video and context features.

2. **Log:** user actions go to one stream, the features used at serving time to another.

3. **Join:** a streaming job pairs each action with its features by request ID; features waiting for late actions spill to disk.

4. **Train online:** training workers read joined examples from the stream and update parameter servers continuously.

5. **Sync:** changed embeddings are pushed to the serving parameter servers every few minutes; dense weights, which change slowly, daily.

##### Why not hash IDs?

Hashing billions of IDs into a smaller table makes unrelated users or videos share one embedding, which blurs what the model learns. A **collisionless** hash table gives each ID its own row. To limit memory, add an ID only after it appears enough times, and expire IDs inactive for a set period.

#### The numbers worth saying out loud

All of these are assumptions for the interview, not figures from a real system.

| Question | Working | Result |
|---|---|---|
| Views a day | 50 million users × 100 videos | **5 billion** |
| Training examples a second | 5 billion ÷ 86,400 | **about 58,000** |
| Embedding memory | 2 billion IDs × 64 dims × 4 bytes | **about 512 GB** |
| Ranking scores a second at peak | 20,000 requests × 1,000 candidates | **20 million** |

Embeddings dominate memory, which is why frequency filtering and expiry matter: most IDs appear only a handful of times.

## In practice

### In practice

#### What every real-time recommender gets asked

- **Cold start:** new videos get exploration traffic and content features; new users get popular and diverse content until their first swipes, which online training picks up within minutes.

- **Late actions:** some actions, like a share or a purchase, come long after the view. The joiner waits a window, then keeps waiting features on disk.

- **Negative sampling:** if you train on a sample of non-actions, correct the predicted probabilities at serving time.

- **Fault tolerance:** parameter servers snapshot daily; losing up to a day of updates barely hurt quality in the paper.

- **Safety:** detect broken streams (sudden label drops) and pause online training automatically.

- **Feed health:** add diversity and freshness rules after ranking so one topic doesn't take over.

#### What the real system reported

- **Embedding table:** a collisionless table using cuckoo hashing; on a public movie dataset, hashing collided 7.73% of user IDs, and collisionless tables consistently did better.

- **Memory controls:** IDs admitted after a minimum count, and expired after inactivity; popular IDs appear millions of times, unpopular ones fewer than ten.

- **Sync:** changed sparse parameters every few minutes, dense ones daily at low traffic; more frequent syncs always helped AUC.

- **Live test:** online training beat batch training by 14 to 18% AUC on an ads model across seven days.

From the paper (2022). It names a commercial product that uses it, not which apps.

### The answer that sounds right

#### "Retrain the model every night"

It sounds standard, but in a short-video feed interests change within a session and new videos need feedback in minutes. In the paper, more frequent syncing always raised AUC, and online training beat batch training by 14 to 18% on a live model.

## Say it

### A short-video app must learn what each user likes within minutes of their first swipes, while new videos and users arrive constantly. Design the recommendation system.

#### The interviewer pushes further

Follow-up 1 of 3

Why not just retrain every night?

Interests change within a session and new videos need feedback fast. In the paper, more frequent syncing always raised AUC, and online training beat batch by a wide margin on a live model.

Follow-up 2 of 3

What's wrong with hashing IDs into a smaller table?

Unrelated IDs share one embedding, which mixes their signals. A collisionless table avoids it; filtering rare IDs and expiring stale ones keeps memory under control.

Follow-up 3 of 3

The share event stream breaks and the model starts recommending junk. Why?

Online training kept learning from data with no positives. Monitor label rates and pause training automatically when they shift suddenly.

#### The 30-second answer

I'd clarify the feed format, how fast interests shift, scale and metrics. Serving is retrieve then rank: a few thousand candidates from several sources, ranked by a deep model. The key is learning in real time. Actions and serving-time features stream separately and a joiner pairs them by request ID, holding features for late actions. Training runs online from that stream, and changed embeddings are pushed to serving every few minutes, with dense weights daily. Each user and video ID gets its own embedding in a collisionless table, with frequency filtering and expiry to control memory. New videos get exploration and content features. I'd guard against broken streams by pausing training, snapshot daily, add diversity rules, and judge by watch time, retention and negative feedback.

**Key terms and sources**

Based on a short-video company's published paper: ["Monolith: Real Time Recommendation System With Collisionless Embedding Table"](https://arxiv.org/abs/2209.07663) (RecSys 2022 workshop). The lab uses the paper's own numbers; the estimate is ours. The paper doesn't say which product runs it. Uses embeddings, classification metrics and training-serving skew. · checked 15 Nov 2026
