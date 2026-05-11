# Task – iter_081

**Hypothesis:** noncontiguous-4bit: A 4-bit non-contiguous seed forms a stable, moving object under the non-conserving rule (A=3,B=14).

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_081/results/` (relative to the project root).

## Task

Create a new script, `src/search_noncontiguous_4bit.py`, to perform a systematic search for gliders from 4-bit non-contiguous seeds.

1. **Load Rule:** Load the C6-symmetric, non-conserving rule from `src/symmetric_rule_nonconserving_A3_B14.json` (kernel A=3↔B=14).

2. **Generate Seeds:**
   a. Systematically generate all unique 4-bit seeds that fit within a hex-radius of 2 (a 37-cell diamond shape).
   b. Filter out all 10 known contiguous tetrahexes.
   c. Reduce the remaining set to its rotationally unique members to create the final list of seeds to test.

3. **Test Each Seed:** For each unique seed:
   a. Initialize a grid (e.g., 150x150) with the pattern.
   b. Simulate for at least 500 steps.
   c. Track the pattern's configuration and bit count at each step to detect cycles. An object is considered stable if it enters a cycle with `bit_count > 0`.
   d. For any stable object, calculate the net displacement of its center of mass over one full period.

4. **Output:** Create `archive/iter_081/result.yaml`. The script should stop and report immediately if a glider is found. If no glider is found after checking all seeds, it should report a summary.
   - `glider_found`: `true` if any seed produced a glider.
   - `patterns_checked`: The number of unique non-contiguous seeds tested.
   - `stable_object_count`: The number of seeds that produced a stable object.
   - `glider_seed_coords`: The coordinates of the seed that produced the first glider, if found.
   - `glider_period`: The period of the first glider found.
   - `glider_velocity_hex`: The (dq, dr) velocity of the first glider found.


## Success Criteria

- Find at least one seed that results in a stable object with `glider_found: true`.
- The found glider must have `final_bit_count > 1`.

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
