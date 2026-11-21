// Moderation + clean-up rules for interview experiences. Pure functions, no I/O, so they can be tested with node.
// moderate(rawRole, rawBody, facts) returns
//   { status: "approved" | "review" | "rejected", reason, message, role: {title, family}, body }
// "message" is shown to the person posting; "reason" is for the owner's review page.
// role and body come back cleaned, so every post reads the same way.

export const FAMILIES = ["AI Engineer", "ML Engineer", "Data Scientist", "Research", "Applied Scientist", "MLOps / LLMOps", "Other"];
export const MAX_CHARS = 8000;
export const DAILY_LIMIT = 3;
export const normalise = (s) => String(s || "").toLowerCase().normalize("NFKD").replace(/[^a-z0-9]+/g, " ").trim();

// ---------- role ----------
const LEVELS = [
  [/\b(intern|internship|trainee)\b/, "Intern"], [/\b(junior|jr)\b/, "Junior"], [/\bassociate\b/, "Associate"],
  [/\b(senior|sr|snr)\b/, "Senior"], [/\bstaff\b/, "Staff"], [/\b(lead|tech lead)\b/, "Lead"], [/\bprincipal\b/, "Principal"],
];
// First match wins, so specific titles come before broad ones.
const TITLES = [
  [/\b(mlops|llmops|ml ops|llm ops|ml platform|ml infra(structure)?)\b/, "MLOps Engineer", "MLOps / LLMOps"],
  [/\bresearch engineer\b/, "Research Engineer", "Research"],
  [/\b(research scientist|research|^rs$)\b/, "Research Scientist", "Research"],
  [/\b(applied scientist|^as$)\b/, "Applied Scientist", "Applied Scientist"],
  [/\b(data scientist|data science|^ds$)\b/, "Data Scientist", "Data Scientist"],
  [/\b(computer vision|^cv engineer$|vision engineer)\b/, "Computer Vision Engineer", "ML Engineer"],
  [/\bnlp\b/, "NLP Engineer", "ML Engineer"],
  [/\b(genai|gen ai|generative ai|llm|llms|ai engineer|aie|applied ai|prompt engineer|agent|agentic|ai developer)\b/, "AI Engineer", "AI Engineer"],
  [/\b(aiml|ai ml)\b/, "AI/ML Engineer", "ML Engineer"],
  [/\b(mle|ml|machine learning|deep learning|dl)\b/, "ML Engineer", "ML Engineer"],
  [/\bai\b/, "AI Engineer", "AI Engineer"],
];
const OUT_OF_SCOPE = /\b(data analyst|business analyst|analyst|data engineer|frontend|front end|full ?stack|web developer|android|ios|devops|qa|tester|sales|marketing|designer|ui|ux|recruiter|hr|accountant|support|consultant)\b/;

export function normaliseRole(raw) {
  let s = String(raw || "").toLowerCase().normalize("NFKC")
    .replace(/ai\s*[\/&-]\s*ml/g, "aiml").replace(/gen\s*-\s*ai/g, "genai")
    .replace(/\bengg?\b|\bengr\b|\beng\.?\b/g, "engineer").replace(/\bsci\b/g, "scientist")
    .replace(/[^a-z0-9 ]+/g, " ").replace(/\s+/g, " ").trim();
  if (!s) return { title: "", family: "", known: false, inScope: false };
  let level = "";
  for (const [re, name] of LEVELS) if (re.test(s)) { level = name; break; }
  for (const [re, title, family] of TITLES) {
    if (re.test(s)) {
      const t = level === "Intern" ? `${title} Intern` : level ? `${level} ${title}` : title;
      return { title: t, family, known: true, inScope: true };
    }
  }
  // Unknown title: tidy it up and let the owner look at it.
  const tidy = s.split(" ").slice(0, 6).map((w) => (w.length <= 3 && /^[a-z]+$/.test(w) && !["and", "for", "the", "of"].includes(w) ? w.toUpperCase() : w[0].toUpperCase() + w.slice(1))).join(" ");
  return { title: tidy.slice(0, 50), family: "Other", known: false, inScope: !OUT_OF_SCOPE.test(s) };
}

// ---------- company (optional) ----------
// Known spellings, matched on the lower-case name with legal suffixes removed. Anything else is tidied, not changed.
const COMPANIES = ["Google", "Microsoft", "Amazon", "AWS", "Meta", "Apple", "NVIDIA", "Netflix", "Uber", "LinkedIn", "Adobe", "Salesforce",
  "Oracle", "Intel", "Qualcomm", "Samsung", "IBM", "Walmart", "Atlassian", "Intuit", "ServiceNow", "Flipkart", "Swiggy", "Zomato", "Razorpay",
  "PhonePe", "Paytm", "Ola", "Meesho", "CRED", "Zepto", "Myntra", "Nykaa", "Freshworks", "Zoho", "Juspay", "Sprinklr", "InMobi", "ShareChat",
  "Dream11", "Groww", "Zerodha", "Unacademy", "BYJU'S", "OYO", "MakeMyTrip", "PolicyBazaar", "Sarvam AI", "Krutrim", "TCS", "Infosys", "Wipro",
  "HCLTech", "Tech Mahindra", "Accenture", "Deloitte", "EY", "KPMG", "PwC", "Capgemini", "Cognizant", "LTIMindtree", "Fractal", "Mu Sigma",
  "Tredence", "Tiger Analytics", "LatentView", "JPMorgan Chase", "Goldman Sachs", "Morgan Stanley", "American Express", "Mastercard", "Visa",
  "PayPal", "Wells Fargo", "Barclays", "HSBC", "Citi", "Optum", "Gartner", "OpenAI", "Anthropic", "Google DeepMind", "Databricks", "Snowflake"];
const COMPANY_ALIASES = { facebook: "Meta", "meta platforms": "Meta", fb: "Meta", "amazon web services": "AWS", nvidia: "NVIDIA",
  deepmind: "Google DeepMind", "google india": "Google", "microsoft india": "Microsoft", "amazon india": "Amazon", byjus: "BYJU'S",
  "tata consultancy services": "TCS", hcl: "HCLTech", "hcl technologies": "HCLTech", amex: "American Express", jpmorgan: "JPMorgan Chase",
  "jp morgan": "JPMorgan Chase", jpmc: "JPMorgan Chase", gs: "Goldman Sachs", "ernst young": "EY", "ernst and young": "EY", citibank: "Citi",
  "flipkart internet": "Flipkart", "swiggy instamart": "Swiggy", sarvam: "Sarvam AI", "ola krutrim": "Krutrim", ltimindtree: "LTIMindtree" };
const COMPANY_MAP = new Map([...COMPANIES.map((c) => [normalise(c), c]), ...Object.entries(COMPANY_ALIASES).map(([k, v]) => [normalise(k), v])]);
const SUFFIX = /\b(private limited|pvt ltd|pvt|ltd|limited|inc|llc|llp|corp|corporation|co)\b\.?/gi;

export function normaliseCompany(raw) {
  const typed = String(raw || "").normalize("NFKC").replace(/\s+/g, " ").trim();
  if (!typed) return "";
  const key = normalise(typed.replace(SUFFIX, ""));
  if (COMPANY_MAP.has(key)) return COMPANY_MAP.get(key);
  const cleaned = typed.replace(SUFFIX, "").replace(/[^\p{L}\p{N}&.' -]+/gu, " ").replace(/\s+/g, " ").trim();
  return cleaned.split(" ").map((w) => (/^(ai|ml|it|io)$/i.test(w) || (w.length <= 4 && w === w.toUpperCase()) ? (/^(ai|ml|it)$/i.test(w) ? w.toUpperCase() : w) : w[0].toUpperCase() + w.slice(1).toLowerCase())).join(" ").slice(0, 60);
}

// ---------- experience text ----------
// Correct spelling of common terms, applied as whole words regardless of how they were typed.
const TERMS = ["AI", "ML", "LLM", "LLMs", "RAG", "NLP", "DSA", "SQL", "API", "APIs", "GPU", "GPUs", "CPU", "KV", "LoRA", "QLoRA", "RLHF", "DPO", "PPO",
  "BERT", "GPT", "PyTorch", "TensorFlow", "NumPy", "pandas", "scikit-learn", "XGBoost", "LightGBM", "LeetCode", "HackerRank", "HR", "OA", "LLD", "HLD",
  "MCP", "AUC", "ROC", "F1", "BM25", "HNSW", "FAISS", "CNN", "CNNs", "RNN", "LSTM", "GAN", "VAE", "MLOps", "LLMOps", "GenAI", "Kubernetes", "Docker",
  "AWS", "GCP", "Azure", "SageMaker", "Python", "Java", "C++", "JavaScript", "Spark", "Kafka", "Airflow", "Redis", "JSON", "PCA", "SVM", "KNN", "SGD",
  "ReLU", "softmax", "SHAP", "CTR", "A/B", "MLE", "SDE", "DS", "CV", "OOP", "OOPs", "DBMS", "OS", "SQL", "NoSQL", "ETL", "EDA",
  "Hugging Face", "LangChain", "LlamaIndex", "vLLM", "TensorRT", "ONNX", "CUDA", "FastAPI", "Flask", "Django"];
const TERM_MAP = new Map(TERMS.map((t) => [t.toLowerCase(), t]));
const termRe = new RegExp("(?<![\\w/+-])(" + TERMS.map((t) => t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).sort((a, b) => b.length - a.length).join("|") + ")(?![\\w/+-])", "gi");

function sentenceCase(s) {
  return s.replace(/(^|[.!?]\s+|\n\s*(?:• )?)([a-z])/g, (m, pre, c) => pre + c.toUpperCase());
}

export function normaliseBody(raw) {
  let s = String(raw || "").normalize("NFKC")
    .replace(/[​-‍﻿]/g, "").replace(/\r\n?/g, "\n").replace(/\t/g, " ");
  // Shouting or all lower case: rebuild the case from scratch.
  const latin = (s.match(/[A-Za-z]/g) || []).length || 1;
  const upper = (s.match(/[A-Z]/g) || []).length / latin;
  if (upper > 0.6) s = s.toLowerCase();
  // Lines: trim, bullets to "• ", at most one blank line between paragraphs.
  s = s.split("\n").map((l) => l.replace(/ {2,}/g, " ").trim().replace(/^(?:[-*•·>]+|->|=>|\d+[.)])\s+/, "• ")).join("\n").replace(/\n{3,}/g, "\n\n").trim();
  // Round names: r1, round1, 1st round, ROUND - 1 → Round 1.
  s = s.replace(/\b(?:r|round)\s*[-#:]?\s*(\d)\b/gi, "Round $1").replace(/\b(\d)(?:st|nd|rd|th)\s+round\b/gi, "Round $1");
  // Punctuation.
  s = s.replace(/([!?])\1+/g, "$1").replace(/\.{4,}/g, "...").replace(/,{2,}/g, ",").replace(/\s+([,.;:!?])/g, "$1")
    .replace(/([a-z])([,;:])([A-Za-z])/g, "$1$2 $3").replace(/([a-z]{2})([.!?])([A-Z][a-z])/g, "$1$2 $3");
  s = s.replace(/\bi\b(?=[\s'’,.!?]|$)/g, "I").replace(/\bi'(m|ve|d|ll)\b/gi, (m, x) => "I'" + x.toLowerCase());
  s = sentenceCase(s);
  s = s.replace(termRe, (m) => TERM_MAP.get(m.toLowerCase()) || m);
  // Every line that ends in a word or number gets a full stop.
  s = s.split("\n").map((l) => (/[\p{L}\p{N})]$/u.test(l) ? l + "." : l)).join("\n");
  return s;
}

// ---------- signals ----------
const AI_TERMS = ["ai", "ml", "llm", "llms", "genai", "gen ai", "machine learning", "deep learning", "model", "models", "rag", "agent", "agents", "agentic",
  "transformer", "transformers", "attention", "embedding", "embeddings", "vector", "vectors", "fine tuning", "finetuning", "fine tune", "lora", "prompt",
  "prompting", "inference", "training", "neural", "nlp", "computer vision", "cv", "recommendation", "recommender", "ranking", "classification",
  "regression", "clustering", "xgboost", "random forest", "gradient", "overfitting", "bias", "variance", "precision", "recall", "f1", "auc", "loss",
  "evaluation", "evals", "mlops", "llmops", "pytorch", "tensorflow", "feature", "features", "dataset", "data", "a b test", "ab test", "statistics",
  "probability", "hypothesis", "sql", "pandas", "numpy", "python", "dsa", "leetcode", "system design", "case study", "metrics", "tokenization",
  "sampling", "retrieval", "reranking", "chunking", "hallucination", "kv cache", "quantization", "distillation", "rlhf", "dpo", "bert", "gpt", "cnn",
  "lstm", "optimizer", "backpropagation", "linear algebra", "pca", "svm", "decision tree", "logistic regression", "linear regression"];
const INTERVIEW_TERMS = ["round", "rounds", "interview", "interviews", "interviewer", "interviewers", "asked", "ask", "question", "questions", "coding",
  "design", "onsite", "oa", "online assessment", "take home", "assignment", "hr", "hiring manager", "panel", "offer", "rejected", "selected", "cleared",
  "explain", "implement", "whiteboard", "behavioural", "behavioral", "project", "projects", "follow up", "resume", "screening", "phone screen",
  "technical", "manager", "discussion", "test", "problem", "problems", "solve", "solved", "deep dive"];
const SPECIFIC = /\b(asked|asked to|asked me|how would you|how do you|how does|what is|what are|explain|design(?:ed)? an?|implement|write an?|difference between|why does|why do|derive|compare|walk(?:ed)? through)\b|\?/gi;

const ABUSE = ["fuck", "fucking", "bitch", "bastard", "asshole", "madarchod", "bhenchod", "behenchod", "chutiya", "randi", "bhosdike", "gandu"];
const PROMO = /\b(dm me|dm for|whats ?app|telegram|join (?:my|our)|subscribe|follow me|follow us|paid (?:course|referral|mentorship)|referral (?:fee|for money)|discount|coupon|guaranteed (?:job|placement|offer)|earn (?:rs|₹|\$|\d)|buy now|contact me|call me|book a call|my channel|instagram|youtube|link in bio|enroll|enrol)\b/i;
const CONFIDENTIAL = /\b(nda|non[- ]disclosure|confidential|proprietary|do not share|internal only)\b/i;
const NAMED_PERSON = /\b(?:interviewer|recruiter|hr|manager|panelist|panellist|engineer)\s+(?:named\s+|called\s+)?(?!was\b|is\b|asked\b|said\b|gave\b|then\b|from\b|at\b|of\b|for\b|and\b|who\b|round\b)[A-Z][a-z]{2,}\b|\b(?:mr|mrs|ms|dr)\.?\s+[A-Z][a-z]{2,}\b/;
const SELF_NAME = /\b(?:[Mm]y name is|[Mm]yself|[Tt]his is|I am|I'm|[Ii]t's me)\s+[A-Z][a-z]{2,}(?:\s+[A-Z][a-z]{2,})?\b(?!\s+(?:engineer|scientist|developer|intern|student))/;
const LINK = /(https?:\/\/|www\.|\b[a-z0-9-]+\.(com|in|io|ai|net|org|co|me|ly|xyz|app|dev|gg|link)\b)/i;
const EMAIL = /[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/i;
const PHONE = /(?:\+?\d[\s-]?){10,}/;

const distinct = (text, list) => { const t = " " + normalise(text) + " "; return list.filter((w) => t.includes(" " + normalise(w) + " ")).length; };

function gibberish(text) {
  const letters = (text.match(/\p{L}/gu) || []).length;
  const visible = text.replace(/\s/g, "").length || 1;
  if (letters / visible < 0.55) return "mostly symbols or numbers";
  if (/(.)\1{7,}/u.test(text)) return "long runs of one character";
  const words = text.toLowerCase().match(/[a-z]{4,}/g) || [];
  if (words.length > 20) {
    if (words.filter((w) => !/[aeiouy]/.test(w)).length / words.length > 0.25) return "random letters";
    if (new Set(words).size / words.length < 0.25) return "the same words repeated";
  }
  const emoji = (text.match(/\p{Extended_Pictographic}/gu) || []).length;
  if (emoji > 12) return "too many emoji";
  return "";
}

// ---------- verdict ----------
const VAGUE_MSG = "Please add specifics: what were the rounds, and what were you asked? One-line reviews like \"it was easy\" don't help the next person.";
const reject = (reason, message, extra) => ({ status: "rejected", reason, message, ...extra });

// facts: { postsToday, duplicate, nearDuplicate } — duplicate = same text or a close rewrite of an existing post (see similarity)
export function moderate(rawRole, rawBody, facts = {}, rawCompany = "") {
  const raw = String(rawBody || "").trim();
  const role = normaliseRole(rawRole);
  const body = normaliseBody(raw);
  const company = normaliseCompany(rawCompany);
  const extra = { role, body, company };
  if (!role.title) return reject("no role", "Please add the role you interviewed for.", extra);
  if (String(rawRole).length > 80) return reject("role too long", "Please keep the role short, like \"Senior ML Engineer\".", extra);
  if (raw.length > MAX_CHARS) return reject("too long", `Please keep it under ${MAX_CHARS.toLocaleString("en")} characters.`, extra);
  if ((facts.postsToday || 0) >= DAILY_LIMIT) return reject("daily limit", "You've shared the most posts allowed for today. Please try again tomorrow.", extra);
  // Spam
  if (EMAIL.test(raw)) return reject("email", "Please remove email addresses.", extra);
  if (LINK.test(raw)) return reject("link", "Please remove links. Posts can't contain web addresses.", extra);
  if (PHONE.test(raw)) return reject("phone", "Please remove phone numbers.", extra);
  if (String(rawCompany).length > 80) return reject("company too long", "Please keep the company name short.", extra);
  if ([rawCompany, rawRole].some((f) => EMAIL.test(f) || LINK.test(f) || PHONE.test(f))) return reject("contact in field", "Please remove links and contact details from the role or company.", extra);
  if (PROMO.test(raw) || PROMO.test(rawRole) || PROMO.test(rawCompany)) return reject("promotion", "Posts can't promote anything or ask people to contact you.", extra);
  const g = gibberish(raw);
  if (g) return reject("gibberish: " + g, "This doesn't look like an interview experience. Please write it in plain sentences.", extra);
  if (ABUSE.some((w) => (" " + normalise(raw + " " + rawRole) + " ").includes(" " + w + " "))) return reject("abuse", "Please remove abusive language.", extra);
  if (facts.duplicate) return reject("duplicate", "This experience has already been shared.", extra);
  // Vague or off topic
  const words = (body.match(/\p{L}{2,}/gu) || []).length;
  const ai = distinct(body, AI_TERMS), iv = distinct(body, INTERVIEW_TERMS), specific = (body.match(SPECIFIC) || []).length;
  if (words < 15) return reject("vague: too few words", VAGUE_MSG, extra);
  if (!role.inScope) return reject("not an AI/ML role", "This page is only for AI/ML roles, such as ML Engineer, AI Engineer, Data Scientist or Research Scientist.", extra);
  if (ai === 0) return reject("off topic", "This page is only for AI/ML interviews. Please describe the AI/ML rounds and what was asked.", extra);
  if (iv === 0) return reject("vague: no interview details", VAGUE_MSG, extra);
  if (words < 40 && specific === 0 && ai < 2) return reject("vague: no specifics", VAGUE_MSG, extra);
  // Passed: it waits for the 7 AM clean-up. Flags tell the clean-up what to look at closely.
  const flags = [];
  if (facts.nearDuplicate) flags.push("near-duplicate of an existing post");
  if (!role.known) flags.push("unrecognised role");
  if (CONFIDENTIAL.test(raw)) flags.push("mentions NDA or confidential material");
  if (NAMED_PERSON.test(raw)) flags.push("may name a person");
  if (SELF_NAME.test(raw) || /\b(?:my name is|myself)\s+\p{L}{3,}/iu.test(raw)) flags.push("may include the candidate's own name");
  if (words < 40 && ai + iv < 4) flags.push("short and light on detail");
  return { status: "pending", reason: flags.join("; "), message: PENDING_MSG, ...extra };
}
export const PENDING_MSG = "Thanks. We tidy every post for easy reading, and yours will appear by tomorrow morning.";

// ---------- duplicates ----------
// Word 3-grams of the normalised text; Jaccard overlap between two posts. Rewording a post keeps many 3-grams.
export function shingles(text) {
  const w = normalise(text).split(" ").filter(Boolean);
  const out = new Set();
  for (let i = 0; i + 2 < w.length; i++) out.add(w[i] + " " + w[i + 1] + " " + w[i + 2]);
  return out;
}
export function similarity(a, b) {
  if (!a.size || !b.size) return 0;
  let both = 0;
  for (const x of a) if (b.has(x)) both++;
  return both / (a.size + b.size - both);
}
export const DUPLICATE_AT = 0.4;   // reject: the same experience posted again, lightly edited
export const SIMILAR_AT = 0.1;     // flag: the 7 AM clean-up compares the two
