# Task – iter_062

**Hypothesis:** dynamics-3cycle: The 3-cycle rule (A=7,B=11,C=14) produces at least one stable, bit-conserving, non-trivial 3-bit object.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_062/results/` (relative to the project root).

## Task

This is a two-part task: first generate the new rule from the 3-cycle kernel, then search for stable 3-bit objects within its dynamics.

**Part 1: Generate the 3-Cycle Rule**
1. Create a new script `src/generate_3cycle_rule.py`.
2. Define the kernel triplet from iter_061: `A = 7` ('0000111'), `B = 11` ('0001011'), `C = 14` ('0001110').
3. Implement the 6-fold hexagonal rotation for 7-bit integer states.
4. Generate the full symmetric rule. This will have 18 non-identity mappings. For each rotation `i` in `0..5`:
   - `A_rot = rotate(A, i)`, `B_rot = rotate(B, i)`, `C_rot = rotate(C, i)`
   - Add mappings: `rule[A_rot] = B_rot`, `rule[B_rot] = C_rot`, `rule[C_rot] = A_rot`.
5. Save the final rule dictionary to `src/symmetric_rule_w3_3cycle.json`.

**Part 2: Search for 3-Bit Objects**
1. Create a new script `src/search_3cycle_objects.py`.
2. Load the rule from `src/symmetric_rule_w3_3cycle.json`.
3. Systematically test all 11 unique, contiguous 3-bit patterns (trihexes).
4. For each seed, simulate for 200 steps on a small grid, checking for two conditions at every step:
   a. **Bit Conservation:** The total number of '1's must remain exactly 3.
   b. **Stability:** The pattern must eventually enter a cycle (i.e., a previously seen configuration of coordinates reappears).
5. The script should stop as soon as it finds the *first* stable, bit-conserving object.
6. Create `archive/iter_062/result.yaml` with the results of the search.

**YAML Output for iter_062:**
- `kernel_A`, `kernel_B`, `kernel_C`: The integers 7, 11, 14.
- `object_found`: `true` or `false`.
- `patterns_checked`: The number of 3-bit seeds tested before finding the first stable object.
- `object_type`: `STILL_LIFE`, `OSCILLATOR`, or `GLIDER`.
- `object_period`: The period of the found object.
- `net_displacement`: The net displacement of the object's center of mass over one period.


## Success Criteria

- The `search_3cycle_objects.py` script completes and generates a result.yaml.
- The `object_found` key in the result is `true`.
- The found object must maintain a bit count of exactly 3 for the duration of the test run.

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
