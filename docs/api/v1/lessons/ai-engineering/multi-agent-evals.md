# Multi-Agent Evals: Hand-offs, Roles and Verification

> Your planner, researcher and writer agents produce a bad report. Which agent failed, and how do you measure it?

- Track: AI Engineering › Applied Evals › Lessons
- Type: Concept · 17 min
- Page: https://aimlrounds.com/tracks/ai-engineering/multi-agent-evals/
- Before this: Agent Evals: End States, pass^k and Cost (`ai-engineering/evaluating-agents`), Multi-Agent Systems (`ai-engineering/multi-agent-systems`)
- Quiz topic: `evals`

## Intuition

### The situation

Your research assistant uses a planner, three researcher agents and a reviewer. Reports are often confidently wrong, and each team owning an agent says their agent works fine on its own tests. The interviewer asks:

> Your planner, researcher and writer agents produce a bad report. Which agent failed, and how do you measure it?

#### Why it matters

Splitting work across agents adds hand-offs, and every hand-off can drop information. When the final report is wrong, "the system failed" doesn't tell you whether the planner set the wrong task, the researcher ignored it, or nobody checked the result. A taxonomy turns a vague failure into something you can count and fix.

### The idea

Think of a relay race where the team keeps losing. Timing each runner alone shows they're all fast. The race is lost in the baton passes, and in the last runner nobody checks for a dropped baton.

[Figure: Three failure groups. Bad design. Agents out of sync. Weak checking.]

_Multi-agent failures hide in the hand-offs._

### Play

**Try to break it.** Label each trace, and read the fix it points to.

#### Which group does it belong to?

What happened in the trace

Your label

Each failure points to a different fix. An agent acting out of order needs a clearer spec; a caveat lost between agents needs better hand-offs; a reviewer approving wrong numbers needs its own test on known-bad reports; repeated questions need loop detection. Labelling failed traces this way, by hand at first and then with a validated judge, tells you which kind dominates your system.

**Now say why:** why does each group need a different fix?

## How it works

### How it works

#### In one breath

Multi-agent systems fail in three ways, per the MAST study of 1,642 traces from 7 frameworks: bad **system design** (agents ignore the task or their role, repeat steps, don't know when to stop), **misalignment between agents** (withholding information, ignoring each other, derailing), and weak **verification** (stopping early, not checking, or checking wrongly). Failure rates ranged from 41% to 86.7%. Evaluate end to end first, then label failed traces with these modes, score each hand-off and each sub-agent, and check the verifier separately.

#### The MAST taxonomy and how to use it

Cemri, Pan and colleagues built the taxonomy from 150 traces, then labelled 1,642 traces from frameworks including ChatDev, MetaGPT, AG2, Magentic-One and OpenManus. Three experts reached Cohen's kappa 0.88.

| Group | Failure modes |
|---|---|
| **System design** | disobeys the task spec; disobeys its role; repeats steps; loses conversation history; unaware of when to stop |
| **Inter-agent misalignment** | conversation reset; fails to ask for clarification; task derailment; withholds information; ignores another agent's input; reasoning doesn't match action |
| **Task verification** | stops too early; no or incomplete verification; incorrect verification |

The most common single modes were step repetition (15.7% of traces), not knowing when to stop (12.4%) and disobeying the task spec (11.8%).

##### An LLM can label at scale

A few-shot o1 judge labelling traces with these modes agreed with the experts at kappa 0.77, and 0.79 on systems it hadn't seen; zero-shot it managed only 0.58. That's the pattern from validating a judge: examples matter.

##### Evaluate in layers

- **End to end:** did the system complete the task? Grade the final artefact or state.

- **Hand-offs:** when the orchestrator delegates, was it the right agent, with the right instructions and context? Score the delegation decision separately from the work.

- **Each agent:** did it stay in its role and do its sub-task? Reuse single-agent checks.

- **Verification:** test the checker on outputs you know are wrong. A verifier that passes everything is worse than none, because it gives false confidence.

##### Fixes, measured

Small changes helped in the study: clearer role specifications and giving the CEO agent final say improved ChatDev's success by 9.4%. But some changes helped one model and not another, so re-run the evals after every structural change.

## In practice

### In practice

#### In practice

- **End-to-end first:** grade the final output or state.

- **Label failures with a taxonomy:** MAST's groups, adapted to your system.

- **Score hand-offs:** right agent, right instructions, context passed on.

- **Test the verifier:** on outputs you know are wrong.

- **Watch loops and stopping:** step counts and duplicate actions.

- **Re-run after structural changes:** a fix for one model may not help another.

### The answer that sounds right

#### "Every agent passes its own tests"

It sounds like the system must work, but most multi-agent failures happen between agents: lost information, ignored inputs and checks that don't check. Evaluate the hand-offs and the verifier, not just each agent.

## Say it

### Your planner, researcher and writer agents produce a bad report. Which agent failed, and how do you measure it?

#### The interviewer pushes further

Follow-up 1 of 3

The final report is wrong. How do you find which agent failed?

Walk the trace to the first failure, as in single-agent error analysis, and label its mode. Then check whether it was a bad delegation, a bad sub-agent result, or a verifier that missed it.

Follow-up 2 of 3

Why test the verifier separately?

A reviewer agent that approves everything makes the system look checked when it isn't. Feed it known-bad outputs and measure how many it catches.

Follow-up 3 of 3

Can an LLM label multi-agent failures reliably?

With few-shot examples, MAST's judge reached kappa 0.77 against experts, versus 0.58 zero-shot. Validate it on your own traces before trusting it.

I'd grade the end result first, then label failed traces with a taxonomy like MAST, which groups multi-agent failures into system design, misalignment between agents, and task verification, with failure rates of 41 to 87% across seven frameworks. I'd score each hand-off separately from the sub-agent's work, test the verifier on outputs I know are wrong since a verifier that passes everything gives false confidence, and watch for loops and premature stopping. A few-shot LLM judge can label these modes at kappa 0.77 against experts, so labelling can scale once validated.

**Key terms and sources**

How multi-agent systems fail (the MAST taxonomy of 14 failure modes in 3 groups), how to label traces with it, scoring both the delegation and each sub-agent's work, and why verification is the weakest link.

#### Sources

- M. Cemri, M. Z. Pan et al., Why do multi-agent LLM systems fail? (MAST), 2025

- Anthropic, Demystifying evals for AI agents, Jan 2026

- H. Husain and S. Shankar, _Evals for AI Engineers_ (O'Reilly): the Analyze-Measure-Improve lifecycle, error analysis, judges, CI and review

Explanations and examples are ours, built from these sources. Lab numbers are illustrative unless a lab says otherwise. Many recent papers are preprints, and benchmark scores change quickly.
