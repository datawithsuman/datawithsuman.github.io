# LLMOps: What's Different

> How do you ship prompt changes without breaking things?

- Track: AI Engineering › LLMOps › Lessons
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/ai-engineering/llmops/
- Before this: Deployment Patterns: Shadow, Canary, A/B and Rollback (`ai-engineering/deployment-patterns`), RAG Evals: Retrieval, Faithfulness and Relevance (`ai-engineering/rag-evals`)
- Quiz topic: `llmops`
- Sources checked: 2026-11-07 · Text last changed: 2026-11-20 · Version: 4dc34251cc

## Intuition

### The situation

The company runs an LLM support assistant, and three prompt changes are proposed this week. Each fixes the complaint that prompted it. A colleague says it works on that complaint, so ship it. The interviewer asks:

> How do you ship prompt changes without breaking things?

**Running example:** alongside the ETA model, the company runs the LLM support assistant. Three prompt changes are proposed this week; which ones should ship?

#### Small text edits, big behaviour changes

A one-line prompt edit can fix one complaint and quietly break ten other cases; a new model version can change tone, format or refusals; a re-indexed knowledge base can change answers. There's no single accuracy number and outputs are open-ended, so classic "train, evaluate, deploy" doesn't map directly.

### The idea

Think of a restaurant chain changing a recipe because one customer complained. It may fix that plate and quietly ruin ten others, or double the cost of ingredients. So every change goes through the same tasting panel and the same checklist before any branch gets it.

[Figure: Three prompts through the release gate. Prompt A raises policy accuracy from 91 to 92.5 percent and passes. Prompt B reaches 93 percent but faithfulness falls from 94 to 89 percent, so it is blocked. Prompt C is flat on quality but costs 48 percent more, so it is blocked.]

_Illustrative golden-set results from the lab. Passing changes still go through a canary._

### Play

**Try to break it.** Run prompts A, B and C through the gate. Read the decision and the reason for each.

#### "The new prompt fixed the complaint, ship it"

Illustrative golden-set results. Gate rules: no quality metric may drop more than 2 points; cost and latency may rise at most 10%. Passing configs still go through a canary.

**Prompt A** improves policy accuracy (91.0% → 92.5%) without breaking anything: it passes and goes to canary. **Prompt B** was written to fix one complaint and does raise accuracy to 93.0%, but faithfulness falls from 94.0% to **89.0%**: "more complete" made the model add unsupported claims. Blocked. **Prompt C** is flat on quality but adds 8 examples to every request, raising cost per conversation by **48%**. Blocked, or reconsidered with fewer examples. Judged on the one failing conversation that prompted it, each change looks good; judged on the whole golden set, only A ships.

**Now say why:** prompt B raised accuracy the most, so why was it blocked?

## How it works

### How it works

#### In one breath

In classic MLOps you retrain and redeploy a model; in LLM apps the **model is usually someone else's** and rarely changes, while the things you change weekly are **prompts, retrieval indexes, tools and model versions**. So the unit of release is a **configuration** (prompt + model ID + parameters + index snapshot + tools), and each needs versioning and a **release gate**: run the golden set through code checks and validated LLM judges, compare every metric with production (accuracy, faithfulness, format, safety, cost, latency), and ship only if nothing regresses beyond its limit, then canary it. In production, **trace** every request (prompt version, retrieved documents, tool calls, tokens, cost), monitor sampled quality scores and user signals, and watch for **silent upstream changes**: hosted model versions change behaviour (Chen et al. measured large shifts between versions of the same API model). What you'll be able to do after this: explain how LLMOps differs from MLOps, design a release gate for prompt changes, and say what to trace and monitor.

#### MLOps vs LLMOps

| | Classic MLOps | LLMOps |
|---|---|---|
| **What changes most** | model weights (retraining) | prompts, retrieval data, tools, provider model versions |
| **What to version** | data, features, model | the whole configuration: prompt, model ID, parameters, index snapshot, tool schemas |
| **Evaluation** | one or a few metrics on a test set | golden sets scored by code checks + validated LLM judges + human review; many metrics |
| **Monitoring** | input drift, performance with labels | sampled quality scores, user feedback, escalations, safety, cost per request, latency |
| **Cost driver** | training compute | tokens per request × traffic |
| **Shared** | staged rollout, rollback, reproducibility, tracing, owners and runbooks | |

## In practice

### In practice

#### LLMOps practices

- **Version configurations** in the repository (prompt text, model ID pinned to a dated version, parameters, index snapshot ID, tool schemas); every response logs the configuration that produced it.

- **Release gates in CI** on every config change; grow the golden set with production failures; validate LLM judges against human labels (Shankar et al.).

- **Trace** each request end to end: prompt version, retrieved document IDs, tool calls and results, tokens, latency, cost (standard GenAI tracing conventions exist).

- **Online monitoring:** judge-score a sample of live traffic, track thumbs-down, escalations, safety flags, cost per resolved conversation; alert on shifts after deploys.

- **Upstream changes:** pin model versions; re-run the gate before adopting a new one; hosted models can change behaviour between versions (Chen, Zaharia & Zou 2023).

- **Same rollout discipline** as models: shadow or canary, instant rollback to the previous configuration.

Averages hide regressions: in a 2026 study, one model upgrade gained 7.3 points on maths while 6% of items got reliably worse, and a single run per item couldn't detect any of the changes. So compare old and new configurations case by case, with several runs. Practice also leans on people: in a 2025 study of 86 deployed agents, 74% relied mainly on human evaluation and 52% used LLM judges. See Tracing and Observability, Model Upgrades and Retirements and LLM API Reliability.

#### Treat the whole configuration as the model

In LLM apps the prompt, model version, retrieval index and tools together define behaviour, so version them together, gate every change on a golden set across quality, safety and cost, trace every request, and roll out like any model.

### The answer that sounds right

#### "The provider's model doesn't change"

It sounds right, if you're calling the same model name. But hosted models can change behaviour between versions, so pin a dated version, and re-run the gate before adopting a new one. Testing a new prompt only on the complaint that prompted it fails the same way: judged on that one conversation, all three prompts look good, and only A survives the full golden set.

## Say it

### How do you ship prompt changes without breaking things?

#### The interviewer pushes further

Follow-up 1 of 3

How is monitoring an LLM app different from monitoring a classifier?

No single label or metric: you combine sampled judge scores, user signals, escalation and safety rates, and cost, and you watch for changes after config or provider updates.

Follow-up 2 of 3

Your provider deprecates the model version you use. What's your process?

Run the golden set on the new version, compare all gate metrics, adjust prompts if needed, shadow or canary, and switch with rollback ready.

Follow-up 3 of 3

What would you put in a trace?

Config version, inputs (redacted), retrieved document IDs, tool calls and results, outputs, tokens, latency, cost and any judge scores, linked by request ID.

#### The 30-second answer

In LLM apps the model weights rarely change; what changes is the prompt, the provider's model version, the retrieval index and tools. So I version the whole configuration and log it with every response. Every change goes through a release gate: run the golden set with code checks and validated LLM judges, compare accuracy, faithfulness, format, safety, cost and latency with production, and block anything that regresses beyond its limit, then canary it with rollback. In production I trace each request, sample live traffic for quality scoring, track user feedback, escalations and cost per conversation, and pin model versions because upstream changes can shift behaviour.

**Go further**

#### What not to say

- "We tested the new prompt on the complaint and it works." Run the full golden set.

- "The provider's model doesn't change." Pin and re-test versions.

**Key terms and sources**

How operating LLM applications differs from classic MLOps: the model is usually fixed and the prompt, retrieval index and tools change instead; versioning prompts and configs; evaluation gates on golden sets instead of single accuracy numbers; tracing every request; monitoring output quality, safety and token cost; and staged rollout of prompt changes · built from Shankar et al. (Who Validates the Validators?, UIST 2024), Zheng et al. (LLM-as-a-Judge, NeurIPS 2023), Liang et al. (HELM, 2022), Chen, Zaharia & Zou (How Is ChatGPT's Behavior Changing over Time?, 2023), Sculley et al. (NeurIPS 2015) and the OpenTelemetry GenAI semantic conventions · checked 7 Nov 2026 (this page is updated as practice evolves)

#### Sources

1. S. Shankar et al., "Who Validates the Validators? Aligning LLM-Assisted Evaluation of LLM Outputs with Human Preferences", UIST 2024, [arXiv:2404.12272](https://arxiv.org/abs/2404.12272).

2. L. Chen, M. Zaharia & J. Zou, "How Is ChatGPT's Behavior Changing over Time?", 2023, [arXiv:2307.09009](https://arxiv.org/abs/2307.09009).

3. L. Zheng et al., "Judging LLM-as-a-Judge", NeurIPS 2023, [arXiv:2306.05685](https://arxiv.org/abs/2306.05685); P. Liang et al., "HELM", 2022, [arXiv:2211.09110](https://arxiv.org/abs/2211.09110).

4. OpenTelemetry, semantic conventions for generative AI systems; D. Sculley et al., NeurIPS 2015.

5. X. Xu & W. Wu, "What Aggregate Scores Miss: Measuring Item-Level Regressions in Commercial LLM API Migrations", 2026, [arXiv:2608.17719](https://arxiv.org/abs/2608.17719); M. Z. Pan et al., "Measuring Agents in Production", ICML 2026, [arXiv:2512.04123](https://arxiv.org/abs/2512.04123).
