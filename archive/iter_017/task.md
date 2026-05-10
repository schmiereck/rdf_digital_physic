# Task – iter_017

**Hypothesis:** dynamics-2D-swap: A center-neighbor bit-swap rule produces a stationary period-2 oscillator.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_017/results/` (relative to the project root).

## Task

Use the existing simulator at `src/simulate_hex.py`.

1.  **Modify the Rule:** Change the rule implemented in the simulator. The new rule is "Swap Center with Neighbor 1".
    - For any 7-bit neighborhood input `b0b1b2b3b4b5b6` (where `b0` is the center and `b1..b6` are neighbors clockwise), the output is `b1b0b2b3b4b5b6`.
    - This rule is a simple permutation and is its own inverse, guaranteeing reversibility.

2.  **Experiment Setup:**
    - Use a 50x50 hexagonal grid with periodic boundaries.
    - Initialize the grid with all cells '0', except for a single '1' at the center.

3.  **Execution:**
    - Run the simulation for 50 steps.
    - The update logic remains the same: the new state of a cell is the central bit of the rule's output for its neighborhood.

4.  **Analysis & Output:**
    - Track the coordinates of the '1' bit at each step.
    - Create `archive/iter_017/result.yaml` with the following keys:
      - `behavior_class`: `STATIONARY_OSCILLATOR`, `GLIDER`, `DECAY`, `STABLE`, or `CHAOTIC`.
      - `oscillation_period`: The number of steps for the '1' bit's position to repeat.
      - `is_bit_conserving`: `true` if the total bit count remains 1.
      - `final_bit_count`: The number of '1's on the grid at step 50.


## Success Criteria

- `behavior_class` is `STATIONARY_OSCILLATOR`
- `oscillation_period` is 2
- `final_bit_count` is 1

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
