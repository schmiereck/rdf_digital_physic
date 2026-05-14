
Run the next generation of evolution (Gen-3) using the `src/evolve.py` script.

1.  **Load Inputs:**
    *   Load the Gen-2 population from `archive/iter_152/results/population_gen2.json`.
    *   Load the Gen-2 fitness scores from `archive/iter_152/results/scores_gen2.csv`.

2.  **Evolutionary Step:**
    *   Select the top 10% of rules from Gen-2 as the elite parent pool.
    *   Create a new population of 100 rules (Gen-3) by breeding the elites. Use the same crossover and mutation operators as in the previous generation. Keep the top 2 elites unchanged in the new generation.

3.  **Evaluation:**
    *   Evaluate the fitness of all 100 rules in the new Gen-3 population.
    *   Use the same simulation parameters and composite fitness metric (`total_displacement / (1 + std_dev)`) as in iter_152.
    *   Simulation: 150x150 grid, 25% density soup, 1600 steps (4 windows of 400).

4.  **Save Outputs:**
    *   Save the new population to `archive/iter_153/results/population_gen3.json`.
    *   Save the fitness scores to `archive/iter_153/results/scores_gen3.csv`.

5.  **Report Metrics:**
    *   `mean_fitness`: The mean fitness of the Gen-3 population.
    *   `max_fitness`: The maximum fitness in the Gen-3 population.
    *   `median_fitness`: The median fitness of the Gen-3 population.
    *   `gen2_mean_fitness`: The mean fitness of the previous generation (should be ~0.609).
    *   `improvement_pct`: The percentage improvement of `mean_fitness` over `gen2_mean_fitness`.
    *   `elite_count`: The number of elite parents used.
    *   `population_size`: The size of the new population.

Please structure your final YAML report as specified in the system prompt.
