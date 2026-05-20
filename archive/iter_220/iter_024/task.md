Modify `src/new_fitness.py` and `src/run_vc_search_consistency.py` to add a velocity gating mechanism to filter out speed-of-light ($v=c$) gliders:
1. In `src/new_fitness.py`, modify `DisplacementConsistencyFitness.__init__` to accept `max_velocity_threshold: float | None = None`. Stash it in `self.max_velocity_threshold`.
2. In `src/new_fitness.py`, modify `DisplacementConsistencyFitness.__call__` to check:
   ```python
   if self.max_velocity_threshold is not None and mean_velocity_magnitude >= self.max_velocity_threshold:
       return 0.0
   ```
3. In `src/run_vc_search_consistency.py`, configure the `fitness_fn` in `main()` to use:
   ```python
   fitness_fn = DisplacementConsistencyFitness(
       num_windows=5,
       max_bit_threshold=6,
       max_velocity_threshold=0.9,
   )
   ```
4. Verify both files can be imported and are syntax-error-free.