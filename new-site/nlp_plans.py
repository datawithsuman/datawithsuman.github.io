# Seven-section plans for NLP Fundamentals lessons. Chapter text comes from the live pages (see ml_import.py).
from maths_plans import _plan

PREP_PICTURE = """<svg viewBox="0 0 480 110" role="img" aria-label="The review Not good, the Pizza was COLD becomes not good the pizza was cold, and then, with stop words removed, good pizza cold. The word not has gone.">
  <g font-size="13" fill="var(--dim)"><text x="4" y="24">Review</text><text x="4" y="60">Normalised</text><text x="4" y="96">No stop words</text></g>
  <g font-size="15" fill="var(--ink)"><text x="116" y="24">Not good, the Pizza was COLD!!</text><text x="116" y="60">not good the pizza was cold</text></g>
  <text x="116" y="96" font-size="15" font-weight="700" fill="var(--bad)">good pizza cold</text>
  <text x="244" y="96" font-size="13" font-weight="600" fill="var(--bad)">"not" is gone, so it reads positive</text>
</svg>"""

TFIDF_PICTURE = """<svg viewBox="0 0 480 156" role="img" aria-label="Word weights for one review. With raw counts, the, was and cold are equally large. With TF-IDF, the and was drop to zero, and cold, raita and biryani carry the review.">
  <g font-size="14" font-weight="600" fill="var(--ink)"><text x="80" y="16">Raw counts</text><text x="290" y="16">TF-IDF</text></g>
  <g font-size="14" fill="var(--ink)" text-anchor="end"><text x="70" y="42">the</text><text x="70" y="68">was</text><text x="70" y="94">cold</text><text x="70" y="120">biryani</text><text x="70" y="146">raita</text></g>
  <g fill="var(--dim)"><rect x="80" y="30" width="150" height="16"/><rect x="80" y="56" width="150" height="16"/><rect x="80" y="82" width="150" height="16"/><rect x="80" y="108" width="75" height="16"/><rect x="80" y="134" width="75" height="16"/></g>
  <g fill="var(--a)"><rect x="290" y="82" width="150" height="16"/><rect x="290" y="108" width="50" height="16"/><rect x="290" y="134" width="85" height="16"/></g>
  <g font-size="13" fill="var(--dim)"><text x="290" y="42">0</text><text x="290" y="68">0</text></g>
</svg>"""

BIGRAM_PICTURE = """<svg viewBox="0 0 480 104" role="img" aria-label="The review the biryani was not cold. With unigrams, not and cold are separate features and both models score about 53 percent. With bigrams, not_cold is one feature and both reach about 94 percent.">
  <g font-size="13" fill="var(--dim)"><text x="4" y="34">Unigrams</text><text x="4" y="84">Bigrams</text></g>
  <g fill="var(--tint)" stroke="var(--c)" stroke-width="2"><rect x="80" y="12" width="56" height="34" rx="6"/><rect x="146" y="12" width="56" height="34" rx="6"/><rect x="212" y="12" width="60" height="34" rx="6"/><rect x="80" y="62" width="86" height="34" rx="6"/></g>
  <rect x="176" y="62" width="96" height="34" rx="6" fill="var(--a)"/>
  <g font-size="14" font-weight="600" fill="var(--ink)" text-anchor="middle"><text x="108" y="34">was</text><text x="174" y="34">not</text><text x="242" y="34">cold</text><text x="123" y="84">was_not</text><text x="224" y="84" fill="#fff">not_cold</text></g>
  <g font-size="14" font-weight="600"><text x="296" y="34" fill="var(--bad)">About 53% accurate</text><text x="296" y="84" fill="var(--ok)">About 94% accurate</text></g>
</svg>"""

NEXTWORD_PICTURE = """<svg viewBox="0 0 480 130" role="img" aria-label="To guess what follows the biryani was, a bigram model looks only at was. It has counted not most often, then other words. It has never seen was crispy, so that gets zero.">
  <text x="4" y="70" font-size="15" fill="var(--dim)">the biryani</text>
  <rect x="84" y="50" width="48" height="30" rx="6" fill="var(--c)"/><text x="108" y="70" font-size="15" font-weight="600" fill="#fff" text-anchor="middle">was</text>
  <path d="M132 65H196" stroke="var(--dim)" stroke-width="2"/><path d="M204 65 194 60V70Z" fill="var(--dim)"/>
  <g font-size="14" fill="var(--ink)" text-anchor="end"><text x="272" y="22">not</text><text x="272" y="52">cold</text><text x="272" y="82">great</text><text x="272" y="112">crispy</text></g>
  <g fill="var(--a)"><rect x="282" y="9" width="170" height="18"/><rect x="282" y="39" width="90" height="18"/><rect x="282" y="69" width="60" height="18"/></g>
  <text x="282" y="112" font-size="13" font-weight="600" fill="var(--bad)">0: never seen</text>
</svg>"""

BRICKS_PICTURE = """<svg viewBox="0 0 480 112" role="img" aria-label="Biryani is one token. The unseen word biryanis becomes biryani, s and an end marker. The rare word unbelievably falls apart into nine small pieces.">
  <g font-size="14" fill="var(--ink)"><text x="4" y="28">biryani</text><text x="4" y="64">biryanis</text><text x="4" y="100">unbelievably</text></g>
  <g fill="var(--tint)" stroke="var(--c)" stroke-width="2"><rect x="110" y="8" width="92" height="28" rx="5"/><rect x="110" y="44" width="92" height="28" rx="5"/><rect x="208" y="44" width="30" height="28" rx="5"/><rect x="244" y="44" width="30" height="28" rx="5"/>
  <rect x="110" y="80" width="34" height="28" rx="5"/><rect x="150" y="80" width="34" height="28" rx="5"/><rect x="190" y="80" width="34" height="28" rx="5"/><rect x="230" y="80" width="34" height="28" rx="5"/><rect x="270" y="80" width="34" height="28" rx="5"/><rect x="310" y="80" width="34" height="28" rx="5"/><rect x="350" y="80" width="34" height="28" rx="5"/><rect x="390" y="80" width="34" height="28" rx="5"/><rect x="430" y="80" width="34" height="28" rx="5"/></g>
  <g font-size="14" font-weight="600" fill="var(--ink)" text-anchor="middle"><text x="156" y="27">biryani</text><text x="156" y="63">biryani</text><text x="223" y="63">s</text><text x="259" y="63">_</text></g>
</svg>"""

BIO_PICTURE = """<svg viewBox="0 0 480 86" role="img" aria-label="Paradise is tagged B-REST, Biryani and House are I-REST, in is O, and Hyderabad is B-CITY.">
  <g fill="var(--a)" fill-opacity=".22"><rect x="4" y="6" width="84" height="72" rx="6"/><rect x="94" y="6" width="84" height="72" rx="6"/><rect x="184" y="6" width="84" height="72" rx="6"/></g>
  <rect x="274" y="6" width="84" height="72" rx="6" fill="none" stroke="var(--line-strong)"/><rect x="364" y="6" width="112" height="72" rx="6" fill="var(--b)" fill-opacity=".25"/>
  <g font-size="15" fill="var(--ink)" text-anchor="middle"><text x="46" y="36">Paradise</text><text x="136" y="36">Biryani</text><text x="226" y="36">House</text><text x="316" y="36">in</text><text x="420" y="36">Hyderabad</text></g>
  <g font-size="13" font-weight="700" text-anchor="middle"><text x="46" y="62" fill="var(--a)">B-REST</text><text x="136" y="62" fill="var(--a)">I-REST</text><text x="226" y="62" fill="var(--a)">I-REST</text><text x="316" y="62" fill="var(--dim)">O</text><text x="420" y="62" fill="var(--b)">B-CITY</text></g>
</svg>"""

SEARCH_PICTURE = """<svg viewBox="0 0 480 124" role="img" aria-label="For the query bawarchi biryani, Bawarchi ranks first with BM25, third with dense and second with hybrid. For fiery rice dish, BM25 finds none of the three spicy rice places, while dense and hybrid each find two.">
  <g font-size="14" font-weight="600" fill="var(--ink)" text-anchor="middle"><text x="264" y="16">BM25</text><text x="344" y="16">Dense</text><text x="430" y="16">Hybrid</text></g>
  <path d="M0 28H480M0 76H480" stroke="var(--line-strong)" stroke-width="1.5"/>
  <g font-size="14" font-weight="600" fill="var(--ink)"><text x="4" y="50">"bawarchi biryani"</text><text x="4" y="98">"fiery rice dish"</text></g>
  <g font-size="13" fill="var(--dim)"><text x="4" y="68">Bawarchi's rank</text><text x="4" y="116">Spicy rice places in the top 3</text></g>
  <g font-size="15" font-weight="700" text-anchor="middle"><text x="264" y="58" fill="var(--ok)">1st</text><text x="344" y="58" fill="var(--bad)">3rd</text><text x="430" y="58" fill="var(--ink)">2nd</text><text x="264" y="106" fill="var(--bad)">0 of 3</text><text x="344" y="106" fill="var(--ok)">2 of 3</text><text x="430" y="106" fill="var(--ok)">2 of 3</text></g>
</svg>"""

BLEU_PICTURE = """<svg viewBox="0 0 480 116" role="img" aria-label="Sentence BLEU against the reference. The correct paraphrase scores 0.29. Word salad and the summary with the opposite meaning both score 0.36.">
  <text x="4" y="14" font-size="13" fill="var(--dim)">Sentence BLEU against "the biryani arrived cold and late"</text>
  <g font-size="14" fill="var(--ink)" text-anchor="end"><text x="150" y="46">Correct paraphrase</text><text x="150" y="76">Word salad</text><text x="150" y="106">Opposite meaning</text></g>
  <rect x="160" y="32" width="203" height="18" fill="var(--ok)"/><rect x="160" y="62" width="252" height="18" fill="var(--bad)"/><rect x="160" y="92" width="252" height="18" fill="var(--bad)"/>
  <g font-size="14" font-weight="600" fill="var(--ink)"><text x="370" y="46">0.29</text><text x="420" y="76">0.36</text><text x="420" y="106">0.36</text></g>
</svg>"""

NLP_PLANS = {
    "fundamentals/text-preprocessing": _plan(
        "A teammate adds the full pipeline to a review sentiment model: lowercase, strip punctuation, remove stop words, then stem. \"Not good, the pizza was cold\" now reaches the model as \"good pizza cold\". The interviewer asks:",
        "Which preprocessing steps help, and when do they hurt?",
        "Think of a clerk tidying a messy filing cabinet. Merging \"Order\", \"ordered\" and \"ORDER!!\" into one folder makes things easier to find. But a clerk who bins every small word also bins \"not\", and the file now says the opposite.",
        PREP_PICTURE, "A review from the lesson, run through the lab's steps.",
        ("c3", "<b>Try to break it.</b> Pick the first review and remove stop words. Then switch between stemming and lemmatisation on the third review, and watch the vocabulary size.", "<b>Now say why:</b> if removing stop words shrinks the vocabulary, why would you ever keep them?"),
        ["c2"], ["c4"], [], ["src"],
        ["The classic steps: lowercase, remove punctuation, tokenise, optionally remove stop words, normalise word forms.",
         "Stemming chops suffixes with rules: fast but crude.",
         "Lemmatisation maps words to a dictionary form, using vocabulary and part of speech.",
         "These steps shrink the vocabulary and reduce sparsity for bag-of-words models and search.",
         "They can destroy meaning: removing \"not\" flips sentiment.",
         "For Transformers, you skip most of it and feed raw text to a subword tokeniser.",
         "Training and serving must use identical preprocessing."],
        tabs=["Intuition", "How it works", "In practice"],
        trap_title="\"Always remove stop words and stem\"",
        trap_html="<p>It sounds right, since a smaller vocabulary means less sparsity. But it depends on the task and the model. For sentiment, stop-word lists delete \"not\". For Transformers and LLMs, removing stop words or stemming usually hurts, because pre-trained models expect raw text. Search is the case where stemming usually pays off, since it raises recall.</p>"),
    "fundamentals/bag-of-words-and-tf-idf": _plan(
        "You want the review most similar to one about cold biryani. With raw word counts, it scores 0.64 to 0.79 against every other review, even the one about a rude rider. The interviewer asks:",
        "Why does TF-IDF find the right review when raw counts can't?",
        "Think of people describing their meals. Everyone says \"the\" and \"was\", so those tell you nothing about who ate what. Few people say \"raita\", so hearing it tells you a lot. TF-IDF scores each word by how much it gives away.",
        TFIDF_PICTURE, "Illustrative weights for \"the biryani was cold and the raita was cold\". A word in every review gets zero.",
        ("c4", "<b>Try to break it.</b> Pick the biryani review and switch between raw counts and TF-IDF, watching the similarities. Then try the paneer review.", "<b>Now say why:</b> under TF-IDF, the paneer review's best match scores only 0.22. Why is that a good result?"),
        ["c2", "c3"], ["c5"], [], ["src"],
        ["Bag-of-words is a sparse vector of word counts over the vocabulary, ignoring order.",
         "N-grams add short sequences like \"not good\" to keep some order.",
         "TF-IDF reweights each count by the log of documents over documents containing the word.",
         "Words that appear everywhere get near-zero weight, and distinctive words get high weight.",
         "Vectors are usually L2-normalised and compared with cosine similarity.",
         "It's a fast, interpretable baseline, and BM25 is the search version.",
         "It has no synonyms or real word order, which embeddings and Transformers add."],
        trap_title="\"TF-IDF understands meaning\"",
        trap_html="<p>It sounds right, since the rankings look so much more sensible. But TF-IDF only matches exact tokens, and \"cold\" and \"chilly\" are unrelated to it. It looks like meaning because the grammar words stopped dominating, not because the model knows what a word means. That's the gap dense embeddings fill.</p>"),
    "fundamentals/text-classification": _plan(
        "The restaurant team wants reviews tagged positive or negative to route complaints, and you have a few hundred labelled examples. Your unigram model scores about 53%, and its \"most positive\" words are cold, soggy and bland. The interviewer asks:",
        "How do you build a text classification baseline, and why does negation break it?",
        "Think of judging a review from its words cut out and shaken in a bag. \"Not\" and \"cold\" are both in there, but you can't tell they were next to each other. Bigrams cut out pairs instead, so \"not cold\" stays in one piece.",
        BIGRAM_PICTURE, "Test accuracy from the lab, on reviews deliberately full of negations.",
        ("c3", "<b>Try to break it.</b> Train with unigrams only, and read logistic regression's most positive and negative features. Then add bigrams and compare.", "<b>Now say why:</b> why did Naive Bayes and logistic regression both fail, and both recover, at the same point?"),
        ["c2"], ["c4", "c5"], [], ["src"],
        ["Vectorise with bag-of-words or TF-IDF, often adding bigrams.",
         "Train multinomial Naive Bayes or logistic regression.",
         "Naive Bayes multiplies per-class word probabilities, assuming independence given the class.",
         "Add-one smoothing stops unseen words zeroing the product.",
         "Logistic regression learns a weight per feature, and is usually more accurate with enough data.",
         "Both ignore word order, so negation breaks unigram models, and bigrams fix much of it.",
         "They're cheap, interpretable baselines before you move to a fine-tuned Transformer."],
        trap_title="\"Switching to a better model will fix the negation errors\"",
        trap_html="<p>It sounds right, since logistic regression is usually stronger than Naive Bayes. But in the lab, both score about 53% on unigrams and both reach 94% with bigrams. The features were the problem, not the model. A fine-tuned Transformer does handle negation better, but at the cost of GPU training and slower inference, so try the cheap fix first.</p>"),
    "fundamentals/n-gram-language-models": _plan(
        "The review box suggests the next word as customers type, using a bigram model built from 400 past reviews. Then someone types \"the paneer was crispy\", which it has never seen, and its probability comes out as zero. The interviewer asks:",
        "How does an n-gram model work, and what do you do about pairs it has never seen?",
        "Think of guessing the next word from a tally of what followed the last word in past reviews. It's quick and needs no training beyond counting. But if the tally has no entry for a pair, it calls that pair impossible.",
        NEXTWORD_PICTURE, "Illustrative bars. In the lab, P(\"not\" | \"was\") is 0.415.",
        ("c4", "<b>Try to break it.</b> Score \"the paneer was crispy\" with no smoothing, then with add-1 and add-k. Then score the scrambled sentence, and watch held-out perplexity.", "<b>Now say why:</b> add-1 fixes the infinite perplexity, so why does held-out perplexity get worse?"),
        ["c2"], ["c5"], ["c3"], ["src"],
        ["A language model assigns probabilities to word sequences, using the chain rule.",
         "An n-gram model approximates the history with the last n − 1 words.",
         "It estimates those probabilities from counts.",
         "Unseen n-grams get zero, so you smooth, with add-k, backoff, interpolation or Kneser–Ney.",
         "Perplexity is the exponential of the average negative log-likelihood on held-out text.",
         "Lower is better, and it's roughly the effective number of choices per word.",
         "LLMs are still next-token predictors measured by perplexity."]),
    "fundamentals/subword-tokenisation": _plan(
        "Your review model must handle \"biryani\", \"biryanis\" and words it has never seen. A word vocabulary turns unseen words into an unknown token, and characters make sequences 4–5 times longer. The interviewer asks:",
        "How do LLMs handle words they've never seen?",
        "Think of a box of building bricks. Common words get their own big brick, and a rare word is built from smaller ones. You can always build something, because the smallest bricks are always in the box.",
        BRICKS_PICTURE, "From the lab, after 120 merges. _ marks the end of a word, and the rare word splits into 9 small pieces.",
        ("c3", "<b>Try to break it.</b> Start at 0 merges, then move to 40 and 120. Watch \"biryani\", the unseen \"biryanis\" and \"unbelievably\".", "<b>Now say why:</b> why does each extra merge shorten sequences by less, and what does a bigger vocabulary cost you?"),
        ["c2"], ["c4", "c5"], [], ["src"],
        ["Subword tokenisers balance word vocabularies, which can't handle unseen words, against characters, which make sequences too long.",
         "BPE starts from characters and repeatedly merges the most frequent adjacent pair.",
         "Common words become single tokens, and rare words split into reusable pieces.",
         "Byte-level BPE can encode any text with no unknowns.",
         "WordPiece, used by BERT, chooses merges by likelihood gain.",
         "The unigram model prunes a large vocabulary instead.",
         "Tokenisation affects cost, context length and multilingual fairness.",
         "It also explains quirks like letter counting and arithmetic."],
        tabs=["Intuition", "How it works", "In practice"],
        trap_title="\"LLMs read words\"",
        trap_html="<p>It sounds right, since words are what we type. But they read subword tokens, chosen by frequency and not by meaning. A model sees \"strawberry\" as 2–3 tokens rather than letters, which is why letter counting can fail. \"Biryani\" and \" biryani\" can be different tokens. And Hindi, Tamil or Bengali text can take many more tokens per word, so the same content costs more.</p>"),
    "fundamentals/sequence-labelling-and-ner": _plan(
        "The app's chat parses \"order 2 chicken biryani from Paradise Biryani House in Hyderabad at 8 pm\" to place the order automatically. A review classifier gives one label per text, but here you need to know which words are the dish and which the restaurant. The interviewer asks:",
        "How do you label spans of text, and how should you score it?",
        "Think of marking a sentence with highlighters, one colour per entity type. B- is where you put the pen down. I- is where you keep going. Because every entity starts with a fresh B-, two neighbouring dishes stay two dishes.",
        BIO_PICTURE, "BIO tags from the lesson's order. Anything outside an entity is O.",
        ("c4", "<b>Try to break it.</b> Switch between perfect, boundary errors, wrong types, missed one entity and predict all O. Compare token accuracy with entity F1.", "<b>Now say why:</b> with boundary errors, token accuracy still says 77%. Why is entity F1 only 0.60?"),
        ["c2", "c3"], ["c5"], [], ["src"],
        ["Sequence labelling assigns a label to every token, as in POS tagging or NER.",
         "BIO tags encode spans: B for the first token, I for the rest, O for outside.",
         "That keeps adjacent entities of the same type separate.",
         "HMMs and CRFs score whole tag sequences and decode with Viterbi, which avoids invalid transitions.",
         "Then came BiLSTM-CRFs, and now fine-tuned BERT-style encoders with a per-token classifier.",
         "Subwords: label the first piece.",
         "Evaluate with entity-level precision, recall and F1, where boundaries and type must match exactly."],
        tabs=["Intuition", "How it works", "In practice"],
        edits=[('<div data-o="tags" style="overflow-x:auto">', '<div data-o="tags" style="overflow-x:auto" tabindex="0" role="group" aria-label="Gold and predicted tags">')],
        trap_title="\"Report token accuracy\"",
        trap_html="<p>It sounds right, since every token gets a label and you can count the correct ones. But most tokens are O, so on real text, predicting all O can score over 80% while finding nothing. In the lab, two boundary errors still give 77% token accuracy, yet the system would look up the wrong restaurant. That's why NER is reported as entity-level F1.</p>"),
    "fundamentals/search-and-retrieval": _plan(
        "The app's search box gets exact names like \"paradise biryani\", vague cravings like \"fiery rice dish\" and mixtures of both. A teammate says to replace keyword search with embeddings, since they understand meaning. The interviewer asks:",
        "Why does search miss exact names, and how does hybrid fix it?",
        "Think of two librarians. One checks the catalogue for your exact words: great for a name, useless if you say \"fiery\" and the book says \"spicy\". The other understands what you're after but is hazy on exact names. So you ask both and merge their lists.",
        SEARCH_PICTURE, "Results from the lab, on 12 listings. The dense vectors are hand-built stand-ins for a trained model.",
        ("c4", "<b>Try to break it.</b> Run \"bawarchi biryani\", then \"fiery rice dish\", then the mixed query, comparing the three columns. Then change BM25's k₁ and b.", "<b>Now say why:</b> why does each method fail on the other's query, and why is hybrid never the worst?"),
        ["c2", "c3"], ["c5"], [], ["src"],
        ["Sparse retrieval uses an inverted index and BM25.",
         "BM25 is TF-IDF with saturation from k1 and length normalisation from b.",
         "It's fast and excellent for exact names and rare terms, but blind to synonyms.",
         "Dense retrieval embeds queries and documents with a contrastively trained encoder, then does approximate nearest-neighbour search.",
         "It matches meaning, but can miss exact terms and degrade out of domain.",
         "Hybrid search fuses the two rankings with reciprocal rank fusion.",
         "A cross-encoder re-ranks the top candidates.",
         "You measure recall@k, MRR or nDCG."],
        edits=[("previous lesson", "TF-IDF lesson")],
        trap_title="\"Dense retrieval has replaced BM25\"",
        trap_html="<p>It sounds right, since matching meaning seems strictly better than matching words. But on the BEIR benchmark of 18 datasets, many dense retrievers failed to beat BM25 out of domain, and exact names and product codes are especially hard for embeddings. Hybrid is standard. And measure retrieval recall by itself, because the LLM can't use a passage it never sees.</p>"),
    "fundamentals/nlp-evaluation-metrics": _plan(
        "The support bot summarises complaints, and you score it automatically against human summaries. A correct paraphrase gets BLEU 0.29, and a word salad gets 0.36. So does a summary saying the opposite of the complaint. The interviewer asks:",
        "How do you score generated text, and what do these metrics miss?",
        "Think of a teacher marking essays by counting the words that match the answer key. Shuffle the key and you score well. Write a correct answer in your own words and you lose marks. The count measures shared words, not shared meaning.",
        BLEU_PICTURE, "Sentence BLEU from the lab, with add-1 smoothing for 2- to 4-grams.",
        ("c3", "<b>Try to break it.</b> Go through identical, paraphrase, word salad, too short and wrong meaning. Compare BLEU, ROUGE-1 and ROUGE-L on each.", "<b>Now say why:</b> why does word salad get a perfect ROUGE-1 and token F1?"),
        ["c2"], ["c4", "c5"], [], ["src"],
        ["BLEU, for translation, is the geometric mean of clipped 1- to 4-gram precisions times a brevity penalty.",
         "It's meant for corpus-level scoring.",
         "ROUGE, for summarisation, measures n-gram recall or F1, and ROUGE-L uses the longest common subsequence.",
         "Extractive QA uses exact match and token F1, and language models use perplexity.",
         "Overlap metrics reward the same words, not the same meaning.",
         "So you add embedding metrics like BERTScore, LLM-as-judge, task checks like faithfulness and human evaluation."],
        trap_title="\"A higher BLEU means a better system\"",
        trap_html="<p>It sounds right, since a higher score ought to mean a closer match. But in the lab, the summary with the opposite meaning beats the correct paraphrase on BLEU and ROUGE-L. And small BLEU differences often don't match human judgement. Nor does ROUGE measure factual correctness, so check faithfulness separately.</p>"),
}
