# Sequence Labelling and NER

> BIO tags, CRFs, and why NER is scored with entity F1.

- Track: Fundamentals › NLP Fundamentals › Tagging, retrieval and evaluation
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/sequence-labelling-and-ner/
- Before this: Text Classification: Naive Bayes vs Logistic Regression (`fundamentals/text-classification`)
- Quiz topic: `nlp`
- Sources checked: 2026-10-29 · Text last changed: 2026-11-20 · Version: 633e786330

## Intuition

### The situation

The app's chat parses "order 2 chicken biryani from Paradise Biryani House in Hyderabad at 8 pm" to place the order automatically. A review classifier gives one label per text, but here you need to know which words are the dish and which the restaurant. The interviewer asks:

> How do you label spans of text, and how should you score it?

**Running example:** the app's chat ordering parses "_order 2 chicken biryani from Paradise Biryani House in Hyderabad at 8 pm_" into QUANTITY, DISH, RESTAURANT, CITY and TIME, so the order can be placed automatically.

#### Labels for spans, not whole texts

A classifier gives one label per review. To place an order we need _which words_ are the dish and _which_ are the restaurant, and entities can be several words long ("Paradise Biryani House"), contain words that look like other entities ("Biryani" inside a restaurant name), or sit right next to each other.

### The idea

Think of marking a sentence with highlighters, one colour per entity type. B- is where you put the pen down. I- is where you keep going. Because every entity starts with a fresh B-, two neighbouring dishes stay two dishes.

[Figure: Paradise is tagged B-REST, Biryani and House are I-REST, in is O, and Hyderabad is B-CITY.]

_BIO tags from the lesson's order. Anything outside an entity is O._

### Play

**Try to break it.** Switch between perfect, boundary errors, wrong types, missed one entity and predict all O. Compare token accuracy with entity F1.

#### Token accuracy vs entity F1

Gold vs predicted BIO tags for the 13-token order. Entity-level scoring (as in the CoNLL shared tasks): a predicted entity counts as correct only if its start, end and type all match a gold entity.

With two **boundary errors** (the model tags "biryani" but not "chicken", and "Paradise Biryani" but not "House"), token accuracy still says **77%**, yet two of the five entities are wrong, so entity F1 is only **0.60** (a missed TIME entity, by contrast, still gives 0.89): the order system would look up the wrong restaurant. Predicting **all O** scores 31% token accuracy here, and on real text, where most tokens are O, it can score over 80% while finding nothing. That's why NER is always reported as entity-level F1.

**Now say why:** with boundary errors, token accuracy still says 77%. Why is entity F1 only 0.60?

## How it works

### How it works

#### In one breath

Many NLP tasks need a label for **every token**, not one for the whole text. **Part-of-speech tagging** labels nouns, verbs and so on; **named entity recognition (NER)** finds spans like dish names, restaurants, cities and times. Spans are turned into per-token labels with the **BIO** scheme: B- marks the beginning of an entity, I- the inside, O outside, so adjacent entities stay separate. Models went from HMMs and **CRFs** (which score whole label sequences, so "I-" can't follow "O") to **BiLSTM-CRF** and now fine-tuned **Transformers** with a classifier per token. NER is evaluated with **entity-level precision, recall and F1**: a span counts only if both its boundaries and type are exactly right. What you'll be able to do after this: convert spans to BIO tags, explain why a CRF layer helps, and compute entity-level F1.

#### The BIO scheme

| token | order | 2 | chicken | biryani | from | Paradise | Biryani | House | in | Hyderabad |
|---|---|---|---|---|---|---|---|---|---|---|
| tag | O | B-QTY | B-DISH | I-DISH | O | B-REST | I-REST | I-REST | O | B-CITY |

- Each entity starts with **B-**; following tokens of the same entity get **I-**; everything else is **O**. With K entity types there are 2K + 1 labels.

- B- is what separates two adjacent entities of the same type: "add biryani raita" as two DISH entities is B-DISH B-DISH; a plain IO scheme would merge them into one.

- Variants: BIOES (also marks the End and Single-token entities). Ramshaw & Marcus (1995) introduced the IOB idea for chunking.

#### From independent guesses to whole-sequence models

- **Naive:** classify each token independently. It can output impossible sequences like O → I-REST (an "inside" with no beginning).

- **HMMs** and **CRFs** (Lafferty, McCallum & Pereira, ICML 2001) score the whole label sequence, including transitions between labels, and decode the best sequence with the Viterbi algorithm.

- **BiLSTM-CRF** (Lample et al., NAACL 2016) used neural features from both directions plus a CRF layer, reaching about 90.9 F1 on CoNLL-2003 English NER.

- **Today:** fine-tune BERT-style encoders with a token classifier (Devlin et al. 2019); subword tokens are labelled by their first piece. LLMs can also extract entities with a prompt and a JSON schema, useful when labelled data is scarce.

To see how whole sequences are decoded, read HMMs, CRFs and Viterbi.

## In practice

### In practice

#### Sequence labelling in practice

- **Information extraction:** pulling dishes, addresses, prices and times from chats, emails and receipts.

- **PII redaction:** tagging names, phone numbers and addresses before logs or training data are stored.

- **Search and query understanding:** "biryani near Koramangala under 300" → DISH, LOCATION, PRICE filters.

- **Benchmarks:** CoNLL-2003 (person, location, organisation, miscellaneous) is the classic English NER dataset (Tjong Kim Sang & De Meulder 2003).

To go from names to facts, read Information Extraction.

### The answer that sounds right

#### "Report token accuracy"

It sounds right, since every token gets a label and you can count the correct ones. But most tokens are O, so on real text, predicting all O can score over 80% while finding nothing. In the lab, two boundary errors still give 77% token accuracy, yet the system would look up the wrong restaurant. That's why NER is reported as entity-level F1.

## Say it

### How do you label spans of text, and how should you score it?

#### The interviewer pushes further

Follow-up 1 of 3

How do you handle subword tokens in BERT NER?

Label only the first subword of each word (ignore the rest in the loss) and map predictions back to words.

Follow-up 2 of 3

What does the CRF layer add on top of a neural tagger?

It learns transition scores between labels and decodes the best overall sequence, enforcing consistency like no I-DISH after O.

Follow-up 3 of 3

How would you do NER with very little labelled data?

Prompt an LLM with a schema and examples, use weak supervision (gazetteers, regexes), or label a small set and fine-tune a pre-trained encoder.

#### The 30-second answer

Sequence labelling assigns a label to every token, as in POS tagging or named entity recognition. Entity spans are encoded with BIO tags: B for the first token of an entity, I for the rest, O for outside, which keeps adjacent entities of the same type separate. Classic models are HMMs and CRFs, which score whole tag sequences and decode with Viterbi so invalid transitions like O to I are avoided; then BiLSTM-CRFs, and now fine-tuned BERT-style encoders with a per-token classifier, labelling the first subword. NER is evaluated with entity-level precision, recall and F1, where boundaries and type must match exactly, because token accuracy is inflated by all the O tokens.

**Go further**

#### What not to say

- "Report token accuracy." It's dominated by O tokens.

- "IO tags are enough." They can't separate adjacent entities of the same type.

**Key terms and sources**

Assigning a label to every token: part-of-speech tagging and named entity recognition, the BIO tagging scheme, models from HMMs and CRFs to BiLSTM-CRF and fine-tuned Transformers, and why NER is scored with entity-level F1 rather than token accuracy · built from Ramshaw & Marcus (1995), Lafferty et al. (2001), Tjong Kim Sang & De Meulder (CoNLL-2003), Lample et al. (2016), Devlin et al. (2019) and Jurafsky & Martin (SLP3, ch. 18) · checked 29 Oct 2026

#### Sources

1. L. Ramshaw & M. Marcus, "Text Chunking using Transformation-Based Learning", Workshop on Very Large Corpora, 1995.

2. J. Lafferty, A. McCallum & F. Pereira, "Conditional Random Fields: Probabilistic Models for Segmenting and Labeling Sequence Data", ICML 2001.

3. E. Tjong Kim Sang & F. De Meulder, "Introduction to the CoNLL-2003 Shared Task: Language-Independent Named Entity Recognition", CoNLL 2003.

4. G. Lample et al., "Neural Architectures for Named Entity Recognition", NAACL 2016, [arXiv:1603.01360](https://arxiv.org/abs/1603.01360).

5. J. Devlin et al., "BERT", NAACL 2019, [arXiv:1810.04805](https://arxiv.org/abs/1810.04805); D. Jurafsky & J. Martin, SLP3 ch. 18, [web.stanford.edu/~jurafsky/slp3](https://web.stanford.edu/~jurafsky/slp3/).
