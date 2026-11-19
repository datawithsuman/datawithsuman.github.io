# Fine-Tuning Incidents

> 9 incidents: wrong chat template, echoing users, forgetting, leaked evals, LoRA that does nothing, flattering DPO, memorised personal data.

- Track: AI Engineering › LLMOps › Scenarios
- Type: Interview · 40 min
- Page: https://aimlrounds.com/tracks/ai-engineering/fine-tuning-incidents/
- Before this: SFT and Instruction Tuning (`fundamentals/supervised-fine-tuning`), LoRA and QLoRA: Parameter-Efficient Fine-Tuning (`fundamentals/lora-and-qlora`)
- Quiz topic: `llmops`

How to use this page

Give yourself about 5 minutes per question, as in an interview. Each is a symptom after fine-tuning a model. Say your diagnosis out loud (most likely cause first, how you'd confirm it, then the fix), then open the answer and compare.

**The diagnosis order:** compare with the base model on the same eval → check the data (format, template, duplicates, leaks) → check the training setup (masking, learning rate, epochs, adapters) → check serving matches training → fix, then keep a general-skills eval beside the task eval.

Question 1 · Easy · chat template

### Your fine-tuned model looked great in the training notebook, but in production it rambles, ignores the system prompt and sometimes writes the user's next turn. What's the first thing to check?

Answer: **the chat template at serving time doesn't match the one used in training**

1. Models learn the exact role markers and special tokens they were trained on; a different template confuses them.

2. Print the exact token sequence the server sends and compare it with a training example.

3. Fix: use the same template, including special tokens and system-prompt format, in training and serving, and test the served endpoint, not just the notebook.

**Follow-up:** It also never stops generating. Why? The end-of-turn token is missing from training examples or not set as a stop token when serving.

Question 2 · Easy · masking

### After fine-tuning on support chats, the model sometimes repeats the customer's message back before answering. What likely went wrong in training?

Answer: **the loss was computed on the prompt tokens too, so the model learned to produce user text**

1. In SFT, only the assistant's tokens should be targets; the prompt is context.

2. Check the data collator or training config for loss masking on non-assistant tokens.

3. Fix: mask the prompt and user turns in the loss, retrain, and add an eval case for echoing.

**Follow-up:** Does masking change what the model sees? No, it still reads the whole conversation; it just isn't rewarded for predicting the user's words.

Question 3 · Medium · forgetting

### You fine-tuned an 8B model on 50,000 support chats. Support answers improved, but it now does worse at simple maths and following general instructions. Why, and what do you change?

Answer: **catastrophic forgetting from narrow data and too much training**

1. Training hard on one narrow task shifts weights away from general skills.

2. Compare with the base model on a general-skills eval, not just the support eval.

3. Fix: lower the learning rate and epochs, use LoRA, mix in some general instruction data, and keep a general eval as a release gate.

**Follow-up:** Would RAG have avoided this? For knowledge, often yes; fine-tune for behaviour and format, and keep facts in retrieval.

Question 4 · Medium · leakage

### The fine-tuned model scores 95% on your evaluation set, but users say it's no better than before. What do you suspect first?

Answer: **the eval set overlaps the training data, so the score measures memorisation**

1. Near-duplicate examples in both sets inflate scores without real improvement.

2. Check for exact and near-duplicate matches between training and eval data.

3. Fix: deduplicate, build the eval from separate, recent real traffic, and keep a held-out set that never touches training.

**Follow-up:** How else can eval mislead? If it doesn't look like real traffic, for example clean questions versus messy real ones, high scores won't carry over.

Question 5 · Medium · overfitting

### Training loss keeps falling, but validation loss starts rising after the second epoch, and the model's answers become oddly templated. What's happening?

Answer: **overfitting to the training examples**

1. The model is memorising phrasing in a small or repetitive dataset.

2. Plot training and validation loss per step, and read samples at each checkpoint.

3. Fix: stop at the best validation checkpoint, train fewer epochs, add more varied data or lower the learning rate.

**Follow-up:** Templated answers aren't always bad. When do you want them? For strict formats, but then enforce the format with structured output instead of overfitting.

Question 6 · Medium · LoRA

### You trained a LoRA adapter, and training metrics improved, but the deployed model behaves exactly like the base model. What could be wrong?

Answer: **the adapter isn't actually applied at serving time, or doesn't match the base model**

1. Common causes: the adapter isn't loaded or merged, the request doesn't select it, or it was trained on a different base model version.

2. Compare outputs with and without the adapter on the same prompt, and check the server logs for adapter loading.

3. Fix: load or merge the adapter explicitly, pin the base model version, and add a smoke test that checks a behaviour only the adapter has.

**Follow-up:** Can one server host many adapters? Yes, multi-LoRA serving loads many adapters on one base model and picks one per request.

Question 7 · Hard · preference tuning

### After DPO on preference data, the model's answers got much longer and more flattering, and win rates from an LLM judge went up, but users are less happy. What happened?

Answer: **the preference data and the judge both reward length and agreeableness, so the model learned to game them**

1. If chosen answers are usually longer or more agreeable, preference tuning learns length and flattery rather than quality.

2. Check the length distribution of chosen versus rejected answers, and compare judge wins with human ratings.

3. Fix: balance or length-control the preference data, tune the strength of the reference constraint, and validate with human evaluation and length-aware metrics.

**Follow-up:** Why did the judge agree? LLM judges also tend to prefer longer answers, so the bias was in both the training signal and the evaluation.

Question 8 · Hard · privacy

### During testing, a fine-tuned model completed a prompt with a real customer's phone number from the training chats. What do you do?

Answer: **the model memorised personal data that was in the training set**

1. Fine-tuning data contained unredacted personal data, and repeated or unusual strings are especially likely to be memorised.

2. Search the training data for the leaked value, and run extraction tests with prefixes from real records.

3. Fix: stop using the model, scrub and deduplicate the data, retrain, add extraction tests to release checks, and follow your data-incident process.

**Follow-up:** Can output filters solve it? They help as a last layer, but the real fix is keeping personal data out of training.

Question 9 · Hard · drift

### Six months after fine-tuning, the support model gives outdated answers about prices and policies, and accuracy keeps sliding. What's the root problem?

Answer: **facts were baked into the weights, and the world changed**

1. Fine-tuning freezes knowledge at training time; prices and policies change.

2. Check which failures are about changed facts rather than behaviour.

3. Fix: move changing facts into retrieval, keep fine-tuning for tone and format, and schedule evaluation on fresh questions.

**Follow-up:** When is retraining still right? When behaviour needs updating, like new tools or formats, and then with a regression eval first.

**More practice and sources**

9 interview questions, easy to hard · answers hidden until you click · checked 10 Nov 2026

Keep practising

Uses these lessons: SFT and Instruction Tuning, LoRA and QLoRA, DPO, Prompt vs RAG vs Fine-Tuning, Evaluating LLM Apps and Model Upgrades.
