## Goal

Create and validate a new `CheckpointFitness` metric that correctly identifies and penalizes the unstable "transient bloomer" rule from `iter_176.3`.

### Step 1: Implement the `CheckpointFitness` Metric

Create a new file `src/fitness.py`. This file should contain a class `CheckpointFitness` with the following logic:

-   **`__init__(self, checkpoints, simulation_steps)`**:
    -   `checkpoints`: A list of integers representing the simulation steps at which to check for bit-count stability.
    -   `simulation_steps`: The total number of steps to run the simulation.

-   **`evaluate(self, rule, seed_bits)`**:
    -   This method takes a rule object and a list of seed bit coordinates.
    -   It should set up a `Particle` and a `Simulator` instance from the existing `src/simulator.py` module.
    -   It must record the initial bit count of the particle from the seed.
    -   It runs the simulation for `simulation_steps`.
    -   At each simulation step that is present in the `checkpoints` list, it must compare the current bit count of the particle to the initial bit count.
    -   **Crucially, if the bit count does not match at ANY checkpoint, the method must immediately terminate the simulation and return a fitness score of 0.0.**
    -   If the simulation completes and the bit count has remained stable at all checkpoints, the fitness score is the Euclidean distance between the initial and final center of mass of the particle.

You will need to import `Simulator` and `Particle` from `src/simulator.py`.

### Step 2: Create a Validation Script

Create a new file `src/validate_fitness.py` to test the new metric. This script must perform the following actions:

1.  **Import necessary modules**: `json`, `numpy`, and the new `CheckpointFitness` class from `src/fitness.py`. Also import `Rule` from `src/rule.py`.
2.  **Load the pathological rule**: Open and read the file `archive/iter_176/results/gen_5/rule_019.json` to load the rule that caused the previous fitness metric to fail.
3.  **Define the seed**: Use the standard 3-bit seed: `[[10, 10], [10, 11], [10, 12]]`.
4.  **Instantiate the metric**: Create an instance of `CheckpointFitness` with `checkpoints=[50, 100, 150, 200]` and `simulation_steps=200`.
5.  **Evaluate the rule**: Call the `evaluate` method on the fitness object, passing the loaded rule and the seed.
6.  **Report the result**: Print the final fitness score to standard output. The expected score is 0.0.

### Step 3: Execute and Report

Run the validation script and capture the results.

**Execution Command:**
```bash
python src/validate_fitness.py
```

**Final Output:**
Your task is complete when you have created the two files (`src/fitness.py`, `src/validate_fitness.py`), executed the validation script, and reported the outcome. The final YAML block in your response must be structured as follows:

```yaml
status: ok
artifacts:
  - "src/fitness.py"
  - "src/validate_fitness.py"
metrics:
  fitness_score_for_pathological_rule: <the_float_value_here>
log_excerpt: |
  <Last ~20 lines of output from `python src/validate_fitness.py`>
experimenter_view: |
  A summary of what you did and whether the new fitness metric behaved as expected. Confirm if it successfully assigned a fitness of 0.0 to the unstable rule.
notes: "Validation of CheckpointFitness complete."
```
