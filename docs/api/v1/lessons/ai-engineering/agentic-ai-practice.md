# Agentic AI Practice

> 9 questions: compounding errors, tool overload, durable runs, trifecta, parallel sub-agents, skills, MCP auth, A2A.

- Track: AI Engineering › Agentic AI › Scenarios
- Type: Interview · 35 min
- Page: https://aimlrounds.com/tracks/ai-engineering/agentic-ai-practice/
- Before this: Agent Safety: Permissions, Sandboxing and the Lethal Trifecta (`ai-engineering/agent-safety`)
- Quiz topic: `agents`
- Sources checked: 2026-10-29 · Text last changed: 2026-11-19 · Version: 1a2b0d13d0

How to use this page

Give yourself about 5 minutes per question, as in an interview. Mix of napkin maths and design questions. Answer out loud (or on paper), then open the answer and compare.

**The toolkit:** task success ≈ (per-step success)^steps; pass^k = probability of succeeding in all k runs; restart-from-scratch cost explodes with steps, checkpoints keep it ≈ steps ÷ (1 − failure rate); N apps × M tools → N + M with MCP; the lethal trifecta = private data + untrusted content + external communication.

Question 1 · Easy · agent vs workflow

### Your team wants to build an 'agent' that classifies incoming support emails into 12 categories and routes them. Is an agent the right design?

Answer: **no: it's a fixed workflow (classify → route); use a classifier or a single LLM call with structured output**

1. The path doesn't depend on intermediate results; there's one decision with a fixed set of outcomes.

2. A single structured-output call (or a fine-tuned small classifier) is cheaper, faster, easier to test and evaluate.

3. Reserve agent loops for parts that need investigation with tools, like resolving the routed ticket.

**Follow-up:** What would make it agentic? If handling required looking things up and deciding next steps based on what was found.

Question 2 · Easy · compounding

### Each step of your agent succeeds 98% of the time. Roughly what is the success rate of a 30-step task, and what are two ways to improve it?

Answer: **about 0.98³⁰ ≈ 55%; shorten the task and add error detection and recovery**

1. 0.98^30 = e^(30·ln 0.98) ≈ e^(−0.606) ≈ 0.55.

2. Shorten: move deterministic steps into code or tools, so the model makes fewer decisions.

3. Detect and recover: validate tool arguments and results, retry failed steps, verify with checks; per-step reliability compounds.

**Follow-up:** What if errors are correlated (a wrong plan early)? Independent retries help less; add checkpoints that re-plan and human escalation.

Question 3 · Medium · tools

### Your agent has 120 tools from several MCP servers and often picks the wrong one. Give three fixes.

Answer: **load fewer tools per step (tool search / grouping), make tools distinct and well-described, and evaluate tool selection**

1. Retrieve only the relevant tools for the current task (tool search, RAG over tool descriptions), or route to sub-agents with smaller toolsets; RAG-MCP raised selection accuracy from 13.6% to 43.1% this way.

2. Merge overlapping tools, rename them clearly, add examples and parameter constraints (enums, IDs).

3. Build a tool-selection test set and track wrong-tool and bad-argument rates per change.

**Follow-up:** What does each extra tool cost even when unused? Its definition (~100–300 tokens) on every call, plus distraction.

Question 4 · Medium · durable execution

### A 150-step nightly agent job has a 1% transient failure rate per step and restarts from scratch on any failure. Estimate how often it finishes cleanly and what you'd change.

Answer: **0.99¹⁵⁰ ≈ 22% clean runs; add per-step checkpoints, retries with backoff and idempotent tools**

1. Clean run probability = 0.99^150 ≈ e^(−1.51) ≈ 0.22.

2. Restarting from scratch repeats most of the work (expected executions ≈ (1 − 0.99^150) / (0.01 × 0.99^150) ≈ 350 for 150 steps).

3. Checkpoint after each step (≈ 152 executions), retry transient errors with backoff, and make side-effecting tools idempotent so replays are safe.

**Follow-up:** Which step types need idempotency keys? Anything with side effects: refunds, emails, writes to external systems.

Question 5 · Hard · safety

### A 'personal assistant' agent reads the user's email, can search their documents and can send emails. Threat-model it and propose controls.

Answer: **it has the lethal trifecta; an injected email can make it exfiltrate documents. Remove or gate a leg.**

1. Private data (documents, inbox) + untrusted content (incoming email) + external communication (send email) = exfiltration path via prompt injection.

2. Controls: require user confirmation for every outbound email (with a clear preview), restrict recipients (allow-list or only replying to existing threads), block auto-rendering of external links/images.

3. Architecturally: process untrusted emails in a quarantined model without tools, extract only structured fields; keep the privileged agent's plan independent of email content.

4. Least-privilege scopes for document access, logging and anomaly alerts on outbound data volume.

**Follow-up:** Why not just tell the model to ignore instructions in emails? Injection is precisely overriding instructions; the defence must be outside the model.

Question 6 · Hard · multi-agent

### An engineer proposes five parallel coding sub-agents, each editing a different file of the same feature, to finish faster. What are the risks and what would you suggest?

Answer: **tightly coupled edits by agents with partial context will conflict; prefer one agent owning the change, with sub-agents for read-only exploration**

1. Each sub-agent makes assumptions (interfaces, names, data formats) the others can't see; merging produces inconsistencies (Cognition's 'share context' principle).

2. Multi-agent works best for independent, read-heavy work (research, search, analysis), as in Anthropic's research system.

3. Suggest: a single agent writes the change; parallel sub-agents may explore the codebase, run tests or review, returning summaries; or define interfaces first and only then parallelise.

**Follow-up:** How would you measure whether the multi-agent version is better? Same task set, compare end-state success (tests pass), pass^k, wall-clock time and total tokens.

Question 7 · Medium · skills

### Your agent has 80 skills, each with a 100-token description and 4,000 tokens of instructions. How many tokens do skills add per call if everything is loaded, and with progressive disclosure while one skill is in use?

Answer: **320,000 against 12,000**

1. Everything loaded: 80 × 4,000 = 320,000 tokens, more than most context windows.

2. Progressive disclosure: 80 × 100 = 8,000 for descriptions, plus 4,000 for the skill in use = 12,000.

What does selection depend on? The descriptions, so write them like tool descriptions: what it does and when to use it.

Question 8 · Medium · MCP auth

### Your remote MCP server accepts any valid token from your company's sign-in server and forwards it to the billing API. What two rules does this break, and what's the risk?

Answer: **No audience check, and token passthrough**

1. The server must accept only tokens issued for it, checking the audience. Otherwise a token meant for another server works here.

2. It must never forward the user's token upstream. It should get its own token for billing.

3. Risk: a token leaked from any service can be replayed here, and the server becomes a confused deputy acting with powers it wasn't given.

Which spec features prevent this? Resource indicators bind tokens to one server, and the security guidance bans passthrough.

Question 9 · Hard · A2A vs MCP

### A travel company wants its agent to book flights through three airlines' agents. Each airline's agent may ask the customer questions and takes minutes to confirm. MCP tools or A2A, and why?

Answer: **A2A: these are peer agents running long, interactive tasks**

1. Each airline's agent has its own model and rules, and won't expose its internals as simple functions.

2. A2A tasks have states like working and input required, with streaming or webhook updates for long jobs.

3. Discovery is through each airline's Agent Card. Treat replies as untrusted input, and verify signed cards.

Where does MCP still fit? For the travel agent's own tools: calendars, the customer database and payments.

**More practice and sources**

9 interview questions, easy to hard · answers hidden until you click · checked 29 Oct 2026

Keep practising

Uses the lessons in this track: What Is an Agent, Tool Calling, Agent Infrastructure, Evaluating Agents, Agent Safety, Multi-Agent Systems. New questions are added over time.

New lessons: Agent Protocols, MCP Under the Hood and Agent Skills.

New lesson: Measuring Agents in Practice.
