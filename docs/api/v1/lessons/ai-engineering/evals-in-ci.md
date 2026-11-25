# Evals in CI: Golden Sets, Regression Gates and Model Upgrades

> A prompt change drops your golden-set pass rate from 94% to 90%. Do you block the release?

- Track: AI Engineering › Applied Evals › Lessons
- Type: Concept · 17 min
- Page: https://aimlrounds.com/tracks/ai-engineering/evals-in-ci/
- Before this: Code Checks First: Assertions, Schemas and Execution (`ai-engineering/code-based-evaluators`), Can You Trust Your Judge? TPR, TNR and Corrected Pass Rates (`ai-engineering/validating-an-llm-judge`)
- Quiz topic: `evals`
- Sources checked: 2026-11-15 · Text last changed: 2026-11-20 · Version: 5ed8e1cce3

## Intuition

### The situation

Your team changed the system prompt to shorten answers. The golden set's pass rate went from 94% to 90% on 150 cases. One engineer says it's noise; another wants to block. The interviewer asks:

> A prompt change drops your golden-set pass rate from 94% to 90%. Do you block the release?

#### Why it matters

LLM apps break silently. Voiceflow swapped in a newer GPT-3.5 for a customer's intent classifier and accuracy dropped about 10 points on the same prompt. In October 2024, the model behind the gpt-4o alias changed and some apps' function calls started arriving as plain text. Teams with a regression suite and pinned versions found out in CI; others found out from customers.

### The idea

Think of a building's fire drill. Passing it means the known exits still work, not that the building is safe from every fire. You still need smoke detectors for the fires nobody planned.

[Figure: Three rules. Curate the set. Gate every change. Read what flipped.]

_CI protects known cases; it doesn't measure production._

### Play

**Try to break it.** Keep the 4-point drop and grow the golden set.

#### Real regression or noise?

On 150 cases, 94% to 90% is six cases and a z score of about 1.3: not enough to call on the average alone. On 600 cases the same drop gives z of about 2.5, a clear regression. Small golden sets are for catching specific cases, so read the flips; bigger sets let the average speak too.

**Now say why:** why does the same drop mean more on a bigger set?

## How it works

### How it works

#### In one breath

A golden set is 100–200 hand-picked cases: core features, past failures and edge cases, each with a reference or criteria. Every prompt, model or tool change runs it, and failures block the merge. Pin model versions, including the judge's. With small sets, a few points can be noise, so look at which cases flipped and use a significance check. Passing CI means you didn't break known cases, not that production is good. Treat model upgrades as code changes: run CI, try removing old workaround instructions, and redo error analysis.

#### The golden set and the gate

##### What goes in

- Cases covering every core feature and path: each tool, RAG queries, prompt branches.

- Every serious past failure, as a regression test.

- Edge cases from error analysis.

100–200 cases is typical for a mature set. It's purpose-built, not a random sample. Checks are reference-based where possible (the right rows, the right tool) and code-based where possible; LLM judges are fine with a pinned model version.

##### Keep it alive

Add each new production failure (often 5–10 examples of it). Retire cases that no longer exercise live code. Capability evals that now pass reliably graduate into the set.

##### Noise versus regression

LLM outputs vary between runs, and small sets have wide error bars. A drop from 94% to 90% on 150 cases is 6 cases. Look at the cases: if the same three critical cases fail every run, that's a regression whatever the average says. For the aggregate, compare the two rates with a significance check, and rerun flaky cases a few times rather than ignoring them.

##### CI is a smoke test

Passing means the known cases still work. It says nothing about the thousands of new queries in production; that's what online evals are for.

##### Model upgrades

1. Pin versions in production; set a maximum age before upgrading.

2. Run the new model through CI like any change.

3. For prompts that pass, try deleting old workaround instructions; newer models often do better without them, and the prompt gets cheaper.

4. For failures, check whether it's a real regression or a format change your checks are too strict about.

5. Redo error analysis on a sample: new models bring new failure modes.

For provider retirement notices and rollout mechanics, see Model Upgrades and Retirements.

#### The maths

$$ {z} = \frac{{\hat p_{old}} - {\hat p_{new}}}{\sqrt{\bar p(1-\bar p)\left(\frac{2}{{n}}\right)}} $$

This treats the runs as independent samples, which is conservative for the same cases; a paired view (which cases flipped) is sharper. Either way, a critical case that fails every time is a regression regardless of z.

- **test statistic**: Above about 1.96, the drop is unlikely to be noise at the 5% level.

- **old pass rate**: On the golden set before the change.

- **new pass rate**: After the change, same cases.

- **golden-set size**: Same n for both runs; p̄ is the average of the two rates.

## In practice

### In practice

#### In practice

- **100–200 purpose-built cases:** features, past failures, edge cases.

- **Run on every change:** prompts, models, tools, retrieval.

- **Code checks first; pin judge models:** so CI doesn't drift by itself.

- **Read the flips:** critical cases must pass; use significance for the average.

- **Grow and prune:** add production failures, retire stale cases.

- **Upgrade deliberately:** pin, CI, simplify prompts, redo error analysis.

### The answer that sounds right

#### "CI passes, so quality is fine"

It sounds like a green light, but CI covers only the cases you chose. New kinds of queries and failures show up only in production. Pair CI with sampled monitoring.

## Say it

### A prompt change drops your golden-set pass rate from 94% to 90%. Do you block the release?

#### The interviewer pushes further

Follow-up 1 of 3

Why not use a random sample of production as the golden set?

CI is for protecting specific behaviours, so the set is chosen to cover features, past bugs and edge cases. Random production samples belong to monitoring.

Follow-up 2 of 3

Your CI judge's results shifted with no code change. Why?

The judge model probably changed behind an alias. Pin exact model versions for judges and the app.

Follow-up 3 of 3

A new model passes CI. Can you ship it?

Not yet: CI covers known cases only. Simplify prompts where you can, redo error analysis on a sample of its outputs, and roll out gradually with monitoring.

#### The 30-second answer

I'd keep a golden set of 100 to 200 purpose-built cases, covering core features, every serious past failure and edge cases, with code checks where possible and pinned judge models elsewhere, and run it on every prompt, model or tool change. A drop doesn't automatically mean a regression on a small set, so I'd read which cases flipped, treat any critical case that fails as blocking, and use a significance check on the average. Passing CI only means known cases still work, so production monitoring is separate. Model upgrades go through CI too, then I'd try removing old workaround instructions and redo error analysis.

**Key terms and sources**

What goes in a golden dataset, how CI checks it on every change, how to tell a real regression from noise, why passing CI doesn't mean production is fine, and how to handle model upgrades. · checked 15 Nov 2026

#### Sources

- H. Husain and S. Shankar, _Evals for AI Engineers_ (O'Reilly): the Analyze-Measure-Improve lifecycle, error analysis, judges, CI and review

- [Anthropic, Demystifying evals for AI agents, Jan 2026](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)

- [H. Husain and S. Shankar, AI Evals: everything you need to know (FAQ)](https://hamel.dev/blog/posts/evals-faq/)

- [L. Chen, M. Zaharia and J. Zou, How is ChatGPT's behavior changing over time?, 2023](https://arxiv.org/abs/2307.09009)

Explanations and examples are ours, built from these sources. Lab numbers are illustrative unless a lab says otherwise. Many recent papers are preprints, and benchmark scores change quickly.
