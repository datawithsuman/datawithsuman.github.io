# RAG: Wrong Answer, Where to Look First

> Your chatbot gave a confident, wrong answer. Where do you look first?

- Track: AI Engineering › RAG › Scenarios
- Type: Interview · 8 min
- Page: https://aimlrounds.com/tracks/ai-engineering/rag-wrong-answer/
- Before this: RAG End to End (`ai-engineering/rag-end-to-end`)
- Quiz topic: `rag`

## Intuition

### The situation

You're the ML engineer on a support team. Your chatbot just gave a customer the wrong refund policy, confidently. A colleague wants to rewrite the prompt. The interviewer asks:

> Your chatbot gave a confident, wrong answer. Where do you look first?

#### The situation: a confident, wrong answer

A customer asks about refunds. The bot answers instantly and sounds sure. It is wrong.

The documents the bot searches (made-up policy snippets):

#### What would you check first?

Tap an answer.

### The idea

Think of a parcel that arrives with the wrong item. You don't start by retraining the driver. You check whether the right item ever left the warehouse. That one check tells you which half of the operation to look at.

[Figure: One check: was the right chunk retrieved for this question? If not, look at the retrieval side: chunking, metadata, top-k and reranking. If so, look at the generation side: context packing, then the prompt.]

_A practical debugging order, not a result from the study._

### Play

**Try to break it.** Pick a case, and click each stage to see what the system had at that point. Then show where the answer was lost, and try the other cases.

#### Spot it: where does the right answer disappear?

Pick a case, then click each stage to see what the system had at that point. The right chunk says annual plans get 14 days.

Illustrative. Green = the right chunk. Red = a chunk that points the model the wrong way.

**Now say why:** if the right chunk never reached the model, why can't any prompt fix it?

## How it works

### How it works

#### In one breath

Most people blame the prompt or reach for a bigger model. A better first move is to look at what the system retrieved. One check splits the problem in two, and each side has its own fixes.

#### Why it happens: seven failure points

A study built on three RAG case studies found these seven ways an answer goes wrong. They fall into three zones along the pipeline.

Here, "generation side" includes the step where retrieved chunks are packed into the prompt (FP3). The "how to check" lines are practical suggestions, not results from the study.

#### Diagnose before you fix

Answer the questions for your own failing example. Each answer narrows the problem.

This order is a practical debugging approach. It is not a result from the study.

## In practice

### In practice

#### Fixes, in order

1. 1 ##### Chunking and metadata Chunk size is a trade-off: too small and some questions can't be answered, too long and the answer picks up noise. In one case study, adding the file name and chunk number to the retrieved text helped the model use it. Watch out: changing how you embed means re-indexing every chunk.

2. 2 ##### Top-k and reranking In practice only the top K chunks are used, so the right one has to rank near the top. Reranking reorders the candidates so the chunk with the answer sits first. Watch out: a bigger K adds more noise and more cost.

3. 3 ##### Context size The step that packs chunks into the prompt can drop a good one. In one case study, a larger context (8K vs 4K) gave more accurate answers. Watch out: that was one system, so measure it on yours.

4. 4 ##### The prompt, last Only once the right text reliably reaches the model does the prompt matter: format, level of detail, splitting multi-part questions, and saying "I don't know" when nothing relevant comes back.

#### Mistakes to avoid

Common

- Swapping to a bigger model before looking at retrieval.

- Re-indexing everything without knowing which stage failed.

- Retrieving more chunks without checking for noise and conflicts.

- Launching with no test questions.

✓ Better

- Read the retrieved chunks for the failing question first.

- Fix the stage that lost the answer, then re-test the same question.

- Remove outdated or conflicting documents.

- Keep a small set of real questions with known answers, and keep monitoring after launch.

Debug retrieval before the prompt.

### The answer that sounds right

#### "Rewrite the prompt, or switch to a bigger model"

It sounds right, since the bad text came out of the model. But rewriting the prompt is a guess: if the right text never reached the model, no wording can fix that. A bigger model can't use a chunk it never received, so you'd pay more and keep the bug. Re-indexing every document is just as blind. Look at what retrieval returned first.

## Say it

### Your chatbot gave a confident, wrong answer. Where do you look first?

#### The interviewer pushes further

Follow-up 1 of 4

How would you test a RAG system before launch?

Build a small set of real questions with known answers and the document each answer comes from. Score retrieval (did the right chunk come back?) separately from the final answer, so you know which half failed. The study notes that these systems are hard to validate up front and need continuous calibration, so keep monitoring after launch.

Follow-up 2 of 4

RAG or fine-tuning for company knowledge?

RAG keeps knowledge in documents you can update and control access to. Fine-tuning bakes the data into the model, so you retrain when the data or the base model changes. Many teams start with RAG for changing knowledge. Compare accuracy, latency, cost and robustness for your case.

Follow-up 3 of 4

How do you choose a chunk size?

It's a trade-off: small chunks can miss context a question needs, long chunks add noise. Try a few sizes on your own test questions and compare whether the right chunk is retrieved. Heuristic chunking (paragraphs, punctuation) and semantic chunking are both worth comparing.

Follow-up 4 of 4

What if the answer isn't in the documents at all?

That's failure point 1. In the happy case the system says it doesn't know. The risk is questions that are related to the content but have no answer, which can fool the system into answering anyway. Include such questions in your tests and make abstaining an expected behavior.

#### The 30-second answer

I wouldn't touch the prompt or the model first. I'd look at the chunks retrieved for that exact question, because one check splits the problem in two. If the right chunk never came back, it's the retrieval side: chunking, metadata, top-k and reranking. If it came back and the answer is still wrong, it's the generation side: the step that packs chunks into the prompt, or the model not extracting the answer. I'd fix the stage that lost the answer, re-test the same question, and keep a small set of real questions with known answers, so it stays fixed.

**Key terms and sources**

Sources checked 5 Nov 2026

#### Sources

–
