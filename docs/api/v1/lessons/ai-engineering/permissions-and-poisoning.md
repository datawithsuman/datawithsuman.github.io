# Permissions and Poisoning in RAG

> How do you stop users retrieving documents they can't see, or attackers planting bad ones?

- Track: AI Engineering › RAG › Lessons
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/ai-engineering/permissions-and-poisoning/
- Before this: RAG End to End (`ai-engineering/rag-end-to-end`), Guardrails and Prompt Injection (`ai-engineering/guardrails-and-prompt-injection`)
- Quiz topic: `rag`

## Intuition

### The situation

You're adding company-wide search over HR files, contracts and engineering docs. During a test, an intern's question returns a line from a salary document. Separately, a planted wiki page changes what the assistant says about expense limits. The interviewer asks:

> How do you stop users retrieving documents they can't see, or attackers planting bad ones?

#### Why it matters

Enterprise RAG is a common interview topic, and permissions are where naive designs fail. Guardrails and prompt injection covers attacks through the prompt. This lesson covers those that come through the index, and how to keep each user's data apart.

### The idea

Think of a records office. The clerk who fetches files must check your badge before going to the shelves, not after reading the file aloud. If the badge reader breaks, the office closes, and doesn't let everyone in. And anyone who can slip a false page into a folder can change what the clerk reports.

[Figure: Three defences. Check access before retrieval. Fail closed. Treat retrieved text as untrusted.]

_Filter before anything reaches the model._

### Play

**Try to break it.** Lower the share the user can see. Then set failures to search anyway.

#### Check the access path

Illustrative arithmetic, for 100 candidates spread evenly. Filter during search assumes your index keeps good recall under the filter. A live check is near-instant, as the source system answers directly.

If a user can see **5%** of documents, filtering after search leaves about 5 of the 10 results you wanted, and at **1%** only 1. Filtering during search fixes that, but a person removed from a project can still retrieve its documents until the next sync, up to 6 hours here. A **live check** closes that window, at the cost of extra calls. Now set the failure mode to **search anyway**: a brief outage in the permission service exposes every document to every user. That single setting matters more than the rest of this design.

**Now say why:** why does filtering after search return so few results?

## How it works

### How it works

#### In one breath

A RAG system can leak what a user was never allowed to see, because the search index and the LLM don't know your permissions. So **check access at retrieval**, using one of three models: forward the user's identity, filter on cached permissions and re-check live, or give access by parent folder and filter on it. Always **fail closed**: if a check breaks, return nothing. Retrieved text is also an attack surface. **Corpus poisoning** plants documents to steer answers, and injected instructions can hide in them. Treat retrieved text as untrusted data.

#### Access and attacks

##### Three ways to enforce access

| Model | How | Strength | Weakness |
|---|---|---|---|
| **Forward identity** | Search with the user's own token, and the data platform applies its rules | One source of truth | The platform must support it |
| **Cached ACLs + live check** | Filter on permissions copied to the index, then check candidates at the source | Revocation shows up quickly | Extra calls and latency |
| **Parent-level filter** | Give roles on folders or workspaces. Each chunk stores its parent ID, and one call lists the user's parents | Few writes, and no per-document sync | Exceptions need extra handling |

These three models and the fail-closed rules below are from WorkOS, a vendor that sells authorization, so treat them as one informed view.

##### Rules that prevent leaks

- **Fail closed:** if the permission call fails, return nothing. If a live check errors, drop that candidate.

- **An empty list means nothing:** a user with no folders must get an empty result, and not an unfiltered search.

- **No shared super-user:** don't fall back to the app's own all-access account.

- **Filter before ranking:** and watch for filters that break recall.

- **Remember the caches:** semantic caches and prefix caches can also leak across users. Key them by tenant.

##### Poisoning the corpus

PoisonedRAG showed that an attacker who adds just 5 crafted texts for a target question, into a database of millions, could reach about 90% attack success. Any source that outsiders can edit is exposed: public web pages, uploaded files, support tickets and wikis.

- **Real pipelines change the picture:** a 2026 study found many attacks weaken once chunking and re-ranking are involved, though attacks built for those stages recover.

- **One document can be enough:** several 2026 attacks work with a single planted document.

- **Measure carefully:** "Prevented is Not Protected" found that defences judged by attack success rate alone can introduce new failures, and that the choice of metric can change which defence ranks best.

##### Defence in layers

1. **Control sources:** know who can write to the index, and label or weight untrusted ones.

2. **Keep provenance:** store where each chunk came from, so you can find and remove bad ones.

3. **Treat text as data:** never let retrieved text act as instructions, and limit what tools can do.

4. **Check outputs:** require citations, and review sensitive actions.

#### The maths

$$ \text{results} = \min\big(k,\ c \times p\big) $$

Simple arithmetic, assuming visible documents are spread evenly among results. Real results may be better or worse.

- **results left after post-filtering**: What you can actually show the user.

- **results you want**: Often 10 or fewer.

- **candidates searched**: How many results you fetch before filtering.

- **share the user can see**: If a user can see only 1% of documents, 100 candidates leave about 1 result.

## In practice

### In practice

#### In practice

- **Test with real identities:** keep automated tests where user A asks for user B's document, and must fail.

- **Log every retrieval:** record who got which chunks. You'll need it to investigate a leak.

- **Handle deletion:** removing a document must remove its chunks, caches and summaries. See Keeping an Index Current.

- **Separate tenants:** large customers may need their own index or namespace, not only a filter.

- **Summaries can leak:** a graph or summary built across documents may mix what different users can see.

### The answer that sounds right

#### "We'll tell the LLM not to reveal restricted documents"

It sounds right, since LLMs follow instructions. But a prompt isn't a security boundary. Once the text is in the context, it can come out through the answer, a clever question or the logs. Keep restricted text out of the context altogether.

## Say it

### How do you stop users retrieving documents they can't see, or attackers planting bad ones?

#### The interviewer pushes further

Follow-up 1 of 3

Why not filter results after the LLM answers?

By then the model has read the text, and it can appear in the answer, in a summary, or in logs. Filter before anything reaches the model.

Follow-up 2 of 3

A user's access was removed an hour ago, but they can still find the document. Why?

Permissions are probably copied into the index and synced periodically. Add a live check against the source for each candidate, or shorten the sync, and decide what delay you can accept.

Follow-up 3 of 3

How would you find out your corpus was poisoned?

Provenance first: which source added the chunks behind a bad answer? Watch for documents that rank highly for many queries, new sources with unusual influence, and answer changes after ingest. Then remove them, and re-test.

The index and the LLM don't know permissions, so I'd enforce them at retrieval. I could forward the user's identity to a platform that applies its own rules, filter on cached permissions and re-check candidates live, or assign roles at folder level and filter by parent ID. I'd fail closed: if the check breaks, return nothing, and an empty list must never become an unfiltered search. I'd watch revocation delay, and cover caches too. For poisoning, PoisonedRAG reached about 90% attack success with 5 planted texts, so I'd control who can write to the index, keep provenance, treat retrieved text as data rather than instructions, and limit what tools can do.

**Key terms and sources**

Three ways to enforce access control, why to fail closed, revocation delays, corpus poisoning, why attack success rate isn't enough, and layered defences.

#### Sources

- WorkOS, Authorization for RAG at scale

- WorkOS, RAG access control and document permissions

- Zou et al., PoisonedRAG

- When Poison Fails After Retrieval

- Prevented is Not Protected: What Attack Success Rate Hides about RAG

- Retrieved But Not Reliable: A Survey on Attacks and Defenses in RAG

Explanations are ours, built from these sources. Lab numbers are illustrative unless a lab says otherwise. Most recent papers are preprints.
