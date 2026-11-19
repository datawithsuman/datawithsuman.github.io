# GenAI App Scenarios: Set 2

> 9 incidents: wrong reply language, wrong dates, malformed tool calls, misread tables, lost caveats, forgotten constraints, a template leak, a broken parser, fake citations.

- Track: AI Engineering › LLMOps › Scenarios
- Type: Interview · 35 min
- Page: https://aimlrounds.com/tracks/ai-engineering/genai-scenarios-set-2/
- Before this: GenAI App Scenarios: Set 1 (`ai-engineering/genai-scenarios-set-1`)
- Quiz topic: `llmops`

How to use this page

Give yourself about 5 minutes per question, as in an interview. Each is a real-world symptom in an LLM application. Say your diagnosis out loud (most likely cause first, how you'd confirm it, then the fix), then open the answer and compare.

**The diagnosis order:** reproduce on the eval set → check the inputs the model saw (context, prompt, date, language) → check the model and its version → check code around the model (parsing, caching, templates) → fix, then add the case to the golden set.

Question 1 · Easy · language

### Users who write in Hindi often get replies in English. The system prompt is in English. What do you change?

Answer: **tell the model explicitly to reply in the user's language, and test it**

1. Models often follow the language of the system prompt or context rather than the user.

2. Check failing conversations: is retrieved content in English too?

3. Fix: instruct the model to answer in the user's language (or a detected language passed in), add multilingual cases to the eval set, and check quality per language.

**Follow-up:** Retrieved documents are only in English. Is that a problem? The model can translate, but check accuracy and terminology per language.

Question 2 · Easy · dates

### Your assistant says a coupon 'expires next week' when it expired yesterday, and it gets 'today' wrong. Why?

Answer: **the model doesn't know the current date unless you tell it**

1. A model's sense of time comes from its training data, not the clock.

2. Check whether the prompt includes the current date and time zone.

3. Fix: pass the current date and the user's time zone in every request, and compute date comparisons in code rather than asking the model.

**Follow-up:** Where should the date go in the prompt? Near the end, after stable content, so it doesn't break prompt caching.

Question 3 · Medium · tool calls

### After upgrading the model, about 4% of tool calls have malformed arguments, like a date in the wrong format, breaking downstream services. What do you do?

Answer: **enforce the tool schema and validate arguments before calling tools**

1. Different models follow loose schemas differently.

2. Collect failing calls and compare argument formats before and after the upgrade.

3. Fix: use strict schema-constrained tool calling, validate arguments in code and return clear errors so the model can retry, and add tool-call accuracy to the upgrade eval.

**Follow-up:** Why return the error to the model rather than failing? Models can usually fix a call when told exactly what was wrong.

Question 4 · Medium · tables

### Your RAG system retrieves the right pricing document, but quotes the price from the wrong row of a table. Where's the bug?

Answer: **parsing flattened the table, so rows and columns got mixed up**

1. When a table becomes plain text, the model can't tell which value belongs to which row.

2. Look at the parsed chunk the model saw for that document.

3. Fix: parse tables with their structure, for example as markdown or row-by-row text with headers repeated, and add table questions to the eval set.

**Follow-up:** Is chunking also involved? Yes, if a table is split across chunks, headers may be separated from rows.

Question 5 · Medium · summaries

### Summaries of legal documents read well, but sometimes drop an important exception, like 'except in Maharashtra'. How do you catch and fix this?

Answer: **the summary isn't checked for faithfulness to critical details**

1. Summaries compress, and exceptions and conditions are easy to lose.

2. Build an eval with documents that contain key exceptions and check whether summaries keep them.

3. Fix: ask for conditions and exceptions as a separate required section, check summaries against the source automatically, and show the source passage for key claims.

**Follow-up:** Why not just make summaries longer? Length doesn't guarantee the right details are kept; structure and checks do.

Question 6 · Medium · long chats

### In turn 2 a user says they're vegetarian; by turn 15, the assistant suggests a chicken recipe. What happened?

Answer: **the constraint fell out of the context or got lost among later turns**

1. Long conversations get truncated or summarised, and early details can drop out.

2. Check what history the model actually received at turn 15.

3. Fix: extract key facts and preferences into a short memory that's always included, and test long conversations explicitly.

**Follow-up:** Where should that memory sit in the prompt? In a clearly labelled section near the current turn, so it isn't buried.

Question 7 · Hard · template bug

### A few users received greetings with another user's name. The model wasn't trained on user data. Where do you look?

Answer: **the code that fills the prompt template, for example a shared variable or cache between requests**

1. Personal data in a prompt comes from your code; if it's the wrong user's, something is shared across requests.

2. Trace a bad request: which user ID and template values were used, and is any state reused across threads or cached?

3. Fix: build prompts from request-scoped data only, never cache filled prompts across users, add a test that checks user isolation, and treat it as a data incident.

**Follow-up:** Why is this an engineering bug, not a model bug? The model only repeats what it's given.

Question 8 · Hard · upgrade

### A model upgrade changed the assistant's answer style slightly, and a downstream parser that extracted 'Total: ₹X' from replies started failing. What's the lesson?

Answer: **don't parse free text from a model; use structured output, and test upgrades**

1. Free-text formats drift between model versions.

2. Find every consumer that parses model text.

3. Fix: return structured output with a schema for anything code reads, pin model versions, and run a regression suite including downstream consumers before upgrading.

**Follow-up:** Can you keep free text for the user and structure for code? Yes: ask for both, a JSON object plus a message, in one schema.

Question 9 · Hard · fake citations

### The assistant sometimes cites document IDs that don't exist in your knowledge base. How do you stop it?

Answer: **validate citations in code against the documents actually retrieved**

1. Models can generate plausible-looking IDs when asked to cite.

2. Compare cited IDs with the retrieved set for each answer.

3. Fix: only allow citations from the retrieved list (by index or structured output), check them in code, and drop or flag answers whose citations fail.

**Follow-up:** What if the answer is right but the citation is wrong? Still flag it; users trust citations, so a wrong one is a real error.

**More practice and sources**

9 interview questions, easy to hard · answers hidden until you click · checked 10 Nov 2026

Keep practising

Uses these lessons: GenAI App Scenarios: Set 1, Structured Output, Parsing and Chunking, Grounded Answers, Memory and Context and Model Upgrades.
