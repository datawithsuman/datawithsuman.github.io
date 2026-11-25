# Attention Is All You Need

> What happens if you remove recurrence and keep only attention?

- Track: Papers Explained › Foundational
- Type: Paper · 30 min
- Page: https://aimlrounds.com/tracks/papers/attention-is-all-you-need/
- Before this: Self-Attention (Q, K, V) (`fundamentals/self-attention`)
- Related: Multi-Head Attention (`fundamentals/multi-head-attention`)
- Sources checked: 2026-11-09 · Text last changed: 2026-11-20 · Version: 0938e87fd8

## Gist

### The paper

Vaswani, Shazeer, Parmar, Uszkoreit, Jones, Gomez, Kaiser, Polosukhin · Google Brain, Google Research, University of Toronto · NeurIPS 2017 · arXiv [1706.03762](https://arxiv.org/abs/1706.03762) · 10 sources, checked 9 Nov 2026

In 2017, the best translation models read a sentence one word at a time with recurrent networks, which made them slow to train and weak at linking distant words. This paper threw recurrence out and built the whole model from **attention**: every word looks at every other word in one step, weighs how relevant each one is, and mixes in what it needs. Add **multiple attention heads**, **position signals** so word order isn't lost, and a stack of identical layers, and you get the **Transformer**. It set new translation records (28.4 BLEU on English-to-German) at a fraction of the training cost, and its architecture became the base of BERT, GPT and every large language model since.

### The problem

#### One sentence, followed through the whole model

from the paper's own figure

"The Law will never be perfect, but **its** application should be just."

To translate this well, the model has to work out that "its" means "the Law", nine words earlier. The paper shows two attention heads that do exactly that, with sharp attention from "its" back to "Law" and "application" [Fig. 4, p. 14](https://arxiv.org/pdf/1706.03762#page=14). We'll follow this sentence through every part of the model.

#### Recurrent models were slow and forgot distant words

In 2017 the best translation systems were recurrent networks (RNNs, usually LSTMs) in an encoder-decoder setup. A recurrent network reads word 1, updates a hidden state, then reads word 2, and so on: each hidden state ht depends on ht−1. The paper names the cost directly: this "inherently sequential nature precludes parallelization within training examples" [p. 2](https://arxiv.org/pdf/1706.03762#page=2).

##### Slow to train

Step 9 can't start until step 8 finishes, so a GPU can't process a sentence's words at the same time. Long sentences make it worse, because memory limits how many sentences you can batch instead.

##### Weak over long distances

To link "its" back to "Law", the signal has to pass through every word in between. The longer the path, the harder the dependency is to learn [p. 6](https://arxiv.org/pdf/1706.03762#page=6).

Attention already existed, as an add-on: it let the decoder look back at the encoder's states while translating. But "in all but a few cases" it sat on top of a recurrent network [p. 2](https://arxiv.org/pdf/1706.03762#page=2). The recurrence, and its sequential bottleneck, stayed.

### The idea

Think of a meeting. In a recurrent model, a message passes from person to person down a line, and it fades on the way. With attention, everyone in the room can hear everyone else directly, and each person decides who to listen to.

[Figure: Top row: a recurrent model passes information along a chain, one word at a time. Bottom row: attention connects every word directly to every other word.]

_Illustrative. A recurrent model reads a sentence in order. Attention connects every word in one step._

### Play

**Try it.** The word "its" is looking for what it refers to. Change the key size, then switch off the scaling.

Illustrative scores for the query "its" against four words, set so that random-like vectors at dk = 1 give scores of 2.0, 0.3, 0.6 and 1.4; larger keys multiply them by √dk, as footnote 4 describes. "Gradient left" is 1 − the largest weight, a rough measure of how much the softmax can still change.

**Notice:** without dividing by √dk, bigger keys make softmax pick one word almost completely, and the head stops learning. That one division is why the paper calls it _scaled_ dot-product attention.

## Method

### Method

#### Recurrent, convolutional, and attention as a helper

| Approach | How it links two words | The catch |
|---|---|---|
| **RNN / LSTM encoder-decoder** (Sutskever 2014) | Passes a hidden state along the sentence | Sequential: no parallelism within a sentence; path length grows with distance |
| **RNN + attention** (Bahdanau 2014) | The decoder attends to all encoder states | Still recurrent underneath, so still sequential |
| **Convolutional** (ByteNet, ConvS2S) | Stacks of convolutions over neighbouring words | Parallel, but linking distant words takes many layers: linear in distance for ConvS2S, logarithmic for ByteNet |

The Transformer's pitch was to keep the parallelism of convolutions and make every pair of words one step apart, using attention alone [p. 2](https://arxiv.org/pdf/1706.03762#page=2). The paper notes one cost of that: averaging over many positions blurs detail, which multi-head attention is designed to fix.

#### Each word asks a question, every word offers an answer

Each word is turned into three vectors. A **query** says what this word is looking for. A **key** says what each word offers. A **value** is the information a word passes on if it's chosen. For "its", the query asks roughly "which noun do I refer to?", and "Law" has a key that matches well.

$$ \text{Attention}(Q,K,V) = {\text{softmax}}\!\left({Q}\,{K^{\top}} \,/\, {\sqrt{d_k}}\right){V} $$

Equation 1 [p. 4](https://arxiv.org/pdf/1706.03762#page=4) · hover a term.

- **what each word looks for**: Q: one query vector per word, packed into a matrix.

- **what each word offers**: K: one key per word. Q times K transposed gives a score for every pair of words at once.

- **the scaling**: Divide by the square root of d_k, the key size (64 in the paper), so scores don’t get too large.

- **turn scores into weights**: Softmax turns each row of scores into weights that are positive and add up to 1.

- **what gets passed on**: V: the values. Each word’s output is the weighted average of every word’s value.

##### Why divide by √dk?

If the parts of a query and key are random with mean 0 and variance 1, their dot product has variance dk [footnote 4, p. 4](https://arxiv.org/pdf/1706.03762#page=4). With dk = 64, typical scores are 8 times larger than with dk = 1. Large scores push softmax into a region where one weight is nearly 1, the rest nearly 0, and the gradients become "extremely small". Dividing by √dk brings the variance back to about 1. Without it, the paper notes, dot-product attention did worse than additive attention at large dk.

With scaling on, "its" puts about half its weight on "Law" and a quarter on "application", whatever the key size. Turn scaling off at dk = 64 and "Law" takes 99.2% of the weight: the head stops learning, because almost no gradient flows to the other words.

##### Why dot products rather than a small network?

Additive attention, which scores pairs with a tiny feed-forward network, has similar theory, but dot-product attention "is much faster and more space-efficient in practice" because it's one big matrix multiplication [p. 4](https://arxiv.org/pdf/1706.03762#page=4).

#### Several smaller attentions beat one big one

One attention function averages everything into a single weighted mix, so it can only look one way at a time. The paper instead projects Q, K and V **h = 8 times** with different learned matrices, runs attention on each in parallel, joins the results and projects them back [p. 5](https://arxiv.org/pdf/1706.03762#page=5).

$$ \text{MultiHead}(Q,K,V) = {\text{Concat}(\text{head}_1,\dots,\text{head}_8)}\,{W^{O}}, \quad {\text{head}_i} = \text{Attention}(Q{W_i^{Q}}, K{W_i^{K}}, V{W_i^{V}}) $$

With dmodel = 512 and 8 heads, each head works in dk = dv = 64 dimensions, so the total cost is about the same as one full-size head [p. 5](https://arxiv.org/pdf/1706.03762#page=5).

- **one head**: Each head runs attention on its own projected copies of Q, K and V.

- **learned projections**: Each head has its own matrices, so each can learn to look for something different.

- **join the heads**: The 8 head outputs (64 numbers each) are concatenated back to 512.

- **mix them**: A final matrix W^O mixes the heads into one output per word.

In our sentence, the paper's visualisations show two heads in layer 5 sharply linking "its" to "Law" and "application", while other heads follow sentence structure: "the heads clearly learned to perform different tasks" [Fig. 5, p. 15](https://arxiv.org/pdf/1706.03762#page=15).

##### How many heads? (Table 3, rows A)

At the same total compute, 1 head scored 24.9 BLEU on the development set, 8 heads 25.8, 16 heads 25.8 and 32 heads 25.4. One head is 0.9 BLEU worse than the best, and too many heads hurts too [p. 9](https://arxiv.org/pdf/1706.03762#page=9).

##### Three places attention is used

- **Encoder self-attention:** every input word attends to every input word.

- **Decoder self-attention, masked:** each output word attends only to earlier output words, so the model can't peek at the answer. Future positions are set to −∞ before the softmax.

- **Encoder-decoder attention:** queries come from the decoder, keys and values from the encoder, so each output word can look at the whole input sentence [p. 5](https://arxiv.org/pdf/1706.03762#page=5).

#### Attention alone can't tell "dog bites man" from "man bites dog"

Attention compares every word with every other word, and nothing in that comparison depends on order. Shuffle the words and each output is the same, just shuffled. So the paper adds a **position signal** to each word's embedding before the first layer [p. 6](https://arxiv.org/pdf/1706.03762#page=6).

$$ PE_{({pos},\,2{i})} = {\sin}\!\left(\frac{{pos}}{{10000}^{2{i}/d_{model}}}\right), \quad PE_{({pos},\,2{i}+1)} = {\cos}\!\left(\frac{{pos}}{{10000}^{2{i}/d_{model}}}\right) $$

Section 3.5 [p. 6](https://arxiv.org/pdf/1706.03762#page=6).

- **position in the sentence**: pos: 0 for the first word, 1 for the second, and so on.

- **which dimension pair**: i picks the dimension pair. Low i gives fast waves, high i gives slow waves.

- **the wavelength range**: 10000 sets the range: wavelengths grow geometrically from 2π to 10000·2π.

- **sine and cosine**: Even dimensions use sine and odd ones cosine, so a fixed offset k is a linear function of the encoding, which the paper hoped would help attend by relative position.

Think of a clock with many hands moving at different speeds. Any moment gets a unique combination of hand positions, and the same gap between two moments always looks the same.

##### Did the fixed formula matter? (Table 3, row E)

Learned position embeddings gave nearly identical results: 25.7 BLEU against 25.8 for sines. The authors kept sines because they "may allow the model to extrapolate to sequence lengths longer than the ones encountered during training" [p. 6](https://arxiv.org/pdf/1706.03762#page=6). That was a hope, not a tested result.

#### Six identical layers on each side

1. Each input word becomes a 512-number embedding, multiplied by √512, plus its position signal.

2. The encoder is 6 identical layers. Each has self-attention, then a feed-forward network applied to each word on its own, each wrapped as LayerNorm(x + sublayer(x)).

3. The decoder is also 6 layers, with a third sublayer. Its self-attention is masked so word i only sees words before i.

4. Encoder-decoder attention lets every output position look at the encoder's final representation of the whole input.

5. A linear layer and softmax turn the top decoder output into next-word probabilities. The same weight matrix is shared with both embedding layers.

Sections 3.1, 3.3 and 3.4 [p. 3–5](https://arxiv.org/pdf/1706.03762#page=3). The residual connections need every sublayer to output dmodel = 512 numbers. The feed-forward network is max(0, xW1 + b1)W2 + b2, with an inner size of 2,048.

| | Layers N | dmodel | dff | Heads h | Dropout | Parameters |
|---|---|---|---|---|---|---|
| **Base** | 6 | 512 | 2,048 | 8 | 0.1 | 65 M |
| **Big** | 6 | 1,024 | 4,096 | 16 | 0.3 | 213 M |

Table 3 [p. 9](https://arxiv.org/pdf/1706.03762#page=9). The big English-to-French model used dropout 0.1, not 0.3.

#### 12 hours on one machine for the base model

| English-German data | WMT 2014, about 4.5 million sentence pairs, byte-pair encoding with a shared vocabulary of about 37,000 tokens |
|---|---|
| English-French data | WMT 2014, 36 million sentences, 32,000 word-piece vocabulary |
| Batch | About 25,000 source and 25,000 target tokens, sentences grouped by length |
| Hardware | One machine with 8 NVIDIA P100 GPUs |
| Base model | 0.4 s per step, 100,000 steps: **12 hours** |
| Big model | 1.0 s per step, 300,000 steps: **3.5 days** |
| Regularisation | Dropout 0.1 on every sublayer output and on embeddings; label smoothing 0.1, which "hurts perplexity" but improves BLEU |

Sections 5.1–5.4 [p. 7–8](https://arxiv.org/pdf/1706.03762#page=7).

##### The warm-up schedule

$$ lrate = {d_{model}^{-0.5}} \cdot \min\!\left({step^{-0.5}},\; {step \cdot warmup^{-1.5}}\right),\quad warmup = 4000 $$

Adam with β1 = 0.9, β2 = 0.98, ε = 10−9. Equation 3 [p. 7](https://arxiv.org/pdf/1706.03762#page=7).

- **model size**: d_model^(−0.5): bigger models get a smaller learning rate overall.

- **warm-up**: For the first 4,000 steps the rate rises linearly, so the early, noisy updates stay small.

- **decay**: After that it falls with the inverse square root of the step number.

Computed from equation 3 with dmodel = 512. It peaks at step 4,000 at about 0.0007, and by step 100,000 it has fallen to about 0.00014.

## Results

### What they found

#### New records, at a fraction of the training cost

##### English-to-German BLEU, WMT 2014 test set (Table 2)

| Model | EN-DE BLEU | EN-FR BLEU | Training cost EN-DE (FLOPs) |
|---|---|---|---|
| GNMT + RL | 24.6 | 39.92 | 2.3 × 1019 |
| ConvS2S | 25.16 | 40.46 | 9.6 × 1018 |
| Mixture of Experts | 26.03 | 40.56 | 2.0 × 1019 |
| GNMT + RL ensemble | 26.30 | 41.16 | 1.8 × 1020 |
| ConvS2S ensemble | 26.36 | 41.29 | 7.7 × 1019 |
| **Transformer base** | **27.3** | 38.1 | **3.3 × 1018** |
| **Transformer big** | **28.4** | **41.8** | 2.3 × 1019 |

Table 2 [p. 8](https://arxiv.org/pdf/1706.03762#page=8). FLOPs are the authors' estimates from training time × GPUs × an assumed GPU speed.

- **English-to-German:** the big model beat every earlier result, ensembles included, by more than 2 BLEU. Even the base model beat all of them, at roughly 1/3 to 1/55 of their training cost.

- **English-to-French:** 41.8 BLEU, a new best for a single model, at less than a quarter of the cost of the previous best. Note: the text on page 8 says 41.0, while the abstract and Table 2 say 41.8, an inconsistency that remains in the latest arXiv version.

- **Beyond translation:** a 4-layer Transformer on English constituency parsing reached 91.3 F1 trained only on the 40,000-sentence WSJ set, and 92.7 with 17 million extra sentences, beating every earlier model except one generative parser (93.3) [Table 4, p. 10](https://arxiv.org/pdf/1706.03762#page=10). Recurrent sequence-to-sequence models had struggled with so little data.

#### Which parts mattered

The authors changed one thing at a time in the base model and measured English-to-German BLEU on the development set (base: 25.8) [p. 9](https://arxiv.org/pdf/1706.03762#page=9).

| Change | Dev BLEU | What it shows |
|---|---|---|
| 1 head instead of 8 (same compute) | 24.9 | Multiple heads help |
| 32 heads | 25.4 | Too many small heads hurts |
| Key size dk 16 instead of 64 | 25.1 | Matching words is hard; small keys lose detail |
| 2 layers instead of 6 | 23.7 | Depth matters |
| dmodel 1,024, 128-wide heads | 26.0 | Bigger is better |
| No dropout | 24.6 | Dropout is essential against overfitting |
| Learned positions instead of sines | 25.7 | The exact position scheme barely matters here |
| **Big model** | **26.4** | Scale wins |

#### Constant path length, full parallelism, quadratic cost

| Layer type | Work per layer | Sequential steps | Longest path between two words |
|---|---|---|---|
| **Self-attention** | O(n²·d) | O(1) | O(1) |
| Recurrent | O(n·d²) | O(n) | O(n) |
| Convolutional | O(k·n·d²) | O(1) | O(logk n) |
| Restricted self-attention | O(r·n·d) | O(1) | O(n/r) |

n = sentence length, d = vector size, k = convolution width, r = neighbourhood size. Table 1 [p. 6](https://arxiv.org/pdf/1706.03762#page=6).

Self-attention is cheaper than recurrence when the sentence is shorter than the vector size (n < d), which was true for translation: sentences of tens of tokens against d = 512. Every pair of words is one step apart, and all positions are computed at once.

##### Try it: when does attention get expensive?

Counts the leading term of Table 1 only, ignoring constants. Recurrent layers also need n sequential steps, which this count doesn't show.

### Where it falls short

#### What the paper didn't solve

- **Quadratic cost in length.** Comparing every pair of words is fine for sentences, expensive for books. The authors flagged this and suggested restricted, local attention as future work [p. 7](https://arxiv.org/pdf/1706.03762#page=7).

- **Position handling was a hope.** The sine encodings were chosen because they "may" extrapolate to longer inputs, but this wasn't tested, and later work found absolute encodings extrapolate poorly.

- **Training stability.** Layer norm after each residual (post-LN) needed the careful warm-up. Later work showed that putting the norm before each sublayer (pre-LN) trains more stably, and most modern models do that.

- **Narrow evidence.** Results cover two translation pairs and one parsing task, with single runs and no variance reported. BLEU itself is a rough measure of translation quality.

- **A small inconsistency.** English-to-French is reported as 41.8 BLEU in the abstract and Table 2, but 41.0 in the text.

## Why it matters

### What it changed

Training could now run in parallel across a whole sequence, and any two words were one step apart. Within two years the same blocks, split into encoder-only and decoder-only models, became BERT and GPT, and the architecture now underlies almost every large language model.

**What to remember.** Attention alone, with multiple heads, position signals and residual layers, replaced recurrence. The core equation, softmax(QKT/√dk)V, is still the heart of today's models.

#### From a translation model to every large language model

| Year | What happened | Which part of the Transformer |
|---|---|---|
| 2018 | GPT: language model pretraining | Decoder only, masked self-attention |
| 2018 | BERT: bidirectional pretraining for understanding | Encoder only |
| 2019 | T5: every text task as text-to-text | The full encoder-decoder |
| 2020 | Vision Transformer: image patches as tokens | Encoder only, applied to images |
| 2020 on | Pre-LN, rotary positions (RoPE), multi-query and grouped-query attention, FlashAttention | Fixes for stability, position handling, inference memory and speed |

Today's large language models are mostly decoder-only Transformers with these fixes. The core equation, softmax(QKT/√dk)V, is unchanged. The authors' closing hope, to extend the model to "images, audio and video" [p. 10](https://arxiv.org/pdf/1706.03762#page=10), came true.

#### Read it

**Read** sections 3 (the architecture) and 4 (why self-attention), plus Figures 1 and 2. They're short, and almost every interview question about Transformers traces back to them. **Skim** the training details unless you plan to reproduce it. **Look at** the attention visualisations in the appendix to see heads learning different jobs.

For a line-by-line code walkthrough, the Annotated Transformer is the classic companion.

**Key terms and sources**

#### Words to know

Self-attention

Each position in a sequence attends to every position in the same sequence.

Query, key, value

Three learned projections of each word: what it looks for, what it offers, and what it passes on.

Scaled dot-product attention

softmax(QKT/√dk)V. The scaling keeps softmax out of its flat, low-gradient region.

Multi-head attention

Several attentions in parallel on smaller projections, joined and mixed.

Masking

Setting scores for future positions to −∞ so the decoder can't see words it hasn't produced yet.

Positional encoding

A signal added to each embedding so the model knows word order.

Residual connection and layer norm

Each sublayer's output is LayerNorm(x + sublayer(x)), which keeps deep stacks trainable.

BLEU

A translation score from 0 to 100 based on overlapping word sequences with reference translations.

Label smoothing

Training targets that give a little probability to wrong words, which makes the model less overconfident.

#### Everything on this page comes from these

1. Vaswani et al. (2017). Attention Is All You Need. NeurIPS 2017. [arXiv 1706.03762](https://arxiv.org/abs/1706.03762) (read in full; page numbers refer to v7)

2. Bahdanau, Cho, Bengio (2014). Neural Machine Translation by Jointly Learning to Align and Translate. [arXiv 1409.0473](https://arxiv.org/abs/1409.0473)

3. Sutskever, Vinyals, Le (2014). Sequence to Sequence Learning with Neural Networks. [arXiv 1409.3215](https://arxiv.org/abs/1409.3215)

4. Devlin et al. (2018). BERT. [arXiv 1810.04805](https://arxiv.org/abs/1810.04805)

5. Dosovitskiy et al. (2020). An Image is Worth 16x16 Words (Vision Transformer). [arXiv 2010.11929](https://arxiv.org/abs/2010.11929)

6. Xiong et al. (2020). On Layer Normalization in the Transformer Architecture. [arXiv 2002.04745](https://arxiv.org/abs/2002.04745)

7. Su et al. (2021). RoFormer: Rotary Position Embedding. [arXiv 2104.09864](https://arxiv.org/abs/2104.09864)

8. Dao et al. (2022). FlashAttention. [arXiv 2205.14135](https://arxiv.org/abs/2205.14135)

9. Ainslie et al. (2023). GQA: Training Generalized Multi-Query Transformer Models. [arXiv 2305.13245](https://arxiv.org/abs/2305.13245)

10. Rush et al. The Annotated Transformer. [nlp.seas.harvard.edu](https://nlp.seas.harvard.edu/annotated-transformer/)

The attention scores in the first lab are illustrative. All other numbers come from the paper. @datawithsuman
