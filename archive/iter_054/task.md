# Task – iter_054

**Hypothesis:** The W=3 rule (A=7, B=14) supports at least one stable, bit-conserving, 4-bit glider.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_054/results/` (relative to the project root).

## Task

Create a new script, `src/find_w3_glider_4bit.py`, to robustly retry the experiment from iter_053.

1.  **Load Rule:** Load the symmetric W=3 rule from `src/symmetric_rule_w3_a7_b14.json`.

2.  **Generate Seeds:** Programmatically generate all unique, contiguous 4-bit patterns (tetrahexes). There are 7 such patterns, often referred to as "straight," "T," "Y," "square," "skew," "L," and "bar." Your generation logic should produce these unique shapes, accounting for rotations and reflections.

3.  **Test Each Seed:** For each of the unique 4-bit seeds:
    a. Initialize a grid (e.g., 50x50) with the pattern.
    b. Simulate for at least 200 steps to robustly detect cycles.
    c. At each step, verify that the bit count remains exactly 4. If it ever deviates, the pattern is unstable; log this and continue to the next seed.
    d. If the bit count is stable, track the history of the pattern's configuration (as a tuple of sorted coordinates) to detect a cycle.
    e. If a cycle is detected, calculate the net displacement of the pattern's center of mass over one full period. A non-zero displacement means a glider has been found.

4.  **Report Results:** The script should run through all unique patterns and report on all stable objects found, stopping if a glider is identified.

5.  **Output:** Create `archive/iter_054/result.yaml` with the following keys:
    - `glider_found`: `true` if a glider was found, otherwise `false`.
    - `patterns_checked`: The total number of unique contiguous 4-bit seeds tested.
    - `stable_still_lifes_found`: The count of stable period-1 objects.
    - `stable_oscillators_found`: The count of stable period > 1 objects with zero displacement.
    - `glider_period`: The integer period of the first glider found (or 0).
    - `glider_velocity_hex`: A tuple `(dq, dr)` for the glider's velocity per step (or `(0,0)`).
    - `glider_seed_coords`: The initial coordinates of the seed that produced the first glider found.


## Success Criteria

- `glider_found` is `true` in the output YAML.
- The found glider maintains a bit count of 4 throughout its cycle.
- The `glider_velocity_hex` is non-zero.
- The script executes without error and checks all unique tetrahex patterns.

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
