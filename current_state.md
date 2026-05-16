# Current Research State

**Goal:** Evolve a Cellular Automata rule that produces a stable, moving particle (glider) in a 2D hexagonal grid with stable, ideally elastic, collision dynamics.

**Confirmed:**
- A `StagedCollisionFitness` function that provides a theoretical gradient for collision stages is implemented (iter_190.1).
- A "warm-start" technique for seeding an evolutionary population with mutated clones of a known rule is implemented and works as expected (iter_191.1).

**Refuted:**
- The hypothesis that seeding evolution with a known single-particle glider rule (`g10_rule_001`) is sufficient to evolve collision dynamics is refuted (iter_191.2).
- The glider-producing property of `g10_rule_001` is highly context-dependent and does not generalize to multi-particle initial conditions. It is not globally bit-conserving.
- Starting with a population that has motion is not sufficient if that population does not also satisfy the bit-conservation constraint on the target (collision) seed.

**Best Result:**
- No viable rule for elastic collisions is currently known. A new "context-switch" or "generalization" problem has been identified as the primary blocker: rules evolved for simple scenarios do not generalize to more complex ones.

**In Progress:**
- Diagnosing the fundamental limitations of the evolutionary approach. The focus has shifted from bootstrapping motion to finding or evolving rules with global conservation properties.

**Open Questions:**
- Can the fitness function be relaxed to use a soft penalty for bit non-conservation, providing a gradient towards conservation instead of a hard gate?
- Can we pre-screen a large random population to find rare rules that *do* conserve bits on the two-particle collision seed, and use those for a warm-start?
- Does a different family of rules, such as reversible block cellular automata, offer better global conservation properties suitable for a warm-start?
