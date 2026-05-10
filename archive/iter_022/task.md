# Task – iter_022

**Hypothesis:** asymmetric-seed: A three-bit 'L-shaped' seed breaks the symmetry of the composite swap rule and produces a stable 2D glider.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_022/results/` (relative to the project root).

## Task

Use the existing script `src/simulate_hex.py` with the symmetric swap update model and the composite conditional rule from iter_021. No changes to the simulation logic are needed.

The ONLY change is the initial condition for the "test" simulation.

1.  **Test Simulation Initial Condition:**
    - On a 50x50 grid, initialize three adjacent cells with '1's in an "L" formation. For a reference center cell `c = (q, r)`, set the following cells to '1':
      - `(q, r)`
      - `(q+1, r)` (its East neighbor, b1)
      - `(q+1, r-1)` (its South-East neighbor, b2)
    - All other cells should be '0'.

2.  **Control Simulation:**
    - Run the same control as before: a single '1' at the grid center.

3.  **Execution:**
    - Run both simulations for 100 steps.

4.  **Outputs:**
    - Create `archive/iter_022/result.yaml` with the following keys:
      - `is_bit_conserving`: `true` if bit counts are maintained.
      - `control_behavior`: `STATIONARY` or `MOVED`.
      - `test_behavior`: `GLIDER`, `OSCILLATOR`, `DECAY`, or `CHAOTIC`.
      - `is_nontrivial_motion`: `true` if control is `STATIONARY` and test is `GLIDER`.
      - `final_bit_count_test`: The final number of '1's in the test simulation.
      - `glider_velocity_hex`: A tuple `(avg_dq_per_step, avg_dr_per_step)` for the test simulation's center of mass.


## Success Criteria

- `is_nontrivial_motion` is true.
- The `glider_velocity_hex` shows a consistent non-zero velocity (e.g., magnitude > 0.1).
- `is_bit_conserving` is true and `final_bit_count_test` is 3.

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
