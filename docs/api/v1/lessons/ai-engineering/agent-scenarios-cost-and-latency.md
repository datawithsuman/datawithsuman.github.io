# Agent Scenarios: Cost and Latency

> Hidden reasoning tokens, cache misses on long histories, too many sub-agents and agents that run too often.

- Track: AI Engineering › Agentic AI › Scenarios
- Type: Interview · 48 min
- Page: https://aimlrounds.com/tracks/ai-engineering/agent-scenarios-cost-and-latency/
- Before this: Agent Infrastructure: Durable Execution, Retries and Budgets (`ai-engineering/agent-infrastructure`)
- Quiz topic: `agents`
- Sources checked: not stated · Text last changed: 2026-11-19 · Version: 0d8b6412aa

How to use this page

Give yourself about 5 minutes per incident, as in an interview. Say the most likely cause first, how you'd confirm it from traces, and the fix; then open the answer and compare.

**The agent debugging order:** pull the trace for the failing runs → find the first wrong step (bad tool choice, bad argument, bad observation, bad decision) → check tools, prompt and context at that step → fix the cause, add the case to the agent eval set, and add a guard (budget, validation, approval) so the same failure can't do damage.

Question 1 · Easy · cache broken

### To help the agent with dates, someone put the current date and time at the top of the system prompt. The next day, input costs per task had multiplied, and the first response got slower. Why?

Answer: **Prompt caching only reuses an unchanged prefix, and the timestamp changed the very first tokens**

1. Agents resend their system prompt, tools and history on every step, so cached reads matter a lot. Anthropic bills cache reads at about 0.1 times the normal input price, and writes at about 1.25 times for its 5-minute cache.

2. A value that changes on every request at the start of the prompt means nothing after it can be reused.

3. Fix: keep stable content first (instructions, tools, examples), add to the history only at the end, and put changing values such as dates after the cached part.

4. Watch the cache hit rate, and alert when it drops after a prompt change.

Does caching change the answers? No. It reuses the computed prefix, so outputs are the same; only cost and time to the first token change.

Question 2 · Easy · sequential tool calls

### A support agent looks up the order, the payment and the delivery status one after another before answering, so each reply takes a long time. The three lookups don't depend on each other. How do you speed it up?

Answer: **Run independent tool calls in parallel, and show progress while the work runs**

1. Models can request several independent tool calls in one turn, and your code can run them at once, so the wait is the slowest call rather than the sum.

2. Stream progress to the user, and move long work to the background with a notification when it's done.

3. Shorter outputs and smaller models for simple steps also cut time, since generating tokens is the slow part.

How much speed do users need? It depends on the task. In a study of 86 deployed agents, 66% allowed response times of minutes or longer, so clear progress often matters more than shaving seconds.

Question 3 · Medium · cost explosion

### Agent costs tripled overnight, though ticket volume is flat. The model and prompt didn't change. What do you check?

Answer: **steps per task and tokens per step: a tool started returning huge outputs, or loops/retries increased**

1. Plot steps per run and input tokens per step from traces; find when it changed.

2. Common causes: a tool now returns full raw records (e.g. entire order history), blowing up context every subsequent step; a dependency failing causing retries; lost prompt caching from a changed prefix.

3. Fix the tool output (return only needed fields), add per-task token/cost budgets and alerts.

**Follow-up:** Why does one big tool result cost so much? It stays in context and is re-read on every following step.

Question 4 · Medium · cost per task

### Cost per model call looks stable on the dashboard, yet the monthly bill keeps rising. Tasks have got longer since the agent gained new tools. What's going on?

Answer: **Each step resends the whole history, so cost per task grows faster than the number of steps**

1. With a 5,000-token prompt and 2,000 tokens added per step, a 20-step task reads about 480,000 input tokens. A 40-step task reads about 1.76 million, about 3.7 times as much for twice the steps (illustrative).

2. Per-call metrics hide this, because each call only gets a little longer.

3. Fix: track tokens, cost and time per task; trim tool outputs; summarise older history; and cache the stable prefix.

4. Also check whether the extra steps help: fewer, better steps are cheaper in every way.

Which metric should finance see? Cost per completed task, or per resolved conversation, alongside success rate.

Question 5 · Medium · cache expiry

### Your agent waits on slow tools, a few minutes each, between model calls. Even with prompt caching set up, almost every step pays full price for its input. Why isn't the cache helping?

Answer: **The cache expires during the waits, so each step has to write it again**

1. Anthropic's default cache lasts 5 minutes. Tool calls that take longer let it expire between steps.

2. Options: a 1-hour cache, which costs about 2 times the input price to write but makes later reads cheap; keeping tool waits short; or running slow tools in the background while the agent does other work.

3. If you self-host, send each conversation back to the replica holding its cache, so its history doesn't have to be processed again.

When is the 1-hour cache worth it? When the same long prefix is reused several times over more than 5 minutes, as in agents with slow tools.

Question 6 · Medium · reasoning everywhere

### Every step of your agent, including simple lookups and formatting, runs with the highest reasoning effort. Answers are no better than at medium, but costs and latency have jumped. What do you change?

Answer: **Set reasoning effort per step, using the lowest level that holds up in evaluations**

1. Reasoning tokens are hidden but billed as output, and they're generated before the answer, so they add both cost and time.

2. Use low or no reasoning for routine steps such as lookups, extraction and formatting, and higher effort for planning or hard decisions.

3. OpenAI advises using its highest effort only when evaluations show a clear benefit worth the extra latency and cost.

4. When experimenting, leave room in the output limit: OpenAI suggests reserving about 25,000 tokens for reasoning and output.

How do you choose per step? Run the evaluation set at each effort level for each step type, and pick the cheapest that keeps quality.

Question 7 · Medium · multi-agent overkill

### Your research assistant sends every question, even 'what's our refund policy?', to a lead agent with five sub-agents. Answers are fine, but costs are many times higher than the old single agent. What's the fix?

Answer: **Scale the effort to the question: one agent for simple ones, sub-agents only for broad research**

1. Anthropic reported its multi-agent research system used about 15 times the tokens of a chat, against about 4 times for a single agent.

2. That cost pays off for broad, parallel questions, not for simple lookups.

3. Fix: classify the question first, cap the number of sub-agents and tool calls by question type, and compare quality and cost against a single-agent baseline.

What does the extra spend buy? Speed and breadth on wide questions, and clean contexts for each sub-task.

Question 8 · Hard · no budget

### One coding-agent task ran for two hours and used tens of millions of tokens before failing. Other runs of similar tasks finished in minutes. What should have stopped it, and how do you decide what a task is worth?

Answer: **Per-task budgets on tokens, time and cost, with alerts on outliers**

1. On Terminal-Bench 2.0, some agents took up to two hours and almost 100 million tokens on a single task, and more tokens or turns didn't predict success.

2. Without a budget, a stuck agent keeps going: retrying, re-reading and exploring.

3. Fix: set step, token, time and cost limits per task type, stop and escalate when they're hit, and alert on runs far above the usual cost.

4. Spend more deliberately where it pays: Anthropic's full harness cost about $200 against $9 for a single agent, and built a much better app.

How do you set the budget? Look at the cost distribution of successful runs, and set the limit a little above, say, the 95th percentile.

**More practice and sources**

8 incidents so far · answers hidden until you click · updated 7 Nov 2026

Keep practising

Uses Agent Infrastructure, Multi-Agent Systems, Serving Agents and Reasoning Models, Prompting Reasoning Models. More incidents are added to this sub-section over time. Other sub-sections: Context and Memory, Tools and MCP, Planning and Reliability, Multi-Agent and Protocols, Observability and Debugging, Evaluation, Safety and Security, Human in the Loop, Long-Running and Scheduled Agents.
