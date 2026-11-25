# Test Rankers Faster with Interleaving

> A ranking A/B test takes weeks, and you have many candidate models. How do you test faster?

- Track: System Design › Experimentation › Designs
- Type: Design · 25 min
- Page: https://aimlrounds.com/tracks/system-design/design-interleaving/
- Before this: Sample Size, Power and Runtime (`fundamentals/sample-size-and-power`), Ranking Metrics (`fundamentals/ranking-metrics`)
- Quiz topic: `sdrec`
- Sources checked: 2026-11-05 · Text last changed: 2026-11-20 · Version: 85cba2a372

## Intuition

### The situation

A search team has 20 candidate ranking models a quarter. Each A/B test takes 3 weeks, because bookings are rare and users differ widely, so most ideas never get tested. The interviewer asks:

> A ranking A/B test takes weeks, and you have many candidate models. How do you test faster?

#### Ask before designing

- **What's being compared?** Rankers on the same candidates, or changes to layout or pricing? Interleaving only suits the first.

- **What outcome?** Clicks arrive quickly. Bookings are rare, and can come days later.

- **Scale:** say 20 candidate models a quarter, with each A/B test taking 3 weeks.

- **Latency:** two rankers must run per request, so can you afford it?

- **Other surfaces:** does anything else reuse the list, like a map view?

### The idea

Think of a taste test. Give one group of people cola A, and another group cola B, and you need many people, since tastes differ so much. Give the same person both, and ask which they prefer, and you need far fewer. But that tells you which they prefer in a sip, not how sales will go.

[Figure: Two rankers each score the candidates. Their lists merge with a coin flip and team draft. Clicks give credit to each ranker per user. Only the best candidate moves to a full A/B test.]

_A fast filter first, then a full A/B test on the winner._

### Play

**Try to break it.** Click items and watch the credit. Tap the shared item. Then flip the coin.

#### Draft a list, then see the time saved

**Ranker A's list**a, b, c, d, e

**Ranker B's list**b, c, a, f, g

**The list the user sees.** Tap an item to record a click:

The lists are a simple example, and the speed-up is an illustration of how much less traffic you might need for similar power. It varies by metric, and a real test should still cover daily patterns.

Tap **c**: nobody gets credit, as both rankers wanted it. Flip the coin: the pairs swap order, and on average neither ranker gets the better position. That's what makes the comparison fair.

**Now say why:** why does the coin flip stop one ranker getting an unfair advantage?

## Architecture

### Architecture

#### In one breath

An A/B test gives each user one ranker, so most of what you measure is differences between users. **Interleaving** shows each user one list **blended from both rankers**, so the same person compares them directly. It can need far less traffic. So use it as a **fast filter**, then confirm the winner with an A/B test, because it tells you which ranker users prefer, not what the launch will do to your business.

#### Merge, credit, compare

##### Team draft with competitive pairs

1. Flip one coin per search to decide who goes first.

2. Take each ranker's top item that isn't on the list yet.

3. If they're the same, add it once. Neither ranker gets credit for it.

4. If they differ, add both as a **competitive pair**, in the coin's order, and tag each with its ranker.

5. Repeat until the list is full.

##### Credit and significance

- **Credit:** when a user clicks or books a tagged item, its ranker wins that pair. Shared items earn nothing, which removes noise.

- **Per user:** each user votes for the ranker with more wins. Users with a tie or no wins drop out.

- **Test:** compare the count of users who prefer each ranker with an even split, using a proportion test.

- **Slow outcomes:** credit a booking to the searches where that listing appeared during the test.

##### Why it's so much more sensitive

- **Same user, both rankers:** differences between users cancel out.

- **Disagreements only:** where rankers agree, no signal is possible, so it isn't counted.

##### The two-stage process

Offline tests shortlist the models, interleaving picks the promising few, and an A/B test on the winner measures its real effect.

##### What it can't do

- **Different experiences:** new layouts, or anything beyond which items rank where.

- **Set-level ranking:** if a ranker's value comes from the list as a whole, such as diversity, a blended list breaks it.

- **Business size:** it tells you which is preferred, not the revenue change. Continuous outcomes like revenue are hard to credit.

- **Marketplace effects:** a ranker that crowds bookings onto a few sellers won't show up.

#### The numbers worth saying out loud

All of these are assumptions for the interview, including the 50 times speed-up.

| Question | Working | Result |
|---|---|---|
| A/B testing all candidates, one by one | 20 models × 3 weeks | **60 weeks** |
| Traffic per interleaving test | 100% ÷ 50 | **about 2%** |
| Interleaving tests at once | 20 models at 2% each | **uses 40% of traffic** |
| Then A/B test the top 2 | 2 × 3 weeks | **about 6 weeks, plus the filter week** |

The gain is in how many ideas you can try, not only in time. Each request also runs two rankers, so ranking compute roughly doubles for interleaved traffic.

## In practice

### In practice

#### What the interviewer will push on

- **Quality and evaluation:** before trusting it, run interleaving and A/B tests on the same pairs, and measure how often they agree. Keep doing this over time.

- **Reliability:** if a ranker fails or is slow, serve the other ranker's list without interleaving, and exclude that request from the result.

- **Latency and cost:** run both rankers in parallel, so the wait is the slower of the two. Caching shared results and retrieval saves compute.

- **Logging:** record which ranker owns each position. Without this, you can't assign credit, and bugs are very hard to find.

- **Dilution:** count only searches where rankers disagreed, and users who actually engaged. One company reports this greatly increased sensitivity.

- **Trust checks:** run A against A. Each ranker should win half the time. If not, the merging or logging has a bias.

- **Counterfactual evaluation:** an alternative is to show one ranker's list and compute what the other would have done. Nothing is blended, so it helps when rankers optimise the set as a whole.

#### How real teams approached it

- **Filter, then confirm:** Search and delivery teams use interleaving to narrow down candidates early, and A/B tests to confirm the winner.

- **Fix the fairness:** Competitive pairs make credit simpler, and one coin flip per search balances positions between the two rankers.

- **Remove what can't help:** Teams increase sensitivity by ignoring results both rankers agree on, and users who never engaged.

- **Check it against A/B:** Before trusting it, teams run both methods on the same rankers and measure how often they pick the same winner.

- **Know its blind spots:** Teams report cases where interleaving and A/B disagree, as seeing options side by side changes behaviour. They avoid it for layouts and fundamentally different search strategies.

### The answer that sounds right

#### "Interleaving is faster, so replace A/B tests"

It sounds right, since it gets an answer with a fraction of the traffic. But it answers a narrower question: which ranker's items users pick when shown both. It can't tell you the revenue change, or test a new layout. One team even saw significantly negative interleaving with a neutral A/B test. Use it to filter, and A/B test the winner.

## Say it

### A ranking A/B test takes weeks, and you have many candidate models. How do you test faster?

#### The interviewer pushes further

Follow-up 1 of 3

Interleaving says B wins, but the A/B test is neutral. Which do you trust?

The A/B test for the launch decision, because it measures the real experience. Interleaving makes users compare options side by side, which isn't how they'd normally use the product. Look at why they differ, though: B may have won clicks that don't turn into bookings.

Follow-up 2 of 3

How do you handle bookings that happen days later?

Keep the user's assignment and logged lists across the test, then credit a booking to the ranker that showed that listing as a competitive item in their searches. Users vote once over the whole period. You can test different attribution windows, and check them against A/B results.

Follow-up 3 of 3

Why does a coin flip per search matter?

Whoever goes first gets the higher position in each pair, and higher positions get more clicks. The coin gives each ranker the better position equally often, so position bias averages out across searches, and a ranker can't win just by being placed first.

#### The 30-second answer

An A/B test gives each user one ranker, so most of the variance is between users. I'd use interleaving as a filter. For each search, a coin picks which ranker goes first, then we take each ranker's top unused item. If they agree, it goes in once with no credit. If they differ, we add a competitive pair, tagged by ranker. When a user clicks or books a tagged item, that ranker wins the pair, and each user votes for whichever won more. I'd test user votes against an even split with a proportion test. Because the same user sees both rankers, and only disagreements count, it can need far less traffic. It only tells me which is preferred, though, not the business effect. It doesn't suit layouts, set-level ranking like diversity, or marketplace effects. So offline shortlists, interleaving filters, and an A/B test confirms the winner. I'd run both on some pairs to measure agreement, and log which ranker owns each position.

**Key terms and sources**

Based on published work: [Airbnb's KDD 2025 paper](https://arxiv.org/html/2508.00751v1) (part read directly and part through a summary), [Walmart's post](https://tech.walmart.com/content/walmart-global-tech/en_us/blog/post/driving-faster-experimentation-through-interleaving-in-walmart-search.html) and [DoorDash's post](https://careers.doordash.com/blog/doordash-experimentation-with-interleaving-designs), which was blocked for us, so we used search excerpts. Uses sample size and ranking metrics. · checked 5 Nov 2026
