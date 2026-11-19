# Design Real-Time Fraud Detection

> An online payments company must decide in under 100 ms whether each payment is fraud. Fraud is about 1 in 1,000 payments, and blocking good customers loses money too. Design the system.

- Track: System Design › Fraud and Risk › Designs
- Type: Design · 25 min
- Page: https://aimlrounds.com/tracks/system-design/design-fraud-detection/
- Before this: Class Imbalance (`fundamentals/class-imbalance`), Thresholds & Misclassification Costs (`fundamentals/thresholds-and-costs`)
- Quiz topic: `sdllm`

## Intuition

### The situation

An online payments company handles 10 million payments a day for many merchants. About 1 in 1,000 is fraud. Each payment needs a decision inside checkout, in under 100 ms, and every good customer blocked is a lost sale. The interviewer asks:

> An online payments company must decide in under 100 ms whether each payment is fraud. Fraud is about 1 in 1,000 payments, and blocking good customers loses money too. Design the system.

#### Ask before designing

- **Scale:** say 10 million payments a day, peaking at 500 a second, across many merchants.

- **Latency:** the decision sits inside checkout, so under 100 ms end to end.

- **Actions:** allow, block, or ask for extra verification such as a one-time password.

- **Costs:** a missed fraud costs the payment plus fees; a blocked good customer loses the sale and maybe the customer.

- **Must never happen:** the scoring service being down and blocking all payments, or a large share of good customers declined.

- **Success metrics:** fraud caught (recall), good payments blocked (false positive rate), fraud losses and checkout conversion.

### The idea

Think of a bank teller who has seen every customer at every branch. A stranger's card was tried at ten shops this morning? The teller notices instantly. Unsure cases get a quick ID check instead of a refusal, and whether they got it right only shows up weeks later.

[Figure: A payment arrives. Hundreds of fresh features are fetched, many counted across the whole network. The model scores it in milliseconds. Rules and thresholds decide: allow, verify or block.]

_Network-wide signals catch what one shop never sees._

### Play

**Try to break it.** Drag the threshold from 0.9 down to 0.6. Then turn on verification, then network features.

#### Where do you draw the line?

Illustrative: 10 million payments a day, 1 in 1,000 fraudulent (the rate the post gives), $80 average fraud, made-up score curves, and verification stopping 80% of fraud that reaches it.

A high threshold blocks few good customers but lets lots of fraud through. Lower it and you block more good customers. **Verification** changes the trade: uncertain payments get a check instead of a block, so most fraud is stopped and good customers can still pay. **Better features** beat any threshold, because they separate fraud from good payments in the first place.

**Now say why:** why do better features beat any choice of threshold?

## Architecture

### Architecture

#### In one breath

Score every payment in **under 100 ms** with a model that sees **hundreds of features**, many of them **network-wide counts** computed in real time, like how many cards one IP address has used today. Fraud is rare and its labels arrive **weeks later**, so train on matured data and watch for drift. Don't just block or allow: send the uncertain middle to **extra verification**. Explain decisions to merchants, let them add **rules**, and judge the system on both fraud caught and good customers blocked.

#### The path of one payment

1. **Request:** checkout sends the payment details: card, amount, merchant, device, IP, email.

2. **Features:** look up precomputed and real-time features, like how many payments this card made in the last hour, how many cards this IP has used today, and whether the name matches the email. Streaming counters keep these fresh.

3. **Score:** the model returns a fraud probability within the latency budget.

4. **Decide:** merchant rules and thresholds turn the score into allow, block or verify.

5. **Log:** store the features and decision, so the outcome can be joined weeks later to make training data.

##### Why network-wide features matter

A single merchant sees a stolen card once. A payments network sees it tried at ten shops in an hour. Counts and patterns across the whole network are often the strongest signals.

##### If the scorer fails

Decide in advance: fall back to rules, or allow low-risk payments, so an outage doesn't block every customer.

#### The numbers worth saying out loud

All of these are assumptions for the interview, not figures from a real system.

| Question | Working | Result |
|---|---|---|
| Fraud cases a day | 10 million × 0.1% | **about 10,000** |
| Peak scoring rate | given | **500 a second** |
| Feature lookups a second | 500 × 1,000 features, mostly batched | **about 500,000** |
| Training rows a year | 10 million × 365 | **about 3.7 billion** |
| Labelled fraud a year | 3.7 billion × 0.1% | **about 3.7 million** |

The model call is cheap; fetching hundreds of fresh features in a few milliseconds is the hard part, so features live in a fast online store fed by streaming counters.

## In practice

### In practice

#### What every fraud design gets asked

- **Delayed labels:** disputes and chargebacks arrive weeks later. Train on data old enough for labels to settle, and use early signals, like manual reviews and refunds, for faster feedback.

- **Feedback loop:** you never learn whether a blocked payment was really fraud. Let a tiny random share of borderline payments through, or verify them, to keep unbiased data.

- **Model choice:** start simple, then move to tree ensembles or deep networks as data grows. A model that retrains in hours lets you react to new attacks fast.

- **Feature work is the biggest lever:** study past attacks, look for signals like throwaway emails or card-testing bursts, and check them across the whole network.

- **Explanations:** show merchants why a payment was declined, such as mismatched name and email or many cards on one IP, so they trust and tune the system.

- **Rules:** let merchants add allow and block rules for their own business, alongside the model.

- **Drift and attacks:** fraud patterns change, for example to rapid card testing. Monitor scores and fraud rates by segment, and retrain often.

##### Rollout

Run a new model in shadow mode, compare its decisions with the current model on settled labels, then ramp it up merchant segment by segment.

#### What the real system reported

- **Speed and features:** more than 1,000 characteristics of each transaction, with a decision in under 100 milliseconds.

- **Results:** fraud around 1 in every 1,000 payments; only 0.1% of legitimate payments incorrectly blocked.

- **Models:** from simpler models like logistic regression to deep networks; in 2022 a Wide & Deep ensemble with XGBoost became a pure deep network inspired by ResNeXt. Dropping XGBoost alone would have cost 1.5% recall, but the new design cut training time by over 85%, to under two hours.

- **Data and features:** 10× more training data still brought significant gains; feature engineering, from studying attacks and the whole network, is one of the biggest levers.

- **Explanations and rules:** risk insights show the features behind a decline, like name and email mismatch or many cards on one IP; merchants can add allow and block rules.

The company's own figures. The post doesn't cover label delay, retraining cadence or thresholds.

### The answer that sounds right

#### "Our model is 99.9% accurate"

It sounds great, but with 1 fraud in 1,000 payments, approving everything is also 99.9% accurate. Accuracy hides the trade-off that matters. Report fraud caught and good payments blocked, and set thresholds from the cost of each mistake.

## Say it

### An online payments company must decide in under 100 ms whether each payment is fraud. Fraud is about 1 in 1,000 payments, and blocking good customers loses money too. Design the system.

#### The interviewer pushes further

Follow-up 1 of 3

Fraud labels arrive 60 days late. How do you know the model is still working today?

Watch score distributions and feature drift, track early signals like manual review outcomes and refunds, and compare segments. When attacks shift, these move long before chargebacks arrive.

Follow-up 2 of 3

Why not just block everything above 0.5?

Fraud is so rare that a low threshold blocks far more good customers than fraudsters, and each blocked customer is lost revenue. Set thresholds from the costs, and use verification for the uncertain middle.

Follow-up 3 of 3

A new card-testing attack starts today. What happens?

Real-time counters on cards per IP and rapid small payments catch it quickly; rules can block the pattern immediately, and fast retraining folds it into the model within hours.

First I'd clarify the volume, the latency budget, the actions available and the cost of each mistake. Each payment arrives at checkout; I'd fetch hundreds of features in milliseconds from an online store fed by streaming counters, including network-wide signals like how many cards an IP has used today. The model scores it within the budget, and thresholds plus merchant rules decide: allow, block, or send the uncertain middle to extra verification. Everything is logged, so outcomes can be joined later. Labels like chargebacks arrive weeks late, so I'd train on matured data, use early signals for faster feedback, and let a small random share of borderline payments through to avoid a feedback loop. I'd start with a simple model and move to deeper ones as data grows, keeping retraining fast. I'd measure fraud caught, good payments blocked and losses, explain declines to merchants, and fail safe if the scorer goes down. New models run in shadow mode first.

**Key terms and sources**

Based on a payments company's published post: Stripe's "How we built it: Stripe Radar" (March 2023). The post doesn't cover label delay, retraining cadence or thresholds, so those parts, the lab's numbers and the estimate are ours. Uses class imbalance, thresholds and costs and feature stores.
