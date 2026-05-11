# Task – iter_052

**Hypothesis:** The W=3 rule (A=7, B=14) supports at least one stable, bit-conserving, 3-bit glider.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_052/results/` (relative to the project root).

## Task

Create a new script, `src/find_w3_glider.py`, to systematically search for moving objects.

1. **Load Rule:** Load the symmetric W=3 rule from `src/symmetric_rule_w3_a7_b14.json`.

2. **Generate Seeds:** Generate all 11 unique, contiguous 3-bit patterns (as identified in iter_051's `total_unique_seeds_available`).

3. **Test Each Seed:** For each of the 11 seeds:
    a. Initialize a small grid (e.g., 50x50) with the pattern.
    b. Simulate for a sufficient number of steps to detect a cycle (e.g., 100 steps).
    c. At each step, verify that the bit count remains exactly 3. If it deviates, the seed is unstable; discard and continue.
    d. If bit count is stable, track the history of the pattern's coordinates to detect a cycle.
    e. If a cycle is detected, calculate the net displacement of the pattern's center of mass over one full period.

4. **Report Results:** The script should run through all 11 patterns and report on all stable objects found. The primary success is finding an object with a non-zero net displacement.

5. **Output:** Create `archive/iter_052/result.yaml` with the following keys:
    - `glider_found`: `true` if a glider was found, otherwise `false`.
    - `patterns_checked`: The total number of unique contiguous 3-bit seeds tested (should be 11).
    - `stable_still_lifes_found`: The count of stable period-1 objects.
    - `stable_oscillators_found`: The count of stable period > 1 objects with zero displacement.
    - `glider_period`: The integer period of the found glider (or 0).
    - `glider_velocity_hex`: A tuple `(dq, dr)` for the glider's velocity per step (or `(0,0)`).
    - `glider_seed_coords`: The initial coordinates of the seed that produced the glider.


## Success Criteria

- `glider_found` is true.
- The found glider maintains a constant bit count of 3 throughout its cycle.
- The `glider_velocity_hex` is non-zero.

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
