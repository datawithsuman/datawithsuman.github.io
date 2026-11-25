# Playing Card Practice

> How many cards until the first ace? Counting without counting.

- Track: Fundamentals › Maths for ML › Probability practice
- Type: Interview · 25 min
- Page: https://aimlrounds.com/tracks/fundamentals/practice-cards/
- Before this: Probability Basics & Bayes' Rule (`fundamentals/probability-and-bayes`)
- Quiz topic: `prob`
- Sources checked: 2026-10-28 · Text last changed: 2026-11-19 · Version: 63ac3a3a5f

How to use this page

Give yourself about 5 minutes per question, as in an interview. Say your approach out loud, then open the answer and compare the method, not just the number.

**The one tool for this page:** Count favourable over total with combinations C(n, k), or multiply probabilities step by step for sequential draws without replacement. For positions in a shuffled deck, use symmetry.

Question 1 · Easy · two aces

### You draw 2 cards from a shuffled 52-card deck. What is the probability both are aces?

Answer: **1/221 ≈ 0.45%**

1. First card an ace: 4/52. Second, given the first was: 3/51.

2. 4/52 × 3/51 = 12/2652 = 1/221.

3. Or with combinations: C(4,2)/C(52,2) = 6/1326.

Question 2 · Easy · same colour

### You draw 2 cards. What is the probability they are the same colour?

Answer: **25/51 ≈ 49%**

1. Whatever the first card's colour, 25 of the remaining 51 cards share it.

2. P = 25/51, slightly less than ½ because the first card removed one of its own colour.

Question 3 · Medium · one suit

### You are dealt 5 cards. What is the probability they are all hearts?

Answer: **1287/2,598,960 ≈ 0.05%**

1. Ways to choose 5 hearts: C(13,5) = 1,287.

2. All 5-card hands: C(52,5) = 2,598,960.

3. 1287 / 2598960 ≈ 0.000495. Any flush (one suit, including straight flushes): 4 × 1287 / 2598960 ≈ 0.2%.

Question 4 · Medium · first ace

### You turn over cards from a shuffled deck one by one. How many cards do you expect to turn up to and including the first ace?

Answer: **53/5 = 10.6**

1. The 4 aces split the 48 other cards into 5 gaps; by symmetry each gap holds 48/5 = 9.6 non-aces on average.

2. Cards before the first ace ≈ 9.6, plus the ace itself: 10.6.

3. General rule: (N + 1)/(k + 1) for the first of k special cards among N.

Question 5 · Medium · until red

### You turn cards over until the first red card. What is the expected number of black cards you see first?

Answer: **26/27 ≈ 0.96**

1. Each of the 26 black cards is before all 26 red cards with probability 1/27 (it must be first among itself and the 26 reds).

2. By linearity of expectation: 26 × 1/27 = 26/27.

Question 6 · Hard · no match

### You shuffle a deck labelled 1 to 52 and lay it out. What is the probability that no card ends up in its original position?

Answer: **≈ 1/e ≈ 36.8%**

1. This is a derangement. By inclusion–exclusion, P = 1 − 1/1! + 1/2! − 1/3! + … ± 1/52!.

2. That series converges to e^(−1) ≈ 0.3679 very quickly; for 52 cards it's 1/e to many decimal places.

3. Expected number of cards in their own position: 52 × 1/52 = 1 (linearity).

**More practice and sources**

6 interview questions, easy to hard · answers hidden until you click · checked 28 Oct 2026

Keep practising

These are classic interview questions. For more in the same style: Frederick Mosteller, _Fifty Challenging Problems in Probability with Solutions_ (Dover, 1987), and Xinfeng Zhou, _A Practical Guide to Quantitative Finance Interviews_ (2008). Related lessons: Class Imbalance (sampling without replacement).
