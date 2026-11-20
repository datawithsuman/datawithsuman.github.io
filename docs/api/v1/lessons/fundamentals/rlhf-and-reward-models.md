# Reward Models and RLHF (PPO)

> Why does optimising a reward model too hard make answers worse?

- Track: Fundamentals › LLMs › Post-training
- Type: Concept · 25 min
- Page: https://aimlrounds.com/tracks/fundamentals/rlhf-and-reward-models/
- Before this: Policy Gradients for LLMs (`fundamentals/policy-gradients-for-llms`)
- Quiz topic: `post`

## Intuition

### The situation

After SFT, the assistant's answers are acceptable, but some are curt, some over-apologise and some promise refunds that the policy doesn't allow. You ask agents to compare pairs of answers, and train a reward model. Then a colleague optimises it as hard as possible. The interviewer asks:

> Why does optimising a reward model too hard make answers worse?

**Running example:** after SFT, the support assistant gives acceptable answers, but agents notice some are curt, some over-apologise, some promise refunds the policy doesn't allow. The team asks agents to compare pairs of answers instead of writing new ones.

#### "Good" is hard to write down, easy to recognise

There's no formula for a helpful, honest, polite answer, and SFT can only copy demonstrations. People can, however, reliably pick the better of two answers. RLHF turns those choices into a reward the model can optimise (Christiano et al. 2017; Stiennon et al. 2020 for summarisation; InstructGPT for general instructions).

### The idea

Think of a teacher who marks essays well but has a slight soft spot for long ones. Chasing that teacher's marks improves your writing at first. Push hard enough and you're padding pages: the marks keep rising while the essays get worse. So you keep the student close to how they wrote before.

[Figure: Best-of-N. At N of 1 the reward-model score is 0.06 and true quality is minus 0.23. At N of 16 the score is 2.58 and quality is 0.21. At N of 1,024 the score is 4.66 and quality is minus 0.44.]

_From the lab's simulation, where the reward model slightly over-rewards long answers._

### Play

**Try to break it.** Drag the number of answers per prompt from 1 up to 1,024. Watch the reward-model score, true quality and the KL.

#### Maximise the reward model as hard as possible

The simplest way to optimise a reward model is **best-of-N**: sample N answers and keep the one it scores highest. More N means more optimisation pressure, measured as the KL divergence from the original policy (log N − (N−1)/N for best-of-N).

Simulation: each answer has a true quality and a verbosity. The reward model, like real ones, slightly over-rewards long answers (score = quality + verbosity + noise); the "gold" judge values quality but dislikes rambling (quality − 0.5 × excess verbosity²). 400 prompts × 1,024 samples, fixed seed. Setup inspired by Gao et al.'s gold-vs-proxy experiments.

At first both scores rise: picking the best of 16 answers lifts true quality from **−0.23** to **0.21**. After that, the reward-model score keeps climbing (2.58 → **4.66** at N = 1,024) while true quality falls to **−0.44**, worse than not optimising at all. The optimiser is finding answers that exploit the reward model's love of length, not better answers. Gao et al. (2023) measured exactly this shape with real reward models: gold reward rises then falls as KL grows, with larger reward models overoptimising less. In real RLHF the symptoms are longer answers (Singhal et al. 2023 found much of RLHF's reward gain came from length), sycophancy and confident-sounding mistakes.

**Now say why:** the reward-model score keeps rising past N = 16, so what is the optimiser actually finding?

## Maths

### Maths

#### In one breath

It's easier for people to say which of two answers is better than to write the perfect one. **RLHF** collects such **comparisons**, trains a **reward model** to score answers so that preferred ones score higher (the **Bradley–Terry** model: P(A preferred over B) = σ(r(A) − r(B))), and then uses reinforcement learning, usually **PPO**, to make the policy produce high-reward answers, with a **KL penalty** that keeps it close to the SFT model. It worked: labellers preferred a 1.3B InstructGPT model to the 175B GPT-3. But the reward model is only a **proxy** for what people want. Push too hard and the policy finds its blind spots, such as longer, more confident, more flattering answers: **reward hacking**. True quality first rises, then falls. What you'll be able to do after this: write the reward-model loss and the RLHF objective, and explain reward hacking and the role of the KL penalty.

#### From comparisons to a reward, then to a policy

$$ \mathcal{L}_{RM} = -\log{\sigma\big(r_\phi(x,y_w) - r_\phi(x,y_l)\big)}, \qquad \max_{\pi_\theta}\; {\mathbb{E}\,[\,r_\phi(x,y)\,]} - {\beta\,\mathrm{KL}\big(\pi_\theta \,\|\, \pi_{ref}\big)} $$

Ouyang et al. 2022, Eq. 1–2. InstructGPT labellers ranked 4–9 answers per prompt, giving many pairs per ranking.

- **Bradley–Terry likelihood**: The reward model r_φ (usually the SFT model with a scalar head) should give the chosen answer y_w a higher score than the rejected y_l; σ of the difference is the probability of that preference.

- **maximise reward**: The policy π_θ generates answers to real prompts and is pushed towards ones the reward model scores highly.

- **KL penalty**: β times the KL divergence from the reference (SFT) model: stops the policy drifting into strange text that fools the reward model, and keeps its language fluent.

- **PPO** (Schulman et al. 2017) updates the policy with a clipped objective so each step stays small; it needs a **value model** (critic) to estimate advantages. RLHF with PPO keeps four models in memory: policy, reference, reward model and value model, which makes it expensive and finicky.

- **Results:** outputs of 175B InstructGPT were preferred to 175B GPT-3 85 ± 3% of the time, and even the 1.3B InstructGPT was preferred to the 175B GPT-3.

New to this? Read Policy Gradients for LLMs first.

## In practice

### In practice

#### Keeping the optimiser honest

- **KL penalty and early stopping:** limit how far the policy moves; pick checkpoints with human or held-out evaluations, not reward-model score.

- **Better reward models:** larger, ensembled, trained on fresh on-policy comparisons each round (Llama 2 retrained its reward models iteratively); separate helpfulness and safety reward models.

- **AI feedback** (RLAIF, Constitutional AI; Bai et al. 2022): an LLM judges answers against written principles, cheaper than humans.

- **Simpler algorithms:** DPO skips the reward model and RL loop; for maths and code, verifiable rewards can't be hacked the same way.

#### Optimise a learned judge, but not too hard

RLHF converts human comparisons into a reward model and optimises the policy against it, and because that reward is an imperfect proxy (Goodhart's law), the KL leash to the SFT model is as important as the reward itself.

### The answer that sounds right

#### "A higher reward-model score means a better model"

It sounds right, since that's the score you're optimising. But it's a proxy. In the lab, the score climbs from 2.58 to 4.66 between N = 16 and N = 1,024, while true quality falls from 0.21 to −0.44. So pick checkpoints with human or held-out evaluations. RLHF doesn't teach new knowledge either: it mainly shapes behaviour and preferences.

## Say it

### Why does optimising a reward model too hard make answers worse?

#### The interviewer pushes further

Follow-up 1 of 3

Why compare pairs instead of rating 1–10?

Absolute ratings are inconsistent between people and over time; relative judgements are more reliable, and Bradley–Terry turns them into a consistent score.

Follow-up 2 of 3

Which models does PPO-based RLHF keep in memory?

The policy being trained, the frozen reference model for the KL term, the reward model, and a value model (critic), often all of similar size.

Follow-up 3 of 3

What does the KL term do if β is too large or too small?

Too large: the policy barely changes from SFT. Too small: it drifts, hacks the reward model and can produce degenerate text.

#### The 30-second answer

RLHF starts from an SFT model, collects human comparisons between pairs of its answers, and trains a reward model with a Bradley–Terry loss so preferred answers score higher. Then it optimises the policy with RL, typically PPO, to maximise the reward minus a KL penalty to the SFT reference model. InstructGPT showed this makes even a 1.3B model preferred over 175B GPT-3. The main risk is reward hacking: the reward model is a proxy, so with too much optimisation the policy exploits it, for example by writing longer or sycophantic answers, and true quality drops. The KL penalty, early stopping, better and refreshed reward models, and human evals guard against that.

**Go further**

#### What not to say

- "Higher reward model score means a better model." It's a proxy; check with humans or held-out judges.

- "RLHF teaches the model new knowledge." It mainly shapes behaviour and preferences.

**Key terms and sources**

How human preferences become a training signal: collecting comparisons, training a Bradley–Terry reward model, optimising the policy with PPO under a KL penalty to the SFT model, and why optimising too hard against a learned reward (reward hacking, overoptimisation) makes the model worse · built from Christiano et al. (2017), Stiennon et al. (2020), Ouyang et al. (InstructGPT, NeurIPS 2022), Schulman et al. (PPO, 2017), Bai et al. (Anthropic HH and Constitutional AI, 2022), Gao et al. (Reward Model Overoptimization, ICML 2023) and Singhal et al. (2023) · checked 29 Oct 2026

#### Sources

1. P. Christiano et al., "Deep Reinforcement Learning from Human Preferences", NeurIPS 2017, [arXiv:1706.03741](https://arxiv.org/abs/1706.03741); N. Stiennon et al., "Learning to summarize from human feedback", NeurIPS 2020, [arXiv:2009.01325](https://arxiv.org/abs/2009.01325).

2. L. Ouyang et al., "Training language models to follow instructions with human feedback", NeurIPS 2022, [arXiv:2203.02155](https://arxiv.org/abs/2203.02155).

3. J. Schulman et al., "Proximal Policy Optimization Algorithms", 2017, [arXiv:1707.06347](https://arxiv.org/abs/1707.06347).

4. L. Gao, J. Schulman & J. Hilton, "Scaling Laws for Reward Model Overoptimization", ICML 2023, [arXiv:2210.10760](https://arxiv.org/abs/2210.10760); P. Singhal et al., "A Long Way to Go: Investigating Length Correlations in RLHF", 2023, [arXiv:2310.03716](https://arxiv.org/abs/2310.03716).

5. Y. Bai et al., "Training a Helpful and Harmless Assistant with RLHF", 2022, [arXiv:2204.05862](https://arxiv.org/abs/2204.05862); "Constitutional AI", 2022, [arXiv:2212.08073](https://arxiv.org/abs/2212.08073).
