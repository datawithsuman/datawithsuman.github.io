# A Prompt Fix That Broke Production

> A one-line prompt fix solved a reported bug, passed five spot checks, and broke other cases in production. What went wrong, and what process prevents it?

- Track: AI Engineering › Prompt engineering › Scenarios
- Type: Concept · 18 min
- Page: https://aimlrounds.com/tracks/ai-engineering/prompt-change-broke-production/
- Before this: Prompt Engineering Patterns (`ai-engineering/prompt-engineering-patterns`), LLM Judges: Pairwise Preferences and Pass/Fail Checks (`ai-engineering/llm-as-a-judge`)
- Quiz topic: `prompt`

## Intuition

### The situation

A product manager reported one wrong answer. An engineer added a line to the prompt, checked five examples and shipped. The next day, escalations rose for cases nobody touched. The interviewer asks:

> A one-line prompt fix solved a reported bug, passed five spot checks, and broke other cases in production. What went wrong, and what process prevents it?

#### The incident

A support assistant gave a customer the wrong return window for sale items. The engineer added: "For sale items, always state that returns are not accepted." Five sale-item questions looked right, so it shipped. The next day, refund escalations rose. The new line also fired for full-price items bought during a sale, and for gift returns, which the policy allows. The average score on a small test set hadn't moved, because one case was fixed and a few others broke. The story is illustrative, but the pattern is common.

### The idea

Think of changing one word in a company-wide policy memo to fix one complaint. Every employee reads the memo, and some apply the new word to cases you never meant. Checking with five colleagues won't show how the whole company reads it.

[Figure: Three safeguards. Version every prompt. Run a regression set. Roll out gradually.]

_A prompt line applies to every request._

### Play

**Try to break it.** Run 5 test cases against a 2% break. Then raise the cases.

#### How many test cases catch a break?

Exact arithmetic for a random sample of traffic. The traffic figure is illustrative.

If the fix breaks 2% of requests, five spot checks catch it only 10% of the time. Fifty cases catch it 64% of the time, and 200 cases 98%. At 1% broken, you need about 299 random cases for a 95% chance. Meanwhile, at 100,000 requests a day, 2% is 2,000 bad answers. That's why a regression set of a few hundred cases, plus every past incident, runs on each change.

**Now say why:** why can the average stay flat while users get worse answers?

## How it works

### How it works

#### In one breath

A product manager reports one bad answer. An engineer adds a line to the prompt, tries five examples, and ships. The next day, other answers have changed for the worse. A prompt is applied to every request, so a one-line change can shift behaviour everywhere, and small wording changes have moved accuracy by large amounts in studies. Five examples almost never catch a problem that affects 2% of requests. The fix is to treat prompts as code: **version** them, run a **regression set** that includes past incidents on every change, compare **case by case**, roll out gradually, and keep **rollback** one step away.

#### Why it happened

##### Prompts have global effects

Code changes usually affect one path. A prompt line is read on every request, and the model decides when it applies. Sclar et al. found that formatting changes alone, such as separators and spacing, changed accuracy by up to 76 points on some tasks for LLaMA-2-13B. A new rule can also conflict with old ones. See System Prompts with Many Rules.

##### Spot checks can't see rare breaks

If a change breaks 2% of requests, five random examples show none of them about 90% of the time. And an average hides trades: one fix and one new failure score the same as no change.

##### Other things change behaviour too

- **The model:** a provider updates a model alias, or you switch models. Pin a dated model version where possible.

- **The schema and tools:** field descriptions and tool definitions are read as instructions.

- **Retrieved context:** a re-index changes what the model sees.

##### What the process should be

1. **Version the prompt** in the repository, with the model version, reviewed like code.

2. **Keep a regression set:** real requests across the main intents, every past incident, and edge cases. Each has expected behaviour checked by code or an LLM judge.

3. **Compare case by case:** list which cases got better and which got worse, not just the average.

4. **Roll out gradually:** shadow traffic or a small percentage, with live metrics such as escalations. See Design an LLM Prompt Test.

5. **Roll back fast:** switch to the previous version by its ID, without a redeploy.

#### The maths

$$ {P(\text{see a break})} = 1 - (1 - {f})^{{n}} $$

This assumes test cases are a random sample of traffic. Adding past incidents and edge cases on purpose catches known risks with fewer cases.

- **chance the test catches it**: The probability at least one broken case appears in your test set.

- **share of requests broken**: How much of your traffic the change makes worse.

- **test cases**: How many representative cases you run.

## In practice

### In practice

#### What to say

- **Diagnose:** the line applied more widely than intended, and five examples couldn't show a 2% problem.

- **Fix now:** roll back to the previous version, then write a narrower rule with the reason, for example "items bought at a sale price can't be returned, except gifts, because the policy says so".

- **Add cases:** the original bug, full-price items bought during a sale, and gift returns go into the regression set.

- **Prevent:** versioned prompts, a regression set run on every change, case-by-case comparison, gradual rollout with live metrics, and one-step rollback.

- **Consider structure:** if the rule is really policy logic, look it up in code and pass the result to the model, rather than asking the model to apply it.

### The answer that sounds right

#### "It passed my spot checks, so it's safe"

It sounds reasonable, since the fixed case works. But five examples miss a problem affecting 2% of requests about 90% of the time. Run a regression set of a few hundred cases, including past incidents, and compare case by case.

## Say it

### A one-line prompt fix solved a reported bug, passed five spot checks, and broke other cases in production. What went wrong, and what process prevents it?

#### The interviewer pushes further

Follow-up 1 of 3

The average score is unchanged after a prompt edit. Is it safe to ship?

Not necessarily. One fixed case and one new failure average out. Look at which cases changed in each direction.

Follow-up 2 of 3

The provider updated the model and answers changed, with no prompt change. How do you prevent this?

Pin a dated model version, and run the regression set before moving to a new one, the same as a prompt change.

Follow-up 3 of 3

How big should a regression set be?

Big enough to catch the failure rates you care about: about 300 random cases for a 95% chance of seeing a 1% problem. Add every past incident and known edge case on top.

#### The 30-second answer

A prompt line applies to every request, and the model decides when it fires, so a narrow fix can change behaviour everywhere. Five spot checks miss a problem that affects 2% of requests about 90% of the time. I'd roll back first, then write a narrower rule with its reason, and add the original bug and the new failures to a regression set. Going forward, prompts are versioned with the model, every change runs a few hundred cases including past incidents, I compare case by case rather than the average, and I roll out gradually with one-step rollback.

**Key terms and sources**

A scenario: why prompt changes have global effects, why spot checks miss regressions, and how to version, evaluate, roll out and roll back prompts like code. · checked 7 Nov 2026

#### Sources

- [Sclar et al., Quantifying Language Models' Sensitivity to Spurious Features in Prompt Design](https://arxiv.org/abs/2310.11324)

- [Anthropic, Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)

- [OpenAI, GPT-5 prompting guide (archived cookbook)](https://developers.openai.com/cookbook/examples/gpt-5/gpt-5_prompting_guide)

- [Zheng et al., Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena](https://arxiv.org/abs/2306.05685)

Explanations are ours, built from these sources. Lab numbers are illustrative unless a lab says otherwise. Many recent papers are preprints, and vendor guides change with each model.
