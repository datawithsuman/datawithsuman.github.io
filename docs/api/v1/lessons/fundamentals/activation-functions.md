# Activation Functions

> Why did ReLU replace sigmoid, and what do LLMs use now?

- Track: Fundamentals › Deep Learning › Neural network basics
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/activation-functions/
- Before this: From Perceptron to MLP (`fundamentals/perceptron-to-mlp`)
- Quiz topic: `nn`

## Intuition

### The situation

Your deep network uses sigmoid in every layer, and its early layers barely learn. The interviewer asks:

> Why did ReLU replace sigmoid, and what do LLMs use now?

**Running example:** the late-delivery network from the previous lesson. Each hidden unit receives a pre-activation z = w·x + b computed from distance and hour; what matters here is the spread of those z values across orders, and what the activation does to them.

#### The non-linearity also sits on the gradient's path

We need a non-linearity between layers, or the network collapses to a linear model. But in backprop every layer multiplies the gradient by the activation's slope f′(z) (backpropagation lesson). If those slopes are small, the gradient reaching early layers is tiny and they barely learn; if they're exactly zero, the unit stops learning altogether. So choosing an activation is choosing how gradients flow.

### The idea

Think of a volume knob that stops responding at both ends. Sigmoid behaves like that: push it far either way, and turning it further changes nothing, so no learning signal gets through. ReLU stays responsive across its whole positive side.

[Figure: Left: a sigmoid curve is flat at both ends, where its slope is almost zero. Right: ReLU is flat below zero and keeps a slope of one above it.]

_Illustrative. Backprop multiplies the gradient by this slope at every layer._

### Play

**Try to break it.** Choose sigmoid and push the mean of the pre-activations far from zero. Then switch to ReLU and make the mean strongly negative.

#### Where do your pre-activations land on the curve?

Teal: f(z). Orange: f′(z). Grey area: the distribution of pre-activations z across orders (normal with the mean and spread you set). Computed exactly by numerical integration.

With z centred at 0 and spread 1, sigmoid's average slope is only **0.21**, and **no** unit passes even half the gradient: through ten sigmoid layers the gradient shrinks by roughly 0.207¹⁰ ≈ 1.4 × 10⁻⁷. Tanh does better (average 0.61; 62% of units pass at least half), and ReLU passes exactly half the inputs at full strength. Now push the mean to −3: **99.9%** of ReLU units are dead, leaky ReLU still passes 0.01 of the gradient everywhere, and GELU keeps an average slope of 0.03 with 38% of units stuck. Put the mean back to 0 and widen the spread to 4: **40%** of tanh units are saturated (slope below 0.005).

**Now say why:** how does each activation get stuck, and what does that do to the gradient?

## Maths

### Maths

#### In one breath

The activation is the non-linearity that makes a network more than a linear model, and its **slope** decides how much gradient flows back through each unit. **Sigmoid** and **tanh** saturate: for large inputs their slope is almost 0, and sigmoid's slope is never above 0.25, so gradients shrink layer after layer. **ReLU** (max(0, z)) has slope exactly 1 for positive inputs, which made deep networks trainable, but a unit whose input is always negative gets zero gradient and **dies**. **Leaky ReLU** keeps a small slope there; **GELU** is a smooth ReLU used in BERT and GPT; and **SwiGLU**, a gated unit, is the feed-forward activation in LLaMA-style LLMs.What you'll be able to do after this: compare activations by output range, slope and failure mode, explain vanishing gradients through saturating units and dead ReLUs, and say which activation goes where.

#### Sigmoid and tanh

$$ \sigma(z) = \frac{1}{1+e^{-z}}, \qquad \tanh(z) = 2\sigma(2z) - 1 $$

Goodfellow et al. §6.3.2: sigmoidal units saturate across most of their domain, which makes gradient-based learning hard; their use as hidden units is now discouraged.

- **sigmoid**: Squashes to (0, 1). Fine for an output probability; poor in hidden layers: not zero-centred, and its slope σ(z)(1 − σ(z)) peaks at only 0.25.

- **tanh**: A rescaled sigmoid with range (−1, 1): zero-centred, slope up to 1 at z = 0. Still saturates: at z = 3 its slope is about 0.01.

#### ReLU and its descendants

$$ \mathrm{ReLU}(z)=\max(0,z), \quad \mathrm{Leaky}(z)=\max(\alpha z, z), \quad \mathrm{GELU}(z)= z\,\Phi(z) $$

- **ReLU**: Slope exactly 1 for z > 0, so gradients pass through unchanged; cheap to compute; outputs exact zeros (sparse). Made deep supervised nets trainable without pre-training (Glorot, Bordes & Bengio 2011; Nair & Hinton 2010).

- **leaky ReLU**: A small slope α (often 0.01) for z < 0, so a unit pushed negative still gets some gradient and can recover (Maas et al. 2013).

- **GELU**: Weights the input by the probability that a standard normal is below it: a smooth ReLU that is slightly negative near zero. Used in BERT and GPT-2/3 (Hendrycks & Gimpel 2016).

**Dying ReLU:** if a large update or a big negative bias pushes a unit's input below zero for every training example, its output and gradient are zero everywhere, and it never recovers. A too-high learning rate can kill a large share of units. Fixes: leaky ReLU / GELU, careful initialisation, lower learning rate.

#### Gated linear units: SwiGLU

$$ \mathrm{FFN}_{\mathrm{SwiGLU}}(x) = \big(\mathrm{Swish}(xW) \otimes xV\big)W_2 $$

Shazeer, "GLU Variants Improve Transformer", 2020 arXiv:2002.05202: in T5 experiments GEGLU and SwiGLU gave the best perplexities among feed-forward variants. SwiGLU is used in PaLM and LLaMA. It has three weight matrices instead of two, so the hidden width is usually cut to about ⅔ to keep the parameter count equal. Covered again in the Transformers lessons.

- **Swish gate**: Swish(z) = z·σ(z) (also called SiLU), computed from one projection xW. It decides how much of each feature passes.

- **value path**: A second, purely linear projection xV. The gate multiplies it element-wise.

- **down projection**: Projects back to the model width, like the second layer of a normal MLP block.

## In practice

### In practice

#### Cheat sheet

| Activation | Range | Max slope | Failure mode | Typical use |
|---|---|---|---|---|
| **Sigmoid** | (0, 1) | 0.25 | saturates, not zero-centred | binary output, gates (LSTM) |
| **Tanh** | (−1, 1) | 1 | saturates | RNN/LSTM state |
| **Softmax** | probabilities | – | overflow (subtract max) | multi-class output, attention |
| **ReLU** | [0, ∞) | 1 | dying units | CNNs, MLP default |
| **Leaky ReLU** | (−∞, ∞) | 1 | extra hyperparameter α | GANs, when ReLUs die |
| **GELU** | ≈ [−0.17, ∞) | ≈ 1.13 | slightly costlier | BERT, GPT, ViT |
| **SwiGLU** | (−∞, ∞) | – | 3 matrices | LLaMA-style LLM FFN |

### The answer that sounds right

#### "Sigmoid everywhere, like the output"

Through 10 sigmoid layers the gradient is multiplied by at most 0.25 ten times: 0.25¹⁰ ≈ 9.5 × 10⁻⁷, before even counting the weights. The early layers effectively stop learning. That's the vanishing gradient problem, and it's a big reason deep networks were so hard to train before ReLU (vanishing & exploding gradients).

## Say it

### Why did ReLU replace sigmoid, and what do LLMs use now?

#### The interviewer pushes further

Follow-up 1 of 3

Why is zero-centred output helpful?

If all inputs to a layer are positive (sigmoid outputs), the gradients for that layer's weights all share a sign per unit, so updates zig-zag. Tanh or zero-mean activations avoid this; normalisation layers also help.

Follow-up 2 of 3

ReLU isn't differentiable at 0. Is that a problem?

Not in practice: frameworks use a subgradient (0 or 1) at exactly 0, and inputs are almost never exactly 0.

Follow-up 3 of 3

How would you detect dead ReLUs?

Log the fraction of units whose output is zero for every example in a batch (or over an epoch), per layer. A rising fraction suggests the learning rate is too high or the initialisation/bias is off.

#### The 30-second answer

Activations add the non-linearity, and their derivative scales every gradient that flows back. Sigmoid and tanh saturate, and sigmoid's slope is at most 0.25, so in deep stacks gradients vanish. ReLU has slope 1 for positive inputs, is cheap, and made deep nets trainable, but units can die if their inputs stay negative; leaky ReLU and GELU keep some gradient there. Today CNNs mostly use ReLU, transformers use GELU, and modern LLMs use gated units like SwiGLU in their feed-forward blocks. Sigmoid and softmax stay at the output for probabilities.

**Go further**

#### What not to say

- "ReLU solves vanishing gradients completely." It helps a lot, but deep nets still need good initialisation, normalisation and residual connections.

- "Use softmax in hidden layers." It's for outputs and attention weights.

**Key terms and sources**

Sigmoid, tanh, ReLU and its variants, GELU and gated units like SwiGLU: what each does to the signal and to the gradient, and why modern networks use the ones they do · built from Glorot, Bordes & Bengio (2011), Nair & Hinton (2010), Maas et al. (2013), Hendrycks & Gimpel (2016), Shazeer (2020) and Goodfellow et al. §6.3 · checked 29 Oct 2026

#### Sources

1. V. Nair & G. Hinton, "Rectified linear units improve restricted Boltzmann machines", ICML 2010.

2. X. Glorot, A. Bordes & Y. Bengio, "Deep sparse rectifier neural networks", AISTATS 2011.

3. A. Maas, A. Hannun & A. Ng, "Rectifier nonlinearities improve neural network acoustic models", ICML Workshop 2013.

4. D. Hendrycks & K. Gimpel, "Gaussian Error Linear Units (GELUs)", arXiv:1606.08415, 2016.

5. N. Shazeer, "GLU Variants Improve Transformer", arXiv:2002.05202, 2020.

6. I. Goodfellow, Y. Bengio & A. Courville, _Deep Learning_, MIT Press 2016, §6.3, deeplearningbook.org.
