# Design Job Recommendations

> A professional network recommends jobs to hundreds of millions of members and candidates to recruiters. Design job recommendations that match on meaning, handle new postings instantly and help both sides.

- Track: System Design › Recommendation Systems › Designs
- Type: Design · 25 min
- Page: https://aimlrounds.com/tracks/system-design/design-job-recommendations/
- Before this: Embeddings and Representation Learning (`fundamentals/embeddings`), Contrastive Learning (SimCLR, CLIP) (`fundamentals/contrastive-learning`)
- Quiz topic: `sdrec`
- Sources checked: 2026-11-15 · Text last changed: 2026-11-20 · Version: 62eb5f0dcc

## Intuition

### The situation

A professional network has over a billion members and tens of millions of active job postings. Members complain that recommended jobs match keywords but not their real skills, and recruiters get floods of unqualified applicants. The interviewer asks:

> A professional network recommends jobs to hundreds of millions of members and candidates to recruiters. Design job recommendations that match on meaning, handle new postings instantly and help both sides.

#### Ask before designing

- **Surfaces:** recommended jobs, job search, and "top applicant" jobs; also candidates for recruiters.

- **Scale:** over a billion members and tens of millions of active postings.

- **Freshness:** a new posting should be recommendable right after it's published.

- **Must never happen:** recommending based on protected characteristics, or flooding a few jobs with unqualified applicants.

- **Success metrics:** qualified applications, dismiss-to-apply ratio, recruiter responses, and fairness across groups.

### The idea

Think of a good recruiter friend. They understand that 'data wrangler' and 'ETL engineer' are the same job, know who moved from your role into which roles, and only introduce you where both sides will be glad.

[Figure: A fine-tuned LLM embeds jobs and profiles. A graph model adds relationships. Nearest-neighbour search retrieves jobs. A ranker predicts apply and recruiter response.]

_A good match is good for both sides._

### Play

**Try to break it.** Add LLM embeddings. Then remove the categorical features.

#### Swap hand-built features for LLM embeddings

From the paper's Table 4. Removing features is only shown with LLM embeddings added.

Add the LLM embeddings: AUC rises, but GPU memory doubles. Then remove the categorical features: memory drops back near the baseline, yet AUC is now a little lower than the baseline. Text embeddings help, but structured features still carry signal.

**Now say why:** why didn't LLM embeddings fully replace the structured features?

## Architecture

### Architecture

#### In one breath

Matching is two-sided: a good recommendation is a job the member applies to **and** where the recruiter responds. Embed job postings and member profiles with a **fine-tuned LLM** in a two-tower setup, so "data wrangler" matches "ETL engineer". Add a **graph** of members, jobs, skills and companies to capture relationships text can't. Regenerate embeddings **nearline** whenever a posting or profile changes. Retrieve, rank, and watch both sides' outcomes.

#### LLM embeddings, a graph, then ranking

1. **Text embeddings:** one fine-tuned 7B LLM embeds jobs and member profiles and resumes, with a different prompt per input type, trained on applications versus skips.

2. **Graph embeddings:** a graph neural network over members, jobs, recruiters and skills uses the LLM embeddings as node features and learns relationships, like members with similar careers applying to similar jobs.

3. **Retrieval:** nearest-neighbour search on embeddings finds candidate jobs for a member.

4. **Ranking:** a ranking model uses the embeddings plus other features to predict apply and response, and orders the list.

5. **Nearline updates:** every posting or profile change triggers a stream event; if the text really changed, the embedding is regenerated and written to the online store and to the training logs.

##### Why two towers?

A cross-encoder that reads a job and a profile together is more accurate, but you can't run it over millions of pairs. Two towers embed each side once; you can then distil some of the cross-encoder's accuracy into them.

#### The numbers worth saying out loud

All of these are assumptions for the interview, not figures from a real system.

| Question | Working | Result |
|---|---|---|
| Profile and posting updates a day | given | **20 million** |
| Real text changes | skip unchanged text, about 1 in 3 | **about 7 million** |
| LLM embedding calls a second | 7 million ÷ 86,400 × 3 at peak | **about 240** |
| Embedding storage | 1 billion members × 4,096 dims × 2 bytes | **about 8 TB** |

Skipping unchanged text is a large saving, and the 4,096-dimension vectors are a big storage and latency cost, which is a reason to shrink them.

## In practice

### In practice

#### What every job recommender gets asked

- **Labels:** applications are rare compared with skips and clicks, so balance positives and negatives; start from relevance labels, then align with engagement.

- **Hard negatives:** semi-hard negatives in the contrastive loss avoid pushing apart pairs that are actually good matches.

- **Cold start:** content embeddings let a brand-new posting or member be matched immediately; the graph helps members who haven't searched recently through people like them.

- **Two-sided health:** cap how often one job is shown so a few postings don't get flooded; reward matches where recruiters respond.

- **Model upgrades:** a new embedding model changes the vector space. Learn a linear map from new vectors to old ones so downstream models keep working during the switch.

- **Fairness:** check AUC and outcomes across groups such as gender, seniority and location.

#### What the real systems reported

- **LLM embeddings:** a fine-tuned 7B model (LoRA) with a contrastive loss; embeddings regenerate nearline at over 200 queries a second and about 270 ms end to end, and unchanged text is skipped.

- **Graph:** 763 million nodes and 12.3 billion edges over six months of activity.

- **Online tests:** total applies +1.5% and dismiss-to-apply −3.2% for job recommendations and search; recruiter messages accepted +3.0%.

- **The embedding platform:** qualified applications +2.07%, dismiss-to-apply −5.13% and total applications +1.91%, the team's biggest gain from one model change in that half year; p95 latency under 300 ms for the 7B model.

From the paper (KDD 2025) and the post (May 2025). The paper claims cold-start benefits but doesn't test them separately.

### The answer that sounds right

#### "Recommend the jobs each member is most likely to apply to"

It sounds right, but it floods popular postings with weak applicants and ignores whether recruiters respond. Optimise for qualified applications and recruiter replies, and cap how often one job is shown.

## Say it

### A professional network recommends jobs to hundreds of millions of members and candidates to recruiters. Design job recommendations that match on meaning, handle new postings instantly and help both sides.

#### The interviewer pushes further

Follow-up 1 of 3

Why not use a cross-encoder for everything?

It reads each job–member pair together, which is too slow for millions of pairs. Two towers embed each side once; distil some cross-encoder accuracy into them, or use it to rerank a short list.

Follow-up 2 of 3

A new posting gets no recommendations for a day. What's wrong?

Embeddings are being built in a daily batch. Generate them nearline from the posting's change event and write them to the online store within seconds.

Follow-up 3 of 3

You upgrade the embedding model. What breaks?

Downstream models trained on old vectors. Learn a mapping from new to old vectors for the transition, or retrain them together.

#### The 30-second answer

I'd clarify the surfaces, scale, freshness and that matching is two-sided. I'd embed jobs and member profiles with one fine-tuned LLM in a two-tower setup, using different prompts per input type and a contrastive loss with semi-hard negatives, so meaning matches beyond keywords. A graph neural network over members, jobs and skills adds relational signals, using the LLM embeddings as features. Retrieval is nearest-neighbour search, then a ranker predicts apply and recruiter response. Embeddings update nearline on every real text change, so new postings are recommendable immediately. I'd measure qualified applications, dismiss-to-apply and recruiter responses, cap exposure per job, check fairness across groups, and handle embedding model upgrades with a compatibility mapping.

**Key terms and sources**

Based on a professional network's published work: the paper ["A Scalable and Efficient Signal Integration System for Job Matching"](https://arxiv.org/abs/2507.09797) (KDD 2025) and the post ["JUDE: LLM-based representation learning for job recommendations"](https://www.linkedin.com/blog/engineering/ai/jude-llm-based-representation-learning-for-linkedin-job-recommendations) (May 2025). The lab uses the paper's own numbers; the estimate is ours. Uses embeddings, contrastive learning and LoRA. · checked 15 Nov 2026
