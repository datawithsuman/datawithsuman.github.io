# Lessons in the seven-section format, shown as tabs. Intuition: situation, idea, play. Then how it works,
# then in practice and the answer that sounds right, then say it. Moved lessons name their source chapters here, and the
# build fails if a chapter has no section, so nothing can go missing.

LOGISTIC_PICTURE = """<svg viewBox="0 0 480 170" role="img" aria-label="Evidence adds up to a score, a curve squashes the score, and out comes a chance between 0 and 100 percent">
  <g font-size="15" fill="var(--ink)">
    <rect x="4" y="30" width="128" height="30" rx="7" fill="none" stroke="var(--ok)" stroke-width="2"/><text x="68" y="50" text-anchor="middle">+2 more study</text>
    <rect x="4" y="68" width="128" height="30" rx="7" fill="none" stroke="var(--ok)" stroke-width="2"/><text x="68" y="88" text-anchor="middle">+1 good sleep</text>
    <rect x="4" y="106" width="128" height="30" rx="7" fill="none" stroke="var(--bad)" stroke-width="2"/><text x="68" y="126" text-anchor="middle">−1 missed class</text>
    <text x="68" y="18" text-anchor="middle" font-weight="600">Evidence</text>
    <text x="240" y="18" text-anchor="middle" font-weight="600">Squash it</text>
    <text x="410" y="18" text-anchor="middle" font-weight="600">Chance</text>
  </g>
  <path d="M140 83h26m-8-7 8 7-8 7" fill="none" stroke="var(--dim)" stroke-width="2"/>
  <path d="M180 136V30M180 136H300" fill="none" stroke="var(--dim)" stroke-width="1.5"/>
  <path d="M182 130C225 130 225 36 298 36" fill="none" stroke="var(--b)" stroke-width="3"/>
  <path d="M314 83h26m-8-7 8 7-8 7" fill="none" stroke="var(--dim)" stroke-width="2"/>
  <text x="410" y="96" text-anchor="middle" font-size="36" font-weight="700" fill="var(--ink)">82%</text>
</svg>"""

VECTOR_PICTURE = """<svg viewBox="0 0 480 190" role="img" aria-label="Three arrows from one point. The customer and the small restaurant point almost the same way. The popular restaurant is much longer but points elsewhere.">
  <defs><marker id="arrowV" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 10 5 0 10z" fill="context-stroke"/></marker></defs>
  <path d="M30 170H470M30 170V10" stroke="var(--line)" stroke-width="1.5" fill="none"/>
  <line x1="30" y1="170" x2="110" y2="90" stroke="var(--a)" stroke-width="3" marker-end="url(#arrowV)"/>
  <line x1="30" y1="170" x2="110" y2="74" stroke="var(--st)" stroke-width="3" marker-end="url(#arrowV)"/>
  <line x1="30" y1="170" x2="350" y2="130" stroke="var(--b)" stroke-width="3" marker-end="url(#arrowV)"/>
  <g font-size="15" font-weight="600">
    <text x="124" y="100" fill="var(--a)">You</text>
    <text x="118" y="66" fill="var(--st)">Small restaurant: same taste</text>
    <text x="360" y="128" fill="var(--b)">Popular</text>
    <text x="360" y="146" fill="var(--b)">restaurant</text>
  </g>
</svg>"""

FUNNEL_PICTURE = """<svg viewBox="0 0 480 170" role="img" aria-label="A funnel: all items narrow to a few hundred candidates, then to the few items shown to the user">
  <g font-size="15" text-anchor="middle" fill="var(--ink)">
    <rect x="10" y="6" width="460" height="42" rx="8" fill="var(--tint)"/><text x="240" y="32" font-weight="600">Every item in the catalogue</text>
    <text x="240" y="66" fill="var(--muted)" font-size="14">cheap step</text>
    <rect x="110" y="74" width="260" height="38" rx="8" fill="var(--tint)"/><text x="240" y="98" font-weight="600">A few hundred candidates</text>
    <text x="240" y="130" fill="var(--muted)" font-size="14">smart, slow step</text>
    <rect x="175" y="136" width="130" height="30" rx="8" fill="var(--c)"/><text x="240" y="156" fill="#fff" font-weight="600">A few shown</text>
  </g>
</svg>"""

PLANS = {
    "fundamentals/logistic-regression": {
        "tabs": ["Intuition", "Maths", "In practice"],
        "situation": "You have 20 students, their hours studied, and whether each one passed. You need a yes or no, and how sure you are. The interviewer asks:",
        "q": "What is logistic regression, and why is it called regression?",
        "analogy": "Think of a judge weighing evidence. Each fact adds or takes away points, and the total can be any number. A curve then squashes that total into a chance between 0 and 100%.",
        "picture": LOGISTIC_PICTURE,
        "caption": "Illustrative. In the model, the points are the weights and the curve is the sigmoid.",
        "situation_chapters": ["c1"],
        "play": {"chapter": "c6",
                 "try": "<b>Try to break it.</b> Here w is how much each hour counts, and b is where the judge starts. Lower log-loss means a better fit. Drag w as high as it goes.",
                 "why": "<b>Now say why:</b> why does the steepest curve get punished, even though it looks so confident?"},
        "how": ["c2", "c5", "c7", "c8", "c9", "c10", "c13"],
        "practice": ["c4", "c12", "c14", "c17"],
        "trap": ["c3", "c11", "c15"],
        "reference": ["c16", "src"],
        "edits": [
            (", as chapter 3 shows", ""),
            ("which makes the gradient in chapter 8 so simple", "which keeps the gradient simple"),
            (" (chapter 8), and it never", ", and it never"),
            ("(chapter 13)", "(see the family tree below)"),
            ("when one exists (chapter 11)", "when one exists (perfectly separable data has none)"),
            ('in chapter 8 <span', 'above <span'),
        ],
        "checklist": [
            "It is a linear classifier that outputs a probability.",
            "It models the log-odds as a weighted sum, and the sigmoid turns that into a probability.",
            "It is trained by maximum likelihood, which means minimising log-loss. That loss is convex.",
            "A weight multiplies the odds. It is not a direct change in probability.",
            "In practice it is regularised, which also handles separable data.",
            "It is called regression because it regresses the log-odds.",
        ],
    },
    "fundamentals/vectors-and-cosine-similarity": {
        "tabs": ["Intuition", "Maths", "In practice"],
        "situation": "Your food app recommends the same popular restaurant to almost everyone, even people whose taste points elsewhere. The interviewer asks:",
        "q": "What is the difference between a dot product and cosine similarity, and which would you use here?",
        "analogy": "Think of two arrows. Cosine only asks whether they point the same way. The dot product also rewards length, so a very long arrow can win even when it points the wrong way.",
        "picture": VECTOR_PICTURE,
        "caption": "You (1, 1). Popular (4, 0.5). Small (1, 1.2). Dot product picks popular, 4.5 against 2.2. Cosine picks small, 0.996 against 0.79.",
        "situation_chapters": ["c1"],
        "play": {"chapter": "c6",
                 "try": "<b>Try to break it.</b> Make the restaurant much longer without changing its angle. Then rotate it until it sits at 90° from the customer.",
                 "why": "<b>Now say why:</b> which measure ignored the extra length, and why did two of them hit zero at 90°?"},
        "how": ["c2", "c5", "c4"],
        "practice": ["c7", "c8", "cNext"],
        "trap": ["c3", "c9"],
        "reference": ["c10", "src"],
        "edits": [
            ("they answer different questions (chapter 6)", "they answer different questions (see In practice)"),
        ],
        "checklist": [
            "A dot product multiplies matching entries and adds them, which equals the two lengths times the cosine of the angle.",
            "So a dot product measures direction and size together.",
            "Cosine divides by both lengths, so it compares direction only, from −1 to 1.",
            "Vectors of length one get the same ranking from dot product, cosine and Euclidean distance.",
            "Use cosine when length is an artefact, like text. Use dot product when length carries signal, like popularity.",
        ],
    },
    "system-design/recommendation-system": {
        "tabs": ["Intuition", "Architecture", "Numbers"],
        "situation": "You are designing the home feed for a video app with millions of videos. Each user sees only a few. The interviewer asks:",
        "q": "How would you pick a few videos for each user? Walk me through the design.",
        "analogy": "Think of hiring. A quick CV screen cuts thousands of applicants to a shortlist, and only the shortlist gets a slow, careful interview. You cannot score every item for every user, so you narrow in stages. Each stage trades accuracy for speed.",
        "picture": FUNNEL_PICTURE,
        "caption": "Illustrative stages. Real counts depend on your latency budget.",
        "body": "recsys",
        "trap_title": "\"Just rank every item with your best model\"",
        "trap_html": "<p>It sounds right, because the best model gives the best scores. But cost grows with the catalogue size times the model cost per item. A cheap first stage cuts the catalogue to a few hundred, so the expensive model only runs where it can change the answer.</p>",
        "checklist": [
            "You cannot score everything, so you narrow in stages.",
            "A fast candidate step aims for high recall.",
            "A slower ranking model aims for high precision.",
            "A final step applies business rules and diversity.",
            "A feature store and an event log sit underneath all the stages.",
            "You named at least one trade-off.",
        ],
        "followups": [
            ("How many candidates should you keep?",
             "Enough that good items survive the first stage, and few enough to meet the ranker's latency budget. There is no universal number, so you measure recall at different counts against that budget."),
            ("Why two towers for retrieval and a richer model for ranking?",
             "Two towers encode the user and item separately, so item vectors can be computed ahead of time and searched quickly. The ranker runs on only a few hundred items, so it can afford features that combine the user and the item."),
            ("What happens if your features go stale?",
             "Relevance drops, but fresher features cost more to serve. Keep fast-changing signals fresh and compute slow ones in batches. Logging features at serving time also keeps training consistent with what the model saw."),
        ],
        "answer": "<h3>The 30-second answer</h3><p class=\"say30\">You can't score every item for every user, so I'd narrow in stages. A fast candidate step finds a few hundred items with high recall. A slower ranking model orders those for precision. A final step applies business rules and diversity. Underneath, a feature store serves fresh user and item features, and an event log feeds training. The main trade-offs are candidate count against latency, and feature freshness against serving cost.</p>",
    },
}

HARNESS_PICTURE = """<svg viewBox="0 0 480 186" role="img" aria-label="The model sits in the centre. Seven parts surround it: agent loop, LLM integration, tools, memory and context, safety, orchestration and extensibility.">
  <g font-size="14" text-anchor="middle" fill="var(--ink)">
    <g fill="none" stroke="var(--a)" stroke-width="2">
      <rect x="4" y="6" width="148" height="44" rx="8"/><rect x="166" y="6" width="148" height="44" rx="8"/><rect x="328" y="6" width="148" height="44" rx="8"/>
      <rect x="4" y="71" width="148" height="44" rx="8"/><rect x="328" y="71" width="148" height="44" rx="8"/>
      <rect x="85" y="136" width="148" height="44" rx="8"/><rect x="247" y="136" width="148" height="44" rx="8"/>
    </g>
    <text x="78" y="33">Agent loop</text><text x="240" y="33">LLM integration</text><text x="402" y="33">Tools</text>
    <text x="78" y="98">Memory, context</text><text x="402" y="98">Safety</text>
    <text x="159" y="163">Orchestration</text><text x="321" y="163">Extensibility</text>
    <rect x="166" y="66" width="148" height="54" rx="10" fill="var(--b)"/><text x="240" y="99" fill="#fff" font-weight="700" font-size="17">The model</text>
  </g>
</svg>"""

AIAYN_PICTURE = """<svg viewBox="0 0 480 190" role="img" aria-label="Top row: a recurrent model passes information along a chain, one word at a time. Bottom row: attention connects every word directly to every other word.">
  <g font-size="14" fill="var(--ink)">
    <text x="4" y="16" font-weight="600">One word at a time</text>
    <text x="4" y="94" font-weight="600">Every word sees every word</text>
  </g>
  <g fill="var(--tint)" stroke="var(--c)" stroke-width="1.5">
    <circle cx="40" cy="44" r="13"/><circle cx="130" cy="44" r="13"/><circle cx="220" cy="44" r="13"/><circle cx="310" cy="44" r="13"/><circle cx="400" cy="44" r="13"/>
    <circle cx="40" cy="170" r="13"/><circle cx="130" cy="170" r="13"/><circle cx="220" cy="170" r="13"/><circle cx="310" cy="170" r="13"/><circle cx="400" cy="170" r="13"/>
  </g>
  <path d="M55 44h60M145 44h60M235 44h60M325 44h60" stroke="var(--muted)" stroke-width="2" fill="none"/>
  <path d="M40 157Q85 134 130 157M40 157Q130 120 220 157M40 157Q175 108 310 157M40 157Q220 100 400 157M130 157Q175 134 220 157M220 157Q265 134 310 157M310 157Q355 134 400 157" stroke="var(--c)" stroke-width="1.5" fill="none"/>
</svg>"""

PAPER_PLANS = {
    "papers/harness-engineering": {
        "analogy": "Think of an engine on a workbench. It has all the power, but it goes nowhere until you build a car around it, with steering, brakes and a fuel gauge. The model is the engine. The harness is everything else, and this paper opens up eleven real cars to see how they are built.",
        "picture": HARNESS_PICTURE,
        "caption": "The paper's seven subsystems around the model. Every system in the study takes a position on all seven.",
        "problem": ["example", "c1"],
        "play": {"lab": "stuckLab", "chapter": "c6",
                 "try": "<b>Try it.</b> Your agent keeps running the same test without changing anything. Drag the slider to repeat the call, and see when each real agent steps in.",
                 "why": "<b>Notice:</b> some production agents never step in at all. The paper still calls them production-quality, and that's why it warns against over-engineering stuck detection."},
        "how": ["c2", "c3", "c5", "c6", "c7", "c8", "c9", "c10", "c11", "c12"],
        "found": ["c13", "c15"],
        "limits": ["c16"],
        "verdict": ["c18"],
        "changed_chapters": ["c14"],
        "reference": ["c4", "c17", "src"],
        "hidden": ["iv"],
        "changed_html": """<p>The paper is only a few months old, so it's too early to say what it changed. What it gives you today is a shared map: one vocabulary for parts that every agent has, and evidence from real source code instead of opinion.</p>
<p><b>What to remember.</b> A coding agent is a small loop surrounded by a large amount of engineering whose job is not to make the model smarter but to make it safe, affordable, recoverable and extensible. The field converged fast: the same seven parts, hand-rolled loops, deterministic retrieval, threshold compaction, coordinator–worker sub-agents and skills. And it copies itself: Codex adopted Claude Code's hook vocabulary verbatim; Hermes' code comments credit OpenCode, Codex and OpenClaw <span class="src"><a href="https://arxiv.org/pdf/2609.00006#page=62" target="_blank" rel="noopener">p. 62</a></span>.</p>
<h3>Since the paper</h3>
<p>Gemini CLI's consumer tier was retired in June 2026 in a move toward the closed-source Antigravity CLI, so the paper's v0.50.0 pin captures the last major open-source state of that lineage (p. 8). Controlled harness × model studies have started (see the update card under What they found, in the Results tab).</p>""",
        "edits": [
            ("Every chapter below shows which part", "The Method tab shows which part"),
            ("As chapter 13 shows, no production", "As the Results tab shows, no production"),
            ("Each system reacts differently. Drag the slider to repeat the same call.", "Each system reacts differently, and you can try that in the Play section of the Gist tab."),
            ("<h2>What to remember, and how far to trust it</h2>", "<h2>How far to trust it</h2>"),
            ("Interview-angle reading:", "Further reading:"),
            ("<h2>A minimum viable harness in about 90 lines</h2>", "<h2>What the authors recommend</h2>"),
            ('<details class="deep"><summary>Go deeper: all 18 recommendations in one list</summary>', '<details class="deep" open><summary>All 18 recommendations</summary>'),
            ('Deliberately omitted, because the right answer depends on context:', 'The paper closes with these 18 recommendations and a 90-line scaffold that implements 10 of them (Listing 3, p. 71–72). The scaffold deliberately omits, because the right answer depends on context:'),
        ],
        "strip": [
            r'<p><b>The lesson\.</b>.*?</p>\s*',
            r'<h3>Since the paper</h3>\s*<p>.*?</p>\s*',
            r'<p>The paper closes with a scaffold.*?</ol>\s*</div>\s*',
        ],
        "tldr_replace": [("draw a harness from memory, explain how real agents handle loops, context, tools, safety, sub-agents and extensions, and answer agent-design interview questions with concrete examples", "draw a harness from memory, and explain how real agents handle loops, context, tools, safety, sub-agents and extensions")],
    },
    "papers/context-language-models": {
        "analogy": "A normal agent is like a person who can only add lines to the bottom of a notebook, while an assistant occasionally tears pages out and replaces them with a summary. A Context Language Model is the person holding the eraser and pen. They cross out stale notes, rewrite a messy page, and keep one important quote exactly as written.",
        "picture_chapter": "flow",
        "problem": ["problem", "why"],
        "how": ["approach", "challenges"],
        "found": ["results"],
        "found_first_figure": True,
        "limits": ["critique"],
        "changed_chapters": ["future"],
        "verdict": ["verdict"],
        "reference": ["related", "terms"],
        "hidden": ["interview"],
        "changed_html": """<p>The paper came out in September 2026, so it's too early to say what it changed. Its lasting claim is the shift in who controls memory: the model edits its own context directly, instead of outside code deciding what to keep.</p>
<p><b>What to remember.</b> Letting the model edit its context can beat fixed rules on long tasks while using less compute, but the gain is largest at small context budgets, and editable context is also a new safety risk.</p>""",
        "strip": [r'<div class="analogy">.*?</div>\s*'],
        "edits": [],
    },
    "papers/attention-is-all-you-need": {
        "analogy": "Think of a meeting. In a recurrent model, a message passes from person to person down a line, and it fades on the way. With attention, everyone in the room can hear everyone else directly, and each person decides who to listen to.",
        "picture": AIAYN_PICTURE,
        "caption": "Illustrative. A recurrent model reads a sentence in order. Attention connects every word in one step.",
        "tldr": "This 2017 paper removed recurrence entirely and built a translation model from attention alone.",
        "meta": 'Vaswani et al., Google · <a href="https://arxiv.org/abs/1706.03762">arXiv 1706.03762</a> · 2017',
        "problem_html": "<p>Recurrent models read a sentence one word at a time, which makes them slow to train and weak over long distances. Each step has to wait for the one before it, so training is hard to run in parallel.</p>",
        "method_html": """<ul class="explain">
  <li>An encoder and a decoder, each a stack of 6 identical layers.</li>
  <li>Multi-head attention with 8 heads and a model size of 512.</li>
  <li>A feed-forward layer applied to each position on its own.</li>
  <li>Sine and cosine position signals, since attention alone ignores word order.</li>
</ul>""",
        "found_html": """<ul class="explain">
  <li>On English-to-German translation (WMT 2014), it reached a BLEU score of 28.4, more than 2 points above the best existing results at the time, including ensembles.</li>
  <li>It trained in 12 hours on eight GPUs, far less time than the best earlier models reported.</li>
  <li>It also worked on English parsing, which showed the idea wasn't limited to translation.</li>
</ul>
<p class="note">Figures from the paper's abstract. <a href="https://arxiv.org/abs/1706.03762">Read the abstract</a>.</p>""",
        "limits_html": """<ul class="explain">
  <li>Attention compares every position with every other, so its cost grows with the square of the sequence length.</li>
  <li>Word order has to be added separately, because attention alone ignores it.</li>
  <li>The results cover translation and parsing, so the paper itself doesn't show how far the idea would go.</li>
</ul>""",
        "changed_html": """<p>Training could now run in parallel across a sequence, and distant words were one step apart. This architecture became the base of modern LLMs.</p>
<p><b>What to remember.</b> Attention can replace recurrence entirely, and that's what made today's large models practical to train.</p>""",
        "verdict_html": "<p><b>Read</b> the architecture section and the attention figures. <b>Skim</b> the training details unless you plan to reproduce it.</p>",
    },
}

from maths_plans import MATHS_PLANS  # noqa: E402
from ml_plans import ML_PLANS  # noqa: E402
from dl_plans import DL_PLANS  # noqa: E402
from nlp_plans import NLP_PLANS  # noqa: E402
from llm_plans import LLM_PLANS  # noqa: E402
from ai_plans import AI_PLANS, SD_PLANS  # noqa: E402
from design_plans import DESIGN_PLANS  # noqa: E402
from ab_plans import AB_PLANS  # noqa: E402
from la_plans import LA_PLANS  # noqa: E402
from calc_plans import CALC_PLANS  # noqa: E402
from prob_plans import PROB_PLANS  # noqa: E402
from stat_plans import STAT_PLANS  # noqa: E402
from info_plans import INFO_PLANS  # noqa: E402
from ml2_plans import ML2_PLANS  # noqa: E402
from dl2_plans import DL2_PLANS  # noqa: E402
from nlp2_plans import NLP2_PLANS  # noqa: E402
from llm2_plans import LLM2_PLANS  # noqa: E402

PLANS.update(MATHS_PLANS)
PLANS.update(ML_PLANS)
PLANS.update(DL_PLANS)
PLANS.update(NLP_PLANS)
PLANS.update(LLM_PLANS)
PLANS.update(AI_PLANS)
PLANS.update(SD_PLANS)
PLANS.update(DESIGN_PLANS)
PLANS.update(AB_PLANS)
PLANS.update(LA_PLANS)
PLANS.update(CALC_PLANS)
PLANS.update(PROB_PLANS)
PLANS.update(STAT_PLANS)
PLANS.update(INFO_PLANS)
PLANS.update(ML2_PLANS)
PLANS.update(DL2_PLANS)
PLANS.update(NLP2_PLANS)
PLANS.update(LLM2_PLANS)
