# Design Support Answers from Past Tickets

> A customer service team has years of resolved support tickets. Design a system that answers a new issue by finding similar past tickets and their fixes.

- Track: System Design › RAG and Search › Designs
- Type: Design · 25 min
- Page: https://aimlrounds.com/tracks/system-design/design-ticket-graph-rag/
- Before this: RAG End to End (`ai-engineering/rag-end-to-end`), Ranking Metrics (`fundamentals/ranking-metrics`)
- Quiz topic: `sdllm`

## Intuition

### The situation

A software company's customer service team has years of resolved tickets, each with a summary, steps to reproduce, a fix, and links to related tickets. Agents waste hours finding similar past issues. The interviewer asks:

> A customer service team has years of resolved support tickets. Design a system that answers a new issue by finding similar past tickets and their fixes.

#### Ask before designing

- **Users:** support agents handling new issues across product lines.

- **Data:** years of tickets with fields like summary, description, priority, steps to reproduce and resolution, plus links such as "duplicate of" or "caused by".

- **Goal:** find the right past ticket and its fix quickly, then draft an answer.

- **Must never happen:** mixing the problem from one ticket with the fix from another.

- **Success metrics:** retrieval (MRR, recall at 1 and 3), answer quality against reference fixes, and time to resolve an issue.

### The idea

Think of a mechanic's logbook. A good mechanic doesn't flip through random torn pages; they look up cars with the same symptom, check the 'fixed by' column, and follow notes like 'same as the job last March'.

[Figure: Parse the question into entities. Match each entity to the same section of past tickets. Query the ticket graph for the section needed. Answer, with text search as a fallback.]

_Keep each ticket's structure, and its links._

### Play

**Try to break it.** Switch from text chunks to the ticket graph.

#### Chunks versus a ticket graph

From the paper's Tables 1 and 2. Both versions used the same LLM and embedding model, so only retrieval changed. The test set size isn't stated.

Switch to the graph. The right ticket goes from first place 40% of the time to 86%, because the system compares the question with the matching section of each ticket instead of with arbitrary text slices.

**Now say why:** why does matching section to section rank the right ticket first so much more often?

## Architecture

### Architecture

#### In one breath

Plain chunking cuts a ticket's problem away from its fix and loses links between tickets. Instead, parse each ticket into **sections** (summary, steps to reproduce, fix), link tickets that reference or resemble each other into a **graph**, and embed each section. For a new question, extract its **entities**, find tickets whose matching sections are close, then **query the graph** for the exact section needed. Fall back to text search if the graph query fails.

#### Tickets as trees, linked into a graph

1. **Parse each ticket into a tree:** rules extract fixed fields; an LLM fills the rest, guided by a template of the usual sections.

2. **Link tickets:** explicit edges come from ticket links; implicit edges join tickets whose title embeddings are very similar.

3. **Embed sections:** each text-rich section is embedded and stored in a vector database, and the graph goes in a graph database.

4. **Parse the question:** an LLM turns it into entities (section: value, such as "summary: login fails after reset") and an intent (such as "find the fix").

5. **Find tickets:** compare each entity with the same section across tickets, sum the scores per ticket, keep the top few.

6. **Query the graph:** an LLM writes a graph query for the needed section of those tickets. If it fails, fall back to plain text retrieval.

7. **Answer:** the LLM writes the answer from what was retrieved.

#### The numbers worth saying out loud

All of these are assumptions for the interview, not figures from a real system.

| Question | Working | Result |
|---|---|---|
| Tickets | given | **2 million** |
| Section nodes | 2 million × 6 sections | **12 million** |
| LLM parsing cost, one-off | 2 million × 2,000 tokens | **4 billion tokens** |
| New tickets a day | given; parsed and linked nearline | **5,000** |

The one-off parse is the big cost; after that, each new ticket is parsed and linked as it closes.

## In practice

### In practice

#### What every ticket-retrieval design gets asked

- **Why not chunks:** fixed-size chunks split a ticket's problem from its solution, and lose "this issue was caused by that one".

- **Implicit links:** tickets that never referenced each other can still be linked when their titles are very similar, with a tuned threshold.

- **Robustness:** the LLM-written graph query can fail; always keep text retrieval as a fallback.

- **Templates:** the section template is hand-built per team; automating it is open work.

- **Freshness:** parse and link tickets when they close, and add new links as they appear.

- **Privacy:** tickets contain customer data; restrict access and remove personal details before indexing.

##### Rollout

Randomly split the support team: half uses the tool, half works as before, and compare resolution times.

#### What the real system reported

- **Retrieval:** MRR rose from 0.522 to 0.927, a 77.6% improvement; recall at 3 reached 1.0 on the test set.

- **Answers:** BLEU rose from 0.057 to 0.377, with METEOR and ROUGE also higher.

- **Deployment:** used by the customer service team for about six months; in a randomised split, median resolution time per issue fell from 7 hours to 5, a 28.6% reduction, and the mean fell from 40 hours to 15.

From the paper (SIGIR 2024). The test set and team sizes aren't stated.

### The answer that sounds right

#### "Chunk the tickets like any other documents"

It sounds standard, but fixed-size chunks split a ticket's problem from its fix and drop links like "caused by". The same model with structured retrieval ranked the right ticket first 86% of the time instead of 40%.

## Say it

### A customer service team has years of resolved support tickets. Design a system that answers a new issue by finding similar past tickets and their fixes.

#### The interviewer pushes further

Follow-up 1 of 3

Why match section to section?

A question's symptoms should be compared with ticket descriptions, not with fixes or metadata. Matching the same section makes similarity meaningful, and several matched entities in one ticket are strong evidence.

Follow-up 2 of 3

The LLM writes a broken graph query. What happens?

Catch the error and fall back to standard text retrieval, so the agent still gets an answer, and log the failure to improve the prompt.

Follow-up 3 of 3

How would you prove it helps the business?

Randomly assign agents to use the tool or not, and compare resolution times; offline metrics alone don't show time saved.

I'd clarify who uses it, what fields tickets have and how tickets link to each other. Plain chunking would split a ticket's problem from its fix, so I'd parse each ticket into a tree of sections, using rules for fixed fields and an LLM with a template for the rest. I'd link tickets by their explicit references and by very similar titles. Each section is embedded. For a new question, an LLM extracts entities and the intent; I match each entity against the same section across tickets, sum per ticket, and keep the top few. Then an LLM writes a graph query for the section needed, like the fix, with plain text retrieval as a fallback. I'd evaluate with MRR and recall against a golden set, then run a randomised trial on resolution time.

**Key terms and sources**

Based on a professional network's published paper: "Retrieval-Augmented Generation with Knowledge Graphs for Customer Service Question Answering" (SIGIR 2024). The lab uses the paper's own numbers; the estimate is ours. Uses RAG end to end, embeddings and vector indexes and ranking metrics.
