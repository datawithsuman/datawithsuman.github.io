# Agent Frameworks and Harnesses: Graphs, State and Middleware

> Your team is choosing between LangGraph, LangChain's agent middleware, Google ADK, an agent SDK, or writing its own loop. What concepts should drive the choice?

- Track: AI Engineering › Agentic AI › Lessons
- Type: Concept · 22 min
- Page: https://aimlrounds.com/tracks/ai-engineering/agent-frameworks-and-harnesses/
- Before this: Agent Infrastructure: Durable Execution, Retries and Budgets (`ai-engineering/agent-infrastructure`)
- Quiz topic: `agents`

## Intuition

### The situation

Your team is building a refund agent that pauses for manager approval, must survive restarts, and needs retries and cost limits. Someone wants to pick whichever framework has the most stars. The interviewer asks:

> Your team is choosing between LangGraph, LangChain's agent middleware, Google ADK, an agent SDK, or writing its own loop. What concepts should drive the choice?

#### Why it matters

The core agent loop is a few lines. Production needs much more: surviving crashes, pausing for approval, trimming context, retrying, limiting cost, and tracing. Frameworks differ in how they provide these, and they change monthly, so interviewers ask about the concepts underneath. This lesson builds on Agent Infrastructure.

### The idea

Think of a car. The engine is the model, but the brakes, seatbelts, dashboard and fuel gauge are what make it safe to drive. That's the harness. Frameworks are different car makers' versions of those parts.

[Figure: Three building blocks. State and checkpoints. Interrupts and replay. Middleware around calls.]

_Agent = model + harness._

### Play

**Try to break it.** Run 40 steps with no retries. Then add retries, a call limit and summarisation.

#### What middleware buys a long run

Illustrative: 40 steps, a 3% transient failure per step, a 4,000-token prompt, and 3,000 tokens of tool results added each step. Summarisation is modelled as capping context at 50,000 tokens. The call limit stops the run at 25 steps, which caps cost but may leave the task unfinished.

Without retries, a 40-step run with 3% transient failures finishes only 30% of the time. Two retries per call lift that to 99.9%. Without summarisation, the context grows to 124,000 tokens, and the run reads 2.62 million input tokens in total. Summarising past 50,000 tokens caps the context and cuts the total to 1.67 million, at the risk of dropping a detail. A tool call limit stops runaway loops, but a legitimate long task will stop unfinished, so pair it with a clear message or escalation.

**Now say why:** why do retries help so much more than a better prompt here?

## How it works

### How it works

#### In one breath

LangChain puts it simply: **agent = model + harness**. The harness is everything around the model: the prompt, tools, loop, memory, error handling and limits. Frameworks package the harness in two main ways. **Graph runtimes** such as LangGraph model the agent as nodes that update a shared **state**, save a **checkpoint** after each step, can **pause** for a human and resume, and can replay or branch from any past step. **Middleware** wraps each model and tool call with reusable behaviour: retries, fallbacks, summarisation, approval, call limits and redaction. "Deep agents" add planning, a file system and sub-agents. Many production teams still write their own loop: 85% of interviewed teams in one 2025 study did.

#### The concepts

##### Graph runtimes

- **State:** a typed object passed between nodes, such as messages, a plan and results.

- **Nodes and edges:** nodes are functions that read state and return updates. Edges decide what runs next, either fixed or conditional. LangGraph can also fan out to many copies of a node, and a node can update state and choose the next step at once.

- **Merge rules:** each state field has a rule for combining updates. Without one, a new value overwrites the old. A message list usually appends.

- **Steps:** nodes that can run together run in one step. LangGraph calls these super-steps, and stops after a limit, 10,007 by default since version 1.1.4.

- **Checkpoints and threads:** a checkpointer saves state after each step under a thread ID, which gives short-term memory, crash recovery and pauses. A separate **store** keeps long-term memory across threads.

- **Interrupts:** a node can pause for human input and resume later on the same thread. When it resumes, the node restarts from its beginning, so code before the pause runs again and must be safe to repeat.

- **Time travel:** replay from an earlier checkpoint, or change state there and branch, without losing history.

##### Middleware

LangChain 1.x builds agents with `create_agent`, and customises them with **middleware**: hooks that run before or after the model, or wrap model and tool calls. Built-in examples include retries with backoff, falling back to another model, summarising old messages past a token threshold, pausing for approve, edit or reject decisions, limits on model and tool calls, and detecting personal data. Google's ADK has similar **callbacks** before and after agents, models and tools.

##### Workflow agents

ADK offers sequential, parallel and loop agents for fixed patterns. Its loop agent doesn't decide when to stop on its own, so you set a maximum or an exit signal. In ADK 2.0, graph-based workflows supersede these templates.

##### Deep agents

For long, open-ended work, "deep agents" add a planning tool (a to-do list), a virtual file system for offloading context, sub-agents with their own clean contexts, memory files such as AGENTS.md, and skills. Claude Code is the best-known example of this shape.

##### Build or buy?

In the Measuring Agents in Production study, 17 of 20 interviewed teams built their own loop, for flexibility, simplicity and security rules, though 61% of surveyed teams used a framework. A framework pays off when you need checkpoints, interrupts and tracing quickly. Your own loop pays off when you need tight control.

#### The maths

$$ P(\text{run finishes}) = \big(1 - f^{\,r+1}\big)^{N} $$

Assumes failures are independent and passing. Retries don't help with real errors, like a bad argument, which is why retry middleware should only retry transient ones.

- **the run finishes**: Every step eventually succeeds.

- **transient failure rate**: The chance a single model or tool call fails for a passing reason.

- **retries**: Retry middleware tries again r times.

- **steps**: More steps give more chances to fail.

## In practice

### In practice

#### In practice

- **Choose on concepts:** durable checkpoints, interrupts, streaming, tracing and how easily you can control the loop, not on demos.

- **Use a real checkpointer in production:** in-memory savers lose everything on restart.

- **Make code before an interrupt safe to repeat:** resuming re-runs the node from its start.

- **Retry only transient errors:** and pair call limits with an escalation path.

- **Summarise with care:** keep critical facts outside the summary, in memory or state. See Memory and Context Engineering.

- **Expect churn:** APIs change between minor versions, so wrap the framework thinly.

### The answer that sounds right

#### "Pick the most popular framework"

It sounds sensible, but frameworks change monthly, and what matters is how they handle checkpoints, interrupts, retries, limits and tracing. Many production teams write their own loop for control. Choose on concepts, and wrap the framework thinly.

## Say it

### Your team is choosing between LangGraph, LangChain's agent middleware, Google ADK, an agent SDK, or writing its own loop. What concepts should drive the choice?

#### The interviewer pushes further

Follow-up 1 of 3

After resuming from an approval interrupt, an email was sent twice. Why?

On resume, the node restarts from its beginning, so the email call before the interrupt ran again. Move side effects after the interrupt, into their own node, or make them idempotent.

Follow-up 2 of 3

Checkpointer or store: what's the difference?

A checkpointer saves one thread's state step by step, for resuming and short-term memory. A store keeps data across threads, such as user preferences, for long-term memory.

Follow-up 3 of 3

When would you skip a framework?

When the loop is simple, you need tight control or strict dependency rules, and you can add checkpoints, retries and tracing yourself.

An agent is a model plus a harness: prompt, tools, loop, memory, error handling and limits. Graph runtimes like LangGraph model it as nodes updating shared state with merge rules, checkpoint after each step under a thread, pause for humans with interrupts, and let you replay or branch from any checkpoint. Middleware, as in LangChain 1.x or ADK callbacks, wraps model and tool calls with retries, fallbacks, summarisation, approvals and limits. Deep agents add planning, a file system and sub-agents. I'd choose on durability, interrupts, tracing and control, and remember many production teams write their own loop: 17 of 20 in one study.

**Key terms and sources**

Agent = model + harness. How graph runtimes work (state, merge rules, steps, checkpoints, threads, interrupts, time travel, subgraphs), middleware hooks around model and tool calls, workflow agents, 'deep agents' with planning, files and sub-agents, and when to build your own.

#### Sources

- LangGraph documentation: graph API, persistence, interrupts, time travel

- LangChain documentation: agents and built-in middleware

- LangChain Deep Agents documentation

- Google Agent Development Kit documentation

- OpenAI Agents SDK guide

- Pan et al., Measuring Agents in Production, ICML 2026

Explanations are ours, built from these sources. Lab numbers are illustrative unless a lab says otherwise. Many recent papers are preprints, and provider policies change.
