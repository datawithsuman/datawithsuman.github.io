# Bayes' Rule Practice

> You test positive for a rare disease. How worried should you be?

- Track: Fundamentals › Maths for ML › Probability practice
- Type: Interview · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/practice-bayes/
- Before this: Probability Basics & Bayes' Rule (`fundamentals/probability-and-bayes`)
- Quiz topic: `prob`
- Sources checked: 2026-10-28 · Text last changed: 2026-11-19 · Version: 300877cf23

How to use this page

Give yourself about 5 minutes per question, as in an interview. Say your approach out loud, then open the answer and compare the method, not just the number.

**The one tool for this page:** P(A | B) = P(B | A) · P(A) / P(B), with P(B) = sum over every way B can happen. Fastest in an interview: imagine 1,000 (or 10,000) people and count.

Question 1 · Easy · medical test

### A disease affects 1% of people. A test catches 95% of sick people and wrongly flags 5% of healthy people. You test positive. What is the probability you have the disease?

Answer: **about 16%**

1. Imagine 10,000 people: 100 are sick, 9,900 healthy.

2. Sick and positive: 95% of 100 = 95.

3. Healthy but positive: 5% of 9,900 = 495.

4. P(sick | positive) = 95 / (95 + 495) = 95/590 ≈ 0.161.

**Follow-up:** What if you test positive twice (independent tests)? Use 0.161 as the new prior: 0.161×0.95 / (0.161×0.95 + 0.839×0.05) ≈ 0.785.

Question 2 · Easy · coins

### A bag has two coins: one fair, one with heads on both sides. You pick one at random, flip it, and get heads. What is the probability it's the double-headed coin?

Answer: **2/3**

1. P(heads | double) = 1, P(heads | fair) = 1/2, each coin picked with probability 1/2.

2. P(double | heads) = (½ × 1) / (½ × 1 + ½ × ½) = (½) / (¾) = 2/3.

**Follow-up:** You flip the same coin again and get heads again. Now? (½·1)/(½·1 + ½·¼) = 4/5.

Question 3 · Medium · witness

### In a city 85% of taxis are green and 15% are blue. A witness says the taxi in an accident was blue. Tested in the same conditions, the witness identifies colours correctly 80% of the time. What is the probability the taxi was blue?

Answer: **about 41%**

1. Of 100 taxis: 15 blue, 85 green.

2. Witness says "blue": correct for 80% of the 15 blue = 12; wrong for 20% of the 85 green = 17.

3. P(blue | says blue) = 12 / (12 + 17) = 12/29 ≈ 0.414.

**Follow-up:** Why is it below 50% even though the witness is 80% reliable? The base rate (few blue taxis) dominates: the classic base-rate fallacy (Kahneman & Tversky).

Question 4 · Medium · two children

### A family has two children. You learn that at least one of them is a boy. What is the probability both are boys? (Assume boys and girls are equally likely and independent.)

Answer: **1/3**

1. Equally likely families: BB, BG, GB, GG.

2. "At least one boy" rules out GG, leaving BB, BG, GB.

3. Only BB has two boys: 1/3.

**Follow-up:** If instead you learn the _older_ child is a boy, the answer is 1/2 (only BB and BG remain). The wording changes the conditioning event.

Question 5 · Medium · spam filter

### 40% of emails are spam. The word "free" appears in 30% of spam emails and in 2% of normal emails. An email contains "free". What is the probability it's spam?

Answer: **about 91%**

1. Of 1,000 emails: 400 spam, 600 normal.

2. Contain "free": 30% of 400 = 120 spam; 2% of 600 = 12 normal.

3. P(spam | free) = 120 / 132 ≈ 0.909.

**Follow-up:** How does Naive Bayes combine several words? Multiply each word's likelihood ratio, assuming the words are independent given the class.

Question 6 · Hard · boxes

### Three boxes: one has two gold coins, one has two silver, one has one of each. You pick a box at random and draw a coin: it's gold. What is the probability the other coin in that box is also gold?

Answer: **2/3**

1. Count gold coins you could have drawn: 2 in the gold-gold box, 1 in the mixed box: 3 equally likely gold coins.

2. In 2 of those 3 cases you're in the gold-gold box, so the other coin is gold.

3. P = 2/3, not 1/2 (Bertrand's box paradox).

**Follow-up:** Why is "1/2" tempting? It treats the two remaining boxes as equally likely, ignoring that the gold-gold box is twice as likely to produce a gold draw.

**More practice and sources**

6 interview questions, easy to hard · answers hidden until you click · checked 28 Oct 2026

Keep practising

These are classic interview questions. For more in the same style: Frederick Mosteller, _Fifty Challenging Problems in Probability with Solutions_ (Dover, 1987), and Xinfeng Zhou, _A Practical Guide to Quantitative Finance Interviews_ (2008). Related lessons: Naive Bayes, Classification Metrics.
