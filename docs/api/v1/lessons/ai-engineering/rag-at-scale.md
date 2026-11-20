# RAG at Scale: Slow and Wrong

> Your RAG worked on 100 docs, but broke at 10 million. Why?

- Track: AI Engineering › RAG › Scenarios
- Type: Interview · 8 min
- Page: https://aimlrounds.com/tracks/ai-engineering/rag-at-scale/
- Before this: RAG End to End (`ai-engineering/rag-end-to-end`), Advanced RAG: Hybrid Search, Re-ranking, Query Rewriting and GraphRAG (`ai-engineering/advanced-rag`)
- Quiz topic: `rag`

## Intuition

### The situation

Your RAG worked on 100 documents. Same code and same model on 10 million, and answers take longer and come back wrong more often. A colleague says to retrieve 50 chunks instead of 5. The interviewer asks:

> Your RAG worked on 100 docs, but broke at 10 million. Why?

#### What would you check first?

Tap an answer.

### The idea

Think of moving from a small office's filing cabinet to a national archive. Searching every shelf is now far too slow, so you need a catalogue. And there are now old versions, drafts and copies that all look alike, so you narrow it by department and year, then have an expert read the shortlist.

[Figure: Two problems with two fixes. Slow: exact search checks every vector, so use an approximate index. Wrong: look-alikes bury the right chunk, so filter by metadata and rerank.]

_The same symptom, with two separate causes and two separate fixes._

### Play

**Try to break it.** Search with no fixes on, and see what reaches the top 5. Turn on the metadata filter, then reranking, then both.

#### Why it's wrong: look-alikes bury the right chunk

With 100 docs, there's one refund policy. With 10 million, there are old versions, drafts, other regions and copies in slide decks, and they all sound alike. Only the top 5 go to the LLM. Turn on the fixes.

–

Illustrative scores. The reranker reads the question and each chunk together, so it can tell “current Support policy” from a look-alike.

**Now say why:** the right chunk is in the index, so why doesn't it reach the LLM?

## How it works

### How it works

#### In one breath

Same code, same model, much bigger pile. Answers now take longer _and_ come back wrong more often. These are two different problems with two different fixes: an index to make search fast, and filtering plus reranking to make it right.

#### Why it's slow: exact search checks every vector

Exact (brute-force) search compares your question with every stored vector. The work grows in step with the pile. Drag the slider.

Exact arithmetic for 768-dimensional embeddings: one similarity = 768 multiply-adds, memory = chunks × 768 × 4 bytes. Real time also depends on hardware, batching and quantization.

#### The speed fix: an approximate index

Approximate nearest neighbour (ANN) indexes skip most of the pile. IVF groups vectors into clusters and searches only the clusters nearest your question. HNSW builds a layered graph and hops from coarse to fine. Both check a small fraction of the vectors.

–

Illustrative drawing. Brown = your question, green rings = its true 5 nearest neighbours, blue dots = the vectors actually checked.

#### The catch: a little recall for a lot of speed

Searching fewer clusters is faster but can miss some true neighbours. Recall@10 = how many of the true top 10 the index still finds. Move the slider and watch the trade-off.

–

HNSW has the same kind of knob (how many candidates it explores per query). In production you tune it on your own data until recall is good enough at the latency you need.

## In practice

### In practice

#### Fixes, in order

1. 1 ##### Measure first Time each stage (embedding the query, vector search, reranking, the LLM call) and keep a small test set of questions with known answers and their source chunks. Then you know whether you have a speed problem, a quality problem or both.

2. 2 ##### Use an approximate index HNSW or IVF instead of brute force. Tune the search knob (clusters searched, or candidates explored) until recall@10 on your test set is high enough. Watch out: HNSW keeps graph links in memory, and IVF needs training and re-balancing as data grows.

3. 3 ##### Filter by metadata first Tag chunks with team, product, region, date and version, and restrict the search to what the question needs. It removes most look-alikes and shrinks the search. Watch out: filtering _after_ the ANN search can leave fewer than k results, so prefer a database that filters during search.

4. 4 ##### Retrieve wide, then rerank Take the top 50 or so from the fast index, rerank them with a slower, sharper cross-encoder, and send only the best 5 to the LLM. Watch out: reranking adds latency, so keep the candidate list small.

5. 5 ##### Clean the pile Remove duplicates and superseded versions when you ingest. Fewer look-alikes is the cheapest quality fix of all.

#### Mistakes to avoid

Common

- Blaming the LLM before timing the retrieval stages.

- Raising top-k to 50 and sending it all to the LLM.

- Switching to ANN without checking recall on real questions.

- Keeping every old version of a document in the index.

✓ Better

- Measure latency per stage and retrieval recall separately.

- Retrieve wide, rerank, and send a few chunks.

- Tune the index knob on your own test set.

- Store metadata at ingest so you can filter later.

Index to make it fast. Filter and rerank to make it right.

### The answer that sounds right

#### "Retrieve 50 chunks instead of 5"

It sounds right, since the right chunk is more likely to be somewhere in 50. But sending them all to the LLM adds noise and cost, and it does nothing for speed. Retrieve wide if you like, but then rerank and send a few. Blaming the LLM is no better: time the retrieval stages first, because these are two different problems.

## Say it

### Your RAG worked on 100 docs, but broke at 10 million. Why?

#### The interviewer pushes further

Follow-up 1 of 4

HNSW or IVF?

HNSW usually gives high recall at low latency and handles inserts well, but uses more memory for its graph. IVF uses less memory, pairs well with compression (IVF-PQ) for very large sets, and needs a training step to learn its clusters. Many vector databases offer both; benchmark on your data.

Follow-up 2 of 4

Why not just use exact search on a GPU?

For a few million vectors, exact search on a GPU can be fast enough, and it gives perfect recall. As the pile and the query volume grow, the cost grows with them, so most large systems switch to an approximate index.

Follow-up 3 of 4

Pre-filtering or post-filtering?

Post-filtering runs the ANN search first, then drops chunks that don't match, which can leave you with fewer than k results. Pre-filtering (or filtering during the search) restricts the candidates up front, so you always get k matching chunks. Prefer filtering during search when your database supports it. Even then, check recall under your real filters: a graph index can lose most of its recall on a narrow filter, with no error. See Embeddings and Vector Indexes.

Follow-up 4 of 4

Does hybrid search help here?

Yes for exact terms. Keyword search (BM25) finds IDs, error codes and product names that embeddings blur together. Combine both result lists, then rerank.

#### The 30-second answer

These are two different problems, so I'd split them first: time each stage, and check whether the right chunk is still retrieved. Slow usually means exact search, where the work grows with the pile, so I'd move to an approximate index like HNSW or IVF and tune its search knob until recall@10 is good enough on my test set. Wrong usually means look-alikes burying the right chunk: old versions, drafts and other regions. So I'd filter by metadata like team, date and version, retrieve wide, rerank with a cross-encoder and send only the best few chunks. And I'd remove duplicates and old versions at ingest.

**Key terms and sources**

Sources checked 5 Nov 2026

#### Sources

–
