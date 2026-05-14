Create a new fitness metric, `StableVelocityFitness`, designed to reward sustained, coherent motion and penalize instability and growth.

**Implementation Details:**

1.  Create a new file `src/fitness_stable_velocity.py`.
2.  The fitness function within this file should perform the following steps:
    a. Run the simulation for a total of 2000 steps using a given rule and the standard 3-bit asymmetric 'L-tromino' seed.
    b. Record the center of mass (COM) at steps 400, 800, 1200, 1600, and 2000. (The first 400 steps are a 'settling' period).
    c. Calculate the displacement (and thus velocity) for the four consecutive 400-step windows: 400-800, 800-1200, 1200-1600, and 1600-2000.
    d. Compute the `mean_velocity` and the standard deviation (`std_dev_velocity`) of these four velocity measurements.
    e. Record the `initial_bit_count` (3) and the `final_bit_count`.
    f. The final fitness score is `(mean_velocity / (1 + std_dev_velocity)) * (initial_bit_count / final_bit_count)`.
3.  Modify the main evaluation script `src/evaluate.py` to accept a `--fitness-metric` argument that allows selecting `StableVelocityFitness`.
4.  Ensure the formula correctly handles the `final_bit_count = 0` case (the score should be 0).