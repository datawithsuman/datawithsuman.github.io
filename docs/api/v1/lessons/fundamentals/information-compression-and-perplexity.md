# Information, Compression and Perplexity

> What does entropy have to do with compression, and what does perplexity tell you about a model?

- Track: Fundamentals › Maths for ML › Information theory
- Type: Concept · 15 min
- Page: https://aimlrounds.com/tracks/fundamentals/information-compression-and-perplexity/
- Before this: Entropy, Cross-Entropy & KL Divergence (`fundamentals/entropy-cross-entropy-kl`)
- Related: N-gram Language Models and Perplexity (`fundamentals/n-gram-language-models`)
- Quiz topic: `info`

## Intuition

### The situation

Your language model's validation loss is 3.1, and a teammate says a second model's perplexity of 18 means it's worse. They use different tokenisers. Another asks what cross-entropy even measures, beyond being the loss you minimise. The interviewer asks:

> What does entropy have to do with compression, and what does perplexity tell you about a model?

#### Why it matters

This is what gives cross-entropy its meaning, beyond being a formula, and it explains why perplexity is a sensible way to evaluate language models. It builds on entropy, cross-entropy and KL.

### The idea

Think of Morse code. E is the most common letter, so it gets a single dot, while rare letters get long patterns. That saves time overall. If you designed Morse for the wrong language, you'd waste time on every message. That waste is exactly what a poor model costs.

[Figure: Three quantities. Entropy is the best possible cost. Cross-entropy is the cost with your model. KL divergence is the waste between them.]

_Cross-entropy equals entropy plus KL divergence._

### Play

**Try to break it.** Raise what the model knows to 100%. Then make all four weights equal.

#### Build a code for four tokens

Illustrative. The model's belief is a blend of the truth and a uniform guess, where 0% is a uniform guess and 100% is the truth. The best real code is a Huffman code, which has whole-number lengths.

Raise what the model knows to **100%**. Wasted bits fall to zero, and its perplexity matches the truth. Now make the four weights **equal**. Entropy reaches its maximum of 2 bits, and perplexity reaches 4: when nothing stands out, there's nothing to exploit.

**Now say why:** why can't a wrong model ever beat the entropy?

## Maths

### Maths

#### In one breath

**Entropy** is the fewest bits per symbol any code can use on average, if you know the true distribution. Common symbols get short codes. If you design the code using the **wrong distribution**, the average cost is the **cross-entropy**, and the extra is KL divergence. So minimising cross-entropy means learning to predict well enough to compress. **Perplexity** turns this into a count: a perplexity of 10 means the model is as uncertain as choosing among 10 equally likely options.

#### Prediction is compression

##### Short codes for common things

Say four tokens appear with chances 1/2, 1/4, 1/8 and 1/8. Giving each 2 bits costs 2 bits per token. A better code gives them 0, 10, 110 and 111, which costs 1.75 bits on average, exactly the entropy. An event of probability p ideally gets −log₂ p bits, so rare events take longer to describe.

##### The cost of a wrong model

- **Entropy, H(p):** the best possible average cost, with a code built for the truth.

- **Cross-entropy, H(p, q):** the average cost if you build the code for q, while data comes from p.

- **KL divergence:** the difference, or the wasted bits. It's never negative, so no wrong model beats the truth.

A better predictor really can compress better, and that's a fair way to think about what training does.

##### Bits or nats?

It's only a matter of units. Base 2 gives bits, and the natural log gives nats, with 1 nat ≈ 1.44 bits. Frameworks use natural logs, so a cross-entropy loss of 0.69 at the start of a balanced binary problem is the same as 1 bit: the model knows nothing yet. That's a useful check.

##### Perplexity

Perplexity is the exponential of the average negative log-likelihood per token, on held-out text. You can read it as an effective number of choices.

- **Lower is better,** and 1 would be perfect.

- **Compare carefully:** values depend on the tokeniser, so a model using different tokens isn't directly comparable. Compare per word, or use the same tokeniser.

- **It isn't quality:** low perplexity means predicting text well, not being helpful or truthful. See benchmarks for other evaluations.

##### Why the uniform has the most entropy

With nothing else known, the uniform distribution makes the fewest assumptions. This idea, **maximum entropy**, also says the Gaussian has the highest entropy for a given mean and variance, and it's one way to justify softmax.

#### The maths

$$ H(p) = -\sum_x p(x)\log_2 p(x), \qquad H(p, q) = H(p) + D_{KL}(p \| q), \qquad \text{Perplexity} = \exp\!\Big(-\frac{1}{N}\sum_{i=1}^N \ln q(x_i)\Big) $$

Worked example: an average loss of 2.3026 nats per token gives a perplexity of e^2.3026 ≈ 10. That’s as uncertain as choosing among 10 equally likely tokens.

- **entropy**: The average bits needed with the best code. Each symbol costs −log p, weighted by how often it appears.

- **cross-entropy**: The average bits using a code built for q. This is the classification loss.

- **KL divergence**: The extra cost of using q instead of p. It’s zero only when they match.

- **perplexity**: The exponential of the average per-token loss, turning it into an effective number of choices.

## In practice

### In practice

#### In practice

- **Sanity-check your first loss:** a classifier with k balanced classes should start near ln k. If it starts far away, something's wrong with your setup.

- **Compare per token, with care:** report the tokeniser with any perplexity, and use the same held-out data.

- **Overconfidence:** log loss punishes confident mistakes heavily. One token given a chance near zero can dominate an average.

- **Real compressors:** arithmetic coding gets close to the entropy limit, and good models can power strong text compressors.

- **Temperature:** sampling temperature changes a distribution's entropy, which affects how varied the output is.

### The answer that sounds right

#### "Lower perplexity means the better model"

It sounds right, as lower loss is usually better. But perplexity is per token, so a different tokeniser changes the number, with no change in skill. And it only measures how well text is predicted, not whether answers are helpful or true. Compare on the same tokens, and evaluate the actual task as well.

## Say it

### What does entropy have to do with compression, and what does perplexity tell you about a model?

#### The interviewer pushes further

Follow-up 1 of 3

What initial loss should you expect with 10 balanced classes?

About ln 10 ≈ 2.30 nats, as a model that knows nothing gives each class a chance of 0.1. If your first loss is far from this, check your labels, your outputs or your initialisation. It's one of the quickest debugging checks in deep learning.

Follow-up 2 of 3

Why can't you compare perplexity between models with different tokenisers?

Perplexity is per token. A tokeniser with larger tokens has fewer, harder predictions, so per-token numbers aren't comparable. You can compare per character or word, or evaluate both models on the same tokens. Also, make sure the same held-out data is used.

Follow-up 3 of 3

Does lower perplexity mean a better chatbot?

Not necessarily. It measures how well a model predicts text like its test set. A model can have low perplexity and still be unhelpful or wrong. Chat quality needs other evaluation, and it's why post-training often changes usefulness more than it changes perplexity.

Entropy is the fewest bits per symbol any code can use on average, if you know the true distribution, because likely symbols get short codes. If you build the code using the wrong distribution, the average cost is the cross-entropy, and the extra cost is KL divergence. So minimising cross-entropy means learning to predict well. Perplexity is the exponential of the average per-token loss, or an effective number of choices. Lower's better, but it depends on the tokeniser, and it measures prediction rather than quality.

**Key terms and sources**

Why entropy is the limit of compression, why cross-entropy is the cost of a wrong model, the difference between bits and nats, and how to read perplexity.

#### Sources

- MacKay, Information Theory, Inference and Learning Algorithms, contents

- Murphy, Probabilistic Machine Learning: An Introduction, chapter 6

- Shannon, A Mathematical Theory of Communication (1948)

- N-gram language models on this site

Explanations are ours, built from these sources. Lab numbers are illustrative, and worked examples were checked by calculation.
