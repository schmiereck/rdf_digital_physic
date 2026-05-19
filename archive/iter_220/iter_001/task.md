**Goal:** Empirically validate the new `DisplacementConsistencyFitness` function.

**Task:**
1.  Create a new Python script `src/validate_fitness.py`.
2.  In this script, import the `DisplacementConsistencyFitness` function and the necessary rule-loading and simulation components.
3.  Create a "validation gallery" of rules to test:
    *   **Good Glider:** The `v=1c` elastic glider rule from `iter_193`. Path: `archive/iter_193/results/champion_rule.json`. Label this "v=1c elastic".
    *   **Drifter Exploit:** The stationary "drifter" object from `iter_218` that exploited the previous fitness function. Path: `archive/iter_218/results/champion_g4_rule_083.json`. Label this "drifter".
    *   **Stationary Object:** A rule known to produce only stable, non-moving objects. Use the rule from `iter_056`. Path: `archive/iter_056/results/rule_1.json`. Label this "still_life".
4.  For each rule, initialize the fitness function and evaluate the rule's performance on the standard 3-bit L-tromino seed over 500 steps on a 128x128 grid.
5.  Print the results in a clear, formatted table showing the rule label and its final fitness score.

**Success Criterion:** The script runs successfully and prints a table where the "v=1c elastic" rule has a significantly positive score, and both the "drifter" and "still_life" rules have scores at or very near zero. This will confirm the function's ability to distinguish coherent motion from exploits.