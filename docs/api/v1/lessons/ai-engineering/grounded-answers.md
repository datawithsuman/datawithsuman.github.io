# Grounded Answers: Citations, Conflicts and Saying No

> The right chunk was retrieved, but the answer is still wrong. Why, and how do you make answers trustworthy?

- Track: AI Engineering › RAG › Lessons
- Type: Concept · 18 min
- Page: https://aimlrounds.com/tracks/ai-engineering/grounded-answers/
- Before this: RAG End to End (`ai-engineering/rag-end-to-end`)
- Quiz topic: `rag`

## Intuition

### The situation

Your assistant retrieves the right policy, but its answer gets an amount wrong. It also cites a document that doesn't say what it claims, and it answers confidently when no document covers the question. The interviewer asks:

> The right chunk was retrieved, but the answer is still wrong. Why, and how do you make answers trustworthy?

#### Why it matters

Teams often stop once retrieval scores look good. But a 2026 study found a clear **retrieval-generation gap**: when retrieval found 83.5% of the right entities, the model's answers used only 47.9%. Better retrieval alone won't close that gap. It's also where users lose trust, since a confident wrong answer with a citation looks like a right one.

### The idea

Think of a student with a stack of notes in an exam. They read the top pages closely and skim the rest. They might write what they already believe, then add a reference that seems to fit. And they'd rather write something than leave a blank. So you shorten the stack, check the references, and give credit for saying "I don't know".

[Figure: Three checks. Order context so it gets used. Test that citations are real. Allow and test saying no.]

_Retrieved doesn't mean used._

### Play

**Try to break it.** Move the right chunk down the ranks. Then raise the threshold.

#### Rank and threshold

Rank figures are measured, from Table 7 of Chen et al. (2026), for one GraphRAG setup with a single model and on one medical dataset. The samples are small, about 20 to 50 per row, which is why rank 3 is above rank 2. The threshold half is illustrative, with invented bell curves: answerable scores centre on +1.2, and unanswerable on −1.2.

Move the right chunk from **rank 1** to **ranks 6 to 10**. Use falls from 97.9% to 43.5%, even though the chunk was in the context the whole time. At ranks 51 and beyond, it wasn't used once. So retrieval metrics can look fine while answers fail. Now move the **threshold**. At 0, 11.5% of answerable questions get refused, and 11.5% of unanswerable ones get answered. At 1.0, invented answers fall to 1.4%, but 42.1% of good questions get refused. In a support bot, a wrong refund promise usually costs more than an escalation, so you might accept that. In a search tool, perhaps not.

**Now say why:** why can a citation be correct, yet not faithful?

## How it works

### How it works

#### In one breath

Retrieval is only half the job, because the model has to use what it's given. Models favour early text: in one study, an answer at rank 1 was used 98% of the time, against 44% at ranks 6 to 10. So send fewer, well-ordered chunks. **Citations** can mislead, as a model may answer from memory, then cite a document that happens to agree. When documents **conflict**, prefer the newest authoritative source, and say so. And when the answer isn't there, the system should **say no**, which you have to design and test for.

#### From context to a trustworthy answer

##### Why evidence gets missed

- **Position:** extraction fell from 85.5% in the first tenth of the context to about 19% around the middle, and to almost nothing at the end, in one test with long graph context.

- **Too much context:** the same study saw that adding more retrieved text often didn't improve answers, while costing more tokens.

- **Question wording:** a singular question can make a model give one answer, even when several are valid.

This fits earlier findings that models lose information in the middle of long contexts. So re-rank, send fewer chunks, and place the best first.

##### Citations that aren't what they seem

| Check | Question | How to test |
|---|---|---|
| **Citation correctness** | Does the cited text support the claim? | An NLI model or a judge, claim by claim |
| **Citation faithfulness** | Did the model really use that text? | Change or remove the document, and see if the answer changes |

Wallat et al. found that up to 57% of citations lacked faithfulness: the model already believed the answer, and then attached a source. That's called post-rationalisation, and a correctness check can't see it.

##### Conflicting and bad documents

- **Stale versions:** remove superseded documents at ingest, and store dates and versions.

- **Real disagreements:** show both, with their sources and dates, rather than picking silently.

- **Bad knowledge:** RAGStress, a 2026 benchmark, found that a clean knowledge base can hide big differences between models, and that a model's accuracy with no retrieval didn't predict how well it copes with corrupted documents. So test with damaged documents too.

##### Saying no

CRAG found that simple RAG raised accuracy from at most 34% to 44%, and that even leading industry systems answered only 63% of questions without hallucination. So plan for failure: tell the model it may say the answer isn't there, check whether retrieval found anything relevant, and test on questions with no answer. Barnett et al. warn that related but unanswerable questions are the ones most likely to fool a system.

#### The maths

$$ {\text{missed answers}} = {P(s < t \mid \text{answerable})}, \qquad {\text{invented answers}} = {P(s \ge t \mid \text{not answerable})} $$

A simple way to frame the trade-off, as with any classifier. Retrieval scores aren’t always comparable across queries, so calibrate this on your own data.

- **wrongly saying no**: Questions you could have answered, but refused.

- **the threshold**: s is a retrieval or support score. Raising t refuses more.

- **wrongly answering**: Questions with no answer in the documents, answered anyway.

- **the other side**: Lowering t answers more of these. A better score helps both, while moving t only trades one for the other.

## In practice

### In practice

#### In practice

- **Number your chunks:** ask the model to cite chunk IDs per claim, then check that each ID exists and supports the claim.

- **Verify by code where you can:** amounts, dates and IDs can be checked against the source text.

- **Test no-answer questions:** include them in your golden set, and track how often they're refused.

- **Change the document:** edit a fact in a retrieved chunk, and see whether the answer changes. If not, it's answering from memory.

- **Don't overdo checks:** in the 450-setup study, some quality gates removed supporting evidence, including 14 of 15 chunks in one case, so test them too.

### The answer that sounds right

#### "It cites a source, so we can trust it"

It sounds right, since a reader can check the citation. But models can answer from memory, then attach a source that agrees, and one study found up to 57% of citations were like this. If the source later changes, the answer won't. Change the document and see whether the answer changes.

## Say it

### The right chunk was retrieved, but the answer is still wrong. Why, and how do you make answers trustworthy?

#### The interviewer pushes further

Follow-up 1 of 3

How would you test whether a citation is real?

Swap or remove the cited document and re-run. If the answer stays the same, the model wasn't relying on it. Also check that the text supports the claim, with an NLI model or judge, and validate that the cited ID exists.

Follow-up 2 of 3

Two retrieved policies disagree. What should the system do?

Prefer the current authoritative one if metadata can tell you, and fix the index by removing old versions. If they really disagree, show both with sources and dates, or escalate, instead of silently picking one.

Follow-up 3 of 3

Why not just send 20 chunks, to be safe?

More chunks can add noise and cost without helping, because the model uses later ones less. Anthropic did find 20 worked best among 5, 10 and 20 for its retrieval tests, so test it, but expect a limit. Re-ranking the best to the top matters more.

#### The 30-second answer

Good retrieval doesn't guarantee a good answer. Models favour early text, and in one study use fell from 98% at rank 1 to 44% at ranks 6 to 10, so I'd re-rank, send fewer chunks and place the best first. I'd require citations per claim, and check both correctness, which asks whether the source supports the claim, and faithfulness, which asks whether the model really used it. One study found up to 57% of citations weren't faithful. I test that by changing the document and seeing if the answer changes. For conflicts, I'd remove stale versions at ingest and show real disagreements. And I'd design abstention, with no-answer questions in my test set.

**Key terms and sources**

Why models miss retrieved evidence, context order, citations that look right but aren't real, conflicting and stale documents, and abstaining when the evidence isn't there. · checked 7 Nov 2026

#### Sources

- [Chen et al., Is GraphRAG Needed?](https://arxiv.org/abs/2606.25656)

- [Wallat et al., Correctness is not Faithfulness in RAG Attributions](https://arxiv.org/abs/2412.18004)

- [Yang et al., CRAG: Comprehensive RAG Benchmark](https://arxiv.org/abs/2406.04744)

- [Yang et al., RAGStress](https://arxiv.org/abs/2610.04691)

- [Barnett et al., Seven Failure Points](https://arxiv.org/abs/2401.05856)

- [Liu et al., Lost in the Middle](https://arxiv.org/abs/2307.03172)

- [Levy, Shlomov and Choshen, Retrieval Augmented Generation Compositionality](https://arxiv.org/abs/2610.29722)

Explanations are ours, built from these sources. Lab numbers are illustrative unless a lab says otherwise. Most recent papers are preprints.
