# Long-Running and Scheduled Agents

> An agent must build an app over many hours, longer than any context window. Another runs every morning without being asked. How do you design harnesses for both?

- Track: AI Engineering › Agentic AI › Lessons
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/ai-engineering/long-running-and-scheduled-agents/
- Before this: Agent Frameworks and Harnesses: Graphs, State and Middleware (`ai-engineering/agent-frameworks-and-harnesses`), Multi-Agent Systems (`ai-engineering/multi-agent-systems`)
- Quiz topic: `agents`
- Sources checked: 2026-11-07 · Text last changed: 2026-11-20 · Version: 99eef1e38e

## Intuition

### The situation

Your agent must build a web app over many hours, far longer than one context window. On the first try, it forgot what it had done, redid work, and declared the job finished with half the features missing. The interviewer asks:

> An agent must build an app over many hours, longer than any context window. Another runs every morning without being asked. How do you design harnesses for both?

#### Why it matters

Agents are moving from chat replies to jobs that take hours, and to work that happens in the background. The hard parts are continuity across sessions, checking the agent's own work, and running without supervision. Interviewers ask how you'd keep a long run on track. This lesson builds on Agent Frameworks and Harnesses.

### The idea

Think of shift workers on a long project. Each shift starts by reading the handover notes and the task board, does one job properly, and updates the notes before leaving. A separate inspector checks the work before it's signed off.

[Figure: Three habits. Write state down. Separate building from judging. Triage before acting on a schedule.]

_Each new session starts with no memory._

### Play

**Try to break it.** Run 200 features with no notes. Then add a progress file.

#### What handoff notes save

Illustrative: 10 features per session, 40,000 tokens of work per session, and re-orientation of 60,000 tokens without notes or 8,000 with them. Notes also stop a session from redoing or skipping work, which this doesn't count.

A 200-feature job at 10 features per session takes 20 sessions. Without notes, each session re-reads the code to work out where things stand, and the job uses 2.0 million tokens. With a progress file and commit log, it's 0.96 million. The bigger win isn't counted here: without notes, sessions redo finished features or declare the job done early, which is what Anthropic's feature list and test rules prevent.

**Now say why:** why does the saving grow with the number of sessions?

## How it works

### How it works

#### In one breath

Long tasks outgrow one context window, so the agent works in **sessions**, and each new session starts with no memory. Anthropic's harness for long coding tasks uses a **setup agent** that writes a feature list and a progress file, then **working agents** that each pick one feature, test it, commit, and update the notes for the next session. A later version added a **planner** and a separate **evaluator** that checks the work. It cost far more, $200 over 6 hours against $9 in 20 minutes for one agent, and produced a much better app. Meanwhile many agents now run on **schedules**: over 70% of LangChain's managed deep agent runs are scheduled, not started by a person.

#### How the harnesses work

##### Working across sessions

- **Setup agent:** turns the request into a structured feature list, over 200 items for a web app clone in Anthropic's example, plus a progress file and an initial commit.

- **Working agent:** each session reads the progress notes and recent commits, picks one unfinished feature, builds and tests it, then commits and updates the notes.

- **Guardrails in the prompt:** Anthropic told agents that removing or editing tests is unacceptable, because agents otherwise mark work done by weakening the checks.

##### Generator and evaluator

Agents grade their own work too kindly. Anthropic's 2026 harness split roles, like a GAN: a **planner** writes the spec, a **generator** builds, and an **evaluator** tests the running app against agreed criteria, such as 27 checks in one sprint. For a retro game maker, one agent took 20 minutes and $9, and the full harness took 6 hours and $200, over 20 times more, for a far more complete result. Their principle: every part of a harness encodes an assumption about what the model can't do alone, so remove parts as models improve. With a newer model, they dropped the sprint structure.

##### Scheduled and proactive agents

Some agents run on a timer: a morning digest, a nightly reconciliation, follow-ups on open tickets. LangChain reported that over 70% of runs on its managed deep agents come from schedules. The hard design question is being proactive without being annoying: triage what's worth raising, follow up once, and consolidate memory between runs.

##### Async sub-agents

Long jobs increasingly hand work to sub-agents that run in parallel and report back later, rather than blocking the main agent.

#### The maths

$$ {\text{tokens}} = {S}\,({t_{\text{orient}}} + {t_{\text{work}}}) $$

Good handoff notes shrink re-orientation in every session, so the saving grows with the number of sessions.

- **total tokens**: Across the whole job.

- **sessions**: How many fresh context windows the job needs.

- **re-orientation**: Tokens each session spends working out where things stand.

- **useful work**: Tokens spent building and testing.

## In practice

### In practice

#### In practice

- **Write state down:** a feature list, a progress file and small commits are the agent's memory between sessions.

- **Separate building from judging:** an evaluator with clear criteria, ideally running real tests, catches what self-review misses.

- **Protect the tests:** forbid editing or deleting them, and check diffs.

- **Budget the harness:** a full harness can cost 20 times more. Use it where quality is worth it.

- **For scheduled agents:** triage before notifying, deduplicate, cap actions per run, and log everything, since nobody is watching live.

- **Revisit the harness with each model:** remove scaffolding the model no longer needs.

### The answer that sounds right

#### "Just give it a bigger context window"

It sounds simpler, but every call re-reads the whole context, models use very long contexts less reliably, and the agent still judges its own work too kindly. Use notes between sessions and a separate evaluator.

## Say it

### An agent must build an app over many hours, longer than any context window. Another runs every morning without being asked. How do you design harnesses for both?

#### The interviewer pushes further

Follow-up 1 of 3

The agent declared the job done with half the features missing. Why?

A new session had no reliable record of what remained, or it judged its own work too kindly. Use a structured feature list it must tick off with tests, and an evaluator that checks the result.

Follow-up 2 of 3

Why not use one huge context window instead of sessions?

Cost and quality: every call re-reads the whole context, and models use very long contexts less reliably. Notes and fresh sessions keep each window focused.

Follow-up 3 of 3

How do you stop a scheduled agent spamming people?

Triage what's worth raising, deduplicate against earlier messages, limit actions per run, and measure how often people act on its messages.

#### The 30-second answer

Long tasks outgrow a context window, so the agent works in sessions that start with no memory. I'd have a setup agent write a feature list and progress file, then working sessions that each pick one feature, test it, commit and update the notes, with a rule never to edit tests. For quality, separate a planner, a generator and an evaluator that tests the running result; Anthropic's full harness cost about 20 times more than one agent but built a far better app. For scheduled agents, which are now most runs on some platforms, I'd triage before notifying, cap actions and log everything.

**Key terms and sources**

Agents that work across many context windows: setup agents, feature lists and progress files, generator and evaluator loops, what harnesses cost, and scheduled, proactive agents that run without a user asking. · checked 7 Nov 2026

#### Sources

- [Anthropic, Effective harnesses for long-running agents, Nov 2025](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

- [Anthropic, Harness design for long-running application development, Mar 2026](https://www.anthropic.com/engineering/harness-design-long-running-apps)

- [LangChain, How to build proactive, always-on agents, Oct 2026](https://www.langchain.com/blog/proactive-agents)

- [LangChain, New context engineering challenges in late 2026](https://www.langchain.com/blog/context-engineering-challenges-late-2026)

- [Merrill et al., Terminal-Bench](https://arxiv.org/abs/2601.11868)

Explanations are ours, built from these sources. Lab numbers are illustrative unless a lab says otherwise. Many recent papers are preprints, and provider policies change.
