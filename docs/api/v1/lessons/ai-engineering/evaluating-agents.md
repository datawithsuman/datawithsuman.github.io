# Agent Evals: End States, pass^k and Cost

> Why is 59% on one run not 59% for your customers?

- Track: AI Engineering › Applied Evals › Lessons
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/ai-engineering/evaluating-agents/
- Before this: What Is an Agent? The ReAct Loop (`ai-engineering/what-is-an-agent`), Code Checks First: Assertions, Schemas and Execution (`ai-engineering/code-based-evaluators`)
- Quiz topic: `evals`

## Intuition

### The situation

The refund agent scores 59% on a 200-case test set, in one run. Product wants to know whether customers will see 59% correct resolutions. A colleague checks that the final messages sound right, and says yes. The interviewer asks:

> Why is 59% on one run not 59% for your customers?

**Running example:** the refund agent scores 59% on a 200-case test set in one run. Product wants to know whether customers will see 59% correct resolutions.

#### Many steps, many valid paths, random behaviour

Two correct agent runs can take different routes; a final message can sound right while the database is wrong; and the same agent on the same task may succeed on Monday and fail on Tuesday. Text-matching metrics and single runs don't capture any of this.

### The idea

Think of judging a batter from one innings. A good score might be luck. "Scored once in eight innings" flatters them, and "scored in all eight" tells you who to trust. Your customer gets one innings, so you need to know which cases the agent solves every time.

[Figure: The same agent with a realistic mix of tasks. A single run scores 59.4 percent. Solved at least once in 8 tries: 97.7 percent. Solved every time in 8 tries: 26 percent.]

_From the lab's realistic mix of easy, flaky and hard tasks, which all average 59.4% per try._

### Play

**Try to break it.** Use the realistic mix of tasks, and raise the trials per task. Then switch to every task at 59.4%.

#### "It scored 59%"

Realistic mix: 30% of tasks almost always solved (98% per try), 30% flaky (60%), 40% hard (30%). Average per-try success is 59.4% in both cases; trials are independent.

Both setups have the same **59.4%** single-run score. With a realistic mix of easy, flaky and hard tasks, the agent solves **97.7%** of tasks at least once in 8 tries (pass@8, the flattering number), but solves only **26.0%** _every_ time (pass^8). That mirrors τ-bench, where gpt-4o dropped from about 61% to about 25% in retail. For a customer, consistency is what matters: a refund agent that gets a case right "sometimes" is a support problem. If every task were equally 59% likely (the hypothetical), pass^8 would be just 1.5%: consistency depends on which tasks are reliably solved.

**Now say why:** both setups score the same on one run, so why are their pass^8 numbers so different?

## How it works

### How it works

#### In one breath

An agent is judged by **outcomes**: did the refund end up correct in the database, did the code pass the tests? Good agent evals run the agent in a realistic (simulated) environment and check the final **state**, not the wording. Because agents are stochastic and take many steps, a single run says little: **pass@k** (solved in at least one of k tries) flatters them, while **pass^k** (solved in _all_ k tries, from τ-bench) measures the consistency users need. On τ-bench retail, gpt-4o's success fell from about 61% on one try to about 25% when it had to succeed in all 8. Also check **trajectories** (no forbidden actions, no wasted steps) and report **cost and latency per task**; public benchmarks (SWE-bench Verified, τ-bench, WebArena, OSWorld) are useful but move fast and can be gamed, so build your own task set. What you'll be able to do after this: design an agent evaluation, explain pass^k, and read agent benchmarks critically.

#### What to measure

- **Outcome / end state:** compare the environment's final state with the expected one (refund amount recorded, ticket closed, tests passing). τ-bench does this with a simulated user and database.

- **Consistency:** run each task k times; report pass^k (all succeed) next to pass@1.

- **Trajectory checks:** forbidden actions (refund above cap without approval), required steps (identity check), wasted or looping steps, tool errors.

- **Efficiency:** steps, tokens, cost and wall-clock per task; a 2% better agent at 3× the cost may lose (Kapoor et al. 2024 argue cost should always be reported).

- **Human or judge review** of tone and explanation, validated against humans.

## In practice

### In practice

#### Benchmarks and your own eval

| Benchmark | Tests |
|---|---|
| **SWE-bench Verified** | 500 real GitHub issues; the agent's patch must pass hidden tests |
| **τ-bench / τ²-bench** | customer-service agents (retail, airline) with a simulated user, policies and a database; pass^k |
| **WebArena, OSWorld** | web and computer-use tasks in realistic sandboxed environments |
| **GAIA** | general assistant questions needing browsing and tools |
| **METR time horizons** | length of tasks (in human time) agents finish at 50% reliability; roughly doubling every 7 months in their 2025 analysis |

- **Caveats:** scores depend on the agent scaffold, budget and number of attempts; leaderboards move monthly; benchmarks can leak or be over-fitted. Compare like with like and report cost.

- **Your own eval:** see also Simulated Users and Test Environments. 100–300 real cases with expected end states, a sandbox (copies of tools and data), a simulated user where needed, k runs per case, trajectory rules, and cost tracking; run on every prompt, model or tool change.

Terminal-Bench 2.0 has 89 hand-checked terminal tasks, and the best agent in its paper solved 63%. Its authors found model choice usually mattered more than the agent scaffold, and more tokens or turns didn't predict success. In practice, a 2025 study of 86 deployed agents found 74% relied mainly on human evaluation and 52% used LLM judges, and 75% of the 20 teams it interviewed had no formal benchmark set.

#### Judge outcomes, repeatedly, with the bill attached

Evaluate agents on end states in realistic environments, across repeated runs (pass^k), with trajectory rules and cost per task, because a single lucky run hides how unreliable an agent can be.

### The answer that sounds right

#### "Check the final message"

It sounds right, since that's what the customer reads. But a final message can sound right while the database is wrong, so check the end state. Report cost as well: a 2% better agent at 3× the cost may lose, and accuracy can be bought with more attempts. And one run tells you little, so run it k times.

## Say it

### Why is 59% on one run not 59% for your customers?

#### The interviewer pushes further

Follow-up 1 of 3

pass@k vs pass^k?

pass@k: at least one of k runs succeeds (useful with a verifier that picks the right run). pass^k: all k runs succeed, measuring reliability for users who get one run.

Follow-up 2 of 3

How do you evaluate without a real customer?

A user simulator (an LLM playing the customer with a hidden goal), as in τ-bench, plus replayed real conversations and human spot checks.

Follow-up 3 of 3

Why report cost?

Accuracy can be bought with more attempts and tokens; without cost, comparisons are misleading.

#### The 30-second answer

I'd evaluate an agent on outcomes: run it in a sandbox with realistic tools, data and a simulated user, and check the final state, like the refund recorded, rather than the wording. Because agents are stochastic I'd run each task several times and report pass^k, success on all k runs, alongside pass at 1; on tau-bench, gpt-4o went from about 61 percent to about 25 percent at pass^8. I'd add trajectory checks for forbidden or wasted actions and report cost and latency per task. Public benchmarks like SWE-bench Verified, tau-bench and WebArena are useful references, but I'd decide with our own task set.

**Go further**

#### What not to say

- "It scored X% on one run." Run it k times.

- "Check the final message." Check the end state.

**Key terms and sources**

How to measure agents: outcome-based task success in realistic environments, consistency across repeated trials (pass^k vs pass@k), trajectory and tool-use checks, cost and latency per task, the main benchmarks (SWE-bench Verified, τ-bench, WebArena, OSWorld, GAIA, METR task horizons) and their caveats, and building your own agent eval · built from Yao et al. (τ-bench, ICLR 2025), Jimenez et al. (SWE-bench, ICLR 2024), Zhou et al. (WebArena, ICLR 2024), Xie et al. (OSWorld, NeurIPS 2024), Mialon et al. (GAIA, ICLR 2024), Kwa et al. (METR, 2025) and Kapoor et al. (AI Agents That Matter, 2024) · checked 7 Nov 2026

#### Sources

1. S. Yao et al., "τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains", ICLR 2025, [arXiv:2406.12045](https://arxiv.org/abs/2406.12045).

2. C. Jimenez et al., "SWE-bench", ICLR 2024, [arXiv:2310.06770](https://arxiv.org/abs/2310.06770); S. Zhou et al., "WebArena", ICLR 2024, [arXiv:2307.13854](https://arxiv.org/abs/2307.13854); T. Xie et al., "OSWorld", NeurIPS 2024, [arXiv:2404.07972](https://arxiv.org/abs/2404.07972).

3. G. Mialon et al., "GAIA", ICLR 2024, [arXiv:2311.12983](https://arxiv.org/abs/2311.12983); T. Kwa et al. (METR), "Measuring AI Ability to Complete Long Tasks", 2025, [arXiv:2503.14499](https://arxiv.org/abs/2503.14499).

4. S. Kapoor et al., "AI Agents That Matter", 2024, [arXiv:2407.01502](https://arxiv.org/abs/2407.01502).

5. M. Merrill et al., "Terminal-Bench", 2026, [arXiv:2601.11868](https://arxiv.org/abs/2601.11868); M. Z. Pan et al., "Measuring Agents in Production", ICML 2026, [arXiv:2512.04123](https://arxiv.org/abs/2512.04123).
