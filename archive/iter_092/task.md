# Task – iter_092

**Hypothesis:** re-evaluate-gen3-motion: The Gen-3 population, evolved for stability, contains at least one rule with non-zero motion-based fitness.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_092/results/` (relative to the project root).

## Task

Create a new script, `src/reevaluate_gen3_for_motion.py`.

1.  **Load Population:** The script must load all 100 rules from the Gen-3 population located in `archive/iter_088/population/`.

2.  **Evaluate Population:** For each of the 100 rules, calculate its fitness using the motion-based metric validated in iter_090.
    - **Procedure per rule:**
      a. Initialize a 150x150 grid with a single 4-bit contiguous "T-shape" seed.
      b. Simulate for 500 steps.
      c. Detect if the pattern enters a stable cycle with `bit_count > 0`.
      d. If a stable object is found, calculate its net displacement over one period.
      e. Fitness = `displacement / (1 + final_bit_count)`. Fitness is 0 if no cycle is found, the object decays, or displacement is zero.

3.  **Report Results:**
    - Save the fitness score and behavior class for all 100 rules to `archive/iter_092/results/gen3_motion_scores.csv`.
    - Create `archive/iter_092/result.yaml` summarizing the findings. It must contain the following keys:
      - `rules_with_motion`: The count of rules with a fitness score > 0.
      - `top_fitness_score`: The highest fitness score found.
      - `top_rule_id`: The filename of the rule with the highest score.
      - `top_rule_glider_period`: The period of the glider produced by the top rule (or 0).
      - `top_rule_glider_bit_count`: The final bit count of the glider from the top rule (or 0).
      - `top_rule_glider_velocity`: The (dq, dr) velocity vector of the glider from the top rule (or (0,0)).


## Success Criteria

- At least one rule has a fitness score > 0.
- The `rules_with_motion` key in result.yaml is >= 1.

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
