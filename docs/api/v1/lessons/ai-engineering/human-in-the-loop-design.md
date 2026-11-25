# Human-in-the-Loop Design for Agents

> Your agent can issue refunds, send emails and change code. Which actions should wait for a person, how should approval work, and why do approvals often fail to catch problems?

- Track: AI Engineering › Agentic AI › Lessons
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/ai-engineering/human-in-the-loop-design/
- Before this: Agent Safety: Permissions, Sandboxing and the Lethal Trifecta (`ai-engineering/agent-safety`), Agent Frameworks and Harnesses: Graphs, State and Middleware (`ai-engineering/agent-frameworks-and-harnesses`)
- Quiz topic: `agents`
- Sources checked: 2026-11-07 · Text last changed: 2026-11-20 · Version: 72a52edd1e

## Intuition

### The situation

Your agent issues refunds, sends emails and edits code, and asks for approval before every action. Reviewers approve almost everything within seconds, and a destructive command slipped through last week. The interviewer asks:

> Your agent can issue refunds, send emails and change code. Which actions should wait for a person, how should approval work, and why do approvals often fail to catch problems?

#### Why it matters

Human approval is the standard answer to "what if the agent does something bad?" But approvals that are too frequent get rubber-stamped, approvals that show too little get fooled, and approvals the model decides to request get skipped. Interviewers ask how you'd design oversight that actually works. This lesson pulls together ideas from Agent Safety and Agent Frameworks and Harnesses.

### The idea

Think of a security guard at a door who must check every single person, all day. By afternoon, they wave everyone through. Put the guard only at the vault, lock the other doors, and make sure the guard sees exactly who is going in.

[Figure: Three principles. Ask rarely, by stakes. Contain instead of prompting. Bind each approval to the exact action.]

_Approval only works if people actually look._

### Play

**Try to break it.** Approve every action. Then approve only high-impact actions, then add a classifier on writes.

#### Where to spend human attention

Illustrative: 1,000 actions a day, of which 800 harmless reads, 150 low-risk writes (1% harmful) and 50 high-impact actions (3% harmful). A person's catch rate is assumed to fall from 90% at 20 prompts a day to 30% at 1,000. The classifier uses Anthropic's published auto mode rates: it misses 17% of bad actions and wrongly blocks 0.4% of safe ones, which go to a person.

Approving **every action** means 1,000 prompts a day. Reviewers stop reading, catch only 30%, and 2.1 harmful actions still run each day. Approving **all writes** cuts prompts to 200 and harm to 0.63. Approving **high-impact only** keeps reviewers sharp at 88%, but every harmful low-risk write now runs: 1.68 a day. Sending high-impact actions to people and checking writes with a **classifier** gives about 52 prompts and 0.58 harmful actions a day, the best of the four. Fewer, better-targeted prompts beat more prompts.

**Now say why:** why can fewer prompts catch more harm?

## How it works

### How it works

#### In one breath

A person approving an agent's actions is only a safeguard if they **look**. Anthropic found users accepted about **93%** of permission prompts, and in a 2026 study people missed most silent defects in an agent's code while feeling confident. So ask rarely and well: require approval by **stakes, reversibility and who sees the result**, enforced in code rather than left to the model, which asks far less when it's acting than when it's judging. Reduce prompts with **containment**: a sandbox cut Claude Code's prompts by 84%. Show the **complete action**, tie the approval to exactly that action, and fail safe when nobody answers.

#### Designing oversight

##### Which actions need a person

- **Stakes:** money, data, people affected. A $5 refund isn't a $5,000 one.

- **Reversibility:** moving a file to the bin can be undone, deleting it can't.

- **Who sees it:** anything sent outside, such as emails, posts or payments.

- **Scope:** whether the user actually asked for this action.

- **The Rule of Two:** if a session reads untrusted input, touches sensitive data and can act externally, a person or reliable check must approve.

Don't leave this to the model. DelegationBench found models that chose to ask in 47.5% of judged cases asked in only 4.2% when actually acting with tools. With explicit written rules, though, models followed them 97 to 100% of the time. Encode the rules in the harness.

##### Levels of autonomy

An agent can suggest and wait, act unless vetoed, or act and report. Choose per action type, not per agent.

##### Approval patterns

- **Approve, edit or reject:** LangChain's middleware offers these per tool call. Its docs warn not to deny a side-effecting tool with a plain reply, because the agent treats that as a successful result.

- **Pause and resume:** the run saves its state, waits minutes or days, and resumes on the decision. OpenAI's Agents SDK returns interruptions plus resumable state, and LangGraph re-runs the paused node from its start.

- **Confirmation inside tools:** Google ADK lets a tool require confirmation, always or above a threshold.

##### Approval fatigue, and containment

The more prompts people see, the less they read each one. Anthropic's answer was to supervise what the agent is _able_ to do: a sandbox with file system and network limits cut prompts by 84%. Its auto mode then sends the remaining middle-ground actions to a model-based check, which wrongly blocked 0.4% of safe actions and let through about 17% of overeager ones, so it's not a replacement for human review on high-stakes systems. After 3 denials in a row, or 20 in total, it stops and hands back to a person.

##### Tie the approval to the action

A 2026 study showed approvals being reused for a different action, either because the screen showed only part of a command, or because the pending action was changed after approval. It reproduced this in several released agent products. Show the complete action, store a fingerprint of exactly what was approved, and compare it again just before running.

##### Help reviewers actually check

In a study of 36 people overseeing a coding agent, silent defects were caught only 28% of the time in the first round and 51% in the second, and 79% of missed defects were rated with high confidence. Reviewers who caught defects spent nearly twice as long. Show diffs, what the tests cover and what they don't, and ask for task-specific checks on high-stakes approvals.

#### The maths

$$ {\text{harm per day}} = \sum_{\text{tiers}} {n_t}\,{b_t}\,\big(1 - {c_t}\big) $$

The design question is where to spend scarce human attention: on the tier where catching a harmful action matters most.

- **harmful actions that run**: What gets through all the checks.

- **actions in each tier**: Reads, low-risk writes, high-impact actions.

- **share that’s harmful**: Usually tiny, but not zero.

- **chance it’s caught**: By a person, a classifier or containment. A person’s catch rate falls as prompts pile up.

## In practice

### In practice

#### In practice

- **Write an approval policy:** list action types by stakes, reversibility and visibility, and enforce it in the harness.

- **Contain first, prompt second:** sandboxes, scoped credentials and limits in code remove most prompts.

- **Make prompts worth reading:** show the complete action, its effect, and what's unusual about it.

- **Bind and re-check:** fingerprint the approved action, and refuse to run anything different.

- **Plan for silence:** expiry, a backup approver, and fail closed when review times out.

- **Measure oversight:** approval rates near 100% and very fast approvals are warning signs.

### The answer that sounds right

#### "Just make the agent ask before everything"

It sounds safest, but people stop reading when every action needs approval, and real problems slip through. Ask only for high-stakes actions, contain the rest, and make each prompt show exactly what will run.

## Say it

### Your agent can issue refunds, send emails and change code. Which actions should wait for a person, how should approval work, and why do approvals often fail to catch problems?

#### The interviewer pushes further

Follow-up 1 of 3

Why not let the model decide when to ask?

Because its judgement and its behaviour differ: in one benchmark, a model that would ask in 47.5% of judged cases asked in 4.2% when acting. Explicit rules in the harness are followed far more reliably.

Follow-up 2 of 3

What's wrong with approving every action?

Reviewers stop reading. Approval rates approach 100%, and real problems slip through. Fewer, higher-stakes prompts get real attention.

Follow-up 3 of 3

What should an approval screen show?

The complete action and its arguments, its effect, who it reaches, whether it can be undone, and what's unusual compared with normal behaviour.

#### The 30-second answer

Approval only helps if people look, and they mostly don't: users accepted about 93% of prompts in Anthropic's data. So I'd require approval by stakes, reversibility and external visibility, enforced in the harness, because models ask far less when acting than when judging. I'd cut prompts with containment, like sandboxes and scoped credentials, which removed 84% of prompts in one case, and use a checked classifier for the middle ground. Each prompt shows the complete action, the approval is bound to exactly that action and re-checked before it runs, and review fails closed if nobody answers.

**Key terms and sources**

Deciding which agent actions need a person, approval patterns (approve, edit, reject), levels of autonomy, approval fatigue, containment instead of prompts, tying each approval to the exact action, and what makes a reviewer actually catch mistakes. · checked 7 Nov 2026

#### Sources

- [Anthropic, Beyond permission prompts: Claude Code sandboxing, Oct 2025](https://www.anthropic.com/engineering/claude-code-sandboxing)

- [Anthropic, How we built Claude Code auto mode, Mar 2026](https://www.anthropic.com/engineering/claude-code-auto-mode)

- [Anthropic, How we contain Claude across products, May 2026](https://www.anthropic.com/engineering/how-we-contain-claude)

- [OpenAI Agents SDK, guardrails and human review](https://developers.openai.com/api/docs/guides/agents/guardrails-approvals)

- [LangChain, human-in-the-loop middleware](https://docs.langchain.com/oss/python/langchain/human-in-the-loop)

- [Google ADK, action confirmations](https://adk.dev/tools-custom/confirmation/)

- [Pochampally, DelegationBench: when AI agents should ask before acting](https://arxiv.org/abs/2610.05532)

- [Arun Kumar, Loopjacking: hijacking human-in-the-loop approval](https://arxiv.org/abs/2609.21081)

- [Dissanayake et al., Looks Fine to Me: understanding oversight in agentic interactions](https://arxiv.org/abs/2610.27801)

Explanations are ours, built from these sources. Lab numbers are illustrative unless a lab says otherwise. Many recent papers are preprints, and provider policies change.
