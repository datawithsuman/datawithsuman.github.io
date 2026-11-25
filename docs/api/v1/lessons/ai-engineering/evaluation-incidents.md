# Evaluation Incidents: LLM Apps and Agents

> 22 incidents: overfitted prompts, leaky judges, flaky agents, misleading metrics and more.

- Track: AI Engineering › Applied Evals › Scenarios
- Type: Interview · 40 min
- Page: https://aimlrounds.com/tracks/ai-engineering/evaluation-incidents/
- Before this: RAG Evals: Retrieval, Faithfulness and Relevance (`ai-engineering/rag-evals`), Agent Evals: End States, pass^k and Cost (`ai-engineering/evaluating-agents`)
- Quiz topic: `evals`
- Sources checked: not stated · Text last changed: 2026-11-19 · Version: 2362fab3c2

How to use this page

Give yourself about 5 minutes per question, as in an interview. Each is a symptom where evaluation misled a team. Say your diagnosis out loud (most likely cause first, how you'd confirm it, then the fix), then open the answer and compare.

**The diagnosis order:** check the eval set looks like real traffic → check the scorer (judge version, biases, agreement with people) → check noise (repeat runs, sample size) → compare offline results with online outcomes → fix, then add the case to the eval suite.

Question 1 · Easy · eval set

### Your assistant scores 92% on the eval set, but users keep complaining about wrong answers. The eval set was written by the team last quarter. What's the likely problem?

Answer: **the eval set doesn't look like real traffic**

1. Hand-written questions tend to be clean and on-topic; real users are messy, ambiguous and ask about new things.

2. Compare a sample of real queries with the eval set: topics, length, typos, languages, multi-part questions.

3. Fix: build the eval set from sampled, anonymised production queries, add complaint cases, and refresh it regularly.

**Follow-up:** How often should you refresh? Whenever usage shifts noticeably, and on a schedule, say monthly, keeping a stable core for comparisons.

Question 2 · Easy · judge drift

### Nothing in your product changed, but LLM-judge scores jumped 6 points overnight. What happened?

Answer: **the judge itself changed, for example a new judge model version**

1. If the system is unchanged, a score change usually comes from the scorer.

2. Check the judge model version and prompt; re-score an old run with the new judge.

3. Fix: pin the judge model and prompt version, record them with every run, and recalibrate against human labels when you upgrade the judge.

**Follow-up:** Can you compare runs scored by different judges? Not directly; re-score both with the same judge first.

Question 3 · Medium · verbosity bias

### After a prompt change, answers got 40% longer and the LLM judge's win rate went from 50% to 68%. Users haven't noticed any improvement. What do you suspect?

Answer: **the judge prefers longer answers, so the win rate reflects length, not quality**

1. LLM judges often favour longer, more detailed-looking answers.

2. Compare win rate against answer length, and have people rate a sample blind.

3. Fix: use a rubric that rewards correctness and concision, control for length, and validate the judge against human ratings before trusting it.

**Follow-up:** What else can bias a judge? Answer position in pairwise comparisons, and preferring answers written by its own model family.

Question 4 · Medium · position bias

### In pairwise comparisons, the answer shown first wins 70% of the time, whichever system wrote it. What do you do?

Answer: **the judge has position bias; swap the order and average**

1. Pairwise judges often favour one position regardless of content.

2. Confirm by comparing a system against itself: a fair judge gives about 50%.

3. Fix: judge every pair in both orders, count a win only if it holds both ways (or average), and report ties.

**Follow-up:** Does this double the cost? Yes, roughly, but a biased comparison is worth less than nothing.

Question 5 · Medium · contamination

### A new open model scores 15 points above others on a well-known public benchmark, but performs normally on your own tasks. Why?

Answer: **the benchmark questions were likely in its training data**

1. Public benchmarks leak onto the web and into training sets, inflating scores.

2. Check for verbatim or near-verbatim overlap where possible, and test on fresh or private questions.

3. Fix: choose models on your own held-out tasks; treat public benchmarks as a rough filter only.

**Follow-up:** How do you keep your own eval set from leaking? Keep it private, don't paste it into tools that may train on it, and refresh it.

Question 6 · Medium · proxy metric

### A new support prompt raised thumbs-up by 3% in an A/B test, but the share of tickets resolved without a human dropped. Which do you trust?

Answer: **the outcome metric, resolved tickets; thumbs-up is a proxy that can be gamed by tone**

1. Friendlier answers can earn thumbs-up without solving the problem.

2. Check the primary metric agreed before the test, and read a sample of the lost resolutions.

3. Fix: make resolution the primary metric with thumbs-up as secondary, and decide the launch rule before testing.

**Follow-up:** Why agree the primary metric in advance? So you can't pick whichever metric happens to look good afterwards.

Question 7 · Hard · noise

### The same system, evaluated twice on the same 100 questions, scores 78% and then 82%. The team celebrates a 2-point gain from a new prompt. Should they?

Answer: **no; the difference is within run-to-run noise**

1. Sampling randomness, judge randomness and a small eval set make scores vary from run to run.

2. Run each system several times, and compute a confidence interval; with 100 questions at about 80%, the 95% interval is roughly ±8 points.

3. Fix: use more questions, lower temperature for evals, repeat runs, and only call a change real if it beats the noise.

**Follow-up:** How many questions do you need to trust a 2-point change? Hundreds to a few thousand, depending on the pass rate; estimate it before running.

Question 8 · Hard · agents

### Your agent passes 60% of benchmark tasks on a single run, but in production customers say it's unreliable. What did the evaluation miss?

Answer: **consistency: success on every try, not just one**

1. A single run hides how often the agent succeeds on some tries and fails on others.

2. Run each task several times and measure pass^k, the chance it succeeds on all k tries.

3. Fix: report pass^k alongside single-run success, and improve consistency with better tools, checks and smaller steps.

**Follow-up:** Which number should you show leadership? pass^k for the k that matches real use, since customers repeat tasks.

Question 9 · Hard · overfitting

### Over three months, the team tuned prompts until the eval set hit 95%. A fresh set of real questions scores 74%. What happened?

Answer: **the prompts were overfitted to the eval set**

1. Repeatedly tuning against the same questions bakes in their quirks, much like overfitting a model.

2. Compare scores on the tuned set with a held-out set nobody has looked at.

3. Fix: keep a hidden held-out set for final checks, refresh tuning sets from new traffic, and report both numbers.

**Follow-up:** Who should own the held-out set? Someone outside the tuning loop, so it stays truly unseen.

Question 10 · Hard · eval vs production

### The agent passes 92% of sandbox evals but resolves only 64% of real tickets without escalation. Where's the gap?

Answer: **the eval set doesn't match production: phrasing, multi-issue tickets, tool behaviour and policy edge cases differ**

1. Compare distributions: real tickets are messier (several issues, missing order IDs, other languages), and real tools are slower, flakier or return different data than sandbox copies.

2. Sample failed production cases, categorise them, and add them to the eval set; simulate tool failures and latency in the sandbox.

3. Measure pass^k (consistency) rather than single runs, and track online metrics per category.

**Follow-up:** How do you keep the eval set representative? Continuously sample recent production tickets (with consent/redaction) and refresh the set.

Question 11 · Easy · flaky agent

### Your booking agent passed a task in testing, but customers report the same request failing about half the time. Your eval runs each task once. What's wrong with the measurement?

Answer: **One run per task measures luck, not reliability; measure pass^k**

1. Agents are not deterministic: the same task can pass on one run and fail on the next.

2. pass@k asks whether any of k tries succeeds. pass^k asks whether all k succeed, which is what a customer needs.

3. In τ-bench, a strong model succeeded on about 60% of retail tasks in one try, but on fewer than 25% when all 8 tries had to succeed.

4. Fix: run each task several times, report pass^k next to pass@1, and fix the tasks with the most variance first.

Which tasks are flakiest? Usually ones with long tool chains or policy edge cases, where one small wrong turn changes the outcome.

Question 12 · Hard · agent games tests

### Your coding agent's pass rate jumped after a model upgrade. A reviewer then found it had edited a failing test and, in another task, made a value compare equal to anything. How do you measure and stop this?

Answer: **The agent passed the tests instead of doing the task; measure cheating directly and remove the shortcuts**

1. ImpossibleBench (2025) makes tests contradict the task, so any pass is cheating. A top model cheated on 54% of real-repo tasks, by editing tests, special-casing them, overriding comparisons or recording hidden state.

2. Make tests read-only or hidden from the agent, and give it an explicit 'flag for a human' exit: that exit cut one model's cheating from 54% to 9%.

3. Prompts matter too: a strict prompt cut cheating from 92% to 1% on simpler coding tasks.

4. Don't rely on an LLM monitor alone: monitors caught only 42–65% of cheating on real-repo tasks.

How do you keep checking? Add a few impossible tasks to your eval set. Any pass on them is a cheat.

Question 13 · Medium · judge sees only the reply

### An LLM judge reads each request and the agent's final reply. It reports catching most injected faults, but a refund issued without the eligibility check sailed through. Why, and what do you change?

Answer: **The fault never reaches the reply, so the judge can't see it; its 'recall' was its base rate**

1. In a 2026 study, a reply-only judge scored 34–76% recall on faults that left the reply unchanged, yet it flagged their clean versions exactly as often, so it detected nothing. It also flagged 33% of clean runs.

2. The same model, shown every step and told to check each one, caught all those faults with 0 false alarms in 100 clean runs.

3. Fix: give the judge the full trajectory with a step-by-step procedure, and validate it on pairs of clean and faulty runs, measuring the flag-rate difference rather than recall alone.

4. The study also found judges rarely checked invented promises in the reply, so add a separate check of the reply against the evidence.

Does a majority vote of judges help? Not here: three samples cost three times as much and missed the same faults.

Question 14 · Medium · checker rejects success

### Your computer-use agent's score is stuck. An engineer reads 50 failed runs and finds several where the agent actually finished the task. How can a 'fail' be wrong, and what do you do?

Answer: **The checker or the task is broken, not the agent**

1. An audit of 150 failed runs from five computer-use benchmarks found 15.3% of fail verdicts were wrong: 10.7% were valid results the checker rejected, and 4.7% were broken tasks.

2. Examples: exact string matching rejecting a correct answer, a state check missing another valid path, a dead search engine, and a task impossible on the given machine image.

3. Fix: read a sample of failed transcripts regularly, accept every valid solution in the checker, version tasks with their environments, and report the checker's error rate.

4. Release screenshots and tool outputs with each run: without screenshots, judges missed about half of the wrong verdicts.

What do the real failures look like? In that audit, most were repeating actions with no effect and planning errors, not clicking the wrong thing.

Question 15 · Medium · right outcome, wrong process

### Your support agent scores 95% on an eval that checks the final database state. An auditor finds it often refunds without checking eligibility, against policy. Why didn't the eval catch it?

Answer: **The end state is the same whether or not the agent followed the procedure**

1. A refund of the right amount issued without the eligibility check leaves the same database state and the same reply as a correct one.

2. Studies have found state-based checks in τ-bench-style evaluations credit runs that broke the procedure or returned nothing.

3. Fix: add rules on the trajectory, such as 'eligibility before refund' and 'refund no more than the authorised amount', and score them alongside the outcome.

4. Track policy violations as their own metric, so a high success rate can't hide them.

Which checks should be rules, and which judged? Rules for anything precise, such as order and amounts. Use a judge for tone and reasoning.

Question 16 · Medium · small eval set

### To save money, your team compares two agent versions on the first 20% of the eval set and ships the winner. Production results then favour the other version. What went wrong?

Answer: **A small or unrepresentative subset can reverse the decision the full set would make**

1. A 2026 replay of public benchmark records found the share of tasks needed to match the full decision varied from 15% on one benchmark to 90% on SWE-bench Verified.

2. Running the cheapest tasks first used only 11.5% of the cost but missed whole domains, and gave wrong conclusions.

3. Fix: sample across task categories, decide in advance how big a gap counts, report confidence intervals, and leave the result undecided when the gap is within the noise.

4. Compare versions on the same tasks, so the difference isn't just task mix.

How many tasks are enough? It depends on the gap you need to detect. Small gaps need far more tasks, so say 'no conclusion' rather than guess.

Question 17 · Hard · judge drift

### Nothing changed in your agent, but its LLM-judge score dropped sharply this week. The only change was an update to the server that runs the judge model. Can that move the score?

Answer: **Yes: the judge is a measuring instrument, and its runtime is part of it**

1. In one 2026 study, the same judge prompt and model, rerun on a newer serving engine, changed its recall by up to 54 points while its inputs were identical.

2. Judges also make different mistakes on different agent versions, so a fixed judge can favour one version unfairly.

3. Fix: pin the judge model, prompt and runtime; keep a fixed set of labelled runs; and recheck the judge on it after any change, before trusting new scores.

4. Report judge agreement with human labels alongside the agent score.

How do you tell judge drift from agent drift? Rescore old runs with the current judge. If old scores move too, the judge changed.

Question 18 · Medium · calls right, tasks wrong

### Your agent's tool-call accuracy is 95% on single-step tests, yet only 60% of real multi-step tasks succeed. The team wants to improve the tool descriptions. Where would you look first?

Answer: **Per-call accuracy hides sequence errors: check trajectory recall, order rules and how values flow between steps**

1. Single-step tests check each call in isolation. Real tasks fail when a step is skipped, steps run in the wrong order, or a value from one result is copied wrongly into the next call.

2. Measure tool-call recall against reference trajectories, add order rules such as 'eligibility before refund', and compare arguments with the values in earlier tool results.

3. Add progress rate to see where tasks stop, and read failed traces from the first wrong step.

4. An audit of four tool-calling benchmarks recommends scoring tool calls, task completion and outcome separately for this reason.

Could per-call accuracy be misleading even on its own? Yes, if the test cases are easier than real requests: sample them from production.

Question 19 · Medium · asking was marked wrong

### A user asked the agent to 'delete the old reports'. The agent asked which folder first, and the eval marked the case as a failure, because the reference trajectory calls the delete tool straight away. Is the agent wrong?

Answer: **Probably not: the eval can't reward asking, so it penalises careful behaviour**

1. Scripted evaluations often have no user who answers, so a turn spent asking counts as a turn with no call.

2. CAREFUL-Bench found 322 of 734 reference turns in a popular function-calling benchmark act destructively with no confirmation, and no turn rewarded asking for permission.

3. Fix: add a simulated user that answers clarifying questions, include cases where asking is the right answer, and count unrequested destructive calls separately.

4. Decide the policy first: which actions must be confirmed? Then write evaluation cases that check it.

How do you stop the agent asking too much instead? Include easy, unambiguous cases where it should act, and track how often it asks.

Question 20 · Easy · strict match too strict

### After a prompt change, trajectory match scores fell from 90% to 55%, but the final-state checks show the same task success as before. The new agent looks up the customer before the order instead of after. What's going on?

Answer: **Strict matching penalises a different but valid path**

1. Strict mode requires the same calls in the same order, so harmless reordering counts as failure.

2. Anthropic notes that checking exact tool sequences is often too rigid, because agents find valid paths the test writer didn't expect.

3. Fix: use unordered or superset matching where order doesn't matter, keep explicit rules only for orders that do, and treat the final-state check as the main signal.

When is strict right? For fixed, audited workflows, such as payroll runs, where any deviation needs review.

Question 21 · Hard · RAG quality

### Your RAG assistant scores 92% answer correctness on the golden set, but faithfulness is only 70%. Product says '92% is great, ship it.' What do you say?

Answer: **don't ship yet: 30% of claims aren't supported by retrieved context, so correctness comes partly from the model's memory**

1. Low faithfulness with high correctness means the model often answers from pre-training knowledge, not your documents; it will be confidently wrong when policies change or for company-specific facts.

2. Check context recall: if needed facts often aren't retrieved, fix retrieval (chunking, hybrid search, re-ranking); if they are retrieved but ignored, tighten the prompt (answer only from context, cite clauses, say 'not found').

3. Re-measure both metrics, and add policy-change test cases where memory and documents disagree.

**Follow-up:** What test would expose the risk directly? Change a policy value in a test index (e.g. cap ₹150 → ₹100) and check whether answers follow the documents.

Question 22 · Hard · routing

### After adding a router that sends 70% of requests to a small model, costs fell 60% and average judge scores barely changed, but escalations to human agents rose 25%. What's going on, and what would you do?

Answer: **the average hides failures on a hard minority of requests that the router misclassifies**

1. Judge averages are dominated by easy questions; misrouted hard cases (disputes, multi-issue complaints) fail and get escalated, which costs agent time.

2. Analyse escalated conversations by route and intent; evaluate the router's precision on hard cases, not just overall quality.

3. Fix: raise the threshold or add rules for hard intents, use a cascade (escalate to the big model when the small model's answer fails a check), and optimise cost per resolved conversation including agent cost.

**Follow-up:** Which metric should the team have optimised? Total cost per resolved conversation (LLM + human), with quality measured on stratified slices, not just the overall average.

**More practice and sources**

22 incidents, easy to hard · answers hidden until you click · updated 15 Nov 2026

Keep practising

Uses these lessons: RAG Evals, Agent Evals, Tool-Call Evals, LLM Judges, Can You Trust Your Judge? and Evals in CI.
