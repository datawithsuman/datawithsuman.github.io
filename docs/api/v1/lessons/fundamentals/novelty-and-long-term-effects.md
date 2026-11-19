# Novelty, Primacy and Long-Term Effects

> Your new feature lifted engagement by 5% in week one. Will that lift last?

- Track: Fundamentals › A/B Testing › Can you trust it?
- Type: Concept · 15 min
- Page: https://aimlrounds.com/tracks/fundamentals/novelty-and-long-term-effects/
- Before this: Reading the Result: Significance and Decisions (`fundamentals/reading-ab-results`)
- Quiz topic: `ab`

## Intuition

### The situation

You redesigned the home page. Engagement jumps 5% in the first week, and the team wants to ship and celebrate. By week two, the lift looks smaller. The interviewer asks:

> Your new feature lifted engagement by 5% in week one. Will that lift last?

#### Why it matters

A test measures what happens during the test, while you're shipping for what happens after it. Decisions based on a week of data can lock in a change that fades, or kill one that would have paid off.

### The idea

Think of a new phone. You use it constantly for a week, and then it's just your phone. Or think of a new keyboard layout, where you're slower for a while and then faster. A one-week test can't tell which of those you're watching.

[Figure: Two shapes over time. With novelty, the effect starts high and fades, so an early result overstates it. With primacy, it starts low and grows, so an early result understates it.]

_Plot the daily effect, by days since first exposure._

### Play

**Try to break it.** Set the bump to −4, and the long-term effect to +0.5. Then lengthen the test.

#### Run the test longer

Illustrative: the bump fades with λ = 7 days. Assumes all users join on day one, and ignores noise.

Try an early bump of **−4** with a long-term effect of **+0.5**. A one-week test says it's harmful, while it ends up helping. That's primacy: the short test gets the direction wrong.

**Now say why:** how can a short test get the direction wrong?

## Maths

### Maths

#### In one breath

People react to change itself. **Novelty**: they try something because it's new, then the lift fades. **Primacy**: they need time to get used to it, so it starts low and improves. So a short test can get the size or even the direction wrong. Plot the effect **by days since first exposure**, compare new users with existing ones, and keep a small **holdback** group to measure what lasts.

#### Recognise the shape

| Effect | What happens | Risk |
|---|---|---|
| **Novelty** | People explore the new thing, then interest falls. | You overestimate it, and ship a change that fades. |
| **Primacy** | People are used to the old way. Engagement grows as they learn. | You underestimate it, and kill a good change. |
| **Slow harm** | More ads earn more now, while people gradually use the product less. | Short-term gain hides long-term loss. |

##### How to spot it

- **Plot the daily effect:** a stable effect is flat. A trend suggests one of these.

- **Use days since first exposure:** by calendar day, each date mixes people who've just joined with those who've been there for weeks.

- **Compare new and existing users:** new users have no old habit, so a novelty effect shouldn't apply in the same way.

- **Check the cumulative effect too:** it can look like it's shrinking simply because the interval is narrowing.

##### Measuring the long term

- **Run longer:** simple, but it slows everything down and users drop out over time.

- **Holdback:** after launch, keep a small share on the old version for months. It must be big enough to detect the effect.

- **User-learning designs:** Google's Hohnhold et al. (2015) measured how exposure over time changes behaviour.

#### The maths

$$ \tau(t) = \tau_\infty + A\,e^{-t/\lambda} $$

An illustrative model, used for the lab. Real effects need not follow a smooth curve, so look at your data.

- **effect on day t**: The lift for users t days after first seeing the change.

- **long-term effect**: What remains once behaviour settles. This is what you care about.

- **early bump**: Positive for novelty and negative for primacy.

- **how quickly it fades**: A larger λ means the bump lasts longer.

## In practice

### In practice

#### In practice

- **Check visible changes more:** people notice redesigns and new features. Invisible improvements, like faster ranking, rarely show novelty.

- **Don't just wait:** if a test runs a long time, users who remain are a selected group, and cookies get lost. Long tests have their own biases.

- **Size the holdback:** a very small holdback can't detect a long-term change, so plan it like any other test.

- **Use cumulative learning:** track what past short tests predicted against what holdbacks later found, and adjust your judgement.

##### Surrogates: predicting the long term

When you can't wait, use short-term metrics to predict the long-term one. Athey et al. combine many intermediate outcomes into a surrogate index, fitted on past data where the long-term result is known. It relies on a strong assumption: that the treatment affects the long-term outcome only through those short-term metrics. Check it against past tests and holdbacks wherever you can.

### The answer that sounds right

#### "Just run every test for three months"

It sounds right, since it measures the long term. But it slows the team to a crawl, and long tests have problems too: cookies get lost, and those who remain are a selected group. Check for a trend in the daily effect, and save holdbacks for major launches.

## Say it

### Your new feature lifted engagement by 5% in week one. Will that lift last?

#### The interviewer pushes further

Follow-up 1 of 3

Why plot by days since first exposure rather than calendar days?

Each calendar day mixes users who've just joined with users who've been there for weeks. Trends get blurred, and can even look like novelty when they're only changes in the mix. Aligning by first exposure compares users at the same stage.

Follow-up 2 of 3

How does comparing new and existing users help?

Existing users have habits to break, so novelty and primacy affect them. New users have no earlier version to compare with. If existing users show a fading lift while new users hold steady, it's probably a novelty effect.

Follow-up 3 of 3

What's the cost of a long-term holdback?

Those users keep the older experience, so you lose some of the benefit, and the team must maintain both versions for months. It also must be large enough to detect the effect. I'd save it for major launches, not every change.

Not necessarily. People react to change itself. With novelty, they try it because it's new, and the lift fades. With primacy, they start worse and improve as they learn. So I'd plot the effect by days since first exposure, because a flat line suggests it's stable. I'd compare new and existing users, since new users have no old habit. For important launches, I'd keep a small holdback for months to measure the lasting effect, and size it so it can detect that.

**Key terms and sources**

Why short-term results can mislead, how to spot novelty and primacy effects, and how long-term holdbacks measure what lasts.

#### Sources

- A 2021 Microsoft paper on user learning, novelty and primacy

- Estimating effects of long-term treatments

- Holdouts for measuring experiment impact, Eppo

- Hohnhold, O'Brien and Tang, Focusing on the Long-term (KDD 2015)

- Athey, Chetty, Imbens and Kang, Estimating Treatment Effects using Multiple Surrogates

Lab numbers are illustrative unless a lab says otherwise. Explanations are ours, built from these sources and standard statistics.
