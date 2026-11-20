# Hallucination: Why LLMs Make Things Up

> Why do models guess confidently, and how do you stop an invented refund policy?

- Track: Fundamentals › LLMs › Generation
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/hallucination/
- Before this: In-Context Learning and Chain-of-Thought (`fundamentals/in-context-learning-and-cot`)
- Quiz topic: `llmgen`

## Intuition

### The situation

A customer asks about a refund for a cancelled festival-day order, and the assistant confidently describes a "48-hour festival guarantee" that doesn't exist. In a real case, Moffatt v. Air Canada, a tribunal held an airline responsible for a policy its chatbot invented. The interviewer asks:

> Why do models guess confidently, and how do you stop an invented refund policy?

**Running example:** a customer asks the assistant whether they can get a refund for a cancelled festival-day order. The assistant confidently describes a "48-hour festival guarantee" that doesn't exist. In a real case (Moffatt v. Air Canada, 2024), a tribunal held an airline responsible for a refund policy its chatbot had invented.

#### Fluent, confident, wrong

Hallucinations are dangerous because they look exactly like correct answers. Researchers separate **intrinsic** hallucinations, which contradict the given source (a summary that changes a number), from **extrinsic** ones, which add claims the source can't verify (Ji et al. 2023). For open-domain questions the issue is **factuality**: the claim is false in the world.

### The idea

Think of an exam with no negative marking. Guessing every question is the smart move, even when you have no idea. Add negative marking, and the same student starts leaving blanks. Most mainstream benchmarks are the first kind of exam, so guessing pays.

[Figure: The same model under two gradings. With binary grading it always answers: 51.4 percent right and 48.6 percent wrong. With a penalty for wrong answers it answers only when confident: 10 percent right, 2.4 percent wrong and 87.6 percent I don't know.]

_The same simulated model under two gradings, from the lab. It answers only when that scores best._

### Play

**Try to break it.** Under binary grading, raise the confidence threshold and watch the score. Switch to the penalty, and find the best threshold again.

#### Grade answers as simply right or wrong

2,000 simulated questions; the model has a calibrated confidence for each (it is right with exactly that probability). Penalised grading: +1 right, −3 wrong, 0 for "I don't know", the scheme Kalai et al. propose for a 75% confidence target (penalty t/(1 − t) = 3).

Under **binary grading**, the score is just accuracy, so the best strategy is to **always answer**: score 0.514, but **48.6%** of answers are wrong. Abstaining below 50% confidence would halve the errors (19.1%) yet lowers the score to 0.359, so a leaderboard punishes the more honest model. With **penalised grading**, always answering scores **−0.944**, and the best policy is to answer only above **0.75** confidence: 10.0% right, just 2.4% wrong, 87.6% "I don't know". The model was the same in every case; only the incentive changed. Kalai et al. found most mainstream benchmarks use binary grading, and argue this is a main reason hallucination persists after post-training.

**Now say why:** nothing about the model changed, so why did the errors fall to 2.4%?

## How it works

### How it works

#### In one breath

A **hallucination** is fluent, confident content that isn't supported by the source or by reality: an invented refund policy, a fake citation, a wrong date. It's not a rare bug but a consequence of how models are built: a next-token predictor must produce _something_ plausible even for facts it saw once or never (Kalai et al. 2025 argue that if 20% of some kind of fact appears only once in training, expect at least ~20% errors on it), fine-tuning on facts the model doesn't know encourages confident guessing, and most benchmarks score "I don't know" the same as a wrong answer, so **guessing is rewarded**. Fixes: ground answers in retrieved documents with citations, let the model abstain and reward it for doing so, check answers with tools or a second pass, and measure hallucination rates on your own data. What you'll be able to do after this: explain the main causes of hallucination, design mitigations for a product, and explain why scoring rules matter.

#### Where hallucinations come from

- **Pre-training statistics:** the model learns plausible patterns, not a database. Facts seen once (a restaurant's founding year, a person's birthday) can't be reliably separated from plausible alternatives; Kalai et al. show errors on such facts are statistically unavoidable for a well-calibrated base model.

- **Post-training:** fine-tuning on answers to questions the model didn't know teaches it to answer confidently anyway; Gekhman et al. (2024) found such examples are learned slowly and increase hallucination. Preference tuning can reward confident, complete-sounding answers.

- **Decoding:** sampling can pick a low-probability wrong continuation, and once written, the model conditions on it (it rarely retracts).

- **Evaluation incentives:** the subject of the lab in the Intuition tab.

## In practice

### In practice

#### Reducing and catching hallucinations

- **Ground it:** retrieval-augmented generation (Lewis et al. 2020) with instructions to answer only from the retrieved policy text and cite it; tools for anything computable (refund amounts, order status).

- **Allow and reward abstention:** include "I'm not sure, let me connect you to an agent" examples in SFT and preference data; score abstentions above wrong answers in your evals.

- **Detect:** SelfCheckGPT (Manakul et al. 2023) samples several answers and flags claims that don't agree across samples; Chain-of-Verification (Dhuliawala et al. 2023) has the model plan and answer verification questions before finalising; FActScore (Min et al. 2023) splits long answers into atomic facts and checks each against a knowledge source.

- **Decode conservatively** for factual answers (low temperature) and constrain output to known options where possible (e.g. pick a policy ID).

- **Measure:** track hallucination rate, citation precision and abstention rate on a labelled set of real questions, and review samples by hand.

Images add their own failures: see Vision-Language Models.

#### Plausible is not true, and guessing is rewarded

Models hallucinate because they are trained to produce plausible text and evaluated in ways that reward guessing; ground them in sources, let them say "I don't know", and score that honesty higher than a confident mistake.

### The answer that sounds right

#### "It's a decoding bug, and a lower temperature will fix it"

It sounds right, since the bad text appears during generation. But it comes from training objectives and incentives. Lowering the temperature removes sampling randomness, but if the most likely answer is wrong, greedy decoding states it confidently. Bigger models don't solve it either: they hallucinate less on common facts, but still on rare ones.

## Say it

### Why do models guess confidently, and how do you stop an invented refund policy?

#### The interviewer pushes further

Follow-up 1 of 3

Does RAG eliminate hallucination?

No. The model can ignore or misread the retrieved text, retrieval can miss the right document, and it can blend sources. Check citation faithfulness and handle "not found" explicitly.

Follow-up 2 of 3

How would you detect hallucinations without ground truth?

Sample several answers and check consistency (SelfCheckGPT), ask the model to verify individual claims, or use an NLI model / LLM judge to check each claim against the source documents.

Follow-up 3 of 3

Why does lowering temperature only partly help?

It removes sampling randomness, but if the model's most likely answer is wrong (an unknown fact), greedy decoding states it confidently.

#### The 30-second answer

Hallucinations are fluent but unsupported or false outputs. They come from next-token training, which learns plausible patterns and can't reliably store rarely seen facts; from fine-tuning that teaches confident answers on unknown facts; from sampling; and from evaluations that give no credit for abstaining, so guessing maximises scores. To reduce them in a product I'd ground answers in retrieved sources with citations, use tools for computable facts, train and prompt the model to abstain when unsure and score abstentions above errors, add a verification step or sample-consistency check, and measure hallucination and abstention rates on real labelled questions.

**Go further**

#### What not to say

- "Bigger models don't hallucinate." They hallucinate less on common facts, but still on rare ones.

- "It's a decoding bug." It comes from training objectives and incentives.

**Key terms and sources**

What hallucinations are (unsupported or false content stated fluently), why they arise from pre-training statistics, fine-tuning and evaluations that reward guessing, how to detect them (sampling consistency, verification, FActScore), and how to reduce them in products (retrieval with citations, abstention, tools, calibrated grading) · built from Kalai et al. (Why Language Models Hallucinate, 2025), Ji et al. (Survey of Hallucination, ACM CSUR 2023), Manakul et al. (SelfCheckGPT, EMNLP 2023), Min et al. (FActScore, EMNLP 2023), Dhuliawala et al. (Chain-of-Verification, 2023), Gekhman et al. (EMNLP 2024) and Lewis et al. (RAG, NeurIPS 2020) · checked 29 Oct 2026

#### Sources

1. A. Kalai, O. Nachum, S. Vempala & E. Zhang, "Why Language Models Hallucinate", 2025, [arXiv:2509.04664](https://arxiv.org/abs/2509.04664).

2. Z. Ji et al., "Survey of Hallucination in Natural Language Generation", ACM Computing Surveys 2023, [arXiv:2202.03629](https://arxiv.org/abs/2202.03629).

3. P. Manakul et al., "SelfCheckGPT", EMNLP 2023, [arXiv:2303.08896](https://arxiv.org/abs/2303.08896); S. Min et al., "FActScore", EMNLP 2023, [arXiv:2305.14251](https://arxiv.org/abs/2305.14251).

4. S. Dhuliawala et al., "Chain-of-Verification Reduces Hallucination in Large Language Models", 2023, [arXiv:2309.11495](https://arxiv.org/abs/2309.11495); Z. Gekhman et al., EMNLP 2024, [arXiv:2405.05904](https://arxiv.org/abs/2405.05904).

5. P. Lewis et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks", NeurIPS 2020, [arXiv:2005.11401](https://arxiv.org/abs/2005.11401); Moffatt v. Air Canada, 2024 BCCRT 149.
