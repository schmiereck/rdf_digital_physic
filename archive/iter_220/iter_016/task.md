1. Modify `src/new_fitness.py` to add two parameters to `DisplacementConsistencyFitness.__init__`:
   - `strict_conservation: bool = False`
   - `max_bit_threshold: int | None = None`
   Update `_compute_conservation_score` or the main evaluation logic in `DisplacementConsistencyFitness` so that:
   - If `strict_conservation` is True, if any step in `sim_history` has a bit count != initial_bits, the fitness is 0.0.
   - If `max_bit_threshold` is not None, if any step in `sim_history` has a bit count > `max_bit_threshold`, the fitness is 0.0.

2. Create a new python script `src/run_vc_search_consistency.py` that is based on `src/run_vc_search.py` but uses `DisplacementConsistencyFitness` with `num_windows=5` and `max_bit_threshold=6` for the evolutionary search.
   - Make sure it uses ONLY standard library modules and numpy (no pandas).
   - Configure it to run 20 generations of 100 C2-symmetric rules, using the 3-bit L-tromino seed and 200 steps of simulation.
   - It should output `archive/iter_220/results/champion_vc_rule_consistency.json` and a trajectory log.

3. Run a quick check (import/syntax check) on both files to ensure no errors. Do NOT run the full evolutionary search yet, just prepare and validate the scripts.