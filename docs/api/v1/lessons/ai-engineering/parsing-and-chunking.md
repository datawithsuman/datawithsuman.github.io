# Parsing and Chunking

> Your RAG misreads tables and splits answers in half. How do you parse and chunk documents?

- Track: AI Engineering › RAG › Lessons
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/ai-engineering/parsing-and-chunking/
- Before this: RAG End to End (`ai-engineering/rag-end-to-end`)
- Quiz topic: `rag`

## Intuition

### The situation

Your policy assistant answers plain questions well, but gets refund amounts wrong. You look at the chunks, and the table's headers are in one chunk and its values are in another. A colleague suggests a smarter chunker. The interviewer asks:

> Your RAG misreads tables and splits answers in half. How do you parse and chunk documents?

#### Why it matters

RAG End to End shows the chunk size trade-off. In real systems, though, the damage often starts earlier. Uber's team found PDF loaders "often fail to correctly capture structured text and formatting (such as bullet points and tables)", and tried several without finding a universal solution. If a table's headers are gone, no retriever can bring them back.

### The idea

Think of photocopying a recipe book and cutting it into cards. If the copier scrambles the ingredients table, no filing system can save you. And if you cut through the middle of a recipe, each card is useless alone. So get a clean copy first, then cut along the natural breaks.

[Figure: Three steps. Parse cleanly, keeping tables and headings. Split on structure. Add context if a chunk can't stand alone.]

_You can't recover what parsing lost._

### Play

**Try to break it.** Start with flattened text at 20 words. Then raise the size. Then keep the table.

#### Break a table

Exact calculation on a short invented refund policy with one table, and 6 questions. Retrieval takes the top 2 chunks by word overlap with the question. A question counts as answerable only if a single retrieved chunk holds the row, the column header and the value. The box shows how the chunk holding the first table row looks.

With **flattened text at 10 words**, only 2 of 6 questions can be answered, as the table's headers land in one chunk and its values in others. Keep the **table row by row**, and it's 4 of 6 at the same size, because every row carries its own headers. At 20 words both reach 6 of 6, but the kept table sends 23 words per question, against 40 for flattened. Raise flattened text to 120 words, and it still scores 6 of 6, but it sends 103 words, as the whole policy is one chunk. This lab also flatters flattened text: it only checks that the words share a chunk. A model still has to work out which number belongs to which column.

**Now say why:** why does a big chunk answer more, yet still cost more?

## How it works

### How it works

#### In one breath

Before you can retrieve anything, messy documents have to become clean text. **Parsing** is where tables lose their headers and scanned pages lose their layout. **Chunking** then decides what each retrieved piece contains. The best start is simple: split on the document's own structure, keep tables whole, and test a few sizes on your own questions. **Semantic chunking** is often not worth its cost. If a chunk doesn't make sense alone, add context with **contextual** or **late chunking**. For pages full of charts, you can embed the **page image** instead.

#### From documents to chunks

##### Parsing comes first

| Content | What goes wrong | What helps |
|---|---|---|
| **Tables** | Rows flatten, headers separate from values | Convert to markdown, repeat headers per row, and never split one mid-table |
| **Headings and lists** | Lost, so a chunk doesn't know its section | Prefer a source with structure, such as HTML, and keep the heading path as metadata |
| **Scans and charts** | OCR drops layout and labels | Layout-aware parsing, captions, or embedding the page image |

Uber moved its policy documents from PDFs to a format with headings and tables it could extract reliably, used an LLM to turn tables into markdown, and gave each table chunk a short summary and keywords.

##### Chunking methods

| Method | How | Evidence and cost |
|---|---|---|
| **Fixed size** | Every N tokens or sentences | Cheap, and a strong baseline |
| **Structure-aware** | Split on headings, paragraphs, list items and tables | Cheap once parsing works. Our suggested default |
| **Semantic** | Split where similarity between sentences drops | Qu et al. found gains were inconsistent, and didn't justify the cost |
| **Contextual** | An LLM adds a sentence of context to each chunk | Anthropic: failures fell from 5.7% to 3.7%, at $1.02 per million document tokens |
| **Late chunking** | Embed the whole document, then pool tokens per chunk | About 3% better than naive chunking on four test sets, with no LLM call |
| **Small to big** | Search small pieces, then send their surrounding section | Precise matching with enough context. In ARAGOG, sentence window retrieval had the best precision |

##### What the evidence says

- **The choice does matter:** in one 450-setup study, 20 chunking setups spanned 0.126 in NDCG@10, a 36% relative gap.

- **Semantic chunking isn't a free win:** Qu et al. saw it help mainly on artificial documents stitched from different topics. On real ones, fixed size often did as well or better.

- **Overlap isn't magic:** Qu et al. saw little from a 1-sentence overlap, and a 16-token overlap showed no clear advantage in the late chunking paper. It can still rescue an answer cut at a boundary, so test it rather than assume it.

- **Chunking still beats no chunking:** even long-context embedding models did better on chunks in most tests, with a 24% average gain at 512 tokens.

##### Pages as images

ColPali embeds page images directly and skips OCR. In one benchmark on financial and technical reports, page-image retrieval beat all the text pipelines. Single-vector page images were also cheap, while the multi-vector version used over 5 GB and took over 20 seconds per query. These documents are visually rich, so don't assume the same result for plain text.

#### The maths

$$ {\text{chunks}} \approx \frac{{D}}{{s - o}}, \qquad {\text{context sent}} = {k} \times {s} $$

Simple arithmetic for fixed-size chunks with overlap. Structure-aware chunks vary in size, so use the average.

- **chunks in the index**: More chunks mean more embedding cost and more memory.

- **document length**: Total tokens to split.

- **chunk size minus overlap**: Each new chunk moves forward by this much, so overlap adds chunks.

- **what the model reads**: Every retrieved chunk goes in the prompt.

- **chunks retrieved**: More chunks raise the chance of including the answer, and add noise.

- **chunk size again**: Doubling it doubles the cost per question.

## In practice

### In practice

#### In practice

- **Look at your chunks:** print a sample of real chunks, especially tables, before tuning anything. Most parsing bugs are obvious once you see them.

- **Keep metadata:** store the source, section path, page, date and permissions with each chunk. You need them for filters and citations.

- **Test on your own questions:** compare two or three chunk sizes on labelled questions, measuring recall and answer quality, because the best size varies by corpus.

- **Test in the full pipeline:** a chunker that wins alone may not win alongside your re-ranker.

- **Re-indexing costs money:** changing chunks means re-embedding. See Keeping an Index Current.

### The answer that sounds right

#### "We just need a smarter chunker"

It sounds right, since chunking is the obvious knob. But if parsing has already scrambled a table, no chunker can restore it. Studies also found that semantic chunking often doesn't beat fixed size. Look at your real chunks first, because the problem is usually visible.

## Say it

### Your RAG misreads tables and splits answers in half. How do you parse and chunk documents?

#### The interviewer pushes further

Follow-up 1 of 3

What's the difference between contextual chunking and late chunking?

Contextual chunking uses an LLM to write context, then adds it to the chunk's text, so BM25 benefits too, at a cost per chunk. Late chunking embeds the whole document, then pools token vectors per chunk, with no LLM call. It needs a long-context embedding model, and only helps vector search.

Follow-up 2 of 3

Should you always use overlap?

Not by default. Studies have found little average gain, though it can rescue an answer cut at a boundary. It also adds chunks and duplicates in results. Test it on your own questions, and prefer splitting on real boundaries.

Follow-up 3 of 3

A question's answer spans two sections. What do you do?

First check whether the chunks hold together. Try retrieving small pieces and sending their surrounding section, or merging neighbouring chunks at answer time. If the question really needs several facts, query decomposition or a second retrieval step may be the real fix.

#### The 30-second answer

I'd start with parsing, because if a table loses its headers, no retriever can fix it. I'd keep tables whole, preserve headings as metadata, and look at real chunks by hand. For chunking, I'd split on document structure first, then test two or three sizes on labelled questions. Evidence for semantic chunking is weak: one study found its gains inconsistent and not worth the cost. If chunks don't make sense alone, I'd add context, either with an LLM-written sentence, as in contextual retrieval, or with late chunking, which embeds the whole document before pooling each chunk. For visual documents like financial reports, I'd consider embedding page images instead.

**Key terms and sources**

Why parsing often matters more than chunk size, keeping tables and structure intact, what the evidence says about semantic chunking and overlap, contextual and late chunking, and page images. · checked 7 Nov 2026

#### Sources

- [Uber, Enhanced Agentic-RAG](https://www.uber.com/en-CA/blog/enhanced-agentic-rag/)

- [Qu, Bao and Tu, Is Semantic Chunking Worth the Computational Cost?](https://arxiv.org/abs/2410.13070)

- [Günther et al., Late Chunking](https://arxiv.org/abs/2409.04701)

- [Anthropic, Introducing Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval)

- [Levy, Shlomov and Choshen, Retrieval Augmented Generation Compositionality](https://arxiv.org/abs/2610.29722)

- [Eibich et al., ARAGOG](https://arxiv.org/abs/2404.01037)

- [Faysse et al., ColPali](https://arxiv.org/abs/2407.01449)

- [Kuru and Keskin, Evaluating Modern RAG](https://arxiv.org/abs/2608.23176)

Explanations are ours, built from these sources. Lab numbers are illustrative unless a lab says otherwise. Most recent papers are preprints.
