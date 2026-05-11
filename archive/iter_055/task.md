# Task – iter_055

**Hypothesis:** composite-glider: Two 3-bit still lifes, placed at a critical non-adjacent distance, form a stable, bit-conserving 6-bit glider.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_055/results/` (relative to the project root).

## Task

Use the existing W=3 rule from `src/symmetric_rule_w3_a7_b14.json` and the standard CA simulator. The task is to stage an interaction between two known stable objects.

1. **Load Rule:** Use the W=3 symmetric rule (from kernel A=7, B=14).

2. **Identify Still Life:** Use the 3-bit straight-line still life confirmed in iter_052.

3. **Initial Condition:** On a 100x100 grid with periodic boundaries, place two of these still lifes on the same row, separated by one empty cell.
    - **Still Life 1:** Place '1's at `(20,50)`, `(21,50)`, and `(22,50)`.
    - **Still Life 2:** Place '1's at `(24,50)`, `(25,50)`, and `(26,50)`.
    - The total initial bit count will be 6.

4. **Simulation:** Run for 200 steps, which is sufficient to detect cycles or long-term stability.

5. **Analysis & Output:**
    - The primary goal is to determine if this 6-bit composite object is a glider.
    - Track the total bit count at each step.
    - Track the pattern's coordinates to detect cycles and calculate net displacement.
    - Create `archive/iter_055/result.yaml` with the following keys:
        - `glider_found`: boolean
        - `is_bit_conserving`: boolean
        - `behavior_class`: `GLIDER`, `STILL_LIFE`, `OSCILLATOR`, `DECAY`, or `CHAOTIC`.
        - `final_bit_count`: integer
        - `net_displacement`: float, distance moved by the center of mass over one period.
        - `object_period`: integer, the period of the final stable object.


## Success Criteria

- The total bit count remains 6 for all 200 steps.
- The 6-bit pattern enters a stable cycle (repeats its shape and relative position).
- The net displacement of the center of mass over one cycle is greater than 0.5.

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
