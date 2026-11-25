# A/B Testing Practice

> 12 by-hand questions: sample size, intervals, SRM, CUPED, multiple testing, peeking, launch rules and uplift.

- Track: Fundamentals › A/B Testing › Beyond the fixed test
- Type: Interview · 40 min
- Page: https://aimlrounds.com/tracks/fundamentals/ab-testing-practice/
- Before this: Running Many Tests at Once (`fundamentals/running-many-tests-at-once`), Heterogeneous Effects and Uplift Modelling (`fundamentals/heterogeneous-effects-and-uplift`)
- Quiz topic: `ab`
- Sources checked: 2026-11-07 · Text last changed: 2026-11-19 · Version: b1a1ad6e7f

How to use this page

Give yourself about 5 minutes per question, as in an interview. The numbers are small enough to work out by hand, so try each one first, then open the answer and compare.

**The toolkit:** users per group ≈ 16σ²/δ²; SE of a difference = √(p₁q₁/n + p₂q₂/n); χ² = Σ(O − E)²/E; design effect = 1 + (m − 1)ρ; CUPED removes ρ² of the variance; Bonferroni = α/m; rule of thumb = 355 × skewness²; corrected β = β/(G + 1).

Question 1 · Easy · sample size

### Checkout converts at 10%. You want to detect a rise of 1 point, at 5% significance and 80% power. You get 20,000 eligible users a day. How many users per group, and how long do you run?

Answer: **About 14,400 per group, and at least 1 full week**

1. σ² = 0.1 × 0.9 = 0.09.

2. 16 × 0.09 ÷ 0.01² = 14,400 per group, so 28,800 in total.

3. 28,800 ÷ 20,000 = 1.44 days.

4. Round up to a full week, to cover weekly patterns.

Why not stop at 1.44 days? You'd miss weekend behaviour, and you can't see whether the effect fades.

Question 2 · Easy · reading a result

### 40,000 users per group. Control converts at 5.0%, and treatment at 5.5%. The smallest lift worth shipping is 0.3 points. Give the 95% interval and the decision.

Answer: **0.19 to 0.81 points: significant, but it crosses the bar, so it's a judgement call**

1. SE = √(0.05 × 0.95 ÷ 40,000 + 0.055 × 0.945 ÷ 40,000) ≈ 0.158 points.

2. Interval = 0.5 ± 1.96 × 0.158 = 0.19 to 0.81.

3. It's above zero, so it's probably real. It also includes values below 0.3.

What would settle it? More data, which narrows the interval until it clears the bar or falls below it.

Question 3 · Easy · SRM

### A 10/90 test should give 10,000 and 90,000 users. You got 10,300 and 89,700. Is that a problem?

Answer: **Yes: χ² = 10, p ≈ 0.0016, so stop and investigate**

1. χ² = 300² ÷ 10,000 + 300² ÷ 90,000 = 9 + 1 = 10.

2. With 1 degree of freedom, p ≈ 0.0016, well below a 0.01 cutoff.

3. Don't read the main metric. Slice the mismatch by browser, version and day.

Note that you must compare with the planned 10/90, not with 50/50.

Question 4 · Medium · ratio metrics

### You assign by user and analyse click-through per page view, using the simple formula. Users have 20 views each, and the correlation within a user is 0.05. What's the real false-positive rate of a test at 5%?

Answer: **About 16%**

1. Design effect = 1 + (20 − 1) × 0.05 = 1.95.

2. The real standard error is √1.95 ≈ 1.40 times larger than the formula says.

3. Your 1.96 cut-off is really 1.96 ÷ 1.40 = 1.40 real standard errors.

4. Two-sided, that's p ≈ 0.16.

The fix is the delta method, or a bootstrap over users.

Question 5 · Medium · CUPED

### A test needs 300,000 users per group, which is 4 full weeks. The correlation between before and during is 0.6. What does CUPED save?

Answer: **36% of the variance: 192,000 users, or about 3 weeks after rounding up**

1. ρ² = 0.36, so 64% of the variance remains.

2. 300,000 × 0.64 = 192,000 users per group.

3. 4 × 0.64 = 2.56 weeks, which rounds up to 3.

What about users with no history? They get no reduction, so the real saving depends on how many have past data.

Question 6 · Medium · multiple testing

### Six metrics give p-values of 0.001, 0.008, 0.012, 0.041, 0.2 and 0.6, at α = 5%. How many pass Bonferroni, and how many pass Benjamini-Hochberg?

Answer: **Bonferroni: 2. Benjamini-Hochberg: 3**

1. Bonferroni's threshold is 0.05 ÷ 6 = 0.0083, which 0.001 and 0.008 pass.

2. Benjamini-Hochberg's thresholds are 0.0083, 0.0167, 0.025, 0.033, 0.042 and 0.05.

3. The third p-value, 0.012, is below 0.025. The fourth, 0.041, is above 0.033.

4. The largest passing rank is 3, so the top three pass.

With no correction, four would pass at 0.05.

Question 7 · Medium · peeking

### A test plans 5 equally spaced looks. At the first look, z = 3.0. Do you stop under Pocock? Under O'Brien-Fleming?

Answer: **Pocock: yes. O'Brien-Fleming: no**

1. Pocock's threshold is about 2.41 at every look, and 3.0 is above it.

2. O'Brien-Fleming's first threshold is 2.04 × √5 ≈ 4.56, and 3.0 is below it.

3. Stopping at the first z above 1.96 with 5 looks would give about 14% false wins.

If Pocock stops here, is the estimate fair? It's likely too high, because stopping early selects a moment when noise was pushing it up.

Question 8 · Medium · heavy tails

### Revenue per user has a skewness of 12. Capping brings it to 4. What does the rule of thumb ask for in each case?

Answer: **About 51,000 per group uncapped, and about 5,700 capped**

1. 355 × 12² = 51,120.

2. 355 × 4² = 5,680.

3. This only covers the normal approximation. Do a power calculation too, and use the larger number.

What might the cap hide? Any change that only affects spending above it.

Question 9 · Hard · launch rule

### You have 1 success metric and 4 guardrails, at α = 5% and β = 20%, using one-sided tests. What level and power does each use, and how many more users does that take?

Answer: **α stays at 5%, with 96% power per metric: about 1.9 times the users**

1. With one success metric, α ÷ 1 = 5%. Guardrails aren't corrected for α.

2. Corrected β = 0.2 ÷ (4 + 1) = 0.04, so 96% power.

3. (1.645 + 1.751)² ≈ 11.5, against (1.645 + 0.842)² ≈ 6.2.

4. 11.5 ÷ 6.2 ≈ 1.9 times.

Why correct power? All guardrails must pass, so more of them means more chances to fail by accident.

Question 10 · Hard · interference

### Riders share a fixed number of cars. A 50/50 test makes treated riders 10% more likely to win a car than control riders, and total bookings don't change. Roughly what happens to each group, and what does the A/B test report?

Answer: **Treatment up about 5%, control down about 5%. The test reports about +10%, while the real gain is 0**

1. The total is fixed, so any gain for one group is a loss for the other.

2. With equal groups, a 10% gap needs about +5% and −5%.

3. The test compares winners with losers, so it counts control's loss as a gain.

What would you run instead? A switchback or a city-level test, which gives less bias at the cost of far more variance.

Question 11 · Hard · overlap

### Tests A and B overlap, each 50/50. A alone adds 2 points, and B alone adds 1. Together, they add only 2. What does each test report, and what's the real gain from shipping both?

Answer: **A reports +1.5, B reports +0.5, and the real gain from both is +2**

1. The interaction I = 2 − (2 + 1) = −1.

2. Test A reports 2 + (½ × −1) = 1.5.

3. Test B reports 1 + (½ × −1) = 0.5.

4. They add up to 2, which is the real gain from shipping both.

If only A ships, its real gain is 2, not the 1.5 it reported.

Question 12 · Hard · uplift

### A coupon costs ₹20, and each extra purchase earns ₹200. Purchase rates without and with the coupon: group A, 30% and 31%. Group B, 5% and 20%. Group C, 60% and 60%. Group D, 50% and 45%. Who gets it?

Answer: **Only group B**

1. Group A: 0.01 × ₹200 = ₹2, which is less than ₹20.

2. Group B: 0.15 × ₹200 = ₹30, which is more than ₹20.

3. Group C: no gain, so it loses ₹20.

4. Group D: it loses sales as well as the coupon cost.

Note that a response model would pick C first, as it has the highest purchase rate.

**More practice and sources**

12 interview questions, easy to hard · answers hidden until you click · checked 7 Nov 2026

Keep practising

Uses the lessons in this section, from Randomisation to Uplift Modelling, and the launch decision rule. The scenarios and numbers are invented, so the answers are worked examples.
