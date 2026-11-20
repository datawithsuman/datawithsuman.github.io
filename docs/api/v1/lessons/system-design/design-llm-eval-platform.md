# Design an LLM Evaluation Platform

> Teams change prompts, models and retrieval every week, and quality keeps slipping without anyone noticing. Design a platform that catches regressions before users do.

- Track: System Design › ML and LLM Platforms › Designs
- Type: Design · 25 min
- Page: https://aimlrounds.com/tracks/system-design/design-llm-eval-platform/
- Before this: RAG Evals: Retrieval, Faithfulness and Relevance (`ai-engineering/rag-evals`), LLMOps: What's Different (`ai-engineering/llmops`)
- Quiz topic: `sdllm`

## Intuition

### The situation

A company has an AI assistant and 20 teams changing its prompts, retrievers and models every week. Quality keeps slipping, and nobody notices until users complain. Results from last month's experiments can't be reproduced. The interviewer asks:

> Teams change prompts, models and retrieval every week, and quality keeps slipping without anyone noticing. Design a platform that catches regressions before users do.

#### Ask before designing

- **What's evaluated:** a RAG assistant, agents, single prompts? Different products need different metrics.

- **Who uses it:** say 20 teams, each changing prompts, retrievers or models several times a week.

- **What counts as good:** correct, grounded in sources, cited, well formatted, fast and cheap enough.

- **Speed:** how long can a check on a pull request take before engineers start skipping it?

- **Must never happen:** a change that breaks citations or safety reaching users, or a "better" score that can't be reproduced.

- **Success metrics:** regressions caught before release, time to get a result, judge agreement with people, and incidents found in production.

### The idea

Think of a school's exams. Questions are written in advance and kept on file, markers follow a marking scheme, and a senior teacher re-marks a sample to check the markers are fair. A quick test each week catches big problems; the full exam at the end of term catches the rest.

[Figure: Versioned datasets, scorers and judges run as gates: a small set on every change, a big set before release, and sampled live traffic after.]

_Evaluation works like testing code: versioned, repeatable and gated._

### Play

**Try to break it.** Keep 150 questions and set a 5-point drop. Then drag the questions up. Then raise the drop to 10.

#### Will your gate catch the regression?

Illustrative: an 85% baseline pass rate compared against a fixed baseline with a one-sided test at 5%, and about 6 seconds per answer plus judging. Real gates are noisier still, because judges and models vary run to run.

Start at 150 questions and a 5-point drop: the gate misses it about half the time. Drag the questions up and watch the time grow. That's why gates are **layered**: a small, fast set catches big breaks on every change, and a large set before release catches the smaller ones.

**Now say why:** why does a small gate set catch big regressions but miss small ones?

## Architecture

### Architecture

#### In one breath

Treat evaluation like testing code. Keep **versioned datasets** built from real use, score answers with **clear metrics** and **LLM judges you calibrate against people**, and run them as **gates**: a fast set on every change, a bigger one before release, and **sampling of live traffic** after. Hard rules block a change; softer scores are tracked. Every run records exactly what was tested, so results can be reproduced.

#### Datasets, scorers, runs and gates

1. **Datasets:** public benchmarks for a baseline, real (anonymised) user queries, synthetic questions generated over representative documents, and hard cases mined from poorly rated live answers. All versioned.

2. **Scorers:** code checks (are citations present?), metrics against references (source recall, answer correctness) and LLM judges with a rubric for things like faithfulness and tone.

3. **Runs:** each run is a dataset, a system version, settings and scorers, saved with an ID so it can be compared and reproduced.

4. **Gates:** a small, fast set on every pull request; a larger set with stricter limits before release; and continuous scoring of sampled live traffic after.

5. **Dashboards and alerts:** side-by-side comparisons, trace-level drill-down and alerts on drift.

##### Three kinds of checks

**Hard rules** block a change, like "every answer must cite a source". **Budgets** set limits, like "source F1 at least 0.85, p95 latency at most 5 seconds". **Rubric scores**, like tone, are tracked and reviewed but don't block, because they're noisier.

##### Why not BLEU or embedding similarity?

Overlap and similarity scores miss what matters here: whether claims are supported, citations are right and the format is usable. Two answers can look alike and differ in exactly those ways.

#### The numbers worth saying out loud

All of these are assumptions for the interview, not figures from a real system.

| Question | Working | Result |
|---|---|---|
| Pull-request runs a week | 20 teams × 15 changes | **300** |
| Judge calls a week for PR gates | 300 × 150 questions × 3 judges | **135,000** |
| Live answers sampled a day | 1 million answers × 1% | **10,000** |
| Human labels for calibration a month | 10 judges × 200 samples | **2,000** |

Judge calls are the main cost, so use a cheaper judge for routine gates, cache results for unchanged answers, and keep the expensive judge for release gates.

## In practice

### In practice

#### What every evaluation design gets asked

- **Can you trust the judge?** Build each judge like code: a rubric, a prompt, a version and tests. Every few weeks, have people label a sample and measure agreement. If the judge drifts, fix its prompt or model, and re-score.

- **Reproducibility:** record the dataset version, prompt hash, retriever version and model for every run. Without that, "it got better" can't be checked.

- **Prompt edits are risky:** a single word can break citations or formatting, so every prompt change goes through the gate, just like a model swap.

- **Hard cases:** mine poorly rated live answers and add them to the suite, so known failures can't come back silently.

- **Production:** score sampled live traffic asynchronously, so users see no extra latency, and alert on sudden drops in metrics like source F1.

- **Other languages and domains:** a general judge can be wrong here; use specialised judges or more human review.

##### Triage when a score drops

Was the right document never retrieved? Check retrieval logs. Was the context there but ignored? Check prompt structure and truncation. Does the judge look wrong? Re-run it on its calibration set.

#### What the real system reported

- **Datasets:** public QA sets for a baseline, then anonymised internal queries, synthetic Q&A over widely shared documents, and hard cases mined from low-rated live traces.

- **Pull-request gate:** about 150 canonical queries, chosen to cover connectors, "no answer" cases and non-English queries, with results in under ten minutes. Merges are blocked on any red-line miss.

- **Three metric types:** boolean gates such as citations present; budgets such as source F1 ≥ 0.85 and p95 latency ≤ 5 s; rubric scores that are logged, not gating.

- **Judges:** designed, calibrated, tested and versioned like software, with spot-checks against human labels every few weeks. People also review 5–10% of the regression suite each release.

- **Production:** live traffic sampled and scored with the same metrics, with no added latency, and alerts on drift.

- **Lesson:** prompt edits caused more regressions than model swaps, and formal gates, not people eyeballing results, became the reliable safety net.

The company's own figures. The post gives no judge-agreement rates or costs.

### The answer that sounds right

#### "If the judge score went up, quality went up"

It sounds right, since the judge is the measure. But judges drift, have biases such as preferring longer answers, and can be gamed by prompt changes that please the judge rather than users. Re-check judges against people regularly, keep a held-out set, and compare offline gains with what users actually experience.

## Say it

### Teams change prompts, models and retrieval every week, and quality keeps slipping without anyone noticing. Design a platform that catches regressions before users do.

#### The interviewer pushes further

Follow-up 1 of 3

Your judge says quality went up, but users complain. What do you check?

Whether the judge still agrees with people: re-run its calibration set and label a fresh sample of recent answers. Then check whether the eval set still looks like real traffic, since usage drifts. I'd add the complaints as test cases.

Follow-up 2 of 3

Why not run the full suite on every pull request?

It would take too long and cost too much, so engineers would work around it. A small set catches big breaks quickly. The full suite runs before release, where a slower check is acceptable and small regressions matter.

Follow-up 3 of 3

How do you stop teams from overfitting to the eval set?

Keep a held-out set that teams can't see, refresh datasets from live traffic regularly, and compare offline gains with online results. If offline keeps improving while users don't notice, the set has stopped measuring what matters.

#### The 30-second answer

First I'd clarify what we evaluate, who changes the system and how fast a check must be. I'd treat evaluation like testing code. Datasets are versioned and come from real anonymised queries, synthetic questions over representative documents, public benchmarks for a baseline, and hard cases mined from bad live answers. Scorers include code checks like "citations present", metrics such as source recall, and LLM judges with rubrics. Each judge is versioned and calibrated against human labels every few weeks. Every run records the dataset, prompt hash, retriever and model, so it can be reproduced. Gates are layered: a small set on every pull request that returns in minutes, a larger stricter set before release, and asynchronous scoring of sampled live traffic with drift alerts. Hard rules block changes, budgets set limits on things like latency, and rubric scores are tracked. A small gate set only catches big regressions, which is why the release gate is larger. Poorly rated live answers flow back into the suite.

**Key terms and sources**

Based on a file-storage company's published approach for its AI assistant: [Dropbox's "A practical blueprint for evaluating conversational AI at scale"](https://dropbox.tech/machine-learning/practical-blueprint-evaluating-conversational-ai-at-scale-dash) (October 2025). The lab's maths and the estimate are ours. Uses evaluating LLM apps, LLMOps and tracing. · checked 5 Nov 2026
