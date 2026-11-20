# Model Upgrades and Retirements

> Your provider is retiring the model your product uses in 60 days. The new one scores higher on benchmarks. How do you migrate safely?

- Track: AI Engineering › LLMOps › Lessons
- Type: Concept · 18 min
- Page: https://aimlrounds.com/tracks/ai-engineering/model-upgrades-and-retirements/
- Before this: LLMOps: What's Different (`ai-engineering/llmops`)
- Quiz topic: `llmops`

## Intuition

### The situation

Your provider emails that the model your product uses retires in 60 days. The successor scores higher on public benchmarks, and the team plans to change the model name the week before. The interviewer asks:

> Your provider is retiring the model your product uses in 60 days. The new one scores higher on benchmarks. How do you migrate safely?

#### Why it matters

A library you depend on can be pinned forever. A hosted model can't: on the shutdown date, every request fails. Providers also release new versions often, and switching changes behaviour even when the average improves. Interviewers ask how you'd handle a forced migration, because it combines evaluation, release safety and operations.

### The idea

Think of a supplier replacing an ingredient with a 'better' one. Most dishes taste the same or better, but a few of your signature dishes may not. You'd cook each dish with both before switching, not just read the supplier's ratings.

[Figure: Three steps. Keep the model ID in configuration. Compare case by case. Release like any change.]

_A better average can hide your worst case._

### Play

**Try to break it.** Pick the maths upgrade. Then the instruction-following ones.

#### What the average hides

Shares are the measured results from Xu and Wu (2026), with 50 runs per item. Case counts apply those shares to your golden set size, which is illustrative: your own tasks will differ.

The maths upgrade gained 7.3 points, yet in a 300-case golden set those shares mean about 18 cases got reliably worse. The first instruction-following upgrade gained only 1.9 points, while about 25 cases got worse and 34 better. The next one lost 3.9 points overall, yet still improved about 20 cases. If your product depends on one of the cases that regressed, the higher average doesn't help you. So compare case by case, with several runs per case.

**Now say why:** why can the average rise while many cases get worse?

## How it works

### How it works

#### In one breath

Hosted models are retired on the provider's schedule: Anthropic promises at least 60 days' notice, and OpenAI at least 6 months for generally available models. A study of thousands of open-source projects found 82% of migrations happened **after** the old model was shut down, and 94% of the apps had the model name hard-coded. A newer model's higher average also hides individual cases that got worse: in one study, an upgrade that gained 7.3 points still made 6% of questions reliably worse. So keep the model ID in configuration, watch deprecation notices, and compare old and new **case by case**, with repeated runs, before switching.

#### What happens in practice

##### Notice periods

- **Anthropic:** at least 60 days' notice for publicly released models, by email and in the documentation.

- **OpenAI:** at least 6 months for generally available models, 3 months for specialised variants, and as little as 2 weeks for previews, unless safety or compliance needs it faster.

##### What happened across thousands of apps

A 2026 study matched 5,139 GitHub commits that moved away from retired OpenAI, Anthropic and Google models to the providers' published dates. An estimated 82% landed after the shutdown date, with a median of 39 days after. For Anthropic's 60 to 114-day notices, 89% were late, and with OpenAI's one-year notice for its Assistants API, only 13% were. The model ID was hard-coded in 94% of apps. About 8% of the migrations checked by hand showed silent failures, where error handling turned the failure into an apologetic message, an empty result or even a constant answer. Only 4.5% of the commit messages mentioned an evaluation suite.

##### Better on average, worse on some

Xu and Wu ran 900 benchmark items 50 times each on three successive GPT versions. Every comparison had items that reliably improved and items that reliably regressed. One upgrade gained 7.3 points on maths while 6% of items got reliably worse. A single run per item couldn't detect any of the 457 reliable changes. Some regressions were only in exact format, which matters if your code parses the output.

##### The migration playbook

1. **Keep the model ID in configuration**, not code, and record it in every trace.

2. **Watch for retirements:** subscribe to deprecation notices, and fail a CI check when a configured model has a retirement date.

3. **Run your golden set on both models**, several times per case, and list which cases changed in each direction, not just the average.

4. **Re-tune prompts and parameters:** newer models may reject old parameters or need different prompts. See Prompting Reasoning Models.

5. **Shadow, then canary** with rollback, as for any release. See LLMOps.

6. **Fail loudly:** an unavailable model must raise an alert, not a polite apology to users.

#### The maths

$$ {\Delta_{\text{avg}}} \approx {P_{+}} - {P_{-}} $$

A rough relation: the average reflects the balance of gains and losses, so it says nothing about how many cases changed. Look at both shares.

- **change in the average**: What a benchmark table reports.

- **share that improved**: Cases the new model now gets right more often.

- **share that regressed**: Cases it now gets wrong more often. The average can rise while this is large.

## In practice

### In practice

#### In practice

- **Plan migrations, don't react:** start testing the successor when a retirement is announced, not near the date.

- **Pinned versions retire too:** pinning gives stable behaviour, but needs a retirement watch.

- **Fine-tuned models cost most:** in the study, fine-tuned apps changed a median of 693 lines, against 6 for prompt-only ones, because the new base model needs new tuning.

- **Check format, not just correctness:** parsers break on small format changes.

- **Track tokens and cost:** a newer model may write much longer answers or more reasoning.

### The answer that sounds right

#### "The new model is better on benchmarks, just swap the name"

It sounds safe, since the new model is better on average. But averages hide cases that got worse, and parameters or formats may change. Compare case by case on your own golden set, then shadow and canary.

## Say it

### Your provider is retiring the model your product uses in 60 days. The new one scores higher on benchmarks. How do you migrate safely?

#### The interviewer pushes further

Follow-up 1 of 3

The new model scores 3 points higher on your golden set. Ship it?

Look case by case first: which cases got worse, and do any matter most, like refunds or safety? Run each several times, since single runs are noisy, then shadow and canary.

Follow-up 2 of 3

Why did the old model's retirement show up as polite apologies instead of errors?

Error handling caught the failure and returned a friendly message. That hid an outage. Errors from a missing model must alert and show as errors.

Follow-up 3 of 3

Should you always use the provider's 'latest' alias?

It avoids retirements of old versions but changes behaviour without warning. Most teams pin a dated version, and upgrade on purpose after testing.

#### The 30-second answer

Hosted models have expiry dates: at least 60 days' notice from Anthropic and 6 months from OpenAI for generally available models. Yet a study of thousands of projects found 82% migrated only after the shutdown, mostly with hard-coded model IDs. I'd keep the model ID in configuration, watch deprecation notices in CI, and run the golden set on old and new models several times per case, listing what got better and worse, because averages hide regressions. One upgrade gained 7.3 points while 6% of items got reliably worse. Then re-tune prompts, shadow and canary, and make sure failures alert rather than hide.

**Key terms and sources**

Why hosted models have expiry dates, what providers promise, what happened when models were retired across thousands of apps, why a better average can hide regressions, and a migration playbook. · checked 7 Nov 2026

#### Sources

- [Kim, When the Model Retires: An Empirical Study of LLM Migration in Open-Source Applications](https://arxiv.org/abs/2609.31288)

- [Xu and Wu, What Aggregate Scores Miss: Measuring Item-Level Regressions in Commercial LLM API Migrations](https://arxiv.org/abs/2608.17719)

- [Chen, Zaharia and Zou, How Is ChatGPT's Behavior Changing over Time?](https://arxiv.org/abs/2307.09009)

- [Anthropic, Model deprecations (checked 7 Nov 2026)](https://platform.claude.com/docs/en/about-claude/model-deprecations)

- [OpenAI, Deprecations (checked 7 Nov 2026)](https://developers.openai.com/api/docs/deprecations)

Explanations are ours, built from these sources. Lab numbers are illustrative unless a lab says otherwise. Many recent papers are preprints, and provider policies change.
