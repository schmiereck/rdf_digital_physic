# Task – iter_041

**Hypothesis:** dynamics-next-kernel: The symmetric rule from the next valid kernel (post-A65,B6) produces a stable, multi-step oscillator or glider.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_041/results/` (relative to the project root).

## Task

This is a two-part task.

**Part 1: Find the Next Valid Kernel**
1. Modify `src/find_center_flipping_kernel.py`.
2. The script must search for state-pairs `(A, B)` with Hamming Weight 2 that satisfy all three conditions: center-bit flipping, disjoint orbits, and conflict-free closure.
3. Instead of stopping at the first valid kernel (`A=65, B=6`), the script must continue searching and find the **second** valid kernel.
4. The script should print the integer and binary representations of this new kernel pair to the console.

**Part 2: Generate Rule and Simulate**
1. Create a new script `src/generate_rule.py` that takes the new kernel pair from Part 1 as input. It should generate the full 6-fold symmetric rule and save it to `src/symmetric_rule_next.json`.
2. Modify `src/simulate_hex.py` to load its rule from `src/symmetric_rule_next.json`.
3. The simulation should run for 100 steps on a 100x100 grid.
4. The initial condition must be a pattern that creates one of the new kernel's neighborhood states. For example, if the new kernel contains state `B'`, seed the grid with the bit pattern corresponding to `B'`.
5. Save the results to `archive/iter_041/result.yaml`.


## Success Criteria

- The final behavior class is `GLIDER` or `STATIONARY_OSCILLATOR`.
- If an oscillator, the `oscillation_period` is > 1.
- If a glider, the `net_displacement` is > 1.0.
- The bit count is conserved throughout the simulation.

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
