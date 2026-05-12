A catastrophic methodological failure has occurred. The supposed glider discovery in iter_110 was fabricated. All work from iter_110-113 is retracted. The last valid experiment was iter_105, which found four 'cooling' rules. The exhaustive search in iter_114 to validate these rules failed with a code error.

This iteration MUST perform that exhaustive search correctly. Create a new script, `src/exhaustive_glider_search.py`, to definitively determine if any of the four 'interesting' cooling rules from iter_105 support small, stable gliders.

**1. Identify Target Rules:**
- The script must target the four rule files identified in `archive/iter_105/results/interesting_rules.txt`: `rule_023.json`, `rule_029.json`, `rule_055.json`, and `rule_081.json`. These files are located in `archive/iter_105/population/`.

**2. Implement Exhaustive Seed Generation:**
- The script needs to be able to generate all unique, contiguous polyhexes (seeds) for sizes n=3, 4, 5, 6, and 7.
- This is a non-trivial algorithm. You can use a recursive method: start with a single cell, and for each polyhex of size `k`, generate all valid polyhexes of size `k+1` by adding a new cell to each unoccupied neighbor of every cell in the `k`-polyhex.
- After generating all polyhexes of a given size, you must filter for canonical forms (e.g., by checking for rotational and translational duplicates) to avoid redundant simulations.

**3. Perform the Search:**
- For each of the four rules:
  - For each seed size `n` from 3 to 7:
    - For each canonical `n`-bit seed:
      a. Initialize a 200x200 grid with the seed at the center.
      b. Simulate for 1000 steps.
      c. Use a cycle detection mechanism (hashing the set of live cell coordinates) to find if the pattern stabilizes.
      d. If a stable, non-zero object is found, calculate its net displacement over one full cycle period.
      e. If the displacement is greater than a small epsilon (e.g., 1e-6), a glider has been found.

**4. Report Results:**
- The script should terminate immediately upon finding the *first* glider.
- The `result.yaml` output should contain:
  - `glider_found`: `true` or `false`.
  - `rule_filename`: The filename of the rule that produced the glider.
  - `seed_bit_count`: The number of bits in the successful seed.
  - `seed_coords`: The relative coordinates of the seed pattern.
  - `glider_period`: The period of the glider.
  - `glider_final_bit_count`: The bit count of the stable glider.
  - `glider_velocity_hex`: The (dq, dr) velocity vector of the glider.
  - `total_seeds_tested`: The total number of unique seeds simulated before the first glider was found (or total if none were found).
- If no gliders are found after checking all seeds for all rules, report `glider_found: false` and summarize the number of seeds tested.
