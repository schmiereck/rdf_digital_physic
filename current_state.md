# Current Research State

**Goal:** Evolve a Cellular Automata rule that produces a stable, moving particle (glider) in a 2D hexagonal grid with stable, ideally elastic, collision dynamics.

**Confirmed:**
- A `StagedCollisionFitness` function that provides a theoretical gradient (scores of 0, 1, or 2 for stages of collision) has been successfully implemented and validated (iter_190.1).
- A robust evolutionary framework for finding rules with conserving collisions exists (iter_187).

**Refuted:**
- The hypothesis that a staged fitness function alone is sufficient to guide evolution out of a flat landscape is refuted (iter_190.2).
- A random population of rules is too sparse in motion-inducing, bit-conserving rules to provide a starting point for evolutionary search, even with a staged fitness function. This is a critical "bootstrap problem".
- The hypothesis that `g10_rule_001` supports elastic collisions is refuted (iter_185).
- Binary, all-or-nothing fitness functions create flat landscapes unsuitable for evolution (iter_189).

**Best Result:**
- No viable rule for elastic collisions is currently known. All recent attempts have been defeated by methodological dead-ends in fitness function design and population seeding.

**In Progress:**
- Iteratively refining the evolutionary methodology. The focus has now shifted from the fitness function's gradient to the quality of the initial population.

**Open Questions:**
- Can "warm-starting" evolution with a population of mutated variants of a known glider rule provide the necessary motion for the `StagedCollisionFitness` to work?
- What is the minimum mutation rate required to evolve collision dynamics from a single parent glider rule without destroying the motion property?
- Is it more effective to evolve two separate single-glider rules and then attempt to combine them?
