# Design a recommendation system

> How do you pick a few items for a user from millions?

- Track: System Design › Recommendation Systems › Designs
- Type: Design · 10 min
- Page: https://aimlrounds.com/tracks/system-design/recommendation-system/
- Before this: Gradient Boosting (`fundamentals/gradient-boosting`), Embeddings and Representation Learning (`fundamentals/embeddings`)
- Quiz topic: `sdrec`
- Sources checked: not stated · Text last changed: 2026-11-19 · Version: ed0caf4afb

## Intuition

### The situation

You are designing the home feed for a video app with millions of videos. Each user sees only a few. The interviewer asks:

> How would you pick a few videos for each user? Walk me through the design.

### The idea

Think of hiring. A quick CV screen cuts thousands of applicants to a shortlist, and only the shortlist gets a slow, careful interview. You cannot score every item for every user, so you narrow in stages. Each stage trades accuracy for speed.

[Figure: A funnel: all items narrow to a few hundred candidates, then to the few items shown to the user]

_Illustrative stages. Real counts depend on your latency budget._

## Architecture

### Four stages

1. 1**Request**User, context

2. 2**Candidate generation**Fast, high recall

3. 3**Ranking model**Slow, high precision

4. 4**Re-rank and filter**Business rules, diversity

Underneath all stages: a feature store for fresh user and item features, and an event log that feeds training.

### Trade-offs to name in the interview

- Candidate count vs latency.

- Feature freshness vs serving cost.

- Two-tower for retrieval vs cross-feature model for ranking.

## Numbers

### Capacity maths

requests per second ≈ [daily users] × [requests per user] ÷ 86,400 peak requests per second ≈ [requests per second] × [peak factor] ranking scores per second ≈ [peak requests per second] × [candidates per request] ranking servers ≈ [ranking scores per second] ÷ [scores per server per second]

Fill in the brackets with numbers from your interviewer or your own stated assumptions.

### The answer that sounds right

#### "Just rank every item with your best model"

It sounds right, because the best model gives the best scores. But cost grows with the catalogue size times the model cost per item. A cheap first stage cuts the catalogue to a few hundred, so the expensive model only runs where it can change the answer.

## Say it

### How would you pick a few videos for each user? Walk me through the design.

#### The interviewer pushes further

Follow-up 1 of 3

How many candidates should you keep?

Enough that good items survive the first stage, and few enough to meet the ranker's latency budget. There is no universal number, so you measure recall at different counts against that budget.

Follow-up 2 of 3

Why two towers for retrieval and a richer model for ranking?

Two towers encode the user and item separately, so item vectors can be computed ahead of time and searched quickly. The ranker runs on only a few hundred items, so it can afford features that combine the user and the item.

Follow-up 3 of 3

What happens if your features go stale?

Relevance drops, but fresher features cost more to serve. Keep fast-changing signals fresh and compute slow ones in batches. Logging features at serving time also keeps training consistent with what the model saw.

#### The 30-second answer

You can't score every item for every user, so I'd narrow in stages. A fast candidate step finds a few hundred items with high recall. A slower ranking model orders those for precision. A final step applies business rules and diversity. Underneath, a feature store serves fresh user and item features, and an event log feeds training. The main trade-offs are candidate count against latency, and feature freshness against serving cost.
