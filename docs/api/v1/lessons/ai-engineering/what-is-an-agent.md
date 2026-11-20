# What Is an Agent? The ReAct Loop

> Agent or workflow, and why does a 95%-per-step agent fail most 20-step tasks?

- Track: AI Engineering › Agentic AI › Lessons
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/ai-engineering/what-is-an-agent/
- Before this: Prompt Engineering Patterns (`ai-engineering/prompt-engineering-patterns`)
- Quiz topic: `agents`

## Intuition

### The situation

A refund agent must read a complaint, look up the order, check the policy, decide a refund and write back. "Where is my order?" fits a fixed flow, but late, missing and charged twice doesn't. A colleague says each step works 95% of the time, so it's reliable. The interviewer asks:

> Agent or workflow, and why does a 95%-per-step agent fail most 20-step tasks?

**Running example (this track):** the food-delivery company builds a **refund agent** that reads a customer's complaint, looks up the order, checks the policy, decides a refund, issues it via a tool and writes back to the customer.

#### Some tasks can't be scripted in advance

"Where is my order?" fits a fixed workflow. "My order was late, one item was missing and I was charged twice" needs several lookups, decisions that depend on what the lookups return, and maybe a follow-up question. Writing every branch by hand is impractical; letting the model choose the next step is the agentic approach.

### The idea

Think of a recipe and a cook. A workflow is the recipe: code decides every step, so it's predictable. An agent is the cook who tastes, then decides what to do next. That handles surprises, but every extra decision is another chance to go wrong, and those chances multiply.

[Figure: Whole-task success. 95 percent per step over 20 steps: 35.8 percent. Over 50 steps: 7.7 percent. 99 percent per step over 50 steps: 60.5 percent. 95 percent per step over 20 steps with error recovery: 78.5 percent.]

_From the lab's simple model, where steps fail independently. Real agents also make correlated errors._

### Play

**Try to break it.** At 95% per step, raise the steps from 20 to 50. Then try 99%. Then turn on error recovery.

#### "Each step works 95% of the time, so it's reliable"

Simple model: steps fail independently; recovery means a failed step is detected (tool error, validation, check) 80% of the time and retried once. Real agents also make correlated errors (a wrong plan early), so this is optimistic.

At **95%** per step, a **20-step** task succeeds only **35.8%** of the time; 50 steps, 7.7%. Even 99% per step gives 60.5% at 50 steps. Detecting and retrying failed steps (tool errors, schema checks, verifying results) lifts the 20-step task to **78.5%** for one extra call. This is why long autonomous tasks are hard, why benchmarks like τ-bench measure consistency, and why METR found the length of tasks agents can complete at 50% reliability has roughly doubled every 7 months: per-step reliability is what's improving.

**Now say why:** 95% sounds good, so how does a 20-step task end up at about a third?

## How it works

### How it works

#### In one breath

An **agent** is an LLM that decides its own next step in a loop: **think** about the goal, **act** by calling a tool (search orders, issue a refund, run code), **observe** the result, and repeat until done. That's the **ReAct** pattern (Yao et al. 2023). A **workflow**, by contrast, follows a path you hard-coded (classify → retrieve → answer). Anthropic's guidance: use the simplest thing that works, and reach for agents only when the steps can't be predicted in advance, because autonomy costs money, latency and reliability. The core reliability problem is **compounding**: if each step succeeds 95% of the time, a 20-step task succeeds only 36% of the time, so agents need error recovery, checks and good tools. What you'll be able to do after this: define an agent, choose between a workflow and an agent, and reason about multi-step reliability.

#### Think, act, observe

1. **Thought:** "The customer says late and missing item. I need the order details." (reasoning tokens)

2. **Action:** `get_order(id="48213")` (a tool call)

3. **Observation:** "delivered 40 min late; items: biryani, raita; raita marked missing by restaurant"

4. Repeat (check policy, compute refund, issue refund) until the model returns a final answer, or a step/budget limit is hit.

ReAct interleaving reasoning with actions beat acting-only and reasoning-only baselines; on ALFWorld and WebShop it improved absolute success rates by 34 and 10 points over imitation and reinforcement learning methods (Yao et al. 2023).

| Workflow patterns (Anthropic) | Agent |
|---|---|
| prompt chaining, routing, parallelisation, orchestrator–workers, evaluator–optimizer: code decides the path | the model decides the path, tool by tool, in a loop |
| predictable, cheaper, easier to test | flexible for open-ended tasks; costlier, less predictable |

## In practice

### In practice

#### When to build an agent, and when not to

- **Start with a workflow** if the steps are known; add agentic loops only where the path depends on intermediate results.

- **Good fits:** coding (tests give feedback), research, customer cases with variable investigation, operations with clear tools and checks.

- **Make each step reliable:** well-designed tools with clear errors, structured outputs, verification, and budgets (max steps, max cost, timeouts).

- **Keep humans in the loop** for irreversible or high-value actions (Agent Safety).

#### A model in a loop with tools, and reliability is the product

An agent lets the model choose actions step by step; because errors compound over steps, the engineering is about making each step reliable, detecting failures, and keeping the loop as short and constrained as the task allows.

### The answer that sounds right

#### "Everything should be an agent"

It sounds right, since agents can handle anything a workflow can. But most production systems are workflows with small agentic parts, and an agent costs more and is harder to test. Add a loop only where the path depends on intermediate results. High per-step accuracy doesn't make it reliable either: multiply it over the steps.

## Say it

### Agent or workflow, and why does a 95%-per-step agent fail most 20-step tasks?

#### The interviewer pushes further

Follow-up 1 of 3

Agent vs chatbot with tools?

A chatbot calls at most a tool or two per turn under user direction; an agent pursues a goal over many self-chosen steps, deciding when it's done.

Follow-up 2 of 3

How do you stop an agent looping forever?

Step, time and cost budgets; detection of repeated identical actions; a final "give up and escalate" path.

Follow-up 3 of 3

Why did ReAct work better than acting alone?

Reasoning between actions lets the model track progress, handle exceptions and update its plan based on observations, instead of blindly issuing actions.

#### The 30-second answer

An agent is an LLM running in a loop: it reasons about the goal, calls a tool, observes the result and decides the next step until it finishes, which is the ReAct pattern. A workflow instead follows a path defined in code, like chaining or routing. I'd use a workflow when the steps are predictable and an agent only when the path depends on intermediate results, because agents cost more and are less predictable. The key engineering problem is compounding error: at 95 percent per step a 20-step task succeeds about a third of the time, so you need reliable tools, validation, error recovery, budgets and human approval for risky actions.

**Go further**

#### What not to say

- "Everything should be an agent." Most production systems are workflows with small agentic parts.

- "Per-step accuracy is high, so it's reliable." Multiply over steps.

**Key terms and sources**

What makes an LLM system an agent: the loop of reasoning, acting with tools and observing results; how agents differ from chatbots and fixed workflows; Anthropic's workflow patterns (chaining, routing, parallelisation, orchestrator–workers, evaluator–optimizer); why per-step errors compound over long tasks; and when not to build an agent · built from Yao et al. (ReAct, ICLR 2023), Anthropic (Building Effective Agents, Dec 2024), Schick et al. (Toolformer, NeurIPS 2023), Kwa et al. (METR, Measuring AI Ability to Complete Long Tasks, 2025) and Yao et al. (τ-bench, ICLR 2025) · checked 29 Oct 2026

#### Sources

1. S. Yao et al., "ReAct: Synergizing Reasoning and Acting in Language Models", ICLR 2023, [arXiv:2210.03629](https://arxiv.org/abs/2210.03629).

2. Anthropic, "Building Effective Agents", Dec 2024, [anthropic.com](https://www.anthropic.com/research/building-effective-agents).

3. T. Schick et al., "Toolformer: Language Models Can Teach Themselves to Use Tools", NeurIPS 2023, [arXiv:2302.04761](https://arxiv.org/abs/2302.04761).

4. T. Kwa et al. (METR), "Measuring AI Ability to Complete Long Tasks", 2025, [arXiv:2503.14499](https://arxiv.org/abs/2503.14499); S. Yao et al., "τ-bench", ICLR 2025, [arXiv:2406.12045](https://arxiv.org/abs/2406.12045).
