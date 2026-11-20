# LoRA

> How do you fine-tune a 175B model by training only a few million numbers?

- Track: Papers Explained › Foundational
- Type: Paper · 25 min
- Page: https://aimlrounds.com/tracks/papers/lora/
- Before this: SFT and Instruction Tuning (`fundamentals/supervised-fine-tuning`)
- Related: LoRA and QLoRA: Parameter-Efficient Fine-Tuning (`fundamentals/lora-and-qlora`)

## Gist

### The paper

Hu, Shen, Wallis, Allen-Zhu, Li, Wang, Wang, Chen · Microsoft · ICLR 2022 · arXiv [2106.09685](https://arxiv.org/abs/2106.09685) · 10 sources, checked 11 Nov 2026

Fine-tuning normally updates every weight, so each task needs a full copy of the model: 350 GB for GPT-3. LoRA's bet is that the _change_ a task needs is simple, so it can be written as the product of two thin matrices, **ΔW = BA**, with a rank r as small as 1 to 8. The original weights stay frozen; only A and B are trained. On GPT-3 175B that cuts trainable parameters about **10,000×**, training memory about **3×** (1.2 TB to 350 GB), and each task's checkpoint from 350 GB to **35 MB**, while matching or beating full fine-tuning. Because BA can be added into W after training, it adds **no extra delay** when the model runs.

### The problem

#### One 175B model, a hundred customers

the paper's own scenario

You run GPT-3 175B and want a version tuned for each of 100 customers: SQL generation for one, chat summaries for another. Full fine-tuning means 100 copies of 350 GB: **35 TB** of checkpoints.

With LoRA you keep one 350 GB base model and 100 adapters of about 35 MB each: about **354 GB** in total [§4.2, footnote 4](https://arxiv.org/abs/2106.09685). We'll follow one weight matrix of this model, the query projection in layer 48, which is 12,288 × 12,288.

#### Full fine-tuning doesn't scale to giant models

Fine-tuning updates every parameter, so "the new model contains as many parameters as in the original model". That was an "inconvenience" for GPT-2 or RoBERTa and becomes "a critical deployment challenge" for GPT-3's 175 billion parameters [§1](https://arxiv.org/abs/2106.09685).

##### Training memory

With Adam, every trainable weight also needs its gradient and two optimiser states. For GPT-3 that's about 1.2 TB of GPU memory just to fine-tune.

##### Storing and switching

Each task produces a full-size model. Serving many tasks means loading and swapping hundreds of gigabytes.

### The idea

Think of a huge printed encyclopedia that needs a few corrections for each customer. Reprinting the whole book for every customer is absurd. Instead you keep one copy and give each customer a thin booklet of corrections that you apply on top. LoRA's A and B matrices are that booklet.

[Figure: A large frozen weight matrix W next to a thin trainable path: a tall narrow matrix B times a short wide matrix A, whose outputs are added.]

_LoRA keeps the pretrained weights frozen and learns the update as two thin matrices, B × A._

### Play

**Try it.** Pick a model and a rank, and see how many numbers LoRA trains compared with full fine-tuning, and how big the adapter file is.

Computed from |Θ| = 2 × (adapted matrices) × d × r. Model sizes and widths: GPT-2 medium (355M, d = 1,024, 24 layers), GPT-2 large (774M, d = 1,280, 36 layers), GPT-3 (175B, d = 12,288, 96 layers).

**Notice:** on GPT-3 with rank 4, LoRA trains about 19 million numbers instead of 175 billion, and the adapter is a file of tens of megabytes. That's why one base model can serve hundreds of tuned versions.

## Method

### Method

#### Earlier cheap methods cost speed or quality

| Approach | What's trained | The catch |
|---|---|---|
| **Adapters** (Houlsby 2019) | Small extra layers inserted into each block | The extra layers run in sequence, adding delay: up to 30% at batch size 1 on GPT-2 medium |
| **Prefix / prompt tuning** (Li & Liang 2021) | Learned "virtual tokens" added to the input | Hard to optimise, performance changes unpredictably with size, and the prefix uses up sequence length |
| **BitFit** | Only the bias terms | Very cheap but usually weaker |
| **Tune the top layers** | Only the last few layers | Still large, and often worse than full fine-tuning |

##### Adapter delay on GPT-2 medium, batch 1, 128 tokens (Table 1)

Milliseconds per forward pass. Fine-tuned and LoRA models take the same time, because LoRA's weights are merged in.

#### The change a task needs is low-rank

Earlier work found that pretrained language models have a low "intrinsic dimension": they can be fine-tuned well even when the update is squeezed into a small random subspace (Aghajanyan et al. 2020). LoRA hypothesises that the weight **change** during fine-tuning also has a low "intrinsic rank" [§4.1](https://arxiv.org/abs/2106.09685). So instead of learning a full d × k update, learn it as the product of a d × r matrix and an r × k matrix:

$$ h = {W_0}\,x + {\frac{\alpha}{r}}\,{B}\,{A}\,x $$

Equation 3 [§4.1](https://arxiv.org/abs/2106.09685) · hover a term.

- **the frozen weights**: W₀: the pretrained matrix, here 12,288 × 12,288. It never changes during LoRA training.

- **the up-projection**: B: d × r. Starts at zero, so the model begins exactly as the pretrained one.

- **the down-projection**: A: r × k. Starts as small random numbers. Together, B times A is a d × k matrix of rank at most r.

- **the scaling**: α / r. α is set once to the first r you try and not tuned, so you can change r without retuning the learning rate.

Both paths see the same input x and their outputs are added. Only A and B get gradients. For our 12,288 × 12,288 query matrix with r = 4, that's 2 × 12,288 × 4 = 98,304 trainable numbers instead of about 151 million.

##### No extra delay when serving

After training, compute W = W₀ + BA once and serve it like any other model. To switch tasks, subtract BA and add a different B′A′, a quick operation [§4.1](https://arxiv.org/abs/2106.09685). Adapters can't do this, because they add layers rather than change existing ones.

##### A generalisation of full fine-tuning

If you apply LoRA to every matrix and set r to the full rank, you recover roughly what full fine-tuning can express. Adapters, by contrast, converge to a different network as you add parameters, and prefix tuning to one that can't take long inputs.

#### Spread a small budget across more matrices

The paper applies LoRA only to the attention projections (Wq, Wk, Wv, Wo) and freezes the feed-forward layers, for simplicity. With a fixed budget of 18M trainable parameters on GPT-3, they compared which matrices to adapt [§7.1](https://arxiv.org/abs/2106.09685):

| Adapted | Rank r | WikiSQL | MultiNLI |
|---|---|---|---|
| Wq only | 8 | 70.4 | 91.0 |
| Wk only | 8 | 70.0 | 90.8 |
| Wv only | 8 | 73.0 | 91.0 |
| Wo only | 8 | 73.2 | 91.3 |
| Wq, Wv | 4 | **73.7** | 91.3 |
| All four | 2 | **73.7** | **91.7** |

Table 5 [§7.1](https://arxiv.org/abs/2106.09685). WikiSQL varies by about ±0.5 between runs, MultiNLI by about ±0.1.

Putting the whole budget into Wq or Wk was clearly worse. Adapting more matrices at a lower rank beat adapting one at a higher rank: even rank 4 captures enough. Most later practice adapts every linear layer, feed-forward included.

#### How small the trainable part really is

$$ {|\Theta|} = {2} \times {\hat{L}_{LoRA}} \times {d_{model}} \times {r} $$

§5.1 [§5.1](https://arxiv.org/abs/2106.09685), for square d × d matrices · hover a term.

- **trainable numbers**: |Θ|: everything LoRA trains.

- **A and B**: 2: one A and one B for each adapted matrix.

- **adapted matrices**: L̂: how many weight matrices get LoRA, e.g. W_q and W_v in all 96 layers = 192.

- **the model width**: d_model: 12,288 for GPT-3.

- **the rank**: r: often 1 to 16.

With GPT-3, Wq and Wv, and r = 4, LoRA trains about 18.9M numbers, roughly 9,300× fewer than 175B and a 38 MB file, in line with the paper's "roughly 10,000×" and 35 MB.

#### Cheaper to train, store and switch

| GPT-3 175B | Full fine-tuning | LoRA |
|---|---|---|
| GPU memory to train | 1.2 TB | **350 GB** |
| Checkpoint per task | 350 GB | **35 MB** (r = 4, Wq and Wv) |
| Training speed per V100 | 32.5 tokens/s | **43.1 tokens/s** (about 25% faster) |
| Extra delay when serving | none | **none**, once merged |

§4.2 and footnote 5 [§4.2](https://arxiv.org/abs/2106.09685).

The memory saving comes from the optimiser: Adam keeps two extra numbers per trainable weight, and gradients aren't needed for frozen weights. The frozen model still has to sit in memory, which is why the saving is about 3×, not 10,000×.

##### Try it: storing many tasks

GPT-3 175B: 350 GB per full copy; 350 GB base + 35 MB per LoRA adapter. Bars use a log scale (each step is 10×).

## Results

### What they found

#### Matching full fine-tuning with 0.003% of the parameters

| GPT-3 175B | Trainable params | WikiSQL | MultiNLI-m | SAMSum (R1/R2/RL) |
|---|---|---|---|---|
| Full fine-tuning | 175,255.8M | 73.8 | 89.5 | 52.0 / 28.0 / 44.5 |
| BitFit | 14.2M | 71.3 | 91.0 | 51.3 / 27.4 / 43.5 |
| Prefix-embedding | 3.2M | 63.1 | 88.6 | 48.3 / 24.2 / 40.5 |
| Prefix-layer | 20.2M | 70.1 | 89.5 | 50.8 / 27.3 / 43.5 |
| Adapter (H) | 40.1M | 73.2 | 91.5 | 53.2 / 29.0 / 45.1 |
| **LoRA** | **4.7M** | 73.4 | **91.7** | **53.8 / 29.8 / 45.9** |
| **LoRA** | **37.7M** | **74.0** | 91.6 | 53.4 / 29.2 / 45.1 |

Table 4 [§5.5](https://arxiv.org/abs/2106.09685). WikiSQL is text-to-SQL, MultiNLI is inference, SAMSum is dialogue summarisation.

- **GPT-3:** LoRA matched or beat full fine-tuning on all three tasks with 4.7M trainable parameters.

- **More isn't always better for other methods:** prefix tuning got worse with more than 256 prefix tokens (or 32 for prefix-layer), which the authors suspect pushes inputs away from what the model saw in pretraining.

- **Smaller models too:** on GPT-2 medium, LoRA scored 70.4 BLEU on the E2E NLG task with 0.35M parameters, above full fine-tuning's 68.2. On RoBERTa and DeBERTa (GLUE), it matched or came close to full fine-tuning.

#### The update really is low-rank

##### WikiSQL accuracy on GPT-3, adapting Wq and Wv (Table 6)

"To our surprise, a rank as small as one suffices" for adapting Wq and Wv on these tasks; Wq alone needed a somewhat larger r [§7.2](https://arxiv.org/abs/2106.09685). Two analyses back this up:

- **Bigger r doesn't find new directions.** The top directions learned with r = 8 are also the top ones learned with r = 64; the extra directions at r = 64 look mostly like noise.

- **ΔW amplifies what's already there.** The update boosts directions that exist in W but weren't emphasised by pretraining, and boosts them a lot: by about 21.5× for r = 4 in layer 48 [§7.3](https://arxiv.org/abs/2106.09685). Fine-tuning seems to turn up useful features the model already had, rather than learn new ones.

##### The authors' own caveat

They "do not expect a small r to work for every task". If the new task were in a different language from pretraining, retraining everything (LoRA with r = d) could clearly win [§7.2, footnote 6](https://arxiv.org/abs/2106.09685).

### Where it falls short

#### What the paper didn't solve

- **Batching different tasks.** If you merge BA into W for speed, one forward pass can only serve one task. Keeping adapters separate allows mixing tasks in a batch, at some cost in speed [§4.2](https://arxiv.org/abs/2106.09685).

- **Heuristic choices.** Which matrices to adapt and which rank to use were picked by experiment; the paper lists finding a principled way as future work.

- **Narrow tests.** The evaluation used classification, text-to-SQL, summarisation and table-to-text tasks, not long instruction tuning or learning new domains.

- **Later evidence of a gap.** On harder targets, code and maths with up to 20B tokens of continued pretraining, "LoRA substantially underperforms full finetuning", but it also forgets less of the base model's other skills. Full fine-tuning learned updates of 10–100× higher rank than typical LoRA settings [arXiv 2405.09673](https://arxiv.org/abs/2405.09673).

## Why it matters

### What it changed

LoRA made fine-tuning cheap enough for anyone with one GPU, and with QLoRA, for models of tens of billions of parameters. It became the default way to customise open models, and serving one base model with many swappable adapters became a standard product pattern.

**What to remember.** Freeze W, learn ΔW = BA with a small rank, start B at zero, scale by α/r, and merge BA into W for serving. It matches full fine-tuning on most adaptation tasks, but can fall short when teaching a lot of genuinely new knowledge.

#### From one paper to the standard fine-tuning method

| Work | What it added |
|---|---|
| **QLoRA** (2023) | Keep the frozen model in 4-bit and train LoRA adapters on top: fine-tune a 65B model on a single 48 GB GPU while keeping 16-bit fine-tuning quality [arXiv 2305.14314](https://arxiv.org/abs/2305.14314) |
| **S-LoRA** (2023) | Serve thousands of adapters on one base model, keeping adapters in main memory and batching requests that use different ones [arXiv 2311.03285](https://arxiv.org/abs/2311.03285) |
| **DoRA** (2024) | Split each weight into a size and a direction, and apply LoRA to the direction [arXiv 2402.09353](https://arxiv.org/abs/2402.09353) |
| **Everywhere else** | LoRA became the usual way to customise open models, from chat models to image generators, and adapter-per-customer serving became a standard product pattern |

Related lessons: LoRA and QLoRA and supervised fine-tuning.

#### Read it

**Read** §1, §4 (the method, its benefits and limits) and Figure 1: they're short and contain everything interviewers ask about. **Read** §7.1–7.2 for which matrices and which rank. **Skim** the GLUE and GPT-2 tables, and §7.3 if you're curious why low rank works.

**Key terms and sources**

#### Words to know

Parameter-efficient fine-tuning (PEFT)

Adapting a model by training only a small number of new or selected parameters.

Rank

The number of independent directions a matrix can represent. A d × r times r × k product has rank at most r.

Low-rank decomposition

Writing a big matrix as the product of two thin ones: ΔW = BA.

Intrinsic dimension / rank

The idea that the useful change during fine-tuning lives in a small subspace.

Adapter

A small extra layer inserted into the network; adds delay because it runs in sequence.

Merging

Adding BA into W₀ after training so the model runs at full speed with no extra layers.

α / r scaling

A constant that scales the update so the learning rate needn't be retuned when r changes.

QLoRA

LoRA on top of a 4-bit quantised frozen model, to fit fine-tuning on one GPU.

#### Everything on this page comes from these

1. Hu et al. (2021). LoRA: Low-Rank Adaptation of Large Language Models. [arXiv 2106.09685](https://arxiv.org/abs/2106.09685) (v2, main text read in full)

2. Aghajanyan, Zettlemoyer, Gupta (2020). Intrinsic Dimensionality Explains the Effectiveness of Language Model Fine-Tuning. [arXiv 2012.13255](https://arxiv.org/abs/2012.13255)

3. Houlsby et al. (2019). Parameter-Efficient Transfer Learning for NLP (adapters). [arXiv 1902.00751](https://arxiv.org/abs/1902.00751)

4. Li and Liang (2021). Prefix-Tuning. [arXiv 2101.00190](https://arxiv.org/abs/2101.00190)

5. Brown et al. (2020). Language Models are Few-Shot Learners (GPT-3). [arXiv 2005.14165](https://arxiv.org/abs/2005.14165)

6. Dettmers et al. (2023). QLoRA: Efficient Finetuning of Quantized LLMs. [arXiv 2305.14314](https://arxiv.org/abs/2305.14314)

7. Sheng et al. (2023). S-LoRA: Serving Thousands of Concurrent LoRA Adapters. [arXiv 2311.03285](https://arxiv.org/abs/2311.03285)

8. Liu et al. (2024). DoRA: Weight-Decomposed Low-Rank Adaptation. [arXiv 2402.09353](https://arxiv.org/abs/2402.09353)

9. Biderman et al. (2024). LoRA Learns Less and Forgets Less. [arXiv 2405.09673](https://arxiv.org/abs/2405.09673)

10. Microsoft's LoRA code. [github.com/microsoft/LoRA](https://github.com/microsoft/LoRA)

The labs compute from the paper's formulas and figures. @datawithsuman
