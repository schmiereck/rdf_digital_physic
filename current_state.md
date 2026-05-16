# Current Research State

**Goal:** Evolve a Cellular Automata rule that produces a stable, moving particle (glider) in a 2D hexagonal grid with stable, ideally elastic, collision dynamics.

**Confirmed:**
- A robust evolutionary framework for finding rules with conserving collisions exists (iter_187).
- The `CollisionFitness` from `iter_187` is flawed; it can be satisfied by static "still-life" patterns (iter_188.1).
- The `DynamicCollisionFitness` function (using strict inequality for distance checks) correctly rejects the static still-life rule from `iter_187` (iter_188.2).

**Refuted:**
- Simple, non-symmetric fitness functions for collision dynamics are easily exploited (iter_187.1).
- The hypothesis that `g10_rule_001` supports elastic collisions is refuted (iter_185).
- The hypothesis that `DynamicCollisionFitness` with strict inequality is sufficient to find dynamic collisions is refuted. It can be exploited by near-static rules that cause glider centers-of-mass to change by amounts on the order of floating-point precision noise (iter_188.2).

**Best Result:**
- No viable rule for elastic collisions is currently known. The champion from iter_187.2 was a stasis exploit, and the champion from iter_188.2 was a micro-jitter exploit.

**In Progress:**
- Iteratively refining the fitness function to eliminate exploits and enforce genuine, dynamic collisions.

**Open Questions:**
- How can the fitness function be improved to reward dynamic scattering properties (e.g., momentum change) and not just end-state counts?
- Can a fitness function with an absolute distance margin (e.g., `distance < initial_distance - 1.0`) prevent the "floating-point noise" exploit?
- What is the minimum margin required to enforce genuine movement?
- Should a cell-displacement metric be added to the fitness function to explicitly reward movement?
