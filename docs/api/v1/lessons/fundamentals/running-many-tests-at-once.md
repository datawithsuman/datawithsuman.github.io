# Running Many Tests at Once

> Your teams want to run 50 tests this month, but you only have so many users. How do you run them together?

- Track: Fundamentals › A/B Testing › Beyond the fixed test
- Type: Concept · 18 min
- Page: https://aimlrounds.com/tracks/fundamentals/running-many-tests-at-once/
- Before this: Randomisation and Assignment (`fundamentals/randomisation-and-assignment`), Multiple Testing and Segments (`fundamentals/multiple-testing`)
- Quiz topic: `ab`

## Intuition

### The situation

Twelve teams want to test changes this month, and each test needs two weeks of full traffic. Running them one by one would take half a year. Someone proposes running them all at once, on the same users, and a colleague says that will invalidate them all. The interviewer asks:

> Your teams want to run 50 tests this month, but you only have so many users. How do you run them together?

#### Why it matters

Traffic is what limits how many ideas you can test. Google built its overlapping system because a single layer of tests, with each query in at most one, couldn't scale. Interviewers often ask whether overlapping tests invalidate each other. The honest answer is "usually not, and here's how you'd check".

### The idea

Think of a school trying a new maths book and a new lunch menu at once. Flip one coin per pupil for each change, and about half of the new-book pupils also get the new menu, so the menu affects both sides of the book comparison equally. Trouble only comes if the two changes affect each other, like two new timetables for the same lesson.

[Figure: Three ideas. Overlap keeps all the traffic. Layers stop clashes. Interactions are the risk to check.]

_Overlap by default, and isolate what could clash._

### Play

**Try to break it.** Set a negative interaction. Then switch to separate users.

#### Overlap two tests

Illustrative, ignoring noise. Overlap assumes a 50/50 split in B. With separate users, each test gets an equal share of the traffic. False alarms assume every pair of tests is checked once, with no real interactions.

A and B each add 1 point alone, and together they lose 1 point of that. **Overlapping** tests each report 0.5, which adds up to the real gain of 1.0 from shipping both. Each test also keeps all the traffic. With **separate users**, each test reports 1.0, which adds up to a wrong 2.0, and each gets only a tenth of the traffic. So overlap is often more honest about the combined launch. Its weak spot is shipping only one: if A launches alone, the real gain is 1.0, not the 0.5 it reported. Now set tests to 50: that's 1,225 pairs, so about 61 false alarms at 5% if you check them all.

**Now say why:** why do overlapping tests add up to the real combined gain?

## Maths

### Maths

#### In one breath

If every test needed its own users, ten tests would get a tenth of the traffic each, and take ten times as long. So large platforms let tests **overlap**: each test hashes users with its own salt, so one person can be in many tests at once. Other tests then act like extra noise, which affects both groups equally. The risk is an **interaction**, where two changes together do something neither does alone. Serious ones appear to be rare, and **layers** keep changes that could clash from reaching the same user.

#### Overlap, layers and interactions

##### Why overlap is usually safe

With a different salt per test, being in treatment for test A tells you nothing about test B. So about half of A's treatment group and half of A's control group are in B's treatment. B affects both sides of A equally, on average.

##### Layers and domains

| Idea | What it is | Use it for |
|---|---|---|
| **Layer** | A group of settings. A user is in at most one test per layer | Changes that could clash, such as two tests of the same button |
| **Domain** | A slice of traffic set aside from the rest | Big changes that touch many layers at once |
| **Launch layer** | A layer across all traffic for gradual rollouts | Features about to launch, kept apart from ordinary tests |

A user gets a fresh, independent bucket in each layer, so tests in different layers overlap, while tests in the same layer never do. PlanOut's namespaces solve the same problem: each one centres on one kind of unit, such as users, and experiments take a share of its traffic.

##### How common are interactions?

Microsoft looked at hundreds of thousands of test-pair and metric combinations across four products, each running hundreds of tests a day. Three products showed no abnormal interactions. In the fourth, about 1 in 50,000 showed one, and none had significant effects pointing in opposite directions. They concluded that most tests don't interact, or do so only weakly. Your product may differ, especially in a small part of the product with many changes at once.

##### Finding one

You can compare A's effect among users in B's treatment and control. But that's hard, as an interaction estimate has twice the standard error of a main effect, so it needs about **four times the users**. With many tests, there are also many pairs to check, so you need multiple testing corrections.

#### The maths

$$ {\hat\tau_A} = {\tau_A} + {p_B}\,{I}, \qquad {\text{both vs neither}} = \tau_A + \tau_B + I $$

A standard two-by-two factorial result. The interaction’s estimate has twice the standard error of a main effect, on the same users.

- **what test A measures**: A’s effect, averaged over everyone in test A, some of whom also have B.

- **A on its own**: The effect of A for users who don’t have B.

- **B’s share**: The share of users in B’s treatment, usually a half.

- **the interaction**: How much more or less the two changes do together than the sum of their separate effects.

- **shipping both**: The real gain if both launch. At a 50/50 split, the two measured effects add up to exactly this.

## In practice

### In practice

#### In practice

- **Isolate what clearly clashes:** if two changes touch the same element, or could break each other, put them in one layer. A colour test and a background test could make text unreadable together.

- **Reset salts:** use a new salt for each test, so effects from an earlier test don't carry over into the next.

- **Scan automatically:** check pairs that share a surface, correct for multiple tests, and treat an alarm as a lead to follow up.

- **Test before launching together:** for two big launches at once, run them as a planned two-by-two test on the combination.

- **Watch for coupling in systems:** tests can also interact through shared caches, models and logs, where hashing can't help.

### The answer that sounds right

#### "Overlapping tests invalidate each other"

It sounds right, as users get several changes at once. But with independent assignment, each other test is balanced across your two groups, so it adds a little noise and no bias on average. An interaction can still shift what you measure, so isolate changes that could clash, and scan for the rest.

## Say it

### Your teams want to run 50 tests this month, but you only have so many users. How do you run them together?

#### The interviewer pushes further

Follow-up 1 of 3

Doesn't overlap add noise to each test?

A little, because other tests add to the variance of your metric. But they're balanced across your groups, so they don't bias the comparison, and the extra noise is usually tiny compared with the gain from having all the traffic.

Follow-up 2 of 3

Why does an interaction need about four times the users?

A main effect compares two halves of the users. An interaction is a difference of differences across four quarters, which doubles its standard error. Sample size depends on its square, so that's four times.

Follow-up 3 of 3

Two teams want to launch big changes to the same page next week. What do you do?

Run a planned two-by-two test across both, or at least keep them in the same layer until one has launched. Then compare each change alone and both together, because the combination is what users will see.

#### The 30-second answer

I'd let tests overlap. Each test hashes the user with its own salt, so being in one test tells you nothing about another, and other tests affect both groups equally. Each test then keeps all the traffic. The risk is an interaction, where two changes together differ from the sum of each. Microsoft's analysis across four products found these were very rare. For changes that could clash, I'd use layers, so a user is in at most one test per layer, and tests in different layers overlap. I'd scan for interactions automatically, knowing they need about four times the users to detect and need multiple testing corrections.

**Key terms and sources**

Why overlapping tests are usually safe, layers and domains, what an interaction does to your results, and how to detect one. · checked 7 Nov 2026

#### Sources

- [Tang, Agarwal, O'Brien and Meyer, Overlapping Experiment Infrastructure (KDD 2010)](https://research.google/pubs/overlapping-experiment-infrastructure-more-better-faster-experimentation/)

- [Jeng, A/B Interactions: A Call to Relax (Microsoft, 2023)](https://www.microsoft.com/en-us/research/articles/a-b-interactions-a-call-to-relax/)

- [Bakshy, Eckles and Bernstein, Designing and Deploying Online Field Experiments (PlanOut, WWW 2014)](https://hci.stanford.edu/publications/2014/planout/planout-www2014.pdf)

Lab numbers are illustrative unless a lab says otherwise. Explanations are ours, built from these sources and standard statistics.
