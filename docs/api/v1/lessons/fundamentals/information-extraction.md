# Information Extraction: Relations, Coreference and Entity Linking

> How do you turn messy text into structured facts, and how far do LLMs replace this work?

- Track: Fundamentals › NLP Fundamentals › Tagging, retrieval and evaluation
- Type: Concept · 18 min
- Page: https://aimlrounds.com/tracks/fundamentals/information-extraction/
- Before this: Sequence Labelling and NER (`fundamentals/sequence-labelling-and-ner`), BERT and Masked Language Models (`fundamentals/bert-and-masked-language-models`)
- Quiz topic: `nlp`
- Sources checked: 2026-11-07 · Text last changed: 2026-11-20 · Version: 3b81269f91

## Intuition

### The situation

You have thousands of restaurant descriptions, and you want a table of who owns what, where and since when. A simple pattern gets some facts, but marks "It" as a restaurant and treats two names for one place as separate. The interviewer asks:

> How do you turn messy text into structured facts, and how far do LLMs replace this work?

#### Why it matters

Companies hold huge amounts of text, and they want to search it, count it and join it with tables. This is behind knowledge graphs, contract and invoice processing, and better retrieval. It extends NER from names to facts.

### The idea

Think of a detective reading statements. They note who's named, work out who "he" and "she" refer to, match names against known records, and write down what connects whom. Miss one step, and the case file has the wrong person in it.

[Figure: Three linked steps. Coreference resolves pronouns. Entity linking finds the record. Relation extraction finds the fact.]

_Mistakes at each step pass to the next._

### Play

**Try to break it.** Tick each step alone. Then tick both.

#### Run the pipeline

_"Spice Route opened in Hyderabad in 2010. It serves biryani. Spice Route Kitchen later moved to Pune. Its founder is Meera Rao."_

A made-up restaurant, with a hand-written example of what a simple pattern-based extractor returns. A fact is correct only if subject, relation and object all match.

Tick each step on its own, then both. Neither is enough alone, as they fix different mistakes. Coreference alone resolves "Its" to the nearest name, Spice Route Kitchen, which still isn't the main record. That's how an error at one step can become a wrong fact later.

**Now say why:** why isn't coreference alone enough here?

## Maths

### Maths

#### In one breath

**Information extraction** turns text into structured facts, like (Spice Route, opened in, Hyderabad). NER finds the names. **Coreference** works out that "it" means Spice Route. **Entity linking** connects a name to one record in a database. **Relation extraction** finds how entities are connected. Each step's mistakes pass to the next. LLMs with a schema are now a fast way to start, but they still need checking, and specialised models can do better on some benchmarks.

#### The pipeline

| Step | Question | Example |
|---|---|---|
| **NER** | What are the names? | Spice Route, Hyderabad, 2010 |
| **Coreference** | Which mentions mean the same thing? | "It" means Spice Route |
| **Entity linking** | Which real-world record is it? | "Spice Route Kitchen" is record #4821 |
| **Relation extraction** | How are they connected? | (Spice Route, opened in, Hyderabad) |

##### Relation extraction: four approaches

| Approach | How it works | Trade-off |
|---|---|---|
| **Patterns** | Rules like "X opened in Y". | Precise and explainable, with low recall. |
| **Supervised** | Train a classifier on labelled sentences. | Accurate, but labelling is expensive. |
| **Distant supervision** | Take facts from a database. Label sentences that mention both entities. | Cheap and large, but noisy. |
| **LLM with a schema** | Ask for JSON in a fixed format. | Fast to start. Needs checks on cost and accuracy. |

Distant supervision's problem: a sentence mentioning both a founder and their company might not say that they founded it.

##### Coreference

Older systems had several steps. Lee et al. instead consider every span as a possible mention, and learn which earlier span it refers to, reaching a gain of 1.5 F1 on OntoNotes. It stays hard, because it can need world knowledge: in "the trophy didn't fit in the suitcase because it was too big", "it" means the trophy.

##### Entity linking

"Paris" may be a city or a person. BLINK works in two stages, like search: a bi-encoder quickly retrieves candidates, and a cross-encoder re-ranks them. It linked against 5.9 million candidates in 2 milliseconds, and can handle entities it never saw in training, because it reads their descriptions.

##### How far do LLMs replace this?

Prompted LLMs need no labelled data and handle new relations easily. But Han et al. reported "a visible performance gap between GPT-4 and state-of-the-art (SOTA) IE methods" on standard benchmarks. A common approach is to prototype with an LLM, check it on labelled examples, and move high-volume stable tasks to a smaller model if it pays off.

#### The maths

$$ {P = \frac{|\text{predicted} \cap \text{gold}|}{|\text{predicted}|}}, \quad {R = \frac{|\text{predicted} \cap \text{gold}|}{|\text{gold}|}}, \qquad {s(i,j) = s_m(i) + s_m(j) + s_a(i,j)} $$

A fact usually counts only if subject, relation and object all match. The coreference score is the form used by Lee et al.

- **fact-level precision**: The share of extracted facts that are correct.

- **fact-level recall**: The share of true facts that were found.

- **a coreference score**: Is span i a mention? Is span j? Could j be what i refers to? The model picks the best earlier span.

## In practice

### In practice

#### In practice

- **Define the schema first:** decide on entities, relations and allowed values, and add examples of what doesn't count.

- **Label a small test set:** even with an LLM, you need labelled documents to measure accuracy.

- **Measure fact-level F1:** report by relation, and look at errors at each step of the pipeline.

- **Keep the evidence:** store the source sentence with each fact, so people can check it.

- **Check LLM output:** use structured output for the format, but a valid format doesn't mean the facts are right. Validate against the source and your database.

### The answer that sounds right

#### "The LLM returned valid JSON, so extraction is solved"

It sounds right, as the output looks clean. But a schema only guarantees the format, and values can still be invented or attached to the wrong entity. Measure field-level accuracy on labelled documents, keep the source sentence, and check that it really appears in the text.

## Say it

### How do you turn messy text into structured facts, and how far do LLMs replace this work?

#### The interviewer pushes further

Follow-up 1 of 3

What's the distant supervision assumption, and why is it weak?

It assumes that if a database says two entities have a relation, a sentence mentioning both expresses it. Many such sentences don't, so labels are noisy. Methods treat this as learning from groups of sentences, where at least one should express the relation.

Follow-up 2 of 3

How is entity linking like search?

A mention is the query, and the database is the collection. BLINK retrieves candidates with a bi-encoder, and re-ranks with a cross-encoder, which mirrors retrieval and re-ranking. Reading entity descriptions also allows it to link new entities.

Follow-up 3 of 3

You extract contracts with an LLM, and the JSON is always valid. Is it accurate?

Not necessarily. A schema only guarantees the format. Values can still be invented or wrong. Compare with a labelled set by field, require a supporting quote, check it appears in the document, and send low-confidence cases to people.

#### The 30-second answer

Information extraction turns text into structured facts. NER finds names, coreference connects "it" to its antecedent, entity linking maps names to database records, and relation extraction finds the links between them. For relations, I can use patterns, supervised models, distant supervision or an LLM with a schema. Distant supervision is cheap, but noisy, because mentioning two entities doesn't mean stating a relation. I'd start with an LLM and a strict schema, measure fact-level precision and recall on a labelled set, and keep the source sentence for checking. For a high-volume stable task, I'd consider a smaller trained model.

**Key terms and sources**

Relation extraction, distant supervision, coreference resolution, entity linking, how to evaluate extracted facts, and using LLMs with a schema. · checked 7 Nov 2026

#### Sources

- [Mintz et al., Distant Supervision for Relation Extraction](https://aclanthology.org/P09-1113/)

- [Lee et al., End-to-end Neural Coreference Resolution](https://arxiv.org/abs/1707.07045)

- [Wu et al., BLINK: Scalable Zero-shot Entity Linking](https://arxiv.org/abs/1911.03814)

- [Han et al., An Empirical Study on Information Extraction using LLMs](https://arxiv.org/abs/2305.14450)

- [Jurafsky and Martin, chapter 21: Information Extraction](https://web.stanford.edu/~jurafsky/slp3/21.pdf)

- [Jurafsky and Martin, chapter 24: Coreference and Entity Linking](https://web.stanford.edu/~jurafsky/slp3/24.pdf)

Explanations are ours, built from these sources. Lab numbers are illustrative, and worked examples were checked by calculation.
