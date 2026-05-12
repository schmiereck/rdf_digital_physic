Phase: Focused Exploration

## Goal
Evolve a rule that produces sustained, coherent motion in a pre-structured "ash" environment.

## Confirmed
- **Parity-Conservation Unblocks Search:** Imposing a bit-count parity constraint (`HW(A)%2 == HW(B)%2`) on rule generation is highly effective. It successfully suppresses chaotic growth and produced a random population containing three "viable founder" rules that exhibit sustained motion with controlled bit counts (iter_138).
- **Local Fitness Metric Works:** A fitness metric focused on a local subset of objects correctly identifies and rewards sustained displacement while penalizing stasis and chaotic growth (iter_135).
- **Remnant Composition & Structure:** The `rule_011` remnant consists of 37 objects (33 still-lifes, 4 oscillators) with a specific spatial layout featuring one very close oscillator pair (iter_133, 134).

## Refuted
- **Viable Founders in Unconstrained Random Populations:** Randomly generated populations of C2-symmetric rules *without* the parity constraint do not contain any viable founders. High displacement is always coupled with high bit-count explosions (iter_136, 137).
- **Local Evolution from Global Elites:** An evolutionary line successful at global animation is not a good source of genes for local animation. The globally-evolved rules are predisposed to freeze the most active local regions into still-lifes (iter_135).

## Current Best
The top parity-conserving rule (`rule_002` from iter_138) achieves a fitness of 0.361 with a bit ratio of 1.003, representing the best candidate for sustained, non-chaotic motion found so far.

## Open Questions
- Can breeding the three viable parity-conserving founders produce a second generation with a higher mean fitness?
- What is the nature of the motion produced by the top rule (`rule_002`)?
- Can we visualize the dynamics of the new viable founders?
- Are there other mathematical constraints that could further improve the search?
