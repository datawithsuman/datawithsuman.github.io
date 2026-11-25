# Improving with Evals: Cheapest Fix First, Then Cut Cost

> Your evals show the agent fails 12% of the time and costs too much. What do you change first?

- Track: AI Engineering › Applied Evals › Lessons
- Type: Concept · 17 min
- Page: https://aimlrounds.com/tracks/ai-engineering/improving-with-evals/
- Before this: Evals in CI: Golden Sets, Regression Gates and Model Upgrades (`ai-engineering/evals-in-ci`)
- Quiz topic: `evals`
- Sources checked: 2026-11-15 · Text last changed: 2026-11-20 · Version: 98630815f2

## Intuition

### The situation

Your agent's evals show a 12% failure rate, mostly missed constraints in multi-step requests, and the monthly bill doubled. One engineer proposes fine-tuning; another wants to switch to the cheapest model. The interviewer asks:

> Your evals show the agent fails 12% of the time and costs too much. What do you change first?

#### Why it matters

Evals only pay off when they drive changes. Teams often jump to the most expensive fix, fine-tuning or a bigger model, when a prompt line would do, or cut cost by switching models without checking what broke. The evaluators and CI you built make every change measurable.

### The idea

Think of fixing a slow, error-prone kitchen. First rewrite the confusing recipe cards. Then reorganise the stations. Hiring a new head chef comes last. For cost, let a junior cook handle simple orders and call the chef only when unsure.

[Figure: Three moves. Fix cheapest first. Cut tokens and models. Cascade the rest.]

_Evals decide which change stays._

### Play

**Try to break it.** Let the cheap model answer everything. Then lower its agreement.

#### Tune the cascade

If the cheap model answers 70% of traces at 96% agreement, overall agreement with the expensive model is 97.2%, and the daily bill falls from $200 to $80, since the cheap model still runs on every trace. Push the cheap model to answer everything and agreement drops to its own 96%; push its share up while its agreement falls, and you miss the target. The threshold is a dial between cost and agreement, set on held-out data.

**Now say why:** why does the threshold trade cost against agreement?

## How it works

### How it works

#### In one breath

Fix in order of effort. **Prompt** edits for specification failures and formatting. **Structural** changes for multi-step errors: split the task, add retrieval or a tool, add a check before the answer. **Automatic prompt optimisation** (like DSPy) once you have 50+ labelled examples and an evaluator. **Fine-tuning** last, for narrow tasks prompting can't fix. Then cut cost: match model size to the task, trim tokens, make prompts cache-friendly, batch what can wait, and use **cascades**: a cheap model answers when confident, an expensive one handles the rest. Your evals decide whether each change stays.

#### Accuracy, then cost

##### Accuracy, by effort

| Fix | Effort | Data needed | Best for |
|---|---|---|---|
| Prompt refinement | low | a few failing examples | specification failures, format, missing constraints |
| Structural change | medium | understanding of the failure pattern | multi-step errors, missing information |
| Automatic prompt optimisation | medium | 50+ labelled examples and an evaluator | when manual iteration plateaus |
| Fine-tuning (LoRA) | high | 50–200+ labelled examples | narrow tasks prompting can't fix |
| Full fine-tuning | high | 500+ labelled examples | style, tone or format at scale |

Structural changes include splitting one prompt into steps, adding retrieval or a tool, running a judgement several times and voting, and adding a synchronous check before the answer goes out.

##### Cost

- **Right-size models:** small models handle classification, extraction and routing well; test them on your evals.

- **Fewer tokens:** shorter prompts, concise tool responses, trimmed history.

- **Cache-friendly prompts:** fixed instructions first, changing content last, so providers' prompt caching applies.

- **Batch:** work that can wait hours, like nightly evaluation, can use batch APIs at lower prices.

##### Cascades

Send every request to a cheap **proxy** model first. If it's confident, use its answer; if not, call the expensive **oracle**. Set the confidence threshold on held-out examples so the combined answers agree with the oracle at your target rate, for example 95%. Confidence can come from token probabilities on classification tasks, or from asking the model to state it. Raw confidence isn't trustworthy, but threshold-finding is: if confidence doesn't separate right from wrong, no threshold qualifies and everything goes to the oracle, the safe default. The book's example: a judge at $0.02 per trace on 10,000 traces a day costs $200 a day before a cascade.

## In practice

### In practice

#### In practice

- **Match fix to failure:** prompts for specification, structure for multi-step errors.

- **Fine-tune last:** once you have the labelled data and a clear, narrow target.

- **Measure every change:** CI plus a fresh look at error analysis.

- **Cut tokens and cache:** fixed content first, changing content last.

- **Cascade with a target:** threshold on held-out data, oracle as the fallback.

- **Watch the trade:** a cheaper path can shift which failures happen.

### The answer that sounds right

#### "Let's fine-tune to fix the 12% failures"

It sounds powerful, but if the failures are missed constraints, a clearer prompt or splitting the task may fix them in a day. Fine-tuning needs labelled data and maintenance; try the cheaper fixes first and let the evals decide.

## Say it

### Your evals show the agent fails 12% of the time and costs too much. What do you change first?

#### The interviewer pushes further

Follow-up 1 of 3

When is fine-tuning the right fix?

When the task is narrow and well defined, prompting and structural changes have plateaued, and you have enough labelled examples, roughly 50–200+ for LoRA.

Follow-up 2 of 3

How do you set a cascade threshold?

Run both models on held-out examples, then pick the lowest confidence threshold at which the combined answers still agree with the expensive model at your target rate.

Follow-up 3 of 3

You switched to a cheaper model and the average score held. Are you done?

Not yet. Check per failure mode and per slice: averages can hide a new failure concentrated in one feature. Redo error analysis on a sample.

#### The 30-second answer

I'd fix in order of effort: prompt edits for specification and format problems, structural changes like splitting the task, adding retrieval or a check for multi-step errors, automatic prompt optimisation once I have 50 or more labelled examples, and fine-tuning last for narrow tasks. Each change is kept only if the evals improve. For cost I'd right-size models, trim tokens, put fixed content first for caching, batch what can wait, and use a cascade: a cheap model answers when confident, with the threshold set on held-out data to hit a target agreement with the expensive model.

**Key terms and sources**

Choosing fixes by effort (prompt, structure, automatic prompt optimisation, fine-tuning), cutting cost without losing accuracy (smaller models, fewer tokens, caching, batching), and model cascades that send only uncertain cases to an expensive model. · checked 15 Nov 2026

#### Sources

- H. Husain and S. Shankar, _Evals for AI Engineers_ (O'Reilly): the Analyze-Measure-Improve lifecycle, error analysis, judges, CI and review

- [L. Chen, M. Zaharia and J. Zou, FrugalGPT: how to use large language models while reducing cost and improving performance, 2023](https://arxiv.org/abs/2305.05176)

- [O. Khattab et al., DSPy: compiling declarative language model calls into self-improving pipelines, 2023](https://arxiv.org/abs/2310.03714)

- [H. Husain and S. Shankar, AI Evals: everything you need to know (FAQ)](https://hamel.dev/blog/posts/evals-faq/)

Explanations and examples are ours, built from these sources. Lab numbers are illustrative unless a lab says otherwise. Many recent papers are preprints, and benchmark scores change quickly.
