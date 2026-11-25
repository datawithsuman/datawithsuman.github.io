# Building Your First Eval Set: Real Traces and Synthetic Queries

> You have no users yet. How do you build a test set that finds real failures?

- Track: AI Engineering › Applied Evals › Lessons
- Type: Concept · 16 min
- Page: https://aimlrounds.com/tracks/ai-engineering/building-an-eval-dataset/
- Before this: Why LLM Apps Fail: The Three Gulfs (`ai-engineering/why-llm-apps-fail`)
- Quiz topic: `evals`
- Sources checked: 2026-11-15 · Text last changed: 2026-11-20 · Version: 8b83f6957a

## Intuition

### The situation

You're about to launch a real estate assistant with no users yet. A teammate generated 200 test queries with one prompt, and the app passes 96% of them. The interviewer asks:

> You have no users yet. How do you build a test set that finds real failures?

#### Why it matters

Error analysis can only find failures your traces contain. If every test query is a clean, well-specified request, you'll never learn that the app falls apart on vague ones. The test set decides what you can see, so building it is the first real eval decision.

### The idea

Think of testing a new car by driving it round the same sunny block 200 times. It passes every lap, and you've learnt nothing about rain, gravel or a steep hill. Pick the conditions first, then drive each one.

[Figure: Three steps for synthetic data. Pick dimensions. Combine them into tuples. Turn tuples into queries.]

_A test set can only find the failures it contains._

### Play

**Try to break it.** Add scenarios and features. Then ask for more queries the direct way.

#### Ask directly, or go through tuples?

With 36 possible tuples, 100 queries drawn through tuples cover about 34 of them. The same 100 from a direct prompt cover about 7, because the model keeps producing clear, common requests. Asking for more queries doesn't help: the direct prompt's coverage stops growing. The coverage model is illustrative, but the pattern is what practitioners report.

**Now say why:** why does asking for more queries not fix a direct prompt?

## How it works

### How it works

#### In one breath

Start with about 100 traces. If you have production logs, sample across features and include bad experiences: thumbs-down, rephrased requests, abandoned sessions. If you don't, don't ask an LLM for "50 user queries": you'll get 50 versions of the same request. Instead, list the **dimensions** where your app could fail (feature, user type, how clear the request is), write combinations (**tuples**) by hand, then have an LLM turn each tuple into a realistic query. Keep going until new traces stop showing new failures.

#### Two sources of traces

##### From production logs (preferred)

Sample across features and input types; cluster query embeddings if there are many. Add traces where users had a bad time: a thumbs-down, the same request rephrased three times, a session that ended by switching to a human. Ask domain experts which requests are hardest; they often know before the data does.

##### From synthetic queries

Asking an LLM to "generate 50 queries for a real estate assistant" gives "Find me a house in San Francisco" in fifty phrasings. Add a layer in between:

1. **Dimensions:** axes where requests differ and your app might fail. For a real estate assistant: feature (search, scheduling, email), client type (first-time buyer, investor, luxury buyer) and scenario (clear, ambiguous, out of scope).

2. **Tuples:** one value per dimension, such as (scheduling, first-time buyer, ambiguous). Write about 20 by hand to learn the space, then let an LLM propose more.

3. **Queries:** in a separate prompt, turn each tuple into a natural request: "Find showings for affordable homes with short notice." Throw out awkward ones.

Before running them, write down what you expect the app to do on each. Comparing predictions with reality exposes assumptions you didn't know you had.

##### When to stop

About 100 is a starting point, not a rule. The real signal is **saturation**: when 20 more traces show no new kind of failure, you have enough for now. Complex agents take longer to saturate than single-call apps.

##### What synthetic data can't do

It shows what _can_ fail, not how _often_ it fails for real users, because you chose the mix. It's also weakest in specialised, high-stakes domains. Replace it with real traces as soon as you have them.

#### The maths

$$ {N} = {|F|} \times {|P|} \times {|S|} $$

Four features, three client types and three scenarios already make 36 combinations. 100 well-spread queries can cover most of them; 100 queries from one blunt prompt usually cover a handful.

- **possible tuples**: Every combination of one value from each dimension.

- **features**: Search, scheduling, email and so on.

- **client types**: First-time buyer, investor, luxury buyer.

- **scenarios**: Clear, ambiguous or out of scope: where apps often break.

## In practice

### In practice

#### In practice

- **Use real logs when you have them:** sampled across features, plus bad experiences.

- **Pick dimensions where you expect failure:** use the app yourself, or watch others use it, to find them.

- **Write 20 tuples by hand:** then scale with an LLM, generating tuples and queries in separate steps.

- **Filter hard:** drop unrealistic queries; everything later depends on these traces.

- **Log full traces:** every model step, tool call and output, exported to a sheet or your tracing tool.

- **Stop at saturation:** when new traces stop showing new failures.

### The answer that sounds right

#### "It passes 96% of 200 test queries"

It sounds reassuring, but if one prompt wrote those queries, they're mostly the same easy request. Check which combinations of feature, user and scenario they cover before trusting the number.

## Say it

### You have no users yet. How do you build a test set that finds real failures?

#### The interviewer pushes further

Follow-up 1 of 3

Why generate tuples and queries in separate steps?

Tuples force coverage of specific combinations; in one step, the model drifts back to the common, clear case and the variety collapses.

Follow-up 2 of 3

Can you report a failure rate from a synthetic set?

No. You chose the mix of queries, so the rate reflects your choice, not your users. Use synthetic sets to discover failures, and real traffic to measure how common they are.

Follow-up 3 of 3

How many traces before you stop?

Start around 100 and stop at saturation: when 20 more traces show nothing new. Complex agents need more.

#### The 30-second answer

If I have production logs, I'd sample about 100 traces across features and include bad experiences like thumbs-down, rephrased requests and abandoned sessions. If not, I wouldn't ask an LLM for queries directly, since it repeats itself. I'd define dimensions where the app might fail, like feature, user type and how clear the request is, write about 20 tuples by hand, scale them with an LLM, and turn each tuple into a realistic query in a separate step. I'd stop when new traces stop showing new failures, and replace synthetic data with real traffic as soon as I can, because synthetic data can't tell me how often a failure happens.

**Key terms and sources**

Where the first 100 traces come from: sampling production logs well, or generating synthetic queries through dimensions and tuples so they're varied, plus when to stop and what synthetic data can't tell you. · checked 15 Nov 2026

#### Sources

- H. Husain and S. Shankar, _Evals for AI Engineers_ (O'Reilly): the Analyze-Measure-Improve lifecycle, error analysis, judges, CI and review

- [H. Husain and S. Shankar, AI Evals: everything you need to know (FAQ)](https://hamel.dev/blog/posts/evals-faq/)

- [Anthropic, Demystifying evals for AI agents, Jan 2026](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)

Explanations and examples are ours, built from these sources. Lab numbers are illustrative unless a lab says otherwise. Many recent papers are preprints, and benchmark scores change quickly.
