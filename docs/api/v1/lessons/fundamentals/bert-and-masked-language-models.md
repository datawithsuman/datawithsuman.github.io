# BERT and Masked Language Models

> How is BERT trained, and how do you adapt it for classification, tagging and question answering?

- Track: Fundamentals › NLP Fundamentals › Tagging, retrieval and evaluation
- Type: Concept · 18 min
- Page: https://aimlrounds.com/tracks/fundamentals/bert-and-masked-language-models/
- Before this: Sequence Labelling and NER (`fundamentals/sequence-labelling-and-ner`), Encoder vs Decoder vs Encoder-Decoder (`fundamentals/encoder-decoder-architectures`)
- Quiz topic: `nlp`

## Intuition

### The situation

You need to tag support tickets and pull out answers from policy documents, for millions of messages a day. An LLM works, but costs too much at this volume. Someone suggests fine-tuning BERT, but a teammate asks how a model trained on no labels can help. The interviewer asks:

> How is BERT trained, and how do you adapt it for classification, tagging and question answering?

#### Why it matters

BERT-style encoders still power classification, tagging, embeddings and re-ranking, as they're smaller and cheaper than LLMs. Interview questions often cover how the masking works and how the heads attach. This builds on encoders and decoders.

### The idea

Think of a fill-in-the-blanks test. To guess the missing word in "the biryani was ___ but the raita was fresh", you must understand the whole sentence, on both sides of the gap. Practise on billions of these, and you learn language. Then you can quickly learn a new job, like sorting tickets.

[Figure: Three stages. Pretrain by filling masked tokens. Add a small head for your task. Fine-tune gently.]

_Bidirectional context suits understanding, not generating._

### Play

**Try to break it.** Raise the share chosen to 50%. Then draw again.

#### Mask a sentence

An illustrative pair of sentences, split by word for simplicity. Special tokens aren't masked. Orange: [MASK]. Purple: a random token. Green: chosen, but unchanged. The model must predict the original word at all three.

Draw again a few times: the choice is random, and it changes the input every time it's drawn. Raise the share to **50%**: the task gets much harder, with less context around each gap. Any green tokens look normal, yet they're still scored, so the model must be useful everywhere, rather than only at [MASK].

**Now say why:** why are some chosen tokens left unchanged?

## Maths

### Maths

#### In one breath

**BERT** is a Transformer encoder trained on unlabelled text by hiding words and predicting them. It masks 15% of tokens: 80% of those become [MASK], 10% become a random token, and 10% stay as they are. Because it sees both sides of each word, it learns rich context, but it can't naturally generate text. To use it, you add a small head for your task, and fine-tune with a low learning rate. Classification uses [CLS], NER labels each token, and QA predicts where the answer starts and ends.

#### Training it, then using it

##### The input

A pair of sentences becomes `[CLS] sentence A [SEP] sentence B [SEP]`. Each token's vector is the sum of three learned embeddings: token, segment (A or B) and position.

| Size | Layers | Width | Heads | Parameters |
|---|---|---|---|---|
| BERT-base | 12 | 768 | 12 | 110 million |
| BERT-large | 24 | 1,024 | 16 | 340 million |

##### Two training tasks

- **Masked language modelling:** predict the hidden tokens. The random and unchanged cases stop the model simply learning that [MASK] means "predict here".

- **Next sentence prediction:** half the time B really follows A, and half the time it's a random sentence. RoBERTa later removed this task, and found that results matched or slightly improved.

##### Heads for each task

| Task | Head | Reported result |
|---|---|---|
| **Classification** | A classifier on [CLS] | – |
| **Entailment** | The same, with both sentences as input | – |
| **NER** | A classifier on each word's first sub-token, with no CRF | 92.8 F1 on CoNLL-2003 with BERT-large. |
| **Question answering** | Start and end scores for each token | 93.2 test F1 on SQuAD v1.1, using an ensemble. |

**Entailment** asks whether one sentence follows from another: entailment, contradiction or neutral. SNLI has about 570,000 labelled pairs. **SQuAD** asks for an answer that's a span of the passage, so it can be found by choosing the best start and end positions.

##### BERT or GPT-style?

| | BERT | GPT-style |
|---|---|---|
| Attention | Both directions | Only earlier tokens |
| Trained to | Fill in masked tokens | Predict the next token |
| Best for | Understanding: labels, spans, embeddings | Generating text |

##### Variants

- **RoBERTa:** trained longer, on more data with bigger batches, with no next sentence task and with masks that change each time. It found BERT "was significantly undertrained".

- **DistilBERT:** distilled to be 40% smaller and 60% faster, keeping 97% of the performance on their benchmark.

#### The maths

$$ {E_i = E_{\text{token}} + E_{\text{segment}} + E_{\text{position}}}, \qquad {L = -\sum_{i \in \text{masked}} \log P(w_i \mid \text{context})}, \qquad {\text{span} = \arg\max_{j \ge i}\ S\cdot T_i + E\cdot T_j} $$

From Devlin et al. The loss form is the standard description of masked language modelling.

- **the input**: Three learned embeddings, added for each token.

- **the masking loss**: Cross-entropy, only on the positions chosen for masking.

- **the QA span**: Learned start and end vectors S and E score each output T. Choose the best pair, with the end not before the start.

## In practice

### In practice

#### In practice

- **Fine-tuning settings:** the paper suggests batch sizes of 16 or 32, learning rates from 2e-5 to 5e-5, and 2 to 4 epochs.

- **Align labels with sub-tokens:** for NER, label each word's first piece, and ignore the rest in the loss.

- **Handle long documents:** position embeddings stop at a fixed length, usually 512. Use overlapping windows, and combine the results.

- **BERT or an LLM?** With good labels and high volume, a fine-tuned encoder is usually cheaper and faster. With no labels, or a task that keeps changing, try an LLM first.

- **Start small:** try DistilBERT or BERT-base before anything larger, and compare against TF-IDF plus logistic regression.

### The answer that sounds right

#### "LLMs have made BERT obsolete"

It sounds right, as LLMs do more. But a fine-tuned encoder can be far cheaper and faster for one fixed task at high volume, and its behaviour is easier to measure. They also remain common for embeddings and re-ranking. Choose using your labels, volume and cost.

## Say it

### How is BERT trained, and how do you adapt it for classification, tagging and question answering?

#### The interviewer pushes further

Follow-up 1 of 3

Why replace some chosen tokens with random ones, or leave them unchanged?

If every target were [MASK], the model could rely on the [MASK] token to know where to predict, and pay less attention elsewhere. Mixing the cases means it must hold a good representation for every token. The random and unchanged cases are 10% each of the chosen tokens.

Follow-up 2 of 3

How does BERT answer a question from a passage?

The input is the question, [SEP], then the passage. Learned vectors score each token as a possible start and end. You choose the highest scoring pair where the end isn't before the start. So it can only answer with text that's in the passage.

Follow-up 3 of 3

Why can't BERT generate text the way GPT does?

It's trained with attention in both directions, so it never learned to predict from left context only. You could fill masks repeatedly, but it's slow and works poorly. GPT-style models are trained with a causal mask for exactly this.

#### The 30-second answer

BERT is a Transformer encoder pretrained by masking. It selects 15% of tokens, replaces 80% of those with [MASK], 10% with a random token and leaves 10% unchanged, and predicts the originals. It also originally predicted whether one sentence followed another, though RoBERTa showed this wasn't needed. Each token's input adds token, segment and position embeddings. To use it, I add a head and fine-tune at about 2e-5 to 5e-5, for 2 to 4 epochs: a classifier on [CLS] for classification and entailment, per-token for NER, and start and end scores for QA. It's bidirectional, so it suits understanding rather than generation.

**Key terms and sources**

Masked language modelling, CLS and SEP tokens, segment embeddings, next sentence prediction, task heads for classification, NER, QA and entailment, and later variants. · checked 7 Nov 2026

#### Sources

- [Devlin et al., BERT](https://arxiv.org/abs/1810.04805)

- [Liu et al., RoBERTa](https://arxiv.org/abs/1907.11692)

- [Sanh et al., DistilBERT](https://arxiv.org/abs/1910.01108)

- [Bowman et al., SNLI](https://arxiv.org/abs/1508.05326)

- [Rajpurkar et al., SQuAD](https://arxiv.org/abs/1606.05250)

- [Jurafsky and Martin, Speech and Language Processing](https://web.stanford.edu/~jurafsky/slp3/)

Explanations are ours, built from these sources. Lab numbers are illustrative, and worked examples were checked by calculation.
