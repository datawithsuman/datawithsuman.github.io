# LSTM and GRU

> How do gates let a network remember for hundreds of steps?

- Track: Fundamentals › Deep Learning › Sequence models
- Type: Concept · 25 min
- Page: https://aimlrounds.com/tracks/fundamentals/lstm-and-gru/
- Before this: RNNs and Backprop Through Time (`fundamentals/rnns-and-backprop-through-time`)
- Quiz topic: `seq`
- Sources checked: 2026-10-29 · Text last changed: 2026-11-20 · Version: f2e1fb26c8

## Intuition

### The situation

Your review says "the biryani was cold", then 40 words about delivery, then "overall I'd order again". A plain RNN has forgotten "cold" by the end. The interviewer asks:

> How do gates let a network remember for hundreds of steps?

**Running example:** the review "_the biryani was cold but … [40 more words about the delivery] … overall I'd order again_". To score it, the model must remember "cold" across 40+ words, then weigh it against "order again".

#### A memory that's rewritten every step fades fast

In a plain RNN, ht = tanh(W ht−1 + …): every step multiplies the old memory by W and squashes it. As the previous lesson showed, the gradient reaching 50 steps back is around 10⁻⁶. We need a path where the memory is kept by default and only changed deliberately.

### The idea

Think of swapping the sticky note for a notebook. Nothing gets rewritten unless you choose to. One gate decides what to erase, and another decides what to add, so old notes survive by default.

[Figure: A straight memory line runs across the top. Gates along it decide what to forget and what to add, so memory is kept by default.]

_Illustrative. The output gate, not shown, decides what to expose at each step._

### Play

**Try to break it.** Move the forget-gate bias up and down, and compare what the LSTM keeps after 50 and 200 steps with the plain RNN.

#### How much survives after many steps?

Green: gradient kept along the LSTM cell state, the product of forget-gate values (each ft = σ(bf + noise from the input), fixed seed). Red: the plain 32-unit tanh RNN from the previous lesson (weight scale 1). Log scale.

With bf = 4 the forget gate averages about 0.98, and the LSTM keeps about **40%** of the signal after 50 steps and still about **1.4%** after 200 (56% with bf = 6), while the plain RNN is down to about **10⁻⁶** at 50 steps. Slide bf down to 0 (f ≈ 0.5) and the LSTM forgets almost immediately: memory is a choice the gate makes, which training learns per slot and per input.

**Now say why:** why does the LSTM keep so much more, and what happens when its forget gate is low?

## Maths

### Maths

#### In one breath

A plain RNN overwrites its memory at every step and its gradients fade within tens of steps. An **LSTM** adds a separate **cell state** ct, a memory conveyor belt that is changed only by **addition** and by a multiplicative **forget gate**. Learned **gates** (sigmoids between 0 and 1) decide what to forget, what to write and what to reveal. When the forget gate stays near 1, information and gradients pass through hundreds of steps almost unchanged, like a residual connection through time. The **GRU** merges the gates into an update gate and a reset gate, with no separate cell: fewer parameters, usually similar accuracy. What you'll be able to do after this: write the LSTM and GRU equations, explain each gate, and explain why gating fixes vanishing gradients.

#### The LSTM cell

$$ {f_t = \sigma(W_f[h_{t-1},x_t]+b_f)},\;\; {i_t = \sigma(W_i[\cdot]+b_i)},\;\; {\tilde{c}_t = \tanh(W_c[\cdot]+b_c)} \\[6pt] {c_t = f_t \odot c_{t-1} + i_t \odot \tilde{c}_t}, \qquad {h_t = o_t \odot \tanh(c_t),\;\; o_t = \sigma(W_o[\cdot]+b_o)} $$

Hochreiter & Schmidhuber, _Neural Computation_ 1997 (with the forget gate from Gers et al. 2000). An LSTM layer has 4 weight matrices: about 4× the parameters of a plain RNN of the same size. Olah's "Understanding LSTM Networks" (2015) is the classic visual walkthrough.

- **forget gate**: For each memory slot, a number between 0 and 1 from a sigmoid: how much of the old cell state to keep. Added by Gers et al. (2000); 1 means keep everything.

- **input gate**: How much of the new candidate to write.

- **candidate**: What could be written: a tanh of the input and previous hidden state, like a plain RNN’s update.

- **cell state update**: Old memory times the forget gate PLUS gated new content. The plus is the key: no squashing on the memory path.

- **output gate**: How much of the (squashed) memory to reveal as the hidden state h_t, which the next layer and the gates see.

#### An additive memory path

Along the cell state, ∂ct/∂ct−1 = ft (element-wise). There's no weight matrix and no tanh slope in the way: if the network learns f ≈ 1 for a slot, that slot's memory and its gradient pass through unchanged, exactly like the identity path in a ResNet. A common trick is to initialise the forget-gate bias to 1 so the cell starts out remembering (Jozefowicz et al. 2015).

## In practice

### In practice

#### The GRU: fewer gates, similar results

$$ {z_t = \sigma(W_z[h_{t-1},x_t])},\;\; {r_t = \sigma(W_r[h_{t-1},x_t])},\;\; \tilde{h}_t = \tanh(W[r_t\odot h_{t-1}, x_t]),\;\; {h_t = (1-z_t)\odot h_{t-1} + z_t \odot \tilde{h}_t} $$

Cho et al., EMNLP 2014. Chung et al. (2014) found GRUs comparable to LSTMs on music and speech modelling; Jozefowicz et al. (2015) found neither consistently better across many tasks. GRUs have 3 weight matrices instead of 4.

- **update gate**: Blends old state and new candidate in one go: z near 0 keeps the old state (like forget ≈ 1, input ≈ 0).

- **reset gate**: How much of the old state to use when computing the candidate: lets the unit ignore the past for a fresh start.

- **interpolation**: The new state is a weighted average of old and candidate: again an additive, gated memory path, but no separate cell state and no output gate.

### The answer that sounds right

#### "An LSTM remembers because it has more memory"

It sounds right, since an LSTM does have more parameters. But the fix is the shape of the path, not its size. Along the cell state, the derivative is just the forget gate, with no weight matrix or tanh slope in the way. When the network learns a forget gate near 1, information and gradients pass through almost untouched.

## Say it

### How do gates let a network remember for hundreds of steps?

#### The interviewer pushes further

Follow-up 1 of 3

Why sigmoid for gates and tanh for content?

Gates are fractions (0 to 1, "how much to let through"); content can be positive or negative, so tanh keeps it centred in (−1, 1).

Follow-up 2 of 3

Do LSTMs fully solve exploding gradients?

No; the paths through the gates and hidden state can still explode, so gradient clipping is still standard.

Follow-up 3 of 3

How many parameters does an LSTM layer have?

4 × (hidden × (hidden + input) + hidden): four gate/candidate blocks, each with a weight matrix over [h, x] and a bias.

#### The 30-second answer

An LSTM adds a cell state that is updated additively: c_t = f_t ⊙ c_{t−1} + i_t ⊙ c̃_t, with sigmoid gates deciding what to forget, what to write, and with an output gate what to expose as h_t. Because the derivative along the cell is just the forget gate, the network can keep information and gradients for hundreds of steps by learning f near 1, which fixes the vanishing-gradient problem of plain RNNs, much like a residual connection through time. A GRU merges this into an update gate that interpolates old and new state plus a reset gate, with fewer parameters and usually similar accuracy. Both have largely been replaced by Transformers for language, but are still used for streaming and small on-device models.

**Go further**

#### What not to say

- "LSTMs have perfect long-term memory." The gates must learn to keep information, and very long contexts still degrade.

- "GRU is always better because it's smaller." Neither wins consistently.

**Key terms and sources**

Gated recurrent cells: the LSTM's cell state and its forget, input and output gates, the simpler GRU with update and reset gates, why an additive memory path stops gradients vanishing, and LSTM vs GRU in practice · built from Hochreiter & Schmidhuber (1997), Gers, Schmidhuber & Cummins (2000), Cho et al. (2014), Chung et al. (2014), Jozefowicz et al. (2015) and Olah, "Understanding LSTM Networks" (2015) · checked 29 Oct 2026

#### Sources

1. S. Hochreiter & J. Schmidhuber, "Long Short-Term Memory", _Neural Computation_ 9(8), 1997.

2. F. Gers, J. Schmidhuber & F. Cummins, "Learning to Forget: Continual Prediction with LSTM", _Neural Computation_ 12(10), 2000.

3. K. Cho et al., "Learning Phrase Representations using RNN Encoder–Decoder for Statistical Machine Translation", EMNLP 2014, [arXiv:1406.1078](https://arxiv.org/abs/1406.1078).

4. J. Chung, C. Gulcehre, K. Cho & Y. Bengio, "Empirical Evaluation of Gated Recurrent Neural Networks on Sequence Modeling", [arXiv:1412.3555](https://arxiv.org/abs/1412.3555), 2014.

5. R. Jozefowicz, W. Zaremba & I. Sutskever, "An Empirical Exploration of Recurrent Network Architectures", ICML 2015.

6. C. Olah, ["Understanding LSTM Networks"](https://colah.github.io/posts/2015-08-Understanding-LSTMs/), 2015.
