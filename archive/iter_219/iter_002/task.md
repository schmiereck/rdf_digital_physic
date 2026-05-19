This is a retry of failed task 219.1. The goal is to extract and save the structure of the v<c glider from iter_218.

**CRITICAL:** Do NOT write new debugging scripts. Use the existing `src/run_simulation.py` and its built-in analysis features.

1.  Locate the champion rule from `iter_218`. The file is `archive/iter_218/results/champion_rule.json`, and the rule is named `g4_rule_083`.
2.  Execute `src/run_simulation.py` with this rule (`--rule_path archive/iter_218/results/champion_rule.json`).
3.  Use the standard 3-bit L-tromino seed (`--seed_name l_tromino`).
4.  Run the simulation for 150 steps. The script has features to find and log objects. Ensure this is enabled.
5.  At step 100, the script should identify the glider. From the logs or output files, extract the glider's coordinates.
6.  Post-process these coordinates: normalize them so that the minimum row and column values are zero.
7.  Save the resulting list of relative coordinates into a new file at `archive/iter_219/results/vc_glider_g4_rule_083_structure.json`.
8.  The JSON file must contain a single list of lists (e.g., `[[0, 1], [1, 0], [1, 1], [2, 0]]`).
9.  Report the number of bits in the glider as the `glider_bit_count` metric.