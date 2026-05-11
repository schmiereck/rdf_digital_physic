# Task – iter_079

**Hypothesis:** noncontiguous-glider: A 2-bit non-contiguous seed forms a stable, moving object under the non-conserving rule (A=3,B=14).

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_079/results/` (relative to the project root).

## Task

Create a new script, `src/search_noncontiguous_2bit.py`, to perform a systematic search for gliders from simple non-contiguous seeds.

1.  **Load Rule:** Load the C6-symmetric, non-conserving rule from `src/symmetric_rule_nonconserving_A3_B14.json` (kernel A=3↔B=14).

2.  **Generate Seeds:** The script should systematically generate and test all unique 2-bit seeds separated by a hexagonal distance of 2. For a seed with one bit at `(0,0)`, the second bit will be at `(2,0)`, `(1,1)`, and `(0,2)`. Due to the rule's C6 symmetry, these three orientations cover all unique cases for distance=2.

3.  **Test Each Seed:** For each of the 3 unique seeds:
    a. Initialize a grid (e.g., 150x150) with the pattern.
    b. Simulate for 500 steps.
    c. Track the pattern's configuration and bit count at each step to detect cycles. An object is stable if it enters a cycle with `bit_count > 0`.
    d. For any stable object, calculate the net displacement of its center of mass over one full period.

4.  **Output:** Create `archive/iter_079/result.yaml` with the following keys:
    - `glider_found`: `true` if any seed produced a glider.
    - `patterns_checked`: The number of unique seeds tested (should be 3).
    - `stable_object_count`: The number of seeds that produced a stable object.
    - `outcomes`: A list of strings, one for each seed, detailing its fate (e.g., "Seed dist=2, orient=(2,0): DECAY", "Seed dist=2, orient=(1,1): GLIDER, period 8, velocity (1.0, 0.5)").


## Success Criteria

- glider_found is true
- The `outcomes` list reports at least one GLIDER with a non-zero velocity.

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
