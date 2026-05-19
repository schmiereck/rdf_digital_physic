Create a new validation script `src/validate_fitness.py`. This script should do the following:

1.  **Load the Debunked Rule:** Load the rule `g4_rule_083` from `archive/iter_218/results/champion_rule.json`.
2.  **Load the Exploited Fitness Function:** Import and instantiate the `LeakySubLightFitness` function from `src/fitness_v_lessthan_c.py` (this file was created in iter_218).
3.  **Evaluate the Rule:** Run the fitness evaluation for the loaded rule using the standard 3-bit L-tromino seed on a 128x128 grid for 400 steps.
4.  **Print the Result:** Print the resulting fitness score and the metrics dictionary to standard output.

The purpose of this script is to create a reproducible test case of the exploit from `iter_218` and `iter_219`. We expect the output to show a high fitness score for a rule that we know produces a stationary object.