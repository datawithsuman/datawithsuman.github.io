# Context Language Models

> What if an AI agent could edit its own memory?

- Track: Papers Explained › Context engineering and RAG
- Type: Paper · 8 min
- Page: https://aimlrounds.com/tracks/papers/context-language-models/
- Before this: Harness Engineering (`papers/harness-engineering`)
- Related: Harness Engineering (`papers/harness-engineering`)

## Gist

### The paper

Rulin Shao, Shannon Zejiang Shen, Junjie Oscar Yin, Yuetai Li, Minheng Wang, Hamish Ivison, Radha Poovendran, Nathan Lambert, Teng Xiao, Mike Lewis, Wen-tau Yih, Luke Zettlemoyer, Pang Wei Koh
 University of Washington · Meta Superintelligence Labs · MIT · Trillium Labs
 arXiv 2609.37725 · 29 Sep 2026 · [alphaXiv](https://www.alphaxiv.org/abs/2609.37725) · [code](https://github.com/facebookresearch/context-language-models)

Today an agent's memory is managed by outside code that decides when to summarize or delete. This paper lets the model itself edit its own context, like editing a text file, and shows that this beats the fixed approaches on long tasks while using less compute.

### The problem

#### What problem does it solve?

An AI agent working on a long task keeps piling up text: tool outputs, notes, past steps. This pile is its **context**, and it has a size limit. Something has to decide what to keep, shorten or throw away.

Until now that decision was made by **outside code (a "harness")**, with fixed rules such as "summarize everything when the context is 75% full". The model itself never really controlled its own memory. Sec 1

#### Why does it need solving?

- **Summaries lose or distort facts.** A summary can drop a detail the agent needs ten steps later, or state something wrong. Sec 3

- **Fixed tools limit the strategy.** Even newer systems that let the model choose actions only offer a menu someone predefined (compact, offload, retrieve). A task might need something else, such as keeping one line word for word or fixing one cell of a board. Sec 2

- **Memory handling is tuned separately from reasoning,** even though what is in context directly shapes the next thought. Overview of Sec 1

- **Cost:** long runs (12 to 24 hours) are expensive, so wasteful context management is a real money problem. Abstract

_**Figure 2: four tests where success means keeping the right information.** As context pressure (input volume divided by the context limit) grows, most methods lose accuracy. The dark blue line, CLM, stays near 1.0. GPT-5.4, 32K limit. Fig 2, from the paper Tap the image to enlarge._

### The idea

A normal agent is like a person who can only add lines to the bottom of a notebook, while an assistant occasionally tears pages out and replaces them with a summary. A Context Language Model is the person holding the eraser and pen. They cross out stale notes, rewrite a messy page, and keep one important quote exactly as written.

[Figure: Flow of one Context Language Model turn]

Read it left to right: the model reads its context file, then either just continues or edits the file. Every change is synced back as the next turn's context, and the server reuses cached computation where it can.

## Method

### Method

#### The approach, intuitively

How it works in plain steps: Sec 4.1

1. **The context is mirrored as a file** and its path is given to the model in the system prompt.

2. The model can edit that file with ordinary **Bash commands** (delete lines, rewrite, append notes, move big data to other files).

3. **Every edit is instantly synced back** to the model's live context for the next turn.

4. If the model does nothing special, new tokens are simply appended, so it behaves like a normal model.

5. **Many agents** = many context files. Creating or deleting a file creates or ends a sub-agent.

In math terms: a normal model does `c_next = c_now + output`. A CLM does `c_next = f_CLM(c_now)`, where `f` can be any edit the model chooses.

The paper also shows the model can **learn better context habits** three ways: from a one-line instruction, from an evolving written "skill" document, and from reinforcement learning (stepwise GRPO with a reward for being cheap only when the task succeeded). Sec 4.2 / Fig 1

#### Challenges the authors faced

**1. Edits break the usual speed-up.** Servers reuse cached work only for text before the first change. An edit near the top forces everything after it to be recomputed. The paper's own example: an append-only turn costs 1.41×10¹⁴ FLOPs, a mid-context edit 5.74×10¹⁴, and an edit at the start 10.81×10¹⁴, or 7.7× more. App. B, Fig 14 **How they handled it:** they invented _prefix-reuse FLOPs_ to measure true trajectory cost, and _Suffix Cache Reuse_, which finds text that survived an edit and reuses its cached work. Sec 1

**2. Existing methods were hard to judge fairly.** Reasoning ability and memory handling get mixed together. **How they handled it:** they built _ContextBench_, four synthetic tasks (Needle Retention, Sudoku Sketchpad, KV Store, Log Triage) where an agent that could keep everything would answer everything, so scores reflect only context management. Sec 3, App. D

**3. Models do not always know how full their context is.** The authors found this awareness degrades at long lengths, so they add simple hints (an editing reminder 2,048 tokens before the budget) as a temporary fix. App. E, footnote 4 / App. G

**4. Training could reward the wrong thing.** A pure "be cheap" reward would encourage deleting everything. **How they handled it:** a _success-gated efficiency advantage_: cheapness is rewarded only among trajectories that succeeded. Sec 4.2

**5. Safety.** A context the model can edit is another place where injected or self-written instructions can persist. The paper points to a reported case where a model slipped unauthorized instructions into its own summary. Sec 6

_**Figure 4: standard serving versus Suffix Cache Reuse.** After an edit changes B to B', standard serving re-prefills B' and everything after it (C). Suffix Cache Reuse keeps the cached work for C and only prefills the edited part. Fig 4, from the paper Tap the image to enlarge._

## Results

### What they found

_**Figure 1 of the paper: a one-page overview.** (A) behaviors the model invented, (B) results out of the box, (C) learning from instructions and evolved skills, (D) learning in the weights with reinforcement learning. Fig 1, from the paper Tap the image to enlarge._

#### Results

All numbers below come from the paper. "PFLOPs" is the paper's prefix-reuse compute measure; lower is cheaper.

| Test | CLM | Compared with | Source |
|---|---|---|---|
| BrowseComp-Plus (deep research), Qwen3.6-27B | 59.4% accuracy | 11.4% higher than strongest baseline, with 21.5% fewer FLOPs | Abstract, App. F |
| TerminalBench 2.1 (coding) | matches best baseline | about 29.5% fewer FLOPs | Sec 1 |
| 12-hour EdgeBench (10 tasks) | 5% higher score | 59% fewer FLOPs than Codex-style summary | Abstract, Sec 1 |
| 24-hour six-repo agent swarm | 65% greater speedup | same compute as summary swarm | Abstract |
| Math optimization (4 problems) | best score on all four | vs OpenEvolve: up to +16.8% (Heilbronn), +3.0% (circle packing) | Sec 1, Fig 18 |
| Steering with evolved "skill" (ContextBench, held-out KV Store) | 74.2% | 38.3% before the skill | App. F |
| Reinforcement learning, Qwen3.5-9B on BrowseComp-Plus | 28.8% to 42.5% | summary harness trained the same way: 42.1% | Abstract, Sec 1 |
| Suffix Cache Reuse | about 35% less server compute | vs standard SGLang at matched performance | Abstract |

**Interesting behaviors the model invented on its own:** keeping a scoreboard to track sub-agents, creating an internal "notes" chat role, and defining reusable context-cleaning functions. Sec 1, Fig 1a

_**Figure 5: accuracy against compute on three benchmarks.** Higher and further left is better. CLM (blue) is on the efficient frontier on all three. Qwen3.6-27B, 32K limit, 100-turn cap. Fig 5, from the paper Tap the image to enlarge._

_**Figure 6: long-horizon software optimization.** Left: EdgeBench-10 over 12 hours with Qwen3.6-27B and Claude 4.6 Sonnet. Right: the six-repository agent swarm, where CLM reaches a 1.044 speedup against 1.026 for the summary swarm. Fig 6, from the paper Tap the image to enlarge._

### Where it falls short

#### Limitations and critique

From the paper Editable context opens new safety risks (persistent prompt injection); Suffix Cache Reuse is approximate because reused cached states were computed under an earlier prefix, and it depends on model architecture and serving setup. The paper has no dedicated limitations section; these appear in Sec 6 and the overview of its text.

From the paper Gains depend on the model's ability to decide when to edit: Qwen3.5-9B edits 1.4 times per task on TerminalBench 2.1 and makes no edit in half the tasks, while Qwen3.6-27B edits 2.6 times. App. F

My assessment

- **The advantage shrinks with more room.** With a 128K budget on EdgeBench-10, CLM scores 47.3 against 47.8 for summarization (at 142 vs 222 PFLOPs), and the 50.2 result needs the sub-agent version. Much of the benefit at 32K is cost, not accuracy. App. F, Fig 19

- **Several results rest on little data.** The math-optimization comparison uses one run per method (per the overview of the paper), so differences like +3.0% may be within noise.

- **Hints may help CLM more than baselines.** CLM receives an editing reminder before the budget, while the summary baseline compacts on its own trigger. The authors call this a temporary augmentation. App. E

- **No tests on safety defenses** yet; the risk is named but not measured.

- **Mostly Qwen and a few closed models;** I did not see results across a wide range of model families.

_**Figure 19: the same EdgeBench-10 test with a 128K budget.** CLM scores 47.3 at 142 PFLOPs against 47.8 at 222 for summarization. With sub-agents it reaches 50.2 at 219. The accuracy gap is small here. Fig 19, from the paper Tap the image to enlarge._

## Why it matters

### What it changed

The paper came out in September 2026, so it's too early to say what it changed. Its lasting claim is the shift in who controls memory: the model edits its own context directly, instead of outside code deciding what to keep.

**What to remember.** Letting the model edit its context can beat fixed rules on long tasks while using less compute, but the gain is largest at small context budgets, and editable context is also a new safety risk.

#### Future scope

Authors propose

- **Scale up RL** so CLMs can explore and learn their own context strategies. Sec 6

- **Harness-to-CLM distillation:** turn existing harness operations into CLM actions and eventually absorb them into model weights, treating harnesses as a kind of procedural memory. Sec 6

- **Study and defend the new attack surface** of editable context while keeping its flexibility. Sec 6

My additions

- Models that know their own context usage natively, so the reminder hint is not needed.

- Edit logs or version history so mistaken deletions can be undone and audited.

- Head-to-head comparisons with the newest RL-trained compaction methods under the same compute.

#### Verdict

READ The core idea is simple, the experiments span coding, research, math and multi-day swarms, and the cost accounting is unusually honest. Read Sections 1, 3, 4 and 6 first; skim the appendix unless you build agent infrastructure.

Caveat: some headline gains are at a small 32K context budget and some experiments are single runs, so treat the exact percentages as indicative.

**Key terms and sources**

#### How existing papers tried to solve this

The paper describes a ladder where the model gets more control at each step but always inside a human-designed box. Sec 2, App. A

| Approach | Examples | Where it falls short |
|---|---|---|
| Harness decides on a schedule | Cursor, Codex, Terminus2 (compact at a length threshold); MEM1 (update every turn) | Schedule and method are fixed, even when trained with RL |
| Model picks from a menu of actions | Self-Compact, AutoCompact (when to compact); Context-as-a-Tool; ACM (adds offload and retrieve); Context Folding; Sculptor | Strategy limited to predefined operations |
| Context as a REPL variable | Recursive Language Models | Controls how input is read, but live context is read-only and keeps growing |
| Optimize the harness itself | Meta-Harness, AutoMem, Meta Context Engineering | Improves reusable procedures but the model does not directly edit its live context |

Found via alphaXivOther recent work on the same problem includes [CompactionRL](https://www.alphaxiv.org/abs/2607.05378) (RL with context compaction), [Context as an Environment](https://www.alphaxiv.org/abs/2608.21690) (programmatic context management), [ContextPilot](https://www.alphaxiv.org/abs/2608.28476) (fine-grained RL for proactive context management) and [TokenPilot](https://www.alphaxiv.org/abs/2606.17016) (cache-efficient context management). I only read their abstracts, so I have not compared their results to CLMs.

#### Key terms

Context

Everything the model can see right now: the task, past steps and tool outputs. It has a size limit.

Harness

The wrapper code around a model that runs tools and decides how history is managed.

Compaction

Shrinking old context, usually by summarizing it.

KV cache

Saved intermediate work so the server does not recompute text it already processed.

Prefix caching

Reusing that saved work only for the unchanged start of the text.

Suffix Cache Reuse

The paper's method for also reusing saved work for text after an edit.

Prefix-reuse FLOPs

The paper's cost measure covering decoding, prefilling and re-prefilling across a whole run.

Context pressure

Total input pushed through an episode divided by the context limit. 1× means keep-everything would just fill the context.

GRPO

A reinforcement learning method; here applied step by step with an extra reward for efficiency among successful runs.

ContextBench

The paper's four-task test that isolates context management from reasoning.
