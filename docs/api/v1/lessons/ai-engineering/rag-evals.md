# RAG Evals: Retrieval, Faithfulness and Relevance

> Why can a correct answer still fail your evaluation?

- Track: AI Engineering › Applied Evals › Lessons
- Type: Concept · 25 min
- Page: https://aimlrounds.com/tracks/ai-engineering/rag-evals/
- Before this: RAG End to End (`ai-engineering/rag-end-to-end`), LLM Judges: Pairwise Preferences and Pass/Fail Checks (`ai-engineering/llm-as-a-judge`)
- Quiz topic: `evals`
- Sources checked: 2026-10-29 · Text last changed: 2026-11-20 · Version: 5ac986b8fa

## Intuition

### The situation

A customer asks how much refund they get for a late order. The right answer needs two facts: 10%, capped at ₹150. The assistant says exactly that, so a colleague says ship it. But the chunk with the cap was never retrieved. The interviewer asks:

> Why can a correct answer still fail your evaluation?

**Running example:** a customer asks "How much refund do I get for a late order?" The reference answer needs two facts from the policy: the refund is 10%, capped at ₹150.

#### Open-ended outputs, many moving parts

An LLM app's answer depends on the prompt, the model version, the retriever, the index, the chunking and the documents. A change to any of them can fix one case and silently break ten others. Without a repeatable evaluation, every change is a guess.

### The idea

Think of a student who answers a comprehension question correctly without reading the passage. They get the mark today. But when the passage changes, they'll confidently give the old answer. So you check that the answer came from the passage, as well as that it's right.

[Figure: Three cases. With good retrieval and a right answer, context recall, faithfulness and correctness are all 1. When the answer adds a voucher, faithfulness falls to 0.67 and correctness stays 1. With noisy retrieval and the right answer, recall and faithfulness are 0.5, and correctness is still 1.]

_Simplified metrics from the lab, on the lesson's refund question._

### Play

**Try to break it.** Start with good retrieval and the right answer. Then add the invented voucher. Then switch to noisy retrieval, and go back to the right answer.

#### "The answer was right, ship it"

Good retrieval: chunks "10% refund for orders over 30 min late", "late refunds capped at ₹150", "wallet refunds are instant". Noisy: "Gold costs ₹149/month", the 10% chunk, "tips go to the partner". Simplified metrics: precision = relevant retrieved chunks ÷ retrieved; recall = needed facts retrieved ÷ needed; faithfulness = answer claims found in the context ÷ answer claims; correctness = needed facts in the answer ÷ needed.

With **good retrieval** and the right answer, everything is 1.00 except precision (0.67: one retrieved chunk was irrelevant, harmless). If the model adds "and a free dessert voucher", correctness stays **1.00** but faithfulness drops to **0.67**: an invented promise that a correctness-only check misses. Now the trap: with **noisy retrieval** (the cap chunk missing), the model still answers "10%, capped at ₹150", so correctness is **1.00**. But context recall is 0.50 and faithfulness **0.50**: half the answer came from the model's memory, not the policy. It's right today; when the cap changes to ₹100, it will confidently say ₹150. If it answers only "10%", faithfulness is 1.00 but correctness falls to 0.50: the metrics together tell you _where_ to fix.

**Now say why:** with noisy retrieval the answer is still correct, so what's actually wrong?

## How it works

### How it works

#### In one breath

"it looked good on five examples" is how LLM apps fail in production. Start a **golden set** early: a few hundred real inputs with the expected answer or behaviour, including hard and adversarial cases. For RAG, score **retrieval** and **generation** separately: **context recall** (did we retrieve everything the answer needs?), **context precision** (how much of what we retrieved is relevant?), **faithfulness** (is every claim in the answer supported by the retrieved context?) and **answer correctness** (does it match the reference?). A correct answer can still be unfaithful, a sign the model is answering from memory, which will fail when memory is wrong. Use **code checks** wherever possible (JSON valid, refund within policy), LLM judges validated against humans for the rest, run the suite on every prompt, model or index change, and watch **online** signals (escalations, thumbs-down, resolution rate). What you'll be able to do after this: design an eval suite for a RAG app, interpret its metrics, and set up regression testing.

#### Component metrics for RAG

| Metric | Question it answers | Points to |
|---|---|---|
| **Context recall** | Were all facts the answer needs retrieved? | retriever, chunking, query |
| **Context precision** | How much of the retrieved context is relevant (and ranked first)? | ranking, k, re-ranker |
| **Faithfulness** | Is every claim in the answer supported by the context? | generator, prompt (hallucination) |
| **Answer relevance / correctness** | Does it answer the question, and match the reference? | whole pipeline |

RAGAS (Es et al. 2024) computes these with an LLM: it splits answers into claims and checks each against the context. Retrieval metrics can also be computed exactly from labelled relevant chunks (recall@k, MRR; retrieval lesson).

## In practice

### In practice

#### Evaluating a RAG pipeline, step by step

1. **Build a retrieval test set:** for each query, label the chunks that answer it. With no real queries yet, generate them from chunks: pick a chunk, have an LLM write a question it answers, then harder ones that paraphrase away the chunk's words or need two chunks. Filter out questions that are trivial or that many chunks answer equally.

2. **Measure retrieval first:** recall@k (did the needed chunks reach the top k), then MRR or NDCG@k for ranking (Ranking Metrics). If retrieval misses, no prompt can fix the answer.

3. **Treat chunking as a variable:** grid-search chunk size, overlap and boundaries against retrieval recall on the same test set.

4. **Then generation:** faithfulness (each claim supported by the retrieved context) and relevance (it answers the question), scored by judges you've validated against human labels.

5. **Diagnose by splitting:** right chunks and a wrong answer is a generation problem; wrong chunks is a retrieval problem. Error analysis on RAG traces usually finds both.

Building the golden set, CI gates and production monitoring work the same way for every app: see Evals in CI and Online Evals.

**Retrieval and faithfulness can move separately.** Across matched setups in a 450-setup study, the two were essentially unrelated (r = −0.01), and different components drove each. Citations need care too: Wallat et al. found up to 57% of citations weren't what the model truly relied on. So score both, and see Grounded Answers for how to test citations.

#### Evaluate each component, on real cases, on every change

Separate retrieval metrics from generation metrics so failures point to their cause, check faithfulness as well as correctness, and make the golden set a regression test that grows with every bug.

### The answer that sounds right

#### "We tested it on a few prompts"

It sounds right, since the answers looked fine. But a change to any part of the pipeline can fix one case and silently break ten others. You need a versioned golden set, run on every prompt, model or index change. And faithful answers can still be unhelpful or incomplete, so check relevance and read the complaints too.

## Say it

### Why can a correct answer still fail your evaluation?

#### The interviewer pushes further

Follow-up 1 of 3

Faithfulness is high but users complain. What's missing?

Faithful answers can still be unhelpful or incomplete: check answer relevance, context recall (maybe the needed facts were never retrieved), tone and format, and read the complaints.

Follow-up 2 of 3

How many examples does the golden set need?

Start with 50–100 to catch obvious regressions, grow to several hundred for decisions; for ±3-point precision on a rate you need around 1,000.

Follow-up 3 of 3

Can you trust an LLM judge for faithfulness?

After validating it against human labels on your data, with a different model family from the generator, and with claim-level checks rather than one overall score.

#### The 30-second answer

I'd build a golden set of a few hundred real questions with reference answers and expected behaviours, including refusals and escalations, and grow it with every production failure. For RAG I evaluate retrieval and generation separately: context recall and precision, faithfulness of each claim to the retrieved context, and answer correctness, because a correct but unfaithful answer means the model is relying on memory. I use code checks wherever I can, LLM judges validated against human labels for the rest, run the suite in CI on every prompt, model or index change, and monitor online signals like escalations, thumbs-down and resolution rate.

**Go further**

#### What not to say

- "We tested it on a few prompts." Use a versioned golden set.

- "The answer was correct, so retrieval is fine." Check faithfulness and context recall.

**Key terms and sources**

How to measure whether an LLM application works: building a golden set, evaluating retrieval and generation separately (context precision and recall, faithfulness, answer correctness), code checks vs LLM judges, regression testing every change, and online signals in production · built from Es et al. (RAGAS, EACL 2024), Saad-Falcon et al. (ARES, NAACL 2024), Zheng et al. (LLM-as-a-Judge, NeurIPS 2023), Liang et al. (HELM, 2022), Shankar et al. (Who Validates the Validators?, UIST 2024) and the OpenAI and Anthropic evaluation guides · checked 29 Oct 2026

#### Sources

1. S. Es et al., "RAGAS: Automated Evaluation of Retrieval Augmented Generation", EACL 2024 (demo), [arXiv:2309.15217](https://arxiv.org/abs/2309.15217).

2. J. Saad-Falcon et al., "ARES: An Automated Evaluation Framework for Retrieval-Augmented Generation Systems", NAACL 2024, [arXiv:2311.09476](https://arxiv.org/abs/2311.09476).

3. L. Zheng et al., "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena", NeurIPS 2023, [arXiv:2306.05685](https://arxiv.org/abs/2306.05685).

4. S. Shankar et al., "Who Validates the Validators? Aligning LLM-Assisted Evaluation of LLM Outputs with Human Preferences", UIST 2024, [arXiv:2404.12272](https://arxiv.org/abs/2404.12272).

5. P. Liang et al., "Holistic Evaluation of Language Models" (HELM), 2022, [arXiv:2211.09110](https://arxiv.org/abs/2211.09110); OpenAI and Anthropic evaluation guides.

6. I. Levy, S. Shlomov & L. Choshen, "Retrieval Augmented Generation Compositionality", 2026, [arXiv:2610.29722](https://arxiv.org/abs/2610.29722); J. Wallat et al., "Correctness is not Faithfulness in RAG Attributions", 2024, [arXiv:2412.18004](https://arxiv.org/abs/2412.18004).
