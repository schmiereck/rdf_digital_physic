# Current Research State

**Goal:** Evolve a Cellular Automata rule that produces a stable, moving particle (glider) in a 2D hexagonal grid with stable, ideally elastic, collision dynamics.

**Confirmed:**
- A "leaky" fitness function with a soft penalty for non-conservation provides a viable evolutionary gradient where strict functions fail (iter_192.1).
- Starting with a "motion-first" population (mutants of `g10_rule_001`) and evolving with a leaky fitness function can produce rules that achieve the "approach" phase of a two-body collision (iter_192.1).
- The champion rule from this approach results in particle fusion, achieving `staged_score=1.0` with `bit_error=2` (iter_192.1).

**Refuted:**
- The "conservation-first" strategy of pre-screening for bit-conserving rules and then evolving for motion is ineffective. The vast majority of conserving rules exhibit no motion, creating a flat fitness landscape (iter_192.2).
- The hypothesis that seeding evolution with a known single-particle glider rule (`g10_rule_001`) is sufficient to evolve collision dynamics is refuted (iter_191.2). The glider-producing property does not generalize to multi-particle seeds.

**Best Result:**
- A rule evolved that produces the "approach" phase of a collision. The two particles merge into a stationary object, gaining 2 bits in the process. This is the first progress on multi-body dynamics. Champion rule is in `archive/iter_192/iter_001/results/champion_rule.json`.

**In Progress:**
- The primary blocker is no longer the absence of a fitness gradient, but finding a way to guide the evolution beyond the local optimum of "particle fusion" towards "particle recession" (a true elastic collision).

**Open Questions:**
- How can the fitness function be modified to specifically reward recession and guide evolution out of the fusion local optimum?
- Can increasing the simulation horizon allow fused particles more time to separate?
- Is the `bit_error=2` of the current champion an irreducible artifact of the `g10_rule_001` family, or can it be eliminated through further evolution?
