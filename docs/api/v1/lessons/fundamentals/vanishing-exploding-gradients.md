# Vanishing & Exploding Gradients

> Why do early layers stop learning, and how do residuals fix it?

- Track: Fundamentals › Deep Learning › Training deep nets
- Type: Concept · 25 min
- Page: https://aimlrounds.com/tracks/fundamentals/vanishing-exploding-gradients/
- Before this: Backpropagation Through a Network (`fundamentals/backpropagation`), Activation Functions (`fundamentals/activation-functions`)
- Quiz topic: `train`

## Intuition

### The situation

In your 30-layer network, the early layers' weights barely change. Occasionally, on a weird batch, the loss spikes and turns into NaN. The interviewer asks:

> Why do early layers stop learning, and how do residual connections fix it?

**Running example:** a deep late-delivery network (30 layers of 128 units), and later a training run whose gradient norm occasionally spikes on a weird batch, such as a festival day with 3-hour deliveries.

#### The gradient is a long product

For a network of L layers, the gradient at layer 1 is the output gradient multiplied by L Jacobians, one per layer (backpropagation). Roughly, each contributes a factor of (weight scale) × (activation slope). If that factor is 0.8, thirty layers give 0.8³⁰ ≈ 0.001; if it's 1.2, they give 1.2³⁰ ≈ 237. Recurrent networks are worse: the same weight matrix is applied at every time step, so a 100-step sequence is a 100-layer product (Bengio, Simard & Frasconi 1994; Hochreiter 1991).

### The idea

Think of passing a bucket down a long line, with each person spilling a fifth of it. After 30 people, almost nothing is left. A residual connection is a pipe running alongside the line, so the water can reach the far end directly.

[Figure: Six layers in a row, with the gradient shrinking through them. A skip connection arcs over each pair of layers and carries the gradient straight through.]

_Illustrative. The identity path passes the gradient straight through._

### Play

**Try to break it.** Set a deep plain network with sigmoid and read the gradient at layer 1. Then switch to residual, and then raise the weight scale.

#### Gradient size per layer, plain vs residual

Width 128, batch 32, at initialisation. "Matched init" = Xavier (1/n) for sigmoid/tanh, He (2/n) for ReLU. Orange: size of the gradient arriving at each layer (log₁₀); the band marks 0.1–10.

The plain 30-layer sigmoid network delivers a gradient of about **10⁻¹⁹** to layer 1, while the last layer gets about 0.2: the early layers can't learn. Switch to **residual** and layer 1 gets about **1.2**: the identity path carries the gradient straight through. Plain ReLU with He init is also healthy here (about 1.1). But try residual + ReLU at full scale: the residual stream keeps adding, and the layer-1 gradient grows to about **10⁶**. That's why residual blocks are always paired with normalisation or a down-scaled branch init.

**Now say why:** why does the gradient shrink so fast with depth, and what does the residual path change?

## Maths

### Maths

#### In one breath

Backprop multiplies the gradient by one factor per layer (the weights times the activation's slope). Multiply many factors below 1 and the gradient reaching the early layers **vanishes**, so they stop learning; many factors above 1 and it **explodes**, so updates become huge and the loss jumps or turns into NaN. Fixes for vanishing: non-saturating activations (ReLU), variance-preserving initialisation, normalisation, and above all **residual connections**, which give the gradient an identity path around every block (and gated RNNs like LSTM for sequences). The standard fix for exploding is **gradient clipping**: if the gradient's norm exceeds a threshold, scale it down to that threshold.What you'll be able to do after this: explain both problems as a product of per-layer factors, spot them in training logs, and pick the right fix.

#### One factor per layer

$$ \frac{\partial L}{\partial a^{(1)}} = \prod_{l=2}^{L} W^{(l)\top}\,\mathrm{diag}\big(\phi'(z^{(l)})\big) \; \frac{\partial L}{\partial a^{(L)}} $$

For RNNs, Pascanu et al. (2013) show that if the largest eigenvalue of the recurrent weight matrix is below 1, long-term gradient components vanish, and it must be above 1 for them to explode.

- **gradient at layer 1**: What the first layer’s weights actually get to learn from.

- **one Jacobian per layer**: The weight matrix transposed, times the diagonal of activation slopes. Its size (largest singular value) decides whether this layer shrinks or grows the gradient.

- **output gradient**: The error signal at the top, e.g. p − y.

#### Residual connections: give the gradient a highway

$$ y = x + F(x) \quad\Rightarrow\quad \frac{\partial y}{\partial x} = I + \frac{\partial F}{\partial x} $$

He, Zhang, Ren & Sun, "Deep Residual Learning for Image Recognition", CVPR 2016 arXiv:1512.03385: plain networks got _worse_ training error going from 18 to 34 layers, while residual networks improved and trained to 152 layers (and over 1000 on CIFAR-10). Every transformer uses the same residual stream.

- **identity path**: The block’s input is added straight to its output, so its derivative contributes exactly I (the identity).

- **learned branch**: The layers only have to learn a correction F(x) to the input, which is easy to start near zero.

- **gradient through the block**: I plus the branch’s Jacobian: even if the branch’s gradient is tiny, the identity keeps the signal alive.

#### Gradient norm clipping

$$ \text{if } \lVert g\rVert > c: \quad g \leftarrow c\,\frac{g}{\lVert g\rVert} $$

Pascanu, Mikolov & Bengio, ICML 2013 arXiv:1211.5063. In PyTorch: `clip_grad_norm_(params, max_norm=1.0)` from `torch.nn.utils`; LLM pre-training commonly clips at 1.0 (e.g. LLaMA, Touvron et al. 2023).

- **the condition**: Compute the norm of the whole gradient (all parameters together) and compare it with a threshold c.

- **rescale**: If it’s too big, shrink the whole vector to length c. The direction is unchanged; only the step size is capped.

200 training steps (illustrative): gradient norms vary around 1, with two spikes from unusual batches. Step size = learning rate (0.1) × gradient norm, capped at 0.1 × c when clipping.

Without clipping, the worst spike makes a step about **117× larger** than a typical one, which can throw the weights far away from everything learned so far. With c = 5, only the **2 spikes** get clipped, so normal training is untouched and the largest step is capped at 0.5. Set c = 1 and more than half the steps (109 of 200) get clipped, which silently lowers the effective learning rate.

## In practice

### In practice

#### Diagnose & fix

| Symptom | Likely cause | Fix |
|---|---|---|
| Early layers' weights barely change; loss plateaus early | vanishing gradients | ReLU/GELU, He init, normalisation, residual connections |
| Loss spikes, then NaN | exploding gradients | gradient clipping, lower LR, warmup, check for bad data |
| RNN forgets anything more than a few steps back | vanishing through time | LSTM/GRU, attention, truncated BPTT |
| Per-layer gradient norms differ by orders of magnitude | either, at a specific depth | log grad norms per layer to find where |

### The answer that sounds right

#### "Just raise the learning rate" / "just lower it"

Vanishing gradients are not a small-learning-rate problem: the early layers get gradients 10¹⁰ times smaller than the late ones, so any single learning rate is either far too small for the early layers or far too large for the late ones. Exploding gradients aren't fixed by a smaller learning rate either: a rare 100× spike still produces a 100× step. Both need structural fixes.

## Say it

### Why do early layers stop learning, and how do residual connections fix it?

#### The interviewer pushes further

Follow-up 1 of 3

Clip by norm or by value?

By global norm is standard: it keeps the gradient's direction and only caps its length. Clipping each value separately changes the direction.

Follow-up 2 of 3

Why do LSTMs help with vanishing gradients?

The cell state is updated additively, ct = ft ⊙ ct−1 + …; when the forget gate is near 1 the gradient flows back through time almost unchanged, much like a residual connection.

Follow-up 3 of 3

Does clipping fix vanishing gradients?

No. Clipping only caps large gradients; it can't make small ones bigger.

#### The 30-second answer

Backprop multiplies the gradient by one Jacobian per layer, roughly weight scale times activation slope. If those factors are below 1 the gradient vanishes exponentially with depth and early layers stop learning; above 1 it explodes and training diverges. Saturating activations like sigmoid make vanishing much worse. Fixes for vanishing are ReLU-family activations, variance-preserving init, normalisation layers and especially residual connections, whose identity path passes the gradient straight through; LSTMs and GRUs do the same for RNNs. For exploding gradients, the standard fix is clipping the global gradient norm, plus warmup and a sensible learning rate.

**Go further**

#### What not to say

- "Batch norm was invented to fix vanishing gradients." It was proposed for "internal covariate shift"; it helps gradient flow, but residuals are the main structural fix.

- "Exploding gradients only happen in RNNs." Deep feed-forward nets and transformers hit them too, which is why LLM training clips.

**Key terms and sources**

Why gradients shrink or blow up as they travel back through many layers or time steps, how to spot it, and the fixes: ReLU, careful init, normalisation, residual connections, gated RNNs and gradient clipping · built from Hochreiter (1991), Bengio, Simard & Frasconi (1994), Pascanu, Mikolov & Bengio (2013), He et al. (2016) and Goodfellow et al. §8.2.5, §10.7 · checked 29 Oct 2026

#### Sources

1. S. Hochreiter, "Untersuchungen zu dynamischen neuronalen Netzen", diploma thesis, TU Munich 1991.

2. Y. Bengio, P. Simard & P. Frasconi, "Learning long-term dependencies with gradient descent is difficult", _IEEE Trans. Neural Networks_ 5(2), 1994.

3. R. Pascanu, T. Mikolov & Y. Bengio, "On the difficulty of training recurrent neural networks", ICML 2013, arXiv:1211.5063.

4. K. He, X. Zhang, S. Ren & J. Sun, "Deep Residual Learning for Image Recognition", CVPR 2016, arXiv:1512.03385.

5. H. Touvron et al., "LLaMA: Open and Efficient Foundation Language Models", arXiv:2302.13971, 2023.

6. I. Goodfellow, Y. Bengio & A. Courville, _Deep Learning_, MIT Press 2016, §8.2.5 and §10.7, deeplearningbook.org.
