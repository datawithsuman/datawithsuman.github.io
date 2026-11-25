# Design a Text-to-SQL System

> Analysts spend too long finding tables and writing SQL. Design a system that turns their questions into queries across a huge data warehouse.

- Track: System Design › RAG and Search › Designs
- Type: Design · 25 min
- Page: https://aimlrounds.com/tracks/system-design/design-text-to-sql/
- Before this: RAG End to End (`ai-engineering/rag-end-to-end`), Advanced RAG: Hybrid Search, Re-ranking, Query Rewriting and GraphRAG (`ai-engineering/advanced-rag`)
- Quiz topic: `sdllm`
- Sources checked: 2026-11-05 · Text last changed: 2026-11-20 · Version: f2ae2b6a8d

## Intuition

### The situation

A company's analysts ask hundreds of data questions a day. Its warehouse has about 100,000 tables, many of them look-alikes, and few people know which to trust. Writing the SQL takes time, and finding the right table takes longer. The interviewer asks:

> Analysts spend too long finding tables and writing SQL. Design a system that turns their questions into queries across a huge data warehouse.

#### Ask before designing

- **Users:** analysts who can check SQL, or business users who can't? This decides how much you can rely on review.

- **Scale:** say 2,500 users, 10 questions each a day and 100,000 tables.

- **Does it run the SQL?** Generating a query to review is much safer than running it and reporting a number.

- **Must never happen:** a user seeing data they have no access to, a query changing data, or a confident number from the wrong table.

- **Success metrics:** queries accepted without edits, the right table found, time saved, and failed or costly queries.

### The idea

Think of a new analyst in a huge company. Knowing SQL isn't their problem. They ask around: which table do people use for this, and which ones are out of date? They look at old queries from colleagues, draft their own, and a test run catches mistakes before it counts.

[Figure: Retrieve candidate tables. The user confirms them. The LLM generates SQL. Code validates it before it runs read-only. An offline job summarises tables and past queries into the index.]

_Finding the table is the hard part. The SQL comes after._

### Play

**Try to break it.** Drag the tables up to 20 with no documentation. Then tick the box, and bring the tables back down.

#### How many tables should the model see?

Illustrative curves, shaped loosely on the real team's finding that documentation lifted its search hit rate from 40% up to 90%. We assume 800 tokens per table schema. Your own data sets the real curve.

Sending more tables gives you more chances, but each extra one costs tokens and gives the model another wrong option. Without documentation, even 20 tables miss the right one nearly half the time here. **Better metadata beats a bigger K.**

**Now say why:** why does sending more tables stop helping, and start to hurt?

## Architecture

### Architecture

#### In one breath

Writing SQL is the easy part. **Finding the right table among thousands is the hard part.** Offline, summarise tables and past queries, then index them. At question time, retrieve candidates, rank them by similarity and trust, and let the user confirm. Generate SQL with real column names and values, **validate it before it runs**, and show the SQL with its tables and warnings. Run it read-only, with the user's own permissions.

#### Two paths: offline and at question time

##### Offline: build the index

1. **Summarise tables:** an LLM reads the schema, the docs and recent queries, and writes what the table holds and when to use it.

2. **Summarise past queries:** for each query, write what it was for and which tables it used. Better still, list the questions it could answer, and strip out dates and IDs so it generalises.

3. **Prefer good tables:** index trusted, documented tables first. The rest add look-alikes.

4. **Keep it fresh:** update the index on a schedule, so removed tables disappear.

##### At question time

1. **Retrieve:** embed the question, and search both indexes for the top N tables.

2. **Rank:** combine several matches per table, and weigh trust signals like tier, owner and freshness.

3. **Reselect:** an LLM reads the summaries and keeps the top K that fit in the context.

4. **Confirm:** show the tables to the user, who can change them before any SQL is written.

5. **Generate:** the prompt holds the question, the SQL dialect, schemas and similar past queries. For columns with few distinct values, include them, so the model writes 'WEB' and not 'web'.

6. **Validate and run:** see below.

##### Validate before running

- Check table and column names against the catalogue.

- Run EXPLAIN. If it fails, retry with the error message, up to a fixed limit.

- Use a read-only role, with the user's own permissions, a default row limit and a limit on cost.

- Show the SQL, the tables, the date range, the sources and warnings, like a suspicious join or an empty result.

Valid SQL can still be wrong. A query can run perfectly and count the wrong thing, so the user must be able to see what it did.

#### The numbers worth saying out loud

All of these are assumptions for the interview, not figures from a real system.

| Question | Working | Result |
|---|---|---|
| Questions per day | 2,500 users × 10 | **25,000** |
| Average load | 25,000 ÷ 86,400 | **about 0.3 per second** |
| Items in the index | 100,000 tables + 20 past queries for each | **about 2.1 million** |
| Daily index updates | 2.1 million × 2% that changed | **about 42,000 LLM summaries** |

Traffic isn't the scaling problem. The size of the warehouse and the cost of one bad query are. A single unfiltered query on a huge table can cost more than a day of LLM calls.

## In practice

### In practice

#### What every LLM design gets asked

- **Quality and evaluation:** measure table retrieval and SQL separately. Public benchmarks use a few clean tables, which is much easier than a real warehouse, so build your test set from your own queries and experts. Compare results on the data as well as the SQL text, since two different queries can both be right.

- **Reliability:** if the LLM or the index is down, the user can still write SQL by hand, so fail visibly. Limit the fix-and-retry loop. Stop queries that run too long.

- **Scalability:** load is low, so scale the index. Update it in small daily batches, and filter by metadata like team or tier before vector search.

- **Latency and cost:** stream the SQL as it's written. Use a smaller schema, with only names and types, and drop columns tagged as unimportant. Cache table summaries, since they change slowly.

- **Safety and security:** run with the user's permissions, so the model can't reach anything they can't. Use a read-only role. Sample values and summaries can leak private data into prompts, so apply the same access rules to the index.

##### When sources disagree

Past queries can be old or plain wrong. Set an order of trust: expert docs for business rules, the catalogue for names and types, past queries checked against the schema, then general knowledge. Give more weight to queries that succeeded and are recent.

##### From a chatbot to an agent

The real system later became an agent. It classifies the task, searches tables, queries and docs in parallel, and fixes its own failed queries within a limit. Start with the simple pipeline, and move to an agent once retrieval and validation work.

#### What the real system reported

- **The first version:** users chose the tables themselves, which proved hard with hundreds of thousands of tables. So table retrieval came next.

- **Documentation:** the search hit rate was 40% without table documentation in the embeddings, and rose with its weight, up to 90%.

- **Acceptance:** generated SQL accepted on the first try rose from 20% to above 40%, as the system matured and users got used to it.

- **Speed:** task completion was 35% faster, on real data that doesn't control for differences between tasks.

- **Later agent:** a summary of the later post reports 2,500+ analytical users and a warehouse being cut from about 400,000 tables towards 100,000, and 40% of analysts using the agent within two months.

- **Still hard:** multi-step logic, undocumented business terms, queries across domains and recently removed tables still in the index.

Self-reported numbers, read through summaries. The later post's figures come from an AI-written summary, so check the original before quoting them.

### The answer that sounds right

#### "The SQL runs, so the answer is right"

It sounds right, since validation passed and numbers came back. But EXPLAIN only proves the query is valid. It can still use a look-alike table, the wrong definition of a metric or a join that duplicates rows, and return a confident wrong number. So show the SQL, tables and definitions used, and warn about risky joins.

## Say it

### Analysts spend too long finding tables and writing SQL. Design a system that turns their questions into queries across a huge data warehouse.

#### The interviewer pushes further

Follow-up 1 of 3

The query runs fine, but the number is wrong. How could that happen, and what do you do?

It may have used the wrong table, a look-alike with a different definition, or a join that duplicates rows. EXPLAIN can't catch that. Show the tables and definitions used, warn about risky joins, use expert metric definitions and past queries, and compare with known answers in the test set. For business users, offer checked metrics rather than free-form SQL.

Follow-up 2 of 3

A user asks a question that needs a table they have no access to. What happens?

The query runs with their own permissions, so the warehouse refuses it. Retrieval should also filter by access, so they don't see restricted tables or summaries. The reply can explain that they need access, and who owns the table, if policy allows that to be shown.

Follow-up 3 of 3

Why not just put all the schemas in the prompt?

With 100,000 tables they'd never fit, and most would be noise. Even if they fit, cost goes up and the model has more wrong tables to choose from. That's why you retrieve a few candidates, and send a shorter schema if space is tight.

#### The 30-second answer

First I'd clarify who the users are, whether it runs the SQL and the access rules. The hard part is finding the right table, so offline I'd summarise tables and past queries with an LLM and index them, starting with trusted, documented tables. At question time, I'd embed the question, retrieve candidate tables, rank them by similarity and trust signals like tier and owner, and have an LLM keep the few that fit. The user confirms them. The prompt holds the question, the dialect, schemas and similar past queries, plus real values for filter columns. Before running, I'd check names against the catalogue and run EXPLAIN, retrying a limited number of times. It runs read-only with the user's permissions, a row limit and a cost limit. The user sees the SQL, tables, date range and warnings, because valid SQL can still be wrong. I'd evaluate table retrieval and SQL separately on my own queries, since public benchmarks are too easy. I'd track first-try acceptance, and feed corrections back into the index.

**Key terms and sources**

Based on a social media company's published design: [Pinterest's first post](https://medium.com/pinterest-engineering/how-we-built-text-to-sql-at-pinterest-30bad30dabff) and [later post](https://medium.com/pinterest-engineering/unified-context-intent-embeddings-for-scalable-text-to-sql-793635e60aac). Both were blocked for us, so we used [ZenML's summary](https://www.zenml.io/llmops-database/text-to-sql-system-with-rag-enhanced-table-selection), [an AI-written summary of the later post](https://enggist.vercel.app/post/9fa18690-8f64-4f5f-b46d-88986109a79d) and our own knowledge. Volumes, permission rules and the lab's numbers are our illustrations. Uses RAG, advanced RAG and structured output. · checked 5 Nov 2026
