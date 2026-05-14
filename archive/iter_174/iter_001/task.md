Continue the evolutionary search from iteration 173.
- Load the final population state from `archive/iter_173/results/gen_2_population.json`.
- Run the evolution for 10 more generations (from generation 3 to 13).
- Use the `StableVelocityFitness` metric implemented in `src/fitness_stable_velocity.py`.
- The initial particle seed should be the 'asymmetric_tromino' used in the previous iteration.
- Save the final population to `archive/iter_174/results/gen_13_population.json`.
- Save the best rule found to `archive/iter_174/results/best_rule.json`.
- Write a summary of the run, including the fitness of the best rule in each generation, to `archive/iter_174/results/evolution_log.csv`.