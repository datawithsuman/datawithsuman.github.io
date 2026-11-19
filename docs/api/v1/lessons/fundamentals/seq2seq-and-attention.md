# Seq2seq and Bahdanau Attention

> How did attention fix translation of long sentences?

- Track: Fundamentals › Deep Learning › Sequence models
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/seq2seq-and-attention/
- Before this: LSTM and GRU (`fundamentals/lstm-and-gru`)
- Quiz topic: `seq`

## Intuition

### The situation

You're translating restaurant notes into French, and your encoder–decoder works on short sentences but falls apart on long ones. The interviewer asks:

> How did attention fix translation of long sentences?

**Running example:** the app translates restaurant notes for a French-speaking courier: "_the cold biryani arrived late_" → "_le biryani froid est arrivé en retard_". French puts the adjective after the noun, so the word order changes.

#### Input and output are both sequences, of different lengths

Translation, summarisation, speech-to-text and question answering map one sequence to another with no one-to-one word correspondence: 5 English words become 7 French words in a different order. An RNN tagger, which outputs one label per input step, can't do that.

### The idea

Think of a translator. The old way is to read the whole sentence, memorise it, and translate from memory. Attention lets the translator glance back at the original for every word they write.

[Figure: An English sentence on top and French underneath, with lines linking each French word to the English word it looks at. The lines for cold and biryani cross, because French puts the adjective after the noun.]

_Illustrative, using the lesson's sentence. The crossed lines show the change in word order._

### Play

**Try to break it.** Step through each French word and see which English word gets the most weight. Then change the softmax temperature.

#### The alignment for our sentence

Scores are dot products between hand-set decoder and encoder vectors chosen to mimic what a trained model learns (illustrative, not trained). Rows: French output words; columns: English source words; darker = more weight. The selected row is outlined.

Producing **froid**, the decoder puts most of its weight on **cold**, and producing **biryani** it looks at **biryani**: the alignment crosses, handling the word-order swap with no rule about adjectives. Lower the temperature and the attention becomes almost a hard pointer; raise it and the weights spread over every word, blurring the context. "en retard" (two French words for "late") shows that one output can align to one input even when the lengths differ.

**Now say why:** why do the weights handle the word-order change without any rule telling them to?

## Maths

### Maths

#### In one breath

**Seq2seq** models handle tasks where both the input and output are sequences of different lengths, like translation or summarisation: an **encoder** RNN reads the input, a **decoder** RNN writes the output one token at a time. The original design squeezed the whole input into **one fixed-size vector**, a bottleneck that hurt long sentences. **Bahdanau attention** removed it: at each output step the decoder scores every encoder state, turns the scores into weights with a softmax, and reads a weighted average (the **context vector**). The weights form a soft **alignment** between output and input words, learned without any alignment labels. This idea, with the RNNs removed, became the Transformer.What you'll be able to do after this: describe an encoder–decoder, explain the bottleneck, and compute attention weights and a context vector.

#### Encoder–decoder (seq2seq)

- **Encoder:** an RNN/LSTM reads the source words and produces a hidden state per word; the last one summarises the sentence.

- **Decoder:** another RNN starts from that summary and generates the output one word at a time, feeding each generated word back in, until it emits an end token.

- Sutskever, Vinyals & Le (NeurIPS 2014) used deep LSTMs and found that **reversing the source sentence** helped, because it put the first source words close to the first target words; Cho et al. (2014) introduced the encoder–decoder with the GRU.

#### Bahdanau attention: look back at every word

$$ e_{ij} = \mathrm{score}(s_{i-1}, h_j), \qquad \alpha_{ij} = \frac{\exp(e_{ij})}{\sum_k \exp(e_{ik})}, \qquad c_i = \sum_j \alpha_{ij}\, h_j $$

Bahdanau, Cho & Bengio, "Neural Machine Translation by Jointly Learning to Align and Translate", ICLR 2015 arXiv:1409.0473: with a bidirectional encoder and attention, English→French quality was comparable to the phrase-based system of the time and, unlike the plain encoder–decoder, held up on long sentences. Luong et al. (EMNLP 2015) introduced simpler dot-product variants.

- **score**: How relevant is source word j for producing output word i? Bahdanau used a small neural net on the decoder state and encoder state (additive attention); Luong et al. used a dot product.

- **attention weights**: A softmax over all source words: positive weights that sum to 1. This row of weights is the soft alignment.

- **context vector**: A weighted average of encoder states, recomputed for every output word and fed to the decoder alongside its own state.

## In practice

### In practice

#### From attention-on-RNNs to attention-only

- Attention fixed the bottleneck but the RNNs still processed words one at a time, slow to train and still forgetful inside each encoder.

- Vaswani et al. (2017) kept the attention and removed the recurrence: every word attends to every other word directly (self-attention), all positions computed in parallel. That is the Transformer.

- The "query" (decoder state) / "key" (encoder state used for scoring) / "value" (encoder state averaged) roles in Bahdanau attention are exactly the Q, K, V of Transformer attention.

For greedy and beam search, see Decoding and Sampling.

### The answer that sounds right

#### "One vector for the whole sentence"

Whether the source has 5 words or 50, the decoder only sees one fixed-size vector. Long sentences don't fit: Cho et al. and Bahdanau et al. both found translation quality **dropped sharply as sentence length grew**. The reversing trick only moves the problem: whichever words end up far from where they're needed get forgotten.

## Say it

### How did attention fix translation of long sentences?

#### The interviewer pushes further

Follow-up 1 of 3

Additive vs dot-product attention?

Additive (Bahdanau) scores with a small MLP: vᵀ tanh(W s + U h). Dot-product (Luong) uses sᵀh or sᵀWh: cheaper and the basis of Transformer attention.

Follow-up 2 of 3

What is teacher forcing?

During training, the decoder is fed the true previous word rather than its own prediction; it speeds training but causes a train–test mismatch (exposure bias).

Follow-up 3 of 3

How is the output generated at inference?

Greedily or with beam search, one token at a time, until an end-of-sequence token.

#### The 30-second answer

A seq2seq model has an encoder RNN that reads the input and a decoder RNN that generates the output token by token. Originally the decoder only got the encoder's final hidden state, a fixed-length bottleneck that made long sentences fail. Bahdanau attention fixes it: at each decoding step, score the decoder state against every encoder state, softmax the scores into weights, and feed the weighted average of encoder states, the context vector, to the decoder. The weights act as a learned soft alignment between output and input. Removing the RNNs and keeping only attention gave the Transformer.

**Go further**

#### What not to say

- "Attention was invented by the Transformer paper." It came from Bahdanau et al. (2014) for RNN translation.

- "Attention weights are hard alignments." They're soft (a probability distribution over source positions).

**Key terms and sources**

Encoder–decoder models for sequence-to-sequence tasks, the fixed-length bottleneck, and the first attention mechanism, which lets the decoder look back at every input word when producing each output word · built from Sutskever, Vinyals & Le (2014), Cho et al. (2014), Bahdanau, Cho & Bengio (ICLR 2015), Luong et al. (2015) and Vaswani et al. (2017) · checked 29 Oct 2026

#### Sources

1. I. Sutskever, O. Vinyals & Q. Le, "Sequence to Sequence Learning with Neural Networks", NeurIPS 2014, arXiv:1409.3215.

2. K. Cho et al., "Learning Phrase Representations using RNN Encoder–Decoder for Statistical Machine Translation", EMNLP 2014, arXiv:1406.1078.

3. D. Bahdanau, K. Cho & Y. Bengio, "Neural Machine Translation by Jointly Learning to Align and Translate", ICLR 2015, arXiv:1409.0473.

4. M.-T. Luong, H. Pham & C. Manning, "Effective Approaches to Attention-based Neural Machine Translation", EMNLP 2015, arXiv:1508.04025.

5. A. Vaswani et al., "Attention Is All You Need", NeurIPS 2017, arXiv:1706.03762.
