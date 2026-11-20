# Scaling Laws and Chinchilla

> For a fixed compute budget, should you train a bigger model or feed it more data?

- Track: Papers Explained › Foundational
- Type: Paper · 30 min
- Page: https://aimlrounds.com/tracks/papers/scaling-laws-and-chinchilla/
- Before this: The Next-Token Objective (`fundamentals/next-token-prediction`)
- Related: Attention Is All You Need (`papers/attention-is-all-you-need`)

## Gist

### The paper

Kaplan et al., OpenAI, 2020 · arXiv [2001.08361](https://arxiv.org/abs/2001.08361) + Hoffmann et al., DeepMind, 2022 (NeurIPS 2022) · arXiv [2203.15556](https://arxiv.org/abs/2203.15556) · 10 sources, checked 11 Nov 2026

In 2020, OpenAI showed that a language model's loss falls as a smooth, predictable **power law** as you add parameters, data or compute, so you can forecast a big model from small ones. Their advice for a fixed compute budget: spend most of it on a **bigger model** and only a little on more data. The field listened: GPT-3 (175B) and Gopher (280B) were trained on only about 300 billion tokens. In 2022, DeepMind redid the experiment with 400+ models and found the opposite balance: model size and data should grow **equally**, about **20 training tokens per parameter**. To prove it, they trained **Chinchilla**, 70B parameters on 1.4 trillion tokens, with the same compute as the 280B Gopher. It beat Gopher on almost every task and costs a quarter as much to run.

### The problem

#### One compute budget, two ways to spend it

from the Chinchilla paper

You have the compute DeepMind used for Gopher: about 5.8 × 1023 floating-point operations. Do you train a **280B** model on 300 billion tokens, or a **70B** model on 1.4 trillion tokens?

Both cost almost the same to train. Gopher took the first option, as everyone did in 2021. Chinchilla took the second [§4](https://arxiv.org/abs/2203.15556). We'll follow this choice through both papers, and you'll be able to try every option in between.

#### You only get to train the big model once

A large training run is planned around a fixed budget: so many accelerators for so many weeks. The Chinchilla paper puts it plainly: "it is typically only feasible to train these large models once", so the model size and the amount of data have to be right before you start [§1](https://arxiv.org/abs/2203.15556).

##### Too big, too little data

A huge model that reads too little is under-trained: it could have learned much more. It's also expensive to serve, forever.

##### Too small, too much data

A small model run for a very long time stops improving: its size caps how good it can get, and extra tokens are wasted.

Somewhere between the two is a best split. Scaling laws are how you find it from small, cheap experiments instead of guessing at full scale.

### The idea

Think of a fixed budget for a student: you can pay for a bigger brain or more books, but not both. Kaplan said buy mostly brain. Chinchilla showed you should split it evenly: every time the brain doubles, double the books too.

[Figure: Two rectangles with the same area: a tall, narrow one for Gopher (big model, little data) and a short, wide one for Chinchilla (smaller model, much more data).]

_Illustrative. Training compute is about 6 × parameters × tokens, so a fixed budget is a fixed area: tall and narrow, or short and wide._

### Play

**Try it.** You have Gopher's compute budget. Drag the model size and see how many tokens you can afford and what loss Chinchilla's formula predicts.

—

Computed from the fitted formula with the paper's published constants and D = C ÷ 6N. The loss differences look small, but on this scale they are large: Chinchilla's whole advantage over Gopher is about 0.05. With these rounded constants the formula's minimum sits well above 20 tokens per parameter (about 90 at Gopher's budget, a 32B model; the paper quotes about 40B from its unrounded fit). That's why approach 3 recommends smaller models than approaches 1 and 2, and why the "20 tokens per parameter" rule comes from approach 1. A later replication found this fit unreliable (chapter 10).

**Notice:** the loss curve is a valley. Gopher's 280B model sits up the right-hand slope with barely one token per parameter; a smaller model trained on more data reaches lower loss for the same compute.

## Method

### Method

#### Training compute is roughly six times parameters times tokens

$$ {C} \approx {6}\,{N}\,{D} $$

Kaplan §1.3, §2.1 [p. 6–7](https://arxiv.org/abs/2001.08361) · hover a term.

- **training compute**: C: the total floating-point operations (FLOPs) to train the model.

- **six operations**: About 2 per parameter per token for the forward pass and 4 for the backward pass.

- **model size**: N: the number of parameters.

- **data**: D: the number of training tokens.

This one line is why the question is a trade-off. With C fixed, N × D is fixed: double the model and you can only afford half the tokens. For our example, 280B × 300B and 70B × 1.4T both come to about 6 × 1023 FLOPs.

#### Loss falls as a power law in size, data and compute

OpenAI trained decoder-only Transformers from 768 to 1.5 billion parameters (not counting embeddings) on WebText2, about 23 billion tokens, and measured the test loss [§2–3](https://arxiv.org/abs/2001.08361). When only one factor limits the model, the loss follows a straight line on a log-log plot:

$$ {L(N)} = \left(\frac{{N_c}}{{N}}\right)^{{\alpha_N}} $$

Equation 1.1 [§1.2](https://arxiv.org/abs/2001.08361). Data and compute have the same form, with αD ≈ 0.095 and αC ≈ 0.050 · hover a term.

- **test loss**: L: cross-entropy loss in nats per token. Lower is better.

- **a fitted constant**: N_c ≈ 8.8 × 10^13. Its exact value depends on the tokenizer, so it has no deep meaning.

- **model size**: N: non-embedding parameters, for a model trained to convergence on plenty of data.

- **the exponent**: α_N ≈ 0.076. Doubling N multiplies the loss by 2^−0.076 ≈ 0.95: about 5% lower.

##### What else they found

- **Shape barely matters.** Depth versus width, number of heads: performance depends "very weakly" on these, and strongly on scale.

- **The trends held over many orders of magnitude** with no sign of bending at the top end.

- **Bigger models learn faster per token.** They reach the same loss with fewer steps and less data.

- **So train big and stop early.** For a fixed budget, the best result came from "training very large models and stopping significantly short of convergence".

##### Their recipe for spending more compute

Kaplan fitted Nopt ∝ C0.73 and Dopt ∝ C0.27. For every 10× more compute, make the model about **5.4× bigger** and give it only about **1.9× more data**. Most of the extra compute goes into parameters [§6, Fig. 14](https://arxiv.org/abs/2001.08361).

#### Every big model read about 300 billion tokens

| Model | Parameters | Training tokens | Tokens per parameter |
|---|---|---|---|
| LaMDA | 137B | 168B | 1.2 |
| GPT-3 | 175B | 300B | 1.7 |
| Jurassic-1 | 178B | 300B | 1.7 |
| Gopher | 280B | 300B | 1.1 |
| MT-NLG | 530B | 270B | 0.5 |
| **Chinchilla** | **70B** | **1,400B** | **20** |

Chinchilla Table 1 [§1](https://arxiv.org/abs/2203.15556); tokens per parameter computed from it.

Following Kaplan and the GPT-3 setup, labs raced to more parameters while keeping data around 300 billion tokens. The largest dense model, MT-NLG, reached 530B parameters, over 3× GPT-3, in two years [§5](https://arxiv.org/abs/2203.15556).

#### 400 models later, a different split

DeepMind asked the same question: for a fixed budget C, which N and D give the lowest loss? They trained over 400 models from 70 million to over 16 billion parameters on 5 to 500 billion tokens, and estimated the answer three independent ways [§3](https://arxiv.org/abs/2203.15556):

| Approach | How | Nopt ∝ Ca | Dopt ∝ Cb |
|---|---|---|---|
| 1 · Training curves | Train each model size for 4 lengths; at every compute level, take the run with the lowest loss | 0.50 | 0.50 |
| 2 · IsoFLOP profiles | At 9 fixed budgets, vary model size and find the bottom of each U-shaped loss curve | 0.49 | 0.51 |
| 3 · Fitted loss formula | Fit L(N, D) to all runs, then minimise it under C = 6ND | 0.46 | 0.54 |
| _Kaplan et al. 2020_ | | 0.73 | 0.27 |

Table 2 [§3.4](https://arxiv.org/abs/2203.15556).

All three agree: a ≈ b ≈ 0.5. **Every time you double the model, double the data.** They also found the same result on two other datasets, C4 and GitHub code.

##### Why Kaplan got a different answer, according to DeepMind

Kaplan used one learning-rate schedule length for every run. Losses read off partway through a long schedule are worse than a run whose schedule matches its length, which made short training look worse than it is, and pushed the advice towards bigger models. Most of Kaplan's runs were also small, many under 100M parameters [§2](https://arxiv.org/abs/2203.15556). Later work found other causes too (chapter 10).

#### Loss = the text's own entropy + a size penalty + a data penalty

$$ \hat{L}(N, D) = {E} + {\frac{A}{N^{\alpha}}} + {\frac{B}{D^{\beta}}} $$

Equations 2 and 10 [§3.3, App. D.2](https://arxiv.org/abs/2203.15556) · hover a term.

- **the floor**: E ≈ 1.69: the loss of a perfect model, roughly the entropy of natural text. No model can go below it.

- **too few parameters**: A / N^α, with A ≈ 406.4 and α ≈ 0.34: how much a model of size N falls short of perfect, even with unlimited training.

- **too little data**: B / D^β, with B ≈ 410.7 and β ≈ 0.28: the extra loss from seeing only D tokens.

With C fixed, making N bigger shrinks the size penalty but forces D smaller, which grows the data penalty. The best model balances the two. Because α and β are close, the balance point moves with N and D growing at nearly the same rate.

#### A compute-optimal model reads about 20 tokens per parameter

| Parameters | Compute-optimal tokens | Training FLOPs |
|---|---|---|
| 400M | 8.0B | 1.92 × 1019 |
| 1B | 20.2B | 1.21 × 1020 |
| 10B | 205.1B | 1.23 × 1022 |
| 67B | 1.5T | 5.76 × 1023 (Gopher's budget) |
| 175B | 3.7T | 3.85 × 1024 |
| 280B | 5.9T | 9.90 × 1024 |
| 1T | 21.2T | 1.27 × 1026 |

Table 3, from approach 1 [§3.4](https://arxiv.org/abs/2203.15556).

Divide the two columns and you get about 20 tokens per parameter at every size: the rule of thumb everyone quotes. By this table, GPT-3 should have read 3.7 trillion tokens, not 300 billion, and a 1-trillion-parameter model isn't worth training unless you have about 250× Gopher's compute.

##### Try it: 10× more compute, two recipes

Kaplan: N × m0.73, D × m0.27. Chinchilla: N × m0.5, D × m0.5. Bars are on a log scale, so equal lengths mean equal growth factors.

## Results

### What they found

#### A 70B model beat a 280B model with the same compute

The analysis put the best size for Gopher's budget between 40B and 70B. DeepMind trained the larger end, **Chinchilla: 70B parameters on 1.4 trillion tokens**, with the same architecture family and data source (MassiveText) as Gopher. The main changes were AdamW instead of Adam and a slightly different tokenizer [§4.1](https://arxiv.org/abs/2203.15556).

##### MMLU, 5-shot accuracy (Table 6)

- **MMLU:** 67.6% against Gopher's 60.0% and GPT-3's 43.9%. It even beat expert forecasts for June 2023 (63.4%). The abstract says 67.5%; Table 6 says 67.6%.

- **BIG-bench:** 65.1% average against 54.4%; worse than Gopher on only 4 of 62 tasks.

- **Reading:** 77.4% on LAMBADA against 74.5%, and more than 10 points better on RACE.

- **Cheaper to use:** 4× smaller, so 4× less memory and roughly 4× less compute per generated token, for the model's whole life.

##### Why the last point matters

Training happens once; inference happens billions of times. A model trained compute-optimally is not just better for the same training cost, it's also far cheaper to deploy. That observation later pushed labs even further towards smaller models trained on more data (chapter 11).

#### What else the two papers measured

| Kaplan: data | WebText2, about 23B tokens, byte-pair encoding with 50,257 tokens, context 1,024 |
|---|---|
| Kaplan: critical batch size | Grows as loss falls: roughly 1–2 million tokens for their largest models |
| Kaplan: forgiving sizes | Models between 0.6× and 2.2× the optimal size need only about 20% more compute for the same loss |
| Kaplan: overfitting | The penalty depends on N0.74/D: 8× the model needs about 5× the data to avoid it |
| Chinchilla: architecture | 80 layers, dmodel 8,192, 64 heads; batch 1.5M rising to 3M tokens; bfloat16 with a float32 copy of the weights |
| Chinchilla: hardware | TPUv3 and TPUv4, with JAX and Haiku |
| Chinchilla: schedule lesson | Set the cosine learning-rate schedule to the planned number of tokens; overshooting it by more than about 25% hurts |

Kaplan §1–5, Chinchilla §2, §4.1 and App. B [Kaplan](https://arxiv.org/abs/2001.08361) · [Chinchilla](https://arxiv.org/abs/2203.15556).

#### Two later papers traced the gap

##### Counting and scale

Pearce and Song showed much of the gap comes from Kaplan counting only non-embedding parameters, combined with working at small scale. Simulating Chinchilla's study under those conditions reproduces exponents close to Kaplan's [arXiv 2406.12907](https://arxiv.org/abs/2406.12907).

##### Three training details

Porian et al. reproduced Kaplan's law and found three causes: ignoring the cost of the last layer, the warm-up length, and optimiser settings not tuned per scale. Fixing them gave "excellent agreement" with Chinchilla. They also found careful learning-rate decay was _not_ essential, against DeepMind's own explanation [arXiv 2406.19146](https://arxiv.org/abs/2406.19146).

##### A problem with approach 3

Besiroglu et al. rebuilt the data from the paper's plots and found the published fit of the loss formula didn't match the data, and that its confidence intervals were implausibly narrow. Refitting gave results consistent with approaches 1 and 2, so the headline answer stands, but the exact constants in chapter 6 shouldn't be trusted to many digits [arXiv 2404.10102](https://arxiv.org/abs/2404.10102).

### Where it falls short

#### The answer to a narrow question

##### Limits the authors list

- **Only two large runs.** Chinchilla and Gopher are the only big-scale test, with nothing in between.

- **The power law is assumed.** They saw some bending at high compute, so they "may still be overestimating the optimal size of large models".

- **Under one epoch.** Every run saw each token at most once; repeating data wasn't studied.

- **Quality is assumed.** More tokens help only if they're good tokens, and web-scale data brings toxicity and privacy problems [§5](https://arxiv.org/abs/2203.15556).

##### What came after

| Idea | What it says |
|---|---|
| **Count inference too** (Sardana et al. 2023) | If a model will serve about a billion requests, train it smaller and longer than Chinchilla-optimal. Quality kept improving up to 10,000 tokens per parameter [arXiv 2401.00448](https://arxiv.org/abs/2401.00448). |
| **Running out of data** (Muennighoff et al. 2023) | Up to about 4 passes over repeated data is nearly as good as fresh data; beyond that, returns fall towards zero [arXiv 2305.16264](https://arxiv.org/abs/2305.16264). |
| **Over-trained open models** | Meta's Llama 3 8B read about 15 trillion tokens, nearly 1,900 per parameter, about 90× the Chinchilla ratio, because a small model that's cheap to serve was the goal [Llama 3](https://arxiv.org/abs/2407.21783). |

##### Tokens per parameter, from 2020 to 2024

Log scale: each step is 10×. GPT-3, Gopher and Chinchilla from Chinchilla Table 1; Llama 3 8B from the Llama 3 report.

Chinchilla answered "what's the best model for this training budget?" Today's labs usually ask "what's the best model for this training _and serving_ budget?", and that answer is smaller still. Both start from the same scaling-law method.

## Why it matters

### What it changed

Chinchilla changed how every lab sizes a model: about 20 training tokens per parameter became the default for compute-optimal training, and data, not just parameters, became the thing to scale. Later models went further, training small models on far more tokens because they are cheaper to serve.

**What to remember.** Loss falls as a predictable power law, training compute is about 6ND, and for a fixed budget you should grow model size and data together. Count inference cost too, and the best model gets smaller still.

#### Read Chinchilla, skim Kaplan

**Read** Chinchilla §1, §3 and §4, with Figures 1–3 and Tables 1–3: they're short, clear, and the source of the "20 tokens per parameter" rule. **Skim** Kaplan's §1 summary and Figures 1–4 for the idea of predictable power laws; its compute-allocation advice is outdated. **Skip** the long benchmark appendices unless you need a specific number.

Then read one of the later reconciliation papers, since "why did Kaplan and Chinchilla disagree?" is a common follow-up question.

**Key terms and sources**

#### Words to know

Scaling law

A fitted formula, usually a power law, for how loss changes with model size, data or compute.

Power law

y ∝ x−α: a straight line on a log-log plot. Each doubling of x multiplies y by the same factor.

Compute-optimal

The model size and token count that give the lowest loss for a fixed training compute.

C ≈ 6ND

Training FLOPs ≈ 6 × parameters × tokens (2 for the forward pass, 4 for the backward pass).

IsoFLOP curve

Loss against model size at one fixed compute budget. Its lowest point is the compute-optimal size.

Tokens per parameter

Training tokens ÷ parameters. About 20 is Chinchilla-optimal; GPT-3 used 1.7.

Under-trained

A model that saw too few tokens for its size, so the same compute could have produced a better model.

Over-training

Deliberately training past compute-optimal to get a smaller model that's cheaper to serve.

#### Everything on this page comes from these

1. Kaplan et al. (2020). Scaling Laws for Neural Language Models. [arXiv 2001.08361](https://arxiv.org/abs/2001.08361) (main text read in full)

2. Hoffmann et al. (2022). Training Compute-Optimal Large Language Models (Chinchilla). [arXiv 2203.15556](https://arxiv.org/abs/2203.15556) (read in full, including appendix D)

3. Brown et al. (2020). Language Models are Few-Shot Learners (GPT-3). [arXiv 2005.14165](https://arxiv.org/abs/2005.14165)

4. Rae et al. (2021). Scaling Language Models: Methods, Analysis & Insights from Training Gopher. [arXiv 2112.11446](https://arxiv.org/abs/2112.11446)

5. Besiroglu et al. (2024). Chinchilla Scaling: A replication attempt. [arXiv 2404.10102](https://arxiv.org/abs/2404.10102)

6. Pearce and Song (2024). Reconciling Kaplan and Chinchilla Scaling Laws. [arXiv 2406.12907](https://arxiv.org/abs/2406.12907)

7. Porian et al. (2024). Resolving Discrepancies in Compute-Optimal Scaling of Language Models. [arXiv 2406.19146](https://arxiv.org/abs/2406.19146)

8. Sardana et al. (2023). Beyond Chinchilla-Optimal: Accounting for Inference in Language Model Scaling Laws. [arXiv 2401.00448](https://arxiv.org/abs/2401.00448)

9. Muennighoff et al. (2023). Scaling Data-Constrained Language Models. [arXiv 2305.16264](https://arxiv.org/abs/2305.16264)

10. Llama Team, Meta (2024). The Llama 3 Herd of Models. [arXiv 2407.21783](https://arxiv.org/abs/2407.21783)

The labs compute from the papers' published formulas. @datawithsuman
