1. Create a python script `src/run_evolution_exp_220_sublight_final.py` that implements the custom `SubLightFitness` class internally, and runs the GA search (identical to `src/run_evolution_exp_220.py` but calling `_fitness_fn(rule_dict)` instead of the old fitness function).
2. Configure it to run for 20 generations, population=100.
3. Run the script and wait for it to finish.
4. Output the progress and final results of the search (fitness of the champion, its period, velocity, reasons for rejection of other rules). Copy the files to `archive/iter_220/results/`.