Phase: 3 - Evolutionary Search

### Goal
Observe deterministic, bit-conserving scattering in a 2D hexagonal grid. This requires first finding a stable, moving particle ("glider").

### Status
The project is applying a new, validated, motion-centric fitness metric to find a glider. Previous attempts with this metric failed because they either used a random population (too sparse, iter_091) or a stability-evolved population with a single, insufficient seed for evaluation (iter_092). The current experiment broadens the search by testing each rule against a full suite of simple seeds.

### Confirmed
- **Motion-Based Fitness Metric is Selective (iter_090):** The metric `displacement / (1 + final_bit_count)` correctly assigns zero fitness to all non-moving rule archetypes.
- **Gliders are Rare (iter_091):** Gliders do not emerge by chance from a random population of rules.
- **Single-Seed Evaluation is Insufficient (iter_092):** Evaluating the stability-evolved Gen-3 population with a single seed found no motion, suggesting the method may not be robust enough.
- **Evolutionary Breeding Works (iter_084, 088):** The crossover and mutation operators are effective at creating new generations of rules that respond to the selection pressure of a fitness metric.
- **Formal Search Exhausted (iter_049-081):** Top-down, principled rule design has failed to produce motion.

### In Progress
- **iter_093:** Re-evaluating the Gen-3 'stability' population with a robust, multi-seed motion-based fitness metric to find the first glider.
