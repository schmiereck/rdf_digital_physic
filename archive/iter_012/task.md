# Task – iter_012

**Hypothesis:** dynamics-2bit: The minimal 2-bit/cell rule from iter_003 produces a stable, stationary period-2 oscillation.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_012/results/` (relative to the project root).

## Task

Create a Python script `archive/iter_004/code/simulate_2bit.py`. This script will be a 1D cellular automaton simulator for a 2-bit/cell lattice.

1.  **Simulator Logic:**
    - The lattice is a 1D array of cells, where each cell holds a 2-bit string (e.g., '00', '01', '10', '11').
    - In each step, calculate the next state of the lattice by applying a rule to the 3-cell neighborhood of each cell.

2.  **Implement the Rule:** The rule to implement is the one constructed in iter_003:
    - `('00', '01', '00')` maps to `('00', '10', '00')`.
    - `('00', '10', '00')` maps to `('00', '01', '00')`.
    - All other 62 possible 3-cell neighborhood configurations map to themselves (identity mapping).

3.  **Experiment Setup:**
    - Initialize a lattice of size 100. All cells are '00'.
    - Set the central cell (at index 50) to '01'. This is the initial condition.
    - Run the simulation for 50 steps with periodic boundary conditions.

4.  **Analysis and Output:**
    - During the simulation, track the state of the central cell at each step.
    - After the simulation, classify the overall behavior.
    - Create `archive/iter_004/result.yaml` with the following keys:
      - `behavior_class`: A string, must be one of `STATIONARY_OSCILLATION`, `STABLE`, `DECAY`, `GLIDER`, or `CHAOTIC`.
      - `oscillation_period`: An integer. The number of steps for the pattern to repeat.

5.  **Logging (Optional but helpful):** Create `archive/iter_004/results/` and save the full lattice state for steps 0, 1, 2, and 3 as text files for inspection.


## Success Criteria

- The `behavior_class` in `result.yaml` is `STATIONARY_OSCILLATION`.
- The `oscillation_period` in `result.yaml` is `2`.

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
