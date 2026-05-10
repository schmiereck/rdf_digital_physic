# Task – iter_016

**Hypothesis:** dynamics-2D-hex: A bit-rotation rule on the 7-cell neighborhood produces stable, linear glider propagation from a single-bit initial state.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_016/results/` (relative to the project root).

## Task

Create a Python script `src/simulate_hex.py` for a 2D cellular automaton on a hexagonal grid.

1.  **Grid Implementation**: Implement a 2D hexagonal grid (e.g., using axial coordinates) of at least 50x50 cells with periodic boundary conditions. Each cell should store a single bit ('0' or '1').

2.  **Rule Definition**: The rule is a permutation `P` of the 128 possible 7-cell neighborhood states. Implement the "Rotate Right" permutation:
    - A neighborhood is a 7-bit string `b0b1b2b3b4b5b6`, where `b0` is the center cell and `b1` to `b6` are the neighbors in clockwise order.
    - The rule maps this input to the output `b6b0b1b2b3b4b5`.

3.  **Update Logic**: The simulation updates the grid simultaneously. To compute the state at `t+1`:
    - For each cell `(x,y)` on the grid, read its 7-cell neighborhood at time `t`.
    - Apply the "Rotate Right" rule `P` to this 7-bit neighborhood state.
    - The new state for cell `(x,y)` at `t+1` is the *central bit* (the new `b0`) of the resulting 7-bit output.

4.  **Experiment Setup**:
    - Initialize the grid with all cells set to '0'.
    - Set a single cell near the center to '1'.
    - Run the simulation for 100 steps.

5.  **Analysis and Output**:
    - At each step, record the total number of '1's on the grid and their coordinates.
    - After 100 steps, determine the behavior.
    - Create `archive/iter_016/result.yaml` with these keys:
      - `is_bit_conserving`: `true` if the number of '1's at step 100 is equal to the initial count (1).
      - `behavior_class`: `GLIDER`, `STABLE`, `DECAY`, or `CHAOTIC`.
      - `final_bit_count`: The number of '1's on the grid at step 100.
      - `glider_velocity_hex`: A tuple `(dq, dr)` representing velocity in axial coordinates, if it's a glider.
      - `glider_period`: The number of steps for the glider's internal pattern to repeat (should be 7 for this rule).


## Success Criteria

- is_bit_conserving is true
- behavior_class is GLIDER
- final_bit_count is 1

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
