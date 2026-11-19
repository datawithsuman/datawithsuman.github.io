# MCP: The Model Context Protocol

> What is MCP, and how is it different from function calling?

- Track: AI Engineering › Agentic AI › Lessons
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/ai-engineering/model-context-protocol/
- Before this: Tool and Function Calling (`ai-engineering/tool-calling`)
- Quiz topic: `agents`

## Intuition

### The situation

The company wants its order system usable from the refund agent, the internal support chat, agents in the IDE and a few vendor tools, without a separate integration for each. A colleague suggests MCP, and says that also makes it safe. The interviewer asks:

> What is MCP, and how is it different from function calling?

**Running example:** the company wants its order system usable from the refund agent, the internal support chat, agents in the IDE and a few vendor tools, without writing a separate integration for each.

#### Every app × every tool

Before MCP, each AI application defined its own plugin or tool format, so connecting a data source meant writing and maintaining an adapter per application. Tool providers repeated the work for every host; hosts repeated it for every tool.

### The idea

Think of USB-C. Before it, every device needed its own cable for every charger. A standard port means each device and each charger is built once. But a standard port tells you nothing about whether that charger is safe to plug in.

[Figure: Without MCP, every application connects to every tool: 10 applications and 20 tools need 200 custom integrations. With MCP, each connects once to the protocol: 30 components.]

_From the lab: integration pieces to build and maintain._

### Play

**Try to break it.** Change the number of AI applications and the number of tools, and watch how far apart the two counts get.

#### Custom glue for every pair

Counts integration components to build and maintain; ignores per-integration size.

With **10** AI applications and **20** tools, custom integrations mean **200** adapters to build and keep working; with MCP, 10 clients (usually built into the host) and 20 servers: **30**, 6.7× fewer, and the gap grows with both numbers. The trap is assuming standard plumbing means safe plumbing: anyone can publish a server, and a server's tool descriptions go straight into the model's context.

**Now say why:** the model still emits tool calls, so what has MCP actually standardised?

## How it works

### How it works

#### In one breath

Every AI app (chat assistant, IDE, agent) wants to connect to every tool and data source (GitHub, Slack, databases, your order system). Without a standard, that's **N apps × M tools** custom integrations. The **Model Context Protocol**, introduced by Anthropic in Nov 2024 and since adopted widely (and donated to the Linux Foundation's Agentic AI Foundation in Dec 2025), standardises the connection: a tool provider writes one **MCP server**; any MCP-capable **host** connects to it through a **client**, so it's **N + M**. Servers expose **tools** (actions the model can call), **resources** (data to read) and **prompts** (templates); messages are **JSON-RPC 2.0** over **stdio** (local) or **Streamable HTTP** (remote, with OAuth). MCP doesn't replace function calling; it's how the tools get discovered and invoked across apps. The spec is versioned by date and changes often, so check the current revision.What you'll be able to do after this: explain MCP's architecture and primitives, compare it with function calling, and name its security risks.

#### Hosts, clients, servers and primitives

- **Host:** the AI application (a desktop assistant, IDE, agent runtime). It runs one **client** per connected server and decides what the model sees and is allowed to do.

- **Server:** a program exposing capabilities. **Tools** (model-invoked actions with JSON-schema inputs), **resources** (readable data, by URI), **prompts** (reusable templates the user can pick).

- **Asking for more:** when a server needs input mid-call, such as a user confirmation, it returns **input required**, and the client repeats the call with the answers. Since the 2026-07-28 spec, this replaces server-initiated requests, and **sampling** (borrowing the client's model), **roots** and logging are deprecated.

- **Protocol:** JSON-RPC 2.0 messages: `server/discover`, `tools/list`, `tools/call`, `resources/read`, and `subscriptions/listen` for changes. Since the 2026-07-28 spec there is no `initialize` handshake or session: every request carries its protocol version and capabilities, so any server instance can answer it.

- **Transports:** **stdio** for local servers launched by the host; **Streamable HTTP** for remote servers, with OAuth 2.1 authorisation. The older HTTP+SSE transport is deprecated.

- **Extensions:** optional features negotiated through capabilities: **tasks** for long-running work, and **MCP Apps** (Jan 2026), which lets a tool return an interactive interface.

The spec is dated: 2025-03-26 (Streamable HTTP, OAuth 2.1), 2025-06-18 (elicitation, structured tool output, resource indicators), 2025-11-25 (experimental tasks, client ID metadata documents) and 2026-07-28 (stateless requests, no sessions, input-required results, tasks as an extension, sampling and dynamic client registration deprecated). Deprecated features get at least 12 months' notice. For the details, see MCP Under the Hood; for A2A and other protocols, Agent Protocols. (Updated 7 Nov 2026.)

## In practice

### In practice

#### Security and practice

- **Tool poisoning:** malicious instructions hidden in a server's tool descriptions (which the user rarely sees) can steer the model; a server can also change its tools after you approved it ("rug pull"). Pin and review server versions; show users what tools do.

- **Over-broad permissions:** a server with full repo or database access is a powerful exfiltration channel if combined with untrusted content (lethal trifecta). Use least-privilege tokens, OAuth scopes and per-tool approval.

- **Too many servers:** every connected server adds tool definitions to context; enable only what the task needs, or use tool search (tool calling).

- **Ecosystem:** official SDKs in many languages, registries of servers, and support across major assistants, IDEs and agent frameworks. Related protocols: A2A (agent-to-agent) addresses agents calling other agents rather than tools.

**Measured, 2026.** A scan found 7,973 live remote MCP servers, and 40.6% exposed tools with no authentication. Of 119 OAuth-enabled servers tested, every one had at least one flaw, and 96.6% had client registration flaws. Another study audited 414 internet-facing servers: 91.8% lacked OAuth, and 687 tools offered shell execution with no access control. Standard plumbing isn't safe plumbing.

#### A USB-C port for AI tools

MCP turns N × M custom integrations into N + M standard ones by defining how hosts discover and call tools, read resources and use prompts, while trust, permissions and context budget remain the host's job.

### The answer that sounds right

#### "MCP makes tools safe"

It sounds right, since standards tend to feel safer. But it standardises access, and security is still yours. Anyone can publish a server, its tool descriptions go straight into the model's context, and a server can change its tools after you approved it. So pin servers, scope tokens and require approval for sensitive tools. It doesn't replace APIs either: servers usually wrap them.

## Say it

### What is MCP, and how is it different from function calling?

#### The interviewer pushes further

Follow-up 1 of 3

MCP vs function calling?

Function calling is how a model requests a tool call in one API; MCP is how tools are packaged, discovered and invoked across many hosts. A host typically converts MCP tools into the model's function-calling format.

Follow-up 2 of 3

Tools vs resources vs prompts?

Tools are model-controlled actions; resources are application-controlled data the host can include in context; prompts are user-selected templates.

Follow-up 3 of 3

How would you expose your order system via MCP safely?

A remote server with OAuth, read-only tools by default, a narrow refund tool with server-side limits and idempotency, audit logs, and human approval above a threshold.

#### The 30-second answer

MCP is an open protocol, started by Anthropic and now under the Linux Foundation, that standardises how AI applications connect to tools and data. A host runs a client per server; servers expose tools the model can call, resources it can read and prompt templates, over JSON-RPC via stdio locally or Streamable HTTP remotely with OAuth. It turns N times M custom integrations into N plus M. It complements function calling rather than replacing it: the model still emits tool calls, MCP standardises discovery and execution. The main risks are untrusted servers, poisoned tool descriptions and over-broad permissions, so pin servers, scope tokens and require approval for sensitive tools.

**Go further**

#### What not to say

- "MCP makes tools safe." It standardises access; security is still yours.

- "MCP replaces APIs." Servers usually wrap existing APIs.

**Key terms and sources**

What MCP is and why it spread: the N×M integration problem, hosts, clients and servers, the primitives (tools, resources, prompts; and and how servers ask for more input), JSON-RPC messages, transports (stdio, Streamable HTTP), authorisation, how MCP relates to plain function calling, security concerns, and how the dated spec evolves · built from the Model Context Protocol specification and changelogs (modelcontextprotocol.io), Anthropic's MCP announcement (Nov 2024), the Linux Foundation Agentic AI Foundation announcement (Dec 2025), and the OWASP and Invariant Labs analyses of MCP tool poisoning · checked 29 Oct 2026

#### Sources

1. Model Context Protocol specification, revisions and changelog, modelcontextprotocol.io; GitHub releases.

2. Anthropic, "Introducing the Model Context Protocol", Nov 2024.

3. Linux Foundation, announcement of the Agentic AI Foundation (MCP contributed by Anthropic), Dec 2025.

4. Invariant Labs, "MCP Security Notification: Tool Poisoning Attacks", 2025; OWASP GenAI Security Project guidance on agentic applications.

5. MCP specification 2026-07-28 and changelog; H. Zhou et al., "A First Measurement Study on Authentication Security in Real-World Remote MCP Servers", 2026, arXiv:2605.22333; N. Padilla, "Exposed by Design", 2026, arXiv:2608.00150.
