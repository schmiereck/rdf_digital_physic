# Task – iter_043

**Hypothesis:** dynamics-next-kernel: The symmetric rule from the second valid kernel produces a stable, multi-step oscillator or glider.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_043/results/` (relative to the project root).

## Task

This is a two-part task to robustly retry the failed iter_041.

**Part 1: Find the Second Valid Kernel**
1. Create a script `src/find_next_kernel.py`.
2. This script must search for state-pairs `(A, B)` with Hamming Weight 2 that satisfy all three conditions from iter_038:
    a. Center-bit of A is different from center-bit of B.
    b. The rotational orbits of A and B are disjoint.
    c. The joint 12-state rotational closure is conflict-free.
3. The script must find and **ignore** the first valid kernel (`A=65, B=6` or equivalent) and then find and output the **second** valid kernel.
4. The script should print the integers and binary strings for the second kernel pair to stdout for verification. Let's call them `A2` and `B2`.

**Part 2: Generate Rule and Simulate**
1. Create a script `src/generate_and_simulate.py`.
2. This script must programmatically take the `A2` and `B2` values and generate the full 6-fold symmetric rule.
3. The simulator part of the script must use this new rule with the standard CA update model.
4. Run the simulation for 100 steps on a 100x100 grid.
5. The initial condition must be a 2-bit pattern that creates the neighborhood `B2` for a central '0' cell. For example, if `B2` is `'0000110'`, place two '1's at the appropriate neighbor positions of a central cell.
6. The script's final action must be to create `archive/iter_043/result.yaml` with the following keys:
    - `kernel_A`: The integer `A2` used.
    - `kernel_B`: The integer `B2` used.
    - `is_bit_conserving`: `true` if the bit count remains stable as expected.
    - `behavior_class`: `GLIDER`, `STATIONARY_OSCILLATOR`, `DECAY`, `CHAOTIC`, or `FIXED_POINT`.
    - `net_displacement`: The final distance the pattern's center of mass moved.
    - `oscillation_period`: The period of the oscillation, if any.


## Success Criteria

- The simulation produces a non-trivial pattern that is not a fixed point (i.e., `net_displacement > 0` or `oscillation_period > 1`).
- The total number of '1's on the grid remains constant after an initial settling period.

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
