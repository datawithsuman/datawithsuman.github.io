# Backpropagation Through a Network

> How does one backward pass get every gradient, and what does it cost?

- Track: Fundamentals › Deep Learning › Neural network basics
- Type: Concept · 25 min
- Page: https://aimlrounds.com/tracks/fundamentals/backpropagation/
- Before this: Derivatives, Gradients & the Chain Rule (`fundamentals/derivatives-and-chain-rule`), From Perceptron to MLP (`fundamentals/perceptron-to-mlp`)
- Quiz topic: `nn`

## Intuition

### The situation

Your model has millions of weights. Nudging each one and re-running the network to measure its effect would take one forward pass per weight. The interviewer asks:

> How does one backward pass get every gradient, and what does it cost?

**Running example:** a small late-delivery network: 2 inputs (distance and hour, standardised) → 3 tanh hidden units → 1 sigmoid output p(late), trained with cross-entropy. The single-neuron version is in Derivatives & the Chain Rule; here we do the whole network.

#### We need the gradient for every weight, cheaply

Gradient descent needs ∂L/∂w for every weight. A modern network has millions to billions of weights. The obvious way, nudging each weight and re-running the network (finite differences), costs one forward pass per weight: hopeless at that scale. Backprop gets all of them in one backward sweep.

### The idea

Think of a company tracing a loss back through its departments. Going forward, each one keeps notes on what it did. Going backward, each one passes the blame to whoever fed it, using those notes. One pass gives everyone their share, with no need to rerun the company once per person.

[Figure: Boxes for input, hidden layer, output and loss. A forward arrow along the top stores values. A backward arrow along the bottom reuses them to give every gradient.]

_Illustrative. The stored values are why training needs so much more memory than prediction._

### Play

**Try to break it.** Move the inputs and flip the label, then compare backprop with finite differences across all 13 weights.

#### Backprop vs finite differences, all 13 weights

Fixed example weights. "Numeric" = (L(w + ε) − L(w − ε)) / 2ε with ε = 10⁻⁵, one pair of forward passes per weight.

Every one of the 13 backprop gradients agrees with the numerical estimate to about **10⁻¹¹**. The network gives this on-time order a 0.82 chance of being late (loss 1.73); one gradient step with η = 0.5 lowers the loss to **0.71**. This is the standard way to unit-test a hand-written backward pass: compare against centred finite differences on a tiny network, then switch the check off (it costs two forward passes per weight).

**Now say why:** why do the two methods agree, and why would you never train with finite differences?

## Maths

### Maths

#### In one breath

Backpropagation is the chain rule applied layer by layer from the loss back to the input, reusing work. The forward pass computes and **stores** each layer's activations. The backward pass starts with the loss's gradient at the output and computes, for each layer, an **error signal δ** = (what the next layer sent back) ⊙ (the activation's slope). The weight gradient is then **δ times the layer's input**, and the signal sent further back is **Wᵀδ**. One backward pass gives the gradient for every weight at about **twice** the cost of the forward pass, compared with one extra forward pass _per weight_ for finite differences. The price is memory: every activation has to be kept until the backward pass uses it. What you'll be able to do after this: write the backward pass of an MLP in matrix form, check gradients numerically, and estimate the compute and memory cost of training.

#### The four backprop equations

$$ {\delta^{(L)} = \hat{p} - y}, \quad {\delta^{(l)} = \big(W^{(l+1)\top}\delta^{(l+1)}\big) \odot \phi'(z^{(l)})}, \quad {\frac{\partial L}{\partial W^{(l)}} = \delta^{(l)}\, a^{(l-1)\top}}, \quad {\frac{\partial L}{\partial b^{(l)}} = \delta^{(l)}} $$

Goodfellow et al. §6.5.4–6.5.6; Rumelhart, Hinton & Williams, _Nature_ 1986. a(l) = φ(z(l)) is layer l's output and a(0) = x.

- **start at the output**: For sigmoid + cross-entropy (or softmax + cross-entropy), the gradient at the output logit is simply p − y.

- **error signal of layer l**: Take the signal from the layer above, send it back through the weights (transpose!), and multiply element-wise by this layer’s activation slope φ′(z).

- **weight gradient**: Each weight’s gradient = the error at its output × the activation at its input. Summed (averaged) over the batch: δ times the input, transposed.

- **bias gradient**: Just the error signal itself (a bias’s input is always 1).

#### Forward stores, backward reuses

1. The network: 2 inputs, 3 tanh hidden units, 1 sigmoid output, then the loss. 2·3 + 3 + 3 + 1 = 13 parameters.

2. Forward pass: compute each layer from the one before, and keep the hidden activations h in memory: the backward pass will need them.

3. Backward pass starts at the output: δ₂ = p − y. The output weights' gradient is δ₂ times the stored h.

4. Send the error back through w₂ and multiply by tanh's slope 1 − h² (again from the stored h): that's δ₁, one number per hidden unit.

5. First-layer gradients are δ₁ times the inputs. Every gradient came from reusing δ₂ and δ₁: nothing was computed twice.

## In practice

### In practice

#### What one training step costs

Square dense layers, ~2 FLOPs per weight per example forward; backward ≈ 2× forward (one matmul for δ, one for the weight gradient). Activations: one fp32 value per unit per layer per example (real frameworks store a few more).

A 12-layer, 1024-wide MLP has about **12.6 million** parameters. A batch of 64 costs about 1.6 GFLOPs forward and **3.2 GFLOPs backward**, so a training step is about 3× a forward pass: the origin of the rule of thumb that training costs **about 6 FLOPs per parameter per token** (Kaplan et al. 2020). Finite differences would need 12.6 million forward passes instead: about **4 million times** more work. Memory is the catch: activations scale with batch × depth × width, which is why large models use activation checkpointing (store only some layers, recompute the rest during backward; Chen et al. 2016).

### The answer that sounds right

#### "Differentiate each weight separately"

Writing out ∂L/∂w for each weight on its own repeats the same products again and again: every first-layer weight shares the whole chain from the hidden layer to the loss. Backprop is reverse-mode automatic differentiation: compute each shared piece (each δ) once, going backwards, and reuse it for every weight that feeds into it (Baydin et al. 2018). The same idea is why PyTorch's `loss.backward()` works on any graph you build.

## Say it

### How does one backward pass get every gradient, and what does it cost?

#### The interviewer pushes further

Follow-up 1 of 3

Why do we need the transpose of W going backwards?

Forward, unit k in layer l+1 sums inputs j weighted by W[k][j]. Backward, input j receives gradient from every k it fed into, weighted by the same W[k][j]: that's row-to-column, i.e. Wᵀ.

Follow-up 2 of 3

How would you debug a custom layer's gradient?

Gradient check in float64 on a tiny input: compare to centred differences with ε ≈ 10⁻⁵ to 10⁻⁶; relative errors around 10⁻⁷ or smaller are fine. In PyTorch, `torch.autograd.gradcheck` does this.

Follow-up 3 of 3

Why does inference need much less memory than training?

Inference can throw each activation away once the next layer is computed; training must keep them for the backward pass, plus gradients and optimiser state (Adam keeps two extra values per parameter).

#### The 30-second answer

Backprop is reverse-mode automatic differentiation: the chain rule applied from the loss backwards, reusing intermediate results. The forward pass computes and stores activations. Going back, each layer gets an error signal δ: the next layer's signal sent back through the transposed weights, times the activation's slope. The weight gradient is δ times the layer's input, and the bias gradient is δ. One backward pass costs about twice a forward pass and gives every gradient, versus one forward pass per parameter with finite differences. The cost is memory, since activations must be stored, which is why big models use activation checkpointing.

**Go further**

#### What not to say

- "Backprop is a learning algorithm." It computes gradients; the optimiser (SGD, Adam) does the learning.

- "The backward pass is free." It's about 2× the forward pass and needs stored activations.

**Key terms and sources**

Backprop in matrix form through a whole MLP, the error signal δ for each layer, checking gradients numerically, why the backward pass costs about twice the forward pass, and why training stores activations · built from Rumelhart, Hinton & Williams (1986), Goodfellow et al. §6.5, Baydin et al. (2018), Kaplan et al. (2020) and Chen et al. (2016) · checked 29 Oct 2026

#### Key terms

| Term | Meaning |
|---|---|
| **Error signal δ** | ∂L/∂z for a layer: how the loss changes with that layer's pre-activations. |
| **Reverse-mode autodiff** | Compute gradients from the output backwards; one sweep gives all parameter gradients. |
| **Gradient check** | Compare backprop gradients to finite differences to catch bugs. |
| **Activation checkpointing** | Trade compute for memory by recomputing activations in the backward pass. |
| **Computation graph** | The graph of operations that autograd records and walks backwards. |

For what uses these gradients, see Gradient Descent, Momentum and Adam.

#### Sources

1. D. Rumelhart, G. Hinton & R. Williams, "Learning representations by back-propagating errors", _Nature_ 323, 1986.

2. I. Goodfellow, Y. Bengio & A. Courville, _Deep Learning_, MIT Press 2016, §6.5, [deeplearningbook.org](https://www.deeplearningbook.org/).

3. A. Baydin, B. Pearlmutter, A. Radul & J. Siskind, "Automatic differentiation in machine learning: a survey", _JMLR_ 18, 2018, [arXiv:1502.05767](https://arxiv.org/abs/1502.05767).

4. J. Kaplan et al., "Scaling Laws for Neural Language Models", [arXiv:2001.08361](https://arxiv.org/abs/2001.08361), 2020 (training compute C ≈ 6N per token).

5. T. Chen, B. Xu, C. Zhang & C. Guestrin, "Training Deep Nets with Sublinear Memory Cost", [arXiv:1604.06174](https://arxiv.org/abs/1604.06174), 2016.
