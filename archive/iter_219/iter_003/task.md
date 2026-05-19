This is the third attempt to extract the v<c glider structure, after two failures by 'low' agents. The task is to identify and save the precise structure of the v<c glider from iter_218.

**Background:** A `low` complexity agent struggled to isolate the glider from potential background debris. Your task is to perform this extraction robustly.

**Plan:**
1.  Load the champion rule `g4_rule_083` from `archive/iter_218/results/champion_rule.json`.
2.  Run a simulation using `src/run_simulation.py` with the standard L-tromino seed for 200 steps.
3.  The core of your task is to **robustly identify the glider**. Do not just grab all coordinates. Instead, analyze the grid state at two different times (e.g., step 100 and step 150) to identify the single, cohesive, moving object. Any stationary bits are debris and must be ignored.
4.  Once you have the list of coordinates for the glider at a specific step, normalize these coordinates so the top-left-most coordinate is at `[0, 0]`.
5.  Save the final, normalized list of coordinates to `archive/iter_219/results/vc_glider_g4_rule_083_structure.json`. The file must be a simple JSON list of lists, like `[[0, 1], [1, 0], [2, 0]]`.
6.  As a final metric, report the `glider_bit_count`, which is simply the number of coordinate pairs in your final JSON file.