# Weight Decay vs L2, and AdamW

> Why is Adam with L2 not the same as AdamW?

- Track: Fundamentals › Deep Learning › Regularisation and debugging
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/weight-decay-and-adamw/
- Before this: Regularized Linear Models (`fundamentals/regularized-linear-models`), Gradient Descent, Momentum & Adam (`fundamentals/gradient-descent`)
- Quiz topic: `train`
- Sources checked: 2026-10-29 · Text last changed: 2026-11-20 · Version: a2517ebd2a

## Intuition

### The situation

You train with Adam and set a weight_decay value. The weights with noisy gradients barely shrink, while quiet ones shrink a lot. The interviewer asks:

> Why is Adam with L2 not the same as AdamW?

**Running example:** two weights in the late-delivery network. Weight A connects to a feature that changes a lot from order to order, so its gradients are large and noisy. Weight B connects to a feature that barely matters, so its gradients are tiny. Both start at 1. A good regulariser should shrink both **by the same rule**; it shouldn't care how noisy their gradients happen to be.

#### Large weights make jagged models

A network that fits noise usually does it with large weights: sharp turns in the decision boundary need big slopes. Penalising weight size is the oldest regulariser in machine learning (ridge regression; Regularised linear models). The question is how to apply it with modern optimisers.

### The idea

Think of a tax. AdamW charges every weight the same rate. Adam with L2 puts the tax through Adam's own scaling first, so weights with big gradients get a discount, and quiet ones get overcharged.

[Figure: With Adam plus L2, a weight with noisy gradients barely shrinks while a quiet weight shrinks a lot. With AdamW, both shrink by the same amount.]

_Illustrative. The grey shows each weight's starting size._

### Play

**Try to break it.** Set the gradient noise to tiny, then to large, and compare the final weight under Adam + L2 and AdamW.

#### How much does each weight shrink?

The weight starts at 1; its loss gradient is pure noise with the chosen size (no signal), so only regularisation moves it on average. Adam, learning rate 0.01, 1,000 steps, averaged over 30 runs, fixed seeds.

With λ = 0.1, **AdamW** shrinks the weight to about **0.34** whether its gradients are tiny or large: the same regularisation for every weight. **Adam + L2** is wildly uneven: a weight with tiny gradients is crushed to **0.015**, while one with large gradients keeps **0.84**, barely regularised. Those busy, high-gradient weights are exactly the ones most likely to overfit.

**Now say why:** why does one method's shrinkage depend on the gradients, while the other's doesn't?

## Maths

### Maths

#### In one breath

**Weight decay** shrinks every weight a little towards zero on each step, which keeps weights small and the model smoother. With plain SGD, that is exactly the same as adding an **L2 penalty** λ‖w‖²/2 to the loss. With **Adam** it is not: an L2 term gets added to the gradient and then divided by Adam's per-weight scale √v, so weights with large, noisy gradients are barely regularised while weights with small gradients are crushed. **AdamW** (Loshchilov & Hutter) **decouples** the decay: Adam updates from the loss gradient only, then every weight shrinks by the same factor (1 − ηλ). It generalises better and is the default optimiser for training transformers. What you'll be able to do after this: explain the SGD equivalence, show why L2 inside Adam is uneven, and choose AdamW settings.

#### L2 penalty vs weight decay

$$ {\tilde{L}(w) = L(w) + \tfrac{\lambda}{2}\lVert w\rVert^2}, \qquad {w \leftarrow (1-\eta\lambda)\,w - \eta\,\nabla L}, \qquad {\text{SGD: identical}} $$

- **L2 penalty**: Add λ‖w‖²/2 to the loss. Its gradient is λw, so it joins the loss gradient before the optimiser sees it.

- **weight decay**: After the gradient step, multiply every weight by (1 − ηλ): a fixed fraction shrink per step (Krogh & Hertz 1992).

- **same for SGD**: For plain SGD, w − η(∇L + λw) = (1 − ηλ)w − η∇L. The two forms are identical.

## In practice

### In practice

#### Typical settings

| Setting | Optimiser and decay |
|---|---|
| ResNet on ImageNet (SGD) | SGD + momentum, weight decay 1e-4 (L2 and decay are the same here) |
| Transformers / LLMs | AdamW, weight decay ≈ 0.1 (LLaMA used 0.1), with warmup + cosine schedule |
| Fine-tuning BERT-style models | AdamW, weight decay ≈ 0.01 |
| What to exclude | biases and normalisation γ/β are usually not decayed |

Because AdamW's shrink per step is ηλ, the effective decay changes with the learning-rate schedule; many codebases tune λ together with the peak learning rate.

### The answer that sounds right

#### "Adam with weight_decay = L2 is fine"

$$ \text{Adam+L2: } w \leftarrow w - \eta\,\frac{\hat{m}({\nabla L + \lambda w})}{{\sqrt{\hat{v}}}+\epsilon} \qquad {\text{AdamW: } w \leftarrow w - \eta\Big(\frac{\hat{m}(\nabla L)}{\sqrt{\hat{v}}+\epsilon} + \lambda w\Big)} $$

Loshchilov & Hutter, "Decoupled Weight Decay Regularization", ICLR 2019 [arXiv:1711.05101](https://arxiv.org/abs/1711.05101): L2 and weight decay are equivalent for SGD but not for adaptive methods; with decoupled decay, Adam generalised substantially better (a 15% relative improvement in test error in their image-classification experiments). Watch out: in PyTorch, `torch.optim.Adam(weight_decay=…)` is the L2 version; `torch.optim.AdamW` is decoupled.

- **L2 enters the gradient**: With Adam + L2, the decay term λw is mixed into the gradient g.

- **divided by √v**: Adam divides by the running RMS of that weight’s gradients. If the loss gradients are large, √v is large and the decay is scaled down to almost nothing; if they are tiny, the decay is scaled up.

- **AdamW**: Apply the decay outside the adaptive step, so every weight shrinks by the same (1 − ηλ) regardless of its gradient history.

## Say it

### Why is Adam with L2 not the same as AdamW?

#### The interviewer pushes further

Follow-up 1 of 3

Why don't we decay biases and LayerNorm weights?

They're few, don't drive overfitting much, and shrinking a norm's gain or a bias towards zero can hurt the function the layer represents.

Follow-up 2 of 3

Is weight decay still useful with BatchNorm?

Yes, but differently: with BatchNorm the output doesn't depend on the scale of the preceding weights, so decay mainly raises the effective learning rate rather than limiting capacity.

Follow-up 3 of 3

L1 vs L2?

L1 pushes weights exactly to zero (sparse); L2 shrinks them smoothly. Deep nets almost always use L2-style decay.

#### The 30-second answer

Weight decay shrinks every weight by a small factor each step; for plain SGD that's mathematically the same as an L2 penalty on the loss. With Adam it isn't: the L2 gradient gets divided by Adam's per-parameter RMS, so weights with large gradients are barely regularised and weights with small gradients are over-regularised. AdamW decouples the decay from the adaptive update, shrinking every weight by the same 1 minus eta lambda, which generalises better. It's the default for transformers, typically with weight decay around 0.1, not applied to biases and norm parameters.

**Go further**

#### What not to say

- "Weight decay and L2 are always the same." Only for plain SGD.

- "Adam's weight_decay argument is AdamW." In PyTorch it's the coupled L2 version.

**Key terms and sources**

What weight decay does, why it equals L2 regularisation for plain SGD but not for Adam, how AdamW fixes it by decoupling the decay, and typical settings for CNNs and LLMs · built from Krogh & Hertz (1992), Loshchilov & Hutter (ICLR 2019), Goodfellow et al. §7.1 and the PyTorch `AdamW` docs · checked 29 Oct 2026

#### Sources

1. A. Krogh & J. Hertz, "A Simple Weight Decay Can Improve Generalization", NeurIPS 1992.

2. I. Loshchilov & F. Hutter, "Decoupled Weight Decay Regularization", ICLR 2019, [arXiv:1711.05101](https://arxiv.org/abs/1711.05101).

3. H. Touvron et al., "LLaMA: Open and Efficient Foundation Language Models", [arXiv:2302.13971](https://arxiv.org/abs/2302.13971), 2023.

4. I. Goodfellow, Y. Bengio & A. Courville, _Deep Learning_, MIT Press 2016, §7.1, [deeplearningbook.org](https://www.deeplearningbook.org/).

5. PyTorch documentation, [torch.optim.AdamW](https://docs.pytorch.org/docs/stable/generated/torch.optim.AdamW.html).
