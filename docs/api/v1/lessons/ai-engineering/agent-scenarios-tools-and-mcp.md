# Agent Scenarios: Tools and MCP

> Wrong tools, bad arguments, bloated tool outputs, changing MCP servers and authorisation mistakes.

- Track: AI Engineering › Agentic AI › Scenarios
- Type: Interview · 48 min
- Page: https://aimlrounds.com/tracks/ai-engineering/agent-scenarios-tools-and-mcp/
- Before this: Tool and Function Calling (`ai-engineering/tool-calling`), MCP Under the Hood: Messages, Transports and Authorization (`ai-engineering/mcp-under-the-hood`)
- Quiz topic: `agents`
- Sources checked: not stated · Text last changed: 2026-11-19 · Version: e6bbf998e0

How to use this page

Give yourself about 5 minutes per incident, as in an interview. Say the most likely cause first, how you'd confirm it from traces, and the fix; then open the answer and compare.

**The agent debugging order:** pull the trace for the failing runs → find the first wrong step (bad tool choice, bad argument, bad observation, bad decision) → check tools, prompt and context at that step → fix the cause, add the case to the agent eval set, and add a guard (budget, validation, approval) so the same failure can't do damage.

Question 1 · Easy · wrong tool

### After adding a 'cancel_subscription' tool, the agent sometimes cancels Gold memberships when customers ask to cancel an order. Why, and how do you fix it?

Answer: **overlapping, ambiguously described tools; clarify names and descriptions and gate destructive actions**

1. 'cancel_order' and 'cancel_subscription' look similar; the description doesn't say when not to use it.

2. Rename and describe precisely (with examples of when to use each), require explicit confirmation for subscription cancellation, and validate arguments in code.

3. Add test cases for both intents to the tool-selection eval.

**Follow-up:** Should destructive tools be auto-executed? No: confirmation or human approval, and reversible where possible.

Question 2 · Easy · huge tool output

### After a tool started returning full customer records instead of a summary, each agent run got slower and costs tripled, though the number of steps didn't change. Why does one tool's output cost so much?

Answer: **The output stays in context and is re-read on every later step**

1. A 40,000-token result added at step 3 of a 20-step run is paid for again on each of the next 17 calls.

2. Anthropic caps Claude Code's tool responses at 25,000 tokens by default, and found a concise response used 72 tokens against 206 for a detailed one.

3. Fix: return only the fields the agent needs, paginate or filter large results, offer a concise mode, and cap response size.

4. For heavy data, let the agent call tools from code and only return the result. Anthropic reported one workflow falling from 150,000 to 2,000 tokens.

How would you catch it? Track input tokens per step and tool response sizes in traces, and alert when they jump.

Question 3 · Medium · exposed MCP server

### A developer deployed an internal MCP server for the CRM to a public host for a demo. It has no authentication, and its tools include a customer search. What's the exposure, and what do you change?

Answer: **Anyone on the internet can call its tools and read customer records**

1. Unauthenticated remote servers are common: 40.6% of 7,973 found in one study, including one exposing over 5,000 CRM records.

2. Take it down, rotate any credentials it held, and check access logs.

3. Require OAuth with PKCE and audience checks, scope tools to the signed-in user, and add server scanning before deploys.

Why does this keep happening? Starting a server is one command, and authentication is opt-in in many templates.

Question 4 · Medium · catalogue growth

### Your assistant started with 10 integrations and now has over 100, with nearly 600 tools. Users say it increasingly picks the wrong one, especially for vague requests. What's happening, and what fixes it?

Answer: **Routing degrades as tools pile up, mostly because the right tool is missed**

1. A 2026 study on a real catalogue of 110 agents and 584 tools found routing F1 on vague requests fell 16 to 23 points as the catalogue grew.

2. Shortlisting the 20 most relevant tools with embeddings recovered 10 to 11 points. Keyword search did worse than no shortlist, because tools shared vocabulary.

3. About 10 points were lost to confusion between similar tools even when the right one was in the list, so merge or clearly separate look-alike tools.

4. Also watch catch-all tools absorbing specific requests: they took 19% of predictions in the full list, and 4% after shortlisting.

Why not just write better descriptions? Richer metadata helped little at the tool level. Narrowing the candidate set mattered more.

Question 5 · Medium · interface drift

### A team renamed some parameters on their tools and added two similar tools. No code changed in your agent, but its tool calls started failing. Why, and what makes calls robust to this?

Answer: **Tool calls depend on the interface text, and look-alike tools cause most of the damage**

1. In a 2026 study, these kinds of changes dropped one model's function-calling accuracy from 0.79 to 0.58.

2. Adding similar distractor tools did far more harm than rewording descriptions or renaming fields.

3. Validating each call against the current schema, then repairing it with the specific errors, restored 0.805. Simply retrying reached only 0.61.

4. Fix: version tool interfaces, validate calls before running them, feed back precise validation errors, and test the agent whenever tools change.

Who owns this risk? Whoever changes the tools. Treat tool schemas like an API with a changelog and tests.

Question 6 · Medium · tool failures

### When the inventory tool times out, your agent still answers customers confidently about stock levels. Traces show it retried twice, then replied without any tool result. What's going wrong?

Answer: **The agent can't tell what kind of failure happened, so it retries blindly and then answers from memory**

1. A 2026 fault-injection study found realistic MCP failures cut agents' task scores by 60%, from 8.08 to 3.23 out of 10.

2. Agents treated every failure as temporary: they retried or switched tools without diagnosing whether the fault was permanent.

3. About 6% of runs gave plausible answers with no tool evidence, which judges often scored well.

4. Fix: return structured errors that say whether to fix an argument, sign in, wait or stop; cap retries; and require answers about live data to cite a successful tool result, or say the data is unavailable.

Did bigger models cope better? Not in that study: the larger model kept no more of its score under faults. The framework's error handling mattered more.

Question 7 · Medium · protocol upgrade

### After a vendor upgraded its MCP server, your agent's calls to it started failing with version errors, while other servers kept working. What changed, and how should you have prepared?

Answer: **The server moved to the 2026-07-28 spec, which changed how versions are negotiated**

1. The new spec removed the opening handshake and sessions: every request now carries its protocol version, and a server that doesn't support it returns a version error.

2. Server-initiated sampling and some older features are deprecated, and the old HTTP+SSE transport is too.

3. Fix: pin and log the protocol version per server, test against new spec versions before vendors switch, and upgrade your client SDK on a schedule.

4. Deprecated features get at least 12 months' notice, so track the MCP changelog and plan migrations early.

How would you spot this quickly? Alert on error rates per MCP server and error type, not just overall tool failures.

Question 8 · Hard · unconfirmed deletion

### Your agent, connected to a project tool's MCP server, deleted a shared folder after reading an injected instruction in a task comment. The server's delete tool has a 'confirm' flag. Why didn't anyone get asked?

Answer: **Neither side asked a person: the server relied on the host, the host didn't prompt, and the model set the flag itself**

1. A 2026 study estimated 90% of destructive MCP tools have no server-side confirmation, and 32 of 41 popular apps and SDKs have no approval step by default.

2. With both defaults combined, 60.7% of app and destructive-tool pairs had no enforced human approval.

3. A confirmation flag the model can set isn't consent: models set confirm=true themselves, and injected deletions ran in 479 of 960 test runs.

4. Fix: in your app, require approval for every tool not marked read-only or non-destructive. In that study, this cut unapproved pairs to 5.4%.

Should you trust a tool's 'non-destructive' annotation? Only from servers you trust. The spec says to treat annotations from untrusted servers as untrusted.

**More practice and sources**

8 incidents so far · answers hidden until you click · updated 7 Nov 2026

Keep practising

Uses Tool Calling, MCP, MCP Under the Hood, Human-in-the-Loop Design. More incidents are added to this sub-section over time. Other sub-sections: Context and Memory, Planning and Reliability, Multi-Agent and Protocols, Observability and Debugging, Evaluation, Safety and Security, Cost and Latency, Human in the Loop, Long-Running and Scheduled Agents.
