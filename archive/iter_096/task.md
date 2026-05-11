# Task – iter_096

**Hypothesis:** dense-c2-motion-search: A population of 'dense' C2-symmetric rules contains at least one rule with non-zero motion fitness.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_096/results/` (relative to the project root).

## Task

Create a new script, `src/run_c2_dense_motion_evolution.py`, to generate and evaluate a population of C2-symmetric rules with a higher density of non-identity mappings.

**1. Implement Dense C2 Rule Generation:**
- Implement a new function to generate a single random, reversible, dense C2-symmetric rule.
- The function should aim for a target number of non-identity mappings (e.g., 32, which is 25% of the 128 states).
- **Generation Logic:**
  a. Start with a list of all 128 states [0-127] marked as "unmapped".
  b. While the number of non-identity mappings is less than the target (32):
     i. Pick a random state `A` from the "unmapped" list.
     ii. Pick another random state `B` from the "unmapped" list, ensuring `A != B`.
     iii. Check if the C2-closure `{A, B, rotate(A, 3), rotate(B, 3)}` is valid (i.e., all members are currently unmapped and distinct from each other).
     iv. If valid, add the mappings `A <-> B` and `rotate(A, 3) <-> rotate(B, 3)` to the rule. Mark all four states as "mapped".
     v. If not valid, try picking a different `B`.
- This process creates a rule with a controlled number of active transitions.

**2. Generate and Evaluate Population:**
- Generate a population of 100 random, **dense** C2-symmetric rules using the new function. Save them to `archive/iter_096/population/`.
- For each rule, calculate its motion fitness using the robust multi-seed evaluation protocol:
  - The final fitness for a rule is the maximum fitness achieved across all 21 standard contiguous seeds (11 trihexes, 10 tetrahexes).
  - Fitness for a single seed is `displacement / (1 + final_bit_count)`.
  - Simulate each seed for 500 steps.

**3. Report Results:**
- Save the final score for each rule to `archive/iter_096/results/c2_dense_scores.csv`.
- Create `archive/iter_096/result.yaml` summarizing the findings, with the standard keys: `rules_with_motion`, `top_fitness_score`, `top_rule_id`, etc.


## Success Criteria

- At least one rule in the population must have a `rules_with_motion` count greater than 0.
- The `top_fitness_score` in the final result must be greater than 0.

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
