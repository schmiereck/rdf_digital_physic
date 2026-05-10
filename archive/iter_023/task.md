# Task – iter_023

**Hypothesis:** asymmetric-rule: An asymmetric swap rule (if East=1, swap Center<->NW) produces a stable, non-trivial 2D glider from a two-bit seed.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_023/results/` (relative to the project root).

## Task

Use the existing script `src/simulate_hex.py` with the symmetric swap update model. No changes to the simulation logic are needed.

1.  **Implement New Rule:** Modify the rule evaluated by each cell `c`.
    - The rule is: "If my neighbor `b1` (East) is '1', then I initiate a swap with my neighbor `b6` (North-West)."
    - This is the only swap condition. If `b1` is '0', the rule is a no-op for cell `c`.

2.  **Test Simulation Initial Condition:**
    - On a 50x50 grid, initialize two cells with '1's:
      - The center cell `c = (25, 25)`
      - Its East neighbor `b1 = (26, 25)`
    - This two-bit seed is designed to trigger the rule from the first step.

3.  **Control Simulation:**
    - Run the standard control: a single '1' at the grid center.

4.  **Execution & Output:**
    - Run both simulations for 100 steps.
    - Create `archive/iter_023/result.yaml` with the usual keys: `is_bit_conserving`, `control_behavior`, `test_behavior`, `is_nontrivial_motion`, `final_bit_count_test`, and `glider_velocity_hex`.


## Success Criteria

- `is_nontrivial_motion` is true (control is stationary, test moves).
- `test_behavior` is 'GLIDER'.
- `glider_velocity_hex` has at least one non-zero component.
- `is_bit_conserving` is true.

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
