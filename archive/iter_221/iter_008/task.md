Task: Run a warm-started evolutionary search for a stable sub-light speed (v<c) glider in the 2D hexagonal grid, and characterize the resulting champion.

Steps to execute:
1. Examine 'src/run_evolution_exp_220_fixed.py' and 'src/new_fitness.py' to understand how 'DisplacementConsistencyFitness' is implemented and used.
2. Load the 100 chromosomes from 'archive/iter_215/results/final_population.json' (which was successfully evolved in iter_215 for motion) to use as Gen 0.
3. Write a new script 'src/run_evolution_exp_221_warm.py' that:
   - Sets up 'DisplacementConsistencyFitness' with 'max_bit_threshold=12' (to eliminate breeders) and 'max_velocity_threshold=0.9' (to exclude light-speed v=1c gliders).
   - Initializes Gen 0 with the 100 chromosomes loaded from iter_215's final population.
   - Runs a generational Genetic Algorithm for 30 generations (or fewer if runtime is constraint, but at least 20) with a population of 100, elitism, crossover, and mutation (C2-symmetric).
   - Writes the evolution log to 'archive/iter_221/results/evolution_summary.csv'.
   - Saves the best rule found to 'archive/iter_221/results/champion_rule.json'.
4. Characterize the best rule by running a 500-step simulation on the standard asymmetric L-tromino seed, recording active cell count and CoM coordinates at each step, and writing this log to 'archive/iter_221/results/trajectory_log.csv'.
5. Render a GIF of the simulation of the best rule and save it to 'archive/iter_221/results/champion_vc_glider.gif'.
6. Verify if the best rule indeed represents a stable v<c glider. Print the final metrics and analysis.