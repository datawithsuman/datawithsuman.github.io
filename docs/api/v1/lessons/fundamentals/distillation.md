# Distillation: How Small Models Learn from Big Ones

> Why did distilling R1 beat RL on the same 32B model?

- Track: Fundamentals › LLMs › Post-training
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/distillation/
- Before this: SFT and Instruction Tuning (`fundamentals/supervised-fine-tuning`)
- Quiz topic: `post`
- Sources checked: 2026-10-29 · Text last changed: 2026-11-20 · Version: 966e26aa06

## Intuition

### The situation

The post-trained 70B assistant is excellent but too expensive to serve to millions. The team wants a 3B model that behaves almost as well. Trained on the same data and labels, a 3B model ends up much weaker. The interviewer asks:

> Why did distilling R1 beat RL on the same 32B model?

**Running example:** the post-trained 70B assistant is excellent but too expensive to serve to millions of customers. The team wants a 3B model that runs cheaply, even on-device, and behaves almost as well.

#### Small models trained from scratch learn less

A 3B model trained on the same data and labels as a 70B model ends up much weaker. Training labels are one-hot: "the next token is _delicious_", full stop. The big model has learned a much richer picture of which alternatives are plausible; if the small model could learn from that picture, every training example would carry more signal.

### The idea

Think of the difference between an answer key and a teacher's notes. The key says "delicious", full stop. The teacher says delicious is likely, tasty is nearly as good, cold is possible and purple is absurd. Each example teaches the student far more.

[Figure: After the biryani was. The one-hot label puts everything on delicious. The teacher gives delicious 65 percent, tasty 29 percent, cold 3.6 percent, late 1.8 percent and purple almost nothing.]

_The next token after "the biryani was", from the lab's illustrative teacher at T = 1._

### Play

**Try to break it.** Move the temperature from 1 to 4, then to 8. Watch "tasty" against "purple", and the share on other tokens.

#### What the teacher knows beyond its top answer

Illustrative teacher logits for the next token after "the biryani was": delicious 6.0, tasty 5.2, cold 3.1, late 2.4, purple −2.0 (a real teacher spreads probability over a 100k+ vocabulary).

A one-hot label says only "delicious". The teacher at **T = 1** also puts **34.7%** on other words, and its numbers say "tasty" is a near-synonym, "cold" and "late" are plausible (complaints), and "purple" is **1,339×** less likely than "tasty". At **T = 4** the distribution is flatter (entropy 2.09 bits instead of 1.20) and the relationships among the small probabilities become a strong training signal. Too high a temperature washes out the ranking (at T = 8, 72.3% of the mass is spread away from the top token), which is why T is tuned, typically 1–4 for LLMs, often just 1.

**Now say why:** if a higher temperature exposes more, why is T usually kept between 1 and 4?

## Maths

### Maths

#### In one breath

A large **teacher** model knows more than its top answer: when it says "delicious", it also believes "tasty" is nearly as good and "purple" is absurd. **Knowledge distillation** trains a small **student** to match the teacher's whole probability distribution (**soft targets**), not just the correct token, which carries far more information per example. A **temperature** T > 1 softens the distribution so this "dark knowledge" is visible. For LLMs there are three main forms: **logit distillation** (match the teacher's next-token distribution at every position; Gemma 2 and Llama 3.2 1B/3B), **sequence-level distillation** (just fine-tune on text the teacher generates; DeepSeek's R1-Distill models, trained on about 800k R1 samples), and **on-policy distillation** (the student writes, the teacher grades each token). Distilling R1 into Qwen2.5-32B reached 72.6% on AIME 2024, versus 47.0% for running large-scale RL on the same 32B model directly. What you'll be able to do after this: explain soft targets and temperature, compare the three kinds of LLM distillation, and say when to distil instead of training directly.

#### Soft targets and temperature

$$ \mathcal{L}_{KD} = \alpha\,{T^2}\;{\mathrm{KL}\Big(\mathrm{softmax}\big(\tfrac{z_{teacher}}{{T}}\big)\,\Big\|\,\mathrm{softmax}\big(\tfrac{z_{student}}{{T}}\big)\Big)} + (1-\alpha)\,{\mathcal{L}_{CE}} $$

Hinton, Vinyals & Dean, "Distilling the Knowledge in a Neural Network", 2015, [arXiv:1503.02531](https://arxiv.org/abs/1503.02531). DistilBERT (Sanh et al. 2019) used it to make a BERT 40% smaller and 60% faster that kept 97% of its language-understanding performance.

- **temperature**: Divide the teacher’s logits by T before the softmax. T = 1 is the normal distribution; larger T flattens it so small probabilities become visible.

- **match the teacher**: KL divergence between the teacher’s and the student’s softened distributions: the student is penalised for every token where its beliefs differ, not only the top one.

- **T² scaling**: Softening shrinks the gradients by about 1/T², so the term is multiplied by T² to keep it comparable to the normal loss.

- **usual hard-label loss**: Optionally mixed in with weight 1 − α.

## In practice

### In practice

#### Three ways to distil an LLM

| Kind | What the student trains on | Examples |
|---|---|---|
| **Logit (token-level)** | the teacher's full next-token distribution at every position (needs the teacher's logits and the same tokeniser) | Gemma 2 2B/9B pre-trained with distillation; Llama 3.2 1B/3B used Llama 3.1 8B/70B logits as targets |
| **Sequence-level** | ordinary SFT on text the teacher generated (Kim & Rush 2016); works across tokenisers and through APIs | DeepSeek-R1-Distill (Qwen, Llama; 1.5B–70B) fine-tuned on ~800k R1-generated samples |
| **On-policy** | the student generates; the teacher scores its tokens (e.g. reverse KL), fixing the mismatch between training on teacher text and generating its own | GKD (Agarwal et al. 2024), MiniLLM (Gu et al. 2024) |

- **Distil or train directly?** DeepSeek ran large-scale RL directly on Qwen2.5-32B and got 47.0% on AIME 2024; distilling R1 into the same base gave **72.6%**, for far less compute. Their conclusion: distil to small models; large-scale RL needs a strong base model.

- **Limits:** a student rarely exceeds its teacher; it inherits the teacher's errors and biases; and many commercial model licences forbid using outputs to train competing models.

#### Teach with distributions, not just answers

A teacher's full probability distribution, or its generated text, carries much more information per example than ground-truth labels, so a small student learns faster and better from the teacher than from the raw data alone.

### The answer that sounds right

#### "Distillation just means fine-tuning on teacher outputs"

It sounds right, since that's how DeepSeek's R1-Distill models were made. But that's only one form, called sequence-level. Logit distillation matches the teacher's full distribution at every position, and needs the same tokeniser. On-policy distillation has the student generate and the teacher score. A student also rarely exceeds its teacher, and it inherits the teacher's errors.

## Say it

### Why did distilling R1 beat RL on the same 32B model?

#### The interviewer pushes further

Follow-up 1 of 3

Why multiply the soft loss by T²?

Gradients of the softened KL scale roughly as 1/T², so multiplying by T² keeps the soft and hard loss terms balanced when T changes.

Follow-up 2 of 3

Logit distillation from a model with a different tokeniser?

Not directly: distributions are over different vocabularies. Use sequence-level distillation, or cross-tokeniser alignment methods.

Follow-up 3 of 3

Forward or reverse KL for generative students?

Forward KL makes the student cover all the teacher's modes (it may spread probability too thinly); reverse KL makes it focus on the teacher's main modes, which MiniLLM found better for generation.

#### The 30-second answer

Knowledge distillation trains a small student to imitate a large teacher. In Hinton's version the student matches the teacher's softened output distribution, using a temperature to expose the relative probabilities of wrong answers, with a KL loss scaled by T squared, often mixed with the normal label loss. For LLMs you can match next-token logits at every position, as Gemma 2 and Llama 3.2 did; fine-tune on teacher-generated text, as DeepSeek did for its R1-Distill models; or do on-policy distillation where the student samples and the teacher scores each token. Distilling R1 into a 32B model beat running RL on that model directly, 72.6 versus 47 percent on AIME.

**Go further**

#### What not to say

- "Distillation just means fine-tuning on teacher outputs." That's one form; logit and on-policy distillation are others.

- "The student can't learn anything the labels don't contain." The teacher's distribution carries information the labels don't.

**Key terms and sources**

Knowledge distillation from Hinton's soft targets to today's LLM practice: temperature and "dark knowledge", logit (token-level) distillation as used for Gemma 2 and Llama 3.2, sequence-level distillation on teacher outputs as used for the DeepSeek-R1 distilled models, on-policy distillation, and when distillation beats training the small model directly · built from Hinton, Vinyals & Dean (2015), Kim & Rush (2016), Sanh et al. (DistilBERT, 2019), Agarwal et al. (GKD, ICLR 2024), Gu et al. (MiniLLM, ICLR 2024), Gemma Team (Gemma 2, 2024), Meta (Llama 3.2, 2024) and DeepSeek-AI (DeepSeek-R1, 2025) · checked 29 Oct 2026

#### Sources

1. G. Hinton, O. Vinyals & J. Dean, "Distilling the Knowledge in a Neural Network", 2015, [arXiv:1503.02531](https://arxiv.org/abs/1503.02531); Y. Kim & A. Rush, "Sequence-Level Knowledge Distillation", EMNLP 2016, [arXiv:1606.07947](https://arxiv.org/abs/1606.07947).

2. V. Sanh et al., "DistilBERT", 2019, [arXiv:1910.01108](https://arxiv.org/abs/1910.01108).

3. R. Agarwal et al., "On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes" (GKD), ICLR 2024, [arXiv:2306.13649](https://arxiv.org/abs/2306.13649); Y. Gu et al., "MiniLLM", ICLR 2024, [arXiv:2306.08543](https://arxiv.org/abs/2306.08543).

4. Gemma Team, "Gemma 2: Improving Open Language Models at a Practical Size", 2024, [arXiv:2408.00118](https://arxiv.org/abs/2408.00118); Meta, "Llama 3.2: Revolutionizing edge AI and vision with open, customizable models", 2024 (blog).

5. DeepSeek-AI, "DeepSeek-R1", 2025, [arXiv:2501.12948](https://arxiv.org/abs/2501.12948) (§2.4 and §4.1, distillation vs RL).
