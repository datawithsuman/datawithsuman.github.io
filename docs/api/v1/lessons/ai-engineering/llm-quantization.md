# LLM Quantization

> How does an LLM survive losing 75% of its bits?

- Track: AI Engineering › LLM inference and serving › Lessons
- Type: Concept · 35 min
- Page: https://aimlrounds.com/tracks/ai-engineering/llm-quantization/
- Before this: Prefill vs Decode (`ai-engineering/prefill-vs-decode`)
- Quiz topic: `infer`

## Intuition

### The situation

You're serving Llama 3.1 70B on 80 GB H100s. In 16-bit, it's 141 GB of weights, which is two GPUs before you've served anyone. A colleague suggests storing every weight in 4 bits. The interviewer asks:

> How does an LLM survive losing 75% of its bits?

**Running examples:** serving Llama 3.1 70B on 80 GB H100s, and 32 real consecutive weights from one row of Qwen2.5-0.5B-Instruct (layer 12, MLP down-projection), including one big outlier. Perplexity numbers are WikiText-2 (lower is better) unless stated.

#### An LLM is mostly numbers you have to store and move

A 70B model in 16-bit is 141 GB of weights before you've served a single user. That's two H100s just to hold it. And every decode step reads every weight from memory, so the bytes also set your speed limit (see Prefill vs Decode). Fewer bits per weight attacks both problems at once.

GB = parameters × bits ÷ 8 (8.03 B, 70.6 B, 405.9 B parameters). Weights only: 4-bit formats add a little for per-group scales (about 0.25–0.5 bits per weight), and you still need memory for the KV cache and activations.

Speed follows the bytes, but not perfectly. One precision step down (16 → 8 bits) is typically 30–50% faster in practice, not 2× (Inference Engineering, P. Kiely, ch. 5.1). The papers report bigger wins against slow baselines: GPTQ's 3-bit OPT-175B generates about 3.25× faster than FP16 on A100s and about 4.5× on A6000s GPTQ, p. 1; AWQ's 4-bit kernels average 3.2–3.3× over Hugging Face FP16 AWQ, p. 2.

The catch is quality. Round every weight carelessly and a large model can fall apart. The rest of this page is about why, and the three ideas that fix it.

### The idea

Think of a ruler with only 16 marks. One huge value forces the marks far apart, and everything small rounds to zero. Give each small group of numbers its own ruler, and a big value only hurts its own group. Every method is a choice about where the rounding error lands.

[Figure: Top: one scale for all weights. A big outlier stretches the grid, so the small weights all round to zero. Bottom: small groups get their own fine grid, so only the outlier's group is coarse.]

_Illustrative. The lab uses 32 real weights from Qwen2.5-0.5B, including one big outlier._

### Play

**Try to break it.** Go from 1 scale per 32 weights down to 1 per 4. Watch the error, the weights crushed to 0 and the extra storage.

#### An outlier should only stretch its own neighbourhood

With one scale per row, a single big weight sets Δ for thousands of small ones. Give every group of, say, 128 weights its own scale, and the damage stays local. The cost is storing more scales.

The same 32 weights at 3 bits, symmetric grid. Dashed lines mark group boundaries. Extra storage assumes one 16-bit scale per group. Real models use groups of 128: about 0.125 extra bits per weight, or about 0.25 with a zero-point too (GPTQ quotes ≈ 0.15).

The papers agree it's the cheapest big win. For 3-bit OPT-175B, GPTQ found group size 1,024 (about 0.02 extra bits) improves perplexity by about 0.2, and group size 128 (about 0.15 extra bits) by about another 0.1, ending only 0.1–0.3 off full precision GPTQ, p. 7. AWQ calls RTN "actually quite strong when using a small group size like 128" and uses g128 throughout AWQ, p. 7.

##### In hardware: block-scaled formats

New GPUs build groups into the number format. MXFP4 shares one scale per 32 values. NVIDIA's NVFP4 shares one per 16, and adds a second, per-tensor scale NVIDIA blog:

$$ x = x_{\text{e2m1}}\cdots_{\text{block}}\cdots_{\text{global}} \qquad \approx 4.5\ \text{bits/value} $$

From NVIDIA's Transformer Engine NVFP4 docs and the NVFP4 blog · hover any symbol.

- **the real value**: The number the model actually uses.

- **4-bit float**: Stored as E2M1: 1 sign, 2 exponent, 1 mantissa bit. Only values like 0, 0.5, 1, 1.5, 2, 3, 4, 6 (and negatives) are possible.

- **block scale**: One per 16 values, stored in FP8 (E4M3), so it can be a non-power-of-two. MXFP4 uses one per 32, restricted to powers of two (E8M0), which wastes precision.

- **tensor scale**: One FP32 scale for the whole tensor, so the block scales fit FP8 range: global max ÷ (448 × 6).

- **cost**: About 4.5 bits per value: 4 bits plus an 8-bit scale shared by 16 values.

**Now say why:** if smaller groups cut the error, why don't real models use a scale for every 4 weights?

## How it works

### How it works

#### In one breath

Quantization stores each number in 8 or 4 bits instead of 16, so the model fits on fewer GPUs and decode moves fewer bytes per token. Rounding always makes errors. The real methods differ in **where those errors land**: spread across small groups, steered away from the 1% of channels that matter (AWQ), cancelled by adjusting the remaining weights (GPTQ), or moved from hard-to-quantize activations into easy weights (SmoothQuant).What you'll be able to do after this: size a quantized deployment on a napkin, explain why plain rounding breaks large models, read the GPTQ, AWQ and SmoothQuant equations, and choose a format for a given bottleneck.

#### Quantizing = snapping numbers onto a grid

Pick a scale (the spacing between grid levels), divide each number by it, round to the nearest integer, and store the integer. To use it, multiply back by the scale. With N bits you get 2N levels, so 4 bits gives just 16.

$$ \bar{X} = \big\lceil\, X / \Delta \,\big\rfloor, \qquad \Delta = \max(|X|) \,/\, (2^{N-1}-1) $$

SmoothQuant's Eq. 1 (symmetric INT-N quantization) p. 2. Asymmetric quantization adds a zero-point so the grid can sit off-centre · hover any symbol.

- **stored integer**: What actually gets saved: an INT8 (or INT4) number.

- **original value**: The 16-bit weight or activation you want to compress.

- **round**: Snap to the nearest integer. This is where the error comes from, at most half a step.

- **step size**: The scale Δ: the gap between neighbouring levels. One Δ is shared by a whole group of numbers.

- **the biggest value**: Δ is set so the largest magnitude in the group lands on the top level. One outlier stretches the grid for everybody else.

- **levels per side**: 127 for INT8, 7 for INT4 (symmetric around zero).

##### Try it on 32 real weights

● original ● after rounding ● a non-zero weight rounded to exactly 0. One scale for all 32 (per-tensor style). The −0.44 weight is about 10× the typical size here, so it sets Δ for everyone.

Three more terms you'll need. **Granularity** is how many numbers share one scale: one per tensor, per row or channel, per token (for activations), or per small **group** such as 128 weights. **Weight-only** schemes (written W4A16: 4-bit weights, 16-bit activations) shrink memory and speed up decode. **Weight-and-activation** schemes (W8A8, FP8) also let the tensor cores do low-precision maths, which speeds up compute-bound prefill AWQ, §2, p. 2.

**Go deeper: why small errors matter**

Errors compound. π rounded to 3.14 is off by 0.05%, but cube it and you're off by 0.15%. Round π to 3 and π³ comes out as 27 instead of 31. An LLM stacks dozens of layers and thousands of tokens on top of every rounding error (example from Inference Engineering, ch. 5.1).

#### You can't avoid rounding error. You choose where it lands.

Every method below accepts that 4 or 8 bits will make mistakes, and differs only in where those mistakes are allowed to go. Each idea maps to one method, in this tab or the Play lab:

| Idea | What it does with the error | Method |
|---|---|---|
| **Confine it** | Give each small group its own scale, so an outlier only hurts its own group | group-wise, MX / NVFP4 |
| **Isolate it** | Keep the few outlier features in 16-bit | LLM.int8() |
| **Steer it** | Make the important channels' relative error smaller | AWQ |
| **Cancel it** | Adjust not-yet-rounded weights to undo the error already made | GPTQ |
| **Move it** | Shift outliers from activations (hard) into weights (easy) | SmoothQuant |

#### Past ~6.7B parameters, a few channels go huge, everywhere

Groups fix outliers in _weights_. Activations have a worse problem, discovered by LLM.int8(): in big models a handful of hidden dimensions carry values up to 20× larger than the rest, in nearly every layer and token LLM.int8(), p. 2.

1. Each bar is one input channel of a layer's activations, for one token (illustrative, shaped after the papers).

2. A few channels are tens of times bigger than the rest. In real OPT layers SmoothQuant measured outliers "∼100× larger than most of the activation values" p. 3.

3. They sit in the **same channels for every token**. At 6.7B, about 150,000 outliers per sequence are concentrated in just 6 hidden dimensions LLM.int8(), p. 2.

4. With one INT8 scale per token, the outliers set Δ and the normal channels get only 2–3 effective levels SmoothQuant, p. 3. Yet zeroing those few dimensions raises perplexity by 600–1,000% LLM.int8(), p. 2: they matter.

**LLM.int8()'s fix:** split each matrix multiply. Any feature dimension with a value above 6.0 runs in 16-bit; the other 99.9% run in INT8. Since outlier dimensions are at most 7 for models up to 13B, this costs about 0.1% extra memory p. 5. It preserved 16-bit accuracy all the way to 175B.

##### What it costs: speed

Mixed-precision decomposition is awkward for GPU kernels. LLM.int8() slows inference for models below 6.7B parameters p. 6, and SmoothQuant measured it "almost always slower than the FP16 baseline" SmoothQuant, p. 8. It's a memory tool, not a speed tool. AWQ and SmoothQuant both set out to protect outliers _without_ mixed precision.

#### Protect the 1% of weights that see the big activations

AWQ (MIT, MLSys 2024 best paper) starts from an experiment. Quantize OPT to 3 bits with g128, but keep 1% of the weight channels in FP16. Which 1%? If you choose by **weight size**, almost nothing improves. If you choose the channels whose **activations** are largest, perplexity nearly recovers. Importance lives in the inputs, not the weights AWQ, Table 1, p. 4.

##### OPT-6.7B, INT3 g128, keep 1% of channels in FP16 · perplexity (↓ better)

FP16 (no quantization)

10.86

RTN, nothing kept

23.54

keep 1%, chosen at random

24.23

keep 1%, biggest weights

22.37

keep 1%, biggest activations

11.39

The same pattern holds on OPT-1.3B and 13B, and with only 0.1% kept (OPT-6.7B: 11.58) Table 1.

But keeping FP16 channels brings back the mixed-precision problem. AWQ's trick: **scale the important channels up before rounding**, and scale their activations down by the same factor. The maths is unchanged, but those weights now span more grid levels, so their relative error shrinks.

$$ \text{Err}\big(Q(w\cdot s)\,(x/s)\big) = \Delta'\cdot\text{RoundErr}(ws/\Delta')\cdotx\cdot1/s $$

AWQ Eq. 3; the ratio of new to old error is (Δ′/Δ)·(1/s) p. 4 · hover any symbol.

- **error after scaling**: The output error for one weight w after multiplying it by s and dividing its input x by s.

- **new step size**: Δ′: the group scale after w is multiplied by s. Scaling one weight rarely changes the group max, so Δ′ ≈ Δ.

- **rounding error**: Still about 0.25 of a step on average, whatever s is: rounding error is roughly uniform.

- **the activation**: FP16, so no error of its own. Big x means this weight matters, which is why AWQ picks channels by activation size.

- **the payoff**: Divided by s. With s greater than 1 and Δ′ ≈ Δ, the error on this channel shrinks to about 1/s of what it was.

##### Try it: how hard should you scale?

Real measurements, not a simulation: OPT-6.7B, 1% salient channels scaled by s, INT3 g128 AWQ, Table 2, p. 4. Bigger s protects the salient channels more, but past s = 2 it starts growing Δ for the other weights in their groups, and perplexity gets worse again.

So AWQ searches for s per layer, on a small calibration set, to minimise the layer's output error:

$$ s^{*} = \arg\min_{s}\big\|Q(W\,\mathrm{diag}(s))\,(\mathrm{diag}(s)^{-1}X) - WX\big\|, \qquad s = s_X^{\,\alpha} $$

AWQ Eqs. 4–5 p. 5; grid of 20 for α p. 7.

- **best scales**: One scale per input channel, chosen per layer.

- **quantized, scaled weights**: Scale the weight columns by s, then quantize (e.g. INT4, g128).

- **inputs, scaled down**: Divide the calibration activations by s. This division gets fused into the previous layer, so it costs nothing at runtime.

- **original output**: The full-precision layer output to match.

- **search space**: s is just the average activation size per channel raised to α. A 20-point grid search over α in [0, 1] picks it. No gradients, no reconstruction.

##### Why practitioners like it

AWQ only measures average activation size per channel, so it needs little calibration data and is less prone to overfitting it than reconstruction methods like GPTQ p. 5. In the paper's tests it matched the 1%-FP16 mixed-precision result while staying all-INT3 (OPT-6.7B: 11.39 both) Table 3.

#### Round one column, then fix up the rest to compensate

GPTQ (IST Austria / ETH, ICLR 2023) doesn't try to make each weight accurate. It tries to make each layer's **output** accurate on real inputs. Rounding a weight creates an error; if inputs are correlated, nudging the not-yet-rounded weights can cancel most of it.

$$ \arg\min_{\widehat{W}}\ \big\|WX - \widehat{W}X\big\|_2^2 $$

GPTQ Eq. 1 p. 3; calibration data p. 6.

- **find quantized weights**: Search over weight matrices that sit on the quantization grid.

- **original output**: The layer applied to X: a small calibration set of real inputs (128 random 2,048-token C4 segments).

- **quantized output**: The same inputs through the quantized weights.

- **squared error**: Minimise the difference in outputs, not in weights. This is the key shift from RTN.

The update rule comes from Optimal Brain Quantization, which GPTQ inherits. After rounding weight q, shift all remaining weights F by:

$$ \delta_F = -\,\big(w_q-\mathrm{quant}(w_q)\big)\,/\,[H_F^{-1}]_{qq}\cdot(H_F^{-1})_{:,q} $$

GPTQ Eq. 2, with HF = 2XFXF⊤ p. 4.

- **the correction**: How much to move every still-unquantized weight in this row.

- **error just made**: The rounding error on weight q.

- **normaliser**: The diagonal entry of the inverse Hessian for weight q.

- **who can help**: Column q of the inverse Hessian, where H = 2XXᵀ. It encodes how the inputs correlate, so it says which other weights can absorb the error.

##### Try it: two weights, one correction

Illustrative toy: y = w₁x₁ + w₂x₂ with weights 0.08 and −0.13, grid step 0.25, unit-variance inputs. GPTQ rounds w₁, then moves w₂ by ρ × w₁'s error (what Eq. 2 gives for two inputs), then rounds w₂. Output error = expected squared error of y. With uncorrelated inputs there's nothing to exploit and both match.

Three engineering changes made this scale from 100M-parameter models to 175B p. 4–5:

1. A layer's weight matrix. The original method (OBQ) quantized weights one at a time in a greedy order, per row: cubic cost, hours for a 25M-parameter ResNet.

2. **Arbitrary order:** quantize columns left to right in the same order for every row. The greedy order barely helps on big layers, and now the inverse Hessian is shared by all rows, so it's updated once per column instead of once per weight.

3. **Lazy batch updates:** work on 128 columns at a time and keep the corrections inside the block. This turns memory-bound updates into compute-friendly ones, an order-of-magnitude speedup.

4. After each block, apply all its corrections to the remaining columns in one big matrix multiply.

5. **Cholesky reformulation:** precompute the needed rows of H⁻¹ with a stable Cholesky decomposition, plus dampening (1% of the mean diagonal added to H). Without it, large models hit numerical blow-ups.

The result: OPT-175B quantized on one A100 in about 4.2 hours Table 2, p. 7, losing only 0.03 perplexity at 4 bits (8.34 → 8.37) where RTN lost 2.2 (→ 10.54) Table 3.

##### Where it bends

Because GPTQ fits each layer to the calibration data, the AWQ authors argue it "may overfit the calibration set", hurting out-of-distribution domains, and that it needs a reordering trick for some models (LLaMA-7B, OPT-66B) AWQ, p. 2. On LLaMA-7B at 3 bits, plain GPTQ scored 8.81 versus RTN's 7.01; GPTQ with reordering scored 6.53 AWQ, Table 4.

#### Push the outliers from activations into the weights

Weight-only quantization saves memory, but the maths still runs in 16-bit. To use fast INT8 tensor cores you must quantize activations too (W8A8), and activation outliers break that. Per-channel activation scales would fix it, but INT8 matrix kernels can only apply scales along the outer dimensions (tokens, output channels), not the input channels SmoothQuant, p. 3. SmoothQuant's answer: divide each activation channel by a factor and multiply the matching weight row by the same factor. The product is identical.

$$ Y = \big(X\,\mathrm{diag}(s)^{-1}\big)\cdot\big(\mathrm{diag}(s)\,W\big), \qquad s_j = \max(|X_j|)^{\alpha} \,/\, \max(|W_j|)^{1-\alpha} $$

SmoothQuant Eqs. 3–4 p. 4; α values p. 5, Table 7.

- **same output**: The layer output does not change at all.

- **smoothed activations**: Each input channel divided by s_j. Outlier channels shrink. The division is folded into the previous layer norm or linear layer, offline.

- **adjusted weights**: Each matching weight row multiplied by s_j. Weights were flat and easy, so they can absorb some spread.

- **the smoothing factor**: Balances the two: activation max to the power α over weight max to the power 1 − α.

- **migration strength**: α = 0.5 splits the difficulty evenly and works for all OPT and BLOOM models; GLM-130B needed 0.75, and the Llama-2 runs used 0.85–0.9.

##### Try it: slide α

–

Illustrative channels shaped after SmoothQuant §3 (a few fixed channels ≈ 100× larger). Lower peak ÷ median means fewer grid levels wasted on outliers. The paper found 0.4–0.6 is the sweet spot on OPT-175B p. 8.

##### OPT-175B, INT8 weights and activations · average zero-shot accuracy (↑ better)

FP16 (original)

66.9%

W8A8, naive

35.5%

ZeroQuant

35.8%

LLM.int8() (FP16 outliers, slow)

66.7%

SmoothQuant-O3 (fastest setting)

66.8%

SmoothQuant Table 3. Measured speed: up to 1.56× faster with about half the memory in FasterTransformer, and up to 1.42× faster per decoding token p. 8, Table 8. On LLaMA it was nearly lossless, e.g. 7B: 11.51 → 11.56 perplexity Table 6.

## In practice

### In practice

#### The map: what gets quantized, and how cleverly

1. **Weight-only** post-training quantization keeps activations in 16-bit and compresses only the weights, usually to 4 bits. It's the standard for memory-bound decode and local inference. RTN with small groups is a strong baseline; GPTQ and AWQ are the two famous smart methods AWQ, p. 2.

2. **Weight and activation** quantization (W8A8) unlocks INT8 or FP8 matrix maths. Activations are much harder to quantize than weights because of outliers, which is what LLM.int8() and SmoothQuant tackle SmoothQuant, p. 3.

3. **Block-scaled formats** move the "one scale per small group" idea into the hardware, so each block of 16 or 32 values gets its own scale for free.

4. **Quantization-aware training** lets the model learn around the rounding. OpenAI post-trained gpt-oss's mixture-of-experts weights in MXFP4 (about 4.25 bits per parameter), which is how the 117B model fits on a single 80 GB GPU (gpt-oss model card).

#### Shipping a quantized model

1. **Pick precision from your bottleneck.** Out of memory or slow decode → weight-only 4-bit (AWQ or GPTQ). Compute-bound prefill or big batches → FP8 or INT8 weights and activations. On Hopper and later, FP8 is the usual first try.

2. **Choose what to quantize.** Start with linear-layer weights. Add activations and the KV cache only if you need them. Keep attention maths, and often embeddings and the output head, in 16-bit.

3. **Use small groups, never one scale per tensor**: g128 for INT4, or block-scaled formats (MXFP8, NVFP4).

4. **Calibrate with a smart method** on a few hundred samples that look like your traffic: AWQ or GPTQ for low-bit weights, SmoothQuant for W8A8.

5. **Measure against the original**: perplexity first, then benchmarks, then your own task evals. The bar is "difference indistinguishable from run-to-run noise".

6. **Back off where it hurts.** FP8 instead of FP4, fewer quantized components, or keep sensitive layers in 16-bit.

##### What's safe to quantize

| Component | Risk | Why |
|---|---|---|
| Linear-layer weights | low | The bulk of the model; flat distributions; well-studied methods |
| Activations | some | Outlier channels (see the outlier features section); needs smoothing or FP8 |
| KV cache | moderate | Big win for long contexts, but errors carry into every later token |
| Attention softmax | high | Sensitive to range; errors compound across thousands of tokens. Usually kept high-precision. |

Sensitivity ordering from Inference Engineering, ch. 5.1; SmoothQuant also keeps softmax, LayerNorm and other element-wise ops in FP16 p. 5.

##### Formats at a glance

| Format | What it is | Where it fits |
|---|---|---|
| BF16 / FP16 | 16-bit float | The baseline |
| FP8 (E4M3) | 1 sign, 4 exponent, 3 mantissa bits; wide dynamic range | Hopper and later: weights, activations, KV cache |
| INT8 (W8A8) | Integer with a scale, uniform levels | With smoothing (SmoothQuant); less range than FP8 |
| INT4 (W4A16) | 4-bit integer weights, g128 scales, 16-bit activations | GPTQ / AWQ checkpoints; memory-bound serving |
| MXFP4 / NVFP4 | 4-bit float, one scale per 32 (MX) or 16 values (NV) + global scale | Blackwell; gpt-oss ships MoE weights in MXFP4 |
| GGUF k-quants | File format with mixed per-layer precision | Laptops and edge (llama.cpp) |

Why float beats int at the same bits: the exponent spaces levels densely near zero and sparsely far out, which suits bell-shaped weights with a few outliers.

#### RTN vs GPTQ vs AWQ, same setup

Perplexity added on top of FP16 (↓ better); the label shows the absolute perplexity (FP16: 5.47, 4.88, 3.32). AWQ paper, Table 4, WikiText-2 p. 7.

##### Read these numbers fairly

- This table comes from the AWQ paper, so the comparison was set up by AWQ's authors. GPTQ's own paper reports on OPT and BLOOM, where it beats RTN by much larger margins because it compares per-row RTN without groups.

- At 4 bits with g128, all three are within about 0.1 perplexity on Llama-2: grouping did most of the work. The method matters mostly at 3 bits and below.

- Perplexity can hide task-specific damage. An INT8 model can pass a perplexity check and still fail a coding task if calibration data doesn't match the workload (interview guide). Always evaluate on your own tasks.

- Bigger models are easier to quantize. GPTQ: "larger models generally (with the exception of OPT-66B) appear easier to quantize" p. 7.

##### Update · my check (28 Oct 2026)

The field moved toward low-precision _formats_ and training. NVIDIA's NVFP4 (Blackwell) uses 16-value blocks with FP8 scales plus a per-tensor FP32 scale, about 4.5 bits per value (NVIDIA blog). OpenAI's gpt-oss-120b (117B total, 5.1B active parameters) was post-trained with MXFP4 MoE weights at about 4.25 bits per parameter so it fits one 80 GB GPU (model card). AWQ and GPTQ checkpoints remain the common open-weight 4-bit formats served by vLLM, TensorRT-LLM and others AWQ, p. 2.

#### Pick by bottleneck

| Situation | Start with |
|---|---|
| Model doesn't fit, decode-heavy chat, small batches | INT4 weight-only (AWQ or GPTQ, g128) |
| Hopper/Blackwell datacenter serving, big batches | FP8 weights + activations (+ FP8 KV cache) |
| INT8 hardware, need faster prefill | SmoothQuant W8A8 |
| Long contexts eating memory | KV-cache quantization (FP8 / INT8), then check quality |
| Laptop, CPU or Apple Silicon | GGUF k-quants (llama.cpp) |
| Blackwell, maximum throughput | NVFP4 / MXFP4, ideally from a model trained or calibrated for it |

#### What to keep, and what to watch

**The lesson:** quantization is a dial, not a switch. Weights are easy, activations are hard, and the whole game is controlling where the rounding error goes: confine it with groups, steer it with AWQ, cancel it with GPTQ, move it with SmoothQuant.

##### Great for

- Fitting a big model on fewer GPUs or a laptop

- Faster decode at small batch sizes (memory-bound)

- Freeing memory for KV cache → bigger batches, longer contexts

- Large models: each weight matters less

##### Watch out

- Small models are fragile: each weight carries more of the load

- 3 bits and below: quality drops fast, even with GPTQ/AWQ

- Calibration data that doesn't match your domain

- Speedups need real low-bit kernels; a smaller file alone isn't speed

- W4A16 barely speeds up compute-bound prefill

Author-stated limits: LLM.int8() is slower than FP16 below 6.7B; GPTQ needs reordering for some models; SmoothQuant needs a per-model α. The "small models are fragile" and "kernels matter" points are my synthesis of the tables above.

#### What changed since these methods, and what to evaluate

##### Four additions

- **FP8 is the safe default on modern GPUs.** A study of over 500,000 evaluations on the Llama 3.1 family found FP8 weights and activations (W8A8-FP) essentially lossless, INT8 W8A8 within about 1–3% per task, and 4-bit weight-only (W4A16) on par with INT8 W8A8; W4A16 suited low-batch serving best, W8A8 high-throughput serving Kurtic et al., ACL 2025.

- **Rotations make 4-bit activations possible.** Multiplying weights and activations by orthogonal (Hadamard) rotations spreads outliers across channels without changing the model's output. QuaRot quantized weights, activations and the KV cache to 4 bits; Llama 2 70B lost at most 0.47 WikiText-2 perplexity and kept 99% of zero-shot accuracy Ashkboos et al., NeurIPS 2024. SpinQuant learns the rotations, narrowing the W4A4KV4 gap on Llama 2 7B to 2.9 points Liu et al., 2024.

- **Quantize the KV cache too.** At high concurrency the KV cache, not the weights, limits batch size; an FP8 KV cache halves it. See Scaling Inference for why FP8 weights alone may not reduce GPU count.

- **Evaluate on tasks, not just perplexity.** Perplexity can hide drops on reasoning, maths, code and long-context tasks; check your own task metrics before and after quantizing.

**Added 7 Nov 2026:** since prefill and decode want different formats, a 2026 paper from NVIDIA and ISTA proposes quantizing them differently, with low-precision maths for prefill and compact weights for decode. It's early research, but it fits the phase split in Prefill vs Decode.

### The answer that sounds right

#### Round-to-nearest works… until it falls off a cliff

The obvious method is **RTN**: pick a scale per row and round every weight to the nearest level. GPTQ's authors ran exactly that, with one scale per row, on the whole OPT family. At 4 bits it mostly survives. At 3 bits it collapses at every size. Drag through the model sizes:

–

OPT models, WikiText-2 perplexity, per-row asymmetric grid, no grouping. Bars are on a log scale capped at 100 GPTQ, Table 3, p. 7.

##### What breaks: outliers

At 175B, 4-bit RTN loses 2.2 perplexity points, "performing worse than the 10× smaller full-precision 13B model", and at 3 bits it "collapses completely" GPTQ, p. 7. The cause is the same thing you saw with the −0.44 weight above, at scale: a few huge values stretch the grid, and everything small gets rounded into a handful of levels or to zero.

## Say it

### How does an LLM survive losing 75% of its bits?

#### The interviewer pushes further

Follow-up 1 of 6

Why does 4-bit weight-only quantization speed up decode but not prefill?

Decode reads every weight for a few tokens, so it's memory-bandwidth-bound: 4× fewer bytes directly helps. Prefill does thousands of FLOPs per byte, so it's compute-bound, and W4A16 dequantizes back to 16-bit before the maths. To speed up prefill you need low-precision compute: W8A8 (SmoothQuant) or FP8.

Follow-up 2 of 6

Symmetric vs asymmetric quantization?

Symmetric centres the grid on zero: Δ = max|w| ÷ (2b−1 − 1), no zero-point, simpler kernels. Asymmetric adds a zero-point so the grid covers [min, max] exactly, which helps one-sided distributions (e.g. after ReLU). LLM.int8() found outliers are mostly one-sided, which is why zero-point quantization did better before decomposition p. 9.

Follow-up 3 of 6

GPTQ or AWQ?

Both give good 4-bit weight-only models. AWQ needs less calibration data and generalises better across domains because it only uses activation statistics; GPTQ reconstructs each layer's output and can overfit the calibration set but is very strong at 3 bits on big models. At 4-bit g128 on Llama-2 they're within about 0.1 perplexity, so pick by tooling and kernel support.

Follow-up 4 of 6

Your INT8 model passes perplexity but fails a coding task. What happened?

Perplexity is an average that hides task-specific regressions. Likely the calibration set didn't look like code, so the wrong channels were protected or the scales were off. Re-calibrate on representative data and evaluate on the downstream task.

Follow-up 5 of 6

Why are activations harder to quantize than weights?

Weights are flat and bell-shaped. Activations have outlier channels about 100× larger than the rest, in fixed channels for every token, emerging around 6.7B parameters. Per-channel activation scales would fix it but don't fit INT8 GEMM kernels, hence LLM.int8()'s decomposition or SmoothQuant's migration.

Follow-up 6 of 6

Would you quantize the KV cache?

For long contexts, yes: it can be bigger than the weights. FP8 KV cache is common and usually safe; INT4 KV has a small but measurable loss. Errors carry into every later token, so test on long-context tasks.

#### The 30-second answer

Quantization stores weights, and sometimes activations, in 8 or 4 bits instead of 16. It cuts memory and speeds up memory-bound decode. The hard part is outliers: a few huge values stretch the grid so small values lose precision. Groups confine them, AWQ protects the channels with big activations by scaling them, GPTQ cancels rounding error using second-order information from calibration data, and SmoothQuant moves activation outliers into weights so INT8 maths works. Then you verify on your own evals, not just perplexity.

**Go further**

#### The 2-minute walkthrough

Size first: 70B in BF16 is 141 GB, two H100s; in 4-bit about 35 GB, one. Then the grid: Δ = max ÷ (2N−1 − 1), and why one outlier wrecks it. RTN's cliff on OPT at 3 bits. Fixes: g128 groups (cheap, ~0.15–0.25 bits); outlier features above 6.7B (LLM.int8 isolates them, but it's slow); AWQ, which keeps the 1% of weights fed by large activations safe by scaling, chosen by a grid search over α; GPTQ, which quantizes columns and pushes each error onto the remaining columns via the inverse Hessian, in 4 GPU-hours for 175B; SmoothQuant for W8A8 via sj = max|X|α ÷ max|W|1−α. Close with the decision: weight-only 4-bit for memory-bound decode, FP8 or W8A8 for compute, block-scaled FP4 on Blackwell, and always check task evals.

#### What not to say

- "4-bit is 4× faster." Speed depends on kernels and on whether you're memory- or compute-bound; one step down is often 30–50% faster.

- "Quantization doesn't hurt quality." At 4-bit g128 on big models it's small; at 3 bits, on small models or on activations without smoothing, it can be severe.

- "Pick important weights by their magnitude." AWQ showed that magnitude is about as good as random; activations tell you importance.

- "Perplexity looked fine, so we shipped." Evaluate on your tasks.

**Key terms and sources**

Built from GPTQ, AWQ, SmoothQuant and LLM.int8() (read in full), NVIDIA's NVFP4 docs and the gpt-oss model card · checked 28 Oct 2026 · updated 29 Oct 2026

#### Glossary

| **Scale (Δ)** | Spacing between quantization levels; one per tensor, channel, token or group. |
|---|---|
| **Zero-point** | Offset that lets an asymmetric grid sit off-centre. |
| **RTN** | Round-to-nearest: the plain baseline. |
| **Group size (g128)** | How many weights share one scale. |
| **W4A16 / W8A8** | Bits for weights / activations. |
| **PTQ / QAT** | Post-training quantization (no retraining) / quantization-aware training. |
| **Calibration set** | A few hundred real inputs used to pick scales or corrections. |
| **Outlier features** | A few hidden dimensions with huge values in every token, from about 6.7B parameters up. |
| **Salient channels** | Weight channels that multiply large activations; AWQ protects them. |
| **Hessian (H = 2XXᵀ)** | Captures how layer inputs correlate; GPTQ uses its inverse to spread corrections. |
| **Migration strength (α)** | SmoothQuant's dial for how much difficulty moves from activations to weights. |
| **Perplexity** | How surprised the model is by real text; lower is better; sensitive to quantization damage. |

#### What this page is built from

1. Frantar et al., GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers, IST Austria / ETH, ICLR 2023 (code).

2. Lin et al., AWQ: Activation-aware Weight Quantization, MIT, MLSys 2024 best paper (code).

3. Xiao et al., SmoothQuant: Accurate and Efficient Post-Training Quantization for LLMs, MIT / NVIDIA, ICML 2023 (code).

4. Dettmers et al., LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale, NeurIPS 2022.

5. NVIDIA, Introducing NVFP4 and Transformer Engine NVFP4 docs.

6. OpenAI, gpt-oss model card (MXFP4 MoE weights, single 80 GB GPU for gpt-oss-120b).

7. P. Kiely, _Inference Engineering_ (Baseten), ch. 5.1: precision speedups, sensitivity ordering, π example.

8. Qwen2.5-0.5B-Instruct weights (layer 12, MLP down-projection) for the 32-weight example.

9. Interview angle: techinterview.org, GPTQ, AWQ and FP8 in the LLM inference interview.

10. "Disaggregated Quantization: Specializing LLM Prefill and Decode", 2026, arXiv:2609.26333.
