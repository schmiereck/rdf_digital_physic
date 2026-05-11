# Task – iter_035

**Hypothesis:** dynamics-symmetric: The symmetric rule from kernel (A=3, B=6) produces a stable, non-trivial oscillator or glider from a 2-bit seed.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_035/results/` (relative to the project root).

## Task

The task is to generate a new symmetric rule and then simulate it.

**Part 1: Rule Generation (in `src/rule_generator.py`)**
1. Define the kernel pair from iter_033: `A=3` ('0000011') and `B=6` ('0000110').
2. Create a function `rotate_neighborhood(state: int)` that performs a 60-degree clockwise rotation on the 6 neighbor bits.
3. Generate the full symmetric rule:
   - Initialize a rule dictionary where all 128 states map to themselves.
   - For `i` in `range(6)`:
     - `A_rot = rotate(A, i)`, `B_rot = rotate(B, i)`
     - Add mappings: `rule[A_rot] = B_rot` and `rule[B_rot] = A_rot`.
4. Save the final rule dictionary to a new file: `src/symmetric_rule_A3_B6.json`.

**Part 2: Simulation (in `src/simulate_hex.py`)**
1. Modify the simulator to load the rule from `src/symmetric_rule_A3_B6.json`.
2. Use the standard CA update model (not the symmetric swap scheduler).
3. Use a 100x100 grid with periodic boundaries for 100 steps.
4. **Initial Condition:** Place a 2-bit pattern near the center that creates neighborhood `A` ('0000011') for the cell at `(50,50)`. This means placing '1's at its SW `(49,51)` and NW `(50,51)` neighbors. The cell at `(50,50)` itself is '0'.

**Part 3: Output**
1. Create `archive/iter_034/result.yaml` with the following keys:
   - `is_bit_conserving`: `true` if the bit count remains 2 throughout.
   - `behavior_class`: `STATIONARY_OSCILLATOR`, `GLIDER`, `DECAY`, `CHAOTIC`, or `FIXED_POINT`.
   - `net_displacement`: The distance the pattern's center of mass moved from its initial position.
   - `final_pattern_coords`: The coordinates of the '1's at the final step.


## Success Criteria

- The total bit count remains 2 for all 100 steps.
- The `behavior_class` is either `STATIONARY_OSCILLATOR` or `GLIDER`.
- The pattern is not a `FIXED_POINT` (i.e., the coordinates of the bits change after step 1).

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
