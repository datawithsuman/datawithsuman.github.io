# InstructGPT

> How did GPT-3 become an assistant that follows instructions?

- Track: Papers Explained › Foundational
- Type: Paper · 30 min
- Page: https://aimlrounds.com/tracks/papers/instructgpt/
- Before this: SFT and Instruction Tuning (`fundamentals/supervised-fine-tuning`)
- Related: Reward Models and RLHF (PPO) (`fundamentals/rlhf-and-reward-models`)

## Gist

### The paper

Ouyang, Wu, Jiang, Almeida, Wainwright, Mishkin and others · OpenAI · NeurIPS 2022 · arXiv 2203.02155 · 10 sources, checked 11 Nov 2026

GPT-3 was trained to predict the next word on the internet, not to help you, so it often ignored instructions, made things up or rambled. OpenAI fixed this in three steps. **Step 1, SFT:** people wrote ideal answers to real prompts, and GPT-3 was fine-tuned on them. **Step 2, reward model:** people ranked several model answers from best to worst, and a model learned to predict which answer they'd prefer. **Step 3, RL:** PPO pushed the model towards answers the reward model scores highly, while a KL penalty kept it close to the SFT model. The result, **InstructGPT**, was preferred to GPT-3 85% of the time, and even the 1.3B version beat the 175B GPT-3, at under 2% of GPT-3's training compute. It's the recipe behind ChatGPT.

### The problem

#### "Explain the moon landing to a 6 year old"

the prompt in the paper's method figure

"Explain the moon landing to a 6 year old in a few sentences."

A model trained only to continue internet text might treat this as the start of a list of homework questions and add more questions, rather than answer it. We'll follow this prompt through all three steps: a person writes a good answer, people rank several model answers, and reinforcement learning makes the model produce answers like the top-ranked ones Fig. 2.

#### The training goal and the user's goal don't match

The paper's first sentence: "Making language models bigger does not inherently make them better at following a user's intent." GPT-3 was trained to predict the next token on a webpage, which is "different from the objective 'follow the user's instructions helpfully and safely'". The authors call the language-modelling objective **misaligned** §1.

##### What went wrong

Making up facts, producing biased or toxic text, and simply not following instructions. Users had to engineer clever prompts to coax out the behaviour they wanted.

##### What "aligned" meant here

Following Askell et al.: **helpful** (solves the user's task), **honest** (doesn't make things up or mislead) and **harmless** (doesn't cause harm).

### The idea

Think of training a new support agent. First they shadow experts and copy their replies. Then a supervisor learns what customers rate highly. Finally the agent practises on new tickets, getting feedback from the supervisor's judgement, but is told not to stray far from what the experts taught.

[Figure: Three steps: people write example answers for supervised fine-tuning, people rank answers to train a reward model, then reinforcement learning optimises the model against the reward model.]

_The three steps of RLHF as InstructGPT ran them. Steps 2 and 3 can repeat with fresh rankings._

### Play

**Try it.** RL pushes the model to score well with the reward model, while a KL penalty pulls it back towards the SFT model. Slide the penalty down to zero and watch what happens to true quality.

—

Illustrative curves, shaped like those measured by Gao et al. (2022): the reward model's score keeps rising as the policy moves away from SFT, but true quality peaks and then falls, because the policy starts exploiting the reward model's mistakes. The policy settles where reward minus β × drift is highest.

**Notice:** the reward model's score keeps climbing as the policy drifts, but true quality peaks and then falls. That gap is reward hacking, and the KL penalty is what stops the policy from chasing it.

## Method

### Method

#### Prompting, instruction datasets, and RLHF on small tasks

| Approach | How | The catch |
|---|---|---|
| **Few-shot prompting** (GPT-3) | Put examples in the prompt so the model continues the pattern | Fragile, and every user has to write good prompts |
| **Instruction tuning on NLP datasets** (FLAN, T0) | Fine-tune on many public tasks rewritten as instructions | Public datasets are mostly classification and QA; real users mostly ask for open-ended writing |
| **RLHF** (Christiano 2017; Stiennon 2020) | Learn a reward from human comparisons, then optimise it with RL | Shown on games and summarisation, not on a general assistant |

InstructGPT takes the RLHF method from "Learning to summarize from human feedback" and applies it to the full, messy range of prompts real customers sent to the OpenAI API §3.1.

#### Show the model good answers

Labellers wrote the answer they'd want for each prompt, such as a few simple sentences about astronauts flying to the moon for our example. GPT-3 was then fine-tuned on these demonstrations with ordinary next-token loss §3.5. See the SFT lesson for the mechanics.

- **Data:** about 13,000 training prompts, from the API and written by labellers.

- **Training:** 16 epochs, cosine learning-rate decay, residual dropout 0.2.

- **A surprise:** validation loss started overfitting after 1 epoch, yet more epochs kept improving both the reward model's score and human ratings. So they picked the checkpoint by reward-model score, not by loss.

##### Why not stop here?

Writing a great answer is slow and hard; judging which of two answers is better is fast and easy. SFT also only shows one good answer per prompt, while comparisons teach the model what makes one answer better than another. Steps 2 and 3 use that cheaper, richer signal.

#### Learn to predict which answer people prefer

For each prompt, the model produced between K = 4 and K = 9 answers, and a labeller ranked them all. A ranking of K answers gives K(K−1)/2 pairs: 6 pairs for 4 answers, 36 for 9. A 6-billion-parameter copy of the SFT model, with its output layer replaced by a single score, was trained on these pairs §3.5.

$$ \text{loss}(\theta) = -\tfrac{1}{\binom{K}{2}}\,\mathbb{E}\Big[\log \sigma\big(r_\theta(x, y_w) - r_\theta(x, y_l)\big)\Big] $$

Equation 1 §3.5 · hover a term.

- **the preferred answer’s score**: r_θ(x, y_w): the reward model’s score for the answer the labeller ranked higher.

- **the other answer’s score**: r_θ(x, y_l): its score for the answer ranked lower.

- **turn the gap into a probability**: σ, the sigmoid, turns the score gap into the probability that a person prefers y_w. A gap of 0 gives 50%.

- **average over all pairs**: Average −log of that probability over every pair from the ranking, so all K(K−1)/2 pairs from one prompt are trained together.

##### Try it: what the reward model learns from one pair

—

The probability is σ(gap) = 1 / (1 + e−gap), the Bradley–Terry model. Only score differences matter, so before RL they shifted all rewards so that human-written demonstrations average 0.

Training all pairs from one ranking in a single batch mattered: shuffling them as separate examples made the reward model overfit within one pass, because pairs from the same ranking are so correlated. The finished reward model agreed with held-out labellers about 70% of the time (69.6%), close to how often labellers agree with each other (about 73%).

#### Optimise the reward, but don't drift too far

The SFT model becomes the policy. For each prompt it writes an answer, the reward model scores it, and PPO updates the policy to make high-scoring answers more likely. Each prompt is one episode with one reward at the end §3.5.

$$ \text{objective}(\phi) = \mathbb{E}\Big[r_\theta(x,y) - \beta \log \tfrac{\pi^{RL}_\phi(y|x)}{\pi^{SFT}(y|x)}\Big] + \gamma\,\mathbb{E}\big[\log \pi^{RL}_\phi(x_{pre})\big] $$

Equation 2, slightly simplified §3.5, App. C · hover a term.

- **the reward model’s score**: r_θ(x, y): how much people are predicted to like answer y to prompt x.

- **the KL penalty**: β × log(π_RL / π_SFT): how much more likely the new policy makes this answer than the SFT model did. Subtracting it keeps the policy close to SFT, so it can’t exploit the reward model’s blind spots. β = 0.02.

- **the pretraining mix**: γ × log-likelihood of ordinary pretraining text, with γ = 27.8. This is PPO-ptx: it keeps skills the RL step would otherwise erode.

The value function PPO needs was initialised from the reward model. RL ran for 256,000 episodes over about 31,000 API prompts, with no human labels needed at this step.

#### What people actually ask a language model

##### The prompts

Real prompts sent to earlier InstructGPT models in the OpenAI Playground, de-duplicated, capped at 200 per user, filtered for personal information, and split by user so the test set contains no training customers. Labellers wrote the very first prompts to bootstrap the process. Over 96% were in English.

##### The labellers

About 40 contractors, hired through Upwork and Scale AI after a screening test on spotting sensitive content. Training labellers agreed with each other 72.6% of the time. A separate group of held-out labellers, who wrote no training data, was used to check the model wasn't just fitting the training labellers' tastes.

| Use case | Share of prompts |
|---|---|
| Generation | 45.6% |
| Open QA | 12.4% |
| Brainstorming | 11.2% |
| Chat | 8.4% |
| Rewrite | 6.6% |
| Summarisation | 4.2% |
| Classification | 3.5% |
| Closed QA | 2.6% |
| Extraction | 1.9% |

Table 1 §3.2, plus 3.5% other. Dataset sizes: about 13k prompts for SFT, 33k for the reward model, 31k for RL.

This table explains a key result: classification and QA, which public NLP datasets cover, are only about 18% of real use, while open-ended generation and brainstorming are about 57%.

## Results

### What they found

#### People preferred a 1.3B InstructGPT to the 175B GPT-3

##### How often labellers preferred 175B InstructGPT (§4.1)

- **Size isn't everything:** outputs from the **1.3B** InstructGPT were preferred to the **175B** GPT-3, despite over 100× fewer parameters. Each step helped: a well-crafted prompt beat plain GPT-3, SFT beat that, and PPO beat SFT.

- **Following instructions:** InstructGPT followed explicit constraints (such as "in 2 paragraphs or less") more often and was rated more appropriate for a customer assistant.

- **Making less up:** on closed tasks such as summarisation, it invented information 21% of the time against GPT-3's 41%. On TruthfulQA it gave truthful and informative answers about twice as often.

- **Toxicity:** about 25% fewer toxic outputs when asked to be respectful, but no improvement on bias benchmarks (Winogender, CrowS-Pairs).

- **Held-out labellers** preferred InstructGPT at about the same rate as the training labellers.

- **Beyond the training data:** it could follow instructions in other languages and answer questions about code, though both were rare in training, and it often replied in English.

#### PPO made some benchmarks worse, and PPO-ptx fixed most of it

Plain PPO lowered scores on several public benchmarks: SQuAD, DROP, HellaSwag and French-to-English translation. The authors call this an **alignment tax**: a cost paid in capability for being better aligned. A technique with a high tax may not get adopted §4.2, §5.1.

##### Mixing in pretraining updates (PPO-ptx)

Adding the γ term, which keeps training on ordinary pretraining text during RL, reversed most of the drops and even beat GPT-3 on HellaSwag, without lowering human preference scores. This version is what "InstructGPT" means in the paper.

##### Simply raising the KL penalty didn't work

A stronger β cut the validation reward significantly and never fully recovered DROP and SQuAD. Some gaps remained even with PPO-ptx, on DROP, SQuADv2 and translation.

#### Alignment was cheap next to pretraining

##### Training compute, petaflop/s-days (§5.1)

Log scale: each step is 10×.

Training the 175B SFT model took 4.9 petaflop/s-days and the 175B PPO-ptx model 60, against 3,640 for pretraining GPT-3 itself. Yet RLHF improved helpfulness more than a 100× increase in model size did. The authors' conclusion: "increasing investments in alignment of existing language models is more cost-effective than training larger models", at least for their customers' tasks §5.1.

### Where it falls short

#### What the paper didn't solve

##### Who the model is aligned to

The authors are blunt: the model is aligned to "a set of labelers' preferences", shaped by the instructions OpenAI wrote, not to "human values" in general. The labellers were mostly English-speaking people in the US or Southeast Asia, and most comparisons were labelled by only one person §5.2–5.3.

##### Failures they show

- **False premises:** asked "Why is it important to eat socks after meditating?", InstructGPT invents theories instead of rejecting the premise.

- **Over-hedging:** it can give long "it depends" answers to simple questions. The authors suspect this comes from asking labellers to reward humility, which the reward model picked up.

- **Multiple constraints** such as "list 10 movies made in the 1930s set in France" still trip it up.

- **It follows harmful instructions:** told to be maximally biased, it produced more toxic output than GPT-3. The paper calls this perhaps its greatest limitation.

##### Problems later work made clear

- **Reward over-optimisation.** Pushing too hard against a learned reward model makes true quality fall even as the reward rises; Gao et al. measured how this scales arXiv 2210.10760.

- **Complexity and cost.** Four models in memory during RL (policy, reference, reward and value) and a finicky PPO setup motivated simpler methods.

## Why it matters

### What it changed

InstructGPT showed that a small amount of human feedback changes behaviour more than a 100× bigger model, for a fraction of the compute. ChatGPT followed eight months later, built the same way, and SFT then preference optimisation became the standard way to turn a base model into an assistant.

**What to remember.** Fine-tune on demonstrations, train a reward model on rankings with a Bradley–Terry loss, then optimise it with PPO while a KL penalty keeps the model close to SFT. Later methods such as DPO and rule-based rewards simplify or replace parts of this pipeline, but keep its shape.

#### From InstructGPT to every chat assistant

| When | What happened | Link to InstructGPT |
|---|---|---|
| Nov 2022 | ChatGPT launched, described by OpenAI as a sibling model to InstructGPT | The same SFT → RM → PPO recipe, applied to dialogue |
| Dec 2022 | Constitutional AI (Anthropic): AI feedback guided by written principles replaces most human harmlessness labels | Swaps the source of preferences |
| 2023 | Llama 2-Chat: SFT, then RLHF with separate helpfulness and safety reward models | The recipe in an open model |
| 2023 | DPO: train directly on preference pairs with a classification-style loss, no reward model and no RL loop | Removes steps 2 and 3 as separate stages |
| 2025 | DeepSeek-R1: rule-based rewards for reasoning, reward models only for general helpfulness | Keeps the RL step, replaces the learned reward where answers can be checked |

Related lessons: RLHF and reward models, DPO and hallucination.

#### Read it

**Read** §1 (the findings), §3.1 and §3.5 (the three steps and both equations) and Figures 1–2. That's the RLHF recipe interviewers expect you to explain. **Read** §5.2–5.3 on who the model is aligned to: short and often asked about. **Skim** the benchmark results and the long appendices on labeller instructions.

**Key terms and sources**

#### Words to know

Alignment

Making a model act on the user's intent: helpful, honest and harmless.

SFT (supervised fine-tuning)

Fine-tuning on human-written example answers with the usual next-token loss.

Reward model

A model that scores a prompt and answer, trained so preferred answers score higher.

Bradley–Terry model

P(A preferred to B) = σ(score A − score B). The basis of the reward model's loss.

RLHF

Reinforcement learning from human feedback: optimise a policy against a reward model trained on human preferences.

PPO

Proximal Policy Optimization: an RL algorithm that limits how far each update can move the policy.

KL penalty

A cost for moving away from the SFT model, which stops the policy exploiting the reward model.

PPO-ptx

PPO plus updates on pretraining text, to reduce the alignment tax.

Alignment tax

Capability lost on some tasks as a side effect of alignment training.

Reward hacking / over-optimisation

The policy finds answers the reward model scores highly but people don't actually prefer.

#### Everything on this page comes from these

1. Ouyang et al. (2022). Training language models to follow instructions with human feedback. arXiv 2203.02155 (main text read in full, plus appendix C)

2. Christiano et al. (2017). Deep reinforcement learning from human preferences. arXiv 1706.03741

3. Stiennon et al. (2020). Learning to summarize from human feedback. arXiv 2009.01325

4. Schulman et al. (2017). Proximal Policy Optimization Algorithms. arXiv 1707.06347

5. Lin et al. (2021). TruthfulQA. arXiv 2109.07958

6. Gao et al. (2022). Scaling Laws for Reward Model Overoptimization. arXiv 2210.10760

7. Bai et al. (2022). Constitutional AI: Harmlessness from AI Feedback. arXiv 2212.08073

8. Touvron et al. (2023). Llama 2: Open Foundation and Fine-Tuned Chat Models. arXiv 2307.09288

9. Rafailov et al. (2023). Direct Preference Optimization. arXiv 2305.18290

10. DeepSeek-AI (2025). DeepSeek-R1. arXiv 2501.12948

The KL lab's curves are illustrative. All other numbers come from the paper. @datawithsuman
