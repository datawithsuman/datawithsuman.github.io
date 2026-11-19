# Can You Trust Your Judge? TPR, TNR and Corrected Pass Rates

> Your LLM judge says 85% of answers pass. How do you know the real pass rate?

- Track: AI Engineering › Applied Evals › Lessons
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/ai-engineering/validating-an-llm-judge/
- Before this: LLM Judges: Pairwise Preferences and Pass/Fail Checks (`ai-engineering/llm-as-a-judge`), Classification Metrics (`fundamentals/classification-metrics`)
- Quiz topic: `evals`

## Intuition

### The situation

Your team's tone judge reports that 88% of client emails pass. A week of complaints says tone is often wrong. The judge was checked by eyeballing ten examples. The interviewer asks:

> Your LLM judge says 85% of answers pass. How do you know the real pass rate?

#### Why it matters

A judge that misses a third of real failures will report a healthy pass rate while users suffer. Teams often skip this step because the judge "looks right" on a few examples. Measuring and correcting the judge is what turns its number into something you can put on a dashboard and alert on.

### The idea

Think of a medical screening test. If it misses some sick people and flags some healthy ones, the share of positives isn't the share of sick people. Knowing the test's two error rates lets you work back to the real number.

[Figure: Three steps. Split the labels. Measure both error rates. Correct the raw number.]

_A judge's raw number is biased until you correct it._

### Play

**Try to break it.** Lower the judge's TNR. Then push both rates towards 50%.

#### Correct the judge's number

A judge with a 95% true positive rate and a 70% true negative rate, reporting 85% passes, really means about 84.6%. Drop the TNR to 60% and the same raw 85% means 81.8%: the judge lets real failures through, so the app looks better than it is. Push both rates down towards chance and the correction refuses to run, because the judge's verdicts carry almost no information.

**Now say why:** why does a low TNR make the app look better than it is?

## How it works

### How it works

#### In one breath

Treat a judge like a classifier you trained with a prompt. Split human-labelled traces into a small **train** set (few-shot examples for the prompt), a **dev** set (to refine the prompt) and a **test** set (touched once, at the end). On the test set, measure how often the judge passes real passes (**TPR**) and fails real failures (**TNR**). On new traffic, its raw pass rate is biased, so correct it: θ = (pobs + TNR − 1) / (TPR + TNR − 1). Bootstrap the test set for a confidence interval, and re-check the judge regularly.

#### Validate, then correct

##### Splits

Writing a judge prompt is like training a classifier, except you tune text and examples instead of weights. So you need separate data:

- **Train (10–20%):** clear pass and fail examples to use as few-shot examples in the prompt.

- **Dev (40–45%):** run the judge after each prompt edit and compare with human labels. Never put these in the prompt.

- **Test (40–45%):** run once, after the prompt is frozen, for an honest estimate.

Aim for 30–50 passes and 30–50 failures in each of dev and test, even if failures are rare in production. Using the same traces in the prompt and in the evaluation (leakage) makes the judge look better than it is.

##### Two error rates, not accuracy

The goal is the true pass rate, and a judge can distort it in only two ways: calling real passes failures, or real failures passes. So measure **TPR** (share of real passes it passes) and **TNR** (share of real failures it fails) separately. Stop refining at roughly 90% on both, or whatever your stakes require. If it stalls, try a stronger model, split the criterion into narrower judges, or add better examples.

##### Correct the raw rate

Run the frozen judge on new traces, count the share it passes, and correct it with the formula below (a classic epidemiology correction, Rogan and Gladen, 1978). Clip the result to 0–100%. If TPR + TNR − 1 is near zero, the judge is no better than chance and no correction can save it.

##### Error bars

Your TPR and TNR come from a finite test set. Resample the test set with replacement many times, recompute TPR, TNR and the corrected rate each time, and take the 2.5th and 97.5th percentiles. A wide interval means improve the judge, or label more.

##### Keep it honest

Judges drift: production changes, and providers update models. Pin the judge's model version, label a few new traces every week, and recompute TPR and TNR. Also run the judge 3–5 times on the same trace: if the verdict flips, the criterion needs a clearer definition or more examples.

#### The maths

$$ \hat\theta = \frac{p_{obs} + \mathrm{TNR} - 1}{\mathrm{TPR} + \mathrm{TNR} - 1} $$

If the denominator TPR + TNR − 1 is close to 0, the judge is guessing and the correction blows up. Practical code refuses to correct below about 0.05.

- **corrected pass rate**: What a human would say passes, estimated from the judge’s verdicts.

- **judge’s raw pass rate**: The share of new traces the judge marked Pass.

- **true negative rate**: Of traces humans failed, the share the judge also failed.

- **true positive rate**: Of traces humans passed, the share the judge also passed.

## In practice

### In practice

#### In practice

- **Label first:** 100–200 human-labelled traces per failure mode, with enough failures.

- **Three splits, no leakage:** prompt examples never appear in dev or test.

- **Report TPR and TNR:** not accuracy, which hides which way the judge errs.

- **Correct and add error bars:** before putting a judge's number on a dashboard.

- **Pin the judge model:** and re-check weekly with a few fresh labels.

- **Check stability:** 3–5 runs per trace; flips mean the rubric is unclear.

### The answer that sounds right

#### "The judge looked right on ten examples"

It sounds like enough, but ten examples can't measure how often the judge misses failures, and a judge with a low TNR reports a rosy pass rate. Measure TPR and TNR on a held-out test set and correct the number.

## Say it

### Your LLM judge says 85% of answers pass. How do you know the real pass rate?

#### The interviewer pushes further

Follow-up 1 of 3

Why TPR and TNR instead of precision and recall?

We want the true pass rate, and a judge distorts it in exactly two ways: failing real passes and passing real failures. TPR and TNR measure those directly.

Follow-up 2 of 3

Failures are 3% of traffic. Should dev and test also be 3% failures?

No. Include 30–50 failures in each so TNR is measured reliably; the correction handles the different mix in production.

Follow-up 3 of 3

The judge's verdict flips between runs on the same trace. What does that mean?

The trace is borderline for your rubric. Clarify the definition or add examples near that boundary, and use temperature 0 in production.

I'd treat the judge as a classifier. I'd split human-labelled traces into a small train set for few-shot examples, a dev set to refine the prompt, and a test set used once. On the test set I'd measure TPR and TNR separately, aiming for about 90% each. Then on production traces I'd correct the judge's raw pass rate with the Rogan–Gladen formula, observed plus TNR minus one, over TPR plus TNR minus one, bootstrap the test set for a confidence interval, pin the judge model, and re-check it with fresh labels every week.

**Key terms and sources**

How to check an LLM judge against human labels with train, dev and test splits, measure the two ways it can be wrong (true positive and true negative rates), correct its raw pass rate, and put error bars on the result.

#### Sources

- H. Husain and S. Shankar, _Evals for AI Engineers_ (O'Reilly): the Analyze-Measure-Improve lifecycle, error analysis, judges, CI and review

- W. J. Rogan and B. Gladen, Estimating prevalence from the results of a screening test, Am. J. Epidemiology, 1978

- H. Husain and S. Shankar, AI Evals: everything you need to know (FAQ)

- E. Yan, Product evals in three simple steps

- S. Shankar et al., Who validates the validators? (EvalGen), UIST 2024

Explanations and examples are ours, built from these sources. Lab numbers are illustrative unless a lab says otherwise. Many recent papers are preprints, and benchmark scores change quickly.
