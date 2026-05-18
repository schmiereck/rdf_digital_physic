**Context:** The `SparseGliderFitness` function was exploited by a stationary oscillator in `iter_201`. The proposed fix is to measure cumulative displacement from t=0 to the final step, which should be immune to this "phase-sampling" exploit. The previous attempt at this task with a 'low' complexity agent failed.

**Task:**
1.  Read the file `src/fitness_v2.py`.
2.  Create a new fitness function class named `CumulativeDisplacementFitness` in that file. It should inherit from `BaseFitness`.
3.  The core logic of this new function should be:
    a. Calculate the center of mass (CoM) at the initial state (t=0).
    b. Calculate the CoM at the final state (t=max_steps).
    c. The displacement is the Euclidean distance between the initial and final CoM.
    d. The fitness score should be `displacement / (1.0 + final_bit_count_float)`.
4.  Modify `src/main_v2.py` to allow selecting this new fitness function via a command-line argument (`--fitness CumulativeDisplacementFitness`).
5.  **Validate the fix:** Run a simulation using the known "bad" rule from `iter_200` (champion of the `v<c` search) and the `L-tromino` seed. This rule is located at `archive/iter_200/results/champion_rule.txt`.
6.  **Success Criterion:** The calculated fitness for the stationary oscillator rule must be less than 0.1. Report the final calculated fitness in the result metrics.
7.  Write the validation results, including the final fitness score, to `archive/iter_202/results/validation_report.txt`.