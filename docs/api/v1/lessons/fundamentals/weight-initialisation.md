# Weight Initialisation

> Why does a 20-layer net die at step 0 with the wrong init?

- Track: Fundamentals › Deep Learning › Training deep nets
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/weight-initialisation/
- Before this: Backpropagation Through a Network (`fundamentals/backpropagation`)
- Quiz topic: `train`

## Intuition

### The situation

You build a 20-layer network, and before any real training its signal has already died. The interviewer asks:

> Why does a deep network fail with the wrong initialisation, and how do Xavier and He fix it?

**Running example:** a deeper version of the late-delivery network: 20 hidden layers of 128 units each, looked at _before_ any training, on a batch of 32 orders.

#### Every layer multiplies the signal

Each layer computes z = Wa. If each weight has variance v and a layer has n inputs, the output variance is roughly n·v times the input variance. After 20 layers that factor is raised to the 20th power: 0.8²⁰ ≈ 0.01 and 1.2²⁰ ≈ 38. The same happens to gradients going backwards. A network that starts with vanished or exploded signals may never train, or train painfully slowly.

### The idea

Think of passing a message down a line of 20 people. If each speaks slightly quieter than the last, it fades to nothing. If each speaks slightly louder, it ends in shouting. Good initialisation sets everyone's volume so the message arrives at the same level.

[Figure: Three signals after 20 layers. A factor of 0.8 per layer shrinks to about 0.01. A factor of 1 stays at 1. A factor of 1.2 grows to about 38.]

_From the lesson: 0.8²⁰ ≈ 0.01 and 1.2²⁰ ≈ 38._

### Play

**Try to break it.** Try N(0, 0.01²) and N(0, 1) with ReLU, then He. Then switch to tanh and compare Xavier with He.

#### A 20-layer network at initialisation

Width 128, batch of 32 random standardised inputs, fixed seed. Teal: standard deviation of each layer's activations. Orange: size of the gradient arriving at each layer (backprop of a random unit-size output gradient). Log scale; the band marks 0.1–10.

With tanh and std 0.01, the activations shrink to about **10⁻¹⁹** by layer 20 and the gradient reaching layer 1 is just as tiny: nothing will learn. Xavier keeps tanh healthy (activations around 0.14 at layer 20, gradients around 0.2). Switch to ReLU: Xavier now loses half the variance per layer (activations around **6 × 10⁻⁴**), while He keeps them near **0.6**. With N(0, 1) and ReLU the activations explode to about 7 × 10¹⁷; with tanh they saturate at ±1 instead, and the gradient reaching layer 1 blows up to about 10⁸.

**Now say why:** why does each activation want a different scale for its weights?

## Maths

### Maths

#### In one breath

Weights must start **random** (to break symmetry) and at the **right scale**. Each layer multiplies its input by a weight matrix; if the weights are a bit too small the signal shrinks layer after layer towards zero, a bit too big and it blows up, and the gradients do the same on the way back. The fix is to pick the weight variance so each layer keeps the signal's variance roughly constant: **Xavier/Glorot** uses Var(w) = 2 / (fan_in + fan_out) (≈ 1/n) for tanh, and **He/Kaiming** uses Var(w) = 2 / fan_in for ReLU, because ReLU zeroes half its inputs. With the right init, a 20-layer network starts with healthy signals in every layer.What you'll be able to do after this: derive why the variance should be about 1/n, choose Xavier vs He for an activation, and diagnose a network whose activations collapse or explode at the start of training.

#### Keep the variance constant from layer to layer

$$ \mathrm{Var}(z_k) = n \cdot \mathrm{Var}(w) \cdot \mathrm{E}[a^2] $$

Glorot & Bengio (2010) required the variance to be preserved both forward (nin·Var(w) = 1) and backward (nout·Var(w) = 1) and took the compromise Var(w) = 2/(nin + nout). He et al. (2015) derived Var(w) = 2/nin for ReLU.

- **one pre-activation**: A sum of n terms, each a weight times an input. With zero-mean independent weights and inputs, the variances add.

- **n · Var(w)**: The factor by which the layer scales the variance. To keep the signal steady we want n · Var(w) ≈ 1, i.e. Var(w) ≈ 1/n.

- **input variance**: What came in from the layer below. For ReLU, only half of it survives (the negative half is zeroed), which is why He et al. use 2/n instead of 1/n.

#### The rules in one table

| Scheme | Variance of w | Use with | PyTorch |
|---|---|---|---|
| **Xavier / Glorot** | 2 / (fan_in + fan_out) | tanh, sigmoid, linear | `xavier_uniform_`, `xavier_normal_` |
| **He / Kaiming** | 2 / fan_in | ReLU, leaky ReLU (gain adjusted) | `kaiming_normal_` |
| **LeCun** | 1 / fan_in | SELU, and the default style for many layers | – |
| **Biases** | 0 | everywhere (symmetry is already broken by W) | `zeros_` |

The uniform version of Xavier draws from U[−a, a] with a = √(6 / (fan_in + fan_out)), which has the same variance. Note PyTorch's `nn.Linear` default is a Kaiming-uniform variant with a = √5, which works out to U[−1/√fan_in, 1/√fan_in] (variance 1/(3·fan_in)).

## In practice

### In practice

#### Init matters less with normalisation, but still matters

- **Normalisation layers** (BatchNorm, LayerNorm) re-scale activations every layer, which makes training much less sensitive to the initial scale.

- **Residual networks** add each block's output to its input; initialising the last layer of each block small (or zero) makes the whole network start close to the identity and keeps very deep stacks stable.

- **Transformers / LLMs** commonly use a small normal init (GPT-2 used std 0.02) and scale the residual-output projections by 1/√(number of layers) so the residual stream doesn't grow with depth (GPT-2 report, Radford et al. 2019).

### The answer that sounds right

#### "Zeros, or small random numbers like N(0, 0.01²)"

- **All zeros (or all equal):** every unit in a layer computes the same output and gets the same gradient, so they stay identical forever. Randomness breaks the symmetry.

- **Small fixed scale (std 0.01):** fine for a 2-layer net, but with 128 inputs each layer multiplies the variance by 128 × 0.0001 = 0.0128. After a few layers the signal is effectively zero.

- **Standard normal (std 1):** each layer multiplies the variance by 128: activations saturate (tanh) or explode (ReLU).

He et al. (2015) report that a 30-layer ReLU network initialised with Xavier's rule **did not converge** at all, while their 2/n rule trained it. The scale has to match both the width and the activation.

## Say it

### Why does a deep network fail with the wrong initialisation, and how do Xavier and He fix it?

#### The interviewer pushes further

Follow-up 1 of 3

Why not initialise all weights to zero?

All units in a layer would compute identical outputs and receive identical gradients, so they'd never become different: the layer behaves like one unit.

Follow-up 2 of 3

How would you notice a bad init?

Log per-layer activation std and gradient norms on the first batch: values collapsing towards 0 or blowing up with depth, a loss that doesn't move, or NaNs in the first steps.

Follow-up 3 of 3

Does pre-training remove the need for init?

For fine-tuning, the pre-trained weights are the init; only new heads need initialising (often small or zero for the final layer).

#### The 30-second answer

Weights must be random to break symmetry, and their scale must keep the signal's variance roughly constant across layers, both forward for activations and backward for gradients. A layer with n inputs scales the variance by n times the weight variance, so we want Var(w) around 1/n. Xavier uses 2 over fan-in plus fan-out, which suits tanh; He uses 2 over fan-in for ReLU, because ReLU zeroes half its inputs. Too small and activations and gradients vanish; too large and they explode. Normalisation and residual connections reduce the sensitivity, but init still matters, especially in deep transformers.

**Go further**

#### What not to say

- "Use Xavier for ReLU." It loses half the variance per layer; He is the right match.

- "Biases need random init too." Zero is standard.

**Key terms and sources**

Why weights must start random, why the scale matters, Xavier/Glorot initialisation for tanh, He/Kaiming initialisation for ReLU, and what modern LLMs do · built from Glorot & Bengio (2010), He et al. (2015), Goodfellow et al. §8.4 and the PyTorch `nn.init` documentation · checked 29 Oct 2026

#### Sources

1. X. Glorot & Y. Bengio, "Understanding the difficulty of training deep feedforward neural networks", AISTATS 2010.

2. K. He, X. Zhang, S. Ren & J. Sun, "Delving Deep into Rectifiers: Surpassing Human-Level Performance on ImageNet Classification", ICCV 2015, arXiv:1502.01852.

3. I. Goodfellow, Y. Bengio & A. Courville, _Deep Learning_, MIT Press 2016, §8.4, deeplearningbook.org.

4. A. Radford et al., "Language Models are Unsupervised Multitask Learners" (GPT-2), OpenAI 2019.

5. PyTorch documentation, torch.nn.init.
