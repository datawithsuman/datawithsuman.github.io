# Trust Checks: SRM and A/A Tests

> You planned a 50/50 split, but got 50,500 users against 49,500. Does it matter?

- Track: Fundamentals › A/B Testing › Can you trust it?
- Type: Concept · 15 min
- Page: https://aimlrounds.com/tracks/fundamentals/sample-ratio-mismatch/
- Before this: Reading the Result: Significance and Decisions (`fundamentals/reading-ab-results`)
- Quiz topic: `ab`

## Intuition

### The situation

You set a 50/50 split. Treatment has 50,500 users, and control has 49,500. Treatment also shows a 2% lift. A colleague says one percent doesn't matter. The interviewer asks:

> You planned a 50/50 split, but got 50,500 users against 49,500. Does it matter?

#### Why it matters

An SRM is like a fever: it tells you something's wrong, not what. If treatment is crashing for some users, those users vanish from its data, and the survivors make it look better. The result could be wrong in either direction, and it can look completely believable.

### The idea

Think of a fever. It doesn't tell you what's wrong, but it does tell you something is. And you wouldn't trust a patient's other test results until you'd found out why they have one. A broken split works the same way for an experiment.

[Figure: A sample ratio check. Planned 50,000 in each group. Got 50,500 and 49,500, which gives p equal to 0.0016, so do not trust the result.]

_A chi-squared test on the group sizes. A share that looks harmless can be far beyond chance._

### Play

**Try to break it.** Keep the share at 50.5%, and change the total users. Then find the smallest gap you can spot at a million users.

#### Is this split broken?

Planned split of 50/50. The verdict uses a cutoff of p below 0.01, a common choice. Because the check runs on every test, teams set it stricter than 0.05.

Keep the share at **50.5%** and change the total users. The same percentage goes from nothing to alarming, so judging by eye doesn't work. Use the test.

**Now say why:** why could missing users make treatment look better?

## Maths

### Maths

#### In one breath

A split that's off by even 1% can be far beyond chance at large scale. That's a **sample ratio mismatch (SRM)**, and it means something broke, so the groups may no longer be comparable. Check with a **chi-squared test** before reading results. If it fails, **don't trust the result**: find the cause. Run **A/A tests**, with the same experience on both sides, to check that the whole system gives honest p-values.

#### Detect, then diagnose

##### Where SRM comes from

| Stage | Example |
|---|---|
| **Assignment** | A bug in hashing, or a change to the split during the test. |
| **Execution** | Treatment loads more slowly or crashes, so fewer of its users get logged. A redirect loses users. |
| **Log processing** | A bot filter removes more users from one group. |
| **Analysis** | You filtered on something the change affects, such as "users who clicked". |
| **Other experiments** | Another test running on the same users disturbs the split. |

##### If you find one

1. Don't read the main metric, because you can't trust it.

2. Slice the mismatch by browser, country, day and app version to find where it starts.

3. Fix the cause, and run the test again. Removing users after the fact rarely fixes it.

##### A/A tests

Run the same experience on both sides. With nothing changed, about 5% should come out significant, and the p-values should spread evenly from 0 to 1. Many repeated A/A tests, or replays on past data, can reveal these problems:

- **Too many significant results:** the variance is underestimated, often from a unit mismatch.

- **An SRM:** the assignment or logging is broken.

#### The maths

$$ \chi^2 = \sum_{g} \frac{(O_g - E_g)^2}{E_g} $$

Example: 50,500 and 49,500, expecting 50,000 each. χ² = 500²/50,000 × 2 = 10, so p ≈ 0.0016. A 50.5% share looks harmless, but chance rarely produces it at this scale.

- **test statistic**: Compare it with a chi-squared distribution with 1 degree of freedom for two groups.

- **observed users**: What you actually got in the group.

- **expected users**: What the planned split predicts, like half of the total.

## In practice

### In practice

#### In practice

- **Automate it:** run the check on every experiment, and block or flag the results when it fails.

- **It's common:** a talk on the KDD 2019 paper reports about 6% of Microsoft experiments having an SRM in a year.

- **Use the intended ratio:** for a 10/90 test, compare with 10/90, not 50/50.

- **Check by day too:** a split that breaks partway through can look almost fine overall.

- **Remember the limit:** passing doesn't prove the test is fine. It's one check among others.

### The answer that sounds right

#### "Just trim the bigger group to the same size"

It sounds right, since the groups would then match. But the size isn't the problem. The users who are missing differ from those who stayed, perhaps because treatment crashed for them. Trimming at random leaves that difference, and hides the warning.

## Say it

### You planned a 50/50 split, but got 50,500 users against 49,500. Does it matter?

#### The interviewer pushes further

Follow-up 1 of 3

Why not just remove the extra users and analyse the rest?

Because the problem isn't the count. It's that the missing or extra users differ in some way. Trimming to equal sizes leaves the groups different, and hides the warning. You need to find and fix the cause.

Follow-up 2 of 3

What should an A/A test show?

About 5% of A/A tests should be significant at the 5% level, with p-values spread evenly between 0 and 1. If far more are significant, the variance is underestimated. Check for a mismatch between the analysis and randomisation units, or other assumptions breaking.

Follow-up 3 of 3

The SRM check passes, but only logged-in users are counted. Could there still be a problem?

Yes. If treatment changes who logs in, the groups may differ even with equal sizes. So define users by assignment, not by behaviour after it. And passing an SRM check doesn't prove the test is valid.

Yes, it matters. With 100,000 users, a chi-squared test gives about p equals 0.0016, so it's unlikely to be chance. That's a sample ratio mismatch: something in assignment, execution, logging or analysis broke. For example, treatment may crash for some users, and they drop out of its data. So I wouldn't trust the results. I'd slice the mismatch by browser, version and day to find the cause, fix it, and rerun. I'd run this check on every test, and use A/A tests to validate the platform.

**Key terms and sources**

How to detect a sample ratio mismatch with a chi-squared test, what causes it, and how A/A tests validate your experiment platform.

#### Sources

- Fabijan et al., Diagnosing Sample Ratio Mismatch (KDD 2019)

- Talk with the 6% figure

- Sample ratio mismatch, Wikipedia

- Book chapter on SRM and trust guardrails

Lab numbers are illustrative unless a lab says otherwise. Explanations are ours, built from these sources and standard statistics.
