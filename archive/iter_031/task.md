# Task – iter_031

**Hypothesis:** interaction-stripe: The arrowhead glider's collision with a stationary stripe results in a non-trivial, bit-conserving interaction.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_031/results/` (relative to the project root).

## Task

Use the existing simulator at `src/simulate_hex.py` with the standard CA update model and the 5-pair permutation rule from iter_024.

1.  **Simulation Setup:**
    - Grid size: 100x100 with periodic boundaries.
    - Total steps: 150.

2.  **Initial Condition:**
    - Create a vertical stripe "wall": set all cells with coordinate `q=70` to '1'.
    - Place the 3-bit arrowhead glider at `q=20, r=50`. The glider points East (positive q direction), so its three '1' bits should be at `(20,50)`, `(19,50)`, and `(19,51)`. This ensures it is on a direct collision course with the stripe.

3.  **Analysis and Data Collection:**
    - At each step, record the total number of '1's on the grid.
    - For visualization, save the full grid state at steps `t=0`, `t=49` (pre-collision), `t=50` (impact), `t=51`, and `t=100` to `archive/iter_031/results/`.

4.  **Output:**
    - Create `archive/iter_031/result.yaml` with the following keys:
      - `collision_step`: The simulation step at which the glider first interacts with the stripe (should be `t=50`).
      - `is_bit_conserving`: `true` if the total bit count remains constant (initially 103 bits).
      - `outcome_class`: A string classification: `REFLECTION`, `ABSORPTION`, `DESTRUCTION`, `PASS_THROUGH`, or `CHAOTIC`.
      - `final_state_summary`: A brief text description of the final state of the glider and the stripe wall.


## Success Criteria

- The total bit count on the grid remains constant throughout the simulation.
- The glider's trajectory or structure changes significantly after `t=50`.
- The outcome is not a chaotic, ever-expanding pattern.

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
