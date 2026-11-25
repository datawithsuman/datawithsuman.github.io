// AIML Rounds MCP server: a Cloudflare Worker that serves the site's lessons, roadmaps, quizzes,
// mock interviews and jobs to Claude and other MCP clients over Streamable HTTP (stateless, JSON responses).
// It owns no content: everything is read from the files build.py publishes under /api/v1/ and /jobs/.

const SERVER = { name: "aimlrounds", title: "AIML Rounds", version: "1.1.0" };
const VERSIONS = ["2025-06-18", "2025-03-26", "2024-11-05"];
const TTL_MS = 10 * 60 * 1000;

const INSTRUCTIONS = `AIML Rounds (aimlrounds.com) is a free AI/ML interview-prep site: lessons from maths to LLMs, RAG, agents, inference, MLOps, evals and AI/ML system design; role roadmaps; topic quizzes; mock interviews; and AI/ML jobs in India from the last 7 days.
Use search to find lessons, then get_lesson to read one. Each lesson says when its sources were checked and when its text last changed; for fast-moving facts (prices, model names, benchmarks) mention that date. When you teach from a lesson, follow its own framing (situation → idea → how it works → in practice → the interview answer) and give the lesson link.
For quizzes and mock interviews, ask one question at a time and let the learner answer before revealing anything.`;

// ---------- data ----------
const cache = new Map();

async function load(env, path, kind = "json") {
  const base = (env && env.DATA_BASE) || "https://aimlrounds.com/";
  const hit = cache.get(path);
  if (hit && Date.now() - hit.at < TTL_MS) return hit.value;
  const res = await fetch(base + path, { cf: { cacheTtl: 600, cacheEverything: true } });
  if (!res.ok) {
    if (hit) return hit.value; // serve stale rather than fail
    throw new Error(res.status === 404 ? "not found" : `could not load ${path} (${res.status})`);
  }
  const value = kind === "json" ? await res.json() : await res.text();
  cache.set(path, { at: Date.now(), value });
  return value;
}

const index = (env) => load(env, "api/v1/index.json");

// ---------- helpers ----------
const norm = (s) => String(s || "").toLowerCase().normalize("NFKD").replace(/[̀-ͯ]/g, "");
const words = (s) => norm(s).split(/[^a-z0-9+#]+/).filter((w) => w.length > 1 && !STOP.has(w));
const STOP = new Set("the a an and or of to in on for is are what why how does do with vs versus by at it its be as from that this which when your you i me".split(" "));

function score(row, terms, phrase) {
  const fields = [
    [norm(row.title), 6], [norm(row.lead + " " + row.q), 3], [norm(row.headings.join(" ")), 2],
    [norm(row.section + " " + row.part), 2], [norm(row.id), 2],
  ];
  let s = 0, hit = 0;
  for (const t of terms) {
    let best = 0;
    for (const [text, w] of fields) {
      if (new RegExp(`\\b${t.replace(/[+#]/g, "\\$&")}`).test(text)) best = Math.max(best, w);
      else if (t.length > 4 && text.includes(t.slice(0, -1))) best = Math.max(best, w / 2);
    }
    if (best) hit++;
    s += best;
  }
  if (!hit) return 0;
  s *= hit / terms.length; // reward matching every word
  if (phrase.length > 3 && norm(row.title).includes(phrase)) s += 10;
  return s;
}

const where = (r) => [r.trackName, r.part, r.section].filter((x, i, a) => x && a.indexOf(x) === i).join(" › ");
const brief = (r) => ({ id: r.id, title: r.title, where: where(r), type: r.type, minutes: r.minutes, question: r.lead, url: r.url,
  sources_checked: r.checked || undefined, last_changed: r.updated || undefined, version: r.version || undefined });

async function findLesson(env, ref) {
  const idx = await index(env);
  const key = norm(ref).replace(/^https?:\/\/[^/]+\//, "").replace(/^tracks\//, "").replace(/\/$/, "").replace(/\.md$/, "");
  let row = idx.lessons.find((l) => l.id === key) || idx.lessons.find((l) => l.id.endsWith("/" + key)) ||
    idx.lessons.find((l) => norm(l.title) === norm(ref));
  if (!row) {
    const terms = words(ref);
    const ranked = idx.lessons.map((l) => [score(l, terms, norm(ref)), l]).filter((x) => x[0] > 0).sort((a, b) => b[0] - a[0]);
    if (ranked.length) row = ranked[0][1];
  }
  return row;
}

function pickRole(roles, ref) {
  if (!ref) return null;
  const r = norm(ref);
  return roles.find((x) => x.id === r) || roles.find((x) => norm(x.name) === r) ||
    roles.find((x) => norm(x.name).includes(r) || r.includes(norm(x.name))) ||
    roles.find((x) => (/\b(ai|genai|llm)\b/.test(r) && x.id === "ai-engineering") ||
      (/\bml\b|machine learning|mlops/.test(r) && x.id === "ml-engineering") || (/data|\bds\b/.test(r) && x.id === "data-science"));
}

// old / alternate city names → the spelling the jobs data uses (arrays = any of these)
const CITY_ALIASES = {
  bangalore: "bengaluru", blr: "bengaluru", bengalooru: "bengaluru",
  bombay: "mumbai", "navi mumbai": "mumbai",
  gurgaon: "gurugram", madras: "chennai", calcutta: "kolkata",
  poona: "pune", hyd: "hyderabad", secunderabad: "hyderabad",
  trivandrum: "thiruvananthapuram", cochin: "kochi", mysore: "mysuru",
  "new delhi": "delhi", ncr: ["delhi", "noida", "gurugram"], "delhi ncr": ["delhi", "noida", "gurugram"],
  "work from home": "remote", wfh: "remote",
};

function expRange(v) {
  const m = { "0-2": [0, 2], "2-5": [2, 5], "5-8": [5, 8], "8+": [8, 99], "8-99": [8, 99] }[String(v || "").replace(/\s|yrs?|years?/g, "")];
  if (m) return m;
  const n = parseFloat(v);
  return Number.isFinite(n) ? [n, n] : null;
}

// ---------- tools ----------
const TOOLS = [
  {
    name: "search",
    title: "Search lessons",
    description: "Search AIML Rounds lessons by keywords or an interview question. Filter by track (fundamentals, ai-engineering, system-design, papers), type (concept, interview, design, paper) or section/part name. Returns lesson ids for get_lesson.",
    inputSchema: {
      type: "object",
      properties: {
        query: { type: "string", description: "Keywords or a question, e.g. 'KV cache', 'why does RAG retrieve the wrong chunk'" },
        track: { type: "string", enum: ["fundamentals", "ai-engineering", "system-design", "papers"], description: "Limit to one track: fundamentals, ai-engineering, system-design or papers" },
        type: { type: "string", enum: ["concept", "interview", "design", "paper"], description: "concept = lesson, interview = scenario set, design = system design question, paper = paper explained" },
        section: { type: "string", description: "Part or section name to filter by, e.g. 'RAG', 'LLMs', 'Recommendation Systems'" },
        limit: { type: "integer", minimum: 1, maximum: 30, default: 8, description: "How many lessons to return (1–30, default 8)" },
      },
      required: ["query"],
    },
    annotations: { readOnlyHint: true, openWorldHint: false },
  },
  {
    name: "browse",
    title: "Browse contents",
    description: "Browse the site's table of contents. No arguments: the 4 tracks with their parts and sections. With track: every section and lesson in it (optionally narrowed by part).",
    inputSchema: {
      type: "object",
      properties: {
        track: { type: "string", enum: ["fundamentals", "ai-engineering", "system-design", "papers"], description: "Limit to one track: fundamentals, ai-engineering, system-design or papers" },
        part: { type: "string", description: "Part name within the track, e.g. 'Maths for ML', 'RAG', 'Agentic AI'" },
      },
    },
    annotations: { readOnlyHint: true, openWorldHint: false },
  },
  {
    name: "get_lesson",
    title: "Read a lesson",
    description: "Read one lesson as Markdown: the interview situation, intuition, how it works (with equations in TeX), in practice, and the model interview answer with follow-ups. Use an id from search (e.g. 'ai-engineering/prefill-vs-decode'), a page URL or a title. Use tab to read one part only.",
    inputSchema: {
      type: "object",
      properties: {
        id: { type: "string", description: "Lesson id, URL or title" },
        tab: { type: "string", description: "Optional: only this part, e.g. 'Intuition', 'How it works' / 'Maths', 'In practice', 'Say it' (the interview answer)" },
      },
      required: ["id"],
    },
    annotations: { readOnlyHint: true, openWorldHint: false },
  },
  {
    name: "roadmap",
    title: "Role roadmap",
    description: "The study roadmap for a role (AI Engineer, ML Engineer, Data Scientist): topics in order, core vs useful, each with its lessons and quiz. No role: list the roles.",
    inputSchema: {
      type: "object",
      properties: {
        role: { type: "string", description: "'ai-engineering', 'ml-engineering' or 'data-science' (names like 'AI engineer' work too)" },
        with_lessons: { type: "boolean", default: true, description: "Include lesson titles and ids for each topic" },
      },
    },
    annotations: { readOnlyHint: true, openWorldHint: false },
  },
  {
    name: "quiz",
    title: "Topic quiz",
    description: "Multiple-choice questions for a roadmap topic (e.g. 'Linear algebra', 'RAG', 'Inference and serving'). Answers stay hidden unless reveal_answers is true: ask the learner first, then call again with reveal_answers to grade and explain. No topic: list topics.",
    inputSchema: {
      type: "object",
      properties: {
        topic: { type: "string", description: "Topic id or name" },
        count: { type: "integer", minimum: 1, maximum: 20, description: "How many questions (default: all)" },
        reveal_answers: { type: "boolean", default: false, description: "Include the correct option and its explanation. Keep false while the learner is answering; set true to grade." },
      },
    },
    annotations: { readOnlyHint: true, openWorldHint: false },
  },
  {
    name: "mock_interview",
    title: "Mock interview",
    description: "Mock interview rounds per role, with model answers and what the interviewer listens for. No round: list the role's rounds. Keep include_answers false while the learner is answering; set it true to give feedback.",
    inputSchema: {
      type: "object",
      properties: {
        role: { type: "string", description: "'ai-engineering', 'ml-engineering' or 'data-science'" },
        round: { type: "string", description: "Round id or name" },
        include_answers: { type: "boolean", default: false, description: "Include model answers and what the interviewer listens for. Keep false during the mock; set true to give feedback." },
      },
      required: ["role"],
    },
    annotations: { readOnlyHint: true, openWorldHint: false },
  },
  {
    name: "jobs",
    title: "AI/ML jobs in India",
    description: "AI/ML job postings in India from the last 7 days (100+ companies, refreshed daily), newest first, with direct apply links to the company's careers page. Most jobs include skills and key requirement lines from the job description, useful for matching against a resume. Filter by keywords (title or skill), company, city or years of experience.",
    inputSchema: {
      type: "object",
      properties: {
        query: { type: "string", description: "Words in the job title or a skill, e.g. 'machine learning engineer', 'GenAI', 'PyTorch'" },
        company: { type: "string", description: "Company name or part of it, e.g. 'Walmart', 'Google'" },
        location: { type: "string", description: "City, e.g. 'Bengaluru', 'Hyderabad', 'Remote'. Old names like 'Bangalore' or 'Gurgaon' also work" },
        experience: { type: "string", description: "'0-2', '2-5', '5-8', '8+' or a number of years" },
        limit: { type: "integer", minimum: 1, maximum: 100, default: 20, description: "How many jobs to return (1–100, default 20)" },
      },
    },
    annotations: { readOnlyHint: true, openWorldHint: false },
  },
  {
    name: "whats_new",
    title: "What's new",
    description: "Lessons, designs, quizzes and mock rounds added to the site recently, newest first.",
    inputSchema: { type: "object", properties: { limit: { type: "integer", minimum: 1, maximum: 60, default: 15, description: "How many recent items to return (1–60, default 15)" } } },
    annotations: { readOnlyHint: true, openWorldHint: false },
  },
];

const HANDLERS = {
  async search(a, env) {
    const idx = await index(env);
    const terms = words(a.query);
    if (!terms.length) throw new Error("query needs at least one keyword");
    const sec = norm(a.section);
    const rows = idx.lessons.filter((l) => (!a.track || l.track === a.track) && (!a.type || l.type === a.type) &&
      (!sec || norm(l.part + " " + l.section).includes(sec)));
    const ranked = rows.map((l) => [score(l, terms, norm(a.query)), l]).filter((x) => x[0] > 0).sort((x, y) => y[0] - x[0]);
    const limit = Math.min(a.limit || 8, 30);
    return { query: a.query, total: ranked.length, results: ranked.slice(0, limit).map((x) => brief(x[1])),
      hint: ranked.length ? "Read one with get_lesson(id)." : "No match. Try fewer or broader words, or browse." };
  },

  async browse(a, env) {
    const idx = await index(env);
    const byId = Object.fromEntries(idx.lessons.map((l) => [l.id, l]));
    if (!a.track) {
      return { tracks: idx.tracks.map((t) => {
        const parts = [];
        for (const s of t.sections) {
          const name = s.part || s.name;
          let p = parts.find((x) => x.part === name);
          if (!p) parts.push((p = { part: name, sections: [], lessons: 0 }));
          if (s.name !== name) p.sections.push(s.name);
          p.lessons += s.lessons.length;
        }
        return { id: t.id, name: t.name, url: t.url, parts };
      }), hint: "Call browse(track) to list lessons." };
    }
    const t = idx.tracks.find((x) => x.id === a.track);
    if (!t) throw new Error("unknown track");
    const part = norm(a.part);
    const sections = t.sections.filter((s) => !part || norm(s.part + " " + s.name).includes(part));
    if (!sections.length) throw new Error(`no part matching '${a.part}' in ${t.name}. Parts: ${[...new Set(t.sections.map((s) => s.part || s.name))].join(", ")}`);
    return { track: t.name, url: t.url, sections: sections.map((s) => ({ part: s.part, section: s.name,
      lessons: s.lessons.map((id) => ({ id, title: byId[id].title, type: byId[id].type, minutes: byId[id].minutes })) })) };
  },

  async get_lesson(a, env) {
    const row = await findLesson(env, a.id);
    if (!row) throw new Error(`no lesson matches '${a.id}'. Use search first.`);
    let md = await load(env, `api/v1/lessons/${row.id}.md`, "text");
    if (a.tab) {
      const parts = md.split(/\n(?=## )/);
      const want = norm(a.tab);
      const alias = { how: ["how", "maths", "math"], maths: ["maths", "how"], answer: ["say"], interview: ["say"], say: ["say"] };
      const keys = alias[want.split(" ")[0]] || [want];
      const hit = parts.slice(1).find((p) => keys.some((k) => norm(p.split("\n")[0]).includes(k)));
      const tabs = parts.slice(1).map((p) => p.split("\n")[0].replace(/^## /, ""));
      md = hit ? parts[0].trim() + "\n\n" + hit.trim() : md + `\n\n(Note: no tab '${a.tab}'. Tabs: ${tabs.join(", ")})`;
    }
    return md;
  },

  async roadmap(a, env) {
    const roles = await load(env, "api/v1/roadmap.json");
    if (!a.role) return { roles: roles.map((r) => ({ id: r.id, name: r.name, about: r.blurb, topics: r.steps.length, url: r.url })) };
    const r = pickRole(roles, a.role);
    if (!r) throw new Error(`unknown role. Roles: ${roles.map((x) => x.id).join(", ")}`);
    const idx = await index(env);
    const byId = Object.fromEntries(idx.lessons.map((l) => [l.id, l]));
    return { role: r.name, about: r.blurb, url: r.url, mock_interview: r.mock || null,
      steps: r.steps.map((s, i) => ({ step: i + 1, topic: s.name, topic_id: s.topic, level: s.level, quiz: s.quiz || null,
        lessons: a.with_lessons === false ? s.lessons.length : s.lessons.map((id) => ({ id, title: byId[id] ? byId[id].title : id })) })),
      note: "core = needed for this role; useful = good to know." };
  },

  async quiz(a, env) {
    const qz = await load(env, "api/v1/quizzes.json");
    const list = Object.values(qz);
    if (!a.topic) return { topics: list.map((q) => ({ id: q.id, name: q.name, questions: q.questions.length })) };
    const t = norm(a.topic);
    const q = qz[a.topic] || list.find((x) => norm(x.name) === t) || list.find((x) => norm(x.name).includes(t) || t.includes(norm(x.name)));
    if (!q) throw new Error(`no quiz for '${a.topic}'. Call quiz() with no topic to list them.`);
    const n = Math.min(a.count || q.questions.length, q.questions.length);
    const L = "ABCD";
    return { topic: q.name, url: q.url, questions: q.questions.slice(0, n).map((x, i) => {
      const out = { n: i + 1, question: x.q, options: x.options.map((o, j) => `${L[j]}. ${o}`) };
      if (a.reveal_answers) Object.assign(out, { answer: L[x.answer], why: x.why, lesson: x.lesson });
      return out;
    }), note: a.reveal_answers ? undefined : "Answers hidden. Ask the learner, then call again with reveal_answers: true to grade." };
  },

  async mock_interview(a, env) {
    const mocks = await load(env, "api/v1/mocks.json");
    const m = pickRole(mocks, a.role);
    if (!m) throw new Error(`unknown role. Roles: ${mocks.map((x) => x.id).join(", ")}`);
    if (!a.round) return { role: m.name, about: m.blurb, url: m.url,
      rounds: m.rounds.map((r) => ({ id: r.id, name: r.name, minutes: r.minutes, questions: r.questions.length, intro: r.intro })) };
    const rr = norm(a.round);
    const r = m.rounds.find((x) => x.id === a.round) || m.rounds.find((x) => norm(x.name).includes(rr) || rr.includes(norm(x.name))) ||
      (/^\d+$/.test(rr) ? m.rounds[+rr - 1] : null);
    if (!r) throw new Error(`no round '${a.round}'. Rounds: ${m.rounds.map((x) => x.id).join(", ")}`);
    return { role: m.name, round: r.name, minutes: r.minutes, intro: r.intro, url: r.url,
      questions: r.questions.map((q, i) => a.include_answers
        ? { n: i + 1, question: q.q, model_answer: q.answer.join("\n\n"), listen_for: q.listen_for, lessons: q.lessons }
        : { n: i + 1, question: q.q }),
      note: a.include_answers ? undefined : "Ask one question at a time. Call again with include_answers: true to give feedback." };
  },

  async jobs(a, env) {
    const data = await load(env, "jobs/jobs.json");
    const terms = words(a.query);
    const co = norm(a.company);
    const rawLoc = norm(a.location).trim();
    const loc = CITY_ALIASES[rawLoc] || rawLoc;
    const er = a.experience ? expRange(a.experience) : null;
    let jobs = data.jobs.filter((j) => {
      const t = norm(j.title + " " + ((j.jd && j.jd.skills) || []).join(" "));
      if (terms.length && !terms.every((w) => t.includes(w) || (w === "ml" && t.includes("machine learning")) || (w === "ai" && /\bai\b|artificial/.test(t)))) return false;
      if (co && !norm(j.company).includes(co)) return false;
      if (loc && ![].concat(loc).some((c) => norm(j.location).includes(c))) return false;
      return true;
    });
    let unstated = [];
    if (er) {
      // same rule as the jobs page: a job matches every band its stated range touches;
      // for a plain number of years, the job's range must include it ("3+" counts as 3–5)
      const fits = (j) => {
        if (!j.exp) return false;
        const lo = j.exp[0];
        if (er[0] === er[1]) return lo <= er[0] && (j.exp[1] ?? lo + 2) >= er[0];
        const hi = j.exp[1] ?? lo;
        return lo < er[1] && hi >= er[0];
      };
      unstated = jobs.filter((j) => !j.exp);
      jobs = jobs.filter(fits);
    }
    const limit = Math.min(a.limit || 20, 100);
    const show = (j) => ({ title: j.title, company: j.company, location: j.location, posted: j.posted,
      experience: j.exp ? (j.exp[1] == null ? `${j.exp[0]}+ yrs` : `${j.exp[0]}–${j.exp[1]} yrs`) : "not stated",
      skills: (j.jd && j.jd.skills) || undefined, they_ask_for: (j.jd && j.jd.needs) || undefined, apply: j.url });
    return { updated: data.updated, window_days: data.days, matches: jobs.length, jobs: jobs.slice(0, limit).map(show),
      experience_not_stated: er ? unstated.slice(0, 10).map(show) : undefined,
      cities_available: rawLoc && !jobs.length
        ? [...new Set(data.jobs.flatMap((j) => j.location.split(/,\s*/)).filter((c) => !/locations? in|^india/i.test(c)))].sort()
        : undefined,
      note: "Links go to each company's own careers page. Listings are collected automatically and not vetted; check details before applying.",
      page: "https://aimlrounds.com/jobs/" };
  },

  async whats_new(a, env) {
    const items = await load(env, "api/v1/new.json");
    return { items: items.slice(0, Math.min(a.limit || 15, 60)).map((x) => ({ date: x.date, title: x.title, kind: x.kind, section: x.section, url: x.url })) };
  },
};

// ---------- prompts ----------
const PROMPTS = [
  { name: "mock_interview", title: "Run a mock interview", description: "A mock interview for a role, one question at a time, with feedback against the model answer.",
    arguments: [{ name: "role", description: "AI Engineering, ML Engineering or Data Science", required: true }, { name: "round", description: "Optional round name" }] },
  { name: "study_topic", title: "Study a topic", description: "Learn one topic from the AIML Rounds lessons, then check understanding with its quiz.",
    arguments: [{ name: "topic", description: "e.g. 'KV cache', 'RAG evaluation', 'bias-variance'", required: true }] },
  { name: "study_plan", title: "Make a study plan", description: "A week-by-week plan from the role roadmap, with lessons, quizzes and mocks.",
    arguments: [{ name: "role", description: "AI Engineering, ML Engineering or Data Science", required: true }, { name: "weeks", description: "How many weeks (default 6)" }] },
  { name: "job_prep", title: "Prepare for a job", description: "Find matching AI/ML jobs, then map what they need to lessons to revise.",
    arguments: [{ name: "role", description: "Job title you want, e.g. 'ML engineer'", required: true }, { name: "experience", description: "Years of experience" }] },
];

function promptText(name, a) {
  switch (name) {
    case "mock_interview":
      return `Run a mock interview for the ${a.role} role using the AIML Rounds mock_interview tool${a.round ? `, round "${a.round}"` : " (list the rounds and let me pick)"}. Ask one question at a time and wait for my answer. After each answer, fetch the model answer (include_answers: true), tell me what I covered and missed from "what the interviewer listens for", give a 1–5 score, and link the lesson to revise. At the end, summarise my weak areas.`;
    case "study_topic":
      return `Teach me "${a.topic}" from AIML Rounds. Search for the best lesson, read it with get_lesson, and teach it in the lesson's order: the interview situation, the intuition, how it works, in practice. Keep it conversational and check my understanding with a question after each part. Finish with the "Say it" interview answer and 3 questions from the matching topic quiz (ask first, reveal after). Link the lesson page.`;
    case "study_plan":
      return `Make me a ${a.weeks || 6}-week study plan for the ${a.role} role from the AIML Rounds roadmap tool. Follow the roadmap order, put core topics first, spread lessons by their minutes, add the topic quiz at the end of each topic and the mock interview rounds in the last week. Give each lesson's link.`;
    case "job_prep":
      return `Find recent "${a.role}" jobs in India with the AIML Rounds jobs tool${a.experience ? ` for about ${a.experience} years of experience` : ""}. Show the best 10 with apply links. Then, from those titles, list the skills they most likely test, map each to AIML Rounds lessons with search, and suggest the matching mock interview round.`;
  }
  return null;
}

// ---------- JSON-RPC ----------
const ok = (id, result) => ({ jsonrpc: "2.0", id, result });
const err = (id, code, message) => ({ jsonrpc: "2.0", id, error: { code, message } });

async function rpc(msg, env) {
  const { id, method, params = {} } = msg || {};
  if (!msg || msg.jsonrpc !== "2.0" || typeof method !== "string") return err(id ?? null, -32600, "Invalid Request");
  if (id === undefined) return null; // notification
  switch (method) {
    case "initialize": {
      const v = VERSIONS.includes(params.protocolVersion) ? params.protocolVersion : VERSIONS[0];
      return ok(id, { protocolVersion: v, capabilities: { tools: { listChanged: false }, prompts: { listChanged: false } },
        serverInfo: SERVER, instructions: INSTRUCTIONS });
    }
    case "ping": return ok(id, {});
    case "tools/list": return ok(id, { tools: TOOLS });
    case "prompts/list": return ok(id, { prompts: PROMPTS });
    case "prompts/get": {
      const p = PROMPTS.find((x) => x.name === params.name);
      if (!p) return err(id, -32602, `Unknown prompt: ${params.name}`);
      const args = params.arguments || {};
      for (const ar of p.arguments) if (ar.required && !args[ar.name]) return err(id, -32602, `Missing argument: ${ar.name}`);
      return ok(id, { description: p.description, messages: [{ role: "user", content: { type: "text", text: promptText(p.name, args) } }] });
    }
    case "resources/list": return ok(id, { resources: [] });
    case "tools/call": {
      const h = HANDLERS[params.name];
      if (!h) return err(id, -32602, `Unknown tool: ${params.name}`);
      try {
        const out = await h(params.arguments || {}, env);
        const text = typeof out === "string" ? out : JSON.stringify(out, null, 1);
        return ok(id, { content: [{ type: "text", text }], ...(typeof out === "string" ? {} : { structuredContent: out }) });
      } catch (e) {
        return ok(id, { content: [{ type: "text", text: `Error: ${e.message}` }], isError: true });
      }
    }
    default: return err(id, -32601, `Method not found: ${method}`);
  }
}

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST, GET, OPTIONS, DELETE",
  "Access-Control-Allow-Headers": "Content-Type, Accept, Mcp-Session-Id, Mcp-Protocol-Version, Authorization",
  "Access-Control-Expose-Headers": "Mcp-Session-Id",
};

const LANDING = `AIML Rounds MCP server

Free AI/ML interview prep inside Claude and other AI tools: search lessons, read them,
follow a role roadmap, take quizzes and mock interviews, and find AI/ML jobs in India.

Add it to Claude Code:
  claude mcp add --transport http aimlrounds https://mcp.aimlrounds.com/mcp

Claude Desktop / claude.ai: Settings → Connectors → Add custom connector → https://mcp.aimlrounds.com/mcp

Site: https://aimlrounds.com
`;

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: CORS });
    if (url.pathname === "/" && request.method === "GET")
      return new Response(LANDING, { headers: { "content-type": "text/plain; charset=utf-8", ...CORS } });
    if (url.pathname !== "/mcp") return new Response("Not found", { status: 404, headers: CORS });
    if (request.method === "GET" || request.method === "DELETE")
      return new Response("Method Not Allowed", { status: 405, headers: { Allow: "POST", ...CORS } }); // stateless: no SSE stream
    if (request.method !== "POST") return new Response("Method Not Allowed", { status: 405, headers: CORS });

    let body;
    try { body = await request.json(); } catch {
      return Response.json(err(null, -32700, "Parse error"), { status: 400, headers: CORS });
    }
    const batch = Array.isArray(body);
    const replies = (await Promise.all((batch ? body : [body]).map((m) => rpc(m, env)))).filter(Boolean);
    if (!replies.length) return new Response(null, { status: 202, headers: CORS });
    return Response.json(batch ? replies : replies[0], { headers: CORS });
  },
};
