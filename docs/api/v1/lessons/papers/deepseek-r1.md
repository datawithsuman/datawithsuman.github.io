# DeepSeek-R1

> Can a model learn to reason without copying human reasoning?

- Track: Papers Explained › Foundational
- Type: Paper · 30 min
- Page: https://aimlrounds.com/tracks/papers/deepseek-r1/
- Before this: InstructGPT (`papers/instructgpt`)
- Related: Reasoning Models: RLVR, GRPO and Test-Time Compute (`fundamentals/reasoning-models-grpo`)
- Sources checked: 2026-11-11 · Text last changed: 2026-11-20 · Version: cf4b3abc74

## Gist

### The paper

DeepSeek-AI · arXiv [2501.12948](https://arxiv.org/abs/2501.12948) (January 2025; v2, January 2026) · also published in [Nature](https://www.nature.com/articles/s41586-025-09422-z) (2025) · 9 sources, checked 11 Nov 2026

Before R1, models learned to reason mostly by copying reasoning that people wrote out step by step, which is expensive and caps the model at human examples. DeepSeek skipped that step. They took their base model, gave it hard maths, code and logic problems with answers a program can check, and trained it with **reinforcement learning**: right answers get rewarded, wrong ones don't, and nothing tells it _how_ to think. The result, **R1-Zero**, taught itself to think longer, check its work and backtrack, and went from 15.6% to 77.9% on the AIME 2024 maths exam. A four-stage pipeline then made it readable and helpful (**R1**, on par with OpenAI's o1 on maths), and its outputs were used to train small models that beat GPT-4o at maths. The RL algorithm, **GRPO**, drops PPO's value model and compares answers within a group instead.

### The problem

#### One maths question, answered sixteen times

from the paper's own example

"If a > 1, then the sum of the real solutions of √(a − √(a + x)) = x is equal to …"

During training the model sees a question like this and writes **16 different attempts**. A program checks each final answer against the known one. Nobody grades the reasoning, only the answer. Partway through training, one attempt stops mid-solution and writes: _"Wait, wait. Wait. That's an aha moment I can flag here. Let's reevaluate this step-by-step"_ [Table 2](https://arxiv.org/abs/2501.12948). Nobody taught it to say that. We'll follow this question through the training loop.

#### Good reasoning needed people to write it out first

By 2024, two things made models reason better. **Chain-of-thought prompting** asked the model to "think step by step". **Training on reasoning traces** fine-tuned it on worked solutions, written or checked by people. The paper names the cost of the second: dependence on human-written traces "hinders scalability and introduces cognitive biases", and copying human reasoning means performance is "inherently capped by the human-provided exemplars" [§1](https://arxiv.org/abs/2501.12948).

##### Expensive to scale

Every training example needs a correct, readable, step-by-step solution. Hard competition problems need experts to write them.

##### Capped by the examples

Human solutions often skip the checking and backtracking that actually find the answer. A model that imitates them learns the polished write-up, not the search.

OpenAI's o1 (September 2024) had shown that a model which "thinks" for longer at test time does much better on maths and code, but OpenAI didn't publish how it was trained. The open question was whether this could be done in the open, and without a mountain of human-written reasoning.

### The idea

Think of learning chess. One way is to copy grandmasters' games move by move. The other is to play thousands of games and only be told who won. R1-Zero did the second: it was told only whether its final answer was right, and it worked out for itself that thinking longer and checking its work wins more often.

[Figure: One question, sixteen sampled answers, each checked right or wrong, then right answers are made more likely and wrong ones less likely.]

_Illustrative. GRPO samples a group of answers, checks each, and scores every answer against the group's average._

### Play

**Try it.** The model wrote 16 answers to one maths question. Change how many were right and watch each answer's advantage.

—

Rewards are 1 for right and 0 for wrong; the standard deviation is the population one. When every answer gets the same reward, the formula divides 0 by 0, and implementations add a tiny constant, so every advantage is 0.

**Notice:** when all 16 answers are right, or all wrong, every advantage is 0 and the question teaches nothing. GRPO learns most from questions the model only sometimes solves.

## Method

### Method

#### Prompting, imitation, step graders and search

| Approach | How it improves reasoning | The catch |
|---|---|---|
| **Chain-of-thought prompting** (Wei et al. 2022) | Ask for intermediate steps at inference | No training: limited by what the model already does |
| **SFT on reasoning traces** | Fine-tune on worked solutions | Costly human data; imitates the write-up, not the search |
| **Process reward models** (Lightman et al. 2023) | A model grades each step, not just the answer | Hard to define a "step", hard to label, and easy to game |
| **Tree search** (MCTS, as in AlphaGo) | Explore many partial solutions guided by a value model | The space of token sequences is enormous, and the value model is hard to train |

Standard post-training ran SFT first, then RL with a learned reward model (RLHF). R1's bet was to drop the SFT step for reasoning, and to drop learned rewards too: only rewards a program can check [Supp. A.2](https://arxiv.org/abs/2501.12948).

#### R1-Zero: reward right answers, don't teach the reasoning

DeepSeek started from **DeepSeek-V3-Base**, a pretrained 671-billion-parameter mixture-of-experts model with 37 billion parameters active per token, which had never been fine-tuned to chat. They skipped SFT entirely, on the hypothesis that "human-defined reasoning patterns may limit model exploration" [§1](https://arxiv.org/abs/2501.12948). The only structure imposed is a prompt template:

A conversation between User and Assistant. The user asks a question, and the Assistant solves it. The assistant first thinks about the reasoning process in the mind and then provides the user with the answer. The reasoning process and answer are enclosed within <think>...</think> and <answer>...</answer> tags … User: _prompt_. Assistant:

Table 1 [§2.3](https://arxiv.org/abs/2501.12948). The authors kept it this bare on purpose, "avoiding any content-specific biases", so they could watch what the model learns by itself.

The training loop, for our running example:

1. Sample **16 answers** to the question from the current model, at temperature 1.

2. Score each with rules: is the final answer right, and is the thinking inside the tags?

3. Compare each answer's reward with the group's average: better-than-average answers become more likely, worse ones less likely.

4. Repeat, for 10,400 steps of 32 questions each.

##### What made this possible

The paper's conclusion names three ingredients: "hard reasoning questions, a reliable verifier, and sufficient computational resources" [§6](https://arxiv.org/abs/2501.12948). And a large enough base model: small ones failed (chapter 11).

#### Judge each answer against its siblings, not against a critic

GRPO comes from DeepSeek's earlier DeepSeekMath paper. It's PPO with one big change: instead of training a separate value model to estimate how good an answer is likely to be, it samples a **group** of answers to the same question and uses the group's own rewards as the baseline [§2.1](https://arxiv.org/abs/2501.12948).

##### Step 1: the advantage

$$ A_i = \frac{{r_i} - {\text{mean}(\{r_1,\dots,r_G\})}}{{\text{std}(\{r_1,\dots,r_G\})}} $$

Equation 3 [§2.1](https://arxiv.org/abs/2501.12948) · hover a term.

- **this answer’s reward**: r_i: the reward for answer i, here 1 if the final answer is right and 0 if not (plus the format reward).

- **the group’s average**: The mean reward of all G answers to the same question. This replaces PPO’s value model as the baseline.

- **the group’s spread**: Dividing by the standard deviation puts every question on the same scale, whether it’s easy or hard.

##### Step 2: the objective

$$ \mathcal{J}(\theta) = {\frac{1}{G}\sum_{i=1}^{G}}\Big(\min\big({\rho_i}{A_i},\ {\text{clip}(\rho_i,1\pm\varepsilon)}{A_i}\big) - {\beta\,\mathbb{D}_{KL}}\Big) $$

Equation 1, simplified by dropping the expectation over questions [§2.1](https://arxiv.org/abs/2501.12948) · hover a term.

- **average over the group**: Average the update over all G answers to the question (G = 16 in R1).

- **how much more likely**: ρ_i = π_θ(o_i|q) / π_θold(o_i|q): the answer’s probability under the new model divided by the old one. Above 1 means the update made it more likely.

- **push up or down**: Multiply by the advantage: good answers (A > 0) get more likely, bad ones (A < 0) less likely.

- **don’t move too far**: Clip ρ_i to the range 1 ± ε and take the smaller value, so one batch can’t change the model too much. This is PPO’s clipping.

- **stay near the reference**: Subtract β times the KL divergence between the model and a reference model, D_KL(π_θ ‖ π_ref), with β = 0.001 in R1, so the model doesn’t drift into nonsense.

Two things to notice. A rare success on a hard question gets a big push: 4 right out of 16 gives each right answer +1.73 and each wrong one −0.58. And if the model gets all 16 right, or all 16 wrong, every advantage is 0, so the question **teaches nothing**. The questions that help most are the ones the model sometimes solves.

##### Why not PPO?

| | PPO (as in RLHF) | GRPO |
|---|---|---|
| Baseline for the advantage | A learned value model, usually as big as the policy | The group's mean reward: no extra model |
| Memory and compute | Two large models to train | One, plus G samples per question |
| KL to the reference | A per-token penalty added to the reward, which also penalises long answers | Added directly to the loss, so length isn't penalised |
| Tuning | Sensitive to the GAE λ: at the default 0.95 it did much worse; at λ = 1.0 it nearly matched GRPO | Fewer knobs |

Supplementary A.3 [Fig. 3–4](https://arxiv.org/abs/2501.12948). The value model also struggles with long reasoning: predicting the final reward from half a solution is hard when the model may later revise what it wrote.

#### Two simple rewards, and no reward model

##### Accuracy reward

Maths answers must be in a set format (for example in a box) and are matched with the reference. Code is compiled and run against test cases. Right is 1, wrong is 0 [§2.2](https://arxiv.org/abs/2501.12948).

##### Format reward

The thinking must sit inside <think> and </think>. The two rewards are added with equal weight.

The authors deliberately avoided neural reward models, whether they grade the final answer or each step, for reasoning tasks. Their reason: neural reward models "are susceptible to reward hacking during large-scale reinforcement learning", and retraining them adds cost and complexity [§2.2](https://arxiv.org/abs/2501.12948). A rule can't be flattered.

| RL data (reasoning) | Size | How it's checked |
|---|---|---|
| Maths: exam and competition problems (no proofs) | 26k | Final answer matches the reference |
| Code: competition problems, plus real GitHub bug fixes | 17k + 8k | Hidden test cases, unit tests |
| STEM: multiple-choice physics, chemistry, biology | 22k | Correct option |
| Logic: puzzles and code-to-reasoning problems | 15k | Automatic checking |

Supplementary B.3.1 [Table 4](https://arxiv.org/abs/2501.12948). Proofs were left out because a program can't easily check them.

#### Making the reasoning readable and the model helpful

R1-Zero reasoned well but was hard to use: poor readability, and **language mixing**, switching between English and Chinese inside one chain of thought, because the base model was trained mostly on both. Its RL also covered only reasoning tasks, so it was weak at writing and open questions [§3](https://arxiv.org/abs/2501.12948). R1 fixes this with four stages, each starting from the last one's model:

| Stage | What happens | Model after |
|---|---|---|
| **1 · Cold-start SFT** | Fine-tune V3-Base on **thousands** of long chain-of-thought examples in a clear, first-person, conversational style. People rewrote some of R1-Zero's traces, then an LLM rewrote more in that style | Dev1 |
| **2 · Reasoning RL** | GRPO with the rule-based rewards, plus a **language consistency reward**: the share of words in the target language | Dev2 |
| **3 · Rejection sampling + SFT** | Sample many answers from the RL model, keep only correct, clean ones: **~600k** reasoning samples. Add **~200k** non-reasoning samples (writing, factual QA, translation, software engineering). Fine-tune **V3-Base again** on these 800k | Dev3 |
| **4 · RL for everything** | Rule rewards for reasoning; reward models for helpfulness and safety on general prompts; 1,700 steps at temperature 0.7, with preference rewards only in the last 400 | R1 |

Figure 2 and Supplementary B.3 [§3, Supp. B.3](https://arxiv.org/abs/2501.12948).

##### The final reward

$$ Reward = {Reward_{reasoning}} + {Reward_{general}} + {\frac{Num(Words_{target})}{Num(Words)}} $$

Equations 7–10 [§3.1–3.2](https://arxiv.org/abs/2501.12948) · hover a term.

- **reasoning prompts**: Rule-based: accuracy plus format, exactly as in R1-Zero.

- **general prompts**: A reward model: a helpfulness model trained on 66,000 preference pairs (judging only the final summary), or a safety model trained on 106,000 labelled responses (judging everything, thinking included), plus the format reward.

- **language consistency**: The fraction of words in the chain of thought that are in the target language.

##### Try it: what each stage bought

—

Table 3 [§4](https://arxiv.org/abs/2501.12948). Codeforces is shown as a percentile.

The table shows a trade-off. The small cold-start set made the model readable but cost reasoning (AIME fell from 77.9 to 59.0), and reasoning RL won it back. The general data and the final RL barely moved maths, but lifted instruction following and helpfulness sharply (AlpacaEval 2.0 from 62.1 to 87.6).

##### Why preference rewards only ran for 400 steps

With the helpfulness reward model, longer training led to reward hacking: the reward kept rising while Codeforces accuracy fell [Supp. B.5, Fig. 6](https://arxiv.org/abs/2501.12948). The language consistency reward also cost a little benchmark accuracy, and they kept it anyway because people found the output easier to read [Supp. B.6](https://arxiv.org/abs/2501.12948).

#### 512 GPUs, about 12 days in total

| Per step (R1-Zero) | 32 questions × 16 answers = a batch of 512; one pass over the 8,192 sampled outputs, in 16 mini-batches |
|---|---|
| Learning rate, KL β, temperature | 3 × 10−6, 0.001, 1.0 |
| Maximum answer length | 32,768 tokens, raised to 65,536 at step 8,200 |
| Length of the run | 10,400 steps, about 1.6 passes over the data |
| Reference model | Replaced with the latest policy every 400 steps, so the KL term doesn't hold the model back over a long run |
| Clip ratio ε (R1, stage 2) | Reported as 10, far looser than PPO's usual 0.2; the paper says lower values cut off the gradient for too many tokens, while higher values made training unstable |
| Hardware | 64 × 8 = 512 NVIDIA H800 GPUs |

§2.1, §3.2 and Supplementary B.4 [Table 7](https://arxiv.org/abs/2501.12948).

| Part | H800 GPU-hours | At $2 per GPU-hour |
|---|---|---|
| R1-Zero (512 GPUs × ~198 hours) | 101K | $202K |
| Creating the SFT data | 5K | $10K |
| R1 (512 GPUs × ~80 hours) | 41K | $82K |
| **Total** | **147K** | **$294K** |

##### Put the number in context

This is the cost of the RL work only. The base model, DeepSeek-V3, took about 2.788 million H800 GPU-hours to train, about $5.6 million at the same rate [V3 report](https://arxiv.org/abs/2412.19437), which itself excludes research and failed runs. So R1's reasoning training added roughly 5% on top. It's cheap relative to pretraining, not cheap in absolute terms. The paper also calls R1's run "about 4 days, or roughly 80 hours", which don't quite match; the GPU-hours fit 80 hours.

The RL system runs in four modules: rollout on vLLM workers (with the MoE experts spread across nodes and the model's multi-token prediction used to speed up decoding), a forward pass for reward and reference models, rule-based rewards such as code execution run asynchronously, and training. Each module's models are moved out of GPU memory when it finishes [Supp. B.1](https://arxiv.org/abs/2501.12948).

## Results

### What they found

#### From 15.6% to 77.9% on AIME, and it started saying "wait"

##### R1-Zero on AIME 2024 during training (Figure 1)

- **Accuracy:** average single-try accuracy (pass@1) on AIME 2024 rose from 15.6% to 77.9%. Taking a majority vote over 16 samples (cons@16) gave 86.7%, above the average human competitor [§2.3](https://arxiv.org/abs/2501.12948).

- **Longer answers:** the average response grew steadily through training to many thousands of tokens. Nothing in the reward asked for length; longer thinking simply got more answers right.

- **New behaviours:** reflection, checking its own work, and trying other approaches, with a sudden jump in the word "wait": the "aha moment" from our running example.

A version note: the January 2025 v1 of the paper reported 71.0% pass@1 and 86.7% with 64 votes. The v2 and Nature version report 77.9% pass@1 after a longer run (the output limit went from 32,768 to 65,536 tokens at step 8,200, and both accuracy and length jumped). Interviewers may quote either.

##### Try it: why voting beats a single try

—

Illustrative, assuming samples are independent. Worst case: every wrong sample gives the _same_ wrong answer, so the right one needs more than half the votes. Best case: every wrong answer is different, so the right one wins with just 2 votes. Real questions fall in between, and each question has its own chance.

Voting helps most when the model is right more often than any single wrong answer. If the model usually converges on the same wrong answer, more votes make it _more_ confidently wrong. That's why cons@16 (86.7%) is well above pass@1 but not near 100%.

#### An open model at the frontier of reasoning

##### AIME 2024, pass@1 (Table 8)

| Benchmark | GPT-4o | Claude 3.5 Sonnet | DeepSeek-V3 | o1-mini | o1 (Dec 2024) | R1 |
|---|---|---|---|---|---|---|
| AIME 2024 | 9.3 | 16.0 | 39.2 | 63.6 | 79.2 | **79.8** |
| MATH-500 | 74.6 | 78.3 | 90.2 | 90.0 | 96.4 | **97.3** |
| Codeforces percentile | 23.6 | 20.3 | 58.7 | 93.4 | **96.6** | 96.3 |
| GPQA Diamond | 49.9 | 65.0 | 59.1 | 60.0 | **75.7** | 71.5 |
| SWE-bench Verified | 38.8 | 50.8 | 42.0 | 41.6 | 48.9 | 49.2 |
| SimpleQA (facts) | 38.2 | 28.4 | 24.9 | 7.0 | **47.0** | 30.1 |
| AlpacaEval 2.0 (LC win rate) | 51.1 | 52.0 | 70.0 | 57.8 | – | **87.6** |

Table 8 [Supp. D.2](https://arxiv.org/abs/2501.12948). Model versions: GPT-4o-0513, Claude-3.5-Sonnet-1022, o1-1217.

- **Maths and code:** level with o1 on AIME, MATH-500 and Codeforces, far ahead of non-reasoning models including its own base, V3.

- **Knowledge:** better than V3 on STEM-heavy knowledge tests, but behind o1 on GPQA Diamond and well behind on SimpleQA factual recall.

- **Software engineering:** only a small gain over V3, because running test suites made RL too slow to apply at scale (chapter 12).

#### A 1.5B model that beats GPT-4o at competition maths

DeepSeek fine-tuned open Qwen2.5 and Llama models on the same **800,000** samples generated by R1, with SFT only, no RL [Supp. F](https://arxiv.org/abs/2501.12948). This is distillation through the teacher's outputs.

##### Distil, or run RL on the small model?

| 32B model | AIME 2024 | MATH-500 | GPQA Diamond | LiveCodeBench |
|---|---|---|---|---|
| Qwen2.5-32B + large-scale RL (10k+ steps) | 47.0 | 91.6 | 55.0 | 40.2 |
| Distilled from R1 (SFT only) | **72.6** | **94.3** | **62.1** | **57.2** |

Table 16 [Supp. F.1](https://arxiv.org/abs/2501.12948).

The paper's two conclusions: distilling a strong model into a small one works far better than running the same RL on the small model, and it's much cheaper. But "advancing beyond the boundaries of human intelligence may still require more powerful base models and larger-scale reinforcement learning". Distillation copies reasoning; RL on a big model discovers it.

#### Small base models, step graders and tree search

##### Small base models

RL on a 7B dense and a 16B MoE model failed to improve AIME: as answers got longer, they started repeating themselves. It worked once they moved to 32B dense, 230B MoE and 671B MoE models [Supp. G.1](https://arxiv.org/abs/2501.12948).

##### Process reward models

Grading each step sounds better than grading the answer, but a "step" is hard to define, step labels are hard to get right, and a model-based grader invites reward hacking. Useful for re-ranking answers, not worth the cost in large-scale RL [Supp. G.2](https://arxiv.org/abs/2501.12948).

##### Monte Carlo tree search

Unlike chess, the space of token sequences is enormous, limiting the search caused local optima, and the value model guiding it was hard to train. It helped at inference with a fixed value model, but not as a way to keep improving the model.

##### Learned reward models, for too long

The helpfulness reward model was hacked within a few hundred steps (chapter 7). For tasks without a reliable checker, the paper uses human-written SFT data and only short RL.

### Where it falls short

#### What the paper didn't solve, and what others questioned

##### Limits the authors list

- **Only verifiable tasks.** Pure RL needs a reliable reward. For writing and other open-ended tasks, there's no checker, and learned rewards get hacked [§6](https://arxiv.org/abs/2501.12948).

- **No tools, weak structured output.** R1 can't call a search engine or calculator while reasoning.

- **Overthinking.** It spends fewer tokens on easy questions than hard ones, but still overthinks simple questions.

- **Language mixing.** Optimised for Chinese and English; it may reason in English for other languages.

- **Prompt sensitivity.** Few-shot examples consistently hurt it; describe the problem directly, zero-shot.

- **Software engineering.** Slow test runs kept RL from scaling there.

##### Critiques from later work

- **The "aha moment" may not be new.** Liu et al. found that some base models, including DeepSeek-V3-Base, already show self-reflection before any RL, so RL may amplify a behaviour rather than create it [arXiv 2503.20783](https://arxiv.org/abs/2503.20783).

- **GRPO has biases.** The same paper argues that GRPO's normalisation (by answer length in the original DeepSeekMath form, and by the group's standard deviation) can make wrong answers grow longer and over-weight very easy or very hard questions. Their fix, Dr. GRPO, removes both.

- **Benchmarks.** AIME 2024 problems are public, so contamination is a fair question for any model. The paper checks this on AIME 2025, released after training: R1 solved 75% (pass@1) against o1's 80%, close to its AIME 2024 level [Supp. E.2](https://arxiv.org/abs/2501.12948).

- **Anthropomorphism.** The paper itself warns that the vivid first-person style is "DeepSeek-engineered" through the cold-start data, not a sign of human-like thought [Supp. B.3.2](https://arxiv.org/abs/2501.12948).

## Why it matters

### What it changed

R1 was the first openly released model to match OpenAI's o1 on maths and code, with its weights, its method and six distilled small models. Reinforcement learning on rewards a program can check became a standard post-training stage, and GRPO, with fixes such as DAPO and Dr. GRPO, became the default algorithm for it.

**What to remember.** Reward only checkable answers, compare each answer with its group instead of a critic, and a large base model learns to reason on its own. Then add a little SFT for readability, and distil the result into small models.

#### The open recipe for reasoning models

| When | What happened | Link to R1 |
|---|---|---|
| Jan 2025 | Weights released openly, with six distilled models from 1.5B to 70B | Anyone could study and fine-tune a reasoning model |
| Early 2025 | Open reproductions and fixes, such as DAPO (looser upper clip, dropping groups where every answer scores the same, token-level loss) and Dr. GRPO | Refinements of GRPO itself |
| 2025 | "RL with verifiable rewards" became a standard post-training stage for maths and code | The R1-Zero recipe |
| Sept 2025 | Published in Nature, with the supplementary detail (training cost, data, safety) used on this page | The v2 paper |

DAPO [arXiv 2503.14476](https://arxiv.org/abs/2503.14476). Note how DAPO's "dynamic sampling" fixes exactly what the GRPO lab shows: groups where every answer scores the same give no gradient.

Related lessons: reasoning models and GRPO, mixture of experts (R1's architecture), serving reasoning models and prompting reasoning models.

#### Read it

**Read** §2 (GRPO, rewards and R1-Zero) and §3 (the pipeline), plus Figure 1 and Table 3. They answer most interview questions about reasoning models. **Read** Supplementary A.3 (GRPO vs PPO) and G (key findings and failures): they're short and full of practical lessons. **Skim** the benchmark and safety appendices unless you need them.

Read the January 2026 v2 or the Nature version rather than v1: it adds the training cost, data recipe and reward-hacking evidence.

**Key terms and sources**

#### Words to know

Reinforcement learning with verifiable rewards

RL where a program checks the answer (maths match, code tests), instead of a learned reward model.

GRPO

Group Relative Policy Optimization: PPO-style updates where each answer's advantage is its reward relative to a group of answers to the same question. No value model.

Advantage

How much better an answer did than expected. In GRPO, (reward − group mean) ÷ group standard deviation.

Value model (critic)

In PPO, a second network that predicts the expected reward, used as the baseline. GRPO drops it.

KL penalty

A term that keeps the trained model close to a reference model, so it doesn't drift into degenerate text.

Cold start

A small SFT set used before RL so the model starts in a readable style.

Rejection sampling

Generate many answers and keep only the ones that pass a check, then train on them.

pass@1 and cons@k

pass@1: average accuracy of single samples. cons@k: accuracy of the majority answer over k samples.

Reward hacking

The model finds ways to score highly that don't reflect real quality.

Distillation

Training a smaller model on a larger model's outputs.

#### Everything on this page comes from these

1. DeepSeek-AI (2025). DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning. [arXiv 2501.12948](https://arxiv.org/abs/2501.12948) (read in full, v2 of January 2026, including the supplementary material)

2. DeepSeek-AI (2025). DeepSeek-R1 incentivizes reasoning in LLMs through reinforcement learning. [Nature](https://www.nature.com/articles/s41586-025-09422-z)

3. Shao et al. (2024). DeepSeekMath, where GRPO was introduced. [arXiv 2402.03300](https://arxiv.org/abs/2402.03300)

4. DeepSeek-AI (2024). DeepSeek-V3 Technical Report. [arXiv 2412.19437](https://arxiv.org/abs/2412.19437)

5. Schulman et al. (2017). Proximal Policy Optimization Algorithms. [arXiv 1707.06347](https://arxiv.org/abs/1707.06347)

6. Lightman et al. (2023). Let's Verify Step by Step. [arXiv 2305.20050](https://arxiv.org/abs/2305.20050)

7. Wang et al. (2022). Self-Consistency Improves Chain of Thought Reasoning. [arXiv 2203.11171](https://arxiv.org/abs/2203.11171)

8. Liu et al. (2025). Understanding R1-Zero-Like Training: A Critical Perspective. [arXiv 2503.20783](https://arxiv.org/abs/2503.20783)

9. Yu et al. (2025). DAPO: An Open-Source LLM Reinforcement Learning System at Scale. [arXiv 2503.14476](https://arxiv.org/abs/2503.14476)

The voting lab is illustrative. All other numbers come from the papers above. @datawithsuman
