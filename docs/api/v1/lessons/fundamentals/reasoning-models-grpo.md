# Reasoning Models: RLVR, GRPO and Test-Time Compute

> How did DeepSeek-R1 learn to think from right/wrong rewards alone?

- Track: Fundamentals › LLMs › Post-training
- Type: Concept · 25 min
- Page: https://aimlrounds.com/tracks/fundamentals/reasoning-models-grpo/
- Before this: Reward Models and RLHF (PPO) (`fundamentals/rlhf-and-reward-models`)
- Related: DeepSeek-R1 (`papers/deepseek-r1`)
- Quiz topic: `post`

## Intuition

### The situation

The assistant must compute refunds: a ₹420 order arrived 40 minutes late, and the policy refunds 10% for delays over 30 minutes. A wrong number costs real money, but the right answer can be checked. Human-written reasoning traces are scarce and expensive. The interviewer asks:

> How did DeepSeek-R1 learn to think from right or wrong rewards alone?

**Running example:** the assistant must compute refunds correctly: "A ₹420 order arrived 40 minutes late and the policy refunds 10% for delays over 30 minutes: how much is refunded?" Real cases chain several such rules. A wrong number is a real cost, and the right answer is checkable.

#### Multi-step problems need more than one forward pass

Answering a multi-step maths question in a single token is hard: the model needs room to work things out. Chain-of-thought prompting helps, but the model was never trained to reason well over thousands of tokens, to notice mistakes and to try again. Human-written reasoning traces are scarce and expensive. Can the model learn to reason from just the correctness of its final answers?

### The idea

Think of a student given only an answer key, with no worked solutions. Try a problem eight times, and reinforce the attempts that got it right compared with the rest. Get it right every time, or never, and you learn nothing from that problem. Over time, the student learns to check their own work.

[Figure: Group-relative advantages for 8 samples. With 1 of 8 correct, the right answer gets plus 2.65 and each wrong one minus 0.38. With 4 of 8, plus 1 and minus 1. With 0 or 8 correct, every advantage is 0.]

_From the GRPO lab in the Maths tab. Hard problems the model occasionally solves teach the most._

### Play

**Try to break it.** This lab is about inference, once the model is trained. At 40% per sample, raise the samples per question. Then drop to 20%, and compare the majority vote with pass@k.

#### Sample more, then vote or verify

Wrong answers are spread evenly over 4 different wrong values. Majority vote = most common final answer (ties split). pass@k counts a question as solved if any sample is right, which needs a verifier to pick it. 4,000 simulated questions, fixed seed.

With a 40% chance per sample, **self-consistency** (majority voting, Wang et al. 2023) lifts accuracy to **53.9%** with 5 samples and **78.6%** with 16, because wrong answers scatter while right ones agree. But at **20%**, no better than each wrong answer, voting stays around **20%** no matter how many samples. With a reliable **verifier** (unit tests, a checker, a good reward model), pass@k is what you get: 97.2% at 20% with 16 samples. Snell et al. (2024) found that allocating test-time compute adaptively can be over 4× more efficient than best-of-N, and can let a smaller model beat one about 14× larger on problems where the small model has a reasonable chance of success. Reasoning models internalise this: one long chain of thought explores, checks and revises before answering.

**Open question.** Yue et al. (2025) found that RLVR-trained models win at small k, but their base models often reach higher pass@k at large k: RL may mostly sharpen the model towards solutions it could already find, rather than create new reasoning abilities.

##### Beyond maths: tools and thinking budgets

- **Training tool use:** Qwen3's final RL stage lets the model run complete, multi-turn tool interactions with real environment feedback. On Qwen's in-house ToolUse test, Qwen3-32B with thinking on rose from 63.3 after reasoning RL to 85.5 after this stage.

- **Thinking on demand:** one model can now cover both modes. Qwen3 is trained to follow /think and /no_think flags.

- **Thinking budgets:** users can limit how much the model reasons, to trade quality against speed. Qwen3-235B's scores rose smoothly with the budget on maths, coding and science tests.

**Now say why:** why does voting stop helping at 20%, and why doesn't that stop a verifier?

## Maths

### Maths

#### In one breath

For maths, code and other checkable tasks we don't need a learned reward model: a program can **verify** the final answer or run the tests. **RL with verifiable rewards (RLVR)** samples many attempts per problem, rewards the correct ones, and reinforces whatever reasoning led there. **GRPO** (DeepSeekMath) makes this cheap: instead of a value model, it compares each attempt with the others in its group, **advantage = (reward − group mean) / group std**. Trained this way from a base model, **DeepSeek-R1-Zero** went from 15.6% to 71.0% on AIME 2024, and learned on its own to write longer chains of thought, re-check and backtrack. The other half of the story is **test-time compute**: thinking longer, sampling several answers and voting, or searching with a verifier often buys more accuracy than a bigger model. What you'll be able to do after this: explain RLVR and GRPO's advantage, what R1-Zero showed, and the pass@k vs majority-vote trade-off at inference.

#### Verifiable rewards and group-relative advantages

$$ A_i = \frac{{r_i} - {\mathrm{mean}(r_1,\dots,r_G)}}{{\mathrm{std}(r_1,\dots,r_G)}} $$

Shao et al., "DeepSeekMath", [arXiv:2402.03300](https://arxiv.org/abs/2402.03300). Every token of answer i gets advantage Ai, used in a PPO-style clipped objective with a KL term to the reference. The term RLVR comes from Tülu 3 (Lambert et al. 2024).

- **verifiable reward**: 1 if the final answer matches (or the code passes the tests), else 0; DeepSeek-R1-Zero also gave a format reward for putting its reasoning inside think tags. No reward model to hack.

- **group mean**: Sample G answers (e.g. 8–64) to the same prompt; the mean reward is the baseline, replacing PPO’s learned value model.

- **group std**: Normalising by the spread keeps advantages on a similar scale whatever the problem’s difficulty.

8 sampled answers to a refund problem, 10% of a ₹420 order, (correct answer ₹42); reward 1 if correct, else 0.

With **4 of 8** correct, correct answers get +1 and wrong ones −1. With only **1 of 8** correct, the rare success gets a big push (**+2.65**) and each failure a small one (−0.38): hard problems the model occasionally solves teach the most. With **0 or 8** correct, every advantage is 0: problems that are too hard or too easy teach nothing, which is why later recipes like DAPO filter such groups out and keep training data at the edge of the model's ability.

For where the baseline comes from, read Policy Gradients for LLMs.

## In practice

### In practice

#### What DeepSeek-R1-Zero showed, and what went wrong

- **Pure RL works:** starting from DeepSeek-V3-Base with no SFT, GRPO with only accuracy and format rewards raised AIME 2024 pass@1 from **15.6% to 71.0%** (86.7% with majority voting), comparable to OpenAI's o1-0912.

- **Emergent behaviour:** responses grew from hundreds to thousands of tokens over training, and the model began re-checking and backtracking ("wait, let me re-evaluate"), without being shown examples of it.

- **The trap:** R1-Zero's reasoning was hard to read and mixed languages. DeepSeek-R1 added a small "cold-start" SFT set of readable long chains of thought, then RL, then rejection-sampled SFT and a final RL stage for general helpfulness.

- **Why not a learned reward model?** DeepSeek avoided neural reward models for reasoning because large-scale RL tends to hack them (reward hacking); rule-based checks are much harder to fool, though models can still exploit weak test suites.

#### Reward the outcome, let the reasoning emerge

Where answers can be checked, RL on outcome rewards with group-relative advantages teaches models to spend tokens reasoning, and that inference-time thinking becomes a new axis to scale alongside parameters and data.

### The answer that sounds right

#### "Reasoning models were trained on human chain-of-thought data"

It sounds right, since reasoning looks like something you'd have to demonstrate. But R1-Zero learned from outcome rewards alone, and re-checking and backtracking emerged without examples. R1 added only a small cold-start set, because R1-Zero's reasoning was hard to read and mixed languages. DeepSeek also avoided learned reward models here, because large-scale RL tends to hack them.

## Say it

### How did DeepSeek-R1 learn to think from right or wrong rewards alone?

#### The interviewer pushes further

Follow-up 1 of 3

Why does GRPO not need a critic?

The average reward of the other samples for the same prompt is a good baseline, so a learned value model is unnecessary; this saves memory and avoids training a second network.

Follow-up 2 of 3

What happens if all samples in a group get the same reward?

All advantages are zero and the prompt gives no gradient; filter or re-sample such prompts and keep training problems at the right difficulty.

Follow-up 3 of 3

How would you apply RLVR to a non-maths product task?

Find checkable sub-goals: JSON that validates against a schema, SQL that returns the right rows, code that passes tests, refund amounts that match a calculator. Use a learned judge only where no check exists, and watch for hacking.

#### The 30-second answer

Reasoning models are trained with reinforcement learning on verifiable rewards: for maths or code, sample several attempts per problem, reward the ones whose final answer or tests check out, and reinforce them. GRPO, from DeepSeekMath, drops PPO's value model and uses the group of samples as a baseline, advantage equals reward minus the group mean, divided by the group standard deviation. DeepSeek-R1-Zero used this from a base model and went from about 16 to 71 percent on AIME 2024, with long chains of thought and self-checking emerging on their own. At inference, more compute, longer thinking, majority voting or verifier-guided search, can beat a larger model, as long as the model has a decent chance of getting it right.

**Go further**

#### What not to say

- "Reasoning models were trained on human chain-of-thought data." R1-Zero learned from outcome rewards alone; R1 used a small cold-start set.

- "More samples always help." Majority voting only helps when the right answer is the most likely one.

**Key terms and sources**

How models like OpenAI o1 and DeepSeek-R1 learn to "think" before answering: reinforcement learning with verifiable rewards on maths and code, GRPO's critic-free group advantages, what emerged in DeepSeek-R1-Zero, and how spending more compute at inference (long chains of thought, majority voting, best-of-N with verifiers) trades against model size · built from Shao et al. (DeepSeekMath / GRPO, 2024), DeepSeek-AI (DeepSeek-R1, 2025), OpenAI (Learning to Reason with LLMs, 2024), Lambert et al. (Tülu 3, 2024), Wang et al. (Self-Consistency, ICLR 2023), Snell et al. (2024), Yu et al. (DAPO, 2025) and Yue et al. (2025) · checked 29 Oct 2026

#### Sources

1. Z. Shao et al., "DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models" (GRPO), 2024, [arXiv:2402.03300](https://arxiv.org/abs/2402.03300).

2. DeepSeek-AI, "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning", 2025, [arXiv:2501.12948](https://arxiv.org/abs/2501.12948); OpenAI, "Learning to Reason with LLMs", 2024.

3. N. Lambert et al., "Tülu 3: Pushing Frontiers in Open Language Model Post-Training", 2024, [arXiv:2411.15124](https://arxiv.org/abs/2411.15124); Q. Yu et al., "DAPO", 2025, [arXiv:2503.14476](https://arxiv.org/abs/2503.14476).

4. X. Wang et al., "Self-Consistency Improves Chain of Thought Reasoning in Language Models", ICLR 2023, [arXiv:2203.11171](https://arxiv.org/abs/2203.11171); C. Snell et al., "Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters", 2024, [arXiv:2408.03314](https://arxiv.org/abs/2408.03314).

5. Qwen Team, "Qwen3 Technical Report", 2025, [arXiv:2505.09388](https://arxiv.org/abs/2505.09388) (tool use and thinking budgets).

6. Qwen Team, "Qwen3 Technical Report", 2025, [arXiv:2505.09388](https://arxiv.org/abs/2505.09388) (tool use and thinking budgets).

7. Qwen Team, "Qwen3 Technical Report", 2025, [arXiv:2505.09388](https://arxiv.org/abs/2505.09388) (tool use and thinking budgets).

8. Y. Yue et al., "Does Reinforcement Learning Really Incentivize Reasoning Capacity in LLMs Beyond the Base Model?", 2025, [arXiv:2504.13837](https://arxiv.org/abs/2504.13837).
