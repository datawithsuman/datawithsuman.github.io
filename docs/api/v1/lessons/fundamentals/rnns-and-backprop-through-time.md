# RNNs and Backprop Through Time

> Why can't a plain RNN remember a word from 50 steps ago?

- Track: Fundamentals › Deep Learning › Sequence models
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/rnns-and-backprop-through-time/
- Before this: Backpropagation Through a Network (`fundamentals/backpropagation`)
- Quiz topic: `seq`
- Sources checked: 2026-10-29 · Text last changed: 2026-11-20 · Version: 20ed87505d

## Intuition

### The situation

Your model reads reviews one word at a time. By the end of a long review, it has lost track of what "cold" referred to. The interviewer asks:

> Why can't a plain RNN remember a word from 50 steps ago?

**Running example (Sequence and Transformer lessons):** the app reads restaurant reviews. Take "_the biryani was cold but the naan was great_". To judge it, a model must remember "cold" belongs to the biryani, and that "but" flips the tone, even if many words sit between them.

#### Inputs that come in order, with any length

An MLP takes a fixed-size input. Reviews, sentences, delivery-tracking events and audio are sequences of different lengths where order matters ("not good" ≠ "good, not"). We need a model that reads one step at a time, carries a memory forward, and reuses the same weights at every position, just as a CNN reuses a filter at every pixel.

### The idea

Think of reading a review with a single sticky note. After each word, you rewrite the note from what's on it and the new word. Early details get fainter with every rewrite, until they're gone.

[Figure: Words pass through a chain of hidden states. The memory of the first word fades at each step.]

_Illustrative. The same weights are reused at every step._

### Play

**Try to break it.** Move the recurrent weight scale below 1 and read the gradient at 10 and 50 steps back. Then push it above 1, and try the linear RNN.

#### How much gradient reaches earlier words?

A 32-unit RNN with random recurrent weights scaled to the chosen size, random inputs, 60 steps, fixed seed. Curve: size of ∂h60/∂ht for each earlier step t (log scale); band = 0.1–10.

With weight scale 1 and tanh, the gradient falls below 10⁻³ about **22 steps** back: words further away barely influence learning. At 0.7 the horizon shrinks to **11 steps**. Push the scale up to about 1.4 and the gradient survives 50 steps (still 0.1), but the network now sits at the edge of chaos: at 2 the gradient _grows_ backwards (about 12 at 50 steps), so tiny changes to early words swing the output wildly. The linear RNN shows the pure exponential: at scale 1.5 the gradient explodes to about **6 × 10⁹**. The useful middle ground is narrow and drifts as the weights train, which is why gated cells that make the memory path explicit won out.

**Now say why:** why does a small change in the scale make the gradient vanish or explode?

## Maths

### Maths

#### In one breath

An **RNN** processes a sequence one item at a time, keeping a **hidden state** ht that mixes the new input with the previous state, using the **same weights at every step**. That lets one small network handle sequences of any length. To train it, we **unroll** it into a deep network with one layer per time step and run ordinary backprop through it: **backpropagation through time (BPTT)**. The catch: the gradient from step T back to step t is a product of T − t Jacobians of the same recurrent matrix, so it **vanishes** or **explodes** exponentially. Plain RNNs struggle to remember more than about 10–20 steps, which is why LSTMs, GRUs and then attention took over. What you'll be able to do after this: write the RNN update, explain BPTT and truncated BPTT, and explain why long-range memory fails.

#### One update, repeated

$$ {h_t} = \tanh\!\big({W_{hh}\,h_{t-1}} + {W_{xh}\,x_t} + b\big), \qquad {\hat{y}_t = W_{hy}\,h_t} $$

The Elman network (1990). Goodfellow et al. ch. 10.

- **new hidden state**: The memory after reading word t: a vector, e.g. 128 numbers.

- **recurrent weights**: How the previous memory feeds the next one. The same W_hh is used at every step: that sharing is what makes the network work for any length.

- **current input**: The embedding of word t, projected by W_xh.

- **output**: Optional at each step (tagging every word) or only at the end (one sentiment score).

#### Unroll it, then backprop through time

1. The review arrives one word at a time.

2. Each step computes a new hidden state from the word and the previous state, with the same W_hh every time. Unrolled, it looks like a deep network with one layer per word, sharing weights.

3. A loss is computed at the end (e.g. sentiment) or at every step.

4. Backprop through time: run normal backprop through the unrolled graph. Because W_hh is shared, its gradient is the sum of its gradients at every step.

5. The signal from the loss to an early word passes through one Jacobian per step. Multiply many of them and it vanishes (or explodes), exactly like a very deep plain network.

## In practice

### In practice

#### Practical fixes and where RNNs stand today

- **Truncated BPTT:** backprop only through the last k steps (e.g. 50–200) while carrying the hidden state forward; cheaper, but can't learn dependencies longer than k.

- **Gradient clipping** for explosions (Pascanu et al. 2013; vanishing & exploding gradients).

- **Gated cells** (LSTM, GRU) for vanishing: next lesson.

- **Bidirectional RNNs** read the sequence both ways when the whole input is available (tagging, encoding).

- **Today:** Transformers replaced RNNs for most language tasks because RNNs process steps one after another (no parallelism over time) and forget long-range context. Recurrent ideas returned in state-space models (e.g. Mamba), which keep a fixed-size state with linear-time processing.

### The answer that sounds right

#### "The hidden state carries everything forward, so an RNN can remember any length"

It sounds right, since the hidden state does flow through every step. But each step multiplies it by the same weights and squashes it, so the gradient linking a late loss to an early word shrinks or explodes exponentially. In practice, a plain RNN remembers only tens of steps.

## Say it

### Why can't a plain RNN remember a word from 50 steps ago?

#### The interviewer pushes further

Follow-up 1 of 3

Why can't an RNN be parallelised over time?

h_t depends on h_{t−1}, so step t can't start until step t − 1 is done. Transformers compute all positions at once.

Follow-up 2 of 3

What does truncated BPTT give up?

Gradients from more than k steps back, so the model can't learn dependencies longer than the window (it can still carry information forward in the state).

Follow-up 3 of 3

Many-to-one vs many-to-many?

Sentiment of a review: read all words, one output at the end. Tagging: one output per word. Translation: an encoder RNN reads, a decoder RNN writes (seq2seq).

#### The 30-second answer

An RNN reads a sequence one step at a time, updating a hidden state h_t = tanh(W_hh h_{t−1} + W_xh x_t + b) with the same weights at every step, so it handles any length. Training unrolls it into a deep network over time and backpropagates through every step; the shared weight's gradient is summed across steps. The gradient from a late loss to an early step is a product of many Jacobians of W_hh and tanh slopes, so it vanishes or explodes exponentially; in practice plain RNNs remember only tens of steps. We use truncated BPTT, gradient clipping, and gated cells like LSTMs, and Transformers largely replaced RNNs because they parallelise over the sequence and attend directly to distant tokens.

**Go further**

#### What not to say

- "Each time step has its own weights." They're shared.

- "RNNs have unlimited memory." In theory the state can carry anything; in practice gradients limit what's learned.

**Key terms and sources**

Recurrent neural networks read a sequence one step at a time with a hidden state as memory; training unrolls them and backpropagates through every step, which makes gradients vanish or explode over long sequences · built from Elman (1990), Rumelhart et al. (1986), Werbos (1990), Bengio, Simard & Frasconi (1994), Pascanu et al. (2013) and Goodfellow et al. ch. 10 · checked 29 Oct 2026

#### Sources

1. J. Elman, "Finding Structure in Time", _Cognitive Science_ 14, 1990.

2. P. Werbos, "Backpropagation through time: what it does and how to do it", _Proc. IEEE_ 78(10), 1990.

3. Y. Bengio, P. Simard & P. Frasconi, "Learning long-term dependencies with gradient descent is difficult", _IEEE Trans. Neural Networks_ 5(2), 1994.

4. R. Pascanu, T. Mikolov & Y. Bengio, "On the difficulty of training recurrent neural networks", ICML 2013, [arXiv:1211.5063](https://arxiv.org/abs/1211.5063).

5. I. Goodfellow, Y. Bengio & A. Courville, _Deep Learning_, MIT Press 2016, ch. 10, [deeplearningbook.org](https://www.deeplearningbook.org/).
