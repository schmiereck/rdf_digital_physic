Write and run a Python script `src/search_mixed.py` to search through all previous final population files and champion files of sub-light speed glider campaigns (specifically look in directories like `archive/iter_215/results/`, `archive/iter_218/results/`, `archive/iter_221/results/`, `archive/iter_222/results/` for JSON files containing populations or rules) to find any rule that supports BOTH:
1. A stable v<c glider (speed between 0.1 and 0.9 with perfect bit conservation, such as the L-tromino).
2. A stable v=1c glider (speed > 0.95 with perfect bit conservation, using any other 3-bit or 4-bit seed).

Make sure the script is robust:
- It should scan all `.json` files in the specified results directories.
- It should extract rule dicts from individual files (like `champion_rule.json`, `champion_vc_rule.json`) as well as population files (like `final_population.json`, `warm_start_population.json`), which may be lists or contain a "population" list.
- For each unique rule, generate all contiguous 3-bit and 4-bit seeds (using `generate_contiguous_seeds` from `src/probe_gliders_223.py`).
- Simulate each seed under the rule on a 128x128 grid for 200 steps.
- Check if the simulation is stable (i.e. period is detected) and HAS PERFECT bit conservation (at every single step of the simulation, the number of live cells on the grid is exactly equal to the seed's bit count).
- Classify the seed: if mean_speed is between 0.1 and 0.9, it is a v<c glider; if mean_speed is > 0.95, it is a v=1c glider.
- Check if any rule supports BOTH.

Print the names of all files searched, the number of unique rules found, and details of any rule supporting both (including the exact seed cells and period for both gliders).
If any such rule is found, run the script and print its full output.