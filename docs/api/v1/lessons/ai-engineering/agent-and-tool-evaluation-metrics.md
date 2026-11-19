# Tool-Call Evals: Selection, Arguments, Trajectories and Effects

> Which metrics tell you where an agent's tool use went wrong?

- Track: AI Engineering › Applied Evals › Lessons
- Type: Concept · 22 min
- Page: https://aimlrounds.com/tracks/ai-engineering/agent-and-tool-evaluation-metrics/
- Before this: Agent Evals: End States, pass^k and Cost (`ai-engineering/evaluating-agents`), Tool and Function Calling (`ai-engineering/tool-calling`)
- Quiz topic: `evals`

## Intuition

### The situation

Your support agent has six tools. Its dashboard shows one number, task success, and it dropped from 78% to 70% after a change. Nobody can tell whether the cause is a wrong tool, a bad argument, a skipped step or extra calls. The interviewer asks:

> You own a support agent with six tools. Which metrics would you track for each tool call, each trajectory, each task and in production, and what does each one miss?

#### Why it matters

Evaluating Agents explains why agents are judged on outcomes, repeated runs and cost. In practice you also need to know _where_ a failure comes from: a wrong tool, a bad argument, an extra destructive call, or a task the agent gave up on. One score hides all of that. Interviewers ask "which metrics would you track for this agent?", and a good answer names metrics at each level, how to compute them from traces, and what each one misses. The running example is a support agent with six tools: look up order, check eligibility, issue refund, send email, search help centre, escalate.

### The idea

Think of a driving test. The examiner checks each manoeuvre, the route you took, whether you reached the destination, and later whether you have accidents on real roads. One pass or fail can't tell you which part needs practice.

[Figure: Four levels. Each call. Each trajectory. Each task. Production.]

_One score hides where it failed._

### Play

**Try to break it.** Switch between exact and normalised arguments, then try each match mode.

#### One run, many verdicts

**Expected:** lookup_order(A123) → check_eligibility(A123) → issue_refund(A123, 40)
**Agent:** search_help("refund policy") → lookup_order(A123) → lookup_order(A123) → issue_refund(a123, 40) → check_eligibility(A123)

A made-up trace. Matching follows LangChain agentevals' modes; precision and recall match each expected call at most once.

With **exact arguments**, superset matching fails and recall is 67%: the refund used "a123" instead of "A123". **Normalised**, the same run passes superset with 100% recall, but precision is only 60% because of the help search and the repeated lookup. Strict, unordered and subset fail in every mode. Meanwhile the **final state passes**: the refund was recorded. Only the **order rule** catches the real problem, a refund issued before checking eligibility. One run gets five different verdicts, so pick metrics that match what you care about.

**Now say why:** why does the same run pass superset matching but fail the order rule?

## How it works

### How it works

#### In one breath

Measure agents at **four levels**. **Each tool call:** right tool, right arguments, valid format, and not calling when no tool fits. **Each trajectory:** compare the calls with a reference using a match mode such as strict, unordered, subset or superset, and count tool-call precision and recall, extra or destructive calls and recovery after errors. **Each task:** check the final state, repeat runs for pass^k, and give partial credit with a progress rate. **In production:** resolution without escalation, cost per resolved task and user feedback. Prefer code checks, use LLM judges only where code can't decide, and check your evaluator: an audit of four tool-calling benchmarks found 18.5% of verdicts disagreed with human experts.

#### Metrics at four levels

##### 1 · Each tool call

| Metric | How to compute it | What it misses |
|---|---|---|
| **Tool selection accuracy** | Share of calls using the expected tool, on single-step test cases. | Whether the whole task worked. |
| **Argument accuracy** | Required arguments present, no invented ones, values correct after normalising. BFCL ignores case and spaces in strings and the order of dictionary keys, but keeps list order. | Arguments that are valid but not what the user meant. |
| **Invalid call rate** | Calls that fail to parse or break the schema. AgentBoard reports the share of valid actions as "grounding accuracy". | Valid calls that do the wrong thing. |
| **Tool error rate** | Calls that return an error, split by cause: agent mistake or tool outage. | Silent wrong results. |
| **Knowing when not to call** | On cases where no tool fits, the agent makes no call (BFCL "relevance detection"); on cases missing a required value, it asks. | Over-asking on easy cases, so test both sides. |

##### 2 · Each trajectory

- **Match modes against a reference:** _strict_ (same calls, same order), _unordered_ (same calls, any order), _subset_ (no tools beyond the expected ones) and _superset_ (all expected calls made, extras allowed). These are the modes in LangChain's agentevals; arguments can be compared exactly, ignored, or with a custom check per tool. Google ADK's tool trajectory score defaults to an exact match.

- **Tool-call precision and recall:** precision is the share of the agent's calls that match an expected call; recall is the share of expected calls the agent made. Low precision means wasted or risky extra calls; low recall means missing steps.

- **Effect-aware counts:** unrequested destructive calls, duplicate writes and redundant reads. CAREFUL-Bench (2026) re-scored a function-calling leaderboard this way: the leader lost 14.5 points, and unneeded steps took 2–28% of input tokens, none of which the official score counted.

- **Order rules:** some steps must come first, such as checking eligibility before refunding. Test those as rules rather than matching the whole sequence.

- **Recovery:** after a tool error, did the agent fix the call? Record first-attempt success and success after repair separately.

**Caution:** Anthropic warns that checking exact tool sequences is often too rigid, because agents find valid paths the test writer didn't expect. Grade the outcome first, and use trajectory checks for things that must or must not happen.

##### 3 · Each task

- **Final-state success:** was the refund recorded, the ticket closed, the test passing? Check the environment, not the agent's message.

- **pass@k and pass^k:** at 75% success per run, all three of three runs succeed only about 42% of the time.

- **Progress rate:** the share of subgoals reached, for partial credit. In AgentBoard, two models with similar success (2.1% and 3.9%) differed clearly in progress (18.9% and 24.6%).

- **Policy-violation rate:** tracked separately, so a high success rate can't hide them.

- **Efficiency:** steps, tokens, cost and time per task, and cost per successful task.

- **Quality:** tone and explanation, scored by a rubric-based LLM judge that has been checked against human labels.

##### 4 · In production

- **Resolution without escalation** and **escalation rate**, by task category.

- **Cost per resolved task** and **p95 latency**.

- **User feedback** and **sampled human review** of real traces.

- **Two suites:** a capability suite that starts at a low pass rate and shows progress, and a regression suite that should pass nearly 100% on every change. Anthropic suggests starting with 20–50 tasks drawn from real failures.

##### Check the evaluator too

An audit of BFCL v4, τ²-Bench, LiveMCPBench and MCP-Atlas found 92 of 496 verdicts (18.5%) disagreed with human experts, from brittle state matching, wrong reference answers and substring checks to LLM judges that changed their rubric. One LLM-judged benchmark ranged from 57.9% to 76.8% across 23 reruns of the same setup. A deterministic-first design, with an LLM judge only for qualitative criteria, agreed with experts 95.5% of the time. The lesson: score tool calls, task completion and outcome separately, and read failed transcripts.

#### The maths

$$ \text{precision} = \frac{m}{|\text{agent calls}|} \qquad \text{recall} = \frac{m}{|\text{expected calls}|} $$

Whether a call matches depends on how you compare arguments: exactly, after normalising, or not at all.

- **matched calls**: Agent calls that match an expected call, each expected call used once.

- **all calls the agent made**: Extra, repeated or wrong calls make this bigger and lower precision.

- **calls in the reference**: Missing steps lower recall.

- **precision**: Low precision means wasted or risky extra calls.

- **recall**: Low recall means the agent skipped expected steps.

## In practice

### In practice

#### Four stages of a tool call, and where failures start

Each tool call has its own flow, and checking only the final output can't tell you which step broke. Evaluate four stages separately:

| Stage | Question | Typical check |
|---|---|---|
| 1 · Selection | Right tool, or rightly no tool? | expected tool on single-step cases; cases where no tool should be called |
| 2 · Arguments | Valid and correct? | schema validation with code, then values against the user's request |
| 3 · Execution | Did the call work? | errors split into agent mistakes and tool outages |
| 4 · Output handling | Was the result used correctly? | facts in the answer match the tool's output; errors not ignored |

Before evaluating, define the agent's level of autonomy: an assistant designed to confirm before sending email fails if it sends without asking, and one designed to act fails if it keeps asking.

##### The transition failure heatmap

For many traces, record the last state that succeeded and the state where the first failure happened, and count each pair. In the book's real estate example, the hotspot was 12 traces failing at execution right after argument generation: arguments that passed the schema but referred to things that didn't exist. Column totals showed execution failing most (12), then argument generation (8, arriving from two different states) and output handling (7). Fix the hottest cell, regenerate the heatmap, and watch the hotspot move.

Evaluating MCP servers specifically, with distractor tools and descriptions as prompts, is covered in Evaluating an MCP Server.

#### In practice

- **Start from failures:** 20–50 real failed cases with expected end states, then grow the set.

- **Outcome first:** check the final state with code; add trajectory rules only for steps that must or must not happen.

- **Choose match modes on purpose:** superset when extra reads are fine, subset when extra tools are risky, strict only for fixed workflows.

- **Normalise arguments:** compare what matters, such as case-insensitive IDs and numbers as numbers, with custom checks per tool.

- **Test both sides:** cases where the agent should call a tool, and cases where it should not, or should ask.

- **Count effects:** destructive calls nobody asked for, duplicate writes and wasted steps, next to success.

- **Repeat runs:** report pass^k and progress rate, not one lucky run.

- **Watch production:** resolution, escalation, cost per resolved task, and a weekly read of sampled traces.

- **Audit the grader:** compare a sample of verdicts with human judgement before trusting a score.

### The answer that sounds right

#### "Just track tool-call accuracy"

It sounds precise, but every call can look right while the task fails: a step skipped, steps out of order, or a value carried wrongly. Add trajectory recall, order rules and final-state checks, and repeat runs.

## Say it

### You own a support agent with six tools. Which metrics would you track for each tool call, each trajectory, each task and in production, and what does each one miss?

#### The interviewer pushes further

Follow-up 1 of 4

Tool-call accuracy is high but task success is low. Why?

Each call can look right while the sequence is wrong: a missing step, steps in the wrong order, or a wrong value carried from an earlier result. Look at trajectory recall, order rules and final-state checks, not per-call accuracy alone.

Follow-up 2 of 4

When would you use superset instead of strict matching?

When extra read-only calls are harmless and agents may take different valid paths. Use strict only for fixed workflows, and subset when extra tools are risky.

Follow-up 3 of 4

Why measure progress rate as well as success?

On hard tasks most runs fail, so success can't tell versions apart. Progress rate gives partial credit for subgoals reached, which shows improvement earlier.

Follow-up 4 of 4

How do you know your evaluator is right?

Compare a sample of its verdicts with human judgement, read failed transcripts, rerun LLM-judged scores to see their spread, and fix checks that reject valid answers.

I'd measure the agent at four levels. For tool calls: selection accuracy, argument accuracy after normalising, invalid-call rate, and whether it avoids calling or asks when it should. For trajectories: tool-call precision and recall against a reference, with a match mode chosen on purpose, plus counts of extra destructive calls, duplicate writes and recovery after errors. For tasks: final-state success, pass^k over repeated runs, progress rate for partial credit, policy violations and cost per successful task. In production: resolution without escalation, cost per resolved task and sampled trace review. Code checks first, a calibrated LLM judge only where needed, and I'd audit the grader against human labels.

**Key terms and sources**

An applied guide to agent metrics at four levels: tool calls (selection, arguments, invalid calls, knowing when not to call), trajectories (match modes, tool-call precision and recall, extra and destructive calls, recovery), tasks (final state, pass^k, progress rate, policy violations, cost) and production (resolution, escalation, cost per resolved task), plus how to check the evaluator itself.

#### Sources

- Anthropic, Demystifying evals for AI agents, Jan 2026

- LangChain, agentevals: trajectory evaluators

- Google ADK, evaluation criteria

- Berkeley Function Calling Leaderboard blog: AST and executable evaluation

- Ma et al., AgentBoard: an analytical evaluation board of multi-turn LLM agents, NeurIPS 2024

- Kovalenko and Redchych, CAREFUL-Bench: effect-aware evaluation of multi-turn function calling

- Vaghasiya et al., Benchmarking the benchmarks: a validity audit of tool-calling evaluation

- Yao et al., τ-bench, ICLR 2025

Explanations are ours, built from these sources. Lab numbers are illustrative unless a lab says otherwise. Many recent papers are preprints, and provider policies change.
