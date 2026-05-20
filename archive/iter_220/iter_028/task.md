1. Create `src/run_evolution_exp_220_sublight.py` by copying the structure of `src/run_evolution_exp_220.py` but modifying the fitness function to use `SubLightFitness` from `src/fitness_functions.py`.
2. Configure it with:
   _fitness_fn = SubLightFitness(simulation_steps=500, window_start=200, window_end=400, period_window_start=200, period_window_end=400)
3. Run the script to execute the evolutionary search for a true, periodic, sub-light speed (v<c) glider.
4. Output the results (the final fitness of the champion, its chromosome, and whether a true v<c glider was found). Ensure the results are saved to `archive/iter_220/results/`.