
Create a Python script `src/analyze_long_run_dynamics.py` to investigate the long-term behavior of the top-evolved rule.

**1. Setup:**
   - Load the top-performing rule from Gen-3: `archive/iter_123/population/rule_001.json`.
   - Load the canonical ash pattern from `src/ash_pattern.json`.
   - Initialize the simulation environment.

**2. Simulation and Data Logging:**
   - Run the simulation for a total of 500 steps.
   - Create a list to store time-series data.
   - At every 10th step (i.e., step 0, 10, 20, ..., 500), record the following into the list:
     - `step`: The current simulation step.
     - `displacement`: The cumulative displacement of the center of mass from its initial position.
     - `bit_count`: The number of live cells.
     - `object_count`: The number of distinct connected components.

**3. Output Results:**
   - Save the collected time-series data to a CSV file: `archive/iter_125/results/long_run_data.csv`.
   - From the collected data, determine the displacement at step 100 and step 500.
   - Create the final `result.yaml` file at `archive/iter_125/result.yaml` with the following metrics:
     - `displacement_at_100_steps`: The displacement recorded at step 100.
     - `displacement_at_500_steps`: The displacement recorded at step 500.
     - `final_bit_count`: The bit count at step 500.
     - `final_object_count`: The object count at step 500.
     - `motion_sustained`: A boolean, `true` if the displacement at 500 steps is at least 4 times greater than the displacement at 100 steps, `false` otherwise. This provides a clear quantitative test for sustained motion versus transient rearrangement.

The script must end with the standard YAML block reporting its execution status.
```yaml
status: ok
artifacts:
  - "archive/iter_125/result.yaml"
  - "archive/iter_125/results/long_run_data.csv"
metrics: { ... } # Copy metrics from the generated result.yaml
log_excerpt: |
  ...
experimenter_view: |
  ...
notes: ""
```
