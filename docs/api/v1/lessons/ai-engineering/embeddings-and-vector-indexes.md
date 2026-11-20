# Embeddings and Vector Indexes

> You have 100 million chunks. Which embedding model and index do you use, and what does it cost?

- Track: AI Engineering › RAG › Lessons
- Type: Concept · 22 min
- Page: https://aimlrounds.com/tracks/ai-engineering/embeddings-and-vector-indexes/
- Before this: RAG End to End (`ai-engineering/rag-end-to-end`), Embeddings and Representation Learning (`fundamentals/embeddings`)
- Quiz topic: `rag`

## Intuition

### The situation

You're indexing 100 million chunks. The team picked the top model on a leaderboard, and float32 vectors. The memory bill is huge, and since you added a department filter, some users say search has got worse, with no errors in the logs. The interviewer asks:

> You have 100 million chunks. Which embedding model and index do you use, and what does it cost?

#### Why it matters

At a million chunks, almost anything works. At a hundred million, the choice of index decides your bill, and a filter can silently drop your recall. These are also common questions in a RAG design interview: how would you size this, and what happens when you filter?

### The idea

Think of a giant library map. The embedding model decides where each book goes, and shorter coordinates take less paper but are less exact. The index is the road network. Close most roads for a filter, and you can't reach the books, even though they're still there.

[Figure: Three decisions. Pick a model by testing it. Compress vectors. Check recall under your filters.]

_A filter can quietly destroy recall._

### Play

**Try to break it.** Size your corpus, and switch encoding. Then move the filter down to 1%.

#### Size it, then filter it

Memory is exact arithmetic. Quality kept is Hugging Face's best case, and it varies by model, as binary needs rescoring. Recall is from Qdrant's own benchmark on 1 million deep-image vectors at hnsw_ef = 64, using a single keyword filter. It isn't linked to the other sliders, and your data will differ.

100 million 1,024-dimensional chunks in float32 need about **410 GB** of memory for vectors alone. Binary cuts that to **12.8 GB**, and the graph's links then cost about as much as the vectors. Now move the filter. At **10%**, a plain graph's recall falls to 20.6%, and at **1%** to just 0.1%, while the query still returns quickly. Nothing errors, so you'd only notice by measuring. A graph built with the filter in mind holds 99%. That's the main trap of filtered search.

**Now say why:** why is there no error when recall collapses?

## How it works

### How it works

#### In one breath

Your embedding model decides what can be found, and your index decides how fast and at what cost. Choose a model by testing it on **your own queries**, not on a leaderboard alone. Vectors can be made far smaller: **Matryoshka** models can be shortened, **int8** is 4 times smaller, and **binary** is 32 times smaller if you re-score the top results. **Filters** can quietly break graph search, because the graph's links lead to points you've filtered out. And single vectors have a hard limit, so keep BM25 and a re-ranker in the stack.

#### Models, compression and indexes

##### Choosing a model

- **Shortlist from a benchmark** such as MTEB, for your language and domain.

- **Test on your data:** measure recall@k on a few hundred real labelled queries. A leaderboard rank needn't predict your result.

- **It matters a lot:** in one 450-setup study, the embedding model was among the largest factors in retrieval quality. In Qu et al., it outweighed the chunking method.

##### Making vectors smaller

| Method | Size | Quality kept | Watch out for |
|---|---|---|---|
| **Matryoshka** | Keep the first N dimensions | One study: 768 of 1,024 dimensions gave 25% less storage, and NDCG@10 rose 2.3% | Only for models trained this way |
| **int8** | 4× smaller | About 99.3% | Needs a calibration set |
| **Binary + rescoring** | 32× smaller | Up to about 96% | Strongly depends on the model: 96.45%, 87.7% and 74.77% across three tested models |

Quantization figures are from Hugging Face's benchmark on retrieval tasks, measured against full float32 vectors. Rescoring means searching with binary vectors, then re-scoring the top results with higher precision vectors.

##### Choosing an index

| Index | Idea | Good for |
|---|---|---|
| **Flat** | Compare with every vector | Small collections. Perfect recall |
| **HNSW** | Hop through a layered graph | High recall at low latency, with memory for links |
| **IVF, IVF-PQ** | Search the nearest clusters, with optional compression | Very large collections, at some recall cost |

##### Why filters break graphs

HNSW walks from node to node through links. If a filter removes most nodes, the walk runs out of valid paths. Qdrant notes that with 96% of points filtered out, fewer than one link per node survives on average. The lab uses its numbers. Fixes include building extra links for filter fields, graph repair methods like ACORN, and simply scanning the matching rows when very few match. A separate 2026 study found partition indexes (IVFFlat) beat HNSW at very low selectivity, and that pgvector's planner often chose poor plans. So measure recall for each filter you use.

##### A single vector has limits

Weller et al. show that a fixed number of dimensions can't represent every possible set of top results. On their deliberately hard LIMIT test, with simple questions like "who likes apples?", the best single-vector models reached under 20% recall@100. BM25 reached 93.6%, and a multi-vector model 54.8%. This test is built to stress that weakness, so everyday scores won't look like this. But it's a good reason to keep BM25 and a re-ranker.

#### The maths

$$ {\text{bytes per vector}} \approx {d \times b} + {8M} $$

The FAISS guideline for HNSW memory. Real systems also store IDs, metadata and the chunk text, and upper graph layers add a little.

- **memory per vector**: What each chunk costs in RAM, before metadata and text.

- **the vector**: d dimensions at b bytes each: 4 for float32, 1 for int8 and 1/8 for binary.

- **the graph**: HNSW stores about 2M links on its base layer, at 4 bytes each. M is usually 16 to 32.

## In practice

### In practice

#### In practice

- **Measure index recall:** compare ANN results with exact search on your own vectors, at your real filters, and watch p99 latency too.

- **Keep exact search when you can:** below a few hundred thousand vectors, or for very selective filters, a flat scan may be simpler and better.

- **Store full vectors on disk:** keep float32 on disk for rescoring, and in-memory binary for the first pass.

- **Check the model card:** don't truncate vectors unless the model was trained for it, or test first.

- **Plan for change:** a new model means new vectors everywhere. See Keeping an Index Current.

### The answer that sounds right

#### "The top model on the leaderboard is the best for us"

It sounds right, since the benchmark is rigorous. But it measures other people's data and questions. Your names, codes and language may behave differently, and memory cost matters too. Shortlist from a benchmark, then decide by recall on a few hundred of your own labelled queries.

## Say it

### You have 100 million chunks. Which embedding model and index do you use, and what does it cost?

#### The interviewer pushes further

Follow-up 1 of 3

Estimate memory for 50 million chunks at 768 dimensions in float32, with HNSW at M = 16.

Vectors: 50M × 768 × 4 bytes = 153.6 GB. Links: 50M × 8 × 16 bytes = 6.4 GB. So about 160 GB, plus the chunk text and metadata. As int8, the vectors fall to 38.4 GB.

Follow-up 2 of 3

Why does a filter hurt recall in HNSW, but return quickly?

The walk follows links, and most neighbours have been filtered out, so it ends early with too few valid results. It's fast because it did little work. Nothing errors, so you only notice by measuring recall with that filter.

Follow-up 3 of 3

Should you truncate a 1,536-dimensional vector to 256 to save money?

Only if the model was trained for it, as in Matryoshka models. Then test recall on your data. Truncating other models usually hurts a lot. If you plan to use binary too, be careful, as very few dimensions leave very few bits.

#### The 30-second answer

I'd shortlist embedding models from a benchmark like MTEB, then pick by recall on a few hundred of my own labelled queries. For memory, 100 million 1,024-dimensional float32 vectors need about 410 GB. int8 is 4 times smaller at about 99% quality, and binary is 32 times smaller at up to 96% with rescoring, though that varies a lot by model. I'd use HNSW for high recall at low latency, or IVF-PQ at very large scale. Filters are the main trap, as they cut the graph's paths: in one benchmark a plain graph fell to 20% recall on a 10% filter. So I'd use a filter-aware index and measure recall per filter. Single vectors also have limits, so I'd keep BM25 and a re-ranker.

**Key terms and sources**

Choosing an embedding model, shortening vectors with Matryoshka, scalar and binary quantization, HNSW and IVF memory, why filters break graph search, and the limits of a single vector. · checked 7 Nov 2026

#### Sources

- [Kusupati et al., Matryoshka Representation Learning](https://arxiv.org/abs/2205.13147)

- [Hugging Face, Binary and Scalar Embedding Quantization](https://huggingface.co/blog/embedding-quantization)

- [Qdrant, Filtered Vector Search and ACORN](https://qdrant.tech/articles/filtered-vector-search-acorn/)

- [Amanbayev et al., Filtered Approximate Nearest Neighbor Search in Vector Databases](https://arxiv.org/abs/2602.11443)

- [Weller et al., On the Theoretical Limitations of Embedding-Based Retrieval](https://arxiv.org/abs/2508.21038)

- [Malkov and Yashunin, HNSW](https://arxiv.org/abs/1603.09320)

- [FAISS, Guidelines to choose an index](https://github.com/facebookresearch/faiss/wiki/Guidelines-to-choose-an-index)

- [Levy, Shlomov and Choshen, Retrieval Augmented Generation Compositionality](https://arxiv.org/abs/2610.29722)

Explanations are ours, built from these sources. Lab numbers are illustrative unless a lab says otherwise. Most recent papers are preprints.
