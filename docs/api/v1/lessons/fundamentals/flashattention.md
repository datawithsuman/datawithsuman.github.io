# FlashAttention

> Why is exact attention faster when it does more maths?

- Track: Fundamentals › LLMs › Modern architecture
- Type: Concept · 25 min
- Page: https://aimlrounds.com/tracks/fundamentals/flashattention/
- Before this: Self-Attention (Q, K, V) (`fundamentals/self-attention`)
- Quiz topic: `arch`
- Sources checked: 2026-10-29 · Text last changed: 2026-11-20 · Version: 4c40e728a0

## Intuition

### The situation

The team fine-tunes the assistant on chat transcripts of up to 32k tokens. Plain attention runs out of memory. FlashAttention runs, finishes faster and gives the same numbers, even though it does more arithmetic. The interviewer asks:

> Why is exact attention faster when it does more maths?

Where this lesson sits: the inside of the attention box. FlashAttention changes how it's computed, not what it computes.

Background: Self-Attention · Attention Variants.

**Running example:** the team fine-tunes the support assistant on long chat transcripts (up to 32k tokens). With plain attention the job runs out of memory; with FlashAttention it runs, faster, and gives the same numbers.

#### Attention is memory-bound

An A100 does about 312 TFLOPS of bf16 matrix maths but moves only about 1.5–2 TB/s from HBM. Softmax, masking and dropout do little arithmetic per byte, so a standard implementation spends most of its time waiting on memory: write S = QKᵀ (N × N) to HBM, read it for the softmax, write P, read P to multiply by V. The fast on-chip SRAM is tiny (about 20 MB in total across the chip, a couple of hundred KB per streaming multiprocessor) but an order of magnitude faster.

### The idea

Think of cooking with the pantry at the far end of a long hall. The slow part isn't the chopping, it's the walking. So you bring one small tray to your counter, finish it there and only then go back. You chop slightly more, and walk far less.

[Figure: On GPT-2 medium, FlashAttention does slightly more arithmetic, 75.2 against 66.6 gigaFLOPs, but moves 4.4 gigabytes of memory against 40.3, and takes 7.3 milliseconds against 41.7.]

_Measured in the paper on GPT-2 medium, sequence length 1,024, on an A100._

### Play

**Try to break it.** Drag the sequence length up to 32k, and compare the score matrix with the saved row statistics.

#### The N × N matrix doesn't fit

32 heads, batch 1, bf16 scores; FlashAttention stores one fp32 log-sum-exp per row and head for the backward pass. Q, K, V and the output are needed by both methods and are not counted.

At **32k tokens** the standard score matrix is **64 GiB for a single layer**, almost a whole 80 GB GPU, and training must keep it for the backward pass. FlashAttention keeps only **4 MiB** of row statistics and recomputes the tiles during the backward pass instead of storing them: more FLOPs, far less memory traffic. On GPT-2 medium (sequence 1,024, A100) the paper measured 66.6 vs 75.2 GFLOPs for standard vs FlashAttention, but 40.3 GB vs **4.4 GB** of HBM reads and writes, and 41.7 ms vs **7.3 ms**.

**Now say why:** FlashAttention throws the matrix away, so how can the backward pass still work?

## Maths

### Maths

#### In one breath

Standard attention writes the full N × N score matrix to GPU main memory (HBM), reads it back for the softmax, writes the probabilities, and reads them again. GPUs compute much faster than they move data, so this traffic, not the FLOPs, dominates the runtime, and the N² matrix also eats memory. **FlashAttention** splits Q, K and V into tiles that fit in fast on-chip SRAM, computes attention tile by tile, and never stores the full matrix. The trick that makes this possible is the **online softmax**: keep a running maximum and running sum per row, and rescale earlier partial results when a bigger score appears. The result is **exact** attention, not an approximation, with memory that grows linearly in sequence length. On GPT-2 medium it cut HBM traffic from 40.3 GB to 4.4 GB and runtime from 41.7 ms to 7.3 ms. What you'll be able to do after this: explain why attention is memory-bound, run the online softmax by hand, and say what each FlashAttention version improved.

#### Softmax without seeing the whole row

Softmax needs the row's maximum (for numerical safety) and its sum, which seems to require the whole row first. The online softmax processes scores in blocks and fixes up the past whenever the maximum changes:

$$ {m_{new} = \max(m, \max_j s_j)}, \quad {\ell_{new} = \ell\,}{e^{m - m_{new}}}{ + \textstyle\sum_j e^{s_j - m_{new}}}, \quad {o_{new} = o\,e^{m-m_{new}} + \textstyle\sum_j e^{s_j - m_{new}} v_j} $$

Milakov & Gimelshein, "Online normalizer calculation for softmax", 2018, [arXiv:1805.02867](https://arxiv.org/abs/1805.02867). FlashAttention applies this per block of rows and keeps m and ℓ (as one log-sum-exp per row) for the backward pass.

- **new running max**: Compare the old maximum with the largest score in the new tile.

- **rescale factor**: Everything accumulated so far was computed relative to the old max; multiplying by e^(m_old − m_new) corrects it.

- **running sum**: Rescaled old sum plus this tile’s exponentials.

- **running output**: The weighted sum of values gets the same rescaling; dividing by ℓ at the end gives exactly softmax(scores)·V.

One query row: scores s = [2, 1, 0.5, 3, −1, 2.5, 0, 4] over 8 keys, values v = [10, 20, …, 80]. The "output so far" column is the softmax-weighted average of the values seen so far.

With tiles of 4, the first tile has maximum 3 and a partial output of **30.81**; the second tile brings a larger score (4), so the old sum and output are rescaled by e3−4 before adding the new terms, and the result is **61.69**. Every tile size gives the same answer as the exact softmax, up to floating-point rounding: this is why FlashAttention is exact, not an approximation.

## In practice

### In practice

#### FlashAttention 1, 2, 3

| Version | What changed | Reported result |
|---|---|---|
| FlashAttention (2022) | IO-aware tiling + online softmax + recomputation in the backward pass | up to 9× fewer HBM accesses; 15% faster BERT-large training, 3× faster GPT-2 (1k context) |
| FlashAttention-2 (2023) | fewer non-matmul operations, parallelism over the sequence, better work split between warps | about 2× faster than v1, 50–73% of A100 peak FLOPs |
| FlashAttention-3 (2024) | Hopper-specific: asynchronous Tensor Cores and TMA, overlapping softmax with matmuls, FP8 | 1.5–2.0× faster than v2 on H100, up to 740 TFLOPS in FP16 (75% of peak) |

FlashAttention is the default attention kernel in PyTorch's `scaled_dot_product_attention`, Hugging Face Transformers and most training and serving stacks. It works with GQA, causal masks and sliding windows. Inference engines add variants like FlashDecoding, which splits the long KV cache across thread blocks when only one query token is processed.

#### Count bytes moved, not FLOPs

On modern GPUs, an algorithm that does a little more arithmetic but moves far fewer bytes between memory levels wins. FlashAttention fuses the whole attention computation into one kernel that keeps tiles in SRAM, made possible by an online softmax that never needs the full row.

For why bytes matter so much, read GPUs, TPUs and Memory Bandwidth.

### The answer that sounds right

#### "It's faster because it does fewer FLOPs"

It sounds right, since faster usually means less work. But it does slightly more: 75.2 against 66.6 GFLOPs on GPT-2 medium. It moves far fewer bytes, 4.4 GB against 40.3 GB. And compute is still quadratic. It's memory that becomes linear, so don't say FlashAttention makes attention linear.

## Say it

### Why is exact attention faster when it does more maths?

#### The interviewer pushes further

Follow-up 1 of 3

Is FlashAttention an approximation?

No. It computes the same result as standard attention up to floating-point rounding; sparse and linear attention are the approximate methods.

Follow-up 2 of 3

Does it change the O(N²) compute?

No, FLOPs stay quadratic (slightly higher due to recomputation). It reduces memory from O(N²) to O(N) and cuts memory traffic, which is what made it faster.

Follow-up 3 of 3

Why recompute in the backward pass instead of storing P?

Storing P is N² memory and traffic; recomputing it from Q, K and the saved log-sum-exp in SRAM is cheaper than reading it back from HBM.

#### The 30-second answer

Standard attention materialises the N by N score and probability matrices in GPU high-bandwidth memory and reads them back several times, so it's memory-bandwidth bound and uses quadratic memory. FlashAttention tiles Q, K and V into blocks that fit in on-chip SRAM and fuses the matmuls, softmax and value multiply into one kernel, using an online softmax that keeps a running max and sum per row and rescales partial results. It's exact, uses linear memory, and recomputes tiles in the backward pass instead of storing them. Version 2 improved parallelism and work partitioning, version 3 uses Hopper's asynchronous hardware and FP8.

**Go further**

#### What not to say

- "FlashAttention makes attention linear." Memory is linear; compute is still quadratic.

- "It's faster because it does fewer FLOPs." It does slightly more; it moves far fewer bytes.

**Key terms and sources**

Why standard attention is slow because of memory traffic rather than arithmetic, how FlashAttention computes exact attention in tiles that stay in fast on-chip memory using an online softmax, and what FlashAttention-2 and -3 added · built from Dao et al. (FlashAttention, NeurIPS 2022), Milakov & Gimelshein (online softmax, 2018), Rabe & Staats (2021), Dao (FlashAttention-2, 2023) and Shah et al. (FlashAttention-3, NeurIPS 2024) · checked 29 Oct 2026

#### Sources

1. T. Dao, D. Fu, S. Ermon, A. Rudra & C. Ré, "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness", NeurIPS 2022, [arXiv:2205.14135](https://arxiv.org/abs/2205.14135) (Fig. 2 for the GPT-2 medium numbers).

2. T. Dao, "FlashAttention-2: Faster Attention with Better Parallelism and Work Partitioning", 2023, [arXiv:2307.08691](https://arxiv.org/abs/2307.08691).

3. J. Shah et al., "FlashAttention-3: Fast and Accurate Attention with Asynchrony and Low-precision", NeurIPS 2024, [arXiv:2407.08608](https://arxiv.org/abs/2407.08608).

4. M. Milakov & N. Gimelshein, "Online normalizer calculation for softmax", 2018, [arXiv:1805.02867](https://arxiv.org/abs/1805.02867); M. Rabe & C. Staats, "Self-attention Does Not Need O(n²) Memory", 2021, [arXiv:2112.05682](https://arxiv.org/abs/2112.05682).
