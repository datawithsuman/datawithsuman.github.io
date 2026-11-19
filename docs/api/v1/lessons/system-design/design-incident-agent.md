# Design an Incident Investigation Agent

> When an alert fires at 3 a.m., the on-call engineer spends most of the first half hour gathering context. Design an agent that investigates the alert and hands the engineer a head start.

- Track: System Design › Agents › Designs
- Type: Design · 25 min
- Page: https://aimlrounds.com/tracks/system-design/design-incident-agent/
- Before this: Tool and Function Calling (`ai-engineering/tool-calling`), Agent Safety: Permissions, Sandboxing and the Lethal Trifecta (`ai-engineering/agent-safety`)
- Quiz topic: `sdllm`

## Intuition

### The situation

A company runs hundreds of services across many clusters and regions. When an alert fires at night, the on-call engineer spends most of the first half hour just gathering context. The interviewer asks:

> When an alert fires at 3 a.m., the on-call engineer spends most of the first half hour gathering context. Design an agent that investigates the alert and hands the engineer a head start.

#### Ask before designing

- **Trigger:** an alert or page, plus maybe failed synthetic tests.

- **Scope:** hundreds of services across many clusters and regions; logs, metrics, traces, deploys and config changes.

- **Latency:** findings within minutes, ideally before the engineer opens a laptop.

- **Must never happen:** the agent changing production on its own, or stating a guess as the root cause.

- **Success metrics:** root-cause accuracy on past incidents, time to first useful finding, engineer ratings, and time to resolve.

### The idea

Think of a junior detective sent ahead to the scene. They collect the facts, check the usual suspects in parallel and write up what they found and how sure they are. They don't make arrests; the senior detective decides.

[Figure: An alert fires. The agent gathers context, runs structured checks in parallel, tests hypotheses with targeted queries, and reports evidence and confidence. Fixes need a human.]

_The agent investigates; the human decides._

### Play

**Try to break it.** Start at 20-second queries and three hypotheses. Turn on parallel testing. Then drop the query latency.

#### Queries times latency, per hypothesis

The guide's example: 20 queries at 20 seconds each is nearly 7 minutes per hypothesis, and agents ran 6 to 27 queries per investigation. Queries run one after another within a hypothesis here, as each depends on the last.

Start at 20-second queries, one hypothesis at a time. Then turn on parallel testing, and drop latency to one second. A slow data store, not the LLM, is often what makes the agent too late to help.

**Now say why:** why can a slow data store matter more than the LLM?

## Architecture

### Architecture

#### In one breath

Start when the alert fires. Gather context first: the alert, runbooks, recent deploys, past incidents. Run **structured checks in parallel** (platform health, the service's logs, metrics and traces, the team's runbook), then let the LLM form **hypotheses** and test each with targeted queries, marking it confirmed, ruled out or unclear. Tools are **read-only** and rate-limited. Report evidence and confidence in the incident channel; any fix needs **human approval**.

#### Checks first, then hypotheses, then a human

1. **Trigger:** the alert arrives with service, severity and timing.

2. **Gather context:** read the alert message and linked runbook, recent deploys and config changes, and past investigations of this alert.

3. **Parallel checks:** platform health (cloud, network, dependencies), service analysis (errors, latency, logs and traces against a baseline), and the team's runbook steps.

4. **Hypothesise and test:** the LLM proposes causes and runs targeted queries for each, marking it confirmed, ruled out or unclear.

5. **Report:** post a summary, the evidence and confidence to the incident channel; the engineer can ask follow-ups.

6. **Act with approval:** suggest a rollback or a fix as a draft; a human approves before anything runs.

##### Tools

Wrap observability, deploy and alert systems behind purpose-built APIs that handle authentication, rate limits and consistent formats. Agents query in bursts and in parallel, unlike people, so the API layer must protect the backends.

#### The numbers worth saying out loud

All of these are assumptions for the interview, not figures from a real system.

| Question | Working | Result |
|---|---|---|
| Investigations a day | given | **2,000** |
| Queries a day | 2,000 × 20 | **40,000** |
| LLM tokens a day | 2,000 × 300,000 | **600 million** |
| Peak queries a second | an outage triggers 200 alerts at once × 20 queries ÷ 60 s | **about 67** |

The peak matters most: one big outage fires many alerts together, so dedupe related alerts into one investigation and rate-limit tools.

## In practice

### In practice

#### What every investigation agent gets asked

- **Tools and permissions:** read-only by default. Writes (rollbacks, restarts) go through a separate approval path; only well-understood, low-risk runbook actions may ever run automatically.

- **Structured before open-ended:** run fixed checks first; they're cheap, reliable and give the LLM evidence to reason about.

- **Memory:** past investigations of the same alert, and engineers' corrections, guide the next one. Short log retention limits this.

- **When to stop:** a budget of queries and time; if confidence stays low, say so and show the evidence gathered, rather than guessing.

- **Cost:** token use per investigation is unpredictable, so cap it and track it per team.

- **Prompt injection:** log lines are untrusted text; never let them change the agent's instructions or tools.

##### Evaluation

Replay past incidents and injected faults with known causes; score whether the agent found the cause, with how much guidance, and how many queries and tokens it used.

#### What the real systems reported

- **Internal agent:** context gathering took 60 to 80% of investigation time; the agent starts on every incident and runs three tracks in parallel. It serves 150+ teams and over 2,000 investigations a day, and today it only investigates, with guided mitigation as the next step.

- **Commercial agent:** generates several hypotheses and marks each validated, invalidated or inconclusive; triage that took over 30 minutes now runs automatically; fixes come as pull requests for engineers to review.

- **Experiment:** four frontier models investigated injected faults through a database tool; none found every root cause without guidance, and the authors concluded autonomous root-cause analysis "is not there yet".

From the posts (2025–2026). Figures are self-reported by the companies.

### The answer that sounds right

#### "Let the agent fix incidents automatically"

It sounds like the end goal, but in a published test four frontier models couldn't find every root cause without guidance. An agent acting on a wrong guess can make an outage worse. Investigate automatically, and keep a human approving fixes.

## Say it

### When an alert fires at 3 a.m., the on-call engineer spends most of the first half hour gathering context. Design an agent that investigates the alert and hands the engineer a head start.

#### The interviewer pushes further

Follow-up 1 of 3

Should the agent roll back a bad deploy on its own?

Not by default. Experiments show models still miss root causes without guidance, so propose the rollback with evidence and let a human approve. Automate only low-risk, well-understood runbook steps.

Follow-up 2 of 3

The agent overloaded the logging cluster during an outage. Why?

Agents query in bursts and in parallel, and an outage fires many alerts at once. Dedupe related alerts into one investigation, and rate-limit tool APIs.

Follow-up 3 of 3

How do you know it's any good?

Replay incidents with known causes and inject faults; measure whether it finds the cause, how much guidance it needs, and its time and cost. Then track engineer ratings live.

I'd clarify triggers, the data available, how fast findings must arrive and what the agent may change. When an alert fires, the agent gathers context first: the alert, runbook, recent deploys and past incidents. It runs structured checks in parallel, like platform health and the service's logs, metrics and traces against a baseline. Then the LLM proposes hypotheses and tests each with targeted queries, marking them confirmed, ruled out or unclear. Tools sit behind APIs that are read-only and rate-limited. It posts a summary with evidence and honest confidence to the incident channel, and the engineer can ask follow-ups. Fixes are drafts that a human approves. I'd evaluate by replaying past incidents and injected faults, and cap queries, time and tokens per investigation.

**Key terms and sources**

Based on published write-ups: an observability company's investigation agent (Jun 2025, updated Dec 2025), a data platform's internal AI SRE (Aug 2026), a database company's guide and its experiment (Aug 2025). The lab's arithmetic follows the guide's example; the estimate is ours. Uses tool calling, agent safety and human-in-the-loop design.
