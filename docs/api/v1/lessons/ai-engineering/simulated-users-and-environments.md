# Simulated Users and Test Environments for Agents

> Your support agent changes databases and talks to customers. How do you test it before real customers do?

- Track: AI Engineering › Applied Evals › Lessons
- Type: Concept · 18 min
- Page: https://aimlrounds.com/tracks/ai-engineering/simulated-users-and-environments/
- Before this: Agent Evals: End States, pass^k and Cost (`ai-engineering/evaluating-agents`)
- Quiz topic: `evals`

## Intuition

### The situation

Your telecom support agent can change account settings, while customers must restart phones and toggle settings themselves. It passed a test set of scripted conversations, yet real customers get stuck halfway through fixes. The interviewer asks:

> Your support agent changes databases and talks to customers. How do you test it before real customers do?

#### Why it matters

Agents that act can't be judged by their final message: the reply can sound right while the database is wrong. And a scripted list of user messages breaks the moment the agent asks something unexpected. So agent evals need an environment that reacts, and a user who can answer back.

### The idea

Think of a doctor giving first-aid instructions over the phone. Knowing the right treatment is half of it; the other half is explaining clearly, checking what the caller actually did, and fixing their mistakes. Test both halves.

[Figure: Three parts. A sandbox that changes. A user who answers and acts. Checks on the end state.]

_Agents fail most when the user has to act too._

### Play

**Try to break it.** Switch between agent alone and dual control, for both models.

#### Where does the agent lose points?

Model

Who acts on the phone

Let the agent do everything and gpt-4.1 passes about 52% of telecom tasks; make it guide a user who acts on their own phone and it falls to 34%. o4-mini drops 25 points. The tasks didn't change, only who had to act. Run the same split on your own agent: if it passes alone and fails with a user, work on how it instructs and checks, not on its reasoning.

**Now say why:** why does the same model lose points when the user acts?

## How it works

### How it works

#### In one breath

Give the agent a sandbox: copies of its tools and data, reset before each run. Each task has a starting state, a hidden goal for a simulated user, and a check on the end state ("refund recorded", "line re-activated"). An LLM plays the user. In τ²-bench the user can act too (toggle airplane mode, restart the phone), which is where agents struggle most: removing the user and letting the agent do everything raised scores by about 20 points. Check the simulator, because its mistakes look like agent failures.

#### Environment, user, checks

##### The sandbox

Copies of the real tools (or faithful fakes) over a test database, reset to a known state for every run. Anthropic's guide calls the final state the **outcome**: for a flight agent, whether the reservation exists in the database. Grade outcomes with code where you can.

##### Tasks built from parts

τ²-bench builds tasks from small subtasks, each with a setup function, a solution and an assert function, so tasks of known difficulty can be composed and checked automatically. Its telecom domain has 114 tasks drawn from 2,285 composed ones.

##### The simulated user

An LLM gets a persona and a hidden goal and reveals information only when asked. In τ²-bench's telecom domain the user also has tools on their own device, so the agent must guide them, check what they did and recover when they get it wrong. That **dual control** is the hard part: when the authors let the agent do everything itself (no-user mode), pass rates rose by 18 points for gpt-4.1 and 25 points for o4-mini.

##### Separate the failure types

The no-user ablation is a useful trick for your own evals: if the agent solves the task alone but fails with a user, the problem is communication and coordination, not reasoning. Fix them differently.

##### Check the simulator

Simulators make mistakes: τ²-bench measured 16% of telecom simulations with a user error (6% critical), against 40% in the original τ-bench retail domain. Read a sample of failed runs and discard or fix those where the user, not the agent, went wrong. Constraining the simulator with its own tools and visible state made it more reliable.

##### Repeat and report

Run each task several times and report pass^k, as in Agent Evals, plus turns, cost and time per task.

## In practice

### In practice

#### In practice

- **Sandbox everything:** tool copies over test data, reset each run.

- **Grade end states with code:** rows changed, tickets closed, settings applied.

- **Hidden-goal users:** personas that reveal information only when asked.

- **Let users act if they do in reality:** coordination is where agents fail.

- **Run the no-user ablation:** to split reasoning failures from communication failures.

- **Audit the simulator:** read failed runs; discard ones where the user erred.

### The answer that sounds right

#### "It passes our scripted conversations"

It sounds tested, but a script can't react when the agent asks something unexpected, and scripted users never make mistakes. Use a simulated user who answers, acts and sometimes gets it wrong.

## Say it

### Your support agent changes databases and talks to customers. How do you test it before real customers do?

#### The interviewer pushes further

Follow-up 1 of 3

Why not script the user's messages?

Agents ask unexpected questions and take different paths, so a fixed script stops making sense after the first deviation. A simulated user can answer whatever is asked.

Follow-up 2 of 3

How do you stop simulator mistakes from polluting the results?

Constrain the simulator with its own tools and visible state, read a sample of failures, and exclude runs where the user, not the agent, made the error.

Follow-up 3 of 3

The agent passes alone but fails with a user. What do you work on?

Communication: clearer step-by-step instructions, confirming what the user did, and recovering from user mistakes, rather than reasoning about the task.

#### The 30-second answer

I'd build a sandbox with copies of the agent's tools over test data, reset for every run, and grade the end state with code, like whether the line was re-activated. An LLM plays the user with a persona and a hidden goal, and if real users act, the simulated user gets tools too, as in τ²-bench's dual control. That's where agents struggle: letting the agent act alone raised pass rates by 18 to 25 points. So I'd run that no-user ablation to separate reasoning from coordination failures, audit the simulator because its errors look like agent failures, and report pass^k and cost per task.

**Key terms and sources**

Building a sandbox where an agent's actions really change state, checking the end state with code, simulating users who also act (τ²-bench's dual control), separating reasoning failures from coordination failures, and checking the simulator itself. · checked 15 Nov 2026

#### Sources

- [V. Barres, H. Dong, S. Ray, X. Si and K. Narasimhan, τ²-Bench: evaluating conversational agents in a dual-control environment, 2025](https://arxiv.org/abs/2506.07982)

- [S. Yao et al., τ-bench, ICLR 2025](https://arxiv.org/abs/2406.12045)

- [Anthropic, Demystifying evals for AI agents, Jan 2026](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)

- H. Husain and S. Shankar, _Evals for AI Engineers_ (O'Reilly): the Analyze-Measure-Improve lifecycle, error analysis, judges, CI and review

Explanations and examples are ours, built from these sources. Lab numbers are illustrative unless a lab says otherwise. Many recent papers are preprints, and benchmark scores change quickly.
