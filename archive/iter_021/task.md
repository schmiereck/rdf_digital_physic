# Task – iter_021

**Hypothesis:** composite-rule: A rule combining two conditional swaps produces a stable, non-trivial 2D glider from a two-bit seed.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_021/results/` (relative to the project root).

## Task

Modify the `src/simulate_hex.py` script. Continue using the symmetric swap update model from iter_020.

1. **Implement Composite Rule:** The rule for a cell `c` to initiate a swap is now determined by two prioritized conditions:
   a. **Condition 1:** If neighbor `b1` (East) is '1', swap with neighbor `b2` (South-East).
   b. **Condition 2:** Else, if neighbor `b2` (South-East) is '1', swap with neighbor `b1` (East).
   (If a cell `c` triggers a swap based on Condition 1, it does not evaluate Condition 2 in the same step).

2. **Run Two Simulations** (100 steps, 50x50 grid):
   a. **Test:** Initial state with two bits: one at center `(q,r)`, one at its East neighbor `(q+1,r)`.
   b. **Control:** Initial state with a single bit at the center.

3. **Analysis and Outputs:**
   - For each simulation, track coordinates and bit count.
   - Create `archive/iter_021/result.yaml` with the following keys:
     - `is_bit_conserving`: `true` if both sims maintain initial bit counts.
     - `control_behavior`: `STATIONARY` or `MOVED`.
     - `test_behavior`: `GLIDER`, `OSCILLATOR`, `STATIONARY`, or `CHAOTIC`.
     - `is_nontrivial_motion`: `true` if control is `STATIONARY` and test is `GLIDER`.
     - `final_bit_count_test`: The final number of '1's in the test simulation.
     - `glider_velocity_hex`: A tuple `(avg_dq_per_step, avg_dr_per_step)` for the test simulation's center of mass.


## Success Criteria

- `is_nontrivial_motion` is true
- `test_bit_count_final` is 2
- `test_behavior` is `GLIDER`
- The calculated `glider_velocity_hex` has at least one non-zero component

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
