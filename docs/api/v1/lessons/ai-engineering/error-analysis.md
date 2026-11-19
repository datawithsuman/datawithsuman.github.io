# Error Analysis: From Traces to Failure Rates

> You have 100 traces. How do you turn reading them into numbers you can act on?

- Track: AI Engineering › Applied Evals › Lessons
- Type: Concept · 18 min
- Page: https://aimlrounds.com/tracks/ai-engineering/error-analysis/
- Before this: Building Your First Eval Set: Real Traces and Synthetic Queries (`ai-engineering/building-an-eval-dataset`)
- Quiz topic: `evals`

## Intuition

### The situation

Your real estate assistant has 100 logged traces. A teammate pasted them into an LLM and asked for the top failure categories. It returned "hallucination, tone, instruction following", and the team wants to build a judge for each. The interviewer asks:

> You have 100 traces. How do you turn reading them into numbers you can act on?

#### Why it matters

Teams that skip this step ask an LLM to list likely failures and get "hallucination, tone, instruction following". They then build months of checks for categories that don't match what actually breaks. Error analysis gives you your own categories, grounded in your traces. Practitioners who teach this say it takes most of their evaluation time, and it's where the useful insight comes from.

### The idea

Think of a doctor learning a new disease. They don't start from a textbook's list of symptoms; they examine patients and write down what they see, then group the notes. The textbook's categories help when stuck, but the patients decide.

[Figure: Four steps. Note the first failure. Group the notes. Label every trace. Count.]

_Your traces decide the categories, not a generic list._

### Play

**Try to break it.** Read only 20 traces. Then 300. Watch the rare modes.

#### When have you read enough?

After 60 traces you'll usually have seen 6 of the 8 failure modes, and the next 20 traces add less than half a new one: that's saturation. But the rarest mode, in 0.5% of traces, needs hundreds of traces to show up even once. That's why error analysis isn't a one-off: you keep sampling production, and new modes appear as the product changes.

**Now say why:** why does reading more stop helping, yet rare modes still hide?

## How it works

### How it works

#### In one breath

Read each trace as the user would, and write a short note on the **first** thing that went wrong (open coding), since one early mistake causes the rest. Then group the notes into a handful of failure modes specific to your app (axial coding): "SQL drops a user's filter", "email tone wrong for the client type". An LLM can help group your notes, but shouldn't invent the categories. Mark each trace 1 or 0 for each mode, count, and you have failure rates that tell you what to fix first.

#### Four steps

##### 1 · Open coding

For each trace, write a short, lowercase note on the first failure you see: "sql dropped the pet-friendly filter the user asked for", "proposed a saturday slot the calendar showed as blocked", "email describes 3 bedrooms; the listing says 2". Judge from the user's side: did they get what they needed? Also give each trace a plain **pass or fail**; forcing a yes or no sharpens your thinking more than a 1–5 score. Do this yourself: it needs your judgement about what counts as a failure.

##### 2 · Axial coding

Group similar notes into failure modes. Some groupings are obvious (ignored budget and ignored bedroom count both become **missing constraint**). Others need splitting: an invented pool and an invented tour booking look alike, but one is invented listing data and the other invented user intent, with different fixes. Here an LLM can help: paste your notes and ask it to propose groups without adding new failure types. Then edit its groups yourself.

##### 3 · Label and count

Add a column per failure mode, mark each trace 1 or 0, and divide by the number of traces. Slice by feature or user type to see where each mode concentrates.

##### 4 · Iterate

Two or three rounds are normal: you'll split, merge and rename modes as you read more. Stop when new traces stop producing new modes. If you're stuck on what feels wrong, use known failure types as lenses (hallucination, wrong tool, ignored constraint), but don't force traces into them.

#### The maths

$$ \hat p = \frac{k}{n} \pm 1.96\sqrt{\frac{\hat p(1-\hat p)}{n}} $$

Rates from 100 traces are rough: good enough to rank what to fix, not to promise a number to a customer.

- **failure rate**: The share of traces showing this failure mode.

- **traces with the failure**: Counted from your 1 or 0 column.

- **traces labelled**: With 100 traces and 20 failures, the rate is 20% ± 8 points.

## In practice

### In practice

#### In practice

- **First failure only:** one upstream mistake explains the downstream ones; fixing it often fixes the chain.

- **Notes a teammate can read:** short, specific and with enough context to understand without the trace.

- **You do open coding; an LLM can help group:** never let it invent the taxonomy from scratch.

- **Split by fix:** if two failures need different fixes, they're different modes.

- **Use a spreadsheet:** one row per trace, a column per mode, pass or fail.

- **Repeat after big changes:** new models and features bring new modes.

### The answer that sounds right

#### "An LLM gave us the failure categories"

It sounds fast, but generic categories like "hallucination" don't match your app's real failures, and checks built on them measure the wrong things. Read the traces yourself first; let an LLM help only with grouping your notes.

## Say it

### You have 100 traces. How do you turn reading them into numbers you can act on?

#### The interviewer pushes further

Follow-up 1 of 3

Why note only the first failure in a trace?

Later problems are often consequences of the first. Labelling every symptom inflates counts and hides the root cause.

Follow-up 2 of 3

Why not let an LLM list the failure modes?

It has strong priors for generic categories and none for your app's specific failures, so its list won't match what actually breaks.

Follow-up 3 of 3

Two failures look similar. One category or two?

Two if they need different fixes, such as invented listing details (a grounding problem) and invented user requests (an intent problem).

I'd read about 100 traces and, for each, write a short note on the first failure, judged from the user's side, plus a pass or fail. Then I'd group the notes into failure modes specific to our app, splitting any that need different fixes; an LLM can help group, but not invent the categories. I'd label every trace 1 or 0 per mode and compute rates, which tell me what to fix first. I'd stop at saturation, when new traces show nothing new, and repeat after big changes.

**Key terms and sources**

Open coding (a short note on the first failure in each trace), axial coding (grouping notes into failure modes specific to your app), labelling every trace, and turning counts into rates with error bars.

#### Sources

- H. Husain and S. Shankar, _Evals for AI Engineers_ (O'Reilly): the Analyze-Measure-Improve lifecycle, error analysis, judges, CI and review

- H. Husain and S. Shankar, AI Evals: everything you need to know (FAQ)

- E. Yan, Product evals in three simple steps

Explanations and examples are ours, built from these sources. Lab numbers are illustrative unless a lab says otherwise. Many recent papers are preprints, and benchmark scores change quickly.
