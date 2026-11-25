# Coin Flip Practice

> Why does HH take 6 flips on average but HT only 4?

- Track: Fundamentals › Maths for ML › Probability practice
- Type: Interview · 25 min
- Page: https://aimlrounds.com/tracks/fundamentals/practice-coins/
- Before this: Expectation, Variance & Covariance (`fundamentals/expectation-and-variance`)
- Quiz topic: `prob`
- Sources checked: 2026-10-28 · Text last changed: 2026-11-19 · Version: 4ee4d00d94

How to use this page

Give yourself about 5 minutes per question, as in an interview. Say your approach out loud, then open the answer and compare the method, not just the number.

**The one tool for this page:** For "how many flips until…" questions, write an equation for the expected value from each state (first-step analysis). For "who wins" questions, use symmetry or a geometric series.

Question 1 · Easy · expected flips

### How many flips of a fair coin do you expect to need to get the first head?

Answer: **2**

1. Let E be the expected number. First flip: head (prob ½) and you're done after 1 flip; tail (prob ½) and you've used 1 flip and start over.

2. E = 1 + ½·0 + ½·E ⇒ E = 2.

3. In general, with success probability p: 1/p (geometric distribution).

Question 2 · Easy · at least one

### You flip a fair coin 3 times. What is the probability of at least one head?

Answer: **7/8**

1. The only way to fail is TTT: probability (½)³ = 1/8.

2. P(at least one head) = 1 − 1/8 = 7/8.

**Follow-up:** "At least one" questions are almost always easiest as 1 − P(none).

Question 3 · Medium · first to head

### A and B take turns flipping a fair coin, A first. The first to flip heads wins. What is the probability that A wins?

Answer: **2/3**

1. A wins on flip 1 (½), or after TT on flip 3 (⅛), or flip 5 (1/32)…

2. Sum = ½ + ⅛ + 1/32 + … = (½) / (1 − ¼) = 2/3.

3. Shortcut: let p = P(A wins). A wins now with ½; otherwise B is in A's position: p = ½ + ½(1 − p) ⇒ p = 2/3.

Question 4 · Medium · HH vs HT

### What is the expected number of fair-coin flips until you see two heads in a row (HH)? And until you see heads followed by tails (HT)?

Answer: **HH: 6 flips; HT: 4 flips**

1. HH. States: start (E₀), just saw H (E₁). E₀ = 1 + ½E₁ + ½E₀; E₁ = 1 + ½·0 + ½E₀. Solving: E₁ = 4, E₀ = 6.

2. HT. After the first H you just wait for a T: E₁ = 2 (any further H keeps you in state H). E₀ = 1 + ½E₁ + ½E₀ ⇒ E₀ = 4.

3. Why different: a T after H resets HH to the start, but an H after H keeps HT "half done".

**Follow-up:** Expected flips until three heads in a row? 14 (in general 2^(n+1) − 2).

Question 5 · Medium · biased coin

### You have a coin that lands heads with an unknown probability p (not 0 or 1). How can you use it to make a fair 50/50 decision?

Answer: **Flip twice: HT → choose A, TH → choose B, HH or TT → flip again**

1. P(HT) = p(1 − p) = P(TH), so the two outcomes you keep are equally likely.

2. Discard HH and TT and repeat (von Neumann's trick).

3. Expected pairs of flips needed: 1 / (2p(1 − p)), e.g. 2 pairs for a fair coin, about 5.6 pairs if p = 0.9.

Question 6 · Hard · gambler's ruin

### You have ₹3. You bet ₹1 on fair coin flips, winning or losing ₹1 each time, until you reach ₹10 or go broke. What is the probability you reach ₹10?

Answer: **3/10**

1. A fair game: your expected money never changes (a martingale).

2. At the end you hold ₹10 with probability p or ₹0 with 1 − p, so 10p = 3 ⇒ p = 3/10.

3. In general, starting at i with target N: i/N.

**Follow-up:** With a biased coin (win probability q ≠ ½), P = (1 − r^i)/(1 − r^N) with r = (1 − q)/q.

**More practice and sources**

6 interview questions, easy to hard · answers hidden until you click · checked 28 Oct 2026

Keep practising

These are classic interview questions. For more in the same style: Frederick Mosteller, _Fifty Challenging Problems in Probability with Solutions_ (Dover, 1987), and Xinfeng Zhou, _A Practical Guide to Quantitative Finance Interviews_ (2008). Related lessons: Logistic Regression (Bernoulli outcomes).
