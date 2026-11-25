# Personalise Images with Bandits

> You want to personalise which image each user sees for each title. How do you choose it, and how do you prove it helps?

- Track: System Design › Experimentation › Designs
- Type: Design · 25 min
- Page: https://aimlrounds.com/tracks/system-design/design-image-personalisation/
- Before this: Bandits vs A/B Tests (`fundamentals/bandits-vs-ab-tests`)
- Quiz topic: `sdrec`
- Sources checked: 2026-11-05 · Text last changed: 2026-11-20 · Version: e201d5495b

## Intuition

### The situation

A streaming service shows one image for each title. A/B tests have found good images overall, but different people respond to different actors or genres. There are huge numbers of image requests a second. The interviewer asks:

> You want to personalise which image each user sees for each title. How do you choose it, and how do you prove it helps?

#### Ask before designing

- **What's the action?** Pick one image per title, per user, on each page.

- **What's a good outcome?** A play followed by enjoying the title. A click and quick exit should count as bad.

- **Scale:** image requests can be enormous, so can it run live or be computed ahead?

- **Where do images come from?** Designers often choose them, which limits how misleading they can be.

- **New titles:** how do you handle titles with no data yet?

### The idea

Think of a bookshop assistant choosing which book cover to show you. They learn your tastes, usually show what you'll like, and sometimes try something else to learn more. To judge a new assistant, you can check old records of cases where they'd have made the same choice, then trial them for real.

[Figure: Each title has candidate images. The system explores and logs its probabilities. A model per image learns from the rewards. Choices are precomputed and served. Replay filters models offline, and an A/B test proves the lift.]

_Exploration creates the data that lets you evaluate new models safely._

### Play

**Try to break it.** Raise exploration to 50%, then raise the images from 6 to 30.

#### How much should you explore?

Illustrative: the best image has a 12% take rate, and others have 8%. Exploration picks images uniformly at random. A replay match is when a fixed policy's choice equals the random image, so it happens once per candidate count. This ignores what's learned from the data, which is the point of paying.

Raise the images from **6** to **30**. Replay matches fall by five times, because the chance a random image matches is one in the number of images. More images means more exploring, and each new image has a cost to create as well.

**Now say why:** why do more images leave you with fewer replay matches?

## Architecture

### Architecture

#### In one breath

A/B testing can find the single best image for a title, but not the best one for each person. A **contextual bandit** uses user context to pick an image, and it **keeps exploring** to gather data. **Log the chance** of every image shown, so **offline replay** can compare models on past data without risk. To prove it works, A/B test the personalised system against an **unpersonalised bandit**. Reward real watching, not clicks, or you'll learn clickbait.

#### Explore, log, learn, serve

##### From A/B tests to bandits

| Approach | Finds | Limit |
|---|---|---|
| **A/B test on images** | The best image overall. | Slow, and one answer for everyone. |
| **Bandit** | The best image overall, while spending less on bad ones. | Still one answer for everyone. |
| **Contextual bandit** | The best image for this person and context. | Needs features, logging and more data. |

##### How it runs

1. **Context:** the user's history, device and page.

2. **Predict:** a model per image estimates the reward for this context.

3. **Explore:** mostly choose the best image, and sometimes try another. Epsilon-greedy explores at random. Thompson sampling explores in proportion to uncertainty.

4. **Log:** the image shown, its probability, the candidates and the features at that moment.

5. **Reward:** join what happened next to that log, and train the next model.

##### Offline replay

1. Take logged sessions where the image was chosen by exploration.

2. Ask the new model what it would have shown.

3. Keep only sessions where its choice matches what was actually shown.

4. Compute the take fraction: of those matches, how many led to a play?

Those rewards are real, not simulated. But few sessions match, especially with many images, so replay needs lots of data and has high variance.

##### Proving it works

Replay filters candidates. Then run an **A/B test**, comparing the personalised system with an unpersonalised bandit. Compare with a good baseline, or you'll credit personalisation for what any bandit could do.

#### The numbers worth saying out loud

All of these are assumptions for the interview.

| Question | Working | Result |
|---|---|---|
| Image requests at peak | Our assumption | **say 20 million a second** |
| Can each be a live model call? | Even at 1 ms each, 20 million × 1 ms | **20,000 CPU seconds, every second** |
| So compute ahead of time | Choices stored per user and title | **a fast lookup at request time** |
| Log size | 1 billion impressions × 500 bytes | **about 500 GB a day** |

That scale decides the architecture. Precompute gets you cheap lookups, at the cost of stale context and of compute for items that are never shown.

## In practice

### In practice

#### What the interviewer will push on

- **Quality and evaluation:** reward watching and enjoying, not just clicks. Otherwise, the model learns images that mislead people, who then quit quickly.

- **Attribution:** a play might come from the recommendation, the image or both. Evaluate the image choice with the title's position held fixed, or account for it in your model.

- **Changing images:** if the image changes between visits, which image caused the play? Changes can confuse people too, so consider keeping a choice stable for a while.

- **Reliability:** a missing image badly harms the experience. Always have a fallback, like a default image, and alert on missing ones.

- **Logging at compute time:** with precompute, log the choice, its probability and the candidate set when you compute it, then match it with the impression. Use the same feature code online and offline, or the model will see different data in training.

- **Cold start:** warm-start from existing data, and explore more for new titles.

- **Monitoring:** set aside a small share for simple exploration, to compare against the model and keep unbiased data.

#### How the real team approached it

- **Frame it as a bandit:** The homepage is the environment, showing an image is the action, and positive engagement is the reward.

- **Guard against clickbait:** Designers choose which images are available, and the reward is about enjoying a title, not only clicking.

- **Filter offline, prove online:** Replay compared algorithms on past sessions. Then an A/B test compared the best personalised bandits with unpersonalised ones.

- **Log at decision time:** They recorded the exploration probability, the candidates and a snapshot of the facts used for features, and shared feature code between training and serving.

- **Let scale shape the design:** With so many requests, they computed choices ahead of time and looked them up, with care to always show some image.

This reflects a 2018 talk, so current systems may differ.

### The answer that sounds right

#### "Just train a classifier on past click data"

It sounds right, since you have plenty of logs. But past data only shows images that were chosen for a reason, so you can't tell what would've happened with others. Without exploration and logged probabilities, the model learns from its own past choices. Clicks also reward clickbait, so reward watching, and pay for some exploration.

## Say it

### You want to personalise which image each user sees for each title. How do you choose it, and how do you prove it helps?

#### The interviewer pushes further

Follow-up 1 of 3

Why log the probability of each image?

Evaluation has to correct for how images were chosen. If the model showed an image 90% of the time, its data isn't comparable with an image shown 5% of the time. With the probabilities, you can reweight logged data, such as with inverse propensity scoring, to estimate how a new model would have done.

Follow-up 2 of 3

Why A/B test against an unpersonalised bandit, not against the old fixed image?

Because you want to know what personalisation adds. A bandit alone already beats a fixed image, by finding the best image overall. Against a fixed image, you'd credit personalisation for that gain too, and might overbuild.

Follow-up 3 of 3

Replay looks great, but the A/B test is flat. Why?

Replay assumes one image's effect can be judged in isolation. Live, images interact with the page, with what the person has seen before and with changes between visits. Replay can also have high variance with few matches. So treat replay as a filter, and trust the A/B test.

#### The 30-second answer

An A/B test finds the best image overall, but I want the best one per person, so I'd use a contextual bandit. For each title, a model per image predicts the reward from the user's history, device and page. Mostly it shows the best image, and it explores with epsilon-greedy or Thompson sampling. I'd reward actual watching, not clicks, or it will learn clickbait. I'd log the image shown, its probability, the candidates and the features at that moment, as all later evaluation depends on this. To compare models offline, I'd use replay: keep logged sessions where a new model's choice matches the image shown, and compute the take fraction. It's real data, but few sessions match. At this scale, I'd precompute choices and serve by lookup, with fallback images. To prove it works, I'd A/B test personalised bandits against unpersonalised ones. That shows what personalisation adds, not what any bandit would give.

**Key terms and sources**

Based on a streaming company's published work: [Netflix's QCon 2018 talk](https://qconsf.com/sf2018/system/files/presentation-slides/2018-11_-_qcon_artwork_personalization_talk.pdf), which we read from its slides, and [a summary of its blog post](https://www.reforge.com/blog/brief-netflix-artwork-personalization-through-multi-armed-bandit-testing), as the post itself was blocked for us. The volumes and lab numbers are illustrations. Uses bandits and LLMOps. · checked 5 Nov 2026
