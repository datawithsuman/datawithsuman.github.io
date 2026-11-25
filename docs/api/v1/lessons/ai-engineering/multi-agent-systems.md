# Multi-Agent Systems

> When do several agents beat one, and what does it cost?

- Track: AI Engineering › Agentic AI › Lessons
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/ai-engineering/multi-agent-systems/
- Before this: What Is an Agent? The ReAct Loop (`ai-engineering/what-is-an-agent`)
- Quiz topic: `agents`
- Sources checked: 2026-11-07 · Text last changed: 2026-11-20 · Version: e3383b332b

## Intuition

### The situation

A weekly report must investigate why refunds rose in 5 cities, checking orders, ratings, delivery times and weather for each. One agent does them in turn, and its context fills up. A colleague proposes agents for everything, including writing one refund decision together. The interviewer asks:

> When do several agents beat one, and what does it cost?

**Running example:** a weekly "complaints intelligence" report: investigate why refunds rose in 5 cities by checking orders, restaurant ratings, delivery times and weather for each, then write one summary.

#### One agent, one context, one thread

A single agent investigating five cities does them one after another, and its context fills with every city's raw data, crowding out the task. Splitting the work could run in parallel and keep each context clean, but coordination has costs.

### The idea

Think of researching five cities with a team. A lead hands each person a clear brief, and each returns a short summary. It's faster, but you pay everyone. Now ask that team to write one paragraph at the same time without talking, and they'll contradict each other.

[Figure: Five independent sub-tasks. A single agent takes 5 minutes and 100 thousand tokens. An orchestrator with parallel workers takes 2 minutes and 170 thousand tokens.]

_Illustrative numbers from the lab. Real ratios vary._

### Play

**Try to break it.** Switch between the single agent and the orchestrator with parallel workers. Then change the number of independent sub-tasks.

#### Faster, but at what cost?

Illustrative: each sub-task takes 60 s and 20k tokens; the orchestrator spends 30 s and 10k tokens planning and again synthesising; each worker repeats instructions and context (+50% tokens). Real ratios vary; Anthropic reported ~15× chat tokens for its multi-agent system vs ~4× for single agents.

For **5 independent cities**, a single agent takes **5 minutes** and 100k tokens; an orchestrator with parallel workers finishes in **2 minutes** but uses **170k** tokens (1.7×), and each worker's context stays focused on one city. That trade (time and breadth for tokens) is worth it for valuable, parallel, read-heavy work. The trap is applying it to coupled work: if the "workers" were editing parts of the same codebase or writing one refund decision together, each would make assumptions the others can't see, and the merge would conflict; failure studies of multi-agent systems find many failures come from mis-specification and inter-agent misalignment rather than the model itself.

**Now say why:** it's so much faster on cities, so why would it fail on editing one codebase?

## How it works

### How it works

#### In one breath

A **multi-agent** system splits work across several LLM agents, usually an **orchestrator** that plans and delegates to **worker** sub-agents, each with its own context and tools, then combines their results. It shines for **broad, parallelisable, read-heavy** work: Anthropic's research system (lead agent + parallel sub-agents) beat a single agent by **90.2%** on an internal research eval, at about **15×** the tokens of a chat (single agents use about 4×). It struggles when sub-tasks are **tightly coupled**: parallel workers with partial context make conflicting decisions (Cognition's argument for coding). So: one agent by default; sub-agents for independent, parallel sub-tasks; **handoffs** for routing a conversation to a specialist. What you'll be able to do after this: choose between a single agent, orchestrator–workers and handoffs, and estimate the time and token trade-off.

#### Patterns

| Pattern | How | Fits |
|---|---|---|
| **Orchestrator–workers** | lead agent plans, spawns sub-agents with clear briefs, merges condensed results | research, analysis, broad search |
| **Handoffs** | one agent transfers the conversation (and context) to a specialist (billing, refunds) | customer support routing |
| **Parallel sampling / debate** | several agents answer or argue, then aggregate | hard reasoning; costly |
| **Agent-to-agent (A2A)** | agents from different vendors/services call each other via a protocol | cross-organisation workflows |

## In practice

### In practice

#### Making multi-agent work

- **Default to one agent;** add sub-agents for independent, parallel sub-tasks or to isolate bulky context (context engineering).

- **Write sub-agent briefs** like delegation to a colleague: goal, scope, tools, output format, effort budget. Return condensed results, not raw transcripts.

- **Share context when decisions interact** (Cognition's principle): pass full traces or keep one agent responsible for coupled decisions.

- **Budget and observe:** cap sub-agent count and tokens; trace every agent's steps; evaluate the end-to-end outcome.

A2A reached version 1.0 and joined the Agentic AI Foundation in Aug 2026. Agents publish Agent Cards, and work runs as tasks with states such as working, input required and completed. See Agent Protocols.

#### Parallelise what's independent, keep coupled decisions together

Multi-agent systems buy speed, breadth and clean contexts with many more tokens and coordination risk; they fit read-heavy parallel tasks and fail on tightly coupled ones.

### The answer that sounds right

#### "More agents means smarter"

It sounds right, since several heads seem better than one. But it means more tokens and more coordination. Failure studies find many problems come from mis-specification and misalignment between agents, rather than from the model. And agents shouldn't just negotiate an answer either, unless they have shared context and a clear owner.

## Say it

### When do several agents beat one, and what does it cost?

#### The interviewer pushes further

Follow-up 1 of 3

Why do sub-agents help with context?

Each explores in its own window and returns only a summary, so the orchestrator's context isn't flooded with raw search results.

Follow-up 2 of 3

How do you evaluate a multi-agent system?

End-to-end task success and quality on a test set, plus cost and time; trace per-agent steps to debug delegation and merge failures.

Follow-up 3 of 3

Handoffs or one agent with all tools?

Handoffs when domains need different prompts, tools or permissions (refunds vs tech support); one agent when the domain is small enough to stay clear.

#### The 30-second answer

The main pattern is orchestrator–workers: a lead agent plans, spawns sub-agents with focused briefs and their own contexts, and synthesises their condensed results; handoffs route a conversation to a specialist. It works well for broad, parallel, read-heavy tasks; Anthropic's research system beat a single agent by about 90 percent on their eval, but used around 15 times the tokens of a chat. It works badly for tightly coupled work like editing one codebase, because parallel agents with partial context make conflicting decisions. So I default to a single agent and add sub-agents only for independent sub-tasks, with clear briefs, budgets and tracing.

**Go further**

#### What not to say

- "More agents means smarter." It means more tokens and more coordination.

- "Agents should negotiate the answer." Only with shared context and a clear owner.

**Key terms and sources**

When several agents beat one: orchestrator–worker (sub-agents), handoffs between specialists, parallel exploration, debate; what they cost in tokens and coordination; why parallel agents that share a task can make conflicting decisions; and the evidence on both sides (Anthropic's research system vs Cognition's "don't build multi-agents") · built from Anthropic (How we built our multi-agent research system, June 2025), Cognition (Don't Build Multi-Agents, June 2025), Wu et al. (AutoGen, 2023), Du et al. (multi-agent debate, ICML 2024), Cemri et al. (Why Do Multi-Agent LLM Systems Fail?, 2025), the OpenAI Agents SDK handoffs docs and Google's A2A protocol · checked 7 Nov 2026

#### Sources

1. Anthropic, "How we built our multi-agent research system", June 2025.

2. Cognition, "Don't Build Multi-Agents", June 2025.

3. Q. Wu et al., "AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation", 2023, [arXiv:2308.08155](https://arxiv.org/abs/2308.08155); Y. Du et al., "Improving Factuality and Reasoning in Language Models through Multiagent Debate", ICML 2024, [arXiv:2305.14325](https://arxiv.org/abs/2305.14325).

4. M. Cemri et al., "Why Do Multi-Agent LLM Systems Fail?", 2025, [arXiv:2503.13657](https://arxiv.org/abs/2503.13657); OpenAI Agents SDK documentation (handoffs); Google, Agent2Agent (A2A) protocol.

5. A2A protocol specification, version 1.0, [a2a-protocol.org](https://a2a-protocol.org/latest/specification/).
