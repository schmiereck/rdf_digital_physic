Phase: 3 - Evolutionary Search

### Goal
Observe deterministic, bit-conserving scattering in a 2D hexagonal grid. This requires first finding a stable, moving particle ("glider").

### Status
The project is blocked. All evolutionary searches have failed to find a "seed" glider. Random populations of both C6 and C2 symmetric rules were found to be barren of motion, even under robust multi-seed evaluation (iter_094, 095). The current working hypothesis is that the random rule generation method produces overly sparse, inactive rules, making the emergence of motion statistically impossible in small populations.

### Confirmed
- **C2 Random Population Barren (iter_095):** A random population of 100 C2-symmetric rules contains zero simple gliders. Reducing symmetry from C6 to C2 is not sufficient to find gliders by chance.
- **C6 Random Population Barren (iter_094):** A random population of 100 C6-symmetric rules contains zero simple gliders. Gliders are extremely rare in this space.
- **Motion-Based Fitness Metric is Selective (iter_090):** The metric `displacement / (1 + final_bit_count)` correctly assigns zero fitness to all non-moving rule archetypes.
- **Evolutionary Breeding Works (iter_084, 088):** The crossover and mutation operators are effective at creating new generations of rules that respond to selection pressure.
- **Formal Search Exhausted (iter_049-081):** Top-down, principled rule design has failed to produce motion.

### In Progress
- **iter_096:** Testing if a population of C2-symmetric rules generated with a higher "density" of non-identity mappings is more likely to contain a seed glider.
