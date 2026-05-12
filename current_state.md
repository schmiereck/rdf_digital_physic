Phase: Focused Exploration

## Goal
Evolve a rule that produces sustained, coherent motion in a pre-structured "ash" environment.

## Confirmed
- **Local Fitness Metric Works:** A fitness metric focused on a local subset of objects correctly identifies and rewards sustained displacement while penalizing stasis and chaotic growth (iter_135).
- **Remnant Composition & Structure:** The `rule_011` remnant consists of 37 objects (33 still-lifes, 4 oscillators) with a specific spatial layout featuring one very close oscillator pair (iter_133, 134).
- **Optimal Rule Density for Motion Signal:** C2-symmetric rules with medium density (8 kernel pairs) are most likely to produce a *signal* of motion, although this is strongly correlated with chaotic growth (iter_129, 136).

## Refuted
- **Viable Founders in Random Populations:** Randomly generated populations of C2-symmetric rules, even at optimal density, do not contain any "viable founders" that exhibit both sustained motion and non-chaotic growth. Stricter fitness penalties confirm that high displacement is always coupled with high bit-count explosions (iter_136, 137).
- **Local Evolution from Global Elites:** An evolutionary line successful at global animation is not a good source of genes for local animation. The globally-evolved rules are predisposed to freeze the most active local regions into still-lifes (iter_135).
- **Remnant is Not a Glider:** The remnant from `rule_011` is a collection of oscillators, not a single translating object (iter_132).

## Open Questions
- Can we visualize the top 'chaotic movers' (e.g., rule_061) to see if they contain any coherent, glider-like structures amidst the noise?
- Can we generate rules with an explicit structural constraint, such as guaranteeing that all mappings are involutions, to suppress chaotic growth at the source?
- Is it possible to evolve a *modifier* to a known stable rule, rather than evolving a whole rule from scratch?
- Would a different evaluation environment, other than the 'ash', be less prone to chaotic explosions?
- If random search is failing, could we return to a constructive approach, designing a simple moving object and deriving the minimal rule to support it?
