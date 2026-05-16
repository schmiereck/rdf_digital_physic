Implement a new `MarginalDynamicCollisionFitness` function that requires particles to move closer by a specified margin, then farther apart. Validate it by confirming it assigns a fitness of 0 to the 'micro-jitter' exploit rule from `iter_188`.

**Instructions:**

1.  Create a new script `src/run_iter_189_fitness_validation.py`.
2.  Copy the `DynamicCollisionFitness` logic from `iter_188` into this new script and rename it to `MarginalDynamicCollisionFitness`.
3.  Modify the function to accept a `margin` parameter (default to `1.0`).
4.  The core logic for a fitness of 1.0 should now require:
    a. `midpoint_distance < initial_distance - margin`
    b. `final_distance > midpoint_distance + margin`
    c. Conserved bit count and object count.
5.  Add a `main` block to the script.
6.  Inside `main`, load the 'micro-jitter' champion rule from `archive/iter_188/results/champion_rule.json`.
7.  Instantiate the simulation environment with the standard two-glider collision setup.
8.  Calculate the fitness of the loaded rule using `MarginalDynamicCollisionFitness` with `margin=1.0`.
9.  Print the resulting fitness score to stdout.
10. The script's success criterion is that the printed fitness score is exactly `0.0`, proving it rejects the exploit.