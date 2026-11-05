# Seven-section plans for Classical ML lessons. Chapter text comes from the live pages (see ml_import.py).
from maths_plans import _plan

LINE_PICTURE = """<svg viewBox="0 0 480 170" role="img" aria-label="Points scattered around a straight line, with a short vertical gap from each point to the line.">
  <path d="M40 10V150H470" fill="none" stroke="var(--dim)" stroke-width="1.5"/>
  <path d="M50 140 450 30" stroke="var(--b)" stroke-width="3"/>
  <g stroke="var(--bad)" stroke-width="2"><path d="M90 129V104M150 113V128M210 96V70M270 80V92M330 63V40M390 47V60"/></g>
  <g fill="var(--a)"><circle cx="90" cy="104" r="5"/><circle cx="150" cy="128" r="5"/><circle cx="210" cy="70" r="5"/><circle cx="270" cy="92" r="5"/><circle cx="330" cy="40" r="5"/><circle cx="390" cy="60" r="5"/></g>
  <text x="470" y="166" font-size="13" fill="var(--dim)" text-anchor="end">Flat size</text>
  <text x="120" y="24" font-size="14" font-weight="600" fill="var(--bad)">Red gaps: the errors the line tries to shrink</text>
</svg>"""

PENALTY_PICTURE = """<svg viewBox="0 0 480 170" role="img" aria-label="Left: a diamond for Lasso, with the best point landing on a corner, so one weight is exactly zero. Right: a circle for Ridge, with the best point on the curve, so both weights shrink but neither reaches zero.">
  <g fill="var(--ink)" font-size="14" font-weight="600" text-anchor="middle"><text x="120" y="18">Lasso: a corner, so a weight hits 0</text><text x="360" y="18">Ridge: a curve, so weights just shrink</text></g>
  <path d="M30 100H210M120 30V165M270 100H450M360 30V165" stroke="var(--line-strong)" stroke-width="1.5"/>
  <path d="M120 58 162 100 120 142 78 100Z" fill="var(--a)" fill-opacity=".18" stroke="var(--a)" stroke-width="2.5"/>
  <circle cx="360" cy="100" r="42" fill="var(--a)" fill-opacity=".18" stroke="var(--a)" stroke-width="2.5"/>
  <circle cx="120" cy="58" r="7" fill="var(--bad)"/><circle cx="386" cy="67" r="7" fill="var(--bad)"/>
</svg>"""

SOFTMAX_PICTURE = """<svg viewBox="0 0 480 150" role="img" aria-label="Three scores, 2, 1 and minus 1, become probabilities of 71, 26 and 4 percent after softmax. They add up to 100 percent.">
  <g fill="var(--ink)" font-size="14" font-weight="600" text-anchor="middle"><text x="95" y="18">Scores (any number)</text><text x="370" y="18">Probabilities (add up to 100%)</text></g>
  <g font-size="15" fill="var(--ink)"><text x="10" y="52">Apple</text><text x="10" y="90">Orange</text><text x="10" y="128">Banana</text></g>
  <g fill="var(--a)" font-size="15" font-weight="600"><text x="80" y="52" fill="var(--ink)">2</text><text x="80" y="90" fill="var(--ink)">1</text><text x="80" y="128" fill="var(--ink)">−1</text></g>
  <path d="M140 84h60m-8-6 8 6-8 6" fill="none" stroke="var(--dim)" stroke-width="2"/>
  <text x="170" y="72" text-anchor="middle" font-size="13" fill="var(--dim)">softmax</text>
  <g fill="var(--a)"><rect x="225" y="36" width="170" height="22"/><rect x="225" y="74" width="62" height="22"/><rect x="225" y="112" width="9" height="22"/></g>
  <g font-size="15" font-weight="600" fill="var(--ink)"><text x="403" y="52">71%</text><text x="295" y="90">26%</text><text x="242" y="128">4%</text></g>
</svg>"""

TREE_PICTURE = """<svg viewBox="0 0 480 170" role="img" aria-label="A small decision tree. First question: credit score above 690? If no, be careful. If yes, a second question: income above 6 lakh? Yes means approve, no means be careful.">
  <g fill="var(--tint)" stroke="var(--c)" stroke-width="2"><rect x="150" y="6" width="180" height="40" rx="8"/><rect x="255" y="72" width="170" height="40" rx="8"/></g>
  <g stroke="var(--dim)" stroke-width="2" fill="none"><path d="M190 46 90 124M290 46 340 72M300 112 240 128M380 112 420 128"/></g>
  <g fill="none" stroke-width="2.5"><rect x="20" y="124" width="140" height="38" rx="19" stroke="var(--bad)"/><rect x="170" y="128" width="130" height="36" rx="18" stroke="var(--bad)"/><rect x="340" y="128" width="130" height="36" rx="18" stroke="var(--ok)"/></g>
  <g font-size="14" fill="var(--ink)" text-anchor="middle" font-weight="600"><text x="240" y="31">Credit score above 690?</text><text x="340" y="97">Income above 6 lakh?</text><text x="90" y="148">Be careful</text><text x="235" y="151">Be careful</text><text x="405" y="151">Approve</text></g>
  <g font-size="13" fill="var(--dim)"><text x="112" y="84">no</text><text x="334" y="54">yes</text><text x="230" y="119">no</text><text x="424" y="119">yes</text></g>
</svg>"""

FOREST_PICTURE = """<svg viewBox="0 0 480 170" role="img" aria-label="Three different trees built from different rows and features. Two vote yes and one votes no, and the forest's combined answer is yes.">
  <g fill="var(--tint)" stroke="var(--c)" stroke-width="2"><path d="M70 22 110 80H30Z"/><path d="M210 22 250 80H170Z"/><path d="M350 22 390 80H310Z"/></g>
  <g font-size="13" fill="var(--dim)" text-anchor="middle"><text x="70" y="14">Rows A, features 1, 3</text><text x="210" y="14">Rows B, features 2, 4</text><text x="350" y="14">Rows C, features 1, 4</text></g>
  <g font-size="15" font-weight="600" text-anchor="middle"><text x="70" y="104" fill="var(--ok)">Yes</text><text x="210" y="104" fill="var(--bad)">No</text><text x="350" y="104" fill="var(--ok)">Yes</text></g>
  <path d="M70 112 195 134M210 112V134M350 112 225 134" stroke="var(--dim)" stroke-width="2" fill="none"/>
  <rect x="130" y="136" width="160" height="30" rx="8" fill="var(--c)"/><text x="210" y="156" text-anchor="middle" font-size="14" font-weight="600" fill="#fff">Forest says: Yes</text>
</svg>"""

BOOST_PICTURE = """<svg viewBox="0 0 480 110" role="img" aria-label="A golf ball travels to a flag in shots that get smaller. Each shot corrects what is left from the one before.">
  <path d="M20 80H460" stroke="var(--line-strong)" stroke-width="2"/>
  <defs><marker id="arrowB" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0 10 5 0 10z" fill="var(--a)"/></marker></defs>
  <g stroke="var(--a)" stroke-width="3" fill="none" marker-end="url(#arrowB)"><path d="M30 68H240" marker-end="url(#arrowB)"/><path d="M246 68H350" marker-end="url(#arrowB)"/><path d="M356 68H405" marker-end="url(#arrowB)"/><path d="M411 68H432" marker-end="url(#arrowB)"/></g>
  <path d="M446 80V32" stroke="var(--ink)" stroke-width="2"/><path d="M446 32 468 41 446 50Z" fill="var(--bad)"/>
  <g font-size="13" fill="var(--ink)" text-anchor="middle" font-weight="600"><text x="135" y="58">First guess: the mean</text><text x="298" y="58">Tree 1</text><text x="380" y="58">Tree 2</text></g>
  <text x="240" y="102" text-anchor="middle" font-size="13" fill="var(--dim)">Each new tree only has to fix what's left</text>
</svg>"""

ML_PLANS = {
    "fundamentals/linear-regression": _plan(
        "You have 12 flats with their size and price, and you need to predict the price of a new one. You could draw endless lines through them. The interviewer asks:",
        "What is linear regression, and how is it fitted?",
        "Think of a stiff rod held by a spring to every data point. The further away a point is, the harder its spring pulls. The rod settles where the total pull balances out, and that's the least-squares line.",
        LINE_PICTURE, "Illustrative. Squaring the gaps means big misses count far more than small ones.",
        ("c6", "<b>Try to break it.</b> Drag the slope and intercept until the red squares are as small as you can get them. Then snap to the least-squares line.", "<b>Now say why:</b> why does a steeper slope need a lower intercept, and how close did you get to the best line?"),
        ["c2", "c5", "c7", "c8", "c9"], ["c4", "c12", "c13", "c16"], ["c3", "c10", "c11", "c14"], ["c15", "src"],
        ["It models the target as a weighted sum of features plus a bias.",
         "It fits the weights by minimising the sum of squared residuals.",
         "There's a closed form, the normal equation, or gradient descent at scale.",
         "The normal equation is a projection of y onto the span of the features.",
         "Under Gaussian noise, least squares is exactly maximum likelihood.",
         "Its weak spots are outliers, non-linearity and collinear features."],
        edits=[(" (chapter 10).", "."),
               ("matches the maths of Gaussian noise (chapter 8)", "matches the maths of Gaussian noise (see the Maths tab)"),
               ("why the next three chapters can find it reliably", "why the methods below can find it reliably"),
               ("features not too collinear (chapter 7 and the ", "features not too collinear (see the normal equation in the Maths tab, and the "),
               ("One bad row can move the line (chapter 9).", "One bad row can move the line (see the outlier lab in the Maths tab).")]),
    "fundamentals/regularized-linear-models": _plan(
        "With 22 flats and 10 features, your model says each extra bedroom makes a flat cheaper. The interviewer asks:",
        "What is the difference between Ridge and Lasso?",
        "Think of charging a model for its weights. Ridge charges more for bigger weights, so every weight shrinks but none disappears. Lasso charges the same for every unit, so small weights can't justify the cost and drop to exactly zero.",
        PENALTY_PICTURE, "Tibshirani's picture: the budget's shape decides whether the best point lands on a zero.",
        ("c9", "<b>Try to break it.</b> Choose Ridge and raise the strength, then do the same with Lasso. Watch how many features are kept, and how many junk ones survive.", "<b>Now say why:</b> why does Lasso reach exact zeros when Ridge never does?"),
        ["c2", "c5", "c6", "c7", "c8"], ["c4", "c10", "c11", "c15"], ["c3", "c13"], ["c12", "c14", "src"],
        ["Regularization adds a penalty on weight size, to cut variance and overfitting.",
         "Ridge uses L2: it shrinks all the weights smoothly, never to zero.",
         "Ridge handles collinearity because XᵀX + λI is always invertible.",
         "Lasso uses L1: its corners set some weights to exactly zero, so it selects features.",
         "Lasso arbitrarily keeps one of a correlated group. Elastic Net mixes the two.",
         "You standardise the features and tune λ by cross-validation."],
        edits=[("is the whole story of chapter 7", "is the whole story of the Lasso section"),
               ("This view gives the geometry in chapter 7.", "This view gives the geometry in the Lasso section."),
               ("That's why Ridge fixes chapter 1's problem.", "That's why Ridge fixes the sign flip from the start of this lesson."),
               ("Try it in the lab in chapter 9.", "Try it in the Play lab, in the Intuition tab.")]),
    "fundamentals/softmax-regression": _plan(
        "You're sorting fruit into apple, orange or banana. A teammate turns scores into probabilities by dividing each by the total, and then one score goes negative. The interviewer asks:",
        "What is softmax regression, and how is it trained?",
        "Think of a vote share. Each class gets a score, and raising e to that score makes it positive and widens the lead. Dividing by the total then gives shares that add up to 100%.",
        SOFTMAX_PICTURE, "Worked from the scores 2, 1 and −1. Percentages are rounded.",
        ("c6", "<b>Try to break it.</b> Add 3 to every logit. Then raise the temperature, and then lower it.", "<b>Now say why:</b> why does adding the same amount change nothing, and what does temperature really do?"),
        ["c2", "c5", "c7", "c8", "c9"], ["c4", "c10", "c11", "c12", "c15"], ["c3", "c13"], ["c14", "src"],
        ["It's multinomial logistic regression, with one weight vector and logit per class.",
         "Softmax exponentiates and normalises the logits into a distribution.",
         "It's trained by minimising cross-entropy.",
         "The gradient on the logits is predicted probabilities minus the one-hot label.",
         "It's convex, and it reduces to the sigmoid with two classes.",
         "It's the output layer of neural classifiers and LLMs."],
        edits=[("log-odds idea to K classes (chapter 9)", "log-odds idea to K classes"),
               ("weren't trained together (chapter 10)", "weren't trained together (see Softmax vs one-vs-rest below)"),
               ("nothing changes (chapter 7)", "nothing changes (the Maths tab shows why)"),
               ("Using the trained model from chapter 9.", "Using the trained model from the next section."),
               ("(the redundancy from chapter 7 in action)", "(the redundancy from the section above, in action)"),
               ("removes the redundancy from chapter 7)", "removes the redundancy in the logits)")]),
    "fundamentals/decision-trees": _plan(
        "A lender wants loan rules it can read, learned from 160 past borrowers. The interviewer asks:",
        "How does a decision tree choose its splits?",
        "Think of a game of twenty questions. Each yes-or-no question splits the group, and you always ask whichever question leaves each side the least mixed. Then you repeat on each side.",
        TREE_PICTURE, "Illustrative, based on the lesson's loan officer rules.",
        ("c6", "<b>Try to break it.</b> Move the threshold until the weighted Gini is as low as you can get it, then snap to the best split. Then switch to the other feature.", "<b>Now say why:</b> why does the algorithm prefer this threshold, and which feature would it choose first?"),
        ["c2", "c5", "c8", "c10"], ["c4", "c11", "c12", "c15"], ["c3", "c7", "c9", "c13"], ["c14", "src"],
        ["A tree recursively splits the data with yes-or-no questions on single features.",
         "At each node, it greedily picks the feature and threshold that most reduce impurity.",
         "Impurity is Gini or entropy for classification, and squared error for regression.",
         "Fully grown trees overfit, so you limit depth or leaf size, or prune.",
         "Trees are readable and need no scaling, but they're unstable and can't extrapolate."],
        edits=[("In the lab in chapter 6, training accuracy climbs", "In the lab below, training accuracy climbs")]),
    "fundamentals/random-forest": _plan(
        "Your deep decision tree changes completely when a single applicant is relabelled. The interviewer asks:",
        "How does a random forest improve on one deep tree?",
        "Think of asking a crowd for an estimate. A crowd only beats one person if people make different mistakes, because mistakes that differ cancel out. A forest makes its trees disagree: each one sees different rows, and each split sees only a few features.",
        FOREST_PICTURE, "Illustrative. Different rows and features make the trees disagree, and the combined answer is steadier.",
        ("c5", "<b>Try to break it.</b> Set the correlation between trees to 0.9 and add as many trees as you can. Then lower the correlation.", "<b>Now say why:</b> why can't more trees fix high correlation, and what does a forest do to lower it?"),
        ["c2", "c6", "c7", "c8", "c9", "c10"], ["c11", "c15"], ["c3", "c13"], ["c4", "c12", "c14", "src"],
        ["A forest averages many deep trees, which each have low bias and high variance.",
         "Averaging only reduces variance if the trees make different mistakes.",
         "Each tree trains on a bootstrap sample of the rows.",
         "Each split considers only a random subset of features, so a dominant feature can't make every tree the same.",
         "The rows a tree didn't see give a free out-of-bag error estimate.",
         "It reduces variance, not bias."],
        situation_chapters=["example", "c1"],
        edits=[("the widgets below run real computations", "the labs in this lesson run real computations"),
               ("what makes plain bagging fail in chapter 3.", "what makes plain bagging fail, as The answer that sounds right shows."),
               ("and chapter 7 shows his bound with both.", "and the random-features section shows his bound with both."),
               ("which gives a free test set (chapter 9).", "which gives a free test set (see the out-of-bag section)."),
               ("Same experiment as chapter 3, but now you choose m.", "Same experiment as the bagging lab in The answer that sounds right, but now you choose m."),
               ("The chapter 3 and 7 widgets show it on our data.", "The bagging and random-features labs show it on our data.")],
        strip=[r'<details class="deep"><summary>Go deeper: the same thing in scikit-learn</summary>.*?</details>\s*']),
    "fundamentals/gradient-boosting": _plan(
        "A shallow tree misses your rush-hour delays, and a deep tree memorises noise. A teammate suggests gradient boosting. The interviewer asks:",
        "How does gradient boosting work, and how does it differ from a random forest?",
        "Think of a round of golf. Your first shot gets you near the hole, and every shot after that only has to fix what's left. Boosting works the same way: each small tree corrects the remaining errors of everything before it.",
        BOOST_PICTURE, "Illustrative. In the model, each shot is a small tree fitted to the remaining errors.",
        ("c6", "<b>Try to break it.</b> Set the learning rate to 1.0 with depth 2, and add trees until you reach the end. Then try a learning rate of 0.1.", "<b>Now say why:</b> why does test error rise at full strength while training error keeps falling, and why does a smaller learning rate help?"),
        ["c2", "c5", "c7"], ["c4", "c8", "c9", "c10", "c12", "c15"], ["c3", "c13"], ["c11", "c14", "src"],
        ["Boosting builds an additive model of shallow trees, one after another.",
         "Each tree fits the negative gradient of the loss, which is the residual for squared error.",
         "It's gradient descent in function space, and it reduces bias step by step.",
         "A random forest instead averages independent deep trees, to reduce variance.",
         "It overfits with too many trees, so you use a small learning rate and early stopping.",
         "You can name the differences between XGBoost, LightGBM and CatBoost."],
        edits=[("In the lab in chapter 6, learning rate 1.0", "In the Play lab, in the Intuition tab, learning rate 1.0")]),
}

STREET_PICTURE = """<svg viewBox="0 0 480 170" role="img" aria-label="Two groups of points separated by a wide empty street. Only the points on the street's edges are ringed, because they alone decide where it goes.">
  <path d="M120 170 300 0H420L240 170Z" fill="var(--tint)"/>
  <path d="M180 170 360 0" stroke="var(--b)" stroke-width="3"/><path d="M120 170 300 0M240 170 420 0" stroke="var(--b)" stroke-width="1.5" stroke-dasharray="6 5"/>
  <g fill="var(--ok)"><circle cx="60" cy="40" r="6"/><circle cx="120" cy="70" r="6"/><circle cx="70" cy="110" r="6"/><circle cx="170" cy="30" r="6"/><circle cx="195" cy="100" r="6"/></g>
  <g fill="var(--bad)"><circle cx="400" cy="130" r="6"/><circle cx="440" cy="70" r="6"/><circle cx="340" cy="150" r="6"/><circle cx="330" cy="85" r="6"/></g>
  <g fill="none" stroke="var(--ink)" stroke-width="2"><circle cx="195" cy="100" r="11"/><circle cx="330" cy="85" r="11"/></g>
  <text x="476" y="166" font-size="14" font-weight="600" fill="var(--ink)" text-anchor="end">Ringed: support vectors</text>
</svg>"""

KNN_PICTURE = """<svg viewBox="0 0 480 170" role="img" aria-label="A new part in the centre with a circle around its five nearest neighbours. Three vote pass and two vote fail, so it's predicted as pass.">
  <circle cx="200" cy="85" r="72" fill="var(--tint)" stroke="var(--c)" stroke-width="2"/>
  <g fill="var(--ok)"><circle cx="160" cy="55" r="7"/><circle cx="170" cy="115" r="7"/><circle cx="235" cy="50" r="7"/><circle cx="60" cy="40" r="7"/><circle cx="75" cy="130" r="7"/></g>
  <g fill="var(--bad)"><circle cx="245" cy="110" r="7"/><circle cx="225" cy="130" r="7"/><circle cx="330" cy="50" r="7"/><circle cx="345" cy="130" r="7"/><circle cx="300" cy="150" r="7"/></g>
  <path d="M200 71 214 85 200 99 186 85Z" fill="var(--ink)"/>
  <g font-size="14" font-weight="600" fill="var(--ink)"><text x="372" y="72">k = 5</text><text x="372" y="94" fill="var(--ok)">3 say pass</text><text x="372" y="116" fill="var(--bad)">2 say fail</text></g>
</svg>"""

BAYES_NB_PICTURE = """<svg viewBox="0 0 480 130" role="img" aria-label="The words free, offer and meeting each multiply the spam score and the ham score separately, giving a 76 percent chance of spam.">
  <g font-size="14" font-weight="600" fill="var(--ink)"><text x="4" y="46">Spam</text><text x="4" y="94">Ham</text></g>
  <g font-size="13" fill="var(--ink)" text-anchor="middle"><text x="96" y="18" font-weight="600">Prior</text><text x="176" y="18" font-weight="600">"free"</text><text x="256" y="18" font-weight="600">"offer"</text><text x="336" y="18" font-weight="600">"meeting"</text>
    <text x="96" y="46">0.40</text><text x="136" y="46">×</text><text x="176" y="46">31/86</text><text x="216" y="46">×</text><text x="256" y="46">26/86</text><text x="296" y="46">×</text><text x="336" y="46">3/86</text>
    <text x="96" y="94">0.60</text><text x="136" y="94">×</text><text x="176" y="94">5/106</text><text x="216" y="94">×</text><text x="256" y="94">6/106</text><text x="296" y="94">×</text><text x="336" y="94">31/106</text></g>
  <rect x="382" y="28" width="94" height="74" rx="10" fill="var(--c)"/><text x="429" y="62" font-size="20" font-weight="700" fill="#fff" text-anchor="middle">76%</text><text x="429" y="84" font-size="13" fill="#fff" text-anchor="middle">spam</text>
</svg>"""

SHRINK_PICTURE = """<svg viewBox="0 0 480 110" role="img" aria-label="A scale of late rate. A pincode with 2 late orders out of 3 has a raw rate of 67 percent. Shrunk towards the 25 percent global rate, it becomes 30 percent.">
  <path d="M20 66H460" stroke="var(--line-strong)" stroke-width="3"/>
  <circle cx="130" cy="66" r="9" fill="var(--st)"/><circle cx="152" cy="66" r="9" fill="var(--ok)"/><circle cx="315" cy="66" r="9" fill="var(--bad)"/>
  <path d="M305 66H172" stroke="var(--dim)" stroke-width="2" stroke-dasharray="5 4"/>
  <g font-size="14" font-weight="600" text-anchor="middle"><text x="92" y="44" fill="var(--st)">Global 25%</text><text x="192" y="28" fill="var(--ok)">Shrunk 30%</text><text x="315" y="44" fill="var(--bad)">Raw 67% (2 of 3)</text></g>
  <path d="M170 34 155 54" stroke="var(--ok)" stroke-width="1.5"/>
  <g font-size="13" fill="var(--dim)"><text x="20" y="96">0%</text><text x="460" y="96" text-anchor="end">100% late</text></g>
</svg>"""

BLANK_PICTURE = """<svg viewBox="0 0 480 140" role="img" aria-label="A row with a blank prep time becomes a row with a guessed prep time and a new column flagging that it was missing.">
  <g font-size="13" font-weight="600" fill="var(--dim)" text-anchor="middle"><text x="50" y="18">Distance</text><text x="130" y="18">Prep time</text><text x="300" y="18">Distance</text><text x="380" y="18">Prep time</text><text x="448" y="18">Missing?</text></g>
  <g fill="none" stroke="var(--line-strong)" stroke-width="1.5"><rect x="10" y="28" width="160" height="40"/><path d="M90 28V68"/><rect x="260" y="28" width="216" height="40"/><path d="M340 28V68M420 28V68"/></g>
  <rect x="91" y="29" width="78" height="38" fill="var(--bad)" fill-opacity=".14"/><rect x="341" y="29" width="78" height="38" fill="var(--b)" fill-opacity=".16"/><rect x="421" y="29" width="54" height="38" fill="var(--ok)" fill-opacity=".16"/>
  <g font-size="15" fill="var(--ink)" text-anchor="middle"><text x="50" y="54">4 km</text><text x="130" y="54" fill="var(--bad)" font-weight="600">blank</text><text x="300" y="54">4 km</text><text x="380" y="54" font-weight="600">guess</text><text x="448" y="54" font-weight="600">yes</text></g>
  <path d="M186 48h56m-8-6 8 6-8 6" fill="none" stroke="var(--dim)" stroke-width="2"/>
  <text x="240" y="104" font-size="14" font-weight="600" fill="var(--ink)" text-anchor="middle">The guess fills the gap. The flag keeps the clue that it was blank.</text>
</svg>"""

NO_CODE = r"<pre[^>]*>.*?</pre>\s*"

ML_PLANS.update({
    "fundamentals/support-vector-machines": _plan(
        "Many lines separate your pass and fail parts perfectly, but a little sensor noise pushes parts over some of those lines. The interviewer asks:",
        "What does an SVM optimise, and what are support vectors?",
        "Think of laying the widest possible road between two groups of houses. Only the houses right at the road's edge decide where it can go. Move any other house, and the road doesn't change.",
        STREET_PICTURE, "Illustrative. The ringed points on the edges are the support vectors.",
        ("c9", "<b>Try to break it.</b> Push γ up to 100 and watch the boundary. Then bring it down to 0.1 and compare the test accuracy.", "<b>Now say why:</b> why does a huge γ score well on training parts but worse on new ones, and what happens to the support-vector count?"),
        ["c2", "c5", "c6", "c7", "c8"], ["c4", "c10", "c11", "c15"], ["c3", "c13"], ["c12", "c14", "src"],
        ["An SVM finds the separating hyperplane with the largest margin.",
         "Only the points on or inside the margin, the support vectors, determine the solution.",
         "The soft margin adds slack penalised by C, which equals hinge loss plus L2.",
         "Small C gives a wide, smooth margin, while large C fits the training points.",
         "The kernel trick gives non-linear boundaries without building the feature map.",
         "You scale features, tune C and γ together, and note training is quadratic to cubic in n."],
        strip=[NO_CODE]),
    "fundamentals/k-nearest-neighbours": _plan(
        "You want to automate an inspector who judges a new part by recalling similar ones. Your first version, with k = 1, scores 100% on training data. The interviewer asks:",
        "How does k-NN make a prediction, and what does k control?",
        "Think of judging a new part by polling the most similar parts you've seen. Ask just one, and an odd neighbour can mislead you. Ask too many, and you're polling parts that aren't similar at all.",
        KNN_PICTURE, "Illustrative. The answer can change with k, so you pick k by validation.",
        ("c6", "<b>Try to break it.</b> Start at k = 1, move to about 15, then push k as high as it goes. Watch the shading and the test accuracy.", "<b>Now say why:</b> why does accuracy on new parts rise and then fall, when training accuracy starts at 100%?"),
        ["c2", "c5", "c7", "c8", "c9"], ["c4", "c10", "c14"], ["c3", "c12"], ["c11", "c13", "src"],
        ["k-NN stores the training data and finds a new point's k nearest neighbours.",
         "It takes a majority vote, or the average for regression.",
         "There's no training, and the cost is at prediction time.",
         "k trades variance for bias and is chosen by cross-validation.",
         "It's distance-based, so you must scale features.",
         "In high dimensions, distances concentrate and neighbours mean less."],
        edits=[("more on that in chapter 8.", "more on that in the scaling section."),
               ("and the next chapters show how to set it.", "and the sections below show how to set it."),
               ("The next four chapters take those one at a time.", "The sections below take those one at a time."),
               ("Switch it on in the lab above.", "Switch it on in the Play lab, in the Intuition tab."),
               ("Cover &amp; Hart 1967, as in chapter 5.", "Cover &amp; Hart 1967, as in The core idea."),
               ("Beyer et al. 1999, as in chapter 9.", "Beyer et al. 1999, as in the curse of dimensionality section.")],
        strip=[NO_CODE]),
    "fundamentals/naive-bayes": _plan(
        "You're building a spam filter from 100 messages. Almost every message is unique, so you can't just count how often each whole message is spam. The interviewer asks:",
        "What is naive about naive Bayes?",
        "Think of a detective who treats every clue as if it were independent of the others. That's rarely true, because clues are often linked. But it makes the case easy to work through, and the detective usually names the right suspect, just with too much confidence.",
        BAYES_NB_PICTURE, "From the lesson's spam example, with Laplace smoothing.",
        ("c6", "<b>Try to break it.</b> Build a message with the word \"lunch\" in it, and set the smoothing as low as it goes. Then raise it.", "<b>Now say why:</b> why can one unseen word overrule everything else in the message?"),
        ["c2", "c5", "c7", "c9"], ["c4", "c10", "c11", "c15"], ["c3", "c8", "c13"], ["c12", "c14", "src"],
        ["It's a generative classifier built on Bayes' rule.",
         "It assumes features are conditionally independent given the class. That's the naive part.",
         "So the likelihood factorises into per-feature probabilities you get by counting.",
         "You smooth the counts, so unseen features don't give zero probability.",
         "You compute in log space, to avoid underflow.",
         "It double-counts correlated evidence, so its probabilities are overconfident."],
        edits=[("<h2>A text classifier in five lines</h2>", "<h2>A text classifier, step by step</h2>"),
               ("With Laplace smoothing (next chapter)", "With Laplace smoothing (try it in the Play lab)"),
               ("Illustrative simulation, chapter 8.", "Illustrative simulation, from the double-counting lab.")],
        strip=[NO_CODE]),
    "fundamentals/categorical-encoding": _plan(
        "Your model has a pincode column with 400 values. One-hot means 400 sparse columns, and replacing each pincode with its average late rate looks great in training but falls apart in test. The interviewer asks:",
        "How would you encode a categorical feature with 400 values?",
        "Think of replacing each pincode with its track record. A record from three orders means little, so you pull it towards the overall average. And a record that includes the very order you're predicting gives away the answer, so you compute it from other orders.",
        SHRINK_PICTURE, "Worked from the lesson's example of 2 late orders out of 3, with smoothing m = 20.",
        ("c6", "<b>Try to break it.</b> Choose naive encoding with low smoothing and read the test log loss. Then switch to cross-fitted.", "<b>Now say why:</b> why does the naive version look so useful to the model, yet do worse than ignoring pincode altogether?"),
        ["c2", "c5"], ["c4", "c7", "c8", "c9", "c13"], ["c3", "c11"], ["c10", "c12", "src"],
        ["The choice depends on cardinality and the model.",
         "For a few unordered categories, you one-hot encode and handle unknown values.",
         "For ordered categories, you use ordinal encoding in the real order.",
         "For many categories with linear models, you use target encoding shrunk towards the global mean.",
         "You compute it out-of-fold, so a row's own label never enters its feature.",
         "Everything sits in the pipeline, refitted within cross-validation."],
        edits=[("(Pargent et al. 2022, chapter 4)", "(Pargent et al. 2022)")],
        strip=[NO_CODE]),
    "fundamentals/missing-values-and-scaling": _plan(
        "Prep time is missing for a third of your orders, and it turns out slow kitchens stop reporting it. A teammate fills every gap with the mean. The interviewer asks:",
        "How do you handle missing values and feature scaling?",
        "Think of a form with a blank answer. You can pencil in a good guess, but the blank is a clue too: slow kitchens hide their times. So you fill the gap and keep a note that it was blank.",
        BLANK_PICTURE, "Illustrative. This is imputation plus a missing indicator.",
        ("c6", "<b>Try to break it.</b> Set the reason to slow kitchens hiding it (MNAR), and try mean fill. Then add the indicator, and try regression fill.", "<b>Now say why:</b> why does the indicator help more here than a smarter guess?"),
        ["c2", "c5", "c7"], ["c4", "c8", "c9", "c13"], ["c3", "c11"], ["c10", "c12", "src"],
        ["You first ask why values are missing: MCAR, MAR or MNAR.",
         "You impute with the median or a model that uses correlated features.",
         "You add a missing indicator when missingness may be informative.",
         "Distance- and penalty-based models need scaling, while trees don't.",
         "With outliers, you use a log transform or a robust scaler.",
         "You fit imputers and scalers on training data only, inside the pipeline."],
        tabs=["Intuition", "How it works", "In practice"],
        strip=[NO_CODE]),
})

CONFUSION_PICTURE = """<svg viewBox="0 0 480 170" role="img" aria-label="A confusion matrix. Precision reads across the flagged column, true positives out of everything flagged. Recall reads across the real positives row, true positives out of all real positives.">
  <g font-size="13" font-weight="600" fill="var(--dim)" text-anchor="middle"><text x="165" y="16">Flagged</text><text x="285" y="16">Not flagged</text></g>
  <g font-size="13" font-weight="600" fill="var(--dim)" text-anchor="end"><text x="98" y="58">Really fraud</text><text x="98" y="116">Really fine</text></g>
  <rect x="106" y="24" width="118" height="56" fill="var(--ok)" fill-opacity=".22" stroke="var(--ok)" stroke-width="2"/><rect x="226" y="24" width="118" height="56" fill="var(--bad)" fill-opacity=".12" stroke="var(--line-strong)"/>
  <rect x="106" y="82" width="118" height="56" fill="var(--bad)" fill-opacity=".12" stroke="var(--line-strong)"/><rect x="226" y="82" width="118" height="56" fill="none" stroke="var(--line-strong)"/>
  <g font-size="14" font-weight="600" fill="var(--ink)" text-anchor="middle"><text x="165" y="57">True positive</text><text x="285" y="57">Missed</text><text x="165" y="115">False alarm</text><text x="285" y="115">True negative</text></g>
  <g font-size="14" font-weight="600" fill="var(--ink)"><text x="354" y="50">Recall: how much</text><text x="354" y="68">real fraud caught?</text><text x="106" y="160">Precision: of the flagged, how many were real?</text></g>
</svg>"""

CURVES_PICTURE = """<svg viewBox="0 0 480 170" role="img" aria-label="Two small charts for the same model with rare positives. The ROC curve hugs the top left and looks excellent. The precision-recall curve falls away quickly and looks much weaker.">
  <g font-size="14" font-weight="600" fill="var(--ink)" text-anchor="middle"><text x="120" y="16">ROC: looks great</text><text x="360" y="16">PR: the honest top of the list</text></g>
  <path d="M40 26V146H200M280 26V146H440" fill="none" stroke="var(--dim)" stroke-width="1.5"/>
  <path d="M40 146 200 26" stroke="var(--line-strong)" stroke-dasharray="5 4"/>
  <path d="M40 146C46 60 70 34 200 26" fill="none" stroke="var(--a)" stroke-width="3"/>
  <path d="M280 40C310 60 330 118 440 138" fill="none" stroke="var(--b)" stroke-width="3"/>
  <g font-size="12" fill="var(--dim)" text-anchor="middle"><text x="120" y="164">False positive rate</text><text x="360" y="164">Recall</text></g>
</svg>"""

COST_PICTURE = """<svg viewBox="0 0 480 170" role="img" aria-label="A U-shaped curve of total cost against the threshold. The lowest cost sits well to the left of the usual 0.5 default.">
  <path d="M40 14V146H460" fill="none" stroke="var(--dim)" stroke-width="1.5"/>
  <path d="M46 96C80 150 110 150 150 118S300 34 450 26" fill="none" stroke="var(--b)" stroke-width="3"/>
  <circle cx="102" cy="136" r="7" fill="var(--ok)"/><path d="M250 74V146" stroke="var(--bad)" stroke-width="2" stroke-dasharray="5 4"/><circle cx="250" cy="66" r="7" fill="var(--bad)"/>
  <g font-size="14" font-weight="600"><text x="102" y="164" text-anchor="middle" fill="var(--ok)">Lowest cost</text><text x="262" y="96" fill="var(--bad)">The default 0.5</text></g>
  <g font-size="13" fill="var(--dim)"><text x="250" y="164" text-anchor="middle">Threshold</text><text x="16" y="84" text-anchor="middle" transform="rotate(-90 16 84)">Total cost</text></g>
</svg>"""

RMSE_PICTURE = """<svg viewBox="0 0 480 130" role="img" aria-label="On a normal day RMSE is 1.8 and MAE is 1.7 minutes. With two orders stuck in traffic, RMSE jumps to 17.1 while MAE only reaches 6.6.">
  <g font-size="14" font-weight="600" fill="var(--ink)"><text x="4" y="42">RMSE</text><text x="4" y="98">MAE</text></g>
  <g fill="var(--line-strong)"><rect x="60" y="20" width="36" height="16"/><rect x="60" y="76" width="34" height="16"/></g>
  <g fill="var(--bad)"><rect x="60" y="38" width="342" height="16"/><rect x="60" y="94" width="132" height="16"/></g>
  <g font-size="13" fill="var(--ink)"><text x="104" y="33">1.8 on a normal day</text><text x="102" y="89">1.7 on a normal day</text><text x="410" y="51" font-weight="600">17.1</text><text x="200" y="107" font-weight="600">6.6 with 2 stuck orders</text></g>
</svg>"""

RANK_PICTURE = """<svg viewBox="0 0 480 140" role="img" aria-label="Bars for result positions 1 to 5. Each position counts for less: 1, 0.63, 0.5, 0.43 and 0.39.">
  <text x="4" y="16" font-size="14" font-weight="600" fill="var(--ink)">How much each position counts in DCG</text>
  <g fill="var(--a)"><rect x="30" y="30" width="60" height="80"/><rect x="110" y="60" width="60" height="50"/><rect x="190" y="70" width="60" height="40"/><rect x="270" y="76" width="60" height="34"/><rect x="350" y="79" width="60" height="31"/></g>
  <g font-size="14" font-weight="600" fill="#fff" text-anchor="middle"><text x="60" y="76">1</text></g>
  <g font-size="14" font-weight="600" fill="var(--ink)" text-anchor="middle"><text x="140" y="54">0.63</text><text x="220" y="64">0.5</text><text x="300" y="70">0.43</text><text x="380" y="73">0.39</text></g>
  <g font-size="13" fill="var(--dim)" text-anchor="middle"><text x="60" y="128">1st</text><text x="140" y="128">2nd</text><text x="220" y="128">3rd</text><text x="300" y="128">4th</text><text x="380" y="128">5th</text></g>
</svg>"""

RELIABILITY_PICTURE = """<svg viewBox="0 0 480 170" role="img" aria-label="A reliability diagram. A dashed diagonal shows perfect calibration. An overconfident model's curve sits below it at high predictions and above it at low ones.">
  <path d="M90 14V146H330" fill="none" stroke="var(--dim)" stroke-width="1.5"/>
  <path d="M90 146 330 14" stroke="var(--ok)" stroke-width="2.5" stroke-dasharray="6 5"/>
  <path d="M90 118C160 104 170 86 210 80S300 62 330 42" fill="none" stroke="var(--bad)" stroke-width="3"/>
  <g font-size="14" font-weight="600"><text x="346" y="28" fill="var(--ok)">Perfectly calibrated</text><text x="346" y="60" fill="var(--bad)">Overconfident</text></g>
  <g font-size="13" fill="var(--dim)"><text x="210" y="164" text-anchor="middle">What the model says</text><text x="70" y="82" text-anchor="middle" transform="rotate(-90 70 82)">What really happens</text></g>
</svg>"""

LAYERS_PICTURE = """<svg viewBox="0 0 480 150" role="img" aria-label="Three layers. A model metric to iterate quickly, a business metric that must move, and guardrails that must not get worse.">
  <g stroke-width="2" fill="none"><rect x="6" y="6" width="468" height="40" rx="8" stroke="var(--a)"/><rect x="6" y="54" width="468" height="40" rx="8" stroke="var(--b)"/><rect x="6" y="102" width="468" height="40" rx="8" stroke="var(--bad)"/></g>
  <g font-size="14" fill="var(--ink)"><text x="20" y="31" font-weight="700">Model metric</text><text x="160" y="31">Fast and offline. It helps you choose models.</text><text x="20" y="79" font-weight="700">Business metric</text><text x="160" y="79">What must actually move.</text><text x="20" y="127" font-weight="700">Guardrails</text><text x="160" y="127">What must not get worse along the way.</text></g>
</svg>"""

ML_PLANS.update({
    "fundamentals/classification-metrics": _plan(
        "Your fraud model is 99.8% accurate, and your manager is unhappy. About 200 of every 100,000 transactions are fraud. The interviewer asks:",
        "Your fraud model is 99.8% accurate. Is it good?",
        "Think of a smoke alarm that never rings. It's right almost every day, and it's useless. Precision asks how many alarms were real fires. Recall asks how many fires set off the alarm.",
        CONFUSION_PICTURE, "Every metric in this lesson is built from these four counts.",
        ("c6", "<b>Try to break it.</b> On Fraud, slide the threshold down until recall is high, and watch precision. Then switch to Spam and do the same.", "<b>Now say why:</b> why does the same threshold move give such different precision on rare fraud and common spam?"),
        ["c2", "c5", "c7", "c8", "c9"], ["c4", "c10", "c11"], ["c3", "c12"], ["c13", "src"],
        ["You start from the confusion matrix.",
         "Accuracy misleads on imbalanced data, because the majority baseline already scores high.",
         "Precision is how many flagged items are right, and recall is how many real positives you catch.",
         "Which you prioritise depends on the costs: recall for screening, precision for spam.",
         "F1 balances them but ignores true negatives.",
         "Precision shifts with prevalence, and macro averaging helps when rare classes matter."],
        edits=[("The next chapters build each piece.", "The sections below build each piece.")]),
    "fundamentals/roc-auc-vs-pr-auc": _plan(
        "Model A gets 70% recall at 40% precision, and model B gets 60% at 55%. Your threshold could change next quarter, so you need a comparison that doesn't depend on it. The interviewer asks:",
        "When would you use PR-AUC instead of ROC-AUC?",
        "Think of ranking a huge pile of CVs. ROC-AUC asks how often a good CV ranks above a bad one, across the whole pile. PR-AUC asks how good the top of the pile is, which is all you'll actually read. When good CVs are rare, the two tell different stories.",
        CURVES_PICTURE, "Illustrative, for a model with rare positives.",
        ("c4", "<b>Try to break it.</b> Keep the model quality fixed and push the prevalence of positives down as far as it goes. Watch both scores.", "<b>Now say why:</b> why does one score hold steady while the other collapses?"),
        ["c2", "c5", "c6", "c7"], ["c8"], ["c3", "c9"], ["c10", "src"],
        ["ROC-AUC is the chance a random positive outscores a random negative.",
         "It's threshold-free and doesn't depend on class balance.",
         "PR-AUC summarises precision across recall, and its baseline is the prevalence.",
         "With heavy imbalance, ROC-AUC can look excellent while precision is poor.",
         "So you report PR-AUC plus precision at the operating point.",
         "Neither one measures calibration."],
        tabs=["Intuition", "Maths", "In practice"],
        edits=[("See it in the lab below:", "See it in the Play lab, in the Intuition tab:")]),
    "fundamentals/thresholds-and-costs": _plan(
        "Your code flags fraud at 0.5, which treats a missed ₹20,000 fraud and a ₹200 manual review as equally bad. The interviewer asks:",
        "How do you choose a classification threshold?",
        "Think of deciding when to call a doctor. A wasted visit costs a little, and a missed illness costs a lot, so you call even when you're only somewhat worried. A threshold works the same way: you act once acting is the cheaper bet.",
        COST_PICTURE, "Illustrative. When misses cost far more than false alarms, the best threshold sits well below 0.5.",
        ("c6", "<b>Try to break it.</b> On Fraud, drag the threshold until you find the lowest cost. Then switch to Spam and find it again.", "<b>Now say why:</b> why does the best threshold move so far between the two, even though neither model changed how it works?"),
        ["c2", "c5", "c7", "c8", "c9"], ["c4", "c10", "c11", "c12"], ["c3", "c13"], ["c14", "src"],
        ["The threshold is a business decision, not a model property.",
         "With calibrated probabilities and known costs, flag when p is at least C_FP ÷ (C_FP + C_FN).",
         "Without costs, you use a constraint like minimum recall, Youden's J or F-beta.",
         "For one summary on imbalanced data, MCC or balanced accuracy beat accuracy and F1.",
         "Class weighting in training is essentially threshold moving."]),
    "fundamentals/regression-metrics": _plan(
        "Two orders get stuck in traffic. Your ETA model's RMSE jumps ninefold, while its MAE barely moves. The interviewer asks:",
        "How do you choose between RMSE and MAE?",
        "Think of a restaurant's average bill. One huge party drags the mean up, but barely moves the median. RMSE behaves like the mean: a few huge misses dominate it. MAE behaves like the median.",
        RMSE_PICTURE, "From the lesson's ETA example, in minutes.",
        ("c5", "<b>Try to break it.</b> Slide the constant prediction and find where each metric is lowest.", "<b>Now say why:</b> why does each metric reward a different number, and what does that mean for what your model will learn to predict?"),
        ["c2", "c6", "c7", "c8", "c9"], ["c4", "c10"], ["c3", "c11"], ["c12", "src"],
        ["The metric decides what the model should predict.",
         "MSE and RMSE are minimised by the mean, and large errors dominate them.",
         "MAE is minimised by the median, and it's robust to outliers.",
         "Pinball loss targets a chosen quantile, for service levels or stocking.",
         "MAPE breaks near zero, so forecasting often uses WAPE or MASE.",
         "You report error in real units against a simple baseline."]),
    "fundamentals/ranking-metrics": _plan(
        "Two search engines return the same 10 products in a different order. Accuracy-style metrics score them the same, but users don't see them the same. The interviewer asks:",
        "Which metrics would you use to evaluate a ranked list?",
        "Think of a shop window. Items at the front get seen, and items at the back barely do. Ranking metrics give more credit for putting good items near the front, and they differ in how much.",
        RANK_PICTURE, "The standard log discount used in DCG, 1 ÷ log₂(position + 1).",
        ("c4", "<b>Try to break it.</b> Compare Engine A and Engine C at a cut-off of 10, then change the cut-off to 3. Then look at the ideal order.", "<b>Now say why:</b> why can two engines tie on one metric and differ on another?"),
        ["c2", "c5", "c6", "c7", "c8"], ["c9", "c10"], ["c3", "c11"], ["c12", "src"],
        ["Ranking metrics score an ordered list at a cut-off k.",
         "Precision@k and Recall@k ignore order within the top k.",
         "MRR looks at the position of the first relevant result.",
         "MAP averages precision at each relevant hit.",
         "NDCG uses graded relevance with a position discount, normalised by the ideal ranking.",
         "You validate online, keeping position bias in mind."],
        edits=[("In the lab below, engines A and C", "In the Play lab, in the Intuition tab, engines A and C")]),
    "fundamentals/probability-metrics": _plan(
        "Your ad model bids price = P(click) × value. It ranks ads perfectly, but it says 4% when the true rate is 2%, so every bid is double what it should be. The interviewer asks:",
        "How do you check whether a model's probabilities can be trusted?",
        "Think of a weather forecaster. When they say 70% chance of rain, it should rain on about 70% of those days. That's calibration. A forecaster can order days perfectly by rain risk and still get the chances wrong.",
        RELIABILITY_PICTURE, "Illustrative. A reliability diagram compares what a model says with what really happens.",
        ("c5", "<b>Try to break it.</b> Move the temperature away from 1 in both directions, and watch AUC, log-loss and the diagram. Then apply temperature scaling.", "<b>Now say why:</b> why can AUC stay put while the probabilities become badly wrong?"),
        ["c2", "c4", "c6", "c8"], ["c7", "c9"], ["c3", "c10"], ["c11", "src"],
        ["When decisions use the probability itself, you check calibration as well as ranking.",
         "AUC can't detect miscalibration, because it only depends on order.",
         "Log-loss and Brier are proper scoring rules that reward calibration and sharpness.",
         "A reliability diagram and ECE isolate calibration.",
         "Modern neural networks tend to be overconfident.",
         "Temperature scaling usually fixes that without changing accuracy."],
        edits=[("The lab in chapter 5 proves it:", "The Play lab, in the Intuition tab, proves it:")]),
    "fundamentals/choosing-the-right-metric": _plan(
        "A team raises their recommender's offline NDCG by 4% and ships it. Engagement goes up, but returns and refund complaints go up more. The interviewer asks:",
        "Which metric would you use?",
        "Think of a shop that rewards staff only for sales. Sales rise, and so do returns. Any metric becomes a target that gets chased, so start from how the output is used, and keep guardrails on what mustn't get worse.",
        LAYERS_PICTURE, "From the lesson's three layers.",
        ("c5", "<b>Try to break it.</b> Set a new model just slightly above the old one and shrink the test set. Then grow the test set until the difference looks real.", "<b>Now say why:</b> when can you trust that one model really is better?"),
        ["c2", "c4"], ["c6", "c7", "c8"], ["c3"], ["src"],
        ["You start from how the output is used: a decision, a ranking, a number or a probability.",
         "You ask which mistake is worse, and roughly by how much.",
         "That gives you the headline metric.",
         "You name the business metric it should move, and the guardrails.",
         "You compare with baselines, using intervals, then confirm with an A/B test."],
        tabs=["Intuition", "How it works", "In practice"]),
})

KMEANS_PICTURE = """<svg viewBox="0 0 480 160" role="img" aria-label="Three groups of customers, each with a marked centre in the middle of its group.">
  <g fill="var(--a)"><circle cx="70" cy="50" r="5"/><circle cx="100" cy="35" r="5"/><circle cx="60" cy="80" r="5"/><circle cx="110" cy="70" r="5"/><circle cx="85" cy="95" r="5"/></g>
  <g fill="var(--b)"><circle cx="240" cy="110" r="5"/><circle cx="275" cy="125" r="5"/><circle cx="215" cy="130" r="5"/><circle cx="260" cy="90" r="5"/><circle cx="290" cy="100" r="5"/></g>
  <g fill="var(--st)"><circle cx="370" cy="35" r="5"/><circle cx="410" cy="45" r="5"/><circle cx="385" cy="70" r="5"/><circle cx="430" cy="75" r="5"/><circle cx="350" cy="60" r="5"/></g>
  <g stroke="var(--ink)" stroke-width="3.5"><path d="M78 56 94 72M94 56 78 72M246 102 262 118M262 102 246 118M382 46 398 62M398 46 382 62"/></g>
  <text x="240" y="154" font-size="14" font-weight="600" fill="var(--ink)" text-anchor="middle">Each × sits at the average of its own customers</text>
</svg>"""

DENDRO_PICTURE = """<svg viewBox="0 0 480 160" role="img" aria-label="A tree of merges over six customers. A dashed cut across the tree gives two clusters, and a lower cut would give more.">
  <g fill="none" stroke="var(--a)" stroke-width="2.5"><path d="M60 130V100H110V130M85 100V60H160V130M250 130V110H300V130M275 110V76H350V130M122 60V28H312V76"/></g>
  <g fill="var(--ink)" font-size="13" text-anchor="middle"><text x="60" y="148">A</text><text x="110" y="148">B</text><text x="160" y="148">C</text><text x="250" y="148">D</text><text x="300" y="148">E</text><text x="350" y="148">F</text></g>
  <path d="M30 46H476" stroke="var(--bad)" stroke-width="2" stroke-dasharray="6 5"/>
  <text x="476" y="36" font-size="13" font-weight="600" fill="var(--bad)" text-anchor="end">Cut: 2 groups</text>
</svg>"""

MOONS_PICTURE = """<svg viewBox="0 0 480 160" role="img" aria-label="Two curved roads of dense points wrap around each other. A few scattered grey points don't belong to either and are marked as noise.">
  <path d="M60 90C90 15 230 15 260 90" fill="none" stroke="var(--a)" stroke-width="13" stroke-linecap="round" stroke-dasharray="1 15"/>
  <path d="M170 60C200 135 340 135 370 60" fill="none" stroke="var(--b)" stroke-width="13" stroke-linecap="round" stroke-dasharray="1 15"/>
  <g fill="var(--dim)"><circle cx="50" cy="35" r="4"/><circle cx="330" cy="40" r="4"/><circle cx="120" cy="140" r="4"/><circle cx="430" cy="130" r="4"/></g>
  <text x="440" y="124" font-size="13" font-weight="600" fill="var(--dim)" text-anchor="end">noise</text>
</svg>"""

GMM_PICTURE = """<svg viewBox="0 0 480 160" role="img" aria-label="Two tilted overlapping ellipses. A customer in the overlap belongs 62 percent to one and 38 percent to the other.">
  <ellipse cx="170" cy="85" rx="100" ry="34" transform="rotate(-30 170 85)" fill="var(--a)" fill-opacity=".16" stroke="var(--a)" stroke-width="2.5"/>
  <ellipse cx="245" cy="85" rx="100" ry="34" transform="rotate(-30 245 85)" fill="var(--b)" fill-opacity=".14" stroke="var(--b)" stroke-width="2.5"/>
  <circle cx="208" cy="85" r="7" fill="var(--ink)"/>
  <path d="M216 85H352" stroke="var(--dim)" stroke-width="1.5"/>
  <g font-size="14" font-weight="600"><text x="358" y="72" fill="var(--a)">62% segment 1</text><text x="358" y="96" fill="var(--b)">38% segment 2</text></g>
</svg>"""

PCA_PICTURE = """<svg viewBox="0 0 480 170" role="img" aria-label="A long tilted cloud of points. A long arrow along it is the first component, and a short arrow across it is the second.">
  <defs><marker id="arrowP" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0 10 5 0 10z" fill="context-stroke"/></marker></defs>
  <g fill="var(--line-strong)"><circle cx="90" cy="140" r="4"/><circle cx="120" cy="115" r="4"/><circle cx="145" cy="125" r="4"/><circle cx="165" cy="95" r="4"/><circle cx="190" cy="105" r="4"/><circle cx="205" cy="75" r="4"/><circle cx="235" cy="85" r="4"/><circle cx="250" cy="55" r="4"/><circle cx="280" cy="60" r="4"/><circle cx="295" cy="35" r="4"/><circle cx="325" cy="40" r="4"/></g>
  <line x1="205" y1="88" x2="330" y2="22" stroke="var(--a)" stroke-width="3.5" marker-end="url(#arrowP)"/>
  <line x1="205" y1="88" x2="224" y2="124" stroke="var(--b)" stroke-width="3.5" marker-end="url(#arrowP)"/>
  <g font-size="14" font-weight="600"><text x="340" y="24" fill="var(--a)">PC1: most spread</text><text x="232" y="136" fill="var(--b)">PC2: what's left</text></g>
</svg>"""

TSNE_PICTURE = """<svg viewBox="0 0 480 160" role="img" aria-label="Left, the true data: one tight group and one much wider group. Right, the 2-D map: the two groups look about the same size.">
  <g font-size="14" font-weight="600" fill="var(--ink)" text-anchor="middle"><text x="120" y="18">True data: very different sizes</text><text x="365" y="18">Map: sizes look alike</text></g>
  <circle cx="70" cy="90" r="16" fill="var(--a)" fill-opacity=".3" stroke="var(--a)" stroke-width="2"/><circle cx="170" cy="90" r="50" fill="var(--b)" fill-opacity=".2" stroke="var(--b)" stroke-width="2"/>
  <path d="M232 90h30m-8-6 8 6-8 6" fill="none" stroke="var(--dim)" stroke-width="2"/>
  <circle cx="320" cy="90" r="30" fill="var(--a)" fill-opacity=".3" stroke="var(--a)" stroke-width="2"/><circle cx="415" cy="90" r="32" fill="var(--b)" fill-opacity=".2" stroke="var(--b)" stroke-width="2"/>
  <g font-size="14" font-weight="600" text-anchor="middle" fill="var(--ink)"><text x="70" y="95">A</text><text x="170" y="95">B</text><text x="320" y="95">A</text><text x="415" y="95">B</text></g>
</svg>"""

ISOLATE_PICTURE = """<svg viewBox="0 0 480 160" role="img" aria-label="A dense cloud of normal orders and one far-off point. Two random cuts are enough to isolate the far-off point, while points in the cloud would need many more.">
  <rect x="8" y="8" width="464" height="144" fill="none" stroke="var(--line-strong)" stroke-width="1.5"/>
  <g fill="var(--a)"><circle cx="120" cy="90" r="4"/><circle cx="140" cy="70" r="4"/><circle cx="160" cy="95" r="4"/><circle cx="110" cy="65" r="4"/><circle cx="175" cy="75" r="4"/><circle cx="135" cy="110" r="4"/><circle cx="95" cy="90" r="4"/><circle cx="155" cy="55" r="4"/><circle cx="185" cy="105" r="4"/></g>
  <circle cx="400" cy="40" r="8" fill="var(--bad)"/>
  <path d="M320 8V152M320 90H472" stroke="var(--b)" stroke-width="2.5" stroke-dasharray="7 5"/>
  <g font-size="14" font-weight="600"><text x="330" y="120" fill="var(--b)">2 random cuts</text><text x="330" y="140" fill="var(--bad)">and it's alone</text><text x="60" y="140" fill="var(--a)">Normal orders need many</text></g>
</svg>"""

ML_PLANS.update({
    "fundamentals/k-means": _plan(
        "Marketing wants three campaigns, one per kind of customer, but no column says which kind each customer is. The interviewer asks:",
        "How does k-means work, and does it always find the best clustering?",
        "Think of opening three shops in a town. Each customer goes to their nearest shop. Then each shop moves to the middle of its customers. Customers re-choose, shops move again, and you repeat until nothing changes.",
        KMEANS_PICTURE, "Illustrative. The assign and move steps repeat until the groups stop changing.",
        ("c6", "<b>Try to break it.</b> Run start A until no points switch, and note the inertia. Then reset and run starts B and C.", "<b>Now say why:</b> why doesn't every start reach the same answer, and how would you protect against a bad one?"),
        ["c2", "c5", "c7", "c8"], ["c4", "c10", "c14"], ["c3", "c9", "c12"], ["c11", "c13", "src"],
        ["k-means minimises the within-cluster sum of squared distances to the centroids.",
         "It alternates two steps: assign to the nearest centroid, then move each centroid to the mean.",
         "Each step can only lower the objective, so it converges, but to a local minimum.",
         "So you use k-means++ seeding and multiple restarts.",
         "You choose k with the elbow, silhouette or domain needs.",
         "It assumes round, similar-sized clusters and needs scaled features."],
        strip=[NO_CODE]),
    "fundamentals/hierarchical-clustering": _plan(
        "Marketing sees three customer segments today, but one might split into weekday and weekend users. You don't want to commit to one number of groups. The interviewer asks:",
        "How does hierarchical clustering work, and how do you pick the number of clusters?",
        "Think of building a family tree from the bottom up. Everyone starts alone, then the closest pairs join, then the closest groups, until one family remains. Cut the tree at any height, and you get that many groups.",
        DENDRO_PICTURE, "Illustrative. Higher joins mean the groups were further apart.",
        ("c6", "<b>Try to break it.</b> Move the cut height up and down and watch the cluster count. Then switch from Ward to single linkage.", "<b>Now say why:</b> why does the same data give such a different tree under single linkage?"),
        ["c2", "c5", "c7"], ["c4", "c8", "c9", "c13"], ["c3", "c11"], ["c10", "c12", "src"],
        ["It starts with every point alone and repeatedly merges the two closest clusters.",
         "Each merge height is recorded in a dendrogram.",
         "You cut the tree, usually at a large gap, so you don't fix k in advance.",
         "The linkage defines cluster distance: single, complete, average or Ward.",
         "It's deterministic, but needs O(n²) memory and up to O(n³) time."],
        edits=[("is the linkage choice (chapter 6)", "is the linkage choice (see below)")],
        strip=[NO_CODE]),
    "fundamentals/dbscan": _plan(
        "Your deliveries follow curved roads, and stray GPS pings land everywhere. k-means cuts straight across both roads. The interviewer asks:",
        "How does DBSCAN find clusters, and what is its main weakness?",
        "Think of finding crowds at a fair. Wherever people stand packed together, you can walk from person to person and stay in the same crowd. Someone standing alone belongs to no crowd at all.",
        MOONS_PICTURE, "Illustrative, based on the lesson's two roads and stray GPS pings.",
        ("c6", "<b>Try to break it.</b> Try eps at 0.25, 0.30 and 0.35. Watch how many clusters it finds and how many points become noise.", "<b>Now say why:</b> why does such a small change in eps swing the result from fragments, to two roads, to one blob?"),
        ["c2", "c5", "c7"], ["c4", "c9", "c10", "c14"], ["c3", "c8", "c12"], ["c11", "c13", "src"],
        ["A core point has at least min_samples neighbours within radius eps.",
         "Clusters are core points reachable through eps-hops, plus nearby border points.",
         "Everything else is noise.",
         "It finds any shape, infers the number of clusters and flags outliers.",
         "Results are very sensitive to eps, which you pick from a k-distance plot.",
         "One global density fails when densities vary, and HDBSCAN fixes that."],
        strip=[NO_CODE]),
    "fundamentals/gaussian-mixture-models": _plan(
        "Your customer segments are tilted and overlap, and k-means slices across them. Marketing also wants to know that a customer is 62% one segment, not just assigned to one. The interviewer asks:",
        "What is a Gaussian mixture model, and how is it fitted?",
        "Think of sorting customers in pencil instead of pen: 62% this segment, 38% that one. Then each segment redraws its shape using those partial votes. Re-score everyone, redraw again, and repeat until it settles.",
        GMM_PICTURE, "Illustrative. The percentages are each customer's responsibilities.",
        ("c6", "<b>Try to break it.</b> Move through the EM iterations from the start. Watch the ellipses tilt, the log-likelihood rise and the uncertain customers change.", "<b>Now say why:</b> why can the likelihood never fall between iterations, and why might this still not be the best fit overall?"),
        ["c2", "c5", "c8"], ["c4", "c7", "c9", "c10", "c14"], ["c3", "c12"], ["c11", "c13", "src"],
        ["It models data as a weighted sum of k Gaussians, each with its own mean and covariance.",
         "It's fitted with EM.",
         "The E-step computes each point's responsibility for each component.",
         "The M-step re-estimates the weights, means and covariances.",
         "The likelihood never decreases, so it converges to a local optimum.",
         "You choose k with BIC, and it handles tilted clusters with soft assignments."],
        strip=[NO_CODE]),
    "fundamentals/pca": _plan(
        "You have ten customer columns, and most of them move together. Feeding them all into a model counts the same idea several times. The interviewer asks:",
        "What does PCA do, and what are the principal components?",
        "Think of photographing a long, thin object. From most angles it looks small, but one angle shows it at full length. PCA finds that angle for your data: the direction with the most spread, then the next-best one at a right angle to it.",
        PCA_PICTURE, "Illustrative. Keeping only PC1 here would keep most of the spread.",
        ("c6", "<b>Try to break it.</b> Keep just one component and read the variance kept. Then add components one at a time until the gain gets small.", "<b>Now say why:</b> why do the first two components capture so much here, and where would you stop?"),
        ["c2", "c5", "c7"], ["c4", "c10", "c14"], ["c3", "c8", "c9", "c12"], ["c11", "c13", "src"],
        ["PCA finds orthogonal directions that capture the most variance.",
         "Each component maximises the remaining variance, orthogonal to the earlier ones.",
         "They're the eigenvectors of the covariance matrix, and eigenvalues are the variance captured.",
         "It's computed in practice by SVD of the centred data.",
         "You pick k from cumulative variance, and standardise features first.",
         "It's linear and unsupervised, so it can miss curves and useful low-variance directions."],
        edits=[("which says nothing about customers (chapter 8)", "which says nothing about customers (see the scaling lab)")],
        strip=[NO_CODE]),
    "fundamentals/t-sne-and-umap": _plan(
        "You've trained customer embeddings and made a 2-D plot. A teammate points at the gaps and sizes of the clusters and draws conclusions from them. The interviewer asks:",
        "How does t-SNE build its 2-D map?",
        "Think of arranging people on a floor so that friends stand together. You'll keep the friend groups intact, but how big each group looks, and how far apart the groups stand, means very little.",
        TSNE_PICTURE, "Illustrative, based on the lesson's groups A and B. Maps keep neighbours, not sizes.",
        ("c6", "<b>Try to break it.</b> Run perplexity from 2 up to 50, then change the seed. Compare the size and distance readouts with their true values.", "<b>Now say why:</b> if the picture changes this much, what can you safely conclude from it?"),
        ["c2", "c5", "c8"], ["c4", "c9", "c10", "c14"], ["c3", "c7", "c12"], ["c11", "c13", "src"],
        ["t-SNE turns high-dimensional distances into neighbour probabilities, with a width set by perplexity.",
         "It finds 2-D positions with matching similarities, using a heavy-tailed Student-t.",
         "It minimises KL divergence with gradient descent.",
         "The heavy tail solves the crowding problem.",
         "It keeps local neighbourhoods, not cluster sizes or distances between clusters.",
         "UMAP builds a neighbour graph, is much faster and has the same reading caveats."],
        strip=[NO_CODE]),
    "fundamentals/anomaly-detection": _plan(
        "Fraud patterns keep changing, glitches are new every time, and you have almost no labelled examples. A normal classifier has nothing to learn from. The interviewer asks:",
        "How would you detect anomalies without labels?",
        "Think of playing twenty questions to single out one person in a crowd. Someone in a strange costume takes only a few questions, while someone ordinary takes many. Isolation Forest counts those questions, and fewer means more unusual.",
        ISOLATE_PICTURE, "Illustrative. Short average paths across many random trees mean a high anomaly score.",
        ("c5", "<b>Try to break it.</b> Isolate the anomaly and count the splits. Then isolate a normal order and compare.", "<b>Now say why:</b> why do random splits find unusual points so quickly, with no labels at all?"),
        ["c2", "c6", "c9"], ["c4", "c8", "c10", "c14"], ["c3", "c7", "c12"], ["c11", "c13", "src"],
        ["Anomaly detection scores how unusual each point is, usually without labels.",
         "Isolation Forest isolates anomalies in few random splits, so short paths mean high scores.",
         "LOF compares a point's local density with its neighbours'.",
         "One-Class SVM learns a boundary around clean data, for novelty detection.",
         "Mahalanobis-style scores assume a single Gaussian blob.",
         "The threshold comes from review capacity or costs, and evaluation needs some labels."],
        tabs=["Intuition", "How it works", "In practice"],
        edits=[("none of its top 10 flags are real anomalies (chapter 7)", "none of its top 10 flags are real anomalies (see the lab below)")],
        strip=[NO_CODE]),
})

TARGET_PICTURE = """<svg viewBox="0 0 480 160" role="img" aria-label="Two archery targets. On the left, arrows cluster tightly but away from the centre, which is high bias. On the right, arrows scatter widely around the centre, which is high variance.">
  <g fill="none" stroke="var(--line-strong)" stroke-width="2"><circle cx="120" cy="80" r="56"/><circle cx="120" cy="80" r="34"/><circle cx="120" cy="80" r="12"/><circle cx="360" cy="80" r="56"/><circle cx="360" cy="80" r="34"/><circle cx="360" cy="80" r="12"/></g>
  <g fill="var(--bad)"><circle cx="150" cy="50" r="5"/><circle cx="158" cy="60" r="5"/><circle cx="142" cy="60" r="5"/><circle cx="152" cy="42" r="5"/><circle cx="163" cy="48" r="5"/></g>
  <g fill="var(--st)"><circle cx="322" cy="52" r="5"/><circle cx="398" cy="60" r="5"/><circle cx="372" cy="118" r="5"/><circle cx="336" cy="104" r="5"/><circle cx="390" cy="36" r="5"/></g>
  <g font-size="14" font-weight="600" text-anchor="middle"><text x="120" y="154" fill="var(--bad)">High bias: wrong the same way</text><text x="360" y="154" fill="var(--st)">High variance: all over the place</text></g>
</svg>"""

FOLDS_PICTURE = """<svg viewBox="0 0 480 150" role="img" aria-label="Five rows of five blocks. In each row, a different block is held out for validation while the other four train the model.">
  <g fill="var(--a)" fill-opacity=".2" stroke="var(--a)">
    <rect x="130" y="34" width="66" height="18"/><rect x="198" y="34" width="66" height="18"/><rect x="266" y="34" width="66" height="18"/><rect x="334" y="34" width="66" height="18"/>
    <rect x="62" y="56" width="66" height="18"/><rect x="198" y="56" width="66" height="18"/><rect x="266" y="56" width="66" height="18"/><rect x="334" y="56" width="66" height="18"/>
    <rect x="62" y="78" width="66" height="18"/><rect x="130" y="78" width="66" height="18"/><rect x="266" y="78" width="66" height="18"/><rect x="334" y="78" width="66" height="18"/>
    <rect x="62" y="100" width="66" height="18"/><rect x="130" y="100" width="66" height="18"/><rect x="198" y="100" width="66" height="18"/><rect x="334" y="100" width="66" height="18"/>
    <rect x="62" y="122" width="66" height="18"/><rect x="130" y="122" width="66" height="18"/><rect x="198" y="122" width="66" height="18"/><rect x="266" y="122" width="66" height="18"/>
  </g>
  <g fill="var(--b)"><rect x="62" y="34" width="66" height="18"/><rect x="130" y="56" width="66" height="18"/><rect x="198" y="78" width="66" height="18"/><rect x="266" y="100" width="66" height="18"/><rect x="334" y="122" width="66" height="18"/></g>
  <g font-size="14" font-weight="600"><text x="62" y="20" fill="var(--b)">Held out</text><text x="150" y="20" fill="var(--a)">Everything else trains</text></g>
</svg>"""

RANK_CUT_PICTURE = """<svg viewBox="0 0 480 130" role="img" aria-label="Orders ranked from low risk to high risk. The default cut at 0.5 catches almost nothing. A much lower cut catches far more of the rare fraud.">
  <path d="M20 66H460" stroke="var(--line-strong)" stroke-width="3"/>
  <g fill="var(--a)"><circle cx="40" cy="66" r="5"/><circle cx="66" cy="66" r="5"/><circle cx="92" cy="66" r="5"/><circle cx="118" cy="66" r="5"/><circle cx="144" cy="66" r="5"/><circle cx="170" cy="66" r="5"/><circle cx="196" cy="66" r="5"/><circle cx="240" cy="66" r="5"/></g>
  <g fill="var(--bad)"><circle cx="218" cy="66" r="5"/><circle cx="268" cy="66" r="5"/><circle cx="312" cy="66" r="5"/><circle cx="420" cy="66" r="5"/></g>
  <path d="M206 36V96" stroke="var(--ok)" stroke-width="2.5"/><path d="M370 36V96" stroke="var(--dim)" stroke-width="2.5" stroke-dasharray="5 4"/>
  <g font-size="14" font-weight="600"><text x="206" y="28" fill="var(--ok)" text-anchor="middle">A cut chosen from costs</text><text x="370" y="114" fill="var(--dim)" text-anchor="middle">Default 0.5</text><text x="20" y="114" fill="var(--a)">Legit</text><text x="66" y="114" fill="var(--bad)">Fraud</text></g>
</svg>"""

SEARCH_PICTURE = """<svg viewBox="0 0 480 170" role="img" aria-label="Left, a grid of nine trials that tests only three distinct values of each setting. Right, nine random trials that test nine distinct values.">
  <g font-size="14" font-weight="600" fill="var(--ink)" text-anchor="middle"><text x="120" y="16">Grid: 9 trials, 3 values each</text><text x="360" y="16">Random: 9 trials, 9 values each</text></g>
  <path d="M40 26V146H200M280 26V146H440" fill="none" stroke="var(--dim)" stroke-width="1.5"/>
  <g fill="var(--a)"><circle cx="75" cy="55" r="5"/><circle cx="120" cy="55" r="5"/><circle cx="165" cy="55" r="5"/><circle cx="75" cy="85" r="5"/><circle cx="120" cy="85" r="5"/><circle cx="165" cy="85" r="5"/><circle cx="75" cy="115" r="5"/><circle cx="120" cy="115" r="5"/><circle cx="165" cy="115" r="5"/></g>
  <g fill="var(--b)"><circle cx="298" cy="72" r="5"/><circle cx="316" cy="118" r="5"/><circle cx="330" cy="46" r="5"/><circle cx="348" cy="98" r="5"/><circle cx="362" cy="62" r="5"/><circle cx="380" cy="128" r="5"/><circle cx="396" cy="84" r="5"/><circle cx="412" cy="40" r="5"/><circle cx="428" cy="108" r="5"/></g>
  <g font-size="12" fill="var(--dim)" text-anchor="middle"><text x="120" y="164">The setting that matters</text><text x="360" y="164">The setting that matters</text></g>
</svg>"""

FORECAST_PICTURE = """<svg viewBox="0 0 480 160" role="img" aria-label="Daily orders over time with a weekly wave. A vertical line marks today. A model trains only on the past to the left and is tested on the future to the right.">
  <path d="M30 14V136H470" fill="none" stroke="var(--dim)" stroke-width="1.5"/>
  <path d="M30 104 50 88 70 112 90 82 110 106 130 76 150 100 170 70 190 94 210 64 230 88 250 58 270 82 290 52 310 76" fill="none" stroke="var(--a)" stroke-width="2.5"/>
  <path d="M310 76 330 46 350 70 370 40 390 64 410 34 430 58 450 28" fill="none" stroke="var(--b)" stroke-width="2.5" stroke-dasharray="6 4"/>
  <path d="M310 14V136" stroke="var(--ink)" stroke-width="2"/>
  <g font-size="14" font-weight="600"><text x="160" y="154" fill="var(--a)" text-anchor="middle">Train on the past</text><text x="390" y="154" fill="var(--b)" text-anchor="middle">Test on the future</text><text x="304" y="26" fill="var(--ink)" text-anchor="end">Today</text></g>
</svg>"""

ML_PLANS.update({
    "fundamentals/bias-variance": _plan(
        "A straight-line model misses your delivery curve the same way every time. A degree-15 model fits its training data, but gives a completely different wiggle on each new sample. The interviewer asks:",
        "What is the bias–variance trade-off?",
        "Think of archery. Bias is every arrow landing together in the wrong spot. Variance is arrows scattered all over the target. Making a model more flexible usually trades the first problem for the second.",
        TARGET_PICTURE, "Illustrative. Test error adds these two to noise you can't remove.",
        ("c5", "<b>Try to break it.</b> Start at degree 1 and move up to the highest degree. Watch the thin lines, and read bias² and variance at each step.", "<b>Now say why:</b> why does total test error fall and then rise, even though training error keeps falling?"),
        ["c2", "c6", "c7", "c8", "c9"], ["c4", "c10", "c14"], ["c3", "c12"], ["c11", "c13", "src"],
        ["For squared error, expected test error is bias², variance and irreducible noise.",
         "Bias is the error of the average model: too simple misses the pattern.",
         "Variance is how much the model changes with the sample: too flexible fits noise.",
         "Test error is U-shaped, so you pick complexity with validation data.",
         "High bias shows as high train and validation error. High variance shows as a large gap.",
         "You fix bias with capacity, and variance with data, regularisation or bagging."],
        strip=[NO_CODE]),
    "fundamentals/cross-validation-and-leakage": _plan(
        "Your cross-validation says 0.92 AUC, and production says 0.70. Nothing in the code threw an error. The interviewer asks:",
        "What is data leakage, and how does cross-validation help you avoid it?",
        "Think of a practice exam where you've already seen the answer key. You'll score brilliantly, and the score tells you nothing. Leakage is any way the answers reach your model before it's tested, and it often looks like good hygiene.",
        FOLDS_PICTURE, "5-fold cross-validation: each block gets one turn being held out.",
        ("c6", "<b>Try to break it.</b> Select features on all the rows, then cross-validate, and read the accuracy. The labels here are random, so the truth is 50%. Then select inside each fold.", "<b>Now say why:</b> how did pure noise score so well, when no line of code looks wrong?"),
        ["c2", "c5", "c9"], ["c4", "c10", "c14"], ["c3", "c7", "c8", "c12"], ["c11", "c13", "src"],
        ["Cross-validation rotates held-out folds and averages the scores, with a test set used once at the end.",
         "The split must mirror production: stratified, grouped or time-based.",
         "Leakage is information at training time that wouldn't exist at prediction time.",
         "Common forms are preprocessing on all rows, tuning on the test set and related rows on both sides.",
         "You put every learned step in a pipeline, refitted inside each fold.",
         "You use nested CV when tuning."],
        edits=[("Inner loop tunes, outer loop scores (chapter 9)", "Inner loop tunes, outer loop scores (see the Maths tab)"),
               ("the score is optimistic (chapter 7, in a milder form)", "the score is optimistic (the same leak as tuning on test, in a milder form)")],
        strip=[NO_CODE]),
    "fundamentals/class-imbalance": _plan(
        "About 2% of your orders are fraud, and the default threshold flags almost nothing. A teammate wants to balance the classes to 50/50. The interviewer asks:",
        "How do you handle a 2% positive class?",
        "Think of airport security. Very few bags are dangerous, but you don't pretend half of them are. You keep an honest risk score for every bag, then decide how risky a bag must be to open, based on what a miss and a search each cost.",
        RANK_CUT_PICTURE, "Illustrative. Ranking orders and deciding where to cut are two separate jobs.",
        ("c7", "<b>Try to break it.</b> Start at a threshold of 0.5 and read the recall and the cost. Then slide it down until the cost is as low as you can get.", "<b>Now say why:</b> why did this help so much without touching the model or the data?"),
        ["c2", "c5", "c9"], ["c4", "c6", "c8", "c10", "c14"], ["c3", "c12"], ["c11", "c13", "src"],
        ["You pick a metric that reflects the decision, because accuracy means nothing at a 2% base rate.",
         "You stratify the splits and train on the real distribution.",
         "You check calibration, and choose the threshold from costs or validation data.",
         "Class weights and resampling mostly shift the threshold and distort the probabilities.",
         "They don't improve AUC for strong models, and a tuned threshold matches them.",
         "If you use them, keep them inside the training folds and correct the probabilities."],
        edits=[("But look at what it costs (chapter 6):", "But look at what it costs (see Compare the fixes, in the In practice tab):"),
               ("from chapter 2)", "from the Maths tab)")],
        strip=[NO_CODE]),
    "fundamentals/hyperparameter-tuning": _plan(
        "Each trial of your ETA model means training it and running 5-fold cross-validation, so you can only afford a few dozen trials. The interviewer asks:",
        "How do you tune hyperparameters efficiently?",
        "Think of finding the best dish in a city with only a few meals to spare. A grid keeps returning to the same few streets. Random search covers more ground. Bayesian optimisation heads towards what's been good so far, and successive halving takes one bite of many dishes before committing.",
        SEARCH_PICTURE, "Illustrative. If only one setting really matters, random search tests far more values of it.",
        ("c5", "<b>Try to break it.</b> Compare grid and random at 9, 16 and 25 trials. Watch the distinct values of the setting that matters, and the best loss.", "<b>Now say why:</b> why does the same budget go further when the trials aren't lined up in a grid?"),
        ["c2", "c6", "c7"], ["c4", "c8", "c9", "c13"], ["c3", "c11"], ["c10", "c12", "src"],
        ["You search settings and score each with cross-validation.",
         "Grid search is wasteful, because usually only a few hyperparameters matter.",
         "Random search explores many more values with the same budget.",
         "Bayesian optimisation fits a surrogate to past trials to pick the next one.",
         "Successive halving and Hyperband start many cheaply and continue the promising ones.",
         "You search rates on a log scale, and evaluate on data the search never saw."],
        strip=[NO_CODE]),
    "fundamentals/forecasting-basics": _plan(
        "Your team needs a 14-day order forecast every week to plan rider shifts. A teammate shuffles the days and cross-validates, and the score looks great. The interviewer asks:",
        "How would you build a forecast for a time series?",
        "Think of predicting this Saturday's rush. Your first answer should be \"about the same as last Saturday\". A fancier model has to beat that, and it has to be tested the way real life works: using only the past to predict the future.",
        FORECAST_PICTURE, "Illustrative. A rolling-origin backtest repeats this split at several cut-offs.",
        ("c6", "<b>Try to break it.</b> Compare mean, naive and seasonal naive, and then the regression. Watch the backtest MAE and the MASE.", "<b>Now say why:</b> why is such a simple seasonal rule so hard to beat here?"),
        ["c2", "c5", "c8", "c9"], ["c4", "c10", "c14"], ["c3", "c7", "c12"], ["c11", "c13", "src"],
        ["You decompose the series into trend and seasonality.",
         "You start with benchmarks, especially seasonal naive.",
         "Then you add structure: calendar features, smoothing or ARIMA, or boosting across many series.",
         "You only use features available at forecast time, for the full horizon.",
         "You evaluate with a rolling-origin backtest, never shuffled cross-validation.",
         "You compare models with a scale-free metric like MASE."],
        strip=[NO_CODE]),
})
# The lab builds its "Lesson" links from the old site's address.
ML_PLANS["fundamentals/choosing-the-right-metric"]["script_edits"] = [("const L = 'https://datawithsuman.github.io/ai/interview-prep/fundamentals/machine-learning/';", "const L = '../';")]
