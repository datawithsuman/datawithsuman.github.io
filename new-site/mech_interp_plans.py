"""Plan for the mechanistic interpretability survey paper page (papers/mech-interp-survey).
Source: Content/Reference/Site lesson kit (deep-learning)/mech_interp_split.py. The lessons live in AI Engineering › AI Interpretability."""

MECH_PLANS = {
    "papers/mech-interp-survey": {
        "analogy": "Testing a model only on its answers is like judging a car by test drives alone. It can pass every drive and still hide a fault the drives never trigger. This survey asks how far we've got at opening the bonnet, and whether it makes the car safer.",
        "picture_chapter": "flow",
        "problem": ["wl-c1"], "how": ["wl-c2", "wl-c3", "wl-c4"], "found": ["wl-c5", "z3-c1"], "limits": ["wl-c6"],
        "verdict": ["wl-c7"], "changed_chapters": ["z3-c2"], "reference": [], "hidden": [], "edits": [],
        "changed_html": """<p><b>What to remember.</b> Behavioural tests tell you what a model does on the inputs you tried. Mechanistic interpretability tries to say how, with causal evidence. The survey's answer to its own question is a qualified yes: understanding helps safety when it is faithful, complete enough for the claim and tested causally. The 15 lessons in AI Engineering › AI Interpretability teach each method, with newer research added.</p>""",
    },
}
