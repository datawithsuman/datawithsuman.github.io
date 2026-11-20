# Online Evals: Sampled Judges, Guardrails and User Signals

> Your assistant handles 100,000 conversations a day. How do you know today's quality without reading them?

- Track: AI Engineering › Applied Evals › Lessons
- Type: Concept · 17 min
- Page: https://aimlrounds.com/tracks/ai-engineering/online-evals-and-guardrails/
- Before this: Evals in CI: Golden Sets, Regression Gates and Model Upgrades (`ai-engineering/evals-in-ci`)
- Quiz topic: `evals`

## Intuition

### The situation

Your support assistant handles 100,000 chats a day. The team runs a hallucination judge on every chat before sending it, which adds three seconds and costs thousands a month, and quality still dipped last week without an alert. The interviewer asks:

> Your assistant handles 100,000 conversations a day. How do you know today's quality without reading them?

#### Why it matters

Production brings inputs nobody tested, and models change underneath you. Monitoring catches what CI can't: drift in what users ask, new failure modes, and slow declines. Without it, users are your alerting system.

### The idea

Think of a water company. It doesn't drink every glass in the city; it samples taps across neighbourhoods every day and tests them in a lab. The filter at the plant handles a few known dangers instantly.

[Figure: Three signals. Sampled judges. Inline guardrails. User behaviour.]

_A small sample measures quality; the budget goes to slicing._

### Play

**Try to break it.** Sample 0.1%, then 10%. Watch cost and the error bar.

#### What does monitoring cost, and what does it tell you?

At 100,000 conversations a day, a 2% sample gives 2,000 judged traces, enough to measure a 5% failure rate to about ±1 point every day, for about $200 with five judges. Judging everything would cost 50 times more for little extra precision. Spend the savings on slicing: the same sample split by feature or customer shows where failures concentrate.

**Now say why:** why does a bigger sample buy so little precision?

## How it works

### How it works

#### In one breath

Run 5–7 evaluators (code and LLM judges, one per known failure mode) on a small sample, often 1–5% of traffic, after each request completes. Correct each judge's rate and alert when its confidence interval crosses a threshold. Put only fast, reliable checks inline as **guardrails** (regex, schema, parsers), with a safe fallback. Track user signals too: retries, rephrasing, abandonment, accepted suggestions. Use A/B tests for big changes. Every new failure found goes back into error analysis and the golden set.

#### Four kinds of signal

##### Sampled evaluators

Log full traces, sample a small share daily, and run your evaluators on them asynchronously. For each failure mode, report the corrected rate with a confidence interval (see validating a judge) and alert when the interval crosses your threshold. Sample per slice (feature, customer, language) if failures concentrate there.

##### Guardrails

A guardrail is a function called on every output before it's sent: if it fires, log it and return a safe fallback ("I drafted this, but it contained sensitive details, so please review the source"). It must be fast and rarely wrong, so most guardrails are code: card-number and ID patterns, schema validation, allow-lists, parsers that confirm SQL or code is valid. A 2–3 second LLM call on every answer is usually too slow. Every guardrail trip is also a free label for monitoring.

##### User signals

Implicit signals scale better than thumbs: the user retries or rephrases, abandons the session, escalates to a human, accepts or deletes a suggestion. GitHub's study of Copilot found that the rate of accepted suggestions predicted how productive developers felt better than other usage measures. Signals are noisy proxies, so use them to choose traces to read and to spot trends, alongside evaluators.

##### A/B tests

For a new model or a big prompt change, split traffic and compare task success, user signals, cost and latency; LLM outputs vary a lot, so plan sample sizes. See the sample size lessons.

##### The flywheel

Monitoring spots a rise in one failure, error analysis on flagged traces finds a new mode, the team adds 5–10 examples to the golden set, builds a check, fixes the app, verifies in CI and redeploys. Each lap makes both the app and the evals stronger.

## In practice

### In practice

#### In practice

- **Log everything, judge a sample:** 1–5% async, per failure mode.

- **Correct rates, alert on intervals:** not on raw judge counts.

- **Guardrails are fast code:** with a safe fallback and a log of every trip.

- **Watch implicit signals:** retries, rephrasing, abandonment, acceptance.

- **A/B test big changes:** with planned sample sizes.

- **Feed the golden set:** every new failure becomes a CI case.

### The answer that sounds right

#### "Run the hallucination judge on every chat before sending"

It sounds thorough, but it adds seconds to every reply and costs a fortune, while a small async sample measures the same rate. Keep inline checks to fast code, and judge after the fact.

## Say it

### Your assistant handles 100,000 conversations a day. How do you know today's quality without reading them?

#### The interviewer pushes further

Follow-up 1 of 3

Why not run the LLM judge on 100% of traffic?

It costs far more and adds little: a modest sample already gives a tight error bar. Spend the budget on slicing by feature or customer instead.

Follow-up 2 of 3

A guardrail blocks 3% of answers. Is that good?

Read a sample of the blocked ones. If many were fine, the false-positive rate is too high and users are being refused for nothing.

Follow-up 3 of 3

Thumbs-down rate is flat but retries are rising. What do you do?

Treat retries as the earlier signal: read retried conversations, look for a new failure mode, and check whether something changed, such as a model or retrieval update.

#### The 30-second answer

I'd log full traces and run five to seven evaluators, one per known failure mode, on a 1 to 5% sample asynchronously, correcting each judge's rate and alerting when its confidence interval crosses a threshold. Inline, only fast and reliable checks act as guardrails, like regex for personal data, schema validation and SQL parsing, with a safe fallback, because a judge on every answer adds seconds. I'd watch implicit signals like retries, rephrasing, abandonment and accepted suggestions, A/B test big changes, and feed every new failure back into error analysis and the golden set.

**Key terms and sources**

Running evaluators on a sample of live traffic with corrected rates and alerts, guardrails that block bad outputs inline, the user signals that work as quality proxies, A/B tests for big changes, and the loop that feeds production failures back into CI. · checked 15 Nov 2026

#### Sources

- H. Husain and S. Shankar, _Evals for AI Engineers_ (O'Reilly): the Analyze-Measure-Improve lifecycle, error analysis, judges, CI and review

- [H. Husain and S. Shankar, AI Evals: everything you need to know (FAQ)](https://hamel.dev/blog/posts/evals-faq/)

- [A. Ziegler et al., Productivity assessment of neural code completion (GitHub Copilot), 2022](https://arxiv.org/abs/2205.06537)

- [Anthropic, Demystifying evals for AI agents, Jan 2026](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)

Explanations and examples are ours, built from these sources. Lab numbers are illustrative unless a lab says otherwise. Many recent papers are preprints, and benchmark scores change quickly.
