
Create and execute a Python script `src/run_evolution.py` to perform an evolutionary search for a stable glider.

**Evolution Parameters:**
- **Fitness Metric:** `SimpleMotionFitness` from `src/fitness_simple_motion.py`.
- **Population Size:** 100 C2-symmetric rules.
- **Generations:** 10.
- **Selection:** Truncation selection (keep top 10%).
- **Mutation:** Mutate the offspring to create the new generation.

**Script Logic:**
1.  **Initialization:** Create a population of 100 random C2-symmetric rules using `rules.random_c2_symmetric_rule()`.
2.  **Evolution Loop (10 generations):**
    a. Evaluate the fitness of each rule in the current population using `SimpleMotionFitness`. The fitness function should be instantiated with `grid_size=64` and `steps=200`.
    b. Record the min, mean, max, and std deviation of fitness for the generation.
    c. Identify the champion rule (the rule with the highest fitness seen so far across all generations) and its generation number.
    d. **Selection:** Select the top 10 rules from the current population.
    e. **Procreation:** Create 90 new rules by mutating the selected top 10 rules to form the next generation's population of 100.
3.  **Artifact Generation:**
    a. Save the best rule found across all generations (the champion) to `archive/iter_176/results/new_champion_rule.txt`.
    b. Save the per-generation fitness statistics (generation, min, mean, max, std) to a CSV file at `archive/iter_176/results/evolution_log.csv`.

**Execution and Reporting:**
1.  Run the `src/run_evolution.py` script.
2.  After the run, analyze the results.
3.  In your final YAML report:
    - **Metrics:** Report `max_fitness` (the fitness of the champion rule) and `champion_generation`.
    - **Experimenter View:** Describe the progress of the evolution (how fitness changed over generations) and the emergent behavior of the final champion rule when simulated.
    - **Artifacts:** List the two created files.
    - **Status:** Should be `ok` if the script runs to completion.
