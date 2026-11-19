# Improving Tools with Evals: Held-Out Tasks and Transcripts

> You keep rewriting tool descriptions and the score keeps rising. How do you know you're not overfitting?

- Track: AI Engineering › Applied Evals › Lessons
- Type: Concept · 16 min
- Page: https://aimlrounds.com/tracks/ai-engineering/improving-tools-with-evals/
- Before this: Evaluating an MCP Server: Tool Choice, Descriptions and Distractors (`ai-engineering/evaluating-mcp-servers`)
- Quiz topic: `evals`

## Intuition

### The situation

Over two weeks, your team rewrote its MCP tools' descriptions 15 times, and the eval score climbed from 62% to 85%. Customers say agents still struggle with the same tasks. The interviewer asks:

> You keep rewriting tool descriptions and the score keeps rising. How do you know you're not overfitting?

#### Why it matters

Tool design is now a big lever on agent quality: Anthropic reports that refining tool descriptions helped Claude reach state-of-the-art on SWE-bench Verified. But tuning against the same tasks you score on rewards changes that only help those tasks. The held-out split is what makes improvements real.

### The idea

Think of a student who memorises last year's exam. Their practice score soars, and the real exam shows nothing changed. Keep some questions back that you never practise on, and judge progress only by those.

[Figure: Three rules. Realistic tasks. A held-out set. Metrics beyond accuracy.]

_If only the tuning score rises, you've taught the tools your test._

### Play

**Try to break it.** Try each change, and compare the two sets.

#### Keep the change, or revert it?

The change you made

Special-casing a phrase from two failing tasks gives the biggest jump on the tuning set, 70% to 78%, and makes the held-out set worse. It's the one change to revert. The concise response format barely moves accuracy but halves tokens per task, which is a real improvement. Numbers are illustrative; the rule is Anthropic's: trust the held-out set.

**Now say why:** why does the biggest tuning gain get reverted?

## How it works

### How it works

#### In one breath

Generate realistic, multi-step tasks with verifiable outcomes, split them into a set you tune on and a **held-out** set you only check. Run each task in a simple agent loop and collect accuracy, tool calls, tokens, runtime and errors. Read the transcripts: what the agent struggles with, and what it never mentions. Change one thing, re-run, and keep the change only if the held-out score improves too; if only the tuning score rises, you've taught the tools your test. Changes that tend to help: clear namespaced names, consolidated tools, concise responses, actionable errors.

#### The loop

##### Strong tasks

Good eval tasks look like real work and need several calls, sometimes dozens. Anthropic's examples:

| Weak | Strong |
|---|---|
| Schedule a meeting with jane@acme.corp next week. | Schedule a meeting with Jane next week to discuss the latest Acme project. Attach the notes from our last planning meeting and reserve a room. |
| Search the payment logs for purchase_complete and customer_id=9182. | Customer 9182 reports being charged three times for one purchase. Find the relevant logs and check whether other customers were affected. |

Each task needs a verifiable outcome, but not a rigid script of expected calls: many paths can be right.

##### What to collect

Top-level accuracy, plus runtime per call and per task, number of calls, total tokens and tool errors. A change that keeps accuracy but halves tokens is a win.

##### Read the transcripts

Look where the agent hesitates, retries or paginates endlessly. Anthropic notes that what agents leave out of their feedback can matter more than what they say.

##### Changes that tend to help

- **Namespacing:** asana_search, jira_search; or by resource, asana_projects_search. The prefix-or-suffix choice measurably affected results, and differed by model.

- **Fewer, higher-level tools:** schedule_event instead of list-then-create.

- **Concise responses:** a response_format option. In Anthropic's Slack example, a detailed response took 206 tokens and a concise one 72. Claude Code caps tool responses at 25,000 tokens by default.

- **Meaningful values:** names instead of UUIDs improved retrieval precision.

- **Actionable errors:** say what to try next, not an error code.

##### The held-out rule

Keep a held-out set you never look at while tuning. If a change raises the tuning score and leaves the held-out score flat, revert it.

## In practice

### In practice

#### In practice

- **Realistic tasks:** multi-step, phrased like users, with verifiable outcomes.

- **Split before you tune:** keep a held-out set you never inspect.

- **Collect more than accuracy:** calls, tokens, runtime and errors per task.

- **Read transcripts:** including what the agent doesn't say.

- **One change at a time:** keep it only if held-out results hold or improve.

- **An agent can help:** let a coding agent propose tool edits, judged by the same held-out rule.

### The answer that sounds right

#### "Our tool eval went from 62% to 85%"

It sounds like progress, but if you tuned against the same tasks you scored, the gain may not transfer. Check a held-out set, and revert changes that only help the tuning tasks.

## Say it

### You keep rewriting tool descriptions and the score keeps rising. How do you know you're not overfitting?

#### The interviewer pushes further

Follow-up 1 of 3

Why not specify the exact tool calls each task expects?

Many paths can be correct. Grading the outcome lets better strategies win; rigid call scripts punish them.

Follow-up 2 of 3

Accuracy didn't change but tokens halved. Is that an improvement?

Yes. Lower tokens mean lower cost and latency, and more room in the context window for the actual task.

Follow-up 3 of 3

What's a sign you're overfitting tool descriptions?

The tuning score rises while the held-out score is flat or falls, often after edits that mention specific phrases or cases from failing tasks.

I'd write realistic, multi-step tasks with verifiable outcomes, phrased like users and without scripting the expected calls, and split them into a tuning set and a held-out set. I'd run each in a simple agent loop and collect accuracy, calls, tokens, runtime and errors, and read the transcripts. Then I'd change one thing at a time, like namespaced names, consolidated tools, concise responses or actionable errors, and keep a change only if the held-out score holds or improves, because a tuning-only gain means I've fitted the tools to my test.

**Key terms and sources**

The eval loop Anthropic uses to improve tools: realistic tasks with verifiable outcomes, a held-out split, metrics beyond accuracy, transcript reading, and the tool changes that tend to help (namespacing, concise responses, actionable errors).

#### Sources

- Anthropic, Writing effective tools for agents, with agents, Sep 2025

- Anthropic, Demystifying evals for AI agents, Jan 2026

- H. Husain and S. Shankar, _Evals for AI Engineers_ (O'Reilly): the Analyze-Measure-Improve lifecycle, error analysis, judges, CI and review

Explanations and examples are ours, built from these sources. Lab numbers are illustrative unless a lab says otherwise. Many recent papers are preprints, and benchmark scores change quickly.
