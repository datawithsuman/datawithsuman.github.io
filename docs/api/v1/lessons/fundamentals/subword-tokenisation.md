# Subword Tokenisation (BPE, WordPiece, SentencePiece)

> How do LLMs handle words they've never seen?

- Track: Fundamentals › NLP Fundamentals › Language models and tokenisation
- Type: Concept · 25 min
- Page: https://aimlrounds.com/tracks/fundamentals/subword-tokenisation/
- Before this: Bag-of-Words, N-grams and TF-IDF (`fundamentals/bag-of-words-and-tf-idf`)
- Quiz topic: `nlp`
- Sources checked: 2026-10-29 · Text last changed: 2026-11-20 · Version: 0a2107109c

## Intuition

### The situation

Your review model must handle "biryani", "biryanis" and words it has never seen. A word vocabulary turns unseen words into an unknown token, and characters make sequences 4–5 times longer. The interviewer asks:

> How do LLMs handle words they've never seen?

**Running example:** the review model must handle "biryani", "biryanis", "spiciest" and words it has never seen, without an "unknown word" token, and without turning every review into hundreds of characters.

#### Words are too many, characters too long

- **Word-level:** the vocabulary keeps growing (every name, typo and plural), and anything outside it becomes <unk>, losing information.

- **Character-level:** no unknowns and a tiny vocabulary, but sequences get 4–5× longer and the model must learn spelling from scratch. Attention cost grows with the square of length (self-attention).

- **Subwords:** a fixed vocabulary (e.g. 32k–100k pieces) where common words are single tokens and rare words decompose into reusable parts.

### The idea

Think of a box of building bricks. Common words get their own big brick, and a rare word is built from smaller ones. You can always build something, because the smallest bricks are always in the box.

[Figure: Biryani is one token. The unseen word biryanis becomes biryani, s and an end marker. The rare word unbelievably falls apart into nine small pieces.]

_From the lab, after 120 merges. _ marks the end of a word, and the rare word splits into 9 small pieces._

### Play

**Try to break it.** Start at 0 merges, then move to 40 and 120. Watch "biryani", the unseen "biryanis" and "unbelievably".

#### Watch the vocabulary grow, merge by merge

Corpus: words from 400 delivery reviews plus spelling variants (spicy / spicier / spiciest, deliver / delivered / delivery …), counted by frequency. Each chip is one token; _ marks the end of a word. Test words include ones never seen in the corpus.

With 0 merges every word is a string of characters: **5.3 tokens per word** on average. After 40 merges the most frequent words and pieces are merged first ("delivered" is already "deliver" + "e" + "d_"), and the average drops to 2.19. By **120 merges** (vocabulary 144) it is 1.05: "biryani" and "delivered" are single tokens, "spiciest" is two pieces, and the never-seen "biryanis" becomes "biryani" + "s" + "_". The rare, unseen "unbelievably" still falls apart into 9 small pieces: **no unknown tokens**, just more of them. Each extra merge helps rarer and rarer pairs, which is why vocabulary size trades sequence length against the size of the embedding table.

**Now say why:** why does each extra merge shorten sequences by less, and what does a bigger vocabulary cost you?

## How it works

### How it works

#### In one breath

Word-level vocabularies can't handle new words ("biryanis", typos, names) and grow without limit; character-level input makes sequences very long. **Subword tokenisation** sits in between: frequent words stay whole, rare words are split into meaningful pieces ("spici" + "est"). **Byte-pair encoding (BPE)** starts from characters and repeatedly **merges the most frequent adjacent pair** into a new token until the vocabulary reaches a target size (GPT-2: 50,257). **WordPiece** (BERT) picks merges that most increase the training data's likelihood; the **unigram** model (SentencePiece) starts big and prunes. **Byte-level BPE** works on raw bytes, so any text can be encoded with no unknown tokens. Tokenisation decides how many tokens your text costs, and explains many LLM quirks. What you'll be able to do after this: run BPE by hand, compare BPE, WordPiece and unigram, and explain tokenisation effects in LLMs.

#### Byte-pair encoding, step by step

1. Split every word in the training corpus into characters, with an end-of-word marker (shown here as _).

2. Count every adjacent pair of symbols, weighted by word frequency.

3. Merge the most frequent pair everywhere into a new symbol and add it to the vocabulary.

4. Repeat until the vocabulary reaches the target size. To tokenise new text, apply the learned merges in the same order.

Gage (1994) introduced BPE for data compression; Sennrich, Haddow & Birch (ACL 2016) adapted it for neural machine translation of rare words [arXiv:1508.07909](https://arxiv.org/abs/1508.07909). GPT-2 applies BPE to raw bytes with a 50,257-token vocabulary (Radford et al. 2019).

## In practice

### In practice

#### BPE, WordPiece, unigram, and bytes

| Method | How it builds the vocabulary | Used by |
|---|---|---|
| **BPE** | bottom-up: merge the most frequent adjacent pair | GPT-2/3/4 (byte-level), LLaMA 3 (tiktoken-style BPE) |
| **WordPiece** | bottom-up: merge the pair that most increases the likelihood of the training data under a language model | BERT (Schuster & Nakajima 2012; Wu et al. 2016) |
| **Unigram LM** | top-down: start with a large vocabulary and prune pieces that least reduce likelihood; can sample segmentations | T5, ALBERT, XLNet via SentencePiece (Kudo 2018) |
| **SentencePiece** | a library that implements BPE and unigram on raw text, treating spaces as a symbol (▁), language-independent | LLaMA 1/2, T5, many multilingual models |

Kudo & Richardson, EMNLP 2018 demo [arXiv:1808.06226](https://arxiv.org/abs/1808.06226). Note: SentencePiece implements BPE and unigram, not WordPiece.

#### Tokenisation quirks you'll be asked about

- **Cost and context:** APIs bill and limit by tokens; English averages roughly 3–4 characters per token, so 1,000 tokens ≈ 750 words.

- **Languages:** tokenisers trained mostly on English split Hindi, Tamil or Bengali text into many more tokens per word, making it slower and costlier for the same content.

- **Spelling and arithmetic:** a model sees "strawberry" as 2–3 tokens, not letters, which is why letter-counting and digit-by-digit arithmetic can fail.

- **Whitespace and case:** "Biryani", " biryani" and "biryani" can be different tokens.

- The tokeniser is fixed with the model: you can't swap it without retraining the embeddings.

### The answer that sounds right

#### "LLMs read words"

It sounds right, since words are what we type. But they read subword tokens, chosen by frequency and not by meaning. A model sees "strawberry" as 2–3 tokens rather than letters, which is why letter counting can fail. "Biryani" and " biryani" can be different tokens. And Hindi, Tamil or Bengali text can take many more tokens per word, so the same content costs more.

## Say it

### How do LLMs handle words they've never seen?

#### The interviewer pushes further

Follow-up 1 of 3

How do you pick the vocabulary size?

Bigger vocabularies shorten sequences but enlarge the embedding and output layers and leave rare tokens under-trained; LLMs typically use 32k–200k.

Follow-up 2 of 3

Why byte-level instead of character-level BPE?

Unicode has over 100,000 characters; 256 byte values cover everything, so no input is ever out of vocabulary.

Follow-up 3 of 3

What's a problem with tokenising numbers?

Numbers split inconsistently ("1234" vs "12" + "34"), hurting arithmetic; some tokenisers split digits individually.

#### The 30-second answer

Subword tokenisers balance word-level vocabularies, which can't handle unseen words, against characters, which make sequences too long. BPE starts from characters and repeatedly merges the most frequent adjacent pair until reaching a target vocabulary, so common words become single tokens and rare words split into reusable pieces; byte-level BPE, as in GPT-2 with about 50k tokens, can encode any text with no unknowns. WordPiece, used by BERT, chooses merges by likelihood gain, and the unigram model in SentencePiece prunes a large vocabulary instead. Tokenisation affects cost, context length, multilingual fairness, and quirks like letter counting and arithmetic.

**Go further**

#### What not to say

- "LLMs read words." They read subword tokens.

- "BPE merges by meaning." It merges by frequency only.

**Key terms and sources**

Why modern models split text into subword pieces rather than whole words or characters; how byte-pair encoding learns its vocabulary by merging frequent pairs; WordPiece and the unigram model; byte-level BPE; and the practical consequences for LLMs (token counts, cost, multilingual text, arithmetic) · built from Gage (1994), Sennrich, Haddow & Birch (ACL 2016), Schuster & Nakajima (2012), Wu et al. (2016), Kudo (2018), Kudo & Richardson (2018) and Radford et al. (GPT-2, 2019) · checked 29 Oct 2026

#### Sources

1. P. Gage, "A New Algorithm for Data Compression", _C Users Journal_ 12(2), 1994.

2. R. Sennrich, B. Haddow & A. Birch, "Neural Machine Translation of Rare Words with Subword Units", ACL 2016, [arXiv:1508.07909](https://arxiv.org/abs/1508.07909).

3. M. Schuster & K. Nakajima, "Japanese and Korean Voice Search", ICASSP 2012; Y. Wu et al., "Google's Neural Machine Translation System", [arXiv:1609.08144](https://arxiv.org/abs/1609.08144), 2016.

4. T. Kudo, "Subword Regularization", ACL 2018, [arXiv:1804.10959](https://arxiv.org/abs/1804.10959); T. Kudo & J. Richardson, "SentencePiece", EMNLP 2018, [arXiv:1808.06226](https://arxiv.org/abs/1808.06226).

5. A. Radford et al., "Language Models are Unsupervised Multitask Learners" (GPT-2), OpenAI 2019.
