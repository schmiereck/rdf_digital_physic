# Task – iter_066

**Hypothesis:** dynamics-nonconserving: The rule from kernel (A=3, B=14) produces a stable, non-trivial object from a 3-bit seed.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_066/results/` (relative to the project root).

## Task

This is a two-part task: first, generate the new non-conserving rule, and second, simulate it.

**Part 1: Generate the Rule**
1. Create a script, `src/generate_nonconserving_rule.py`.
2. Define the kernel pair from iter_065: `A = 3` ('0000011', popcount=2) and `B = 14` ('0001110', popcount=3).
3. Implement the 6-fold hexagonal rotation for 7-bit integer states.
4. Generate the full symmetric rule: Initialize a rule dictionary with identity mappings, then add the 12 mappings for the 6 rotations of the `(A, B)` pair and their inverses (A_rot -> B_rot and B_rot -> A_rot).
5. Save the final rule dictionary to `src/symmetric_rule_nonconserving_A3_B14.json`.

**Part 2: Simulate the Rule**
1. Create a script, `src/simulate_nonconserving.py`, that loads the rule from `src/symmetric_rule_nonconserving_A3_B14.json`.
2. Use the standard CA update model.
3. Run the simulation for 300 steps on a 100x100 grid with periodic boundaries.
4. **Initial Condition:** A 3-bit seed that creates neighborhood `B=14` for a central '0' cell at `(50,50)`. This is achieved by placing '1's at its E, SE, and S neighbors: `(51,50)`, `(51,49)`, and `(50,49)`.
5. The script must create `archive/iter_066/result.yaml` with the following keys:
    - `kernel_A`, `kernel_B`: The integers 3, 14.
    - `object_found`: `true` if a stable object was found, `false` otherwise.
    - `behavior_class`: `GLIDER`, `STILL_LIFE`, `OSCILLATOR`, `DECAY`, or `CHAOTIC_GROWTH`.
    - `final_bit_count`: The bit count of the stable object, or the final count after 300 steps.
    - `is_globally_bit_conserving`: `true` if the total bit count remains 3 throughout.
    - `object_period`: The period of the found object.
    - `net_displacement`: The net displacement of the object's center of mass over one period.


## Success Criteria

- The simulation completes and generates a result.yaml.
- The total bit count of the pattern stabilizes or enters a stable cycle.
- The pattern itself enters a cycle (still life, oscillator, or glider).

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
