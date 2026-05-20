1. Create `src/run_evolution_exp_220_fixed.py` by copying `src/run_evolution_exp_220.py` and modifying it so that `DisplacementConsistencyFitness` is initialized with `max_bit_threshold=12` and `max_velocity_threshold=0.9`.
2. Run this fixed evolutionary search script.
3. Verify that the evolutionary search runs successfully, is not blocked by pandas, and does not find breeders or v=c gliders.
4. Output the results (the final fitness of the champion, its chromosome/rule, and whether a v<c glider was found). Ensure the files in `archive/iter_220/results/` are updated with the new champion rule.