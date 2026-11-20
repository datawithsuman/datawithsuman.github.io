# Design an AI Tutor

> Students working on maths problems can ask an AI tutor for help. Design it so it guides them to the answer instead of giving it away, is fast and correct, and provably helps them learn.

- Track: System Design › LLM Apps and Chatbots › Designs
- Type: Design · 25 min
- Page: https://aimlrounds.com/tracks/system-design/design-ai-tutor/
- Before this: Prompt Engineering Patterns (`ai-engineering/prompt-engineering-patterns`), RAG Evals: Retrieval, Faithfulness and Relevance (`ai-engineering/rag-evals`)
- Quiz topic: `sdllm`

## Intuition

### The situation

An education platform wants an AI tutor beside its maths practice problems, for millions of students, many under 13. Teachers worry it will just give answers. Leadership wants proof that it helps students learn. The interviewer asks:

> Students working on maths problems can ask an AI tutor for help. Design it so it guides them to the answer instead of giving it away, is fast and correct, and provably helps them learn.

#### Ask before designing

- **Users:** school students, many of them under 13, plus teachers and parents who need visibility.

- **Subjects:** start with maths practice problems, where right and wrong can be checked.

- **Scale:** say 2 million tutoring threads a week, mostly during school hours.

- **Teaching goal:** the tutor should not give away answers; it should help students work them out.

- **Must never happen:** wrong maths stated confidently, unsafe conversations with children, or student data used without consent.

- **Success metrics:** learning, not chat volume: does the student solve the next problem alone? Plus response time, maths error rate and how often answers are given away.

### The idea

Think of a good private tutor. They already know what you got wrong last week, ask what you'd try first rather than solving it for you, double-check their own arithmetic, and judge themselves by whether you can do the next problem alone.

[Figure: The tutor sees the problem and a summary of the student's work, guides instead of telling, has its maths checked, and every change is tested on learning.]

_Learning is the metric; chat is just the medium._

### Play

**Try to break it.** Turn on example problems alone. Then the two context changes. Then the speed changes.

#### Ship only what moves learning

Changes are the post's measured A/B results (each over hundreds of thousands to over a million threads). The 8-second starting response time is our assumption, and adding the effects together is our simplification; the post reports a combined 6.1% for the two context changes.

Turn on the context changes: each one helps a few percent, and together they add up. Example problems change nothing, so in a real team they'd only ship if harmless. The speed changes don't move learning directly, but they make the tutor usable and cheaper. **No single change was a big leap**; steady, measured improvements were.

**Now say why:** why ship a change that doesn't improve learning but makes replies faster?

## Architecture

### Architecture

#### In one breath

A tutor that hands out answers is easy and useless. Prompt it to **guide**: ask for the next step, give hints, keep tone encouraging. Give it the **student's context**, like recent attempts and missing prerequisite skills, in a clean structured form. Check its **maths** with a separate verification step, keep it **fast**, protect children with **moderation**, and judge every change with **A/B tests on learning**, such as whether the student gets the next problem right on their own.

#### One tutoring turn

1. **Context:** the tutor sees the problem the student is on, plus structured learning data: recent attempts, skill levels and prerequisites they haven't mastered.

2. **Tutoring prompt:** sets the tone and method: ask what the first step might be, give hints, praise effort, redirect off-topic chat, and don't reveal the answer before the student tries.

3. **Draft reply:** the LLM writes a response.

4. **Maths check:** a separate step verifies calculations and expressions, but only when the reply contains maths, to save time.

5. **Safety:** moderation stops inappropriate conversations and alerts teachers or parents.

6. **Log and learn:** threads, outcomes and metrics feed evaluation and A/B tests.

##### Context is the lever

A tutor that only sees the current problem can't tell a student who's stuck on fractions from one who misread the question. Passing in a summary of recent attempts and missing prerequisites lets it pitch the hint correctly. Raw, messy logs don't help; clean, meaningful summaries do.

##### Speed matters twice

Slow replies lose students' attention, and every extra second across millions of threads costs money. Choose faster models for checks, keep outputs short, and skip steps that aren't needed.

#### The numbers worth saying out loud

All of these are assumptions for the interview, not figures from a real system.

| Question | Working | Result |
|---|---|---|
| Turns a week | 2 million threads × 6 turns | **12 million** |
| Peak turns per second | 12 million ÷ 5 school days ÷ 6 hours ÷ 3,600 × 2 | **about 220** |
| LLM calls per turn | tutor + maths check (about half the time) + moderation | **about 2.5** |
| Threads per group to detect a 2–3% relative change in a rate around 60% | 16 × 0.6 × 0.4 ÷ (0.012 to 0.018)²; more if one student's threads are correlated | **about 12,000–27,000** |

Learning effects are small, so tests need large samples; at this volume, a test can still finish in days.

## In practice

### In practice

#### What every tutor design gets asked

- **What to measure:** next-item correctness without help, cognitive engagement (passive, active or constructive), plus guardrails: answers given away, maths errors and response time.

- **Shipping rule:** ship only with a high probability of improvement, say above 95%, and no harm to any guardrail.

- **Maths correctness:** LLMs make arithmetic mistakes, so verify with a separate checker, and don't let the tutor contradict a student's correct work.

- **Prompting:** test prompts with varied student personas before release, and fix repeated complaints, such as the tutor repeating itself or using emojis in serious moments.

- **Children's safety and privacy:** moderation that stops inappropriate chats and informs adults, plus compliance with student-privacy law.

- **Memory:** pass meaningful, structured summaries of past work rather than raw logs; the post found raw logs had no measurable effect at first.

##### Rollout

Pilot with a few classrooms, observe and interview, then A/B test one change at a time at scale, keeping what helps and discarding what doesn't.

#### What the real system reported

- **Testing:** about 20 substantive A/B tests from October 2025 to April 2026, over more than 15 million tutoring threads. A change ships only if its chance of being better is above 0.95 with no harm to guardrails.

- **Metrics:** response time, next-item correctness without help, and cognitive engagement; guardrails include giving answers away, maths errors and interactions per thread.

- **Context:** recent attempts +3.4% next-item correctness; prerequisite skills +2.7%; together 6.1%. Including the prior 24 hours of related threads raised cognitive engagement by 5.09%.

- **Speed:** a faster maths checker saved 0.3 s; concise output about 3 s; limiting it to the student's own maths saved 0.4 s more and halved answers given away; a pre-check saved about 0.3 s.

- **No effect:** example problems and extra content links; raw, hard-to-parse logs.

The organisation's own figures. The posts don't name models or describe the maths checker's internals.

### The answer that sounds right

#### "Students love it, so it's working"

It sounds right, since engagement and ratings look good. But students often enjoy a tutor that does the work for them, which is exactly what stops learning. Measure whether they solve the next problem alone, and treat answers given away as a guardrail.

## Say it

### Students working on maths problems can ask an AI tutor for help. Design it so it guides them to the answer instead of giving it away, is fast and correct, and provably helps them learn.

#### The interviewer pushes further

Follow-up 1 of 3

Why not measure success by how long students chat?

Long chats can mean confusion, or a student getting the tutor to do the work. I care whether they can solve the next problem alone, so that's the main metric, with chat length only as a guardrail.

Follow-up 2 of 3

The tutor sometimes states wrong maths. What do you do?

Add a verification step that checks calculations and expressions before the reply is shown, track the maths error rate as a guardrail, and limit the checker to the student's own work so it stays fast and focused.

Follow-up 3 of 3

Should the tutor remember students across days?

Useful context helps, but it should be meaningful summaries of their work, like skills and recent attempts, under strict privacy rules. Raw transcripts mostly add noise and risk.

#### The 30-second answer

First I'd clarify the students' ages, the subject, the volume, and that the goal is learning, not chat. The tutor sees the current problem plus structured learning data: recent attempts, skill levels and missing prerequisites, as clean summaries rather than raw logs. The prompt sets the method: ask for the next step, give hints, encourage, and never reveal the answer before the student tries. The LLM drafts a reply, and a separate checker verifies any maths, called only when needed to save time. Moderation stops unsafe conversations and informs teachers or parents, and student data follows privacy law. I'd measure next-problem correctness without help and engagement quality, with guardrails on answers given away, maths errors and response time. Every change is an A/B test that ships only with a high chance of improvement and no guardrail harm. I'd expect steady, small gains rather than one big win, and I'd pilot in classrooms before scaling.

**Key terms and sources**

Based on an education nonprofit's published learnings: [Khan Academy's "How Khan Academy Is Building a Better AI Tutor: Our Most Recent Learnings"](https://blog.khanacademy.org/?p=21314) (2026) and its [prompt engineering approach](https://blog.khanacademy.org/khan-academys-7-step-approach-to-prompt-engineering-for-khanmigo). The baseline response time in the lab and the estimate are ours; the changes are the post's. Uses prompt patterns, context engineering and evaluation. · checked 5 Nov 2026
