# Current Research State

**Goal:** Evolve a Cellular Automata rule that produces a stable, moving particle (glider) in a 2D hexagonal grid with stable, ideally elastic, collision dynamics.

**Confirmed:**
- A robust evolutionary framework for finding rules with conserving collisions exists (iter_187).
- A `MarginalDynamicCollisionFitness` function with a distance margin correctly rejects both "stasis" and "micro-jitter" exploits (iter_189.1).

**Refuted:**
- The hypothesis that `g10_rule_001` supports elastic collisions is refuted (iter_185).
- Simple, non-symmetric fitness functions are easily exploited by static or near-static rules (iter_187, iter_188).
- A strict, binary, all-or-nothing fitness function (like `MarginalDynamicCollisionFitness`) is unsuitable for evolutionary search, as it creates a flat fitness landscape with no gradient for optimization (iter_189.2).

**Best Result:**
- No viable rule for elastic collisions is currently known. All recent attempts have been defeated by exploits or methodological dead-ends in the fitness function design.

**In Progress:**
- Iteratively refining the fitness function to eliminate exploits and guide evolution.

**Open Questions:**
- How can the fitness function be redesigned to be continuous and provide a gradient for evolution?
- Could a composite fitness score rewarding partial achievements (e.g., +0.25 for approach, +0.25 for recession) be more effective?
- Is rewarding any particle displacement a necessary precursor to rewarding specific collision dynamics?
