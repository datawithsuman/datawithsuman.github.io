# HMMs, CRFs and the Viterbi Algorithm

> How do you find the best label for every word at once, and how do HMMs and CRFs differ?

- Track: Fundamentals › NLP Fundamentals › Tagging, retrieval and evaluation
- Type: Concept · 18 min
- Page: https://aimlrounds.com/tracks/fundamentals/hmms-crfs-and-viterbi/
- Before this: Sequence Labelling and NER (`fundamentals/sequence-labelling-and-ner`)
- Quiz topic: `nlp`

## Intuition

### The situation

Your tagger labels each word on its own. It reads "order" as a noun in "order the cold biryani", and sometimes outputs an I-DISH tag with no B-DISH before it. You need the best tags for the sentence as a whole. The interviewer asks:

> How do you find the best label for every word at once, and how do HMMs and CRFs differ?

#### Why it matters

Sequence labelling mentions these models, and interviewers often go further: write the Viterbi recursion, or say what a CRF adds to a tagger. Viterbi is also a good example of dynamic programming that's used well beyond language, in speech and in decoding signals.

### The idea

Think of the shortest route across a city. To find the best way to any junction, you only need the best way to each junction before it. You don't have to remember every route. Viterbi does this with tags: at each word, it keeps the best path into each tag.

[Figure: Three ideas. HMMs model tag transitions and word emissions. Viterbi finds the best sequence. CRFs model tags given all the words.]

_Best sequence, without checking every sequence._

### Play

**Try to break it.** Set the trust in transitions to 0. Then try each sentence.

#### Decode a sentence

Illustrative, hand-set probabilities for 4 tags: N noun, V verb, A adjective, D determiner. Each cell shows the Viterbi score. Green marks the best path. Exact calculation.

Set the trust in transitions to **0**: Viterbi now matches each word alone, because no context remains. Raise it again, and "order" becomes a verb, as sentences often start with one here. In **the cold arrived**, "cold" becomes a noun, since an adjective rarely comes directly before a verb.

**Now say why:** why does "cold" change tag in "the cold arrived"?

## Maths

### Maths

#### In one breath

Labels depend on their neighbours, so choosing each word's label alone can give nonsense. An **HMM** models tag-to-tag transitions and tag-to-word emissions. The **Viterbi algorithm** finds the best whole sequence with dynamic programming, in O(T·S²) rather than ST. A **CRF** keeps the sequence scoring, but models P(tags | words) directly, so it can use any features of the input. In neural versions, a network supplies the scores, and Viterbi still decodes them.

#### From HMMs to CRFs

##### Hidden Markov models

An HMM imagines that hidden tags generate the words. It has two tables, both estimated by counting on labelled text:

- **Transitions:** how likely each tag follows another. An adjective is often followed by a noun.

- **Emissions:** how likely a tag produces a given word. A verb might produce "order".

##### Three classic questions

| Question | Algorithm | Combines paths using |
|---|---|---|
| **Decoding:** what's the best tag sequence? | Viterbi | Maximum |
| **Likelihood:** how probable are these words? | Forward | Sum |
| **Learning:** what if there are no tags? | Baum-Welch, a form of EM | Expected counts |

##### Why Viterbi is fast

With S tags and T words, there are ST possible sequences. But the best path to a tag at step t only needs the best paths to every tag at step t − 1, so we never need to look at the rest. That's S² work per word. For 4 tags and 30 words, this is 480 steps rather than about 1018 sequences.

##### HMM or CRF?

| | HMM | Linear-chain CRF |
|---|---|---|
| Models | P(tags, words), generative | P(tags \| words), discriminative |
| Features | Only the current word, given its tag | Anything: capitals, suffixes, neighbouring words |
| Training | Counting | Gradient-based, slower |
| Decoding | Viterbi | Viterbi |

A CRF normalises over all possible tag sequences. Summing them is what the forward algorithm does, so training stays practical.

##### Neural CRFs, and when to skip them

In a BiLSTM-CRF, the network gives each word a score for each tag, and the CRF adds transition scores. Lample et al. reached an F1 of 90.94 on CoNLL-2003, and removing the CRF layer cost them 1.79 points. Later, BERT reached 92.8 with a per-token classifier and no CRF. Strong context can reduce the benefit, though a CRF or a simple rule can still prevent impossible sequences.

#### The maths

$$ P(t, w) = \prod_{i} P(t_i \mid t_{i-1})\, P(w_i \mid t_i), \qquad v_i(s) = \max_{r}\, v_{i-1}(r)\, P(s \mid r)\, P(w_i \mid s) $$

Standard HMM forms, as in the Viterbi article and Jurafsky and Martin’s appendix on HMMs. In practice, sum logs to avoid underflow.

- **the joint probability**: How likely this tag sequence and these words are together.

- **a transition**: How likely this tag is to follow the previous one.

- **an emission**: How likely this tag is to produce this word.

- **the Viterbi score**: The best probability of any path that ends in tag s at word i.

- **reuse earlier work**: The best scores from the previous word. Keep a pointer to the winning tag, to rebuild the path at the end.

## In practice

### In practice

#### In practice

- **Use logs:** multiplying many small probabilities underflows, so add log scores.

- **Block impossible sequences:** setting the O → I-DISH transition to zero prevents invalid tags, even without a learned CRF.

- **Handle unknown words:** HMMs need smoothing or word-shape rules. CRFs handle this better through features.

- **Try without a CRF first:** on a strong encoder, measure whether it adds enough to justify the extra code and compute.

- **Remember Viterbi's limit:** the highest-scoring sequence isn't always the sequence with the most correct labels. It's just a good default.

### The answer that sounds right

#### "Picking the best tag for each word gives the best sequence"

It sounds right, as each choice is individually the best. But good local choices can combine into an unlikely or invalid sequence, and the best sequence may need a weaker label on one word. Viterbi looks at the sequence as a whole, without needing to list every option.

## Say it

### How do you find the best label for every word at once, and how do HMMs and CRFs differ?

#### The interviewer pushes further

Follow-up 1 of 3

What's the difference between Viterbi and the forward algorithm?

They have the same structure. Viterbi takes the maximum over previous tags, to find the single best path. Forward takes the sum, to get the total probability of the words across all paths. Forward is also needed to train CRFs.

Follow-up 2 of 3

What does a CRF add on top of a neural tagger?

Scores for moving between tags, and decoding of the whole sequence together. So it can learn that I-DISH doesn't follow O. How much it helps depends on the encoder. It helped a BiLSTM by 1.79 F1 in one study, while BERT did well without it.

Follow-up 3 of 3

With 10 tags and 20 words, how much faster is Viterbi than brute force?

Brute force checks 10²⁰ sequences. Viterbi does 20 × 10² = 2,000 steps. The saving comes from keeping only the best path into each tag at each word.

Labelling each word alone ignores its neighbours, and can give invalid sequences. An HMM models tag transitions and word emissions, and the Viterbi algorithm finds the best sequence with dynamic programming. Each cell keeps the best score for ending in a tag, plus a pointer, so it costs T times S squared, not S to the T. The forward algorithm replaces max with sum, to get the likelihood. A CRF models tags given words directly, so it can use rich features, and it still decodes with Viterbi. In neural taggers, the network gives the scores, and a CRF layer can add transitions.

**Key terms and sources**

Why labelling words one at a time fails, hidden Markov models, the Viterbi algorithm, forward and Baum-Welch, conditional random fields and neural CRFs.

#### Sources

- Viterbi algorithm, Wikipedia

- Jurafsky and Martin, Appendix A: Hidden Markov Models

- Lample et al., Neural Architectures for Named Entity Recognition

- Devlin et al., BERT

- Conditional random field, Wikipedia, citing Lafferty et al. (2001)

Explanations are ours, built from these sources. Lab numbers are illustrative, and worked examples were checked by calculation.
