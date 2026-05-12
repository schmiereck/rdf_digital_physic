Phase: Focused Exploration

## Goal
Evolve a rule that produces sustained, coherent motion in a pre-structured "ash" environment.

## Confirmed
- **Local Fitness Metric Works:** A fitness metric focused on a local subset of objects correctly identifies and rewards sustained displacement while penalizing stasis and chaotic growth (iter_135).
- **Remnant Composition & Structure:** The `rule_011` remnant consists of 37 objects (33 still-lifes, 4 oscillators) with a specific spatial layout featuring one very close oscillator pair (iter_133, 134).
- **Optimal Rule Density:** C2-symmetric rules with medium density (8 kernel pairs) are most likely to produce viable, non-chaotic, sustained motion (iter_129).

## Refuted
- **Local Evolution from Global Elites:** An evolutionary line successful at global animation is not a good source of genes for local animation. The globally-evolved rules are predisposed to freeze the most active local regions into still-lifes (iter_135).
- **Remnant is Not a Glider:** The remnant from `rule_011` is a collection of oscillators, not a single translating object (iter_132).

## Open Questions
- Can a fresh, random population of rules yield any "founder" individuals with non-chaotic local motion?
- Is it more effective to evolve a rule to move a single, isolated oscillator before attempting to move a pair?
- Would a fitness metric rewarding periodicity ("blinking") over translation be more effective?
- Can we evolve rules to manipulate the still-lifes instead of the oscillators?
- Is the `rule_011` remnant the best environment, or would a different "ash" be more amenable to animation?
