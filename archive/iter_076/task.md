# Task – iter_076

**Hypothesis:** composite-2-gap: Two 3-bit still lifes under rule (A=3,B=14), placed at a 2-cell critical distance, form a stable, moving 6-bit composite object.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_076/results/` (relative to the project root).

## Task

Use the C6 non-conserving rule and the standard synchronous simulator to stage an interaction between two known stable objects, separated by a two-cell gap.

1.  **Load Rule:** Load the C6-symmetric, non-conserving rule from `src/symmetric_rule_nonconserving_A3_B14.json` (kernel A=3↔B=14).
2.  **Identify Still Life:** Use the stable 3-bit "L-shape" still life from iter_068, seeded with coordinates `(0,0), (1,0), (0,1)`.
3.  **Initial Condition:** On a 150x150 grid, place two of these still lifes in a symmetric arrangement with a **two-cell gap** between them.
    - **Still Life 1:** Place '1's at `(50,50)`, `(51,50)`, and `(50,51)`.
    - **Still Life 2:** Place '1's at `(54,50)`, `(55,50)`, and `(54,51)`.
    - The total initial bit count will be 6.
4.  **Simulation:** Run for 500 steps.
5.  **Analysis & Output:** Create `archive/iter_076/result.yaml` with the following keys:
    - `glider_found`: boolean
    - `behavior_class`: `GLIDER`, `STILL_LIFE`, `OSCILLATOR`, `DECAY`, `NO_INTERACTION`, or `CHAOTIC`.
    - `is_bit_count_stable`: boolean (is the bit count constant after any initial transient?)
    - `initial_bit_count`: 6
    - `final_bit_count`: integer
    - `object_period`: integer
    - `net_displacement_hex`: A tuple `(dq, dr)` for the net displacement over one period.


## Success Criteria

- The final `behavior_class` is not `NO_INTERACTION`.
- The final `behavior_class` is `GLIDER`.

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
