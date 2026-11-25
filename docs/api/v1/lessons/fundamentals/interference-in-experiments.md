# Interference: When Groups Affect Each Other

> Your A/B test on a ride app shows 10% more bookings for treated riders. After launch, bookings barely move. Why?

- Track: Fundamentals › A/B Testing › Can you trust it?
- Type: Concept · 15 min
- Page: https://aimlrounds.com/tracks/fundamentals/interference-in-experiments/
- Before this: Randomisation and Assignment (`fundamentals/randomisation-and-assignment`)
- Quiz topic: `ab`
- Sources checked: 2026-11-07 · Text last changed: 2026-11-20 · Version: 73f99313a8

## Intuition

### The situation

A ride app tests a new booking screen, randomised by rider. Treated riders book 10% more, with a clean test. After launch to everyone, total bookings hardly change. The interviewer asks:

> Your A/B test on a ride app shows 10% more bookings for treated riders. After launch, bookings barely move. Why?

#### Why it matters

Research on marketplaces finds this bias can range from a third of the true effect to as large as the effect itself, and a 2021 paper on budget-split designs reports up to 230% in ad marketplaces. So this is a common way for a real team to launch something that never delivers what the test promised.

### The idea

Think of giving half a queue a fast pass for one ride. They get on more often, so the pass looks great. But the ride carries the same number of people, and those without a pass just waited longer. Give everyone the pass, and nothing changes.

[Figure: Illustrative result from the lab. The A/B test reports plus 10 percent, as treated riders take cars from control. After launch, the real gain is close to plus 1 percent.]

_Illustrative numbers from our simple model._

### Play

**Try to break it.** Set supply to 100% limited, then change the share of riders treated.

#### A test in a market with limited cars

Our own simple model, not a real market. At 100% limited, a fixed number of cars is shared in proportion to pull. At 0%, there are always spare cars. In between, it blends the two.

At **100%** limited supply, the test still reports a gain, yet total bookings don't change at all. Treated riders simply took cars from control riders. The test measured a shift, not growth.

**Now say why:** what is the test measuring, if not growth?

## Maths

### Maths

#### In one breath

Standard tests assume one user's outcome doesn't depend on who else is treated. In a marketplace, that fails: **treated riders can simply take cars from control riders**. The test compares winners with losers, so it overstates the gain, sometimes hugely. Reduce this by changing what you randomise: **cities** (cluster), or **time windows** (switchback). You get less bias, but much more variance.

#### How groups leak into each other

The assumption has a name: **SUTVA**, the stable unit treatment value assumption. It says that each user's outcome depends only on their own group. It breaks in two common ways:

- **Shared limited supply:** rides, delivery partners or ad budget. If treatment wins more, control is left with less.

- **Network effects:** a treated user messages a friend in control, so control's behaviour changes too. This often makes tests **understate** the gain.

##### Designs that reduce it

| Design | What you randomise | Downside |
|---|---|---|
| **Cluster** | Whole cities, or groups of closely connected friends. | Few units, so wide intervals. Regions differ, and some spillover remains. |
| **Switchback** | Time windows: the whole market gets one version per window, then flips. | Effects can carry over between windows. Doesn't suit long-term metrics. |
| **Two-sided** | Both buyers and sellers, and comparing the combinations. | More complex to run and analyse. |
| **Geo holdout** | A launch in some regions only, kept apart from others. | Few regions, and they must match well. |

##### Which way does the bias go?

It depends on the mechanism. Competing for the same supply usually overstates a win. Spillover to friends usually understates it. One study even shows a test can point the wrong way for profit.

#### The maths

$$ {\text{Global effect}} = {E[Y \mid \text{all treated}]} - {E[Y \mid \text{none treated}]} \;\neq\; {E[Y_T] - E[Y_C]} $$

With no interference, the two quantities match. With interference, the A/B difference also includes the harm done to control, which isn’t a benefit of the change.

- **what you want to know**: The change if everyone gets it, compared with nobody getting it.

- **everyone on the new version**: This world doesn’t exist during a 50/50 test.

- **everyone on the old version**: Neither does this one.

- **what an A/B test measures**: The gap between two groups who share a market. With interference, this differs from the global effect.

## In practice

### In practice

#### In practice

- **Ask where outcomes connect:** shared supply, shared budgets, messaging, social feeds or a shared cache.

- **Compare the two designs:** run a user-level and a cluster-level test, and the gap estimates the bias.

- **Expect less power:** switching from millions of users to a few hundred cities or time windows makes intervals much wider, so variance reduction matters more.

- **Tune the window:** switchback windows must be longer than the time an effect lingers, but short enough to give many samples.

- **Watch the control group:** if control gets worse while treatment gets better, that's a strong sign of interference.

### The answer that sounds right

#### "Just run it with a much bigger sample"

It sounds right, since larger tests are more precise. But bias doesn't shrink with sample size. You'd only measure the wrong quantity more precisely: the gap between riders competing for the same cars. You have to change what you randomise.

## Say it

### Your A/B test on a ride app shows 10% more bookings for treated riders. After launch, bookings barely move. Why?

#### The interviewer pushes further

Follow-up 1 of 3

When would you choose a switchback over a city-level test?

When supply and demand are tightly linked within a market and effects fade quickly, as with pricing or dispatch algorithms. All users in a window get one version, and each city acts as its own control. It suits short-lived effects, because anything that carries over between windows adds bias.

Follow-up 2 of 3

Can interference make a test understate an effect?

Yes. In a messaging app, treated users may send more, and that lifts control users too. The gap between groups shrinks, so the test understates the global effect. The direction depends on the mechanism.

Follow-up 3 of 3

How would you know whether your test has interference?

Think through the mechanism first: what do users share? Then check whether control gets worse during the test. The strongest evidence comes from comparing a user-level test with a cluster-level or switchback version, because the gap estimates the bias.

#### The 30-second answer

The test probably suffered from interference. Riders share a limited supply of cars, so treated riders can win cars from control riders. The A/B difference then counts control's loss as a gain, while the total hardly changes. This breaks the assumption that one user's outcome doesn't depend on others' groups. I'd randomise at a higher level: whole cities in a cluster design, or time windows in a switchback. That reduces bias at the cost of far more variance, and I'd use variance reduction to help.

**Key terms and sources**

Why A/B tests break when users affect each other, as in marketplaces and social networks, and how cluster and switchback designs reduce the bias. · checked 7 Nov 2026

#### Sources

- [Li, Zhao, Johari and Weintraub, interference and bias in two-sided marketplace experiments](https://arxiv.org/pdf/2104.12222)

- [Columbia Business School on A/B testing bias in marketplaces (Hannah Li)](https://business.columbia.edu/research-brief/ab-testing-bias-marketplaces)

- [Marketplace experimentation, Statsig](https://statsig.com/perspectives/marketplace-experimentation-platforms)

- [Experimental design on two-sided platforms](https://par.nsf.gov/biblio/10428500)

- [Liu et al., Trustworthy Online Marketplace Experimentation with Budget-split Design](https://arxiv.org/abs/2012.08724)

Lab numbers are illustrative unless a lab says otherwise. Explanations are ours, built from these sources and standard statistics.
