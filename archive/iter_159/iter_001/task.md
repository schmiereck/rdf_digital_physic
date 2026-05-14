## Task: Validate Composite Fitness Metric

Modify `src/main.py` to implement and test a new composite fitness metric.

### 1. Modify `main.py`:
- Add a new fitness function `calculate_composite_fitness`.
- This function should calculate:
    - `late_displacement`: Euclidean distance between Center of Mass at `t=1200` and `t=2000`.
    - `final_bit_count`: The total number of live cells at `t=2000`.
    - `composite_fitness`: `late_displacement / (1 + final_bit_count)`.
- Add command-line arguments to support running a simulation for a *single, specific rule* identified by its key from a given population JSON file.
    - `--rule-key <key>` (e.g., `rule_058`)
    - `--population-file <path>` (e.g., `archive/iter_158/results/population_gen1.json`)

### 2. Run Simulation:
- Execute the modified script to test rule `rule_058` from the population file `archive/iter_158/results/population_gen1.json`.
- Use the standard simulation parameters:
    - Steps: 2000
    - Grid size: 128x128
    - Initial soup seed: 42
    - Initial soup density: 0.25

### 3. Report Results:
- The final YAML output must include the following metrics:
    - `late_displacement`
    - `final_bit_count`
    - `composite_fitness`
    - The original `late_displacement_fitness` (which is just `late_displacement`) for comparison.
- Save a visualization of the final grid state at `t=2000` to `archive/iter_159/results/final_grid_rule_058.png`.
- In the `experimenter_view`, qualitatively describe the final grid state. Is it a compact object or a diffuse, messy collection of ash?

The goal is to verify if the new metric correctly penalizes the non-compact nature of the previous best-performing rule.
```yaml
status: ok
artifacts:
- relative/path/to/final_grid_rule_058.png
metrics:
  late_displacement: 0.158514
  final_bit_count: 531
  composite_fitness: 0.000298
  late_displacement_fitness: 0.158514
log_excerpt: |
  ...
experimenter_view: |
  ...
notes: "Implemented new metric and tested rule_058."
```