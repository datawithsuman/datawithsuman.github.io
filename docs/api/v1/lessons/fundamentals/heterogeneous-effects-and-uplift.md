# Heterogeneous Effects and Uplift Modelling

> Your coupon test is flat overall. Could it still work for some users, and who should get it?

- Track: Fundamentals › A/B Testing › Beyond the fixed test
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/heterogeneous-effects-and-uplift/
- Before this: Multiple Testing and Segments (`fundamentals/multiple-testing`), Reading the Result: Significance and Decisions (`fundamentals/reading-ab-results`)
- Quiz topic: `ab`

## Intuition

### The situation

You have budget to send a coupon to 20% of users. A colleague trains a model on who's most likely to buy, and plans to send it to the top 20%. Last quarter's test of the same coupon was flat overall. The interviewer asks:

> Your coupon test is flat overall. Could it still work for some users, and who should get it?

#### Why it matters

Many ML systems choose who gets something: a coupon, a notification, a retention call. Interviewers often move from A/B tests to this question. The usual mistake is to train a model on who's likely to buy, then send them the coupon. Many would have bought anyway, so the money is wasted.

### The idea

Think of a doctor with a limited supply of a medicine. Giving it to patients who'd recover anyway is a waste, and so is giving it to those it can't help. The medicine belongs with those it changes the outcome for. Those aren't the same as the patients most likely to recover.

[Figure: Three steps. Run a randomised test. Model each user's uplift. Check it on held-out random data.]

_You're ranking by the change you cause, not by who buys._

### Play

**Try to break it.** Treat 20%, then raise the model error. Then move the share to 100%.

#### Who gets the coupon?

Our simulation of 20,000 users with a fixed seed. The numbers are invented: middling buyers gain the most, the keenest buyers can lose out, and about 18% of users are harmed. Green: by uplift. Grey dashed: at random. Red: by likely buyers. The uplift score here is the true effect plus error. Real data never shows you the true effect.

Treating 20% of users, **targeting likely buyers** gives about −168 extra purchases: you reach sure things and sleeping dogs, so the campaign does harm. **Random** targeting gives about 303. Even a noisy **uplift model** gives about 505. Set the model's error to 0 and it rises to 658. Now move the share to 100%. All three lines meet at about 1,515, because everyone gets treated, so the ranking stops mattering. The value of a model is in choosing who not to treat.

**Now say why:** why does targeting likely buyers do so badly?

## Maths

### Maths

#### In one breath

An A/B test gives one average, but a change may help some people and hurt others. **Heterogeneous effects** are those differences. If you can only treat some users, you should target those whose behaviour the treatment **changes**, not those most likely to buy anyway. **Uplift models** estimate each user's effect, using a randomised test as training data. You can never see one person's effect directly, so you evaluate on a held-out randomised group, by checking whether top-ranked users really show a larger gap between treatment and control.

#### Target the change

##### Four kinds of user

| Group | Without a coupon | With a coupon | Should you treat them? |
|---|---|---|---|
| **Persuadable** | Doesn't buy | Buys | Yes: this is the only group that pays back |
| **Sure thing** | Buys | Buys | No: you give away margin |
| **Lost cause** | Doesn't buy | Doesn't buy | No: you pay for nothing |
| **Sleeping dog** | Buys | Doesn't buy | No: contact makes it worse, such as a reminder to cancel |

This is the standard way to explain uplift modelling. In reality, you estimate each user's chance of being helped, because you can't sort people into these groups directly.

##### Three ways to build one

| Learner | How it works | Weak spot |
|---|---|---|
| **S-learner** | One model, with treatment as a feature. Predict with it on and off, then subtract | A regularised model can ignore treatment altogether |
| **T-learner** | Two models, one per group. Subtract their predictions | Errors from two models stack up, especially with few treated users |
| **X-learner** | Fit two models, compute each user's imputed effect from the other group's model, model those, then blend them | More steps, and it needs care when the data is thin |

Künzel et al. found the X-learner performed well in simulations, but none of the learners was best everywhere. **Causal forests** instead extend random forests to estimate effects directly, and split the data so that the same users don't both choose the splits and estimate the effects.

##### Evaluating without seeing the truth

1. Keep a held-out set from a randomised test.

2. Rank its users by predicted uplift.

3. In each slice, compare treated and control users. A good model shows larger gaps at the top.

4. Plot the cumulative gain against the share treated: an uplift or Qini curve. Compare it with treating at random.

#### The maths

$$ \tau(x) = E[Y(1) - Y(0) \mid X = x], \qquad \hat\tau_T(x) = \hat\mu_1(x) - \hat\mu_0(x) $$

Notation as in Künzel et al. These estimates need randomised data, or strong assumptions when treatment wasn’t random.

- **the conditional effect**: The average effect for users who look like x.

- **two outcomes you can’t both see**: Each user’s result with and without treatment. One is always missing, so this has to be estimated over groups.

- **the T-learner**: Fit one model on treated users and another on control users, then subtract their predictions.

## In practice

### In practice

#### In practice

- **Train on random data:** if past targeting was by rule, treated and control users differ. Keep a random holdout to supply clean training data.

- **Effects are small:** individual effects are harder to predict than outcomes, so uplift models need a lot of data. The public Criteo benchmark has 13.9 million samples.

- **Plan your segments:** mining many segments finds false winners. See multiple testing, and confirm a finding with a new test.

- **Include the cost:** treat a user only when the expected gain beats the cost. A coupon that's used by a sure thing costs margin.

- **Keep testing the policy:** compare the model's targeting with a simple rule in a live A/B test. Keep a share at random, or you'll lose your training data.

### The answer that sounds right

#### "Send it to the people most likely to buy"

It sounds right, since they're your best customers. But they were likely to buy anyway, so the coupon gives away margin for nothing, and some may even respond badly. What matters is the change the coupon causes, which only a randomised test can teach a model.

## Say it

### Your coupon test is flat overall. Could it still work for some users, and who should get it?

#### The interviewer pushes further

Follow-up 1 of 3

Why not target users with the highest predicted purchase probability?

They're the most likely to buy without help. The coupon then costs you margin for no extra sales. What you want is the change the coupon causes, which a response model doesn't estimate.

Follow-up 2 of 3

How do you evaluate an uplift model, if the true effect is never seen?

Use a randomised held-out set. Rank users by predicted uplift, split them into slices, and compare treated and control results in each slice. The cumulative gain against the share treated gives the uplift or Qini curve, which you compare with random targeting.

Follow-up 3 of 3

A test is flat overall, but a model finds a segment with a big lift. Do you ship to them?

Not yet, because searching for a segment finds false winners. Check that the segment holds on held-out data and makes sense, then run a new test on that segment alone.

An average can hide who benefits. If I can only treat some users, I want those whose behaviour changes, not those likely to buy anyway, because sure things give away margin and sleeping dogs can be harmed. So I'd run a randomised test, then train an uplift model to estimate each user's effect. A T-learner fits one model per group and subtracts them, an S-learner uses one model with treatment as a feature, and an X-learner and causal forests are more advanced. You can't observe one person's effect, so I'd evaluate on a held-out randomised set: rank by predicted uplift, and check that top slices show larger gaps between treatment and control, using an uplift or Qini curve. Then I'd test the targeting policy live.

**Key terms and sources**

Why an average can hide who benefits, targeting uplift rather than response, T, S and X learners, causal forests, and how to evaluate uplift without seeing it directly.

#### Sources

- Künzel, Sekhon, Bickel and Yu, Metalearners for Estimating Heterogeneous Treatment Effects

- Wager and Athey, Estimation and Inference of Heterogeneous Treatment Effects using Random Forests

- Athey and Imbens, Recursive Partitioning for Heterogeneous Causal Effects

- Gutierrez and Gérardy, Causal Inference and Uplift Modeling: A Review (2017)

- Diemert et al., A Large Scale Benchmark for Uplift Modeling

Lab numbers are illustrative unless a lab says otherwise. Explanations are ours, built from these sources and standard statistics.
