# Task – iter_073

**Hypothesis:** dynamics-c2: The C2-symmetric rule from kernel (A=3, B=14) supports at least one stable, 4-bit glider.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_073/results/` (relative to the project root).

## Task

This is a two-part task: first generate the C2-symmetric rule, then search for 4-bit gliders.

**Part 1: Generate the C2-Symmetric Rule**
1. Create a script `src/generate_c2_rule.py`.
2. The script should define the kernel pair from iter_072: `A = 3` (popcount=2) and `B = 14` (popcount=3).
3. Generate the full C2-symmetric rule. This rule will have exactly four non-identity mappings (and their inverses):
   - `A` -> `B`
   - `rotate(A, 3)` -> `rotate(B, 3)`
   - `B` -> `A`
   - `rotate(B, 3)` -> `rotate(A, 3)`
4. Save the final rule dictionary to `src/symmetric_rule_c2_A3_B14.json`.

**Part 2: Search for 4-Bit Gliders**
1. Create a script `src/search_c2_gliders_4bit.py`.
2. Load the rule from `src/symmetric_rule_c2_A3_B14.json`.
3. Perform an exhaustive search using all 10 unique, one-sided contiguous 4-bit patterns (tetrahexes) as seeds.
4. For each seed, simulate for at least 400 steps on a 100x100 grid.
5. Check for stable objects (patterns that enter a finite cycle with bit_count > 0).
6. For any stable object found, calculate its net displacement per period. A non-zero displacement indicates a glider.
7. After testing all 10 seeds, create `archive/iter_073/result.yaml` with a summary of the findings, including the standard glider-search keys (`glider_found`, `patterns_checked`, `stable_object_count`, `decayed_seed_count`, `glider_period`, `glider_velocity_hex`).


## Success Criteria

- At least one 4-bit seed evolves into a stable object (final_bit_count > 0, enters a cycle).
- The net displacement of at least one stable object is greater than zero.

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
