# Seven-section plans for Maths for ML lessons. Chapter text comes from the live pages (see ml_import.py).

MATRIX_PICTURE = """<svg viewBox="0 0 480 170" role="img" aria-label="A unit square on the left becomes a slanted parallelogram on the right. On the far right, a flattened line shows a matrix with determinant zero.">
  <g fill="var(--ink)" font-size="14" text-anchor="middle" font-weight="600"><text x="70" y="18">Before</text><text x="240" y="18">After a matrix</text><text x="410" y="18">Determinant 0</text></g>
  <path d="M25 150H125M25 150V50" stroke="var(--line)" stroke-width="1.5" fill="none"/>
  <rect x="25" y="70" width="80" height="80" fill="none" stroke="var(--a)" stroke-width="2.5"/>
  <path d="M130 100h28m-8-6 8 6-8 6" fill="none" stroke="var(--dim)" stroke-width="2"/>
  <path d="M175 150H310M175 150V40" stroke="var(--line)" stroke-width="1.5" fill="none"/>
  <path d="M175 150 265 150 305 80 215 80Z" fill="none" stroke="var(--b)" stroke-width="2.5"/>
  <path d="M340 150H470M340 150V40" stroke="var(--line)" stroke-width="1.5" fill="none"/>
  <line x1="340" y1="150" x2="460" y2="70" stroke="var(--bad)" stroke-width="4"/>
</svg>"""

EIGEN_PICTURE = """<svg viewBox="0 0 480 180" role="img" aria-label="Three arrows before and after a matrix. Two eigenvector arrows stay on their lines and only change length. A third arrow swings to a new direction.">
  <defs><marker id="arrowE" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 10 5 0 10z" fill="context-stroke"/></marker></defs>
  <g fill="var(--ink)" font-size="14" font-weight="600" text-anchor="middle"><text x="110" y="18">Before</text><text x="360" y="18">After the matrix</text></g>
  <g stroke-width="3" fill="none">
    <line x1="110" y1="110" x2="160" y2="60" stroke="var(--ok)" marker-end="url(#arrowE)"/>
    <line x1="110" y1="110" x2="160" y2="160" stroke="var(--ok)" marker-end="url(#arrowE)"/>
    <line x1="110" y1="110" x2="180" y2="110" stroke="var(--b)" marker-end="url(#arrowE)"/>
    <line x1="360" y1="110" x2="435" y2="35" stroke="var(--ok)" marker-end="url(#arrowE)"/>
    <line x1="360" y1="110" x2="385" y2="135" stroke="var(--ok)" marker-end="url(#arrowE)"/>
    <line x1="360" y1="110" x2="430" y2="75" stroke="var(--b)" marker-end="url(#arrowE)"/>
  </g>
  <path d="M215 100h40m-8-6 8 6-8 6" fill="none" stroke="var(--dim)" stroke-width="2"/>
  <text x="444" y="40" font-size="13" fill="var(--ok)" font-weight="600">×1.5</text>
  <text x="404" y="150" font-size="13" fill="var(--ok)" font-weight="600">×0.5</text>
  <text x="438" y="92" font-size="13" fill="var(--b)" font-weight="600">swings</text>
</svg>"""

SVD_PICTURE = """<svg viewBox="0 0 480 130" role="img" aria-label="A matrix equals a sum of layers, drawn darker for the most important layer and fainter for later layers.">
  <g fill="var(--ink)" font-size="22" font-weight="600" text-anchor="middle"><text x="96" y="74">=</text><text x="196" y="74">+</text><text x="296" y="74">+</text><text x="396" y="74">+</text><text x="450" y="74">…</text></g>
  <rect x="10" y="26" width="70" height="70" rx="6" fill="var(--a)"/>
  <rect x="116" y="26" width="64" height="70" rx="6" fill="var(--a)" fill-opacity=".72"/>
  <rect x="216" y="26" width="64" height="70" rx="6" fill="var(--a)" fill-opacity=".38"/>
  <rect x="316" y="26" width="64" height="70" rx="6" fill="var(--a)" fill-opacity=".14"/>
  <g fill="var(--ink)" font-size="13" text-anchor="middle"><text x="45" y="116">Your matrix</text><text x="148" y="116">Layer 1</text><text x="248" y="116">Layer 2</text><text x="348" y="116">Layer 3</text></g>
</svg>"""

CHAIN_PICTURE = """<svg viewBox="0 0 480 130" role="img" aria-label="A chain from weight w to score z to probability a to loss L, with a slope on each link. Multiplying the slopes 1, 0.21 and 1.38 gives about 0.30.">
  <g fill="var(--tint)" stroke="var(--c)" stroke-width="2"><circle cx="40" cy="48" r="26"/><circle cx="175" cy="48" r="26"/><circle cx="310" cy="48" r="26"/><circle cx="440" cy="48" r="26"/></g>
  <g fill="var(--ink)" font-size="17" font-weight="600" text-anchor="middle"><text x="40" y="54">w</text><text x="175" y="54">z</text><text x="310" y="54">a</text><text x="440" y="54">L</text></g>
  <path d="M70 48h72m-8-6 8 6-8 6M205 48h72m-8-6 8 6-8 6M340 48h66m-8-6 8 6-8 6" fill="none" stroke="var(--dim)" stroke-width="2"/>
  <g fill="var(--ink)" font-size="14" text-anchor="middle"><text x="106" y="36">× 1</text><text x="241" y="36">× 0.21</text><text x="373" y="36">× 1.38</text></g>
  <text x="240" y="112" text-anchor="middle" font-size="16" font-weight="600" fill="var(--ink)">How much L moves when w moves: 1 × 0.21 × 1.38 ≈ 0.30</text>
</svg>"""

VALLEY_PICTURE = """<svg viewBox="0 0 480 170" role="img" aria-label="Oval contour lines of a narrow valley, with a path that zig-zags from wall to wall as it moves towards the centre.">
  <g fill="none" stroke="var(--line-strong)" stroke-width="1.5"><ellipse cx="260" cy="85" rx="210" ry="72"/><ellipse cx="260" cy="85" rx="150" ry="50"/><ellipse cx="260" cy="85" rx="90" ry="30"/><ellipse cx="260" cy="85" rx="36" ry="12"/></g>
  <path d="M60 60 96 124 136 48 176 116 210 62 232 100 248 76 258 88" fill="none" stroke="var(--b)" stroke-width="2.5"/>
  <circle cx="60" cy="60" r="5" fill="var(--b)"/><circle cx="260" cy="85" r="5" fill="var(--ok)"/>
  <text x="54" y="44" font-size="14" font-weight="600" fill="var(--b)">Start</text>
  <text x="274" y="90" font-size="14" font-weight="600" fill="var(--ok)">Minimum</text>
</svg>"""

BOWL_PICTURE = """<svg viewBox="0 0 480 150" role="img" aria-label="Left: a smooth bowl with one marble at the single lowest point. Right: a bumpy curve with two dips, one deeper, and marbles settled in each.">
  <g fill="var(--ink)" font-size="14" font-weight="600" text-anchor="middle"><text x="115" y="18">Convex: one bottom</text><text x="360" y="18">Non-convex: several dips</text></g>
  <path d="M20 40Q115 220 210 40" fill="none" stroke="var(--a)" stroke-width="3"/>
  <circle cx="115" cy="122" r="8" fill="var(--ok)"/>
  <path d="M250 50C275 170 315 170 345 90S395 110 415 110 455 80 470 50" fill="none" stroke="var(--b)" stroke-width="3"/>
  <circle cx="296" cy="137" r="8" fill="var(--ok)"/>
  <circle cx="415" cy="102" r="8" fill="var(--bad)"/>
</svg>"""

MATHS_PLANS = {
    "fundamentals/matrices-as-transformations": {
        "tabs": ["Intuition", "Maths", "In practice"],
        "situation": "Your recommendation model stacks two linear layers with no activation between them, and the second layer adds nothing. The interviewer asks:",
        "q": "What does a matrix do to a vector, and why do two linear layers act like one?",
        "analogy": "Think of a matrix as a rule that moves every point on a rubber sheet. Its columns say where the two axis arrows land. The determinant says how much area changes, and zero means the sheet was flattened onto a line, which can't be undone.",
        "picture": MATRIX_PICTURE,
        "caption": "Illustrative. Straight lines stay straight, and the origin stays put.",
        "situation_chapters": ["c1"],
        "play": {"chapter": "c6",
                 "try": "<b>Try to break it.</b> Pick the squash preset, then drag the entries until the two column arrows point the same way.",
                 "why": "<b>Now say why:</b> what happens to the determinant and the rank, and why can't this matrix be undone?"},
        "how": ["c2", "c5", "c4", "c7"],
        "practice": ["c8"],
        "trap": ["c3"],
        "reference": ["c9", "src"],
        "checklist": [
            "A matrix is a linear transformation of space.",
            "Its columns say where the basis vectors land.",
            "Multiplying matrices chains transformations, so order matters.",
            "The determinant is the area or volume scaling factor. Zero means no inverse.",
            "Stacked linear layers collapse into one matrix, which is why activations matter.",
        ],
    },
    "fundamentals/eigenvalues-and-eigenvectors": {
        "tabs": ["Intuition", "Maths", "In practice"],
        "situation": "You're running PCA on customer data where orders and app sessions move together. The interviewer asks:",
        "q": "What is an eigenvector, and how does PCA use eigenvectors?",
        "analogy": "Think of stretching a rubber sheet with arrows drawn on it. Most arrows swing to a new direction. A few stay on their own line and only get longer or shorter. Those are eigenvectors, and how much they stretch is the eigenvalue.",
        "picture": EIGEN_PICTURE,
        "caption": "Illustrative, using the lesson's covariance matrix: one direction stretches by 1.5, the other by 0.5.",
        "situation_chapters": ["c1"],
        "play": {"chapter": "c5",
                 "try": "<b>Try to break it.</b> On the covariance matrix, find the arrows that stay on their line. Then switch to rotation 45° and look for them again.",
                 "why": "<b>Now say why:</b> why does the rotation have no such arrows, while the covariance matrix has two perpendicular ones?"},
        "how": ["c2", "c4", "c6"],
        "practice": ["c7"],
        "trap": ["c3"],
        "reference": ["c8", "src"],
        "checklist": [
            "An eigenvector is a direction the matrix only stretches: Av = λv.",
            "The eigenvalue is the stretch factor.",
            "Symmetric matrices, like covariance matrices, have real eigenvalues and perpendicular eigenvectors.",
            "PCA's components are the covariance eigenvectors, and the eigenvalues are their variances.",
            "You named another use, like Hessian curvature or PageRank.",
        ],
    },
    "fundamentals/svd-and-low-rank": {
        "tabs": ["Intuition", "Maths", "In practice"],
        "situation": "You need to fine-tune a huge language model, and a teammate suggests training only a low-rank update to its weights. The interviewer asks:",
        "q": "What is SVD, and what do you get by keeping only the top k singular values?",
        "analogy": "Think of a picture as a stack of transparent layers, sorted from most to least important. The first few layers give you almost the whole picture. Later layers add fine detail, and eventually mostly noise. SVD finds those layers for any matrix.",
        "picture": SVD_PICTURE,
        "caption": "Illustrative. Each layer is one rank-one term, and its singular value says how much it matters.",
        "situation_chapters": ["c1"],
        "play": {"chapter": "c5",
                 "try": "<b>Try to break it.</b> Slide the rank up from 1 and watch the error against the clean icon. Keep going all the way to 32.",
                 "why": "<b>Now say why:</b> why does the error against the clean icon stop falling and then rise, even as you keep more of the image?"},
        "how": ["c2", "c4", "c6"],
        "practice": ["c7"],
        "trap": ["c3", "c8"],
        "reference": ["c9", "src"],
        "checklist": [
            "SVD writes any matrix as UΣVᵀ, for any shape.",
            "It's a sum of rank-one layers ordered by importance.",
            "Keeping the top k gives the best rank-k approximation (Eckart–Young).",
            "The error is the root sum of squares of the dropped singular values.",
            "You named a use, like PCA, recommenders or LoRA.",
        ],
    },
    "fundamentals/derivatives-and-chain-rule": {
        "tabs": ["Intuition", "Maths", "In practice"],
        "situation": "Your model has billions of weights, and nudging each one to measure its effect would take billions of passes for a single step. The interviewer asks:",
        "q": "How does backpropagation use the chain rule?",
        "analogy": "Think of a row of gears. Turn the first one, and the last one moves by the product of every gear ratio in between. The chain rule is that product. Backprop walks the gears backwards from the loss to find how much each weight matters.",
        "picture": CHAIN_PICTURE,
        "caption": "From the lesson's one-neuron example, with w = 1, x = 1, b = −0.2 and y = 0.",
        "situation_chapters": ["c1"],
        "play": {"chapter": "c6",
                 "try": "<b>Try to break it.</b> Here z is the neuron's score before the sigmoid. Raise w and x until z is above about 5, for example w = 3 and x = 2.",
                 "why": "<b>Now say why:</b> why does the gradient vanish even when the prediction is badly wrong?"},
        "how": ["c2", "c4", "c5"],
        "practice": ["c7"],
        "trap": ["c3"],
        "reference": ["c8", "src"],
        "checklist": [
            "A derivative measures how much the output changes for a small change in the input.",
            "The gradient collects the partial derivatives and points uphill, so we step against it.",
            "The chain rule says the derivative through a composition is the product of local derivatives.",
            "Backprop applies it from the loss backwards and reuses shared products.",
            "All the gradients cost about one extra pass.",
            "Saturating activations make local slopes tiny, which causes vanishing gradients.",
        ],
    },
    "fundamentals/gradient-descent": {
        "tabs": ["Intuition", "Maths", "In practice"],
        "situation": "Someone raises the learning rate slightly, and your training loss explodes to NaN. The interviewer asks:",
        "q": "Why can a larger learning rate make training diverge, and how do momentum and Adam help?",
        "analogy": "Think of walking down a narrow valley in fog. You can only feel the slope under your feet. Take steps that are too big and you bounce from wall to wall, climbing higher each time. Momentum is like a heavy ball that keeps rolling along the valley floor, and Adam adjusts your stride to the steepness in each direction.",
        "picture": VALLEY_PICTURE,
        "caption": "Illustrative. Plain gradient descent zig-zags across a valley that's much steeper in one direction than the other.",
        "situation_chapters": ["c1"],
        "play": {"chapter": "c5",
                 "try": "<b>Try to break it.</b> Choose gradient descent with η = 0.19, then move to η = 0.21. Then try momentum and Adam at 0.21.",
                 "why": "<b>Now say why:</b> why does such a small change blow up plain gradient descent, while the other two still converge?"},
        "how": ["c2", "c4", "c6"],
        "practice": ["c7", "c8"],
        "trap": ["c3"],
        "reference": ["c9", "src"],
        "checklist": [
            "Gradient descent subtracts the learning rate times the gradient.",
            "The learning rate must stay below about 2 over the largest curvature, or training diverges.",
            "When curvatures differ a lot, plain gradient descent zig-zags and crawls.",
            "Momentum averages gradients into a velocity, which damps the oscillation.",
            "Adam adds per-parameter scaling and bias correction.",
        ],
    },
    "fundamentals/convexity-and-local-minima": {
        "tabs": ["Intuition", "Maths", "In practice"],
        "situation": "Logistic regression gives you the same answer on every run, but your neural network ends somewhere different with each seed. The interviewer asks:",
        "q": "What does convexity guarantee, and which models have a convex loss?",
        "analogy": "Think of dropping a marble. In a smooth bowl, it always ends at the same lowest point. On a bumpy surface, it settles in whichever dip is nearest, and that may not be the deepest one.",
        "picture": BOWL_PICTURE,
        "caption": "Illustrative. The red marble is stuck in a local minimum, and its slope there is zero, so it has no reason to move.",
        "situation_chapters": ["c1"],
        "play": {"chapter": "c6",
                 "try": "<b>Try to break it.</b> Choose the non-convex loss, start at θ = 0, then start at θ = 0.5. Then switch to the convex loss and try any start you like.",
                 "why": "<b>Now say why:</b> why does the same algorithm land in different places on one loss, but not on the other?"},
        "how": ["c2", "c5"],
        "practice": ["c4", "c7"],
        "trap": ["c3"],
        "reference": ["c8", "src"],
        "checklist": [
            "A function is convex if the line between any two points on it lies above the graph.",
            "Equivalently, its Hessian is positive semi-definite everywhere.",
            "For a convex loss, every local minimum is global, so the start doesn't matter.",
            "Linear and logistic regression, ridge, lasso and SVMs are convex.",
            "Neural networks, k-means and Gaussian mixtures aren't.",
            "In high dimensions, saddle points are the bigger problem.",
        ],
    },
}

BAYES_PICTURE = """<svg viewBox="0 0 480 130" role="img" aria-label="A bar of 585 flagged orders out of 10,000. A small red part, 90 orders, is real fraud. A much larger part, 495 orders, is legitimate.">
  <text x="4" y="18" font-size="14" font-weight="600" fill="var(--ink)">585 flagged orders, out of 10,000</text>
  <rect x="4" y="30" width="72" height="44" fill="var(--bad)"/><rect x="76" y="30" width="400" height="44" fill="var(--a)" fill-opacity=".28" stroke="var(--a)"/>
  <text x="40" y="58" font-size="16" font-weight="700" fill="#fff" text-anchor="middle">90</text><text x="276" y="58" font-size="16" font-weight="700" fill="var(--ink)" text-anchor="middle">495 legitimate</text>
  <text x="4" y="98" font-size="14" font-weight="600" fill="var(--bad)">Real fraud</text>
  <text x="4" y="122" font-size="15" font-weight="600" fill="var(--ink)">So a flag means only 90 ÷ 585 = 15.4% fraud</text>
</svg>"""

DIST_PICTURE = """<svg viewBox="0 0 480 150" role="img" aria-label="Four small shapes with their uses. Bernoulli: two bars for yes or no, giving log loss. Poisson: bars for counts, giving Poisson loss. Gaussian: a bell for measurement errors, giving squared error. Exponential: a falling curve for waiting times.">
  <g fill="var(--a)"><rect x="24" y="60" width="26" height="40"/><rect x="58" y="36" width="26" height="64"/>
    <rect x="136" y="84" width="14" height="16"/><rect x="153" y="54" width="14" height="46"/><rect x="170" y="42" width="14" height="58"/><rect x="187" y="62" width="14" height="38"/><rect x="204" y="84" width="14" height="16"/></g>
  <path d="M250 100C275 100 280 38 300 38S325 100 350 100" fill="none" stroke="var(--a)" stroke-width="3"/>
  <path d="M376 34C395 80 420 96 472 100" fill="none" stroke="var(--a)" stroke-width="3"/>
  <path d="M10 100H100M130 100H226M246 100H354M372 100H476" stroke="var(--line-strong)" stroke-width="1.5"/>
  <g font-size="14" font-weight="600" fill="var(--ink)" text-anchor="middle"><text x="55" y="20">Yes or no</text><text x="178" y="20">A count</text><text x="300" y="20">An error</text><text x="424" y="20">A wait</text></g>
  <g font-size="13" fill="var(--dim)" text-anchor="middle"><text x="55" y="122">Bernoulli</text><text x="178" y="122">Poisson</text><text x="300" y="122">Gaussian</text><text x="424" y="122">Exponential</text>
    <text x="55" y="142">log loss</text><text x="178" y="142">Poisson loss</text><text x="300" y="142">squared error</text><text x="424" y="142">time-to-event</text></g>
</svg>"""

AVERAGE_PICTURE = """<svg viewBox="0 0 480 170" role="img" aria-label="Error against number of models averaged. With independent errors the curve keeps falling towards zero. With correlated errors it flattens at a floor.">
  <path d="M50 14V140H470" fill="none" stroke="var(--dim)" stroke-width="1.5"/>
  <path d="M50 30C80 110 150 128 460 134" fill="none" stroke="var(--ok)" stroke-width="3"/>
  <path d="M50 30C80 72 140 80 460 84" fill="none" stroke="var(--bad)" stroke-width="3"/>
  <g font-size="14" font-weight="600"><text x="470" y="72" text-anchor="end" fill="var(--bad)">Correlated errors hit a floor</text><text x="470" y="122" text-anchor="end" fill="var(--ok)">Independent errors keep falling</text></g>
  <g font-size="13" fill="var(--dim)"><text x="260" y="162" text-anchor="middle">Number of models averaged</text><text x="16" y="85" text-anchor="middle" transform="rotate(-90 16 85)">Error</text></g>
</svg>"""

MAP_PICTURE = """<svg viewBox="0 0 480 110" role="img" aria-label="A scale from 0 to 100 percent late. The platform average is at 25 percent, MAP at 42 percent and MLE at 100 percent.">
  <path d="M20 66H460" stroke="var(--line-strong)" stroke-width="3"/>
  <g font-size="13" fill="var(--dim)" text-anchor="middle"><text x="20" y="100">0%</text><text x="476" y="100" text-anchor="end">100% late</text></g>
  <circle cx="130" cy="66" r="9" fill="var(--st)"/><circle cx="205" cy="66" r="9" fill="var(--ok)"/><circle cx="460" cy="66" r="9" fill="var(--b)"/>
  <g font-size="14" font-weight="600" text-anchor="middle"><text x="118" y="44" fill="var(--st)">Platform 25%</text><text x="225" y="24" fill="var(--ok)">MAP 42%</text><text x="420" y="44" fill="var(--b)">MLE 100%</text></g>
  <path d="M205 30V54" stroke="var(--ok)" stroke-width="1.5"/>
</svg>"""

CI_PICTURE = """<svg viewBox="0 0 480 160" role="img" aria-label="Eight horizontal intervals around a vertical line marking the true mean. Seven cross the line. One misses it and is drawn in red.">
  <path d="M240 18V150" stroke="var(--b)" stroke-width="2.5"/>
  <text x="240" y="13" font-size="14" font-weight="600" fill="var(--b)" text-anchor="middle">True mean</text>
  <g stroke="var(--a)" stroke-width="3"><path d="M120 28H300M170 44H340M100 60H270M190 76H360M140 108H320M160 124H290M110 140H280"/></g>
  <path d="M270 92H430" stroke="var(--bad)" stroke-width="3.5"/>
  <text x="438" y="97" font-size="13" font-weight="600" fill="var(--bad)">miss</text>
</svg>"""

PVALUE_PICTURE = """<svg viewBox="0 0 480 160" role="img" aria-label="A bell curve showing results if nothing changed. A marker shows the observed result, and the shaded tail beyond it is the p-value.">
  <path d="M30 130C130 130 160 26 240 26S350 130 450 130" fill="none" stroke="var(--a)" stroke-width="3"/>
  <path d="M340 130H450C410 130 375 118 340 90Z" fill="var(--bad)" fill-opacity=".35"/>
  <path d="M30 130H450" stroke="var(--dim)" stroke-width="1.5"/><path d="M340 58V130" stroke="var(--bad)" stroke-width="2.5"/>
  <text x="240" y="16" font-size="14" font-weight="600" fill="var(--a)" text-anchor="middle">If nothing had changed</text>
  <text x="346" y="54" font-size="14" font-weight="600" fill="var(--bad)">Your result</text>
  <text x="476" y="152" font-size="14" font-weight="600" fill="var(--bad)" text-anchor="end">p-value: this far or further</text>
</svg>"""

CONFOUND_PICTURE = """<svg viewBox="0 0 480 170" role="img" aria-label="Engagement sits at the top with arrows to using tracking and to reordering. A dashed line between tracking and reordering shows a correlation with no arrow of cause.">
  <defs><marker id="arrowC" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="var(--dim)"/></marker></defs>
  <rect x="170" y="8" width="140" height="42" rx="8" fill="var(--st)"/><rect x="20" y="118" width="140" height="42" rx="8" fill="none" stroke="var(--a)" stroke-width="2"/><rect x="320" y="118" width="140" height="42" rx="8" fill="none" stroke="var(--a)" stroke-width="2"/>
  <path d="M195 50 110 116" stroke="var(--dim)" stroke-width="2" fill="none" marker-end="url(#arrowC)"/><path d="M285 50 370 116" stroke="var(--dim)" stroke-width="2" fill="none" marker-end="url(#arrowC)"/>
  <path d="M164 139H316" stroke="var(--bad)" stroke-width="2" stroke-dasharray="6 5"/>
  <g font-size="14" font-weight="600" text-anchor="middle"><text x="240" y="34" fill="#fff">Engagement</text><text x="90" y="144" fill="var(--ink)">Uses tracking</text><text x="390" y="144" fill="var(--ink)">Reorders</text><text x="240" y="128" fill="var(--bad)">Correlated</text></g>
</svg>"""

ENTROPY_PICTURE = """<svg viewBox="0 0 480 120" role="img" aria-label="A bar showing cross-entropy of 3.77 bits as entropy of 1.74 bits plus KL divergence of 2.03 bits.">
  <text x="4" y="18" font-size="14" font-weight="600" fill="var(--ink)">Cross-entropy: 3.77 bits</text>
  <rect x="4" y="30" width="218" height="44" fill="var(--a)"/><rect x="222" y="30" width="254" height="44" fill="var(--bad)"/>
  <text x="113" y="58" font-size="15" font-weight="700" fill="#fff" text-anchor="middle">Entropy 1.74</text><text x="349" y="58" font-size="15" font-weight="700" fill="#fff" text-anchor="middle">KL 2.03</text>
  <g font-size="13" fill="var(--dim)" text-anchor="middle"><text x="113" y="96">Surprise you can't avoid</text><text x="349" y="96">Extra cost of the wrong model</text></g>
</svg>"""


def _plan(situation, q, analogy, picture, caption, play, how, practice, trap, reference, checklist, tabs=None, edits=None, situation_chapters=None, strip=None, trap_title=None, trap_html=None):
    return {"tabs": tabs or ["Intuition", "Maths", "In practice"], "situation": situation, "q": q, "analogy": analogy, "picture": picture, "caption": caption,
            "situation_chapters": situation_chapters or ["c1"], "play": {"chapter": play[0], "try": play[1], "why": play[2]}, "how": how, "practice": practice, "trap": trap,
            "reference": reference, "checklist": checklist, "edits": edits or [], "strip": strip or [], "trap_title": trap_title, "trap_html": trap_html}


MATHS_PLANS.update({
    "fundamentals/probability-and-bayes": _plan(
        "Your fraud alarm catches 90% of fraud and wrongly flags 5% of legitimate orders, and 1% of orders are fraud. A teammate says a flagged order is 90% likely to be fraud. The interviewer asks:",
        "Why can an accurate test for a rare event still produce mostly false positives?",
        "Think of a guard at a packed stadium looking for a few pickpockets. Even a good guard stops plenty of innocent people, simply because there are so many more of them. Bayes' rule is how you count both groups before you trust the flag.",
        BAYES_PICTURE, "From the lesson's fraud alarm, counted over 10,000 orders.",
        ("c6", "<b>Try to break it.</b> Raise sensitivity from 90% to 99%. Then put it back and cut false alarms from 5% to 1%.", "<b>Now say why:</b> why does cutting false alarms help so much more than catching more fraud?"),
        ["c2", "c4", "c5"], ["c7"], ["c3"], ["c8", "src"],
        ["Bayes' rule: the posterior is the likelihood times the prior, divided by the evidence.",
         "The evidence comes from the law of total probability.",
         "The trap is ignoring the prior. Rare events give mostly false positives.",
         "You can solve these by counting a population, say 10,000.",
         "You linked it to ML, like precision on imbalanced data or Naive Bayes."]),
    "fundamentals/probability-distributions": _plan(
        "You're predicting how many orders arrive each hour. A teammate uses squared error, and the model sometimes predicts −2 orders. The interviewer asks:",
        "How does the distribution you assume for the target decide the loss?",
        "Think of a drawer of measuring tools. A yes or no, a count, a waiting time and a measurement error each need a different tool. Pick the right one, and it also tells you which loss to train with.",
        DIST_PICTURE, "Illustrative shapes. The losses come from maximum likelihood.",
        ("c5", "<b>Try to break it.</b> On the Poisson, raise the rate and watch the shape. Then compare its mean and variance.", "<b>Now say why:</b> why does a Poisson stop fitting if your counts vary much more than their average?"),
        ["c2", "c6", "c7"], ["c4"], ["c3"], ["c8", "src"],
        ["You matched each distribution to its kind of quantity: yes or no, count, waiting time, sum of small effects.",
         "Binomial is a sum of Bernoullis, and Poisson is its rare-event limit.",
         "The central limit theorem makes averages roughly Gaussian.",
         "Choosing the distribution fixes the loss through maximum likelihood.",
         "Gaussian gives squared error, Bernoulli gives log loss, and categorical gives cross-entropy."]),
    "fundamentals/expectation-and-variance": _plan(
        "Your team averages 100 ETA models, expecting the error to fall tenfold, but it barely moves. The interviewer asks:",
        "Why does averaging correlated models help less than averaging independent ones?",
        "Think of asking friends to guess a delivery time. If they guess independently, their errors cancel out. If they all read the same forecast, they share the same mistake, and asking more friends barely helps.",
        AVERAGE_PICTURE, "Illustrative. The floor depends on how correlated the errors are.",
        ("c6", "<b>Try to break it.</b> Set the correlation to 0.3 and raise the number of models as far as it goes. Then set the correlation to 0.", "<b>Now say why:</b> why can't more models get you below the floor, and what would you change to lower it?"),
        ["c2", "c4", "c5"], ["c7"], ["c3"], ["c8", "src"],
        ["Expectation is the probability-weighted average, and it's linear even for dependent variables.",
         "Covariance measures joint movement, and correlation is its scaled version.",
         "The variance of a sum adds the variances plus twice the covariance.",
         "Independent errors shrink like 1/n, while correlated ones hit a floor.",
         "That's why random forests decorrelate their trees."]),
    "fundamentals/mle-and-map": _plan(
        "A new restaurant's first order was late. Its estimated late rate is now 100%, and it drops to the bottom of your rankings. The interviewer asks:",
        "What is the difference between MLE and MAP?",
        "Think of judging a new restaurant after one late order. The data alone says it's always late, but your experience with other restaurants says that's unlikely. MLE trusts only the data. MAP blends in that experience, and as orders pile up, the data takes over.",
        MAP_PICTURE, "From the lesson's example: 3 orders, all late, with a prior worth 10 imaginary orders at 25%.",
        ("c6", "<b>Try to break it.</b> Set 3 orders, all late, and compare MLE with MAP. Then raise the orders to 100.", "<b>Now say why:</b> why do the two estimates start far apart and then nearly agree?"),
        ["c2", "c5", "c7"], ["c4"], ["c3"], ["c8", "src"],
        ["MLE picks the parameters that make the observed data most probable.",
         "We maximise the log-likelihood because products become sums.",
         "Common losses are negative log-likelihoods, like squared error and log loss.",
         "MAP adds a prior and maximises likelihood times prior.",
         "A Gaussian prior gives L2, and a Laplace prior gives L1."]),
    "fundamentals/confidence-intervals-and-bootstrap": _plan(
        "You report 87% accuracy on 500 test rows, and a stakeholder asks how sure you are. The interviewer asks:",
        "What does a 95% confidence interval actually mean, and when would you use the bootstrap?",
        "Think of throwing a ring at a hidden peg. Once it lands, it either circles the peg or it doesn't. The 95% describes how good your throw is: about 95 of every 100 throws land around the peg.",
        CI_PICTURE, "Illustrative. Each line is one sample's interval, and most of them cover the true mean.",
        ("c4", "<b>Try to break it.</b> Start at n = 10 and read the coverage. Then move up to n = 100.", "<b>Now say why:</b> why do intervals on skewed data miss more often when the sample is small?"),
        ["c2", "c5"], ["c6"], ["c3", "c7"], ["c8", "src"],
        ["The standard error is how much a statistic varies between samples, s over root n for a mean.",
         "The central limit theorem makes the mean roughly Gaussian, so mean ± about 2 standard errors gives 95%.",
         "The 95% describes the procedure, not this one interval.",
         "Coverage falls short with small or skewed samples.",
         "The bootstrap resamples your data with replacement, for any statistic."],
        edits=[("The lab below shows 100 such intervals at once.", "The lab in the Intuition tab shows 100 such intervals at once.")]),
    "fundamentals/hypothesis-testing-and-ab-tests": _plan(
        "After a week, your new checkout button converts at 10.4% against 10.0%, and the product manager wants to ship it. The interviewer asks:",
        "How would you run an A/B test, and what does the p-value mean?",
        "Think of a coin you suspect is biased. A few heads in a row proves little. An A/B test asks how surprising your result would be if nothing had changed. And flipping until you like the answer doesn't count.",
        PVALUE_PICTURE, "Illustrative. The p-value assumes no real difference, so it isn't the chance that B is better.",
        ("c6", "<b>Try to break it.</b> Compare checking once at day 20 with checking daily and stopping at the first p below 0.05. Neither arm has any real difference here.", "<b>Now say why:</b> why does looking more often create false wins when nothing changed?"),
        ["c2", "c4", "c5"], ["c7"], ["c3"], ["c8", "src"],
        ["An A/B test randomises users and tests the null hypothesis of no difference.",
         "The p-value is how likely a difference this large is if the null were true.",
         "Before launch, you fix the primary metric, the minimum detectable effect and the sample size.",
         "You avoid peeking, or use sequential methods.",
         "You check sample-ratio mismatch and correct for multiple metrics.",
         "You report the effect size with a confidence interval."]),
    "fundamentals/correlation-vs-causation": _plan(
        "Customers who use live order tracking reorder far more often, and someone wants to push tracking on everyone. The interviewer asks:",
        "How can correlation mislead you, and how do you estimate a causal effect?",
        "Think of umbrellas and wet streets. They rise and fall together, but handing out umbrellas won't make it rain. Rain causes both. A hidden common cause like this can make two things look linked when neither affects the other.",
        CONFOUND_PICTURE, "From the lesson's simulation: engagement drives both tracking use and reordering.",
        ("c4", "<b>Try to break it.</b> Look at all patients, then split them by stone size.", "<b>Now say why:</b> how can one treatment win in both groups and still lose overall?"),
        ["c2", "c5"], ["c6"], ["c3"], ["c7", "src"],
        ["A correlation can come from a confounder, reverse causation, selection bias or chance.",
         "Confounding can even reverse a comparison, as in Simpson's paradox.",
         "Randomisation is the cleanest route, because nothing about the unit affects assignment.",
         "Without it, you adjust for measured confounders and argue there are no unmeasured ones.",
         "Feature importance in a predictive model isn't a causal effect."],
        tabs=["Intuition", "How it works", "In practice"],
        edits=[("Data scientists are asked the second kind constantly", "ML engineers are asked the second kind constantly")]),
    "fundamentals/entropy-cross-entropy-kl": _plan(
        "Two models have the same accuracy, but one says 99% on its top guess and the other says 51%. You need a score that tells them apart. The interviewer asks:",
        "How are entropy, cross-entropy and KL divergence related?",
        "Think of surprise as a cost. Entropy is the surprise you can't avoid, even with perfect knowledge. Cross-entropy is the surprise you get when you bet using your model. KL divergence is the difference: the extra price of being wrong.",
        ENTROPY_PICTURE, "From the lesson's lab, for the confident and wrong prediction.",
        ("c5", "<b>Try to break it.</b> Move the model's prediction from close, to uniform, to confident and wrong. Watch the KL and compare its two directions.", "<b>Now say why:</b> why does uniform cost less than confident and wrong, and why do the two KL directions differ?"),
        ["c2", "c4", "c6"], ["c7"], ["c3"], ["c8", "src"],
        ["Entropy is the expected surprise, measuring uncertainty.",
         "Cross-entropy is the surprise when outcomes follow p but you predict q.",
         "With one-hot labels it's the log loss, and minimising it is maximum likelihood.",
         "Cross-entropy equals entropy plus KL divergence.",
         "KL is non-negative, zero only when they match, and asymmetric.",
         "You named a use, like distillation, VAEs or RLHF."]),
})
