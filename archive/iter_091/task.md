# Task – iter_091

**Hypothesis:** motion-evolution: A random population of 100 rules contains at least one rule with non-zero fitness when evaluated with the motion-based metric.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_091/results/` (relative to the project root).

## Task

Create a new script, `src/run_motion_evolution_gen1.py`, to perform a full generation and evaluation cycle with the new motion-based fitness metric.

**1. Generate Population:**
- Create a new population of 100 random, reversible, C6-symmetric, non-conserving rules. Use the same procedure as in iter_083 (2-4 kernel pairs, A/B in [1,127]).
- Save the 100 new rules to `archive/iter_091/population/`.

**2. Evaluate Population:**
- For each of the 100 new rules, calculate its fitness using the motion-based metric validated in iter_090.
- **Procedure per rule:**
  a. Initialize a 150x150 grid with a single 4-bit contiguous "T-shape" seed.
  b. Simulate for 500 steps, detecting if the pattern enters a stable cycle.
  c. If a stable, non-zero object is found, calculate its net displacement over one period.
  d. Fitness = `displacement / (1 + final_bit_count)`. Fitness is 0 if no cycle is found, the object decays, or displacement is zero.
- Save all results to `archive/iter_091/results/fitness_scores.csv`.

**3. Report Summary:**
- After evaluating all 100 rules, create `archive/iter_091/result.yaml` with the following information:
  - `glider_rule_found`: `true` if any rule had a fitness score > 0, otherwise `false`.
  - `population_size`: 100
  - `rules_with_motion`: The count of rules with a non-zero fitness score.
  - `top_fitness_score`: The highest fitness score found.
  - `top_rule_id`: The filename of the rule with the highest score.
  - `top_rule_glider_period`: The period of the glider produced by the top rule.
  - `top_rule_glider_bit_count`: The final bit count of the glider from the top rule.
  - `top_rule_glider_velocity`: The (dq, dr) velocity vector of the glider from the top rule.


## Success Criteria

- At least one rule in the population has a fitness score > 0.
- `result.yaml` is created with all specified keys.

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
