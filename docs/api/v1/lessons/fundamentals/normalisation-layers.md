# BatchNorm vs LayerNorm vs RMSNorm

> Why do transformers use LayerNorm instead of BatchNorm?

- Track: Fundamentals › Deep Learning › Training deep nets
- Type: Concept · 25 min
- Page: https://aimlrounds.com/tracks/fundamentals/normalisation-layers/
- Before this: Vanishing & Exploding Gradients (`fundamentals/vanishing-exploding-gradients`)
- Quiz topic: `train`

## Intuition

### The situation

Your transformer works in training, then a colleague swaps in BatchNorm, and results change with the batch size. The interviewer asks:

> Why do transformers use LayerNorm instead of BatchNorm?

**Running example:** a hidden layer of the delivery network produces 8 activations per order. Different features sit at very different scales (one hovers around 40, another around 0.2). We follow one particular order, order #1, through the normalisation layer.

#### Activations drift to awkward scales

As weights change during training, each layer's outputs shift in mean and scale, so the next layer keeps chasing a moving target, and features at very different scales make the loss surface badly conditioned. Ioffe & Szegedy (2015) called this _internal covariate shift_ and fixed it by normalising each layer's inputs. BatchNorm let their Inception network reach the same accuracy in **14× fewer training steps** and tolerate much higher learning rates.

### The idea

Think of grading exam papers on a curve. BatchNorm grades each question against everyone in the room, so your score depends on who else showed up. LayerNorm rescales within your own paper, so the room doesn't matter.

[Figure: Two grids with examples as rows and features as columns. BatchNorm normalises down a column across the batch. LayerNorm normalises along a row within one example.]

_The same recipe applied along a different axis._

### Play

**Try to break it.** On BatchNorm, shrink the batch size and watch the spread across random batches. Then switch to LayerNorm and RMSNorm.

#### Does order #1's output depend on its batch-mates?

400 batches, each = order #1 plus (B − 1) random other orders from 2,000. Histogram of order #1's normalised feature 1 (before γ, β). Fixed seed.

With BatchNorm at batch size 8, order #1's normalised value has a spread of **0.40** across batches: the same order gets a different representation depending on who it was batched with. At batch size 64 the spread drops to 0.14, and at batch size 1 the output is exactly **0**. LayerNorm and RMSNorm give the **same value in every batch** (spread 0), because they only look at order #1's own 8 features.

**Now say why:** why does one order's output depend on its batch-mates only under BatchNorm?

## Maths

### Maths

#### In one breath

A normalisation layer rescales activations to a standard range (then lets the network learn its own scale γ and shift β), which keeps signals well-behaved and lets you train faster with higher learning rates. **BatchNorm** normalises each feature **across the examples in the batch**, so an example's output depends on what else is in its batch; it needs running averages for inference and breaks down for tiny batches. **LayerNorm** normalises **across the features of one example**, so it behaves the same at any batch size, in training and inference; that's why transformers use it. **RMSNorm** drops LayerNorm's mean-subtraction and only divides by the root-mean-square: cheaper, about as good, and the norm used in LLaMA-style LLMs. What you'll be able to do after this: say which axis each norm uses, explain BatchNorm's batch dependence and train/inference gap, and explain why LLMs use pre-norm RMSNorm.

#### Same recipe, different axis

$$ \hat{x} = \frac{x - {\mu}}{{\sqrt{\sigma^2 + \epsilon}}}, \qquad y = {\gamma\,\hat{x} + \beta} $$

- **mean**: BatchNorm: the mean of this feature over the B examples in the batch. LayerNorm: the mean over the d features of this one example.

- **standard deviation**: Same choice of axis as the mean; ε (e.g. 10⁻⁵) avoids dividing by zero.

- **learned scale and shift**: γ and β are trained, so the network can undo the normalisation if that helps; normalising doesn’t limit what the layer can represent.

$$ \mathrm{RMSNorm}(x) = \frac{x}{{\sqrt{\tfrac{1}{d}\sum_i x_i^2 + \epsilon}}} \odot {\gamma} $$

Zhang & Sennrich, NeurIPS 2019 [arXiv:1910.07467](https://arxiv.org/abs/1910.07467): comparable quality to LayerNorm with 7%–64% less running time across their models. Used in T5, LLaMA, Mistral and most recent open LLMs.

- **root mean square**: RMSNorm skips the mean entirely and divides by the RMS of the features: one statistic instead of two.

- **learned gain**: Only a scale γ, no shift β.

#### Smoother loss, not (only) less covariate shift

Santurkar et al. (2018) [arXiv:1805.11604](https://arxiv.org/abs/1805.11604) showed that BatchNorm networks train well even when noise is injected to _increase_ covariate shift. Their explanation: normalisation makes the loss surface and its gradients **smoother** (more Lipschitz), so larger learning rates are safe. In practice normalisation layers give: faster training, higher usable learning rates, less sensitivity to initialisation, and (for BatchNorm) a mild regularising effect from the batch noise you saw in the lab.

#### Pre-norm vs post-norm

##### Post-norm (original Transformer, 2017)

x ← LayerNorm(x + Sublayer(x)). The norm sits on the residual path, so gradients near the input can be badly scaled; training needs a careful learning-rate warmup.

##### Pre-norm (GPT-2 onwards, LLaMA)

x ← x + Sublayer(Norm(x)). The residual path stays a clean identity; Xiong et al. (2020) show gradients are well-behaved at initialisation and warmup can be shortened or removed. Standard in today's LLMs, usually with RMSNorm.

Xiong et al., "On Layer Normalization in the Transformer Architecture", ICML 2020 [arXiv:2002.04745](https://arxiv.org/abs/2002.04745). Covered again in the Transformer block lesson.

## In practice

### In practice

#### Cheat sheet

| | BatchNorm | LayerNorm | RMSNorm |
|---|---|---|---|
| **Statistics over** | batch (and spatial dims), per feature | features of one example | features of one example |
| **Subtracts mean?** | yes | yes | no |
| **Learned params** | γ, β | γ, β | γ |
| **Train ≠ inference?** | yes (running stats) | no | no |
| **Batch size 1** | breaks | fine | fine |
| **Typical use** | CNNs (ResNet) | Transformers (BERT, GPT-2) | LLMs (T5, LLaMA) |

Group Norm (Wu & He 2018) is the usual BatchNorm replacement for vision with small batches (e.g. detection, segmentation).

### The answer that sounds right

#### "BatchNorm everywhere"

- **Small batches:** with 2–4 examples the batch mean and variance are noisy; with batch size 1 every feature normalises to exactly 0 (each value equals its own mean).

- **Train/inference mismatch:** at inference there's no batch, so BatchNorm uses **running averages** collected during training. Forget `model.eval()` and predictions depend on the batch; data drift makes the stored statistics stale.

- **Sequences:** variable lengths and padding make per-position batch statistics awkward, and autoregressive generation runs one token at a time. This is why transformers use LayerNorm.

## Say it

### Why do transformers use LayerNorm instead of BatchNorm?

#### The interviewer pushes further

Follow-up 1 of 3

What changes between model.train() and model.eval() for BatchNorm?

Training uses the current batch's statistics and updates exponential running averages; eval uses the stored running averages, so outputs no longer depend on the batch.

Follow-up 2 of 3

Where does BatchNorm go relative to the activation?

The original paper put it before the non-linearity (after the linear/conv layer); both orders are used in practice. In ResNets it's conv → BN → ReLU.

Follow-up 3 of 3

Why doesn't LayerNorm need running statistics?

Its statistics come from the example itself, which is available at inference.

#### The 30-second answer

All three standardise activations and then apply a learned scale (and shift). BatchNorm computes mean and variance per feature across the batch, so outputs depend on the batch, it needs running statistics at inference, and it fails with tiny batches; it works well in CNNs. LayerNorm computes them across the features of each example, so it's batch-independent and identical in training and inference, which suits transformers and variable-length sequences. RMSNorm drops the mean and only divides by the root mean square, which is cheaper with similar quality, so modern LLMs use pre-norm RMSNorm. Normalisation mainly helps by smoothing the loss landscape, which permits higher learning rates.

**Go further**

#### What not to say

- "LayerNorm normalises across the batch." It's across features.

- "BatchNorm works because it removes internal covariate shift." That was the original motivation; later work points to a smoother loss landscape.

**Key terms and sources**

What normalisation layers compute, which axis each one normalises over, train vs inference behaviour, why transformers use LayerNorm/RMSNorm, and pre-norm vs post-norm · built from Ioffe & Szegedy (2015), Ba, Kiros & Hinton (2016), Santurkar et al. (2018), Zhang & Sennrich (2019) and Xiong et al. (2020) · checked 29 Oct 2026

#### Sources

1. S. Ioffe & C. Szegedy, "Batch Normalization: Accelerating Deep Network Training by Reducing Internal Covariate Shift", ICML 2015, [arXiv:1502.03167](https://arxiv.org/abs/1502.03167).

2. J. Ba, J. Kiros & G. Hinton, "Layer Normalization", [arXiv:1607.06450](https://arxiv.org/abs/1607.06450), 2016.

3. S. Santurkar, D. Tsipras, A. Ilyas & A. Mądry, "How Does Batch Normalization Help Optimization?", NeurIPS 2018, [arXiv:1805.11604](https://arxiv.org/abs/1805.11604).

4. B. Zhang & R. Sennrich, "Root Mean Square Layer Normalization", NeurIPS 2019, [arXiv:1910.07467](https://arxiv.org/abs/1910.07467).

5. R. Xiong et al., "On Layer Normalization in the Transformer Architecture", ICML 2020, [arXiv:2002.04745](https://arxiv.org/abs/2002.04745).

6. Y. Wu & K. He, "Group Normalization", ECCV 2018, [arXiv:1803.08494](https://arxiv.org/abs/1803.08494).
