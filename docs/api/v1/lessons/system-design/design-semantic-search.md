# Design Semantic Product Search

> Shoppers type long, specific queries, and keyword search returns nothing useful for them. Design search that understands meaning, without breaking exact matches like model numbers.

- Track: System Design › RAG and Search › Designs
- Type: Design · 25 min
- Page: https://aimlrounds.com/tracks/system-design/design-semantic-search/
- Before this: Embeddings and Vector Indexes (`ai-engineering/embeddings-and-vector-indexes`), Advanced RAG: Hybrid Search, Re-ranking, Query Rewriting and GraphRAG (`ai-engineering/advanced-rag`)
- Quiz topic: `sdrec`

## Intuition

### The situation

An online retailer with millions of products sees many long, specific searches, like "waterproof hiking boots for wide feet". Keyword search returns poor results for these, but works well for exact product names and model numbers. The interviewer asks:

> Shoppers type long, specific queries, and keyword search returns nothing useful for them. Design search that understands meaning, without breaking exact matches like model numbers.

#### Ask before designing

- **Catalogue:** how many products, and how good are titles and attributes?

- **Queries:** what share are short head queries like "milk", and what share are long tail ones like "waterproof hiking boots for wide feet"?

- **Latency:** say the whole search must return in 200 ms, so retrieval gets a few tens of milliseconds.

- **Must keep working:** exact matches on product IDs, brands and model numbers, plus filters and facets.

- **Success metrics:** recall of relevant products, relevance ratings, add-to-cart and conversion, with no added latency.

### The idea

Think of a shop with two assistants. One knows every product code by heart; the other understands what you mean when you describe what you need. You ask both at once, and the manager puts their suggestions in the best order.

[Figure: The query goes to the keyword index and the embedding index in parallel. Results are merged, then the re-ranker orders them.]

_Keep exact matching, and add meaning beside it._

### Play

**Try to break it.** Drag the embedding size down from 768 to 64. Then turn on hard negatives.

#### How small can the embedding get?

From the paper: Table 5 (linear projection to smaller sizes, recall@40 relative to the 768 model), Table 4 (hard negatives, +5.15%) and Table 1 (ANN service at the best tested setting: 98.94% recall@20 in 12.8 ms at 256 dimensions, 98.84% in 12.9 ms at 768). Adding the two effects together is our simplification.

Drag the size down: 368 and 256 cost almost nothing, then recall falls off a cliff. A smaller embedding means a **cheaper index that can be refreshed more often**, which matters when the catalogue changes daily. Now turn on hard negatives: picking difficult wrong products during training helps more than any size change.

**Now say why:** why does a smaller embedding make the whole system easier to run?

## Architecture

### Architecture

#### In one breath

Keep the **keyword index** for what it's good at, exact product IDs and model numbers, filters and facets, and add **embedding-based retrieval** for meaning, synonyms and misspellings, especially on long-tail queries. A **two-tower** model embeds queries and products; train it on engagement with **hard negatives**, shrink the embedding to keep the index cheap, merge both result sets, and let the existing **re-ranker** order them. Prove it with human ratings and interleaving.

#### Two retrievers, one ranked list

1. **Query planner:** decides whether a query goes to semantic retrieval, typically tail queries, and builds the keyword query.

2. **Query embedding:** a small transformer encodes the query at request time.

3. **Two fetchers in parallel:** the keyword index returns exact and filtered matches; an approximate nearest neighbour (ANN) index returns products with the closest embeddings. ANN results are cached for repeated queries.

4. **Merge:** remove duplicates and combine both sets.

5. **Re-rank:** a gradient-boosted ranker scores everything with query, product and engagement features, now including the query–product embedding similarity.

##### The model

A two-tower (Siamese) transformer embeds the query and the product separately, and their cosine similarity is the score. Products are embedded offline from the title plus a few key attributes like category, brand, colour and gender; queries are embedded online. Training uses engagement: purchases score highest, then clicks, then impressions.

##### Why keep keyword search?

Embeddings blur rare tokens like product IDs and model numbers, and the keyword index already supports facets and filters that are hard to rebuild. Hybrid gives you both.

#### The numbers worth saying out loud

All of these are assumptions for the interview, not figures from a real system.

| Question | Working | Result |
|---|---|---|
| Index size at 768 dims | 10 million products × 768 × 4 bytes | **about 31 GB** |
| Index size at 256 dims | 10 million × 256 × 4 bytes | **about 10 GB** |
| Queries per second at peak | given | **5,000** |
| Semantic queries at peak | 5,000 × 30% tail | **1,500 per second** |
| Re-embedding the catalogue | 10 million ÷ 2,000 per second per GPU | **about 1.4 GPU-hours** |

A third of the storage means the index fits in less memory and can be rebuilt quickly when products change.

## In practice

### In practice

#### What every search design gets asked

- **Labels from engagement:** score each query–product pair from purchases, clicks and impressions, with purchases highest. Distinguishing purchased from merely clicked items matters a lot.

- **Hard negatives:** random negatives are too easy. Mine the model's own top results, keep only ones that are clearly wrong (for example, a different product type), and add in-batch hard negatives.

- **Measuring recall honestly:** you can't label every relevant product. Use a golden set of known relevant items, plus a category-level check that flags results from unrelated categories.

- **Latency:** a bigger query encoder can double tail latency. Use a small distilled model, fixed input length and a GPU for the query encoder; cache ANN results.

- **Which attributes help:** title plus a few key attributes helps; long descriptions often add noise and no gain.

- **Online proof:** human relevance ratings on tail queries and interleaving tests on add-to-cart, before a full A/B test.

##### Rollout

Start with tail queries only, where keyword search fails most, and keep head queries on the existing path until the hybrid proves itself.

#### What the real system reported

- **Architecture:** a query planner, an ANN fetcher with a result cache alongside the existing Solr keyword fetcher, merged and passed to a gradient-boosted re-ranker that uses the BERT similarity as a feature.

- **Model:** a Siamese DistilBERT (6 layers), trained on a year of engagement data, top 2 million queries, with a softmax loss over 20 products per query. Adding category, brand, colour and gender to the title helped; more attributes didn't.

- **Negatives and size:** hard negatives gave +5.15% recall@40; a linear projection to 256 dimensions kept recall while cutting storage to a third.

- **Serving:** a managed ANN service at about 13 ms for 99% recall@20 at 256 dimensions; the 6-layer query encoder nearly doubled p99 latency on CPUs, fixed by serving it on GPUs.

- **Online results:** human ratings on tail queries improved NDCG@5 by about 2% and NDCG@10 by about 3%; interleaving showed more add-to-carts.

The paper's own figures (KDD 2022).

### The answer that sounds right

#### "Embeddings understand meaning, so drop keyword search"

It sounds right, since semantic search handles synonyms and long queries. But embeddings blur rare exact tokens like model numbers and product IDs, and you'd lose filters and facets the keyword index already provides. Run both, and let the re-ranker combine them.

## Say it

### Shoppers type long, specific queries, and keyword search returns nothing useful for them. Design search that understands meaning, without breaking exact matches like model numbers.

#### The interviewer pushes further

Follow-up 1 of 3

Why not replace keyword search entirely?

Embeddings blur rare tokens like model numbers and IDs, and the keyword index already handles filters and facets well. Hybrid keeps exact matching where it's best and adds meaning where keywords fail.

Follow-up 2 of 3

Recall looks great offline, but results look unrelated. What's wrong?

The golden set only knows some relevant items, so recall can look high while the rest of the results come from the wrong category. Add a category-level check, and use human ratings on a sample.

Follow-up 3 of 3

The query encoder adds 50 ms. How do you fix it?

Use a smaller distilled model, fix the input length to avoid dynamic shapes, serve it on GPUs, cache embeddings and ANN results for frequent queries, and only call semantic retrieval for queries that need it.

#### The 30-second answer

First I'd clarify the catalogue size, the mix of head and tail queries, the latency budget and what must keep working, like exact model numbers and filters. I'd build a hybrid. The existing keyword index stays for exact matches and facets. Alongside it, a two-tower transformer embeds the query at request time and products offline, and an ANN index returns the closest products. Both run in parallel, results are merged and de-duplicated, and the gradient-boosted re-ranker orders them, with the embedding similarity as a new feature. I'd train on engagement, with purchases scored above clicks, and use hard negatives mined from the model's own results, filtered to remove products that are actually relevant. I'd shrink the embedding with a linear projection, since 256 dimensions keeps recall at a third of the storage. For latency, a small query encoder on GPUs and cached ANN results. I'd measure recall on a golden set, then prove it with human ratings and interleaving, starting with tail queries.

**Key terms and sources**

Based on a retailer's published paper: ["Semantic Retrieval at Walmart"](https://arxiv.org/abs/2412.04637) (KDD 2022). The lab uses the paper's own reported numbers; the estimate is ours. Uses embeddings and vector indexes, hybrid search and re-ranking. · checked 5 Nov 2026
