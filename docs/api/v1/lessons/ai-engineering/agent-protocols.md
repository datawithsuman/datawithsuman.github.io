# Agent Protocols: MCP, A2A, AG-UI and Commerce

> Your agent needs tools from other teams, help from another company's agent, a live UI and the ability to pay. Which protocols cover which connection?

- Track: AI Engineering › Agentic AI › Lessons
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/ai-engineering/agent-protocols/
- Before this: MCP: The Model Context Protocol (`ai-engineering/model-context-protocol`)
- Quiz topic: `agents`
- Sources checked: 2026-11-07 · Text last changed: 2026-11-20 · Version: d6f2dbea17

## Intuition

### The situation

Your travel agent uses internal tools, books through three airlines' agents, shows progress in a web app, and pays on the customer's behalf. A colleague says MCP covers all of it. The interviewer asks:

> Your agent needs tools from other teams, help from another company's agent, a live UI and the ability to pay. Which protocols cover which connection?

#### Why it matters

Early agents wired everything by hand: each tool, each partner and each UI had custom glue. As agents connect to more systems, and to each other, standards decide what can talk to what. Interviewers now ask "MCP or A2A?" and expect you to say they solve different problems. This lesson places each protocol on one map. For MCP's internals, see MCP Under the Hood.

### The idea

Think of a building's wiring. Power sockets, network cables, the intercom and the card reader at the door each have their own standard. One plug doesn't do everything, and that's fine, as long as each fits its job.

[Figure: Four connections. Tools via MCP. Other agents via A2A. Interfaces via AG-UI. Payments via AP2, ACP or UCP.]

_MCP and A2A solve different problems._

### Play

**Try to break it.** Pick each scenario, and watch which protocols it needs. Then raise the number of agents.

#### Which protocols does it need?

A simplified mapping. Real systems may use other options, such as plain APIs, for some connections.

A **support agent** with internal tools needs only MCP. A **travel agent** that books through airline agents adds A2A, because each airline's agent is a peer with its own rules. A **shopping agent** that pays adds AP2 or ACP, so the merchant can check what the user approved. A **copilot inside a web app** adds AG-UI to stream progress and tool calls to the screen. And with 8 agents from different teams, custom pairwise links would be 28, against 8 implementations of one protocol.

**Now say why:** why is another company's agent not just another MCP tool?

## How it works

### How it works

#### In one breath

Agents connect to four kinds of thing, and each now has an open protocol. **MCP** connects an agent to tools and data. **A2A** lets an agent hand a task to another agent, possibly from another company: it finds it through an **Agent Card**, sends messages, and tracks a **task** through states like working, input required and completed. **AG-UI** streams an agent's progress to a user interface as events. **AP2**, **ACP** and **UCP** let agents shop and pay with proof of what the user authorised. MCP, A2A, Agent Skills and AGENTS.md now sit under the Linux Foundation's **Agentic AI Foundation**. They layer rather than compete.

#### The map

| Connection | Protocol | What it standardises |
|---|---|---|
| Agent ↔ tools and data | **MCP** | Servers expose tools, resources and prompts. Latest spec 2026-07-28. |
| Agent ↔ agent | **A2A** | Agent Cards for discovery, messages, tasks with states, streamed updates. Version 1.0. |
| Agent ↔ user interface | **AG-UI** | A stream of events: text, tool calls, state changes, reasoning, sub-agents. |
| Agent ↔ payments and shops | **AP2**, **ACP**, **UCP** | Signed proof of what the user authorised, checkout and payment flows. |
| Agent ↔ instructions | **Agent Skills**, **AGENTS.md** | Packaged know-how in folders, and project instructions for coding agents. |

##### A2A in more detail

Google started A2A, gave it to the Linux Foundation, and it reached version 1.0 in 2026. In August 2026 it joined the Agentic AI Foundation, backed by over 150 organisations.

- **Agent Card:** a JSON file, usually at `/.well-known/agent-card.json`, listing the agent's skills, endpoints, supported bindings and security schemes. Version 1.0 lets cards be signed.

- **Tasks:** work has a lifecycle: submitted, working, input required, auth required, completed, failed, cancelled or rejected. Long jobs report progress rather than blocking.

- **Messages, parts and artifacts:** messages carry parts (text, files, data), and results come back as artifacts.

- **Bindings:** JSON-RPC, gRPC or plain HTTP+JSON, with streaming and push notifications to a webhook.

##### MCP or A2A?

An MCP tool is a function the agent controls: call it, get a result. An A2A agent is a peer with its own model, tools and judgement, which may ask questions back, take hours, and keep its internals private. Use MCP to give your agent capabilities, and A2A to delegate a goal to someone else's agent.

##### Commerce

- **AP2** (Google, Sep 2025): signed "mandates" record what the user approved, from an open budget to a specific checkout, so merchants and payment networks can check an agent's authority. It extends A2A and UCP.

- **ACP** (OpenAI and Stripe, Sep 2025): checkout and delegated payment between an AI platform and merchants, used for buying inside ChatGPT.

- **UCP** (Google with Shopify, Walmart, Target and others): building blocks for agentic shopping across industries, using AP2 for payment mandates.

These protocols change monthly. Check the current versions before quoting details.

#### The maths

$$ {\text{custom links}} = \frac{{K}({K}-1)}{2}, \qquad {\text{with a protocol}} = {K} $$

The same argument as MCP's N × M to N + M, applied to agents talking to each other.

- **pairwise integrations**: Every pair of agents agrees on its own format.

- **number of agents**: Agents from different teams or companies that must work together.

- **one implementation each**: Each agent speaks the protocol once, and can talk to all the others.

## In practice

### In practice

#### In practice

- **Start with MCP:** most agents only need tools and data. Add A2A when you delegate goals across team or company boundaries.

- **Treat remote agents as untrusted:** an A2A peer's replies are input, like web pages. Its Agent Card name is not an identity, so verify signatures and authenticate.

- **Pass authority carefully:** when one agent delegates to another, make sure the second can't do more than the user allowed. Studies of multi-hop A2A delegation show this is easy to get wrong.

- **Keep humans in payment loops:** mandates prove what was approved, but set limits and confirmations too.

- **Watch versions:** pin protocol versions, and plan for breaking changes. MCP promises at least 12 months' notice before removing a deprecated feature.

### The answer that sounds right

#### "MCP covers everything"

It sounds right, since MCP is everywhere. But MCP connects an agent to functions it controls. Another company's agent is a peer with its own judgement, long tasks and private internals, which is what A2A is for. Interfaces and payments have their own protocols too.

## Say it

### Your agent needs tools from other teams, help from another company's agent, a live UI and the ability to pay. Which protocols cover which connection?

#### The interviewer pushes further

Follow-up 1 of 3

When would you use A2A instead of exposing the other team's agent as an MCP tool?

When the other agent is a peer with its own judgement, may need to ask questions back, runs for a long time, or belongs to another company that won't expose its internals. For a simple function, MCP is simpler.

Follow-up 2 of 3

What does an Agent Card contain?

The agent's name and description, its skills, the endpoints and protocol bindings it supports, its capabilities like streaming, and its security schemes. Version 1.0 cards can be signed.

Follow-up 3 of 3

Why does a payment protocol need mandates?

A merchant and payment network must check that a human authorised this purchase, within limits. A mandate is signed proof of that, rather than trusting the agent's word.

#### The 30-second answer

They solve different connections. MCP connects an agent to tools and data. A2A lets an agent delegate a task to another agent, possibly another company's: it finds it through an Agent Card, sends messages, and tracks a task through states like working, input required and completed, over JSON-RPC, gRPC or HTTP. AG-UI streams an agent's progress to a user interface as events. AP2, ACP and UCP handle shopping and payments with signed proof of what the user approved. MCP and A2A are now both under the Linux Foundation's Agentic AI Foundation. I'd start with MCP, add A2A for cross-boundary delegation, and treat every remote agent's output as untrusted.

**Key terms and sources**

A map of the open agent protocols in late 2026: MCP for tools and data, A2A for agent-to-agent tasks, AG-UI for agent-to-user interfaces, AP2, ACP and UCP for payments and shopping, plus Agent Skills and AGENTS.md, and who governs them. · checked 7 Nov 2026

#### Sources

- [Model Context Protocol specification, 2026-07-28](https://modelcontextprotocol.io/specification/latest)

- [A2A protocol specification, version 1.0](https://a2a-protocol.org/latest/specification/)

- [A2A joins the Agentic AI Foundation, Aug 2026](https://a2a-protocol.org/latest/blog/2026/08/27/a-new-chapter-for-a2a-joining-the-agentic-ai-foundation/)

- [AG-UI documentation](https://docs.ag-ui.com/)

- [Agent Payments Protocol (AP2)](https://ap2-protocol.org/)

- [Agentic Commerce Protocol (ACP)](https://agenticcommerce.dev/)

- [Universal Commerce Protocol (UCP)](https://ucp.dev/)

- [Agentic AI Foundation](https://aaif.io/)

- [Ehtesham et al., A survey of agent interoperability protocols](https://arxiv.org/abs/2505.02279)

Explanations are ours, built from these sources. Lab numbers are illustrative unless a lab says otherwise. Many recent papers are preprints, and provider policies change.
