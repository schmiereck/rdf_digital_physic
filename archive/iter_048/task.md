# Task – iter_048

**Hypothesis:** interaction-critical-distance: Two 3-bit oscillators, placed at a non-adjacent critical distance, interact in a non-trivial and bit-conserving manner.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_048/results/` (relative to the project root).

## Task

Use the existing `src/generate_and_simulate.py` script with the symmetric rule from the contiguous kernel `(A=3, B=6)` established in iter_044. The only change is the initial condition.

1.  **Simulation Setup:**
    - Grid Size: 100x100 with periodic boundaries.
    - Steps: 200.

2.  **Initial Condition:**
    - Place two 3-bit oscillator seeds on the grid, separated by one empty column of cells.
    - **Oscillator 1 Seed:** Place '1's at `(21,49)`, `(21,50)`, and `(22,50)`.
    - **Oscillator 2 Seed:** Place '1's at `(24,49)`, `(24,50)`, and `(25,50)`.
    - This setup ensures the initial patterns are not adjacent, but their oscillating fields will interact at `t=1`.

3.  **Analysis and Output:**
    - At each step, record the total number of '1's.
    - Track the coordinates of all '1's.
    - Create `archive/iter_048/result.yaml` with the following keys:
      - `is_bit_conserving`: `true` if the bit count remains 6.
      - `interaction_step`: The first step where the patterns are no longer two independent oscillators. Should be step 1 or 2.
      - `outcome_class`: A classification: `REFLECTION`, `FUSION`, `ANNIHILATION`, `PASS_THROUGH`, `STABLE_COMPOUND`, or `CHAOTIC`.
      - `final_state_summary`: A brief description of the final pattern(s) on the grid.


## Success Criteria

- The total bit count remains exactly 6 throughout the simulation.
- The final state is not chaotic and is not two independent oscillators.
- An interaction is observed (the state differs from the non-interacting case from iter_045).

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
