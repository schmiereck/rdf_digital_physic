# Task – iter_078

**Hypothesis:** composite-other-sl: Two instances of the second stable 3-bit still life, placed symmetrically with a 1-cell gap, form a stable, moving composite object under the non-conserving rule.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_078/results/` (relative to the project root).

## Task

Use the C6 non-conserving rule and the standard synchronous simulator to stage an interaction between the *other* known stable 3-bit still life.

1.  **Load Rule:** Load the C6-symmetric, non-conserving rule from `src/symmetric_rule_nonconserving_A3_B14.json` (kernel A=3↔B=14).

2.  **Identify Still Life:** The results of iter_068 showed that two distinct 3-bit seeds produced stable 3-bit still lifes. The experiments in iter_075-077 used one of them (the "L-shape"). Your task is to identify and use the *other* stable 3-bit still life for this experiment.

3.  **Initial Condition:** On a 150x150 grid, place two instances of this second still life in a symmetric arrangement with a one-cell gap between them, analogous to the setup in iter_075.
    - Center the 6-bit composite object on the grid.
    - The total initial bit count must be 6.

4.  **Simulation:** Run for 500 steps.

5.  **Analysis & Output:** Create `archive/iter_078/result.yaml` with the following keys:
    - `glider_found`: boolean
    - `behavior_class`: `GLIDER`, `STILL_LIFE`, `OSCILLATOR`, `DECAY`, or `CHAOTIC`.
    - `is_bit_count_stable`: boolean (is the bit count constant after any initial transient?)
    - `initial_bit_count`: 6
    - `final_bit_count`: integer
    - `object_period`: integer
    - `net_displacement_hex`: A tuple `(dq, dr)` for the net displacement over one period.


## Success Criteria

- `glider_found` is true.
- The object enters a stable cycle with `final_bit_count > 1`.
- The `net_displacement_hex` is non-zero.

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
