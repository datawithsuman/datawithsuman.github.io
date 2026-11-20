# The Next-Token Objective

> How does one sentence become eight training examples?

- Track: Fundamentals › LLMs › Pretraining
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/next-token-prediction/
- Before this: N-gram Language Models and Perplexity (`fundamentals/n-gram-language-models`), The Transformer, End to End (`fundamentals/transformer-end-to-end`)
- Quiz topic: `pre`

## Intuition

### The situation

The team has a huge pile of raw text and almost no labels. A new hire asks where the training labels come from when you pre-train an LLM. The interviewer asks:

> How does one sentence become eight training examples?

Where this lesson sits: the causal mask inside attention, and the softmax over the vocabulary at the top of the stack.

Background: Encoder vs Decoder · Loss Functions.

**Running example:** one sentence from the assistant's training text, "your biryani will arrive in 20 minutes.", and the probability the model gives each true next token.

#### Learning from text with no labels

Labelled data is scarce; raw text is effectively unlimited. Next-token prediction turns every piece of text into its own labels: the "answer" at each position is simply the token that comes next. To predict well, a model has to pick up grammar, facts, reasoning patterns and style, which is why this one objective produces such general models.

### The idea

Think of reading with a card that covers everything after the current word. You guess the next word, slide the card along, and check. Every word becomes its own small test, so any text is full of them. The causal mask is the card.

[Figure: The sentence your biryani will arrive in 20 minutes. Each position sees the tokens so far and predicts the next token, the same sentence shifted by one, giving eight training examples.]

_Each position sees only the tokens so far. One forward pass gives all eight predictions._

### Play

**Try to break it.** Start with the trained model and find the most surprising token. Then try the confidently wrong model, and the one that memorised the sentence.

#### Per-token losses on one sentence

Illustrative probabilities for the true next token at each position (not from a real model). Loss = −ln p. Each chip shows the context it was predicted from.

The 8-token sentence gives **8** training examples from one forward pass. The average loss is **1.42** (perplexity 4.14). Function words after a clear context are easy ("in" 0.16, "minutes" 0.08), while content words that could have been many things are expensive: "biryani" costs **3.91** and "20" costs 2.81. Being **confidently wrong** on a single token (p = 0.01 for "minutes") adds 4.6 to that token and lifts the sentence's average to 1.99 (perplexity 7.29): cross-entropy punishes confident mistakes hard. A model that has **memorised** the sentence scores 0.01, which is why training loss alone says nothing about generalisation: always watch held-out loss, and deduplicate the data (next lesson).

**Now say why:** the memorising model scores almost zero, so why is it no good?

## Maths

### Maths

#### In one breath

Pre-training an LLM is one task repeated trillions of times: **predict the next token**. By the chain rule, the probability of a text is the product of each token's probability given the tokens before it, so the model is trained to minimise the average **cross-entropy** (−log p of the true next token) over every position. A **causal mask** stops each position from seeing the future, which means one forward pass over a 4,096-token sequence produces **4,096 training examples** at once. During training the model always conditions on the true previous tokens (**teacher forcing**); at generation time it conditions on its own outputs. The loss of a randomly initialised model starts near ln(vocabulary size), about 11.8 for a 128k vocabulary, and lower is better; exp(loss) is the perplexity. What you'll be able to do after this: write the pre-training loss, explain causal masking and teacher forcing, and read a loss curve.

#### Cross-entropy over every position

$$ \mathcal{L}(\theta) = {-\frac{1}{T}\sum_{t=1}^{T}}{\log p_\theta(x_t \mid }{x_{<t}}{)} $$

The same objective as an n-gram model, with a Transformer instead of a count table (Bengio et al. 2003; Radford et al. 2018).

- **average over positions**: Every position in every sequence is a training example; the loss is their mean.

- **−log probability**: The penalty is large when the model gave the true next token a small probability: −ln(0.5) = 0.69, −ln(0.01) = 4.6.

- **only the past**: The prediction may use tokens 1…t−1 and nothing after; the causal mask enforces this inside attention.

- **Causal mask:** attention scores to future positions are set to −∞ before the softmax, so the output at position t depends only on tokens ≤ t. All T predictions are computed in one parallel forward pass.

- **Teacher forcing:** during training, position t always sees the _true_ previous tokens, even if the model would have predicted something else.

- **Packing:** documents are concatenated with an end-of-text token and cut into fixed-length sequences, so no compute is wasted on padding.

## In practice

### In practice

#### Reading the loss in real training

- **Starting loss ≈ ln V:** a fresh model spreads probability evenly, so with Llama 3's 128,256-token vocabulary the first loss is about ln 128,256 ≈ 11.8. A much higher start means a bad initialisation of the output layer.

- **Exposure bias:** teacher forcing never shows the model its own mistakes, so errors can compound during generation (Bengio et al. 2015, scheduled sampling). In LLMs this is mostly addressed later, by post-training on the model's own outputs.

- **Loss is per token, so it depends on the tokeniser:** compare models with different tokenisers in bits per byte or per word, not per-token loss.

- Variants: **multi-token prediction** (DeepSeek-V3 predicts an extra future token as an auxiliary objective), and **fill-in-the-middle** for code models.

#### Compression as learning

Minimising next-token cross-entropy is the same as compressing the training text: every pattern the model learns, from spelling to arithmetic, lowers the number of bits needed to predict what comes next, and the causal mask lets every position of every document teach in parallel.

### The answer that sounds right

#### "Lower training loss means a better model"

It sounds right, since loss is what training minimises. But a model that has memorised the lab's sentence scores 0.01, and that says nothing about new text. Watch held-out loss, and deduplicate the data. Also note that the model doesn't generate during training: that's teacher forcing in parallel, and generation is sequential.

## Say it

### How does one sentence become eight training examples?

#### The interviewer pushes further

Follow-up 1 of 3

Why does a decoder-only model train efficiently?

Every token is a target, and the causal mask makes all of them computable in one pass; a masked-LM like BERT only trains on the ~15% masked tokens.

Follow-up 2 of 3

Your loss starts at 25 with a 50k vocabulary. What's wrong?

ln 50,000 ≈ 10.8, so the initial logits are far too large: the output layer is initialised too big (or a scaling factor is missing).

Follow-up 3 of 3

Do you compute loss on padding or on the prompt?

Not on padding (it's masked out). In pre-training all real tokens count; in SFT the loss is usually masked to the response tokens only.

#### The 30-second answer

LLMs are pre-trained with next-token prediction: by the chain rule a text's probability is the product of each token's probability given the previous tokens, so we minimise the average cross-entropy of the true next token across all positions. A causal mask blocks attention to future tokens, so one forward pass over a sequence gives a prediction and a loss at every position in parallel. Training uses teacher forcing, always feeding the true previous tokens, which can cause exposure bias at generation time. Documents are packed into fixed-length sequences with end-of-text separators. The loss starts near the log of the vocabulary size, and exp of the held-out loss is perplexity.

**Go further**

#### What not to say

- "The model generates during training." Training is parallel with teacher forcing; generation is sequential.

- "Lower training loss means a better model." Use held-out loss, and watch for memorisation.

**Key terms and sources**

How LLMs are pre-trained: the autoregressive factorisation, cross-entropy on every position, the causal mask that makes one forward pass produce N training examples, teacher forcing and exposure bias, sequence packing, what the loss value means, and why such a simple objective teaches so much · built from Bengio et al. (2003), Radford et al. (GPT, 2018; GPT-2, 2019), Brown et al. (GPT-3, 2020), Vaswani et al. (2017), Bengio et al. (scheduled sampling, 2015) and Jurafsky & Martin (SLP3) · checked 29 Oct 2026

#### Sources

1. Y. Bengio, R. Ducharme, P. Vincent & C. Jauvin, "A Neural Probabilistic Language Model", _JMLR_ 3, 2003.

2. A. Radford et al., "Improving Language Understanding by Generative Pre-Training" (GPT), OpenAI 2018; "Language Models are Unsupervised Multitask Learners" (GPT-2), OpenAI 2019.

3. T. Brown et al., "Language Models are Few-Shot Learners" (GPT-3), NeurIPS 2020, [arXiv:2005.14165](https://arxiv.org/abs/2005.14165).

4. S. Bengio et al., "Scheduled Sampling for Sequence Prediction with Recurrent Neural Networks", NeurIPS 2015, [arXiv:1506.03099](https://arxiv.org/abs/1506.03099).

5. DeepSeek-AI, "DeepSeek-V3 Technical Report", 2024, [arXiv:2412.19437](https://arxiv.org/abs/2412.19437) (multi-token prediction).
