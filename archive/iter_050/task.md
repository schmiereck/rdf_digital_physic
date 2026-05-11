# Task – iter_050

**Hypothesis:** dynamics-w3: The symmetric rule from the W=3 kernel (A=7, B=14) produces a stable, bit-conserving, non-trivial object from a 3-bit seed.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_050/results/` (relative to the project root).

## Task

This is a two-part task: generate the new rule, then simulate it.

**Part 1: Generate the W=3 Rule**
1. Create a script, `src/generate_w3_rule.py`, that performs the following:
2. Define the kernel pair from iter_049: `A = 7` ('0000111') and `B = 14` ('0001110').
3. Implement the 6-fold hexagonal rotation for 7-bit integer states.
4. Generate the full symmetric rule: Initialize a rule dictionary with identity mappings, then add the 12 mappings for the 6 rotations of the `(A, B)` pair and their inverses.
5. Save the final rule dictionary to `src/symmetric_rule_w3_a7_b14.json`.

**Part 2: Simulate the New Rule**
1. Modify `src/generate_and_simulate.py` (or a similar script) to load the rule from `src/symmetric_rule_w3_a7_b14.json`.
2. Use the standard CA update model.
3. Run the simulation for 200 steps on a 100x100 grid with periodic boundaries.
4. **Initial Condition:** A 3-bit seed that creates neighborhood `B=14` ('0001110') for a central '0' cell at `(50,50)`. This is achieved by placing '1's at its E, SE, and S neighbors: `(51,50)`, `(51,49)`, and `(50,49)`.
5. The script must create `archive/iter_050/result.yaml` with the standard keys: `kernel_A`, `kernel_B`, `is_bit_conserving`, `behavior_class`, `net_displacement`, `oscillation_period`, and `final_bit_count`.


## Success Criteria

- The final bit count remains 3 throughout the simulation.
- The final pattern is non-trivial (not a fixed point or decayed).
- The final pattern is stable and periodic (either oscillating or moving).

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
