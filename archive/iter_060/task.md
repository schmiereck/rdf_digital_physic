# Task – iter_060

**Hypothesis:** The second W=3 rule (A=11, B=14) supports at least one stable, bit-conserving, 4-bit glider.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_060/results/` (relative to the project root).

## Task

Create a new script, `src/find_gliders_w3_rule2_4bit.py`, to perform an exhaustive search for moving 4-bit objects under the second W=3 rule.

1.  **Load Rule:** Load the symmetric W=3 rule generated in iter_058 from `src/symmetric_rule_w3_next.json` (derived from kernel A=11, B=14).

2.  **Generate Seeds:** Programmatically generate all unique, contiguous 4-bit patterns (tetrahexes). There are 7 unique free tetrahexes, but be mindful of the rule's C6 symmetry (not D6), which may require testing more than 7 orientations. Test all unique shapes.

3.  **Test Each Seed:** For each of the unique 4-bit seeds:
    a. Initialize a grid (e.g., 50x50) with the pattern.
    b. Simulate for at least 300 steps to robustly detect cycles and movement.
    c. At each step, verify that the bit count remains exactly 4. If it deviates, the pattern is unstable; log this and continue to the next seed.
    d. If the bit count is stable, track the history of the pattern's configuration to detect a cycle.
    e. If a cycle is detected, calculate the net displacement of the pattern's center of mass over one full period. A non-zero displacement means a glider has been found.

4.  **Report Results:** The script should test all unique patterns and create `archive/iter_060/result.yaml` with a summary of the findings.

5.  **YAML Output:** The `result.yaml` must contain these keys:
    - `glider_found`: `true` if a glider was found, otherwise `false`.
    - `patterns_checked`: The total number of unique contiguous 4-bit seeds tested.
    - `stable_still_lifes_found`: The count of stable period-1 objects.
    - `stable_oscillators_found`: The count of stable period > 1 objects with zero displacement.
    - `glider_period`: The integer period of the first glider found (or 0).
    - `glider_velocity_hex`: A tuple `(dq, dr)` for the glider's velocity per step (or `(0,0)`).
    - `glider_seed_coords`: The initial coordinates of the seed that produced the first glider found.


## Success Criteria

- `glider_found` is true in the output YAML.
- The reported `glider_velocity_hex` is not `(0,0)`.

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
