# Task – iter_019

**Hypothesis:** conditional-swap: A rule swapping a cell with its neighbor, conditioned on a second neighbor's state, produces a non-trivial 2D glider from a two-bit seed.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_019/results/` (relative to the project root).

## Task

Use the existing simulator at `src/simulate_hex.py`.

1. **Implement the Conditional Rule:**
   - A neighborhood is a 7-bit string `b0b1b2b3b4b5b6` (center `b0`, neighbors `b1..b6` clockwise).
   - The rule is: if neighbor `b1` is '1', then swap the center `b0` with neighbor `b2`.
   - This means any neighborhood `b01b2...` maps to `b21b0...`. This rule is its own inverse, ensuring reversibility.
   - All neighborhoods where `b1` is '0' are identity mappings (they map to themselves).

2. **Run Two Simulations:**
   - Use a 50x50 hexagonal grid with periodic boundaries. Run for 100 steps.
   - **Simulation 1 (Control):** Initialize the grid with a single '1' at the center.
   - **Simulation 2 (Test):** Initialize the grid with two adjacent '1's: one at the center, and one at the position of neighbor 1.

3. **Analysis and Output:**
   - For each simulation, track the coordinates and number of '1' bits.
   - Create `archive/iter_019/result.yaml` with the following keys:
     - `single_bit_behavior`: Classify as `STATIONARY`, `OSCILLATOR`, `GLIDER`, or `DECAY`.
     - `two_bit_behavior`: Classify as `GLIDER`, `STATIONARY_OSCILLATOR`, `DECAY`, or `CHAOTIC`.
     - `is_nontrivial_motion`: A boolean, `true` only if `single_bit_behavior` is `STATIONARY` and `two_bit_behavior` is `GLIDER`.
     - `final_bit_count_single`: Final number of '1's for simulation 1.
     - `final_bit_count_two`: Final number of '1's for simulation 2.
     - `glider_velocity_hex`: The `(dq, dr)` velocity in axial coordinates if a glider is formed in sim 2.


## Success Criteria

- The `is_nontrivial_motion` key in result.yaml is `true`.
- The final bit count for both simulations is equal to the initial bit count (1 and 2 respectively).
- The glider in the two-bit simulation maintains a stable, contiguous shape.

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
