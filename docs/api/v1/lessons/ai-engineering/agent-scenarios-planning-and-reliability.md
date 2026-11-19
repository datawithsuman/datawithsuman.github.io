# Agent Scenarios: Planning and Reliability

> Loops, early 'done' claims, bad plans, retry storms, crashes and repeated side effects.

- Track: AI Engineering › Agentic AI › Scenarios
- Type: Interview · 48 min
- Page: https://aimlrounds.com/tracks/ai-engineering/agent-scenarios-planning-and-reliability/
- Before this: Planning and Reflection (`ai-engineering/planning-and-reflection`), Agent Infrastructure: Durable Execution, Retries and Budgets (`ai-engineering/agent-infrastructure`)
- Quiz topic: `agents`

How to use this page

Give yourself about 5 minutes per incident, as in an interview. Say the most likely cause first, how you'd confirm it from traces, and the fix; then open the answer and compare.

**The agent debugging order:** pull the trace for the failing runs → find the first wrong step (bad tool choice, bad argument, bad observation, bad decision) → check tools, prompt and context at that step → fix the cause, add the case to the agent eval set, and add a guard (budget, validation, approval) so the same failure can't do damage.

Question 1 · Easy · infinite loop

### Some refund-agent runs never finish: traces show it calling get_order with the same arguments 40 times until the timeout. What's going on, and what do you add?

Answer: **the agent isn't getting usable feedback from the tool (or doesn't recognise the result), so it repeats; add loop detection, budgets and better tool responses**

1. Check the tool result: an empty or ambiguous response (e.g. 'null', a generic error) gives the model nothing new, so it tries again.

2. Return actionable results/errors ('order not found for this customer; ask for the order number').

3. Add a step budget, detect repeated identical calls, and escalate to a human when stuck.

**Follow-up:** How would you catch this before production? Agent evals with tool failure injection (empty, error, timeout responses).

Question 2 · Easy · compounding steps

### Your 20-step agent passed every demo, but in production it finishes only about a third of tasks. Each step on its own looks right about 95% of the time. Why so low, and what do you change?

Answer: **Small per-step error rates multiply across a long chain**

1. If each step succeeds 95% of the time independently, 20 steps succeed together 0.95^20 ≈ 36% of the time.

2. Demos use short, clean paths, so they hide this. METR's measurements show the same pattern: agents succeed far less often as tasks get longer.

3. Fix: cut the number of model-driven steps, run the fixed parts as plain code, and check each step's result so errors are caught before they spread.

4. Measure end-to-end task success, not per-step accuracy.

What does raising each step to 99% give? 0.99^20 ≈ 82%, which is why small per-step gains matter so much for long tasks.

Question 3 · Medium · error cascade

### A research agent misread a date in step 3, and every later step built on it. The final report was confidently wrong, and the agent never noticed. Why don't agents recover, and how do you design for it?

Answer: **An early wrong step becomes trusted context for every later one, and agents rarely go back**

1. In a 2026 study of agent trajectories, agents recovered after their first mistake in only 30.5% of runs, and a wrong step made the next one wrong 40–58% of the time.

2. The same study found 46% of failures started with a reasoning or planning error, not a tool failure.

3. Fix: check important intermediate results against the source, mark facts the plan depends on, and re-plan from the last good checkpoint when a check fails.

4. In traces, look for the first wrong step, not the last one.

Why doesn't asking the agent to reflect at the end fix it? By then the wrong fact is everywhere in its context, and it tends to agree with its own earlier work.

Question 4 · Medium · stale plan

### A travel agent plans: find a flight, book a hotel near the airport, then book the flight. The flight sells out between steps 1 and 3, but the agent still books the hotel and then fails. What's missing?

Answer: **The plan never gets checked against new results, so the agent keeps following an outdated plan**

1. Plan-and-execute agents save calls by planning once, but the plan rests on assumptions that can change.

2. Fix: record each step's assumptions, and re-plan when a result breaks one, such as a sold-out flight or a failed tool.

3. Order steps so the hardest-to-undo action comes after the ones most likely to fail, or hold the bookings and confirm together.

4. Keep a cap on re-plans, so a changing world doesn't cause a loop.

When is planning once fine? When steps are cheap, quick and easy to undo. The more side effects, the more checks you need between steps.

Question 5 · Medium · stops too early

### An agent asked to fix all failing tests reports 'done' after fixing two of five. Its final message is confident, and nothing checked it. How do you stop early 'done' claims?

Answer: **The agent decides when it is finished, and nothing outside it checks**

1. The MAST study of multi-agent failures found 12.4% came from not knowing when to stop, and 15.7% from repeating steps.

2. Models tend to judge their own work kindly and stop when the text sounds complete.

3. Fix: define 'done' in code, such as the full test suite passing, and run that check before accepting the claim. If it fails, send the agent back with the failures.

4. Put a step limit on the loop too, so 'not done yet' can't run forever.

Who should check? Something outside the agent: tests, a validator, or a separate evaluator with its own instructions.

Question 6 · Medium · retry storm

### A slow inventory tool started timing out. Within minutes it was flooded and went down completely, taking other services with it. The agent, the agent framework and the HTTP client each retry three times. What happened?

Answer: **Retries at several layers multiply, turning one slow call into a flood**

1. With three layers each making up to 4 attempts, one request can become up to 4 × 4 × 4 = 64 calls (illustrative).

2. Agents add another layer: the model may decide to call the tool again after an error.

3. Fix: retry at one layer only, with exponential backoff and jitter; set a retry budget; add a circuit breaker that stops calls to a failing tool; and tell the model plainly that the tool is down.

4. Return errors the model can act on, such as 'unavailable, try later', so it doesn't keep trying.

How would you spot it? A sudden jump in calls per task to one tool, while successful tasks drop.

Question 7 · Hard · crash repeats side effect

### A worker crashed after the agent charged a customer's card but before it saved its progress. The task restarted from its last checkpoint and charged the card again. How do you make long agent runs survive crashes safely?

Answer: **Durable execution with a checkpoint after each step, plus idempotency keys on every side effect**

1. Crashes are normal in long runs: with 100 steps and a 2% chance of a problem at each, only 0.98^100 ≈ 13.3% of runs finish without one.

2. Restarting from the beginning is costly, and restarting from a checkpoint repeats any step that ran after it.

3. Fix: save state after every step, and give each side effect an idempotency key based on the task and step, so the payment service ignores a repeat.

4. Keep side effects in their own steps, and record their results before moving on.

Which steps need keys? Any that change the outside world: payments, emails, bookings and writes. Reads can usually be repeated safely.

Question 8 · Hard · overeager agent

### A user asked a coding agent to 'tidy up this folder'. It removed the junk files, and also deleted an old credentials backup that was the only copy. The task technically succeeded. How do you prevent this?

Answer: **The agent guessed the scope of the request, and nothing stopped it acting beyond what was asked**

1. The Overeager benchmark (2026, 500 scenarios) found that permissive agent setups took actions nobody asked for in 5.4–27.7% of runs, against 0.2–4.5% for setups that ask before continuing.

2. Removing the line that spelled out what the agent may touch raised one agent's rate from 0% to 17.1%, so agents lean heavily on explicit scope.

3. Fix: state the scope in the task, enforce it in code with allowed paths and actions, and require confirmation for deletes or edits outside it.

4. Score evaluations on what the agent did beyond the task, not only whether the task passed.

Why don't normal benchmarks catch it? They check whether the task was solved, and an overeager run that destroys a file can still pass.

**More practice and sources**

8 incidents so far · answers hidden until you click · updated 7 Nov 2026

Keep practising

Uses Planning and Reflection, Agent Infrastructure, Agent Frameworks and Harnesses, Agent Safety. More incidents are added to this sub-section over time. Other sub-sections: Context and Memory, Tools and MCP, Multi-Agent and Protocols, Observability and Debugging, Evaluation, Safety and Security, Cost and Latency, Human in the Loop, Long-Running and Scheduled Agents.
