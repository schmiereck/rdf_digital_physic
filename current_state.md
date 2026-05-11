Phase: 3 - Evolutionary Search

### Goal
Observe deterministic, bit-conserving scattering in a 2D hexagonal grid. This requires first finding a stable, moving particle ("glider").

### Status
The project is blocked. All attempts to find a "seed" glider for evolution within the C6-symmetric rule space have failed. Both random and stability-evolved populations were found to be devoid of motion, even with a robust multi-seed evaluation. The current hypothesis is that the high C6 symmetry constraint is too restrictive and that gliders may be more common in a lower-symmetry (C2) rule space.

### Confirmed
- **C6 Random Population Barren (iter_094):** A random population of 100 C6-symmetric rules contains zero simple gliders, even when evaluated against 21 seeds per rule. Gliders are extremely rare in this space.
- **Multi-Seed Evaluation on Gen-3 Fails (iter_093):** Robustly evaluating the stability-evolved Gen-3 population with 21 seeds per rule found zero motion, confirming this population is a dead end for finding gliders.
- **Motion-Based Fitness Metric is Selective (iter_090):** The metric `displacement / (1 + final_bit_count)` correctly assigns zero fitness to all non-moving rule archetypes.
- **Evolutionary Breeding Works (iter_084, 088):** The crossover and mutation operators are effective at creating new generations of rules that respond to the selection pressure of a fitness metric.
- **Formal Search Exhausted (iter_049-081):** Top-down, principled rule design has failed to produce motion.

### In Progress
- **iter_095:** Generating and evaluating a random population of C2-symmetric rules to test if this less-constrained space is more likely to contain gliders.
