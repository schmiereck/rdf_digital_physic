Write and run a Python script `src/search_mixed_gliders_final.py` that does the following:

1. Scan for all JSON files under `archive/iter_215/results/`, `archive/iter_218/results/`, `archive/iter_221/results/`, `archive/iter_222/results/` (and potentially other results directories).
2. Use the robust JSON rule-extraction logic from `src/test_scan.py` to extract all rule dictionaries. Convert all rules into standard dictionaries (keys as strings or integers, values as integers) and deduplicate them.
3. For each unique rule, generate all contiguous 3-bit and 4-bit seeds (using `generate_contiguous_seeds` from `src/probe_gliders_223.py`).
4. For each seed, simulate 200 steps on a 128x128 grid and check if:
   - The period is detected (period is not None, final_bit_count > 0).
   - There is PERFECT bit conservation (i.e. at every single step, `grid.sum()` is exactly equal to the initial seed's bit count).
   - If `0.1 <= mean_speed <= 0.9`, it's a stable v<c glider.
   - If `mean_speed >= 0.95`, it's a stable v=1c glider.
5. Identify if any rule supports BOTH:
   - A stable v<c glider under one seed.
   - A stable v=1c glider under another seed.
6. Print a detailed summary: files searched, number of unique rules found, and details of any rule supporting both (including seed cells, period, speed).

Run the script and print its full output.