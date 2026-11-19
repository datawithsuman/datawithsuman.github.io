# Design Notification Optimisation

> A learning app sends millions of daily reminders, choosing from dozens of message templates. Design a system that picks the best message for each user each day, without wearing users out with the same one.

- Track: System Design › Growth and Notifications › Designs
- Type: Design · 25 min
- Page: https://aimlrounds.com/tracks/system-design/design-notification-optimization/
- Before this: Bandits vs A/B Tests (`fundamentals/bandits-vs-ab-tests`), Bayesian Inference and Conjugate Priors (`fundamentals/bayesian-inference-and-conjugate-priors`)
- Quiz topic: `sdrec`

## Intuition

### The situation

A language-learning app sends millions of daily practice reminders, each picked from dozens of message templates, some only for certain users. Leadership wants more people practising, without users tuning reminders out. The interviewer asks:

> A learning app sends millions of daily reminders, choosing from dozens of message templates. Design a system that picks the best message for each user each day, without wearing users out with the same one.

#### Ask before designing

- **Goal:** users complete a lesson, so the reward is "did they do a lesson within two hours of the reminder".

- **Options:** dozens of templates, some only allowed for some users, like a streak message for users with a streak.

- **Scale:** millions of reminders a day, in 25 languages.

- **Must never happen:** sending a template to someone it doesn't apply to, or spamming the same message until users ignore it.

- **Success metrics:** the two-hour lesson rate, daily active users, and retention, especially for new users.

### The idea

Think of a friend who nudges you to go to the gym. If they say the same line every day, you stop hearing it. A good friend knows which line works best, saves the 'you're on a streak' line for when it's true, and mixes things up.

[Figure: For each reminder, eligible templates are scored, recent ones are penalised, and a softmax picks one. Every choice is logged; a daily job rescores templates.]

_The best message, repeated, stops being the best message._

### Play

**Try to break it.** Set γ to zero. Put it back and shorten the half-life. Then raise τ.

#### Which template does today's user get?

**Chance of sending each template**

Settings from the paper (γ = 0.017, h = 15 days, τ = 0.0025). The three templates' scores (+3.0%, +2.2%, +1.5% relative lift) and days since each was last sent (1, 20, 4) are made up for illustration. Modified score = score − γ · 0.5^(days ÷ h).

Set γ to zero: the best template wins every day, and users start ignoring it. Turn the penalty back on: yesterday's message loses its edge, so a fresh one gets a turn. Raise τ and the choice gets more random, which helps learning but costs a little reward.

**Now say why:** why compare a template with rounds where it was eligible, rather than its plain average?

## Architecture

### Architecture

#### In one breath

Treat each message template as an arm of a **bandit**. Score each template by how much better users do when it's sent than when it was **eligible but not sent**, which removes the bias from templates only some users can get. Shrink noisy scores with a **Bayesian prior**. Penalise templates the user saw **recently**, with a penalty that fades over days, because fresh messages work better. Pick with a **softmax** so there's a little exploration, log every choice and its probability, and keep a small **random holdout**.

#### Choose, log, score, repeat

1. **Arm selector:** when a reminder is due, get the eligible templates, compute each one's score minus a recency penalty for this user, and sample with a softmax.

2. **Decision log:** record the time, user, the chosen template and the probability of every eligible template.

3. **User arm history:** store when each template was last sent to each user, for the recency penalty.

4. **Scorer:** a daily batch job joins decisions with lesson events, computes each template's score and writes it to a store the selector reads.

5. **Holdout:** a small share of reminders, say 5%, chosen uniformly at random, to measure the bandit and gather data on rarely used templates.

##### Why "used versus eligible"?

A streak template is only sent to engaged users, so it looks great on raw averages. Comparing rounds where it was sent with rounds where it was eligible but another was sent cancels that out. Importance weights correct for how likely each choice was.

#### The numbers worth saying out loud

All of these are assumptions for the interview, not figures from a real system.

| Question | Working | Result |
|---|---|---|
| Reminders a day | given | **10 million** |
| Decision log rows a year | 10 million × 365 | **about 3.7 billion** |
| Arms with per-language scores | 40 templates × 25 languages | **1,000** |
| Holdout reminders a day | 10 million × 5% | **500,000** |

Effects are small, around a percentage point, so scores need weeks of data per arm, which is why daily batch scoring is enough.

## In practice

### In practice

#### What every notification design gets asked

- **Noisy reward:** many users do a lesson anyway. Counting only lessons within two hours of the reminder keeps some of that noise out.

- **Small samples:** new or rare templates have wild scores; a Bayesian prior pulls them towards average until data arrives.

- **Old data:** template performance drifts, so keep only enough recent history for a tight confidence interval.

- **Language:** translations perform differently; scoring each template-and-language pair as its own arm helped.

- **New templates:** start at a neutral score; recency penalties and softmax exploration give them a chance.

- **Beyond templates:** contextual bandits can personalise further by user features, at the cost of much more data per arm.

##### Rollout

Evaluate offline with importance-weighted replay on logs from random selection, then run an online A/B test against the current system, and keep a holdout afterwards.

#### What the real system reported

- **Method:** the Recovering Difference Softmax algorithm: scores as relative lift when used versus eligible, Bayesian shrinkage, an exponentially fading recency penalty and softmax selection.

- **Offline:** on logs with 88 million training and 114 million test rows, template-and-language arms gave +1.8% reward over random, and the recency penalty +1.9%; reusing the last template scored −0.5%.

- **Settings:** γ = 0.017, half-life 15 days, τ = 0.0025, keeping more than 90% of the potential gain while exploring.

- **Online A/B test:** +0.5% daily active users, +0.4% lessons completed, and +2.2% and +2.0% new-user day-1 and day-7 retention.

- **Five months later:** rounds using the bandit had 2.5% higher reward than a 5% random holdout.

From the paper (KDD 2020).

### The answer that sounds right

#### "Send everyone the template with the best average"

It sounds right, but templates limited to engaged users look great because of who gets them, and repeating any message makes users ignore it. Compare each template with rounds where it was eligible but not sent, and penalise recent repeats.

## Say it

### A learning app sends millions of daily reminders, choosing from dozens of message templates. Design a system that picks the best message for each user each day, without wearing users out with the same one.

#### The interviewer pushes further

Follow-up 1 of 3

Why not just send each user the template with the highest average success?

Two reasons. Templates only some users can get look better or worse because of who receives them, not the message; and repeating the same message makes users tune it out. Compare used versus eligible, and penalise recent repeats.

Follow-up 2 of 3

A brand-new template has a sky-high score after one day. What do you do?

Shrink it with a Bayesian prior towards the average, so a small sample can't dominate; let softmax exploration and more data settle its real value.

Follow-up 3 of 3

How do you know the bandit is still helping months later?

Keep a small holdout that chooses at random, and compare its reward with the bandit's rounds. It also catches bugs that quietly break the bandit.

First I'd clarify the goal, the templates and their eligibility rules, and the volume. I'd treat templates as bandit arms. The reward is a lesson within two hours of the reminder. Each template's score is its relative lift when sent compared with when it was eligible but another was sent, using importance weights from the logged probabilities, which removes the bias from eligibility rules. Noisy scores are shrunk with a Bayesian prior. Because fresh messages work better, I'd subtract a recency penalty that fades exponentially with days since this user last saw the template, and choose with a softmax so there's some exploration. Every decision is logged with all the probabilities; a daily batch job recomputes scores. I'd score template-and-language pairs, keep a small random holdout to monitor the bandit, evaluate offline with importance-weighted replay, then A/B test online on daily active users and retention.

**Key terms and sources**

Based on a language-learning app's published paper: "A Sleeping, Recovering Bandit Algorithm for Optimizing Recurring Notifications" (Duolingo, KDD 2020). The lab uses the paper's chosen settings; the template scores in it and the estimate are ours. Uses bandits vs A/B tests, Bayesian estimates and feedback loops.
