The champion rule from `iter_200` was found to be a stationary oscillator, implying the evolutionary fitness function was exploited. Your task is to perform a "forensic analysis" to determine if the `SparseGliderFitness` function was fooled by transient initial motion.

Create a script `src/forensic_fitness_analysis.py`.

**Requirements:**

1.  **Load Assets:** Load the champion rule from `archive/iter_200/results/champion_v_lt_c_rule.json` and the `SparseGliderFitness` function from `src/fitness_v2.py`.
2.  **Simulate and Checkpoint:** Run a simulation for 512 steps using the standard L-tromino seed. At steps 32, 64, 128, 256, 384, and 512, calculate and log the cumulative displacement (Euclidean distance of the Center of Mass from its starting position).
3.  **Final Fitness:** Calculate the final fitness score using the `SparseGliderFitness` function's default settings to confirm you can reproduce the original score.
4.  **Log Output:** Print a clear log to stdout showing the displacement at each checkpoint.
5.  **CSV Output:** Save the checkpoint data to `archive/iter_201/results/displacement_over_time.csv` with columns `step, displacement`.
6.  **Analysis:** In the `experimenter_view`, explicitly state whether the results confirm the "transient puffer" exploit hypothesis and why.