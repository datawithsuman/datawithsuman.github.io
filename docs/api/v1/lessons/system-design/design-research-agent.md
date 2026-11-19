# Design a Research Agent

> Users ask open-ended questions that need many sources. Design an agent that splits the work across parallel subagents and writes one answer.

- Track: System Design › Agents › Designs
- Type: Design · 25 min
- Page: https://aimlrounds.com/tracks/system-design/design-research-agent/
- Before this: Multi-Agent Systems (`ai-engineering/multi-agent-systems`), Agent Infrastructure: Durable Execution, Retries and Budgets (`ai-engineering/agent-infrastructure`)
- Quiz topic: `sdllm`

## Intuition

### The situation

An AI assistant gets broad questions, like comparing every company in a sector, that need dozens of searches across many sources. A single agent is slow, and its context fills up. A long run sometimes fails near the end. The interviewer asks:

> Users ask open-ended questions that need many sources. Design an agent that splits the work across parallel subagents and writes one answer.

#### Ask before designing

- **Scope:** web only, or private sources like documents and chat too? Must each claim carry a citation?

- **Scale:** say 10,000 research runs a day, each taking a few minutes.

- **User experience:** people accept waiting minutes for a good report, if they can see progress and aren't left with nothing after a failure.

- **Limits:** a budget per run for tokens, time and number of subagents.

- **Success metrics:** factual accuracy, citation accuracy, completeness, source quality and cost per run.

### The idea

Think of an editor with a team of researchers. The editor writes the plan and gives each researcher one clear topic. They go off separately and bring back short notes, not everything they read. The editor combines the notes, sends people back if something's missing, and a fact-checker adds the references.

[Figure: A lead agent plans. Subagents search in parallel. The lead combines their reports. A final step adds citations. The plan and progress are saved outside the agents, so a failed run can resume.]

_Each subagent reads a lot and returns a little, which is what keeps the lead's context clear._

### Play

**Try to break it.** Set the question to 1 part, and add subagents. Then go to 20 parts. Then tick the stuck subagent.

#### How many subagents should you start?

Illustrative: 1 minute per part, 30 seconds to plan and write, 20,000 tokens per part, 10,000 for the lead and 10,000 per subagent. Real runs use far more tokens than this model, so read the trend and not the percentage.

With **8 parts**, 4 subagents cut the time from 8.5 minutes to 2.5. With **1 part**, extra subagents do nothing. Now tick the stuck subagent: the lead waits for each batch, so one slow worker holds up everyone.

**Now say why:** why does one stuck subagent delay the whole run?

## Architecture

### Architecture

#### In one breath

A **lead agent** plans and saves the plan outside its context. It then starts **subagents in parallel**, each with its own context, clear task and limits. Each subagent searches and returns a short report. The lead combines them, decides whether more research is needed, and a final step attaches citations. It costs many more tokens than a chat, so **use it only when the question is broad and worth it**. Save progress so a failed run can resume.

#### A lead and its workers

1. **Plan:** the lead agent reads the question, works out an approach and saves its plan to external memory. A long run can overflow its context, and the plan must survive that.

2. **Delegate:** it starts subagents, each with an objective, an output format, the tools and sources to use, and clear boundaries.

3. **Search in parallel:** each subagent has its own context. It starts with broad searches, judges what comes back and narrows down. It returns only what matters.

4. **Combine:** the lead reads the reports, and decides whether to start more subagents or finish.

5. **Cite:** a citation step matches each claim to the exact place in a source.

6. **Return:** the user gets one report with citations.

##### Why several agents help here

You can't script a fixed path for open research, because each finding changes what to look for next. Listing the board members of every company in a sector is the clear case: a single agent searching in turn is slow and runs out of room. Subagents compress the work, since each reads a lot and returns a little.

##### Tools and permissions

- Each tool needs one clear purpose and a good description. A web search for something that only exists in the company chat is doomed from the start.

- Tell agents which source types to trust. Left alone, they can prefer SEO pages over primary sources.

- Everything read from the web is untrusted, so research agents should have read-only tools. Private sources use the user's own permissions.

##### Planning and memory

Save the plan, and summarise finished phases to external storage. When a context nears its limit, start a fresh subagent with a clean handover. Subagents can write long outputs to storage and pass back a reference, so details aren't lost by being retold.

##### When to stop

Match the effort to the question: a simple fact needs one agent and a few searches, and a comparison needs a few subagents. Set hard limits too, because early versions started dozens of subagents for simple questions and kept searching for sources that didn't exist. When the budget runs out, return what was found and say what's missing.

#### The numbers worth saying out loud

All of these are assumptions for the interview, not figures from a real system.

| Question | Working | Result |
|---|---|---|
| Runs at once, on average | 10,000 ÷ 86,400 × 150 seconds | **about 17** |
| Runs at once, at peak | 17 × 3 | **about 52** |
| Agents running at peak | 52 × 4 subagents | **about 208** |
| Tokens per day | 10,000 runs × 210,000 tokens | **2.1 billion** |

The request rate looks tiny, but each run is long and heavy. Your limits are model rate limits and search quotas, so runs need a job queue, and each run needs a budget.

## In practice

### In practice

#### What every agent design gets asked

- **Quality and evaluation:** see the next section. Agents take different valid routes, so judge the result and whether the process was reasonable.

- **Reliability:** runs are long and errors compound, so a restart is expensive. Checkpoint regularly and resume from there. Use retries and timeouts in code, and tell the model when a tool is failing so it can try another way.

- **Scalability:** run each research job as a durable background task, separate from the web request. Queue work when you reach rate limits. Agents run for a long time, so shift traffic gradually between old and new versions.

- **Latency and cost:** parallelism gives the speed. Use a stronger model for the lead and a cheaper one for subagents. Run several tools at once inside each subagent as well.

- **Safety and security:** web pages can carry injected instructions, so keep tools read-only and keep private data away from anything that can send it out. Trace decisions so you can debug without reading private conversations.

##### When not to use several agents

- The question is simple, because you pay many times more for no gain.

- The work has many dependencies, or every agent needs the same context.

- The task doesn't split well. Most coding tasks have less truly parallel work than research.

##### Debugging

The same question takes a different path each time, and a small change to the lead can change how subagents behave. So trace every run in full, and step through real prompts to see what agents actually do.

#### Start small, and start now

1. **Begin with about 20 real queries:** early changes have big effects, so a small set shows them. Waiting until you've built hundreds of cases is a mistake.

2. **Use one judge with a clear rubric:** score factual accuracy, citation accuracy, completeness, source quality and tool efficiency, from 0 to 1 with a pass or fail. The real team found one LLM call with one prompt was the most consistent.

3. **Keep human testers:** people find made-up answers on unusual queries, system failures and biased choices of sources.

4. **Let agents help:** a model can read failed runs and suggest prompt fixes. A test agent can use a tool many times, then rewrite its description.

#### What the real system reported

- **Quality:** the multi-agent system beat a single agent by 90.2% on the company's internal research evaluation.

- **Speed:** parallel work cut research time by up to 90% for complex queries, with the lead starting 3 to 5 subagents and each using 3 or more tools at once.

- **Cost:** agents typically use about 4 times the tokens of a chat, and multi-agent systems about 15 times.

- **Why it works:** in one evaluation, token use alone explained 80% of the performance differences, so it helps largely by spending enough tokens on the problem.

- **Tool descriptions:** rewriting them cut task time by 40% for later agents.

- **Still limited:** the lead waits for each batch, can't steer subagents as they run, and they can't coordinate. Running them independently would bring new problems with state and errors.

These are the company's own numbers, and it builds the models used.

### The answer that sounds right

#### "More agents give a better answer"

It sounds right, since many hands make light work. But agents only help when the work really splits. On a simple question you pay many times more for the same answer. If tasks depend on each other, or the instructions are vague, agents repeat each other's work. Multi-agent systems use far more tokens than a chat, so use them only when the question is worth it.

## Say it

### Users ask open-ended questions that need many sources. Design an agent that splits the work across parallel subagents and writes one answer.

#### The interviewer pushes further

Follow-up 1 of 3

A run fails after 10 minutes at 80% complete. What happens?

It resumes from the last checkpoint. The plan and finished subagent reports are saved outside the agents, so only unfinished subagents run again. Because the tools are read-only, repeating a step is safe. If the budget is gone, return what's there and say what's missing.

Follow-up 2 of 3

Two subagents keep researching the same thing. How do you fix it?

That usually means the lead's instructions were too short. Each task needs an objective, an output format, sources to use and clear boundaries. I'd step through a real run to see where the overlap starts, fix the delegation prompt and add that case to the test set.

Follow-up 3 of 3

Would you use this design for a coding agent?

Probably not as the default. Code changes depend on each other, and agents need shared context, while most coding tasks have less parallel work than research. I'd use one agent, and maybe send separate subagents for read-only exploration, where they can return a summary without touching the code.

First I'd clarify sources, citations, volume and the budget per run. I'd use a lead agent and parallel subagents, because research can't follow a fixed path and it splits well. The lead plans and saves the plan outside its context. It starts subagents with a clear task, format, tools and limits. Each has its own context, searches broad then narrow, and returns a short report. The lead combines them and decides whether to continue. A final step attaches citations. Effort should match the question, so a simple fact gets one agent, and hard limits stop runaway runs. Each run is a durable job with checkpoints, so a failure resumes instead of restarting. Tools are read-only and web content is untrusted. For evaluation, I'd start with about 20 real queries and a judge scoring accuracy, citations, completeness and source quality, plus human testers. The main trade-off is cost: this uses far more tokens than chat, so I'd save it for broad questions worth the money, and use one agent otherwise.

**Key terms and sources**

Based on an AI company's published design: Anthropic's post on its multi-agent research system. Volumes and the lab's numbers are our own illustrations. Uses multi-agent systems, agent infrastructure, memory and context and evaluating agents.
