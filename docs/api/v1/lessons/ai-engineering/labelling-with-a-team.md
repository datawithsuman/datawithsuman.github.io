# Labelling with a Team: Rubrics, Cohen's Kappa and Alignment

> Two experts label the same 50 answers and agree 90% of the time. Is your rubric good?

- Track: AI Engineering › Applied Evals › Lessons
- Type: Concept · 16 min
- Page: https://aimlrounds.com/tracks/ai-engineering/labelling-with-a-team/
- Before this: Error Analysis: From Traces to Failure Rates (`ai-engineering/error-analysis`)
- Quiz topic: `evals`
- Sources checked: 2026-11-15 · Text last changed: 2026-11-20 · Version: 1c209e99c0

## Intuition

### The situation

Three people labelled 50 support answers for tone and agree 86% of the time. You're about to use their labels to validate a tone judge. Most answers are fine. The interviewer asks:

> Two experts label the same 50 answers and agree 90% of the time. Is your rubric good?

#### Why it matters

Every judge you build is checked against human labels, so the labels have to be consistent. If two of your experts disagree about what "too casual" means, no judge can match both, and its accuracy number is meaningless. Interviewers also like the kappa question because percent agreement looks reassuring when it shouldn't.

### The idea

Think of two weather forecasters in a desert. If both say "sunny" every day, they agree 95% of the time and you've learnt nothing about their skill. What matters is whether they agree on the rare rainy days.

[Figure: Three steps. Label independently. Measure kappa per criterion. Align on disagreements.]

_Agreement on easy cases is free; agreement on failures is what counts._

### Play

**Try to break it.** Keep disagreements fixed and move labels from both-pass to both-fail.

#### Agreement that looks good and isn't

With 40 shared passes, 2 shared fails and 8 disagreements, the annotators agree 84% of the time, which sounds great. But each passes about 88% of answers, so they'd agree 78.9% of the time by chance, and kappa is only 0.24: they rarely agree on the failures, which are what you care about. Move to 30 passes and 12 fails with the same disagreements and kappa rises to 0.63.

**Now say why:** why does the same 84% agreement give such different kappas?

## How it works

### How it works

#### In one breath

Someone has to define "good". Often the fastest way is one trusted domain expert who makes the call (a "benevolent dictator"). When the domain is subjective or high stakes, use several annotators: draft a rubric, have everyone label the same 20–50 traces independently, measure agreement **per criterion** with Cohen's kappa (which subtracts agreement expected by chance), then meet to discuss disagreements and sharpen the rubric. The outputs are a rubric, gold labels for validating judges, and notes on edge cases.

#### Who decides, and how to agree

##### One expert, when you can

If the domain is narrow, the criteria are clear and one trusted expert has the time, let them decide: a lawyer for a legal tool, a senior agent for a support bot. It cuts weeks of debate. Smaller companies can usually do this; larger ones often need several voices from product, legal and support.

##### A team workflow

1. Draft one rubric per criterion: a definition plus a few pass and fail examples, usually straight from error analysis.

2. Pick 20–50 shared traces, including hard ones.

3. Everyone labels independently. Labelling together hides disagreement.

4. Measure agreement for each criterion separately; people may agree on facts and disagree on tone.

5. Run an alignment session on the disagreements: what did each person see, which rubric line was unclear, what should the rule be?

6. Revise the rubric (sharper definitions, new examples, explicit edge cases), relabel, and repeat until agreement is good enough.

7. Escalate deadlocks to one lead, and save everything: labels, decisions and why.

##### Why percent agreement misleads

If 90% of answers are fine, two people who both say "pass" to almost everything agree about 82% of the time by luck. **Cohen's kappa** compares observed agreement with that chance level: 0 means no better than chance, 1 means perfect. A common reading (Landis and Koch) calls 0.41–0.60 moderate, 0.61–0.80 substantial and above 0.80 almost perfect. For reference, the MAST study of multi-agent failures reached kappa 0.88 between expert annotators after three rounds of rubric refinement. For more than two annotators, use Fleiss' kappa; for ordered scales, a weighted kappa.

#### The maths

$$ {\kappa} = \frac{{p_o} - {p_e}}{1 - {p_e}} $$

When almost everything passes, chance agreement is high, so the same percent agreement means much less.

- **Cohen’s kappa**: Agreement beyond chance, from 0 (chance) to 1 (perfect).

- **observed agreement**: The share of traces where both annotators gave the same label.

- **agreement expected by chance**: From each annotator’s own pass rate: p_A·p_B + (1−p_A)(1−p_B).

## In practice

### In practice

#### In practice

- **One decider when possible:** a trusted expert is faster than a committee.

- **Label independently:** then compare, never label together.

- **Kappa per criterion:** one overall number hides which rubric line is unclear.

- **Discuss disagreements, not averages:** each one should change the rubric or confirm it.

- **Write edge cases down:** with the decision and the reason.

- **Keep the gold labels:** they validate every judge you build later.

### The answer that sounds right

#### "Our annotators agree 86% of the time"

It sounds solid, but if most answers pass, much of that agreement is chance. Compute kappa per criterion, and look at whether they agree on the failures.

## Say it

### Two experts label the same 50 answers and agree 90% of the time. Is your rubric good?

#### The interviewer pushes further

Follow-up 1 of 3

Why is percent agreement misleading?

When most answers pass, two annotators who pass almost everything agree by chance. Kappa subtracts that chance agreement, so it reflects agreement on the hard cases.

Follow-up 2 of 3

Kappa is 0.3 on tone and 0.85 on factual accuracy. What do you do?

The factual rubric works. The tone rubric needs an alignment session: collect the disagreements, find which definition is unclear, add examples and relabel.

Follow-up 3 of 3

Should the judge's agreement with humans beat human-human agreement?

It can't reliably exceed the humans' own agreement, so human-human kappa is the ceiling to compare against.

#### The 30-second answer

If one trusted expert can define quality, I'd let them decide, because it's fastest. For subjective or high-stakes criteria I'd use several annotators: draft a rubric per criterion, have everyone label the same 20 to 50 traces independently, and measure agreement per criterion with Cohen's kappa rather than percent agreement, since chance agreement is high when most answers pass. Then I'd run alignment sessions on the disagreements, sharpen the rubric and relabel until kappa is good, keeping the gold labels to validate judges later.

**Key terms and sources**

Who decides what "good" means, how to run a labelling round with several people, why percent agreement misleads, how Cohen's kappa corrects for chance, and how alignment sessions turn disagreements into a sharper rubric. · checked 15 Nov 2026

#### Sources

- H. Husain and S. Shankar, _Evals for AI Engineers_ (O'Reilly): the Analyze-Measure-Improve lifecycle, error analysis, judges, CI and review

- [J. Cohen, A coefficient of agreement for nominal scales, 1960](https://doi.org/10.1177/001316446002000104)

- [J. R. Landis and G. G. Koch, The measurement of observer agreement for categorical data, Biometrics, 1977](https://doi.org/10.2307/2529310)

- [M. Cemri, M. Z. Pan et al., Why do multi-agent LLM systems fail? (MAST)](https://arxiv.org/abs/2503.13657)

- [E. Yan, Product evals in three simple steps](https://eugeneyan.com/writing/product-evals/)

Explanations and examples are ours, built from these sources. Lab numbers are illustrative unless a lab says otherwise. Many recent papers are preprints, and benchmark scores change quickly.
