# Test an LLM Prompt in Production

> Your new LLM tutor's prompt looks better in demos. How do you test it in production, and what's your metric?

- Track: System Design › Experimentation › Designs
- Type: Design · 25 min
- Page: https://aimlrounds.com/tracks/system-design/design-llm-prompt-test/
- Before this: Sample Size, Power and Runtime (`fundamentals/sample-size-and-power`), LLM Judges: Pairwise Preferences and Pass/Fail Checks (`ai-engineering/llm-as-a-judge`)
- Quiz topic: `sdexp`
- Sources checked: 2026-11-05 · Text last changed: 2026-11-20 · Version: ef093b90a0

## Intuition

### The situation

An education app has an LLM tutor, with about 200,000 chat threads a day. A new prompt looks better in demos, and the team wants to ship it. Good here should mean students learn, not that they enjoy being handed answers. The interviewer asks:

> Your new LLM tutor's prompt looks better in demos. How do you test it in production, and what's your metric?

#### Ask before designing

- **What's the change?** One sentence in a prompt, a whole new prompt, or a different model?

- **What's good?** Does good mean more use, deeper thinking, or actually learning the skill? Students may enjoy a tutor that simply hands over answers.

- **Scale:** say 200,000 chat threads a day.

- **Must never happen:** harmful content for students, or a tutor that just gives the answer.

- **Limits:** latency and cost per chat, plus the privacy rules around student data.

### The idea

Think of a school trying a new teaching method. Teachers saying it feels better proves little. So first agree what good teaching looks like, and train assessors until they agree. Only then compare classes, and if your assessors are unreliable, you'll need many more classes to see a difference.

[Figure: New prompt versions are assigned per thread or user. An LLM judge scores a sample of chats, and results are compared on the main metric and guardrails. Experts label chats and tune the judge before any live test.]

_The judge is only useful once it matches your experts._

### Play

**Try to break it.** Lower the judge's accuracy from 85% to 65%. Then shrink the real lift to 0.5 points.

#### A noisy judge makes the test slower

Illustrative: 200,000 threads a day, 30% good chats in control, 2,000 tokens to score one, 5% significance and 80% power. Assumes the judge is equally accurate on good and bad chats, so the lift it sees is the real lift × (2 × accuracy − 1). Real runs should cover at least a full week.

Lower the judge's accuracy from **85%** to **65%**. A 2-point lift shrinks to 0.6 points, and the test needs about six times more scored chats. Improving the judge can be cheaper than running longer.

**Now say why:** why does a noisy judge hide a real improvement?

## Architecture

### Architecture

#### In one breath

Demos and thumbs-up ratings won't tell you whether a tutor teaches better. So first **define good**: experts label real chats against a rubric, and an **LLM judge** is tuned until it matches them. Then run a live test with **the chat thread or the user as the unit**, a primary learning metric and guardrails like giving away answers. A **noisy judge shrinks the effect you can see**, so it directly increases how long you must run.

#### Build the measure first, then experiment

1. **Choose a metric that reflects the goal:** for a tutor, cognitive engagement: is the student thinking, or copying?

2. **Write a rubric:** experts define each level with examples.

3. **Label real chats:** check experts agree with each other. If they can't agree, the rubric isn't ready.

4. **Build an LLM judge:** tune its prompt until its labels match the experts on data it hasn't seen.

5. **Score production chats:** run the judge nightly on a sample, because scoring everything costs too much.

6. **Run A/B tests:** feed prompt or model versions through the same experiment system as any other change.

##### Choosing the unit

| Unit | Good | Watch out for |
|---|---|---|
| **Chat thread** | More samples, and it suits a quality metric that's about one conversation. | A student can see both versions, and their threads are related, so use an analysis that allows for that. |
| **User** | A consistent experience. It's needed for long-term results like learning a skill. | Fewer units, so it takes longer. |

##### Metrics

- **Primary:** the judge's quality score, plus a real outcome like skills learned.

- **Guardrails:** gives away the answer, too wordy, thread length, latency, cost per chat and safety flags.

- **Weak on their own:** thumbs-up is rare and biased, and long chats can mean confusion.

##### Before the test

Run new versions offline against your labelled data and the judge first. This catches bad ideas cheaply. Offline can't tell you how real people respond, so it's a filter, not the final answer.

#### The numbers worth saying out loud

All of these are assumptions for the interview.

| Question | Working | Result |
|---|---|---|
| Chats scored per day | 200,000 × 20% | **40,000** |
| Judge tokens per day | 40,000 × 2,000 | **80 million** |
| Chats needed with a perfect judge | 16 × 0.21 ÷ 0.02² | **about 8,400 per group** |
| Chats needed at 85% accuracy | The visible lift falls to 1.4 points | **about 18,600 per group** |

The judge's cost is small next to the tutor's own LLM calls, and it's what makes the test possible. A real run should still cover full weeks, and longer if you measure learning.

## In practice

### In practice

#### What the interviewer will push on

- **Quality and evaluation:** check the judge against fresh expert labels regularly. A prompt change can shift what the judge sees, so a judge tuned on old chats may drift.

- **Model-specific bias:** if the judge prefers one model's writing style, it can favour that version for the wrong reason. Hide which version wrote each chat, and check the judge separately per version.

- **Answers vary:** the same prompt gives different replies, which adds noise. Log the prompt version, model and parameters for each reply.

- **Novelty:** a new tutor feature can show a fading lift, so look at the effect over time.

- **Cost and latency:** a stronger model might win on quality and lose on budget. Treat them as guardrails, and agree the trade-off beforehand.

- **Safety:** always run safety checks on every reply, not on a sample. Kill a version immediately on a safety failure, and don't wait for the test to end.

- **Rollout:** start at a small share, like 5%, and watch the guardrails before you widen it.

#### How real teams approached it

- **Start from what good means:** The team moved from judging prompts by feel to first defining a measure of how much students were thinking, based on a learning framework.

- **Experts before automation:** Experts labelled real chats against a rubric, and checked that they agreed with each other. Only then was an LLM judge tuned to match them.

- **Sample, don't score everything:** The judge scored a share of production chats nightly, which kept the cost manageable.

- **Pick the unit that fits the question:** They randomised by chat thread, because tutoring quality belongs to a conversation.

- **Test small changes:** They tested prompts, system instructions and different models, sometimes as small as one sentence, and treated experiments as a safety net rather than a delay.

- **Balance the metrics:** Thinking and skills learned were the goal, while guardrails watched for giving away answers, long threads, wordiness and slow replies.

### The answer that sounds right

#### "Use thumbs-up ratings, since users decide what's good"

It sounds right, since it's direct user feedback. But few people rate, and those who do aren't typical. Worse, a student may love a tutor that hands out answers, so the rating can reward the very behaviour you want to stop. Measure the outcome you care about, using a judge checked against experts, and treat ratings as a side signal.

## Say it

### Your new LLM tutor's prompt looks better in demos. How do you test it in production, and what's your metric?

#### The interviewer pushes further

Follow-up 1 of 3

Why not just use thumbs-up ratings?

They're rare, so the sample is small and biased towards people who like rating things. A student may also rate a tutor highly because it gave the answer, which is exactly what you don't want. They can be a secondary signal, but they don't measure learning.

Follow-up 2 of 3

The new model wins on the judge's score but costs three times more. What do you do?

That's a decision to agree on before the test: how much quality is worth how much cost. I'd look at the real outcomes too, not only the judge. I'd also test whether routing only the hard chats to the stronger model gets most of the gain at much lower cost.

Follow-up 3 of 3

How do you know the judge isn't favouring one model?

I'd have experts label a fresh sample from each version, with the version hidden, then compare judge accuracy per version. If the judge is much less accurate for one, the comparison isn't fair, and I'd fix the judge before trusting the result.

#### The 30-second answer

First I'd clarify what good means, because students can enjoy a tutor that gives away answers. I'd pick a metric tied to learning, like cognitive engagement, and have experts label real chats against a rubric, checking they agree with each other. Then I'd tune an LLM judge until it matches them on unseen data, and score a sample of production chats nightly. New prompts first run offline against those labels, as a filter. Live, I'd randomise by chat thread if quality is about one conversation, or by user for long-term learning, and analyse with that in mind. The primary metric is the judge's score plus a real outcome like skills learned. Guardrails are giving away answers, wordiness, latency, cost and safety. A noisy judge shrinks the visible effect by two times accuracy minus one, so judge quality directly sets the runtime. I'd keep validating the judge, hide which version wrote each chat, watch for novelty, and roll out from a small share.

**Key terms and sources**

Based on an education company's approach, from [a vendor's account of Khan Academy's webinar](https://www.growthbook.io/blog/what-i-learned-from-khan-academy-about-a-b-testing-ai), not from the team's own paper. The volumes, assumed judge accuracy and lab are our own illustrations. Uses randomisation, sample size and LLM as a judge. · checked 5 Nov 2026
