Phase: 3 - Evolutionary Search

### Goal
Observe deterministic, bit-conserving scattering in a 2D hexagonal grid. This requires first finding a stable, moving particle ("glider").

### Status
The project is attempting to kickstart an evolutionary search for motion using a validated, motion-centric fitness metric. All previous attempts to find a rule with non-zero fitness have failed because the evaluation was either too narrow (single seed) or applied to the wrong population (one evolved for stability). The current experiment is the first to combine a random population with a robust, multi-seed evaluation, representing the most promising attempt to find the initial "spark" of motion needed for evolution.

### Confirmed
- **Multi-Seed Evaluation on Gen-3 Fails (iter_093):** Robustly evaluating the stability-evolved Gen-3 population with 21 seeds per rule found zero motion, confirming this population is a dead end.
- **Single-Seed Evaluation on Random Fails (iter_091):** Gliders are rare enough that a random population of 100 rules showed no motion when tested against a single seed.
- **Motion-Based Fitness Metric is Selective (iter_090):** The metric `displacement / (1 + final_bit_count)` correctly assigns zero fitness to all non-moving rule archetypes.
- **Evolutionary Breeding Works (iter_084, 088):** The crossover and mutation operators are effective at creating new generations of rules that respond to the selection pressure of a fitness metric.
- **Formal Search Exhausted (iter_049-081):** Top-down, principled rule design has failed to produce motion.

### In Progress
- **iter_094:** Re-evaluating the random population from iter_091 with a robust, multi-seed motion-based fitness metric to find the first glider.
