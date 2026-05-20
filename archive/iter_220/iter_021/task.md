Create a fixed evolution script `src/run_evolution_exp_220_fixed.py` based on `src/run_evolution_exp_220.py`.
Modify the instantiation of the fitness function to be:
`_fitness_fn = DisplacementConsistencyFitness(num_windows=5, max_bit_threshold=12, max_velocity_threshold=0.9)`
Run this fixed script to execute the evolutionary search for a true, sub-light speed (v<c) glider.
Ensure that the results (such as `champion_rule.json`, `evolution_summary.csv`, and any trajectory plots/GIFs) are saved under `archive/iter_220/results/`.
Output the evolution log/summary and the properties of the discovered champion rule.