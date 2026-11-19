# Prompt Engineering Patterns

> How should a production prompt be structured, ordered and tested?

- Track: AI Engineering › Prompt engineering › Lessons
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/ai-engineering/prompt-engineering-patterns/
- Before this: In-Context Learning and Chain-of-Thought (`fundamentals/in-context-learning-and-cot`)
- Quiz topic: `prompt`

## Intuition

### The situation

The team writes the support assistant's system prompt, and a colleague's first draft is "Be a helpful support bot". The answers vary between requests, and again when the model version changes. The interviewer asks:

> How should a production prompt be structured, ordered and tested?

**Running example:** the team writes the support assistant's system prompt: friendly tone, policy-bound refunds, JSON output for the app, and escalation when unsure.

#### "Be a helpful support bot" isn't a spec

A one-line prompt leaves the model to guess the tone, the rules, which facts it may use, the output shape and what to do in edge cases. Its guesses vary between requests and between model versions. Every behaviour you care about should be stated, shown in an example, or enforced in code.

### The idea

Think of briefing a capable new hire. "Be helpful" leaves them guessing. A good brief gives their role, the rules, the policy file kept separate from the customer's note, a few examples and the exact format wanted. Then you check their work against a fixed set of cases.

[Figure: A production prompt. Role, rules, policy, examples and format come first and stay the same, so they can be cached. Order data and the customer's message come last and change on every request.]

_The order from the lab, with the full prompt at about 1,900 tokens._

### Play

**Try to break it.** Untick everything to see the naive prompt. Then add the parts back one at a time, watching the prompt tokens and the cacheable prefix.

#### Assemble the support prompt

The customer's message is always included, last. Token counts are approximate; the policy is abbreviated in the display.

Untick everything and you have the naive prompt: just the customer's message, and the model must guess everything else. The full prompt is about **1,900 tokens**, and because the stable parts (role, rules, policy, examples, format) come first and only the order data and message change, **97.6%** of it is a cacheable prefix. Put the order data or a timestamp at the top and that saving disappears. The other trap is tweaking wording until one example looks right: formatting choices alone can move accuracy by tens of points (Sclar et al. 2024), so every prompt change should be run against a fixed test set before shipping.

**Now say why:** why does the order of the parts change what you pay?

## How it works

### How it works

#### In one breath

A production prompt is a small program with parts: a **role** and goal, explicit **rules** (what to do, what never to do, what to do when unsure), **context** wrapped in clear delimiters such as XML tags, a few **examples** of ideal input → output, a precise **output format**, and the user's message last. Order parts from most to least stable so the shared prefix can be cached. Models are surprisingly sensitive to wording and formatting (Sclar et al. measured up to 76 accuracy points of difference from formatting alone on LLaMA-2-13B), so prompts must be **versioned and evaluated** on a test set like any code change, not tweaked by feel. Split complex tasks into **chained** prompts, and for reasoning let the model think first.What you'll be able to do after this: write a well-structured production prompt, order it for caching, and set up prompt evaluation.

#### The parts of a production prompt

- **Role and goal:** who the model is and what success looks like for this product.

- **Rules:** positive instructions ("only promise refunds in the policy"), hard limits ("never ask for card numbers") and a fallback ("if unsure, say so and offer an agent"). Explain _why_ for non-obvious rules, as models generalise from the reason. Say what to do, not only what to avoid, and check rules don't contradict each other: OpenAI's GPT-5 guide says contradictions can hurt newer models more.

- **Delimited context:** wrap documents, order data and user text in tags (`<policy>`, `<customer>`) so the model knows what's instruction and what's data, which also helps against prompt injection.

- **Examples:** 3–5 diverse input → ideal output pairs, covering edge cases, as Anthropic suggests; they teach format and tone faster than descriptions. Too many similar ones can make the model copy them too closely.

- **Long documents first, question last:** with long inputs, put the documents at the top and the question at the end. Anthropic reports this can improve answers by up to 30% on complex, multi-document inputs.

- **Output format:** an exact schema; enforce it with structured output.

- **Reasoning and chaining:** for multi-step tasks on models that don't reason by default, ask for reasoning before the answer, or split into a chain (classify → retrieve → draft → check). Reasoning models already think first, so give them the goal and constraints instead: see Prompting Reasoning Models.

**Start minimal.** Anthropic and OpenAI both suggest starting with a short, clear prompt on the best model, then adding instructions only for failures you actually see in testing. Prompts that grow by habit get long, slow and contradictory. See System Prompts with Many Rules.

## In practice

### In practice

#### Prompts as code

- **Version and review** prompts in the repository, with the model version pinned; a prompt is tied to the model it was tested on.

- **Evaluate:** a golden set of 100–500 real inputs with expected behaviour, scored by code checks and an LLM judge; run it on every change (Evaluating LLM Apps).

- **Optimise automatically:** DSPy compiles prompts and few-shot examples against a metric; APE had LLMs propose and select instructions, and GEPA rewrites prompts by reflecting on failures. Useful once you have a metric and data: see Automatic Prompt Optimisation.

- **Know when to stop:** if the prompt keeps growing to cover cases, consider retrieval for knowledge or fine-tuning for consistent behaviour (how to choose).

#### Specify, show, delimit, then measure

Good prompts state the rules, show examples, separate instructions from data and fix the output shape; because models are sensitive to small changes, every change is tested on a fixed evaluation set.

### The answer that sounds right

#### "Prompt engineering is just trying phrasings"

It sounds right, since you do spend time on wording. But it's specification plus evaluation. Tweaking until one example looks right is the trap, because formatting choices alone can move accuracy by tens of points. So run every change against a fixed test set. And don't put today's date at the top, because it breaks prefix caching.

## Say it

### How should a production prompt be structured, ordered and tested?

#### The interviewer pushes further

Follow-up 1 of 3

Why use XML tags or delimiters?

They separate instructions from data, make it easy to reference sections ("using the <policy>…"), and reduce the chance that text inside a document is followed as an instruction.

Follow-up 2 of 3

A new model version broke your prompt. Why, and how do you prevent it?

Prompts are tuned to a model's quirks; pin model versions, run the golden set on any upgrade, and fix regressions before switching.

Follow-up 3 of 3

Few-shot examples or more instructions?

Examples for format, tone and edge-case behaviour; instructions for hard rules. Use diverse examples so the model doesn't copy one too closely.

#### The 30-second answer

I structure prompts in parts: a role and goal, explicit rules including what to do when unsure, context wrapped in clear delimiters like XML tags, a few diverse examples, an exact output format, and the user's message last. Stable parts go first so the prefix can be cached. Models are sensitive to small wording and format changes, so I treat prompts as code: versioned with the model they target and evaluated on a golden set with code checks and an LLM judge before every change. Complex tasks get split into chained prompts, and when a prompt keeps growing I consider RAG or fine-tuning instead.

**Go further**

#### What not to say

- "Prompt engineering is just trying phrasings." It's specification plus evaluation.

- "Put today's date at the top." It breaks prefix caching.

**Key terms and sources**

How production prompts are structured: system role, explicit rules, delimited context (XML tags), few-shot examples, output format, chain-of-thought and prompt chaining; ordering for prompt caching; why small formatting changes swing accuracy; and treating prompts like code with versioning and evaluation (including DSPy-style optimisation) · built from the Anthropic and OpenAI prompt engineering guides, Sclar et al. (ICLR 2024), Brown et al. (GPT-3, 2020), Wei et al. (Chain-of-Thought, 2022), Khattab et al. (DSPy, ICLR 2024) and Zhou et al. (APE, ICLR 2023) · checked 29 Oct 2026

#### Sources

1. Anthropic, "Prompt engineering overview" and related guides (XML tags, examples, chaining); OpenAI, "Prompt engineering" guide.

2. M. Sclar et al., "Quantifying Language Models' Sensitivity to Spurious Features in Prompt Design", ICLR 2024, arXiv:2310.11324.

3. O. Khattab et al., "DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines", ICLR 2024, arXiv:2310.03714; Y. Zhou et al., "Large Language Models Are Human-Level Prompt Engineers" (APE), ICLR 2023, arXiv:2211.01910.

4. T. Brown et al. (GPT-3), NeurIPS 2020, arXiv:2005.14165; J. Wei et al. (Chain-of-Thought), NeurIPS 2022, arXiv:2201.11903.

5. Anthropic, Prompting best practices (examples, long-context layout, explaining rules), checked 7 Nov 2026; OpenAI, GPT-5 prompting guide (contradictory instructions).
