# Task – iter_057

**Hypothesis:** asymmetric-composite: An asymmetric arrangement of two 3-bit still lifes forms a stable, bit-conserving glider.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_057/results/` (relative to the project root).

## Task

Use the existing W=3 rule from `src/symmetric_rule_w3_a7_b14.json` and the standard CA simulator. The task is to stage an asymmetric interaction between two known stable 3-bit objects.

1. **Load Rule:** Use the W=3 symmetric rule (from kernel A=7, B=14).

2. **Simulation Setup:**
   - Grid: 100x100 with periodic boundaries.
   - Steps: 300.

3. **Initial Condition:**
   - Place two 3-bit straight-line still lifes in an adjacent but non-collinear "stepped" configuration.
   - **Still Life 1:** Place '1's at `(20,50)`, `(21,50)`, `(22,50)`.
   - **Still Life 2:** Place '1's at `(22,51)`, `(23,51)`, `(24,51)`.
   - The total initial bit count must be 6.

4. **Analysis & Output:**
   - Determine if the resulting 6-bit composite object is a stable glider.
   - Track the total bit count at each step.
   - Track the pattern's coordinates to detect cycles and calculate net displacement.
   - Create `archive/iter_057/result.yaml` with the following keys:
       - `is_bit_conserving`: boolean
       - `behavior_class`: `GLIDER`, `STILL_LIFE`, `OSCILLATOR`, `DECAY`, or `CHAOTIC`.
       - `final_bit_count`: integer
       - `net_displacement`: float, distance moved by the center of mass over one period.
       - `object_period`: integer, the period of the final stable object.


## Success Criteria

- The final object must be bit-conserving (final_bit_count == 6).
- The behavior_class must be 'GLIDER'.
- The net_displacement over one period must be greater than 0.1.

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
