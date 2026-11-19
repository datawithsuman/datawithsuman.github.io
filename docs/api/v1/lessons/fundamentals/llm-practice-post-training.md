# LLM Practice 2: Post-training and Generation

> 9 scenarios: SFT bugs, reward hacking, DPO and GRPO maths, hallucination, judges, safety.

- Track: Fundamentals › LLMs › Evaluating LLMs and practice
- Type: Interview · 35 min
- Page: https://aimlrounds.com/tracks/fundamentals/llm-practice-post-training/
- Before this: LoRA and QLoRA: Parameter-Efficient Fine-Tuning (`fundamentals/lora-and-qlora`), Benchmarks and Contamination (`fundamentals/benchmarks-and-contamination`)
- Quiz topic: `llmgen`

How to use this page

Give yourself about 5 minutes per question, as in an interview. Say your diagnosis out loud (most likely cause first, then how you'd confirm and fix it), then open the answer and compare.

**The checklist:** check the chat template and loss mask; separate model problems from decoding settings; watch for reward hacking (length, sycophancy) when a learned reward goes up; ground facts and allow abstention; evaluate with both orders, error bars and a human-validated judge.

Question 1 · Easy · SFT

### After SFT, your support model answers well but never stops: it keeps writing a fake customer reply and then answers that too. What's wrong?

Answer: **the model never learned to emit the end-of-turn token, or inference doesn't stop on it**

1. Check the training data: is the end-of-turn token in every assistant turn, and is it inside the loss mask (it must be trained)?

2. Check inference: same chat template as training, and the end-of-turn token set as a stop token.

3. Writing the user's next message is the giveaway: the model is continuing the conversation format because nothing taught it to stop.

**Follow-up:** Why mask the user turns at all? Otherwise most of the loss is spent learning to imitate customers, and the model learns to write user messages.

Question 2 · Easy · decoding

### An LLM extracts order IDs and amounts into JSON. Results differ between runs and ~2% of outputs aren't valid JSON. What settings and techniques fix this?

Answer: **temperature 0 (greedy) plus constrained / structured decoding against a JSON schema**

1. Extraction has one right answer, so sampling only adds variance: use temperature 0.

2. Constrained decoding masks any token that would break the schema, so every output parses.

3. Keep a small labelled set to measure field-level accuracy after the change.

**Follow-up:** Is temperature 0 perfectly deterministic in production? Not always: batching and floating-point order can still change near-ties.

Question 3 · Medium · reward hacking

### During RLHF, the reward-model score keeps rising, responses have grown from 120 to 400 tokens, and agents rate the new checkpoints worse. What's happening and what do you do?

Answer: **reward hacking: the policy is exploiting the reward model's length preference**

1. The reward model is a proxy; optimising it hard finds its blind spots (here, longer answers score higher regardless of quality).

2. Stop at an earlier checkpoint chosen by human or held-out evaluation, not RM score.

3. Raise the KL penalty, add a length penalty or length-normalised reward, retrain the RM on fresh comparisons that include long-but-worse answers, and report length-controlled win rates.

**Follow-up:** How would you spot this automatically? Track response length and RM score against a small human-rated set every few hundred steps; diverging curves are the alarm.

Question 4 · Medium · DPO maths

### With β = 0.1, the policy makes the chosen answer 2 nats more likely than the reference does, and the rejected answer 3 nats less likely. What is the DPO loss for this pair, and how much does it still contribute to the gradient?

Answer: **margin = 0.1 × (2 − (−3)) = 0.5; loss = −ln σ(0.5) ≈ 0.474; gradient weight σ(−0.5) ≈ 0.38**

1. Implicit rewards: 0.1 × 2 = 0.2 (chosen) and 0.1 × (−3) = −0.3 (rejected); margin 0.5.

2. Loss = −ln σ(0.5) = ln(1 + e^(−0.5)) ≈ 0.474 (it starts at ln 2 ≈ 0.693).

3. The gradient is scaled by σ(−margin) ≈ 0.38: the pair is partly learned and still contributes.

**Follow-up:** If both log-ratios drop (chosen −4, rejected −9), what happens to the loss? Same margin, same loss: DPO only cares about the difference, so both answers can become less likely (likelihood displacement).

Question 5 · Medium · GRPO

### In GRPO, a maths prompt gets 4 sampled answers with rewards [1, 0, 0, 0]. Compute the advantages. What happens for a prompt where all 4 are correct?

Answer: **correct answer +1.73, each wrong answer −0.58; all-correct groups give 0 advantage and no learning signal**

1. Mean = 0.25; std = √(0.25 × 0.75) ≈ 0.433.

2. Correct: (1 − 0.25) / 0.433 ≈ +1.73. Wrong: (0 − 0.25) / 0.433 ≈ −0.58.

3. All four correct (or all wrong): every reward equals the mean, so every advantage is 0: filter such prompts or resample (as DAPO does).

**Follow-up:** Why no value model? The group mean is the baseline, saving a whole network's memory and training.

Question 6 · Hard · hallucination

### Your support assistant sometimes invents refund policies ("48-hour festival guarantee"). Product wants it fixed before launch. What's your plan?

Answer: **ground answers in the policy documents, allow and reward abstention, verify, and measure**

1. Retrieve the relevant policy sections (RAG) and instruct the model to answer only from them, citing the section; escalate to a human if nothing relevant is found.

2. Teach abstention: SFT and preference data with "I'm not sure, let me check with an agent" examples; score abstentions above wrong answers in evals.

3. Use tools for anything computable (refund amounts, order status) instead of free-text generation.

4. Add a check: verify each policy claim in the draft against the retrieved text (NLI model or LLM judge) before sending.

5. Measure hallucination, citation accuracy and escalation rate on a labelled set of real questions; review samples weekly.

**Follow-up:** Why not just lower the temperature? If the model doesn't know the policy, its most likely answer is still a confident invention; grounding and abstention fix the cause.

Question 7 · Hard · LLM-as-judge

### A GPT-class judge says your new prompt beats the old one in 62% of 300 support conversations, always with the new answer shown first. Can you ship it?

Answer: **not yet: the setup has position bias, and even without it the margin is about ±5.5 points**

1. The new answer was always first, so position bias alone could produce a >50% win rate. Re-run with both orders and count only consistent verdicts (inconsistent = tie).

2. Margin of error at n = 300, p = 0.62: 1.96 × √(0.62 × 0.38 / 300) ≈ 0.055, so roughly 56–68% if the judge were unbiased.

3. Check length: if new answers are longer, report a length-controlled win rate.

4. Validate the judge on ~200 human-labelled pairs from your domain and use a different model family from the one being tested.

**Follow-up:** What result would convince you? An order-balanced, length-controlled win rate whose interval stays above 50%, from a judge with good agreement with human labels, plus no regression on policy-accuracy checks.

Question 8 · Medium · policy gradient

### One prompt gets 4 sampled answers with rewards [11, 10, 10, 10]. Give each answer's policy gradient weight with no baseline, and with the group mean as a baseline. Why does this matter?

Answer: **No baseline: 11, 10, 10, 10. Group mean: +0.75, −0.25, −0.25, −0.25**

1. With no baseline, all weights are large and positive, so every answer gets pushed up, whichever is good.

2. The group mean is 10.25, so subtracting it gives +0.75 and −0.25.

3. Now the better answer rises and the rest fall. The expected gradient is the same, but there's far less noise.

Does GRPO divide these by anything else? Yes, by the group's standard deviation, here about 0.43, which gives +1.73 and −0.58.

Question 9 · Hard · safety

### You fine-tune an assistant on 20,000 harmless support chats. Quality is up, but your safety test now shows far more harmful requests answered. Nothing in the training data was harmful. What happened, and what do you do before release?

Answer: **Fine-tuning can weaken safety even on harmless data. Fix it, then re-test both kinds of error**

1. Safety behaviour is learned, and narrow training can move the model away from it. Qi et al. (2023) found this with harmless datasets.

2. Mix safety examples into the training data, and lower the number of epochs or the learning rate.

3. Add an output classifier as a separate layer.

4. Re-run the safety tests and an over-refusal test, such as XSTest-style prompts, so you don't just swing to refusing everything.

Why test over-refusal too? A model that refuses everything passes a safety test while being useless.

**More practice and sources**

9 interview questions, easy to hard · answers hidden until you click · checked 29 Oct 2026

Keep practising

Uses the methods in this track: SFT, RLHF, DPO, Reasoning Models, Decoding, Hallucination, LLM-as-a-Judge. Part 1: Pretraining and Scaling Maths.

New lessons: Policy Gradients and Safety Training.
