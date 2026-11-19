# Topic Modelling: LDA, NMF and BERTopic

> How would you find what thousands of documents are about, without any labels?

- Track: Fundamentals › NLP Fundamentals › Text basics
- Type: Concept · 15 min
- Page: https://aimlrounds.com/tracks/fundamentals/topic-modelling/
- Before this: Bag-of-Words, N-grams and TF-IDF (`fundamentals/bag-of-words-and-tf-idf`)
- Quiz topic: `nlp`

## Intuition

### The situation

You have 50,000 customer reviews and no labels. Your manager asks what people are complaining about this quarter, and asks for ten themes by Friday. Reading them all isn't possible. The interviewer asks:

> How would you find what thousands of documents are about, without any labels?

#### Why it matters

When you have thousands of reviews or tickets and no labels, a topic model gives you a quick map of what people are saying. It can guide labelling and reveal new issues. A warning on names: LDA here means Latent Dirichlet Allocation, not Linear Discriminant Analysis.

### The idea

Think of sorting a pile of old newspapers with no section labels. You notice that "goal" and "match" appear together, and "budget" and "minister" appear together, so you make piles. No one told you those piles are called sports and politics. You name them after you've looked.

[Figure: Three approaches. LDA tells a probabilistic story. NMF factorises a matrix. BERTopic clusters embeddings.]

_They return word lists. People give them meaning._

### Play

**Try to break it.** Set topics to 2, then 6. Then raise α.

#### Fit LDA

Our seeded simulation: 90 short reviews generated from 3 hidden themes. The model never sees the themes. It's fitted in your browser with 150 rounds of Gibbs sampling. The match score assigns each topic to its most common theme.

Set topics to **2**: two themes must share one topic. Set it to **6**: real themes split up, yet the match score stays high, so it can't warn you of this. That's why you also read the words. Now raise α: documents spread across more topics, and each main topic gets a smaller share.

**Now say why:** why can't the match score warn you about too many topics?

## Maths

### Maths

#### In one breath

Topic models find themes in unlabelled text. **LDA** assumes each document is a mix of topics, and each topic is a mix of words. **NMF** factorises the document-word matrix into two non-negative parts, giving a similar result. **BERTopic** embeds documents, clusters them, then finds each cluster's distinctive words with c-TF-IDF. None of them knows what a topic means: they return word lists for people to interpret, so results need checking.

#### Three approaches

| Method | Idea | Input | Good for | Weak on |
|---|---|---|---|---|
| **LDA** | A probabilistic story of how words get generated. | Word counts | Documents of a fair length, and topic mixes. | Short texts. Ignores word order. |
| **NMF** | Factorise X ≈ WH, with no negative values. | TF-IDF | A fast, simple baseline. | Short texts. Ignores word order. |
| **BERTopic** | Embed, cluster, then describe each cluster. | Raw text | Short texts, and meaning beyond exact words. | Gives each document one main cluster by default. Results vary between runs. |

##### LDA's story

1. Each topic is a distribution over words, drawn from a Dirichlet.

2. Each document draws its own mix of topics, also from a Dirichlet.

3. For each word, pick a topic from the document's mix, then a word from that topic.

We only see the words. Fitting reverses the story, using Gibbs sampling or variational inference. A small α encourages each document to use few topics.

##### BERTopic's steps

1. **Embed** documents using a sentence embedding model.

2. **Reduce** dimensions with UMAP.

3. **Cluster** with HDBSCAN, which leaves outliers out of every cluster.

4. **Describe** each cluster with c-TF-IDF: join its documents into one, then find the words distinctive to it.

##### Choosing the number of topics

There's no single right answer. Try a range, and use a **coherence** score, which measures how often a topic's top words appear together. Then read the topics, because a high score doesn't guarantee they're useful. The best number is often whatever your team can use.

##### Where LLMs fit

LLMs are useful at the end: give one a topic's top words and sample documents, and ask for a clear name. You can also ask an LLM to find themes directly on a sample. Check its labels against real documents, as a neat name can hide a messy topic.

#### The maths

$$ P(w \mid d) = \sum_{k} \theta_{d,k}\, \beta_{k,w}, \qquad X \approx WH, \qquad W_{t,c} = \mathrm{tf}_{t,c} \cdot \log\!\Big(1 + \frac{A}{\mathrm{tf}_t}\Big) $$

LDA as described by scikit-learn and Blei et al. NMF as in scikit-learn. c-TF-IDF from the BERTopic paper.

- **a word in a document**: Its probability comes from a mix across topics.

- **the topic mix**: How much of document d is topic k.

- **the topic’s words**: How likely topic k is to produce word w.

- **NMF**: Documents × topics, multiplied by topics × words, all non-negative.

- **c-TF-IDF**: A word’s frequency in cluster c, weighted by how rare it is overall. A is the average words per cluster.

## In practice

### In practice

#### In practice

- **Clean first for LDA and NMF:** remove stop words and very common or very rare words. Here, unlike with Transformers, preprocessing matters a lot.

- **Short texts:** for tweets and reviews, embedding methods usually do better than word-count methods.

- **Check for stability:** refit with different seeds. Topics that come and go aren't dependable.

- **Read real documents:** sample several per topic, as top words alone can mislead.

- **Move to a classifier when you can:** once themes are clear, label some examples, and train a classifier, which is usually easier to monitor.

### The answer that sounds right

#### "The model found ten topics, so there are ten topics"

It sounds right, as the output looks definite. But you chose that number, and the model must fill it. Different seeds and settings give different topics, and a high coherence score doesn't make a topic useful. Read sample documents, test stability, and treat topics as a starting point.

## Say it

### How would you find what thousands of documents are about, without any labels?

#### The interviewer pushes further

Follow-up 1 of 3

LDA or BERTopic for short customer reviews?

I'd start with BERTopic. LDA relies on word co-occurrence within a document, and short reviews give little to work with. Embeddings bring in meaning learned elsewhere. But BERTopic gives one main cluster per document by default, so if reviews mix themes, I'd look at that too.

Follow-up 2 of 3

How do you pick the number of topics?

Fit several values, and compare coherence. Then read the top words and sample documents, and check stability across seeds. The final choice also depends on use: three broad themes may suit a dashboard, and thirty may suit a support team.

Follow-up 3 of 3

How is NMF related to LDA?

Both represent documents as mixtures of topics, and topics as mixtures of words, with non-negative values. LDA is a probabilistic model with Dirichlet priors. NMF minimises reconstruction error, and is simpler and usually faster.

Topic models find themes with no labels. LDA is generative: each document is a mix of topics, and each topic is a distribution over words, fitted with Gibbs sampling or variational inference. NMF factorises a TF-IDF matrix into non-negative parts, and it's a fast baseline. BERTopic embeds documents, reduces dimensions with UMAP, clusters with HDBSCAN, and describes clusters with c-TF-IDF, and it tends to suit short texts. I'd choose the number of topics with coherence plus reading the topics, check stability across seeds, and read sample documents. Then I might use the themes to train a classifier.

**Key terms and sources**

Latent Dirichlet Allocation, non-negative matrix factorisation, BERTopic and c-TF-IDF, how to choose the number of topics, and how to check the results.

#### Sources

- Blei, Ng and Jordan, Latent Dirichlet Allocation (2003)

- Grootendorst, BERTopic

- scikit-learn on decomposition: LDA and NMF

Explanations are ours, built from these sources. Lab numbers are illustrative, and worked examples were checked by calculation.
