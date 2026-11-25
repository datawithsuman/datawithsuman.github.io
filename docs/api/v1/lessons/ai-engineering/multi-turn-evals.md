# Multi-Turn Chat Evals: Sessions, Simulated Users and Drift

> Your chatbot answers single questions well and falls apart in long conversations. How do you evaluate that?

- Track: AI Engineering › Applied Evals › Lessons
- Type: Concept · 17 min
- Page: https://aimlrounds.com/tracks/ai-engineering/multi-turn-evals/
- Before this: Error Analysis: From Traces to Failure Rates (`ai-engineering/error-analysis`), LLM Judges: Pairwise Preferences and Pass/Fail Checks (`ai-engineering/llm-as-a-judge`)
- Quiz topic: `evals`
- Sources checked: 2026-11-15 · Text last changed: 2026-11-20 · Version: 8ad2d899cf

## Intuition

### The situation

Your shopping assistant scores 92% on a single-question test set. In production, long conversations end with users repeating themselves, and some leave with the wrong product. The interviewer asks:

> Your chatbot answers single questions well and falls apart in long conversations. How do you evaluate that?

#### Why it matters

Laban and colleagues split instructions into pieces revealed over several turns and ran over 200,000 simulated conversations across 15 models. Average performance fell 39% compared with giving the full instruction at once. Single-question tests never see this, and real users rarely state everything up front.

### The idea

Think of a waiter taking a big table's order one person at a time. If they start cooking after the first person speaks, later changes get lost. Judge whether the table got their meals, then find the moment the order went wrong.

[Figure: Three levels. Did the session succeed? Which turn failed? Did it remember?]

_Models lose reliability over turns more than ability._

### Play

**Try to break it.** Switch from all at once to several turns.

#### Same model, one turn or many

How the user gives the instruction

Spread the same instruction over several turns, and the average falls from 90 to 65. The best runs only fall from 95 to 80, while the worst fall to 38: the best-to-worst gap more than doubles. That's the pattern Laban and colleagues found. The model still knows how; it commits early to a wrong guess and doesn't recover. Numbers are illustrative; the shape is from the paper.

**Now say why:** why do the worst runs fall so much further than the best?

## How it works

### How it works

#### In one breath

Start with one pass or fail per **conversation**: did the user get what they came for? Only for failed sessions, walk the turns to find where it went wrong, and check memory: did the bot forget something said earlier? Try to reproduce each failure as a single-turn test; many "multi-turn" bugs aren't. Generate conversations with an LLM playing users with hidden goals, report success by conversation length, and perturb passing conversations (change the goal midway, push back) to test robustness. Research shows models get much less _reliable_ over turns, more than less capable.

#### Three levels, then simulation

##### Session, turn, memory

- **Session:** did the conversation achieve the user's goal? Write it as a rubric, label pass or fail. Start here.

- **Turn:** for failed sessions only, find the first turn that went wrong, and ask the single-turn questions: relevant, correct, right tone?

- **Memory and coherence:** did it keep earlier facts ("my partner hates sci-fi") and stay consistent across sessions where state persists?

##### Isolate the failure

Rebuild the failing turn as a single-turn test with the needed context written in. If it still fails, it's a single-turn problem in disguise; fix it there. If it passes, the problem really is the conversation: context lost, an early guess the bot anchored on, or instructions drifting. A related trick is N−1 testing: replay a real conversation's first N−1 turns and test only the last reply.

##### Simulated users

Have an LLM play the user with a persona and a hidden goal, revealing information gradually. Vary persona and goal to cover the space, and check a sample of simulations, since simulators make mistakes too. Report success rates by conversation length: averages hide that long conversations fail more.

##### Perturbation tests

Take conversations that pass and change one thing: switch the goal midway, make a message vague, or tell the bot it's wrong. A bot that only works on the exact test conversations breaks here.

##### What breaks across turns

In Laban's study, the best runs got only somewhat worse (aptitude fell about 16%), but the gap between best and worst runs more than doubled (unreliability rose about 112%). The causes: answering too early on partial information and then sticking with it, long bloated answers, and leaning on the last turn. So run each conversation several times, and look at the spread, not just the average.

## In practice

### In practice

#### In practice

- **Session-level first:** one pass or fail per conversation against the user's goal.

- **Turn-level only for failures:** find the first turn that went wrong.

- **Reproduce as single-turn:** many multi-turn bugs aren't.

- **Simulate users:** personas with hidden goals; spot-check the simulator.

- **Stratify by length:** report success for short, medium and long conversations.

- **Perturb passing conversations:** goal changes, vagueness, pushback.

- **Repeat runs:** watch the spread, not just the average.

### The answer that sounds right

#### "It scores 92% on our question set, so chat works"

It sounds like good coverage, but single questions give the model everything at once. Real users reveal needs over several turns, where models get much less reliable. Evaluate whole conversations.

## Say it

### Your chatbot answers single questions well and falls apart in long conversations. How do you evaluate that?

#### The interviewer pushes further

Follow-up 1 of 3

Why start at the session level?

It answers the question that matters, did the user get what they needed, with one label per conversation. Turn-level labelling is costly and only needed to diagnose failures.

Follow-up 2 of 3

How do you know your simulated users are realistic?

Read a sample, compare their messages with real logs, and measure how often the simulator itself errs; drop or fix simulated conversations where the user, not the bot, went wrong.

Follow-up 3 of 3

The bot answers the last message well but forgets constraints from turn 2. What's happening?

Over-reliance on the latest turn, or context truncation. Test with N−1 replays and coherence checks, and consider restating key constraints in a running summary.

#### The 30-second answer

I'd start with one pass or fail per conversation against the user's goal, and only for failed sessions go turn by turn to find the first mistake, plus check memory of earlier facts. I'd try to reproduce each failure as a single-turn test, since many aren't really multi-turn. To scale, I'd simulate users with personas and hidden goals, report success by conversation length, and perturb passing conversations by changing the goal or pushing back. Research shows models get much less reliable over turns, so I'd run each conversation several times and watch the spread.

**Key terms and sources**

Evaluating conversations at the session, turn and memory levels; reproducing failures as single-turn tests; simulated users and perturbation tests; and why reliability, not ability, is what drops across turns. · checked 15 Nov 2026

#### Sources

- H. Husain and S. Shankar, _Evals for AI Engineers_ (O'Reilly): the Analyze-Measure-Improve lifecycle, error analysis, judges, CI and review

- [P. Laban, H. Hayashi, Y. Zhou and J. Neville, LLMs get lost in multi-turn conversation, 2025](https://arxiv.org/abs/2505.06120)

- [H. Husain and S. Shankar, AI Evals: everything you need to know (FAQ)](https://hamel.dev/blog/posts/evals-faq/)

- [Anthropic, Demystifying evals for AI agents, Jan 2026](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)

Explanations and examples are ours, built from these sources. Lab numbers are illustrative unless a lab says otherwise. Many recent papers are preprints, and benchmark scores change quickly.
