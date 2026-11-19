# LLM Judges: Pairwise Preferences and Pass/Fail Checks

> Can you trust a GPT judge's 62% win rate, and how do you write one for your app?

- Track: AI Engineering › Applied Evals › Lessons
- Type: Concept · 22 min
- Page: https://aimlrounds.com/tracks/ai-engineering/llm-as-a-judge/
- Before this: Error Analysis: From Traces to Failure Rates (`ai-engineering/error-analysis`), Benchmarks and Contamination (`fundamentals/benchmarks-and-contamination`)
- Quiz topic: `evals`

## Intuition

### The situation

The team changes the assistant's prompt, and wants to compare replies across 3,000 real conversations. Human review would take weeks, so they use a GPT judge, and the new prompt wins 62% of pairs. The interviewer asks:

> Can you trust a GPT judge's 62% win rate?

**Running example:** the team changes the assistant's prompt and wants to know whether replies got better across 3,000 real support conversations. Human review of every pair would take weeks.

#### No answer key for open-ended answers

Overlap metrics like BLEU and ROUGE reward matching words, not helpfulness, and benchmarks with fixed answers don't cover tone, completeness or policy compliance. We need preference judgements: given the same question, which reply is better?

### The idea

Think of a food critic who tends to favour whichever dish arrives first. So you serve each pair twice, swapping the order, and only count the verdict if they pick the same dish both times. You lose some pairs, but the ones you keep are about the food, not the serving order.

[Figure: With position bias 1.0, judging once agrees with humans 66.2 percent of the time on every pair. Judging both orders and keeping consistent verdicts agrees 77.5 percent of the time on 59.7 percent of pairs.]

_From the lab's simulation, with a position bias of 1.0._

### Play

**Try to break it.** Set the position bias to 1.0, and compare judging once with judging both orders. Then set the bias to 0.

#### Ask the judge once, in one order

3,000 simulated answer pairs with a hidden quality difference; humans and the judge both prefer the better answer with a logistic probability, and the judge adds the bias (in logits) to whichever answer is shown first. Even an unbiased judge disagrees with humans sometimes, because humans disagree with each other too. Fixed seed.

With a position bias of 1.0, judging each pair once agrees with the human verdict **66.2%** of the time, and **40.3%** of verdicts flip when the two answers are swapped: the judge is partly reading the layout, not the content. Asking twice with the order swapped and keeping only consistent verdicts raises agreement to **77.5%**, at the cost of setting aside the 40.3% of inconsistent pairs as ties (59.7% kept). Wang et al. (2024) found exactly this kind of position sensitivity in GPT-4 and ChatGPT judges, enough to flip rankings between models. Set the bias to 0 and judging once agrees 68.6%: the remaining gap is the noise in human labels themselves.

**Now say why:** at zero bias, the judge still agrees with humans only 68.6% of the time. Why isn't that closer to 100%?

## How it works

### How it works

#### In one breath

For open-ended tasks (support replies, summaries, advice) there is no answer key, so we ask a judge which answer is better. **Humans** are the gold standard but slow and costly; **Chatbot Arena** crowdsources pairwise votes on anonymous models and fits **Bradley–Terry** ratings. An **LLM judge** is cheap and fast: Zheng et al. (2023) found GPT-4's verdicts agreed with human experts over 80% of the time, about as often as humans agreed with each other. But judges are **biased**: they favour the answer shown first (**position bias**), longer answers (**verbosity bias**), and their own model family (**self-preference**). Standard fixes: evaluate both orders and keep only consistent verdicts, control for length, give a rubric or reference answer, and validate the judge against a few hundred human labels. Arenas can be gamed too, e.g. by testing many private variants and publishing the best.What you'll be able to do after this: set up an LLM judge with bias controls, interpret Arena ratings, and explain why judges must be validated against humans.

#### Human arenas and LLM judges

$$ P(A \succ B) = \frac{1}{1 + 10^{-(R_A - R_B)/400}} $$

Chiang et al., "Chatbot Arena: An Open Platform for Evaluating LLMs by Human Preference", ICML 2024, arXiv:2403.04132. Ratings come with confidence intervals; overlapping intervals mean no clear ranking.

- **chance A beats B**: Bradley–Terry, the same model behind reward models: each model has a strength score, and win probability depends only on the difference.

- **rating difference**: Arena reports ratings on an Elo-like scale: a 100-point gap means about a 64% expected win rate; 400 points, about 91%.

- **Pairwise judging:** show the judge the question and two answers, ask which is better (or tie). Most sensitive for comparing two systems.

- **Single-answer grading:** score one answer 1–10 against a rubric (MT-Bench, G-Eval). Scales to many systems but is less stable.

- **Reference-guided:** give the judge a correct answer or policy text; essential for maths and factual questions, where judges otherwise accept confident wrong answers.

#### Pass/fail judges for one failure mode each

Arena-style preference judging compares models. For your own app, you usually need a judge per failure mode found in error analysis, answering pass or fail. A good judge prompt has four parts:

1. **One criterion:** "is the tone right for a luxury-buyer client", not "is this email good".

2. **Precise pass and fail definitions:** taken from your failure-mode notes.

3. **Examples:** clear passes and clear fails from human-labelled traces, kept out of the data used to test the judge.

4. **Structured output:** a short reasoning, then the verdict, as JSON.

Common mistakes: no examples in the prompt; one judge scoring several criteria at once; skipping the check against human labels; and not re-checking after the judge's model changes. Anthropic also suggests letting the judge answer "unknown" rather than forcing a guess. Run the judge 3–5 times on the same trace: if the verdict flips, the criterion needs a clearer definition. Then measure and correct it as in Can You Trust Your Judge?

## In practice

### In practice

#### Building a judge you can trust

- **Biases to control:** position (swap and average), verbosity (length-controlled win rates; length-controlled AlpacaEval raised correlation with Arena from 0.94 to 0.98), self-preference (use a judge from a different model family, or several), and style (Arena added "style control" to separate formatting from substance).

- **Give it a rubric** tied to your product: correct refund policy, polite tone, no invented promises; ask for a short rationale before the verdict.

- **Validate:** label 200–500 pairs by hand, measure judge–human agreement (and human–human agreement as the ceiling), and re-check whenever the judge model or prompt changes.

- **Arena caveats:** "The Leaderboard Illusion" (Singh et al. 2025) reported that some providers tested many private variants before release (Meta tested 27 before Llama 4) and that a few providers received far more battle data, which can inflate rankings. Treat Arena as one signal of general chat preference, not task-specific quality.

#### A judge is a model too: evaluate it

LLM judges make open-ended evaluation cheap and roughly human-level, but only after you control their position, length and self-preference biases and check them against real human labels.

### The answer that sounds right

#### "GPT-4 as a judge is unbiased"

It sounds right, since a model has no opinions of its own. But it has measurable biases. In the lab, 40.3% of verdicts flip when the answers are swapped, and Wang et al. found position sensitivity strong enough to change rankings between models. Arena rank won't settle it either: it reflects the general chat preferences of its voters, not your task.

## Say it

### Can you trust a GPT judge's 62% win rate?

#### The interviewer pushes further

Follow-up 1 of 3

Pairwise or pointwise grading?

Pairwise is more sensitive and consistent for comparing two systems; pointwise scales to many systems and gives absolute monitoring scores but drifts and clusters around a few values.

Follow-up 2 of 3

Can the judge be the same model you're evaluating?

Avoid it: self-preference bias inflates its own outputs. Use a different family or an ensemble.

Follow-up 3 of 3

What does a 50-point Arena gap mean?

About a 57% expected win rate, and only meaningful if the confidence intervals don't overlap.

#### The 30-second answer

For open-ended outputs we use preference evaluation. Chatbot Arena collects human pairwise votes on anonymous models and fits Bradley–Terry ratings. LLM-as-a-judge uses a strong model to compare or grade answers; Zheng et al. found GPT-4 agreed with experts over 80 percent of the time, similar to human–human agreement. Judges have position, verbosity and self-preference biases, so I'd judge both orders and keep consistent verdicts, control for length, use a rubric or reference answer, use a judge from a different model family, and validate against a few hundred human labels before trusting it. For a product I'd compare the old and new prompt pairwise on real conversations and report the win rate with a confidence interval.

**Go further**

#### What not to say

- "GPT-4 as a judge is unbiased." It has measurable biases.

- "Arena rank tells me which model is best for my task." It reflects general chat preferences of its voters.

**Key terms and sources**

Evaluating open-ended answers when there's no single correct output: human pairwise preference and Chatbot Arena's Bradley–Terry ratings, LLM judges (pairwise, single-answer grading, reference-guided), their biases (position, verbosity, self-preference), how to measure and reduce them, and how arenas can be gamed · built from Zheng et al. (MT-Bench and Chatbot Arena, NeurIPS 2023), Chiang et al. (Chatbot Arena, ICML 2024), Wang et al. (Large Language Models are not Fair Evaluators, ACL 2024), Dubois et al. (Length-Controlled AlpacaEval, 2024), Liu et al. (G-Eval, EMNLP 2023) and Singh et al. (The Leaderboard Illusion, 2025) · checked 29 Oct 2026

#### Sources

1. L. Zheng et al., "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena", NeurIPS 2023, arXiv:2306.05685.

2. W.-L. Chiang et al., "Chatbot Arena: An Open Platform for Evaluating LLMs by Human Preference", ICML 2024, arXiv:2403.04132.

3. P. Wang et al., "Large Language Models are not Fair Evaluators", ACL 2024, arXiv:2305.17926.

4. Y. Dubois et al., "Length-Controlled AlpacaEval", 2024, arXiv:2404.04475; Y. Liu et al., "G-Eval", EMNLP 2023, arXiv:2303.16634.

5. S. Singh et al., "The Leaderboard Illusion", 2025, arXiv:2504.20879.
