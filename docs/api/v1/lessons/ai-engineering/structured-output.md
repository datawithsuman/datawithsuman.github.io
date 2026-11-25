# Structured Output and Constrained Decoding

> Why does 'return JSON' fail, and how do grammars fix it?

- Track: AI Engineering › Prompt engineering › Lessons
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/ai-engineering/structured-output/
- Before this: Prompt Engineering Patterns (`ai-engineering/prompt-engineering-patterns`), Decoding: Temperature, Top-k, Top-p and Min-p (`fundamentals/decoding-and-sampling`)
- Quiz topic: `prompt`
- Sources checked: 2026-10-29 · Text last changed: 2026-11-20 · Version: 8c4a6070c6

## Intuition

### The situation

The support app needs every reply as JSON, so the backend can issue refunds automatically. A colleague adds "return JSON" to the prompt. Now and then, the reply starts with "Here's the JSON:" or writes forty-two instead of 42, and the pipeline crashes. The interviewer asks:

> Why does "return JSON" fail, and how do grammars fix it?

**Running example:** the support app needs every reply as JSON with fields like `reply`, `refund_inr`, `reason_code`, `escalate`, so the backend can issue refunds automatically.

#### One broken brace breaks the pipeline

Downstream code needs exact keys and types. Free-text generation occasionally adds "Here's the JSON:", forgets a closing brace, invents a field or writes "forty-two" instead of 42. Each failure means a retry (latency and cost) or a crash.

### The idea

Think of asking someone to write their details neatly on blank paper, against giving them a form with fixed boxes and dropdowns. The form can't come back in the wrong shape. They can still enter the wrong number, though, so you check the values as well.

[Figure: Three levels. Prompting guarantees nothing: a 12-field object is valid 88.6 percent of the time at 1 percent error per field. JSON mode guarantees valid JSON, but not your schema. Schema-constrained decoding always matches the structure and types.]

_The lab's example has 12 fields, each with a 1% chance of a formatting slip._

### Play

**Try to break it.** Use prompted JSON, and raise the fields in the schema and the chance of a slip. Add retries. Then switch to schema-constrained decoding.

#### "Return JSON, please"

Simple model: each field independently malformed with the given probability; a retry is a fresh independent attempt. Real error rates depend on the model and schema; measure yours.

Prompted JSON with **12 fields** and a 1% chance per field of a formatting slip is valid only **88.6%** of the time; at 30 fields, **74.0%**. Retries rescue it (two retries reach 99.85%) but cost 13% more calls on average and add latency to the unlucky requests. **Constrained decoding** is valid **100%** of the time in a single call. The remaining trap is semantic: the schema can't know that a ₹420 refund breaks the "10%, capped at ₹150" rule, so validate values (ranges, enums, cross-field rules) in code and treat violations like errors.

**Now say why:** retries get prompted JSON to 99.85%, so what's left that constrained decoding still can't fix?

## How it works

### How it works

#### In one breath

Apps need fields, not prose: `{"refund_inr": 42, "escalate": false}`. Asking nicely for JSON mostly works, but every field is a chance for a stray comment, a missing quote or a wrong key, and the chances multiply: at 1% per field, a 12-field object is valid only 88.6% of the time. **Constrained decoding** fixes the syntax: the schema is compiled into a grammar, and at every step the decoder **masks out** tokens that would break it, so output always parses (OpenAI reported 100% schema adherence with strict Structured Outputs, versus under 40% for gpt-4-0613 with prompting alone on its complex-schema eval). It doesn't fix _content_: a valid number can still be the wrong refund, so you still validate values in code. Forcing a format can also hurt reasoning, so let the model reason first (or in a `reasoning` field placed before the answer fields). What you'll be able to do after this: choose between prompting, JSON mode and constrained decoding, design schemas, and combine them with validation.

#### Three levels of enforcement

| Level | How | Guarantee |
|---|---|---|
| **Prompting** | describe the format, show examples, parse and validate | none; failures need retries |
| **JSON mode** | the API/engine guarantees syntactically valid JSON | valid JSON, but not your schema |
| **Schema-constrained decoding** | a JSON Schema (or regex/grammar) is compiled to a state machine; at each step tokens that can't continue a valid output get probability 0 (Outlines, XGrammar, llguidance; OpenAI "strict", vLLM and SGLang guided decoding) | always matches the schema's structure and types |

Masking happens on the logits before sampling, so it adds little overhead with modern grammar engines. It is the same mechanism used for function/tool-call arguments (Agentic AI track).

## In practice

### In practice

#### Schema design and the reasoning trade-off

- **Design schemas for the model:** descriptive field names, enums for categories, required fields, few optional ones, flat over deeply nested; put free-text `reasoning` _before_ decision fields so the model "thinks" before committing.

- **Format restrictions and accuracy are disputed:** Tam et al. (2024) found strict format constraints lowered performance on reasoning tasks. A rerun by the Outlines team (dottxt) used the same prompt for both and found structured output matched or slightly beat free text, for example 0.78 against 0.77 on GSM8K with Llama-3-8B, and argued the gap came from prompt differences and answer parsing. So test both on your own task. Either way, a reasoning field before the decision fields, or a second extraction call, lets the model think first.

- **Field descriptions are instructions too:** a 2026 study moved category definitions between the system prompt and the schema's field descriptions. When the two disagreed, accuracy fell by 5 to 45 points depending on the model, with Claude Haiku 4.5 dropping from 52.5% to 7.1%. A required reasoning field placed before the label added 15 to 24 points where there was room to improve. Keep one source of truth, and generate both the prompt and the schema from it.

- **Validate in code** with Pydantic / Zod models generated from the same schema; log and alert on validation failures.

- **Version schemas** and keep backward compatibility, since prompts, examples and downstream code depend on them.

#### Enforce the shape in the decoder, check the values in code

Constrained decoding makes the output always parse by masking invalid tokens; correctness of the values still needs validation, and reasoning should happen before the model is boxed into a format.

### The answer that sounds right

#### "Constrained output means correct output"

It sounds right, since the output now always parses. But it means parseable, not correct. The schema can't know that a ₹420 refund breaks the "10%, capped at ₹150" rule. That's a content problem: validate values in code, and compute amounts with a tool. JSON mode doesn't guarantee your schema either, only the syntax.

## Say it

### Why does "return JSON" fail, and how do grammars fix it?

#### The interviewer pushes further

Follow-up 1 of 3

How does constrained decoding work technically?

The schema or grammar becomes a finite-state machine or pushdown automaton over tokens; at each step the engine computes which tokens keep the output valid and sets the others' logits to −∞ before sampling.

Follow-up 2 of 3

Does it slow generation down?

Modern engines (XGrammar, llguidance) precompute token masks and add little overhead; very complex grammars can still cost some latency.

Follow-up 3 of 3

The JSON is valid but the refund amount is often wrong. Next step?

That's a content problem: improve retrieval of the policy, compute amounts with a tool instead of the model, and add value checks and evals.

#### The 30-second answer

There are three levels: prompting for JSON, which fails occasionally and the failures multiply with schema size; JSON mode, which guarantees valid JSON but not your schema; and schema-constrained decoding, which compiles the schema into a grammar and masks invalid tokens at each step so the output always matches the structure. I'd use constrained decoding, OpenAI strict mode or guided decoding in vLLM, then validate the values with Pydantic, because a valid field can still hold a wrong value. And since tight format constraints can hurt reasoning, I'd put a reasoning field before the decision fields or do a separate extraction step.

**Go further**

#### What not to say

- "JSON mode guarantees my schema." Only syntax.

- "Constrained output means correct output." It means parseable output.

**Key terms and sources**

Getting LLMs to return machine-readable output reliably: prompting for JSON, JSON mode, schema-constrained decoding (how grammars mask invalid tokens), validation and retries, schema design, and the cost of format restrictions on reasoning · built from OpenAI (Introducing Structured Outputs, 2024), Willard & Louf (Outlines, 2023), Dong et al. (XGrammar, 2024), Tam et al. (Let Me Speak Freely?, EMNLP 2024), and the vLLM, SGLang and Pydantic documentation · checked 29 Oct 2026

#### Sources

1. OpenAI, "Introducing Structured Outputs in the API", Aug 2024.

2. B. Willard & R. Louf, "Efficient Guided Generation for Large Language Models" (Outlines), 2023, [arXiv:2307.09702](https://arxiv.org/abs/2307.09702); Y. Dong et al., "XGrammar", 2024, [arXiv:2411.15100](https://arxiv.org/abs/2411.15100).

3. Z. R. Tam et al., "Let Me Speak Freely? A Study on the Impact of Format Restrictions on Performance of Large Language Models", EMNLP Industry 2024, [arXiv:2408.02442](https://arxiv.org/abs/2408.02442).

4. vLLM and SGLang structured output / guided decoding documentation; Pydantic documentation.

5. W. Kurt, ["Say What You Mean: A Response to Let Me Speak Freely"](https://blog.dottxt.ai/say-what-you-mean.html), dottxt, 2024; S.-Y. Lin, "Your Prompt Is Not the Only Prompt: How Much Do LLMs Weight Structured-Output Schema Descriptions?", 2026, [arXiv:2608.08254](https://arxiv.org/abs/2608.08254).
