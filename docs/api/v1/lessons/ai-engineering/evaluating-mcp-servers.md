# Evaluating an MCP Server: Tool Choice, Descriptions and Distractors

> You're shipping an MCP server for your product. How do you test that agents can actually use it?

- Track: AI Engineering › Applied Evals › Lessons
- Type: Concept · 18 min
- Page: https://aimlrounds.com/tracks/ai-engineering/evaluating-mcp-servers/
- Before this: Tool-Call Evals: Selection, Arguments, Trajectories and Effects (`ai-engineering/agent-and-tool-evaluation-metrics`), MCP: The Model Context Protocol (`ai-engineering/model-context-protocol`)
- Quiz topic: `evals`

## Intuition

### The situation

Your company publishes an MCP server for its CRM. Developers report that agents call contacts_search when they mean deals_search, and sometimes call a different vendor's search tool instead of yours. The interviewer asks:

> You're shipping an MCP server for your product. How do you test that agents can actually use it?

#### Why it matters

If you publish an MCP server, its users will plug it into agents you don't control, next to other servers you've never seen. A vague description or a confusing tool split means agents call the wrong tool, pass the wrong arguments or don't call yours at all, and your users blame your product. Your tool descriptions are effectively prompts, and they need evals like any prompt.

### The idea

Think of labelling switches in a building's control room. With five switches, "lights" is enough. With two hundred from different contractors, you need "floor 3, east, lights", or people flip the wrong one.

[Figure: Two layers. Rule checks on every call. Outcome checks on real tasks.]

_Format is mostly solved; choosing and planning aren't._

### Play

**Try to break it.** Add tools with vague descriptions. Then make them clear.

#### More tools, more confusion

Your tool descriptions

With 40 tools and vague descriptions, this illustrative agent picks wrongly on about 16 tasks in 100; clear, namespaced descriptions cut that to about 6. Both get worse as more tools are connected, and every definition also costs context. The numbers are made up, but the direction matches the benchmarks: MCP-Universe found that connecting unrelated servers lowered success.

**Now say why:** why do clear, namespaced names hold up as servers pile up?

## How it works

### How it works

#### In one breath

With MCP, an agent picks from tools it didn't come with, guided only by names, descriptions and schemas, often next to dozens of other servers' tools. So evaluate two layers. **Rule checks** on every call: real tool name, valid schema, call succeeded. **Outcome checks** on realistic multi-step tasks: right tool chosen among distractors, task done, verified by executing a check. Benchmarks agree that format is mostly solved and planning isn't: models follow schemas over 98% of the time, yet the best one completed only about 44% of MCP-Universe tasks.

#### Two layers of checks

##### Rule checks on each call

MCP-Bench (28 live servers, 250 tools) scores three things on every call with code: is the tool name real, do the arguments match the schema, did the call run without error. Top models scored above 98% on schema compliance and naming. Track these on your own traces too, since a drop usually means a description or schema change confused models.

##### Outcome checks on tasks

The hard part is choosing and sequencing tools. MCP-Bench's tasks are rewritten so they don't name the tools or steps, and add distractor servers; judges then score task completion, tool appropriateness and planning. Even strong models were weakest at running independent calls in parallel.

MCP-Universe (231 tasks over 11 servers and 133 tools) checks outcomes by execution rather than with an LLM judge: format checks, static answer checks, and dynamic checks that fetch live ground truth for time-sensitive tasks. The best model, GPT-5, completed 43.72%. Two lessons for your evals: context grows fast with each step, and agents often don't know how a specific server works, so a short exploration phase helped some models.

MCPMark (127 tasks with verification scripts) shows the reliability gap: the best model passed 52.6% on one try but only 33.9% on all four tries. MCP-Atlas (1,000 human-written tasks, 36 servers) found that 63% of failures were reasoning errors, not malformed calls.

##### Your own server eval

- Write 20–50 realistic tasks that need your tools, phrased the way users talk, without naming tools.

- Include tasks where your tools should **not** be called, and run with other popular servers connected as distractors.

- Grade outcomes by executing a check (the record exists, the file changed), and log call-level rule checks.

- Track tool-choice accuracy, calls per task, tokens per tool response and errors, across more than one model, since descriptions that suit one model can confuse another.

## In practice

### In practice

#### In practice

- **Descriptions are prompts:** version them and evaluate every change.

- **Test with distractors:** other popular servers connected, generic tool names nearby.

- **Test both sides:** tasks that need your tool, and tasks that shouldn't call it.

- **Execute outcome checks:** verify the state, not the agent's claim.

- **Log rule checks:** name, schema and execution success on every call.

- **Several models, several runs:** report pass^k, calls and tokens per task.

### The answer that sounds right

#### "Schema compliance is 99%, so the server works"

It sounds healthy, but valid calls to the wrong tool are still failures. Benchmarks show models format calls well and choose and plan poorly. Measure outcomes on real tasks with distractors.

## Say it

### You're shipping an MCP server for your product. How do you test that agents can actually use it?

#### The interviewer pushes further

Follow-up 1 of 3

Schema compliance is 99% but users say the agent ignores your server. What's wrong?

Selection, not format. The descriptions may not say when to use the tools, or other servers' tools look more relevant. Test tasks that should use your tools with distractors connected.

Follow-up 2 of 3

Why execute checks instead of asking an LLM judge whether the task was done?

Agents often claim success. Checking the actual state, as MCP-Universe and MCPMark do, can't be talked round.

Follow-up 3 of 3

How do you test that your tool isn't over-used?

Include tasks where it shouldn't be called, and count calls to it there.

With MCP, the agent chooses among tools it didn't come with, guided only by names, descriptions and schemas, often next to many other servers. I'd evaluate two layers: rule checks on every call, meaning a real tool name, a valid schema and a successful execution, and outcome checks on realistic tasks that don't name the tools, run with distractor servers connected, and verified by executing a check. Benchmarks show format is nearly solved, over 98% schema compliance, while planning isn't: the best model completed about 44% of MCP-Universe tasks. I'd version tool descriptions like prompts and test them across models.

**Key terms and sources**

What changes when tools come from MCP servers (descriptions act as prompts, many servers crowd the context), the checks to run on calls and outcomes, what MCP-Bench, MCP-Universe, MCPMark and MCP-Atlas found, and how to build your own server eval.

#### Sources

- Z. Wang et al., MCP-Bench: benchmarking tool-using LLM agents with complex real-world tasks via MCP servers, 2025

- Z. Luo et al., MCP-Universe: benchmarking LLMs with real-world MCP servers, 2025

- Z. Wu et al., MCPMark: a benchmark for stress-testing realistic and comprehensive MCP use, 2025

- Scale AI, MCP-Atlas, 2026

- Anthropic, Writing effective tools for agents, with agents, Sep 2025

Explanations and examples are ours, built from these sources. Lab numbers are illustrative unless a lab says otherwise. Many recent papers are preprints, and benchmark scores change quickly.
