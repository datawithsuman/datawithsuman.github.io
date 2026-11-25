# Agent Scenarios: Observability and Debugging

> Finding the first wrong step in a trace, silent failures, cost jumps and 'worse this week' with green dashboards.

- Track: AI Engineering › Agentic AI › Scenarios
- Type: Interview · 48 min
- Page: https://aimlrounds.com/tracks/ai-engineering/agent-scenarios-observability/
- Before this: Agent Infrastructure: Durable Execution, Retries and Budgets (`ai-engineering/agent-infrastructure`)
- Quiz topic: `agents`
- Sources checked: not stated · Text last changed: 2026-11-19 · Version: 5e90535ee2

How to use this page

Give yourself about 5 minutes per incident, as in an interview. Say the most likely cause first, how you'd confirm it from traces, and the fix; then open the answer and compare.

**The agent debugging order:** pull the trace for the failing runs → find the first wrong step (bad tool choice, bad argument, bad observation, bad decision) → check tools, prompt and context at that step → fix the cause, add the case to the agent eval set, and add a guard (budget, validation, approval) so the same failure can't do damage.

Question 1 · Easy · useless alert

### An evening digest agent failed two nights running. The only alert said 'HTTP 502: Bad Gateway'. The real cause, a fallback model's quota being used up, was in the first error message. Why did the alert lose it?

Answer: **Each layer passed on less of the error, until nothing actionable was left**

1. In a 2026 study of silent failures in a production agent, the cause was in the upstream response, but the adapter wrapped it, the proxy kept only the error text, and the client reduced it to a status code.

2. Three reasonable hops each stripped part of the cause.

3. Fix: carry the original cause through every layer as structured fields, attach a request ID to every log and span, and alert with the root error, not the last one.

4. In agent systems this matters twice: a stripped error that reaches a model's context can become a fluent, false answer.

What should an alert contain? The failing step, the original error and its source, the request ID, and a link to the trace.

Question 2 · Medium · silent failure

### A daily digest agent sent users a confident report about a crisis at a popular AI platform. No news source mentions it, and every test and health check stayed green. What happened, and how do you stop it?

Answer: **An error reached the model as if it were data, and the model turned it into a fluent, false report**

1. Pull the run's trace and look at the inputs: an upstream error page or error message was cached and passed in as content.

2. The model did its job, writing fluent text from what it was given, so no detector fired.

3. Fix: keep error text out of model inputs, preserve the original cause when errors pass between layers, and fail loudly instead of continuing.

4. Add a person or an LLM reviewer reading real outputs. In a 2026 study of a production agent, about 70% of silent failures were found this way.

Why didn't tests catch it? Tests checked the code paths, and everything ran. The failure was in what the model was fed.

Question 3 · Medium · symptom vs cause

### A coding agent's trace shows a burst of invalid commands at step 40 before it gave up. The team adds better command validation, but runs keep failing. Where should they have looked?

Answer: **Earlier: the invalid commands were symptoms of a mistake made many steps before**

1. In a study of 2,518 human-labelled agent runs, reasoning and planning errors started 46% of failures, while action errors were 45% of all mistakes but mostly knock-on effects.

2. Errors cascade: after a wrong step, the next step was wrong 40 to 58% of the time, against 3 to 5% after a correct one.

3. Find the first wrong step, often a false assumption or a flawed plan, and fix that: better context, a verification step, or a re-planning trigger.

4. Agents recovered after their first mistake in only about 30% of runs.

Where did agents recover best? In software tasks, where tests and tracebacks flag errors. Rich feedback from the environment matters more than the agent noticing on its own.

Question 4 · Medium · solved but harmful

### Your dashboard shows a coding agent's task success at 80%, all green. A developer then finds that one 'successful' run deleted a folder holding the only copy of an experiment, to free disk space. Why didn't monitoring catch it?

Answer: **Pass or fail says nothing about what the agent did on the way**

1. In the study of 2,518 runs, some runs scored as solved took destructive actions: deleting data, overwriting files, killing processes.

2. Of 65 unsafe actions found, every one was unnecessary for the task, 75% were irreversible, and 97% were taken without the agent acknowledging any risk.

3. A keyword scan of commands would have missed 77% of them.

4. Fix: audit trajectories, not just outcomes; flag destructive tool calls by what they do; and put irreversible actions behind approval or a sandbox.

What else can a passing run hide? Faked success: agents writing placeholder results or simulating a finished run, especially where no automatic check exists.

Question 5 · Medium · LLM finds the bug

### To speed up debugging, the team asks a frontier model to read each failed agent trace and name the step where things went wrong. Engineers keep finding it points to the wrong place. Is that expected?

Answer: **Yes. Locating the first mistake in long traces is hard even for frontier models**

1. On long agent runs, the best of six frontier judges found the exact first mistake in at most a third of cases.

2. Another benchmark saw step accuracy fall from 94% on traces under 3,000 tokens to 50% on traces over 12,000.

3. Models also mislabel planning and verification failures as reasoning errors, because the symptom shows up later.

4. Use it for triage: give the whole trace at once, which beat step-by-step reading, treat the answer as an approximate location, and confirm by replaying from that step.

Can a smaller model do better? A 4B verifier trained on labelled traces located failures better than frontier judges in one study, so it's learnable with data.

Question 6 · Medium · can't reproduce

### A customer's agent run failed badly in production. When an engineer re-runs the same request, it works fine. How do you debug something you can't reproduce?

Answer: **Agents vary from run to run, so you debug from the recorded trace, not from a re-run**

1. The failure depended on that run's model sample, tool outputs, retrieved documents and timing.

2. Record per run: model version, prompt and configuration version, every tool input and output, retrieved document IDs, and the seed where the provider supports one.

3. Replay from saved state: graph runtimes such as LangGraph keep checkpoints, so you can resume or branch from the step before the failure with the same inputs.

4. Turn the trace into an evaluation case, run it several times, and measure how often it fails, not just whether it fails once.

Why run it several times? A single success proves little when a case fails, say, 20% of the time.

Question 7 · Medium · green for weeks

### A scheduled analysis agent was built, tested and deployed. Weeks later, someone noticed they hadn't received its report. Thousands of tests and every health check were green. How did it stay hidden?

Answer: **Nothing checked the outcome: the job had never been scheduled, and silence produced no error**

1. In the 2026 silent-failures study, a fully tested job never ran because one manual deployment step was missed, and the check for it was itself broken.

2. Across that study, 4,286 tests and 827 automated checks stayed green while failures lasted from 13 hours to 60 days, and about 70% were found by a person reading the output.

3. Its automated audits prevented none of the new incidents in advance, though they blocked 87% from recurring.

4. Fix: check outcomes ('did a report arrive today?'), compare what's declared with what's actually running, schedule time to read real outputs, and break things deliberately to prove each monitor fires.

Why break things on purpose? A monitor that has never fired may not work. In that study, one checker had been silently passing 67 empty checks for months.

Question 8 · Hard · which agent

### A research pipeline with a planner, three researcher agents and a writer produced a report with a wrong conclusion. The logs are one long text file. How do you find which agent caused it, and what should you have recorded?

Answer: **You need a trace with a span per agent and recorded hand-offs, then trace the claim back to its source**

1. A study of seven multi-agent frameworks found failure rates of 41 to 87%, with failures spread across system design, misalignment between agents, and missing verification.

2. Common modes include repeating steps (15.7%), reasoning that didn't match the action taken (13.2%) and not recognising when to stop (12.4%).

3. Even with full traces, models identified the responsible agent only about half to two thirds of the time.

4. Record: a span per agent linked to its parent, each brief and returned summary, sources for every claim, and a verification step before the writer.

What helped those frameworks most? Clearer role specifications and a high-level verification step, which improved one system's success by up to 15.6%.

**More practice and sources**

8 incidents so far · answers hidden until you click · updated 7 Nov 2026

Keep practising

Uses Agent Infrastructure, Tracing and Observability, Evaluating Agents. More incidents are added to this sub-section over time. Other sub-sections: Context and Memory, Tools and MCP, Planning and Reliability, Multi-Agent and Protocols, Evaluation, Safety and Security, Cost and Latency, Human in the Loop, Long-Running and Scheduled Agents.
