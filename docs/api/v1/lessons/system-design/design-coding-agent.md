# Design a Background Coding Agent

> Engineers want an agent that makes code changes across thousands of repositories, like migrations and upgrades, and opens pull requests for review. Design it so its changes can be trusted.

- Track: System Design › Developer Tools › Designs
- Type: Design · 25 min
- Page: https://aimlrounds.com/tracks/system-design/design-coding-agent/
- Before this: What Is an Agent? The ReAct Loop (`ai-engineering/what-is-an-agent`), Agent Safety: Permissions, Sandboxing and the Lethal Trifecta (`ai-engineering/agent-safety`)
- Quiz topic: `sdllm`
- Sources checked: 2026-11-05 · Text last changed: 2026-11-20 · Version: 1fa903b148

## Intuition

### The situation

A company has thousands of code repositories. Upgrades and migrations are written as scripts that keep growing, and engineers spend weeks on repetitive changes. Leadership wants an AI agent to make these changes and open pull requests. The interviewer asks:

> Engineers want an agent that makes code changes across thousands of repositories, like migrations and upgrades, and opens pull requests for review. Design it so its changes can be trusted.

#### Ask before designing

- **Tasks:** fleet-wide migrations and upgrades, like moving to a new framework version, or one-off requests from engineers?

- **Scale:** say thousands of repositories with different languages and build setups.

- **Who reviews:** does every change need a human review, and can some merge automatically?

- **Where it runs:** what may the agent access? Network, secrets, other systems?

- **Must never happen:** pushing directly to production, leaking secrets, or a change that passes tests but breaks behaviour.

- **Success metrics:** pull requests merged, share failing CI, changes later reverted, and engineer time saved.

### The idea

Think of a contractor renovating hundreds of identical flats. They get one clear brief, work only inside each flat, and an inspector checks the wiring and plumbing before the owner is called. A second inspector checks they did only what was asked, not a surprise new kitchen.

[Figure: A tested prompt runs per repository. The agent works in a sandbox, verifiers build and test, a judge checks scope, and only then does a PR open.]

_Keep the agent's world small, and check its work before anyone sees it._

### Play

**Try to break it.** Start with no checks. Turn on verifiers, then the judge. Then drag the turns down to 3.

#### Which changes reach a reviewer?

Illustrative, except the judge: in the series, the judge vetoes about a quarter of sessions, and the agent course-corrects about half of those. Other rates are made up.

Start with no checks: many PRs fail CI, and some pass while doing the wrong thing, which is the worst case because **it erodes trust**. Turn on verifiers, and CI failures mostly vanish, but only if the agent has enough turns to fix them. The judge catches the agent being too ambitious: refactoring extra code or disabling a flaky test.

**Now say why:** why is a PR that passes CI but is wrong worse than no PR at all?

## Architecture

### Architecture

#### In one breath

Keep the agent's job narrow and its world small. A task is a **tested, versioned prompt** applied to many repositories. The agent runs in a **sandbox** with only a few tools, and before any pull request opens, **verifiers** run the build, tests and formatters, and an **LLM judge** checks the change stayed within the task. Reuse the existing system for targeting repositories, opening pull requests and getting reviews. The worst failure isn't a missing PR, it's one that **passes CI but is wrong**.

#### From task to pull request

1. **Specify:** an engineer writes a task prompt: the desired end state, ideally as tests, when not to act, and examples. Prompts are versioned and tested on a few repositories first.

2. **Target:** the existing fleet system picks the repositories and starts one job per repository.

3. **Run:** the agent works in a sandboxed container with few tools: read and edit files, a restricted shell, limited Git, and a verify tool.

4. **Verify:** verifiers matching the repository's build system run formatters, the build and tests, and return only the key errors. The agent fixes what fails, within a turn limit.

5. **Judge:** an LLM compares the diff with the original prompt and vetoes changes that wander outside the task.

6. **Open and review:** only then does a pull request open, with a standard commit message, for normal review and merge.

##### Why so few tools?

Every tool is something that can go wrong or be misused. With no network and an allowlist of commands, the agent's mistakes stay inside the sandbox, and its runs are more predictable.

##### Why build knowledge goes into tools

Repositories build in very different ways. Rather than explaining each one in a prompt, a verify tool knows how to build and test any repository, and the agent just calls it.

#### The numbers worth saying out loud

All of these are assumptions for the interview, not figures from a real system.

| Question | Working | Result |
|---|---|---|
| Jobs for one migration | 2,000 repositories | **2,000 agent runs** |
| Tokens per run | 10 turns × 30,000 tokens of context | **about 300,000** |
| Tokens per migration | 2,000 × 300,000 | **about 600 million** |
| Build minutes | 2,000 × 3 verify runs × 5 minutes | **30,000 minutes** |
| Review time saved | 2,000 × 30 minutes of manual work, minus 5 to review | **about 830 hours** |

Builds can cost as much as tokens, so run verifiers selectively and cache dependencies. The real constraint is reviewer attention: batch similar PRs and make each one easy to review.

## In practice

### In practice

#### What every coding-agent design gets asked

- **Writing the task:** describe the end state rather than every step, say when not to act, give examples, and make one change at a time. Too generic and the agent guesses; too specific and it breaks on the first unusual repository.

- **Failure modes, ranked:** no PR is a minor annoyance; a PR failing CI frustrates engineers; a PR that passes CI but is wrong is the most serious, because it erodes trust.

- **Weak tests:** if a repository has little test coverage, verifiers can't catch much, so be more cautious there, or skip it.

- **Safety:** the agent never pushes or changes the remote, has no secrets, and runs with almost no network access. Its commits are clearly labelled.

- **Evaluation:** track merge rate, CI failures, reverts and review comments per task, and evaluate prompts and the judge on held-out repositories before a fleet-wide run.

- **Observability:** log every run and its traces, so a bad pattern can be found and the prompt fixed before it spreads.

##### Rollout

Run a new task on a handful of repositories first and review every result. Then widen in waves, pausing if merge rates drop or reverts appear.

#### What the real system reported

- **Starting point:** an existing fleet framework already ran code changes across all repositories and opened PRs; scripts for complex changes had grown to over 20,000 lines. The agent replaced the scripts, and targeting, PRs, review and merge stayed the same.

- **Scale:** more than 1,500 merged pull requests, hundreds of developers using it, and a time saving of 60–90% versus writing the code by hand. The agent of choice had been used for about 50 migrations.

- **Harness:** a container with limited permissions and almost no access to other systems; a verify tool for formatters, linters and tests; a Git tool that never pushes; a shell with a strict allowlist.

- **Verification:** independent verifiers chosen by what's in the repository, run before any PR opens; then an LLM judge comparing the diff with the prompt. The judge vetoes about a quarter of sessions, and the agent course-corrects about half of those.

- **Honest gaps:** they had yet to evaluate the judge itself, and said they were still choosing prompts and models mostly by intuition.

The company's own figures, from parts 1–3 of the series. We didn't read part 4.

### The answer that sounds right

#### "Tests pass, so the change is safe to merge"

It sounds right, since tests are the safety net. But many repositories have thin coverage, and agents sometimes disable a flaky test or refactor code they weren't asked to touch. Passing CI then proves little. Keep human review, add a judge that checks the change against the task, and be extra careful where tests are weak.

## Say it

### Engineers want an agent that makes code changes across thousands of repositories, like migrations and upgrades, and opens pull requests for review. Design it so its changes can be trusted.

#### The interviewer pushes further

Follow-up 1 of 3

Why not let the agent merge its own changes when tests pass?

Passing tests doesn't prove a change is right, especially where coverage is thin. A wrong change that merges silently does more damage than a slow review. I'd only consider auto-merge for trivial, well-tested change types with a long clean record.

Follow-up 2 of 3

The agent keeps "improving" unrelated code. How do you stop it?

Say in the prompt exactly what to change and what not to touch, and add a judge that compares the diff with the task and vetoes extras. Keep each task to one change, so out-of-scope edits stand out.

Follow-up 3 of 3

How do you know a new prompt is better than the old one?

Run both on the same held-out set of repositories and compare merge rate, CI failures, judge vetoes and review comments. Without that, you're choosing by intuition.

#### The 30-second answer

First I'd clarify the kinds of tasks, how many repositories, who reviews and what the agent may access. A task is a versioned prompt that describes the end state, says when not to act and includes examples, tested on a few repositories first. The existing fleet system targets repositories and runs one job each. The agent works in a sandboxed container with few tools: file edits, a restricted shell, Git that can't push, and a verify tool that knows how to build and test any repository and returns only the key errors. The agent fixes failures within a turn limit. Then an LLM judge compares the diff with the task and vetoes out-of-scope changes. Only then does a pull request open for normal review. The worst failure is a change that passes CI but is wrong, so I'd be careful with repositories that have weak tests, and track merges, CI failures and reverts per task. Rollout goes in waves, pausing if quality drops.

**Key terms and sources**

Based on a music-streaming company's published series: [Spotify's background coding agent, parts 1–3](https://engineering.atspotify.com/2025/11/spotifys-background-coding-agent-part-1) (November–December 2025). The lab's numbers, apart from the judge's veto rate, and the estimate are ours. Uses agents, agent safety and evaluating agents. · checked 5 Nov 2026
