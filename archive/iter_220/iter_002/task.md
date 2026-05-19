**Goal:** Empirically validate the new `DisplacementConsistencyFitness` function.

**Task:**
1.  Create a new Python script `src/validate_fitness.py`.
2.  In this script, import `DisplacementConsistencyFitness` and the relevant rule-loading utilities.
3.  Load the following three rules for testing:
    *   The known-good `v=1c` elastic collision rule from `iter_193` (`g10_f_rule_034_c2`). This should get a high score.
    *   The `v=1c` glider rule from `iter_179` (`g10_rule_001`). This should also get a high score.
    *   The "drifter" exploit rule from `iter_218` (`g4_rule_083`). This MUST get a very low or zero score.
4.  For each rule, initialize the fitness function and evaluate the rule with the standard 3-bit L-tromino seed on a 128x128 grid for 500 steps.
5.  Print the resulting fitness score for each rule to stdout, clearly labeled.
6.  The script should exit with a non-zero error code if the "drifter" rule scores higher than either of the glider rules.
7.  Execute the script. The success criterion is a clean exit with the drifter rule scoring significantly lower than the glider rules.