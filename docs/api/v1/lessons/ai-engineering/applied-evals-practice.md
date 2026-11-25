# Applied Evals Practice

> 16 questions: gulfs, placement, datasets, error analysis, judges, kappa, pass^k, trajectories, faithfulness, coding agents, MCP, security.

- Track: AI Engineering › Applied Evals › Scenarios
- Type: Interview · 25 min
- Page: https://aimlrounds.com/tracks/ai-engineering/applied-evals-practice/
- Before this: Can You Trust Your Judge? TPR, TNR and Corrected Pass Rates (`ai-engineering/validating-an-llm-judge`)
- Quiz topic: `evals`
- Sources checked: not stated · Text last changed: 2026-11-19 · Version: f5a2a5fd17

How to use this page

Say your answer out loud first, in about a minute, then open the answer and compare.

Question 1 · Easy · lifecycle

### Your new summariser sometimes uses bullets and sometimes paragraphs. Should you build an LLM judge for format?

Answer: **No: fix the prompt first**

1. It's a specification failure: the prompt never said which format.

2. Add one line, such as bullets, at most five.

3. Build evals only for failures that remain once the prompt is clear.

Lesson: Why LLM Apps Fail.

Question 2 · Easy · placement

### Where should a check for leaked card numbers run, and why?

Answer: **Inline, as a guardrail**

1. A regex runs in milliseconds and rarely misfires, so it can check every answer.

2. On a match, log it and return a safe fallback.

3. Each trip is also a monitoring signal.

Lesson: Choosing the Right Eval.

Question 3 · Medium · datasets

### You asked an LLM for 200 test queries and the app passes 96%. What's wrong with the test set?

Answer: **It probably covers only easy, similar requests**

1. Direct prompts produce many phrasings of the same clear request.

2. Define dimensions such as feature, user type and scenario.

3. Generate tuples, then queries, and check coverage.

Lesson: Building Your First Eval Set.

Question 4 · Medium · error analysis

### Why note only the first failure in each trace during open coding?

Answer: **Later problems are usually caused by the first**

1. One upstream mistake cascades into downstream symptoms.

2. Labelling every symptom inflates counts and hides the root cause.

3. Fixing the first often fixes the chain.

Lesson: Error Analysis.

Question 5 · Medium · judges

### Your judge's TPR is 95% and TNR 60%. It reports an 85% pass rate. Is the true rate higher or lower?

Answer: **Lower, about 82%**

1. Low TNR means the judge passes real failures.

2. Corrected: (0.85 + 0.60 − 1) / (0.95 + 0.60 − 1) ≈ 0.82.

3. Improve the judge's TNR before trusting the dashboard.

Lesson: Can You Trust Your Judge?

Question 6 · Medium · labelling

### Two annotators agree on 88% of labels. Why might Cohen's kappa still be low?

Answer: **Most answers pass, so chance agreement is high**

1. Kappa subtracts agreement expected by chance.

2. If both pass about 90% of answers, chance agreement is about 82%.

3. Check whether they agree on the failures.

Lesson: Labelling with a Team.

Question 7 · Hard · agents

### An agent succeeds 75% of the time per try. What share of tasks does it get right on all 3 of 3 tries?

Answer: **About 42%**

1. pass^k for independent tries is p to the power k: 0.75³ ≈ 0.42.

2. pass@3, at least once, would be about 98%.

3. Users who get one try care about consistency.

Lesson: Agent Evals.

Question 8 · Hard · coding agents

### Your coding agent's pass rate jumped 27 points after an upgrade. What do you check before celebrating?

Answer: **Whether patches edited the tests**

1. Agents can pass by changing what tests check.

2. Count diffs touching tests and fixtures; make tests read-only.

3. Give the agent a way to abort and flag impossible tasks.

Lesson: Coding Agent Evals.

Question 9 · Hard · MCP

### Schema compliance on your MCP server is 99%, yet users say agents ignore your tools. What do you test?

Answer: **Tool selection among distractors**

1. Valid calls to the wrong tool still fail.

2. Write tasks that don't name the tools, with other servers connected.

3. Include tasks that shouldn't call your tools.

Lesson: Evaluating an MCP Server.

Question 10 · Hard · security

### A defence cuts prompt-injection success from 58% to 8%. Why might you still reject it?

Answer: **It may cut normal task success too much**

1. In AgentDojo, an injection detector cut attack success to about 8%.

2. But normal tasks solved fell from 69% to 41%.

3. Always report utility alongside attack success.

Lesson: Safety and Red-Team Evals.

Question 11 · Medium · evaluation

### Your agent scores 70% pass@1 on 200 cases. Leadership asks, 'So 70% of customers get a correct resolution?' What do you say and measure?

Answer: **not necessarily: measure consistency (pass^k), end-state correctness, and cost; run each case several times**

1. A single run hides flakiness: some cases are solved only sometimes. Run each case k times (e.g. 5) and report pass^5 alongside pass@1.

2. Make sure 'success' means the right end state (refund recorded correctly), not a plausible message.

3. Report cost and latency per resolved case, and break down failures by type (tool errors, policy mistakes, escalations).

**Follow-up:** Why might production be worse than the eval? Distribution shift (new issues, phrasing), injected content, tool outages; monitor online resolution and escalation rates.

Question 12 · Easy · tool-call precision and recall

### The reference for a task is three calls: lookup_order, check_eligibility, issue_refund. The agent made five: search_help, lookup_order, lookup_order, check_eligibility, issue_refund, all with correct arguments. What are tool-call precision and recall, and what does each tell you?

Answer: **Precision 3/5 = 60%, recall 3/3 = 100%**

1. Each expected call is matched at most once, so the second lookup_order and search_help are unmatched.

2. Recall is 100%: every expected step happened. Precision is 60%: two of five calls were not needed.

3. Low precision costs tokens and time, and is dangerous if the extra calls write or delete. Check whether they were reads or writes.

Would you fail this run? Not if extra reads are allowed: use superset matching, plus a separate count of extra writes.

Question 13 · Medium · choosing a match mode

### You're evaluating three agents: a payroll agent that must run a fixed five-step workflow, a research agent that may search as often as it likes, and an email agent that must never use any tool beyond lookup and draft. Which trajectory match mode suits each?

Answer: **Strict for payroll, superset for research, subset for email**

1. Strict: same calls in the same order, right for fixed, audited workflows.

2. Superset: all required calls happen and extras are allowed, right when exploration is fine.

3. Subset: no tools beyond the expected ones, right when extra tools are risky.

4. For all three, still check the final state; trajectory checks add rules, they don't replace outcomes.

What about argument comparison? Normalise what doesn't matter, such as case in IDs, and use custom checks for fields like dates or amounts.

Question 14 · Medium · pass^k

### Your agent passes 80% of single runs on a booking task. Customers retry rarely, so a task needs to work on every attempt. What is pass^3, and what does it mean for your launch target?

Answer: **0.8³ ≈ 51%: only about half of tasks succeed on all three runs**

1. pass^k is the chance that all k runs succeed, assuming runs are independent: 0.8 × 0.8 × 0.8 = 0.512.

2. pass@3, the chance at least one run succeeds, is 1 − 0.2³ = 99.2%, which looks far better and hides the problem.

3. Report pass^k next to pass@1, and work on the tasks with the most variation between runs.

Why might real pass^k be higher than the formula? Runs on the same task are correlated: easy tasks pass every time and hard ones fail every time.

Question 15 · Easy · faithfulness

### An answer makes 4 claims. Three appear in the retrieved context. The fourth is true, but isn't in the context. What's its faithfulness, and is the answer OK?

Answer: **0.75. It's right today, but it isn't grounded**

1. Faithfulness = 3 ÷ 4 = 0.75.

2. The fourth claim came from the model's memory.

3. It'll stay wrong after the fact changes, because no document supports it.

That's why you score correctness and faithfulness separately.

Question 16 · Medium · diagnosis

### Recall@50 is 95%, recall@5 is 55%, and faithfulness is high, but users say answers miss things. Where do you look?

Answer: **Ranking: add or improve a re-ranker, then check how much context reaches the model**

1. High recall@50 means retrieval finds it.

2. Low recall@5 means it's ranked too low to be used.

3. Models favour early context, so put the best chunks first.

Would a better embedding model help? It might, but a re-ranker is the direct fix here. Test both.

**More practice and sources**

16 interview questions, easy to hard · answers hidden until you click · updated 15 Nov 2026

### Keep practising

Each answer names the lesson it comes from. For real incidents, try Evaluation Incidents.
