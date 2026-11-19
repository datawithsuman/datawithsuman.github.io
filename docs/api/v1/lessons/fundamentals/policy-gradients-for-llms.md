# Policy Gradients for LLMs

> How can a reward that isn't differentiable train an LLM, and why do you need a baseline?

- Track: Fundamentals › LLMs › Post-training
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/policy-gradients-for-llms/
- Before this: SFT and Instruction Tuning (`fundamentals/supervised-fine-tuning`)
- Quiz topic: `post`

## Intuition

### The situation

Your model writes SQL, and you can check each query by running it. But pass or fail isn't differentiable, so you can't simply backpropagate through it. You also notice training gets very noisy after someone adds a bonus to every reward. The interviewer asks:

> How can a reward that isn't differentiable train an LLM, and why do you need a baseline?

#### Why it matters

The RLHF and reasoning model lessons use PPO and GRPO. This lesson explains what they're doing underneath. Interviewers like to ask why you need reinforcement learning at all, and why GRPO doesn't need a critic.

### The idea

Think of a coach who can't see a player's technique, only the score of each match. After a good match, the coach says to do more of what you did. After a bad one, to do less. If the coach praises every match, because every score is above zero, the player learns nothing. What helps is praise relative to the usual score.

[Figure: Three ideas. Reward-weighted log-probabilities need no gradient from the reward. A baseline cuts noise. Clipping lets you reuse samples.]

_PPO learns its baseline. GRPO uses the group's mean._

### Play

**Try to break it.** Choose no baseline, with 10 added to every reward. Then try the group mean.

#### Train with a baseline

Simulation with one prompt and four possible answers, one right. Reward: 1 if right, 0 if wrong, plus the added amount. 150 updates at a learning rate of 0.5, averaged over 40 fixed runs. Grey shows no baseline. A run counts as stuck if it ends with over 90% on a wrong answer.

Rewards of 11 or 10 carry the same information as 1 or 0. But with 8 answers per update, and **no baseline**, the right answer ends at only 50%, and 19 of 40 runs get stuck on a wrong one. Everything gets pushed up, so whichever answer happens to be sampled first runs away. The **group mean** removes the added 10 entirely: 99%, with none stuck, and about 20 times less gradient noise (0.08 against 1.68). Now set the added amount to 0: no baseline works fine, because a reward of 0 pushes nothing. Bigger groups also help: at G = 64, even no baseline reaches 99%, though each update then costs 64 answers.

**Now say why:** why does adding a constant hurt when there's no baseline?

## Maths

### Maths

#### In one breath

RLHF and GRPO both train a model from a score it gets after answering. That score comes from a reward model or a checker, so you can't backpropagate through it. The **policy gradient** gets around this: sample an answer, then raise the probability of its tokens in proportion to its reward. Good answers get more likely, and bad ones less. Alone, this is very noisy, so we subtract a **baseline**, an estimate of the usual reward. **PPO** learns the baseline with a value model, and clips each update. **GRPO** uses the average reward of the group as its baseline instead.

#### Text as a game

| RL word | In an LLM |
|---|---|
| Policy | The model's next-token distribution |
| State | The prompt and the tokens so far |
| Action | The next token |
| Episode | One whole answer |
| Reward | Usually one number at the end, from a reward model or a checker |

##### Why not use ordinary training?

SFT needs the right answer, token by token. Here we only have a score for an answer the model wrote itself. We can't differentiate through "did the tests pass?", and sampling a token isn't differentiable either. The policy gradient needs neither: it only uses the gradient of the model's own log-probabilities.

##### Why a baseline?

Say every answer scores between 10 and 11. Without a baseline, every answer gets pushed up, the good ones only slightly more than the bad, and the signal is lost in noise. Subtracting the usual reward fixes this: above-average answers go up, and below-average ones go down. On average the gradient is unchanged, because the baseline term has an expected value of zero. Only the noise falls.

##### Three algorithms

| | REINFORCE | PPO | GRPO |
|---|---|---|---|
| Baseline | None, or a simple one | Learned value model | Mean of the group's rewards |
| Extra models | None | Value model, and often reward and reference | Reference only |
| Reusing samples | One update | Several updates, kept safe by clipping | Clipped objective. DeepSeekMath used one update |

##### Why PPO clips

Samples come from the old policy. As the policy changes, those samples describe it less well. PPO measures this with the ratio r of new to old probability, and stops giving credit once r leaves a small range, usually 1 ± 0.1 to 0.3. That makes it safe to take several gradient steps on one batch.

##### What InstructGPT and GRPO did

InstructGPT used PPO, with the value model initialised from the reward model. GRPO keeps PPO's clipped form, but drops the value model. DeepSeekMath sampled 64 answers per question, used a KL coefficient of 0.04, and made one update after each sampling round.

#### The maths

$$ \nabla_\theta J = \mathbb{E}\Big[\sum_t \nabla_\theta \log \pi_\theta(a_t \mid s_t)\,\big(R - b\big)\Big], \qquad L = \min\big(r A,\ \mathrm{clip}(r, 1{-}\epsilon, 1{+}\epsilon) A\big) $$

The policy gradient with a baseline and the PPO clipped objective, in the form given in OpenAI’s Spinning Up. GRPO replaces A with the group-normalised reward.

- **the direction to improve**: How to change the weights to raise the expected reward.

- **make this token more likely**: The ordinary gradient of a token’s log-probability. The reward itself is never differentiated.

- **the advantage**: How much better than usual this answer was. Positive pushes its tokens up, and negative pushes them down.

- **PPO’s clip**: r is the new probability over the old. Once r leaves the range, more movement earns no extra credit.

## In practice

### In practice

#### In practice

- **One reward, many tokens:** each token in an answer gets the answer's advantage, whether it helped or not. That's a noisy signal, so large groups help.

- **Keep it on-policy:** samples must come from a recent policy. Fresh samples are expensive, as generation is slow, so RL training spends much of its time generating.

- **Keep it close:** a KL term to the reference stops the policy drifting into odd text, which reward hacking exploits.

- **Watch for no signal:** if every answer in a group gets the same reward, the advantages are all 0. Choose problems the model sometimes solves.

- **Check the reward first:** the algorithm will find any weakness in it. Test the reward on known good and bad answers before a long run.

### The answer that sounds right

#### "A positive reward means the model is doing well, so it should be reinforced"

It sounds right, as positive sounds good. But only reward relative to the usual level carries information. If every answer scores about 10, a reward of 10 is merely average, and reinforcing it adds noise. The advantage, reward minus baseline, is what tells the model which answers were better.

## Say it

### How can a reward that isn't differentiable train an LLM, and why do you need a baseline?

#### The interviewer pushes further

Follow-up 1 of 3

Why doesn't subtracting a baseline bias the gradient?

The expected value of the gradient of log π, given the state, is zero. So a baseline that depends only on the state multiplies something with zero mean, and adds nothing on average. It only changes the variance.

Follow-up 2 of 3

A prompt gets rewards of 11, 10, 10 and 10. What are the weights, with and without the group mean?

Without a baseline, all four are positive, so every answer gets pushed up. With the group mean of 10.25, the good answer gets +0.75 and the others get −0.25, which is the signal we want.

Follow-up 3 of 3

Why can PPO reuse a batch, when plain policy gradient can't?

The plain gradient only holds for the policy that produced the samples. PPO corrects for the change with a probability ratio, and clips it so that the policy can't gain by moving far from where the samples are reliable.

We use reinforcement learning when we only get a score for a whole answer, such as from a reward model or a test suite, and can't backpropagate through it. The policy gradient samples an answer and raises its tokens' log-probabilities in proportion to its reward, so the reward itself never needs a gradient. That's noisy, so we subtract a baseline. It doesn't change the expected gradient, but above-average answers go up and below-average ones go down. PPO learns the baseline with a value model, and clips the probability ratio so it can safely reuse samples. GRPO keeps the clipping, but uses the group's mean reward as the baseline, so it doesn't need a critic.

**Key terms and sources**

How reinforcement learning maps onto text, the policy gradient, why baselines reduce noise, PPO's clipping, value models, and how GRPO replaces them.

#### Sources

- OpenAI Spinning Up, policy gradient and baselines

- OpenAI Spinning Up, PPO

- Schulman et al., Proximal Policy Optimization

- Schulman et al., Generalized Advantage Estimation

- Ouyang et al., InstructGPT

- Shao et al., DeepSeekMath and GRPO

- Stanford CME295, reinforcement learning with LLMs

Explanations are ours, built from these sources. Lab numbers are illustrative, and worked examples were checked by calculation.
