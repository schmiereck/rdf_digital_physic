# Task – iter_087

**Hypothesis:** A fitness function rewarding low final bit count from a small seed will correctly identify known chaotic rules as 'unfit' and known stabilizing rules as 'fit'.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_087/results/` (relative to the project root).

## Task

Create a new script, `src/validate_new_fitness_metric.py`, to test a redesigned fitness function.

**1. Define the New Fitness Function:**
The function will evaluate a given rule based on its behavior from a single, small seed.
- **Metric:** `fitness = 1 / (1 + final_bit_count)`.
- **Procedure:**
  a. Initialize a 150x150 grid with a single, 4-bit contiguous "T-shape" seed.
  b. Simulate for 500 steps.
  c. Record the final `bit_count` at step 500.
  d. Calculate the fitness score. A rule that destroys the seed (final_bit_count=0) gets a score of 1.0. A rule that creates a stable 4-bit object gets 1/(1+4) = 0.2. A rule that explodes to 1000 bits gets ~0.001.

**2. Test on Known Rules:**
The script will evaluate three specific rules to validate the metric's effectiveness:
a. **Chaotic High-Fitness Rule:** Load `archive/iter_084/population/rule_023.json` (the top-fitness rule from iter_085).
b. **Chaotic Medium-Fitness Rule:** Load `archive/iter_084/population/rule_056.json` (the median-fitness rule from iter_086).
c. **Stabilizing Rule:** Load `src/symmetric_rule_nonconserving_A3_B14.json` (the rule from iter_069, known to produce stable still lifes from 4-bit seeds).

**3. Report Results:**
Create `archive/iter_087/result.yaml` with the following keys:
- `chaotic_high_fitness_rule_score`: The new fitness score for rule_023.
- `chaotic_medium_fitness_rule_score`: The new fitness score for rule_056.
- `stabilizing_rule_score`: The new fitness score for the A3-B14 rule.
- `metric_is_discriminating`: `true` if the stabilizing rule's score is at least 10x higher than both chaotic scores, `false` otherwise.


## Success Criteria

- The stabilizing rule's score is at least 10 times greater than the score of the chaotic high-fitness rule.
- The stabilizing rule's score is at least 10 times greater than the score of the chaotic medium-fitness rule.
- The final bit count for both chaotic rules is > 1000.
- The final bit count for the stabilizing rule is < 10.

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
