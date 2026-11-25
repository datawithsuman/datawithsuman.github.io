# Classic Probability Puzzles

> Monty Hall, birthdays, broken sticks and the secretary problem.

- Track: Fundamentals › Maths for ML › Probability practice
- Type: Interview · 25 min
- Page: https://aimlrounds.com/tracks/fundamentals/practice-classic-puzzles/
- Before this: Expectation, Variance & Covariance (`fundamentals/expectation-and-variance`)
- Quiz topic: `prob`
- Sources checked: 2026-10-28 · Text last changed: 2026-11-19 · Version: 22f89a993e

How to use this page

Give yourself about 5 minutes per question, as in an interview. Say your approach out loud, then open the answer and compare the method, not just the number.

**The one tool for this page:** For geometric "random point" puzzles, draw the sample space (a square or a circle) and compare areas. For decision puzzles, compare the expected value of each choice.

Question 1 · Easy · Monty Hall

### A prize is behind one of 3 doors. You pick door 1. The host, who knows where the prize is, opens another door with no prize and offers you the chance to switch. Should you?

Answer: **Switch: you win with probability 2/3**

1. Your first pick is right with probability 1/3 and stays 1/3: the host's action doesn't change it.

2. The remaining 2/3 is now concentrated on the one unopened door.

3. Switching wins whenever your first pick was wrong: 2/3.

**Follow-up:** With 100 doors and the host opening 98 empty ones, switching wins 99/100. The answer depends on the host knowingly avoiding the prize.

Question 2 · Easy · birthday

### How many people do you need in a room for the chance that two share a birthday to exceed 50%? (365 equally likely days.)

Answer: **23 people (50.7%)**

1. P(all different) = (365/365)(364/365)…((365 − n + 1)/365).

2. For n = 23 this is about 0.493, so P(shared) ≈ 0.507.

3. It's small because there are C(23,2) = 253 pairs, each a chance to match.

Question 3 · Medium · meeting

### Two friends each arrive at a café at a uniformly random time between 12:00 and 1:00, and each waits 15 minutes for the other. What is the probability they meet?

Answer: **7/16 ≈ 0.44**

1. Draw the square of arrival times (x, y) in [0, 60]². They meet if |x − y| ≤ 15.

2. The two corner triangles where they miss have total area (45)² = 2025 out of 3600.

3. P(meet) = 1 − 2025/3600 = 1 − 9/16 = 7/16.

Question 4 · Medium · broken stick

### A stick is broken at two uniformly random points. What is the probability the three pieces form a triangle?

Answer: **1/4**

1. The pieces form a triangle exactly when every piece is shorter than half the stick.

2. In the unit square of the two break points, that region is 1/4 of the area.

3. Equivalently: P(some piece > ½) = 3 × ¼ = ¾, so the answer is 1 − ¾ = ¼.

Question 5 · Medium · circle

### Three points are chosen uniformly at random on a circle. What is the probability the triangle they form contains the centre?

Answer: **1/4**

1. The triangle misses the centre exactly when all three points lie in some semicircle.

2. P(all n points in a semicircle) = n / 2^(n−1); for n = 3: 3/4.

3. So P(contains centre) = 1 − 3/4 = 1/4.

Question 6 · Hard · secretary

### You interview 100 candidates in random order and must accept or reject each on the spot, aiming to hire the single best. What strategy works, and how often does it succeed?

Answer: **Reject the first 37, then hire the first who beats them all; succeeds about 37% of the time**

1. Observe the first r candidates without hiring, then take the first candidate better than all of them.

2. The success probability is maximised at r ≈ n/e (37 for n = 100), and the best probability tends to 1/e ≈ 0.368.

3. Remarkably, this doesn't shrink as n grows.

**Follow-up:** Where does this show up in ML? Optimal stopping ideas appear in early stopping and in choosing when to stop a hyperparameter search.

**More practice and sources**

6 interview questions, easy to hard · answers hidden until you click · checked 28 Oct 2026

Keep practising

These are classic interview questions. For more in the same style: Frederick Mosteller, _Fifty Challenging Problems in Probability with Solutions_ (Dover, 1987), and Xinfeng Zhou, _A Practical Guide to Quantitative Finance Interviews_ (2008). Related lessons: Bayes' Rule Practice.
