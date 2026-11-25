# Design Spam and Fake Account Detection

> A professional network with hundreds of millions of members is hit by fake accounts, scraping and spam. Design defences that stop bulk abuse early without blocking real members.

- Track: System Design › Trust and Safety › Designs
- Type: Design · 25 min
- Page: https://aimlrounds.com/tracks/system-design/design-spam-abuse-detection/
- Before this: Anomaly Detection (`fundamentals/anomaly-detection`), Thresholds & Misclassification Costs (`fundamentals/thresholds-and-costs`)
- Quiz topic: `sdllm`
- Sources checked: 2026-11-05 · Text last changed: 2026-11-20 · Version: 4282bbd691

## Intuition

### The situation

A professional network with hundreds of millions of members sees bulk fake-account attacks, scraping and spam. Its checks run millions of times a second across the product, and must be invisible to real members. The interviewer asks:

> A professional network with hundreds of millions of members is hit by fake accounts, scraping and spam. Design defences that stop bulk abuse early without blocking real members.

#### Ask before designing

- **Abuse types:** fake accounts, scraping, spam, fraud, phishing and account takeover.

- **Scale:** hundreds of millions of members, a few sign-ups a second, and millions of checks a second across the product.

- **Latency:** checks in the request path must be invisible, around a millisecond.

- **Must never happen:** blocking real members in large numbers, or a bulk fake-account attack succeeding.

- **Success metrics:** fake accounts caught and how early, real members challenged or blocked, and abuse reports.

### The idea

Think of a busy office building. Visitors are screened at the door; anyone suspicious is asked for ID rather than turned away. Security also notices when twenty visitors arrive together with the same story, and guards walking the floors catch the rest.

[Figure: Every sign-up is scored: allow, challenge or block. Clusters of similar new accounts are scored together. Behaviour models catch the rest, and investigators feed in new signals.]

_No single layer has to be perfect._

### Play

**Try to break it.** Raise the block threshold to 0.99. Lower the challenge threshold to 0.2. Then add cluster detection.

#### Who gets in, who gets challenged?

Illustrative: one day with 200,000 real sign-ups and a bulk attack of 100,000 fakes, made-up risk curves, challenges that stop 90% of fakes, and cluster detection that catches 85% of bulk fakes that get through.

Raise the block threshold and more fakes slip in; lower the challenge threshold and real people hit friction. Now add cluster detection: bulk fakes look alike, so a later layer catches them, which lets the first layer be **gentler with real people**. That's the point of a funnel.

**Now say why:** why does a later layer let the first layer be gentler with real people?

## Architecture

### Architecture

#### In one breath

Build a **funnel**, so whatever slips past one layer is caught by the next. **Score every sign-up**: allow low risk, **challenge** medium risk, block high risk. Then catch bulk fakes as **clusters** of similar accounts, and the rest by **behaviour**. Feed models with **real-time counters** per user and IP, keep checks fast and invisible, decide how to fail safely, and let **investigators** find what the models miss and turn it into new signals.

#### A funnel of defences

1. **Sign-up scoring:** a model scores each registration. Low risk passes, high risk is blocked, medium risk gets a challenge to prove it's a real person.

2. **Cluster detection:** group new accounts by shared attributes; a supervised model scores whole clusters with abnormal patterns, and the label passes down to each account, before they act.

3. **Activity models:** for fakes created slowly or by hand, models look for abusive or unusual behaviour, like scraping sequences or mass messaging.

4. **Member reports and investigators:** reports get extra scoring and review; investigators hunt what slipped through and feed new signals back into models.

5. **Protection by default:** shared filters at the edge, a common content filter for spam and malicious links, and stronger checks on high-risk actions like login, sign-up and payments.

##### Counters are the backbone

Many signals are velocities: sign-ups from one IP in an hour, profile views per minute, messages per day. A fast counter store per user, IP and other keys feeds both simple thresholds and models.

##### Most work off the request path

Do heavy processing nearline or offline; only check synchronously where you must. Decide per check what happens if it fails: block, allow and re-check later, or degrade to defaults.

#### The numbers worth saying out loud

All of these are assumptions for the interview, not figures from a real system.

| Question | Working | Result |
|---|---|---|
| Checks a second across the product | given | **4 million** |
| Machines for synchronous checks | 4 million ÷ 10,000 per machine | **about 400** |
| Counter reads a second | 4 million × 1 read | **about 4 million** |
| Sign-ups a day | 3 per second × 86,400 | **about 260,000** |

The counter store is the hot spot; reads far outnumber writes, so design it for very high read throughput and short-lived keys.

## In practice

### In practice

#### What every anti-abuse design gets asked

- **Why clusters?** Attackers spread abuse thinly across many accounts so each looks harmless; looking at the group exposes them.

- **Labels:** confirmed takedowns, member reports and investigator findings; noisy and late, so keep a clean, reviewed set for evaluation.

- **Adversaries adapt:** retrain often, add new signals from investigations, and watch for sudden shifts in risk scores or challenge pass rates.

- **Challenges, not just blocks:** a challenge costs a real person a few seconds but stops scripts; tune who gets one.

- **Sequences:** deep models over sequences of member actions catch scraping and automation that single events miss.

- **Failure modes:** if the scoring service is down, decide per endpoint whether to fail open, fail closed or re-score later.

##### Rollout

Run new models in shadow, review samples of what they'd block, then enable them on one endpoint at a time, watching appeals and support tickets.

#### What the real system reported

- **Funnel:** every registration gets a risk score; low risk registers, high risk is blocked, medium risk is challenged. Downstream, cluster models score groups of similar accounts and pass labels to members; activity models catch the rest; investigators find what evades automation, and their findings feed the models.

- **Example:** the sign-up model blocked five million fake accounts in less than a day during one attack.

- **Scale (2018):** over 590 million members; abuse systems processing over 4 million transactions a second in real time, using ML models and statistical rules.

- **Performance:** services handling 10,000 QPS on one 24-core machine with 99% of traffic under 1 ms; counters with 5 billion transient records, 200,000 writes and 3 million reads a second.

- **Failure strategies:** fail the transaction, re-score asynchronously after letting the user through, or degrade gracefully to default values.

The company's own figures, from 2018.

### The answer that sounds right

#### "Block anything suspicious at sign-up"

It sounds safe, but at sign-up you know little, so a strict block turns away many real people. Challenge the uncertain ones instead, and rely on later layers, like cluster and behaviour models, to catch fakes that get through.

## Say it

### A professional network with hundreds of millions of members is hit by fake accounts, scraping and spam. Design defences that stop bulk abuse early without blocking real members.

#### The interviewer pushes further

Follow-up 1 of 3

Why challenge instead of blocking uncertain sign-ups?

A challenge costs a real person a few seconds, while a wrong block loses them entirely. Scripts and bulk attackers usually fail challenges, so they cut abuse with much less harm.

Follow-up 2 of 3

Each fake account does only a little abuse. How do you catch them?

Look at groups: cluster accounts by shared attributes and behaviour, score the cluster, and act on all of them. Individually they look harmless; together the pattern is obvious.

Follow-up 3 of 3

The scoring service goes down. What happens to sign-ups?

It depends on risk: for sign-ups, let them through but re-score asynchronously and restrict new accounts until scored; for payments, fail closed or fall back to stricter rules.

#### The 30-second answer

First I'd clarify the abuse types, the scale and the latency budget. I'd build a funnel. Every sign-up is scored: low risk passes, high risk is blocked, and medium risk gets a challenge to prove it's a person. Next, cluster detection groups new accounts by shared attributes and scores whole clusters, catching bulk fakes before they act. Activity models catch slower fakes by behaviour, such as scraping sequences or mass messaging. Member reports and investigators find what slips through and feed new signals back. Everywhere, a fast counter store tracks velocities per user and IP for thresholds and models. Synchronous checks stay around a millisecond, with heavy work done nearline, and each endpoint has a defined failure strategy. Shared protections at the edge and a common content filter make abuse defence the default. I'd retrain often as attackers adapt, and roll out new models in shadow first.

**Key terms and sources**

Based on a professional network's published posts: [LinkedIn's "Automated Fake Account Detection"](https://www.linkedin.com/blog/engineering/trust-and-safety/automated-fake-account-detection-at-linkedin) and ["Defending Against Abuse at LinkedIn's Scale"](https://www.linkedin.com/blog/engineering/trust-and-safety/defending-against-abuse-at-linkedins-scale) (both 2018). The lab's numbers and the estimate are ours. Uses anomaly detection, thresholds and costs and class imbalance. · checked 5 Nov 2026
