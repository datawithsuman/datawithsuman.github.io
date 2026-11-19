# Search: BM25, Dense and Hybrid Retrieval

> Why does RAG search miss exact names, and how does hybrid fix it?

- Track: Fundamentals › NLP Fundamentals › Tagging, retrieval and evaluation
- Type: Concept · 25 min
- Page: https://aimlrounds.com/tracks/fundamentals/search-and-retrieval/
- Before this: Bag-of-Words, N-grams and TF-IDF (`fundamentals/bag-of-words-and-tf-idf`), Embeddings and Representation Learning (`fundamentals/embeddings`)
- Related: RAG End to End (`ai-engineering/rag-end-to-end`)
- Quiz topic: `nlp`

## Intuition

### The situation

The app's search box gets exact names like "paradise biryani", vague cravings like "fiery rice dish" and mixtures of both. A teammate says to replace keyword search with embeddings, since they understand meaning. The interviewer asks:

> Why does search miss exact names, and how does hybrid fix it?

**Running example:** the app's search box over 12 restaurant listings. Customers type exact names ("paradise biryani"), vague cravings ("fiery rice dish") and mixtures ("cheesy pizza late night").

#### Rank millions of documents in milliseconds

Comparing a query against every document with a large model is far too slow for a search box or a RAG pipeline. Retrieval needs an index that returns the top few dozen candidates almost instantly, and those candidates must contain the right answer, because later stages (re-rankers, the LLM) can only work with what retrieval hands them.

### The idea

Think of two librarians. One checks the catalogue for your exact words: great for a name, useless if you say "fiery" and the book says "spicy". The other understands what you're after but is hazy on exact names. So you ask both and merge their lists.

[Figure: For the query bawarchi biryani, Bawarchi ranks first with BM25, third with dense and second with hybrid. For fiery rice dish, BM25 finds none of the three spicy rice places, while dense and hybrid each find two.]

_Results from the lab, on 12 listings. The dense vectors are hand-built stand-ins for a trained model._

### Play

**Try to break it.** Run "bawarchi biryani", then "fiery rice dish", then the mixed query, comparing the three columns. Then change BM25's k₁ and b.

#### BM25 vs dense vs hybrid on 12 listings

Each column: the top 3 results; green = relevant. Dense vectors come from a small hand-built concept map (rice, spicy, cheese, late-night…) standing in for a trained embedding model (illustrative). Hybrid = reciprocal rank fusion of the BM25 and dense rankings with k = 60.

For the exact name **"bawarchi biryani"**, BM25 ranks Bawarchi first: the rare word "bawarchi" carries the score (MRR 1.00). Dense retrieval only "sees" biryani and ranks it **third**, behind the listing that is purest biryani (MRR 0.33). For **"fiery rice dish"** it's the reverse: BM25 matches only the word "rice", in Royal Pulao's "jeera rice", and finds **none** of the three spicy rice places (recall@3 0%), while dense retrieval maps fiery → spicy and rice dish → biryani / pulao and finds two of three. **Hybrid** is never the worst: Bawarchi stays in its top 3 (rank 2) and it keeps dense's 67% on the craving query. That robustness, rather than winning every query, is why hybrid is the common default for RAG. (Drag b to 0 to switch off length normalisation and watch the long Paradise listing gain score.)

**Now say why:** why does each method fail on the other's query, and why is hybrid never the worst?

## Maths

### Maths

#### In one breath

Retrieval ranks documents by relevance to a query, and it's the first step of search engines and **RAG**. **Sparse** retrieval matches exact words through an **inverted index**; its standard scoring function, **BM25**, is TF-IDF with two fixes: repeated words **saturate** (k₁) and long documents are **normalised** (b). It's fast, needs no training and is great for exact names, codes and rare terms, but it misses synonyms. **Dense** retrieval embeds queries and documents into vectors and finds nearest neighbours, so "fiery rice dish" can match "spicy biryani", but it can blur exact names. **Hybrid** search combines both, often with **reciprocal rank fusion**, and a **re-ranker** (cross-encoder) can re-score the top results.What you'll be able to do after this: compute a BM25 score, explain k₁ and b, choose between sparse, dense and hybrid retrieval, and evaluate with recall@k and MRR.

#### BM25: TF-IDF that saturates and normalises

$$ \mathrm{BM25}(q,d) = \sum_{t\in q} \mathrm{IDF}(t)\cdot \frac{f(t,d)\,(k_1+1)}{f(t,d) + k_1\big(1 - b + b\,\frac{|d|}{\mathrm{avgdl}}\big)} $$

Robertson & Zaragoza, "The Probabilistic Relevance Framework: BM25 and Beyond", _Foundations and Trends in IR_ 3(4), 2009. BM25 is the default similarity in Lucene / Elasticsearch / OpenSearch. TF-IDF: TF-IDF lesson.

- **IDF**: Rare query words count more, as in TF-IDF. BM25 uses log(1 + (N − df + 0.5)/(df + 0.5)).

- **saturating term frequency**: More occurrences help, but with diminishing returns: the score approaches (k₁ + 1) instead of growing forever. k₁ ≈ 1.2–2.

- **length normalisation**: Long documents mention everything more often, so their term counts are discounted relative to the average length. b = 0 turns this off, b = 1 is full normalisation; 0.75 is typical.

#### Dense retrieval: match meaning, not words

- Encode every document once into a vector with a sentence embedding model; at query time, embed the query and return the nearest vectors (cosine / dot product) using an approximate nearest-neighbour index (HNSW, IVF-PQ).

- Encoders are trained contrastively on (question, relevant passage) pairs; DPR (Karpukhin et al. 2020) beat BM25 by 9–19 points in top-20 passage accuracy on open-domain QA.

- **The trap:** dense models trained on one domain can underperform BM25 elsewhere. On the BEIR benchmark of 18 datasets, BM25 was a strong zero-shot baseline that many dense retrievers failed to beat out of domain (Thakur et al. 2021). Exact names, product codes and rare terms are especially hard for embeddings.

## In practice

### In practice

#### Hybrid retrieval, re-ranking and metrics

$$ \mathrm{RRF}(d) = \sum_{r\in\text{rankers}} \frac{1}{k + \mathrm{rank}_r(d)} $$

- **reciprocal rank fusion**: Add up 1 / (k + rank) for each document across the rankings being fused. Only ranks are used, so BM25 scores and cosine similarities don’t need to be on the same scale. k = 60 is the usual constant (Cormack et al. 2009).

- **Re-ranking:** a cross-encoder reads query and document together and re-scores the top 50–100 candidates; much more accurate, too slow for the whole corpus (Nogueira & Cho 2019).

- **Metrics:** recall@k (did a relevant document make the top k?), MRR (1 / rank of the first relevant result, averaged over queries), nDCG (graded relevance with position discount; ranking metrics).

- **For RAG:** recall@k of the retriever caps answer quality: the LLM can't use a passage it never sees.

### The answer that sounds right

#### "Dense retrieval has replaced BM25"

It sounds right, since matching meaning seems strictly better than matching words. But on the BEIR benchmark of 18 datasets, many dense retrievers failed to beat BM25 out of domain, and exact names and product codes are especially hard for embeddings. Hybrid is standard. And measure retrieval recall by itself, because the LLM can't use a passage it never sees.

## Say it

### Why does search miss exact names, and how does hybrid fix it?

#### The interviewer pushes further

Follow-up 1 of 3

What do k₁ and b do?

k₁ controls how quickly repeated occurrences stop adding score (k₁ = 0 means presence only); b controls how much long documents are penalised (b = 0 none, b = 1 full).

Follow-up 2 of 3

Why fuse ranks rather than scores?

BM25 scores are unbounded and query-dependent while cosine similarities are in [−1, 1]; ranks are comparable without calibration.

Follow-up 3 of 3

Bi-encoder vs cross-encoder?

A bi-encoder embeds query and document separately (precomputable, fast); a cross-encoder reads them together (more accurate, must run per pair), so it's used for re-ranking.

#### The 30-second answer

Sparse retrieval uses an inverted index and BM25, which is TF-IDF with term-frequency saturation controlled by k1 and document-length normalisation controlled by b; it's fast, training-free and excellent for exact names, codes and rare terms, but blind to synonyms. Dense retrieval embeds queries and documents with a contrastively trained encoder and does approximate nearest-neighbour search, so it matches meaning, but it can miss exact terms and degrade out of domain, where BM25 is often stronger. In practice I'd use hybrid search, fusing the two rankings with reciprocal rank fusion, then a cross-encoder re-ranker on the top candidates, and measure recall@k, MRR or nDCG.

**Go further**

#### What not to say

- "Dense retrieval has replaced BM25." Hybrid is standard; BM25 remains a strong baseline.

- "Evaluate retrieval with the final answer only." Measure retrieval recall separately.

**Key terms and sources**

Finding the right documents for a query: the inverted index, BM25 (TF-IDF with saturation and length normalisation), dense retrieval with embeddings, why each fails on different queries, hybrid search with reciprocal rank fusion, re-ranking, and retrieval metrics · built from Robertson & Zaragoza (2009), Manning et al. (2008), Karpukhin et al. (DPR, EMNLP 2020), Thakur et al. (BEIR, NeurIPS 2021), Cormack, Clarke & Büttcher (SIGIR 2009) and Nogueira & Cho (2019) · checked 29 Oct 2026

#### Sources

1. S. Robertson & H. Zaragoza, "The Probabilistic Relevance Framework: BM25 and Beyond", _Foundations and Trends in Information Retrieval_ 3(4), 2009.

2. V. Karpukhin et al., "Dense Passage Retrieval for Open-Domain Question Answering", EMNLP 2020, arXiv:2004.04906.

3. N. Thakur et al., "BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models", NeurIPS 2021 Datasets & Benchmarks, arXiv:2104.08663.

4. G. Cormack, C. Clarke & S. Büttcher, "Reciprocal Rank Fusion outperforms Condorcet and individual Rank Learning Methods", SIGIR 2009.

5. R. Nogueira & K. Cho, "Passage Re-ranking with BERT", arXiv:1901.04085, 2019.

6. C. Manning, P. Raghavan & H. Schütze, _Introduction to Information Retrieval_, 2008, ch. 1, 6, 11, nlp.stanford.edu/IR-book.
