# Memory and Context Engineering

> How does an agent remember a peanut allergy 50 turns later?

- Track: AI Engineering › Agentic AI › Lessons
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/ai-engineering/memory-and-context-engineering/
- Before this: What Is an Agent? The ReAct Loop (`ai-engineering/what-is-an-agent`)
- Quiz topic: `agents`

## Intuition

### The situation

In turn 1 of a long support chat, a customer says they're allergic to peanuts. Fifty turns later they ask the agent to reorder a dish. A colleague keeps only the last 10 turns, to save tokens. The interviewer asks:

> How does an agent remember a peanut allergy 50 turns later?

**Running example:** a long support conversation. In turn 1 the customer says "I'm allergic to peanuts"; 50 turns later they ask the agent to reorder a dish.

#### Context is finite, expensive and imperfectly used

Agents loop many times, and each loop adds tool outputs (order JSON, policy text, search results). Keeping everything blows the budget and buries the important facts; dropping things loses them. Memory design decides what the model sees at every step.

### The idea

Think of a small desk. Keep today's papers on it, summarise the older ones into a note and file anything important on a card in a drawer. You don't keep everything on the desk, and you don't throw the allergy card away. You pull the card out when food comes up.

[Figure: At turn 200. Full history: 62,000 tokens per call, and the allergy is there but buried. Last 10 turns: 5,000 tokens, and it is forgotten. Last 10 with a summary and a memory store: 5,950 tokens, and it is retrieved when needed.]

_From the lab, at turn 200. Long contexts are used least reliably in the middle._

### Play

**Try to break it.** Set the turns to 50, then 200. Switch between full history, the last 10 turns, the last 10 with a summary and the last 10 with a summary and memory store.

#### "Just keep the whole history"

2,000-token system prompt and tools; 300 tokens per turn (message + tool results); summary 500 tokens; 3 retrieved memories ≈ 450 tokens. Cost and latency scale with input tokens per call.

**Full history** is simplest and remembers everything: at turn 50 each call carries 17,000 tokens; at turn 200, **62,000**, and the conversation has consumed **6.43 M** input tokens, with the allergy buried in the middle where models use information least reliably. A **10-turn window** caps calls at 5,000 tokens (0.99 M total) but has **forgotten** the allergy, a dangerous failure. A **summary** keeps it only if the summariser judged it important. A **memory store** that saves durable facts and retrieves them when relevant keeps calls at 5,950 tokens and still knows: the allergy is retrieved when the customer orders food.

**Now say why:** a summary might keep the allergy, so why isn't that good enough?

## How it works

### How it works

#### In one breath

The model only knows what's in its **context window** right now. In an agent, that window fills with the system prompt, tool definitions, the conversation and, above all, **tool results**, and it grows every step. Long contexts cost more (every call re-reads them), get slower, and models use them less reliably ("lost in the middle", and accuracy decaying as inputs grow, sometimes called context rot). **Context engineering** is deciding what goes in: keep a **window** of recent turns, **summarise or compact** older ones, store durable facts in **long-term memory** (a database or vector store) and retrieve them when relevant, write large intermediate results to files, and give sub-agents their own clean contexts. The aim is the smallest set of high-signal tokens for the next step.What you'll be able to do after this: design an agent's memory, estimate context growth and cost, and choose between windowing, summaries and retrieval.

#### Kinds of memory

| Memory | Where it lives | Example |
|---|---|---|
| **Working / short-term** | the context window | current conversation, latest tool results, the task list |
| **Summaries / compaction** | the context window, rewritten | "Customer: late order #48213, refund 10% issued; allergic to peanuts" |
| **Long-term semantic** | database or vector store, retrieved per step | preferences, allergies, account facts |
| **Episodic** | store of past interactions | "last month we gave a goodwill credit" |
| **Procedural** | prompts, tools, learned instructions | refund procedure, tone rules |

MemGPT (Packer et al.) framed this like an operating system: the model pages information between a small context and larger external storage. Generative Agents (Park et al.) stored observations and retrieved them by recency, importance and relevance.

## In practice

### In practice

#### Context engineering techniques

- **Trim tool results:** return compact, relevant fields from tools instead of raw dumps; this is often the biggest saving.

- **Compaction:** when the context nears a limit, summarise older turns and keep critical facts and open tasks verbatim.

- **Explicit memory writes:** let the agent (or code) save important facts (allergies, decisions, IDs) to a store with clear schemas; retrieve by relevance and recency.

- **Offload:** write large intermediate artefacts to files or a scratchpad and keep references in context.

- **Isolate:** run sub-tasks in sub-agents with their own contexts and return only the result.

- **Cache the stable prefix** (system prompt, tools) with prompt caching, and keep it unchanged between turns.

**Added 7 Nov 2026.** Frameworks now separate per-conversation memory, saved as checkpoints under a thread ID, from a long-term **store** shared across conversations. Agents can also keep a playbook of lessons from past runs: ACE gained 10.6% on agent tasks with small, itemised updates. Rewriting the whole playbook at once risks **context collapse**: in one case, 18,282 tokens shrank to 122 and accuracy fell below having no playbook. See Agent Skills and Self-Improving Context.

**Added 8 Nov 2026: effective context is shorter than the window.** In NVIDIA's RULER, all 17 models claimed 32K tokens or more and nearly all passed simple needle tests, yet only about half kept a good score at 32K on harder tasks. NoLiMa found 11 of 13 models fell below half their short-context score at 32K when the question and answer shared no words. Even with perfect retrieval, accuracy fell 13.9–85% as inputs grew. So keep context small: clear stale tool results (Anthropic reported 29% better agentic search from this alone, and 84% fewer tokens in a 100-turn test), keep references to reload content, write notes outside the context, and use sub-agents that return short summaries. See Agent Scenarios: Context and Memory.

#### The smallest high-signal context for each step

Agent memory is about choosing what the model sees next: recent turns verbatim, older ones compacted, durable facts in a store retrieved when relevant, and bulky material kept outside the window.

### The answer that sounds right

#### "A sliding window is enough"

It sounds right, since it caps the cost so neatly. But it forgets critical early facts, and the allergy is exactly that kind of fact. Keeping the whole history isn't the answer either, even with huge contexts: cost grows with every call's input, and recall degrades. Long-term memory has its own risks too: stale facts, privacy and injected content.

## Say it

### How does an agent remember a peanut allergy 50 turns later?

#### The interviewer pushes further

Follow-up 1 of 3

What should go into long-term memory?

Durable, user-specific or task-critical facts (preferences, constraints, decisions, IDs), with timestamps and sources; not raw transcripts.

Follow-up 2 of 3

Risks of long-term memory?

Stale or wrong memories persisting, privacy (store consent and deletion), and memory poisoning via injected content; scope memories per user and let users view and delete them.

Follow-up 3 of 3

Why not just use a 1M-token context model?

Cost and latency grow with every call's input, and recall degrades in very long contexts; selection still beats stuffing.

#### The 30-second answer

An agent only knows what's in its context, which grows every step with tool results, so cost and latency climb and models use long contexts less reliably. I'd keep recent turns verbatim, compact older turns into summaries that preserve key facts and open tasks, store durable facts like preferences or allergies in a long-term memory and retrieve them by relevance, trim tool outputs to what's needed, offload big artefacts to files and use sub-agents for isolated sub-tasks. I'd also keep the system prompt and tools stable so they're cached.

**Go further**

#### What not to say

- "Keep the whole history; contexts are huge now." Cost and reliability still suffer.

- "A sliding window is enough." It forgets critical early facts.

**Key terms and sources**

What goes into an agent's context window at each step and why it matters: short-term memory (conversation and tool results), context growth and "context rot", sliding windows, summarisation and compaction, long-term memory stores (episodic and semantic, retrieved like RAG), offloading to files, and sub-agents for context isolation · built from Packer et al. (MemGPT, 2023), Park et al. (Generative Agents, UIST 2023), Liu et al. (Lost in the Middle, TACL 2024), Hong et al. (Chroma, Context Rot, 2025), Anthropic (Effective context engineering for AI agents, 2025) and LangChain / LangGraph memory documentation · checked 29 Oct 2026

#### Sources

1. C. Packer et al., "MemGPT: Towards LLMs as Operating Systems", 2023, arXiv:2310.08560.

2. J. S. Park et al., "Generative Agents: Interactive Simulacra of Human Behavior", UIST 2023, arXiv:2304.03442.

3. N. Liu et al., "Lost in the Middle", TACL 2024, arXiv:2307.03172; K. Hong et al. (Chroma), "Context Rot: How Increasing Input Tokens Impacts LLM Performance", 2025.

4. Anthropic, "Effective context engineering for AI agents", 2025; LangChain / LangGraph memory documentation.

5. Q. Zhang et al., "Agentic Context Engineering", ICLR 2026, arXiv:2510.04618; LangGraph memory documentation (checkpointers and stores).

6. C.-P. Hsieh et al., "RULER: What's the Real Context Size of Your Long-Context Language Models?", COLM 2024, arXiv:2404.06654; A. Modarressi et al., "NoLiMa", ICML 2025, arXiv:2502.05167; Y. Du et al., "Context Length Alone Hurts LLM Performance Despite Perfect Retrieval", 2025, arXiv:2510.05381; Anthropic, "Effective context engineering for AI agents" and "Managing context", Sep 2025.
