# RAG Practice

> 10 questions to work by hand: recall, MRR, fusion, memory, filters, tokens and migrations.

- Track: AI Engineering › RAG › Scenarios
- Type: Interview · 40 min
- Page: https://aimlrounds.com/tracks/ai-engineering/rag-practice/
- Before this: Re-ranking and Late Interaction (`ai-engineering/reranking-and-late-interaction`), RAG Evals: Retrieval, Faithfulness and Relevance (`ai-engineering/rag-evals`)
- Quiz topic: `rag`
- Sources checked: 2026-11-07 · Text last changed: 2026-11-19 · Version: bae7faf580

How to use this page

Give yourself about 5 minutes per question, as in an interview. Work each one out by hand, then open the answer and compare.

**The toolkit:** precision@k = relevant found ÷ k; recall@k = relevant found ÷ all relevant; MRR = average of 1 ÷ first relevant rank; RRF score = Σ 1 ÷ (60 + rank); memory = chunks × dimensions × bytes, plus 8M bytes per chunk for HNSW links; loop tokens = Σ (S + i × C); faithfulness = supported claims ÷ all claims.

Question 1 · Easy · precision and recall

### A question has 3 relevant chunks. You retrieve 5, and 2 of them are relevant. What are precision@5 and recall@5?

Answer: **Precision@5 = 0.40, and recall@5 = 0.67**

1. Precision: 2 relevant ÷ 5 retrieved = 0.40.

2. Recall: 2 found ÷ 3 relevant = 0.67.

Which matters more for RAG's first stage? Usually recall, because a re-ranker can fix order, but not what's missing.

Question 2 · Easy · MRR

### Across 4 questions, the first relevant chunk appears at ranks 1, 3, not at all, and 2. What's the MRR?

Answer: **About 0.46**

1. Reciprocal ranks: 1, 1/3, 0 and 1/2.

2. Their sum is 1.83, and 1.83 ÷ 4 ≈ 0.46.

A missing chunk counts as 0, so a few misses hurt a lot.

Question 3 · Medium · fusion

### BM25 returns A, B, C. Dense search returns C, A, D. Using reciprocal rank fusion with k = 60, what's the merged order?

Answer: **A, C, B, D**

1. A: 1/61 + 1/62 = 0.01639 + 0.01613 = 0.03252.

2. C: 1/63 + 1/61 = 0.01587 + 0.01639 = 0.03226.

3. B: 1/62 = 0.01613, and D: 1/63 = 0.01587.

Why ranks, rather than raw scores? BM25 and cosine scores aren't on the same scale.

Question 4 · Medium · memory

### You have 10 million chunks at 1,024 dimensions. How much memory do float32 vectors need? And binary? How much do HNSW links add at M = 16?

Answer: **About 41 GB, or 1.28 GB as binary, plus about 1.28 GB of links**

1. Float32: 10M × 1,024 × 4 bytes ≈ 41 GB.

2. Binary: 41 GB ÷ 32 ≈ 1.28 GB.

3. Links: 10M × 8 × 16 bytes = 1.28 GB.

With binary, the links cost as much as the vectors, and you still need full vectors somewhere for rescoring.

Question 5 · Medium · filters

### You filter after search. You fetch 100 candidates, and a user can see 5% of documents. You want 10 results. What happens, and what do you do?

Answer: **About 5 results come back. Filter during search, or fetch far more**

1. 100 × 5% = about 5 visible candidates.

2. That's fewer than the 10 you want, and worse for rarer filters.

3. Fetching more costs time. Filtering during search is better, but you must check recall under that filter.

A filter-blind graph can lose most of its recall, with no error to warn you.

Question 6 · Medium · agent cost

### An agent has a 2,000-token base prompt, and adds 5,000 tokens of results per search. It does 3 searches, then answers. How many input tokens does it use, keeping full history?

Answer: **38,000 tokens**

1. Call 1: 2,000.

2. Call 2: 7,000. Call 3: 12,000.

3. Call 4: 17,000. The total is 38,000.

One static search uses 7,000. What cuts this? Batching searches, capping rounds and trimming old results.

Question 7 · Medium · should you index?

### Your documents total 120,000 tokens and change monthly. Your manager wants a vector database. What do you suggest?

Answer: **Try putting it in the prompt first, with prompt caching**

1. Anthropic suggests this under about 200,000 tokens.

2. It has no chunking, syncing or retrieval failures to manage.

3. Measure cost and latency, and add retrieval when they hurt, or the corpus grows.

When would you index anyway? When cost per call is too high, permissions differ per document, or it's growing fast.

Question 8 · Hard · migration

### You have 200 million chunks of 300 tokens, and a limit of 10 million tokens a minute. Embedding costs $0.13 per million tokens. What are the cost and time, and how do you switch without downtime?

Answer: **About $7,800 and about 4.2 days. Build a second index, dual write, backfill, test, then flip an alias**

1. Tokens: 200M × 300 = 60 billion.

2. Cost: 60,000 million × $0.13 = $7,800.

3. Time: 60B ÷ 10M = 6,000 minutes, about 4.2 days.

4. Dual writes keep the new index current during those days.

Why can't you mix old and new vectors in one index? They live in different spaces, so their scores mean nothing together.

Question 9 · Hard · permissions

### Your permission service has an outage. The code catches the error, and sets the allowed-folders list to empty, and the search code treats an empty list as no filter. What happens, and how do you fix it?

Answer: **Every user can retrieve every document. Fail closed, and test for it**

1. An empty filter must mean no results, not all results.

2. On error, return nothing and show a clear message.

3. Add a test where the permission call fails, and one where user A asks for user B's document.

Which is worse here: an outage or a leak? Usually a leak, so accept the outage.

Question 10 · Hard · conflicting results

### A paper says late interaction doubles the hit rate, and another says it loses to dense search. Your team asks which to believe. What do you say?

Answer: **Both may be right for their setups. Test on your own data, and count the costs**

1. The first used synthetic questions and a different encoder, on 463,971 paper abstracts.

2. The second used visually rich reports, and text late interaction lost there.

3. Compare recall on your labelled questions, plus memory and latency.

It's a good general rule: gains measured alone may not survive in your full pipeline.

**More practice and sources**

10 interview questions, easy to hard · answers hidden until you click · checked 7 Nov 2026

Keep practising

Uses RAG End to End, Embeddings and Vector Indexes, Re-ranking, Grounded Answers, Agentic RAG, Permissions, Keeping an Index Current and Evaluating LLM Apps. Scenarios and numbers are invented, so the answers are worked examples.
