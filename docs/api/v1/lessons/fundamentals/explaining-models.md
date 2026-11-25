# Explaining Models: SHAP, Permutation Importance and PDPs

> How would you explain what your model learned, and why it made a particular prediction?

- Track: Fundamentals › Classical ML › Core concepts
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/explaining-models/
- Before this: Random Forest (`fundamentals/random-forest`), Cross-Validation & Data Leakage (`fundamentals/cross-validation-and-leakage`)
- Quiz topic: `mlcore`
- Sources checked: 2026-11-06 · Text last changed: 2026-11-20 · Version: 0e6ed5f933

## Intuition

### The situation

Your delivery-time model is accurate, but operations want to know why one order was predicted at 68 minutes, and which features matter overall. A colleague shows the tree's built-in importance chart, with an order ID near the top. The interviewer asks:

> How would you explain what your model learned, and why it made a particular prediction?

#### Why it matters

People ask why a model refused a loan or flagged an order. Debugging also starts here, as an important feature that shouldn't be there often means data leakage. Getting a number is easy. Reading it correctly is the skill.

### The idea

Think of a team that won a prize. To split it fairly, you ask how much each person added, trying them joining in every possible order, and you average. Shapley values do this for features. The shares always add up to the whole prize.

[Figure: Three tools. Permutation importance answers which features matter overall. Partial dependence shows how a feature moves predictions. SHAP explains one prediction.]

_Each answers a different question, and none of them shows cause._

### Play

**Try to break it.** Raise the interaction to 5. Then set rain to 0.

#### Share credit for one prediction

A made-up model: minutes = 20 + 2 × distance + 10 × rain + 8 × peak + interaction × distance × rain. The baseline uses distance 5, no rain and peak 0.3. Absent features take these values. Shares are exact, from every ordering.

Raise the interaction to **5**. Part of the effect now exists only when distance and rain act together, and Shapley values split that part between them. Now set rain to **0**: it matches the baseline, so it gets exactly zero credit.

**Now say why:** why does rain get no credit when it matches the baseline?

## Maths

### Maths

#### In one breath

**Permutation importance** shuffles one feature, and measures how much the score drops: which features the model relies on overall. **Partial dependence** shows how predictions change as one feature changes. **SHAP** explains a single prediction, splitting the gap from a baseline fairly among features. All of them **explain the model, not the world**, so they don't show cause, and correlated features can mislead each one.

#### Which tool answers which question

| Question | Tool | How it works | Watch out for |
|---|---|---|---|
| Which features does the model rely on? | **Permutation importance** | Shuffle one column, and measure the score's fall. | Correlated features hide each other. |
| How does a feature move predictions on average? | **Partial dependence** | Set the feature to each value for all rows, and average. | Averages hide interactions. Can create unrealistic rows. |
| Does the effect differ across rows? | **ICE plots** | One line per row. Their average is the PDP. | Hard to read with many rows. |
| Why this prediction? | **SHAP** | Share the gap from the baseline among features. | Depends on the baseline, and on how absent features are handled. |
| Why this prediction, simply? | **LIME** | Fit a small linear model on nearby perturbed samples. | Results depend on its settings, and can be unstable. |

##### Shapley values, in one idea

Imagine the features as a team, sharing credit for a prediction. A feature's contribution can depend on which others are already present. So average its added value across **every order** in which features could join. The result is the only way of sharing that meets three properties:

- **Local accuracy:** the contributions add up exactly to the prediction minus the baseline.

- **Missingness:** a feature that's absent gets no credit.

- **Consistency:** if a model comes to rely on a feature more, its credit shouldn't fall.

Trying every order is exponential. So practical tools use shortcuts, and TreeSHAP makes it fast for tree models.

##### Why built-in tree importance can mislead

Impurity-based importance is calculated on training data, and it favours features with many values, like IDs. It can rank a useless feature highly, so prefer permutation importance on held-out data.

##### How correlated features fool each tool

- **Permutation:** shuffle one of two twin features, and the model still has the other, so both look unimportant.

- **PDP and SHAP:** these can evaluate impossible combinations, like a 6-foot-tall child. The model's answer on those rows means little.

Group correlated features first, or look at them together.

#### The maths

$$ {\phi_i} = \sum_{S \subseteq F \setminus \{i\}} {\frac{|S|!\,(|F| - |S| - 1)!}{|F|!}}\; {\big[v(S \cup \{i\}) - v(S)\big]}, \qquad {f(x) = \phi_0 + \sum_i \phi_i} $$

From Lundberg and Lee (2017), building on Shapley’s work in game theory. SHAP sets absent features using expected values, and independence is a common simplifying assumption.

- **feature i’s Shapley value**: Its fair share of the gap between this prediction and the baseline.

- **the weight**: The share of all orderings in which exactly the features in S come before i.

- **its added value**: How much the prediction changes when i joins the features in S.

- **local accuracy**: The baseline plus all the contributions gives exactly the prediction.

## In practice

### In practice

#### In practice

- **Use them to find leaks:** if one feature dominates, ask if it could really be known at prediction time.

- **Evaluate first:** explaining a poor model tells you little, so check its score on held-out data.

- **Say it correctly:** "the model's prediction rose because of X", not "X causes delays". Changing X in the real world may do nothing. See causal inference.

- **Check stability:** retrain with a different seed. If the explanations change a lot, trust them less.

- **Simple models help:** if a small model does nearly as well, it may be easier to justify than a complex one with an explanation attached.

### The answer that sounds right

#### "SHAP says this feature causes the outcome"

It sounds right, as the number looks precise. But SHAP describes what the model does with its inputs. A feature can be a proxy for something else, and changing it may change nothing in the real world. To learn what a change would do, run an experiment or a causal analysis.

## Say it

### How would you explain what your model learned, and why it made a particular prediction?

#### The interviewer pushes further

Follow-up 1 of 3

Why might two important features both look unimportant?

If they're strongly correlated, shuffling one leaves the other available, so the score barely falls, and both seem unimportant. Group correlated features, permute them together or remove one, and compare. It's a known weakness of permutation importance.

Follow-up 2 of 3

A feature has a large SHAP value. If you change that feature, will the outcome change?

Not necessarily. SHAP explains the model's output. It could be a proxy for something else, or the model may have learned a correlation. To know whether changing it changes real outcomes, you need an experiment or a causal analysis.

Follow-up 3 of 3

Why not use a tree model's built-in feature importance?

Impurity importance is computed on training data, so it can reward overfitting, and it favours features with many unique values. A random ID can look important. Permutation importance on held-out data avoids that, though it has its own issue with correlated features.

#### The 30-second answer

It depends on the question. For which features matter overall, I'd use permutation importance on held-out data: shuffle a feature, and measure the score drop. For how a feature moves predictions, I'd use partial dependence, with ICE to reveal interactions. For one prediction, I'd use SHAP, which splits the gap from a baseline fairly among features, and always adds up. I'd watch correlated features, which hide each other or create unrealistic rows. And these explain the model, not the world, so they don't show cause.

**Key terms and sources**

Global and local explanations: permutation importance, partial dependence and ICE, SHAP and LIME, how each can mislead, and why none shows cause. · checked 6 Nov 2026

#### Sources

- [Lundberg and Lee, A Unified Approach to Interpreting Model Predictions (2017)](https://arxiv.org/abs/1705.07874)

- [scikit-learn on permutation importance](https://scikit-learn.org/stable/modules/permutation_importance.html)

- [scikit-learn on partial dependence and ICE](https://scikit-learn.org/stable/modules/partial_dependence.html)

- [Molnar, Interpretable Machine Learning: SHAP](https://christophm.github.io/interpretable-ml-book/shap.html)

Explanations are ours, built from these sources. Lab numbers are illustrative, and worked examples were checked by calculation.
