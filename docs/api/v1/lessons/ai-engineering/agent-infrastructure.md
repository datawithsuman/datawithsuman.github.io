# Agent Infrastructure: Durable Execution, Retries and Budgets

> How do long agent runs survive failures without paying twice?

- Track: AI Engineering › Agentic AI › Lessons
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/ai-engineering/agent-infrastructure/
- Before this: What Is an Agent? The ReAct Loop (`ai-engineering/what-is-an-agent`)
- Quiz topic: `agents`

## Intuition

### The situation

A nightly agent reconciles the day's refunds in 100 steps, and each step has a small chance of a transient failure. A colleague says if it fails, just run it again. Some of those steps have already issued refunds. The interviewer asks:

> How do long agent runs survive failures without paying twice?

**Running example:** a nightly agent reconciles the day's refunds: 100 steps of lookups, checks and corrections. Each step has a small chance of a transient failure (API timeout, rate limit).

#### Long chains of unreliable calls

LLM APIs return rate-limit errors, tools time out, workers get redeployed. A 30-second chatbot reply can simply be retried; a 2-hour agent run can't afford to restart from step 1 each time something blips, and some of its steps have already changed the world (refunds issued).

### The idea

Think of a long video game. Without save points, one mistake sends you back to level 1. And when you retry a shop purchase after a crash, you want a receipt number, so the shop knows not to charge you again. Those are checkpoints and idempotency keys.

[Figure: A 100-step task with 2 percent failures per step. Restarting from scratch takes about 327 step executions, with 69.4 percent wasted. Checkpointing every step takes about 102, with 2 percent wasted.]

_From the lab, with independent transient failures and a failed step retried._

### Play

**Try to break it.** At 100 steps and 2% failures, compare restarting from scratch with checkpointing every step. Then raise the steps to 200.

#### "If it fails, just run it again"

Independent transient failures; a failed step is retried. Restart: any failure sends the task back to step 1. Checkpoint: only the failed step is repeated.

With **100 steps** and a **2%** transient failure rate per step, only **13.3%** of runs finish without a hiccup. If every failure means **starting over**, finishing takes about **327** step executions on average: **69.4%** of the work (and the money) is repeated, and at 200 steps it's 93% waste. With a **checkpoint** after every step, it takes about **102** executions (2% waste). And because steps like "issue refund" may have run before the crash, replays must be **idempotent**.

**Now say why:** checkpoints mean a crash just re-runs a step, so what could go wrong if that step was issue_refund?

## How it works

### How it works

#### In one breath

An agent task can run for minutes or hours, making dozens of model and tool calls, any of which can fail: rate limits, timeouts, flaky APIs, a deploy restarting the worker. If a failure means **starting over**, long tasks rarely finish and you pay for the same work again and again. **Durable execution** saves the agent's state after every step (a **checkpoint**), so it resumes exactly where it stopped; combined with **retries with backoff**, **idempotent tools** (so a retried refund doesn't pay twice), **timeouts**, **step and cost budgets**, pauses for **human approval**, and **tracing** of every step, it turns a demo into a service. Frameworks like LangGraph (checkpointers), the OpenAI and Claude Agent SDKs, and workflow engines like Temporal provide these pieces; the details change fast, the needs don't. What you'll be able to do after this: design reliable agent execution, explain checkpoints and idempotency, and list what to monitor.

#### The reliability toolkit

- **Checkpointing / durable execution:** persist state (messages, tool results, plan) after each step; on failure, resume from the last checkpoint. LangGraph checkpointers and Temporal-style workflows do this.

- **Retries:** exponential backoff with jitter for transient errors; don't retry non-transient ones (invalid arguments).

- **Idempotency:** side-effecting tools take an idempotency key, so replays after a crash don't duplicate refunds or emails.

- **Timeouts and budgets:** per call, per step and per task (max steps, max tokens, max dollars); stop and escalate when exceeded.

- **Human-in-the-loop:** pause at approval points, persist state while waiting (minutes or days), resume on approval.

- **Observability:** trace every model call, tool call, token count and cost per step (OpenTelemetry GenAI conventions, LangSmith-style tools); replay failed runs.

## In practice

### In practice

#### Frameworks and what to look for

- **Agent frameworks:** LangGraph (graphs with checkpointers, human interrupts), OpenAI Agents SDK (agents, handoffs, guardrails, tracing), Claude Agent SDK (the agent loop behind Claude Code, tools, sub-agents, context compaction), and others. They change quickly: choose on persistence, observability, control and team fit.

- **Durable workflow engines** (Temporal and similar) run long agent processes with retries, timers and state as ordinary workflows, increasingly used for production agents.

- **Deployment:** run agents as async jobs with queues, not inside an HTTP request; stream progress to the user; make cancellation possible.

- **Monitor:** success rate, steps and cost per task, tool error rates, loops detected, budget stops, escalations; alert on drifts.

Current frameworks share a few concepts: LangGraph saves checkpoints per thread, pauses with interrupts and can replay or branch from any checkpoint; LangChain 1.x adds middleware for retries, fallbacks, summarisation, approvals and call limits; Google ADK has callbacks and graph workflows. See Agent Frameworks and Harnesses and Long-Running and Scheduled Agents.

#### Treat an agent run like a long-running transaction

Persist state after every step, retry transient failures, make side effects idempotent, bound everything with budgets, and trace it all, so long tasks finish once and safely.

### The answer that sounds right

#### "Just retry the whole task"

It sounds right, since it's how you'd handle a 30-second chatbot reply. But in the lab, restarting a 100-step task wastes 69.4% of the work, and at 200 steps it's 93%. It also repeats side effects. And don't run the agent inside the API request: long tasks need async jobs.

## Say it

### How do long agent runs survive failures without paying twice?

#### The interviewer pushes further

Follow-up 1 of 3

A crash happened right after issue_refund succeeded but before the checkpoint. What now?

On resume the step re-runs; the idempotency key makes the refund service return the existing result instead of paying again.

Follow-up 2 of 3

How do you stop runaway costs?

Hard per-task budgets on steps, tokens and dollars, loop detection (repeated identical calls), and alerts on cost-per-task outliers.

Follow-up 3 of 3

What would you trace?

Each step's prompt version, model, inputs/outputs (redacted), tool calls and results, latency, tokens and cost, linked by a run ID for replay.

#### The 30-second answer

Agent runs are long chains of calls that fail transiently, so I'd use durable execution: checkpoint state after every step so the run resumes instead of restarting; with 100 steps at 2 percent failure, restarting wastes about 70 percent of the work while checkpointing wastes about 2. Add retries with backoff for transient errors, idempotency keys on side-effecting tools so replays don't double-refund, timeouts and step, token and cost budgets, persisted pauses for human approval, and full tracing of every call. Frameworks like LangGraph or the agent SDKs, or a workflow engine like Temporal, provide these; I'd run agents as async jobs with progress streaming and cancellation.

**Go further**

#### What not to say

- "Just retry the whole task." It wastes work and repeats side effects.

- "Run the agent inside the API request." Long tasks need async jobs.

**Key terms and sources**

What it takes to run agents reliably in production: long-running tasks that survive crashes (durable execution and checkpoints), retries with backoff, idempotent tools, timeouts and budgets, human-in-the-loop pauses, observability and tracing, and the framework landscape (LangGraph, OpenAI Agents SDK, Claude Agent SDK, Temporal-style workflow engines) · built from the LangGraph persistence documentation, Temporal documentation, the OpenAI Agents SDK and Claude Agent SDK documentation, OpenTelemetry GenAI semantic conventions, and Meta's Llama 3 report on long-running job reliability · checked 7 Nov 2026

#### Sources

1. LangGraph documentation: persistence, checkpointers and human-in-the-loop.

2. Temporal documentation: durable execution, retries and idempotency.

3. OpenAI Agents SDK documentation (agents, handoffs, guardrails, tracing); Anthropic, Claude Agent SDK documentation.

4. OpenTelemetry, semantic conventions for generative AI systems; Llama Team, "The Llama 3 Herd of Models", 2024, [arXiv:2407.21783](https://arxiv.org/abs/2407.21783) (checkpointing long jobs through frequent interruptions).
