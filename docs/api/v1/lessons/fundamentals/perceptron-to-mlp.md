# From Perceptron to MLP

> Why can't one neuron learn XOR, and what does a hidden layer add?

- Track: Fundamentals › Deep Learning › Neural network basics
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/perceptron-to-mlp/
- Before this: Logistic Regression (`fundamentals/logistic-regression`)
- Quiz topic: `nn`

## Intuition

### The situation

Your delivery model scores orders with one weighted sum, but orders run late in two separate rush-hour bands. No single straight line can capture that. The interviewer asks:

> Why can't a single neuron learn XOR, and what does a hidden layer add?

**Running example (all Deep Learning lessons):** the food-delivery app predicts whether an order will arrive **late** from two numbers: the **distance** (0–10 km) and the **hour** it was placed (10:00–23:00). Orders run late when they're far away, and also during the lunch rush (around 13:00) and dinner rush (around 20:30), even when they're close.

#### Some patterns can't be separated by one straight line

Logistic regression scores an order as w₁·distance + w₂·hour + b and says "late" when the score is positive. That's a single straight boundary across the (distance, hour) plane. But "late" here is two separate bands of hours plus a far-away region: no single line can carve that out. We need a model that can learn curved, multi-part boundaries without us hand-crafting features like "is it rush hour?".

### The idea

Think of drawing fences on a map. One neuron can only draw one straight fence. Each hidden unit draws its own fence, and the output combines them, so together they can fence off odd shapes.

[Figure: Left: one straight line can't separate a band of late orders. Right: several lines from hidden units together fence the band off.]

_Illustrative, based on the lesson's rush-hour bands._

### Play

**Try to break it.** Start with 0 hidden units, then try 2, 4 and 16. Watch the boundary and compare train and test accuracy.

#### Add hidden units, watch the boundary bend

Each run trains a tanh MLP in your browser (600 full-batch Adam steps on log loss, fixed seed). Shaded regions: predicted late (orange) or on time (teal); dots: test orders.

Logistic regression is stuck near **72%** test accuracy: its one straight line can't follow the rush-hour bands. Two hidden units barely help (75%), four get most of the shape (86%), and sixteen reach **89%**. Notice the 16-unit model is at 98% on the training orders: more capacity also means more room to overfit, which the Regularisation lessons later in this track deal with.

**Now say why:** what does each extra hidden unit add, and when does adding more stop helping?

## Maths

### Maths

#### In one breath

A **neuron** takes a weighted sum of its inputs plus a bias and passes it through an **activation function**. One neuron (a **perceptron** or logistic regression) can only draw a straight line between classes, so it fails on patterns like XOR. Stack neurons into a **hidden layer** and the network can bend its boundary: each hidden unit draws one line, and the output combines them. Without a non-linear activation, any stack of layers collapses back into one linear layer. With one, a wide enough single hidden layer can approximate any continuous function (**universal approximation**), and in practice **deeper** networks get there with far fewer units.What you'll be able to do after this: write the forward pass of an MLP, explain why it needs a non-linearity, count its parameters, and explain why width and depth help.

#### One neuron

$$ a = f\big(w_1 x_1 + w_2 x_2 + b\big) $$

Rosenblatt's perceptron (1958) used a step function and a simple error-driven update rule; logistic regression is the same neuron with a sigmoid and log loss (Logistic Regression).

- **weights**: How much each input matters, learned from data. For our example, one weight for distance and one for hour.

- **bias**: Shifts the threshold: how big the weighted sum must be before the neuron fires.

- **activation**: A non-linear squashing function: step (perceptron), sigmoid, tanh, ReLU. Without it, the neuron is just a linear function.

#### The multi-layer perceptron (MLP)

$$ \mathbf{h} = \phi(W_1 \mathbf{x} + \mathbf{b}_1), \qquad \hat{p} = \sigma(\mathbf{w}_2^{\top} \mathbf{h} + b_2) $$

Parameters: 2 × 16 + 16 for the hidden layer plus 16 + 1 for the output = 65. "Fully connected" or "dense" layer = this matrix-product-plus-bias layer. Goodfellow et al. ch. 6.

- **hidden layer**: A layer of neurons computed together as a matrix product: each row of W₁ is one hidden unit’s weights. With 16 hidden units and 2 inputs, W₁ is 16 × 2.

- **element-wise non-linearity**: Applied to every hidden unit separately (tanh in our lab, ReLU or GELU in most modern networks).

- **output layer**: Combines the hidden units into one score; a sigmoid turns it into the probability that the order is late.

#### Each hidden unit draws a line; the output combines them

1. The (distance, hour) plane. The late orders sit in two horizontal bands (the rush hours) and a vertical strip on the right (far away).

2. A single neuron can only split the plane with one straight line. Whatever line it picks, it misclassifies a big chunk.

3. Give the network a hidden layer. Each hidden unit learns its own line and outputs "which side am I on" (smoothly, through tanh or ReLU).

4. The output neuron learns to combine those yes/no signals: late inside a band or past the far line. With smooth activations the corners round off, and more units give a finer boundary.

## In practice

### In practice

#### Universal approximation, and why we still go deep

- **Universal approximation:** an MLP with one hidden layer and a non-linear activation can approximate any continuous function on a bounded region as closely as you like, given enough hidden units (Cybenko 1989 for sigmoids; Hornik 1991 for general activations). It says such a network _exists_, not that training will find it, or how many units it needs.

- **Depth is more efficient:** some functions need exponentially many units in a shallow network but only polynomially many in a deep one (Goodfellow et al. §6.4.1). Each layer can reuse the features of the layer below: edges → shapes → objects in vision.

- **Depth is harder to train:** gradients have to pass through every layer, so they can vanish or explode. That's why the next lessons cover initialisation, vanishing gradients and normalisation.

**Counting parameters** (a common interview warm-up): a dense layer from n inputs to m outputs has n·m weights + m biases. An MLP 784 → 256 → 10 (MNIST) has 784·256 + 256 + 256·10 + 10 = **203,530** parameters.

### The answer that sounds right

#### "Just stack linear layers"

Two linear layers in a row, W₂(W₁x + b₁) + b₂, equal one linear layer (W₂W₁)x + (W₂b₁ + b₂). A 100-layer network with no activation is still a straight-line model. The fix is the activation function between layers: it's what lets each layer bend the space before the next one looks at it.

Minsky and Papert's 1969 book _Perceptrons_ showed that a single-layer perceptron can't compute XOR. Multi-layer networks could, but nobody had a good way to train their hidden weights until backpropagation was popularised by Rumelhart, Hinton & Williams in 1986 (the chain rule lesson).

## Say it

### Why can't a single neuron learn XOR, and what does a hidden layer add?

#### The interviewer pushes further

Follow-up 1 of 3

Why can't a single perceptron learn XOR?

XOR's positive points (0,1) and (1,0) sit on opposite corners; no single straight line separates them from (0,0) and (1,1). Two hidden units (one for OR, one for AND) plus an output (OR and not AND) solve it.

Follow-up 2 of 3

If one hidden layer is universal, why use deep networks?

Universality may need an impractically large layer; depth lets layers reuse lower-level features, giving exponentially more efficient representations for many functions, and deep nets generalise better in practice.

Follow-up 3 of 3

What happens if all weights are initialised to zero?

Every hidden unit computes the same thing and gets the same gradient, so they stay identical forever (symmetry is never broken). Weights must start random (initialisation lesson).

#### The 30-second answer

A neuron computes a weighted sum plus bias and applies a non-linear activation. One neuron is a linear classifier, so it can't solve XOR-like patterns. An MLP stacks layers of neurons: each hidden unit carves the input space with one boundary and later layers combine them, so the network can learn curved, multi-part boundaries. The non-linearity is essential, because stacked linear layers collapse into one linear map. By the universal approximation theorem, one wide hidden layer can approximate any continuous function, but deeper networks usually represent the same function with far fewer parameters, at the cost of being harder to train.

**Go further**

#### What not to say

- "More layers always means better." Deeper nets are harder to optimise and can overfit.

- "Universal approximation means a network will learn any function." It's an existence result, not a guarantee about training or data.

**Key terms and sources**

The artificial neuron, the perceptron and its XOR limit, hidden layers, why a non-linearity is essential, the universal approximation theorem and why depth helps · built from Rosenblatt (1958), Minsky & Papert (1969), Rumelhart, Hinton & Williams (1986), Cybenko (1989), Hornik (1991) and Goodfellow et al., _Deep Learning_, ch. 6 · checked 29 Oct 2026

#### Key terms

| Term | Meaning |
|---|---|
| **Perceptron** | One neuron with a step activation; a linear classifier. |
| **Hidden layer** | Neurons between input and output; learn intermediate features. |
| **Dense / fully connected** | Every input connects to every unit: Wx + b. |
| **Activation function** | The non-linearity applied to each unit (next lesson). |
| **Universal approximation** | One wide hidden layer can approximate any continuous function. |

#### Sources

1. F. Rosenblatt, "The perceptron: a probabilistic model for information storage and organization in the brain", _Psychological Review_ 65(6), 1958.

2. M. Minsky & S. Papert, _Perceptrons_, MIT Press 1969.

3. D. Rumelhart, G. Hinton & R. Williams, "Learning representations by back-propagating errors", _Nature_ 323, 1986.

4. G. Cybenko, "Approximation by superpositions of a sigmoidal function", _Mathematics of Control, Signals and Systems_ 2, 1989.

5. K. Hornik, "Approximation capabilities of multilayer feedforward networks", _Neural Networks_ 4(2), 1991.

6. I. Goodfellow, Y. Bengio & A. Courville, _Deep Learning_, MIT Press 2016, ch. 6, deeplearningbook.org.
