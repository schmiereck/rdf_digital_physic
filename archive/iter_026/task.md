# Task – iter_026

**Hypothesis:** interaction: The arrowhead glider collides with a stationary bit, resulting in non-trivial, bit-conserving scattering.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_026/results/` (relative to the project root).

## Task

Use the existing simulator at `src/simulate_hex.py` with the standard CA update model and the hand-crafted 5-pair permutation rule from iter_024.

1.  **Simulation Setup:**
    - Use a larger grid, e.g., 100x100, with periodic boundary conditions to provide space for scattering.
    - Run the simulation for 150 steps.

2.  **Initial Condition:**
    - Place the 3-bit arrowhead glider with its tip at `(q=20, r=50)`, pointing East (positive q direction). The three '1's should be at `(20,50)`, `(19,50)`, and `(19,51)`.
    - Place a single stationary '1' bit at `(q=70, r=50)`, directly in the glider's path.

3.  **Analysis and Data Collection:**
    - At each step, record the total number of '1's on the grid.
    - At each step, record the coordinates of all '1's. This data can be saved to `archive/iter_025/results/path_trace.json`.
    - Characterize the final state of the system after 150 steps.

4.  **Output:**
    - Create `archive/iter_025/result.yaml` with the following keys:
      - `collision_step`: The simulation step at which the glider first interacts with the stationary bit.
      - `is_bit_conserving`: `true` if the total bit count remained 4 throughout.
      - `outcome_class`: A string classification: `DEFLECTION`, `ABSORPTION`, `DESTRUCTION`, `PASS_THROUGH`, `CHAOTIC_GROWTH`.
      - `final_state_summary`: A brief description of the final particle(s), their final positions, and their velocities.


## Success Criteria

- The total bit count remains exactly 4 for all 150 steps.
- The final state is not chaotic (i.e., the number of particles is small and stable).
- The glider's trajectory after the collision step is measurably different from its initial trajectory.

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
