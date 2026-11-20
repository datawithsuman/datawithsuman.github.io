# Design a Codebase Q&A Assistant

> Engineers ask questions about a company's code, spread across thousands of repositories. Design an assistant that finds the right code and answers with it.

- Track: System Design › RAG and Search › Designs
- Type: Design · 25 min
- Page: https://aimlrounds.com/tracks/system-design/design-codebase-qa/
- Before this: Parsing and Chunking (`ai-engineering/parsing-and-chunking`), Keeping an Index Current (`ai-engineering/keeping-an-index-current`)
- Quiz topic: `sdllm`

## Intuition

### The situation

A company has thousands of code repositories, much of it old. Engineers lose hours finding where things are handled and how services are called. Leadership wants an assistant that answers questions about the codebase. The interviewer asks:

> Engineers ask questions about a company's code, spread across thousands of repositories. Design an assistant that finds the right code and answers with it.

#### Ask before designing

- **Who asks what:** engineers asking "where is X handled?", "how do I call this service?" or "why does this fail?". Most questions are plain English, some paste code.

- **Scale:** thousands of repositories, millions of lines, much of it old code.

- **Freshness:** code changes all day, so answers must reflect today's main branch.

- **Must never happen:** code from a repository the engineer can't see appearing in the answer, or confident answers about functions that don't exist.

- **Success metrics:** retrieval quality (did the right file come back?), answer acceptance, and time saved, plus latency of a few seconds.

### The idea

Think of a librarian in a huge archive. They don't search every shelf; they go to the right rooms first. Some requests name an exact title, so the catalogue is fastest; others describe a topic, so they need to understand meaning.

[Figure: Route the question to a few repositories. Retrieve chunks with keywords and embeddings. Pack the best into the token budget. Answer with file citations. The index updates on every merge.]

_Narrow first, and match the retriever to the question._

### Play

**Try to break it.** Compare the three retrievers on English questions. Then switch to code queries.

#### The answer depends on the question type

From the paper: section 4.2 and Table 1 (English question to code, NDCG and latency) and section 4.3 (code completion, exact match at 16K tokens). The commercial model wasn't tested for completion.

Start with English questions: the commercial code embeddings win clearly, but take far longer. Switch to code queries: BM25 wins on quality **and** speed. That's why a Q&A assistant, whose queries are mostly English, needs embeddings, and why autocomplete often doesn't.

**Now say why:** why can keyword search beat embeddings for code-to-code queries?

## Architecture

### Architecture

#### In one breath

First pick the **few repositories** likely to matter, then search inside them. Chunk code along its structure, but keep the class name and imports with each piece. Use **keyword search (BM25)** when the query is code, and **embeddings** when it is a plain-English question. Pack the best chunks into the **token budget** in rank order, keep the index fresh as code changes, and answer with file links.

#### Narrow, retrieve, pack, answer

1. **Route to repositories:** use repository metadata and summaries to pick the top 5 to 10 likely repositories, or let the user choose them.

2. **Retrieve chunks:** search inside those repositories with keyword search, embeddings or both, filtered by the user's access rights.

3. **Rerank:** merge results from all sources (search, open files in the editor) into one ranking. An LLM or cross-encoder can filter the top few.

4. **Pack:** add the best chunks to the prompt in rank order until the token budget is full; drop the rest.

5. **Answer:** the LLM answers only from that context and links each claim to a file and line.

##### Chunking code

Split along functions and classes, but re-attach what each piece needs: a method keeps its class definition and imports. One team aims for chunks around 500 characters and adds a short English description of each chunk before embedding, so plain-English questions match code.

##### Keyword or embeddings?

It depends on the query. When the query is code (finish this line), BM25 over words is strong and fast. When the query is English (find the bug for this issue), good code embedding models win, at a much higher cost. Many systems run both.

#### The numbers worth saying out loud

All of these are assumptions for the interview, not figures from a real system.

| Question | Working | Result |
|---|---|---|
| Code size | 3,000 repos × 200,000 lines × 40 characters | **24 billion characters** |
| Chunks | 24 billion ÷ 500 characters | **about 48 million** |
| Vector storage | 48 million × 1,024 dimensions × 2 bytes | **about 100 GB** |
| Re-embedding a day | 2% of chunks change | **about 1 million chunks** |

Narrowing to 5 to 10 repositories first cuts each search from 48 million chunks to well under a million, which keeps latency low.

## In practice

### In practice

#### What every codebase assistant gets asked

- **Freshness:** indexing is continuous, not a nightly job. Re-index only changed files on each merge, using stable chunk IDs so updates overwrite and deleted code is removed.

- **Permissions:** filter by the user's repository access inside the search, never after the LLM has seen the code.

- **Context budget:** with small budgets, chunks of 32 to 64 lines work best; with around 16,000 tokens, whole files become competitive. Rank order matters: pack the best first.

- **Cheap signals:** file paths and import statements help find the right files a lot, and they cost almost nothing.

- **Where code lives:** sending code to an outside embedding API may be forbidden. One team dropped embeddings partly for this reason and used its keyword search engine instead.

- **Hallucination:** require file and line citations, and check that cited symbols really exist before showing the answer.

##### Evaluation

Build a set of real questions with the files that answer them. Track recall of the right file in the top results, answer acceptance, and how often engineers open the cited files.

#### What the real systems reported

- **Keyword-first:** one assistant first used embeddings, then switched to its existing search engine with an adapted BM25 ranking, citing sending code to a third party, keeping vectors updated, and cost at over 100,000 repositories. It then ranks snippets from all sources together and takes the top N.

- **Embedding-first:** another team chunks with language-aware parsing, keeps class and import context with each chunk, adds English descriptions, retrieves by embeddings and uses an LLM to filter and rank, with repositories narrowed first.

- **Benchmark:** for code-to-code retrieval, BM25 with word splitting beat dense models and was much faster; for English-to-code, commercial code embeddings won but were about 100× slower. Simple line-based chunks matched syntax-aware ones, and retrieval latency varied up to 200× across setups.

From the two posts (2024) and the paper (Oct 2025). The paper tested retrieval inside one repository, not routing across thousands.

### The answer that sounds right

#### "Embed every file and use vector search"

It sounds modern, but for code queries keyword search matched or beat embeddings in a benchmark and was far faster, and embeddings bring cost, freshness and data-sharing problems. Use embeddings where they clearly win: plain-English questions.

## Say it

### Engineers ask questions about a company's code, spread across thousands of repositories. Design an assistant that finds the right code and answers with it.

#### The interviewer pushes further

Follow-up 1 of 3

Why not just use embeddings for everything?

For code-to-code queries, BM25 matched or beat embeddings in a benchmark and was far faster. Embeddings also mean sending code to a model, storing vectors and keeping them in sync. Use them where they clearly win: English questions.

Follow-up 2 of 3

A function was renamed an hour ago, and the assistant still cites the old name. What failed?

Freshness. The index should update on each merge, with stable chunk IDs so the new version replaces the old and deleted code is removed. Also check cited symbols exist before showing the answer.

Follow-up 3 of 3

How big should chunks be?

It depends on the context budget. With small budgets, 32 to 64 lines worked best in a benchmark; with about 16,000 tokens, whole files became competitive. Very small chunks of 8 to 16 lines did worse.

#### The 30-second answer

First I'd clarify the users, the number of repositories, how fresh answers must be and access rules. With thousands of repositories, I'd route first: pick the top 5 to 10 likely repositories from metadata and summaries, then search inside them. I'd chunk code along functions and classes, keeping class definitions and imports with each chunk, and add a short English description to help plain-English questions match. Retrieval depends on the query: BM25 is strong and cheap for code queries, while code embeddings win for English questions, so I'd run both and merge them. A reranker picks the best, and I pack chunks into the token budget in rank order. Access filtering happens in the search. The index updates continuously on every merge. Answers must cite files and lines, and I'd evaluate with real questions and their known answer files.

**Key terms and sources**

Based on published write-ups: a code search company's post ["How Cody understands your codebase"](https://sourcegraph.com/blog/how-cody-understands-your-codebase) (Feb 2024), a code review company's post ["RAG for a Codebase with 10k Repos"](https://www.qodo.ai/blog/rag-for-large-scale-code-repos/) (Jul 2024), and the benchmark paper ["Practical Code RAG at Scale"](https://arxiv.org/abs/2510.20609) (arXiv 2510.20609, Oct 2025). The lab uses the paper's numbers; the estimate is ours. Uses chunking, hybrid retrieval and keeping an index current. · checked 15 Nov 2026
