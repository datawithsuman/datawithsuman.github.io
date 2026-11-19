# Design a Document Extraction Pipeline

> Thousands of suppliers send invoices in different layouts and languages, and people type them in by hand. Design a system that extracts the data accurately and knows when to ask a person.

- Track: System Design › Document AI › Designs
- Type: Design · 25 min
- Page: https://aimlrounds.com/tracks/system-design/design-document-extraction/
- Before this: Parsing and Chunking (`ai-engineering/parsing-and-chunking`), Structured Output and Constrained Decoding (`ai-engineering/structured-output`)
- Quiz topic: `sdllm`

## Intuition

### The situation

A large company pays thousands of suppliers. Invoices arrive by email and upload, in over 25 languages and many layouts, some scanned or handwritten. People type in about 20 fields per invoice, and rule-based tools break on every new layout. Say 10,000 invoices a day. The interviewer asks:

> Thousands of suppliers send invoices in different layouts and languages, and people type them in by hand. Design a system that extracts the data accurately and knows when to ask a person.

#### Ask before designing

- **Documents:** which types, from how many senders, in how many languages and layouts? Scans, photos, handwriting, multi-page files?

- **Fields:** say 15–20 header fields like invoice number, date and total, plus line items. Which ones are critical?

- **Scale:** say 10,000 invoices a day, mostly as PDFs by email or upload.

- **Accuracy:** what does a wrong field cost? A wrong amount means a wrong payment, so some fields need near-perfect accuracy.

- **Must never happen:** paying the wrong amount or the wrong supplier, or losing an invoice.

- **Success metrics:** field accuracy, share processed without a person, handling time per invoice and cost per invoice.

### The idea

Think of a careful new clerk. They read any invoice layout, copy the details onto a standard form, then check the sums add up and the supplier is real before passing it on. Anything odd goes to a senior clerk, who sees the invoice and the form side by side.

[Figure: Files become one format, OCR reads them, an LLM fills a fixed schema, and rules check the result before a person reviews anything uncertain.]

_The model fills the form; rules and people decide what's safe to pay._

### Play

**Try to break it.** Start with the top band only. Lower the line one step at a time. Then turn on the rule checks.

#### Where do you set the auto-approve line?

Illustrative: four confidence bands. The top band, 35% of invoices at 99.5% accuracy, mirrors the post's share of near-perfect invoices; the other bands (30% at 95%, 20% at 85%, 15% at 60%) are made up. Rule checks catch 70% of errors in auto-approved invoices. A review takes 2 minutes. 10,000 invoices a day.

Start at the top band only. Then lower the line, and watch errors climb faster than review time falls. Now turn on rule checks: they catch many errors cheaply, which is why **validation sits between the model and the payment**. Full automation only makes sense for fields and suppliers where accuracy has stayed near-perfect over time.

**Now say why:** why do rule checks catch errors that the model's confidence misses?

## Architecture

### Architecture

#### In one breath

Turn every file into a **standard format**, run **OCR**, and ask an LLM to fill a **fixed schema** of fields. Don't trust the output blindly: a **post-processing layer** applies business rules and cross-checks against your own records, and anything uncertain goes to a **person** who sees the document and the extracted fields side by side. Measure accuracy **per field**, and only automate fully where accuracy has been proven over time.

#### From inbox to payment

1. **Ingest:** pull invoices from email, tickets and uploads into object storage, with a record for each.

2. **Pre-process:** convert PDFs, Word files and images into one standard format, split pages, and clean up low-resolution scans.

3. **OCR:** extract text and layout from each page.

4. **Extract:** an LLM reads the text and fills a fixed schema of fields and line items, using structured output so the result always parses.

5. **Validate:** business rules and cross-checks: do line items add up to the total? Does the supplier exist? Does a purchase order match?

6. **Review:** uncertain or failed invoices go to a person, who sees the document and extracted fields side by side, with warnings. Approved data goes to the finance system.

##### Why a workflow engine

Documents take many paths: retries, reviews, re-extraction. A durable workflow engine tracks each document's state, so nothing is lost when a step fails.

##### One platform, many document types

Build the pipeline once and make new document types a configuration: a schema, rules and examples. Then receipts or contracts don't need a new system.

#### The numbers worth saying out loud

All of these are assumptions for the interview, not figures from a real system.

| Question | Working | Result |
|---|---|---|
| Pages a day | 10,000 invoices × 3 pages | **30,000** |
| LLM tokens a day | 10,000 × (3 pages × 1,500 + 800 output) | **about 53 million** |
| Peak rate | 10,000 ÷ 8 working hours ÷ 3,600 × 3 | **about 1 invoice a second** |
| Storage a year | 10,000 × 300 days × 500 KB | **about 1.5 TB** |

The volume is modest, so the design is driven by accuracy, traceability and review cost, not raw throughput. Batch processing is fine; invoices don't need answers in milliseconds.

## In practice

### In practice

#### What every extraction design gets asked

- **Which model?** Fine-tuned small models can do well on header fields but struggle with line items and can invent rows. A strong general LLM often adapts better to new layouts. Compare on your own labelled invoices, per field.

- **Measuring accuracy:** compare against data people already entered. Use exact match for IDs and amounts, and fuzzy matching for free text like descriptions. Track header and line-item accuracy separately, over time and per supplier.

- **Labelling:** start with the highest-volume suppliers and the fields with the worst accuracy, where fixes pay off most.

- **Confidence:** combine model signals with rule checks to decide what goes to review. Rules catch errors the model is confident about.

- **The review screen:** show the document and fields side by side, highlight where each value came from, and flag warnings, so a check takes seconds.

- **Feedback:** corrections become labelled data for evaluation, prompts and examples.

- **Security:** invoices hold bank details, so restrict access, keep an audit trail and check that bank details match the supplier's record.

##### Rollout

Run the system alongside the manual process first, comparing results without acting on them. Then let it pre-fill fields for reviewers, and only later auto-approve the safest cases.

#### What the real system reported

- **The problem:** thousands of suppliers with different templates, invoices in over 25 languages, handwriting and scans, and 15–20 fields plus line items. Rule-based tools and RPA needed manual rules for every new format.

- **The platform:** a shared document platform giving a reusable interface over OCR and LLMs: ingestion into object storage, pre-processing, OCR through an internal vision platform, LLM extraction, business-rule post-processing and human review, managed by a workflow engine.

- **Models:** fine-tuned open models reached over 90% on header fields but dropped sharply on line items and hallucinated; they chose an out-of-the-box GPT-4 model for accuracy and adaptability.

- **Results:** about 90% overall accuracy; 35% of invoices at near-perfect 99.5% accuracy and 65% above 80%; a 2× reduction in manual invoicing, 70% lower handling time and 25–30% cost savings.

- **Next:** a document classification layer, and full automation only where 100% accuracy has held historically.

The company's own figures, without baselines or sample sizes. We couldn't read the post's diagrams or model comparison table.

### The answer that sounds right

#### "The model is 99% confident, so skip the review"

It sounds right, since confidence seems to mean accuracy. But models can be confidently wrong, especially on new layouts and line items, and a wrong amount means a wrong payment. Check money fields with rules that don't depend on the model, and only auto-approve suppliers and fields with a long, proven record.

## Say it

### Thousands of suppliers send invoices in different layouts and languages, and people type them in by hand. Design a system that extracts the data accurately and knows when to ask a person.

#### The interviewer pushes further

Follow-up 1 of 3

Why not fine-tune a small model? It's cheaper.

It can be, and it may match a large model on simple header fields. But line items vary a lot, and fine-tuned small models can drop in accuracy or invent rows. I'd compare both on our own labelled invoices, per field, and could use a small model for easy fields and a large one for the rest.

Follow-up 2 of 3

The model is 99% confident, but the amount is wrong. How do you catch that?

With rules that don't depend on the model: line items must sum to the total, tax must match the rate, and the amount should match the purchase order. Confidence alone isn't enough for money.

Follow-up 3 of 3

A new supplier sends a layout you've never seen. What happens?

The LLM handles new layouts better than templates, but I'd send that supplier's first invoices to review regardless of confidence, use the corrections as examples, and only auto-approve once their accuracy has been proven.

First I'd clarify the document types, senders, languages, fields, volume and the cost of a wrong field. Invoices come in by email and upload into storage, tracked by a workflow engine so none are lost. I'd convert every file to a standard format, run OCR, and ask an LLM to fill a fixed schema with structured output. I wouldn't trust it directly: a validation layer checks that totals add up and that the supplier, purchase order and bank details match our records. Uncertain or failed invoices go to a person, who sees the document and fields side by side with warnings. I'd measure accuracy per field against data people already entered, exact match for amounts and fuzzy match for text, and track it per supplier. Labelling starts with high-volume suppliers and weak fields. I'd choose the model by per-field accuracy on our own invoices, especially line items. Rollout runs in parallel with the manual process first, then pre-fills for reviewers, and only auto-approves cases with a proven record.

**Key terms and sources**

Based on a ride-hailing company's published system: Uber's "Advancing Invoice Document Processing using GenAI" (April 2025). We couldn't read the post's diagrams or its model comparison table. The lab's numbers, apart from the share of near-perfect invoices, and the estimate are ours. Uses parsing, structured output and human-in-the-loop design.
