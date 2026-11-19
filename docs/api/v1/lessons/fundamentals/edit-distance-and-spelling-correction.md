# Edit Distance and Spelling Correction

> How do you measure how different two strings are, and how would you correct a misspelt word?

- Track: Fundamentals › NLP Fundamentals › Language models and tokenisation
- Type: Concept · 15 min
- Page: https://aimlrounds.com/tracks/fundamentals/edit-distance-and-spelling-correction/
- Before this: N-gram Language Models and Perplexity (`fundamentals/n-gram-language-models`)
- Quiz topic: `nlp`

## Intuition

### The situation

Customers search for "biriyani", "biryani" and "briyani", and two of those return nothing. A colleague suggests comparing every query against every dish with a simple loop. The interviewer asks:

> How do you measure how different two strings are, and how would you correct a misspelt word?

#### Why it matters

It's a classic coding question and a useful tool: fuzzy search, matching names across databases, cleaning user input and scoring speech recognition. It also connects a dynamic programming pattern to the language models you've already seen.

### The idea

Think of editing a word on paper, using only three moves: cross out a letter, write in a letter, or overwrite one. Edit distance is the fewest moves needed. Rather than trying every sequence of moves, you build the answer from shorter pieces, and write them in a table, so nothing gets worked out twice.

[Figure: Three moves. Delete, insert or substitute a letter. Each costs 1, and a match costs nothing.]

_Each table cell needs only its three neighbours._

### Play

**Try to break it.** Slide the cells filled down. Then set the substitution cost to 2.

#### Fill the table

Exact calculation. The first string runs down the side, and the second along the top. Green cells mark one best path, once the table is full.

Slide **cells filled** down to watch it build row by row. Each new cell only needs the three next to it. Set the substitution cost to **2** for intention → execution: the answer rises from 5 to 8, as substituting now costs as much as a delete plus an insert.

**Now say why:** why don't we need to try every possible sequence of edits?

## Maths

### Maths

#### In one breath

**Edit distance** counts the fewest insertions, deletions and substitutions that turn one string into another. Trying every edit sequence is hopeless, so **dynamic programming** fills a table, using the answers for shorter prefixes. It takes O(mn) time. A **spelling corrector** combines this with a language model: among known words near the typo, choose the one with the highest P(word) × P(typo | word). This is the **noisy channel** idea.

#### Building the table

Let D(i, j) be the distance between the first i letters of one string and the first j letters of the other. To reach it, the last step must be one of three:

| Last step | Comes from | Cost |
|---|---|---|
| **Delete** a letter | The cell above | 1 |
| **Insert** a letter | The cell to the left | 1 |
| **Substitute or match** | The diagonal cell | 1, or 0 if the letters match |

Take the cheapest. The first row and column are just i and j, because turning a string into nothing takes one deletion per letter.

##### Worked example

"kitten" to "sitting" takes 3 edits: substitute k with s, substitute e with i, and insert g.

##### Getting the edits, and saving memory

- **Backtrace:** store which cell each value came from, then walk back from the corner. This gives the alignment as well as the number.

- **Less memory:** each row needs only the row before it. If you only want the distance, that takes O(min(m, n)) memory rather than O(mn).

- **Other costs:** costs can vary. Keyboard neighbours might cost less, or substitution might cost 2, which Jurafsky and Martin also show.

- **Transpositions:** "teh" to "the" costs 2 here, though it's one slip of the fingers. **Damerau-Levenshtein** counts swapping two neighbours as one edit.

##### The noisy channel model

Imagine the intended word passing through a noisy channel that sometimes changes letters. To recover it, combine how common a word is with how likely this typo is for that word.

1. **Candidates:** known words within a small edit distance.

2. **Language model P(c):** how common each one is, ideally given the surrounding words.

3. **Error model P(w | c):** how likely this typo is for that word.

Norvig's short corrector shows why simple versions go a long way, and also where they stop. It got 75% of 270 test words right in development, and 68% of 400 on a final test. Only 3 of the 270 needed more than two edits. Its words unknown to the model and its crude error model caused many of the misses.

#### The maths

$$ D(i,j) = \min\begin{cases}D(i-1,j) + 1\\ D(i,j-1) + 1\\ D(i-1,j-1) + \delta(a_i,b_j)\end{cases} \qquad \hat c = \arg\max_c P(c)\,P(w\mid c) $$

The recurrence is the standard Levenshtein form. The noisy channel formula is as in Norvig’s essay, where P(w) is dropped because it’s the same for every candidate.

- **one table cell**: The distance between the first i letters and the first j letters.

- **delete**: Remove a letter from the first string.

- **insert**: Add a letter from the second string.

- **substitute or match**: δ is 0 when the letters match, and 1 otherwise.

- **the noisy channel**: Pick the candidate c that is both common and a likely source of the typo w.

## In practice

### In practice

#### In practice

- **Don't compare against everything:** over a large dictionary, generate candidates first, using an index of character n-grams or precomputed deletions.

- **Stop early:** if you only care about distance 2 or less, you can compute a narrow band around the diagonal.

- **Use context:** "their" and "there" are both real words, so only a language model can pick between them.

- **Words, not letters:** run the same algorithm over words to get word error rate, the standard speech recognition metric.

- **Normalise first:** lowercase and strip accents if those differences don't matter to you. Divide by length to compare across string sizes.

### The answer that sounds right

#### "The closest word is the right correction"

It sounds right, as fewer edits seems more likely. But several real words can be equally close, and a rare word shouldn't beat a common one. The noisy channel model weighs how common each word is and how likely the typo is, and context can settle cases like "form" and "from".

## Say it

### How do you measure how different two strings are, and how would you correct a misspelt word?

#### The interviewer pushes further

Follow-up 1 of 3

What is the edit distance between "sunday" and "saturday"?

3. Keep the s, insert a and t, keep u, substitute n with r, and keep d, a and y. The table gives the same answer, and shows nothing shorter exists.

Follow-up 2 of 3

How would you spell check against a million-word dictionary quickly?

Don't run the table against every word. Generate candidates with an index: for example, precompute all deletions within distance 2, or use a character n-gram index. Then score the candidates with edit distance and a language model.

Follow-up 3 of 3

Why isn't edit distance enough for spelling correction?

Several real words can be equally close, and it ignores how common they are and what's around them. A typo near both "form" and "from" needs a language model to decide. That's what the noisy channel adds.

Edit distance is the fewest insertions, deletions and substitutions to turn one string into another. I'd use dynamic programming: each cell is the minimum of the cell above plus 1, the cell to the left plus 1, and the diagonal plus 0 or 1, depending on whether the letters match. That's O(mn) time, and O(min(m, n)) memory if I only need the distance. A backtrace recovers the edits. For spelling correction, I'd use the noisy channel model: generate known words nearby, and choose the one that maximises P(word) times P(typo given word), using context where I can.

**Key terms and sources**

Levenshtein distance with dynamic programming, backtrace and alignment, Damerau transpositions, and the noisy channel model for spelling correction.

#### Sources

- Norvig, How to Write a Spelling Corrector

- Levenshtein distance, Wikipedia

- Jurafsky and Martin, Speech and Language Processing

Explanations are ours, built from these sources. Lab numbers are illustrative, and worked examples were checked by calculation.
