"""Plans for the 12-part mechanistic interpretability survey (papers/mech-interp-*).
Sources come from Content/Reference/Site lesson kit (deep-learning)/mech_interp_split.py."""


def _p(analogy, problem, how, found, limits, verdict, changed, reference=(), **extra):
    return {"analogy": analogy, "picture_chapter": "flow", "problem": list(problem), "how": list(how),
            "found": list(found), "limits": list(limits), "verdict": list(verdict), "reference": list(reference),
            "hidden": [], "changed_html": changed, "edits": [], **extra}


MECH_PLANS = {
    "papers/mech-interp-why-look-inside": _p(
        "Testing a model only on its answers is like judging a car by test drives alone. It can pass every drive and still hide a fault the drives never trigger. Mechanistic interpretability opens the bonnet.",
        ["wl-c1"], ["wl-c2", "wl-c3", "wl-c4"], ["wl-c5"], ["wl-c6"], ["wl-c7"],
        """<p><b>What to remember.</b> Behavioural tests tell you what a model does on the inputs you tried. Mechanistic interpretability tries to say how it does it, with causal evidence, so you can catch failures your tests never trigger. The rest of the series asks how far the field has got.</p>"""),
    "papers/mech-interp-building-blocks": _p(
        "A transformer is like a shared whiteboard passed down a row of people. Each person reads the board and adds a note, and nobody erases anything. Features are the ideas written on the board, and a circuit is the set of people whose notes together produce one answer.",
        ["nf-c1"], ["nf-c2", "nf-c3", "nf-c4", "rs-c1", "rs-c2", "rs-c3", "rs-c4", "ci-c1", "ci-c2", "ci-c3"],
        ["ci-c4", "ci-c5"], ["nf-c5", "rs-c5"], ["nf-c6", "rs-c6", "ci-c6"],
        """<p><b>What to remember.</b> The unit of analysis is a feature, not a neuron. The residual stream is a sum, which is why a prediction can be split into contributions. A circuit is a hypothesis about which features and components compute a behaviour, and the induction and name-mover circuits are the classic worked examples.</p>"""),
    "papers/mech-interp-four-bets": _p(
        "Think of four bets that a whole building rests on. If concepts are directions, if models pack many of them into few neurons, if a model can sometimes read itself, and if different models learn alike, then today's tools make sense. Each bet pays off only partly.",
        ["lr-c1"], ["lr-c2", "lr-c3", "lr-c4", "sp-c1", "sp-c2", "sp-c3", "sp-c5", "sp-c6", "sp-c7", "sp-c8", "sp-c9", "pa-c1", "un-c1", "un-c2", "un-c3"],
        ["sp-c11", "pa-c2", "un-c4"], ["lr-c5", "sp-c12", "pa-c3"], ["lr-c6", "pa-c4", "un-c5"],
        """<p><b>What to remember.</b> Linear representations and superposition are the working assumptions behind probes, steering and SAEs, and both have strong support in toy models and suggestive support in real ones. Privileged access and universality hold only in some settings, so claims that lean on them need extra checks.</p>""",
        reference=["sp-src"]),
    "papers/mech-interp-sparse-autoencoders": _p(
        "A sparse autoencoder is like un-mixing a smoothie. It learns a long list of possible ingredients and explains each sip with only a few of them. If you push too hard for few ingredients, it under-measures the ones that are really there.",
        ["s1-c1"], ["s1-c2", "s1-c3", "s1-c4", "s1-c5", "s2-c1", "s2-c2", "s4-c1", "s4-c2"],
        ["s2-c3", "s4-c3"], ["s3-c1", "s3-c2", "s3-c3"], ["s1-c6", "s2-c4", "s3-c4", "s4-c4"],
        """<p><b>What to remember.</b> SAEs are the field's main tool for open-ended feature discovery. Top-k and JumpReLU fix the L1 shrinkage problem, but dead latents, absorption and seed dependence mean an SAE feature is one useful approximation, not ground truth. Test features causally, and use supervised directions when you already know the concept.</p>"""),
    "papers/mech-interp-beyond-one-layer": _p(
        "An SAE is a snapshot of what one layer holds. A transcoder is a readable replacement part for one MLP, and a crosscoder tracks one feature across many layers. Building the model readable from the start is like designing a machine with labelled parts, but the hidden wiring tends to come back somewhere else.",
        ["t1-c1"], ["t1-c2", "t1-c3", "x2-c1", "x2-c2", "d3-c1", "d3-c2", "d3-c3", "d3-c4"],
        ["x2-c3", "x2-c4"], ["t1-c4"], ["t1-c5", "x2-c5", "d3-c5"],
        """<p><b>What to remember.</b> Transcoders and cross-layer transcoders make feature-to-feature wiring readable, which is what attribution graphs are built on, at a large parameter cost. Crosscoders remove duplicate features across layers and make model comparison possible. Interpretable-by-design models help, but the network routes superposition around the constraint.</p>"""),
    "papers/mech-interp-finding-circuits": _p(
        "Finding a circuit is like finding which wires in a house matter for one light. Swap one wire's signal for a broken one and see if the light changes. A backup wire can make an important wire look useless, so you test both ways: cut the circuit, then cut everything else.",
        ["p1-c1"], ["p1-c2", "p1-c3", "p2-c1", "p2-c2", "p2-c3", "p3-c1", "p3-c2", "p4-c1", "p4-c2"],
        ["p2-c4"], ["p1-c4", "p3-c3"], ["p1-c5", "p4-c3"],
        """<p><b>What to remember.</b> Activation patching is the core causal test, and ACDC and EAP automate it. Attribution graphs give feature-level circuits per prompt. The choice of corruption and metric changes the answer, backup components hide importance, and real circuits usually explain only part of a behaviour, so report necessity and sufficiency.</p>"""),
    "papers/mech-interp-judging-claims": _p(
        "Interpretability results today are like restaurant reviews that each use a different scale. One counts stars, one counts dishes, one just says it felt nice. The survey proposes one report card so explanations can be compared.",
        ["j1-c1"], ["j2-c1", "j2-c2", "j2-c3", "j2-c4"], ["j1-c3"], ["j1-c2"], ["j2-c5"],
        """<p><b>What to remember.</b> Ask five things of any explanation: are its importance scores faithful to real interventions, how much of the behaviour does it cover, does it survive new seeds and paraphrases, is it causally necessary and sufficient, and does it help people predict or fix the model. No single score is enough.</p>"""),
    "papers/mech-interp-reading-the-mind": _p(
        "Reading activations is like reading a draft before the author finishes. A lens peeks at the half-written sentence. A verbaliser asks the author to describe the draft in words. A probe checks whether a fact is in the draft, but that doesn't mean the author will use it.",
        ["l1-c1"], ["l1-c2", "l1-c3", "l1-c4", "l2-c1", "l2-c2", "l3-c1", "l3-c2", "l4-c1", "l4-c2"],
        ["l4-c4"], ["l3-c3"], ["l4-c3"],
        """<p><b>What to remember.</b> Lenses and verbalisers read an activation as a whole. A probe's accuracy shows a property is decodable, not used, so compare against control tasks and confirm with amnesic or patching-based causal probing. Probes are cheap and useful monitors when you know what you are looking for.</p>"""),
    "papers/mech-interp-compare-locate-steer": _p(
        "Think of a recipe that was edited. Model diffing finds which lines changed, localisation finds which line holds the salt, and steering adds a pinch more salt while cooking without rewriting the recipe.",
        ["m1-c1"], ["m1-c3", "m2-c1", "m2-c2", "m3-c1"], ["m1-c2", "m3-c2"], ["m2-c3"], ["m3-c3"],
        """<p><b>What to remember.</b> Diffing shows what fine-tuning added, but rotated features can look like new ones. Causal tracing locates where a fact matters, yet where a fact matters is not always the best place to edit it. Steering vectors change behaviour at inference with no retraining, and the refusal direction shows both their power and their risk.</p>"""),
    "papers/mech-interp-watching-models-learn": _p(
        "Studying one finished checkpoint is like studying an adult and guessing their childhood. Training checkpoints are the photo album: you can see when each skill appeared, and sometimes the skill was quietly growing long before it showed up.",
        ["g1-c1"], ["g1-c2", "g2-c1", "g2-c3", "g3-c1", "g3-c2", "g4-c1", "g4-c2", "g4-c3"],
        ["g2-c4", "g1-c3"], ["g2-c2"], ["g3-c3"],
        """<p><b>What to remember.</b> Smooth loss can hide abrupt skill jumps, some emergence is a metric artefact and some is real, and internal precursors can grow before behaviour changes. Forecasting specific capabilities is still mostly retrospective. Training data attribution offers a second route, tracing behaviour to the examples that caused it.</p>"""),
    "papers/mech-interp-six-schools": _p(
        "The six schools are like different ways to make a city safe. One fixes the worst streets now, one maps every street, one studies how the city grew, and one asks residents what they see. Each answers a different question.",
        ["o1-c1"], ["o1-c2", "o1-c3", "o2-c1", "o2-c2"], [], [], ["o2-c3"],
        """<p><b>What to remember.</b> Pick the orientation from the question. Pragmatic work helps safety now, ambitious work aims for full understanding, developmental work explains how structure forms, introspection is cheap but least robust to deception, and automated interpretability scales only with human checks.</p>""",
        found_note="<h3>How the schools compare</h3><p>The survey does not rank the six orientations. It argues they answer different questions, and that the same method, such as SAEs or patching, can serve several of them. The Method tab walks through each one, and the verdict below says how to choose.</p>",
        limits_note="<h3>Where each school is weakest</h3><p>Pragmatic work may help without real understanding. Ambitious reverse-engineering scales badly. Introspective self-reports can confabulate or lie. Automated pipelines propagate their own errors and invite over-trust in polished output.</p>"),
    "papers/mech-interp-safety": _p(
        "Interpretability for safety is like a medical scan. It can find problems a check-up misses and guide a treatment, but a clean scan of 30% of the body doesn't mean the patient is healthy.",
        ["z1-c1"], ["z1-c2", "z1-c3"], ["z3-c1"], ["z2-c1", "z2-c2", "z2-c3"], ["z3-c2"],
        """<p><b>What to remember.</b> White-box tools such as concept erasure, knowledge editing, steering and monitoring can act where black-box safety can't, but interpretability has its own risks: false confidence, silent failure in deployment, help for attackers and opportunity cost. The survey's answer to its central question is a qualified yes.</p>""",
        reference=["z3-c3"]),
}
