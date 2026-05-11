# Task – iter_067

**Hypothesis:** search-stable-nonconserving: The non-conserving rule (A=3↔B=14) supports at least one stable, non-trivial object (still life or oscillator) from a 2-bit or 3-bit seed.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_067/results/` (relative to the project root).

## Task

Create a new script, `src/search_stable_nonconserving_objects.py`, to systematically search for stable objects under the rule from iter_066.

1. **Load Rule:** Load the symmetric, non-conserving rule from `src/symmetric_rule_nonconserving_A3_B14.json` (kernel A=3↔B=14).

2. **Systematic Search:** The script should perform the search in two stages, stopping as soon as the first stable object is found.
   - **Stage 1 (2-bit seeds):** Generate and test all unique contiguous 2-bit seeds (dihexes).
   - **Stage 2 (3-bit seeds):** If no stable object is found in Stage 1, proceed to generate and test all 11 unique contiguous 3-bit seeds (trihexes).

3. **Test Procedure for Each Seed:**
   a. Initialize a grid (e.g., 50x50) with the seed pattern.
   b. Simulate for up to 300 steps.
   c. At each step, record the total bit count and the pattern's configuration (a sorted tuple of coordinates).
   d. A seed is considered to have produced a **stable object** if its evolution enters a finite cycle (a previously seen configuration and bit count repeats). Decay to 0 bits is not a stable object.

4. **Output:** Create `archive/iter_067/result.yaml` with the following keys:
    - `object_found`: `true` if a stable object was found, `false` otherwise.
    - `seed_bit_count`: The bit count of the seed that produced the first stable object (2 or 3).
    - `patterns_checked`: The total number of unique seeds tested before finding the object.
    - `behavior_class`: `STILL_LIFE` (period 1) or `OSCILLATOR` (period > 1).
    - `object_period`: The integer period of the found object.
    - `final_bit_count`: The bit count of the stable object itself.
    - `net_displacement`: The net displacement of the object's center of mass over one period.


## Success Criteria



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
