# System design lessons in the seven-section format. Questions stay generic, and the real system is named only in the sources.
from maths_plans import _plan

_HINT = "This one's a walkthrough, so aim for about 2 minutes. It feels different from reading it, and that's the point."
_TABS = ["Intuition", "Architecture", "In practice"]


def _flow(label, boxes, note, strip):
    """Four boxes in a row, the last one highlighted, with one note below and a dashed strip at the bottom."""
    xs = [2, 124, 246, 368]
    rects, heads, subs = "", "", ""
    for i, (x, (head, sub)) in enumerate(zip(xs, boxes)):
        w = 110 if i == 3 else 104
        fill = 'fill="var(--c)"' if i == 3 else 'fill="var(--tint)" stroke="var(--c)" stroke-width="2"'
        colour = ' fill="#fff"' if i == 3 else ""
        rects += f'<rect x="{x}" y="6" width="{w}" height="58" rx="8" {fill}/>'
        heads += f'<text x="{x + w / 2:g}" y="31"{colour}>{head}</text>'
        subs += f'<text x="{x + w / 2:g}" y="50"{colour}>{sub}</text>'
    return f"""<svg viewBox="0 0 480 136" role="img" aria-label="{label}">
  {rects}
  <path d="M106 35h18M228 35h18M350 35h18" stroke="var(--dim)" stroke-width="2"/>
  <g font-size="14" font-weight="700" fill="var(--ink)" text-anchor="middle">{heads}</g>
  <g font-size="12" fill="var(--dim)" text-anchor="middle">{subs}</g>
  <text x="240" y="86" font-size="13" font-weight="600" fill="var(--ok)" text-anchor="middle">{note}</text>
  <rect x="2" y="98" width="476" height="32" rx="8" fill="none" stroke="var(--a)" stroke-width="2" stroke-dasharray="6 5"/>
  <text x="240" y="119" font-size="13" font-weight="600" fill="var(--ink)" text-anchor="middle">{strip}</text>
</svg>"""


STORE_PICTURE = _flow("The merchant asks. The LLM picks a tool. Code checks and runs it. The result returns with its instructions. Store changes become a draft the merchant confirms. Before release, real conversations and simulated merchants test each version.",
                      [("Ask", "Merchant request"), ("Pick a tool", "LLM decides"), ("Check, run", "Code, scoped"), ("Result", "With instructions")],
                      "Loop until done. Store changes become a draft the merchant confirms.",
                      "Before release: real conversations and simulated merchants")
RESEARCH_PICTURE = _flow("A lead agent plans. Subagents search in parallel. The lead combines their reports. A final step adds citations. The plan and progress are saved outside the agents, so a failed run can resume.",
                         [("Plan", "Lead agent"), ("Search", "Many subagents"), ("Combine", "Lead, maybe loop"), ("Cite", "One clear report")],
                         "The lead can start more subagents until the answer is good enough.",
                         "Saved outside the agents: plan, progress, reports")
SQL_PICTURE = _flow("Retrieve candidate tables. The user confirms them. The LLM generates SQL. Code validates it before it runs read-only. An offline job summarises tables and past queries into the index.",
                    [("Retrieve", "Candidate tables"), ("Confirm", "User checks"), ("Generate", "Writes the SQL"), ("Validate, run", "Read-only")],
                    "Show the SQL, tables and warnings, because valid SQL can still be wrong.",
                    "Offline: summarise tables and past queries into an index")
CODE_PICTURE = _flow("The IDE waits for a pause and sends a short prompt to the nearest proxy over an open connection. The proxy checks a token and forwards to a model in the same region. Cancels travel back down the same path.",
                     [("IDE", "Waits for a pause"), ("Network", "Open connection"), ("Proxy", "Same region"), ("Model", "Fast, streams")],
                     "If the user keeps typing, the cancel travels all the way to the model.",
                     "The proxy leaves DNS when its own success rate drops")
PLATFORM_PICTURE = _flow("Teams call one API. The gateway checks access and limits, redacts personal data, then routes to a vendor or in-house model. Every request is logged for cost and audit.",
                         [("Teams", "One API format"), ("Check", "Access, budget"), ("Redact", "Personal data"), ("Route", "Vendor, in-house")],
                         "The reply comes back the same way, with the real values restored.",
                         "Every request logged: team, model, tokens, cost")

DESIGN_PLANS = {
    "system-design/design-store-assistant": _plan(
        "An e-commerce platform wants an assistant for its merchants. It should do things in the store, like finding customers, writing product descriptions and creating discounts. It starts with a handful of tools, and teams keep adding more. Say 100,000 conversations a day. The interviewer asks:",
        "Merchants want an assistant that can act in their store, not just answer questions. Design it, knowing tools will grow from a handful to dozens.",
        "Think of a new assistant in a shop. They look things up freely and fill in forms, but the owner signs anything that changes the shop. As the shop grows, a giant rulebook read every morning stops working, so each rule is printed on the form it applies to.",
        STORE_PICTURE, "The model decides what to do next, and code decides what's allowed to happen.",
        ("c3", "<b>Try to break it.</b> Drag the tools up to 80, and watch the prompt grow. Then turn on each fix, one at a time.", "<b>Now say why:</b> why do instructions returned with a tool's result keep the prompt cache working?"),
        ["c2", "c4"], ["c5", "c6", "c7"], [], [],
        ["You clarified the jobs, the volume and what the assistant may do alone.",
         "You used one agent in a loop, and said why not several.",
         "Tools are narrow and scoped to the signed-in store in code.",
         "Store changes are drafts the merchant confirms, with idempotent writes.",
         "You named the tool growth problem, and returned instructions with tool results.",
         "You evaluated with real conversations labelled by several experts.",
         "You tuned judges against human agreement, and watched for gaming.",
         "You capped steps and cost, and rolled out read-only first."],
        tabs=_TABS,
        trap_title="\"More tools make it more capable\"",
        trap_html="<p>It sounds right, since each tool adds a skill. But past a point, tools overlap, the model picks the wrong one and the prompt fills up with rules that conflict. Capability goes up on paper while the system gets harder to debug. Keep tools distinct, load only what fits the request, and test whether a new tool helps before you keep it.</p>"),
    "system-design/design-research-agent": _plan(
        "An AI assistant gets broad questions, like comparing every company in a sector, that need dozens of searches across many sources. A single agent is slow, and its context fills up. A long run sometimes fails near the end. The interviewer asks:",
        "Users ask open-ended questions that need many sources. Design an agent that splits the work across parallel subagents and writes one answer.",
        "Think of an editor with a team of researchers. The editor writes the plan and gives each researcher one clear topic. They go off separately and bring back short notes, not everything they read. The editor combines the notes, sends people back if something's missing, and a fact-checker adds the references.",
        RESEARCH_PICTURE, "Each subagent reads a lot and returns a little, which is what keeps the lead's context clear.",
        ("c3", "<b>Try to break it.</b> Set the question to 1 part, and add subagents. Then go to 20 parts. Then tick the stuck subagent.", "<b>Now say why:</b> why does one stuck subagent delay the whole run?"),
        ["c2", "c4"], ["c5", "c6", "c7"], [], [],
        ["You clarified sources, citations, volume and the budget per run.",
         "You said why research suits several agents, and when it doesn't.",
         "A lead plans and saves the plan outside its context.",
         "Subagents run in parallel with clear tasks, formats, tools and limits.",
         "A final step attaches citations.",
         "Effort matches the question, with hard limits on runs.",
         "Runs are durable jobs with checkpoints, so failures resume.",
         "You started evaluation small, with a rubric and human testers."],
        tabs=_TABS,
        trap_title="\"More agents give a better answer\"",
        trap_html="<p>It sounds right, since many hands make light work. But agents only help when the work really splits. On a simple question you pay many times more for the same answer. If tasks depend on each other, or the instructions are vague, agents repeat each other's work. Multi-agent systems use far more tokens than a chat, so use them only when the question is worth it.</p>"),
    "system-design/design-text-to-sql": _plan(
        "A company's analysts ask hundreds of data questions a day. Its warehouse has about 100,000 tables, many of them look-alikes, and few people know which to trust. Writing the SQL takes time, and finding the right table takes longer. The interviewer asks:",
        "Analysts spend too long finding tables and writing SQL. Design a system that turns their questions into queries across a huge data warehouse.",
        "Think of a new analyst in a huge company. Knowing SQL isn't their problem. They ask around: which table do people use for this, and which ones are out of date? They look at old queries from colleagues, draft their own, and a test run catches mistakes before it counts.",
        SQL_PICTURE, "Finding the table is the hard part. The SQL comes after.",
        ("c3", "<b>Try to break it.</b> Drag the tables up to 20 with no documentation. Then tick the box, and bring the tables back down.", "<b>Now say why:</b> why does sending more tables stop helping, and start to hurt?"),
        ["c2", "c4"], ["c5", "c6"], [], [],
        ["You clarified the users, whether it runs SQL and the access rules.",
         "You said finding the table is the hard part.",
         "Offline, you summarised tables and past queries into an index.",
         "You ranked by similarity and trust, then let the user confirm.",
         "The prompt has schemas, past queries and real filter values.",
         "You validated before running: names, EXPLAIN and limited retries.",
         "It runs read-only with the user's permissions and a cost limit.",
         "You evaluated retrieval and SQL separately, on your own queries."],
        tabs=_TABS,
        trap_title="\"The SQL runs, so the answer is right\"",
        trap_html="<p>It sounds right, since validation passed and numbers came back. But EXPLAIN only proves the query is valid. It can still use a look-alike table, the wrong definition of a metric or a join that duplicates rows, and return a confident wrong number. So show the SQL, tables and definitions used, and warn about risky joins.</p>"),
    "system-design/design-code-autocomplete": _plan(
        "A code editor plugin suggests the next lines as developers type, for users all over the world. A suggestion that arrives late is useless. It must serve hundreds of millions of requests a day, with a mean under 200 ms. The interviewer asks:",
        "Design code autocomplete for hundreds of millions of requests a day, with suggestions arriving in under 200 ms.",
        "Think of a friend finishing your sentences, on a phone call. If they're slow, you've already moved on, and what they say is wasted. Hanging up and redialling each time you talk over them would be absurd, so you stay on the line and just say \"never mind\".",
        CODE_PICTURE, "Staying on the line is HTTP/2. \"Never mind\" is a cancel that reaches the model.",
        ("c3", "<b>Try to break it.</b> Start with both boxes off, and see how far you are from 200 ms. Make the round trip shorter. Then try each box.", "<b>Now say why:</b> why can't a faster model alone meet the target?"),
        ["c2", "c4"], ["c5", "c6"], [], [],
        ["You confirmed the scale, the target and where users are.",
         "You said the network matters as much as the model.",
         "You explained how the client decides when to ask, and builds a short prompt.",
         "You made cancelling central, and said it must reach the model.",
         "You used HTTP/2 streams, and open connections on both sides.",
         "A proxy runs in each region with the model, routed by DNS.",
         "Short-lived tokens are checked locally, and the model key stays hidden.",
         "Unhealthy proxies remove themselves, and you measure acceptance and percentiles."],
        tabs=_TABS,
        trap_title="\"Just get a faster model and more GPUs\"",
        trap_html="<p>It sounds right, since the model is the expensive part. But reconnecting takes five or six round trips, so distance alone can use up 200 ms. And if requests aren't cancelled, about half of those extra GPUs do work no one will see. Fix the wasted work and the network path first, then see how much model speed you still need.</p>"),
    "system-design/design-llm-platform": _plan(
        "A large company has dozens of teams building with LLMs. Each has its own vendor keys and its own way of connecting, and nobody can see the total cost or say what data is leaving the company. Say 100 million requests a month. The interviewer asks:",
        "Dozens of teams want to use LLMs from different vendors, and customer data mustn't leak. Design a shared platform for them.",
        "Think of a company's post room. Every team hands letters to one desk, in one format. The desk checks the sender, blacks out private details on anything leaving the building, sends it by the right courier and keeps a record of the cost. If the desk closes, though, nothing gets sent, so it needs cover.",
        PLATFORM_PICTURE, "Every team gets the same checks, without building them again.",
        ("c3", "<b>Try to break it.</b> Turn redaction off, and read what the vendor sees. Turn it back on, and swap the names. Then drag the message length up.", "<b>Now say why:</b> why might an answer get worse once the names are hidden?"),
        ["c2", "c4"], ["c5", "c6"], [], [],
        ["You clarified the teams, models, data rules and volume.",
         "You put a gateway between all teams and all models, with one API.",
         "It handles sign-in, approved use cases, rate limits and budgets.",
         "It redacts personal data for outside vendors, and restores it.",
         "You named the cost of redaction in latency and quality.",
         "Every request is logged by team, model, tokens and cost.",
         "You removed the single point of failure, and shared quotas by priority.",
         "Fallbacks respect data rules, and quality stays with each team."],
        tabs=_TABS,
        trap_title="\"Add a fallback, and send everything to the next vendor\"",
        trap_html="<p>It sounds right, since it keeps products running when a vendor is down. But each vendor has its own data approvals, and a different model can behave differently. A silent global switch could send customer data somewhere it isn't allowed, or change a product's behaviour untested. Make fallback a per-team choice, limited to approved models.</p>"),
}
for _key in DESIGN_PLANS:
    DESIGN_PLANS[_key]["say_hint"] = _HINT
