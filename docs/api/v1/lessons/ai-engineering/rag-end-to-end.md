# RAG End to End

> How do you build RAG, and how big should a chunk be?

- Track: AI Engineering › RAG › Lessons
- Type: Concept · 25 min
- Page: https://aimlrounds.com/tracks/ai-engineering/rag-end-to-end/
- Before this: Search: BM25, Dense and Hybrid Retrieval (`fundamentals/search-and-retrieval`), Embeddings and Representation Learning (`fundamentals/embeddings`)
- Quiz topic: `rag`

## Intuition

### The situation

The support assistant must answer from a 30-rule refund and service policy that changes every few weeks. Putting it all in every prompt is expensive, and a colleague's plan to fine-tune on it would need redoing at every update. The interviewer asks:

> How do you build RAG, and how big should a chunk be?

**Running example (this track):** the food-delivery support assistant must answer from the company's 30-rule refund and service policy, which changes every few weeks.

#### The model doesn't know your documents

Pre-trained knowledge is general, frozen at a cutoff and can't be cited. Putting every document in every prompt is slow and expensive, and models use very long contexts unevenly. Fine-tuning on documents teaches facts poorly and must be redone at every update. Retrieval gives the model just the passages it needs, fresh each time.

### The idea

Think of an open-book exam. Nobody expects the student to memorise the book, but the answer can only be as good as the pages they turn to. So most of the work is indexing the book well and finding the right pages quickly.

[Figure: Offline: parse, chunk, embed and index your documents. Online: take the query, retrieve, re-rank and generate an answer from those chunks.]

_The pipeline, stage by stage. Each stage has its own typical failure._

### Play

**Try to break it.** Try 1-sentence chunks, then 3, 5 and 10. Watch the questions answered and the context sent. Then try 2 sentences with a 1-sentence overlap.

#### How big should a chunk be?

A 30-sentence refund and service policy; 8 customer questions, several needing two adjacent sentences (e.g. "10% refund" + "capped at ₹150"). Retrieval: TF-IDF cosine, top 3 chunks. A question counts as answered only if every sentence it needs is in the retrieved chunks. Tokens ≈ words × 1.3.

With **1-sentence** chunks, retrieval is precise (39 tokens per question) but only **4 of 8** questions get their full answer: answers that need two sentences ("the refund is 10%" + "capped at ₹150") are split across chunks that don't both make the top 3. Bigger chunks keep related sentences together: 3 sentences get 7 of 8 at 115 tokens, 5 get all 8 at 194, and 10-sentence chunks also get 8 of 8 but send **379** tokens of mostly irrelevant policy, which costs money and can distract the model. Adding a **1-sentence overlap** to 2-sentence chunks gets **all 8** at just **77 tokens**: boundaries no longer cut answers in half. Real systems tune chunk size and overlap on their own questions, and prefer splitting on document structure (sections, list items) over fixed counts.

Overlap rescues this small example, as answers sit right next to each other. Larger studies have found little average gain from overlap, so test it on your own data. See Parsing and Chunking.

**Now say why:** small chunks are so precise, so why do they miss half the answers?

## How it works

### How it works

#### In one breath

An LLM doesn't know your refund policy, and it was trained months ago. **RAG** fetches the relevant text at question time and puts it in the prompt, so answers are grounded, current and citable. The pipeline: **ingest** documents (parse PDFs, HTML, tables) → **chunk** them into passages → **embed** each chunk into a vector → store in a **vector index** (HNSW or IVF for approximate nearest-neighbour search) → at query time, embed the question, **retrieve** the top-k chunks (often hybrid with BM25), and **generate** an answer from them with citations. Most quality problems are retrieval problems, and chunking is the first knob: chunks too small split answers across pieces; too large and you send lots of irrelevant text.What you'll be able to do after this: draw the RAG pipeline, choose chunking and index settings, and say where RAG systems fail.

#### The pipeline, stage by stage

| Stage | Choices | Typical failure |
|---|---|---|
| **Ingest & parse** | PDF/HTML/table extraction, OCR, metadata (source, date, section) | tables garbled, headers lost, stale versions indexed |
| **Chunk** | fixed size (e.g. 200–800 tokens) with overlap; by structure (headings, paragraphs); semantic, though evidence for it is weak | answer split across chunks; chunks without context ("it is capped at…") |
| **Embed** | an embedding model chosen on a benchmark like MTEB and on your own queries; same model for docs and queries | domain terms, codes and names embed poorly |
| **Index** | HNSW graph (fast, memory-heavy), IVF/PQ (compressed, for billions); a vector DB or Postgres with pgvector | approximate search misses neighbours (recall < 100%); no metadata filtering |
| **Retrieve** | top-k by cosine, hybrid with BM25, metadata filters (date, product), re-ranking | right chunk ranked 12th; filters missing |
| **Generate** | prompt with chunks + instructions to answer only from them and cite sources; say "not found" otherwise | model ignores context or blends in its own knowledge |

Barnett et al. (2024) list seven failure points, from missing content and missed top-ranked documents to answers not extracted from the context and wrong format. The two scenario pages in this track (wrong answer, at scale) practise diagnosing them.

## In practice

### In practice

#### Production defaults

- **Hybrid retrieval** (BM25 + dense, fused with RRF) plus a **re-ranker** on the top 20–50; see Advanced RAG.

- **Metadata** on every chunk (source, section, date, access rights) for filtering, citations and permission checks.

- **Index choice:** HNSW for up to tens of millions of vectors in memory; IVF with product quantization (FAISS) or disk-based indexes for larger corpora; keep exact search for small collections. Measure recall@k of the ANN index against exact search.

- **Prompt:** put the most relevant chunks first or last (models use the middle of long contexts less well), number them, and require citations; instruct the model to say when the answer isn't in the context.

- **Freshness:** incremental re-indexing when documents change, and remove old versions.

Go deeper: Parsing and Chunking, Embeddings and Vector Indexes, Permissions and Poisoning and Keeping an Index Current. If your documents are small, you may not need an index: see When Not to Index.

#### Retrieval quality caps answer quality

RAG gives the model the right passages at question time; the generator can only be as good as what retrieval hands it, so most of the engineering goes into parsing, chunking, indexing and ranking.

### The answer that sounds right

#### "Just use a vector database"

It sounds right, since vector search is the part everyone talks about. But parsing, chunking and ranking matter more, and retrieval quality caps answer quality. RAG doesn't eliminate hallucination either: the model can still ignore or misread the context, so you have to measure faithfulness.

## Say it

### How do you build RAG, and how big should a chunk be?

#### The interviewer pushes further

Follow-up 1 of 3

How do you choose the embedding model?

Shortlist from MTEB for retrieval in your languages and domain, then test recall@k on a few hundred real queries with labelled relevant chunks; consider cost, dimension and latency.

Follow-up 2 of 3

HNSW vs IVF-PQ?

HNSW gives high recall and low latency but stores full vectors plus a graph in memory; IVF-PQ compresses vectors and scales to billions with some recall loss.

Follow-up 3 of 3

How do you handle access control?

Store permissions as chunk metadata and filter at retrieval time (before ranking), so users never retrieve documents they can't see.

#### The 30-second answer

RAG retrieves relevant passages from your own data at query time and puts them in the prompt, so answers are grounded, up to date and citable without retraining. Offline you parse documents, chunk them with some overlap or by structure, embed each chunk and store it in a vector index such as HNSW, with metadata. Online you embed the query, retrieve top-k with hybrid BM25 plus dense search and metadata filters, re-rank, and prompt the model to answer only from the context with citations or say it can't find it. Chunking is a key trade-off: small chunks split answers, large chunks add noise and cost. I'd evaluate retrieval recall and answer faithfulness separately.

**Go further**

#### What not to say

- "Just use a vector database." Parsing, chunking and ranking matter more.

- "RAG eliminates hallucination." The model can still ignore or misread the context.

**Key terms and sources**

How a retrieval-augmented generation system is built: ingestion and parsing, chunking (size, overlap, structure), embedding models, vector databases and approximate nearest-neighbour indexes (HNSW, IVF), retrieval, prompt assembly with citations, and the failure points at each stage · built from Lewis et al. (RAG, NeurIPS 2020), Karpukhin et al. (DPR, EMNLP 2020), Malkov & Yashunin (HNSW, TPAMI 2018), Johnson et al. (FAISS, 2019), Muennighoff et al. (MTEB, EACL 2023), Liu et al. (Lost in the Middle, TACL 2024) and Barnett et al. (Seven Failure Points When Engineering a RAG System, 2024) · checked 29 Oct 2026

#### Sources

1. P. Lewis et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks", NeurIPS 2020, arXiv:2005.11401; V. Karpukhin et al., "Dense Passage Retrieval", EMNLP 2020, arXiv:2004.04906.

2. Y. Malkov & D. Yashunin, "Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs", TPAMI 2018, arXiv:1603.09320; J. Johnson, M. Douze & H. Jégou, "Billion-scale similarity search with GPUs" (FAISS), 2019, arXiv:1702.08734.

3. N. Muennighoff et al., "MTEB: Massive Text Embedding Benchmark", EACL 2023, arXiv:2210.07316.

4. S. Barnett et al., "Seven Failure Points When Engineering a Retrieval Augmented Generation System", CAIN 2024, arXiv:2401.05856; N. Liu et al., "Lost in the Middle", TACL 2024, arXiv:2307.03172.
