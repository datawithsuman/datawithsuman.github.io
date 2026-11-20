# Agentic RAG, and When Not to Index

> Should your RAG be an agent? When do you skip the index altogether?

- Track: AI Engineering › RAG › Lessons
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/ai-engineering/agentic-rag/
- Before this: Advanced RAG: Hybrid Search, Re-ranking, Query Rewriting and GraphRAG (`ai-engineering/advanced-rag`), What Is an Agent? The ReAct Loop (`ai-engineering/what-is-an-agent`)
- Quiz topic: `rag`

## Intuition

### The situation

Your RAG works for most questions, but fails on those needing facts from two places. A colleague proposes rebuilding it as an agent. Another says agents have replaced vector search, and you should just use grep. Your corpus is 8 million documents. The interviewer asks:

> Should your RAG be an agent? When do you skip the index altogether?

#### Why it matters

"Just make it an agent" is now a common suggestion, and "is RAG dead?" a common headline. Neither helps you decide. Interviewers want you to say when each one is worth its cost. This lesson covers retrieval decisions, and What Is an Agent? covers the loop in general.

### The idea

Think of finding something in a library. If you know the exact title, use the catalogue. If you only know the topic, ask a librarian once. If the question needs several books, you read one, then go back for another, but each trip takes time, and you carry everything you've collected.

[Figure: Choose by need. Small corpus: put it in the prompt. Exact lookups: use text search. Multi-step questions: add a loop.]

_Add a loop only for questions that need one._

### Play

**Try to break it.** Raise the search rounds. Then switch to a batch.

#### Count the tokens

Illustrative. A 2,000-token base prompt, 500 tokens per chunk, and an invented price of $3 per million input tokens. Static RAG makes one call with one search. A batch makes one call to plan, and one to answer with all results. Prompt caching and summarising old results would lower these numbers.

One static search uses 7,000 tokens. **Five rounds** of 10 chunks use 87,000, about 12 times as much, and six calls' worth of waiting. That's because every round resends earlier results. **Batching** the five searches brings it to 29,000. Chen et al. saw batching raise coverage while lowering token use, though its better coverage didn't always improve answers. Now try 10 rounds, one at a time: it passes 280,000 tokens. So an agent should stop searching once it has enough, and old results should be summarised or dropped.

**Now say why:** why do tokens grow faster than the number of rounds?

## How it works

### How it works

#### In one breath

Static RAG retrieves once. **Agentic RAG** lets the model decide what to search, read the results, and search again. That helps with questions needing facts from several places, but it costs more: each round resends the whole conversation. Evidence is mixed, as agents won in one study and lost in others. Often you don't need an index at all: a small knowledge base can go straight in the prompt, and exact lookups can use plain text search. Start simple, measure, and add a loop only for the questions that need one.

#### What the evidence says

##### Four ways to find information

| Approach | Best for | Weak spot |
|---|---|---|
| **Everything in the prompt** | Small knowledge bases. Anthropic suggests under about 200,000 tokens | Cost per call, though prompt caching helps |
| **Text search, grep** | Exact names, IDs and code, always fresh | Different wording for the same idea |
| **Static RAG** | Single questions over large corpora | Questions needing several steps |
| **Agentic RAG** | Multi-step questions, and using several tools | Tokens, latency and less predictable behaviour |

##### Do agents help? It depends

| Study | Finding | Setting |
|---|---|---|
| Uber, on policy documents | 27% more acceptable answers, 60% less incorrect advice (relative) | A fixed flow of agents. 100+ test queries |
| Chen et al. | An agent with one search tool was among the best, at Hit@1 of 0.69, while adding a graph tool or thinking didn't help | One medical dataset |
| Rathi et al. | A model-decides tool call scored below plain RAG | One search allowed, small quantized model |
| Levy et al. | An agentic loop on a strong stack: a negligible faithfulness gain, and worse retrieval and latency | 450 setups, up to 200K documents |
| Is Complex Agentic Memory Always Needed? | Plain retrieval and re-ranking over raw history beat complex memory systems in 6 of 7 settings | Conversation memory benchmarks |

So agents aren't simply better. They help most with strong models, several real steps, and useful tools. Note the different setups, which is partly why results disagree.

##### Grep or semantic search?

Some coding agents now rely on text search and no index, which keeps results fresh and avoids a lot of machinery. But Cursor's own tests point the other way for large repositories: with semantic search, its agent answered 12.5% more accurately on average. In an A/B test, code retention rose 0.3%, and 2.6% on codebases of 1,000 files or more. Cursor concluded that using both works best. These are vendor numbers, though with a real A/B test. Agents can also combine them: GRASP trained a policy that uses semantic search to explore, and keyword search for specific names.

##### GraphRAG and friends

Chen et al. found that simply adding related facts to each document beat a more complex GraphRAG setup on their data. Microsoft's LazyGraphRAG cuts indexing to 0.1% of full GraphRAG's cost by deferring LLM work to query time. So try simple structure first, as with agents.

#### The maths

$$ {\text{input tokens}} = \sum_{i=0}^{{R}} \big({S} + i\,{C}\big) = (R+1)\,S + \frac{R(R+1)}{2}\,C $$

Our own arithmetic for a simple loop that keeps its full history. Chen et al. saw the same effect: a 5-call session used about 250K tokens, while a 3-call session used only 36K.

- **total tokens the model reads**: Across every call in the loop.

- **search rounds**: Each round adds another call to the model, and one final call writes the answer.

- **the base prompt**: System prompt, tools and question, resent on every call.

- **retrieved text per round**: Earlier results stay in the history, so they’re resent too. That’s why cost grows with the square of the rounds.

## In practice

### In practice

#### In practice

- **Start with a baseline:** measure plain retrieval and re-ranking first. Agentic systems should have to beat it.

- **Route by question:** use a cheap single search for simple questions, and allow a loop only for the hard ones.

- **Fix the flow where you can:** a fixed pipeline of steps is easier to test than a free-running loop, as in Uber's design.

- **Set limits:** cap rounds and tokens, and watch cost per question. Summarise or drop old results.

- **Offer a keyword tool:** give agents both keyword and semantic search, plus a way to read the surrounding section.

### The answer that sounds right

#### "Agents have replaced RAG, so rebuild it as an agent"

It sounds right, as agents are more flexible. But agents still retrieve, and they cost far more. Studies disagree: one found a simple agent best, and another found a loop added almost nothing on a strong retrieval stack. Build the baseline first, then make the agent prove itself on your own questions.

## Say it

### Should your RAG be an agent? When do you skip the index altogether?

#### The interviewer pushes further

Follow-up 1 of 3

Your corpus is 150,000 tokens. Do you need a vector database?

Probably not. Put it in the prompt with prompt caching, and measure. Anthropic suggests this under about 200,000 tokens. Add retrieval once cost or latency hurts, or the corpus grows.

Follow-up 2 of 3

Why does an agent cost so much more than one search?

Each round resends the system prompt and all earlier results, so input tokens grow with the square of the rounds. Five rounds of 5,000 tokens are about 12 times one static search. Batch the searches, cap the rounds, and trim old results.

Follow-up 3 of 3

Grep or embeddings for a code assistant?

Both. Text search handles exact names and is always fresh. Semantic search finds code when you don't know the words, and Cursor saw more benefit in large repositories. Give the agent both tools, and test on real tasks.

#### The 30-second answer

I'd start from the simplest thing that works. A small knowledge base can go straight in the prompt, and exact lookups can use text search. For large corpora I'd use static RAG with re-ranking as the baseline. I'd add an agentic loop only for questions needing several steps, because each round resends the history, so tokens grow with the square of the rounds. Evidence is mixed: agents won in one study and added nothing on a strong retrieval stack in another. For code, some agents use only grep, while Cursor measured clear gains from adding semantic search, especially in large repositories. So I'd route by question, cap the rounds, and make the agent beat the baseline on my own test set.

**Key terms and sources**

Static against agentic retrieval, why each search round costs more, conflicting evidence on agents, grep against semantic search, whole-document prompts and simple baselines. · checked 7 Nov 2026

#### Sources

- [Cursor, Improving agent with semantic search](https://cursor.com/blog/semsearch)

- [Uber, Enhanced Agentic-RAG](https://www.uber.com/en-CA/blog/enhanced-agentic-rag/)

- [Chen et al., Is GraphRAG Needed?](https://arxiv.org/abs/2606.25656)

- [Rathi, Chawla and Andreopoulos, A Controlled Comparison of RAG Strategies](https://arxiv.org/abs/2609.38473)

- [Levy, Shlomov and Choshen, Retrieval Augmented Generation Compositionality](https://arxiv.org/abs/2610.29722)

- [Bao et al., Is Complex Agentic Memory Always Needed?](https://arxiv.org/abs/2610.30755)

- [Gandhi et al., GRASP](https://arxiv.org/abs/2607.10463)

- [Anthropic, Introducing Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval)

- [Microsoft Research, LazyGraphRAG](https://www.microsoft.com/en-us/research/blog/lazygraphrag-setting-a-new-standard-for-quality-and-cost)

Explanations are ours, built from these sources. Lab numbers are illustrative unless a lab says otherwise. Most recent papers are preprints.
