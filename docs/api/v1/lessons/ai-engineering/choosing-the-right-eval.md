# Choosing the Right Eval: Ship Checks, Regression Tests, Monitors and Guardrails

> Should this check run in CI, on live traffic, or before every answer reaches the user?

- Track: AI Engineering › Applied Evals › Lessons
- Type: Concept · 15 min
- Page: https://aimlrounds.com/tracks/ai-engineering/choosing-the-right-eval/
- Before this: Why LLM Apps Fail: The Three Gulfs (`ai-engineering/why-llm-apps-fail`)
- Quiz topic: `evals`
- Sources checked: 2026-11-15 · Text last changed: 2026-11-20 · Version: 91ffd0630f

## Intuition

### The situation

Your team built an LLM judge that checks answers for invented policy details. It agrees with experts 93% of the time. The product manager wants it on every answer before users see it; engineering wants it in CI only. The interviewer asks:

> Should this check run in CI, on live traffic, or before every answer reaches the user?

#### Why it matters

Teams often build one big "eval" and then don't know what to do with its number. Is 82% good? Should it block a release? Can it run on every request? Interviewers probe exactly this: where each check lives, and why. The answer depends on the check's job and on how fast and cheap it is.

### The idea

Think of quality checks in a bakery. A metal detector checks every loaf on the line in a split second. A taster samples a few loaves each hour. A new recipe gets a full panel before launch. Each check does a different job, and none could do the others'.

[Figure: Four places a check can live. Every answer, inline. CI, before release. A sample of live traffic. A human queue.]

_Latency and cost decide where a check lives._

### Play

**Try to break it.** Put the LLM judge inline with a 200 ms budget. Then raise traffic.

#### Where can this check run?

Kind of check

A regex fits any latency budget, so it can block a leaked card number before the user sees it. An LLM judge at about 2.5 seconds doesn't fit a 200 ms budget, and on all 10,000 daily answers it would cost about $200 a day. On a 2% sample it costs $4 and still tells you the failure rate. That's why judges usually run after the fact, and guardrails are mostly cheap code.

**Now say why:** why does sampling make the judge affordable without losing the failure rate?

## How it works

### How it works

#### In one breath

An eval is a check with a job. A **capability** eval starts with a low pass rate and shows progress. A **regression** eval should pass nearly 100% and guards what already works. A **monitor** runs on a sample of live traffic after the fact. A **guardrail** runs on every answer before the user sees it, so it must take milliseconds and rarely fire by mistake. Code checks fit everywhere; LLM judges take seconds and cost money, so they belong in CI and sampled monitoring; humans go where judgement and new failures need finding.

#### Jobs and kinds

##### The jobs

| Job | Question | Healthy pass rate | Runs |
|---|---|---|---|
| Capability | Can we do this at all yet? | low at first, a hill to climb | during development |
| Regression | Did this change break something that worked? | close to 100% | CI, on every prompt, model or tool change |
| Monitor | How often does this failure happen in production? | tracked over time, with error bars | async, on a 1–5% sample of traffic |
| Guardrail | Should this answer reach the user? | fires rarely, almost never by mistake | inline, on every answer |
| Migration | Is the new model at least as good on our cases? | compared side by side | before switching models |

Anthropic's agent-evals guide describes capability evals "graduating" into the regression suite once they pass reliably. An eval stuck at 100% still catches regressions but no longer tells you how to improve.

##### The kinds of check

- **Code:** schema validation, regex, running generated SQL, comparing to a reference. Fast, cheap, reproducible, but brittle on open-ended text.

- **LLM judge:** a model grades one failure mode with a pass/fail answer. Handles nuance, but takes seconds, costs money and needs checking against human labels.

- **Human:** the gold standard, and slow. Best for finding new failure types and labelling the data judges are checked against.

##### Two more distinctions

**Reference-based** checks compare with a known right answer, which suits CI's fixed test cases. **Reference-free** checks test a property ("cites a source", "no personal data"), which suits live traffic where no right answer exists. And **absolute** evals ask "good enough to ship?", while **comparative** ones ask "is B better than A?" with pairwise judging or an A/B test.

## In practice

### In practice

#### In practice

- **Give every eval a job:** capability, regression, monitor, guardrail or migration, and decide what its number will trigger.

- **Guardrails are mostly code:** they must be fast and rarely wrong, since a false alarm blocks a good answer.

- **Judges run async:** on CI's fixed set and on a small sample of live traffic.

- **Use humans to discover:** new failure types, and the labels that keep judges honest.

- **Graduate evals:** once a capability eval passes reliably, move it into the regression suite.

### The answer that sounds right

#### "Run the judge on every answer to be safe"

It sounds safer, but it adds seconds to every reply and costs far more, and a 2% sample gives the same failure rate. Keep inline checks fast and cheap, and run judges after the fact.

## Say it

### Should this check run in CI, on live traffic, or before every answer reaches the user?

#### The interviewer pushes further

Follow-up 1 of 3

Can an LLM judge be a guardrail?

Sometimes, for slow, high-stakes flows where a few seconds are acceptable, or with a small fast classifier. For chat, a 2–3 second judge on every answer is usually too slow, so guardrails are mostly code.

Follow-up 2 of 3

Your eval passes 100%. Is that good?

For a regression suite, yes. For a capability eval, it means the eval no longer tells you how to improve, so add harder cases.

Follow-up 3 of 3

When do you need a comparative eval rather than an absolute one?

When choosing between two versions, prompts or models. Pairwise judging or an A/B test answers "which is better" more reliably than two separate scores.

#### The 30-second answer

I'd give each eval a job. Capability evals start low and show progress. Regression evals should pass almost 100% and run in CI on every prompt, model or tool change. Monitors run judges on a small sample of live traffic, asynchronously. Guardrails run inline on every answer, so they must take milliseconds and rarely fire wrongly, which usually means code like regex and schema checks. LLM judges take seconds and cost money, so they belong in CI and sampled monitoring, and humans find new failures and label data for the judges.

**Key terms and sources**

The different jobs an eval can do (capability, regression, monitoring, guardrail, model migration), the kinds of check (code, LLM judge, human), and how latency and cost decide where each one can run. · checked 15 Nov 2026

#### Sources

- H. Husain and S. Shankar, _Evals for AI Engineers_ (O'Reilly): the Analyze-Measure-Improve lifecycle, error analysis, judges, CI and review

- [Anthropic, Demystifying evals for AI agents, Jan 2026](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)

- [H. Husain and S. Shankar, AI Evals: everything you need to know (FAQ)](https://hamel.dev/blog/posts/evals-faq/)

- [OpenAI, Evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices)

Explanations and examples are ours, built from these sources. Lab numbers are illustrative unless a lab says otherwise. Many recent papers are preprints, and benchmark scores change quickly.
