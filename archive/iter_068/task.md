# Task – iter_068

**Hypothesis:** The non-conserving rule (A=3↔B=14) supports at least one stable, multi-bit object (final_bit_count > 1) from a 3-bit seed.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_068/results/` (relative to the project root).

## Task

Create a new script, `src/search_all_3bit_nonconserving.py`, to perform an exhaustive search of all 3-bit seeds under the non-conserving rule.

1.  **Load Rule:** Load the symmetric, non-conserving rule from `src/symmetric_rule_nonconserving_A3_B14.json` (kernel A=3↔B=14).

2.  **Exhaustive Search:** The script must generate and test **all 11** unique, contiguous 3-bit seeds (trihexes). It should not stop after the first finding.

3.  **Test Procedure for Each Seed:**
    a. Initialize a grid (e.g., 50x50) with the seed pattern.
    b. Simulate for up to 300 steps.
    c. A seed is considered to have produced a **stable object** if its evolution enters a finite cycle. Decay to 0 bits is an unstable outcome, not a stable object.

4.  **Analysis & Output:** After testing all 11 seeds, the script must analyze the results and create `archive/iter_068/result.yaml` with the following keys:
    - `multi_bit_object_found`: `true` if any stable object with `final_bit_count > 1` was found.
    - `glider_found`: `true` if any stable object had a non-zero net displacement.
    - `patterns_checked`: The total number of seeds tested (should be 11).
    - `stable_object_count`: The total number of seeds that resulted in a stable object (final_bit_count > 0).
    - `decayed_seed_count`: The total number of seeds that decayed to 0 bits.
    - `outcomes`: A list of summary objects, one for each of the 11 seeds, detailing the outcome. Each object should have keys like `seed_shape`, `outcome_class` (`STILL_LIFE`, `OSCILLATOR`, `DECAY`), `final_bit_count`, and `period`.


## Success Criteria

- The script successfully tests all 11 unique contiguous 3-bit seeds.
- At least one seed results in a stable, cycling object with `final_bit_count > 1`.
- The `outcomes` list in the result YAML contains exactly 11 entries.

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
