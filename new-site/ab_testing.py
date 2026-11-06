# The A/B Testing part of the Fundamentals track. Lesson text comes from the source pages (see ml_import.py).
GROUPS = [
    ("ab-design", "Designing a test", "Random assignment, choosing metrics, and working out how long to run."),
    ("ab-reading", "Reading the result", "Making decisions, ratio metrics, CUPED, peeking and multiple testing."),
    ("ab-trust", "Can you trust it?", "Sample ratio mismatch, novelty effects and interference."),
    ("ab-beyond", "Beyond the fixed test", "Bandits, and when to use them."),
]

LESSONS = {
    "randomisation-and-assignment": {"prereqs": ["hypothesis-testing-and-ab-tests"], "related": ["correlation-vs-causation"]},
    "choosing-ab-metrics": {"prereqs": ["randomisation-and-assignment"], "related": ["choosing-the-right-metric"]},
    "sample-size-and-power": {"prereqs": ["hypothesis-testing-and-ab-tests", "choosing-ab-metrics"]},
    "reading-ab-results": {"prereqs": ["sample-size-and-power", "confidence-intervals-and-bootstrap"]},
    "ratio-metrics-and-delta-method": {"prereqs": ["reading-ab-results"]},
    "variance-reduction-cuped": {"prereqs": ["sample-size-and-power"]},
    "sequential-testing": {"prereqs": ["reading-ab-results"]},
    "multiple-testing": {"prereqs": ["reading-ab-results"]},
    "sample-ratio-mismatch": {"prereqs": ["reading-ab-results"]},
    "novelty-and-long-term-effects": {"prereqs": ["reading-ab-results"]},
    "interference-in-experiments": {"prereqs": ["randomisation-and-assignment"]},
    "bandits-vs-ab-tests": {"prereqs": ["reading-ab-results"]},
}
for _l in LESSONS.values():
    _l["prereqs"] = [f"fundamentals/{k}" for k in _l.get("prereqs", [])]
    if "related" in _l:
        _l["related"] = [f"fundamentals/{k}" for k in _l["related"]]
