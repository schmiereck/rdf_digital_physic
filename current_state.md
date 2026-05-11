Phase: 3 - Evolutionary Search

### Goal
Observe deterministic, bit-conserving scattering in a 2D hexagonal grid.

### Status
**CRITICAL BLOCKER.** The current evolutionary search paradigm is optimizing for a flawed fitness metric that rewards chaos and unbounded growth, which is antithetical to the goal of finding stable, localized particles (gliders). Both the highest-fitness (iter_085) and medium-fitness (iter_086) rules from the evolved population produced chaotic, explosive behavior. The immediate priority is to design and validate a new fitness function that rewards localized stability and penalizes explosive growth.

### Confirmed
- **Evolutionary Process Works (iter_084):** The G1->G2 breeding process successfully increases the population's average fitness according to the defined metric.
- **Fitness Metric is Flawed (iter_085, iter_086):** The `mean * stddev` metric selects for chaotic, space-filling rules, not glider-supporting rules.
- **Formal Search Failure (iter_049-081):** All top-down, principled searches for rules have failed to produce motion. This paradigm is considered exhausted.

### In Progress
- **iter_087:** Designing and validating a new fitness function based on penalizing bit growth from a small, fixed seed. This is a meta-experiment to fix the evolutionary search's objective function.
