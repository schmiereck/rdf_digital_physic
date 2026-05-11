# Task – iter_040

**Hypothesis:** dynamics-disjoint-orbit: The symmetric rule from kernel (A=65, B=6) produces a stable, non-trivial glider or oscillator from a 2-bit seed.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_040/results/` (relative to the project root).

## Task

The task is to generate a rule from the first valid disjoint-orbit kernel and simulate it.

**Part 1: Rule Generation**
1. Create or modify a script `src/rule_generator.py`.
2. The kernel is the state-pair `(A, B)` where `A = 65` (`0b1000001`) and `B = 6` (`0b0000110`).
3. Generate the full symmetric rule by applying all 6 rotations to this kernel. The rule is a permutation of the 128 neighborhood states.
   - For each of the 6 rotations `i`, calculate `A_rot = rotate(A, i)` and `B_rot = rotate(B, i)`.
   - The rule should contain the 12 mappings `rule[A_rot] = B_rot` and `rule[B_rot] = A_rot`.
   - All other 116 states should be identity mappings (`rule[X] = X`).
4. Save this complete rule mapping to `src/symmetric_rule_A65_B6.json`.

**Part 2: Simulation**
1. Modify `src/simulate_hex.py` to load the rule from `src/symmetric_rule_A65_B6.json`.
2. Ensure the simulator uses the **standard CA update model** (each cell's new state is the center bit of its neighborhood's output from the rule table).
3. Run a simulation for 100 steps on a 100x100 grid with periodic boundaries.
4. **Initial Condition:** Place a 2-bit pattern designed to trigger the rule. The cell at `(50,50)` needs to see neighborhood `B=6` (`0b0000110`). This is achieved by placing '1's at its neighbors `b2` (South-East) and `b3` (South). For a reference cell at (50,50), place '1's at `(51, 49)` and `(50, 49)`.

**Part 3: Output**
1. Create `archive/iter_037/result.yaml` with the following keys:
   - `is_bit_conserving`: `true` if the bit count evolves as expected by the rule (e.g., 2 -> 3 -> ...).
   - `behavior_class`: `GLIDER`, `STATIONARY_OSCILLATOR`, `DECAY`, `CHAOTIC`, or `FIXED_POINT`.
   - `net_displacement`: The net distance the center of mass of the pattern moved from its initial position.
   - `final_pattern_coords`: A list of coordinates of the '1's at the final step.


## Success Criteria

- The `behavior_class` is `GLIDER` or `STATIONARY_OSCILLATOR`.
- The final pattern is stable (not chaotic or decaying).
- The initial 2-bit pattern evolves into a new, non-trivial state within the first few steps.

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
