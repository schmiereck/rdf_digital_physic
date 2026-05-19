**Goal:** Empirically validate the new `DisplacementConsistencyFitness` function against a gallery of known rules to confirm it distinguishes true motion from exploits.

**Task:**

1.  **Create a validation script:** Write a new Python script named `src/validate_fitness.py`.

2.  **Import necessary components:** Inside the script, import `DisplacementConsistencyFitness` from `src/fitness_functions.py` and the required simulation environment components from `src/game_of_life.py`.

3.  **Load the rules for testing:**
    *   Load the stable `v=1c` glider rule (`g10_rule_001`) from `archive/iter_179/results/champion_glider.json`.
    *   Load the `v=1c` elastic collision rule (`g1_rule_001`) from `archive/iter_193/results/champion_rule.json`.
    *   Load the 'drifter' exploit rule (`g4_rule_083`) from `archive/iter_218/results/champion_rule.json`.

4.  **Instantiate and run the fitness function:**
    *   For each of the three rules, instantiate `DisplacementConsistencyFitness`.
    *   Evaluate each rule using the standard 3-bit L-tromino seed on a 128x128 grid for 400 simulation steps.

5.  **Output the results:**
    *   Print the final fitness scores for all three rules clearly to standard output.
    *   Save the results in a structured JSON file at `archive/iter_220/results/validation_scores.json`. The JSON should map rule names to their scores, like `{"v1c_glider": score1, "elastic_glider": score2, "drifter_exploit": score3}`.

**Success Criterion:** The script executes successfully and the output shows a high score for the two `v=1c` gliders and a very low (near-zero) score for the drifter exploit, confirming the function works as designed.