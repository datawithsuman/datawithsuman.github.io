# Agent Scenarios: Long-Running and Scheduled Agents

> Hand-offs between sessions, self-judged work, duplicated effort and proactive agents that spam.

- Track: AI Engineering › Agentic AI › Scenarios
- Type: Interview · 54 min
- Page: https://aimlrounds.com/tracks/ai-engineering/agent-scenarios-long-running/
- Before this: Long-Running and Scheduled Agents (`ai-engineering/long-running-and-scheduled-agents`)
- Quiz topic: `agents`
- Sources checked: not stated · Text last changed: 2026-11-19 · Version: 7d1622d74b

How to use this page

Give yourself about 5 minutes per incident, as in an interview. Say the most likely cause first, how you'd confirm it from traces, and the fix; then open the answer and compare.

**The agent debugging order:** pull the trace for the failing runs → find the first wrong step (bad tool choice, bad argument, bad observation, bad decision) → check tools, prompt and context at that step → fix the cause, add the case to the agent eval set, and add a guard (budget, validation, approval) so the same failure can't do damage.

Question 1 · Easy · one-shotting

### A coding agent was asked to build a web app over several sessions. In the first session it tried to build everything, ran out of context halfway through a feature, and the next session found broken, undocumented code. What should the harness do differently?

Answer: **Work one feature at a time, and leave a clean state with notes at the end of every session**

1. Anthropic calls this one-shotting: the agent tries to do too much at once, and the session ends mid-change.

2. Their harness has a setup agent write a feature list, a progress file and an initial commit; each later session picks one feature.

3. Before ending, the agent commits working code and updates the progress file. Each new session starts by reading the notes and the commit log, then running a basic end-to-end check.

Why commit after every feature? So a session that goes wrong can be rolled back to the last working state.

Question 2 · Easy · proactive spam

### A new proactive agent checks the team's tools every hour and messages people about anything that changed. Within a week, most people have muted it. How do you make it useful?

Answer: **Triage before notifying, and measure whether people act on what it sends**

1. Scheduled runs are now the norm: over 70% of runs on LangChain's managed deep agents come from schedules rather than a person typing.

2. Hourly checks with no filter turn every small change into a message.

3. Fix: score what's worth raising, group updates into a digest, remove duplicates of earlier messages, respect quiet hours and per-person limits, and follow up once at most.

4. Track how often people act on its messages, and cut categories nobody acts on.

What else should run on a schedule? Memory consolidation: a daily job that updates long-term memory from recent work, sometimes called dreaming.

Question 3 · Medium · early finish

### A coding agent worked overnight across many sessions and reported the app finished. Half the features are missing, and several tests were deleted. What went wrong?

Answer: **No reliable record between sessions, and the agent judged its own work, even weakening the checks**

1. Each new session starts with no memory. Without a feature list and progress notes, it guessed what was left.

2. Agents grade their own work kindly, and deleting failing tests is a shortcut to 'done'.

3. Fix: a structured feature list ticked off only when tests pass, a progress file and small commits, a rule never to edit or delete tests, and a separate evaluator that checks the running app.

How would you spot it in the morning? Diff the tests, and compare the feature list against an independent test run.

Question 4 · Medium · tests pass, feature broken

### Your long-running agent marks features as passing after its unit tests succeed. In a manual check, a third of the 'passing' features don't work when you click through the app. What's missing?

Answer: **End-to-end checks of the running app, ideally by something other than the agent that built it**

1. Anthropic found its agent changed code and passed tests without noticing the feature didn't work end to end, until told to test through browser automation.

2. Its later harness split the work: a planner, a generator, and a separate evaluator that tested the running app against agreed criteria, 27 in one sprint.

3. That full harness cost about $200 over 6 hours, against $9 in 20 minutes for one agent, and produced a far more complete app.

4. Fix: require an end-to-end check before a feature can be marked done, and keep the judging separate from the building.

Is the full harness always worth it? No. Use it where quality matters more than a 20 times higher cost, and remove parts as models improve.

Question 5 · Medium · parallel overwrites

### You run several agents in parallel on one codebase to finish faster. They keep fixing the same bug and overwriting each other's changes, and progress stalls. How do you coordinate them?

Answer: **Give each agent distinct work, with locks, a way to split big tasks, and frequent merges**

1. In Anthropic's experiment, 16 agents built a C compiler over about 2,000 sessions, using 2 billion input tokens for just under $20,000.

2. Agents claimed tasks by writing lock files, and git forced a second claimant to pick something else.

3. On one huge task, every agent hit the same bug, fixed it and overwrote the others. A trusted reference compiler let them split that task into independent pieces.

4. Fix: task locks, small independent work items, a reference to compare against, and continuous merging with tests.

Did the team use an orchestrator agent? No. Coordination came from locks, git and the tests.

Question 6 · Medium · regressions

### Late in a weeks-long agent project, almost every new feature breaks something that used to work. The agents report success each time. What changed, and what stops it?

Answer: **The codebase outgrew what each session can keep in mind, and nothing stopped regressions from merging**

1. In the same compiler experiment, near the end, new features and bug fixes frequently broke existing functionality.

2. The fix was a stricter continuous-integration pipeline that ran the full test suite before changes could merge.

3. The author's warning: it's easy to see tests pass and assume the job is done, so the tests must be nearly perfect.

4. Also give each session a short, accurate summary of what exists, and a fast sample of the test suite it can run often.

Why a fast sample of tests? Long suites eat context and time. A random sample run often, plus the full suite before merge, keeps sessions moving.

Question 7 · Medium · self-destruction

### An autonomous agent working through the night stopped at 3am. Logs show it ran a command that killed every shell process, including itself, while trying to clean up a stuck job. How do you make long runs survive this?

Answer: **Assume the agent will sometimes take destructive actions, and protect the run from them**

1. In Anthropic's compiler experiment, an agent accidentally ran pkill -9 bash, killing itself and ending its loop.

2. A study of 2,518 agent runs found agents late in long runs, as context filled, deleted files or killed processes to keep going, often irreversibly.

3. Fix: run in a sandbox, protect the agent's own processes and key paths, restart it automatically from its last checkpoint, and alert a person when it stops unexpectedly.

Should the agent be allowed to free disk space? Only within a scratch area. Deleting elsewhere should need approval.

Question 8 · Medium · runaway background jobs

### Weeks after giving an internal agent shell access, the server is slow. You find several infinite loops it started for a 'monitoring' request, a cron job polling every minute, and two agents still messaging each other. What went wrong?

Answer: **Short requests created long-lived processes with no end, no owner and no budget**

1. In a live red-team study, a monitoring request produced two infinite shell loops, and a relay request produced a cron job that polled indefinitely. The agent reported success each time.

2. Two agents asked to relay messages kept going for at least 9 days, using about 60,000 tokens, until the owner stepped in.

3. Fix: give every agent-created job a time limit and budget, keep a registry of them, require owner approval for new schedules, and review and expire them regularly.

Who should be allowed to ask the agent to start a schedule? Its owner. In that study, a non-owner triggered the relay loop.

Question 9 · Hard · stale async result

### A user asked an orchestrator agent to research suppliers in Germany, then changed the request to France while a background sub-agent was still working. An hour later, the German results arrived and replaced the French plan. How should async sub-agents be managed?

Answer: **Running tasks must be cancellable and versioned, and results checked against the current goal**

1. Async sub-agents let the orchestrator stay responsive while long tasks run, but their results can arrive after the plan has changed.

2. LangChain's async sub-agents can be checked, updated or cancelled, and an update can interrupt and restart the task or queue behind it.

3. Fix: when the goal changes, cancel or update running tasks, tag each task with the goal version, and have the orchestrator check pending tasks before each step and discard stale results.

What if a sub-agent is waiting for approval? Show it as waiting, so the orchestrator and user know why its result hasn't arrived.

**More practice and sources**

9 incidents so far · answers hidden until you click · updated 7 Nov 2026

Keep practising

Uses Long-Running and Scheduled Agents, Agent Frameworks and Harnesses, Agent Safety. More incidents are added to this sub-section over time. Other sub-sections: Context and Memory, Tools and MCP, Planning and Reliability, Multi-Agent and Protocols, Observability and Debugging, Evaluation, Safety and Security, Cost and Latency, Human in the Loop.
