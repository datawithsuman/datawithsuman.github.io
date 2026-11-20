# Advanced RAG: Hybrid Search, Re-ranking, Query Rewriting and GraphRAG

> Which upgrade cut retrieval failures by 67%?

- Track: AI Engineering › RAG › Lessons
- Type: Concept · 25 min
- Page: https://aimlrounds.com/tracks/ai-engineering/advanced-rag/
- Before this: RAG End to End (`ai-engineering/rag-end-to-end`)
- Quiz topic: `rag`

## Intuition

### The situation

The assistant's RAG works for most questions, but misses order IDs like ORD-48213, vague ones like "that thing with my money back" and two-part ones. A colleague wants to jump straight to GraphRAG and agents. The interviewer asks:

> How do you improve retrieval, and which upgrades cut failures by 67%?

**Running example:** the support assistant's RAG works for most questions but misses ones with order IDs ("ORD-48213"), vague ones ("that thing with my money back"), and two-part ones ("refund for late and cold food?").

#### Dense top-k isn't enough

Embedding similarity blurs exact identifiers, chunks lose meaning when cut out of their document, the best chunk is often ranked 8th rather than 1st, and user questions are vague, multi-part or phrased nothing like the documents. Each has a targeted fix.

### The idea

Think of hiring. You can't interview every applicant, so a quick CV screen makes a wide shortlist and a slow interview picks from it. Retrieval is the screen, which has to keep the right person in the pile. The re-ranker is the interview.

[Figure: Top-20 retrieval failure rate. Plain embeddings 5.7 percent. With contextual embeddings 3.7. With contextual BM25 2.9. With re-ranking 1.9, a 67 percent reduction.]

_From Anthropic's "Introducing Contextual Retrieval" (Sept 2024). This is retrieval failure, not end-to-end answer accuracy._

### Play

**Try to break it.** Stack the upgrades one at a time: plain embeddings, contextual embeddings, contextual BM25 and re-ranking. Note what each adds.

#### How much does each step buy?

Numbers from Anthropic's "Introducing Contextual Retrieval" (Sept 2024): share of queries whose relevant chunk was not in the top 20, averaged over their test datasets (codebases, fiction, papers and more). Not end-to-end answer accuracy.

Plain embeddings miss the relevant chunk in the top 20 for **5.7%** of queries. Adding situating context to each chunk before embedding cuts that to 3.7%; adding the same contextual chunks to a BM25 index (hybrid search) brings it to 2.9%; re-ranking the candidates reaches **1.9%**, a **67%** reduction. The trap is reaching for the most complex option first (agents, GraphRAG) when hybrid search and a re-ranker fix most failures cheaply. Each step has a cost: contextualising chunks needs one LLM call per chunk at indexing time (cheap with prompt caching), and re-ranking adds query latency.

**Now say why:** a re-ranker is much more accurate, so why not use it for all of retrieval?

## How it works

### How it works

#### In one breath

When basic RAG misses, the fix is usually one of a few well-tested upgrades. **Hybrid search** combines BM25 (exact words, codes, names) with dense embeddings (meaning). **Re-ranking** runs a slower cross-encoder over the top 20–100 candidates to put the truly relevant ones first. **Contextual chunks** prepend a sentence of context to each chunk before indexing, so "capped at ₹150" knows it's about late refunds. **Query rewriting** turns vague or multi-part questions into better search queries. Together these cut Anthropic's measured top-20 retrieval failure rate from 5.7% to **1.9%** (−67%). For "summarise themes across all 10,000 tickets" questions, **GraphRAG** builds an entity graph with community summaries instead of retrieving a few chunks. What you'll be able to do after this: pick the right upgrade for a RAG failure, explain bi-encoders vs cross-encoders, and say when GraphRAG is worth it.

#### The upgrade toolkit

| Technique | How | Fixes |
|---|---|---|
| **Hybrid search** | BM25 + dense, fused with reciprocal rank fusion (lesson) | IDs, codes, rare names |
| **Re-ranking** | a **cross-encoder** reads query and chunk together and scores relevance (Nogueira & Cho 2019); or late-interaction models like ColBERT | right chunk retrieved but ranked low |
| **Contextual chunks** | an LLM writes 50–100 tokens situating each chunk in its document; prepended before embedding and BM25 | chunks that don't make sense alone |
| **Query rewriting** | an LLM rewrites, expands or splits the query; HyDE embeds a hypothetical answer instead of the question (Gao et al. 2023) | vague, conversational or multi-part questions |
| **Multi-step / agentic retrieval** | retrieve, read, decide whether to search again (Self-RAG, iterative retrieval) | questions needing facts from several places |
| **GraphRAG** | extract entities and relations into a graph, cluster communities, pre-summarise them (Edge et al. 2024) | "global" questions about a whole corpus |

**Bi-encoder vs cross-encoder:** a bi-encoder embeds query and document separately (fast, pre-computable, used for first-stage retrieval); a cross-encoder reads them together (much more accurate, but must run per pair at query time, so only on a short list).

## In practice

### In practice

#### Diagnose, then upgrade

- **Measure first:** label 100–300 real questions with their relevant chunks; compute recall@k and MRR (Evaluating LLM Apps). If recall@50 is high but recall@5 low, add a re-ranker; if recall@50 is low, fix chunking, hybrid search or query rewriting.

- **Default stack:** structure-aware chunks with context → hybrid retrieval of ~50 to 150 → cross-encoder re-rank to ~5–20 → answer with citations.

- **GraphRAG** answers corpus-wide "what are the main themes" questions far better than chunk retrieval, in its authors' tests, but classic indexing is expensive (many LLM calls), and it isn't needed for specific factual questions. Microsoft's LazyGraphRAG reports 0.1% of that indexing cost, by deferring LLM work to query time. One 2026 test found simply adding related facts to each document beat a more complex GraphRAG setup, so try simple structure first.

- **Long-context models** reduce the need for aggressive chunking on small corpora; for large or changing corpora, retrieval remains cheaper and more controllable.

**Upgrades don't simply add up.** In the lab above, each step shows a gain on Anthropic's tests. But a 2026 study of 450 setups found three strong retrieval techniques predicted +47% together, and delivered +17%, because they overlap. Across 17 combinations, the shortfall ranged from 7% to 72%. The best setup also changed as the corpus grew. So test upgrades in your full pipeline, at your real scale.

Go deeper: Re-ranking and Late Interaction, and Agentic RAG.

#### Retrieve broadly, then rank precisely

Get the right chunk into a wide candidate set with hybrid, context-aware retrieval, then let an accurate but slow re-ranker put it first; reach for query rewriting, multi-step retrieval or GraphRAG only for the question types that need them.

### The answer that sounds right

#### "GraphRAG is better RAG"

It sounds right, since it's the most sophisticated option. But it's for a different question type: corpus-wide ones, like the themes across all tickets. It adds cost without benefit for pinpoint facts, and hybrid search with a re-ranker fixes most failures cheaply. Just increasing k isn't the answer either: more chunks add noise and cost, so rank better instead.

## Say it

### How do you improve retrieval, and which upgrades cut failures by 67%?

#### The interviewer pushes further

Follow-up 1 of 3

Why not use a cross-encoder for first-stage retrieval?

It must run once per query–document pair at query time; over millions of chunks that's far too slow. Bi-encoders allow pre-computed document vectors and ANN search.

Follow-up 2 of 3

Recall@50 is 95% but answers are still wrong. Next step?

The right chunk is found but ranked too low (or the LLM misuses it): add a re-ranker, check recall@5, and check faithfulness of the generation.

Follow-up 3 of 3

When is GraphRAG worth it?

When users ask global, sensemaking questions over a large corpus (themes, trends, relationships); not for pinpoint facts, where it adds cost without benefit.

#### The 30-second answer

To improve RAG I first measure retrieval recall on labelled queries. Then the standard upgrades: hybrid BM25 plus dense retrieval for exact terms, contextual chunks that carry a summary of their document, and a cross-encoder re-ranker on the top 50 candidates. Anthropic measured these cutting top-20 retrieval failures from 5.7 to 1.9 percent. For vague or multi-part questions I add query rewriting or decomposition, HyDE in some cases, and multi-step retrieval for questions that need several sources. GraphRAG is for corpus-wide questions like themes across all tickets, at a much higher indexing cost.

**Go further**

#### What not to say

- "Just increase k." More chunks add noise and cost; rank better instead.

- "GraphRAG is better RAG." It's for a different question type.

**Key terms and sources**

The techniques that take a basic RAG system from "often finds the right passage" to "almost always does": hybrid sparse + dense retrieval, cross-encoder re-ranking, contextualised chunks, query rewriting and decomposition (including HyDE), multi-step retrieval, and graph-based RAG for questions about a whole corpus · built from Anthropic (Contextual Retrieval, 2024), Nogueira & Cho (BERT re-ranking, 2019), Khattab & Zaharia (ColBERT, SIGIR 2020), Gao et al. (HyDE, ACL 2023), Ma et al. (Query Rewriting, EMNLP 2023), Edge et al. (GraphRAG, 2024) and Asai et al. (Self-RAG, ICLR 2024) · checked 29 Oct 2026

#### Sources

1. Anthropic, "Introducing Contextual Retrieval", Sept 2024, [anthropic.com/news/contextual-retrieval](https://www.anthropic.com/news/contextual-retrieval).

2. R. Nogueira & K. Cho, "Passage Re-ranking with BERT", 2019, [arXiv:1901.04085](https://arxiv.org/abs/1901.04085); O. Khattab & M. Zaharia, "ColBERT", SIGIR 2020, [arXiv:2004.12832](https://arxiv.org/abs/2004.12832).

3. L. Gao et al., "Precise Zero-Shot Dense Retrieval without Relevance Labels" (HyDE), ACL 2023, [arXiv:2212.10496](https://arxiv.org/abs/2212.10496); X. Ma et al., "Query Rewriting for Retrieval-Augmented Large Language Models", EMNLP 2023, [arXiv:2305.14283](https://arxiv.org/abs/2305.14283).

4. D. Edge et al., "From Local to Global: A Graph RAG Approach to Query-Focused Summarization", 2024, [arXiv:2404.16130](https://arxiv.org/abs/2404.16130).

5. A. Asai et al., "Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection", ICLR 2024, [arXiv:2310.11511](https://arxiv.org/abs/2310.11511).

6. I. Levy, S. Shlomov & L. Choshen, "Retrieval Augmented Generation Compositionality", 2026, [arXiv:2610.29722](https://arxiv.org/abs/2610.29722); L. Chen et al., "Is GraphRAG Needed?", 2026, [arXiv:2606.25656](https://arxiv.org/abs/2606.25656); Microsoft Research, [LazyGraphRAG](https://www.microsoft.com/en-us/research/blog/lazygraphrag-setting-a-new-standard-for-quality-and-cost), 2024.
