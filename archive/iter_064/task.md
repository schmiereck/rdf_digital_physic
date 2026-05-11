# Task – iter_064

**Hypothesis:** The 3-cycle rule (A=7,B=11,C=14) supports at least one stable, bit-conserving, 4-bit glider.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_064/results/` (relative to the project root).

## Task

Create a new script, `src/find_gliders_3cycle_4bit.py`, to perform an exhaustive search for moving 4-bit objects.

1. **Load Rule:** Load the symmetric 3-cycle W=3 rule from `src/symmetric_rule_w3_3cycle.json`.

2. **Generate Seeds:** Generate all unique, contiguous 4-bit patterns (tetrahexes). There are 7 free tetrahexes, but the rule's C6 symmetry (not D6) means you must test all 10 unique one-sided orientations.

3. **Test Each Seed:** For each of the unique 4-bit seeds:
    a. Initialize a grid (e.g., 50x50) with the pattern.
    b. Simulate for at least 300 steps to robustly detect cycles and movement.
    c. At each step, verify that the bit count remains exactly 4. If it deviates, the seed is unstable; log this and continue.
    d. If the bit count is stable, track the history of the pattern's configuration to detect a cycle.
    e. If a cycle is detected, calculate the net displacement of the pattern's center of mass over one full period.

4. **Report Results:** The script should test all unique patterns and create `archive/iter_064/result.yaml` with a summary of the findings.

5. **YAML Output:** The `result.yaml` must contain these keys:
    - `glider_found`: `true` if a glider was found, otherwise `false`.
    - `patterns_checked`: The total number of unique contiguous 4-bit seeds tested.
    - `stable_still_lifes_found`: The count of stable period-1 objects.
    - `stable_oscillators_found`: The count of stable period > 1 objects with zero displacement.
    - `glider_period`: The integer period of the first glider found (or 0).
    - `glider_velocity_hex`: A tuple `(dq, dr)` for the glider's velocity per step (or `(0,0)`).


## Success Criteria

- glider_found is true
- The net_displacement of at least one stable 4-bit object is greater than zero

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
