# Task – iter_083

**Hypothesis:** evolution-select: Selecting the top 10% of a 100-rule population based on the dynamic fitness metric yields a set of 'elite' rules whose average fitness is at least 10x the population average.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_083/results/` (relative to the project root).

## Task

Create a new script, `src/evolve_rules.py`, that implements the first generation (generation, evaluation, selection) of an evolutionary algorithm.

1.  **Generation:**
    - Generate a population of 100 random, reversible, C6-symmetric, non-conserving rules.
    - Use the same random generation method as in iter_082 (2-4 kernel pairs, `A` and `B` from 1-127).
    - Save each of the 100 rule files to `archive/iter_083/population/rule_NNN.json`.

2.  **Evaluation:**
    - For each of the 100 rules, calculate its fitness score.
    - Use the exact same procedure from iter_082:
        - Initialize a 100x100 grid with 50% random noise.
        - Simulate for 500 steps.
        - Fitness metric: `mean(bit_count_last_100_steps) * stddev(bit_count_all_steps)`. If stddev is 0, fitness is 0.
    - Save all 100 scores to `archive/iter_083/results/fitness_scores.csv` with columns: `rule_id`, `fitness_score`, `final_bit_count`, `mean_bit_count`, `stddev_bit_count`.

3.  **Selection:**
    - Identify the top 10 rules with the highest fitness scores. These are the "elites".
    - Copy the 10 elite rule files into a new directory: `archive/iter_083/elites/`.

4.  **YAML Output:**
    - Create `archive/iter_083/result.yaml` summarizing the results. It must contain:
        - `population_size`: 100
        - `elite_count`: 10
        - `population_fitness_mean`: The mean fitness of all 100 rules.
        - `elite_fitness_mean`: The mean fitness of the top 10 elite rules.
        - `top_elite_fitness`: The single highest fitness score found.
        - `selection_pressure_ratio`: `elite_fitness_mean / population_fitness_mean`.


## Success Criteria

- The script successfully generates, evaluates, and selects 10 elite rules from a population of 100.
- The `selection_pressure_ratio` is >= 10.0.
- The `elite_fitness_mean` is at least one order of magnitude larger than the population mean.

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
