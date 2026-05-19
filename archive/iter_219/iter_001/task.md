The goal is to extract and save the precise structure of the v<c glider discovered in iter_218.

1.  Read the champion rule `g4_rule_083` from `archive/iter_218/results/champion_rule.json`.
2.  Use the `src/run_simulation.py` script.
3.  Configure the simulation with the champion rule, the standard 3-bit L-tromino seed (`--seed_name l_tromino`), and run for 150 steps.
4.  Use the `find_objects` utility (already in the codebase) at step 100 to identify the coordinates of the moving glider.
5.  Normalize the coordinates so the top-left-most bit is at (0,0).
6.  Save the final list of relative coordinates to `archive/iter_219/results/vc_glider_g4_rule_083_structure.json`.
7.  The final JSON should be a simple list of lists, e.g., `[[0,0], [1,0], [1,1]]`.
8.  Add a metric `glider_bit_count` to the result with the number of bits in the glider.