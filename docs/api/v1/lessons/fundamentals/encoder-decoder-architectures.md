# Encoder vs Decoder vs Encoder-Decoder

> BERT vs GPT vs T5: what's actually different?

- Track: Fundamentals › Deep Learning › Attention and Transformers
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/encoder-decoder-architectures/
- Before this: The Transformer Block (`fundamentals/transformer-block`)
- Quiz topic: `attn`
- Sources checked: 2026-10-29 · Text last changed: 2026-11-20 · Version: 765cc27465

## Intuition

### The situation

You have three jobs: classify a review, generate a reply and translate a note. A colleague asks which of BERT, GPT and T5 to use. The interviewer asks:

> BERT vs GPT vs T5: what's actually different?

**Running example:** three jobs on restaurant text: **classify** a review as positive or negative, **generate** a reply to it, and **translate** a note ("the cold biryani arrived late" → French).

Where this lesson sits: the attention box, and in particular its **mask**.

Full walkthrough: The Transformer, End to End.

#### Understanding and generating need different views

To classify a review, every word should see the whole review, including words after it ("not" changes what comes before it as well as after). To _generate_ text one word at a time, a word must not see the future: during training, if token 5 could look at token 6, predicting token 6 would be trivial and the model would learn nothing usable at generation time.

### The idea

Think of reading a finished book, writing a new one, and translating. A reader can flip to any page. A writer can only see what's written so far. A translator reads the original while writing the new text. Those are the three attention masks.

[Figure: Three grids showing which tokens can see which. The encoder sees everything, the decoder only earlier tokens in a triangle, and cross-attention sees all of the source.]

_The same attention, with different masks deciding who can see whom._

### Play

**Try to break it.** Switch between encoder, decoder and cross-attention, and select different query tokens. Watch which tokens they can see.

#### Who can see whom?

Rows: queries; columns: keys. Teal = allowed, red = masked. In cross-attention, the rows are the decoder's French tokens and the columns the encoder's English tokens.

In the **decoder**, "cold" (token 4) sees only **"the biryani was cold"**: 45 of the 81 pairs are allowed (the lower triangle). In the **encoder** it sees all 9 tokens, including "but … great". In **cross-attention**, every French token may look at every English token, which is how the decoder reads the source sentence.

**Now say why:** what would go wrong if a token could see the future during training?

## Maths

### Maths

#### In one breath

The same block becomes three kinds of model depending on **which tokens may attend to which**. An **encoder** lets every token see every other token (bidirectional); it's trained to fill in masked words and is great for classification and embeddings (BERT). A **decoder** uses a **causal mask**: each token sees only itself and earlier tokens, so it can be trained to predict the next token and then **generate** text (GPT, LLaMA). An **encoder–decoder** encodes the input bidirectionally, then a causal decoder generates the output while attending to the encoder through **cross-attention** (original Transformer, T5). Today's LLMs are almost all decoder-only. What you'll be able to do after this: draw the three attention masks, match each family to its training objective and uses, and explain cross-attention.

#### A mask added to the attention scores

$$ \mathrm{softmax}\Big(\frac{QK^{\top}}{\sqrt{d_k}} + {M}\Big)V, \qquad {M_{ij} = \begin{cases}0 & j \le i\\ -\infty & j > i\end{cases}} $$

Vaswani et al. (2017), §3.2.3: masking in the decoder "ensures that the predictions for position i can depend only on the known outputs at positions less than i". Because all positions are still computed in parallel, a decoder trains on every next-token prediction in a sequence at once.

- **mask**: 0 where attention is allowed, −∞ where it isn’t. After the softmax, −∞ becomes a weight of exactly 0.

- **causal mask**: For a decoder, position i may attend to j only if j ≤ i: the lower triangle of the n × n score matrix.

#### Three families, three training objectives

| Family | Attention | Pre-training objective | Examples | Good for |
|---|---|---|---|---|
| **Encoder-only** | bidirectional | masked language modelling: predict ~15% hidden tokens | BERT, RoBERTa | classification, NER, embeddings / retrieval |
| **Decoder-only** | causal | next-token prediction | GPT series, LLaMA, Mistral | generation, chat, in-context learning |
| **Encoder–decoder** | bidirectional encoder + causal decoder + cross-attention | span corruption / denoising | original Transformer, T5, BART | translation, summarisation |

BERT (Devlin et al. 2019) masked 15% of input tokens; T5 (Raffel et al. 2020) framed every task as text-to-text with span corruption; BART (Lewis et al. 2020) trained a denoising autoencoder.

For encoders in detail, read BERT and Masked Language Models.

## In practice

### In practice

#### Why LLMs are decoder-only

- **One simple objective** on any text: every token is a training example, no corruption scheme needed.

- **Generation is native:** the same causal model that trains on next-token prediction generates at inference, reusing cached keys and values for earlier tokens.

- **Scales and generalises:** with prompting, one decoder handles classification, translation and reasoning. Wang et al. (ICML 2022) found causal decoders trained on next-token prediction gave the best zero-shot generalisation right after pre-training, while encoder–decoders did better after multitask fine-tuning.

- Encoders are still the workhorse for **embeddings** and retrieval, where the bidirectional view and small size win.

### The answer that sounds right

#### "BERT, GPT and T5 are basically the same model at different sizes"

It sounds right, since they're all built from the same blocks. But the attention mask and the training objective differ, and that decides what each can do. BERT sees the whole text and predicts hidden tokens, so it isn't built to generate. GPT only sees earlier tokens and predicts the next one, so generating text is natural.

## Say it

### BERT vs GPT vs T5: what's actually different?

#### The interviewer pushes further

Follow-up 1 of 3

Can BERT generate text?

Not naturally: it never learned left-to-right prediction and its bidirectional attention sees the future. It's built for understanding.

Follow-up 2 of 3

In cross-attention, which side gives Q, K and V?

Queries come from the decoder; keys and values come from the encoder output.

Follow-up 3 of 3

Why is training a decoder efficient despite generating one token at a time at inference?

With teacher forcing and the causal mask, all next-token predictions in a sequence are computed in one parallel forward pass.

#### The 30-second answer

The three families differ mainly in the attention mask. Encoders like BERT use bidirectional attention and masked-language-model pre-training, which suits classification and embeddings. Decoders like GPT and LLaMA use a causal mask so each token only sees earlier tokens, trained on next-token prediction, which makes generation natural and lets them train on every position in parallel. Encoder–decoders like the original Transformer and T5 encode the input bidirectionally and generate with a causal decoder that reads the encoder through cross-attention, which suits translation and summarisation. Modern LLMs are decoder-only because the objective is simple, it scales, and prompting covers most tasks.

**Go further**

#### What not to say

- "GPT has an encoder." GPT-style LLMs are decoder-only.

- "The causal mask is only used at inference." It's essential during training to stop the model from seeing the answer.

**Key terms and sources**

The three Transformer families: bidirectional encoders (BERT) for understanding, causal decoders (GPT, LLaMA) for generation, and encoder–decoders (original Transformer, T5, BART) for sequence-to-sequence; the attention masks that define them, their training objectives, and why decoder-only won for LLMs · built from Vaswani et al. (2017), Devlin et al. (2019), Radford et al. (2018, 2019), Raffel et al. (T5, JMLR 2020), Lewis et al. (BART, 2020) and Wang et al. (ICML 2022) · checked 29 Oct 2026

#### Sources

1. A. Vaswani et al., "Attention Is All You Need", NeurIPS 2017, [arXiv:1706.03762](https://arxiv.org/abs/1706.03762).

2. J. Devlin, M.-W. Chang, K. Lee & K. Toutanova, "BERT", NAACL 2019, [arXiv:1810.04805](https://arxiv.org/abs/1810.04805).

3. A. Radford et al., "Improving Language Understanding by Generative Pre-Training" (GPT), OpenAI 2018; "Language Models are Unsupervised Multitask Learners" (GPT-2), 2019.

4. C. Raffel et al., "Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer" (T5), _JMLR_ 21, 2020, [arXiv:1910.10683](https://arxiv.org/abs/1910.10683).

5. M. Lewis et al., "BART", ACL 2020, [arXiv:1910.13461](https://arxiv.org/abs/1910.13461).

6. T. Wang et al., "What Language Model Architecture and Pretraining Objective Work Best for Zero-Shot Generalization?", ICML 2022, [arXiv:2204.05832](https://arxiv.org/abs/2204.05832).
