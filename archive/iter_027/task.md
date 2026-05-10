# Task – iter_027

**Hypothesis:** probe-stationary-target: A simple two-bit pattern forms a stationary fixed point or oscillator under the arrowhead-glider rule.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_027/results/` (relative to the project root).

## Task

Use the existing simulator at `src/simulate_hex.py` with the standard CA update model and the hand-crafted 5-pair permutation rule from iter_024. No code changes are required.

1. **Simulation Setup:**
   - Grid size: 100x100 with periodic boundaries.
   - Steps: 100.

2. **Initial Condition:**
   - Initialize the grid with all cells '0'.
   - Place a two-bit pattern near the center by setting two adjacent cells to '1': `(50,50)` and `(51,50)`.

3. **Analysis:**
   - At each step, track the total number of '1's and their coordinates.
   - Calculate the net displacement of the pattern's center of mass over the 100 steps.

4. **Output:**
   - Create `archive/iter_027/result.yaml` with the following keys:
     - `is_bit_conserving`: `true` if the bit count remains 2.
     - `behavior_class`: `STATIONARY_FIXED_POINT`, `STATIONARY_OSCILLATOR`, `GLIDER`, `DECAY`, or `CHAOTIC`.
     - `net_displacement`: The total distance the center of mass moved from its initial position.
     - `final_pattern_coords`: The coordinates of the '1's at the final step.


## Success Criteria

- The total bit count on the grid remains 2 throughout the simulation.
- The net displacement of the pattern's center of mass after 100 steps is less than 2.0 cells.

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
