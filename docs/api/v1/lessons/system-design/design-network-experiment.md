# Measure a Feed Change with Network Effects

> A feed change affects what a user's connections see. How do you measure its real effect?

- Track: System Design › Experimentation › Designs
- Type: Design · 25 min
- Page: https://aimlrounds.com/tracks/system-design/design-network-experiment/
- Before this: Interference: When Groups Affect Each Other (`fundamentals/interference-in-experiments`)
- Quiz topic: `sdexp`

## Intuition

### The situation

A professional network changes its feed ranking. Viewers scroll a little less in the A/B test, so it looks bad. But creators may get more comments, and that could bring them back. A normal test can't see this. The interviewer asks:

> A feed change affects what a user's connections see. How do you measure its real effect?

#### Ask before designing

- **Direct or network effect?** The direct effect is how the change alters my behaviour. The network effect is how my connections' behaviour alters my experience.

- **Which way does it travel?** A feed ranking change alters what viewers do, which then changes what creators receive.

- **Which metrics?** Sessions and engagement for the people affected, and posting for creators.

- **Scale:** how much traffic can you spare, given a test like this takes up many users?

- **The graph:** who really influences whom: all connections, or those you interact with?

### The idea

Think of testing whether a new phone plan makes people call more. Give it to random people, and those without it also get more calls, from friends who have it. So give it to all of one person's friends, then see what happens to that one person. That shows the effect of their friends' change.

[Figure: Pick focal users called egos. Attach their connections, called alters. Flip a coin per cluster and treat the alters. Measure only the egos, who are all kept on one version.]

_A test between all my connections getting A, and all my connections getting B._

### Play

**Try to break it.** Drop the egos to 40,000. Then raise the loss rate to 50%.

#### Loss rate and cluster count

Illustrative: we assume a 1.5% smallest effect at 200,000 egos, and 50 people treated per ego. The measured effect assumes a share of connections equal to the loss rate wasn't treated, and that the effect is proportional, which is our simplification. Real sizes depend on your graph and metric.

Drop to **40,000 egos**. The smallest detectable effect rises above 3%, and you can no longer see a true 3% effect. Accepting a higher loss rate fits more clusters, but it **shrinks what you measure**, so you have to balance the two.

**Now say why:** why does a higher loss rate shrink the effect you measure?

## Architecture

### Architecture

#### In one breath

If a change makes me comment more, my connections see more comments, even if they're in control. A normal A/B test mixes the two groups, and **misses that effect**. An **ego cluster** takes one focal user (the ego) and their connections (the alters), treats all the alters together, and **measures only the ego**. Comparing egos whose connections all got the change against those whose connections didn't isolates the network effect. It's costly, because you **treat many people for each ego you measure**.

#### Treat the connections, measure the ego

##### Why a normal test misses it

A user in control has connections in treatment, and vice versa. Both groups receive some of the network effect, so the difference between them hides it. Your test can then call a change bad when it's actually helping people elsewhere in the network.

##### Building ego clusters

1. **Choose the graph:** use who actually affects whom, like past feed impressions. A full connections graph makes clusters too big.

2. **Select egos:** sample by degree, so egos represent all users. Starting at lower degrees helps more clusters fit.

3. **Attach alters:** assign each alter to one ego by the strength of their link. Each person belongs to one cluster.

4. **Accept some loss:** an alter already claimed elsewhere can't join, so a share of each ego's connections isn't treated as planned. This is the **loss rate**.

##### Running the test

1. Flip a coin per cluster.

2. Give the alters that group's version.

3. Put all egos in the same version, like control, so the only difference between them is what their connections received.

4. Compare egos across groups with a t-test. Alters aren't analysed for the network effect.

It's an A/B test between "all my connections got A" and "all my connections got B".

##### Costs and risks

- **Traffic:** most of the treated people are only there to create the effect.

- **Biased leftovers:** clusters take many engaged users, so what's left for other tests is less active.

- **Stale clusters:** relationships change, so rebuild often. It doesn't suit tests lasting months.

- **One hop only:** it assumes that only direct connections matter, so effects travelling further are not captured.

#### The numbers worth saying out loud

All of these are assumptions for the interview.

| Question | Working | Result |
|---|---|---|
| People per ego | Our assumption, from a typical cluster size | **say 50** |
| Egos per group | 200,000 ÷ 2 | **100,000** |
| Detectable effect at 4 times the egos | 1.5% ÷ √4 | **about 0.75%** |
| People at that size | 800,000 × 50 | **40 million, if clusters stayed this size** |

So you can't buy precision with traffic forever. This is why teams use it only for changes where network effects are large and matter.

## In practice

### In practice

#### What the interviewer will push on

- **Quality and evaluation:** before the test, check that egos look representative, and run A/A tests on data from before the test.

- **Reliability:** clusters go out of date as people connect. Use recent clusters, and watch the loss rate during the test, as it grows over time.

- **Scalability:** building clusters over a huge graph is a heavy job. The newer method moved from one framework to Spark and cut run time.

- **Traffic competition:** clusters use many engaged users, so other experiments see lower-engagement traffic. Reserve a share, and make it visible to other teams.

- **Which graph:** an impressions graph captures who sees whom, while a graph of comments and likes captures stronger links. Stronger links give fewer leaks, but fewer clusters.

- **Alternatives:** cluster randomisation, or using graph-aware assignment in dense networks. Each trades off different biases.

- **The decision:** combine direct and network effects. A change can look bad directly and good across the network, so agree on how to weigh them.

#### How the real team approached it

- **The surprise that justified it:** A change that looked bad for the people who received it turned out to help their connections. A normal test would've seen only the harm.

- **Use the graph that matters:** The team built clusters from who actually sees whom, not from all connections, which kept clusters a workable size.

- **Accept low power:** Since only egos are analysed, results are noisier than in a normal test, and they read them with that in mind.

- **Count the cost to others:** Clusters absorb many engaged users, so what's left for other experiments is less active.

- **Keep clusters fresh:** Relationships change, so they avoid reusing old clusters, and don't use this for tests lasting months.

- **Improve the method:** A later version used a simpler way to assign alters, which gave more clusters, fewer leaks and much faster builds.

### The answer that sounds right

#### "Just run a bigger A/B test"

It sounds right, since bigger tests detect smaller effects. But the problem is bias, not noise. Control users still get part of the effect from treated connections, however big the sample is, so you'd measure the wrong thing more precisely. You have to change how users are grouped.

## Say it

### A feed change affects what a user's connections see. How do you measure its real effect?

#### The interviewer pushes further

Follow-up 1 of 3

Why treat the alters and measure the ego, not the other way round?

You want the effect of connections' behaviour on a person. So you change the connections, and watch that person. Keeping egos on one version means their own experience of the feature can't explain any difference between the groups.

Follow-up 2 of 3

The direct test is negative, and the network effect is positive. Do you ship?

You need to decide how to weigh them before the test. Scale both to the whole population, because the network effect may reach far more people. Then look at long-term metrics, as a change that moves engagement from viewers to creators may help or hurt the product overall.

Follow-up 3 of 3

Why not use city-level or graph cluster randomisation instead?

Those can work, but dense professional networks connect across cities, and clusters leak. Graph clusters also tend to be very unequal in size. Ego clusters measure a specific one-hop effect with a simple comparison, though they cost more traffic and only analyse the egos.

#### The 30-second answer

A normal A/B test mixes treated and control users who are connected, so both groups get part of the network effect, and the test misses it. I'd use ego clusters. I'd build a graph of who actually affects whom, such as past feed impressions, and sample egos across all degrees. Each ego gets their alters, the connections that influence them, and each person belongs to one cluster. I'd flip a coin per cluster, and give that version to the alters. All egos stay on the same version, and I compare only egos. That's a test between all my connections getting A and all my connections getting B. Some alters will be unavailable, which is the loss rate, and that shrinks the measured effect. It's expensive, because I treat many people for each ego. It also takes engaged users from other tests, goes stale quickly and only covers one hop. So I'd use it when network effects really matter, and weigh direct and network effects together in the launch decision.

**Key terms and sources**

Based on a professional network's published method: [LinkedIn's ego-cluster paper](https://arxiv.org/abs/1903.08755), which we read in full, and [its later improvement](https://arxiv.org/abs/2308.05945), which we read in part. The volumes and lab numbers are illustrations. Uses interference and randomisation. · checked 5 Nov 2026
