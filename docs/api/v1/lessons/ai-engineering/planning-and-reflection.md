# Planning and Reflection

> When does 'check your work' actually help an agent?

- Track: AI Engineering › Agentic AI › Lessons
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/ai-engineering/planning-and-reflection/
- Before this: What Is an Agent? The ReAct Loop (`ai-engineering/what-is-an-agent`)
- Quiz topic: `agents`
- Sources checked: 2026-10-29 · Text last changed: 2026-11-20 · Version: b42860c812

## Intuition

### The situation

The refund agent must compute a complicated case: late, a missing item and a double charge. Its amount must match the policy calculator, and sometimes it forgets the double charge. A colleague adds "double-check your work" to the prompt. The interviewer asks:

> When does "check your work" actually help an agent?

**Running example:** the refund agent must compute the refund for a complicated case (late + missing item + double charge) and its amount must match the policy calculator.

#### Long tasks drift; first attempts are often wrong

Without structure, an agent may repeat lookups, forget a sub-goal (the double charge) or commit to a wrong number. Humans plan, check their work and fix mistakes; agents need explicit mechanisms for the same.

### The idea

Think of re-reading your own maths homework, against checking it on a calculator. Re-reading feels careful, but you can't always see your mistake, and you may even change a right answer. With a calculator, you know which ones to redo. Reflection needs a signal from outside.

[Figure: With a 60 percent first attempt and 2 retries, final success is 60 percent with self-review only, and 93.6 percent with a reliable check.]

_From the lab's simplified model. A real self-review catches some errors, and also breaks some right answers._

### Play

**Try to break it.** With no reliable check, raise the retries. Then switch to the tests or the policy calculator, and change the chance an attempt is correct.

#### "Just ask it to check its work"

Simplified: attempts are independent; with a check, failures are always detected and retried; without one, the agent accepts its first answer (in practice, self-review catches some errors and also "fixes" some correct answers into wrong ones).

With a **reliable check** (unit tests, the policy calculator, a tool error), a 60% first attempt plus **2 retries** reaches **93.6%**, using only 1.56 attempts on average because most cases pass early. With **no reliable check**, retries don't help: the agent can't tell which answers are wrong, so success stays at 60%. Reflexion's gains came from test feedback; Huang et al. found that asking models to self-correct reasoning _without_ external feedback didn't improve, and sometimes hurt, accuracy. Design the loop around a signal.

**Now say why:** why do extra retries add nothing without a reliable check?

## How it works

### How it works

#### In one breath

Agents plan in two broad ways. **ReAct** decides one step at a time based on the latest observation: flexible, but it can wander. **Plan-and-execute** writes a plan up front (often with a strong model), executes steps (often with a cheaper model) and **re-plans** when something fails: more structured and cheaper, but brittle if the plan is wrong. **Reflection** asks the agent to critique its own attempt and try again; Reflexion lifted GPT-4 on HumanEval from 80% to 91% by reflecting on failed unit tests. The catch: reflection works when there's an **external signal** (tests, tool errors, a checker). Without one, models often can't tell they're wrong, and "self-correction" can even make reasoning worse (Huang et al. 2024). What you'll be able to do after this: choose between ReAct and plan-and-execute, and design reflection loops that actually improve results.

#### Planning and reflection patterns

| Pattern | How | Good for |
|---|---|---|
| **ReAct** | think → act → observe, one step at a time | exploratory tasks where each result changes the next step |
| **Plan-and-execute** | planner writes steps; executor runs them; re-plan on failure (Plan-and-Solve prompting showed explicit plans help reasoning) | tasks with a clear structure; cost (cheap executor) |
| **Reflection / Reflexion** | after a failed attempt, write a short critique and retry with it in memory | tasks with feedback: tests, errors, checkers |
| **Evaluator–optimizer** | one call generates, another evaluates against criteria, loop until pass | writing, translation, code review |
| **Search** (Tree of Thoughts) | explore several partial solutions and backtrack | puzzles and planning with evaluable states; expensive |

## In practice

### In practice

#### In production

- **Reasoning models** (RLVR-trained) plan internally; explicit planning prompts matter less, but tool-based checks matter as much as ever.

- **Keep a visible plan** (a to-do list in context or a scratch file) for long tasks so the agent tracks sub-goals; update it as steps complete.

- **Prefer verifiable steps:** compute amounts with tools, run tests, validate outputs; reflect on concrete failures.

- **Cap loops:** max retries and budgets; escalate to a human when the check keeps failing.

#### Plan to stay on track, reflect on evidence

Planning keeps multi-step work organised, and reflection turns failures into fixes, but only when an external signal says what failed.

### The answer that sounds right

#### "Ask it to double-check, and it fixes errors"

It sounds right, since that works for careful people. But Huang et al. found that asking models to self-correct reasoning without external feedback didn't improve accuracy, and sometimes hurt it. Reflexion's gains came from test feedback. Planning doesn't make agents deterministic either: if early observations invalidate the plan, it needs re-planning.

## Say it

### When does "check your work" actually help an agent?

#### The interviewer pushes further

Follow-up 1 of 3

When would plan-and-execute fail?

When early observations invalidate the plan; without re-planning it executes a wrong plan confidently. Add checkpoints that trigger re-planning.

Follow-up 2 of 3

Is an LLM judge a good enough verifier?

Sometimes, for style or completeness, after validation; for correctness, prefer executable checks (tests, calculators, database queries).

Follow-up 3 of 3

How does Tree of Thoughts differ from reflection?

It explores multiple partial solutions in parallel and backtracks using evaluations of intermediate states; reflection improves one trajectory after it fails.

#### The 30-second answer

ReAct plans step by step from observations, which is flexible but can wander; plan-and-execute writes a plan first, often with a strong model, executes with cheaper calls and re-plans on failure, which is more structured. Reflection has the agent critique a failed attempt and retry; Reflexion took GPT-4 from 80 to 91 percent on HumanEval using test feedback. The key is an external signal: tests, tool errors or a checker. Without one, self-correction often doesn't help reasoning and can hurt. In production I'd keep an explicit task list, verify with tools, and cap retries with escalation.

**Go further**

#### What not to say

- "Ask it to double-check, and it fixes errors." Not without a reliable signal.

- "Planning makes agents deterministic." Plans still need re-planning.

**Key terms and sources**

How agents organise multi-step work and recover from mistakes: ReAct's step-by-step planning vs plan-and-execute, task decomposition, re-planning, reflection and self-critique (Reflexion), evaluator–optimizer loops, and why reflection only works when there is a reliable signal to reflect on · built from Yao et al. (ReAct, 2023), Wang et al. (Plan-and-Solve, ACL 2023), Shinn et al. (Reflexion, NeurIPS 2023), Madaan et al. (Self-Refine, NeurIPS 2023), Huang et al. (LLMs Cannot Self-Correct Reasoning Yet, ICLR 2024), Yao et al. (Tree of Thoughts, NeurIPS 2023) and Anthropic (Building Effective Agents, 2024) · checked 29 Oct 2026

#### Sources

1. N. Shinn et al., "Reflexion: Language Agents with Verbal Reinforcement Learning", NeurIPS 2023, [arXiv:2303.11366](https://arxiv.org/abs/2303.11366); A. Madaan et al., "Self-Refine", NeurIPS 2023, [arXiv:2303.17651](https://arxiv.org/abs/2303.17651).

2. J. Huang et al., "Large Language Models Cannot Self-Correct Reasoning Yet", ICLR 2024, [arXiv:2310.01798](https://arxiv.org/abs/2310.01798).

3. L. Wang et al., "Plan-and-Solve Prompting", ACL 2023, [arXiv:2305.04091](https://arxiv.org/abs/2305.04091); S. Yao et al., "Tree of Thoughts", NeurIPS 2023, [arXiv:2305.10601](https://arxiv.org/abs/2305.10601).

4. S. Yao et al., "ReAct", ICLR 2023, [arXiv:2210.03629](https://arxiv.org/abs/2210.03629); Anthropic, "Building Effective Agents", 2024.
