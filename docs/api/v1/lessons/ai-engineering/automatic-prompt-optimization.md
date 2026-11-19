# Automatic Prompt Optimisation

> Instead of hand-tuning prompts, your team wants an optimiser to write them. How do these work, and what can go wrong?

- Track: AI Engineering › Prompt engineering › Lessons
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/ai-engineering/automatic-prompt-optimization/
- Before this: Prompt Engineering Patterns (`ai-engineering/prompt-engineering-patterns`), RAG Evals: Retrieval, Faithfulness and Relevance (`ai-engineering/rag-evals`)
- Quiz topic: `prompt`

## Intuition

### The situation

Your team spends days hand-tuning prompts for a multi-step pipeline. Someone suggests an optimiser, and a first run on 30 examples reports a 12-point gain. The interviewer asks:

> Instead of hand-tuning prompts, your team wants an optimiser to write them. How do these work, and what can go wrong?

#### Why it matters

Hand-tuning prompts by feel is slow, and a change that fixes one case can break others. If you already have a metric and labelled examples, an optimiser can search far more prompts than a person, and do it again whenever the model changes. Interviewers ask how these tools work, when they're worth it, and how you'd trust the result.

### The idea

Think of auditioning 100 singers with one short song each. The one who sounds best that day may just have been lucky with the song. A longer audition, or a second round, shows who's really best.

[Figure: Three parts. A metric and data. A search over prompts. A fair final check.]

_The winner of many noisy tries looks better than it is._

### Play

**Try to break it.** Try 100 prompts on 30 examples. Then raise the examples to 1,000.

#### The winner looks better than it is

Illustrative simulation, averaged over 1,500 runs. Each candidate's real accuracy is drawn around 75%, with a spread of 2 points, and its validation score adds sampling noise for the chosen number of examples.

Trying 10 prompts on 30 validation examples, the winner scores 87.5% on validation, but its real accuracy is 75.7%, so its score is overstated by 11.8 points. Try 100 prompts on the same 30 examples, and the gap grows to 19.3 points, as more candidates means more chances for noise to win. With 1,000 validation examples, 10 prompts are overstated by only 1.2 points, and the winner's real score, 77.5%, is close to the best available, 78.1%. That's the multiple-testing problem ESPO points to, with about 10 candidates on about 30 examples. Use more validation data, and confirm on a held-out test set.

**Now say why:** why does trying more prompts make the winner's score less trustworthy?

## How it works

### How it works

#### In one breath

A prompt optimiser treats the prompt as something to search over. You give it a program, a metric and a few hundred labelled examples, and it proposes prompts, scores them, and keeps the best. Older methods searched over instructions and few-shot examples. **GEPA** reads the system's traces, reflects on failures in plain language, and rewrites prompts. It reported 14 points of gain against 7 for MIPROv2, and beat reinforcement learning with up to 35 times fewer runs. The risks: picking the best of many candidates on a small validation set flatters the winner, and optimised prompts can **bloat** with rules.

#### How optimisers work

##### What you need first

- **A program:** one or more LLM calls, such as retrieve, then answer.

- **A metric:** exact match, a code check, or an LLM judge.

- **Data:** a training set to learn from, and a separate validation set to choose the winner. Keep a held-out test set too.

##### The main methods

| Method | How it searches |
|---|---|
| **APE** (2022) | An LLM proposes many instructions from examples, and the best-scoring one is kept. |
| **OPRO** (2023) | An LLM sees earlier prompts with their scores, and proposes better ones. |
| **DSPy** (2023) | You write the pipeline as modules. It collects successful runs and uses them as few-shot examples. |
| **MIPROv2** (2024) | Proposes instructions and example sets, then picks combinations with Bayesian search. |
| **GEPA** (2025) | Reads full traces, including reasoning, tool calls and error messages, reflects on what went wrong, and rewrites prompts. It keeps the best prompt for each example, not one overall winner, so useful strategies survive. |

##### What GEPA reported

Across four tasks, GEPA improved the aggregate score by 14.29 points with GPT-4.1 mini, against 7.04 for MIPROv2. With Qwen3 8B, it gained 12.44 points, against 6.26 for MIPROv2 and 2.29 for GRPO, a reinforcement learning method that updates the model's weights over 24,000 runs. GEPA needed up to 35 times fewer runs, and its prompts were about 33% shorter than MIPROv2's. The authors expect weight updates to win when data and compute are plentiful.

##### Prompt bloat

Each round of reflection tends to add rules and caveats. A 2026 study, ESPO, found GEPA's prompts were up to 3 times longer than its own, at 1,878 characters on average against 1,004, yet less accurate, 70.9% against 74.7% across seven benchmarks. Its fixes: study all errors before rewriting, and choose the winner in a way that's stable under resampling. Longer prompts also cost more on every request.

#### The maths

$$ \Pi^{*} = \arg\max_{\Pi} \; \mathbb{E}_{(x,m)}\big[\mu(\Phi(x;\Pi), m)\big] \quad \text{s.t.} \quad \#\text{runs} \le B $$

The objective as the GEPA paper writes it. The catch is the expectation: you only see a small validation set, so the winner's score is an estimate, and choosing the best of many estimates flatters it.

- **the chosen prompts**: The best set of prompts found.

- **the prompts**: What the optimiser changes. The model’s weights stay fixed.

- **over real inputs**: Averaged over examples x with expected results m. In practice, a validation set stands in for it.

- **the metric**: How each output is scored.

- **the budget**: Each run costs money and time, so the search is limited.

## In practice

### In practice

#### In practice

- **Get the metric right first:** an optimiser will exploit a weak metric. Check a sample of outputs by hand.

- **Use enough validation data:** with a few dozen examples and many candidates, the winner's score is inflated. Confirm on a held-out test set before shipping.

- **Watch length:** track prompt length and cost per request alongside accuracy, and prefer the shorter prompt when scores are close.

- **Read the result:** optimised prompts can contain odd rules fitted to a few examples. Review them like code.

- **Re-run when the model changes:** a prompt tuned for one model is tied to it.

- **Know the alternative:** with lots of data and a fixed model you control, fine-tuning may win. See Prompt vs RAG vs Fine-Tuning.

### The answer that sounds right

#### "The optimiser found a prompt 12 points better"

It sounds convincing, but if it was chosen from many candidates on a few dozen examples, much of that gain can be noise. Check the winner on a fresh, larger test set, and watch its length and cost.

## Say it

### Instead of hand-tuning prompts, your team wants an optimiser to write them. How do these work, and what can go wrong?

#### The interviewer pushes further

Follow-up 1 of 3

You have 25 labelled examples. Should you run an optimiser?

Probably not yet. With so few examples, the winner's score is mostly noise, and you can't hold out a test set. Label more real cases first, or use the examples to guide manual changes.

Follow-up 2 of 3

The optimised prompt scores 6 points higher on validation but no better in production. Why?

Likely overfitting: it was chosen from many candidates on a small set, or the validation data doesn't match production traffic. Check on a fresh, representative test set.

Follow-up 3 of 3

Why might an optimiser beat fine-tuning with little data?

It learns from rich feedback, such as error messages and reasoning traces, rather than a single score per run, and a few rules in a prompt can fix a whole class of errors.

An optimiser treats prompts as parameters. I give it the pipeline, a metric and labelled data, and it proposes, scores and keeps better prompts. DSPy and MIPROv2 search over instructions and few-shot examples. GEPA reflects on full traces in plain language, and reported about 14 points of gain against 7 for MIPROv2, with far fewer runs than reinforcement learning. I watch two risks. Choosing the best of many prompts on a small validation set inflates the winner's score, so I confirm on held-out data. And prompts can bloat with rules, so I track length and cost too.

**Key terms and sources**

How prompt optimisers such as APE, OPRO, DSPy, MIPROv2 and GEPA search for better prompts against a metric, what they need, and the risks: overfitting to small validation sets and prompts that keep growing.

#### Sources

- Zhou et al., Large Language Models Are Human-Level Prompt Engineers (APE)

- Yang et al., Large Language Models as Optimizers (OPRO)

- Khattab et al., DSPy

- Opsahl-Ong et al., Optimizing Instructions and Demonstrations for Multi-Stage Language Model Programs (MIPROv2)

- Agrawal et al., GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning

- Liu et al., ESPO: Error-Structured Prompt Optimization

Explanations are ours, built from these sources. Lab numbers are illustrative unless a lab says otherwise. Many recent papers are preprints, and vendor guides change with each model.
