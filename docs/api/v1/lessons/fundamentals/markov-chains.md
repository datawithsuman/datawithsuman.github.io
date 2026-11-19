# Markov Chains

> What is a Markov chain, and what is its stationary distribution?

- Track: Fundamentals › Maths for ML › Probability
- Type: Concept · 15 min
- Page: https://aimlrounds.com/tracks/fundamentals/markov-chains/
- Before this: Probability Basics & Bayes' Rule (`fundamentals/probability-and-bayes`), Eigenvalues & Eigenvectors (`fundamentals/eigenvalues-and-eigenvectors`)
- Quiz topic: `prob`

## Intuition

### The situation

Users move between browsing and ordering, and you want the long-run share of time in each, whichever page they start on. A colleague also asks how PageRank relates to this. The interviewer asks:

> What is a Markov chain, and what is its stationary distribution?

#### Why it matters

A lot of the world can be modelled as moving between states: users across pages, or an agent in an environment. Markov chains are the simplest way of reasoning about the long run, and they connect probability with eigenvectors.

### The idea

Think of a board game where your next square depends only on your current square and the dice, not on how you got there. Play long enough, and the share of time on each square settles, wherever you started. That settled share is the stationary distribution.

[Figure: A Markov chain. The next step depends only on the current state. Transitions form a matrix. The long run settles to a stationary distribution.]

_The stationary distribution is an eigenvector with eigenvalue 1._

### Play

**Try to break it.** Change the start. Then set a and b to 1.00, then both to 0.01.

#### Run a chain

Exact calculation, with made-up transition chances. The dashed line is the stationary share. The gap to it shrinks by the second eigenvalue, 1 − a − b, at each step.

Change the starting share, and the line ends in the same place. Now set both a and b to **1.00**: the chain flips forever, and never settles. Set them both to **0.01**: it does settle, but very slowly, because the second eigenvalue is close to 1.

**Now say why:** why does the chain forget where it started?

## Maths

### Maths

#### In one breath

A **Markov chain** moves between states, with the next state depending **only on the current one**, not the path taken. You write the transitions as a matrix. Many chains forget where they started and settle into a **stationary distribution**: the long-run share of time in each state. Mathematically, it's an **eigenvector with eigenvalue 1**. This powers PageRank, MCMC sampling, simple language models and the foundations of reinforcement learning.

#### Steps and the long run

##### The setup

Say a user is either **browsing (A)** or **ordering (B)**. Each step, a browsing user orders with chance a, and an ordering user goes back to browsing with chance b. As a matrix, each row adds up to 1:

| From \ to | A | B |
|---|---|---|
| **A** | 1 − a | a |
| **B** | b | 1 − b |

To move a distribution forward one step, multiply by the matrix: πt+1 = πtP. For t steps, use Pᵗ.

##### The stationary distribution

A distribution π is stationary if πP = π: one more step doesn't change it. Here, π = (b, a) / (a + b). It's about the balance of flows: users moving into each state match those moving out.

##### When does a chain settle?

- **Irreducible:** every state can reach every other. Otherwise, you can get trapped in one part.

- **Aperiodic:** it doesn't cycle on a fixed schedule. If a = b = 1, it flips forever, and never settles.

A finite chain with both properties has one stationary distribution, reached from any start. How fast depends on the **second-largest eigenvalue**: the closer to 1, the slower it forgets its start.

##### Where you'll see them

- **PageRank:** a random surfer. A page's rank is its stationary probability, and the random jump makes the chain irreducible and aperiodic.

- **N-gram language models:** the next word depends only on the last few. LLMs go beyond this, by using far more context.

- **MCMC:** build a chain whose stationary distribution is what you want to sample.

- **Reinforcement learning:** Markov decision processes add actions and rewards to this framework.

#### The maths

$$ P(X_{t+1} \mid X_t, \ldots, X_0) = P(X_{t+1} \mid X_t), \qquad \pi P = \pi, \qquad \pi = \frac{(b,\; a)}{a + b} $$

Worked example: with a = 0.1 and b = 0.3, π = (0.75, 0.25), so users spend 75% of the time browsing, wherever they started.

- **the Markov property**: Given the present, the past adds nothing. It’s about what’s in the state, so you can often make a process Markov by adding to its state.

- **stationary distribution**: It doesn’t change after a step. That makes it a left eigenvector of P, with eigenvalue 1.

- **for two states**: The long-run shares depend only on the two transition chances.

## In practice

### In practice

#### In practice

- **Is it really Markov?** Often not, at first. Adding recent history to the state can fix that, at the cost of many more states.

- **Estimating transitions:** count moves between states in your logs, and rescale each row. Rare transitions need smoothing.

- **User journeys:** absorbing states, like purchase or churn, let you compute the chance of each final outcome.

- **Time to settle:** a long burn-in may be needed before a chain represents the long run, which matters a lot in MCMC.

### The answer that sounds right

#### "Markov means it has no memory, so it can't model real users"

It sounds right, since people do have histories. But Markov is about what's in the state, not about the real world being memoryless. Include recent pages or a user type in the state, and the process can be Markov over that. The cost is a larger state space, which is the trade-off.

## Say it

### What is a Markov chain, and what is its stationary distribution?

#### The interviewer pushes further

Follow-up 1 of 3

Why does PageRank add a random jump?

Without it, surfers could get stuck on pages with no outgoing links, or in closed loops, so the chain wouldn't have a single stationary distribution. Jumping to a random page with a small chance makes every page reachable, and removes cycles. So it guarantees one answer, and speeds up convergence.

Follow-up 2 of 3

Is an LLM a Markov chain?

Not in the usual sense over words, since each token depends on a long context, not just the last. You could call the whole context the state, and technically the process is Markov over that. But the state space is so huge that this framing tells you little. A bigram model is a true, simple Markov chain.

Follow-up 3 of 3

How is the stationary distribution related to eigenvectors?

πP = π says π is a left eigenvector of P with eigenvalue 1. A stochastic matrix always has eigenvalue 1, and no eigenvalue larger in size. Repeatedly multiplying by P is power iteration, which is why the distribution converges to this eigenvector, at a rate set by the next eigenvalue.

A Markov chain moves between states, where the next state depends only on the current one. Transitions form a matrix whose rows sum to one. A stationary distribution satisfies pi P equals pi, so it's a left eigenvector with eigenvalue one. If the chain can reach every state and doesn't cycle on a schedule, it converges to that from any start, at a rate set by the second-largest eigenvalue. PageRank is the stationary distribution of a random surfer. MCMC builds a chain with a chosen stationary distribution.

**Key terms and sources**

States and transitions, the Markov property, stationary distributions and when chains converge, with PageRank, language models, MCMC and reinforcement learning.

#### Sources

- Blitzstein and Hwang, Introduction to Probability

- Murphy, Probabilistic Machine Learning: An Introduction

- Brin and Page, The PageRank paper (1998)

- Eigenvalues on this site

Explanations are ours, built from these sources. Lab numbers are illustrative, and worked examples were checked by calculation.
