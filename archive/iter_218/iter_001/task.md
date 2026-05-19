Create a new Python file `src/leaky_fitness.py`. Inside, define a new fitness function class called `LeakySubLightFitness`. This class should inherit from `CheckpointFitness` but relax the bit conservation rule.

**Logic for the `LeakySubLightFitness`:**

1.  It should still perform all the checks from `CheckpointFitness` (displacement, period gating, etc.).
2.  It should calculate a `base_fitness` score based on net displacement, just like the `SubLightFitness` function it is meant to improve upon.
3.  It should also calculate a `velocity` and reject any particles with `velocity > 0.9` by returning a fitness of 0.0.
4.  **Crucially, instead of returning 0.0 fitness for any bit count mismatch, it should apply a penalty.**
    -   Calculate a `conservation_factor` for each checkpoint. If the `bit_count` at a checkpoint equals the `initial_bit_count`, the factor is 1.0.
    -   If the bit counts do not match, the factor should be `min(bit_count, initial_bit_count) / max(bit_count, initial_bit_count)`.
    -   The final `total_conservation_score` is the average of the `conservation_factor` across all checkpoints.
5.  The final returned fitness should be `base_fitness * total_conservation_score`.

This creates a 'leaky' function that rewards displacement but penalizes poor bit conservation, providing a gradient for evolution.