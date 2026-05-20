Write and run a Python script `src/search_mixed.py` to search through previous final population and champion files of sub-light speed glider campaigns to find any rule that supports BOTH a stable v<c glider AND a stable v=1c glider, both with perfect bit conservation.

Follow these instructions:
1. Scan for all JSON files under `archive/iter_215/results/`, `archive/iter_218/results/`, `archive/iter_221/results/`, `archive/iter_222/results/` (and feel free to scan other `archive/iter_*/results/` directories as well).
2. Load and extract all rule dicts. Extract rules from single-rule files (having a 'rule_dict' key) and population files (where the JSON is a list of individuals, or has a key like 'population' or 'warm_start_population').
3. Convert rule dicts to a standard form (keys and values as integers, 0 to 127) and deduplicate them.
4. For each unique rule, generate all contiguous 3-bit and 4-bit seeds (using the contiguous seed generation from `src/probe_gliders_223.py`).
5. For each seed under the rule, simulate for 200 steps on a 128x128 grid:
   - Calculate `bit_counts` at every step.
   - Ensure the glider has *perfect* bit conservation: the bit count must be exactly constant at every step of the simulation (i.e. all(b == initial_bits for b in bit_counts)).
   - Determine stability: a period is detected (period is not None, final_bit_count > 0).
   - Measure mean speed: if 0.1 <= mean_speed <= 0.9, it's a stable v<c glider. If mean_speed > 0.95, it's a stable v=1c glider.
6. Check if any rule supports BOTH a stable v<c glider and a stable v=1c glider (with perfect bit conservation).
7. Print the results of the search, including the name of the file(s) where any such rule was found, the rule dictionary, and the details of the two gliders (seed cells, period, speed, and final bit counts).

Run the script and output the full results.