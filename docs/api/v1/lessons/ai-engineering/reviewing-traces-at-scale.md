# Reviewing Traces at Scale: Sampling, Clustering and Review Tools

> You have 50,000 traces a day and time to read 50. Which 50?

- Track: AI Engineering › Applied Evals › Lessons
- Type: Concept · 16 min
- Page: https://aimlrounds.com/tracks/ai-engineering/reviewing-traces-at-scale/
- Before this: Error Analysis: From Traces to Failure Rates (`ai-engineering/error-analysis`), Tracing and Observability for LLM Apps and Agents (`ai-engineering/tracing-and-observability`)
- Quiz topic: `evals`

## Intuition

### The situation

Your assistant serves 50,000 conversations a day. The team reviews 50 a week, all taken from thumbs-down feedback. Quality looks stable, yet a big customer reports a problem nobody has seen. The interviewer asks:

> You have 50,000 traces a day and time to read 50. Which 50?

#### Why it matters

After launch, error analysis becomes a weekly habit, and the bottleneck is choosing what to read. Teams that only read flagged traces get very good at known problems and blind to new ones. Teams that read random traces spend most of their time confirming that things work.

### The idea

Think of a fishing boat that only checks the nets where the sonar beeped. It catches what it knows about, and never learns there are fish in the quiet water. Cast some nets at random too.

[Figure: Three ways to pick traces. Random for honesty. Flagged for known problems. Disagreements for borderline cases.]

_You only find the failures your sampling can reach._

### Play

**Try to break it.** Spend all 50 reviews on flagged traces. Then try the mix.

#### Spend 50 reviews a week

Sampling mix

Reading only flagged traces gives you 50 examples of problems you already know about, and finds nothing new. Random reviews are honest but slow. The mix reads plenty of known failures, about one silent failure a week that no signal would ever surface, and about ten borderline cases to sharpen your rubric. The rates are illustrative; the blind spots are real.

**Now say why:** why does failure-driven sampling never find a new problem?

## How it works

### How it works

#### In one breath

You can't read everything, so choose. **Random** samples are unbiased but mostly confirm things work. **Failure-driven** samples (thumbs-down, guardrail trips) explain known problems fast but never show failures nobody flagged. **Uncertainty** samples (traces where two checks disagree) find borderline cases that sharpen your criteria. Mix all three, and include some traces that passed every check. Across thousands of traces, cluster them, plot simple per-trace numbers, and use semantic search to find every trace like a bad one. Treat what tools and coding assistants find as hypotheses to check in the traces.

#### Choosing and finding

##### Three ways to sample

| Sampling | Good at | Misses |
|---|---|---|
| Random | an honest picture of quality | rare failures; mostly shows passes |
| Failure-driven: thumbs-down, guardrail trips, retries | explaining known problems quickly | failures no signal catches |
| Uncertainty: checks disagree, or a judge flips between runs | borderline cases that sharpen your rubric | clear failures nobody checks for |

A mix works best, plus a random slice of traces that passed every automated check, which is where silent failures hide.

##### Seeing patterns in thousands of traces

- **Per-trace numbers:** turns, tool calls, latency, tokens, user sentiment. Plot distributions and outliers; a spike in tool calls often marks a loop.

- **Clustering:** group traces by embedding or topic, then read a few from each cluster. Clusters suggest hypotheses; they don't prove them.

- **Semantic search:** once you've found one bad trace, find all the traces like it to see how big the problem is. Searching on an LLM-extracted summary of what went wrong often works better than the raw text.

- **AI coding assistants:** great for loading traces, plotting and drafting rubrics. Check their conclusions against real traces, since they can confidently describe patterns that aren't there.

##### Review tools

Spreadsheets break on long, nested traces. A small custom viewer (rendered conversations, tool calls folded open, one-key pass or fail, a notes box, progress) makes reviewing much faster. Practitioners call it one of the best investments a team makes. Build review into the week, and make it easy to turn a finding into a bug, a golden-set example or a prompt fix.

## In practice

### In practice

#### In practice

- **Mix sampling:** random, failure-driven and uncertainty, plus a slice of traces that passed everything.

- **Track simple numbers per trace:** turns, tool calls, tokens, latency; outliers point to loops and confusion.

- **Cluster, then read:** a few traces per cluster, as hypotheses.

- **Size a problem with semantic search:** find every trace like a bad one.

- **Build a small review tool:** rendered traces, one-key labels, notes.

- **Close the loop:** each finding becomes a bug, a golden-set case or a prompt fix.

### The answer that sounds right

#### "We review every thumbs-down, so we'd know"

It sounds thorough, but most unhappy users never click thumbs-down, and some failures don't look bad to the user at all. Add random and disagreement-based samples, and read traces that passed every check.

## Say it

### You have 50,000 traces a day and time to read 50. Which 50?

#### The interviewer pushes further

Follow-up 1 of 3

Why read traces that passed every check?

Your checks only cover known failure modes. Failures nobody has defined yet pass them, and only reading reveals them.

Follow-up 2 of 3

Your coding assistant says 30% of traces show confusion about dates. Do you trust it?

Treat it as a hypothesis. Search for and read those traces, and count them yourself before acting.

Follow-up 3 of 3

What makes uncertainty sampling useful?

Disagreement between checks marks traces where your criteria are unclear, so labelling them improves both your rubric and your judges.

I'd mix three kinds of sampling: random for an honest picture, failure-driven from thumbs-down and guardrail trips to explain known problems, and uncertainty sampling where checks disagree to find borderline cases, plus a slice of traces that passed everything, since that's where silent failures hide. Across thousands of traces I'd plot simple per-trace numbers, cluster and read a few per cluster, and use semantic search to size a problem once I've found it. A small custom review tool makes this fast, and every finding should become a bug, a test case or a fix.

**Key terms and sources**

How to choose traces for human review (random, uncertainty and failure-driven sampling), how to find patterns across thousands of traces (clustering, per-trace statistics, semantic search), and what makes a review tool worth building.

#### Sources

- H. Husain and S. Shankar, _Evals for AI Engineers_ (O'Reilly): the Analyze-Measure-Improve lifecycle, error analysis, judges, CI and review

- H. Husain and S. Shankar, AI Evals: everything you need to know (FAQ)

- S. Shankar et al., Who validates the validators? (EvalGen), UIST 2024

Explanations and examples are ours, built from these sources. Lab numbers are illustrative unless a lab says otherwise. Many recent papers are preprints, and benchmark scores change quickly.
