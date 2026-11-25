# MLOps Practice

> 10 production questions: skew, drift alerts, canaries, audits, retraining, label-free estimation, feedback loops, LLMOps.

- Track: AI Engineering › MLOps › Scenarios
- Type: Interview · 35 min
- Page: https://aimlrounds.com/tracks/ai-engineering/mlops-practice/
- Before this: Retraining Pipelines and Continuous Training (`ai-engineering/retraining-pipelines`)
- Quiz topic: `mlops`
- Sources checked: 2026-10-29 · Text last changed: 2026-11-19 · Version: 0419e65db8

How to use this page

Give yourself about 5 minutes per question, as in an interview. These are the production questions interviewers ask. Give your diagnosis out loud (most likely cause, how you'd confirm it, the fix and how you'd prevent it), then open the answer and compare.

**The checklist:** is it the data (skew, drift, pipeline bug), the labels (delay, definition), the model (staleness, a bad retrain) or the release (a config or version change)? Confirm with logs and slices; fix; then add a monitor, a test or a gate so it can't happen silently again.

Question 1 · Easy · skew

### A new fraud model improved offline AUC from 0.86 to 0.91, but after launch it catches fewer frauds than the old one. What's your first hypothesis and how do you check it?

Answer: **training/serving skew or leakage: offline features differ from what the model sees live**

1. Compare logged serving features with the training values for the same transactions: missing or stale features online, different encodings or units.

2. Check for leakage: training features built with information after the transaction time (e.g. counts that include later chargebacks).

3. Fix with point-in-time training data, shared feature definitions, and training on logged serving features.

**Follow-up:** How would you have caught it before launch? Shadow mode comparing live feature distributions and predictions with offline ones.

Question 2 · Easy · serving mode

### Product wants 'personalised restaurant recommendations on the home screen' for 30 million users, updated in real time. How do you serve it?

Answer: **hybrid: batch-generate candidates per user, re-rank online with session context**

1. Most of the work (candidate generation from long-term preferences) changes slowly: batch it daily or hourly for active users.

2. Re-rank the candidates online at request time using time, location and current session.

3. Stream only the features where freshness matters (recent clicks); fall back to batch results if online ranking fails.

**Follow-up:** Why not compute everything online? Cost and latency at 30 million users for little gain on slow-changing parts.

Question 3 · Medium · drift

### Your drift dashboard shows 40 of 120 features with KS p < 0.01 every day. The team ignores it. What do you change?

Answer: **replace p-value alerts with effect-size thresholds on important features, by slice, tied to performance**

1. With large samples, KS flags trivial differences; daily alerts become noise.

2. Monitor effect sizes (PSI or distance metrics) on the features that matter most for the model, with thresholds calibrated on history.

3. Alert on prediction drift and performance (once labels arrive) by slice; give each alert an owner and a runbook.

**Follow-up:** How do you pick 'important' features? Feature importance or ablations, plus business-critical inputs.

Question 4 · Medium · canary

### Your canary ran for 2 hours at 2% traffic and showed no difference, so the team wants to go to 100%. 2% is about 400 requests/hour. Is that enough to catch a meaningful regression?

Answer: **probably not: ~800 requests only detect large regressions; size the test from the smallest regression that matters**

1. Compute the sample size for the regression you care about: smaller effects need many more requests (n grows with 1/δ²).

2. 800 requests may detect a big jump but not a subtle one, and 2 hours misses daily cycles.

3. Extend duration or traffic share, cover peak periods, keep guardrails with automatic rollback, and ramp gradually.

**Follow-up:** What would you check besides the main metric? Latency, errors, slices (new users, cities), and business guardrails.

Question 5 · Medium · reproducibility

### An auditor asks which data trained the credit-risk model that rejected a customer 8 months ago. You have the code in git and the model file. Can you answer?

Answer: **only if the run recorded an immutable data snapshot and lineage; code and weights aren't enough**

1. The training tables have changed since; without a snapshot ID or time range you can't reconstruct the data.

2. Lineage links: data snapshot → feature definitions → training run → model version → deployment window.

3. Going forward: immutable training snapshots, automated run tracking, a registry with lineage and model cards.

**Follow-up:** What else would the auditor want? The model card, evaluation by group, and the features used for that specific prediction (from logs).

Question 6 · Hard · retraining

### Automated weekly retraining shipped a model that's 15% worse in one city. The pipeline had no human in the loop. What went wrong and what gates would you add?

Answer: **no data validation or per-slice comparison against production before promotion**

1. Likely cause: a data issue in that city (pipeline bug, label delay, an event) that the new model learned from.

2. Add data validation (schema, ranges, volumes per slice, label completeness) that stops the pipeline on anomalies.

3. Require the candidate to match or beat production overall and on key slices on the same recent test set; then shadow/canary with automatic rollback.

4. Keep the previous model deployable and alert on per-slice performance.

**Follow-up:** When should a human approve? Large changes in behaviour, high-risk domains, or when gates are borderline.

Question 7 · Hard · LLMOps

### Nobody changed the prompt or code, but your LLM support bot's escalation rate jumped from 8% to 14% overnight. What happened, and how do you prevent surprises like this?

Answer: **an upstream change: the provider's model alias moved to a new version, or the retrieval index/data changed**

1. Check traces: model version per request, retrieval index version, tool behaviour, input mix; compare before vs after.

2. Hosted model aliases (e.g. 'latest') can change behaviour; re-indexing can change retrieved documents.

3. Pin model versions and index snapshots, log the full configuration per request, run the golden-set gate before any upstream change, and alert on post-change shifts in escalations and judge scores.

**Follow-up:** How would you roll back? Switch back to the previous pinned model version or index snapshot via configuration.

Question 8 · Medium · label-free estimation

### Your classifier made 1,000 predictions today, with no labels yet. 700 have 0.95 confidence in the predicted class, and 300 have 0.70. What's the estimated accuracy, and what has to be true for it to hold?

Answer: **About 87.5%, if the probabilities are still calibrated**

1. Expected correct: 700 × 0.95 + 300 × 0.70 = 665 + 210 = 875.

2. 875 ÷ 1,000 = 87.5%.

3. It holds only if confidence still matches accuracy: a change in the input mix is fine, but concept drift breaks it.

How would you check? Label a small random sample each week, and compare it with the estimate.

Question 9 · Medium · feedback loop

### A loan model approves 30% of applicants. It's retrained every quarter on repayment data, and each version shows lower default rates. Approvals keep falling. What's going on?

Answer: **A feedback loop: you only learn about applicants the model approved**

1. Repayment is observed only for approved loans, so rejected groups never get labels.

2. Each model learns from a narrower group, and grows more cautious about everyone else.

3. Fix: approve a small, controlled share near the threshold, log the approval probability, and evaluate with those weights or a holdout.

What's the business cost of not fixing it? Good applicants are turned away, and the model can't notice.

Question 10 · Hard · propensity weighting

### Your logs show three recommendations: clicked with logged probability 0.5, not clicked with 0.1, and clicked with 0.05. A new policy would show the first two items for sure, and never the third. Estimate the new policy's click rate with inverse propensity scoring.

Answer: **About 0.67 clicks per user**

1. Weight each outcome by new chance ÷ logged chance: 1 × (1 ÷ 0.5) = 2, 0 × (1 ÷ 0.1) = 0, and 1 × (0 ÷ 0.05) = 0.

2. Average over the 3 logs: 2 ÷ 3 ≈ 0.67.

3. With 3 logs, it's very noisy, and it only works because every logged probability is above zero.

Why log probabilities at serving time? You can't reconstruct them later, and without exploration many would be zero.

**More practice and sources**

10 interview questions, easy to hard · answers hidden until you click · checked 29 Oct 2026

Keep practising

Uses the lessons in this track: Skew and Feature Stores, Batch vs Online, Deployment Patterns, Tracking and Registry, Drift and Monitoring, Retraining, LLMOps. New questions are added over time.

New lessons: Monitoring Without Labels and Feedback Loops and Unbiased Training Data.
