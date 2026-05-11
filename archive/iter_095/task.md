# Task – iter_095

**Hypothesis:** c2-motion-search: A random population of C2-symmetric rules contains at least one rule with non-zero motion fitness.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_095/results/` (relative to the project root).

## Task

Create a new script, `src/run_c2_motion_evolution_gen1.py`. This script will generate and evaluate a population of C2-symmetric rules.

**1. Implement C2 Rule Generation:**
- Create a function to generate a single random, reversible, C2-symmetric, non-conserving rule.
- This function should randomly choose `k` (between 2-4) kernel pairs `(A, B)`.
- For each pair, it adds only the C2-symmetric mappings to the rule dictionary: `A -> B`, `rotate(A, 3) -> rotate(B, 3)`, and their inverses. Ensure no mapping conflicts arise.

**2. Generate and Evaluate Population:**
- Generate a population of 100 random C2-symmetric rules and save them to `archive/iter_095/population/`.
- For each rule, calculate its motion fitness using the robust multi-seed evaluation protocol from iter_093/094:
  - The final fitness for a rule is the maximum fitness achieved across all 21 standard contiguous seeds (11 trihexes, 10 tetrahexes).
  - Fitness for a single seed is `displacement / (1 + final_bit_count)`.
  - Simulation per seed should run for 500 steps.

**3. Report Results:**
- Save the final score for each rule to `archive/iter_095/results/c2_random_multiseed_scores.csv`.
- Create `archive/iter_095/result.yaml` summarizing the findings, with the standard keys:
  - `rules_with_motion`: Count of rules with a final fitness score > 0.
  - `top_fitness_score`: The highest score found.
  - `top_rule_id`: The filename of the best rule, or "" if none found.
  - `top_rule_glider_seed_info`: A string describing the seed that produced the best glider.


## Success Criteria

- At least one rule in the population must have a fitness score > 0.

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
