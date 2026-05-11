Phase: 3 - Evolutionary Search

### Goal
Observe deterministic, bit-conserving scattering in a 2D hexagonal grid.

### Status
**MAJOR PIVOT.** The project is now pursuing a bottom-up, evolutionary approach after all top-down, formal rule design methods failed to produce motion (iter_049-081). The core evolutionary loop is being implemented and validated.

### Confirmed
- **Fitness Metric Validated (iter_082):** A metric based on the mean and standard deviation of grid population over time is effective at identifying rules that support sustained, complex dynamics.
- **Selection Validated (iter_083):** The fitness metric successfully identified a top 10% elite population with an average fitness 6.58x higher than the baseline random population.

### Refuted
- **Formal Search Paradigms (iter_049-081):** A comprehensive series of experiments has proven that top-down design based on pre-supposed structural properties (symmetry, conservation, etc.) is insufficient for finding rules that produce motion.

### In Progress
- **iter_084:** Breeding the second generation of rules by applying crossover and mutation operators to the Gen-1 elites. The goal is to demonstrate that the evolutionary process successfully improves the average population fitness over generations.
