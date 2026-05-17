**Goal:** Implement the `SublightFitness` function and the main evolution script `evolve_sublight.py`.

**1. Create `src/fitness.py` and Implement `SublightFitness`:**

*   Create a new file: `src/fitness.py`.
*   Copy the `CheckpointFitness` class from `archive/iter_179/src/fitness.py` into this new file. You will also need to copy any necessary base classes or imports it depends on, such as `Fitness` and `collections.deque`.
*   Create a new class `SublightFitness` that inherits from `CheckpointFitness`.
*   Override the `calculate_fitness` method in `SublightFitness`.
*   The new method should first call the parent's `calculate_fitness` to get the base `displacement` and `num_checkpoints_passed`.
*   Implement the sub-light speed fitness logic:
    *   Calculate `velocity = displacement / total_steps` if `total_steps > 0`, otherwise `velocity = 0`.
    *   The final fitness should be `displacement * num_checkpoints_passed * (1.0 - velocity)`. Make sure to handle the case where velocity might be >= 1.0, clamping the multiplier to be non-negative.
    *   The method should still return a dictionary containing `fitness`, `displacement`, `velocity`, and any other relevant metrics.

**2. Create the Evolution Script `src/evolve_sublight.py`:**

*   Create a new file: `src/evolve_sublight.py`.
*   This script will be very similar to previous evolution scripts (e.g., from iter_179 or iter_196.1). Adapt the logic from one of those.
*   **Key configurations:**
    *   Import `SublightFitness` from `src/fitness.py`.
    *   Set `BITS_PER_CELL = 2`. This is critical.
    *   Set the `FITNESS_CLASS` to `SublightFitness`.
    *   Use the standard 'L-tromino' seed.
    *   The LUT size will be `2**(2 * 7) = 16384`. Adjust evolutionary parameters for this larger search space. A good starting point:
        *   `POPULATION_SIZE = 100`
        *   `GENERATIONS = 50`
        *   `MUTATION_RATE = 0.05`
        *   `ELITISM_COUNT = 4`
    *   The script should run the evolutionary loop and, upon completion, save the champion rule (the one with the highest fitness) to `archive/iter_196.2/results/champion_rule.txt`.

**3. Final Output:**

*   At the end of your execution, make sure the two new files `src/fitness.py` and `src/evolve_sublight.py` exist and are well-formed.
*   The script should not save any other files. The champion rule will be saved by the *next* step, which runs this script.
*   Your final `status` should be `ok` if the files are created correctly. No metrics are expected yet.

```yaml
status: ok
artifacts:
  - src/fitness.py
  - src/evolve_sublight.py
metrics: {}
log_excerpt: |
  File src/fitness.py created.
  File src/evolve_sublight.py created.
experimenter_view: |
  Successfully created the SublightFitness class and the evolution script `evolve_sublight.py`. The fitness function now correctly penalizes high velocities, and the evolution script is configured for a 2-bit-per-cell search. Ready to execute the search.
notes: ""
```