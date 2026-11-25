# DPO and Preference Optimisation

> How does DPO skip the reward model, and what can go wrong?

- Track: Fundamentals › LLMs › Post-training
- Type: Concept · 25 min
- Page: https://aimlrounds.com/tracks/fundamentals/dpo/
- Before this: Reward Models and RLHF (PPO) (`fundamentals/rlhf-and-reward-models`)
- Quiz topic: `post`
- Sources checked: 2026-10-29 · Text last changed: 2026-11-20 · Version: f7f4e16178

## Intuition

### The situation

The team has 20,000 comparisons from support agents, the same data RLHF would use. Chosen: "Sorry about that! I've refunded the biryani." Rejected: "Refunds aren't possible after delivery." They don't want to build an RL pipeline. The interviewer asks:

> How does DPO skip the reward model, and what can go wrong?

**Running example:** the team has 20,000 comparisons from support agents (the same data RLHF would use). Chosen: "Sorry about that! I've refunded the biryani." Rejected: "Refunds aren't possible after delivery." They want to use it without building an RL pipeline.

#### RLHF works, but it's a lot of machinery

PPO-based RLHF samples from the policy during training, scores with a separate reward model, estimates advantages with a value model, and is sensitive to many hyperparameters. Could we optimise the same objective directly from the preference data?

### The idea

Think of skipping the judge at a cooking contest, because you already have a list of which dish beat which. You adjust your recipes so winners become more likely than losers, compared with how you cooked before. The catch is that you only care about the gap, so both dishes can get worse.

[Figure: RLHF with PPO keeps four models in memory: policy, reference, reward model and value model. DPO keeps two: policy and reference.]

_RLHF with PPO keeps four models in memory, and DPO keeps two._

### Play

**Try to break it.** Set chosen to +5 and rejected to −5, and read the loss at each β. Then set chosen to −4 and rejected to −10.

#### What lowers the DPO loss?

Log-ratios in nats, summed over the answer's tokens. 0 means the policy gives the answer the same probability as the SFT reference.

At the start the policy equals the reference: margin 0, loss **ln 2 = 0.693**, gradient weight 0.5. Making the chosen answer 5 nats more likely and the rejected 5 nats less likely (β = 0.1) gives margin 1.0 and loss **0.313**. Now the trap: set chosen to **−4** and rejected to **−10**. Both answers have become _less_ likely than before, yet the loss falls to **0.437**, because only the _difference_ matters. Real DPO runs often show this "likelihood displacement": probability mass leaves both answers and can go to responses that appear in neither. With β = 0.5 the same ±5 shift gives margin 5 and loss **0.007**: the pair is "solved" and contributes almost no gradient (weight 0.007).

**Now say why:** in that second setting both answers became less likely, so why did the loss fall?

## Maths

### Maths

#### In one breath

RLHF needs a reward model, an RL loop, a value model and careful tuning. **DPO** (Rafailov et al. 2023) showed that the KL-regularised RLHF objective has a closed-form optimal policy, so the reward can be written in terms of the policy itself: the **implicit reward** of an answer is β · log(πθ/πref), how much more likely the model makes it than the SFT reference does. Plugging that into the Bradley–Terry loss gives a loss you can minimise directly on (prompt, chosen, rejected) triples: **raise the chosen answer's log-ratio relative to the rejected one**. It's stable, cheap (two models: policy and frozen reference) and matched or beat PPO in the paper; Llama 3 used it. The catches: it learns only from a fixed dataset (offline), the loss can fall while _both_ answers become less likely, and it can favour length. Tuned PPO or online variants can still win. What you'll be able to do after this: write the DPO loss, explain β and the implicit reward, and compare DPO with PPO and its variants.

#### The implicit reward and the DPO loss

$$ \mathcal{L}_{DPO} = -\log {\sigma\Big(}{\beta}\Big[{\log\frac{\pi_\theta(y_w\mid x)}{\pi_{ref}(y_w\mid x)}} - {\log\frac{\pi_\theta(y_l\mid x)}{\pi_{ref}(y_l\mid x)}}\Big]{\Big)} $$

Rafailov et al., "Direct Preference Optimization: Your Language Model is Secretly a Reward Model", NeurIPS 2023, [arXiv:2305.18290](https://arxiv.org/abs/2305.18290), Eq. 7. log π(y|x) is the sum of the answer's token log-probabilities.

- **chosen log-ratio**: How much more (or less) likely the policy makes the chosen answer than the frozen SFT reference does, in log space.

- **rejected log-ratio**: The same for the rejected answer.

- **β**: Scales the implicit reward β·log(π/π_ref). It plays the role of the KL coefficient: larger β keeps the policy closer to the reference (typical 0.1–0.5).

- **logistic loss**: Bradley–Terry again: −log σ(margin). Minimising it pushes the chosen log-ratio above the rejected one.

The gradient weights each pair by **σ(−margin)**: pairs the model already gets right contribute little, pairs it gets wrong contribute a lot, like a classifier focusing on its mistakes.

## In practice

### In practice

#### DPO vs PPO, and the variants

- **Results:** in the paper DPO reached a better reward–KL trade-off than PPO on controlled sentiment generation and matched or beat it on TL;DR summarisation and Anthropic HH dialogue. Llama 3's post-training used rounds of rejection sampling, SFT and DPO.

- **But:** Xu et al. (ICML 2024) found that well-tuned PPO outperformed DPO, especially on hard tasks like code; DPO is **offline** and can exploit answers outside the preference data's coverage. **Online/iterative DPO** samples fresh answers from the current policy and labels them each round.

- **Variants:** IPO (adds regularisation against overfitting to deterministic preferences), KTO (needs only thumbs-up/down labels, not pairs), ORPO (combines SFT and preference loss, no reference model), SimPO (length-normalised log-probs, no reference model, curbs length exploitation).

#### Your language model is secretly a reward model

Because the KL-regularised optimal policy determines its own reward, β·log(π/πref), preference learning reduces to a logistic loss on log-probability ratios: same goal as RLHF, no sampling loop.

### The answer that sounds right

#### "Lower DPO loss means the chosen answer got more likely"

It sounds right, since that's what the pair is asking for. But only the margin is guaranteed to grow. With chosen at −4 and rejected at −10, both are less likely than before, yet the loss falls to 0.437. Real runs show this "likelihood displacement": probability can move to responses that appear in neither answer. And DPO does optimise a reward, just an implicit one.

## Say it

### How does DPO skip the reward model, and what can go wrong?

#### The interviewer pushes further

Follow-up 1 of 3

What does β control?

The strength of the implicit KL constraint: higher β keeps the policy closer to the reference and saturates the loss faster; lower β allows bigger changes.

Follow-up 2 of 3

Why do we need the reference model?

The implicit reward is defined relative to it; without it, the loss could be lowered just by changing overall probabilities. Reference-free variants like ORPO and SimPO add other terms instead.

Follow-up 3 of 3

DPO or PPO for a new project?

DPO for a quick, stable preference-tuning step with an existing dataset; PPO or GRPO-style online RL when you have a reliable reward (especially verifiable ones) and want the model to explore.

#### The 30-second answer

DPO optimises the same KL-regularised preference objective as RLHF but without a reward model or RL. The optimal policy of that objective implies a reward equal to beta times the log-ratio of policy to reference probability, so substituting into the Bradley–Terry loss gives a logistic loss on the difference between the chosen and rejected answers' log-ratios. It needs only the policy and a frozen reference, is stable and cheap, and matched PPO in the original paper; Llama 3 used it. Downsides: it's offline, so it can't explore beyond the dataset; the loss can drop while both answers lose probability; and it can favour longer answers. Online DPO and variants like IPO, KTO, ORPO and SimPO address these.

**Go further**

#### What not to say

- "DPO doesn't optimise a reward." It optimises an implicit one, with the same objective as RLHF.

- "Lower DPO loss means the chosen answer got more likely." Only the margin is guaranteed to grow.

**Key terms and sources**

How Direct Preference Optimization trains on preference pairs with a simple classification-style loss and no reward model or RL loop: the implicit reward, the role of β, what the gradient does, its failure modes (offline data, likelihood displacement, length), and the family of variants (IPO, KTO, ORPO, SimPO, online DPO) · built from Rafailov et al. (DPO, NeurIPS 2023), Azar et al. (IPO, 2023), Ethayarajh et al. (KTO, 2024), Hong et al. (ORPO, 2024), Meng et al. (SimPO, NeurIPS 2024), Xu et al. (Is DPO Superior to PPO?, ICML 2024) and Meta's Llama 3 report (2024) · checked 29 Oct 2026

#### Sources

1. R. Rafailov et al., "Direct Preference Optimization: Your Language Model is Secretly a Reward Model", NeurIPS 2023, [arXiv:2305.18290](https://arxiv.org/abs/2305.18290).

2. S. Xu et al., "Is DPO Superior to PPO for LLM Alignment? A Comprehensive Study", ICML 2024, [arXiv:2404.10719](https://arxiv.org/abs/2404.10719).

3. M. Azar et al., "A General Theoretical Paradigm to Understand Learning from Human Preferences" (IPO), 2023, [arXiv:2310.12036](https://arxiv.org/abs/2310.12036); K. Ethayarajh et al., "KTO", 2024, [arXiv:2402.01306](https://arxiv.org/abs/2402.01306).

4. J. Hong et al., "ORPO", 2024, [arXiv:2403.07691](https://arxiv.org/abs/2403.07691); Y. Meng et al., "SimPO", NeurIPS 2024, [arXiv:2405.14734](https://arxiv.org/abs/2405.14734).

5. N. Razin et al., "Unintentional Unalignment: Likelihood Displacement in Direct Preference Optimization", 2024, [arXiv:2410.08847](https://arxiv.org/abs/2410.08847); Llama Team, "The Llama 3 Herd of Models", 2024, [arXiv:2407.21783](https://arxiv.org/abs/2407.21783).
