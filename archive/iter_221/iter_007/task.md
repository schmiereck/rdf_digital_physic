1. Inspect the class definition of `DisplacementConsistencyFitness` in `src/new_fitness.py`. Print its constructor parameters and the core of its `__call__` or `evaluate` method.
2. Create a new python script `src/run_evolution_exp_221.py` that:
   - Loads the initial warm-started population of chromosomes from `archive/iter_215/results/final_population.json` (or `warm_start_population.json` if final is not present or less suitable - check both and load the better one).
   - Instantiates `DisplacementConsistencyFitness` with `max_bit_threshold=12` and `max_velocity_threshold=0.9`.
   - Runs the genetic algorithm for 30 generations with population size of 100.
   - Saves the final population, champion rule dict, evolution summary, and any log files into `archive/iter_221/results/`.
3. Do a quick check/validation of this script (e.g., dry-run 1 generation) to make sure everything loads and runs without errors.
Print the results of your findings.