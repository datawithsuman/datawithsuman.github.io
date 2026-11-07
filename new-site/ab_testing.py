# The A/B Testing part of the Fundamentals track. Lesson text comes from the source pages (see ml_import.py).
GROUPS = [
    ("ab-design", "Designing a test", "Random assignment, choosing metrics, and working out how long to run."),
    ("ab-reading", "Reading the result", "Making decisions, ratio metrics, CUPED, heavy tails, peeking and multiple testing."),
    ("ab-trust", "Can you trust it?", "Sample ratio mismatch, novelty effects and interference."),
    ("ab-beyond", "Beyond the fixed test", "Bandits, many tests at once, uplift modelling and practice."),
]

LESSONS = {
    "randomisation-and-assignment": {"prereqs": ["hypothesis-testing-and-ab-tests"], "related": ["correlation-vs-causation"]},
    "choosing-ab-metrics": {"prereqs": ["randomisation-and-assignment"], "related": ["choosing-the-right-metric"]},
    "sample-size-and-power": {"prereqs": ["hypothesis-testing-and-ab-tests", "choosing-ab-metrics"]},
    "reading-ab-results": {"prereqs": ["sample-size-and-power", "confidence-intervals-and-bootstrap"]},
    "ratio-metrics-and-delta-method": {"prereqs": ["reading-ab-results"]},
    "variance-reduction-cuped": {"prereqs": ["sample-size-and-power"]},
    "revenue-and-heavy-tailed-metrics": {"prereqs": ["sample-size-and-power"]},
    "sequential-testing": {"prereqs": ["reading-ab-results"]},
    "multiple-testing": {"prereqs": ["reading-ab-results"]},
    "sample-ratio-mismatch": {"prereqs": ["reading-ab-results"]},
    "novelty-and-long-term-effects": {"prereqs": ["reading-ab-results"]},
    "interference-in-experiments": {"prereqs": ["randomisation-and-assignment"]},
    "bandits-vs-ab-tests": {"prereqs": ["reading-ab-results"]},
    "running-many-tests-at-once": {"prereqs": ["randomisation-and-assignment", "multiple-testing"]},
    "heterogeneous-effects-and-uplift": {"prereqs": ["multiple-testing", "reading-ab-results"]},
    "ab-testing-practice": {"type": "interview", "prereqs": ["running-many-tests-at-once", "heterogeneous-effects-and-uplift"]},
}
for _l in LESSONS.values():
    _l["prereqs"] = [f"fundamentals/{k}" for k in _l.get("prereqs", [])]
    if "related" in _l:
        _l["related"] = [f"fundamentals/{k}" for k in _l["related"]]
