# Task – iter_082

**Hypothesis:** A dynamic fitness metric, based on object count and grid entropy over time, can effectively discriminate between trivial and complex dynamics in a random sample of reversible rules.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_082/results/` (relative to the project root).

## Task

This is a meta-experiment to validate a new research methodology. It has two parts: generating random rules and then evaluating them.

**Part 1: Create `src/generate_random_rules.py`**
1. This script should generate 20 random, reversible, C6-symmetric, non-conserving rules.
2. To generate one random rule:
   a. Choose a number of kernel pairs, `k`, randomly between 2 and 4.
   b. For each of the `k` pairs, randomly select integers `A` and `B` from 1 to 127.
   c. Generate the full C6-symmetric rule by applying 6-fold rotation to each pair, adding both `A_rot -> B_rot` and the inverse `B_rot -> A_rot` to the rule dictionary. Ensure no conflicts arise.
3. Save each of the 20 generated rules to a unique file in `archive/iter_082/rules/`, e.g., `random_rule_01.json`.

**Part 2: Create `src/evaluate_rule_fitness.py`**
1. This script will iterate through the 20 rule files generated in Part 1.
2. For each rule:
   a. Initialize a 100x100 grid with 50% random noise.
   b. Simulate for 500 steps using the standard synchronous update.
   c. Record the `bit_count` (number of live cells) at each step.
   d. Calculate a "fitness score" designed to reward sustained, bounded complexity. A good candidate is: `fitness = mean(bit_count_last_100_steps) * stddev(bit_count_all_steps)`. A rule where everything dies or freezes will have a stddev of ~0, yielding a low score. A rule that explodes will have a high mean but may stabilize, while a complex one will have both sustained population and high variability.
   e. If `stddev` is zero, the fitness is zero.
3. After evaluating all 20 rules, create `archive/iter_082/results/fitness_scores.csv` with columns: `rule_id`, `fitness_score`, `final_bit_count`, `mean_bit_count`, `stddev_bit_count`.
4. Create `archive/iter_082/result.yaml` summarizing whether the fitness metric showed significant variance, suggesting it can discriminate between rule types. Include `min_fitness`, `max_fitness`, and `variance_of_scores`.


## Success Criteria

- The variance of the calculated fitness scores across the 20 rules is greater than 1.0.
- At least three distinct classes of behavior (e.g., rapid death, frozen state, sustained activity) are identified among the random rules, and these classes correspond to different fitness score ranges.

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
