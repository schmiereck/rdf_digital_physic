This is a retry of sub-task 179.2, which failed with a transient `code_error`.

Based on the results of 179.1, no prior rules pass the `CheckpointFitness` metric. The next step is to launch a new evolutionary search guided by this robust metric.

**Instructions:**
1.  Create a new, random population of 100 C2-symmetric rules. Each rule should have a density of 8 kernel pairs.
2.  Run an evolutionary search for 10 generations.
3.  Use the `CheckpointFitness` metric as the objective function.
    - Seed: 'L-tromino'
    - Total steps: 200
    - Checkpoints: [50, 100, 150, 200] (The particle's bit count must be exactly 3 at each of these steps).
4.  Use tournament selection (size 4), two-point crossover (rate 0.8), and per-bit mutation (rate 0.01).
5.  Log the fitness of the best rule and the population average for each generation to `archive/iter_179/results/evolution_log.csv`.
6.  Save the entire final population to `archive/iter_179/results/final_population.json`.
7.  The primary goal is to find any rule with a fitness score greater than 0. If successful, report the `best_fitness_found` and the `generation_of_best` as key metrics.
