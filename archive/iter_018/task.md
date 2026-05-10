# Task – iter_018

**Hypothesis:** glider-rules-interact: At least one of the 22 known v=c glider rules produces a non-trivial, non-chaotic interaction from a two-bit ('11') initial condition.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_018/results/` (relative to the project root).

## Task

Create a new Python script `src/characterize_rules.py` based on the 1D simulator logic.

1.  **Load Rules:** Load the 33 valid rules from `archive/iter_001/results/valid_rules.json`. Identify the 22 rules that produced gliders in iter_002.
2.  **Simulation Setup:** For each of the 22 glider-producing rules:
    a. Initialize a 1D lattice of size 100 with all cells set to '0'.
    b. Set the initial condition to be two adjacent '1's at the center: cell 49 = '1', cell 50 = '1'.
    c. Run the simulation for 100 steps with periodic boundary conditions.
3.  **Analysis & Classification:** After each simulation, classify the rule's outcome into one of the following categories based on the final state:
    - `ELASTIC`: The final state consists of two single '1' bits moving away from each other.
    - `FUSION`: The final state is a new stable pattern (stationary or moving) that is not two separate '1's.
    - `ANNIHILATION`: The lattice returns to all '0's.
    - `CHAOTIC`: The number of '1's grows, or the pattern is complex and non-repeating.
4.  **Output:** Write a summary to `archive/iter_007/result.yaml` with the following keys:
    - `rules_tested`: 22
    - `elastic_collisions`: (count)
    - `fusions`: (count)
    - `annihilations`: (count)
    - `chaotic_outcomes`: (count)
    - `elastic_rule_indices`: A list of indices for rules that produced elastic collisions.


## Success Criteria

- The script successfully tests all 22 glider rules.
- The sum of outcome counts equals 22.
- At least one rule is classified as `ELASTIC` or `FUSION`.

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
