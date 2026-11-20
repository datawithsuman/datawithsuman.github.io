# Design Recommendations for a New Category

> A delivery app with years of restaurant orders launches grocery and retail. Most users have never shopped there. Design recommendations for users who are new to the category.

- Track: System Design › Recommendation Systems › Designs
- Type: Design · 25 min
- Page: https://aimlrounds.com/tracks/system-design/design-cross-category-cold-start/
- Before this: Ranking Metrics (`fundamentals/ranking-metrics`), LLM Judges: Pairwise Preferences and Pass/Fail Checks (`ai-engineering/llm-as-a-judge`)
- Quiz topic: `sdrec`

## Intuition

### The situation

A food delivery app with years of restaurant orders has launched grocery, retail and beauty. Most users have never shopped in these new categories, so the ranker knows nothing about their tastes there. The interviewer asks:

> A delivery app with years of restaurant orders launches grocery and retail. Most users have never shopped there. Design recommendations for users who are new to the category.

#### Ask before designing

- **Verticals:** restaurants are data-rich; grocery, retail and beauty are newer and sparse.

- **Users:** "cold-start" users who are new to the new verticals, and "power" users already active there.

- **Existing system:** a multi-task ranker predicting clicks, add-to-cart and purchases from engagement features.

- **Must never happen:** invented categories outside the taxonomy, or LLM costs growing with every page view.

- **Success metrics:** ranking AUC and MRR on conversions, overall and per user group, then online tests.

### The idea

Think of a friend who knows your restaurant habits. You've never been grocery shopping together, but they can guess you'd want naan and good spices, because of all that Indian takeaway.

[Figure: Restaurant orders and searches go to an LLM, which outputs confident affinities over the new category's taxonomy. A daily batch stores them. The ranker uses them as features.]

_Translate what you know about users into the new category._

### Play

**Try to break it.** Compare all users, cold-start users and power users.

#### Different signals help different users

From the paper, offline on a 15-day holdout. Lifts are relative; no significance tests are reported. A shadow test on live traffic gave +4.3% AUC and +3.2% MRR.

Look at cold-start users: their order history from restaurants is what carries over. Power users already shop in the category, so their searches add fresh intent.

**Now say why:** why do restaurant orders help cold-start users most, and searches help power users most?

## Architecture

### Architecture

#### In one breath

A user new to grocery still has a **restaurant history** and **searches**. Ask an LLM to turn those into **affinities** over the grocery taxonomy (Indian takeaway → naan, specialty breads), coarse levels first, then finer ones. Keep only **confident** outputs, cache the fixed prompt, use a small model and update only when the user acts. Check feature quality with people and an LLM judge, then add the affinities as features to the existing **multi-task ranker**.

#### LLM-made features, used by the existing ranker

1. **Inputs:** each user's recent restaurant orders (restaurant and items, newest first) and recent searches.

2. **Hierarchical generation:** the LLM first picks broad categories, which limit the choices at the next, finer level. Coarsest levels are too vague and the finest too sparse, so keep the middle two.

3. **Output control:** strict JSON, exact taxonomy names only, a confidence per affinity, and keep only those at 0.8 or above.

4. **Two profiles:** long-term affinities from orders, short-term intent from searches.

5. **Materialise:** a daily batch writes affinities to the data lake for training and an online feature store for serving.

6. **Rank:** the ranker embeds each affinity ID list, averages it, and concatenates it with existing user features before the shared layers and task heads.

#### The numbers worth saying out loud

All of these are assumptions for the interview, not figures from a real system.

| Question | Working | Result |
|---|---|---|
| Users | given | **30 million** |
| Users who act on a given day | 30 million × 20% | **6 million LLM calls** |
| Tokens a day | 6 million × 1,500 new tokens (taxonomy cached) | **9 billion** |
| Serving cost | a feature store lookup per request | **no LLM in the request path** |

The LLM never runs when a page loads; it runs in a daily batch, and only for users with new activity.

## In practice

### In practice

#### What every cold-start design gets asked

- **Cost:** a smaller model gave comparable quality here; caching the fixed instructions and taxonomy, and updating only on new actions, cut cost by about 80%.

- **Feature quality:** people rated 1,000 samples per signal for how personalised they were, and an LLM judge rated the same; search-based affinities rated higher, as search intent is explicit.

- **Hallucinated categories:** require exact taxonomy names, validate outputs, and drop anything not in the taxonomy.

- **Why features, not LLM ranking:** the ranker stays fast and well-understood; the LLM only adds a signal it was missing.

- **Other cold-start tools:** popular and trending items, onboarding questions, and exploration still matter, especially for users with no history at all.

- **Next steps:** use affinities in retrieval too, and add session-level signals.

#### What the real system reported

- **Setup:** a four-level product taxonomy, a 20% sample of three months of users, temperature 0.1 and a 0.8 confidence cut-off.

- **Model:** a smaller model matched the larger one's quality for this task at much lower cost; overall cost fell about 80%.

- **Quality:** 53% of order-based and 71% of search-based affinities were rated highly personalised by people.

- **Ranking:** offline AUC +4.4% and MRR +4.8% for all users; +4.0% and +1.1% for cold-start users; a shadow test on live traffic gave +4.3% and +3.2%.

From the paper. It reports no user-facing A/B test or business metrics.

### The answer that sounds right

#### "Show new users the most popular items"

It's a reasonable fallback, but it ignores the rich history most users already have in the main category. Translating that history into affinities for the new category gave cold-start users a clear lift in ranking quality.

## Say it

### A delivery app with years of restaurant orders launches grocery and retail. Most users have never shopped there. Design recommendations for users who are new to the category.

#### The interviewer pushes further

Follow-up 1 of 3

Why not ask the LLM to rank products directly?

Too slow and costly per page view, and hard to control. Generating features offline adds the missing signal while the fast, tested ranker keeps doing the ranking.

Follow-up 2 of 3

The LLM returns categories that don't exist. What do you do?

Give it the taxonomy, require exact names in strict JSON, validate every output and drop unknown categories, and keep only high-confidence affinities.

Follow-up 3 of 3

Why did cold-start users gain less on MRR than power users?

They have no history in the category, so the affinities are informed guesses; they help separate good items from bad (AUC) more than they nail the single top item (MRR).

#### The 30-second answer

I'd clarify the verticals, which users are new to them, and what ranker exists today. Most new-category users still have a long history in the main category, so I'd use an LLM to translate restaurant orders and searches into affinities over the new category's taxonomy, coarse levels first to narrow the finer ones. Outputs are strict JSON with exact taxonomy names and a confidence, and I keep only confident ones. Orders give long-term affinities and searches short-term intent. A daily batch writes them to a feature store, so there's no LLM in the request path, and I control cost with a small model, prompt caching and updating only active users. The ranker adds them as embedded, averaged features. I'd check feature quality with people and an LLM judge, then measure AUC and MRR by user group and run an online test.

**Key terms and sources**

Based on a delivery company's published paper: ["Mind the Gap: Bridging Behavioral Silos with LLMs in Multi-Vertical Recommendations"](https://arxiv.org/abs/2606.06779) (GenAI for E-Commerce workshop, 2025; arXiv 2026). The lab uses the paper's own numbers; the estimate is ours. Uses ranking metrics, LLM as a judge and feature engineering. · checked 15 Nov 2026
