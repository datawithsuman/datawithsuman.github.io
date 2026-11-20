# Design an Enterprise RAG System

> Design a system that answers employees' questions across 10 million internal documents, respecting who can see what.

- Track: System Design › RAG and Search › Designs
- Type: Design · 30 min
- Page: https://aimlrounds.com/tracks/system-design/design-enterprise-rag/
- Before this: Permissions and Poisoning in RAG (`ai-engineering/permissions-and-poisoning`), Advanced RAG: Hybrid Search, Re-ranking, Query Rewriting and GraphRAG (`ai-engineering/advanced-rag`)
- Quiz topic: `sdllm`

## Intuition

### The situation

Employees waste hours hunting across wikis, tickets, PDFs and chat. Leadership wants one assistant that answers from all of it, across 10 million documents. Legal insists nobody sees anything they couldn't already open. The interviewer asks:

> Design a system that answers employees' questions across 10 million internal documents, respecting who can see what.

#### Ask before designing

- **Scale:** say 10 million documents, about 50 chunks each, with 100,000 employees and a peak of 100 questions a second.

- **Sources:** wikis, tickets, chat, PDFs and code? Each needs its own connector and parser.

- **Permissions:** do they differ per document? How quickly must a removal take effect?

- **Freshness:** minutes for tickets, or hours for policies?

- **Latency:** say first token under 2 seconds at p95.

- **Must never happen:** showing someone a document they can't access, or inventing a policy.

### The idea

Think of a very large company's records office with one helpful clerk. The clerk must keep the files tidy and current, check your badge before fetching anything, find the right pages fast, and quote them exactly. If nothing fits, the clerk says so, rather than guessing.

[Figure: Two paths. Offline: connect, parse, chunk and index with permissions. Online: check access, search, re-rank and answer with citations.]

_Permissions and freshness make it hard._

### Play

**Try to break it.** Grow the documents. Switch the vector type. Then raise the peak questions.

#### What does this cost at scale?

Illustrative: 1,024 dimensions, HNSW at M = 16, 100 candidates re-ranked per question, 400 tokens per chunk and a 1,000-token prompt. The text itself and BM25 add more storage.

10 million documents means about 500 million chunks, and about **2.1 TB** for float32 vectors with links. That's several large memory machines. Switch to **binary**, and it falls to about 128 GB, though you'd keep full vectors on disk for rescoring. At peak, re-ranking 100 candidates per question is 10,000 pairs a second, and that needs real GPU capacity. The LLM reads about 420,000 tokens a second, so sending 8 chunks rather than 16 cuts that by over 40%. Filter first, and you may not need to search everything.

**Now say why:** what dominates running cost, and what dominates setup cost?

## Architecture

### Architecture

#### In one breath

Offline, connectors pull documents with their permissions, parse them, chunk them on structure, and store text, vectors and metadata. Online, resolve the user's access first, run hybrid search filtered by that access, re-rank, and answer with citations, or say it can't find the answer. Permissions and freshness are what make it hard. Fail closed, delete quickly, and judge every change on a test set of real questions.

#### Offline and online

##### Offline: indexing

1. **Connectors** pull content, permissions and change events from each source.

2. **Parsing** keeps tables and headings. Check by source type, since one parser rarely fits all.

3. **Chunking** follows structure, then adds a short context line where it helps.

4. **Enrichment** stores source, section, date, version and permission parents with each chunk.

5. **Indexing** writes to a vector index and a BM25 index, with the raw text kept for rebuilds.

##### Online: answering

1. **Resolve access:** get the user's allowed parents. If this fails, stop.

2. **Understand the question:** resolve follow-ups using chat history, and split multi-part questions.

3. **Search:** hybrid search with the access filter applied during search.

4. **Re-rank:** take about 100 candidates down to about 10.

5. **Live check:** optionally check the final chunks against the source, for sensitive content.

6. **Generate:** answer only from numbered chunks, with citations, or say it wasn't found.

7. **Verify:** check that cited IDs exist, and that any numbers appear in the source.

##### Key choices

| Choice | Default | Why |
|---|---|---|
| Retrieval | Hybrid plus re-ranker | Employees search with exact names and codes, as well as loose descriptions |
| Permissions | Parent-level filter, plus a live check for sensitive sources | Avoids syncing every document, and still handles revocation |
| Agents | Fixed pipeline first, with a loop only for hard questions | Easier to test, and cheaper |
| Graphs | Only if evaluation shows a need | Simple relations in documents can do as well |
| Tenancy | One index with filters, or a separate index for the most sensitive data | A trade-off between cost and isolation |

#### The numbers worth saying out loud

All of these are assumptions for the interview.

| Question | Working | Result |
|---|---|---|
| Chunks | 10M documents × 50 | 500 million |
| Vector memory | 500M × 1,024 × 4 bytes | About 2 TB |
| First embedding run | 500M × 400 tokens × $0.13 per million | About $26,000 |
| Backfill time | 200B tokens at 10M a minute | About 14 days, so ask for a higher limit, or run on your own GPUs |
| Daily changes | 1% of 500M chunks | 5 million re-embeds a day |
| Latency budget | Access 50 ms, search 100 ms, re-rank 200 ms, first token 1 s | About 1.4 seconds at p95 |

The LLM usually dominates running cost and latency, while embedding and memory dominate the setup. Permission checks are cheap but must not be skipped.

## In practice

### In practice

#### What the interviewer will push on

- **Quality and evaluation:** keep a golden set per source, with real questions, expected chunks and answers, plus no-answer and access tests. Score retrieval and faithfulness separately, as they can move independently.

- **Permissions:** test that user A can't get user B's documents, make failures return nothing, and cover caches and summaries too.

- **Freshness and deletes:** use change events, re-embed only changed sections, and test that a deleted document really can't be retrieved.

- **Conflicts:** prefer the current version using metadata, remove superseded copies, and show real disagreements.

- **Poisoning and injection:** employees and outsiders can edit many sources. Treat retrieved text as data, and limit tools.

- **Reliability:** if the re-ranker fails, fall back to hybrid order. If the LLM fails, show the search results.

- **Cost:** cache answers per permission set only, route simple questions to cheaper models, and cap agent loops.

- **Scaling:** shard by tenant or source, and filter first. A result measured on a small corpus may not hold at full size, so re-test at scale.

- **Online signals:** track thumbs-down, re-asks, clicks on citations and escalations, and review samples.

#### What published work says

- **Parsing came first:** Uber found no universal PDF parser, moved its policy documents to a more structured format, and kept tables whole with their own summaries and keywords.

- **Query steps helped:** Uber added steps that rewrite the query, narrow down the source documents, and tidy results. It reported 27% more acceptable answers, and 60% less incorrect advice, relative to its earlier system, on 100+ test queries.

- **Upgrades don't simply add up:** in the 450-setup study, three upgrades predicted +47% but delivered +17%, and the best setup changed as the corpus grew past about 25K documents.

- **Retrieval and faithfulness differ:** that study found they were essentially unrelated, so measure both.

- **Permissions have several patterns:** identity forwarding, cached filters with live checks, and parent-level filters are all in use, with different costs.

### The answer that sounds right

#### "Build one index, and filter the results at the end"

It sounds simple, since the same search serves everyone. But filtering after search leaves too few results for users with narrow access, and any bug or outage may expose everything. Caches and summaries can leak too. Make access part of retrieval, and test that it fails closed.

## Say it

### Design a system that answers employees' questions across 10 million internal documents, respecting who can see what.

#### The interviewer pushes further

Follow-up 1 of 3

Where do you enforce permissions, and why not after the LLM?

At retrieval, before anything reaches the model. After generation, the text may already appear in the answer, or in logs and caches. I'd use a filter during search, and a live check on sensitive sources, and fail closed on any error.

Follow-up 2 of 3

Can you cache answers?

Only carefully, because two users asking the same question may be allowed to see different documents. Key any cache by permission set and document version, or cache retrieval results per user. Otherwise, a cache becomes a leak.

Follow-up 3 of 3

Quality dropped after adding 3 million documents. What do you check?

Look for new near-duplicates and stale versions first, then recall on the golden set by source. Check whether filters and index settings still hold recall at this size. Results measured at a smaller scale may not carry over, so a setup may need re-tuning.

#### The 30-second answer

I'd clarify scale, sources, permissions and freshness first. Offline, connectors pull content and permissions. I'd parse carefully, keep tables whole, chunk on structure, and store text, vectors and metadata, including permission parents. Online, I'd resolve the user's access first, and if that fails, return nothing. Then hybrid search with that filter applied during search, a re-ranker from about 100 candidates to about 10, and generation from numbered chunks with citations, or saying it can't find the answer. At 500 million chunks, float32 vectors alone need about 2 TB, so I'd consider int8 or binary with rescoring, and I'd measure recall under real filters. For freshness, I'd use change events and re-embed only what changed, and for a new embedding model, a second index with dual writes and an alias. I'd keep a golden set with no-answer and access tests, score retrieval and faithfulness separately, and run it on every change. I'd start with a fixed pipeline, and add an agent loop only for the questions that need it.

**Key terms and sources**

Built from published work: [Uber's agentic RAG post](https://www.uber.com/en-CA/blog/enhanced-agentic-rag/), [Anthropic's Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval), [a 450-setup study](https://arxiv.org/abs/2610.29722) and [WorkOS on access control](https://workos.com/blog/rag-access-control-document-permissions). It isn't any one company's design, and the volumes and lab numbers are our own illustrations. Uses parsing, permissions and keeping an index current. · checked 7 Nov 2026
