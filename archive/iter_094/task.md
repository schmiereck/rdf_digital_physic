# Task – iter_094

**Hypothesis:** The random population from iter_091 contains at least one rule with non-zero motion fitness when evaluated across all 21 standard 3- and 4-bit seeds.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_094/results/` (relative to the project root).

## Task

Create a new script, `src/reevaluate_random_for_motion.py`.

1.  **Load Population:**
    - The script must load the 100 random rules from the population generated in iter_091, located at `archive/iter_091/population/`.

2.  **Define Seed Suite:**
    - The script must define the standard suite of 21 seeds: all 11 unique contiguous 3-bit trihexes and all 10 unique one-sided contiguous 4-bit tetrahexes.

3.  **Evaluate Population with Multi-Seed Metric:**
    - For each of the 100 rules:
      a. Initialize a `max_fitness_for_rule` to 0.0.
      b. Iterate through each of the 21 seeds.
      c. For each seed, calculate its motion fitness using the standard procedure:
         - Initialize a 150x150 grid with the seed.
         - Simulate for 500 steps, detecting cycles.
         - If a stable object is found, calculate `fitness = displacement / (1 + final_bit_count)`.
         - If no stable object is found (decay, chaos, timeout), fitness is 0.
      d. Update `max_fitness_for_rule = max(max_fitness_for_rule, fitness)`.
      e. The final score for the rule is `max_fitness_for_rule`.

4.  **Report Results:**
    - Save the final score for each rule to `archive/iter_094/results/random_multiseed_scores.csv`.
    - Create `archive/iter_094/result.yaml` summarizing the findings, with keys:
      - `rules_with_motion`: Count of rules with a final fitness score > 0.
      - `top_fitness_score`: The highest score found.
      - `top_rule_id`: The filename of the best rule, or "" if none found.
      - `top_rule_glider_seed_info`: A string describing the seed that produced the best glider.
      - `top_rule_glider_period`: Period of the best glider.
      - `top_rule_glider_velocity`: The (dq, dr) velocity of the best glider.


## Success Criteria

- The script successfully evaluates all 100 rules against all 21 seeds.
- The value of `rules_with_motion` in the final YAML is >= 1.

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
