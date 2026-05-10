# Task – iter_028

**Hypothesis:** symmetry: A 60-degree rotated arrowhead seed produces a stable glider with a correspondingly rotated velocity vector.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_028/results/` (relative to the project root).

## Task

Use the existing simulator at `src/simulate_hex.py` with the standard CA update model and the 5-pair permutation rule from iter_024. No code changes are required. The only change is the initial condition.

1. **Simulation Setup:**
   - Grid size: 100x100 with periodic boundaries.
   - Steps: 100.

2. **Initial Condition (Rotated Arrowhead):**
   - Initialize the grid with all cells '0'.
   - Create a 3-bit arrowhead pattern rotated 60 degrees counter-clockwise, pointing North-East.
   - For a central cell `c` at `(50,50)`, the three '1's should be at:
     - `(50, 50)`
     - `(49, 51)` (South-West neighbor)
     - `(50, 51)` (South neighbor)

3. **Analysis:**
   - Track the total bit count and the coordinates of the '1's at each step.
   - Calculate the average velocity vector of the pattern's center of mass.

4. **Output:**
   - Create `archive/iter_028/result.yaml` with the following keys:
     - `is_bit_conserving`: `true` if the bit count remains 3.
     - `is_stable`: `true` if the 3-bit pattern remains intact.
     - `behavior_class`: `GLIDER`, `STATIONARY`, `DECAY`, or `CHAOTIC`.
     - `glider_velocity_hex`: The final measured velocity `(dq, dr)` in axial coordinates.


## Success Criteria

- The total bit count remains 3 for all 100 steps.
- The glider pattern remains stable and does not decay.
- The measured velocity vector is non-zero and not parallel to the original (1, 0) vector.

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
