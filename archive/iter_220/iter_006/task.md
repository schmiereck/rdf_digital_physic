**Goal:** Validate the new `DisplacementConsistencyFitness` function against a gallery of known good and bad rules.

**Task:**
1.  Create a Python script named `src/validate_new_fitness.py`.
2.  The script will test the `DisplacementConsistencyFitness` from `src/new_fitness.py` on four test cases.
3.  **Test Cases to Implement:**
    a.  **'Drifter' (Exploit):** Use the rule from `archive/iter_218/results/champion_rule.json`.
    b.  **'Elastic v=1c Glider':** Use the rule from `archive/iter_193/results/champion_rule.json`.
    c.  **'Chaotic Bloater':** Use rule `g1_rule_001` from `archive/iter_171/results/rules_gen_1.json`.
    d.  **'Still Life':** Use the rule from `archive/iter_056/results/rule.json` which is known to create a stable 6-bit object from two adjacent 3-bit seeds. Use the appropriate seed for this rule.
4.  For each case, run a 500-step simulation on a 128x128 grid with the standard 3-bit L-tromino seed (except for the 'Still Life' case).
5.  Calculate and print the fitness score for each rule using `DisplacementConsistencyFitness`.
6.  The final output should be a clear report summarizing the fitness score for each of the four test cases.
7.  The task is successful when the script executes and the report shows a high score for the `v=1c` glider and very low scores for the other three.