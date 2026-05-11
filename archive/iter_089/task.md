# Task – iter_089

**Hypothesis:** glider-from-stabilizing-evolution: The best non-annihilating rule from the Gen-3 population supports at least one stable, moving glider from a small contiguous seed.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_089/results/` (relative to the project root).

## Task

Create a new script, `src/analyze_top_stabilizing_rule.py`, to find and analyze the most promising rule from the Gen-3 population.

**Part 1: Identify the Best Candidate Rule**
1. Read the `archive/iter_088/results/fitness_scores.csv` file.
2. Filter out any rules with a `fitness_score` exactly equal to 1.0, as these are likely simple annihilators.
3. From the remaining rules, identify the one with the highest `fitness_score`. This is the best candidate for supporting persistent, non-trivial structures.
4. Record the `rule_id` and its `fitness_score`.

**Part 2: Search for Gliders**
1. Load the identified best candidate rule from `archive/iter_088/population/{rule_id}.json`.
2. Perform an exhaustive search for gliders using all 21 standard contiguous seeds:
   - All 11 unique 3-bit trihexes.
   - All 10 unique one-sided 4-bit tetrahexes.
3. For each seed:
   - Initialize a 150x150 grid.
   - Simulate for 500 steps.
   - Detect if the pattern enters a stable cycle (bit_count > 0).
   - For stable objects, calculate the net displacement over one period.

**Part 3: Report Results**
1. Create `archive/iter_089/result.yaml` with a summary of the findings.
2. The YAML must contain:
   - `best_rule_id`: The filename of the rule tested.
   - `best_rule_fitness`: The fitness score of that rule from iter_088.
   - `glider_found`: `true` or `false`.
   - `seeds_tested`: The total number of seeds checked (21).
   - `stable_objects_found`: The count of seeds that resulted in a stable object.
   - `decayed_seeds_found`: The count of seeds that decayed to 0 bits.
   - `glider_seed_bits`: The bit count of the seed that produced the first glider, or 0.
   - `glider_period`: The period of the first glider found, or 0.


## Success Criteria

- A glider is found (a stable object with non-zero net displacement).
- The script successfully identifies the best non-annihilating rule from the Gen-3 population.

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
