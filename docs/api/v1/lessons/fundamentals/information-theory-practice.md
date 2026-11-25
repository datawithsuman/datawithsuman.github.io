# Information Theory Practice

> Entropy, surprise, KL and information gain: can you work them out by hand?

- Track: Fundamentals › Maths for ML › Information theory
- Type: Interview · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/information-theory-practice/
- Before this: Entropy, Cross-Entropy & KL Divergence (`fundamentals/entropy-cross-entropy-kl`)
- Quiz topic: `info`
- Sources checked: 2026-11-06 · Text last changed: 2026-11-19 · Version: 6ad19fc26a

How to use this page

Give yourself about 5 minutes per question, as in an interview. Say your approach out loud, then open the answer and compare the method, not just the number.

**Tools for this page:** every result here starts from −log p, the surprise of one event. Be clear whether you're in bits or nats, and check which way round a KL goes.

Question 1 · Easy · entropy

### What's the entropy of a fair coin? Of a fair four-sided die?

Answer: **1 bit, and 2 bits**

1. For a uniform distribution over n outcomes, entropy is log₂ n.

2. Coin: log₂ 2 = 1. Die: log₂ 4 = 2.

The uniform distribution has the highest entropy for a given number of outcomes.

Question 2 · Easy · surprise

### A model gives the correct class a probability of 0.25. What's the log loss in bits for that example?

Answer: **2 bits**

1. The loss is −log₂ 0.25.

2. 0.25 is 2⁻², so the loss is 2.

In nats, that's ln 4 ≈ 1.39, and frameworks usually report nats.

Question 3 · Easy · starting loss

### What cross-entropy would you expect at the start of training with 10 balanced classes?

Answer: **About 2.30 nats**

1. An untrained model should give each class about 0.1.

2. −ln 0.1 = ln 10 ≈ 2.30.

If your first loss is far from this, check your setup.

Question 4 · Medium · KL divergence

### P = (0.5, 0.5) and Q = (0.75, 0.25). What's KL(P ‖ Q) in bits? Is it the same as KL(Q ‖ P)?

Answer: **About 0.208 bits. No, the reverse is about 0.189**

1. KL(P ‖ Q) = 0.5 log₂(0.5/0.75) + 0.5 log₂(0.5/0.25) = 0.5(−0.585) + 0.5(1) ≈ 0.208.

2. KL(Q ‖ P) = 0.75 log₂(1.5) + 0.25 log₂(0.5) ≈ 0.189.

KL isn't symmetric.

Question 5 · Medium · perplexity

### A language model has an average loss of 2.3026 nats per token. What's its perplexity, and what does it mean?

Answer: **10, or as uncertain as choosing among 10 options**

1. Perplexity = e^(average loss).

2. e^2.3026 ≈ 10.

It only compares directly between models with the same tokeniser.

Question 6 · Medium · information gain

### Half of the orders are late. A split makes two equal groups, with 90% late in one and 10% in the other. What's the information gain?

Answer: **About 0.531 bits**

1. H(Y) = 1 bit.

2. Each group has entropy H(0.9) ≈ 0.469 bits, so H(Y | X) ≈ 0.469.

3. Gain = 1 − 0.469 ≈ 0.531.

Information gain is mutual information between the split and the label.

Question 7 · Hard · XOR

### X and Y are independent fair coin flips, and Z = X XOR Y. What's I(X; Z)? What's I(X, Y; Z)?

Answer: **0 bits, and 1 bit**

1. Knowing X alone leaves Z equally likely 0 or 1, so I(X; Z) = 0.

2. Knowing both determines Z, whose entropy is 1 bit, so I(X, Y; Z) = 1.

So a one-feature-at-a-time filter would drop both of these features.

Question 8 · Hard · zero probability

### Q gives zero probability to an outcome that P gives 0.1. What's KL(P ‖ Q)? What would you do about it?

Answer: **Infinite. Smooth Q, or use Jensen-Shannon**

1. That term is 0.1 × log(0.1 / 0), which is infinite.

2. Add a small value to all outcomes, or use a bounded measure such as Jensen-Shannon.

It's why models shouldn't assign exactly zero, and why monitoring tools smooth empty bins.

**More practice and sources**

8 interview questions, easy to hard · answers hidden until you click · checked 6 Nov 2026

Keep practising

Review entropy and KL, compression and perplexity, mutual information and comparing distributions.
