# Task – iter_069

**Hypothesis:** The non-conserving rule (A=3↔B=14) supports at least one stable, 4-bit glider.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_069/results/` (relative to the project root).

## Task

Create a new script, `src/search_4bit_nonconserving.py`, to perform an exhaustive search for moving 4-bit objects.

1.  **Load Rule:** Load the symmetric, non-conserving rule from `src/symmetric_rule_nonconserving_A3_B14.json` (kernel A=3↔B=14).

2.  **Generate Seeds:** Programmatically generate all 10 unique, one-sided contiguous 4-bit patterns (tetrahexes). This is necessary because the rule only has C6 (rotational) symmetry, not full D6 symmetry.

3.  **Test Each Seed:** For each of the 10 seeds:
    a. Initialize a grid with the pattern.
    b. Simulate for at least 400 steps to robustly detect cycles and movement.
    c. A seed's evolution is considered a **stable object** if it enters a finite cycle with a final bit count > 0.
    d. If a stable object is found, calculate the net displacement of its center of mass over one full period.

4.  **Report Results:** The script should test all 10 patterns and create `archive/iter_069/result.yaml` with a summary of the findings.

5.  **YAML Output:** The `result.yaml` must contain these keys:
    - `glider_found`: `true` if any stable object had a non-zero net displacement.
    - `patterns_checked`: The total number of seeds tested (should be 10).
    - `stable_object_count`: The total count of seeds that resulted in a stable object (final_bit_count > 0).
    - `decayed_seed_count`: The total count of seeds that decayed to 0 bits.
    - `glider_period`: The period of the first glider found (or 0).
    - `outcomes`: A list of summary strings, one for each of the 10 seeds, detailing its fate (e.g., "Seed 1 (straight): DECAY", "Seed 2 (T-shape): STILL_LIFE, 4 bits, period 1").


## Success Criteria

- Find at least one 4-bit seed that evolves into a stable object (final_bit_count > 0).
- The stable object has a non-zero net displacement over its period.

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
