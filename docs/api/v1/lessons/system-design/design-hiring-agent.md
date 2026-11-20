# Design a Recruiting Assistant Agent

> Recruiters spend hours turning a role into searches, reading profiles and writing outreach. Design an agent that does this work with them, across many steps and days.

- Track: System Design › Agents › Designs
- Type: Design · 25 min
- Page: https://aimlrounds.com/tracks/system-design/design-hiring-agent/
- Before this: Multi-Agent Systems (`ai-engineering/multi-agent-systems`), Human-in-the-Loop Design for Agents (`ai-engineering/human-in-the-loop-design`)
- Quiz topic: `sdllm`

## Intuition

### The situation

A professional network wants an AI assistant for recruiters. Recruiters spend hours turning a role into searches, reading hundreds of profiles and writing messages, and a single role can take days. The interviewer asks:

> Recruiters spend hours turning a role into searches, reading profiles and writing outreach. Design an agent that does this work with them, across many steps and days.

#### Ask before designing

- **Tasks:** turn a role into search criteria, find and evaluate hundreds or thousands of candidates, draft outreach, and track follow-ups.

- **Duration:** work spans hours to days, with the recruiter coming and going.

- **Integrations:** the platform's search and messaging, plus the customer's applicant tracking system.

- **Must never happen:** messaging or rejecting a candidate without the recruiter's say, unfair screening, or one customer's data leaking to another.

- **Success metrics:** time spent reviewing, profiles reviewed per decision, outreach acceptance, and recruiter feedback.

### The idea

Think of a good research assistant. They plan the work, split it among helpers, remember what their boss liked last time, and never send a letter in their boss's name without a signature.

[Figure: A supervisor plans the steps. Sub-agents source, evaluate and draft outreach. The recruiter approves before anything reaches a candidate. Steps run as durable messages.]

_Autonomous inside; a human for anything that reaches a person._

### Play

**Try to break it.** Turn on sending messages and rejecting candidates.

#### Choose what the agent may do alone

Our illustration of the principle; the time shares are made up. The real system was described as a recommendation agent that leaves real-world actions to the human.

Turn on sending and rejecting. The extra time saved is small, but each action reaches a real person and can't be taken back. Internal work can be autonomous; outward, irreversible actions need a human.

**Now say why:** why do outward, irreversible actions need a human even when they save little time?

## Architecture

### Architecture

#### In one breath

A **supervisor** breaks the job into steps (understand the role, source, evaluate, reach out) and hands each to a **sub-agent** built on existing services. Long tasks run as **messages** with guaranteed order and retries, so they survive restarts. **Memory** keeps what the recruiter liked and rejected. The agent **recommends**; the recruiter approves at key points, especially before anything reaches a candidate. Trace everything, and roll out to a few customers first.

#### A supervisor, sub-agents and durable messages

1. **Intake:** the recruiter describes the role; the agent drafts criteria and asks clarifying questions.

2. **Supervisor:** plans the steps and their dependencies, and decides when to pause for the human.

3. **Sub-agents:** sourcing (searches), evaluation (match profiles to criteria and explain why), outreach (draft messages), each calling existing services as tools.

4. **Messaging backbone:** each step is a message, delivered in order, persisted and retried, so a long task survives failures and scales out.

5. **Memory:** conversation memory for the current thread, and experiential memory of preferences learned over time, such as the kinds of profiles this recruiter shortlists.

6. **Client:** streams progress ("searching for qualified profiles…") and pushes results across devices.

##### Agents as services

Each agent is a regular service listed in a registry with its description and how to call it, so the supervisor can discover it. Open protocols like MCP for tools and A2A between agents replace custom wiring over time.

#### The numbers worth saying out loud

All of these are assumptions for the interview, not figures from a real system.

| Question | Working | Result |
|---|---|---|
| Open roles using the agent | given | **50,000** |
| Profiles evaluated a day | 50,000 × 200 | **10 million** |
| Tokens a day for evaluation | 10 million × 3,000 | **30 billion** |
| With a cheap first filter | embeddings drop 80% before the LLM | **6 billion** |

Evaluating every profile with a large LLM is the cost driver; filter first with retrieval and a small model, and save the big model for the shortlist.

## In practice

### In practice

#### What every long-running agent design gets asked

- **Plan or react:** a supervisor that plans steps up front suits a known workflow better than free-form step-by-step reasoning; it's easier to resume and to show progress.

- **Tools and permissions:** authentication and authorisation on every call, including tool calls, scoped to the recruiter and customer.

- **Asking for help:** when unsure, the agent says "I don't know" and asks, rather than guessing.

- **Learning:** implicit signals (repeated profile visits) and explicit ones (shortlisting, declining) update memory, kept separate per recruiter.

- **Fairness:** criteria must be job-related; audit shortlists for bias, and explain each match.

- **Observability:** rich tracing and evaluation before release; privacy-safe traces of LLM calls, tools and memory in production, saved as datasets for regression tests.

##### Rollout

Start with a small beta of customers, watch thumbs-up and thumbs-down on each step, then expand.

#### What the real system reported

- **Architecture:** the existing messaging system became the orchestration layer, with ordered, persisted messages; agents are services in a registry, adopting MCP and A2A; two siloed memories, experiential and conversational.

- **Human control:** agents ask for clarification, feedback or approval at key points; the product acts as a recommendation agent.

- **Tracing:** one tracing tool before release, OpenTelemetry in production, with traces reused for offline evaluation.

- **Results:** users spent 48% less time reviewing applications, reviewed 62% fewer profiles before deciding, and saw 69% higher message acceptance than with traditional sourcing.

From the engineering post and interviews (Sep–Oct 2025). The results are self-reported.

### The answer that sounds right

#### "Make it fully autonomous to save the most time"

It sounds efficient, but most of the time saved comes from searching and shortlisting. Sending messages or rejecting candidates on its own adds little time saved and affects real people irreversibly. Keep those as recommendations the recruiter approves.

## Say it

### Recruiters spend hours turning a role into searches, reading profiles and writing outreach. Design an agent that does this work with them, across many steps and days.

#### The interviewer pushes further

Follow-up 1 of 3

Why not let one big agent loop do everything?

A supervisor with sub-agents is easier to test, resume and scale, and each part can use the right tools and model. A known workflow also suits planning up front.

Follow-up 2 of 3

The service restarts halfway through a two-day task. What happens?

Each step is a persisted message, so the task picks up where it stopped. Steps should be safe to retry, so a repeated step doesn't double-message anyone.

Follow-up 3 of 3

How do you make screening fair?

Use only job-related criteria, explain every match, audit shortlists across groups, and keep a human deciding who is contacted or rejected.

#### The 30-second answer

I'd clarify the tasks, how long they run, the integrations, and which actions affect candidates. A supervisor plans the workflow and delegates to sub-agents for sourcing, evaluation and outreach, each calling existing services as tools. Because tasks span days, every step is a persisted message with ordered delivery and retries, so work survives failures. Memory has two parts: the current conversation, and learned preferences per recruiter. The agent recommends, and the recruiter approves at key points, always before a message or rejection reaches a candidate; when unsure it asks. Every tool call is authenticated and scoped. To control cost, a cheap filter narrows profiles before the LLM evaluates. I'd trace everything, test on saved traces, check fairness, and roll out to a small beta first.

**Key terms and sources**

Based on a professional network's published material: its engineering post ["The LinkedIn Generative AI Application Tech Stack: Extending to Build AI Agents"](https://news.linkedin.com/2025/linkedin-s-ai-stack--expanding-to-build-tomorrow-s-agents) (Sep 2025), [InfoQ's summary](https://www.infoq.com/news/2025/09/linkedin-multi-agent/) (Sep 2025) and an [interview with its engineering lead](https://leaddev.com/ai/how-linkedin-built-ai-hiring-agent) (Oct 2025). The lab is our own illustration; the estimate is ours. Uses multi-agent systems, memory and human-in-the-loop design. · checked 15 Nov 2026
