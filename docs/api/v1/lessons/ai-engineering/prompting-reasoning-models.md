# Prompting Reasoning Models

> Your team moved to a reasoning model, but kept the old prompt full of step-by-step instructions. What should change?

- Track: AI Engineering › Prompt engineering › Lessons
- Type: Concept · 18 min
- Page: https://aimlrounds.com/tracks/ai-engineering/prompting-reasoning-models/
- Before this: Prompt Engineering Patterns (`ai-engineering/prompt-engineering-patterns`), Reasoning Models: RLVR, GRPO and Test-Time Compute (`fundamentals/reasoning-models-grpo`)
- Quiz topic: `prompt`

## Intuition

### The situation

Your team switched its assistant to a reasoning model, but kept the old prompt: a 12-step procedure, "think step by step" and a prefilled answer. Answers got slower and pricier, and one model now returns an error. The interviewer asks:

> Your team moved to a reasoning model, but kept the old prompt full of step-by-step instructions. What should change?

#### Why it matters

Many prompts were written for models that answered straight away. Writers added "think step by step", long lists of steps, and examples of worked reasoning, and these helped. Most frontier models now reason by default, in hidden tokens before the visible answer. Prompts written the old way can waste tokens, slow answers down, and sometimes do worse. Interviewers ask about this because it's a common mistake when teams switch models. For how these models are trained, see Reasoning Models and GRPO.

### The idea

Think of briefing a senior colleague compared with a new intern. The intern needs every step written down. The senior colleague needs the goal, the limits and what done looks like, and works better without a script.

[Figure: Three changes. Give goals, not steps. Tune effort, not wording. Remove old tricks and contradictions.]

_Reasoning models already think. Tell them what, not how._

### Play

**Try to break it.** Add "think step by step" to each model type. Then raise the effort.

#### What a prompt habit costs

–

Token counts, prices and speed are illustrative: 2,000 input tokens at $2 per million, output at $10 per million, and 100 tokens per second. The accuracy notes are the Wharton report's measured results on GPQA Diamond.

A non-reasoning model writes about 300 tokens, costing about $7 per 1,000 requests. Asking it to think step by step raises that to 1,000 tokens, $14 and 10 seconds per answer, and for some models that bought a real gain. A reasoning model at medium effort already writes about 4,000 hidden tokens, so it costs $47 and takes about 43 seconds. Adding the instruction makes it write its reasoning out as well, for $50, while the measured gain was about 3% at most. At high effort, cost rises to $127. So the choice that matters is the effort setting, chosen with your evaluations, not the wording.

**Now say why:** why does the instruction help one model type and barely help the other?

## How it works

### How it works

#### In one breath

Reasoning models already think before they answer, in hidden tokens you pay for. So old tricks like "think step by step" add little: one study found gains of about 3% or less for reasoning models, and up to 80% more time. The vendors now give the same advice. Describe the **goal**, the **constraints** and the **output you expect**, then let the model plan. Add step-by-step guidance only when the first attempt fails. Control how much it thinks with the **reasoning effort** setting, not with prompt tricks, and remove contradictions, which hurt these models more.

#### What changes

| Old habit | For a reasoning model |
|---|---|
| "Think step by step" | Usually unnecessary, as it already reasons. Ask for a short summary of the reasoning if users need one. |
| A long list of steps to follow | Give the goal, the constraints and what counts as done. Add steps only if results show they're needed. |
| A token budget written in the prompt | Use the API's reasoning effort setting. |
| Prefilling the start of the answer | Not supported on some newer models. Ask for the format directly, or use structured output. |
| Rules added over months, some in tension | Remove contradictions. A reasoning model tries to satisfy all of them, and spends effort doing so. |

##### What the evidence says

The Wharton Generative AI Labs tested chain-of-thought prompts on 198 PhD-level science questions (GPQA Diamond), with 25 runs per question. For models that don't reason by default, asking for step-by-step reasoning raised average accuracy by 13.5% for Gemini Flash 2.0 and 11.7% for Claude 3.5 Sonnet, but only 4.4% for GPT-4o-mini, which wasn't significant. It also made answers more variable. For reasoning models, the gains were 2.9% for o3-mini and 3.1% for o4-mini, and Gemini Flash 2.5 got 3.3% worse. The prompt took 20 to 80% longer for reasoning models, and 35 to 600% longer for the others.

##### What the vendors now advise

- **OpenAI:** give reasoning models a clear goal, strong constraints and an explicit output contract, rather than prescribing every step. Its GPT-5 guide warns that contradictory or vague instructions can be more damaging to GPT-5 than to other models. Depending on the model, reasoning effort can run from none up to xhigh or max, with medium as the default for its newest models.

- **Google:** for thinking models, start with general instructions that describe the outcome you want, and add step-by-step guidance only if the first attempt fails. Ask the model to check its own work.

- **Anthropic:** newer Claude models think adaptively, and effort replaces a fixed thinking budget. Prefilling the last assistant turn now returns an error on these models. Explain why each rule exists, as the model generalises from the reason.

These guides change with each model release, so check the current one for your model.

#### The maths

$$ \text{cost} = p_{\text{in}}\,T_{\text{in}} + p_{\text{out}}\,(T_{\text{think}} + T_{\text{answer}}) $$

Reasoning tokens are billed as output tokens, so effort settings change cost and latency far more than prompt wording does.

- **cost per request**: What you pay for one answer.

- **input**: Your prompt and context, priced per input token.

- **output price**: Usually several times the input price.

- **hidden reasoning**: Thinking tokens. You pay for them, even though users never see them.

- **the visible answer**: What the user reads.

## In practice

### In practice

#### In practice

- **Start minimal:** state the task, the goal, the constraints and the output format. Run your evaluation set before adding anything.

- **Tune effort, not wording:** try low and medium first. Use the highest settings only when evaluations show a clear gain worth the time and cost.

- **Clean out old instructions:** remove "think step by step", fixed step lists and prefills when moving to a reasoning model, then re-test.

- **Look for contradictions:** have a colleague, or the model itself, list rules that conflict.

- **Few-shot examples still help:** keep a few varied ones, especially for format and tone.

- **Budget for hidden tokens:** set a generous output limit, as reasoning uses part of it. OpenAI suggests reserving at least 25,000 tokens when you start experimenting.

### The answer that sounds right

#### "Always tell the model to think step by step"

It sounds right, since it helped older models. But reasoning models already think, and in one study the instruction added 3% or less while taking up to 80% longer. Give the goal and constraints, and set the effort level instead.

## Say it

### Your team moved to a reasoning model, but kept the old prompt full of step-by-step instructions. What should change?

#### The interviewer pushes further

Follow-up 1 of 3

Should you remove all examples from prompts for reasoning models?

No. Examples still teach format, tone and edge cases well. Keep a few varied ones, and drop worked reasoning chains, as the model reasons on its own.

Follow-up 2 of 3

Users want to see why the model decided something. Do you ask it to write out its reasoning?

Ask for a short explanation in the answer, or use the vendor's reasoning summary feature. Hidden reasoning is not shown in full on most APIs, and writing it all out again costs tokens and time.

Follow-up 3 of 3

The new model got worse on one task after migration. What do you check first?

Old instructions written for the previous model: fixed step lists, prefills, and conflicting rules. Then try a different effort level, and compare both models on the same evaluation set.

Reasoning models already think before answering, so old tricks like 'think step by step' add little. A Wharton study found about 3% or less for reasoning models, at up to 80% more time, against 12 to 14% for some older models. I'd give the model a clear goal, the constraints and the exact output I need, and add step-by-step guidance only where evaluations show failures. I'd control thinking with the reasoning effort setting, starting low or medium, since hidden tokens are billed as output. And I'd remove contradictory rules, which the GPT-5 guide says hurt these models more.

**Key terms and sources**

Why reasoning models want goals, constraints and an output contract rather than steps, what chain-of-thought prompting still adds, reasoning effort settings, and what to stop doing.

#### Sources

- Meincke, Mollick, Mollick and Shapiro, Prompting Science Report 2: The Decreasing Value of Chain of Thought in Prompting (Wharton, 2025)

- OpenAI, Reasoning models guide

- OpenAI, GPT-5 prompting guide (archived cookbook)

- Google Cloud, Prompting guide for thinking models

- Anthropic, Prompting best practices

- Wei et al., Chain-of-Thought Prompting

Explanations are ours, built from these sources. Lab numbers are illustrative unless a lab says otherwise. Many recent papers are preprints, and vendor guides change with each model.
