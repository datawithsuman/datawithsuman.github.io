# Design an On-Call Engineering Copilot

> Engineering teams answer tens of thousands of questions a month in chat support channels. Design a copilot that answers them from internal docs, including long policy documents full of tables.

- Track: System Design › RAG and Search › Designs
- Type: Design · 25 min
- Page: https://aimlrounds.com/tracks/system-design/design-oncall-copilot/
- Before this: RAG End to End (`ai-engineering/rag-end-to-end`), Agentic RAG, and When Not to Index (`ai-engineering/agentic-rag`)
- Quiz topic: `sdllm`

## Intuition

### The situation

Engineers at a large company post tens of thousands of questions a month in chat support channels. The answers are scattered across a wiki, an internal Q&A site and long policy documents. The interviewer asks:

> Engineering teams answer tens of thousands of questions a month in chat support channels. Design a copilot that answers them from internal docs, including long policy documents full of tables.

#### Ask before designing

- **Where:** inside existing chat support channels, replying in the thread, so engineers don't change habits.

- **Volume:** tens of thousands of questions a month across many channels.

- **Sources:** the internal wiki, an internal Q&A site, design docs, and security and privacy policies.

- **Must never happen:** leaking restricted documents to people without access, or giving wrong security advice confidently.

- **Success metrics:** share of answers marked helpful or resolved, accuracy on a golden set, and engineering hours saved.

### The idea

Think of a new team member who keeps a folder of the best pages and always says where an answer came from. For the thick policy binders, they first check the table of contents, then read whole tables instead of torn-out scraps.

[Figure: Rewrite the question. Pick likely documents. Search with vectors and keywords over enriched chunks. Answer only from cited sources in the chat thread.]

_Cite everything, and keep tables whole._

### Play

**Try to break it.** Turn on the enhanced pipeline. Then raise the baseline share of incorrect advice.

#### Better answers, far less wrong advice

The post gives only relative changes (+27% acceptable, −60% incorrect advice, on 100+ expert-written questions about 40+ policy documents). The baseline values here are illustrative.

Turn on the enhanced pipeline. The bigger win is the drop in wrong advice: for security and privacy questions, a wrong answer is worse than no answer.

**Now say why:** for security questions, which matters more: fewer wrong answers, or more right ones?

## Architecture

### Architecture

#### In one breath

Index a **curated set** of wikis and internal Q&A, answer in the chat thread with **citations**, and collect one-click feedback. Policy documents are harder: tables break when PDFs are parsed, so load them from a structured source, keep **tables whole**, add summaries and keywords to each chunk, **rewrite the query**, pick likely documents first, and search with **keywords plus vectors**. Measure with a golden set and an LLM judge.

#### A plain pipeline, then an agentic one for hard documents

1. **Ingest:** a batch job pulls pages through each source's API, chunks them, embeds them and pushes vectors to the vector database. Only sources most engineers can already read are included.

2. **Retrieve:** embed the question and fetch the most similar chunks.

3. **Answer:** each chunk goes into the prompt as a labelled section with its URL; the LLM must answer only from those sections and cite the URL.

4. **Act:** buttons under each answer: resolved, helpful, not helpful, not relevant, plus "ask a follow-up" and "contact a human".

5. **Learn:** feedback streams to a table and a dashboard; an LLM judge scores answers and also flags weak documentation to fix.

##### The policy-document upgrade

For long policy documents, add steps: a **query optimiser** rewrites vague questions and splits complex ones; a **source identifier** picks likely documents from a list of titles and summaries; retrieval combines **vector and keyword search** over chunks enriched with summaries, FAQs and keywords; a **post-processor** removes duplicates and puts chunks back in document order.

#### The numbers worth saying out loud

All of these are assumptions for the interview, not figures from a real system.

| Question | Working | Result |
|---|---|---|
| Questions a month | given | **45,000** |
| LLM calls a month | 45,000 × 3 (rewrite, pick sources, answer) | **135,000** |
| Helpful answers | 45,000 × 50% | **22,500** |
| Hours saved | 22,500 × 15 minutes | **about 5,600 a month** |

Even at a few cents a call, the LLM bill is tiny next to engineering time; quality is the real constraint.

## In practice

### In practice

#### What every internal copilot gets asked

- **Tables:** standard PDF loaders turn multi-page nested tables into loose text. No single PDF parser worked for every document, so the team loaded documents from an editable source with structure, converted tables to markdown and kept each table in one chunk with a two-line summary.

- **Access:** index access-control metadata with each document and filter at answer time, or include only widely readable sources.

- **Hallucination:** labelled source sections plus "answer only from these" and required citations.

- **Evaluation:** experts write reference answers once; each new version answers the golden set in a batch, and an LLM judge scores 0 to 5 against them. Evaluation went from weeks to minutes.

- **Cost tracking:** pass a request ID through every call so cost can be audited per channel.

- **Fixing docs:** score documents too, since many wrong answers come from missing or outdated pages.

#### What the real system reported

- **Need:** about 45,000 questions a month in support channels, with answers scattered across a wiki, an internal Q&A site and other places.

- **Why RAG:** it needed no training examples, so it reached users faster than fine-tuning.

- **Reach:** launched September 2023; 154 channels, over 70,000 questions answered, a 48.9% helpfulness rate, and an estimated 13,000 engineering hours saved.

- **Policy documents:** the agentic pipeline raised acceptable answers by a relative 27% and cut incorrect advice by a relative 60%. Its steps run in sequence for now.

From the two posts (Oct 2024 and May 2025). All figures are self-reported.

### The answer that sounds right

#### "Just load the PDFs and chunk them"

It sounds simple, but standard PDF loaders turn multi-page tables into loose text, and chunks lose the row and column they came from. Load from a structured source, keep tables whole and add summaries, or the answers will miss the details that matter.

## Say it

### Engineering teams answer tens of thousands of questions a month in chat support channels. Design a copilot that answers them from internal docs, including long policy documents full of tables.

#### The interviewer pushes further

Follow-up 1 of 3

Why not fine-tune a model on your documentation?

RAG needs no training examples, updates as soon as docs change, and can cite sources. Fine-tuning bakes in knowledge that goes stale and can't show where an answer came from.

Follow-up 2 of 3

Answers about policies keep missing details from tables. What do you change?

Parsing and chunking. Load from a structured source, convert tables to markdown, keep each table in one chunk with a short summary and keywords, and add keyword search so exact terms are found.

Follow-up 3 of 3

How do you test a new prompt before shipping?

Run the golden set through the new version, and have an LLM judge score each answer against the expert reference. Compare with the current version, then watch live feedback after release.

I'd clarify where engineers ask, the volume, the sources and access rules. The bot lives in the existing chat channels and answers in the thread. A batch pipeline pulls a curated set of widely readable sources, chunks and embeds them. At query time I retrieve the closest chunks, put each in the prompt with its URL, and require the answer to use only those and cite them. Buttons collect resolved, helpful or not helpful, and offer a human. For policy documents with big tables I'd keep tables whole and summarised, add summaries and keywords to chunks, rewrite the query, pick likely documents first, then search with vectors plus keywords and put chunks back in order. I'd measure with an expert-written golden set scored by an LLM judge, plus live feedback, and use bad answers to fix the docs.

**Key terms and sources**

Based on a ride-hailing company's posts: "Genie: Uber's Gen AI On-Call Copilot" (Oct 2024) and "Enhanced Agentic-RAG" (May 2025). The lab's baseline is illustrative; the relative gains are the post's. Uses RAG end to end, parsing and chunking and agentic RAG.
