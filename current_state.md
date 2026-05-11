Phase: 3 - Evolutionary Search

### Goal
Observe deterministic, bit-conserving scattering in a 2D hexagonal grid. This requires first finding a stable, moving particle ("glider").

### Status
The project has pivoted to an evolutionary search guided by a new, motion-centric fitness function. Previous evolutionary attempts failed due to flawed metrics that rewarded either chaos or annihilation. This is the first attempt to breed rules by directly selecting for motion.

### Confirmed
- **Motion-Based Fitness Metric is Selective (iter_090):** The metric `displacement / (1 + final_bit_count)` correctly assigns zero fitness to known non-moving rule archetypes (chaotic, annihilating, still-life).
- **Evolutionary Breeding Works (iter_084, 088):** The technical implementation of crossover and mutation effectively creates new generations of rules whose population fitness responds to selection pressure.
- **Previous Fitness Metrics are Flawed (iter_085, 089):** Metrics based on abstract complexity or simple stability are misaligned with the goal and produce rules that are either chaotic or annihilating.
- **Formal Search Exhausted (iter_049-081):** Top-down, principled rule design has been comprehensively explored and has failed to produce motion.

### In Progress
- **iter_091:** Launching the first generation of an evolutionary search using the new, validated, motion-based fitness function to find a glider-producing rule.
