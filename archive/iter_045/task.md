# Task – iter_045

**Hypothesis:** interaction-oscillator: Two 3-bit oscillators, under the rule from iter_044, interact in a non-trivial, bit-conserving manner.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_045/results/` (relative to the project root).

## Task

Use the existing `src/generate_and_simulate.py` script and the symmetric rule generated from the contiguous kernel `(A=3, B=6)` as established in iter_044.

1.  **Simulation Setup:**
    - Grid Size: 100x100 with periodic boundaries.
    - Steps: 200.

2.  **Initial Condition:**
    - Place two 3-bit oscillator seeds on the grid, positioned close enough for their oscillating patterns to interact.
    - **Oscillator 1 Seed:** Place '1's at `(21,49)`, `(21,50)`, and `(22,50)`.
    - **Oscillator 2 Seed:** Place '1's at `(25,49)`, `(25,50)`, and `(26,50)`.
    - The total initial bit count must be 6.

3.  **Analysis and Output:**
    - At each step, record the total number of '1's on the grid.
    - Track the coordinates of all '1's throughout the simulation.
    - Create `archive/iter_045/result.yaml` with the following keys:
      - `is_bit_conserving`: `true` if the bit count remains 6.
      - `interaction_step`: The first step where a bit from one oscillator is in the neighborhood of a bit from the other.
      - `outcome_class`: A classification of the result: `REFLECTION`, `FUSION`, `ANNIHILATION`, `PASS_THROUGH`, `STABLE_COMPOUND`, or `CHAOTIC`.
      - `final_state_summary`: A brief description of the final pattern(s) on the grid.


## Success Criteria

- The total bit count remains 6 throughout the simulation.
- The final state is not two independent, unchanged oscillators identical to the single-oscillator case.
- The outcome is deterministic and stable (i.e., not chaotic).

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
