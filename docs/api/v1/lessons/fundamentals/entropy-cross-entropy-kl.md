# Entropy, Cross-Entropy & KL Divergence

> Why every classifier is trained on cross-entropy, and what KL adds.

- Track: Fundamentals › Maths for ML › Information theory
- Type: Concept · 25 min
- Page: https://aimlrounds.com/tracks/fundamentals/entropy-cross-entropy-kl/
- Before this: Common Probability Distributions (`fundamentals/probability-distributions`), Maximum Likelihood & MAP (`fundamentals/mle-and-map`)
- Related: Softmax Regression (`fundamentals/softmax-regression`)
- Quiz topic: `info`

## Intuition

### The situation

Two models have the same accuracy, but one says 99% on its top guess and the other says 51%. You need a score that tells them apart. The interviewer asks:

> How are entropy, cross-entropy and KL divergence related?

**Running example:** the food-delivery app predicts which of 4 cuisines a customer will order next: North Indian, Chinese, Pizza or Biryani. The customer's true habits are a distribution p (e.g. 50%, 25%, 15%, 10%); the model predicts a distribution q. How good is q, in bits?

#### Measuring how wrong a probability is

Accuracy only checks the top guess. A model that says "North Indian 51%" and one that says "North Indian 99%" are equally accurate when the customer orders North Indian, but very different when they don't. We need a score for whole probability distributions that rewards confident correct predictions and punishes confident wrong ones. Information theory gives it, and it's the loss behind almost every classifier and language model.

### The idea

Think of surprise as a cost. Entropy is the surprise you can't avoid, even with perfect knowledge. Cross-entropy is the surprise you get when you bet using your model. KL divergence is the difference: the extra price of being wrong.

[Figure: A bar showing cross-entropy of 3.77 bits as entropy of 1.74 bits plus KL divergence of 2.03 bits.]

_From the lesson's lab, for the confident and wrong prediction._

### Play

**Try to break it.** Move the model's prediction from close, to uniform, to confident and wrong. Watch the KL and compare its two directions.

#### Move the model's distribution, watch the bits

Teal bars: p. Orange bars: q. All values in bits (log base 2).

The "close" prediction costs only about 0.03 extra bits. "Uniform" costs about 0.26 bits: it knows nothing, but never bets heavily against reality. "Confident and wrong" costs 2.03 extra bits (cross-entropy 3.77 bits), more than the entropy itself, because it put 5% on the customer's favourite cuisine. Notice KL(p ‖ q) ≠ KL(q ‖ p): for the confident-wrong case they differ (2.03 vs 2.06 bits), and dragging Biryani in p to 0 makes KL(q ‖ p) infinite while KL(p ‖ q) stays small (0.15 bits for "close").

**Now say why:** why does uniform cost less than confident and wrong, and why do the two KL directions differ?

## Maths

### Maths

#### In one breath

The **surprise** of an outcome with probability p is −log p: rare events are surprising. **Entropy** H(p) is the average surprise, a measure of uncertainty (bits with log₂). **Cross-entropy** H(p, q) is the average surprise when reality follows p but you predicted q; it's always ≥ H(p), and with a one-hot true label it is exactly the **log loss** used to train classifiers and language models. The gap is the **KL divergence**, KL(p ‖ q) = H(p, q) − H(p) ≥ 0: the extra cost of using the wrong distribution. KL is **asymmetric**, which matters: it's the penalty in knowledge distillation, the regulariser in VAEs, and the leash that keeps an RLHF-tuned model close to its starting point. What you'll be able to do after this: compute entropy, cross-entropy and KL for small distributions, explain why cross-entropy is the classification loss, and explain KL's asymmetry and its uses.

#### Surprise and entropy

$$ {I(x) = -\log_2 p(x)}, \qquad {H(p) = -\textstyle\sum_x p(x)\log_2 p(x)} $$

Shannon, "A mathematical theory of communication", 1948; Cover & Thomas ch. 2. Entropy is also the minimum average number of bits per symbol for a lossless code. For p = (0.5, 0.25, 0.15, 0.1), H ≈ 1.74 bits (a uniform choice of 4 would be 2 bits).

- **surprise of one outcome**: −log₂ p(x) bits. A sure thing (p = 1) carries 0 bits; a 1-in-8 event carries 3 bits.

- **entropy**: Average surprise when outcomes follow p. 0 when one outcome is certain; maximal (log₂ K bits) when all K are equally likely.

#### Cross-entropy and KL divergence

$$ {H(p,q) = -\textstyle\sum_x p(x)\log q(x)}, \quad {\mathrm{KL}(p\,\Vert\,q) = \textstyle\sum_x p(x)\log\tfrac{p(x)}{q(x)}}, \quad {H(p,q) = H(p) + \mathrm{KL}(p\,\Vert\,q)} $$

Goodfellow et al. §3.13; Cover & Thomas §2.3. Minimising cross-entropy over the training labels is maximum likelihood (MLE & MAP).

- **cross-entropy**: Average surprise when reality follows p but you score with q. With a one-hot p (the actual cuisine), it is −log q(actual): the log loss.

- **KL divergence**: Extra bits paid for using q instead of p. Always ≥ 0, and 0 only if q = p (Gibbs’ inequality).

- **the decomposition**: Cross-entropy = irreducible uncertainty H(p) + model’s mistake KL(p‖q). Training can only shrink the KL part.

#### Forward vs reverse KL

- **KL(p ‖ q)** ("forward", what cross-entropy training minimises) is huge wherever p has mass and q doesn't, so q is pushed to **cover** everything p does: mass-covering, sometimes spreading too thin.

- **KL(q ‖ p)** ("reverse", used in variational inference) is huge wherever q has mass and p doesn't, so q prefers to **sit inside** one mode of p and ignore others: mode-seeking.

- KL isn't a distance (not symmetric, no triangle inequality). The Jensen–Shannon divergence is a symmetric alternative.

#### Bits, nats and where to go next

Entropy in base 2 is measured in **bits**, and with the natural log in **nats**, where 1 nat ≈ 1.44 bits. Frameworks use natural logs, so a binary classifier that knows nothing starts near 0.69, which is ln 2, or exactly 1 bit.

Next: compression and perplexity shows what these numbers mean in practice, mutual information applies entropy to pairs of variables, and comparing distributions covers forward and reverse KL alongside other measures.

## In practice

### In practice

#### KL and cross-entropy across ML

- **Classification and language modelling:** the loss is cross-entropy with the one-hot label; for an LLM, the next-token cross-entropy; perplexity = 2cross-entropy in bits.

- **Knowledge distillation:** a small student matches a large teacher's softened output distribution by minimising cross-entropy / KL to the teacher's "soft targets", which carry more information than one-hot labels (Hinton, Vinyals & Dean, 2015) [arXiv:1503.02531](https://arxiv.org/abs/1503.02531).

- **RLHF:** InstructGPT optimises a reward model's score with a per-token KL penalty from the supervised fine-tuned model, to stop the policy drifting into reward hacking (Ouyang et al., 2022) [arXiv:2203.02155](https://arxiv.org/abs/2203.02155).

- **Variational autoencoders:** the loss includes KL(q(z | x) ‖ p(z)), keeping the latent code close to the prior.

- **Decision trees:** information gain is the drop in entropy after a split (Decision Trees).

- **Monitoring:** KL or population stability index between training and live feature distributions detects drift.

### The answer that sounds right

#### "Use squared error between probability vectors"

Squared error (the Brier score) is a valid proper score, but as a training loss with softmax it gives weak gradients when the model is confidently wrong, exactly when learning should be fastest. Cross-entropy's −log q(correct) grows without bound as q(correct) → 0, and with softmax its gradient with respect to the logits is simply q − p: large when wrong, zero when right (see the chain rule lesson).

## Say it

### How are entropy, cross-entropy and KL divergence related?

#### The interviewer pushes further

Follow-up 1 of 3

Why is cross-entropy preferred to MSE for classification?

It's the negative log-likelihood of a categorical model, heavily penalises confident mistakes, and with softmax gives the simple gradient q − p, avoiding the weak gradients MSE gives through a saturating output.

Follow-up 2 of 3

What's perplexity?

2^H (or e^H in nats) of the per-token cross-entropy: an LLM with perplexity 10 is as uncertain as choosing uniformly among 10 tokens.

Follow-up 3 of 3

Why a KL penalty in RLHF?

Maximising a learned reward alone lets the policy exploit the reward model; the KL term to the reference model keeps outputs in the region where the reward model is reliable and preserves language quality.

#### The 30-second answer

Entropy is the expected surprise, minus the sum of p log p, measuring uncertainty. Cross-entropy is the expected surprise when outcomes follow p but you predict q; with one-hot labels it's the log loss, and minimising it is maximum likelihood. Cross-entropy equals entropy plus the KL divergence, so KL is the extra cost of using q instead of p; it's non-negative, zero only when they match, and asymmetric: forward KL is mass-covering, reverse KL is mode-seeking. KL appears in knowledge distillation, the VAE objective, and the KL penalty that keeps RLHF policies close to the reference model.

**Go further**

#### What not to say

- "KL divergence is a distance." It's asymmetric.

- "Cross-entropy and KL give different optimal models." With fixed p they differ by the constant H(p), so they have the same minimiser.

**Key terms and sources**

Information as surprise, entropy, cross-entropy and why it is the classification loss, KL divergence and its asymmetry, and where KL appears in distillation, VAEs and RLHF · built from Shannon (1948), Cover & Thomas, _Elements of Information Theory_, Goodfellow et al., _Deep Learning_ (§3.13), Hinton et al. (2015) and Ouyang et al. (2022) · checked 28 Oct 2026

#### Key terms

| Term | Meaning |
|---|---|
| **Entropy** | Average surprise; uncertainty of a distribution. |
| **Cross-entropy** | Average surprise using model q when truth is p; log loss. |
| **KL divergence** | Cross-entropy minus entropy; extra cost of q; asymmetric. |
| **Perplexity** | 2 to the cross-entropy (bits): effective number of equally likely choices. |
| **Mutual information** | How much knowing X reduces uncertainty about Y. |

#### Sources

1. C. Shannon, "A mathematical theory of communication", _Bell System Technical Journal_ 27, 1948.

2. T. Cover & J. Thomas, _Elements of Information Theory_, 2nd ed., Wiley 2006, ch. 2.

3. I. Goodfellow, Y. Bengio & A. Courville, _Deep Learning_, MIT Press 2016, §3.13, [deeplearningbook.org](https://www.deeplearningbook.org/).

4. G. Hinton, O. Vinyals & J. Dean, "Distilling the knowledge in a neural network", [arXiv:1503.02531](https://arxiv.org/abs/1503.02531), 2015.

5. L. Ouyang et al., "Training language models to follow instructions with human feedback", NeurIPS 2022, [arXiv:2203.02155](https://arxiv.org/abs/2203.02155).
