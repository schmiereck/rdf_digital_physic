
Create a new script `src/measure_baseline.py` to establish a performance baseline for the new velocity-stability fitness metric.

**Methodology:**
1.  **Generate Population:** Create a new, random population of 100 C2-symmetric rules. Use a fixed random seed for reproducibility. Each rule should have a medium density (8 kernel pairs).
2.  **Evaluate Fitness:** For each rule in the population:
    a. Run a simulation for 1600 steps from the standard 'soup' initial condition.
    b. Calculate the velocity-stability fitness score using the implementation from `src/fitness.py`.
    c. **Crucially, add a check for annihilation:** If the total displacement over the entire 1600 steps is zero, assign a fitness score of 0.0 to that rule. This prevents rewarding rules that simply erase everything.
3.  **Analyze and Report:**
    a. Save the raw fitness scores for all 100 rules to `archive/iter_150/results/fitness_scores.csv`.
    b. Calculate and report the following statistics as the primary metrics for this experiment: `mean_fitness`, `median_fitness`, `max_fitness`, and `std_dev_fitness`.
    c. Report the `annihilation_count`, the number of rules that had zero total displacement and were assigned a fitness of 0.

**Final YAML:**
The final YAML block in the script's output should include these calculated metrics.
```yaml
status: ok
artifacts:
  - "archive/iter_150/results/fitness_scores.csv"
metrics:
  mean_fitness: <value>
  median_fitness: <value>
  max_fitness: <value>
  std_dev_fitness: <value>
  annihilation_count: <value>
  population_size: 100
log_excerpt: |
  ...
experimenter_view: |
  ...
notes: "Baseline measurement for velocity-stability metric."
```
