# Re-ranking and Late Interaction

> The right chunk is retrieved, but it's ranked 12th. What do you do, and what's late interaction?

- Track: AI Engineering › RAG › Lessons
- Type: Concept · 18 min
- Page: https://aimlrounds.com/tracks/ai-engineering/reranking-and-late-interaction/
- Before this: Advanced RAG: Hybrid Search, Re-ranking, Query Rewriting and GraphRAG (`ai-engineering/advanced-rag`)
- Quiz topic: `rag`

## Intuition

### The situation

Recall@50 is 94%, but recall@5 is only 58%. The right chunk is usually found, then buried. A colleague wants to send 50 chunks to the model. Another has read that ColBERT doubles results. The interviewer asks:

> The right chunk is retrieved, but it's ranked 12th. What do you do, and what's late interaction?

#### Why it matters

Only the top few chunks reach the model, and the model uses early chunks most. So a good chunk ranked 12th might as well be missing. Re-ranking is often the cheapest big gain, and a common interview follow-up. See Search and Retrieval for BM25 and fusion.

### The idea

Think of hiring. Sorting 10,000 CVs by keywords is quick but crude, so you use it to get a shortlist. Then you read those 50 carefully. Late interaction is like checking each requirement against the best line in a CV, rather than judging its overall impression.

[Figure: Three scorers. A bi-encoder compares single vectors. Late interaction compares every token. A cross-encoder reads both together.]

_Retrieve broadly, then rank precisely._

### Play

**Try to break it.** Add off-topic words to document A. Watch both scores.

#### Average against MaxSim

Exact calculation on invented 4-number word vectors, with topics refund, delay, plan and food. Query: "gold refund late". Document A: "gold refund for late orders", plus off-topic words about food. Document B: "plan offers delivery refund", which is only partly relevant. Single vector: cosine of the averaged word vectors. MaxSim: the sum of each query word's best cosine. Scores are divided by the number of query words.

With no off-topic words, both methods pick document A. Add just **2 off-topic words**, and the single vector flips to B: A falls from 0.99 to 0.70, against B's 0.89. At 10 words, A is down to 0.23. **MaxSim** stays at 1.00, because each query word still finds its exact match. The cost is storage: 14 vectors rather than 1 for this short document. MaxSim also has a blind spot: it ignores everything else in the document, so it can't tell that A is mostly about food. These are invented vectors, built to show the mechanism. See the conflicting results above for real data.

**Now say why:** why does MaxSim hold up, when averaging doesn't?

## How it works

### How it works

#### In one breath

A first-stage retriever must be fast, so it compares one vector per chunk. A **cross-encoder** reads the query and chunk together, which is far more accurate, but too slow for more than a short list. **Late interaction** sits between them: ColBERT stores a vector for every token, and scores each query token against its best match in the document. That keeps fine detail, but uses much more memory. Measured gains vary. In one study, late interaction doubled the hit rate, and in another it did worse than a single vector. So test on your own data.

#### Three ways to compare

| | Bi-encoder | Late interaction | Cross-encoder |
|---|---|---|---|
| Compares | One vector each | Every query token with every document token | Reads both together |
| Precomputed | Yes | Yes, one vector per token | No |
| Use for | First-stage retrieval | First stage or re-ranking | Re-ranking a short list |
| Main cost | Least memory | Much more memory | Latency per candidate |

##### What re-ranking delivers

- **Microsoft (vendor test):** hybrid search scored 51.2 NDCG@3, and adding its new ranker raised that to 72.3. It re-ranked 50 documents in about 158 ms on average.

- **Anthropic (vendor test):** re-ranking took retrieval failures from 2.9% to 1.9%, from 150 candidates down to 20.

- **Newer isn't always better:** in the 450-setup study, a 2019 MiniLM cross-encoder beat all four recent rerankers it tested, on those corpora.

- **Gains overlap:** that same study found re-ranking leaves less room for other upgrades, and for a strong embedding model. Test the full stack.

##### Does MMR help?

Maximal marginal relevance penalises results that look like ones already chosen. In the 450-setup study, it cut NDCG@10 by 3.6% on average, and ARAGOG found no notable gain. On focused corpora, similar passages are often exactly the evidence you need. Use it only if your problem is near-duplicates, and consider removing duplicates at ingest instead.

##### Late interaction: conflicting results

| Study | Result | Caveat |
|---|---|---|
| 463,971 arXiv papers | ColBERT: Hit@3 of about 93 to 95%, against 46 to 47% for plain dense | Synthetic questions, and a different encoder too |
| Financial and technical reports | Text late interaction: nDCG@5 of 0.32, against 0.46 for dense. Visual late interaction was best, at 0.74 | Visually rich documents |
| LIMIT test | Multi-vector: 54.8% recall@100, against under 20% for dense | A deliberately hard test |

So don't treat it as an automatic upgrade. The memory cost is real: in the second study, text late interaction used about 2.8 times the memory of dense, and page-image late interaction about 15 times.

#### The maths

$$ {S(q, d)} = \sum_{{i \in q}} {\max_{j \in d}}\ {q_i \cdot d_j} $$

The MaxSim operator from ColBERT (Khattab and Zaharia, 2020). A single vector averages everything into one point before comparing.

- **the score**: How well document d matches query q.

- **every query token**: Each word in the question gets its own vote.

- **its best match**: Each query token looks for the one document token most like it. Other tokens don’t dilute it.

- **a similarity**: The dot product of two token vectors, stored at indexing time.

## In practice

### In practice

#### In practice

- **Diagnose first:** if recall@50 is high and recall@5 is low, a re-ranker should help. If recall@50 is low, it can't.

- **Tune the candidate count:** more candidates raise the chance of including the answer, and add latency. Try 50 to 150.

- **Budget latency:** measure the re-ranker at your p99, and cap the candidate length.

- **Use metadata where you can:** a re-ranker can't tell a current policy from an old one that reads the same. Filter or add dates.

- **Compare to no re-ranker:** keep measuring the gain, as a stronger embedding model can shrink it.

### The answer that sounds right

#### "Just send more chunks to the model"

It sounds right, since the answer is then in the prompt. But models use later text less, so a chunk at rank 30 may be ignored, while you pay for all of them. Put the right chunk near the top instead. That's a re-ranker's job.

## Say it

### The right chunk is retrieved, but it's ranked 12th. What do you do, and what's late interaction?

#### The interviewer pushes further

Follow-up 1 of 3

Why does averaging hurt long chunks?

A single vector squeezes everything into one point, so off-topic text pulls it away from the relevant part. That's why chunks are kept small, and why MaxSim, where each query token finds its best match, holds up better.

Follow-up 2 of 3

A re-ranker adds 200 ms. Is it worth it?

Compare it with the rest of the request. Next to a few seconds of LLM time, 200 ms is often fine if answer quality rises. Measure the gain on labelled questions, and try fewer candidates first.

Follow-up 3 of 3

Recall@50 is 60%. Will a re-ranker fix it?

No. A re-ranker can only reorder what it's given. Fix retrieval first with hybrid search, better parsing or chunking, query rewriting or a better embedding model.

#### The 30-second answer

If the right chunk is found but ranked low, I'd add a second stage. A bi-encoder compares single vectors, so it's fast but coarse. A cross-encoder reads the query and chunk together, which is much more accurate, so I'd run it on the top 50 to 150. Late interaction, like ColBERT, stores a vector per token, and sums each query token's best match, which keeps detail without running a model per pair at query time, but costs much more memory. Results vary: it doubled the hit rate in one study, and lost to dense in another. I'd also check MMR before using it, as it hurt on focused corpora. And I'd measure the whole stack, because gains overlap.

**Key terms and sources**

Why a second ranking stage helps, cross-encoders, how ColBERT's MaxSim works, latency and memory costs, why MMR can hurt, and conflicting evidence on late interaction. · checked 7 Nov 2026

#### Sources

- [Nogueira and Cho, Passage Re-ranking with BERT](https://arxiv.org/abs/1901.04085)

- [Khattab and Zaharia, ColBERT](https://arxiv.org/abs/2004.12832)

- [Microsoft, Raising the bar for RAG excellence](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/raising-the-bar-for-rag-excellence-query-rewriting-and-new-semantic-ranker/4302729)

- [Anthropic, Introducing Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval)

- [Levy, Shlomov and Choshen, Retrieval Augmented Generation Compositionality](https://arxiv.org/abs/2610.29722)

- [Rathi, Chawla and Andreopoulos, A Controlled Comparison of RAG Strategies](https://arxiv.org/abs/2609.38473)

- [Kuru and Keskin, Evaluating Modern RAG](https://arxiv.org/abs/2608.23176)

- [Eibich et al., ARAGOG](https://arxiv.org/abs/2404.01037)

- [Weller et al., On the Theoretical Limitations of Embedding-Based Retrieval](https://arxiv.org/abs/2508.21038)

Explanations are ours, built from these sources. Lab numbers are illustrative unless a lab says otherwise. Most recent papers are preprints.
