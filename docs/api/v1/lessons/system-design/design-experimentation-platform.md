# Design an Experimentation Platform

> Your company runs a few A/B tests by hand. Design a platform that lets teams run hundreds at once, and trust the results.

- Track: System Design › Experimentation › Designs
- Type: Design · 30 min
- Page: https://aimlrounds.com/tracks/system-design/design-experimentation-platform/
- Before this: Running Many Tests at Once (`fundamentals/running-many-tests-at-once`), Trust Checks: SRM and A/A Tests (`fundamentals/sample-ratio-mismatch`)
- Quiz topic: `sdexp`
- Sources checked: 2026-11-07 · Text last changed: 2026-11-20 · Version: dc8e977a3c

## Intuition

### The situation

Your company runs a few A/B tests by hand, with analysts writing queries for each one. Results take a week, teams argue about definitions, and a broken test recently shipped. Leadership wants hundreds of tests running at once. The interviewer asks:

> Your company runs a few A/B tests by hand. Design a platform that lets teams run hundreds at once, and trust the results.

#### Ask before designing

- **Scale:** say 50 million users a day, 300 tests at once, and 2 billion events a day.

- **Where do changes run?** Backend, web, mobile apps? Mobile users may not update their app for weeks.

- **What's the unit?** Mostly users, but do you need sessions, devices, or cities?

- **How fresh must results be?** Daily for decisions, but guardrail alarms in minutes.

- **Who uses it?** If non-specialists read the results, the platform must prevent mistakes by design.

- **Must never happen:** a slow or failed platform call breaking the product, or a broken test silently shipped.

### The idea

Think of a large hospital running many clinical trials. You need a fair way to assign patients, careful records of who actually took what, one agreed way to measure outcomes, and an independent office that checks each trial before anyone reads the results. Assigning patients is the easy part. Trust takes the rest of the work.

[Figure: Four jobs. Assign locally by hash. Log real exposure. Join exposures to metrics. Compute results after trust checks.]

_The hash is easy. Trust is the hard part._

### Play

**Try to break it.** Raise the tests and metrics. Then change the sample ratio cutoff.

#### What does scale do to trust?

Illustrative. Each result is read once a day, at 5% significance, with no real effects. Exposure rows assume each user reaches half of the running tests, with one row per test per day. That's why real systems deduplicate and aggregate early.

With 300 tests and 50 metrics each, a dashboard shows 15,000 results a day. If nothing worked, about 750 would still look significant. So the platform must lead with a few **decision metrics**, and label the rest as exploratory. At a 0.01 cutoff, 3 healthy tests get a sample ratio alarm each day. Move it to 0.001, and that falls to 0.3, which is why large platforms use stricter cutoffs. Now look at the exposure rows: they grow with tests times users, which is why this is the part of the pipeline to design first.

**Now say why:** why must a platform show only a few decision metrics by default?

## Architecture

### Architecture

#### In one breath

Split it into four jobs. **Assignment** hashes each user locally, with no network call. **Exposure logging** records who actually reached each change. A **metrics pipeline** joins exposures to events each day. A **stats engine** computes results, with trust checks first. The hard parts aren't the hashing, but making results trustworthy by default: automatic sample ratio checks, one agreed metric definition, and stopping rules built in, so a dashboard can't invite peeking.

#### Four jobs, plus the rules around them

| Part | What it does | Key choice |
|---|---|---|
| **Config service** | Stores tests, splits, targeting and metrics, with review before launch | Pushed as data files, not code, so tests launch quickly and non-engineers can create them |
| **Assignment SDK** | Computes hash(user, salt) mod buckets, inside the app or server | Local, with no network call and no stored table, and a safe default if the config is missing |
| **Exposure logs** | Records when a user actually reached the change | Log at the moment of use, not at assignment |
| **Metrics pipeline** | Joins exposures to events, and builds per-user daily totals | One central metric definition, so teams don't disagree on what "orders" means |
| **Stats engine** | Computes effects, intervals, CUPED, the delta method and corrections | Store per-user totals, so results can be recomputed |
| **Trust and decision layer** | Runs sample ratio checks and guardrails, then shows the result | Hide or flag results if trust checks fail |

##### Running many tests

Use layers. Each layer has its own hash, so a user gets one bucket per layer. Tests in different layers overlap, and tests in the same layer are exclusive. Keep a small domain for big changes that touch many layers. The system tracks which settings belong to which layer, and rejects conflicting tests when they're created.

##### Getting exposure right

If everyone assigned counts, those who never saw the change dilute the effect. So analyse users from their first exposure, in both groups. Control must log too, at the point where treatment would've changed. Otherwise the groups won't be comparable.

##### Launch flow

1. Create the test: hypothesis, primary metric, guardrails, sample size and runtime, filled from past data.

2. Run automatic checks: is there a control, is the traffic free, is the split valid?

3. Canary on a small share, watching crashes and latency in near real time.

4. Ramp up to the planned size.

5. Read results only at planned looks, once trust checks pass.

6. Decide by the agreed rule, and record it.

#### The numbers worth saying out loud

All of these are assumptions for the interview.

| Question | Working | Result |
|---|---|---|
| Assignment calls | 50 million users × 40 checks a day | 2 billion a day, about 23,000 a second |
| As a network call | 23,000 a second, at a 20 ms wait each | Too slow and too fragile, so hash locally |
| Exposure rows | 50 million × 300 tests × half reached | 7.5 billion a day, before deduplication |
| Per-user totals | 7.5 billion × 50 metrics | 375 billion values at worst, so compute only what each test needs |
| Storage for exposures | 7.5 billion × 40 bytes | About 300 GB a day |

The hash is cheap. The join between exposures and events is what costs money, so that's what to optimise: partition by day and user, reuse daily totals, and backfill only what changed.

## In practice

### In practice

#### What the interviewer will push on

- **Hash quality:** test that assignment is random and independent across salts, using A/A tests on past data. A bad hash correlates tests silently.

- **Ramping:** widening a test should keep users in their group. Keep the same hash and extend the bucket range. Analyse carefully, as early users have had longer exposure.

- **Mobile:** old app versions can't be updated. Ship the config with a safe default, and log the version, because exposure is delayed and uneven.

- **Logged-out users:** device or cookie IDs change, so one person can land in both groups. Decide what happens at sign-in, and measure how often it occurs.

- **Peeking by design:** show daily guardrails freely, but hide the primary decision until a planned look, or use always-valid intervals.

- **Automatic shutdown:** a guardrail alarm can stop a test, using sequential thresholds, as long as the rule was agreed beforehand.

- **Interactions:** scan pairs that share a surface, with corrections for how many you check. Real ones appear rare, so treat alarms as leads.

- **Failure modes:** if the platform fails, the product must carry on in the default experience, and that period must be flagged in the analysis.

- **Institutional memory:** store every test, its result and its decision. Past tests supply variance estimates and show which proxy metrics really predict outcomes.

#### How real teams approached it

- **Layers made it scale:** Google moved from a single layer, which couldn't scale, to overlapping layers and domains. Launch layers handle rollouts apart from ordinary tests.

- **Config as data:** Google's tests live in data files that are easy to read and pushed more often than code, so non-engineers can create them, with automatic checks first.

- **Tooling matters as much:** the same paper says the infrastructure isn't enough alone, and describes sizing tools, a metrics dashboard and education.

- **Namespaces:** PlanOut lets each team allocate a share of a namespace, centred on one kind of unit, to separate experiments over time.

- **Interactions are rare, though not never:** Microsoft, running hundreds of tests a day per product, found them very rare, which supports overlap as the default.

- **Scale across the industry:** 13 organisations at a 2018 summit together reported more than 100,000 experiment treatments in a year.

### The answer that sounds right

#### "The hard part is assigning users at scale"

It sounds right, since it's billions of calls. But a hash is cheap and can run locally. The hard parts are logging true exposure, joining it to events at a reasonable cost, and stopping people from misreading results. A platform that's fast but untrustworthy just helps you ship wrong answers sooner.

## Say it

### Your company runs a few A/B tests by hand. Design a platform that lets teams run hundreds at once, and trust the results.

#### The interviewer pushes further

Follow-up 1 of 3

Why hash locally rather than call an assignment service?

A service adds latency to every check, and becomes a single point of failure. A hash needs only the user ID and the config, gives the same answer everywhere and needs no stored table. The cost is that config must reach every client, so changes aren't instant.

Follow-up 2 of 3

Results show a win, but the sample ratio check failed. What should the platform do?

Flag it, and hide or grey out the result by default, because the groups may no longer be comparable. Then help people diagnose it, by showing the split by browser, version and day. Allow an override only with a recorded reason.

Follow-up 3 of 3

Two tests touch the same settings. How does the platform stop them clashing?

Each setting belongs to a layer, and a user is in at most one test per layer. Two tests on the same setting must then share a layer, so they split traffic and never overlap. The check runs when the test is created, so the conflict is rejected before launch.

#### The 30-second answer

I'd first clarify the scale, the platforms, the units, and who reads the results. Then I'd split it into four jobs. Assignment runs in an SDK, hashing user and salt locally, so there's no network call and no stored table, with a safe default if anything fails. Exposure logs record when a user actually reaches the change, in both groups, because counting everyone dilutes the effect. A daily pipeline joins exposures to events, using one central definition per metric, and stores per-user totals. A stats engine computes intervals, with CUPED and the delta method. For many tests at once, I'd use layers: tests in different layers overlap, and tests in the same layer are exclusive. The hard part is trust, so I'd run sample ratio checks on every test and hide results when they fail, let teams pick only a few decision metrics, and build in planned looks or always-valid intervals. With 300 tests and 50 metrics each, about 750 results a day would look significant by chance. So the platform has to make the right behaviour the default, rather than rely on people being careful.

**Key terms and sources**

Built from published accounts: [Google's overlapping experiments paper](https://research.google/pubs/overlapping-experiment-infrastructure-more-better-faster-experimentation/), which we read in part, the [PlanOut paper](https://hci.stanford.edu/publications/2014/planout/planout-www2014.pdf) and [Microsoft's interaction study](https://www.microsoft.com/en-us/research/articles/a-b-interactions-a-call-to-relax/). No single company's design is shown here, and the volumes and lab numbers are our own illustrations. Uses running many tests, trust checks and sequential testing. · checked 7 Nov 2026
