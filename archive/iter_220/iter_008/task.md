**Goal:** Empirically validate the new `DisplacementConsistencyFitness` function.

**Task:**
1.  Create a new Python script `src/validate_fitness.py`.
2.  In this script, import the `DisplacementConsistencyFitness` class from `src/fitness_functions.py`.
3.  The script must test the fitness function against two specific scenarios:
    *   **Test Case 1 (Stable Glider):** Load the rule `g13_rule_035` from `iter_193` (the elastic collision rule). Evaluate the fitness of a single 3-bit L-tromino seed simulated for 500 steps. This rule produces a stable `v=1c` glider and should receive a high positive fitness score.
    *   **Test Case 2 (Drifter Exploit):** Load the rule `g4_rule_083` from `iter_218`. Evaluate the fitness of a single 3-bit L-tromino seed simulated for 500 steps. This rule produces a stationary pattern that drifts erratically and should receive a fitness score of exactly `0.0`.
4.  The script should print the resulting fitness scores for both test cases to standard output.
5.  Execute the script and report the results. The success of this task is determined by the script running and the fitness function demonstrating the expected behavior.