# Agent Skills and Self-Improving Context

> Your agent needs dozens of procedures, like how to file an expense or write a release note. How do you give it that know-how without filling its context, and can it learn new ones?

- Track: AI Engineering › Agentic AI › Lessons
- Type: Concept · 18 min
- Page: https://aimlrounds.com/tracks/ai-engineering/agent-skills-and-self-improving-context/
- Before this: Memory and Context Engineering (`ai-engineering/memory-and-context-engineering`)
- Quiz topic: `agents`

## Intuition

### The situation

Your agent needs 80 procedures, from filing expenses to writing release notes. Someone pastes them all into the system prompt, and calls get slow and expensive. Another wants the agent to write its own lessons. The interviewer asks:

> Your agent needs dozens of procedures, like how to file an expense or write a release note. How do you give it that know-how without filling its context, and can it learn new ones?

#### Why it matters

Prompts that try to cover every procedure grow huge and contradictory. Fine-tuning procedures in is slow. Skills and evolving playbooks keep know-how as editable text that loads when needed. Interviewers ask how agents gain capabilities without retraining. For general memory design, see Memory and Context Engineering.

### The idea

Think of a library. You don't carry every book. You read the catalogue, then fetch the one book you need. And when you learn something, you add a note to the right page, rather than rewriting the whole library.

[Figure: Three ideas. Load descriptions, then details. Keep project instructions in AGENTS.md. Grow a playbook in small edits.]

_Know-how loads when it's needed._

### Play

**Try to break it.** Load 50 skills in full. Then switch to descriptions only, and raise the count.

#### Fifty skills, one context

Illustrative: 100 tokens of metadata and 3,000 tokens of instructions per skill, one skill in use at a time, input at $3 per million tokens, before any caching.

Loading 50 skills in full puts 150,000 tokens in every call, three quarters of a 200,000-token context, before the task even starts. With descriptions only and one skill in use, it's 8,000. At 200 skills, loading everything doesn't fit at all, while descriptions plus the skill in use take 23,000 tokens. That's why skills scale where giant prompts don't. The descriptions must be good, though: the agent picks skills by reading them, as it picks tools.

**Now say why:** why does loading on demand scale when a big prompt doesn't?

## How it works

### How it works

#### In one breath

A **skill** is a folder with a `SKILL.md` file: a name, a description and instructions, plus optional scripts and reference files. The agent loads only each skill's **description** at startup, about 100 tokens, and reads the full instructions only when a task needs them. So 50 skills cost about 5,000 tokens, not 150,000. Anthropic made skills an open standard in Dec 2025. Agents can also **improve their own context**: ACE keeps a playbook of lessons from past runs, updated in small pieces, and gained 10.6% on agent tasks. Rewriting the whole playbook at once can cause **context collapse**, and lessons learned without a reliable signal can make things worse.

#### How it works

##### Skills and progressive disclosure

- **Metadata:** the name and description, about 100 tokens per skill, always in context so the agent knows what exists.

- **Instructions:** the body of SKILL.md, recommended under 5,000 tokens, loaded when the skill is chosen.

- **Resources:** scripts, templates and references, read only when needed. Scripts can run without their code entering the context.

The format is an open standard, with the name up to 64 characters and the description up to 1,024. It's now hosted by the Agentic AI Foundation, and can be served over MCP.

##### AGENTS.md

A plain file in a repository telling coding agents how to build, test and follow the project's conventions, like a README for agents. It's also an Agentic AI Foundation project.

##### Agents that edit their own context

ACE, at ICLR 2026, treats context as an evolving **playbook**. A generator does the task, a reflector draws lessons from what worked and what failed, and a curator adds them as small, itemised entries, each with counters for how often it helped or hurt. On AppWorld it lifted a ReAct agent by up to 17.1%, using only execution feedback, and matched the top production agent on the leaderboard with a smaller open model. It also cut adaptation time by 82.3% against GEPA.

##### Two failure modes

- **Context collapse:** when a model rewrites its whole playbook each time, it can suddenly compress it. In one ACE case, an 18,282-token playbook scoring 66.7% became 122 tokens scoring 57.1%, below the 63.7% with no playbook.

- **Bad signals:** without reliable feedback, such as labels or test results, self-written lessons can mislead. ACE and Dynamic Cheatsheet both got worse on some finance tasks without labels.

#### The maths

$$ {T_{\text{context}}} = {n}\cdot{m} + {k}\cdot{s} $$

Progressive disclosure. Loading everything instead would cost n × s on every call.

- **tokens spent on skills**: What sits in context on every call.

- **installed skills**: How many the agent knows about.

- **metadata per skill**: About 100 tokens: name and description.

- **skills in use**: Usually one or two at a time.

- **full instructions**: Up to about 5,000 tokens each, loaded only when used.

## In practice

### In practice

#### In practice

- **Write sharp descriptions:** say what the skill does and when to use it, since selection depends on them.

- **Keep SKILL.md short:** under about 500 lines, with details in reference files.

- **Review skills like code:** a skill can run scripts, so a malicious one is a supply-chain risk.

- **Update playbooks in small pieces:** add and edit entries, de-duplicate, and never let a model rewrite the whole thing at once.

- **Learn only from reliable signals:** tests, labels or tool results, and check lessons on held-out tasks.

- **Cache the stable part:** ACE served 91.8% of input tokens from the prompt cache, cutting billed input cost by 82.6%.

### The answer that sounds right

#### "Put every procedure in the system prompt"

It sounds thorough, but 80 procedures can fill most of the context on every call, slowing and confusing the agent. Load short descriptions, and fetch the full skill only when a task needs it.

## Say it

### Your agent needs dozens of procedures, like how to file an expense or write a release note. How do you give it that know-how without filling its context, and can it learn new ones?

#### The interviewer pushes further

Follow-up 1 of 3

Skills or MCP tools?

Tools are actions the agent calls. Skills are know-how: instructions, and sometimes scripts, for doing a task well. A skill often tells the agent how to use certain tools.

Follow-up 2 of 3

Why are itemised updates safer than rewriting the playbook?

Small edits keep everything else intact. A full rewrite can silently drop most of it, as in ACE's case where 18,282 tokens collapsed to 122.

Follow-up 3 of 3

Can an agent safely write its own skills?

Only with review and tests. Self-written instructions can encode mistakes, and scripts can do damage, so treat them like code contributions.

#### The 30-second answer

A skill is a folder with a SKILL.md: name, description and instructions, plus optional scripts and references. The agent keeps only descriptions in context, about 100 tokens each, and loads the full instructions when a task needs them, so 50 skills cost thousands of tokens, not 150,000. AGENTS.md gives coding agents project instructions. Agents can also improve their own context: ACE keeps an itemised playbook of lessons from execution feedback and gained about 10% on agent tasks. The risks are context collapse, when a model rewrites the whole playbook and loses it, and learning wrong lessons without reliable feedback.

**Key terms and sources**

Agent Skills as packaged know-how with progressive disclosure, AGENTS.md project instructions, and agents that improve by editing their own context: ACE playbooks, context collapse, and when self-written lessons help or hurt. · checked 7 Nov 2026

#### Sources

- [Agent Skills specification](https://agentskills.io/specification)

- [Anthropic, Equipping agents for the real world with Agent Skills, Oct 2025](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

- [Zhang et al., Agentic Context Engineering (ACE), ICLR 2026](https://arxiv.org/abs/2510.04618)

- [Suzgun et al., Dynamic Cheatsheet](https://arxiv.org/abs/2504.07952)

- [AGENTS.md](https://agents.md/)

- [Hu et al., Memory in the Age of AI Agents (survey)](https://arxiv.org/abs/2512.13564)

Explanations are ours, built from these sources. Lab numbers are illustrative unless a lab says otherwise. Many recent papers are preprints, and provider policies change.
