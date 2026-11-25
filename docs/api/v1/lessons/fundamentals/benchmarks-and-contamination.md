# Benchmarks and Contamination

> Is a 3-point GPQA gap real, and did the model see the test?

- Track: Fundamentals › LLMs › Evaluating LLMs and practice
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/benchmarks-and-contamination/
- Before this: Pretraining Data: Deduplication, Filtering and Mixtures (`fundamentals/pretraining-data`)
- Quiz topic: `llmgen`
- Sources checked: 2026-10-29 · Text last changed: 2026-11-20 · Version: f73bc20a7f

## Intuition

### The situation

Two candidate models for the support assistant differ by 3 points on GPQA Diamond and 1 point on MMLU. A colleague wants to pick the one with the higher scores. The interviewer asks:

> Is a 3-point GPQA gap real, and did the model see the test?

**Running example (evaluation):** two candidate models for the support assistant differ by 3 points on GPQA Diamond and 1 point on MMLU. The team must decide whether either gap means anything, and how to test what actually matters to them.

#### Comparing models needs shared, fair tests

Generated text has no single right answer, and every lab reports the benchmarks it looks best on. Shared benchmarks give a common yardstick, but only if the questions are hard enough, correct, unseen during training, and numerous enough that differences aren't noise.

### The idea

Think of ranking students by a very short class test. On 30 questions, one lucky guess moves your score by over 3 points, so a small gap means little. And if the paper leaked, the score only tells you who saw it. A good test needs enough questions, correct answers and questions nobody has seen.

[Figure: 95 percent margins at 60 percent accuracy. MMLU plus or minus 0.8 points, SWE-bench Verified 4.3, GPQA Diamond 6.8 and AIME 17.5.]

_95% margin of error in points, at 60% accuracy, from the lab._

### Play

**Try to break it.** Switch between MMLU, SWE-bench Verified, GPQA Diamond and AIME 2024. Then move the model accuracy, and watch the gap needed between two models.

#### "Model A scored 3 points higher, so it's better"

Normal approximation for a proportion: margin = 1.96 √(p(1 − p)/n); gap needed = 1.96 √(2p(1 − p)/n) for two independent evaluations. Paired tests on the same questions (Miller 2024) are tighter, and repeated sampling adds its own variance.

At 60% accuracy, **GPQA Diamond**'s 198 questions give a margin of **±6.8 points**; two models need to differ by roughly **9.7 points** before the gap is clearly real, so the team's 3-point difference is noise. **MMLU**'s 14,042 questions narrow the margin to ±0.8, but a 1-point gap is still borderline, and MMLU is saturated and partly mislabelled. **AIME** is the extreme: with 30 problems each one is worth 3.33 points and the margin is ±17.5, which is why labs report averages over many samples per problem. **SWE-bench Verified** sits in between at ±4.3.

**Now say why:** GPQA Diamond is a respected test, so why is a 3-point gap on it noise?

## How it works

### How it works

#### In one breath

Benchmarks are fixed test sets that let us compare models on the same questions: **MMLU** (57 subjects, multiple choice), **GPQA** (graduate-level science questions that experts get 65% right and skilled non-experts with web access only 34%), **AIME** (competition maths), **SWE-bench Verified** (500 real GitHub issues the model must fix so the tests pass). Three things make scores misleading. **Noise:** a 198-question benchmark has a 95% margin of about ±7 points, so small leaderboard gaps mean little. **Saturation and label errors:** once models score 90%+, remaining errors are often in the benchmark itself (about 6.5% of MMLU questions have errors). **Contamination:** test questions leak into training data, so scores measure memory; on a fresh GSM8K-style set (GSM1k), some models dropped by up to 13 points. Always pair public benchmarks with your own held-out evaluation. What you'll be able to do after this: describe the main benchmarks, compute a benchmark's error bars, and explain how contamination is detected and avoided.

#### The benchmarks you'll be asked about

| Benchmark | What it tests | Notes |
|---|---|---|
| **MMLU** (2021) | 57 subjects, 4-option multiple choice; 14,042 test questions | saturated near 90%; ~6.5% of questions have errors; MMLU-Pro uses 10 options and harder questions |
| **GPQA Diamond** | 198 "Google-proof" biology, physics and chemistry questions | experts 65%, skilled non-experts with 30+ minutes of web search 34% |
| **AIME** | 30 competition maths problems per year, integer answers | new problems each year limit contamination; tiny, so very noisy |
| **SWE-bench Verified** | 500 real GitHub issues from Python repos; the patch must make hidden tests pass | human-validated subset of SWE-bench's 2,294 issues; OpenAI, which created it, stopped reporting it in 2026, citing contamination and flawed tests |
| Others | HumanEval (saturated), GSM8K (saturated), Humanity's Last Exam, LiveCodeBench (rolling, post-cutoff problems), MT-Bench / Arena (open-ended; next lesson) | live and rolling benchmarks fight contamination |

## In practice

### In practice

#### When the test set is in the training data

- **How it happens:** benchmarks are public on the web, copied into forums, GitHub and datasets, and scraped into pre-training corpora; fine-tuning sets can include near-copies.

- **Evidence:** Zhang et al. (2024) wrote GSM1k, 1,000 new problems in GSM8K's style; several model families scored up to 13 points lower than on GSM8K, while frontier models showed little drop.

- **Detection:** n-gram overlap between training data and test sets; canary strings (unique markers in benchmark files, as in BIG-bench) that should never appear in training data; membership tests such as Min-K% Prob (unusually high likelihood on a test item's rarest tokens suggests it was seen).

- **Mitigation:** private held-out sets, rolling benchmarks with problems newer than the model's cutoff (LiveCodeBench, new AIME years), decontaminating training data, and reporting contamination analyses.

**For your own product:** build a held-out set of real, representative tasks (support tickets with correct resolutions), never train on it, version it, and report confidence intervals. It predicts deployment quality far better than a public leaderboard.

**A benchmark's life cycle: SWE-bench Verified.** In February 2026, OpenAI said it would stop reporting this benchmark, which it had helped create. It audited 27.6% of the problems its model had failed, and found that at least 59.4% of those had tests that rejected correct solutions. Frontier models could also reproduce some of the original fixes from memory. So rising scores increasingly measured exposure to the test. It recommended SWE-bench Pro instead, which keeps some of its data private. Expect any public benchmark to wear out this way, and re-check how much your own favourite is still telling you.

#### A score is only as good as its test set

Benchmark numbers need error bars, correct labels and unseen questions; small gaps, saturated tests and contaminated data turn leaderboards into noise, so decisions should rest on your own held-out evaluations.

### The answer that sounds right

#### "High MMLU means it'll work for our users"

It sounds right, since it's a broad knowledge test. But MMLU is saturated near 90%, and about 6.5% of its questions have errors. Benchmarks can also be contaminated. And a 1-point gap needs error bars before it means anything. A held-out set of your own real tasks, such as support tickets with correct resolutions, predicts deployment quality far better than a public leaderboard.

## Say it

### Is a 3-point GPQA gap real, and did the model see the test?

#### The interviewer pushes further

Follow-up 1 of 3

How many examples does an eval set need?

For ±3 points at 95% confidence near 50% accuracy, n ≈ (1.96 × 0.5 / 0.03)² ≈ 1,070. To detect smaller differences, use paired comparisons on the same items.

Follow-up 2 of 3

How would you check whether a model has seen a benchmark?

Search training data for n-gram overlap or canary strings if you have it; otherwise compare performance on the original vs. paraphrased or newly written equivalent questions, and use membership-inference scores.

Follow-up 3 of 3

Why does SWE-bench need a "Verified" subset?

Some original tasks had underspecified issues or tests that rejected valid fixes; human annotators filtered to 500 tasks. Even so, a 2026 audit by OpenAI found many remaining failures were due to flawed tests, and that models could recall some fixes from memory.

#### The 30-second answer

LLM benchmarks include MMLU for broad knowledge, GPQA Diamond for expert-level science, AIME for competition maths and the SWE-bench family for real coding tasks, though its creator has now dropped SWE-bench Verified. I treat scores with care for three reasons: small test sets are noisy, for example GPQA Diamond's 198 questions give about plus or minus 7 points at 60 percent; older benchmarks are saturated and contain label errors; and test data leaks into training, which GSM1k exposed with drops of up to 13 points for some models. Contamination is detected with n-gram overlap, canary strings and membership-inference tests, and avoided with private or rolling benchmarks. For a product, I'd rely on our own held-out evaluation set.

**Go further**

#### What not to say

- "Model A is better: it scored 1 point higher." Check the error bars.

- "High MMLU means it'll work for our users." Test on your own tasks.

**Key terms and sources**

How LLMs are compared: knowledge and reasoning benchmarks (MMLU, GPQA, AIME), agentic and coding benchmarks (SWE-bench Verified), what makes a benchmark trustworthy, statistical noise from small test sets, saturation and label errors, and test-set contamination and how to detect it · built from Hendrycks et al. (MMLU, ICLR 2021), Rein et al. (GPQA, COLM 2024), Jimenez et al. (SWE-bench, ICLR 2024), OpenAI (SWE-bench Verified, 2024), Gema et al. (Are We Done with MMLU?, NAACL 2025), Zhang et al. (GSM1k, NeurIPS 2024), Shi et al. (Min-K% Prob, ICLR 2024) and Miller (Adding Error Bars to Evals, 2024) · checked 29 Oct 2026

#### Sources

1. D. Hendrycks et al., "Measuring Massive Multitask Language Understanding", ICLR 2021, [arXiv:2009.03300](https://arxiv.org/abs/2009.03300); A. Gema et al., "Are We Done with MMLU?", NAACL 2025, [arXiv:2406.04127](https://arxiv.org/abs/2406.04127).

2. D. Rein et al., "GPQA: A Graduate-Level Google-Proof Q&A Benchmark", COLM 2024, [arXiv:2311.12022](https://arxiv.org/abs/2311.12022).

3. C. Jimenez et al., "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?", ICLR 2024, [arXiv:2310.06770](https://arxiv.org/abs/2310.06770); OpenAI, "Introducing SWE-bench Verified", 2024; OpenAI, ["Why we no longer evaluate SWE-bench Verified"](https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/), 2026, as reported by [The Decoder](https://the-decoder.com/openai-wants-to-retire-the-ai-coding-benchmark-that-everyone-has-been-competing-on/) and [Gigazine](https://gigazine.net/gsc_news/en/20260429-swe-bench-verified).

4. H. Zhang et al., "A Careful Examination of Large Language Model Performance on Grade School Arithmetic" (GSM1k), NeurIPS 2024 Datasets & Benchmarks, [arXiv:2405.00332](https://arxiv.org/abs/2405.00332); W. Shi et al., "Detecting Pretraining Data from Large Language Models" (Min-K% Prob), ICLR 2024, [arXiv:2310.16789](https://arxiv.org/abs/2310.16789).

5. E. Miller, "Adding Error Bars to Evals: A Statistical Approach to Language Model Evaluations", 2024, [arXiv:2411.00640](https://arxiv.org/abs/2411.00640).
