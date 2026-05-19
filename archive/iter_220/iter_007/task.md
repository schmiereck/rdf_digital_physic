**Goal:** Validate the new `DisplacementConsistencyFitness` function against the two most critical test cases.

**Task:**
1.  Create a Python script named `src/validate_new_fitness.py`.
2.  The script will test `DisplacementConsistencyFitness` on two key rules:
    a.  **'Drifter' (Exploit):** Use the rule from `archive/iter_218/results/champion_rule.json`.
    b.  **'Elastic v=1c Glider':** Use the rule from `archive/iter_193/results/champion_rule.json`.
3.  For each rule, run a 500-step simulation on a 128x128 grid with the standard 3-bit L-tromino seed.
4.  Calculate and print the fitness score for both rules using `DisplacementConsistencyFitness`.
5.  The final output should be a clear, comparative report summarizing the two scores.
6.  Success is defined as the script running to completion and reporting a significantly higher score for the 'Elastic v=1c Glider' than for the 'Drifter'.