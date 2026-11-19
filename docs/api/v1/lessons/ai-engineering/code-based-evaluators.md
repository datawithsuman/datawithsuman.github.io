# Code Checks First: Assertions, Schemas and Execution

> Before reaching for an LLM judge, what can you check with plain code, and how can code checks go wrong?

- Track: AI Engineering › Applied Evals › Lessons
- Type: Concept · 15 min
- Page: https://aimlrounds.com/tracks/ai-engineering/code-based-evaluators/
- Before this: Error Analysis: From Traces to Failure Rates (`ai-engineering/error-analysis`), Structured Output and Constrained Decoding (`ai-engineering/structured-output`)
- Quiz topic: `evals`

## Intuition

### The situation

Your data agent answers numeric questions. Its pass rate on a 200-question eval is 41%, far below what users report. A teammate wants to switch models. The interviewer asks:

> Before reaching for an LLM judge, what can you check with plain code, and how can code checks go wrong?

#### Why it matters

Many failure modes from error analysis are objective: a filter missing from the SQL, an invented tool name, a draft emailed without asking. An LLM judge for these is slower, costs money and can disagree with itself. Code gets them right every time, if the code is right.

### The idea

Think of a teacher marking a maths test with an answer key that says 0.50. A strict marker fails every student who wrote 0.5 or ½; a careless one accepts 0.55. Test the marking on a few papers you've already checked before marking the whole class.

[Figure: Three properties of a good code check. Fast. Repeatable. Graded fairly.]

_A grading bug looks exactly like a weak model._

### Play

**Try to break it.** Switch between the three graders.

#### How strict should the grader be?

Grader for the expected answer 96.124991

Exact matching fails two of the three right answers, the same kind of bug that held a model at 42% on CORE-Bench. A 1% tolerance accepts 96.2, which is wrong. Parsing the number and comparing at the precision the task asked for passes every right answer and neither wrong one. Every grader needs the same test: run it on answers you already know are right and wrong.

**Now say why:** why does rounding to the task's precision beat both other graders?

## How it works

### How it works

#### In one breath

If a failure can be checked by a rule, check it with code: the output parses, the JSON matches the schema, the SQL runs and returns the right rows, the email address exists, the tool name is real, the cited document exists. Code checks are fast, free and repeatable, so they run in CI, as guardrails and on all traffic. Their risk is the grading itself: too strict and right answers fail (Anthropic saw a model jump from 42% to 95% once grading bugs were fixed); too loose and wrong answers pass. Test the grader on known right and wrong answers before trusting it.

#### What code can check

| Failure mode | Code check |
|---|---|
| Broken output format | parse it; validate against a JSON schema |
| Missing SQL filter | parse the query and check the filter is present, or run it on a test database and compare rows with a reference query |
| Invented tool or argument | tool name in the registry; arguments match the tool's schema |
| Wrong recipient | address exists in the client database and belongs to the active deal |
| Irreversible action without asking | send_email never appears before a user confirmation in the trace |
| Invented citation | every cited document ID exists in what was retrieved |
| Code that doesn't work | run the tests in a sandbox |

##### Reference-based or reference-free

Reference-based checks compare with a known answer (the right rows, the expected tool), so they suit fixed test cases. Reference-free checks test a property ("parses", "no card numbers", "cites a retrieved document"), so they also run on live traffic.

##### Grading bugs

Anthropic reported that Claude Opus 4.5 scored 42% on CORE-Bench until the team fixed grading problems. One example: the grader expected "96.124991…" and marked "96.12" wrong. After fixes, the score was 95%. Loose graders fail the other way: a 1% tolerance accepts 96.2 when the answer is 96.12. Before trusting any grader, run it on answers you know are right and wrong, and read some failures to check they're fair.

## In practice

### In practice

#### In practice

- **Code first:** every failure mode with an objective rule gets a code check.

- **Normalise before comparing:** case, whitespace, number formats, key order; compare what matters.

- **Execute when you can:** run SQL and code against test data rather than matching strings.

- **Test the grader:** on known right and wrong answers, and read failures to check they're fair.

- **Watch for 0%:** a task nobody ever passes is usually a broken task or grader.

- **Hand the rest to judges:** tone, completeness and relevance need an LLM judge.

### The answer that sounds right

#### "The model only scores 41%, so let's switch models"

It sounds decisive, but a strict grader can make a good model look bad. Read some failures first: if right answers are failing, fix the grader, not the model.

## Say it

### Before reaching for an LLM judge, what can you check with plain code, and how can code checks go wrong?

#### The interviewer pushes further

Follow-up 1 of 3

When should you use an LLM judge instead of code?

When the criterion needs judgement, like tone, completeness or whether an answer addresses the question. If a rule can decide it, use code.

Follow-up 2 of 3

An agent scores 0% on one task across 100 runs. What do you check first?

The task and the grader. A 0% pass rate over many runs usually means a broken task or a grader that rejects valid answers.

Follow-up 3 of 3

How do you compare generated SQL with a reference?

Run both on a test database and compare the result sets, rather than the query text, since many different queries are correct.

I'd use code for every failure mode with an objective rule: output parses, the schema matches, the SQL runs and returns the reference rows, tool names and arguments are valid, the recipient exists, cited documents were actually retrieved. Code is fast, free and repeatable, so it runs in CI, as guardrails and on all traffic. The risk is the grader itself: too strict fails right answers, like a model held at 42% on CORE-Bench until grading was fixed, and too loose passes wrong ones. So I'd normalise before comparing, execute where possible, and test the grader on known right and wrong answers.

**Key terms and sources**

What code-based evaluators can check (schemas, values, execution results, references), why they come first, and the grading bugs that make a strong agent look weak: overly strict matching, and checks loose enough to pass wrong answers.

#### Sources

- H. Husain and S. Shankar, _Evals for AI Engineers_ (O'Reilly): the Analyze-Measure-Improve lifecycle, error analysis, judges, CI and review

- Anthropic, Demystifying evals for AI agents, Jan 2026

- H. Husain and S. Shankar, AI Evals: everything you need to know (FAQ)

Explanations and examples are ours, built from these sources. Lab numbers are illustrative unless a lab says otherwise. Many recent papers are preprints, and benchmark scores change quickly.
