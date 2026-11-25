# Dice Practice

> Should you re-roll a 3? Expected values in five minutes.

- Track: Fundamentals › Maths for ML › Probability practice
- Type: Interview · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/practice-dice/
- Before this: Expectation, Variance & Covariance (`fundamentals/expectation-and-variance`)
- Quiz topic: `prob`
- Sources checked: 2026-10-28 · Text last changed: 2026-11-19 · Version: 725d10926b

How to use this page

Give yourself about 5 minutes per question, as in an interview. Say your approach out loud, then open the answer and compare the method, not just the number.

**The one tool for this page:** Expected value is linear: E[X + Y] = E[X] + E[Y] even when X and Y depend on each other. For "wait until" questions, the wait for an event of probability p averages 1/p.

Question 1 · Easy · waiting

### What is the expected value of one roll of a fair die? How many rolls do you expect to need until you roll a 6?

Answer: **3.5; 6 rolls**

1. E = (1 + 2 + … + 6)/6 = 21/6 = 3.5.

2. Rolling a 6 has probability 1/6 each time, so the wait is geometric with mean 1/(1/6) = 6.

Question 2 · Easy · sum

### You roll two fair dice. What is the probability their sum is 7?

Answer: **1/6**

1. 36 equally likely ordered pairs.

2. Sum 7: (1,6), (2,5), (3,4), (4,3), (5,2), (6,1) = 6 pairs.

3. 6/36 = 1/6. 7 is the most likely sum.

Question 3 · Medium · de Méré

### Which is more likely: at least one 6 in 4 rolls of one die, or at least one double-six in 24 rolls of two dice?

Answer: **The single 6 in 4 rolls (51.8% vs 49.1%)**

1. P(no 6 in 4 rolls) = (5/6)⁴ ≈ 0.482, so P(at least one) ≈ 0.518.

2. P(no double-six in 24 rolls) = (35/36)²⁴ ≈ 0.509, so P(at least one) ≈ 0.491.

3. The famous gambler's puzzle that Pascal and Fermat solved in 1654.

Question 4 · Medium · maximum

### You roll two fair dice. What is the expected value of the larger of the two numbers?

Answer: **161/36 ≈ 4.47**

1. P(max ≤ k) = (k/6)², so P(max = k) = (k² − (k − 1)²)/36 = (2k − 1)/36.

2. E[max] = Σ k(2k − 1)/36 = (1 + 6 + 15 + 28 + 45 + 66)/36 = 161/36 ≈ 4.47.

**Follow-up:** Expected minimum? 7 − 161/36 = 91/36 ≈ 2.53, because max + min = sum of both dice, whose mean is 7.

Question 5 · Medium · re-roll game

### You roll a die and win its value in rupees. You may re-roll once, but then you must keep the second roll. What strategy maximises your expected winnings, and what is the expectation?

Answer: **Re-roll on 1, 2 or 3; expected ₹4.25**

1. A re-roll is worth 3.5 on average, so keep any first roll above 3.5 (4, 5, 6) and re-roll 1–3.

2. E = P(keep)·E[first | keep] + P(re-roll)·3.5 = ½·5 + ½·3.5 = 4.25.

**Follow-up:** With two re-rolls allowed? Keep 5 or 6 on the first roll (the rest of the game is worth 4.25): E = (2/6)·5.5 + (4/6)·4.25 ≈ 4.67.

Question 6 · Hard · all faces

### How many rolls of a fair die do you expect to need until every face has appeared at least once?

Answer: **14.7 rolls**

1. Split into stages. After seeing k distinct faces, a new face appears with probability (6 − k)/6, so that stage takes 6/(6 − k) rolls on average.

2. Total = 6/6 + 6/5 + 6/4 + 6/3 + 6/2 + 6/1 = 6 × (1 + ½ + ⅓ + ¼ + ⅕ + ⅙) = 14.7.

3. This is the coupon collector's problem: n·H(n) ≈ n ln n for n faces.

**More practice and sources**

6 interview questions, easy to hard · answers hidden until you click · checked 28 Oct 2026

Keep practising

These are classic interview questions. For more in the same style: Frederick Mosteller, _Fifty Challenging Problems in Probability with Solutions_ (Dover, 1987), and Xinfeng Zhou, _A Practical Guide to Quantitative Finance Interviews_ (2008). Related lessons: Bias–Variance (expected values).
