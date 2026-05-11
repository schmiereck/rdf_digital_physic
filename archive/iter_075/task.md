# Task – iter_075

**Hypothesis:** composite-nonconserving: Two 3-bit still lifes under rule (A=3,B=14), placed at a critical distance, form a stable, moving 6-bit composite object.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_075/results/` (relative to the project root).

## Task

Use the C6 non-conserving rule and the standard synchronous simulator to stage an interaction between two known stable objects.

1.  **Load Rule:** Load the C6-symmetric, non-conserving rule from `src/symmetric_rule_nonconserving_A3_B14.json` (kernel A=3↔B=14).
2.  **Identify Still Life:** From the results of iter_068, use one of the two 3-bit seeds that produced a stable 3-bit still life (e.g., a "bent" or "L-shape" trihex). Let's use the seed with coordinates `(0,0), (1,0), (0,1)`.
3.  **Initial Condition:** On a 150x150 grid, place two of these still lifes in a symmetric arrangement with a one-cell gap between them.
    - **Still Life 1:** Place '1's at `(50,50)`, `(51,50)`, and `(50,51)`.
    - **Still Life 2:** Place '1's at `(53,50)`, `(54,50)`, and `(53,51)`.
    - This creates a 6-bit composite object.
4.  **Simulation:** Run for 500 steps.
5.  **Analysis & Output:** Create `archive/iter_075/results/result.yaml` with the following keys:
    - `glider_found`: boolean
    - `behavior_class`: `GLIDER`, `STILL_LIFE`, `OSCILLATOR`, `DECAY`, or `CHAOTIC`.
    - `is_bit_count_stable`: boolean (is the bit count constant after an initial transient?)
    - `initial_bit_count`: 6
    - `final_bit_count`: integer
    - `object_period`: integer
    - `net_displacement_hex`: A tuple `(dq, dr)` for the net displacement over one period.


## Success Criteria

- The resulting composite object must be stable (enter a finite, non-decaying cycle).
- The composite object must have a non-zero net displacement over its period.

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
