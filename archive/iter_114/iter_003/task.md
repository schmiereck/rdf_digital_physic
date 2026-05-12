**Goal:** Find the minimal seed that generates the known 6-bit, period-4 glider under rule_023.

This is a re-run of the timed-out task `114.2`.

**1. Create the script `src/find_minimal_seed.py`:**

**2. Script Logic:**
   a. **Load Rule:** Load the C2-symmetric rule from `archive/iter_105/population/rule_023.json`.
   b. **Load Glider Structure:** Load the known 4-phase structure of the 6-bit glider from `archive/iter_113/results/glider_structure.json`. The target structure is the set of coordinates for the first phase of this glider.
   c. **Search Algorithm:**
      - The search space is the power set of the glider's initial 6 cells.
      - Iterate through all possible subsets of the 6 glider cells, from smallest (size 1) to largest (size 5).
      - For each subset (candidate seed):
         i. Initialize a 150x150 grid with the candidate seed.
         ii. Simulate the rule for a sufficient number of steps (e.g., 20 steps) to see if it evolves into the target 6-bit glider structure.
         iii. If the grid state matches any of the 4 phases of the target glider, you have found a valid precursor. Since the search is ordered by size, the first one found will be the minimal seed.
   d. **Termination:**
      - If a minimal seed is found, stop immediately and report it.
      - If all subsets up to size 5 are tested and none produce the glider, conclude that the glider itself is the minimal seed.

**3. Output:**
   - Create the final `result.yaml` in `archive/iter_114/results/`.
   - The YAML must contain:
     - `minimal_seed_found`: `true` or `false`.
     - `minimal_seed_size`: The number of cells in the minimal seed (e.g., 4), or 6 if none smaller are found.
     - `minimal_seed_coords_q`: A list of the q-coordinates of the minimal seed.
     - `minimal_seed_coords_r`: A list of the r-coordinates of the minimal seed.
     - `steps_to_stabilize`: The number of simulation steps it took for the minimal seed to evolve into the full glider.

**4. Final YAML for Executor:**
The script's execution must conclude by printing the standard YAML block to stdout.
```yaml
status: ok
artifacts:
  - "archive/iter_114/results/result.yaml"
metrics: { ... }
log_excerpt: |
  ...
experimenter_view: |
  ...
notes: "Minimal seed search complete."
```