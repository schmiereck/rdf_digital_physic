**Goal:** Launch a new evolutionary search using the `late-displacement` fitness metric validated in iter_156.

**Task Description:**

1.  Create a new main script, `src/evolve_velocity_stability.py`. This script should be adapted from the previous `src/evolve.py`.
2.  The script will initialize a new, random population of 100 C2-symmetric rules.
3.  For each rule, it will run a simulation for **2000 steps**.
4.  The fitness function must be implemented as the **Euclidean distance of the center of mass between t=1200 and t=2000**.
5.  Evaluate all 100 rules in the initial population (Generation 1).
6.  Save the entire evaluated population, including each rule's fitness score, to `archive/iter_157/results/population_gen1.json`.
7.  The final `metrics` in the executor's YAML should include:
    *   `max_fitness`: The highest fitness score achieved in the generation.
    *   `mean_fitness`: The average fitness of the population.
    *   `num_viable_rules`: The count of rules with a fitness score > 0.1.

**Success Criteria:**
The experiment succeeds if the executor identifies at least one rule with a fitness score greater than 0.2. The experimenter_view should explicitly state whether this threshold was met.