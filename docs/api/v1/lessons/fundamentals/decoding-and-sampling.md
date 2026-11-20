# Decoding: Temperature, Top-k, Top-p and Min-p

> Why does top-p fall apart at high temperature, and is min-p really better?

- Track: Fundamentals › LLMs › Generation
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/decoding-and-sampling/
- Before this: The Next-Token Objective (`fundamentals/next-token-prediction`)
- Quiz topic: `llmgen`

## Intuition

### The situation

The assistant is writing "Your biryani will arrive in …", and the next token should be a number of minutes, not "purple". A colleague turns the temperature up to 2 for livelier replies, with top-p at 0.9, and the text derails. The interviewer asks:

> Why does top-p fall apart at high temperature, and is min-p really better?

**Running example (generation):** the assistant is writing "Your biryani will arrive in …". The next token should be a number of minutes, not "purple".

#### The most likely text is not the best text

Maximising probability sounds right, but Holtzman et al. (2020) showed that greedy and beam search on open-ended text produce bland, repetitive output that loops ("I don't know. I don't know. …"), while human text is full of individually less likely words. Pure sampling from the full distribution has the opposite problem: once in a while it picks a token from the huge unreliable tail, and the text derails.

### The idea

Think of choosing from a huge menu. Temperature is how adventurous you feel. Top-p says to keep the dishes that make up 90% of orders, and if tastes are flat, that's most of the menu. Min-p says to keep dishes at least a tenth as popular as the favourite, so the cut moves with how clear the favourite is.

[Figure: At temperature 1, top-p keeps 131 tokens with 1.5 percent junk, and min-p keeps 5 with no junk. At temperature 2, top-p keeps 887 tokens with 79.7 percent junk, and min-p keeps 9 with no junk.]

_From the lab: nine sensible tokens plus 1,000 junk tokens._

### Play

**Try to break it.** Set the temperature to 1, and switch between no truncation, greedy, top-k, top-p and min-p. Then raise it to 2 and repeat.

#### "Your biryani will arrive in …"

Illustrative logits: nine sensible continuations ("30" 4.0, "20" 3.6, "25" 3.1, "40" 2.6, "15" 1.9, "45" 1.2, "an" 0.9, "about" 0.7, "two" 0.2) plus 1,000 junk tokens at logit −4 each, standing in for a real vocabulary's long tail.

At **T = 1** with no truncation, each junk token is negligible but together they hold **11.4%** of the probability: roughly one token in nine would derail the sentence. **Top-p 0.9** keeps 131 tokens, including 122 junk ones (**1.5%** chance); **top-k 5** and **min-p 0.1** keep only the five best. Turn the temperature up to **2** for more varied replies: the tail now holds 81.7%, top-p needs **887** tokens to reach 90% and samples junk **79.7%** of the time, while **min-p** keeps just 9 sensible tokens and no junk, because its cut-off moves with the top token. That's the idea behind min-p: usable variety at high temperature, though see the caution below. Lowering T to 0.5 sharpens "30" to 58.9%.

**Now say why:** each junk token is negligible, so how does the tail derail the sentence?

## Maths

### Maths

#### In one breath

The model outputs a probability for every token in its vocabulary; **decoding** decides which one to emit. **Greedy** always takes the top token (deterministic, but prone to repetitive loops); **beam search** keeps the few best partial sequences (good for translation, bland for open-ended text). **Sampling** picks at random in proportion to the probabilities, and **temperature** T reshapes them first: T < 1 sharpens, T > 1 flattens. Because the vocabulary has 100k+ tokens, the long **tail** of individually unlikely tokens adds up, so samplers truncate it: **top-k** keeps the k best, **top-p** keeps the smallest set covering p of the probability, and **min-p** keeps tokens at least a fraction of the top token's probability. At high temperature top-p can let junk back in, and min-p's cut-off tightens instead, though a later critique found little evidence that this gives better text overall. What you'll be able to do after this: explain each decoding method, pick settings per task, and explain why min-p holds up at high temperature.

#### Temperature and truncation

$$ p_i = {\frac{\exp({z_i}/{T})}{\sum_j \exp(z_j/T)}} $$

- **logits**: The raw scores the model outputs for each token.

- **temperature**: Divide every logit by T. T → 0 becomes greedy; T = 1 is the model’s own distribution; T > 1 flattens it so unlikely tokens get more probability.

- **softmax**: Turn the scaled scores into probabilities, then truncate and renormalise before sampling.

- **Top-k** (Fan et al. 2018): keep the k most likely tokens. Simple, but k is fixed whether the model is sure (1 sensible option) or unsure (hundreds).

- **Top-p / nucleus** (Holtzman et al. 2020): keep the smallest set whose probabilities sum to p (e.g. 0.9). Adapts to the shape, but when the distribution is flat the "nucleus" can contain many tail tokens.

- **Min-p** (Nguyen et al. 2025): keep tokens with probability ≥ pbase × (top token's probability), e.g. 0.1×. The cut-off scales with the model's confidence.

## In practice

### In practice

#### Choosing settings

| Task | Typical setting | Why |
|---|---|---|
| Extraction, classification, JSON, code fixes | T = 0 (greedy) or low | one right answer; reproducibility |
| Chat assistants | T ≈ 0.6–1.0, top-p 0.9–0.95 | natural variety without derailing |
| Creative writing, brainstorming | moderate to higher T, with top-p or min-p ≈ 0.05–0.1 | diversity while cutting the tail |
| Self-consistency / best-of-N | T ≈ 0.7–1.0 | samples must differ to be worth voting over |
| Translation, summarisation (older seq2seq) | beam search, width 4–5 | output is tightly constrained by the input |

- Add a **repetition / frequency penalty** to discourage loops; use **stop sequences** and max tokens to end cleanly.

- **Constrained decoding** masks tokens that would break a grammar (e.g. a JSON schema) so the output always parses.

- T = 0 is not always perfectly deterministic in serving: batching and floating-point non-associativity can change ties.

**Don't overclaim min-p.** The lab's maths is right: min-p's cut-off moves with the top token, so junk stays out at high temperature. But Schaeffer et al. (2025) re-analysed the original paper. They report that its human evaluation left out data and that min-p was largely indistinguishable from other samplers, and that on benchmarks it had no clear edge once every sampler got the same amount of tuning. They allow a weak benefit at high temperature, where quality is lower anyway. They also quote a later study by the original authors, which found no apparent advantage over basic or top-p sampling. Treat min-p as a reasonable option, not as a proven upgrade.

#### Reshape, then cut the tail

Temperature controls how adventurous sampling is, and truncation removes the thousands of individually rare tokens whose combined probability would otherwise derail the text; min-p's confidence-relative cut-off removes junk reliably at high temperature, though that hasn't been shown to give better text at normal settings.

### The answer that sounds right

#### "Top-p always cuts out bad tokens"

It sounds right, since cutting the tail is its job. But on a flat distribution the nucleus can be huge. At T = 2 in the lab, top-p needs 887 tokens to reach 90%, and samples junk 79.7% of the time. Higher temperature doesn't make the model smarter or more creative either: it only flattens the distribution.

## Say it

### Why does top-p fall apart at high temperature, and is min-p really better?

#### The interviewer pushes further

Follow-up 1 of 3

What does temperature 0 mean?

The limit is greedy decoding (argmax); implementations special-case it because dividing by zero is undefined.

Follow-up 2 of 3

Why does beam search produce repetitive text?

It maximises sequence likelihood, and repeated phrases become self-reinforcing high-probability paths; human text is not the most likely text.

Follow-up 3 of 3

Should you set both temperature and top-p?

You can (truncation is applied after temperature), but tune one at a time; OpenAI's API docs recommend altering one or the other.

#### The 30-second answer

Decoding turns the next-token distribution into text. Greedy and beam search pick high-probability sequences but give repetitive, bland text for open-ended generation. Sampling adds variety, with temperature dividing the logits to sharpen or flatten the distribution. Because the vocabulary is huge, the long tail of unlikely tokens adds up, so we truncate: top-k keeps a fixed number, top-p keeps the smallest set covering, say, 90 percent of the probability, and min-p keeps tokens above a fraction of the top token's probability, so junk stays out at high temperature, though later analysis found little evidence that it gives better text overall. I use near-zero temperature for extraction and code, moderate temperature with top-p for chat, and I'd test any sampler on my own task before trusting a claim about it.

**Go further**

#### What not to say

- "Higher temperature makes the model smarter or more creative." It only flattens the distribution.

- "Top-p always cuts out bad tokens." On flat distributions the nucleus can be huge.

**Key terms and sources**

How an LLM turns next-token probabilities into text: greedy decoding and beam search, why they produce repetitive text, sampling with temperature, and the truncation rules (top-k, nucleus/top-p, min-p) that cut off the long tail of junk tokens · built from Holtzman et al. (The Curious Case of Neural Text Degeneration, ICLR 2020), Fan et al. (top-k, 2018), Nguyen et al. (min-p, ICLR 2025), Ackley et al. (temperature, 1985), and the Hugging Face generation docs · checked 29 Oct 2026

#### Sources

1. A. Holtzman et al., "The Curious Case of Neural Text Degeneration", ICLR 2020, [arXiv:1904.09751](https://arxiv.org/abs/1904.09751).

2. A. Fan, M. Lewis & Y. Dauphin, "Hierarchical Neural Story Generation", ACL 2018, [arXiv:1805.04833](https://arxiv.org/abs/1805.04833).

3. M. Nguyen et al., "Turning Up the Heat: Min-p Sampling for Creative and Coherent LLM Outputs", ICLR 2025, [arXiv:2407.01082](https://arxiv.org/abs/2407.01082).

4. R. Schaeffer, J. Kazdan & Y. Denisov-Blanch, "Min-p, Max Exaggeration: A Critical Analysis of Min-p Sampling in Language Models", 2025, [arXiv:2506.13681](https://arxiv.org/abs/2506.13681).

5. D. Ackley, G. Hinton & T. Sejnowski, "A Learning Algorithm for Boltzmann Machines", Cognitive Science, 1985.

6. R. Schaeffer, J. Kazdan & Y. Denisov-Blanch, "Min-p, Max Exaggeration: A Critical Analysis of Min-p Sampling in Language Models", 2025, [arXiv:2506.13681](https://arxiv.org/abs/2506.13681).

7. D. Ackley, G. Hinton & T. Sejnowski, "A Learning Algorithm for Boltzmann Machines", Cognitive Science, 1985.

8. R. Schaeffer, J. Kazdan & Y. Denisov-Blanch, "Min-p, Max Exaggeration: A Critical Analysis of Min-p Sampling in Language Models", 2025, [arXiv:2506.13681](https://arxiv.org/abs/2506.13681).

9. D. Ackley, G. Hinton & T. Sejnowski, "A Learning Algorithm for Boltzmann Machines", Cognitive Science, 1985.

10. Hugging Face, "Generation strategies" (Transformers documentation); OpenAI API reference (temperature, top_p).
