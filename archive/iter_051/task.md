# Task – iter_051

**Hypothesis:** search-w3-objects: The W=3 rule (A=7, B=14) supports at least one stable, bit-conserving, non-trivial 3-bit object.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_051/results/` (relative to the project root).

## Task

Create a new script `src/find_w3_objects.py`. This script will perform a combinatorial search, not a long-running simulation.

1. **Load Rule:** Load the symmetric W=3 rule from `src/symmetric_rule_w3_a7_b14.json`.
2. **Generate Seeds:** Systematically generate all unique, contiguous 3-bit patterns. A pattern is contiguous if its '1's form a single connected component on the hex grid. Consider all patterns that can fit within a small bounding box (e.g., a 3x3 hex area) to keep the search space manageable.
3. **Test Each Seed:** For each generated 3-bit seed pattern:
    a. Initialize a small grid with the pattern.
    b. Run the CA simulation for a fixed number of steps (e.g., 20).
    c. At each step, check the total bit count. If it ever deviates from 3, the seed is unstable; discard it and move to the next.
    d. If the bit count remains 3 for all 20 steps, check if the pattern has repeated. Store the sequence of patterns. If a pattern state repeats, a stable object has been found.
4. **Stop and Report:** The script should stop as soon as the *first* stable object (still life or oscillator) is found.
5. **Output:** Create `archive/iter_051/result.yaml` with the following keys:
    - `object_found`: `true` if a stable object was found, otherwise `false`.
    - `patterns_checked`: The total number of unique contiguous 3-bit seeds tested.
    - `object_type`: A string, `STILL_LIFE` (period 1) or `OSCILLATOR` (period > 1).
    - `object_period`: The integer period of the found object.
    - `initial_seed_coords`: A list of the `(q, r)` coordinates for the seed that produced the first stable object.


## Success Criteria

- `object_found` is true.
- `object_type` is either `STILL_LIFE` or `OSCILLATOR`.

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
