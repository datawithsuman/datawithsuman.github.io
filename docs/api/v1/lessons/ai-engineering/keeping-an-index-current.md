# Keeping an Index Current

> Documents change daily, and a better embedding model has come out. How do you keep your index current?

- Track: AI Engineering › RAG › Lessons
- Type: Concept · 18 min
- Page: https://aimlrounds.com/tracks/ai-engineering/keeping-an-index-current/
- Before this: Embeddings and Vector Indexes (`ai-engineering/embeddings-and-vector-indexes`)
- Quiz topic: `rag`
- Sources checked: 2026-11-07 · Text last changed: 2026-11-20 · Version: 75c0b2bd96

## Intuition

### The situation

An outdated refund policy keeps appearing in answers, though it was deleted weeks ago. Meanwhile, the team wants to move to a newer embedding model, and someone suggests re-embedding documents gradually in the same index. The interviewer asks:

> Documents change daily, and a better embedding model has come out. How do you keep your index current?

#### Why it matters

Tutorials end once the index is built, but real work starts there. A stale policy gives a confident wrong answer, and a deleted document that's still retrievable can be a legal problem. Migrations are expensive enough that you should plan for them. See RAG Wrong Answer for what stale data looks like from the outside.

### The idea

Think of moving a library to a new shelving system. You can't mix the two systems on one shelf, as nobody could find anything. So you set up the new shelves beside the old ones, shelve new books in both, move the rest over time, check it works, then change the signs overnight.

[Figure: Three jobs. Update what changed. Clean up deletes. Migrate models with a second index.]

_Time is usually a bigger limit than money._

### Play

**Try to break it.** Raise the chunks, then the rate limit. Then raise the tombstones.

#### Plan a migration

Exact arithmetic, at the $0.13 per million tokens used in the source's example. Batch endpoints usually run slower, which isn't modelled here. Live results assume tombstones are spread evenly among 40 search candidates.

100 million chunks of 400 tokens is 40 billion tokens: about **$5,200**, and **5.6 days** at 5 million tokens a minute. The money is small next to the time. During those days, about 2.8 million chunks change, and that's why you dual write. Raise the rate limit to 50, and it takes about half a day for the same money. Now raise tombstones to 50%: only 20 of 40 search candidates are live, so recall and speed suffer until you clean up.

**Now say why:** why do you need dual writes during a backfill?

## How it works

### How it works

#### In one breath

An index goes stale from the moment you build it. Update it **incrementally**: hash each document, and re-embed only what changed. **Deletes** are harder than they look, as graph indexes usually mark items as deleted, and those tombstones slow searches and crowd out real results until a cleanup. Changing the **embedding model** means rebuilding everything, because old and new vectors can't be compared. The safe way is a second index, dual writes, a background backfill, a recall check, then an instant switch with an alias.

#### Updates, deletes and migrations

##### Incremental updates

1. **Detect changes:** use events from the source, or compare a content hash per document or section.

2. **Re-chunk and embed only what changed:** stable section IDs avoid re-embedding a whole document for one edit.

3. **Replace, don't add:** write new chunks and remove old ones together, so the same document never appears twice in different versions.

4. **Track freshness:** store the source version and indexed time, and alert when ingestion falls behind.

##### Why deletes are hard

A node in an HNSW graph can't simply be removed, because other nodes link through it. So databases usually mark it as deleted, a **tombstone**, and clean up later. Until then, search still walks through dead nodes. If 20% of candidates are tombstones, a search for 40 candidates finds about 32 live ones. Cleanup, such as a vacuum or segment rebuild, can be slow. So plan for it, and if you have a legal duty to erase data, check when it's actually gone, including backups, caches and summaries.

The tombstone mechanism and cleanup steps here come from engineering blogs. Check your own database's documentation for exact behaviour.

##### Migrating an embedding model

| Step | What to do | Why |
|---|---|---|
| 1. Build beside it | A second index, with the new model's dimensions | The old one keeps serving |
| 2. Dual write | Embed every new or changed document with both | The new index doesn't fall behind |
| 3. Backfill | Embed history in the background | Don't overwrite a newer vector from a dual write |
| 4. Evaluate | Compare recall@k on a few hundred real queries, and optionally shadow live traffic | A newer model isn't always better for you |
| 5. Switch | Flip an alias, and keep the old index for rollback | Instant, and reversible |

##### Can you avoid re-embedding?

Drift-Adapter trains a small mapping from old vectors into the new model's space, from a sample of paired embeddings. It reports recovering 95 to 99% of the recall of a full re-embedding, at over 100 times lower recompute cost, and under 10 microseconds added per query. Treat this as a bridge. One practitioner cites a lower range of 85 to 95%, with no source, so test it on your data before relying on it.

#### The maths

$$ {\text{days}} = \frac{{N} \times {T}}{{\text{tokens per minute}} \times 1{,}440}, \qquad {\text{cost}} = {N} \times T \times {\text{price}} $$

Worked example from Tian Pan’s post: 100M chunks of 400 tokens is 40B tokens, about $5,200 at $0.13 per million, and over 5 days at 5M tokens per minute.

- **backfill time**: How long the migration runs, if nothing fails.

- **chunks**: All of them, because old and new vectors can’t mix.

- **tokens per chunk**: Larger chunks cost more.

- **your rate limit**: Often the real bottleneck, more than the price.

- **embedding cost**: Often smaller than you’d expect. Engineering time and rate limits can matter more.

- **chunks again**: The same count.

- **price per token**: Batch endpoints may cost less, but take longer.

## In practice

### In practice

#### In practice

- **Version everything:** store the embedding model and chunker version with each chunk, so you know what needs rebuilding.

- **Never mix models:** query and document vectors must come from the same model and version.

- **Keep the raw text:** you can't re-embed or re-chunk what you didn't keep.

- **Watch index health:** track tombstones, recall on a fixed test set, and ingestion lag. Set a cleanup rule.

- **Test before you upgrade:** run your golden queries against the new model, because a higher benchmark score doesn't guarantee a gain on your data.

### The answer that sounds right

#### "We'll re-embed gradually, in the same index"

It sounds right, as it avoids a big switch. But vectors from two models live in different spaces, so their similarity scores mean nothing together. A query can only match one of them. Use a second index, or a second named vector, then switch once it's complete and tested.

## Say it

### Documents change daily, and a better embedding model has come out. How do you keep your index current?

#### The interviewer pushes further

Follow-up 1 of 3

Why can't you upgrade embeddings gradually, chunk by chunk, in one index?

Vectors from different models live in different spaces, so comparing them is meaningless, and query vectors can only match one. You need a second index, a second named vector, or an adapter that maps between the two.

Follow-up 2 of 3

Users still get answers from a deleted document. Where do you look?

The chunks may not have been removed, or they may be marked deleted but still served. Check the search filter, and look at caches, summaries, semantic caches and any graph built from it. Then add a test that deletes a document and checks that it can't be retrieved.

Follow-up 3 of 3

How often should you re-index?

Update content as it changes, on events if you can. Do full rebuilds only when the chunker or model changes, or when tombstones and drift hurt recall. Let your freshness needs and a fixed recall test decide.

#### The 30-second answer

I'd update incrementally: detect changes with events or content hashes, re-embed only changed sections, and replace old chunks with new ones together. Deletes need care, as graph indexes usually leave tombstones, which slow search and crowd out real results until cleanup, so I'd track them. For a new embedding model, vectors can't be mixed, so I'd build a second index, dual write new documents, backfill history, compare recall on real queries, then flip an alias and keep the old index for rollback. 100 million chunks of 400 tokens costs about $5,000, but takes over 5 days at 5 million tokens a minute, so rate limits often set the schedule. An adapter can bridge the gap, but test it.

**Key terms and sources**

Incremental updates and hashing, why deletes are hard in HNSW, tombstones and vacuuming, migrating embedding models with dual writes and an alias, costs, and adapters. · checked 7 Nov 2026

#### Sources

- [Tian Pan, Retiring an embedding model](https://tianpan.co/blog/2026/07/05/retiring-an-embedding-model-reindex-without-downtime)

- [Vejendla, Drift-Adapter](https://arxiv.org/abs/2509.23471)

- [Doug Turnbull, Updating a graph vector database](https://softwaredoug.com/blog/2026/08/18/update-graph-vector-db)

- [Deletion that reaches the vector index](https://dev.to/multigrid/deletion-that-reaches-the-vector-index-5bf1)

- [Vector database GDPR erasure and HNSW soft deletes](https://particula.tech/blog/vector-database-gdpr-erasure-hnsw-soft-delete)

Explanations are ours, built from these sources. Lab numbers are illustrative unless a lab says otherwise. Most recent papers are preprints.
