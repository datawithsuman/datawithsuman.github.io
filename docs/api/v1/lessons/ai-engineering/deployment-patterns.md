# Deployment Patterns: Shadow, Canary, A/B and Rollback

> How long must a canary run to catch a regression?

- Track: AI Engineering › MLOps › Lessons
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/ai-engineering/deployment-patterns/
- Before this: Batch vs Online vs Streaming Inference (`ai-engineering/batch-vs-online-inference`)
- Quiz topic: `mlops`
- Sources checked: 2026-10-29 · Text last changed: 2026-11-20 · Version: 066f7f4137

## Intuition

### The situation

A new ETA model is 0.5 minutes better in offline tests, and the app serves 200,000 orders a day. A colleague runs a canary for an hour, sees nothing wrong and wants to ship. The interviewer asks:

> How long must a canary run to catch a regression?

**Running example:** a new ETA model is 0.5 minutes better in offline tests. The app serves 200,000 orders a day; a wrong ETA costs customer trust and support tickets.

#### Offline wins don't guarantee online wins

Skew, data the test set didn't cover, feedback effects and plain bugs mean a model can look better offline and be worse live. Switching everyone at once turns any of these into an outage; never switching means never improving.

### The idea

Think of changing a recipe at a busy restaurant. First you run it in the kitchen without serving it. Then one table gets it, then a section, then everyone, with the old recipe still ready. One happy table tells you it isn't poison, not that it's better.

[Figure: A staged release: offline gate, shadow, canary, A/B test and ramp. At a 5 percent canary, detecting a 0.5 minute regression takes about 4,000 orders per model and 10 hours. Detecting 0.25 minutes takes 16,000 orders and 1.6 days.]

_From the lab: 80% power, and an error spread of 8 minutes. Real tests must also cover daily and weekly cycles._

### Play

**Try to break it.** Move the regression from 0.5 to 0.25 minutes, and watch the orders needed. Then raise the traffic share on the canary, and watch the time and the customers exposed.

#### "Run the canary for an hour, it looks fine"

Two-sample comparison of mean absolute ETA error: per-order error standard deviation 8 minutes, 5% significance (two-sided), 80% power: n ≈ 2(1.96 + 0.84)²σ² / δ² per model. 200,000 orders a day. Real tests must also cover daily and weekly cycles.

To detect a **0.5-minute** worsening with 80% power, you need about **4,000 orders on each model**; with 5% of traffic on the canary that's roughly **10 hours**. To catch a subtler **0.25-minute** regression you need four times as many orders, **16,000**, about 1.6 days at 5%. So "an hour looked fine" only rules out large regressions, and since ETA errors differ between lunch, dinner and weekends, real tests also need to span those cycles. More traffic on the canary is faster but exposes more customers if it's bad: that trade-off is why releases ramp.

**Now say why:** what does an hour of "looks fine" actually rule out?

## How it works

### How it works

#### In one breath

A model that passes offline tests can still fail on live traffic, so models are released in stages. **Shadow**: the new model receives real requests and its predictions are logged but not used; this catches crashes, latency and skew with zero user risk. **Canary**: a small share of traffic (1–5%) actually uses the new model while you watch error, latency and business metrics, with **automatic rollback** if they regress. **A/B test**: a controlled experiment with enough users and time to measure the business effect with statistical confidence. Then **ramp up** gradually. The key number is sample size: detecting a small regression takes many more requests than a big one (halving the effect you want to detect quadruples the traffic needed), which sets how long each stage must run. What you'll be able to do after this: design a staged rollout, estimate canary size and duration, and choose rollback criteria.

#### A staged release

1. **Offline gate:** beats the current model on a recent, time-split test set and on key slices (cities, peak hours); passes data and model validation checks.

2. **Shadow:** runs on live requests in parallel; compare predictions, latency and errors with the current model; no user impact.

3. **Canary:** 1–5% of traffic uses it; guardrail metrics (error, latency, crash rate, complaint rate) with automatic rollback thresholds.

4. **A/B test:** enough traffic for long enough to measure the target metric and business outcomes (late-order complaints, conversion); decide on pre-registered criteria.

5. **Ramp and keep a holdout:** 25% → 50% → 100%, keeping the previous model deployable for instant rollback; optionally a small long-term holdout to measure lasting effects.

For ranking models, **interleaving** (mixing both models' results in one list and seeing which items users pick) detects differences with far less traffic than A/B tests (Chapelle et al. 2012).

## In practice

### In practice

#### Making rollouts safe and boring

- **Automatic rollback** on guardrail breaches (error spikes, latency, crash rate); rollback must be one switch, with the previous model still deployed.

- **Pre-register** the success metric, guardrails, sample size and duration before starting, to avoid peeking and cherry-picking (Kohavi et al.).

- **Watch slices,** not just averages: a model can improve on average and be much worse for one city or for new restaurants.

- **Separate model and code releases** when possible, so a regression can be attributed.

- **Feedback loops:** a model that changes behaviour (e.g. ETAs that change ordering) needs longer tests and holdouts to see the full effect.

#### Increase exposure only as evidence accumulates

Shadow for safety, canary for guardrails, A/B for impact, ramp with instant rollback; size each stage from the smallest regression you need to catch.

### The answer that sounds right

#### "An hour of canary is enough"

It sounds right, if nothing has gone wrong by then. But an hour only rules out large regressions. Catching 0.5 minutes takes about 10 hours at 5% traffic, and errors also differ between lunch, dinner and weekends. Deploying to everyone because offline metrics improved is worse still: offline isn't online.

## Say it

### How long must a canary run to catch a regression?

#### The interviewer pushes further

Follow-up 1 of 3

Shadow vs canary?

Shadow has zero user impact and validates technical behaviour and prediction differences; canary measures real user effect on a small share, with real risk.

Follow-up 2 of 3

The A/B test shows +0.3% conversion, p = 0.04, after peeking daily. Ship?

Repeated peeking inflates false positives; use the pre-registered duration or sequential testing methods, check guardrails and slices, and consider replicating.

Follow-up 3 of 3

How do you roll back an ML model quickly?

Keep the previous version deployed behind a traffic switch or registry alias, with compatible features; rollback is a config change, not a rebuild.

#### The 30-second answer

I'd release in stages. First an offline gate on a recent time-split test set and key slices. Then shadow mode, running the model on live traffic without acting on it, to catch crashes, latency and skew. Then a canary on a few percent of traffic with guardrail metrics and automatic rollback, then an A/B test sized to detect the effect we care about, and a gradual ramp with the old model kept for instant rollback. Sample size drives duration: detecting half as large a regression needs four times the traffic, so I'd compute it upfront, cover daily cycles and pre-register the criteria.

**Go further**

#### What not to say

- "Deploy to everyone if offline metrics improve." Offline ≠ online.

- "An hour of canary is enough." Only for large regressions.

**Key terms and sources**

How to replace a production model safely: offline validation gates, shadow deployment (predict but don't act), canary releases (a small share of real traffic), A/B tests for business impact, interleaving for ranking, gradual ramp-up, automatic rollback, and how much traffic and time it takes to detect a regression · built from Kohavi, Tang & Xu (Trustworthy Online Controlled Experiments, 2020), Breck et al. (The ML Test Score, 2017), Sculley et al. (NeurIPS 2015), Huyen (Designing Machine Learning Systems, 2022) and Chapelle et al. (Large-scale validation of interleaving, TOIS 2012) · checked 29 Oct 2026

#### Sources

1. R. Kohavi, D. Tang & Y. Xu, _Trustworthy Online Controlled Experiments: A Practical Guide to A/B Testing_, Cambridge University Press 2020.

2. E. Breck et al., "The ML Test Score", IEEE Big Data 2017.

3. O. Chapelle et al., "Large-Scale Validation and Analysis of Interleaved Search Evaluation", ACM TOIS 2012.

4. C. Huyen, _Designing Machine Learning Systems_, O'Reilly 2022 (ch. 9, continual learning and test in production).

5. D. Sculley et al., "Hidden Technical Debt in Machine Learning Systems", NeurIPS 2015.
