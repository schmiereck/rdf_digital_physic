
The evolutionary search for a rule that animates a local pair of oscillators is blocked at generation zero. The random population tested in iter_135 was barren, yielding no viable "founder" rules. This mirrors a previous block in the *global* motion search, which was successfully resolved in iter_129 by performing a density scan.

This task re-applies that successful strategy to the current problem. We will perform a density scan to find the optimal rule density for generating viable founders under the *local* fitness metric.

**1. Create a new script: `src/run_local_density_scan.py`**

**2. Implement Rule Generation and Evaluation:**
   - The script should create three populations of 100 random C2-symmetric rules each:
     - `low_density`: 4 kernel pairs (16 non-identity mappings).
     - `medium_density`: 8 kernel pairs (32 non-identity mappings).
     - `high_density`: 16 kernel pairs (64 non-identity mappings).
   - Save the generated rules to `archive/iter_136/population/{low,medium,high}/`.
   - For each rule, evaluate it using the precise *local* fitness metric established in iter_135:
     - Load the canonical ash pattern from `src/ash_pattern.json`.
     - The target objects are the close oscillator pair (object IDs 2 and 3).
     - The simulation runs for 200 steps.
     - The fitness is based on the center-of-mass displacement of the target pair between steps 100 and 200.
     - The fitness formula is: `displacement / (1 + abs(bit_ratio - 1))`, where `bit_ratio` is the final-to-initial bit count ratio within the target region.

**3. Classification and Reporting:**
   - For each of the three density levels, determine:
     - The number of "viable" rules, where a rule is viable if its `local_fitness > 0.001` and `bit_ratio < 3.0`.
     - The top fitness score achieved within that population.
   - The script's primary output MUST be a YAML file at `archive/iter_136/results/result.yaml` containing these keys:
     - `low_density_viable_rules`
     - `low_density_top_fitness`
     - `medium_density_viable_rules`
     - `medium_density_top_fitness`
     - `high_density_viable_rules`
     - `high_density_top_fitness`

**4. Final Executor Output:**
   The executor must end its response with a YAML block containing the status, artifacts, metrics, and other required fields. The metrics should be copied directly from the `result.yaml` file produced by the script.
