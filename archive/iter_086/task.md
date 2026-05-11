# Task – iter_086

**Hypothesis:** mid-fitness-glider: A medium-fitness rule from Gen-2 supports a stable glider, unlike the chaotic highest-fitness rule.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_086/results/` (relative to the project root).

## Task

Create a new script, `src/analyze_median_elite_rule.py`, to search for gliders under a medium-performing rule from the Gen-2 population.

**Part 1: Identify the Median-Fitness Rule**
1. Read the `archive/iter_084/results/fitness_scores.csv` file.
2. Filter out any rules with a fitness score of 0.
3. Sort the remaining rules by `fitness_score`.
4. Find the rule at the 50th percentile (the median) of this filtered list.
5. The path to this rule will be in `archive/iter_084/population/{rule_id}.json`.

**Part 2: Search for Gliders**
1. Load the identified median-fitness rule.
2. Perform an exhaustive search for gliders, testing all unique, contiguous seeds of both 3-bits (11 trihexes) and 4-bits (10 tetrahexes).
3. For each of the 21 total seeds:
   a. Initialize a 150x150 grid with the seed pattern.
   b. Simulate for at least 500 steps.
   c. Track the pattern's configuration and bit count to detect cycles. A stable object is one that enters a cycle with `bit_count > 0`.
   d. For any stable object, calculate the net displacement of its center of mass over one full period.

**Part 3: Report Results**
1. Create `archive/iter_086/result.yaml` summarizing the findings.
2. The script should stop and report immediately if a glider is found. If no glider is found after checking all 21 seeds, report the negative result.
3. The YAML output must contain:
   - `median_rule_id`: The filename of the rule that was tested.
   - `median_rule_fitness`: The fitness score of that rule from iter_084.
   - `glider_found`: `true` or `false`.
   - `glider_seed_bits`: The number of bits in the seed that produced the first glider (3 or 4), or 0.
   - `glider_period`: The period of the first glider found, or 0.
   - `outcomes_summary`: A brief string summarizing the results (e.g., "No gliders found. 18 seeds decayed, 3 formed still lifes.").


## Success Criteria

- A stable object with a non-zero net displacement is found.
- The final bit count of the glider object is less than 50.

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
