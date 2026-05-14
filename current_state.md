# Current Research State

**Goal:** Evolve a Cellular Automata rule that produces a stable, moving particle (glider) in a 2D hexagonal grid.

**Confirmed:**
- The `StableVelocityFitness` metric can guide evolution to a fitness score > 0.5 (iter_174.1).
- Extending the evolutionary run from 3 to 13 generations was sufficient to break the prior fitness plateau, discovering a new champion rule (`g7_rule_076`) with fitness 0.674 (iter_174.1).
- The new champion rule produces a complex, non-glider object with intermittent motion. This object is characterized by a large transient expansion (up to 129 bits) followed by a stable, period-64 oscillation (iter_174.2).

**Refuted:**
- The assumption that a fitness score > 0.5 using the `StableVelocityFitness` metric corresponds to a simple, stable glider. High fitness can also describe complex, periodic "wobblers".

**Best Result:**
- The current champion is `rule g7_rule_076` from iter_174.1. It produces a particle with complex, sustained, and periodic motion.

**In Progress:**
- Analysis of the complex dynamics of the new champion particle.

**Open Questions:**
- Can we evolve for *simpler* motion by adding a penalty for transient growth or bit-count variance to the fitness metric?
- Does an alternative seed particle exist that produces a simpler glider with the current champion rule?
- Can the champion rule be "fine-tuned" via further evolution to stabilize its output?
