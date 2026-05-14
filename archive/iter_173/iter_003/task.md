Conduct a new 3-generation evolutionary search using the validated `StableVelocityFitness` metric.

**Procedure:**

1.  Initialize a new, random population of 100 C2-symmetric rules.
2.  Configure the evolutionary script (`src/evolution.py`) to use the `StableVelocityFitness` metric for selection.
3.  Ensure all rule evaluations are performed using the standard 3-bit asymmetric 'L-tromino' seed.
4.  Run the evolution for 3 generations (Gen 0, Gen 1, Gen 2).
5.  **Goal:** Discover at least one rule in the final generation with a `StableVelocityFitness` score greater than 0.5.
6.  Log the maximum fitness and mean fitness for each generation.
7.  Save the complete final population, including IDs and fitness scores, to `archive/iter_173/results/gen2_population.csv`.
8.  Save the rule dictionary of the single best-performing rule from the final generation to `archive/iter_173/results/champion_rule.json`.