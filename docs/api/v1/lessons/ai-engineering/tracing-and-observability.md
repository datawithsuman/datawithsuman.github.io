# Tracing and Observability for LLM Apps and Agents

> Users say your assistant 'got worse this week', but every dashboard is green. What should you have been recording, and how do you find the problem?

- Track: AI Engineering › LLMOps › Lessons
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/ai-engineering/tracing-and-observability/
- Before this: LLMOps: What's Different (`ai-engineering/llmops`)
- Quiz topic: `llmops`

## Intuition

### The situation

Users say the assistant 'got worse this week'. Uptime, latency and error rates all look normal, and nobody can tell what changed or which step is at fault. The interviewer asks:

> Users say your assistant 'got worse this week', but every dashboard is green. What should you have been recording, and how do you find the problem?

#### Why it matters

An agent run may involve retrieval, several model calls and tool calls. When an answer is wrong, you need to see which step went wrong, with what inputs. Quality changes don't show up in uptime or latency. A 2025 study of 86 deployed agents found 74% relied mainly on human evaluation, and 52% used LLM judges. In its 20 interviews, 75% of teams had no formal benchmark set, and relied on A/B tests and user feedback instead. Good traces are what make both possible.

### The idea

Think of a flight recorder. When something goes wrong, you don't guess. You replay what every instrument showed and what each pilot did, step by step. A trace is the flight recorder for each request.

[Figure: Three layers. Trace every step. Score a sample of live traffic. Turn bad traces into tests.]

_Green dashboards can hide bad answers._

### Play

**Try to break it.** Score 1% of a small product's traffic. Then raise the rate.

#### How much live traffic to score?

Illustrative: a judge call costs $0.002, and the target is noticing a rise from 5% to 6% bad answers with 80% power. The judge must be checked against human labels first.

At 50,000 conversations a day, scoring 1% gives 500 judged conversations a day, and it takes about 15 days to notice bad answers rising from 5% to 6%. Scoring 5% cuts that to about 3 days, for $5 a day, and 20% to about 0.7 days for $20. For a small product, even 20% may take weeks, so lean on user signals and a human review of flagged traces. Score every conversation after a release, when changes are most likely.

**Now say why:** why does a small change take so long to notice?

## How it works

### How it works

#### In one breath

Ordinary monitoring checks that a service answers. An LLM app can answer fast, every time, and still answer badly. So record a **trace** for every request: the configuration, the retrieved documents, each model and tool call, tokens, latency and cost, linked together. Score a **sample** of live traffic with code checks and an LLM judge, and watch user signals like thumbs-down and escalations. Keep personal data out of logs, or redact it. And make failures loud: in one production agent, about 70% of silent failures were caught by a person reading the output, not by any test or alert.

#### What to record

##### Traces and spans

A trace is one request from start to finish. Each step inside it is a span: retrieval, a model call, a tool call, a guardrail check. Spans record their inputs, outputs, timing and errors, and link to their parent. OpenTelemetry defines common names for LLM spans and attributes, such as the model and token counts, now kept in a separate GenAI conventions repository.

| Record | Why |
|---|---|
| Configuration version: prompt, model ID, parameters, index snapshot | To link any change in behaviour to a release |
| Retrieved document IDs and scores | To tell retrieval failures from generation failures |
| Each model call: tokens in, out and cached, latency, finish reason | Cost and latency by step, cut-off answers, cache misses |
| Tool calls, arguments, results and errors | Wrong tool, wrong arguments, failures hidden by the model |
| Guardrail and judge results | What was blocked, and quality scores over time |
| User signals: thumbs, edits, escalations, retries | Real outcomes |

##### Privacy

Prompts and outputs often contain personal data. Redact it before logging, limit who can read raw traces, set retention periods, and keep full content only where you need it.

##### Silent failures

A 2026 study of a production agent with 4,286 unit tests and 827 automated checks documented 22 incidents over eight weeks where everything stayed green. About 70% were found by a person reading the output. In one, an error page was cached, and the model turned it into a confident report about a crisis that didn't exist. Errors that reach a model's context can become fluent, false output, so keep error text out of model inputs, and preserve the original cause when errors pass between layers.

##### From traces to evaluation

Every bad trace a user or reviewer flags becomes a golden set case. Over time, the golden set reflects real traffic, and the release gate catches regressions on cases that once failed.

#### The maths

$$ n \approx \frac{2\,(z_{\alpha/2}+z_{\beta})^2\,p(1-p)}{\delta^2} $$

The usual sample-size formula for comparing two rates, with 5% significance and 80% power. It sets how much live traffic you need to score, or how long you wait.

- **sampled conversations needed**: Per period, before and after a change, to notice it.

- **baseline failure rate**: How often the judge marks an answer bad today.

- **the change to detect**: A smaller change needs many more samples.

## In practice

### In practice

#### In practice

- **Trace everything, keep content selectively:** metadata for every request, full content for a sample, errors and flagged cases.

- **Cost and latency by step:** find which model or tool call dominates, and watch cache hit rates.

- **Alert on outcomes:** escalations, thumbs-down, judge scores and cost per task, especially after releases.

- **Review traces by hand:** schedule time to read real conversations. It catches what metrics miss.

- **Keep judges honest:** check them against human labels, and re-check after model changes. See LLM-as-a-Judge.

### The answer that sounds right

#### "Our dashboards are green, so the assistant is fine"

It sounds reasonable, since nothing is failing. But an LLM can answer quickly and wrongly, and errors can even become confident answers. Trace each request, score a sample of answers, and read real conversations.

## Say it

### Users say your assistant 'got worse this week', but every dashboard is green. What should you have been recording, and how do you find the problem?

#### The interviewer pushes further

Follow-up 1 of 3

Latency and error rates are normal, but complaints are up. Where do you look?

Compare traces before and after: configuration version, retrieved documents, tool errors and answer length. Sample complaints and read them, then check judge scores by intent.

Follow-up 2 of 3

Should you log full prompts and answers?

Log metadata for everything, and full content for a sample, errors and flagged cases, after redacting personal data, with strict access and retention.

Follow-up 3 of 3

Your judge says quality is flat after a model upgrade. Trust it?

Not without checking. The judge may share the new model's blind spots, or have drifted itself. Compare it with human labels on a fresh sample.

Dashboards that check uptime miss quality, so I'd trace every request: configuration version, retrieved documents, each model and tool call with tokens, latency and cost, and user signals, all linked. I'd redact personal data and keep full content for a sample and for errors. I'd score a sample of live traffic with checked LLM judges, sized so a real drop shows up in days, and score more right after releases. I'd keep error text out of model inputs, since a study found errors turned into confident false answers, and most silent failures were caught by a person reading output. Every flagged trace becomes a golden set case.

**Key terms and sources**

What to record for each LLM request and agent run, traces and spans, cost and latency by step, privacy and retention, sampling live traffic for quality scoring, silent failures, and turning traces into evaluation cases.

#### Sources

- Pan et al., Measuring Agents in Production, ICML 2026

- Wu, When Errors Become Narratives: silent failures in a production LLM agent runtime

- OpenTelemetry, GenAI semantic conventions

- Shankar et al., Who Validates the Validators?

Explanations are ours, built from these sources. Lab numbers are illustrative unless a lab says otherwise. Many recent papers are preprints, and provider policies change.
