# Prompt Engineering Practice

> 8 questions: effort costs, layout, many rules, regression sets, optimisers, schemas and migrations.

- Track: AI Engineering › Prompt engineering › Scenarios
- Type: Interview · 35 min
- Page: https://aimlrounds.com/tracks/ai-engineering/prompt-engineering-practice/
- Before this: A Prompt Fix That Broke Production (`ai-engineering/prompt-change-broke-production`)
- Quiz topic: `prompt`
- Sources checked: 2026-11-07 · Text last changed: 2026-11-19 · Version: 2ab9096825

How to use this page

Give yourself about 5 minutes per question, as in an interview. Work each one out, then open the answer and compare.

**The toolkit:** cost = input tokens × input price + (hidden + visible tokens) × output price; P(all N rules kept) ≈ pN; P(test catches a break) = 1 − (1 − f)n; standard error of an accuracy = √(p(1 − p) ÷ n).

Question 1 · Easy · reasoning effort

### Your app sends 10,000 requests a day to a reasoning model. At medium effort it writes about 4,000 hidden tokens per request, and at low effort about 1,000, with the same accuracy on your evaluations. Output costs $10 per million tokens. What does switching to low save?

Answer: **About $300 a day, or $9,000 a month**

1. Tokens saved per request: 4,000 − 1,000 = 3,000.

2. Per day: 3,000 × 10,000 = 30 million tokens.

3. 30 × $10 = $300 a day, and about $9,000 over 30 days.

Answers also arrive faster, as hidden tokens are generated before the visible answer.

Question 2 · Easy · long-context layout

### You pass a 40-page contract and ask one question about it. Where do the contract and the question go in the prompt, and why?

Answer: **The contract first, inside tags, and the question at the end**

1. Anthropic reports that putting the question after long documents can improve answers by up to 30% on complex inputs.

2. Wrap the document in tags, such as <contract>, so it's clearly data, not instructions.

3. Optionally ask the model to quote the relevant clauses before answering.

Google gives the same advice for Gemini: context first, then the question, introduced with a line like "Based on the information above".

Question 3 · Medium · many rules

### A system prompt has 15 rules, each followed 97% of the time when triggered. If a conversation triggers all of them, how often are all kept? What if 5 hard rules move into code?

Answer: **About 63%, rising to about 74%**

1. 0.9715 ≈ 0.633.

2. With 5 rules in code, 10 are left to the model: 0.9710 ≈ 0.737.

3. This assumes independent failures. A stress test found real models fell even faster as rules were added.

Which rules go into code? Hard limits with no judgement needed, such as refund caps and allowed tools.

Question 4 · Medium · regression sets

### A prompt change breaks 1% of requests. With a random test set, how many cases do you need for a 95% chance of seeing at least one broken case? What does a 100-case set give you?

Answer: **About 300 cases. 100 cases give about 63%**

1. Solve 1 − 0.99n ≥ 0.95, so n ≥ ln 0.05 ÷ ln 0.99 ≈ 298.1, which rounds up to 299.

2. With 100 cases: 1 − 0.99100 ≈ 0.634.

Seeing one broken case isn't enough to measure the rate, but it's enough to stop and look.

Question 5 · Medium · optimiser results

### Your baseline prompt scores 78% on a 50-example validation set. An optimiser tries 30 prompts, and the best scores 84%. Is the 6-point gain convincing?

Answer: **No. It's within what chance alone would give**

1. Standard error at 78% with 50 examples: √(0.78 × 0.22 ÷ 50) ≈ 0.059, or about 6 points.

2. So 6 points is about one standard error.

3. Even if all 30 prompts were really no better than the baseline, the best of 30 noisy scores would land about 2 standard errors, or 12 points, above its true value by chance.

What do you do? Score the winner and the baseline on a fresh, larger test set before shipping.

Question 6 · Hard · schema conflicts

### A classifier's category definitions live in the system prompt. Months later, someone edits the definitions there, but the JSON schema's field descriptions still hold the old ones. Accuracy drops on one model, but not another. Why?

Answer: **Schema descriptions act as a second instruction channel, and models weight them differently**

1. In a 2026 study, contradictory schema descriptions cut accuracy by 5 to 45 points, depending on the model.

2. Claude Haiku 4.5 fell from 52.5% to 7.1%, while GPT-4.1 barely moved.

3. Fix: keep definitions in one place and generate both the prompt and the schema from it.

The same study found a required reasoning field before the label added 15 to 24 points where there was room to improve.

Question 7 · Medium · structured output

### A colleague cites a 2024 paper saying JSON output hurts reasoning, and wants to drop structured output. What do you say?

Answer: **The finding is disputed. Test it, and put reasoning before the answer**

1. Tam et al. found format restrictions lowered reasoning scores.

2. A rerun by the Outlines team (dottxt) used matching prompts, and found structured output scored the same or slightly better, such as 0.78 against 0.77 on GSM8K with Llama-3-8B.

3. Either way, a reasoning field before the answer field lets the model think first.

Run both versions on your own evaluation set. The result depends on the model and the prompt.

Question 8 · Hard · migration

### You move an assistant to a reasoning model. The old prompt has a 12-step procedure, "think step by step", and a prefilled start to the answer. Latency triples, and one model returns an error. What do you change?

Answer: **Remove the old scaffolding, then tune the effort setting**

1. The prefill causes the error: some newer models no longer accept a prefilled assistant turn. Ask for the format directly, or use structured output.

2. Replace the 12 steps with the goal, the constraints and the output format. Keep steps only where evaluations show they help.

3. Drop "think step by step", and try low or medium effort to bring latency down.

Re-run the evaluation set after each change, so you know which one mattered.

**More practice and sources**

8 interview questions, easy to hard · answers hidden until you click · checked 7 Nov 2026

Keep practising

Uses Prompt Engineering Patterns, Prompting Reasoning Models, Structured Output, System Prompts with Many Rules, Automatic Prompt Optimisation and A Prompt Fix That Broke Production. Scenarios and prices are invented, so the answers are worked examples, except where a study is named.
