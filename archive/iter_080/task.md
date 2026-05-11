# Task – iter_080

**Hypothesis:** noncontiguous-3bit: A 3-bit non-contiguous seed forms a stable, moving object under the non-conserving rule (A=3,B=14).

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_080/results/` (relative to the project root).

## Task

Create a new script, `src/search_noncontiguous_3bit.py`, to perform a systematic search for gliders.

1.  **Load Rule:** Load the C6-symmetric, non-conserving rule from `src/symmetric_rule_nonconserving_A3_B14.json` (kernel A=3↔B=14).

2.  **Generate Seeds:** Systematically generate all unique 3-bit non-contiguous seeds that fit within a hex-radius of 2 (a 37-cell diamond). This ensures the patterns are compact enough to interact but are not contiguous. The script should enumerate all 3-cell combinations, filter out the 11 known contiguous trihexes, and then reduce the remaining set to its rotationally unique members.

3.  **Test Each Seed:** For each unique seed:
    a. Initialize a grid (e.g., 150x150) with the pattern.
    b. Simulate for 500 steps.
    c. Track the pattern's configuration and bit count at each step to detect cycles. An object is stable if it enters a cycle with `bit_count > 0`.
    d. For any stable object, calculate the net displacement of its center of mass over one full period.

4.  **Output:** Create `archive/iter_080/result.yaml`. The script should stop and report immediately if a glider is found. If no glider is found after checking all seeds, it should report a summary.
    - `glider_found`: `true` if any seed produced a glider.
    - `patterns_checked`: The number of unique non-contiguous seeds tested.
    - `stable_object_count`: The number of seeds that produced a stable object.
    - `outcomes`: A list of strings, one for each seed, detailing its fate, especially for the first glider found (e.g., "Seed #55: GLIDER, period 12, velocity (0.5, 0.25)").


## Success Criteria

- At least one seed produces a stable object with `bit_count > 0` and a non-zero net displacement over its cycle period.
- The `glider_found` key in `result.yaml` is `true`.

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
