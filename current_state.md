Phase: 3 - Evolutionary Search

### Goal
Observe deterministic, bit-conserving scattering in a 2D hexagonal grid. This requires first finding a stable, moving particle ("glider").

### Status
The project is redesigning the core of its evolutionary search. Previous fitness metrics have failed, selecting for either chaos or annihilation. A new, motion-centric fitness function is currently being designed and validated.

### Confirmed
- **Evolutionary Breeding is Technically Sound (iter_084, 088):** The crossover/mutation mechanics successfully create new generations of rules, and the population's average fitness demonstrably responds to selection pressure.
- **Flawed Fitness Metric (Chaos, iter_085):** A metric rewarding `mean_bit_count * stddev` successfully bred for complexity, but this manifested as chaotic, space-filling rules antithetical to stable particles.
- **Flawed Fitness Metric (Annihilation, iter_089):** A metric rewarding stability (`1 / (1 + final_bit_count)`) successfully bred for non-chaotic behavior, but this manifested as rules that annihilate patterns, also failing to produce motion.
- **Formal Search Exhausted (iter_049-081):** All top-down, principled rule searches failed to produce motion, validating the pivot to evolutionary search.

### In Progress
- **iter_090:** Validating a new, motion-based fitness metric (`displacement / (1 + final_bit_count)`) to ensure it correctly rejects known non-glider-producing rules before it is used to guide a new evolutionary search.