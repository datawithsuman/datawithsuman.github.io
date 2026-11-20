# Tool and Function Calling

> How do models call tools, and why do 100 tools make an agent worse?

- Track: AI Engineering › Agentic AI › Lessons
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/ai-engineering/tool-calling/
- Before this: What Is an Agent? The ReAct Loop (`ai-engineering/what-is-an-agent`), Structured Output and Constrained Decoding (`ai-engineering/structured-output`)
- Quiz topic: `agents`

## Intuition

### The situation

The refund agent has tools like get_order, get_policy and issue_refund, and the company wants to add 50 more from other teams. A colleague says just give the agent every tool, since more tools means more capable. The interviewer asks:

> How do models call tools, and why do 100 tools make an agent worse?

**Running example:** the refund agent has tools like `get_order`, `get_policy`, `issue_refund` and `message_customer`, and the company wants to add 50 more from other teams.

#### Models write text; systems need actions

To look up an order or issue a refund, the model's output must become a precise, validated function call, and its result must flow back so the model can continue. Free-text parsing ("call get_order with 48213 please") is brittle.

### The idea

Think of a waiter writing an order ticket. The waiter doesn't cook: the kitchen reads the ticket, checks it and makes the dish. Now hand that waiter a 200-page menu. They read for longer and pick the wrong dish more often. The model proposes, and your code disposes.

[Figure: With 50 tools in the prompt, definitions cost 7,500 tokens per call. With tool search they cost 960. In the RAG-MCP stress test, the right tool was picked 13.6 percent of the time from a large set, and 43.1 percent after retrieving descriptions first.]

_Tokens from the lab, at about 150 per definition. The accuracy figures are from the RAG-MCP stress test, with a much larger toolset._

### Play

**Try to break it.** Raise the tools available from 50 to 200. Switch to tool search. Then compare 3 lookups one after another with 3 in parallel.

#### "Just give the agent every tool"

~150 tokens per tool definition; tool search adds one ~60-token search tool and shows the top 5 matches. Latency: 1.2 s per model turn, 0.8 s per tool call; the three lookups (order, payment, policy) are independent.

With **50 tools** in the prompt, **7,500 tokens** of definitions ride along on every call; at 200 tools, 30,000. Beyond cost, accuracy suffers: in the RAG-MCP stress test, picking the right tool from a large set succeeded only **13.6%** of the time, and retrieving relevant tool descriptions first raised it to **43.1%** while halving prompt tokens. With **tool search**, the agent sees about 6 definitions (960 tokens). Separately, letting the model issue the three independent lookups **in parallel** cuts latency from 7.2 s to **3.2 s**.

**Now say why:** a definition is only about 150 tokens, so what's the harm in adding more?

## How it works

### How it works

#### In one breath

The model can't run code; it can only write text. **Tool calling** makes that text structured: you describe each tool (name, description, JSON-schema parameters), the model replies with a **call** like `{"name": "get_order", "arguments": {"order_id": "48213"}}` (generated with constrained decoding), **your code** executes it, and the result goes back into the conversation for the next step. Models can request several independent calls at once (**parallel calls**), cutting latency. Most agent failures are tool failures: vague descriptions, overlapping tools, unhelpful errors, or too many tools; every tool definition costs context tokens, and selection accuracy drops as tools pile up (RAG-MCP: 13.6% with all tools loaded, 43.1% when relevant tools were retrieved first). What you'll be able to do after this: explain the tool-call loop, design good tools, and handle large tool sets.

#### The tool-call loop

1. You send the conversation plus tool definitions (name, description, parameter schema).

2. The model returns either a final answer or one or more tool calls with arguments.

3. Your code validates arguments, checks permissions, executes, and returns results (including errors) as tool-result messages.

4. The model continues with the results; repeat.

- **Good tool design** (Anthropic's guidance): few, clearly distinct tools that match how a person would do the task; descriptive names and docs with examples; parameters that are hard to misuse (enums, IDs not free text); responses that return what the agent needs (not raw dumps); errors that say how to fix the call.

- **Never trust arguments:** the model chose them, possibly influenced by injected text. Validate and authorise every call in code.

## In practice

### In practice

#### Production patterns

- **Strict schemas** so arguments always parse; validation and authorisation in code before execution.

- **Tool search / dynamic loading** for large toolsets (also offered by some providers and in MCP clients); group tools by task and expose only what the current step needs.

- **Errors as feedback:** return actionable messages ("order_id must look like ORD-12345") so the model can self-correct; cap retries.

- **Idempotency** for side effects: an `issue_refund` called twice must not pay twice (idempotency keys).

- **Evaluate tools** like prompts: test sets of tasks, track wrong-tool and bad-argument rates.

**Code instead of definitions.** With many MCP tools, an agent can write code that calls them, instead of loading every definition and passing every result through its context. Anthropic reported one workflow falling from 150,000 to 2,000 tokens, a 98.7% saving. Its tool guide also caps Claude Code tool responses at 25,000 tokens by default, and found a concise response used 72 tokens against 206 for a detailed one.

#### The model proposes, your code disposes

Tool calling turns model output into structured requests that your code validates and executes; agent quality depends as much on clear, few, well-documented tools as on the model.

### The answer that sounds right

#### "The model runs the API"

It sounds right, from the way people describe agents. But the model only emits a request. Execution, permissions and side effects are under your control, which is why you never trust the arguments: the model chose them, possibly influenced by injected text. More tools don't make it more capable either: past a point, they make it worse.

## Say it

### How do models call tools, and why do 100 tools make an agent worse?

#### The interviewer pushes further

Follow-up 1 of 3

The agent calls the wrong tool. What do you check?

Overlapping or vague descriptions, too many tools in context, ambiguous parameter names; then add examples, merge or split tools, and evaluate selection on a test set.

Follow-up 2 of 3

How do you make a refund tool safe to retry?

Idempotency key per refund request, server-side checks of amount and eligibility, and returning the existing result if called again.

Follow-up 3 of 3

Who executes the tool: the model or your system?

Your system. The model only emits the request; execution, permissions and side effects are under your control.

#### The 30-second answer

You give the model tool definitions with names, descriptions and JSON-schema parameters; it responds with structured calls instead of text; your code validates, authorises and executes them and returns results, including errors, and the loop continues. Models can request independent calls in parallel to cut latency. Good tools are few, distinct, well documented, hard to misuse and return concise results with actionable errors. Many tools bloat the context and hurt selection, so for large toolsets I'd retrieve relevant tools dynamically. And side-effecting tools need idempotency and permission checks in code.

**Go further**

#### What not to say

- "The model runs the API." Your code does.

- "More tools make the agent more capable." Past a point they make it worse.

**Key terms and sources**

How LLMs call tools: JSON-schema tool definitions, the model emitting a structured call, your code executing it and returning the result, parallel calls, error handling, and designing tools agents can use well (clear names and descriptions, few overlapping tools, helpful errors); plus why loading hundreds of tools hurts and how tool search fixes it · built from Schick et al. (Toolformer, 2023), Patil et al. (Gorilla, NeurIPS 2024), Gan & Sun (RAG-MCP, 2025), Anthropic (Writing tools for agents, 2025), and the OpenAI and Anthropic tool-use documentation · checked 7 Nov 2026

#### Sources

1. T. Schick et al., "Toolformer", NeurIPS 2023, [arXiv:2302.04761](https://arxiv.org/abs/2302.04761); S. Patil et al., "Gorilla: Large Language Model Connected with Massive APIs", NeurIPS 2024, [arXiv:2305.15334](https://arxiv.org/abs/2305.15334).

2. T. Gan & Q. Sun, "RAG-MCP: Mitigating Prompt Bloat in LLM Tool Selection via Retrieval-Augmented Generation", 2025, [arXiv:2505.03275](https://arxiv.org/abs/2505.03275).

3. Anthropic, "Writing effective tools for agents", 2025; Anthropic and OpenAI tool-use / function-calling documentation.

4. Anthropic, ["Code execution with MCP"](https://www.anthropic.com/engineering/code-execution-with-mcp), Nov 2025; ["Writing effective tools for agents"](https://www.anthropic.com/engineering/writing-tools-for-agents), Sep 2025.
