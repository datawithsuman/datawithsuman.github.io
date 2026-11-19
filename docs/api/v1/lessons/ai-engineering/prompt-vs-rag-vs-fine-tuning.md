# Prompt vs RAG vs Fine-Tuning: How to Choose

> Knowledge or behaviour: which tool fixes which gap?

- Track: AI Engineering › Prompt engineering › Lessons
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/ai-engineering/prompt-vs-rag-vs-fine-tuning/
- Before this: Prompt Engineering Patterns (`ai-engineering/prompt-engineering-patterns`), LoRA and QLoRA: Parameter-Efficient Fine-Tuning (`fundamentals/lora-and-qlora`)
- Quiz topic: `prompt`

## Intuition

### The situation

Three requests land on the team: answer from our latest refund policy, always reply in our brand voice and JSON format, and classify tickets into 40 categories, 2 million times a month. A colleague says to fine-tune for all of them. The interviewer asks:

> Knowledge or behaviour: which tool fixes which gap?

**Running example:** three requests land on the team: "answer from our latest refund policy", "always reply in our brand voice and JSON format", and "classify tickets into 40 categories, 2 million times a month".

#### Three tools, often confused

"Fine-tune it on our documents" is the most common wrong first instinct: it's slow to update, hard to cite and teaches facts poorly. "Just add it to the prompt" stops scaling once the prompt is thousands of tokens on millions of calls. Each tool changes a different thing.

### The idea

Think of a new hire again. Instructions on the day are the prompt. Handing them the current manual to look things up in is RAG. Months of drilling until it's habit is fine-tuning. You wouldn't drill someone on a manual that changes every few weeks.

[Figure: Three requests. The latest refund policy is changing knowledge, so use RAG. Brand voice and JSON format is behaviour, so start with a prompt, then LoRA. A classifier running 2 million times a month is a narrow skill at volume, so fine-tune a small model.]

_The lesson's three requests. Most real assistants use all three tools._

### Play

**Try to break it.** Describe each of the three requests with the buttons, and read the recommendation. Then change one thing at a time: how often it changes, the examples you have and the volume.

#### Describe the requirement

A simplified rule set summarising the guidance above; real decisions also weigh latency, privacy and team skills.

The refund-policy request is **missing, changing knowledge → RAG**: re-index when the policy changes, cite the clause. The brand voice and JSON request is **style/format**: start with a prompt and few-shot examples; with thousands of good examples, **LoRA fine-tuning** makes it consistent and shortens the prompt. The 2-million-a-month ticket classifier is a **narrow skill at high volume**: label data (possibly with a big model), **fine-tune a small model** and distil, cutting cost per call dramatically. The trap is picking one tool for everything; most real assistants use all three.

**Now say why:** why is fine-tuning a poor way to teach the refund policy?

## How it works

### How it works

#### In one breath

Ask **what is missing**. If the model lacks **knowledge** (your policies, products, latest data) → **RAG**: it's updatable, citable, and beats fine-tuning for injecting facts (Ovadia et al. found retrieval consistently outperformed unsupervised fine-tuning on knowledge tasks). If it lacks **behaviour** (tone, format, a narrow skill done consistently) → **prompting** first, then **fine-tuning** once you have hundreds to thousands of good examples, or when long prompts become too slow or costly at volume. They combine: many production systems fine-tune a small model to follow the format and use RAG for the facts. The standard order is: prompt a capable model → add RAG → evaluate → fine-tune (and distil) only where data and volume justify it.What you'll be able to do after this: pick the right approach for a requirement and defend the choice with evidence and cost.

#### What each approach changes

| | Prompting | RAG | Fine-tuning |
|---|---|---|---|
| **Changes** | instructions in context | knowledge in context, per query | the model's weights (behaviour) |
| **Best for** | rules, format, quick iteration | facts that change; citations; large corpora | consistent style/format, narrow skills, shorter prompts, small models |
| **Data needed** | a few examples | documents | hundreds to thousands of high-quality examples |
| **Update speed** | instant | re-index (minutes) | retrain and redeploy |
| **Weak at** | long prompts cost tokens on every call | retrieval misses; style | new facts (and can increase hallucination), freshness, citations |

Gekhman et al. (2024) found that fine-tuning on facts the model didn't already know was learned slowly and increased hallucination. RAFT (Zhang et al. 2024) shows the combination: fine-tune the model to _use_ retrieved documents well, including ignoring distractors.

## In practice

### In practice

#### The usual escalation path

1. **Prompt a strong model** with clear rules and examples; build an evaluation set from day one.

2. **Add RAG** when answers need your data; measure retrieval recall and faithfulness separately.

3. **Optimise the prompt and pipeline** (re-ranking, structured output, routing) against the eval set. Automatic optimisers can help here: GEPA beat GRPO, a fine-tuning method, by about 10% on average with up to 35 times fewer runs, though its authors expect fine-tuning to win when data is plentiful. See Automatic Prompt Optimisation.

4. **Fine-tune** when you have data and a clear behaviour gap, or when volume makes long prompts and big models too expensive; often distil a big model's outputs into a smaller one.

5. **Keep evaluating:** every step must beat the previous one on the same eval set.

#### Knowledge goes in context, behaviour goes in weights

Use retrieval for what the model must know and fine-tuning for how it must behave, start with prompting, and let evaluation results and volume decide when to escalate.

### The answer that sounds right

#### "Fine-tuning is how you teach the model your data"

It sounds right, since training is how a model learns. But it's slow to update and hard to cite, and fine-tuning on facts the model didn't already know was learned slowly and increased hallucination. Use RAG for facts. RAG won't fix tone and format either: that's prompting or fine-tuning.

## Say it

### Knowledge or behaviour: which tool fixes which gap?

#### The interviewer pushes further

Follow-up 1 of 3

The business wants the model to "know" 5,000 product manuals. Fine-tune?

No: RAG over the manuals, with citations and re-indexing on updates; fine-tuning would learn the facts poorly, go stale, and can increase hallucination.

Follow-up 2 of 3

When does fine-tuning save money?

At high volume, when a fine-tuned small model replaces a large model with a long prompt; the training cost is repaid by cheaper calls.

Follow-up 3 of 3

How many examples for fine-tuning?

Format and style can improve with a few hundred high-quality examples; harder skills need thousands; quality and diversity matter more than count.

#### The 30-second answer

I start by asking what's missing. If it's knowledge, especially changing or citable knowledge, I use RAG: it's updatable and studies show it beats fine-tuning for injecting facts. If it's behaviour, tone, format or a narrow skill, I start with prompting and examples, and fine-tune with LoRA once I have enough good examples or when long prompts get too costly at high volume. They combine well: a fine-tuned small model for format plus RAG for facts. I escalate in order, prompt, then RAG, then fine-tuning and distillation, and every step has to win on the same evaluation set.

**Go further**

#### What not to say

- "Fine-tuning is how you teach the model your data." Use RAG for facts.

- "RAG fixes tone and format." That's prompting or fine-tuning.

**Key terms and sources**

A practical decision framework for adapting an LLM to a product: what each approach changes (instructions, knowledge, behaviour), the evidence that fine-tuning is a poor way to add knowledge, how they combine (RAG + fine-tuned model, RAFT), the usual order of escalation, and the costs that decide it at scale · built from Ovadia et al. (Fine-Tuning or Retrieval?, EMNLP 2024), Gekhman et al. (EMNLP 2024), Zhang et al. (RAFT, 2024), Lewis et al. (RAG, 2020), Hu et al. (LoRA, 2022) and the OpenAI and Anthropic model-optimisation guides · checked 29 Oct 2026

#### Sources

1. O. Ovadia et al., "Fine-Tuning or Retrieval? Comparing Knowledge Injection in LLMs", EMNLP 2024, arXiv:2312.05934.

2. Z. Gekhman et al., "Does Fine-Tuning LLMs on New Knowledge Encourage Hallucinations?", EMNLP 2024, arXiv:2405.05904.

3. T. Zhang et al., "RAFT: Adapting Language Model to Domain Specific RAG", 2024, arXiv:2403.10131.

4. P. Lewis et al. (RAG), NeurIPS 2020, arXiv:2005.11401; E. Hu et al. (LoRA), ICLR 2022, arXiv:2106.09685.

5. OpenAI, "Optimizing LLM accuracy" guide; Anthropic, model customisation and prompt engineering documentation.

6. L. A. Agrawal et al., "GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning", 2025, arXiv:2507.19457.
