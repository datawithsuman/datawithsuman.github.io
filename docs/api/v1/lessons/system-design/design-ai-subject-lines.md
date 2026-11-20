# Fix a Failing AI Feature

> AI-written email subject lines lost to the old rule-based ones in an A/B test. What do you do next?

- Track: System Design › Experimentation › Designs
- Type: Design · 25 min
- Page: https://aimlrounds.com/tracks/system-design/design-ai-subject-lines/
- Before this: Reading the Result: Significance and Decisions (`fundamentals/reading-ab-results`), Prompt Engineering Patterns (`ai-engineering/prompt-engineering-patterns`)
- Quiz topic: `sdexp`

## Intuition

### The situation

A local news app replaced its rule-based email subject lines, which are the first few words of a post, with LLM-written ones. They read better, but clicks fell sharply in an A/B test. The team wants to try more prompts. The interviewer asks:

> AI-written email subject lines lost to the old rule-based ones in an A/B test. What do you do next?

#### Ask before designing

- **How did it lose?** On clicks only, or also on sessions and retention? Across all posts, or only some?

- **What's the baseline?** A simple rule, like the first few words of the post, can be surprisingly good.

- **Scale:** say 10,000 new posts a day, each sent to about 600 people.

- **Must never happen:** a subject line that makes up facts, or misleads people into clicking.

- **Limits:** emails can't wait for slow calls, and LLM calls per email would cost too much.

### The idea

Think of a new headline writer whose headlines are polished, but sell fewer papers. You wouldn't just send them on a writing course. You'd have an experienced editor who's seen what actually sells choose between their headline and the old one, and print the new one only when it's likely to do better.

[Figure: A post comes in. The LLM extracts a subject line. A reward model scores it against the rule-based line. The better one is sent. The model is monitored daily.]

_The reward model is that editor, trained on real click results._

### Play

**Try to break it.** Lower the precision until the gain disappears. Then raise the loss when it's wrong.

#### Why a so-so model can turn a loss into a win

Our simple model, compared with the rule-based line at 0%. All the values are invented for illustration. It also assumes wins and losses are the same size across posts.

The default model is often wrong, and it misses most winners. Yet it flips **−6%** to a small gain, because it blocks most of the losing lines. Lower the precision until the gain disappears, and that's the break-even point: **precision must beat loss ÷ (lift + loss)**.

**Now say why:** why can a model that misses most winners still turn a loss into a win?

## Architecture

### Architecture

#### In one breath

A subject line that reads better isn't always one people click. So don't only rewrite the prompt. **Learn from your A/B data**: use real click results to train a **reward model** that predicts which line people prefer. Generate a line, score it, and send it only if it beats the old rule-based line, which remains the **safe fallback**. Cache by post to cut cost, and monitor the model daily.

#### Generate, then score, then choose

##### First, diagnose

Read the lines that lost, and compare them with the rule-based lines. You often find the model is writing a polished summary, while users respond to the post's own voice. Next, split results by post type. If the AI wins on some posts and loses on others, the job becomes **picking when to use it**.

##### The pipeline

1. **Generate:** tell the model to extract the most interesting part of the post. Extracting also reduces made-up content, compared with writing from scratch.

2. **Enforce limits in code:** cut anything over the length limit.

3. **Score:** the reward model compares the AI line with the rule-based line.

4. **Choose:** send the AI line only if it's predicted to win. Otherwise, send the rule-based line.

5. **Cache:** generate once per post, and reuse it for all recipients.

6. **Fall back:** if the API fails after retries, send the rule-based line.

##### Training the reward model

1. Send both lines to a small share of users for many posts, as small A/B tests.

2. Label each post by real results: if the AI line's click rate is over 10% better, it wins. If it's over 10% worse, it loses. Discard posts with too few sends.

3. Fine-tune a small model to predict the winner from the post and its candidate line.

This is a learning loop: real user behaviour teaches the model what the prompt couldn't express.

#### The numbers worth saying out loud

All of these are assumptions for the interview.

| Question | Working | Result |
|---|---|---|
| Emails per day | 10,000 posts × 600 sends | **6 million** |
| LLM calls with no cache | One per send | **6 million a day** |
| LLM calls with a cache | One per post | **10,000 a day** |
| Reward model checks | One per post | **10,000 a day** |

Caching changes the economics: from a cost per email to a cost per post. It only works if the line isn't personalised, so personalising later would cost far more.

## In practice

### In practice

#### What the interviewer will push on

- **Quality and evaluation:** clicks can reward clickbait. So use sessions and weekly active users as the final measure, and watch unsubscribes and complaints as guardrails.

- **Reliability:** LLM APIs fail. Retry with backoff, cache the results, and fall back to the rule-based line, so an email always goes out.

- **Drift:** preferences and models change. Check the reward model's accuracy daily, retrain it when it falls, and keep a small share of random traffic to supply fresh labels.

- **Selection bias:** if you only send what the model likes, you stop learning what it rejects. A small random share keeps your training data honest.

- **Safety:** extraction limits made-up content, and the reward model adds a second filter, but neither is a guarantee. Use blocklists and sample reviews, since an email can't be recalled.

- **Why not only fine-tune the generator?** Trained on data the rule produced, it may simply learn to copy the rule. In the real case, it matched the rule-based line most of the time, with no clear gain.

- **Rollout:** test the full system against the baseline, in stages, not just its parts.

#### How real teams approached it

- **Accept the surprise:** The plain LLM lines lost to a very simple rule. The team concluded that a more informative line doesn't mean more clicks.

- **Prompts have limits:** Asking the model to extract rather than write helped, but prompt changes alone couldn't beat the rule.

- **Turn tests into labels:** They used real click results as labels, rather than human opinions of which line was better, with thresholds to ignore close calls and low-volume posts.

- **Choose, don't replace:** A small fine-tuned model decided when to use the AI line, keeping the rule for everything else. Even an imperfect model was enough to turn the result around.

- **Keep it simple:** Generating many candidates per post wasn't clearly better than generating a couple.

- **Operate it properly:** They cached per post, retried failed calls, fell back to the rule, checked the model's accuracy daily and retrained it when it dropped.

### The answer that sounds right

#### "The prompt needs more work"

It sounds right, since prompts are the easy thing to change. But more informative lines weren't what people clicked on, and prompts can only express what you already know. In the real case, even the better prompt still lost. Use your A/B data to teach a model what people actually prefer, and keep the old line for when the AI won't win.

## Say it

### AI-written email subject lines lost to the old rule-based ones in an A/B test. What do you do next?

#### The interviewer pushes further

Follow-up 1 of 3

Why does a model with only 67% precision help?

Because the fallback is a good baseline. It only needs to be right often enough that wins outweigh losses. Blocking most losing lines is what turns the overall result positive. The break-even precision is the loss divided by the lift plus the loss.

Follow-up 2 of 3

Could you just train on clicks and ship whatever gets the most?

That invites clickbait. Clicks can rise while people lose trust and unsubscribe. So keep the extraction constraint and safety filters, use sessions and retention as the final measure, and watch complaints and unsubscribes as guardrails.

Follow-up 3 of 3

How would you personalise this?

It would break the per-post cache, so cost grows towards one call per email. I'd start with a few versions per post, and choose among them by user segment, using a bandit if rewards are quick. I'd test whether the gain justifies the cost before going further.

#### The 30-second answer

First I'd diagnose it: read the losing lines, and split results by post type. A line that reads better isn't always one people click. If the AI wins on some posts, the problem becomes choosing when to use it. So I'd generate by extraction, which also reduces made-up content, and enforce length in code. I'd run small A/B tests across many posts, and label each by real click rates, ignoring posts with too few sends. Then I'd train a reward model to predict the winner, and send the AI line only when it's predicted to win. Otherwise, the rule-based line goes out, and it's also the fallback if the API fails. I'd cache per post, because each post goes to hundreds of people. I'd judge the full system on sessions and weekly actives, with unsubscribes as guardrails. I'd check the reward model daily, retrain when it drops, and keep some random traffic, so I keep learning what it rejects.

**Key terms and sources**

Based on a neighbourhood app's published work: [Nextdoor's paper, Let AI Entertain You](https://arxiv.org/abs/2312.12457). We read most of the paper directly and the later sections through a summary. Volumes and the lab's numbers are our own illustrations. Uses reading results, prompts and LLMOps. · checked 5 Nov 2026
