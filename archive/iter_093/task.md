# Task – iter_093

**Hypothesis:** multi-seed-evaluation: The Gen-3 population contains at least one rule with non-zero motion fitness when evaluated across all 21 standard 3- and 4-bit seeds.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_093/results/` (relative to the project root).

## Task

Create a new script, `src/run_multiseed_motion_evaluation.py`.

**1. Load Population:**
- The script must load all 100 rules from the Gen-3 population located in `archive/iter_088/population/`.

**2. Define Seed Suite:**
- The script must define a standard suite of 21 seeds: all 11 unique contiguous 3-bit trihexes and all 10 unique one-sided contiguous 4-bit tetrahexes.

**3. Evaluate Population with Multi-Seed Metric:**
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

**4. Report Results:**
- Save the final score and best-performing seed for each rule to `archive/iter_093/results/gen3_multiseed_scores.csv`.
- Create `archive/iter_093/result.yaml` summarizing the findings, with keys:
  - `rules_with_motion`: Count of rules with a final fitness score > 0.
  - `top_fitness_score`: The highest score found.
  - `top_rule_id`: The filename of the best rule.
  - `top_rule_glider_seed_info`: A string describing the seed that produced the best glider (e.g., "4-bit T-shape").
  - `top_rule_glider_period`: Period of the best glider.
  - `top_rule_glider_bit_count`: Final bit count of the best glider.
  - `top_rule_glider_velocity`: The (dq, dr) velocity of the best glider.


## Success Criteria

- At least one rule in the Gen-3 population achieves a fitness score > 0.
- The script successfully evaluates all 100 rules against all 21 seeds.

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
