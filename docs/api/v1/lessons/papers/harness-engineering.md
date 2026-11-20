# Harness Engineering

> What is actually inside a coding agent?

- Track: Papers Explained › Agents and tool use
- Type: Paper · 25 min
- Page: https://aimlrounds.com/tracks/papers/harness-engineering/
- Before this: What Is an Agent? The ReAct Loop (`ai-engineering/what-is-an-agent`)
- Related: Context Language Models (`papers/context-language-models`)

## Gist

### The paper

Barbaste, Darrigol, Vu, Wiltberger · Inclusive Brains, Wavestone AI Lab · arXiv [2609.00006](https://arxiv.org/abs/2609.00006) · July 2026 · 9 sources, checked 27 Oct 2026

An agent is a model plus a harness, and the harness is everything except the model. The authors read the source code of eleven production coding agents (Claude Code, Codex CLI, Gemini CLI, Mistral Vibe, OpenHands, Aider, Mini-SWE-Agent, Hermes, Pi, OpenCode, OpenClaw) and found that every one of them is built from the same seven subsystems. They also found two things none of them use: agent frameworks and vector RAG over code. After this you can draw a harness from memory, and explain how real agents handle loops, context, tools, safety, sub-agents and extensions.

### The problem

#### One task, followed through every part

you, in the terminal

"The tests in `test_invoice.py` are failing. Fix it."

A real coding agent has to find the file, read it, run the tests, edit the code, run the tests again, and stop. The Method tab shows which part of the harness handles which step.

#### The model can write the fix. It cannot run anything.

A language model takes text in and gives text out. It can suggest the fix for `test_invoice.py`, but on its own it cannot open the file, run pytest, or decide whether it is done. Everything that turns its text into actions is the harness: "the runtime that couples an LLM to the world—its loop, its tools, its context, its safety controls, its orchestration, and its extension surfaces" [p. 3](https://arxiv.org/pdf/2609.00006#page=3).

1. On its own, the model only produces text. It can describe the fix to `test_invoice.py`, but nothing on disk changes.

2. Wrap the same model in a harness: a program that runs around it.

3. The harness gives it hands: it reads files, runs tests, applies edits, and decides when to stop.

4. That is the paper's one-line definition. The model supplies the intelligence; the harness turns it into work.

By mid-2026 every major AI lab shipped one of these, and the term "harness engineering" was barely five months old (first used by Mitchell Hashimoto, then defined by LangChain's Vivek Trivedy in February 2026) [p. 3](https://arxiv.org/pdf/2609.00006#page=3). What was missing was a reference: a description, from real source code, of what a harness is made of. That is this paper. It reads eleven production harnesses at source level and does not benchmark or rank them; it describes how they are built [p. 1](https://arxiv.org/pdf/2609.00006#page=1).

### The idea

Think of an engine on a workbench. It has all the power, but it goes nowhere until you build a car around it, with steering, brakes and a fuel gauge. The model is the engine. The harness is everything else, and this paper opens up eleven real cars to see how they are built.

[Figure: The model sits in the centre. Seven parts surround it: agent loop, LLM integration, tools, memory and context, safety, orchestration and extensibility.]

_The paper's seven subsystems around the model. Every system in the study takes a position on all seven._

### Play

**Try it.** Your agent keeps running the same test without changing anything. Drag the slider to repeat the call, and see when each real agent steps in.

Rules from §6.2 and Table 5 [p. 15–17](https://arxiv.org/pdf/2609.00006#page=15). Simplified: real detectors also look at errors, alternating patterns and output chunks.

**Notice:** some production agents never step in at all. The paper still calls them production-quality, and that's why it warns against over-engineering stuck detection.

## Method

### Method

#### At the core: ask the model, run what it asks for, repeat

Every system in the study runs a variation of the ReAct loop: the model thinks, asks for an action, the harness runs it, and the result goes back into the conversation [p. 13](https://arxiv.org/pdf/2609.00006#page=13). The smallest real example is Mini-SWE-Agent, whose loop fits on one screen. Step through it with our task.

```
def run(self, task):
 self.add_messages(system_prompt)
 self.add_messages(user_prompt(task))
 while True:
 result = self.step()
 if result.role == "exit":
 return result
def query(self):
 self.check_limits()
 msg = self.model.query(self.messages)
 self.add_messages(msg)
def execute_actions(self):
 for action in msg["extra"]["actions"]:
 obs = self.env.execute(action) # subprocess.run()
 self.add_messages(observation(obs))
```

1. Start: a system prompt and your task ("tests in test_invoice.py are failing") become the first two messages.

2. Then loop forever. Each turn is one call to step().

3. Ask the model, after checking the step and cost limits. It replies with a thought and one bash command, say `pytest test_invoice.py`.

4. Run that command in a fresh subprocess. Every action is independent; there is no long-lived shell.

5. Append the output (the failing test's traceback) to the message list. The list only grows.

6. Repeat until the model replies with an exit. That is the whole agent.

Condensed from the paper's Listing 1 [p. 14](https://arxiv.org/pdf/2609.00006#page=14); the project README describes "just some 100 lines of python for the agent class", bash as the only tool, and a completely linear history [repo](https://github.com/SWE-agent/mini-swe-agent).

#### A 100-line loop scores like the big ones. So why are the big ones huge?

Mini-SWE-Agent reports 74%+ on SWE-bench Verified, in the same range as systems three orders of magnitude larger [p. 5](https://arxiv.org/pdf/2609.00006#page=5) (self-reported, different models and dates, so not a clean comparison). The paper's first observation: **loop sophistication does not predict benchmark performance** [Obs. 1, p. 12](https://arxiv.org/pdf/2609.00006#page=12). So is the rest of a production harness wasted code?

1. The minimal loop solves benchmark tasks surprisingly well.

2. But on a long real session the history grows past the context window, and nothing compresses it.

3. It will run any command the model writes, with your permissions.

4. It has no stuck detection beyond simple caps, so a model repeating itself burns money.

5. And it has nothing for teams: no extension points, no IDE, no sub-agents.

6. The paper's answer: production code goes into "safety, user experience, extensibility—and increasingly clients and transport", which no benchmark measures (p. 12).

##### The resolution

Production systems "invest in scaffolding not because models need it for task completion, but because users need it for safety, reliability, and workflow integration" [p. 58](https://arxiv.org/pdf/2609.00006#page=58). Roughly three-fifths of OpenCode's non-test source is clients (TUI, web, desktop, SDK), not the harness proper [p. 12](https://arxiv.org/pdf/2609.00006#page=12).

#### Every harness takes a position on the same seven parts

From the 100-line baseline to the million-line Codex, every system "must take a position on the same seven subsystems … even when that position is deliberate absence" [p. 4](https://arxiv.org/pdf/2609.00006#page=4). For each, the paper records the smallest and the largest version found.

$$ {\text{Agent}} \;=\; {\text{Model}} \;+\; {\text{Harness}} $$

The paper's definition, popularized by Trivedy's LangChain series [p. 3](https://arxiv.org/pdf/2609.00006#page=3) · hover a term.

- **what you use**: The agent: the thing you type the task into, e.g. Claude Code or Codex.

- **the intelligence**: The language model, which only reads text and writes text.

- **everything else**: The harness: loop, model integration, tools, memory, safety, orchestration and extensions, plus the interface you drive it through.

1. **Agent loop**: alternates model calls with actions; owns stopping and recovery. Smallest: a `while` over one bash tool. Largest: OpenHands' event-sourced conversation with parallel action batches.

2. **LLM integration**: speaks the provider's API, assembles the prompt, manages caching and thinking. Smallest: one LiteLLM call. Largest: Hermes with five owned transports and 29 provider profiles.

3. **Tools and actions**: what the agent can do, file editing above all. Smallest: bash only. Largest: Claude Code's 43 typed tools with deferred loading.

4. **Memory and context**: rations the context window and keeps knowledge across turns and sessions. Smallest: an unbounded message list. Largest: Codex's agent-maintained cross-session memory.

5. **Safety and permissions**: decides what runs, what asks, what is forbidden. Smallest: cost and step limits. Largest: Codex's policy rules, LLM reviewer and three-OS sandbox.

6. **Orchestration**: spawns and coordinates sub-agents. Smallest: none (Aider). Largest: Claude Code's recursive composition.

7. **Extensibility**: lets users add capability through config, hooks, skills, plugins and MCP. Smallest: Python protocols. Largest: Pi's everything-is-an-extension runtime and Codex's plugin marketplace.

Minimal and maximal forms from Table 1 [p. 5](https://arxiv.org/pdf/2609.00006#page=5). Chapters 6–12 take them one at a time.

#### The hard part of a loop is knowing when it is stuck

The paper finds three loop shapes [p. 13](https://arxiv.org/pdf/2609.00006#page=13): the plain **action–observation** loop (nine systems), the **reflection** loop (Aider lints and tests after each edit and re-asks the model, up to 3 times), and a **coordinator–worker** overlay where a lead agent dispatches workers (Claude Code, Codex; configuration-gated in Hermes).

Suppose our agent keeps running `pytest test_invoice.py` without changing anything. Each system reacts differently, and you can try that in the Play section of the Gist tab.

##### What the paper recommends

Start with a linear `while` loop; move to a middleware pipeline (Mistral Vibe's design, where turn limits, cost caps and compaction are pluggable policies) only once you have three or more independent turn policies. Ship the cheap caps (they "cost a dozen lines"), but do not over-engineer stuck detection: Claude Code and Codex ship none and are production-quality [Recs. 1, 18](https://arxiv.org/pdf/2609.00006#page=70).

#### Split the prompt so most of it never changes

Every turn re-sends the system prompt. Providers can cache a prompt prefix that is byte-identical to last time, so harnesses arrange the prompt around that. Claude Code splits its dozen-plus sections at a `SYSTEM_PROMPT_DYNAMIC_BOUNDARY`: identity, rules, tool guidance and tone go before it and stay cached; session guidance, memory, environment and MCP instructions go after it and are recomputed each turn [p. 21](https://arxiv.org/pdf/2609.00006#page=21). OpenHands arrived at the same static/dynamic split independently.

1. Most of the system prompt is the same on every turn: who the agent is, its rules, how to use tools.

2. Claude Code puts a boundary after that part. Everything that changes per turn goes after it.

3. Because the prefix is byte-identical, the provider's prompt cache serves it instead of re-processing it.

4. Sub-agents are forked with the parent's exact rendered prompt, so they reuse the cache too.

##### Try it: tokens the model must process

Illustrative model of the system prompt only (conversation history is cached separately). Real savings depend on the provider's cache rules and expiry.

##### Coupling to one provider buys the update loop

The paper's Observation 2: provider tricks like caching, thinking budgets and model-specific prompts are not exclusive to single-provider harnesses; multi-provider ones (Hermes, Pi, OpenCode) reach them by paying for per-provider code. What only the vendor keeps is **server-side co-evolution**: Codex downloads its per-model prompts from a catalog endpoint, so OpenAI can re-tune the harness on model-release day without shipping a client [p. 19](https://arxiv.org/pdf/2609.00006#page=19).

#### How many tools, and how to edit a file safely

##### Built-in tools or edit formats per system (July 2026)

Figure 3 [p. 27](https://arxiv.org/pdf/2609.00006#page=27). Aider's 13 are edit formats; Pi builds 7 and exposes 4 by default; OpenClaw's count includes messaging channels.

##### Deferred tool loading

Every tool's schema costs prompt space. Claude Code marks most of its 43 tools as deferred: they stay out of the prompt until the model searches for them with a `ToolSearch` tool, which cuts the initial prompt by about 40% [Table 18, p. 77](https://arxiv.org/pdf/2609.00006#page=77). Codex and Hermes later added the same idea with BM25 search. The paper recommends it once you pass about 15 tools [Rec. 4](https://arxiv.org/pdf/2609.00006#page=68).

Illustrative token counts. The paper's measured figure for Claude Code's whole prompt is about 40% smaller.

##### File editing: the most consequential tool

The eleven systems use eight different editing strategies [Table 7, p. 28](https://arxiv.org/pdf/2609.00006#page=28). For our task, the agent must change one line in `invoice.py`:

| Strategy | Who | How the edit is located |
|---|---|---|
| Exact unique string | Claude Code, Mistral Vibe | The old text must appear exactly once in the file, or the tool errors |
| Patch format | Codex | A custom `*** Begin Patch` diff language |
| Fuzzy cascade | OpenCode, Hermes | Nine fallbacks from exact to whitespace-tolerant to similarity matching |
| LLM repair | Gemini CLI | If matching fails, a model sub-call fixes the old/new pair |
| Per-model formats | Aider (13 formats), OpenCode | Pick the format the current model handles best |
| Just bash | Mini-SWE-Agent | `sed` through the shell |

##### The trend

Mistral Vibe deleted its fuzzy search-replace tool between April and July 2026 and moved to Claude Code's exact-match contract, "evidence that stronger models shift the optimum from tool-side drift tolerance toward strict contracts" [p. 29](https://arxiv.org/pdf/2609.00006#page=29). Recommendation 5: exact matching for frontier models, a fuzzy cascade for weaker ones, and never line numbers.

#### When the conversation outgrows the window, summarize the old part

Long debugging sessions eventually overflow the context window. Four strategies appear [Fig. 4, p. 31](https://arxiv.org/pdf/2609.00006#page=31): keep everything (Mini-SWE-Agent), recursive summarization (Aider), pluggable condensers (OpenHands), and **threshold compaction**, used by seven of the eleven, including all four provider-native systems.

$$ {n_{\text{context}}} \;\ge\; {W} - {B} \;\;\Longrightarrow\;\; {\text{summarize the old, keep the recent}} $$

Claude Code's trigger (`AUTOCOMPACT_BUFFER_TOKENS = 13 000`), §9.5 [p. 32](https://arxiv.org/pdf/2609.00006#page=32). Gemini CLI fires at 50% of the window instead; Pi at W − 16,384.

- **tokens in context**: How many tokens the conversation currently occupies.

- **window size**: The model’s usable context window.

- **safety buffer**: Room kept free for the next response. Claude Code uses 13,000 tokens.

- **then compact**: When the condition is true, an LLM summarizes the older messages, recent ones stay verbatim, and the summary replaces the history.

Trigger rules from §9.5 [p. 32–33](https://arxiv.org/pdf/2609.00006#page=32); tokens per turn is illustrative.

##### The new frontier: who writes long-term memory?

Compaction has converged. What differs now is cross-session memory, and the paper's Observation 5 sorts it by who writes it and who reviews it [p. 34](https://arxiv.org/pdf/2609.00006#page=34):

| Model | Example | How it works |
|---|---|---|
| Agent-maintained | Codex | A sandboxed sub-agent extracts memories from past sessions and consolidates them into a git-tracked folder |
| Human-gated | Gemini CLI | A sub-agent proposes memory patches into an inbox you review with `/memory` |
| Model-direct, bounded | Hermes, Claude Code, OpenHands | The model edits small Markdown files (Hermes caps MEMORY.md at 2,200 characters) |
| Pre-turn recall | OpenClaw | A memory sub-agent runs before every reply |

And for the repository itself, every system auto-discovers Markdown context files (CLAUDE.md, AGENTS.md, GEMINI.md) from the project up to the root, often loading nested ones just in time when a tool touches that folder (§9.7).

#### Every command passes through checks before it runs

Safety is where the systems differ most. Claude Code uses three layers: static hook rules, then an LLM permission classifier, then an interactive dialog [Fig. 5, p. 35](https://arxiv.org/pdf/2609.00006#page=35). Codex grew to four [p. 36](https://arxiv.org/pdf/2609.00006#page=36). Follow one command from our task through Codex's stack.

1. After fixing the bug, the model asks to run `git push`.

2. Layer 1, execution policy written in Starlark: `git status` is allowed outright; `git push` is not matched by the allow rule, so it needs approval. Rules carry their own test examples, checked when the policy loads.

3. Layer 2, lifecycle hooks: your own scripts can block or allow. Codex copied Claude Code's hook names almost verbatim.

4. Layer 3, Guardian: when approval would be needed, an LLM reviewer re-assesses the exact action against a policy and fails closed on timeout.

5. Layer 4, the OS sandbox: even approved commands run with a read-only filesystem outside writable roots and network isolation (Bubblewrap on Linux, Seatbelt on macOS, restricted tokens on Windows); network rules can open specific hosts such as *.github.com.

6. Cheap deterministic checks first, then a model's judgment, then the operating system as the backstop.

##### Try it: what would stop each command?

Illustrative stack built from the paper's examples (Codex's `git status` rule and GitHub network rule, Hermes' hardline floor, OpenCode's `.env` ask); no single harness has exactly these layers [p. 36–38](https://arxiv.org/pdf/2609.00006#page=36).

##### Sandboxing is a choice, not a side effect of size

Hermes, about 642K lines, has zero OS-level isolation and spends its safety budget on scanning content for prompt injection instead; OpenCode is policy-only. Hermes' floor of twelve hardline patterns (`rm -rf /`, `mkfs`, fork bombs…) survives even `--yolo` mode, and the yolo flag is frozen at start-up so an injected skill cannot flip it [Obs. 6, p. 37–38](https://arxiv.org/pdf/2609.00006#page=37).

#### Hand slices of the task to sub-agents with their own context

Nine of the eleven systems can spawn sub-agents, in six patterns from sequential delegation to recursive composition [p. 39](https://arxiv.org/pdf/2609.00006#page=39). Claude Code's coordinator mode is the most structured.

1. A lead agent receives the task. It mostly plans and delegates.

2. A research worker explores the codebase to find why test_invoice.py fails. Its long search output stays in its own context.

3. After the coordinator synthesizes the findings, an implementation worker makes the edit.

4. A verification worker runs the tests.

5. Each worker gets a forked context and only 16 allowed tools, and reports back in a `<task-notification>` block (p. 42).

6. The workflow is fixed: research, synthesis, implementation, verification.

##### Why not always use sub-agents?

Anthropic's multi-agent case study reported about 15× the tokens of a single chat [p. 7](https://arxiv.org/pdf/2609.00006#page=7), and warns that coding has fewer truly parallel tasks than research. The paper finds sub-agents are mostly used for breadth-first exploration, not parallel implementation, and recommends staying single-agent until you can point to such a phase [Rec. 12](https://arxiv.org/pdf/2609.00006#page=69).

#### Skills overtook MCP

Two standards compete. **MCP** is a wire protocol: the agent talks to a separately running server that exposes tools. **Skills** are a file convention: a folder with a `SKILL.md` (instructions plus YAML front matter) that the agent reads when relevant. By July 2026 skills led 9 to 8, because Pi adopted skills while rejecting MCP ("build CLI tools with READMEs") [Obs. 8, p. 51](https://arxiv.org/pdf/2609.00006#page=51).

##### Adoption across the 11 systems

§12.4–12.5 and §14.1 [p. 47–59](https://arxiv.org/pdf/2609.00006#page=47).

Eight of the nine skill adopters load only each skill's name and description up front and fetch the body on demand, the same trick as deferred tools. Some skills activate only when the agent touches matching files (Claude Code's `paths`, OpenHands' PathTrigger). And skills now have a supply chain: registries in four systems, trust tiers and quarantine in Hermes, and the first skills written by agents themselves.

##### Recommendation 14

Use skills for capability templates (workflows, domain knowledge, recipes) and MCP for external integrations (Slack, databases, internal APIs), in that order of priority. Treat third-party skills like packages: scan and quarantine them.

## Results

### What they found

#### No agent frameworks. No vector RAG over code.

The authors grepped about four million lines of Python, TypeScript and Rust for imports of LangChain, LangGraph, LlamaIndex, AutoGen, CrewAI, Pydantic AI, Genkit, Google ADK, Semantic Kernel and more. **No production agent code path imports any of them.** Gemini CLI uses neither of Google's own frameworks [p. 53](https://arxiv.org/pdf/2609.00006#page=53). Every loop is hand-written in the language's async primitives.

A parallel search for vector stores and embedding libraries found **zero systems that retrieve code with embeddings**. They use ripgrep, glob, tree-sitter and auto-discovered Markdown files. Embeddings appear only for chat memory, on by default in exactly one system (OpenClaw) [p. 54–56](https://arxiv.org/pdf/2609.00006#page=54).

##### Why no frameworks

Anthropic's guidance warned that frameworks "often create extra layers of abstraction that can obscure the underlying prompts and responses, making them harder to debug." When the agent edits real code, silent prompt corruption and opaque caching are too expensive to tolerate (p. 55).

##### Why no code RAG

Code has exact structure (paths, symbols, language servers) that similarity search cannot match, it changes minute to minute so embeddings go stale, and ripgrep is already a near-optimal search engine (p. 56).

##### The platform turn

The paper's thesis is that in the first half of 2026 the harness went from tool to platform [Obs. 12, p. 63](https://arxiv.org/pdf/2609.00006#page=63). Harnesses became importable SDKs (Claude Agent SDK, openai-codex), framework vendors shipped harnesses (LangChain's Deep Agents), plugin marketplaces appeared, Codex shipped an importer for Claude Code's sessions and settings, and Databricks' Omnigent now orchestrates 23 harness adapters behind one API. That also resolves the framework puzzle: harnesses did not adopt frameworks, they replaced them.

#### What backs these claims

This is a **source-code study, not a benchmark**. Its evidence is what the code contains, counted across systems:

##### How many of the 11 harnesses do it

Counts from Observations 5–9 and §14.1. "Native OS sandbox" counts the two with built-in cross-platform sandboxes (Codex, Gemini CLI); Claude Code's is opt-in.

##### Independent evidence that structure matters

The paper leans on a separate study, Agentic Harness Engineering (AHE), which evolves a harness automatically from a bash-only seed to 71.9% on SWE-bench Verified. Its ablation shows which parts carry the gain [p. 66](https://arxiv.org/pdf/2609.00006#page=66):

##### Percentage-point change from each evolved component (AHE)

Tools, middleware and long-term memory add points; the evolved system prompt alone costs 2.3. The paper reads this as "structural scaffold is more portable than prose-level prompt strategy."

##### Update · my check (27 Oct 2026)

A controlled study published 23 Oct 2026, _When Agents Fail: Model or Harness?_ (Shanghai AI Lab), crossed four harnesses (OpenCode, Codex CLI, Pi CLI, DeepAgents) with four models over 52,168 trajectories. Harness rankings flip depending on the model. On LOCA-Bench, harness choice accounted for 67.2% of the variation in mean scores, against 9.4% for the model and 23.4% for their interaction [Zhang et al. 2026, Table 22](https://arxiv.org/abs/2610.32483). That is the measurement this paper explicitly did not run, and it supports its premise that the harness matters as much as the model.

Self-reported SWE-bench Verified figures from spring 2026, which the authors removed from their main table as not comparable: OpenHands 77.6%, Mini-SWE-Agent 74%+, Claude Code 72.7%, Codex 69.1% (p. 11).

### Where it falls short

#### How far to trust it

- **It reads code, it does not run it.** No claims about speed or quality; benchmark numbers are the systems' own (p. 66).

- **Claude Code comes from a circulated March 2026 source snapshot**, not an official release, the weakest link for reproducibility (p. 67).

- **Inventory claims decay in weeks.** Three April observations had to be revised by July; tool counts and versions will be out of date. Structural claims (the seven parts, the absences) have held up (p. 63).

- **Scoring involves judgment calls**, and the Anthropic-guidance match (Obs. 10) shows correlation, not causation.

- **The paper was written with substantial help from Claude** (via Claude Code), with findings verified against the code, per its disclosure (p. 74). worth knowing when it praises Claude Code's design.

## Why it matters

### What it changed

The paper is only a few months old, so it's too early to say what it changed. What it gives you today is a shared map: one vocabulary for parts that every agent has, and evidence from real source code instead of opinion.

**What to remember.** A coding agent is a small loop surrounded by a large amount of engineering whose job is not to make the model smarter but to make it safe, affordable, recoverable and extensible. The field converged fast: the same seven parts, hand-rolled loops, deterministic retrieval, threshold compaction, coordinator–worker sub-agents and skills. And it copies itself: Codex adopted Claude Code's hook vocabulary verbatim; Hermes' code comments credit OpenCode, Codex and OpenClaw [p. 62](https://arxiv.org/pdf/2609.00006#page=62).

#### Since the paper

Gemini CLI's consumer tier was retired in June 2026 in a move toward the closed-source Antigravity CLI, so the paper's v0.50.0 pin captures the last major open-source state of that lineage (p. 8). Controlled harness × model studies have started (see the update card under What they found, in the Results tab).

#### What the authors recommend

The paper closes with these 18 recommendations and a 90-line scaffold that implements 10 of them (Listing 3, p. 71–72). The scaffold deliberately omits, because the right answer depends on context: sandboxing, multi-agent orchestration, MCP and skills. "Start here, measure, add the minimum that your observed failure modes demand" (p. 72).

**All 18 recommendations**

1. Start with a linear loop; move to a middleware pipeline at 3+ turn policies.

2. Couple to your home provider with a fallback; multi-provider can still reach native optimizations via per-model metadata.

3. Begin with just bash; add tools only for observed failures.

4. Adopt deferred tool loading above ~15 tools.

5. Exact matching for frontier models, fuzzy for weaker ones; never line numbers.

6. Auto-discover hierarchical Markdown context files, including neighbors' filenames.

7. Threshold compaction below the window, verbatim recent tail, incremental summaries, reactive on overflow.

8. Do not build RAG over code; use ripgrep, glob and tree-sitter.

9. Developer tools: PLAN / DEFAULT / YOLO modes with permission patterns.

10. Enterprise: OS-level sandbox, policy-as-code, per-agent audit trails.

11. Safety rules as data; keep a floor beneath any YOLO mode.

12. Stay single-agent until a breadth-first phase clearly benefits.

13. Ship an ACP server; keep your own sub-agents in-process.

14. Skills for capabilities, MCP for integrations.

15. Do not use agent frameworks for the runtime (or use a harness SDK instead).

16. Do not build a vector layer for code without proving it beats ripgrep.

17. Do not wrap every SaaS API one-to-one as a tool.

18. Do not over-engineer stuck detection, but ship the cheap caps.

§16 [p. 67–70](https://arxiv.org/pdf/2609.00006#page=67).

#### Verdict

**Read** sections 2 (the anatomy), 9–10 (memory and safety), 13.2 (twin absences) and 16 (recommendations and the 90-line harness). **Skim** the per-system deep dives and prompt-rhetoric section unless you build harnesses. It is the best single map of how real coding agents are built, with the caveat that it describes code rather than measuring it.

**Key terms and sources**

#### Interfaces, frameworks and surveys, but no anatomy

Three earlier lines of work circle the same object:

- **SWE-agent's Agent-Computer Interface (2024).** It showed that designing tools for the model matters: custom file viewer, editor and search commands solved 10.7 points more SWE-bench Lite tasks than a plain shell (a 64% relative gain) [SWE-agent](https://arxiv.org/abs/2405.15793). That is one subsystem (tools), studied alone.

- **Agent frameworks** (LangChain, LangGraph, AutoGen, CrewAI): libraries you import to build an agent. As the Results tab shows, no production coding harness uses them.

- **Surveys and taxonomies** describe patterns "without implementations"; the one concurrent source-level taxonomy (Rombaut, 13 open-source scaffolds) excludes the provider-native systems [p. 2](https://arxiv.org/pdf/2609.00006#page=2).

##### Not quite a scaffold

Near-synonyms. Scaffold = the loop and registries; harness = the shipped runtime around them.

##### Not a framework

A framework is a library you import. A harness is a runtime you work inside.

##### Not an eval harness

SWE-bench's "harness" wraps an agent to test it. Same word, opposite direction.

##### Not an orchestrator

A meta-harness coordinates harnesses from above and has no editing loop of its own.

From §2.2 [p. 3–4](https://arxiv.org/pdf/2609.00006#page=3).

#### Key terms

Harness

Everything in an agent except the model: loop, tools, context, safety, orchestration, extensions.

ReAct loop

Model reasons, picks an action, sees the result, repeats.

Compaction

Summarizing old conversation into a short note when the context fills up.

Deferred loading

Keeping tool or skill details out of the prompt until the model searches for them.

Prompt cache boundary

A split between the static part of the prompt (cached) and the per-turn part.

Policy-as-code

Safety rules written as data files (Starlark, TOML) instead of buried in code.

Sandbox

OS-level isolation limiting files, network and processes a command can touch.

MCP

Model Context Protocol: a wire protocol for calling tools on a separate server.

Skill

A folder with SKILL.md instructions and optional scripts, loaded when relevant.

ACP / A2A

Agent Client Protocol (editor ↔ agent, now also hosting one harness inside another); Agent-to-Agent (cross-vendor mesh).

Meta-harness

A layer that orchestrates several harnesses behind one API (Omnigent).

#### Everything on this page comes from these

1. Barbaste, Darrigol, Vu, Wiltberger (2026). Harness Engineering: Anatomy, Architecture, and Evolution of Coding Agents. [arXiv 2609.00006](https://arxiv.org/abs/2609.00006) (read in full)

2. mini-swe-agent repository and README. [github.com/SWE-agent/mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent)

3. Yang et al. (2024). SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering. [arXiv 2405.15793](https://arxiv.org/abs/2405.15793)

4. Anthropic. Building Effective Agents (Dec 2024) and related engineering posts, as cited by the paper. [anthropic.com](https://www.anthropic.com/research/building-effective-agents)

5. Zhang et al. (2026). When Agents Fail: Model or Harness—Who's to Blame? [arXiv 2610.32483](https://arxiv.org/abs/2610.32483)

6. Google Cloud Tech (2026). AI harness crash course. [YouTube](https://www.youtube.com/watch?v=2C_CefSQEAQ)

7. Böckeler (2026). Harness engineering for coding agent users. [martinfowler.com](https://martinfowler.com/articles/harness-engineering.html)

8. Further reading: [Context Engineering for AI Agents (Schmid)](https://www.philschmid.de/context-engineering-part-2). The authors' own blog or talk: searched, none found.

The test_invoice.py task and the numbers inside the widgets (tokens per schema, tokens per turn, the example policy) are illustrative. All other facts and numbers come from the sources above. @datawithsuman
