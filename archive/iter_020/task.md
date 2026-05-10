# Task – iter_020

**Hypothesis:** symmetric-update: A symmetric swap-based update model, combined with a conditional rule, can produce a non-trivial, localized 2D particle.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_020/results/` (relative to the project root).

## Task

Modify `src/simulate_hex.py` to use a new, symmetric update scheduler.

1.  **New Update Mechanism ("Symmetric Swap"):**
    - The simulation step should no longer compute a new state for each cell from scratch. Instead, it will apply swaps to the existing grid state.
    - To avoid conflicting operations, only one cell in a potential swap pair should initiate the action. A simple convention is that a cell `c` can only initiate a swap with a neighbor `n` if `c`'s index/coordinates are less than `n`'s.
    - The main loop should iterate through all cells `c`. For each `c`, it will evaluate a rule. The rule's output determines *if and with which neighbor* `c` should swap its state. If the rule says to swap with neighbor `n` (and `c < n`), the states of `c` and `n` are exchanged in place.

2.  **Implement Conditional Swap Rule:**
    - The rule to evaluate for each cell `c` is: "If my neighbor `b1` (East) is '1', then I should swap with my neighbor `b2` (South-East)."
    - Note: This rule is evaluated from the perspective of cell `c`. The swap itself is a symmetric operation on the grid.

3.  **Run Two Simulations (for 100 steps on a 50x50 grid):**
    - **Sim 1 (Test):** Initial state is a two-bit pattern. Place a '1' at the grid center `(q,r)` and another '1' at its neighbor `b1` `(q+1, r)`.
    - **Sim 2 (Control):** Initial state is a single '1' at the grid center.

4.  **Outputs:**
    - Create `archive/iter_020/result.yaml` with the following keys:
      - `is_bit_conserving`: `true` if both simulations maintained their initial bit counts.
      - `control_behavior`: Behavior of the single-bit simulation (`STATIONARY` or `MOVED`).
      - `test_behavior`: Behavior of the two-bit simulation (`GLIDER`, `OSCILLATOR`, `STATIONARY`, `DECAY`).
      - `is_nontrivial_motion`: `true` only if `control_behavior` is `STATIONARY` AND `test_behavior` is `GLIDER` or `OSCILLATOR`. This is the primary success criterion.
      - `final_pattern_test`: A string representation of the final coordinates of the '1's in the test simulation.


## Success Criteria

- The total number of '1's remains constant in both simulations.
- The single-bit particle remains stationary (`control_behavior` is `STATIONARY`).
- The two-bit particle moves from its initial position (`test_behavior` is `GLIDER`).

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
