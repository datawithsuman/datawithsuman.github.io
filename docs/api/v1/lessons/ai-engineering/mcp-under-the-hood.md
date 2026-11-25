# MCP Under the Hood: Messages, Transports and Authorization

> Walk me through what actually happens when an agent calls a tool on a remote MCP server, including how it's authorised. What changed in the 2026 spec?

- Track: AI Engineering › Agentic AI › Lessons
- Type: Concept · 22 min
- Page: https://aimlrounds.com/tracks/ai-engineering/mcp-under-the-hood/
- Before this: MCP: The Model Context Protocol (`ai-engineering/model-context-protocol`)
- Quiz topic: `agents`
- Sources checked: 2026-11-07 · Text last changed: 2026-11-20 · Version: b5c8c91116

## Intuition

### The situation

Your company is exposing its order system as a remote MCP server. The team followed a 2025 tutorial with an initialise handshake and sessions, and plans to forward users' tokens to the billing API. The interviewer asks:

> Walk me through what actually happens when an agent calls a tool on a remote MCP server, including how it's authorised. What changed in the 2026 spec?

#### Why it matters

The MCP overview explains why the protocol exists. Interviews for agent platform roles go deeper: what's on the wire, how remote servers scale, and how authorisation stops one server's token being used at another. The spec also changed a lot in July 2026, so answers based on older versions are now out of date.

### The idea

Think of a hotel key card. It opens your room and nothing else, it was issued at the front desk after checking your identity, and the bellboy can't copy it to open the safe. Each MCP token should work the same way: for one server, issued after a proper sign-in, and never passed on.

[Figure: Three layers. Stateless requests. Input-required results. Tokens bound to one server.]

_Most real servers get authorisation wrong._

### Play

**Try to break it.** Make PKCE optional and accept any redirect. Then accept any token.

#### Which attacks are still open?

A simplified threat model. Measured in 119 real OAuth-enabled MCP servers: 68.1% allowed PKCE to be skipped or downgraded, and 95.8% let anyone register a client with any redirect address.

With all four controls on, the three attacks are closed. Make PKCE optional and accept any redirect address, and an attacker who lures a user into signing in can catch the code and swap it for a token, which is account takeover. A study of 119 real OAuth-enabled MCP servers found every one had at least one flaw: 96.6% had client registration flaws, and 68.1% allowed PKCE to be skipped or downgraded. Accept tokens issued for any server, and a token stolen from one server works at yours. Pass the user's token upstream, and your server becomes a confused deputy.

**Now say why:** why must a token name the server it's for?

## How it works

### How it works

#### In one breath

Since the **2026-07-28** spec, MCP is **stateless**: there's no initialise handshake or session, and every JSON-RPC request carries its protocol version and capabilities. A client calls `server/discover`, lists tools, and calls them. When a server needs more input mid-call, such as a user confirmation, it returns **input required**, and the client repeats the call with the answers. That replaces server-initiated sampling and elicitation. Remote servers use **Streamable HTTP** and **OAuth 2.1**: the client finds the authorisation server from the server's metadata, signs the user in with PKCE, and gets a token issued for **that server only**. Real deployments often get this wrong: 40.6% of 7,973 live remote servers needed no authentication at all.

#### How a call works

##### Stateless requests

Earlier versions began with an `initialize` handshake and kept a session, identified by a header, on the server. The 2026-07-28 spec removed both. Every request now carries the protocol version and the client's capabilities in its metadata, and a server that doesn't support the version returns an error. Servers must answer `server/discover`. Without sessions, any server instance behind a load balancer can answer any request.

##### The main messages

- `server/discover`: what the server supports.

- `tools/list`, `resources/list`, `prompts/list`: what it offers. Lists can say how long they may be cached.

- `tools/call`: run a tool. Results can include structured content that matches an output schema.

- `subscriptions/listen`: one long-lived stream for change notifications, replacing the old separate GET stream.

##### Asking for more input

Previously, a server could send its own requests back to the client, to ask the user something (elicitation) or to borrow the client's model (sampling). Now a result has a type: **complete**, or **input required** with a list of questions. The client gathers the answers and repeats the call with them. Sampling, roots and logging are deprecated.

##### Tasks and extensions

Long-running work moved into an optional **tasks** extension, polled with `tasks/get`. Extensions are negotiated through capabilities. The first official one, **MCP Apps** (Jan 2026), lets a tool return an interactive interface, rendered in a sandboxed frame by clients such as Claude, VS Code's Copilot and Microsoft 365 Copilot.

##### Transports

**stdio** runs a local server as a subprocess. **Streamable HTTP** is the remote transport: the client POSTs each request, and the server answers with JSON or a stream. The old HTTP+SSE transport is deprecated, and if a stream breaks, the client re-sends the request.

##### Authorisation, step by step

1. The client calls the server without a token and gets **401**, pointing to the server's **protected resource metadata** (RFC 9728), which names its authorisation server.

2. The client identifies itself with a **client ID metadata document**, a URL describing it. Dynamic client registration is now deprecated.

3. The user signs in and consents. The client uses **PKCE**, so a stolen authorisation code is useless without the client's secret verifier.

4. The token request names the MCP server as the **resource** (RFC 8707), so the token is issued for that server only.

5. The server checks the token's audience. It must **never pass the user's token through** to other services; it gets its own tokens for those.

#### The maths

$$ {\text{code\_challenge}} = \text{BASE64URL}\big(\text{SHA256}({\text{code\_verifier}})\big) $$

PKCE. Local MCP clients can't keep a secret, so this one-time pair is what binds the sign-in to the token request. Servers that let clients skip it, or downgrade it, lose that protection.

- **sent at sign-in**: The client sends only this hash when it starts the sign-in.

- **kept secret**: A random string the client keeps, and reveals only when exchanging the code for a token. An attacker who steals the code doesn’t have it.

## In practice

### In practice

#### In practice

- **Never expose a remote server without authentication:** a July 2026 scan audited 414 internet-facing servers, 91.8% had no OAuth, and 687 tools offered shell execution with no access control.

- **Use a hardened OAuth setup:** enforce PKCE with S256, validate redirect addresses exactly, and check audience and issuer on every token.

- **Scope tightly:** request the fewest permissions, and give risky tools their own consent.

- **Validate inputs at the tool:** MCP servers have shipped SQL injection, SSRF and path traversal bugs, like any web service.

- **Plan for spec changes:** pin a protocol version, and track deprecations. Removed features get at least 12 months' notice.

- **Fewer tokens with code:** for many tools, let the agent write code that calls them, instead of loading every definition. Anthropic reported one workflow falling from 150,000 to 2,000 tokens.

### The answer that sounds right

#### "We followed the tutorial, so it's secure"

It sounds safe, but many tutorials predate the 2026 spec, and real servers are often misconfigured: every one of 119 tested OAuth servers had a flaw. Enforce PKCE, check redirects and audiences, and never forward the user's token.

## Say it

### Walk me through what actually happens when an agent calls a tool on a remote MCP server, including how it's authorised. What changed in the 2026 spec?

#### The interviewer pushes further

Follow-up 1 of 3

Why did MCP remove sessions?

Sessions tied a client to one server instance, which made load balancing and scaling harder. Stateless requests can go to any instance, and state that matters is passed explicitly.

Follow-up 2 of 3

What's token passthrough, and why is it banned?

An MCP server forwarding the user's token to another service. The token wasn't issued for that service, and the server loses control of what's done with it. The server must get its own tokens upstream.

Follow-up 3 of 3

A tool needs the user to confirm a refund mid-call. How does that work now?

The server returns input required with a confirmation question. The client shows it to the user and repeats the call with the answer.

#### The 30-second answer

Since the July 2026 spec, MCP is stateless: no initialise handshake or sessions, and each JSON-RPC request carries its version and capabilities, so any instance can serve it. The client discovers the server, lists tools and calls them; if the server needs input, it returns input required and the client repeats the call with answers, replacing server-initiated sampling and elicitation. Remote servers use Streamable HTTP and OAuth 2.1: the client finds the authorisation server from the server's metadata, signs in with PKCE, and gets a token bound to that server, which checks the audience and never passes the token on. Real servers often get this wrong: 40% of nearly 8,000 had no authentication.

**Key terms and sources**

The 2026-07-28 MCP specification in detail: stateless requests, discovery, tool calls, multi round-trip requests, tasks and extensions, Streamable HTTP, the OAuth flow step by step, and the security pitfalls measured in real servers. · checked 7 Nov 2026

#### Sources

- [MCP specification 2026-07-28 and changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog)

- [MCP authorization, 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization)

- [MCP security best practices](https://modelcontextprotocol.io/specification/2026-07-28/basic/security_best_practices)

- [MCP Apps extension](https://modelcontextprotocol.io/extensions/apps/overview)

- [Zhou et al., A First Measurement Study on Authentication Security in Real-World Remote MCP Servers](https://arxiv.org/abs/2605.22333)

- [Padilla, Exposed by Design: A Dynamic Security Assessment of Internet-Facing MCP Servers at Scale](https://arxiv.org/abs/2608.00150)

- [Anthropic, Code execution with MCP, Nov 2025](https://www.anthropic.com/engineering/code-execution-with-mcp)

Explanations are ours, built from these sources. Lab numbers are illustrative unless a lab says otherwise. Many recent papers are preprints, and provider policies change.
