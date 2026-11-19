# Balls & Urns Practice

> With or without replacement, and the symmetry shortcut that saves minutes.

- Track: Fundamentals › Maths for ML › Probability practice
- Type: Interview · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/practice-balls-and-urns/
- Before this: Probability Basics & Bayes' Rule (`fundamentals/probability-and-bayes`)
- Quiz topic: `prob`

How to use this page

Give yourself about 5 minutes per question, as in an interview. Say your approach out loud, then open the answer and compare the method, not just the number.

**The one tool for this page:** Without replacement, multiply step by step (or use combinations); with replacement, draws are independent. Symmetry often beats calculation: every ball is equally likely to be in any position.

Question 1 · Easy · without replacement

### An urn has 5 red and 3 blue balls. You draw 2 without replacement. What is the probability both are red? And with replacement?

Answer: **5/14 ≈ 0.357 without; 25/64 ≈ 0.391 with**

1. Without: 5/8 × 4/7 = 20/56 = 5/14.

2. With: 5/8 × 5/8 = 25/64.

3. Without replacement is lower because the first red removes a red.

Question 2 · Easy · last ball

### A bag has 3 red and 2 green balls. You draw them all one by one. What is the probability the last ball is green?

Answer: **2/5**

1. By symmetry, every ball is equally likely to be last.

2. 2 of the 5 balls are green: 2/5. The same as the first ball being green.

Question 3 · Medium · which urn

### Urn A has 2 red and 1 blue ball; urn B has 1 red and 3 blue. You pick an urn at random and draw a red ball. What is the probability it came from urn A?

Answer: **8/11 ≈ 0.73**

1. P(red | A) = 2/3, P(red | B) = 1/4, each urn chosen with ½.

2. P(A | red) = (½ · 2/3) / (½ · 2/3 + ½ · 1/4) = (1/3) / (11/24) = 8/11.

Question 4 · Medium · Pólya urn

### An urn starts with 1 red and 1 blue ball. Each time you draw a ball, you put it back along with another ball of the same colour. What is the probability that the first two draws are both red?

Answer: **1/3**

1. First draw red: 1/2. Then the urn has 2 red, 1 blue, so second red: 2/3.

2. 1/2 × 2/3 = 1/3.

3. Surprising fact: after n draws, the number of reds drawn is uniformly distributed on 0…n.

Question 5 · Medium · empty boxes

### You throw 10 balls independently into 10 boxes, each box equally likely. How many boxes do you expect to stay empty?

Answer: **10 × 0.9¹⁰ ≈ 3.49**

1. A given box stays empty if all 10 balls miss it: (9/10)¹⁰ ≈ 0.349.

2. By linearity of expectation over the 10 boxes: 10 × 0.349 ≈ 3.49.

3. For large n, about n/e boxes stay empty (≈ 36.8%).

**Follow-up:** This is the same maths as the share of rows a bootstrap sample leaves out (out-of-bag rows in a Random Forest): about 36.8%.

Question 6 · Hard · same colour pair

### An urn has 4 red and 4 blue balls. You draw 4 without replacement. What is the probability you get exactly 2 of each colour?

Answer: **18/35 ≈ 0.51**

1. Ways to choose 2 red and 2 blue: C(4,2) × C(4,2) = 36.

2. All ways to choose 4 of 8: C(8,4) = 70.

3. 36/70 = 18/35 (the hypergeometric distribution).

**More practice and sources**

6 interview questions, easy to hard · answers hidden until you click · checked 28 Oct 2026

Keep practising

These are classic interview questions. For more in the same style: Frederick Mosteller, _Fifty Challenging Problems in Probability with Solutions_ (Dover, 1987), and Xinfeng Zhou, _A Practical Guide to Quantitative Finance Interviews_ (2008). Related lessons: Cross-Validation (sampling).
