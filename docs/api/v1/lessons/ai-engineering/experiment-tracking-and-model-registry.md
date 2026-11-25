# Experiment Tracking, Reproducibility and the Model Registry

> Can you rebuild last month's model, and roll back in minutes?

- Track: AI Engineering › MLOps › Lessons
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/ai-engineering/experiment-tracking-and-model-registry/
- Quiz topic: `mlops`
- Sources checked: 2026-10-29 · Text last changed: 2026-11-20 · Version: 4cf6ec781f

## Intuition

### The situation

Last month's ETA model was better than this week's retrained one. Leadership asks what changed, whether you can go back and whether you can rebuild last month's model exactly. A colleague says the code is in git, so that's covered. The interviewer asks:

> Can you rebuild last month's model, and roll back in minutes?

**Running example:** last month's ETA model was better than this week's retrained one. Leadership asks: what changed, can we go back, and can we rebuild last month's model exactly?

#### "It worked on my notebook"

ML results depend on many moving parts that ordinary version control doesn't capture: the data changes daily, features get redefined, hyperparameters live in someone's command line, and library upgrades change numerics. Without records, debugging a regression becomes guesswork.

### The idea

Think of a dish that came out brilliantly last month. The recipe alone won't recreate it, if you don't know which batch of ingredients went in, which oven you used or how long it really cooked. Code is only the recipe, and the data is the ingredients.

[Figure: Code and config are usually recorded. Data snapshot, feature definitions, seeds, environment, evaluation set version and model registry are what usually go missing.]

_The lab's eight records. With only code and config, none of its five questions can be answered._

### Play

**Try to break it.** Tick only code version and config. Then add the data snapshot and eval set version, then seeds and environment, then the registry. Watch which questions you can answer.

#### "We have the code in git, that's enough"

Which records each question needs is a simplified mapping of standard practice.

With only **code and config** in version control, you can't answer any of the five questions: the data that trained last month's model is gone (the table has changed), so you can't rebuild it, explain the regression, compare runs fairly or satisfy an auditor, and without a registry there's nothing to roll back to. Add the **data snapshot** and **eval set version** and "why is this week worse?" becomes answerable; add **seeds and environment** and you can rebuild; add a **registry** and rollback takes minutes. Even with everything recorded, two runs with different seeds differ: Bouthillier et al. found such variance can be as large as reported improvements, so compare models over several seeds.

**Now say why:** why doesn't having the code let you rebuild the model?

## How it works

### How it works

#### In one breath

A model is the product of **code + data + configuration + randomness + environment**. If any of these isn't recorded, you can't rebuild the model, explain why this week's version is worse, or prove to an auditor what it learned from. **Experiment tracking** means every training run automatically records its code version, a pointer to an immutable data snapshot, feature definitions, hyperparameters, random seeds, library versions and hardware, plus metrics on a **versioned evaluation set**. A **model registry** is the catalogue of trained models with their lineage, stage (candidate, production, archived), approvals and documentation, so deployment and rollback are a matter of pointing to a version. Even then, GPU non-determinism and seeds cause run-to-run variance; measure it before calling a 0.2-point gain real. What you'll be able to do after this: list what to record per run, explain sources of non-determinism, and describe what a registry enables.

#### What every run should record

| Item | Why |
|---|---|
| **Code version** (commit) | the exact training and feature code |
| **Data snapshot** (immutable, by ID or time range) | re-reading "the orders table" tomorrow gives different data |
| **Feature definitions** and their versions | the same feature name can change meaning |
| **Configuration** (hyperparameters, splits) | results depend on them |
| **Seeds** | initialisation, shuffling, sampling |
| **Environment** (library versions, hardware) | numerics and defaults change across versions and GPUs |
| **Evaluation set version and metrics** | comparisons are meaningless on different test sets |
| **Registry entry** (artefact, lineage, stage, approver, model card) | deploy, roll back and audit by version |

Datasheets for datasets and model cards document what the data and model are for, their limits and their evaluation across groups.

## In practice

### In practice

#### Practices

- **Automate recording** inside the training pipeline (not by hand), so every run is tracked, including failed ones.

- **Immutable data:** write training snapshots to versioned, read-only storage; record the query and time range.

- **Lineage:** link data snapshot → features → run → model version → deployment, so you can trace any prediction back.

- **Registry stages and approvals:** candidate → staging → production with automated checks and a named approver; keep the previous production version ready for rollback.

- **Non-determinism:** fix seeds, record hardware and library versions, accept small GPU differences, and report mean ± spread across seeds.

#### A model is only as reproducible as its least-recorded input

Record code, data, features, config, seeds, environment and evaluation for every run, and manage trained models in a registry, so you can rebuild, explain, compare, roll back and audit.

### The answer that sounds right

#### "We can retrain it if we need to"

It sounds right, since you have the code. But the same code on today's data produces a different model, and re-reading "the orders table" tomorrow gives different data. So you need the snapshot. And don't trust "Model B is 0.2 points better" either: Bouthillier et al. found seed variance can be as large as reported improvements.

## Say it

### Can you rebuild last month's model, and roll back in minutes?

#### The interviewer pushes further

Follow-up 1 of 3

Why isn't storing the code enough?

Data and feature definitions change independently; the same code on today's data produces a different model.

Follow-up 2 of 3

Where does non-determinism come from in training?

Random initialisation, data shuffling, dropout, sampling, and non-deterministic GPU kernels and parallel reductions.

Follow-up 3 of 3

What should a model card contain?

Intended use, training data summary, evaluation results overall and by slice, limitations and known risks, owner and version.

#### The 30-second answer

A model depends on code, data, feature definitions, configuration, random seeds and the software environment, so each training run should automatically record all of them, pointing to an immutable data snapshot and a versioned evaluation set, plus its metrics. A model registry stores each trained model with its lineage, stage and approvals, which makes deployment and rollback a version switch and supports audits. Without data snapshots you can't rebuild or explain a regression. And because seeds and GPU non-determinism cause run-to-run variance, I compare models across several seeds before trusting small gains.

**Go further**

#### What not to say

- "We can retrain it if we need to." Not without the data snapshot.

- "Model B is 0.2 points better." Check seed variance first.

**Key terms and sources**

What to record for every training run (code version, data snapshot, feature definitions, configuration, seeds, environment, evaluation set) and why; sources of non-determinism; lineage from data to deployed model; and the model registry as a concept (versions, stages, approvals, rollback) · built from Pineau et al. (Improving Reproducibility in ML Research, JMLR 2021), Bouthillier et al. (Accounting for Variance in ML Benchmarks, MLSys 2021), Sculley et al. (NeurIPS 2015), Breck et al. (ML Test Score, 2017), Gebru et al. (Datasheets for Datasets, CACM 2021) and Mitchell et al. (Model Cards, FAT* 2019) · checked 29 Oct 2026

#### Sources

1. J. Pineau et al., "Improving Reproducibility in Machine Learning Research", JMLR 2021, [arXiv:2003.12206](https://arxiv.org/abs/2003.12206).

2. X. Bouthillier et al., "Accounting for Variance in Machine Learning Benchmarks", MLSys 2021, [arXiv:2103.03098](https://arxiv.org/abs/2103.03098).

3. T. Gebru et al., "Datasheets for Datasets", CACM 2021, [arXiv:1803.09010](https://arxiv.org/abs/1803.09010); M. Mitchell et al., "Model Cards for Model Reporting", FAT* 2019, [arXiv:1810.03993](https://arxiv.org/abs/1810.03993).

4. D. Sculley et al., NeurIPS 2015; E. Breck et al., "The ML Test Score", IEEE Big Data 2017.
