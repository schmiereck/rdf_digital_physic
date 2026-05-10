# Task – iter_025

**Hypothesis:** collision: The arrowhead-glider rule from iter_024 produces a deterministic, non-chaotic, bit-conserving outcome from a head-on collision.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_025/results/` (relative to the project root).

## Task

Use the existing simulator at `src/simulate_hex.py` with the standard CA update model.

1.  **Extend the Rule for West-Moving Glider:**
    - The rule from iter_024 moves an East-pointing arrowhead `{(0,0), (-1,0), (-1,1)}` one step East.
    - You must now extend the rule permutation to also handle a West-pointing arrowhead, e.g., `{(0,0), (1,0), (1,-1)}`, moving one step West.
    - This requires deriving the 5 new neighborhood-state permutation pairs for the West-moving glider's active cells.
    - Crucially, these new mappings must also be reversible (e.g., if `A->B` for the new motion, then `B->A` must also be in the rule). Combine these new pairs with the existing ones from iter_024 into a single rule dictionary.

2.  **Simulation Setup:**
    - Use a rectangular grid of at least 100x50 cells to provide ample space.
    - **Initial Condition:** Place two 3-bit arrowhead gliders on the grid, positioned for a head-on collision in the center.
      - Place the East-moving glider at `(q=20, r=25)`.
      - Place the West-moving glider at `(q=80, r=25)`.
    - Run the simulation for 100 steps.

3.  **Analysis and Output:**
    - At each step, track the total number of '1's on the grid.
    - Record the state of the grid before (e.g., step 49), during, and after (e.g., step 60) the collision.
    - Create `archive/iter_025/results/` and save snapshots of the grid state at these key steps as text files.
    - Create `archive/iter_025/result.yaml` with the following keys:
      - `is_bit_conserving`: `true` if the total bit count remains 6 throughout.
      - `collision_outcome`: A string classifying the result, e.g., `ELASTIC_PASS_THROUGH`, `ELASTIC_SCATTER`, `FUSION`, `ANNIHILATION`, `STUCK`, `CHAOTIC`.
      - `final_particle_count`: The number of distinct glider-like patterns after the collision.


## Success Criteria

- The total bit count on the grid remains 6 throughout the simulation.
- The collision outcome is deterministic and not chaotic (i.e., does not result in uncontrolled growth of bits).

## Required Output

You MUST end your final response with a ```yaml``` code block in this exact schema (the orchestrator reads it to determine success):

```yaml
status: ok  # or experiment_failed or code_error
artifacts:
  - path/to/created/file  # relative to the project root
metrics:
  key: value  # any numeric results
log_excerpt: |  # last ~20 lines of relevant output
  ...
experimenter_view: |  # your qualitative observations
  ...
notes: brief technical remark
```
