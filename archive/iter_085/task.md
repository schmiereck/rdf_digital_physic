# Task – iter_085

**Hypothesis:** glider-from-evolution: The highest-fitness rule from Gen-2 supports at least one stable, moving glider from a small (3- or 4-bit) contiguous seed.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_085/results/` (relative to the project root).

## Task

Create a new script, `src/analyze_top_elite_rule.py`, to search for gliders under the best rule found in the previous iteration.

**Part 1: Identify the Top Rule**
1. Read the `archive/iter_084/results/fitness_scores.csv` file.
2. Find the `rule_id` corresponding to the highest `fitness_score`.
3. The path to the top rule will be in `archive/iter_084/population/{rule_id}.json`.

**Part 2: Search for Gliders**
1. Load the identified top-performing rule.
2. Perform an exhaustive search for gliders, testing all unique, contiguous seeds of both 3-bits (11 trihexes) and 4-bits (10 tetrahexes).
3. For each of the 21 total seeds:
   a. Initialize a 150x150 grid with the seed pattern.
   b. Simulate for at least 500 steps.
   c. Track the pattern's configuration and bit count to detect cycles. An object is stable if it enters a cycle with `bit_count > 0`.
   d. For any stable object, calculate the net displacement of its center of mass over one full period.

**Part 3: Report Results**
1. Create `archive/iter_085/result.yaml` with a summary of the findings.
2. The script should stop and report immediately if a glider is found. If no glider is found after all 21 seeds are checked, it should report the negative result.
3. The YAML output must contain:
   - `top_rule_id`: The filename of the rule that was tested.
   - `top_rule_fitness`: The fitness score of that rule from iter_084.
   - `glider_found`: `true` or `false`.
   - `glider_seed_bits`: The number of bits in the seed that produced the first glider (3 or 4), or 0.
   - `glider_period`: The period of the first glider found, or 0.
   - `glider_velocity_hex`: A tuple `(dq, dr)` for the glider's velocity, or `(0,0)`.
   - `outcomes_summary`: A brief string summarizing the results (e.g., "Found 1 glider from 4-bit seeds. 15 seeds decayed, 5 formed still lifes.").


## Success Criteria

- The script correctly identifies and loads the top rule from iter_084.
- `glider_found` is true.
- `glider_velocity_hex` is a non-zero tuple.

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
