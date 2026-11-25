# Batch vs Online vs Streaming Inference

> When do you precompute predictions, and when compute them live?

- Track: AI Engineering › MLOps › Lessons
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/ai-engineering/batch-vs-online-inference/
- Quiz topic: `mlops`
- Sources checked: 2026-10-29 · Text last changed: 2026-11-20 · Version: 45e98078d2

## Intuition

### The situation

The app needs two predictions: restaurant prep time, which changes slowly, and order ETA, which depends on the address and the courier's position. A colleague says to run everything in real time, and another says to precompute everything more often. The interviewer asks:

> When do you precompute predictions, and when do you compute them live?

**Running example:** the app needs two predictions. **Restaurant prep time** (per restaurant, changes slowly through the day) and **order ETA** (per order: depends on the customer's address, the courier's position and live traffic). 50,000 restaurants, 200,000 orders a day.

#### When should the prediction be computed?

Computing in advance makes serving trivial and cheap, but only works if you can enumerate the inputs and the answer won't go stale. Computing on demand handles any input and is always current, but needs a low-latency service, fresh features and capacity for peak traffic.

### The idea

Think of a kitchen. Dishes you can predict get cooked ahead and served instantly, though they may be sitting a while, and some never sell. A custom order has to be made when it comes in. And no amount of cooking ahead can prepare a dish for an order nobody has placed yet.

[Figure: Batch every 6 hours is about 3 hours stale with a 5 millisecond lookup. Online with hourly features is about 60 milliseconds. Online with streaming features is about 30 seconds stale and about 60 milliseconds.]

_Illustrative numbers from the lab._

### Play

**Try to break it.** In batch mode, shorten the refresh interval, and watch the share of predictions requested. Then switch to online, and to online with streaming.

#### "Just precompute everything more often"

Illustrative: 50,000 restaurants; batch staleness = half the interval; online features refreshed about hourly; streaming features ~30 s old; ~5 ms lookup vs ~60 ms online prediction. "Share requested" compares requests with predictions computed (a rough waste indicator).

**Batch every 6 hours** computes 200,000 prep-time predictions a day with lookups in about 5 ms, but they're on average **3 hours** stale: a restaurant that got swamped at 7 pm still shows its 4 pm estimate. Refreshing **hourly** cuts staleness to 30 minutes but computes **1.2 million** predictions, only 16.7% of them ever requested. And no refresh rate can produce an **order ETA** in advance: it depends on the customer's address and the courier's position at request time. That needs **online** inference, and with **streaming** traffic and courier features, staleness drops to seconds at the price of a streaming pipeline.

**Now say why:** why can no refresh rate produce an order ETA in advance?

## How it works

### How it works

#### In one breath

**Batch inference** computes predictions for every entity on a schedule (say every 6 hours) and stores them for instant lookup: cheap per prediction and simple, but predictions are as stale as the last run and you compute many that nobody asks for. **Online inference** computes a prediction when a request arrives, using the request's own inputs: needed whenever the prediction depends on things only known at request time (this customer, this address, right now), at the cost of serving infrastructure and latency. **Streaming** keeps features fresh (seconds, from event streams) for an online model, for when the world changes fast. Most production systems are hybrids: batch for slow-changing, entity-level scores; online for request-specific predictions; streaming only for the features where freshness pays. What you'll be able to do after this: choose a serving mode for a prediction, and explain the freshness / latency / cost trade-off.

#### The three modes

| | Batch | Online | Online + streaming features |
|---|---|---|---|
| **When computed** | on a schedule, for all entities | per request | per request, features updated continuously |
| **Freshness** | up to one interval old | as fresh as its features | seconds |
| **Serving latency** | a key–value lookup (ms) | model + feature lookups (tens of ms) | same as online |
| **Works for** | entity-level scores: recommendations for a user, restaurant prep time, churn risk | request-specific predictions: ETA for this order, fraud on this payment | fast-changing signals: live traffic, courier positions, recent clicks |
| **Costs** | computes predictions nobody uses | always-on service sized for peaks | streaming pipelines are the hardest to build and run |

## In practice

### In practice

#### Hybrid designs

- **Batch candidates, online ranking:** recommenders precompute candidate lists per user overnight and re-rank online with session context.

- **Batch features, online model:** slow features (restaurant history) computed in batch, fast features (current queue, traffic) via streams, both fed to an online model; keep them consistent with a feature store.

- **Fallbacks:** if the online service is slow or down, serve the last batch prediction or a simple heuristic, and monitor how often fallbacks fire.

- **Edge / on-device** inference for latency or privacy, with model updates shipped periodically.

- **LLMs** are almost always online (inputs are open-ended); batch APIs are used for offline jobs like summarising yesterday's tickets (cost and latency).

#### Precompute what you can enumerate, compute live what you can't

Batch is cheapest when inputs are known in advance and change slowly; online is required when the prediction depends on the request; streaming is worth its complexity only for features whose freshness changes the answer.

### The answer that sounds right

#### "Real-time is always better"

It sounds right, since fresher feels better. But it's costlier and harder, and streaming pipelines are the hardest of all to build and run. Use it only where freshness pays. Precomputing everything fails the other way: it's not possible when inputs are open-ended, and an hourly refresh in the lab leaves only 16.7% of predictions ever requested.

## Say it

### When do you precompute predictions, and when do you compute them live?

#### The interviewer pushes further

Follow-up 1 of 3

How would you serve recommendations for 100 million users?

Batch-generate candidates per user, store them, and re-rank online using recent activity; only active users need online computation.

Follow-up 2 of 3

When is streaming worth it?

When predictions change meaningfully within minutes (fraud velocity, live traffic, inventory) and that change has business value; otherwise hourly batch features are simpler.

Follow-up 3 of 3

What's the main risk of mixing batch and streaming features?

Skew: the same feature computed differently in the two paths or at different freshness in training vs serving; define features once and log served values.

#### The 30-second answer

Batch inference precomputes predictions for all entities on a schedule and serves them by lookup: cheap and simple, but stale and wasteful for entities nobody asks about. Online inference computes on request with the request's inputs, which is required for things like an order ETA that depends on the customer's address and live courier positions, at the cost of a low-latency service sized for peaks. Streaming adds features updated within seconds for fast-changing signals. Most real systems are hybrids: batch for slow entity-level scores and candidates, online for request-specific predictions, streaming only where freshness changes the outcome, with fallbacks to batch values.

**Go further**

#### What not to say

- "Real-time is always better." It's costlier and harder; use it only where freshness pays.

- "Precompute every possible prediction." Not possible when inputs are open-ended.

**Key terms and sources**

How and when predictions get computed: batch (precompute and look up), online (compute on request), and streaming features feeding online models; the trade-offs in freshness, latency, cost and complexity; which prediction types can be precomputed; and hybrid designs used in real systems · built from Huyen (Designing Machine Learning Systems, O'Reilly 2022, ch. 7), Zinkevich (Rules of ML), Sculley et al. (NeurIPS 2015), Hermann & Del Balso (Meet Michelangelo, 2017) and Kleppmann (Designing Data-Intensive Applications, 2017) · checked 29 Oct 2026

#### Sources

1. C. Huyen, _Designing Machine Learning Systems_, O'Reilly 2022 (ch. 7, model deployment and prediction service).

2. M. Zinkevich, "Rules of Machine Learning", Google.

3. J. Hermann & M. Del Balso, "Meet Michelangelo: Uber's Machine Learning Platform", 2017 (batch and online prediction, shared features).

4. M. Kleppmann, _Designing Data-Intensive Applications_, O'Reilly 2017 (batch and stream processing).

5. D. Sculley et al., "Hidden Technical Debt in Machine Learning Systems", NeurIPS 2015.
